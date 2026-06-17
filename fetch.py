#!/usr/bin/env python3
"""fetch.py — download generated outputs from the VM to the repo's output/ dir,
or upload them to Google Drive for persistence.
Usage:
  python fetch.py list                 # list files in /content/ComfyUI/output
  python fetch.py pull                 # copy all outputs to repo/output/
  python fetch.py gdrive               # mount Drive & copy outputs there
"""
import sys, os, shutil, glob

COMFY_OUT = "/content/ComfyUI/output"
REPO_DIR = os.path.dirname(os.path.abspath(__file__))
FETCH_DIR = os.path.join(REPO_DIR, "output")


def list_outputs():
    if not os.path.isdir(COMFY_OUT):
        print(f"{COMFY_OUT} does not exist")
        return
    files = sorted(glob.glob(os.path.join(COMFY_OUT, "*")))
    for f in files:
        print(f"  {os.path.getsize(f)//1024:>8} KB  {os.path.basename(f)}")
    print(f"({len(files)} files)")


def pull():
    os.makedirs(FETCH_DIR, exist_ok=True)
    files = sorted(glob.glob(os.path.join(COMFY_OUT, "*")))
    for f in files:
        shutil.copy2(f, os.path.join(FETCH_DIR, os.path.basename(f)))
    print(f"copied {len(files)} files to {FETCH_DIR}")


def gdrive():
    try:
        from google.colab import drive
        drive.mount("/content/drive")
        dest = "/content/drive/MyDrive/comfy-colab-output"
        os.makedirs(dest, exist_ok=True)
        files = sorted(glob.glob(os.path.join(COMFY_OUT, "*")))
        for f in files:
            shutil.copy2(f, os.path.join(dest, os.path.basename(f)))
        print(f"copied {len(files)} files to Drive: {dest}")
    except ImportError:
        print("Not running in Colab (no google.colab). Use 'pull' instead.")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    {"list": list_outputs, "pull": pull, "gdrive": gdrive}.get(cmd, lambda: print(__doc__))()
