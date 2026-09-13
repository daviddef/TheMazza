#!/usr/bin/env python3
"""United States census households.

A manifest gives you one person at a time. A census sheet gives you the whole
household in one line -- and for this family it gave five surnames living under
one Manhattan roof that the family tree has no idea were ever in the same room.
"""
import csv, json
rows = list(csv.DictReader(open("data/us-census.tsv"), delimiter="\t"))
for r in rows:
    r["memberList"] = [m.strip() for m in r["members"].split(";")]
    r["arkUrl"] = "https://www.familysearch.org/ark:/61903/" + r["ark"]
json.dump(rows, open("site/src/data/census.json", "w"), indent=1, ensure_ascii=False)
print(f"{len(rows)} census households")
for r in rows:
    print(f"  {r['year']}  {r['head']:16s} {r['place']}  — {len(r['memberList'])} people")
