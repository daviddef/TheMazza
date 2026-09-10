#!/usr/bin/env python3
"""Find which image holds a given act, by reading the act numbers in the margin.

These volumes run TWO ACTS PER IMAGE, but the offset varies with how much front
matter each book has, so the mapping has to be calibrated per volume rather than
assumed. This fetches the left margin of several images and stacks them, so one
look establishes the offset for the whole volume.

  python3 tools/act_locate.py <manifest.json> <img,img,...> <out.jpg>
"""
import sys, json, io, urllib.request
from PIL import Image

def grab(img_id, pct, w):
    url = f"https://iiif-antenati.cultura.gov.it/iiif/2/{img_id}/pct:{pct}/{w},/0/default.jpg"
    req = urllib.request.Request(url, headers={
        "Referer": "https://antenati.cultura.gov.it/",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return Image.open(io.BytesIO(r.read())).convert("L")

man = json.load(open(sys.argv[1]))
pages = [int(x) for x in sys.argv[2].split(",")]
out = sys.argv[3]
tiles = []
for p in pages:
    img = man["images"][p - 1]["id"]
    tiles.append((p, grab(img, "5,6,17,92", 620)))
gap = 14
W = sum(t.width for _, t in tiles) + gap * (len(tiles) + 1)
H = max(t.height for _, t in tiles) + gap * 2
c = Image.new("L", (W, H), 110)
x = gap
for p, t in tiles:
    c.paste(t, (x, gap)); x += t.width + gap
c.save(out, "JPEG", quality=74)
print(out, c.size, "pages:", pages)
