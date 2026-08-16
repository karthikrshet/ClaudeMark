#!/usr/bin/env bash
# ClaudeMark Environment Setup & Verification Script (Linux / macOS)
set -euo pipefail

echo "=================================================="
echo " ClaudeMark v2.0 Environment Bootstrap"
echo "=================================================="

# Check Python version
PYTHON_CMD="python3"
if ! command -v "$PYTHON_CMD" &>/dev/null; then
    PYTHON_CMD="python"
fi

if ! command -v "$PYTHON_CMD" &>/dev/null; then
    echo "[-] Error: Python 3.10+ is required but not found in PATH." >&2
    exit 1
fi

PY_VER=$($PYTHON_CMD -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "[+] Detected Python $PY_VER"

# Create virtual environment if not present
if [ ! -d ".venv" ]; then
    echo "[*] Creating virtual environment (.venv)..."
    "$PYTHON_CMD" -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip and install development dependencies
echo "[*] Installing dependencies..."
pip install --upgrade pip
pip install -r requirements-dev.txt

# Run test suite
echo "[*] Running verification test suite..."
python -m pytest tests/ -q

echo "=================================================="
echo " ClaudeMark Environment Ready!"
echo " Start server: python claudemark.py serve"
echo "=================================================="
