#!/usr/bin/env python3
"""Pull Antenati register images down to disk.

The Falco archive recorded these IIIF images as Cloudflare-blocked to direct
fetch, readable only inside the Mirador viewer. On 10 September 2026 they serve
fine to curl with a Referer header — which turns reading a register from a
screenshot exercise into an ordinary download.

  python3 tools/antenati.py <ark-slug> <out-dir> <id,id,...> [width]

Rate limiting is real: Antenati returns a blanket 403 to everything, including
its own home page, after a burst. Requests are paced.
"""
import sys, os, time, json, urllib.request

HDRS = {
    "Referer": "https://antenati.cultura.gov.it/",
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                   "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"),
}

def native(img_id):
    """The image's own width. Asking for one pixel more than this returns 403,
    not a smaller image -- and the widths vary WITHIN a volume: Scilla Nati 1817
    holds 1758, 1757 and 1756 side by side, so a single width for the run fails
    on three images in ten for no visible reason."""
    req = urllib.request.Request(
        f"https://iiif-antenati.cultura.gov.it/iiif/2/{img_id}/info.json", headers=HDRS)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)["width"]

def fetch(img_id, dest, width=1800):
    if width in (0, None, "native"):
        width = native(img_id)
        time.sleep(0.6)
    url = f"https://iiif-antenati.cultura.gov.it/iiif/2/{img_id}/full/{width},/0/default.jpg"
    req = urllib.request.Request(url, headers=HDRS)
    with urllib.request.urlopen(req, timeout=90) as r, open(dest, "wb") as fh:
        fh.write(r.read())
    return os.path.getsize(dest)

if __name__ == "__main__":
    out, ids = sys.argv[2], sys.argv[3].split(",")
    # width 0 (or "native") asks each image for its own full width
    width = int(sys.argv[4]) if len(sys.argv) > 4 else 1800
    os.makedirs(out, exist_ok=True)
    for n, i in enumerate(ids, 1):
        # page numbers are 1-based positions in the manifest, passed in order
        dest = os.path.join(out, f"p{n:03d}_{i}.jpg")
        if os.path.exists(dest) and os.path.getsize(dest) > 5000:
            print(f"  p{n:03d} cached"); continue
        try:
            sz = fetch(i, dest, width)
            print(f"  p{n:03d} {i} {sz//1024} KB")
        except Exception as e:
            if "403" in str(e) and width:
                try:                      # almost always an overshoot by a pixel or two
                    sz = fetch(i, dest, 0)
                    print(f"  p{n:03d} {i} {sz//1024} KB (at its own width)")
                    time.sleep(1.2); continue
                except Exception as e2:
                    e = e2
            print(f"  p{n:03d} {i} FAILED {e}")
        time.sleep(1.2)
