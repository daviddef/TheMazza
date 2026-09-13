#!/usr/bin/env python3
"""Pull one page (or half-opening) of a Scilla volume at native size, upscaled for reading.

  python3 tools/scilla_page.py <manifest-tag> <image-number> [L|R|F] [scale]
"""
import json, sys, time, io, urllib.request
from PIL import Image

def get(iid, region, size, tries=3):
    url = f"https://iiif-antenati.cultura.gov.it/iiif/2/{iid}/{region}/{size}/0/default.jpg"
    req = urllib.request.Request(url, headers={
        "Referer": "https://antenati.cultura.gov.it/", "User-Agent": "Mozilla/5.0"})
    for a in range(tries):
        try:
            return Image.open(io.BytesIO(urllib.request.urlopen(req, timeout=120).read()))
        except Exception as e:
            print("   retry", str(e)[:30]); time.sleep(4)

if __name__ == "__main__":
    tag, num = sys.argv[1], int(sys.argv[2])
    half = sys.argv[3] if len(sys.argv) > 3 else "F"
    scale = float(sys.argv[4]) if len(sys.argv) > 4 else 2.0
    ims = json.load(open(f"data/manifests/scilla-{tag}.json"))["images"]
    iid = ims[num-1]["id"]
    req = urllib.request.Request(
        f"https://iiif-antenati.cultura.gov.it/iiif/2/{iid}/info.json",
        headers={"Referer": "https://antenati.cultura.gov.it/", "User-Agent": "Mozilla/5.0"})
    info = json.load(urllib.request.urlopen(req, timeout=90))
    W = info["width"]
    region = {"F": "full", "L": "pct:0,0,50,100", "R": "pct:48,0,52,100"}[half]
    w = W if half == "F" else int(W * 0.52)
    im = get(iid, region, f"{w},")
    dest = f"/tmp/pg-{tag}-{num}{half}.png"
    im.resize((int(im.size[0]*scale), int(im.size[1]*scale)), Image.LANCZOS).save(dest)
    print(f"{iid}  native {W}x{info['height']}  ->  {dest}  {im.size}")
