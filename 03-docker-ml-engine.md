# 03 — Build and Run the ML Engine Using Docker

## Purpose

This guide explains how to containerize and run the Insider Threat ML pipeline using Docker.

The Docker container runs the Python-based insider threat detection engine that processes CloudTrail-style data, engineers features, trains an Isolation Forest model, and exports anomaly results.

## Prerequisites

Install:

- Docker Desktop on Windows, or Docker Engine on Linux
- Git
- Python project files

Verify:

```powershell
docker --version
docker compose version
```

## Recommended Project Structure

```text
insider-threat-ml/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
├── src/
│   ├── parse_cloudtrail.py
│   ├── feature_engineer_cloudtrail.py
│   └── train_iforest.py
├── data/
│   ├── raw/
│   └── processed/
├── models/
├── outputs/
└── docs/
```

## Step 1 — Create `requirements.txt`

```text
pandas
numpy
scikit-learn
matplotlib
boto3
joblib
```

## Step 2 — Create `Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    git \
    curl \
    jq \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p data/raw data/processed models outputs

CMD ["python", "src/train_iforest.py"]
```

## Step 3 — Create `docker-compose.yml`

```yaml
services:
  insider-threat-ml:
    build: .
    container_name: insider-threat-ml
    volumes:
      - ./data:/app/data
      - ./models:/app/models
      - ./outputs:/app/outputs
    environment:
      - AWS_DEFAULT_REGION=us-east-1
    command: python src/train_iforest.py
```

## Step 4 — Build Docker Image

From the project root:

```powershell
docker build -t insider-threat-ml:latest .
```

## Step 5 — Run the Container

```powershell
docker run --rm `
  -v ${PWD}/data:/app/data `
  -v ${PWD}/models:/app/models `
  -v ${PWD}/outputs:/app/outputs `
  insider-threat-ml:latest
```

## Step 6 — Run with Docker Compose

```powershell
docker compose up --build
```

## Step 7 — Check Outputs

After running, check:

```powershell
dir outputs
```

Expected files may include:

```text
scored_events.csv
anomaly_events.csv
model_summary.txt
anomaly_score_distribution.png
```

## Step 8 — Run Parser Script Manually

```powershell
docker run --rm `
  -v ${PWD}/data:/app/data `
  -v ${PWD}/outputs:/app/outputs `
  insider-threat-ml:latest `
  python src/parse_cloudtrail.py
```

## Step 9 — Run Feature Engineering Manually

```powershell
docker run --rm `
  -v ${PWD}/data:/app/data `
  -v ${PWD}/outputs:/app/outputs `
  insider-threat-ml:latest `
  python src/feature_engineer_cloudtrail.py
```

## Step 10 — Run Model Training Manually

```powershell
docker run --rm `
  -v ${PWD}/data:/app/data `
  -v ${PWD}/models:/app/models `
  -v ${PWD}/outputs:/app/outputs `
  insider-threat-ml:latest `
  python src/train_iforest.py
```

## Step 11 — Pass AWS Credentials into Docker

Only do this for lab use. Avoid hardcoding credentials.

```powershell
docker run --rm `
  -e AWS_ACCESS_KEY_ID=$env:AWS_ACCESS_KEY_ID `
  -e AWS_SECRET_ACCESS_KEY=$env:AWS_SECRET_ACCESS_KEY `
  -e AWS_DEFAULT_REGION=us-east-1 `
  -v ${PWD}/data:/app/data `
  -v ${PWD}/outputs:/app/outputs `
  insider-threat-ml:latest
```

Better option: mount your AWS profile:

```powershell
docker run --rm `
  -v $env:USERPROFILE\.aws:/root/.aws:ro `
  -v ${PWD}/data:/app/data `
  -v ${PWD}/outputs:/app/outputs `
  insider-threat-ml:latest
```

## Step 12 — Run on EC2

SSH into EC2:

```powershell
ssh -i .\insider-threat-key ec2-user@EC2_PUBLIC_IP
```

Install Docker if not already installed:

```bash
sudo dnf update -y
sudo dnf install -y docker git
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker ec2-user
```

Log out and log back in.

Clone repo:

```bash
git clone https://github.com/YOUR_USERNAME/insider-threat-ml.git
cd insider-threat-ml
```

Build:

```bash
docker build -t insider-threat-ml:latest .
```

Run:

```bash
docker run --rm \
  -v $PWD/data:/app/data \
  -v $PWD/models:/app/models \
  -v $PWD/outputs:/app/outputs \
  insider-threat-ml:latest
```

## Step 13 — Clean Docker Resources

```powershell
docker ps -a
docker images
docker system prune
```

## Troubleshooting

### Docker Desktop not running

Start Docker Desktop, then retry:

```powershell
docker version
```

### Permission denied on Linux

Add user to Docker group:

```bash
sudo usermod -aG docker $USER
```

Log out and back in.

### Output files missing

Check that volume mounts are correct:

```powershell
docker run --rm -v ${PWD}/outputs:/app/outputs insider-threat-ml:latest ls -la /app/outputs
```

### Python module missing

Rebuild image:

```powershell
docker build --no-cache -t insider-threat-ml:latest .
```
