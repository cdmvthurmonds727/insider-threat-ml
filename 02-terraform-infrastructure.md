# 02 — Create AWS Infrastructure Using Terraform

## Purpose

This guide creates the AWS infrastructure for the Insider Threat ML project using Terraform.

## Prerequisites

Install:

- Terraform
- AWS CLI
- Git
- PowerShell

Verify:

```powershell
terraform version
aws sts get-caller-identity
```

## Step 1 — Create Terraform Project Folder

```powershell
mkdir insider-threat-terraform
cd insider-threat-terraform
```

Create files:

```powershell
New-Item main.tf
New-Item variables.tf
New-Item outputs.tf
New-Item versions.tf
New-Item terraform.tfvars
```

## Step 2 — Create `versions.tf`

```hcl
terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}
```

## Step 3 — Create `variables.tf`

```hcl
variable "aws_region" {
  description = "AWS region for the lab"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name prefix"
  type        = string
  default     = "insider-threat-ml"
}

variable "instance_type" {
  description = "EC2 instance type for ML engine"
  type        = string
  default     = "t3.micro"
}

variable "ssh_cidr" {
  description = "CIDR allowed to SSH into EC2"
  type        = string
}
```

## Step 4 — Create `terraform.tfvars`

Replace the CIDR with your public IP.

```hcl
aws_region    = "us-east-1"
project_name  = "insider-threat-ml"
instance_type = "t3.micro"
ssh_cidr      = "YOUR_PUBLIC_IP/32"
```

Find your IP in PowerShell:

```powershell
Invoke-RestMethod https://checkip.amazonaws.com
```

## Step 5 — Create `main.tf`

```hcl
data "aws_caller_identity" "current" {}

data "aws_vpc" "default" {
  default = true
}

data "aws_ami" "amazon_linux_2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-2023*-x86_64"]
  }

  filter {
    name   = "state"
    values = ["available"]
  }
}

resource "aws_s3_bucket" "cloudtrail_logs" {
  bucket = "${var.project_name}-logs-${data.aws_caller_identity.current.account_id}-${var.aws_region}"

  tags = {
    Name    = "${var.project_name}-cloudtrail-logs"
    Project = var.project_name
  }
}

resource "aws_s3_bucket_public_access_block" "cloudtrail_logs" {
  bucket = aws_s3_bucket.cloudtrail_logs.id

  block_public_acls       = true
  ignore_public_acls      = true
  block_public_policy     = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "cloudtrail_logs" {
  bucket = aws_s3_bucket.cloudtrail_logs.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "cloudtrail_logs" {
  bucket = aws_s3_bucket.cloudtrail_logs.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

data "aws_iam_policy_document" "cloudtrail_bucket_policy" {
  statement {
    sid = "AWSCloudTrailAclCheck"

    principals {
      type        = "Service"
      identifiers = ["cloudtrail.amazonaws.com"]
    }

    actions   = ["s3:GetBucketAcl"]
    resources = [aws_s3_bucket.cloudtrail_logs.arn]
  }

  statement {
    sid = "AWSCloudTrailWrite"

    principals {
      type        = "Service"
      identifiers = ["cloudtrail.amazonaws.com"]
    }

    actions = ["s3:PutObject"]

    resources = [
      "${aws_s3_bucket.cloudtrail_logs.arn}/AWSLogs/${data.aws_caller_identity.current.account_id}/*"
    ]

    condition {
      test     = "StringEquals"
      variable = "s3:x-amz-acl"
      values   = ["bucket-owner-full-control"]
    }
  }
}

resource "aws_s3_bucket_policy" "cloudtrail_logs" {
  bucket = aws_s3_bucket.cloudtrail_logs.id
  policy = data.aws_iam_policy_document.cloudtrail_bucket_policy.json
}

resource "aws_cloudtrail" "main" {
  name                          = "${var.project_name}-trail"
  s3_bucket_name                = aws_s3_bucket.cloudtrail_logs.id
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_logging                = true

  depends_on = [aws_s3_bucket_policy.cloudtrail_logs]
}

resource "aws_iam_role" "ec2_role" {
  name = "${var.project_name}-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_policy" "ec2_s3_read_policy" {
  name = "${var.project_name}-s3-read-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket"
        ]
        Resource = aws_s3_bucket.cloudtrail_logs.arn
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject"
        ]
        Resource = "${aws_s3_bucket.cloudtrail_logs.arn}/*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ec2_s3_read_attach" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = aws_iam_policy.ec2_s3_read_policy.arn
}

resource "aws_iam_instance_profile" "ec2_profile" {
  name = "${var.project_name}-ec2-profile"
  role = aws_iam_role.ec2_role.name
}

resource "aws_security_group" "ml_engine" {
  name        = "${var.project_name}-sg"
  description = "Allow SSH access to ML engine"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "SSH from approved IP"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.ssh_cidr]
  }

  egress {
    description = "Allow outbound internet access"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name    = "${var.project_name}-sg"
    Project = var.project_name
  }
}

resource "aws_key_pair" "ml_key" {
  key_name   = "${var.project_name}-key"
  public_key = file("${path.module}/insider-threat-key.pub")
}

resource "aws_instance" "ml_engine" {
  ami                    = data.aws_ami.amazon_linux_2023.id
  instance_type          = var.instance_type
  key_name               = aws_key_pair.ml_key.key_name
  vpc_security_group_ids = [aws_security_group.ml_engine.id]
  iam_instance_profile   = aws_iam_instance_profile.ec2_profile.name

  user_data = <<-EOF
              #!/bin/bash
              dnf update -y
              dnf install -y docker git python3 python3-pip
              systemctl enable docker
              systemctl start docker
              usermod -aG docker ec2-user
              mkdir -p /opt/insider-threat-ml/{data,models,outputs,scripts}
              echo "EC2 ML Engine Ready" > /opt/insider-threat-ml/status.txt
              EOF

  tags = {
    Name    = "${var.project_name}-engine"
    Project = var.project_name
  }
}
```

