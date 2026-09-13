#!/usr/bin/env python3
"""Sicily, after a fortnight in Calabria.

The Mazza are the archive's namesake and its oldest unfinished business. The
Calabrian work ran hot for two weeks while Piedimonte Etneo sat untouched. This
is what one afternoon on FamilySearch's full-text and indexed search produced.
"""
import csv, json, collections
rows = list(csv.DictReader(open("data/sicily-reads.tsv"), delimiter="\t"))
json.dump(rows, open("site/src/data/sicily-reads.json", "w"), indent=1, ensure_ascii=False)
c = collections.Counter(r["status"] for r in rows)
print(f"{len(rows)} Sicilian outcomes: " + ", ".join(f"{v} {k}" for k, v in c.most_common()))
for r in rows:
    print(f"  [{r['status']:11s}] {r['who']:34s} {r['what']}")
