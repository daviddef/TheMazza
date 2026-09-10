#!/usr/bin/env python3
"""The Polistena at Arneytown — from the VA's Nationwide Gravesite Locator."""
import csv, json
rows = list(csv.DictReader(open("data/arneytown.tsv"), delimiter="\t"))
json.dump(rows, open("site/src/data/arneytown.json", "w"), indent=1, ensure_ascii=False)
print(f"{len(rows)} Arneytown burials")
for r in rows:
    print(f"  {r['name']:20s} {r['rank'] or '—':14s} {r['born']} – {r['died']}  {r['plot']}")
