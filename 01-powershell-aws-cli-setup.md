# 01 — Create AWS Infrastructure Using PowerShell and AWS CLI

## Purpose

This guide shows how to create the AWS infrastructure for the Insider Threat ML project using PowerShell and the AWS CLI.

## Prerequisites

Install the following on Windows:

- AWS CLI v2
- PowerShell 7 or Windows PowerShell
- Git
- Terraform
- Docker Desktop

Verify tools:

```powershell
aws --version
git --version
terraform version
docker --version
```

## Step 1 — Configure AWS CLI

Run:

```powershell
aws configure
```

Enter:

```text
AWS Access Key ID
AWS Secret Access Key
Default region name: us-east-1
Default output format: json
```

Verify identity:

```powershell
aws sts get-caller-identity
```

## Step 2 — Set Environment Variables

Update the bucket name so it is globally unique.

```powershell
$REGION="us-east-1"
$ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
$BUCKET="insider-threat-lab-$ACCOUNT_ID-$REGION"
$TRAIL_NAME="insider-trail"
```

Check values:

```powershell
Write-Host "Account ID: $ACCOUNT_ID"
Write-Host "Bucket: $BUCKET"
Write-Host "Region: $REGION"
```

## Step 3 — Create S3 Bucket for CloudTrail Logs

For `us-east-1`:

```powershell
aws s3api create-bucket `
  --bucket $BUCKET `
  --region $REGION
```

Enable encryption:

```powershell
@"
{
  "Rules": [
    {
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }
  ]
}
"@ | Out-File -Encoding ascii "$env:USERPROFILE\Downloads\s3-encryption.json"

aws s3api put-bucket-encryption `
  --bucket $BUCKET `
  --server-side-encryption-configuration file://$env:USERPROFILE\Downloads\s3-encryption.json
```

Block public access:

```powershell
aws s3api put-public-access-block `
  --bucket $BUCKET `
  --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
```

Enable versioning:

```powershell
aws s3api put-bucket-versioning `
  --bucket $BUCKET `
  --versioning-configuration Status=Enabled
```

## Step 4 — Create CloudTrail Bucket Policy

Create the policy file in Downloads, not `C:\Windows\System32`.

```powershell
$POLICY_PATH="$env:USERPROFILE\Downloads\cloudtrail-bucket-policy.json"

@"
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AWSCloudTrailAclCheck",
      "Effect": "Allow",
      "Principal": {
        "Service": "cloudtrail.amazonaws.com"
      },
      "Action": "s3:GetBucketAcl",
      "Resource": "arn:aws:s3:::$BUCKET"
    },
    {
      "Sid": "AWSCloudTrailWrite",
      "Effect": "Allow",
      "Principal": {
        "Service": "cloudtrail.amazonaws.com"
      },
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::$BUCKET/AWSLogs/$ACCOUNT_ID/*",
      "Condition": {
        "StringEquals": {
          "s3:x-amz-acl": "bucket-owner-full-control"
        }
      }
    }
  ]
}
"@ | Out-File -Encoding ascii $POLICY_PATH

aws s3api put-bucket-policy `
  --bucket $BUCKET `
  --policy file://$POLICY_PATH
```

## Step 5 — Create CloudTrail

```powershell
aws cloudtrail create-trail `
  --name $TRAIL_NAME `
  --s3-bucket-name $BUCKET `
  --is-multi-region-trail
```

Start logging:

```powershell
aws cloudtrail start-logging `
  --name $TRAIL_NAME
```

Verify:

```powershell
aws cloudtrail get-trail-status `
  --name $TRAIL_NAME
```

You should see:

```json
"IsLogging": true
```

## Step 6 — Generate Test AWS Activity

Run several harmless commands:

```powershell
aws sts get-caller-identity
aws ec2 describe-regions
aws iam list-users
aws s3 ls
```

CloudTrail delivery may take several minutes.

## Step 7 — Verify CloudTrail Logs in S3

```powershell
aws s3 ls s3://$BUCKET/AWSLogs/$ACCOUNT_ID/CloudTrail/ --recursive
```

## Step 8 — Create EC2 Key Pair

```powershell
aws ec2 create-key-pair `
  --key-name insider-threat-key `
  --query "KeyMaterial" `
  --output text | Out-File -Encoding ascii "$env:USERPROFILE\Downloads\insider-threat-key.pem"
```

## Step 9 — Create Security Group

Get default VPC:

```powershell
$VPC_ID=$(aws ec2 describe-vpcs `
  --filters Name=isDefault,Values=true `
  --query "Vpcs[0].VpcId" `
  --output text)
```

Create security group:

```powershell
$SG_ID=$(aws ec2 create-security-group `
  --group-name insider-threat-ml-sg `
  --description "Security group for Insider Threat ML EC2" `
  --vpc-id $VPC_ID `
  --query "GroupId" `
  --output text)
```

Allow SSH from your IP only:

```powershell
$MY_IP=$(Invoke-RestMethod https://checkip.amazonaws.com)

aws ec2 authorize-security-group-ingress `
  --group-id $SG_ID `
  --protocol tcp `
  --port 22 `
  --cidr "$MY_IP/32"
```

## Step 10 — Launch EC2 ML Engine

Find latest Amazon Linux 2023 AMI:

```powershell
$AMI_ID=$(aws ec2 describe-images `
  --owners amazon `
  --filters "Name=name,Values=al2023-ami-2023*-x86_64" "Name=state,Values=available" `
  --query "sort_by(Images, &CreationDate)[-1].ImageId" `
  --output text)
```

Launch instance:

```powershell
$INSTANCE_ID=$(aws ec2 run-instances `
  --image-id $AMI_ID `
  --instance-type t3.micro `
  --key-name insider-threat-key `
  --security-group-ids $SG_ID `
  --iam-instance-profile Name=insider-threat-ec2-profile `
  --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=insider-threat-ml-engine}]" `
  --query "Instances[0].InstanceId" `
  --output text)
```

Check status:

```powershell
aws ec2 describe-instances `
  --instance-ids $INSTANCE_ID `
  --query "Reservations[0].Instances[0].State.Name"
```

## Step 11 — Connect to EC2

Get public IP:

```powershell
$PUBLIC_IP=$(aws ec2 describe-instances `
  --instance-ids $INSTANCE_ID `
  --query "Reservations[0].Instances[0].PublicIpAddress" `
  --output text)

Write-Host $PUBLIC_IP
```

SSH:

```powershell
ssh -i "$env:USERPROFILE\Downloads\insider-threat-key.pem" ec2-user@$PUBLIC_IP
```

## Common PowerShell Fixes

### Problem: Access denied writing JSON file

Do not write files from `C:\Windows\System32`.

Use:

```powershell
cd $env:USERPROFILE\Downloads
```

### Problem: Bash slash used in PowerShell

Wrong:

```powershell
aws s3api put-bucket-encryption \
```

Correct:

```powershell
aws s3api put-bucket-encryption `
```
