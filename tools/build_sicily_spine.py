#!/usr/bin/env python3
"""The Mazza surname line, as the Sicilian registers now give it.

Before 10 September 2026 this line was four generations deep and stopped at a
Rosario Mazza with no dates and no source. It now runs from Mariano Mazza,
named in his grandson's act of birth, to two children born in Brisbane.
"""
import csv, json
rows = list(csv.DictReader(open("data/mazza-spine-sicily.tsv"), delimiter="\t"))
json.dump(rows, open("site/src/data/sicily-spine.json", "w"), indent=1, ensure_ascii=False)
print(f"{len(rows)} generations on the Mazza name")
for r in rows:
    print(f"  {r['gen']}. {r['name']:44s} {r['born']:18s} {('x '+r['spouse']) if r['spouse']!='—' else ''}")
