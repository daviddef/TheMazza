#!/usr/bin/env python3
"""The Prostamo of Briatico, and how much of the line is actually evidenced.

The archive's headline claim is eleven generations to 1697. This file exists to
say plainly which of those generations rest on a document and which rest on the
family tree alone — because on 10 September 2026 the same tree was found to be
six years out on two Sicilian births and wrong about where a man died.
"""
import csv, json
rows = list(csv.DictReader(open("data/briatico-prostamo.tsv"), delimiter="\t"))
json.dump(rows, open("site/src/data/briatico-line.json", "w"), indent=1, ensure_ascii=False)
doc = [r for r in rows if r["status"].startswith("DOCUMENTED")]
un = [r for r in rows if r["status"] == "UNTESTED"]
print(f"{len(rows)} generations: {len(doc)} documented, {len(un)} untested, {len(rows)-len(doc)-len(un)} tree-only")
for r in rows:
    print(f"  {r['gen']}. {r['name']:28s} {r['born']:20s} {r['status']}")
