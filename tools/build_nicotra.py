#!/usr/bin/env python3
"""The Nicotra line, and the year-by-year sweeps that have not found him.

WHY THIS EXISTS. It was written into three page templates first, and the kit's
`checkinline` refused the build: «6 list(s) of evidence in a template, and the
ratchet is 5 — this number may only go down». That check is right and it caught
me doing the thing this archive tells everybody else not to do. Evidence in a
template is evidence nobody can count, nobody can re-sort, and nobody can find
without opening a `.astro` file.

Two files, because they answer two different questions:

  nicotra-line.tsv    the descent, as four acts give it — gen, who, what, source
  nicotra-sweeps.tsv  every year read at the N section of a birth Tavola, with
                      what was in it. `entries` is a WORD, not a number, because
                      the distinctions matter and a count would lose them:
                        none   — the alphabet has no N section at all
                        empty  — the N heading is WRITTEN and left blank
                        —      — not read yet
                      «none» and «empty» look identical in a summary and are not
                      the same fact: the second proves the clerk wrote the
                      heading when he had anything to put under it.

  data/nicotra-*.tsv  ->  site/src/data/nicotra.json
"""
import csv, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(HERE, ".."))

ENTRIES = {"none", "empty", "one", "two", "three", "—"}

line = list(csv.DictReader(open("data/nicotra-line.tsv", encoding="utf-8"), delimiter="\t"))
sweeps = list(csv.DictReader(open("data/nicotra-sweeps.tsv", encoding="utf-8"), delimiter="\t"))
# The households the sweeps turned up. Not one of them is Rosario's, which is
# the whole point of keeping them: they show the surname IS in these towns.
houses = list(csv.DictReader(open("data/nicotra-households.tsv", encoding="utf-8"), delimiter="\t"))

fails = []
for r in line:
    if not (r.get("gen") or "").strip().isdigit():
        fails.append(f"  FAIL  «{r.get('who','')[:40]}» has no numeric gen")
    if not (r.get("src") or "").strip():
        fails.append(f"  FAIL  «{r.get('who','')[:40]}» has no source — a line without an act is a tree, not a line")
for r in sweeps:
    e = (r.get("entries") or "").strip()
    if e not in ENTRIES:
        fails.append(f"  FAIL  {r.get('comune')} {r.get('year')}: entries «{e}» is not one of {sorted(ENTRIES)}")
    if not (r.get("note") or "").strip():
        fails.append(f"  FAIL  {r.get('comune')} {r.get('year')}: no note — «{e}» on its own is not a reading")
if fails:
    print("\n".join(fails))
    sys.exit(1)

by_comune = {}
for r in sweeps:
    by_comune.setdefault(r["comune"], []).append(r)

read = [r for r in sweeps if r["entries"] != "—"]
found = [r for r in sweeps if r["entries"] not in ("—", "none", "empty")]

by_house = {}
for r in houses:
    by_house.setdefault(r["comune"], []).append(r)

json.dump({"line": line, "sweeps": sweeps, "byComune": by_comune,
           "households": houses, "housesByComune": by_house,
           "read": len(read), "unread": len(sweeps) - len(read),
           "withEntries": len(found)},
          open("site/src/data/nicotra.json", "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)

print(f"{len(houses)} Nicotra households found, none of them Rosario's")
print(f"{len(line)} generations documented; {len(sweeps)} birth years listed across "
      f"{len(by_comune)} comuni — {len(read)} read, {len(sweeps)-len(read)} still to read, "
      f"{len(found)} holding any N entry at all")
for c, rows in by_comune.items():
    r = sum(1 for x in rows if x["entries"] != "—")
    print(f"  {c:10s} {r}/{len(rows)} read")
