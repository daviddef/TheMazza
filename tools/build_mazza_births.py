#!/usr/bin/env python3
"""The Mazza births actually found in the Sicilian civil registers."""
import csv, json
rows = list(csv.DictReader(open("data/pe-mazza-births.tsv"), delimiter="\t"))
for r in rows:
    r["found"] = r["name"] != "(none)"
json.dump(rows, open("site/src/data/mazza-births.json", "w"), indent=1, ensure_ascii=False)
found = [r for r in rows if r["found"]]
print(f"{len(rows)} year/comune index reads, {len(found)} Mazza births found")
for r in rows:
    print(f"  {r['year']} {r['comune']:18s} {r['act'] or '—':>4}  {r['name']:18s} {('f. '+r['father']+' '+r['fatherAge']) if r['father'] != '—' else ''}")
