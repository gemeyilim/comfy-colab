#!/usr/bin/env python3
"""generate.py — submit a workflow to ComfyUI, poll, download, optionally display.
Usage:
  python generate.py --workflow sdxl --prompt "a cat" [--seed 42] [--show]
  python generate.py --workflow sdxl --fields '{"5":{"text":"..."}}'
"""
import sys, os, json, time, argparse, urllib.request, urllib.parse

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
WORKFLOWS_DIR = os.path.join(REPO_DIR, "workflows")
FETCH_DIR = os.path.join(REPO_DIR, "output")
SERVER = os.environ.get("COMFY_URL", "http://127.0.0.1:8188")


def list_workflows():
    return sorted(os.path.splitext(f)[0] for f in os.listdir(WORKFLOWS_DIR) if f.endswith(".json"))


def load_workflow(name):
    path = os.path.join(WORKFLOWS_DIR, f"{name}.json")
    if not os.path.exists(path):
        sys.exit(f"unknown workflow '{name}'. available: {list_workflows()}")
    with open(path) as f:
        return json.load(f)


def positive_node_id(nodes):
    """CLIPTextEncode whose output feeds a KSampler's 'positive' input."""
    positive_feeds = set()
    for n in nodes.values():
        if n.get("class_type") in ("KSampler", "KSamplerAdvanced"):
            pos = n["inputs"].get("positive")
            if isinstance(pos, list):
                positive_feeds.add(str(pos[0]))
    for nid, n in nodes.items():
        if n.get("class_type") == "CLIPTextEncode" and nid in positive_feeds:
            return nid
    for nid, n in nodes.items():
        if n.get("class_type") == "CLIPTextEncode":
            return nid
    return None


def patch_workflow(wf, prompt, seed, fields):
    nodes = wf["prompt"]
    if prompt:
        nid = positive_node_id(nodes)
        if nid:
            nodes[nid]["inputs"]["text"] = prompt
    if seed is not None:
        for n in nodes.values():
            if "seed" in n.get("inputs", {}):
                n["inputs"]["seed"] = seed
    if fields:
        for nid, overrides in fields.items():
            if nid in nodes:
                for k, v in overrides.items():
                    nodes[nid]["inputs"][k] = v
    return wf


def display_image(path):
    try:
        from IPython.display import Image, display
        display(Image(filename=path))
    except Exception:
        print(f"(cannot display inline; file at {path})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workflow", "-w", required=True)
    ap.add_argument("--prompt", "-p", default=None, help="override positive prompt")
    ap.add_argument("--seed", "-s", type=int, default=None)
    ap.add_argument("--fields", default=None, help='JSON: {"node_id":{"field":value}}')
    ap.add_argument("--show", action="store_true", help="display inline (Colab)")
    ap.add_argument("--server", default=SERVER)
    args = ap.parse_args()

    fields = json.loads(args.fields) if args.fields else None
    wf = load_workflow(args.workflow)
    wf = patch_workflow(wf, args.prompt, args.seed, fields)

    req = urllib.request.Request(args.server + "/prompt",
        data=json.dumps(wf).encode(), headers={"Content-Type": "application/json"})
    pid = json.loads(urllib.request.urlopen(req).read())["prompt_id"]
    print(f"submitted: {pid}", flush=True)

    t0 = time.time()
    while time.time() - t0 < 300:
        try:
            h = json.loads(urllib.request.urlopen(f"{args.server}/history/{pid}").read())
        except Exception:
            h = {}
        if pid in h:
            print(f"DONE in {time.time()-t0:.1f}s")
            os.makedirs(FETCH_DIR, exist_ok=True)
            for node_id, out in h[pid]["outputs"].items():
                for kind in ("images", "gifs", "videos"):
                    for item in out.get(kind, []):
                        fname, sub = item["filename"], item.get("subfolder", "")
                        q = urllib.parse.urlencode({"filename": fname, "subfolder": sub, "type": "output"})
                        data = urllib.request.urlopen(f"{args.server}/view?{q}").read()
                        dest = os.path.join(FETCH_DIR, fname)
                        open(dest, "wb").write(data)
                        print(f"SAVED: {dest} ({len(data)//1024} KB)")
                        if args.show:
                            display_image(dest)
            return
        time.sleep(1)
    print("TIMEOUT after 300s")
    sys.exit(1)


if __name__ == "__main__":
    main()
