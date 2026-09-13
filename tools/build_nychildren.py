#!/usr/bin/env python3
"""The New York children of Rocco Arena and Generosa Costa.

The family tree has this couple leaving Scilla and coming back. It does not have
the four children the New York City birth register gives them in between -- three
of whom it does not know existed at all, and one of whom died at seventeen months.
"""
import csv, json
rows = list(csv.DictReader(open("data/ny-children.tsv"), delimiter="\t"))
json.dump(rows, open("site/src/data/ny-children.json", "w"), indent=1, ensure_ascii=False)
new = [r for r in rows if r["inTree"] == "NO"]
print(f"{len(rows)} New York births; {len(new)} absent from the family tree")
for r in rows:
    print(f"  {r['name']:20s} {r['born']:20s} {'' if r['inTree']=='yes' else '<- NOT IN TREE'}")
