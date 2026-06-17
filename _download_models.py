#!/usr/bin/env python3
"""Download models listed in models.yaml. Idempotent. Colab-path-aware."""
import sys, os, yaml, urllib.request, shutil

def dest_dir(comfy, dest_type):
    # ComfyUI model subfolders. unet/ is alias for diffusion_model in recent versions.
    mapping = {
        "checkpoint": "checkpoints",
        "vae": "vae",
        "lora": "loras",
        "clip": "clip",
        "unet": "unet",
        "diffusion_model": "unet",
        "text_encoder": "text_encoders",
    }
    sub = mapping.get(dest_type, dest_type)
    d = os.path.join(comfy, "models", sub)
    os.makedirs(d, exist_ok=True)
    return d

def main():
    yaml_path, comfy = sys.argv[1], sys.argv[2]
    wanted = sys.argv[3:] or ["sdxl"]
    with open(yaml_path) as f:
        manifest = yaml.safe_load(f)
    for name in wanted:
        if name not in manifest:
            print(f"  ! unknown model '{name}', skipping. known: {list(manifest)}")
            continue
        print(f"  - model set: {name}")
        for item in manifest[name]:
            d = dest_dir(comfy, item["dest_type"])
            target = os.path.join(d, item["dest"])
            if os.path.exists(target) and os.path.getsize(target) > 0:
                print(f"      exists: {item['dest']} ({os.path.getsize(target)//1024} KB)")
                continue
            print(f"      downloading: {item['dest']} <- {item['url'][:70]}...")
            urllib.request.urlretrieve(item["url"], target)
            print(f"        ok ({os.path.getsize(target)//1024} KB)")

if __name__ == "__main__":
    main()
