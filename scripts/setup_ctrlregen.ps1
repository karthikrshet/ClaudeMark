# Bootstrap setup for external CtrlRegen controllable regeneration harness (Windows PowerShell)
param (
    [string]$Dir = (Join-Path $HOME "noai-watermark")
)
$ErrorActionPreference = "Stop"

Write-Host "[*] Setting up CtrlRegen (noai-watermark) at $Dir..." -ForegroundColor Yellow
if (-not (Test-Path $Dir)) {
    git clone https://github.com/mertizci/noai-watermark.git $Dir
}

Set-Location $Dir
python -m venv .venv
$Activate = Join-Path ".venv" "Scripts" "Activate.ps1"
if (Test-Path $Activate) { . $Activate }
python -m pip install --upgrade pip
python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
python -m pip install diffusers transformers accelerate opencv-python pillow
Write-Host "[+] CtrlRegen setup complete at $Dir" -ForegroundColor Green
