#!/usr/bin/env python3
"""The gap between an act read and an edge graded.

Work-list row 53. `data/parent-links.tsv` grades a parent edge `read`, `index`
or `line`; anything ungraded falls through to `tree` and the blood-relatives
chart draws it dashed, meaning «the family says so and nothing else does».

Of 746 parent edges in this export, 721 are dashed. Some of those are honest —
no act has ever been read for that person. But some are not: the act HAS been
read, it names the parent, and nobody went back to `parent-links.tsv` to say so.
The chart then tells a reader that a documented descent is hearsay, which is the
same class of error as the audit page that went on calling a disproved negative
«still standing».

This does not grade anything. It cannot: only a person who has read the act
knows whether it names the parent. It lists the CANDIDATES — a person for whom
this archive holds a read record, whose parent edge is still `tree` — so the
gap is visible and finite instead of invisible and assumed empty.

Advisory by default. `--strict` exits 1, for a future where the list is meant
to stay at zero.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(HERE, ".."))

people = json.load(open("site/src/data/people.json", encoding="utf-8"))
by_slug = {p["slug"]: p for p in people}

# «A record has been read for this person» is what build_person_extras already
# works out. But only some records NAME PARENTS, and the first version of this
# tool did not make that distinction: it matched the word «register» inside
# «Brisbane Catholic Cemeteries register» and reported twenty burials as
# gradeable edges. A burial plot names who is buried beside whom; it does not
# name a father. So: civil and church acts in, cemetery and shipping out.
REGISTERISH = ("birth register", "marriage register", "death record",
               "birth record", "marriage record", "birth act", "marriage act",
               "death act", "births", "baptism", "processetti", "documented")
NOT_ACTS = ("cemeter", "burial", "plot", "interment", "passenger", "shipping",
            "naa", "index", "ellis", "manifest", "census")

def has_act(p):
    for r in p.get("records", []) or []:
        k = (r.get("kind") or "").lower()
        w = (r.get("what") or "").lower()
        if any(x in k or x in w for x in NOT_ACTS):
            continue
        if any(x in k or x in w for x in REGISTERISH):
            return r.get("what") or k
    return None

# An edge this archive has DELIBERATELY left ungraded because a record
# contradicts it is not a gap. data/disputed-edges.tsv is that list, and
# reporting its rows here would ask someone to grade a link the archive is
# arguing against.
import csv
DISPUTED = set()
try:
    for r in csv.DictReader(open("data/disputed-edges.tsv", encoding="utf-8"),
                            delimiter="\t"):
        a, b = (r.get("a") or "").strip(), (r.get("b") or "").strip()
        DISPUTED.add((a, b)); DISPUTED.add((b, a))
except FileNotFoundError:
    pass

gaps, graded, nofacts = [], 0, 0
for p in people:
    act = has_act(p)
    for pa in p.get("parents", []) or []:
        via = pa.get("via", "tree")
        if via != "tree":
            graded += 1
            continue
        if (p["slug"], pa["slug"]) in DISPUTED:
            continue
        if not act:
            nofacts += 1
            continue
        gaps.append((p["slug"], p["name"], pa["slug"], pa["name"], act))

print(f"  {graded} parent edge(s) graded; {nofacts} ungraded with no act read "
      f"for the child, which is honest")
if not gaps:
    print("  ok    no edge is dashed for a person whose act this archive has read")
    sys.exit(0)

print(f"  note  {len(gaps)} edge(s) are dashed although an act HAS been read for "
      f"the child — each may or may not name the parent, and only reading it says which:")
for slug, name, pslug, pname, act in sorted(gaps):
    print(f"        {name} → {pname}")
    print(f"            {slug} → {pslug}   ({act[:96]})")

sys.exit(1 if "--strict" in sys.argv else 0)
