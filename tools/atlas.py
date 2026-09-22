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
    # The bare comune names matter now that places can arrive from
    # documented-additions, where the `place` column holds «Zambrone» and not
    # «Zambrone, Vibo Valentia». Without them Zambrone fell through to «other»
    # and drew grey in the middle of Calabria.
    s = p.lower()
    if re.search(r"sicil|catania|piedimonte|messina|palermo|"
                 r"mascali|giarre|riposto|fiumefreddo|linguaglossa", s):  return "sicily"
    if re.search(r"calabria|briatico|scilla|vibo|reggio|"
                 r"zambrone|pizzo|potenzoni|san costantino", s):          return "calabria"
    if re.search(r"queensland|australia|brisbane|nudgee", s):          return "au"
    if re.search(r"new york|america|ellis|united states|argentin", s): return "away"
    return "other"

# THREE QUESTIONS OF THE SAME GROUND — 21 September 2026.
#
# This archive asked all three and could answer only one on the map. The kit's
# Atlas has carried a `schemes` prop since Defranceschi's layer model was
# promoted into it, and no archive in the estate had ever passed it.
#
# people  where a named person can be put — the category this file always had
# shelf   how far the registers of a comune have been got through, out of
#         coverage.json, which is keyed on `comune` and lands on 12 of its 13
# ground  where somebody is actually buried, out of burials.json, 18 of whose
#         20 rows land on a place this map already draws
#
# A place answering more than one takes the colour of the RAREST it answers,
# counted off the data by the component rather than declared here — so the
# burial is the thing worth seeing and the shelf is the ground it sits on.
SHELF = {"open": "shelf-open", "partial": "shelf-part",
         "route": "shelf-route", "gap": "shelf-gap"}

# A comune has one row PER SERIES, so most have several and they disagree.
# Piedimonte Etneo has six `open` and one `route`; Scilla has three `open`.
# THE FIRST VERSION OF THIS SIMPLY OVERWROTE, so a comune's colour was decided
# by whichever row happened to sit last in the TSV. It read correctly for all
# seven comuni on the day it was written and would have turned Piedimonte green
# the moment somebody appended an `open` row beneath its `route` one -- a silent
# change of meaning caused by the order of a data file, which is the exact class
# of failure this archive spends its time cataloguing.
#
# THE WORST STATUS WINS, and the ranking is build_coverage.py's own vocabulary:
#   gap      a real hole in the holding -- nothing will ever be there
#   partial  the listing itself is incomplete, so NOTHING IS SETTLED
#   route    reachable, but through a different archive -- a known errand
#   open     reachable now
# `route` sits ABOVE `partial` because a named errand beats not knowing what you
# are looking at. The shelf answers «how far have we got», and one hole means
# you have not got all the way.
WORST = {"shelf-gap": 0, "shelf-part": 1, "shelf-route": 2, "shelf-open": 3}

def head(s):
    return str(s or "").split(",")[0].strip().lower()

def layers():
    """place-head -> {scheme: cat}, and the counts that go with them."""
    cats, ns = {}, {}
    # coverage.json is {rows, held}; burials.json is a bare list. Read the
    # shape rather than assume one — they were written by different scripts.
    cov = J("coverage.json")
    cov = cov if isinstance(cov, list) else (cov.get("rows") or [])
    for r in cov:
        h = head(r.get("comune"))
        if not h:
            continue
        cat = SHELF.get(r.get("status"), "shelf-part")
        have = cats.setdefault(h, {}).get("shelf")
        if have is None or WORST[cat] < WORST[have]:
            cats[h]["shelf"] = cat
    buried = {}
    bur = J("burials.json")
    bur = bur if isinstance(bur, list) else (bur.get("rows") or [])
    for r in bur:
        h = head(r.get("place"))
        if not h:
            continue
        buried[h] = buried.get(h, 0) + 1
    for h, n in buried.items():
        cats.setdefault(h, {})["ground"] = "ground"
        ns.setdefault(h, {})["ground"] = n

    # THE DOCUMENTED, work-list row 176. Every other layer here is keyed on the
    # EXPORT's people, and the archive's best-evidenced people are not in the
    # export: 114 rows of documented-additions.tsv, every one added from a
    # register this archive opened. They were invisible on this map, which meant
    # ZAMBRONE -- a comune with a read register run and a recorded gap in its
    # deaths -- had no marker at all, because no exported person is placed there.
    #
    # They are drawn from the `place` column, which is NOT derived from `source`:
    # the source names the comune of the RECORD, and the two come apart exactly
    # where it matters. Rosario Nicotra is named in a PIEDIMONTE act and was a
    # MASCALI man, and the act says so in the same line. A blank `place` is «not
    # recorded» and is skipped, never guessed at.
    docs = {}
    for r in J("additions.json"):
        h = head(r.get("place"))
        if not h or h in BLANK:
            continue
        docs[h] = docs.get(h, 0) + 1
    for h, n in docs.items():
        cats.setdefault(h, {})["documented"] = "documented"
        ns.setdefault(h, {})["documented"] = n
    return cats, ns


# A place whose ONLY claim on the map is that documented people belong to it has
# no row in places.json, because that file is built from the export. These are
# the names to draw anyway, with the label the coverage table already uses so a
# reader meets one spelling per comune.
BLANK = {"", "—", "-", "?"}

def doc_only_places():
    """head -> display name, for comuni that exist only in documented-additions."""
    out = {}
    for r in J("additions.json"):
        p = (r.get("place") or "").strip()
        if p in BLANK:
            continue
        out.setdefault(head(p), p)
    return out


def main():
    places = J("places.json")
    ppl = {p["slug"]: p for p in J("people.json") if p.get("slug")}
    extra, extraN = layers()
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
        # The layers, attached on the same head() the roster attaches on, so a
        # place cannot be pinned correctly and lose its layer (work-list 158).
        h = head(name)
        c = dict(extra.get(h) or {})
        if slugs:
            c["people"] = cat(name)
        if c:
            rows[-1]["cats"] = c
            n2 = dict(extraN.get(h) or {})
            if slugs:
                n2["people"] = len(slugs)
            rows[-1]["ns"] = n2

    # Comuni that exist ONLY because documented people belong to them. Without
    # this, Zambrone, Mascali, Giarre and Riposto have no marker: places.json is
    # built from the export and the export has nobody there. Row 176.
    drawn = {head(r["_lookup"]) for r in rows}
    adds = J("additions.json")
    for h, name in sorted(doc_only_places().items()):
        if h in drawn:
            continue
        who = [r for r in adds if head(r.get("place") or "") == h]
        rows.append({
            "name": name.split(",")[0].strip() or name,
            "_lookup": name, "cat": cat(name),
            "n": 0, "when": "",
            "what": f"{len(who)} documented, none in the family tree",
            "people": [], "more": None,
            "cats": dict(extra.get(h) or {}),
            "ns": dict(extraN.get(h) or {}),
        })
    atlasdata.build(rows, OUT, gaz=gazetteer(), countries=["Italia","Italy","Australia","United States","Argentina","United Kingdom","Indonesia","Fiji","South Africa","Suid-Afrika","Österreich","Austria"])

if __name__ == "__main__":
    sys.exit(main())
