#!/usr/bin/env python3
"""End-to-end insider threat anomaly detection proof of concept."""

from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

RANDOM_STATE = 42


def build_synthetic_dataset(rows: int = 300) -> pd.DataFrame:
    rng = np.random.default_rng(RANDOM_STATE)
    users = [f"user{i}" for i in range(1, 16)]
    sources = ["cloudtrail", "ssh", "iam", "ec2", "s3"]
    event_names = [
        "DescribeInstances", "ListBuckets", "GetObject", "ConsoleLogin",
        "AssumeRole", "CreateAccessKey", "AttachUserPolicy", "StopLogging"
    ]

    df = pd.DataFrame({
        "event_time": pd.date_range("2026-03-01", periods=rows, freq="h"),
        "user": rng.choice(users, rows),
        "source": rng.choice(sources, rows),
        "eventName": rng.choice(event_names, rows),
        "api_call_count": rng.poisson(4, rows),
        "failed_login_count": rng.poisson(0.25, rows),
        "privileged_action_count": rng.binomial(2, 0.08, rows),
        "s3_access_count": rng.poisson(2, rows),
        "iam_change_count": rng.binomial(2, 0.05, rows),
        "unique_services": rng.integers(1, 5, rows),
        "data_transfer_gb": rng.gamma(1.5, 0.25, rows).round(3),
    })

    df["off_hours"] = df["event_time"].dt.hour.isin(list(range(0, 6)) + list(range(20, 24))).astype(int)
    df["is_known_threat"] = 0

    threat_idx = rng.choice(df.index, size=max(10, rows // 12), replace=False)
    df.loc[threat_idx, "api_call_count"] += rng.integers(10, 35, len(threat_idx))
    df.loc[threat_idx, "failed_login_count"] += rng.integers(2, 8, len(threat_idx))
    df.loc[threat_idx, "privileged_action_count"] += rng.integers(2, 6, len(threat_idx))
    df.loc[threat_idx, "iam_change_count"] += rng.integers(1, 4, len(threat_idx))
    df.loc[threat_idx, "data_transfer_gb"] += rng.gamma(4, 1.2, len(threat_idx)).round(3)
    df.loc[threat_idx, "off_hours"] = 1
    df.loc[threat_idx, "is_known_threat"] = 1
    return df


def severity_score(row: pd.Series) -> int:
    score = 0
    score += int(min(row.get("api_call_count", 0), 40) * 1.2)
    score += int(row.get("failed_login_count", 0) * 8)
    score += int(row.get("privileged_action_count", 0) * 12)
    score += int(row.get("iam_change_count", 0) * 15)
    score += int(row.get("off_hours", 0) * 10)
    score += int(min(row.get("data_transfer_gb", 0), 25) * 3)
    return min(score, 100)


def severity_label(score: int) -> str:
    if score >= 80:
        return "Critical"
    if score >= 60:
        return "High"
    if score >= 35:
        return "Medium"
    return "Low"


def run_pipeline(input_csv: str | None, output_dir: str) -> None:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    if input_csv:
        print(f"[INFO] Loading dataset: {input_csv}")
        df = pd.read_csv(input_csv)
    else:
        print("[INFO] No CSV supplied. Using synthetic insider threat dataset.")
        df = build_synthetic_dataset()

    drop_cols = ["event_time", "user", "username", "source", "eventName", "is_known_threat"]
    features = df.drop(columns=[c for c in drop_cols if c in df.columns], errors="ignore")
    features = features.select_dtypes(include=["int64", "float64", "int32", "float32"])

    model = IsolationForest(n_estimators=150, contamination=0.08, random_state=RANDOM_STATE)
    model.fit(features)

    df["prediction"] = model.predict(features)
    df["predicted_threat"] = (df["prediction"] == -1).astype(int)
    df["anomaly_score"] = -model.decision_function(features)
    df["severity_score"] = df.apply(severity_score, axis=1)
    df["severity"] = df["severity_score"].apply(severity_label)

    results_file = out / "insider_threat_results.csv"
    anomalies_file = out / "anomaly_events.csv"
    df.to_csv(results_file, index=False)
    df[df["predicted_threat"] == 1].sort_values(
        ["severity_score", "anomaly_score"], ascending=False
    ).to_csv(anomalies_file, index=False)

    plt.figure(figsize=(9, 5))
    plt.hist(df["anomaly_score"], bins=30)
    plt.title("Anomaly Score Distribution")
    plt.xlabel("Anomaly Score")
    plt.ylabel("Event Count")
    plt.tight_layout()
    chart_file = out / "anomaly_score_distribution.png"
    plt.savefig(chart_file, dpi=160)

    print(f"[INFO] Saved results to {results_file}")
    print("\n================ INSIDER THREAT POC SUMMARY ================")
    print(f"Total events analyzed   : {len(df)}")
    print(f"Predicted normal events : {(df['predicted_threat'] == 0).sum()}")
    print(f"Predicted threat events : {(df['predicted_threat'] == 1).sum()}")

    if "is_known_threat" in df.columns:
        print("\nClassification Report:")
        print(classification_report(df["is_known_threat"], df["predicted_threat"], digits=4))

    print("============================================================")
    print("\n[INFO] Generated files:")
    print(f" - {results_file}")
    print(f" - {anomalies_file}")
    print(f" - {chart_file}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run insider threat anomaly detection POC.")
    parser.add_argument("--input", help="Optional input CSV file.")
    parser.add_argument("--output-dir", default="outputs", help="Output directory.")
    args = parser.parse_args()
    run_pipeline(args.input, args.output_dir)


if __name__ == "__main__":
    main()
