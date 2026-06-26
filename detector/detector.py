from detector.terraform_runner import TerraformRunner
from detector.parser import TerraformPlanParser
from detector.report import ReportGenerator
import json


def main():

    runner = TerraformRunner()
    parser = TerraformPlanParser()
    report = ReportGenerator()

    print("Initializing Terraform...")

    init = runner.init()

    if init.returncode != 0:
        print(init.stderr)
        return

    print("Running Terraform Plan...")

    plan = runner.plan()

    # Exit Code 0 -> No Drift
    if plan.returncode == 0:
        print("✅ No drift detected.")
        return

    # Exit Code 2 -> Drift Found
    elif plan.returncode == 2:

        print("\n⚠ Drift detected!")

        json_plan = runner.show()

        plan = json.loads(json_plan.stdout)

        resources = []

        for resource in plan["resource_changes"]:

            action = resource["change"]["actions"][0]

            # Ignore unchanged resources
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

        # Still print to console for now
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

        # Generate HTML report
        report_path = report.generate_html(resources)

        print("\n✅ HTML report generated successfully!")
        print(f"📄 Report saved at: {report_path}")

    # Exit Code 1 -> Error
    else:
        print("❌ Terraform Error")
        print(plan.stderr)


if __name__ == "__main__":
    main()