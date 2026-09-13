#!/usr/bin/env python3
"""Find and pull the Tavola pages at the end of a Scilla restaurazione volume.

  python3 tools/scilla_index.py <container> <tag> [tailcount]

Writes /tmp/idx-<tag>/pNNN.jpg thumbnails and a contact sheet at /tmp/idx-<tag>.png
so the index openings can be spotted, then the A section pulled at full size.
"""
import json, sys, os, time, urllib.request, io
from PIL import Image, ImageDraw
sys.path.insert(0, "tools")
from manifest import manifest, images

def fetch(iid, dest, width):
    url = f"https://iiif-antenati.cultura.gov.it/iiif/2/{iid}/full/{width},/0/default.jpg"
    req = urllib.request.Request(url, headers={
        "Referer": "https://antenati.cultura.gov.it/", "User-Agent": "Mozilla/5.0"})
    for a in range(3):
        try:
            d = urllib.request.urlopen(req, timeout=120).read()
            open(dest, "wb").write(d); return len(d)
        except Exception as e:
            print("   retry", str(e)[:30]); time.sleep(4)
    return 0

if __name__ == "__main__":
    container, tag = sys.argv[1], sys.argv[2]
    tail = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    j = manifest(container)
    imgs = images(j)
    path = f"data/manifests/scilla-{tag}.json"
    json.dump({"container": container, "label": j.get("label"), "images": imgs},
              open(path, "w"), indent=1, ensure_ascii=False)
    print(f"{len(imgs)} images -> {path}")
    out = f"/tmp/idx-{tag}"; os.makedirs(out, exist_ok=True)
    tiles = []
    for i in range(max(0, len(imgs) - tail), len(imgs)):
        d = f"{out}/p{i+1:03d}.jpg"
        if not (os.path.exists(d) and os.path.getsize(d) > 5000):
            fetch(imgs[i]["id"], d, 800)
        try:
            im = Image.open(d); im.thumbnail((330, 330), Image.LANCZOS); tiles.append((i+1, im))
        except Exception: pass
    sheet = Image.new("L", (len(tiles) * 340, 370), 255); dr = ImageDraw.Draw(sheet)
    for n, (num, im) in enumerate(tiles):
        sheet.paste(im.convert("L"), (n*340+5, 18)); dr.text((n*340+8, 4), f"p{num}", fill=0)
    sheet.save(f"/tmp/idx-{tag}.png")
    print("contact sheet ->", f"/tmp/idx-{tag}.png", sheet.size)
