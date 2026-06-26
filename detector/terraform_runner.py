from pathlib import Path
import subprocess


class TerraformRunner:

    def __init__(self):
        self.terraform_dir = (
            Path(__file__).resolve().parent.parent / "terraform"
        )

    def run(self, command):

        return subprocess.run(
            command,
            cwd=self.terraform_dir,
            capture_output=True,
            text=True
        )

    def init(self):
        return self.run(["terraform", "init"])

    def plan(self):

        return self.run([
            "terraform",
            "plan",
            "-detailed-exitcode",
            "-out=tfplan"
        ])

    def show(self):

        return self.run([
            "terraform",
            "show",
            "-json",
            "tfplan"
        ])