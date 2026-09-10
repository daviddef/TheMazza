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
import sys, os, time, urllib.request

def fetch(img_id, dest, width=1800):
    url = f"https://iiif-antenati.cultura.gov.it/iiif/2/{img_id}/full/{width},/0/default.jpg"
    req = urllib.request.Request(url, headers={
        "Referer": "https://antenati.cultura.gov.it/",
        "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                       "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"),
    })
    with urllib.request.urlopen(req, timeout=90) as r, open(dest, "wb") as fh:
        fh.write(r.read())
    return os.path.getsize(dest)

if __name__ == "__main__":
    out, ids = sys.argv[2], sys.argv[3].split(",")
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
            print(f"  p{n:03d} {i} FAILED {e}")
        time.sleep(1.2)
