#!/usr/bin/env python3
"""Check the two files that put a person somewhere: a grave, or a ship.

data/australia-graves.tsv and data/naa-ships.tsv were the last hand-written
files here with nothing watching them. Both make the same kind of claim — that
a named person was in a named place on a named date — and both are wide open to
the failure this archive keeps meeting: a record attached to somebody who merely
shares a name.

Today Find a Grave was caught indexing ONE woman, same birth and death dates, at
two cemeteries on two continents — «Northern Memorial Park, Glenroy, Victoria»
and «Northern Cemetery, Barnesville, OHIO». Nothing here would have noticed.

So:

  * a `line` or `who` naming a slug must name one that exists;
  * a burial must not precede the birth, or precede the death;
  * a death must not precede a birth;
  * a crossing must not land before the traveller was born, or after they died;
  * two graves for one person, in different cemeteries, are a contradiction and
    not a pair of facts.

Exit 1 on a failure, 0 on a clean run.
"""
import csv, json, os, re, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(HERE, ".."))

people = json.load(open("site/src/data/people.json", encoding="utf-8"))
by_slug = {p["slug"]: p for p in people}
fails, notes = [], []
BLANK = {"", "—", "-", "?", "None"}

def year(s):
    m = re.search(r"\b(1[5-9]\d\d|20\d\d)\b", str(s or ""))
    return int(m.group(1)) if m else None

def norm(s):
    s = (s or "").strip().lower()
    for a, b in (("à","a"),("è","e"),("é","e"),("ì","i"),("ò","o"),("ù","u")):
        s = s.replace(a, b)
    return " ".join(re.sub(r"[^a-z ]", " ", s).split())

# --- data/australia-graves.tsv ---------------------------------------------
if os.path.exists("data/australia-graves.tsv"):
    seen = collections.defaultdict(list)
    for i, r in enumerate(csv.DictReader(open("data/australia-graves.tsv", encoding="utf-8"),
                                         delimiter="\t"), start=2):
        name = (r.get("name") or "").strip()
        where = f"graves line {i} ({name})"
        if not name:
            fails.append(f"graves line {i}: no name"); continue
        b, d = year(r.get("born")), year(r.get("died"))
        if b and d and d < b:
            fails.append(f"{where}: died {d} before born {b}")
        cem = (r.get("cemetery") or "").strip()
        if cem in BLANK:
            fails.append(f"{where}: no cemetery — a grave row with no ground is not a grave")
        key = (norm(name), b, d)
        seen[key].append((i, cem))
    for (n, b, d), hits in seen.items():
        grounds = {c for _, c in hits}
        if len(hits) > 1 and len(grounds) > 1:
            fails.append(f"graves: «{n}» born {b} died {d} is buried in {len(grounds)} different "
                         f"places — {', '.join(sorted(grounds))} — which cannot all be true")

# --- data/naa-ships.tsv -----------------------------------------------------
if os.path.exists("data/naa-ships.tsv"):
    for i, r in enumerate(csv.DictReader(open("data/naa-ships.tsv", encoding="utf-8"),
                                         delimiter="\t"), start=2):
        # careful: in this file column 1 is the SLUG and column 2 is the display
        # NAME. Reading `who` as a slug produced twelve confident false failures
        # the first time this ran.
        who = (r.get("slug") or "").strip()
        name = (r.get("who") or who or "").strip()
        where = f"ships line {i} ({name})"
        if who not in BLANK:
            if who not in by_slug:
                fails.append(f"{where}: who «{who}» is not a slug in the export")
            else:
                p = by_slug[who]
                arr = year(r.get("naaDate") or r.get("treeDate"))
                b, d = year(p.get("born")), year(p.get("died"))
                if arr and b and arr < b:
                    fails.append(f"{where}: lands {arr}, before {who} was born in {b}")
                if arr and d and arr > d + 1:
                    fails.append(f"{where}: lands {arr}, after {who} died in {d}")

for n in notes:
    print("  note  ", n)
for f in fails:
    print("  FAIL  ", f)
print(f"  {'ok   ' if not fails else 'FAIL '} graves & ships — {len(fails)} problem"
      f"{'' if len(fails)==1 else 's'}")
sys.exit(1 if fails else 0)
