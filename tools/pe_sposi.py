#!/usr/bin/env python3
"""Montage the "cognomi e nomi degli sposi" columns of Piedimonte marriage indexes.

Each index opening carries two tables side by side; the spouse-name column sits at a
fixed fraction of the page width. Cutting just those two strips lets eight openings be
read in one image instead of eight.

  python3 tools/pe_sposi.py <out.png> <year:page> [year:page ...]
"""
import io, json, sys, time, urllib.request
from PIL import Image, ImageDraw

H = {"Referer": "https://antenati.cultura.gov.it/", "User-Agent": "Mozilla/5.0"}

def full(tag, num):
    ims = json.load(open(f"data/manifests/scilla-{tag}.json"))["images"]
    iid = ims[num-1]["id"]
    for a in range(3):
        try:
            r = urllib.request.Request(
                f"https://iiif-antenati.cultura.gov.it/iiif/2/{iid}/info.json", headers=H)
            W = json.load(urllib.request.urlopen(r, timeout=60))["width"]
            r = urllib.request.Request(
                f"https://iiif-antenati.cultura.gov.it/iiif/2/{iid}/full/{W},/0/default.jpg", headers=H)
            return Image.open(io.BytesIO(urllib.request.urlopen(r, timeout=120).read())).convert("L")
        except Exception:
            time.sleep(4)

if __name__ == "__main__":
    out, specs = sys.argv[1], sys.argv[2:]
    strips = []
    for s in specs:
        y, n = s.split(":")
        im = full(f"pe-matr-{y}", int(n))
        if im is None:
            print("  FAIL", s); continue
        w, h = im.size
        for side, (a, b) in (("L", (0.16, 0.34)), ("R", (0.52, 0.70))):
            strips.append((f"{y} p{n} {side}", im.crop((int(w*a), 0, int(w*b), h))))
    hh = max(s.height for _, s in strips)
    ww = sum(s.width for _, s in strips) + 10*len(strips)
    sh = Image.new("L", (ww, hh+22), 255); dr = ImageDraw.Draw(sh); x = 0
    for lab, s in strips:
        sh.paste(s, (x, 22)); dr.text((x+4, 5), lab, fill=0); x += s.width + 10
    sh.save(out); print(out, sh.size, len(strips), "strips")
