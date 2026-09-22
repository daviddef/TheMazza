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
  nicotra-sweeps.tsv  every year read at the N section of a Tavola — `series`
                      says which register it came out of — with
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
# Which series the Tavola came out of. It started as births only, and the
# moment marriages were added a row saying «Riposto 1838, one» meant two
# different things depending on a column that did not exist. A closed
# vocabulary rather than free text, for the same reason `entries` is one.
SERIES = {"Nati", "Matrimoni", "Morti"}

line = list(csv.DictReader(open("data/nicotra-line.tsv", encoding="utf-8"), delimiter="\t"))
sweeps = list(csv.DictReader(open("data/nicotra-sweeps.tsv", encoding="utf-8"), delimiter="\t"))
# The households the sweeps turned up. Not one of them is GIOVANNI'S Rosario,
# which is the whole point of keeping them: they show the surname IS in these
# towns, in ordinary untitled families. Giarre 1820 does hold a «Nicotra
# Rosario», and the file says in its own note why the generation is wrong —
# that distinction is the reason `note` is required on every row.
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
    sr = (r.get("series") or "").strip()
    if sr not in SERIES:
        fails.append(f"  FAIL  {r.get('comune')} {r.get('year')}: series «{sr}» is not one of {sorted(SERIES)}")
    if not (r.get("note") or "").strip():
        fails.append(f"  FAIL  {r.get('comune')} {r.get('year')}: no note — «{e}» on its own is not a reading")
if fails:
    print("\n".join(fails))
    sys.exit(1)

by_comune = {}
for r in sweeps:
    by_comune.setdefault(r["comune"], []).append(r)
# comune -> series -> rows, so a page can show the birth sweep and the
# marriage sweep as the two different arguments they are.
by_cs = {}
for r in sweeps:
    by_cs.setdefault(r["comune"], {}).setdefault(r["series"], []).append(r)

read = [r for r in sweeps if r["entries"] != "—"]
found = [r for r in sweeps if r["entries"] not in ("—", "none", "empty")]

by_house = {}
for r in houses:
    by_house.setdefault(r["comune"], []).append(r)

json.dump({"line": line, "sweeps": sweeps, "byComune": by_comune, "byComuneSeries": by_cs,
           "households": houses, "housesByComune": by_house,
           "read": len(read), "unread": len(sweeps) - len(read),
           "withEntries": len(found)},
          open("site/src/data/nicotra.json", "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)

print(f"{len(houses)} Nicotra households found, none of them Giovanni's Rosario")
print(f"{len(line)} generations documented; {len(sweeps)} Tavola years listed across "
      f"{len(by_comune)} comuni — {len(read)} read, {len(sweeps)-len(read)} still to read, "
      f"{len(found)} holding any N entry at all")
for c, ser in by_cs.items():
    for sname, rows in ser.items():
        r = sum(1 for x in rows if x["entries"] != "—")
        print(f"  {c:10s} {sname:10s} {r}/{len(rows)} read")
