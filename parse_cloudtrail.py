# Appendix Descriptions

## Appendix A — Data Processing Script

`parse_cloudtrail.py` converts AWS CloudTrail JSON or compressed JSON.GZ files into structured CSV data. The script extracts timestamps, event names, usernames, source IP addresses, user agents, AWS regions, and error fields. This prepares raw AWS audit data for feature engineering.

## Appendix B — Feature Engineering Script

`feature_engineer_cloudtrail.py` groups cloud activity by user and hourly time window. It creates numerical behavioral features such as API call count, failed activity count, privileged action count, S3 access count, IAM change count, unique AWS services, unique source IPs, and off-hours activity.

## Appendix C — Machine Learning Model

`train_iforest.py` trains an Isolation Forest model using engineered behavior features. Isolation Forest is an unsupervised anomaly detection algorithm that isolates unusual records based on how different they are from the rest of the dataset.

## Appendix D — Severity Scoring Upgrade

The severity score ranks suspicious events from 0 to 100. The score increases when a record includes failed activity, privileged actions, IAM changes, off-hours behavior, unusual source IP activity, or high API volume.

## Appendix E — Sample Output Data

The output files include `scored.csv`, `insider_threat_results.csv`, and `anomaly_events.csv`. These files support reporting by showing normal events, anomalous events, anomaly scores, severity scores, and severity labels.

## Appendix F — AWS Environment Setup

The project can be deployed on an AWS EC2 instance configured with Python, pip, virtual environments, AWS CLI, and common data science libraries. CloudTrail logs can be stored in S3 and copied into the project for analysis.
