#!/usr/bin/env python3
"""What FindMyPast was worth, on a six-day trial that expires 16 September 2026.

Recorded in full, negatives included, because the most useful thing a search
can do for the next person is stop them repeating it. Driven through the site's
own GraphQL endpoint rather than by clicking: POST /titan/marshal/graphql with
recordSearch(filters, order, pageNumber) under root { search { ... } }.
"""
import csv, json, collections
rows = list(csv.DictReader(open("data/findmypast.tsv"), delimiter="\t"))
json.dump(rows, open("site/src/data/findmypast.json", "w"), indent=1, ensure_ascii=False)
c = collections.Counter(r["kind"] for r in rows)
print(f"{len(rows)} FindMyPast outcomes: " + ", ".join(f"{v} {k.lower()}" for k, v in c.most_common()))
for r in rows:
    print(f"  [{r['kind']:13s}] {r['what']}")
