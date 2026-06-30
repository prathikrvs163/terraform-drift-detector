## Automation

The project uses GitHub Actions to automatically:

- Run Terraform drift detection every day
- Authenticate to Azure
- Generate an HTML report
- Upload the report as a GitHub Artifact
- Send email notifications when drift is detected