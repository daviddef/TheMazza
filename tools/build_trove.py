#!/usr/bin/env python3
"""The Trove gazette and archive findings, for the Queensland page.

WHY THIS EXISTS AT ALL. data/trove-gazette.tsv was written on 27 September and
then sat there: no builder, no JSON, no page. The seven names in it existed
only inside two prose paragraphs on /searched/ and /worklist/.

That is the SAME FAULT this archive diagnosed and fixed for plates the same
morning — a manifest nobody consumes is indistinguishable from no manifest —
and it was committed within hours of writing the check that catches it. A
check only guards the thing it was pointed at.

  data/trove-gazette.tsv  ->  site/src/data/trove.json
"""
import csv, json, os, sys

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

rows = list(csv.DictReader(open("data/trove-gazette.tsv", encoding="utf-8"), delimiter="\t"))

fails = []
for r in rows:
    if not (r.get("gazetted") or "").strip():
        fails.append(f"  FAIL  {r.get('surname')} {r.get('given')}: no gazette date")
    if not (r.get("note") or "").strip():
        fails.append(f"  FAIL  {r.get('surname')} {r.get('given')}: no note — a name and a date is "
                     f"not a finding until something says what it is and is not")
if fails:
    print("\n".join(fails)); sys.exit(1)

new = [r for r in rows if (r.get("inTree") or "—").strip() == "—"]
json.dump({"rows": rows, "new": len(new), "candidates": len(rows) - len(new)},
          open("site/src/data/trove.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(f"{len(rows)} Trove gazette entries — {len(new)} name(s) absent from the export, "
      f"{len(rows)-len(new)} matching someone already in it")
