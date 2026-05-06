# Runbook

## Local Demo

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/insider_threat_poc.py --output-dir outputs
```

## Expected Results

After successful execution, review:

```text
outputs/insider_threat_results.csv
outputs/anomaly_events.csv
outputs/anomaly_score_distribution.png
outputs/severity_distribution.png
```

## Troubleshooting

### ModuleNotFoundError

Install dependencies again:

```bash
pip install -r requirements.txt
```

### Empty outputs

Confirm the input CSV has numeric behavioral features. Identifier columns such as user, event_time, and source are removed before training.

### GitHub Actions failure

Run the same check locally:

```bash
python -m py_compile scripts/*.py
python scripts/insider_threat_poc.py --output-dir outputs
```
