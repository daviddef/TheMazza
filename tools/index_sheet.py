#!/usr/bin/env python3
"""Build one readable sheet out of an Antenati annual index.

An Indice Annuale spread carries FOUR surname columns — two on each page. Read
whole, the spread is too small to be legible; read column by column it costs
four images. This crops the four columns server-side through IIIF and stacks
them side by side at a resolution that survives one look.

  python3 tools/index_sheet.py <imageId> <out.jpg> [colwidth]
"""
import sys, os, io, urllib.request
from PIL import Image

# left page: two name+number pairs; right page: two more. Measured off the
# 1879 Piedimonte Etneo index and stable across these volumes.
COLS = ["6,8,21,90", "26,8,21,90", "50,8,20,90", "69,8,21,90"]
HDRS = ["col 1", "col 2", "col 3", "col 4"]

def grab(img_id, pct, w):
    url = f"https://iiif-antenati.cultura.gov.it/iiif/2/{img_id}/pct:{pct}/{w},/0/default.jpg"
    req = urllib.request.Request(url, headers={
        "Referer": "https://antenati.cultura.gov.it/",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return Image.open(io.BytesIO(r.read())).convert("L")

def sheet(img_id, out, w=760):
    tiles = [grab(img_id, p, w) for p in COLS]
    H = max(t.height for t in tiles)
    gap = 16
    canvas = Image.new("L", (sum(t.width for t in tiles) + gap * (len(tiles) + 1), H + gap * 2), 120)
    x = gap
    for t in tiles:
        canvas.paste(t, (x, gap))
        x += t.width + gap
    canvas.save(out, "JPEG", quality=72)
    return canvas.size

if __name__ == "__main__":
    img_id, out = sys.argv[1], sys.argv[2]
    w = int(sys.argv[3]) if len(sys.argv) > 3 else 760
    print(img_id, "->", out, sheet(img_id, out, w))
