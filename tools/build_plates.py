#!/usr/bin/env python3
"""Register images read from Antenati, with their citations."""
import csv, json, os
rows = list(csv.DictReader(open("data/register-reads.tsv"), delimiter="\t"))
out = [r for r in rows if os.path.exists("site/public/plates/" + r["plate"])]
json.dump(out, open("site/src/data/reads.json", "w"), indent=1, ensure_ascii=False)
print(f"{len(out)} register plates")
for r in out: print("  ", r["plate"], "—", r["title"])
