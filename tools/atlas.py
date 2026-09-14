#!/usr/bin/env python3
"""Mazza's places, for the map.

This list is the richest of the four: every place already carries who was born,
who died and who was buried there, the first and last year it appears, and the
slugs of the people themselves.
"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "site", "node_modules",
                                "@daviddef", "archive-kit", "kit", "tools"))
import atlasdata
import geocode as _geocode
D = os.path.join(HERE, "..", "site", "src", "data")
LOCAL_GAZ = os.path.join(HERE, "..", "data", "gazetteer-local.json")


def gazetteer():
    """The estate gazetteer, plus the handful of places only this archive needs.

    The kit keeps the shared list and its own overrides; anything peculiar to the
    Mazza -- a Calabrian comune too small to be in the estate file -- goes in
    data/gazetteer-local.json rather than into the shared kit, with the reason
    beside it.
    """
    gaz = _geocode.load()
    try:
        local = json.load(open(LOCAL_GAZ, encoding="utf-8"))
    except FileNotFoundError:
        return gaz
    for k, v in local.items():
        if not k.startswith("_"):
            gaz[k] = v
    return gaz
J = lambda n: json.load(open(os.path.join(D, n), encoding="utf-8"))
OUT = os.path.join(HERE, "..", "site", "public", "atlas-data.json")

def cat(p):
    s = p.lower()
    if re.search(r"sicil|catania|piedimonte|messina|palermo", s):      return "sicily"
    if re.search(r"calabria|briatico|scilla|vibo|reggio", s):          return "calabria"
    if re.search(r"queensland|australia|brisbane|nudgee", s):          return "au"
    if re.search(r"new york|america|ellis|united states|argentin", s): return "away"
    return "other"

def main():
    places = J("places.json")
    ppl = {p["slug"]: p for p in J("people.json") if p.get("slug")}
    rows = []
    for p in places:
        name = p["name"]
        slugs, seen = [], set()
        for s in (p.get("who") or []):
            if s not in seen:
                seen.add(s); slugs.append(s)
        bits = [f"{p[k]} {k}" for k in ("born", "died", "buried", "lived") if p.get(k)]
        span = (f"{p['first']}–{p['last']}" if p.get("first") and p.get("last")
                else str(p.get("first") or ""))
        rows.append({
            "name": name.split(",")[0].strip() or name,
            "_lookup": name, "cat": cat(name),
            "n": len(slugs), "when": span,
            "what": ", ".join(bits) if bits else name,
            "people": [{"n": (ppl.get(s) or {}).get("name") or s.replace("-", " ").title(),
                        "w": f"/people/{s}/"} for s in slugs[:12]],
            "more": max(0, len(slugs) - 12) or None,
        })
    atlasdata.build(rows, OUT, gaz=gazetteer(), countries=["Italia","Italy","Australia","United States","Argentina","United Kingdom","Indonesia","Fiji","South Africa","Suid-Afrika","Österreich","Austria"])

if __name__ == "__main__":
    sys.exit(main())
