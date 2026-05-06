# AWS Infrastructure Setup Guide

This folder contains step-by-step documentation for creating the AWS infrastructure used in the Insider Threat ML project.

## Documents

| File | Purpose |
|---|---|
| `01-powershell-aws-cli-setup.md` | Create AWS resources manually with PowerShell and AWS CLI |
| `02-terraform-infrastructure.md` | Create the same infrastructure using Terraform |
| `03-docker-ml-engine.md` | Build and run the ML engine with Docker |
| `04-validation-and-troubleshooting.md` | Validate CloudTrail, S3, EC2, Docker, and Terraform |

## Target Architecture

The lab architecture includes:

- AWS CLI workstation using PowerShell
- S3 bucket for CloudTrail logs
- CloudTrail trail for AWS API activity logging
- IAM permissions for CloudTrail access
- EC2 instance for the ML processing engine
- Docker container for Python-based insider threat analysis
- Local or EC2-based execution of the ML pipeline

## Recommended Order

1. Complete AWS CLI setup with PowerShell.
2. Create or verify the S3 logging bucket.
3. Deploy infrastructure with Terraform.
4. Build the Docker ML engine.
5. Validate CloudTrail logs and ML output.
