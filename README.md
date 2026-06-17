# comfy-colab

Generate **images (SDXL)** and **video (Wan2.2)** on a free **Google Colab T4 GPU** — no local GPU needed.

One self-contained notebook: all logic lives in the cells with `#@param` form fields, nothing external.

## Use it

Opens in Colab, ready to run:

**[comfy_colab.ipynb](https://colab.research.google.com/github/gemeyilim/comfy-colab/blob/main/comfy_colab.ipynb)**

1. **Runtime → Change runtime type → T4 GPU** (free tier)
2. Run cells **1 → 3** once (setup, optional video models, server).
3. Re-run a **Generate** cell on demand to iterate:
   - **Cell 4** — SDXL image (~52 s)
   - **Cell 5** — Wan2.2 video (GGUF Q4, several minutes)
4. Run **cell 6** to display the last result.

First run clones ComfyUI + the ComfyUI-GGUF node and downloads SDXL (~6.5 GB). Video
models (cell 2) are optional — skip if you only want images.

## Cells

| # | Cell | What it does |
|---|------|--------------|
| 1 | Setup | Clone ComfyUI, install deps + ComfyUI-GGUF node, download SDXL base |
| 2 | Video models *(optional)* | Download Wan2.2 5B GGUF Q4_K_M + umt5 encoder + VAE |
| 3 | Start server | Boot ComfyUI on `:8188` in the background (idempotent) |
| 4 | Generate · SDXL image | Build workflow, POST to API, poll, save PNG |
| 5 | Generate · Wan2.2 video | Build workflow, POST to API, poll, save WEBM |
| 6 | Display last result | Show the most recent image or video inline |

## Iterate

Edit the **`prompt`** field in a Generate cell and re-run that cell + cell 6. Change `seed`
for variations. `#@param` fields (seed, width, height, steps, frames) give a form UI.

## Notes

- Colab storage is ephemeral — download outputs via the file browser, or mount Google Drive to persist them.
- The Wan2.2 video cell uses the **GGUF Q4_K_M** quant (3.3 GB) so it fits the T4's 15 GB VRAM; it needs the ComfyUI-GGUF custom node (installed automatically in cell 1).
- Everything targets the free T4. Larger models (e.g. text-in-image like Ideogram-4) need more than 15 GB and won't fit the free tier.

## License

MIT
