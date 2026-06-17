#!/usr/bin/env bash
# setup.sh — clone ComfyUI, install deps, download model(s).
# Usage: bash setup.sh [model ...]   (default: sdxl)
# Reads models.yaml for URLs. Idempotent: skips existing files.
set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
COMFY="/content/ComfyUI"
MODELS="${@:-sdxl}"

echo "=== [1/4] Clone ComfyUI ==="
if [ ! -d "$COMFY/.git" ]; then
  git clone -q https://github.com/comfyanonymous/ComfyUI.git "$COMFY"
else
  echo "ComfyUI already present, pulling latest."
  git -C "$COMFY" pull -q || true
fi

echo "=== [2/4] Install dependencies ==="
pip install -q -r "$COMFY/requirements.txt"

echo "=== [3/4] Parse models.yaml & download: $MODELS ==="
python "$REPO_DIR/_download_models.py" "$REPO_DIR/models.yaml" "$COMFY" $MODELS

echo "=== [4/4] Done. Start server with: python server.py start ==="
