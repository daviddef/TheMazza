#!/usr/bin/env python3
"""Stack the same narrow crop of several pages into ONE readable image.

WHY. Finding the N section of an annual Tavola means looking at three or four
pages of a volume, and a volume is one of dozens. Read one page at a time it is
a picture each; and the thing being looked for — a section letter and a surname
— lives in a strip about a fifth of the page wide. This crops that strip
server-side through IIIF and stands the strips side by side, so a whole
volume's Tavola is one look instead of four.

It does NOT replace reading the entry. Once a strip shows an N, go back to
antenati_index.py and read that page properly, at full width: this archive has
twice misread a surname off a narrow band and had to correct it in public.

  python3 tools/montage_pages.py <container> <out.jpg> <pct> <page>...
  python3 tools/montage_pages.py <container> <out.jpg> auto <page>...

`pct` is the IIIF percentage region x,y,w,h — e.g. 5,10,24,86 for the left
page's first column, 52,10,24,86 for the right page's. `auto` takes BOTH, in
reading order, which is what an opening actually is.
"""
import sys, io, urllib.request
from PIL import Image, ImageDraw

def grab(img_id, pct, w=620):
    url = f"https://iiif-antenati.cultura.gov.it/iiif/2/{img_id}/pct:{pct}/{w},/0/default.jpg"
    req = urllib.request.Request(url, headers={
        "Referer": "https://antenati.cultura.gov.it/",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return Image.open(io.BytesIO(r.read())).convert("L")

if __name__ == "__main__":
    sys.path.insert(0, __file__.rsplit("/", 1)[0])
    from antenati_index import ids
    container, out, pct = sys.argv[1], sys.argv[2], sys.argv[3]
    pages = [int(x) for x in sys.argv[4:]]
    all_ids = ids(container)
    if pct == "auto":
        want = [(f"{p}L", "5,8,26,88") for p in pages]
        want = [x for p in pages for x in ((f"{p}L", "5,8,26,88"), (f"{p}R", "52,8,26,88"))]
        tiles = [(lab, grab(all_ids[int(lab[:-1]) - 1], r)) for lab, r in want]
    else:
        tiles = [(str(p), grab(all_ids[p - 1], pct)) for p in pages]
    H, gap, lab = max(t.height for _, t in tiles), 14, 26
    sheet = Image.new("L", (sum(t.width for _, t in tiles) + gap * (len(tiles) - 1),
                            H + lab), 255)
    d, x = ImageDraw.Draw(sheet), 0
    for p, t in tiles:
        sheet.paste(t, (x, lab))
        d.text((x + 6, 6), f"p{p}", fill=0)
        x += t.width + gap
    sheet.save(out, quality=88)
    print(f"{container} {pct} pages {pages} -> {out}  ({sheet.width}x{sheet.height})")