## Step 6 — Create `outputs.tf`

```hcl
output "cloudtrail_bucket_name" {
  value = aws_s3_bucket.cloudtrail_logs.id
}

output "cloudtrail_name" {
  value = aws_cloudtrail.main.name
}

output "ec2_public_ip" {
  value = aws_instance.ml_engine.public_ip
}

output "ec2_instance_id" {
  value = aws_instance.ml_engine.id
}
```

## Step 7 — Create SSH Key Pair

From PowerShell:

```powershell
ssh-keygen -t ed25519 -f .\insider-threat-key -N '""'
```

This creates:

```text
insider-threat-key
insider-threat-key.pub
```

Terraform uses the `.pub` file.

## Step 8 — Initialize Terraform

```powershell
terraform init
```

## Step 9 — Format and Validate

```powershell
terraform fmt
terraform validate
```

## Step 10 — Review the Plan

```powershell
terraform plan
```

## Step 11 — Apply Infrastructure

```powershell
terraform apply
```

Type:

```text
yes
```

## Step 12 — View Outputs

```powershell
terraform output
```

## Step 13 — SSH to EC2

```powershell
$PUBLIC_IP=$(terraform output -raw ec2_public_ip)
ssh -i .\insider-threat-key ec2-user@$PUBLIC_IP
```

## Step 14 — Validate CloudTrail

```powershell
$BUCKET=$(terraform output -raw cloudtrail_bucket_name)
aws s3 ls s3://$BUCKET/AWSLogs/ --recursive
```

## Step 15 — Destroy Lab When Finished

```powershell
terraform destroy
```

Type:

```text
yes
```

## Troubleshooting

### Provider checksum or init issues

```powershell
Remove-Item -Recurse -Force .terraform
Remove-Item -Force .terraform.lock.hcl
terraform init
```

### SSH does not work

Check:

- Your public IP is correct in `terraform.tfvars`
- Security group allows port 22
- EC2 instance has a public IP
- You are using the private key, not the `.pub` key

### S3 bucket already exists

S3 bucket names are globally unique. Change `project_name` or include your initials.
