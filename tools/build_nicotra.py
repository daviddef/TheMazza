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
import collections, csv, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(HERE, ".."))

ENTRIES = {"absent", "none", "empty",
           "one", "two", "three", "four", "five", "six", "seven", "—"}
# «six» and «seven» were added on 11 October 2026 for GIARRE MORTI. The
# vocabulary is closed to stop typos, not to cap what a register holds, and
# Giarre's death Tavole are much larger than its marriage ones: 1857 rules five
# N entries and 1860 rules seven. Writing «five» for seven would have been a
# false count dressed as a valid word, which is the one thing a closed
# vocabulary must never be allowed to produce.
# «absent» was added on 9 October 2026 and does NOT mean a Tavola with nothing
# in it. It means THERE IS NO VOLUME: the year was never deposited, so there is
# nothing to read and never will be. Mascali has no 1844 in any restaurazione
# series — not births, deaths, marriages, esposti, processetti or memorandum —
# and antenati-coverage.tsv has said so since 21 September, verified against a
# listing of 498 results and 498 distinct arks with the facets agreeing.
#
# It needed a word of its own because the page was showing nine birth rows
# across a span of ten years and explaining nothing, and because a reader who
# notices the hole has no way to tell a lost volume from an unread one. Those
# are opposite facts: «—» is work outstanding, «absent» is work that cannot be
# done. Counting «absent» as unread would also understate every negative this
# archive has drawn at Mascali for a decade of births.
# «four» and «five» were added on 8 October 2026 when Mascali's death index of
# 1880 turned out to hold five N entries. The vocabulary is closed to force the
# none/empty distinction, not to cap how many a section may hold — so it grows
# when a register says so, and the gate did its job by refusing the build until
# somebody decided that deliberately.
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
# SORT BY YEAR, because /nicotra/ prints each series' span as rows[0].year to
# rows[last].year. That was right only for as long as the TSV happened to be
# hand-written in year order: a single row appended out of order would have
# published a span like «1873-1872» and no gate would have seen it. Sorting
# here makes the page's first-and-last reading true by construction rather
# than by the luck of how the file was typed.
for ser in by_cs.values():
    for rows in ser.values():
        rows.sort(key=lambda r: int(r["year"]))
for rows in by_comune.values():
    rows.sort(key=lambda r: (r["series"], int(r["year"])))

# «absent» is neither read nor outstanding: there is no volume behind it.
read = [r for r in sweeps if r["entries"] not in ("—", "absent")]
absent = [r for r in sweeps if r["entries"] == "absent"]
found = [r for r in sweeps if r["entries"] not in ("—", "absent", "none", "empty")]

_by_surname_pre = collections.Counter(r.get("surname") or "Nicotra" for r in houses)
by_house = {}
for r in houses:
    by_house.setdefault(r["comune"], []).append(r)

json.dump({"line": line, "sweeps": sweeps, "byComune": by_comune, "byComuneSeries": by_cs,
           "households": houses, "housesByComune": by_house,
           "bySurname": dict(_by_surname_pre),
           "read": len(read), "unread": len(sweeps) - len(read) - len(absent),
           "absent": len(absent),
           "withEntries": len(found)},
          open("site/src/data/nicotra.json", "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)

# COUNTED BY THE NAME EACH HOUSEHOLD ACTUALLY CARRIES. This file began as
# Nicotra households only and the page's heading said so by taking its length.
# On 9 October 2026 a MURABITO household was added — Venera Murabito is half
# the name this archive is looking for — and the heading went on saying
# «N Nicotra households» about a list that was no longer all Nicotra. A count
# is only true of the thing it counts.
_by_surname = collections.Counter(r.get("surname") or "Nicotra" for r in houses)
print(f"{_by_surname['Nicotra']} Nicotra households and {_by_surname['Murabito']} Murabito, "
      f"none of them Giovanni's Rosario")
print(f"{len(line)} generations documented; {len(sweeps)} Tavola years listed across "
      f"{len(by_comune)} comuni — {len(read)} read, {len(sweeps)-len(read)-len(absent)} still to "
      f"read, {len(absent)} never deposited, "
      f"{len(found)} holding any N entry at all")
for c, ser in by_cs.items():
    for sname, rows in ser.items():
        r = sum(1 for x in rows if x["entries"] not in ("—", "absent"))
        a = sum(1 for x in rows if x["entries"] == "absent")
        print(f"  {c:10s} {sname:10s} {r}/{len(rows) - a} read"
              + (f"  ({a} year(s) never deposited)" if a else ""))
