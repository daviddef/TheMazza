#!/usr/bin/env python3
"""What this archive does not know, and what would settle each one.

Work-list row 119. Two hundred lines of prose in `open-questions.astro`, which
meant the questions could not be counted, filtered or added to without editing a
template — and, worse, meant nobody came back to them. Three of the seven were
headed ANSWERED and still sat in the same list as the open ones, and two
questions answered since were never added at all.

The kit's `Questions.astro` has been waiting for this. Its own comment says the
extraction «is research work belonging to each archive rather than something to
guess at from outside», which is exactly right: only this archive knows which of
its own questions are still open.

The field that does the work is `settles` — THE SPECIFIC RECORD THAT WOULD
ANSWER IT. A page of questions without that is a list of regrets; with it, it is
a work queue. So the builder refuses a row that has none.

  data/questions.tsv  ->  site/src/data/questions.json
"""
import csv, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(HERE, ".."))

STATES = {"open", "answered"}
rows = list(csv.DictReader(open("data/questions.tsv", encoding="utf-8"),
                           delimiter="\t"))
fails = []
for r in rows:
    if (r.get("state") or "").strip() not in STATES:
        fails.append(f"  FAIL  «{r.get('q','')[:50]}»: state «{r.get('state')}» "
                     f"is not open or answered")
    if not (r.get("settles") or "").strip():
        fails.append(f"  FAIL  «{r.get('q','')[:50]}» has no `settles` — a question "
                     f"without the record that would answer it is a regret, not a queue item")
if fails:
    print("\n".join(fails))
    sys.exit(1)

out = []
for i, r in enumerate(rows, start=1):
    out.append({"n": i,
                "q": (r.get("q") or "").strip(),
                "state": (r.get("state") or "").strip(),
                "known": (r.get("known") or "").strip(),
                "tried": (r.get("tried") or "").strip(),
                "settles": (r.get("settles") or "").strip(),
                "since": (r.get("since") or "").strip(),
                "rank": (r.get("rank") or "").strip()})

json.dump(out, open("site/src/data/questions.json", "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
op = sum(1 for r in out if r["state"] == "open")
print(f"{len(out)} questions — {op} open, {len(out)-op} answered")
for r in out:
    print(f"  {r['state']:8s} {r['q'][:88]}")
