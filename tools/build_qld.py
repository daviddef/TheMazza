#!/usr/bin/env python3
"""The Queensland BDM historical index — free, authoritative, and it names parents.

The Registry's index is searchable by the FATHER'S and MOTHER'S names on birth
and death records, which is what makes it powerful here: one search on
"Salvatore Mazza" returns his children's deaths, and each of those names their
mother too. That is how three of Sebastiano Mazza's siblings were found.
"""
import csv, json
rows = list(csv.DictReader(open("data/qld-bdm.tsv"), delimiter="\t"))
json.dump(rows, open("site/src/data/qld-bdm.json", "w"), indent=1, ensure_ascii=False)
print(f"{len(rows)} Queensland registrations")
for r in rows:
    print(f"  {r['date']:22s} {r['type']:9s} {r['name']:26s} {r['reg']:14s} "
          f"f:{r['father']:20s} m:{r['mother']}")
