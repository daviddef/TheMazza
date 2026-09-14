#!/usr/bin/env python3
"""Australian graves for the Calabrian half of the family.

Nudgee holds the Mazza. The Prostamo are somewhere else entirely — Mount
Gravatt, Nerang, and a Melbourne cemetery this archive did not know about —
which is itself a finding about how the two halves of the family settled.
"""
import csv, json, os

# the build runs this from site/, so anchor on the repo root
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
rows = list(csv.DictReader(open("data/australia-graves.tsv", encoding="utf-8"), delimiter="\t"))
json.dump(rows, open("site/src/data/australia-graves.json", "w"), indent=1, ensure_ascii=False)
by = {}
for r in rows:
    by.setdefault(r["line"], []).append(r)
print(f"{len(rows)} graves: " + ", ".join(f"{k} {len(v)}" for k, v in by.items()))
for r in rows:
    print(f"  {r['name']:42s} {r['died']:20s} {r['cemetery']}")
