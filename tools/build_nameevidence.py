#!/usr/bin/env python3
"""Evidence, from the registers, that the unmerged names really are different people.

The archive's oldest rule is that it will not merge two records on a shared name.
That has always been stated as a principle. After a fortnight in the Scilla
registers it can be stated as a FINDING instead -- here are the actual people the
registers hold behind each of these names, including one couple who gave two of
their own sons the same name.
"""
import csv, json
rows = list(csv.DictReader(open("data/name-evidence.tsv"), delimiter="\t"))
json.dump({r["name"]: r["evidence"] for r in rows},
          open("site/src/data/name-evidence.json", "w"), indent=1, ensure_ascii=False)
print(f"{len(rows)} names now carry register evidence for staying unmerged")
for r in rows:
    print(f"  {r['name']}")
