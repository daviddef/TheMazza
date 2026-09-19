#!/usr/bin/env python3
"""Find the annual index at the back of an Antenati volume, in one look.

Most of these volumes carry an INDICE ANNUALE in their last pages. Reading it
turns a register sweep into three downloads: the index gives the act number, the
acts run two per image, so the act's page is arithmetic.

THE INDEX IS NOT AT A FIXED OFFSET AND GUESSING ONE WASTES DOWNLOADS. Across
Scilla's death volumes the first index page sat at n-1, n-2, n-3 and n-5, and in
1898 the A block was on the LEFT page of the spread while the right page was
already into C. So this tiles the last few images into a single contact sheet,
which you read once to find the page you want, then crop at full width.

  # list the image ids for a container
  python3 tools/antenati_index.py ids <container>

  # contact sheet of the last N pages (default 6), labelled with page numbers
  python3 tools/antenati_index.py sheet <container> <out.jpg> [n]

  # one page, or a percentage region of it, at full width
  python3 tools/antenati_index.py page <container> <page-no> <out.jpg> [pct:x,y,w,h]

Containers cost a rate-limited page load each and belong in the arks TSVs once
found -- see data/scilla-arks-italiano.tsv. The manifest and the images
themselves are NOT rate limited and fetch straight to curl.
"""
import json, os, subprocess, sys, tempfile, urllib.request

HDRS = {
    "Referer": "https://antenati.cultura.gov.it/",
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"),
}
MANIFEST = "https://dam-antenati.cultura.gov.it/antenati/containers/{}/manifest"
# ImageMagick on this machine has no default font and BOTH magick and montage
# abort with "unable to read font ''" without one, even when only tiling.
FONT = next((f for f in ("/System/Library/Fonts/Supplemental/Arial.ttf",
                         "/System/Library/Fonts/Helvetica.ttc",
                         "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
             if os.path.exists(f)), None)
FONTARG = ["-font", FONT] if FONT else []
IIIF = "https://iiif-antenati.cultura.gov.it/iiif/2/{}/{}/{},/0/default.jpg"


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=HDRS), timeout=90) as r:
        return r.read()


def ids(container):
    """Every image id in the volume, in page order."""
    j = json.loads(get(MANIFEST.format(container)))
    canvases = (j.get("sequences") or [{}])[0].get("canvases") or j.get("items") or []
    out = []
    for c in canvases:
        res = (c.get("images") or [{}])[0].get("resource") or {}
        svc = res.get("service") or {}
        out.append((svc.get("@id") or res.get("@id") or "").rsplit("/", 1)[-1])
    return out


def image(img_id, region="full", width=1800):
    return get(IIIF.format(img_id, region, width))


def sheet(container, out, n=6):
    """A labelled contact sheet of the last n pages, for locating the index."""
    all_ids = ids(container)
    pages = list(range(max(1, len(all_ids) - n + 1), len(all_ids) + 1))
    tmp = tempfile.mkdtemp()
    tiles = []
    for p in pages:
        f = os.path.join(tmp, f"{p:04d}.jpg")
        with open(f, "wb") as fh:
            fh.write(image(all_ids[p - 1], width=760))
        # the page number has to travel with the tile or the sheet is useless
        subprocess.run(["magick", f, "-gravity", "North", "-background", "yellow",
                        "-splice", "0x30", "-pointsize", "26", "-fill", "black",
                        *FONTARG, "-annotate", "+0+2", f"p{p}", f], check=False,
                       stderr=subprocess.DEVNULL)
        tiles.append(f)
    subprocess.run(["montage", *FONTARG, *tiles, "-tile", "3x", "-geometry", "+4+4",
                    "-background", "gray30", out], check=True)
    print(f"{container}: {len(all_ids)} images; sheet of pages "
          f"{pages[0]}-{pages[-1]} -> {out}")


def page(container, no, out, region="full"):
    all_ids = ids(container)
    with open(out, "wb") as fh:
        fh.write(image(all_ids[int(no) - 1], region=region))
    print(f"{container} page {no} ({region}) -> {out}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    cmd = sys.argv[1]
    if cmd == "ids":
        v = ids(sys.argv[2])
        print(f"{len(v)} images")
        print(" ".join(v))
    elif cmd == "sheet":
        sheet(sys.argv[2], sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else 6)
    elif cmd == "page":
        page(sys.argv[2], sys.argv[3], sys.argv[4],
             sys.argv[5] if len(sys.argv) > 5 else "full")
    else:
        sys.exit(__doc__)
