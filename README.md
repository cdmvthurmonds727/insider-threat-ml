#!/usr/bin/env python3
"""Train Isolation Forest on engineered features and export scored results."""

from __future__ import annotations

import argparse
from pathlib import Path
import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest


def severity_score(row: pd.Series) -> int:
    score = 0
    score += int(min(row.get("api_call_count", 0), 40) * 1.2)
    score += int(row.get("failed_login_count", 0) * 8)
    score += int(row.get("privileged_action_count", 0) * 12)
    score += int(row.get("iam_change_count", 0) * 15)
    score += int(row.get("off_hours", 0) * 10)
    score += int(row.get("unique_source_ips", 0) * 4)
    return min(score, 100)


def severity_label(score: int) -> str:
    if score >= 80:
        return "Critical"
    if score >= 60:
        return "High"
    if score >= 35:
        return "Medium"
    return "Low"


def main() -> None:
    parser = argparse.ArgumentParser(description="Train and score Isolation Forest model.")
    parser.add_argument("--input", required=True, help="Feature CSV.")
    parser.add_argument("--output", required=True, help="Scored CSV output.")
    parser.add_argument("--model", default="models/isolation_forest.joblib", help="Model output path.")
    parser.add_argument("--contamination", type=float, default=0.08, help="Expected anomaly ratio.")
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    drop_cols = ["event_time", "user", "username", "source", "eventName"]
    features = df.drop(columns=[c for c in drop_cols if c in df.columns], errors="ignore")
    features = features.select_dtypes(include=["int64", "float64", "int32", "float32"])

    model = IsolationForest(n_estimators=150, contamination=args.contamination, random_state=42)
    model.fit(features)

    df["prediction"] = model.predict(features)
    df["predicted_threat"] = (df["prediction"] == -1).astype(int)
    df["anomaly_score"] = -model.decision_function(features)
    df["severity_score"] = df.apply(severity_score, axis=1)
    df["severity"] = df["severity_score"].apply(severity_label)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.model).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False)
    joblib.dump(model, args.model)
    print(f"Saved scored results to {args.output}")
    print(f"Saved model to {args.model}")


if __name__ == "__main__":
    main()
