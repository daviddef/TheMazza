#!/usr/bin/env python3
"""Montage the same vertical column out of several register openings already on disk.

The Piedimonte birth index has the child's name in a narrow column at a fixed fraction of
each opening; cutting just that column lets six openings be scanned in one image.

  python3 tools/col_strip.py <out.png> <l0,l1,r0,r1> <file> [file ...]
"""
import sys
from PIL import Image, ImageDraw

if __name__ == "__main__":
    out, frac, files = sys.argv[1], [float(x) for x in sys.argv[2].split(",")], sys.argv[3:]
    strips = []
    for f in files:
        im = Image.open(f).convert("L"); w, h = im.size
        lab = f.split("/")[-1].replace(".png", "")
        strips.append((lab + " L", im.crop((int(w*frac[0]), 0, int(w*frac[1]), h))))
        strips.append((lab + " R", im.crop((int(w*frac[2]), 0, int(w*frac[3]), h))))
    hh = max(s.height for _, s in strips)
    sh = Image.new("L", (sum(s.width + 8 for _, s in strips), hh + 20), 255)
    dr = ImageDraw.Draw(sh); x = 0
    for lab, s in strips:
        sh.paste(s, (x, 20)); dr.text((x + 3, 4), lab, fill=0); x += s.width + 8
    sh.save(out); print(out, sh.size, len(strips), "strips")
