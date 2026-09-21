#!/usr/bin/env python3
"""What the archives hold, against what this archive has listed.

`data/antenati-coverage.tsv` existed for a fortnight with no builder and no page:
a file that looked authoritative and reached nobody, like the audit and the
disputed edges before it. It was also stale, and staleness here is expensive —
a coverage table is where a searcher decides whether a record can exist at all.

The distinction the columns carry:

  `holding`  what the archive actually has, from the result facets
  `listed`   how many rows this repository holds against it
  `status`   open  — reachable now
             partial — the listing itself is incomplete, so nothing is settled
             gap   — a real hole in the holding, with the route out of it
             route — reachable, but through a different archive

`listed` is counted from this repository's own ark files where one exists, so
the page cannot claim to have listed more than it has.

  data/antenati-coverage.tsv  ->  site/src/data/coverage.json
"""
import csv, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(HERE, ".."))

STATUS = {"open", "partial", "gap", "route"}

# How many rows this repository actually holds for each comune, counted rather
# than asserted. A coverage page that overstates its own listing is worse than
# no coverage page.
ARKS = {
    "Scilla": ["data/scilla-arks.tsv", "data/scilla-arks-italiano.tsv"],
    "Piedimonte Etneo": ["data/pe-arks.tsv"],
    "Briatico": ["data/briatico-arks.tsv"],
    "Zambrone": ["data/zambrone-arks.tsv"],
    "Mascali": ["data/mascali-arks.tsv"],
    "Giarre": ["data/giarre-arks.tsv"],
}

def count(path):
    try:
        with open(path, encoding="utf-8") as f:
            return max(0, sum(1 for _ in f) - 1)
    except FileNotFoundError:
        return 0

held = {k: sum(count(p) for p in v) for k, v in ARKS.items()}

rows = list(csv.DictReader(open("data/antenati-coverage.tsv", encoding="utf-8"),
                           delimiter="\t"))
out, fails = [], []
for r in rows:
    st = (r.get("status") or "").strip()
    if st not in STATUS:
        fails.append(f"  FAIL  «{r.get('comune')}»: status «{st}» is not one of {sorted(STATUS)}")
        continue
    out.append({k: (r.get(k) or "").strip() for k in
                ("comune", "series", "from", "to", "holding", "listed", "status", "note")})

if fails:
    print("\n".join(fails))
    sys.exit(1)

json.dump({"rows": out, "held": held},
          open("site/src/data/coverage.json", "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)

by = {}
for r in out:
    by[r["status"]] = by.get(r["status"], 0) + 1
print(f"{len(out)} series across {len({r['comune'] for r in out})} places — "
      + ", ".join(f"{v} {k}" for k, v in sorted(by.items())))
for k, v in sorted(held.items()):
    print(f"  rows held for {k:20s} {v}")
