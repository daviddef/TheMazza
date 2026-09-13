#!/usr/bin/env python3
"""People the records prove and the family tree does not contain.

Every other page here works from Michael Mazza's export. This one does not: it
holds people who are NOT in the export and who the registers nevertheless place
in the direct line of Mia and Rocco. They cannot be drawn on the charts, because
the charts draw the tree as given -- so they are listed here instead, with the
act that names each one.
"""
import csv, json
rows = list(csv.DictReader(open("data/documented-additions.tsv"), delimiter="\t"))
json.dump(rows, open("site/src/data/additions.json", "w"), indent=1, ensure_ascii=False)
print(f"{len(rows)} documented people absent from the family tree")
for r in rows:
    print(f"  gen {r['gen']}  {r['name']:26s} b.{r['born']:20s} {r['trade']}")
