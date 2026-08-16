#!/usr/bin/env bash
# Bootstrap setup for external CtrlRegen controllable regeneration harness (Linux/macOS)
set -euo pipefail

DEST_DIR="${1:-$HOME/noai-watermark}"
echo "[*] Setting up CtrlRegen (noai-watermark) at $DEST_DIR..."

if [ ! -d "$DEST_DIR" ]; then
    git clone https://github.com/mertizci/noai-watermark.git "$DEST_DIR"
fi

cd "$DEST_DIR"
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install diffusers transformers accelerate opencv-python pillow
echo "[+] CtrlRegen setup complete in $DEST_DIR/.venv"
