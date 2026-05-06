#!/usr/bin/env python3
"""Create behavioral features from parsed CloudTrail CSV data."""

from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd

SENSITIVE_ACTIONS = [
    "CreateAccessKey", "AttachUserPolicy", "PutUserPolicy", "AssumeRole",
    "StopLogging", "DeleteTrail", "AuthorizeSecurityGroupIngress",
    "PutBucketPolicy", "DeleteBucketPolicy"
]


def engineer_features(input_csv: str) -> pd.DataFrame:
    df = pd.read_csv(input_csv)
    df["event_time"] = pd.to_datetime(df["event_time"], errors="coerce")
    df["hour_bucket"] = df["event_time"].dt.floor("h")
    df["username"] = df["username"].fillna("unknown")
    df["eventName"] = df["eventName"].fillna("unknown")
    df["event_source"] = df["event_source"].fillna("unknown")
    df["failed"] = df["errorCode"].notna().astype(int)
    df["off_hours"] = df["event_time"].dt.hour.isin(list(range(0, 6)) + list(range(20, 24))).astype(int)
    df["privileged_action"] = df["eventName"].isin(SENSITIVE_ACTIONS).astype(int)
    df["s3_access"] = df["event_source"].str.contains("s3", case=False, na=False).astype(int)
    df["iam_change"] = df["event_source"].str.contains("iam", case=False, na=False).astype(int)

    features = df.groupby(["hour_bucket", "username"], dropna=False).agg(
        api_call_count=("eventName", "count"),
        failed_login_count=("failed", "sum"),
        privileged_action_count=("privileged_action", "sum"),
        s3_access_count=("s3_access", "sum"),
        iam_change_count=("iam_change", "sum"),
        unique_services=("event_source", "nunique"),
        unique_source_ips=("sourceIPAddress", "nunique"),
        off_hours=("off_hours", "max"),
    ).reset_index()

    features = features.rename(columns={"hour_bucket": "event_time", "username": "user"})
    return features


def main() -> None:
    parser = argparse.ArgumentParser(description="Engineer behavioral features from parsed CloudTrail CSV.")
    parser.add_argument("--input", required=True, help="Parsed CloudTrail CSV.")
    parser.add_argument("--output", required=True, help="Output feature CSV.")
    args = parser.parse_args()

    features = engineer_features(args.input)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    features.to_csv(args.output, index=False)
    print(f"Wrote {len(features)} feature rows to {args.output}")


if __name__ == "__main__":
    main()
