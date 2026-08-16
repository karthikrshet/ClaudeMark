# Bootstrap setup for external reverse-SynthID scoring harness (Windows PowerShell)
param (
    [string]$Dir = (Join-Path $HOME "reverse-SynthID")
)
$ErrorActionPreference = "Stop"

Write-Host "[*] Setting up reverse-SynthID at $Dir..." -ForegroundColor Yellow
if (-not (Test-Path $Dir)) {
    git clone https://github.com/aloshdenny/reverse-SynthID.git $Dir
}

Set-Location $Dir
python -m venv .venv
$Activate = Join-Path ".venv" "Scripts" "Activate.ps1"
if (Test-Path $Activate) { . $Activate }
python -m pip install --upgrade pip
python -m pip install numpy scipy pillow
Write-Host "[+] reverse-SynthID setup complete at $Dir" -ForegroundColor Green
