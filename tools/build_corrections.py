#!/usr/bin/env python3
"""Everything this archive would change in Michael Mazza's family tree.

A research archive that only ever agrees with its source is not doing any work.
This is the list of places where a record and the tree disagree, or where a
record says something the tree does not say at all -- written for the person who
made the tree, with the source for every line so he can check each one himself.

Nothing here has been changed in the tree or in the charts on this site. The
export is drawn exactly as it was given.
"""
import csv, json, collections

rows = list(csv.DictReader(open("data/corrections.tsv"), delimiter="\t"))
ORDER = ["Parentage", "Birth year", "Birth date", "Death date",
         "Death -- missing entirely", "Missing people", "Relationship",
         "Duplicate record", "Crossing date", "Crossing -- ship named",
         "Crossing -- missing entirely", "Port", "Trade -- missing entirely"]
groups = collections.OrderedDict()
for k in ORDER:
    g = [r for r in rows if r["kind"] == k]
    if g:
        groups[k] = g
for r in rows:                                   # anything not in ORDER
    groups.setdefault(r["kind"], []).append(r) if r["kind"] not in ORDER else None

out = {
    "count": len(rows),
    "documented": sum(1 for r in rows if r["confidence"] == "documented"),
    "groups": [{"kind": k, "rows": v} for k, v in groups.items()],
}
json.dump(out, open("site/src/data/corrections.json", "w"), indent=1, ensure_ascii=False)
print(f"{len(rows)} corrections, {out['documented']} documented")
for k, v in groups.items():
    print(f"  {k:30s} {len(v)}")
