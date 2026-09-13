#!/usr/bin/env python3
"""Montage the marginal name boxes of an Italian civil marriage register.

Each act page carries, in the left margin, a box with the act number and the two
spouses' names. Cutting just those boxes lets a whole volume be scanned for one
couple in a handful of images — which is the only way in when the annual index is
damaged.

  python3 tools/margin_names.py <out.png> <manifest-tag> <from> <to> [cols]
"""
import io, json, sys, time, urllib.request
from PIL import Image, ImageDraw, ImageOps

H = {"Referer": "https://antenati.cultura.gov.it/", "User-Agent": "Mozilla/5.0"}

def box(tag, num):
    ims = json.load(open(f"data/manifests/scilla-{tag}.json"))["images"]
    iid = ims[num-1]["id"]
    for _ in range(3):
        try:
            r = urllib.request.Request(
                f"https://iiif-antenati.cultura.gov.it/iiif/2/{iid}/info.json", headers=H)
            info = json.load(urllib.request.urlopen(r, timeout=60))
            W, Hh = info["width"], info["height"]
            out = []
            for x0, x1 in ((0.02, 0.19), (0.80, 0.97)):        # left page box, right page box
                x, y, w, h = int(W*x0), int(Hh*0.05), int(W*(x1-x0)), int(Hh*0.22)
                u = f"https://iiif-antenati.cultura.gov.it/iiif/2/{iid}/{x},{y},{w},{h}/{w},/0/default.jpg"
                im = Image.open(io.BytesIO(urllib.request.urlopen(
                    urllib.request.Request(u, headers=H), timeout=120).read())).convert("L")
                out.append(ImageOps.autocontrast(im))
            return out
        except Exception:
            time.sleep(4)
    return []

if __name__ == "__main__":
    out, tag, a, b = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    cols = int(sys.argv[5]) if len(sys.argv) > 5 else 6
    tiles = []
    for n in range(a, b+1):
        for i, im in enumerate(box(tag, n)):
            im = im.resize((int(im.width*1.5), int(im.height*1.5)), Image.LANCZOS)
            tiles.append((f"p{n}{'LR'[i]}", im))
    if not tiles:
        sys.exit("nothing fetched")
    cw = max(t.width for _, t in tiles); ch = max(t.height for _, t in tiles)
    rows = (len(tiles) + cols - 1)//cols
    sh = Image.new("L", (cols*(cw+8), rows*(ch+22)), 255); dr = ImageDraw.Draw(sh)
    for n, (lab, im) in enumerate(tiles):
        c, r = n % cols, n//cols
        dr.text((c*(cw+8)+3, r*(ch+22)+4), lab, fill=0)
        sh.paste(im, (c*(cw+8), r*(ch+22)+20))
    sh.save(out); print(out, sh.size, len(tiles), "boxes")
