# Colab Video & Image Generation — Howto

Run ComfyUI on free Colab GPUs (Tesla T4, 15 GB VRAM) to generate images and short videos. Pi drives Colab by running shell cells that call the scripts in this repo.

## TL;DR

Two cells, run in order:

```python
# Cell 1 — one-time per session
!git clone https://github.com/nerkn/comfy-colab.git /content/comfy-colab && \
 bash /content/comfy-colab/setup.sh sdxl && \
 python /content/comfy-colab/server.py start
```

```python
# Cell 2 — per generation
!cd /content/comfy-colab && git pull -q && \
 python generate.py --workflow sdxl \
 --prompt "a majestic snow leopard on a mossy rock, golden hour" \
 --seed 42 --show
```

## Prerequisites

- A Google account (Colab free tier is enough).
- **Runtime must be GPU.** `Runtime → Change runtime type → T4 GPU`.
- No GitHub auth needed — the repo is public.

## How it works

1. `setup.sh` clones ComfyUI into `/content/ComfyUI`, pip-installs its deps, and downloads the model files listed in `models.yaml`.
2. `server.py start` launches ComfyUI's HTTP server on `http://127.0.0.1:8188` as a **detached** process (using `start_new_session=True`) so it survives cell exits and Colab UI navigation.
3. `generate.py` POSTs a workflow JSON to `/prompt`, polls `/history/{id}`, and downloads each output from `/view` into `output/`.

No tunnel (cloudflared/ngrok) is required, because pi runs the Python code **inside the VM** via cells, and the VM reaches `localhost:8188` directly.

## The commands

### `setup.sh <model> [<model> ...]`
Downloads model files. Idempotent — re-running skips existing files. Default: `sdxl`.
```python
!bash /content/comfy-colab/setup.sh sdxl flux-schnell
```

### `server.py {start|stop|status|log [N]}`
```python
!python /content/comfy-colab/server.py status
!python /content/comfy-colab/server.py log 50
!python /content/comfy-colab/server.py stop
```

### `generate.py --workflow <name> [...]`
```python
!python generate.py --workflow sdxl --prompt "..." --seed 42 --show
# Override any node field directly:
!python generate.py --workflow sdxl --fields '{"5":{"width":1344,"height":768}}'
```
- `--prompt` overwrites the workflow's positive-prompt node (auto-detected).
- `--seed` overwrites every node that has a `seed` field.
- `--show` displays the image inline in the Colab cell output.

### `fetch.py {list|pull|gdrive}`
- `list` — show files in `/content/ComfyUI/output` with sizes.
- `pull` — copy them into the repo's `output/` folder.
- `gdrive` — mount Google Drive and copy outputs to `MyDrive/comfy-colab-output` (persists across sessions).

## Where do generated images live? How to save them

This is the critical question because **everything in `/content/` is wiped when the Colab runtime dies** (~12h max, ~90 min idle disconnect). Three persistence options:

| Method | Persists? | How |
|---|---|---|
| **Google Drive** (recommended) | ✅ across sessions, your account | `python fetch.py gdrive` → mounts Drive, copies to `MyDrive/comfy-colab-output/` |
| **Download to your laptop** | ✅ | In Colab: `Files` sidebar → right-click file → Download. Or `fetch.py pull` then download the repo's `output/`. |
| **Push to this repo** | ✅ (but unwise for big media) | Don't commit PNGs — `.gitignore` blocks them. Use a separate branch or skip. |
| **Leave in `/content/`** | ❌ gone on disconnect | only for throwaway previews |

**Recommended workflow:** generate with `--show` to preview inline; once happy, run `python fetch.py gdrive` to keep it.

## Session lifecycle

- **Cold start** (new session): run Cell 1 (clone + setup + start server). Takes 1–3 min depending on model download size.
- **Warm** (same session, server still up): just run `generate.py` for each new image.
- **Server died but VM alive**: `python server.py status` → if STOPPED, `python server.py start`.
- **Runtime disconnected**: everything is gone. Re-run Cell 1.

## Available models (T4 = 15 GB VRAM)

| Workflow | Model | Size | Steps | Time/image | Notes |
|---|---|---|---|---|---|
| `sdxl` | SDXL base 1.0 | 6.5 GB | 25 | ~50 s | Proven, reliable baseline |
| `flux-schnell` | FLUX.1-schnell | ~12 GB (4 files) | 4 | ~30–60 s | Best quality/speed; fp8 fits T4 |
| `wan-video` | Wan2.1 | TBD | — | — | Placeholder — pending model-research pass |

Add models by editing `models.yaml` + adding a workflow JSON, then `git push`.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `server.py start` times out | `python server.py log 80` — usually a missing model or pip dep |
| `generate.py` says "TIMEOUT" | check the server log; the workflow JSON may reference a node/model that doesn't exist |
| Generation slow (>2 min) | reduce `steps`; for SDXL 25→15. For FLUX-schnell keep at 4. |
| `CUDA out of memory` | lower `width`/`height`; reduce `batch_size`; for FLUX use fp8 weights |
| Runtime vanished | expected — re-run Cell 1. Outputs were lost unless saved to Drive |

## Notes for pi

- To run a cell: set the Monaco editor value, then dispatch Ctrl+Enter at `document.body`:
  ```js
  monaco.editor.getEditors()[0].setValue(code);
  document.body.dispatchEvent(new KeyboardEvent('keydown',
    {key:'Enter',code:'Enter',keyCode:13,ctrlKey:true,bubbles:true,cancelable:true}));
  ```
- To read output: `document.body.innerText` (reliable; tree-walker misses collapsed cells).
- Use `print("PI_SENTINEL_N")` + `browse97_wait` to know when a cell finished.
