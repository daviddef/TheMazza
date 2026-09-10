#!/usr/bin/env python3
"""Pull the 131 images out of the MyHeritage export before the links die.

The GEDCOM cites every photo as a signed sites-cf.mhcache.com URL carrying an
expiry (e=1789610400 — about 16 September 2026). After that the export is a
list of dead links. So the images come down first, once, and everything else
is built against local copies.

Photos are sorted by whether the person they belong to is dead. The archive
publishes the dead; the living are kept out of the build entirely.
"""
import sys, os, re, json, urllib.request, collections
sys.path.insert(0, os.path.dirname(__file__))
from ged import parse, kid, kids, val

R = parse()
I = {x: v for x, v in R.items() if v["tag"] == "INDI"}

def nm(x):
    n = kid(I[x], "NAME")
    return re.sub(r"\s+", " ", (n["val"] if n else "?").replace("/", " ")).strip()

def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

def birth_year(i):
    for t in ("BIRT", "CHR", "BAPM"):
        e = kid(i, t)
        if e:
            m = re.search(r"\b(1[6-9]\d\d|20\d\d)\b", val(e, "DATE"))
            if m:
                return int(m.group(1))
    return None

def is_dead(i):
    """Dead if the tree says so, or if they would be over 100."""
    if kid(i, "DEAT") or kid(i, "BURI"):
        return True
    y = birth_year(i)
    return bool(y and y < 1926)

manifest, seen = [], set()
for x, i in I.items():
    dead = is_dead(i)
    for n, o in enumerate(kids(i, "OBJE"), 1):
        url = val(o, "FILE")
        if not url.startswith("http"):
            continue
        ext = (re.search(r"\.(jpg|jpeg|png|gif)(?:\?|$)", url, re.I) or [None, "jpg"])[1].lower()
        name = f"{slug(nm(x))}-{n}.{ext}"
        if name in seen:
            name = f"{slug(nm(x))}-{x.strip('@')}-{n}.{ext}"
        seen.add(name)
        manifest.append({
            "xref": x, "person": nm(x), "file": name, "url": url,
            "dead": dead, "size": int(val(o, "_FILESIZE") or 0),
            "rin": val(o, "_PHOTO_RIN"),
        })

for d in ("photos/deceased", "photos/living"):
    os.makedirs(d, exist_ok=True)

ok = fail = skip = 0
for m in manifest:
    dest = os.path.join("photos", "deceased" if m["dead"] else "living", m["file"])
    m["path"] = dest
    if os.path.exists(dest) and os.path.getsize(dest) > 1000:
        skip += 1
        continue
    try:
        req = urllib.request.Request(m["url"], headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as r, open(dest, "wb") as fh:
            fh.write(r.read())
        ok += 1
    except Exception as e:
        m["error"] = str(e)[:120]
        fail += 1

json.dump(manifest, open("data/photo-manifest.json", "w"), indent=1, ensure_ascii=False)
print(f"photos: {ok} fetched, {skip} already present, {fail} failed, {len(manifest)} total")
print("  deceased:", sum(1 for m in manifest if m["dead"]), " living:", sum(1 for m in manifest if not m["dead"]))
