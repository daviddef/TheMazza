#!/usr/bin/env python3
"""Fetch an Antenati IIIF manifest and list its image ids, in page order.

The manifest serves fine to curl once you have the container id; only the
ark -> container step needs the browser, because the ark record page is
Cloudflare-blocked. So: look the container up once in the browser, then do
everything else from here.

  python3 tools/manifest.py <containerId> [out.json]
"""
import sys, json, urllib.request

def manifest(container):
    url = f"https://dam-antenati.cultura.gov.it/antenati/containers/{container}/manifest"
    req = urllib.request.Request(url, headers={
        "Referer": "https://antenati.cultura.gov.it/",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.load(r)

def images(j):
    seq = (j.get("sequences") or [{}])[0]
    out = []
    for c in seq.get("canvases", j.get("items", [])):
        try:
            if "images" in c:
                sid = c["images"][0]["resource"]["service"]["@id"]
            else:
                sid = c["items"][0]["items"][0]["body"]["service"][0]["@id"]
            out.append({"id": sid.rstrip("/").split("/")[-1],
                        "label": c.get("label") if isinstance(c.get("label"), str)
                                 else json.dumps(c.get("label"))})
        except Exception:
            out.append({"id": None, "label": c.get("label")})
    return out

if __name__ == "__main__":
    container = sys.argv[1]
    j = manifest(container)
    imgs = images(j)
    print(f"{j.get('label')}\n{len(imgs)} images")
    print("  first:", [i["label"] for i in imgs[:3]])
    print("  last: ", [i["label"] for i in imgs[-4:]])
    if len(sys.argv) > 2:
        json.dump({"container": container, "label": j.get("label"), "images": imgs},
                  open(sys.argv[2], "w"), indent=1, ensure_ascii=False)
        print("  ->", sys.argv[2])
