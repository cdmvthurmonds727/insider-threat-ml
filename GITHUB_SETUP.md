# GitHub Setup Instructions

## Create a New Repository

1. Go to GitHub.
2. Select **New repository**.
3. Name it `insider-threat-ml`.
4. Choose Public or Private.
5. Do not initialize with README if uploading this package as-is.

## Push from Your Computer

```bash
cd insider-threat-ml-github
git init
git add .
git commit -m "Initial insider threat ML project"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/insider-threat-ml.git
git push -u origin main
```

## Run Locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/insider_threat_poc.py
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts\insider_threat_poc.py
```
