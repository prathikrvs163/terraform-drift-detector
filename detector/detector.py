from detector.terraform_runner import TerraformRunner
from detector.parser import TerraformPlanParser
from detector.report import ReportGenerator
from detector.database import DriftDatabase
from detector.emailer import EmailSender
import json


def main():

    emailer = EmailSender()
    runner = TerraformRunner()
    parser = TerraformPlanParser()
    report = ReportGenerator()
    database = DriftDatabase()

    print("Initializing Terraform...")

    init = runner.init()

    if init.returncode != 0:
        print(init.stderr)
        database.close()
        return

    print("Running Terraform Plan...")

    plan = runner.plan()

    # Exit Code 0 -> No Drift
    if plan.returncode == 0:

        print("✅ No drift detected.")

        database.close()
        return

    # Exit Code 2 -> Drift Found
    elif plan.returncode == 2:

        print("\n⚠ Drift detected!")

        json_plan = runner.show()

        plan = json.loads(json_plan.stdout)

        resources = []

        for resource in plan["resource_changes"]:

            action = resource["change"]["actions"][0]

            if action == "no-op":
                continue

            before = resource["change"]["before"]
            after = resource["change"]["after"]

            changes = parser.find_changes(before, after)

            resources.append({
                "resource": resource["address"],
                "type": resource["type"],
                "action": action,
                "changes": changes
            })

        # ----------------------------
        # Console Output
        # ----------------------------

        print("\nTerraform Drift Report")
        print("=" * 60)

        for resource in resources:

            print(f"\nResource : {resource['resource']}")
            print(f"Type     : {resource['type']}")
            print(f"Action   : {resource['action']}")

            print("\nDetected Changes")
            print("-" * 30)

            for change in resource["changes"]:

                print(f"\nProperty   : {change['property']}")
                print(f"Azure      : {change['azure']}")
                print(f"Terraform  : {change['terraform']}")

        print("\n" + "=" * 60)

        # ----------------------------
        # Save to SQLite
        # ----------------------------

        database.save_all(resources)

        print("✅ Drift history saved to SQLite.")

        # ----------------------------
        # Generate HTML Report
        # ----------------------------

        report_path = report.generate_html(
            resources,
            checked=len(plan["resource_changes"])
        )

        print("✅ HTML report generated successfully!")
        print(f"📄 Report saved at: {report_path}")

        emailer.send_report(report_path, resources)
        print("📧 Email sent successfully!")

        database.close()

    # Exit Code 1 -> Error
    else:

        print("❌ Terraform Error")
        print(plan.stderr)

        database.close()


if __name__ == "__main__":
    main()