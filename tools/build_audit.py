#!/usr/bin/env python3
"""The audit of this archive's own negatives — TSV to JSON.

`site/src/data/audit-negatives.json` has been on the site since the audit was
written and NOTHING HAS EVER REGENERATED IT. It was produced once, by hand, and
`data/audit-negatives.tsv` has sat beside it as a file that looks authoritative
and reaches nobody. So when a negative on that page was later PROVEN WRONG —
Filippo Arena's marriage, found at Scilla in 1815 on 20 September — the page went
on calling it «still standing».

That is the worst failure mode an evidence-first archive has: not a wrong
finding, but a right finding that never arrives. This closes it.

  data/audit-negatives.tsv  ->  site/src/data/audit-negatives.json

Columns: who, window, setBy, yearsRead, outcome, missBy, note.
`outcome` is WRONG (the negative has since been disproved) or STANDING.
"""
import csv, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(HERE, ".."))

rows = list(csv.DictReader(open("data/audit-negatives.tsv", encoding="utf-8"),
                           delimiter="\t"))

OK = {"WRONG", "STANDING"}
bad = [r for r in rows if (r.get("outcome") or "").strip() not in OK]
if bad:
    for r in bad:
        print(f"  FAIL  «{r.get('who')}»: outcome «{r.get('outcome')}» is not WRONG or STANDING")
    sys.exit(1)

out = [{k: (r.get(k) or "").strip() for k in
        ("who", "window", "setBy", "yearsRead", "outcome", "missBy", "note")}
       for r in rows]

json.dump(out, open("site/src/data/audit-negatives.json", "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)

wrong = [r for r in out if r["outcome"] == "WRONG"]
print(f"{len(out)} negatives audited — {len(wrong)} since proven wrong, "
      f"{len(out) - len(wrong)} still standing")
for r in out:
    mark = "WRONG   " if r["outcome"] == "WRONG" else "standing"
    print(f"  {mark}  {r['who'][:58]:58s} {r['missBy']}")
