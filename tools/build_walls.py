#!/usr/bin/env python3
"""Where each quarter stops, and why it stops there.

Four quarters, four walls, four different causes — and until today they existed
only scattered across searched.tsv, scilla-reads.tsv, the additions and four
separate commit messages. A wall established by reading is a finding; a wall
assumed from silence is a shrug, and the difference is the whole argument of
this archive. So it is written down as a record with its evidence attached.
"""
import csv, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(HERE, ".."))
rows = list(csv.DictReader(open("data/walls.tsv", encoding="utf-8"), delimiter="\t"))
json.dump(rows, open("site/src/data/walls.json", "w"), indent=1, ensure_ascii=False)
print(f"{len(rows)} walls, all established by reading")
for r in rows:
    print(f"  {r['quarter']:22s} stops at {r['person']:20s} ({r['born']})")
