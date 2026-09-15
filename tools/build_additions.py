#!/usr/bin/env python3
"""People the records prove and the family tree does not contain.

Every other page here works from Michael Mazza's export. This one does not: it
holds people who are NOT in the export and who the registers nevertheless place
in the direct line of Mia and Rocco. They cannot be drawn on the charts, because
the charts draw the tree as given -- so they are listed here instead, with the
act that names each one.
"""
import csv, json, os

# the build runs from site/, so anchor on the repo root
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
rows = list(csv.DictReader(open("data/documented-additions.tsv", encoding="utf-8"), delimiter="\t"))
json.dump(rows, open("site/src/data/additions.json", "w"), indent=1, ensure_ascii=False)
absent = [r for r in rows if (r.get("inTree") or "\u2014") == "\u2014"]
print(f"{len(rows)} documented people — {len(absent)} absent from the family tree, "
      f"{len(rows) - len(absent)} in it but without their dates or parents")
for r in rows:
    where = "" if r in absent else f"  [in the tree as {r['inTree']}]"
    print(f"  gen {r['gen']}  {r['name']:26s} b.{r['born']:20s} {r['trade']}{where}")
