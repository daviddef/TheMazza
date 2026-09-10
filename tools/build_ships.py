#!/usr/bin/env python3
"""Attach the NAA passenger index to the crossings.

The National Archives' passenger arrivals index, 1898-1972, is arranged by
voyage: one item is one ship on one date, and every passenger on it shares the
item ID. That is why two people the tree records arriving at Brisbane on
6 October 1953 turn up in the index at Fremantle on 23 September — same item,
same ship, an earlier port of call. The archive keeps both dates and says which
is which rather than quietly replacing one with the other.
"""
import csv, json

rows = list(csv.DictReader(open("data/naa-ships.tsv"), delimiter="\t"))
people = {p["slug"]: p for p in json.load(open("site/src/data/people.json"))}
out = []
for r in rows:
    if r["slug"] not in people:
        print("  !! no such person:", r["slug"])
        continue
    r["name"] = people[r["slug"]]["name"]
    r["year"] = int(r["naaDate"][-4:])
    out.append(r)
out.sort(key=lambda r: r["year"])
json.dump(out, open("site/src/data/ships.json", "w"), indent=1, ensure_ascii=False)
print(f"{len(out)} crossings with a named ship")
for r in out:
    print(f"  {r['naaDate']:12s} {r['name']:24s} {r['ship']:12s} ex {r['naaFrom']:10s} -> {r['naaPort']:12s} [{r['confidence']}]")
