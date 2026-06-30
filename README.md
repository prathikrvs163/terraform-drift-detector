# Terraform Drift Detector

A Python-based tool that detects **Terraform drift** by comparing your Terraform configuration with live Azure infrastructure. It generates HTML reports, stores drift history, sends email notifications, and automates execution using GitHub Actions.

## Features

- 🔍 Detects Terraform drift
- ☁️ Supports Microsoft Azure
- 📄 Generates HTML drift reports
- 🗄️ Stores drift history in SQLite
- 📧 Sends email notifications
- ⚙️ Automated with GitHub Actions
- 📦 Uploads reports as GitHub Action artifacts

## Tech Stack

- Python
- Terraform
- Microsoft Azure
- SQLite
- GitHub Actions
- HTML & CSS

## Project Structure

```text
terraform-drift-detector/
├── detector/
├── terraform/
├── templates/
├── static/
├── .github/workflows/
├── reports/
├── requirements.txt
└── README.md
```

## Workflow

```text
Terraform Plan
      │
      ▼
Detect Drift
      │
      ▼
Parse JSON
      │
      ├── HTML Report
      ├── SQLite History
      ├── Email Notification
      └── GitHub Artifact
```

## GitHub Actions

The workflow automatically:

- Runs Terraform drift detection
- Authenticates to Azure
- Generates an HTML report
- Uploads the report as an artifact

It also supports manual execution using **workflow_dispatch**.

## Run Locally

```bash
git clone https://github.com/prathikrvs163/terraform-drift-detector.git

cd terraform-drift-detector

pip install -r requirements.txt

python -m detector.detector
```

## Future Improvements

- AWS & GCP support
- Slack / Microsoft Teams notifications
- Web dashboard
- Drift trend analytics

## Author

**Sriram Prathik Rachakonda**

- GitHub: https://github.com/prathikrvs163
- LinkedIn: https://linkedin.com/in/rvsp16