# Security Model

## Detection Approach

The project uses unsupervised anomaly detection. This is useful when labeled insider threat data is limited or unavailable.

## Feature Categories

| Category | Example Features | Security Meaning |
|---|---|---|
| Authentication | failed_login_count | Brute force, credential misuse, suspicious access |
| Privilege | privileged_action_count, iam_change_count | Permission escalation or unauthorized IAM changes |
| Activity Volume | api_call_count, unique_services | Unusual cloud usage patterns |
| Data Access | s3_access_count, data_transfer_gb | Possible data staging or exfiltration |
| Time Context | off_hours | Activity outside normal working hours |

## Severity Scoring

The severity score is a rule-based layer added after model scoring. It gives analysts a readable risk level based on security-relevant indicators.

| Score Range | Label |
|---:|---|
| 0-34 | Low |
| 35-59 | Medium |
| 60-79 | High |
| 80-100 | Critical |

## Limitations

- Synthetic data does not fully represent production behavior.
- Unsupervised models require tuning to reduce false positives.
- Human analyst review is still required.
- CloudTrail coverage depends on correct AWS logging configuration.
