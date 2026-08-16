# ClaudeMark Environment Setup & Verification Script (Windows PowerShell)
$ErrorActionPreference = "Stop"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host " ClaudeMark v2.0 Windows Bootstrap" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# Locate Python
$PythonCmd = (Get-Command py -ErrorAction SilentlyContinue)
if (-not $PythonCmd) {
    $PythonCmd = (Get-Command python -ErrorAction SilentlyContinue)
}

if (-not $PythonCmd) {
    Write-Error "Python 3.10+ is required but not found in PATH."
    exit 1
}

$PyVer = & $PythonCmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
Write-Host "[+] Detected Python $PyVer" -ForegroundColor Green

# Create venv if needed
if (-not (Test-Path ".venv")) {
    Write-Host "[*] Creating virtual environment (.venv)..." -ForegroundColor Yellow
    & $PythonCmd -m venv .venv
}

# Activate
$ActivateScript = Join-Path ".venv" "Scripts" "Activate.ps1"
if (Test-Path $ActivateScript) {
    . $ActivateScript
}

# Install dependencies
Write-Host "[*] Installing dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt

# Run pytest
Write-Host "[*] Running verification test suite..." -ForegroundColor Yellow
python -m pytest tests/ -q

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host " ClaudeMark Environment Ready!" -ForegroundColor Green
Write-Host " Start server: python claudemark.py serve" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Cyan
