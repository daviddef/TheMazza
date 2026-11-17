#!/usr/bin/env python3
"""The place links and flags on /corrections/ (kit lib/placelinks.js, kit/tools/placeflags.py).

    python3 ../tools/build_correction_places.py          # from site/

Reads the places that have a page (public/atlas-data.json, `places` with a slug), writes src/data/place-rows.json ({name, href}, one per
place page), runs the kit's placeflags.py over the era snapshot (src/data/era-snapshot.json, with flag-places.json and flag-countries.json as
the ribbon's alias and country tables) into src/data/place-flags.json, and copies only the flag svgs that table names into public/flags/.
A place the snapshot cannot give a flag for keeps its link and has none. Nothing here is a person: the inputs are place names and addresses."""
import json, os, shutil, subprocess, sys

SITE = os.getcwd()
KIT = os.path.join(SITE, "node_modules", "@daviddef", "archive-kit", "kit")
D = os.path.join(SITE, "src", "data")

atlas = json.load(open(os.path.join(SITE, "public", "atlas-data.json"), encoding="utf-8"))
rows = [{"name": p["name"], "href": "/places/%s/" % p["slug"]} for p in atlas["places"] if p.get("slug")]
with open(os.path.join(D, "place-rows.json"), "w", encoding="utf-8") as f:
    json.dump(rows, f, ensure_ascii=False, indent=1); f.write("\n")
r = subprocess.run([sys.executable, os.path.join(KIT, "tools", "placeflags.py"),
                    "--snapshot", os.path.join(D, "era-snapshot.json"), "--places", os.path.join(D, "place-rows.json"),
                    "--alias", os.path.join(D, "flag-places.json"), "--countries", os.path.join(D, "flag-countries.json"),
                    "--out", os.path.join(D, "place-flags.json")], capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip())
if r.returncode:
    sys.exit(r.returncode)
table = json.load(open(os.path.join(D, "place-flags.json"), encoding="utf-8"))
need = set()
for v in table.values():
    if v.get("today"): need.add(v["today"]["svg"])
    for e in v.get("eras") or []: need.add(e[2])
out = os.path.join(SITE, "public", "flags")
shutil.rmtree(out, ignore_errors=True); os.makedirs(out)
for s in sorted(need):
    shutil.copy(os.path.join(KIT, "data", "flags", s), os.path.join(out, s))
print("flags copied: %d" % len(need))
