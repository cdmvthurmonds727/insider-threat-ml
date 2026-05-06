# 04 — Validation and Troubleshooting Guide

## Purpose

This guide validates the AWS, Terraform, PowerShell, Docker, and ML pipeline setup.

## Validate AWS CLI

```powershell
aws sts get-caller-identity
```

Expected:

```json
{
  "UserId": "...",
  "Account": "...",
  "Arn": "..."
}
```

## Validate S3 Bucket

```powershell
aws s3 ls
```

Check specific bucket:

```powershell
aws s3 ls s3://YOUR_BUCKET_NAME
```

## Validate CloudTrail Status

```powershell
aws cloudtrail describe-trails
```

Check logging:

```powershell
aws cloudtrail get-trail-status --name insider-trail
```

Expected:

```json
"IsLogging": true
```

## Validate CloudTrail Delivery to S3

```powershell
aws s3 ls s3://YOUR_BUCKET_NAME/AWSLogs/ --recursive
```

If empty, generate activity:

```powershell
aws sts get-caller-identity
aws ec2 describe-regions
aws iam list-users
```

Wait several minutes, then check again.

## Validate Terraform

```powershell
terraform fmt
terraform validate
terraform plan
```

If deployed:

```powershell
terraform output
```

## Validate EC2

```powershell
aws ec2 describe-instances `
  --filters "Name=tag:Name,Values=insider-threat-ml-engine" `
  --query "Reservations[*].Instances[*].[InstanceId,State.Name,PublicIpAddress]" `
  --output table
```

## Validate SSH

```powershell
ssh -i .\insider-threat-key ec2-user@EC2_PUBLIC_IP
```

## Validate Docker Locally

```powershell
docker version
docker run hello-world
```

## Validate Docker Project Build

```powershell
docker build -t insider-threat-ml:latest .
```

## Validate Docker Project Run

```powershell
docker run --rm `
  -v ${PWD}/data:/app/data `
  -v ${PWD}/outputs:/app/outputs `
  insider-threat-ml:latest
```

## Validate Output Files

```powershell
dir outputs
```

Expected:

```text
scored_events.csv
anomaly_events.csv
model_summary.txt
```

## Common Errors and Fixes

### Error: `TrailNotFoundException`

Cause: The CloudTrail trail was not created successfully.

Fix:

```powershell
aws cloudtrail describe-trails
```

If missing, recreate trail and then start logging.

---

### Error: `InsufficientS3BucketPolicyException`

Cause: CloudTrail does not have permission to write to S3.

Fix:

1. Confirm account ID.
2. Confirm bucket name.
3. Reapply CloudTrail bucket policy.
4. Retry trail creation.

---

### Error: PowerShell `Access denied` writing JSON file

Cause: You are writing in `C:\Windows\System32`.

Fix:

```powershell
cd $env:USERPROFILE\Downloads
```

---

### Error: PowerShell does not recognize `--bucket`

Cause: Bash line continuation slash was used.

Wrong:

```powershell
aws s3api put-bucket-encryption \
```

Correct:

```powershell
aws s3api put-bucket-encryption `
```

---

### Error: Terraform provider checksum mismatch

Fix:

```powershell
Remove-Item -Recurse -Force .terraform
Remove-Item -Force .terraform.lock.hcl
terraform init
```

---

### Error: S3 bucket already exists

Cause: S3 names are globally unique.

Fix: Change bucket name or project prefix.

---

### Error: SSH timeout

Check:

- EC2 has public IP
- Security group allows your current public IP
- Instance is running
- Correct private key is used

---

### Error: Docker build fails

Rebuild with no cache:

```powershell
docker build --no-cache -t insider-threat-ml:latest .
```

---

### Error: Docker output folder is empty

Check volume mounts:

```powershell
docker run --rm `
  -v ${PWD}/outputs:/app/outputs `
  insider-threat-ml:latest `
  ls -la /app/outputs
```

---

## Final Validation Checklist

- [ ] AWS CLI authenticated
- [ ] S3 bucket created
- [ ] S3 encryption enabled
- [ ] Public access blocked
- [ ] CloudTrail bucket policy applied
- [ ] CloudTrail created
- [ ] CloudTrail logging enabled
- [ ] CloudTrail logs delivered to S3
- [ ] Terraform validates successfully
- [ ] EC2 instance deployed
- [ ] Docker builds successfully
- [ ] ML container runs successfully
- [ ] Output CSV files are created
- [ ] README and documentation updated
