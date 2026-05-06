# Project Overview

## Mission

This project demonstrates how cloud telemetry can be transformed into behavioral security features and analyzed with machine learning to identify potential insider threat activity.

## Problem Statement

Insider threats are difficult to detect because activity may originate from legitimate accounts. Static rules alone may miss suspicious behavior when users have valid credentials. This project uses anomaly detection to identify unusual activity patterns that may require investigation.

## Dataset

The repository includes synthetic sample data for safe public demonstration. The same pipeline can process AWS CloudTrail JSON or JSON.GZ logs exported from an AWS environment.

## Pipeline

1. Collect CloudTrail logs
2. Parse raw JSON records into CSV
3. Engineer behavioral features by user and time window
4. Train an Isolation Forest model
5. Generate anomaly predictions and severity scores
6. Export ranked findings for analyst review

## Security Use Case

Example findings may include:

- Privileged IAM changes outside normal hours
- Excessive failed login attempts
- Unusual S3 access activity
- Attempts to stop or modify logging
- Abnormal API call volume compared with normal behavior
