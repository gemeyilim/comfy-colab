# comfy-colab

Generate images and videos with ComfyUI on free Colab GPUs (Tesla T4, 15 GB VRAM).

Pi drives Colab by running shell cells that call the scripts in this repo — no Monaco surgery, no tunnels. Each generation is one cell.

## Quick start (in Colab)

```bash
# Cell 1 — one-time per session: clone + install + download a model + start server
!git clone https://github.com/nerkn/comfy-colab.git /content/comfy-colab && \
 bash /content/comfy-colab/setup.sh sdxl && \
 python /content/comfy-colab/server.py start

# Cell 2 — per generation:
!cd /content/comfy-colab && git pull -q && python generate.py --workflow sdxl \
 --prompt "a majestic snow leopard on a mossy rock, golden hour" --seed 42 --show
```

## Layout

| Path | Purpose |
|---|---|
| `setup.sh` | Clone ComfyUI, pip install, download chosen model(s) |
| `server.py` | Launch/stop/status the ComfyUI HTTP server (detached, survives cell exit) |
| `generate.py` | Submit a workflow → poll → download → optionally display image |
| `fetch.py` | Download generated outputs from the VM to inspect |
| `workflows/*.json` | ComfyUI workflow API JSON (sdxl, flux-schnell, wan-video) |
| `models.yaml` | Model manifest: URLs + destination paths |

## Where generated files live

- **Inside the VM**: `/content/ComfyUI/output/` — wiped when the runtime dies.
- **Persisted**: anything you push to this repo's `output/` branch, or download via `fetch.py`, or upload to Google Drive (see `colab-video-gen.md`).

## Adding a new model

Add an entry to `models.yaml`, add a workflow JSON to `workflows/`, then `git push`. Next Colab session: `git pull && bash setup.sh <newmodel>`.

See `colab-video-gen.md` for the full howto.
