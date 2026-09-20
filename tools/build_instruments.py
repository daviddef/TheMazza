#!/usr/bin/env python3
"""The instruments — how this archive reads, as opposed to what it found.

Work-list row 83: «four findings today were about HOW TO READ, not about the
family, and each one will otherwise be rediscovered». It has been more than four
since, and every one of them was learnt twice before it was written down once.

The distinction that makes this worth a page: a FINDING belongs to a person and
lives on /corrections/ or /searched/. An INSTRUMENT belongs to a record series
and will be wanted by whoever reads it next — including the other six archives,
which use the same registers in different towns.

Every row carries a CAUTION, and that field is not optional. An instrument
described without the way it fails is how a method becomes a superstition: the
annual Tavola is the best tool in this archive and it changes its alphabetical
key between adjacent years, which has produced at least one confident, complete
and entirely false negative.

  data/instruments.tsv  ->  site/src/data/instruments.json
"""
import csv, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(HERE, ".."))

rows = list(csv.DictReader(open("data/instruments.tsv", encoding="utf-8"),
                           delimiter="\t"))
fails = [r for r in rows if not (r.get("caution") or "").strip()]
if fails:
    for r in fails:
        print(f"  FAIL  «{r.get('instrument')}» has no caution — an instrument "
              f"described without the way it fails is a superstition")
    sys.exit(1)

out = [{k: (r.get(k) or "").strip() for k in
        ("instrument", "where", "what", "how", "caution")} for r in rows]
json.dump(out, open("site/src/data/instruments.json", "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
print(f"{len(out)} instruments, every one with a caution")
for r in out:
    print(f"  {r['instrument']:38s} {r['where'][:52]}")
