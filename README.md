# Behavioral AI for Insider Threat Detection in AWS Cloud Systems

This project is a GitHub-ready proof of concept for detecting potential insider threat behavior using AWS activity logs and machine learning. It supports synthetic sample data for demonstration and can be adapted to AWS CloudTrail logs exported from S3.

## Project Goals

- Parse AWS CloudTrail-style activity logs.
- Engineer behavioral features from cloud events.
- Train an Isolation Forest anomaly detection model.
- Score events and rank anomalies by severity.
- Export results, figures, and CSV files for reports or presentations.

## Repository Structure

```text
.
├── scripts/
│   ├── parse_cloudtrail.py
│   ├── feature_engineer_cloudtrail.py
│   ├── train_iforest.py
│   ├── train_iforest_real.py
│   └── insider_threat_poc.py
├── data/
│   └── sample/
│       └── sample_events.csv
├── outputs/
│   └── .gitkeep
├── models/
│   └── .gitkeep
├── docs/
│   ├── Appendix_Descriptions.md
│   └── references_apa.md
├── diagrams/
│   └── aws_architecture.mmd
├── requirements.txt
├── .gitignore
└── LICENSE
```

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/insider_threat_poc.py
```

Results are written to the `outputs/` folder.

## Run the Full Pipeline

### 1. Parse CloudTrail JSON

```bash
python scripts/parse_cloudtrail.py --input data/cloudtrail.json --output outputs/parsed_cloudtrail.csv
```

### 2. Engineer Features

```bash
python scripts/feature_engineer_cloudtrail.py --input outputs/parsed_cloudtrail.csv --output outputs/features.csv
```

### 3. Train and Score with Isolation Forest

```bash
python scripts/train_iforest.py --input outputs/features.csv --output outputs/scored.csv --model models/isolation_forest.joblib
```

### 4. Run End-to-End Demo

```bash
python scripts/insider_threat_poc.py
```

## Severity Scoring

The project includes a simple severity score to help prioritize anomalies:

- Higher anomaly score = more suspicious behavior.
- Off-hours activity adds risk.
- Failed login activity adds risk.
- Privileged or sensitive API activity adds risk.
- High activity volume adds risk.

Severity labels:

- Low
- Medium
- High
- Critical

## Example Use Case

A security analyst can use this project to identify unusual IAM, EC2, S3, or CloudTrail activity patterns that may indicate compromised credentials, privilege misuse, or insider threat behavior.

## Academic Context

This project was designed for an independent study / final paper on Behavioral AI for Insider Threat Detection in DoD or AWS cloud systems. It can support appendices, screenshots, architecture diagrams, and model output tables in APA or IEEE reports.

## Disclaimer

This is an educational proof of concept. It is not a production security monitoring platform. For production environments, integrate with AWS CloudTrail, GuardDuty, Security Hub, SIEM tooling, least-privilege IAM, alerting, and incident response workflows.
