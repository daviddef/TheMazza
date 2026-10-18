#!/usr/bin/env python3
"""The place table behind the "at the time" notes: which Record Atlas region each place on a person's page belongs to.

THE DECISION IS data/era-ground.tsv, written by hand: one row per place string exactly as people.json prints it, with the Atlas
region it belongs to, or '-' for "looked at, and no region covers it", and the reason. This tool turns those rows into
site/src/data/era-places.json (each mapped place with the coordinates the gazetteer holds for it, which erasnap.py uses to refuse a
town the Atlas's approximate ring would give to its neighbour) and refuses to pass when the rows and the data disagree:

    python3 ../tools/build_era.py                       write src/data/era-places.json
    python3 ../tools/build_era.py --check               build gate: the file is what the rows build, every place in a
                                                        non-living person's events has a row, and no row is stale
    python3 ../tools/build_era.py --snapshot <Record Atlas>/site/public/regions.json
                                                        also rebuild src/data/era-snapshot.json from that Atlas file (the
                                                        deliberate refresh: nothing in a build ever reads the Atlas)

Only places of people who are NOT living are read: a living person's page prints a town and a country and no event, and
the notes are never drawn there.
"""
import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(HERE, "..", "site")
KIT_TOOLS = os.path.join(SITE, "node_modules", "@daviddef", "archive-kit", "kit", "tools")
sys.path.insert(0, KIT_TOOLS)
import geocode  # noqa: E402

DATA = os.path.join(SITE, "src", "data")
GROUND = os.path.join(HERE, "..", "data", "era-ground.tsv")
LOCAL_GAZ = os.path.join(HERE, "..", "data", "gazetteer-local.json")
OUT = os.path.join(DATA, "era-places.json")
SNAP = os.path.join(DATA, "era-snapshot.json")


def ground():
    rows = {}
    for line in open(GROUND, encoding="utf-8"):
        if line.startswith("#") or not line.strip() or line.startswith("place\t"):
            continue
        place, region, why = (line.rstrip("\n").split("\t") + ["", "", ""])[:3]
        if not place or not region or not why:
            raise SystemExit("era-ground.tsv: a row needs a place, a region (or '-') and a reason: %r" % line[:60])
        if place in rows:
            raise SystemExit("era-ground.tsv: a place appears twice (a row must say one thing)")
        rows[place] = (region, why)
    return rows


def event_places():
    out = {}
    for p in json.load(open(os.path.join(DATA, "people.json"), encoding="utf-8")):
        if p.get("living"):
            continue
        for e in p.get("events") or []:
            if e.get("place"):
                out[e["place"]] = out.get(e["place"], 0) + 1
    return out


def gazetteer():
    gaz = geocode.load()
    try:
        for k, v in json.load(open(LOCAL_GAZ, encoding="utf-8")).items():
            if not k.startswith("_"):
                gaz[k] = v
    except FileNotFoundError:
        pass
    return gaz


def spellings():
    """place-spellings.tsv: a name as written -> the name the gazetteer knows (applied until nothing changes)."""
    out = {}
    path = os.path.join(HERE, "..", "data", "place-spellings.tsv")
    for line in open(path, encoding="utf-8").read().splitlines()[1:]:
        cols = line.split("\t")
        if len(cols) >= 2 and cols[0]:
            out[cols[0]] = cols[1]
    return out


def locate(place, gaz, fixes, rows):
    """A coordinate for the ring cross-check: the name as written; then as place-spellings.tsv corrects it; then another place of this
    archive with the same first segment, sent to the same region (a bare «Pizzo» takes the coordinate of «Pizzo, Vibo Valentia, Calabria»)."""
    hit = geocode.find(place, gaz)
    name = place
    for _ in range(3):
        if hit:
            return hit
        if name not in fixes:
            break
        name = fixes[name]
        hit = geocode.find(name, gaz)
    head = place.split(",")[0].strip().lower()
    for other in sorted(rows):
        if other != place and rows[other][0] == rows[place][0] and other.split(",")[0].strip().lower() == head:
            hit = geocode.find(other, gaz)
            if hit:
                return hit
    return None


def build():
    rows = ground()
    used = event_places()
    gaz = gazetteer()
    fixes = spellings()
    table = {}
    for place in sorted(rows):
        region, _ = rows[place]
        if region == "-":
            table[place] = None
            continue
        hit = locate(place, gaz, fixes, rows)
        table[place] = {"region": region}
        if hit and isinstance(hit.get("lat"), (int, float)) and isinstance(hit.get("lon"), (int, float)):
            table[place].update(lat=round(hit["lat"], 4), lon=round(hit["lon"], 4))
    return rows, used, table


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--snapshot", default=None, help="a local copy of the Record Atlas's regions.json: also rebuild era-snapshot.json")
    a = ap.parse_args()
    rows, used, table = build()
    missing = sorted(set(used) - set(rows))
    stale = sorted(set(rows) - set(used))
    out = {"_about": "Built by tools/build_era.py from data/era-ground.tsv. Place as printed -> {region, lat, lon}, or null where no Atlas region "
                     "covers it. Read by kit erasnap.py.", "places": table}
    text = json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    if a.check:
        bad = False
        if missing:
            print("  FAIL  era-ground  %d place string(s) in a non-living person's events have no row in data/era-ground.tsv "
                  "(decide a region, or '-', for each)" % len(missing))
            bad = True
        if stale:
            print("  FAIL  era-ground  %d row(s) in data/era-ground.tsv match no event place (stale)" % len(stale))
            bad = True
        try:
            have = open(OUT, encoding="utf-8").read()
        except OSError:
            have = None
        if have != text:
            print("  FAIL  era-ground  site/src/data/era-places.json is not what the rows build (run tools/build_era.py)")
            bad = True
        if not bad:
            mapped = sum(1 for v in table.values() if v)
            print("  ok    era-ground  %d place strings decided (%d mapped to a region, %d to none); the table matches" % (len(table), mapped, len(table) - mapped))
        return 1 if bad else 0
    open(OUT, "w", encoding="utf-8").write(text)
    print("era-places.json: %d place strings (%d mapped)" % (len(table), sum(1 for v in table.values() if v)))
    if missing:
        print("  WARNING %d place string(s) in events have no row in data/era-ground.tsv" % len(missing))
        return 1
    if a.snapshot:
        r = subprocess.run([sys.executable, os.path.join(KIT_TOOLS, "erasnap.py"), "--atlas", a.snapshot, "--places", OUT, "--out", SNAP])
        return r.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main())
