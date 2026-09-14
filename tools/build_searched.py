#!/usr/bin/env python3
"""The negative-results page: what was searched, and what it did not turn up.

A source that returned nothing is evidence too — it is the difference between
"we have not looked" and "it is not there". data/searched.tsv is the record;
this writes it out for the site.
"""
import csv, json, os

# the build runs this from site/, so anchor on the repo root
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
rows = list(csv.DictReader(open("data/searched.tsv", encoding="utf-8"), delimiter="\t"))
json.dump(rows, open("site/src/data/searched.json", "w"), indent=1, ensure_ascii=False)
done = [r for r in rows if r["status"] == "done"]
print(f"{len(rows)} searches: {len(done)} done, {len(rows)-len(done)} outstanding")
