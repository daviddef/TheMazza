#!/usr/bin/env python3
"""The American manifests.

Two men this archive could not find in Italian registers left records in
America, and American arrival manifests carry an AGE. That is the whole point:
an age converts to a birth year, and a birth year is the thing the family tree
keeps getting wrong.

The Statue of Liberty & Ellis Island Foundation's Arrival Records Collection is
free and needs no account for the index. Its rows carry a FamilySearch image ark
for the manifest page itself, which does need one.
"""
import csv, json

rows = list(csv.DictReader(open("data/ellis-island.tsv"), delimiter="\t"))
cohort = list(csv.DictReader(open("data/ellis-cohort.tsv"), delimiter="\t"))

for r in rows:
    r["arkUrl"] = ("https://www.familysearch.org/ark:/61903/" + r["ark"]) if r["ark"] else ""

json.dump({"rows": rows, "cohort": cohort},
          open("site/src/data/ellis.json", "w"), indent=1, ensure_ascii=False)

print(f"{len(rows)} manifest lines recorded, {sum(int(c['count']) for c in cohort)} in the cohort sweeps")
for r in rows:
    print(f"  {r['name']:22s} {r['arrived']:>16s}  age {r['age']:>2s} -> b.{r['birthYear']}  {r['ship']}")
