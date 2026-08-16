#!/usr/bin/env bash
# Bootstrap setup for external reverse-SynthID scoring harness (Linux/macOS)
set -euo pipefail

DEST_DIR="${1:-$HOME/reverse-SynthID}"
echo "[*] Setting up reverse-SynthID at $DEST_DIR..."

if [ ! -d "$DEST_DIR" ]; then
    git clone https://github.com/aloshdenny/reverse-SynthID.git "$DEST_DIR"
fi

cd "$DEST_DIR"
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install numpy scipy pillow
echo "[+] reverse-SynthID setup complete in $DEST_DIR/.venv"
