#!/usr/bin/env python3
"""Register images read from Antenati, with their citations.

It anchors on the repo root rather than trusting the cwd. It did not, and that
is the small reason it was never wired into the build: npm runs its scripts
from site/, where "data/register-reads.tsv" does not resolve, so adding it to
the chain crashed and the manifest stayed a file nobody built or read.
"""
import csv, json, os

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
rows = list(csv.DictReader(open("data/register-reads.tsv"), delimiter="\t"))
out = [r for r in rows if os.path.exists("site/public/plates/" + r["plate"])]
json.dump(out, open("site/src/data/reads.json", "w"), indent=1, ensure_ascii=False)
print(f"{len(out)} register plates")
for r in out: print("  ", r["plate"], "—", r["title"])
