#!/usr/bin/env python3
"""What this archive rests on, and whether it has seen the document or the index.

Work-list row 120: seventy lines of source list were inline in `sources.astro`,
which meant they could not be counted, checked or added to without editing a
page. That is the same failure mode as the audit and the disputed edges — a fact
living where only a template can reach it.

And extracting it exposed that the page had gone stale in the worst way. It
opened: «Almost every source below is an INDEX cited by the family tree, not a
document this archive has seen», and it listed no Italian civil register at all.
By the time it was read again this archive had opened several hundred acts at
four comuni and reached the 1720s. A sources page that undersells itself is not
modesty; it tells a reader the archive is weaker than it is.

So every row now carries `seen`, which is the only thing about a source that
really matters:

  act    the document itself has been read here, in the original
  index  an index entry, which proves a name was written somewhere
  tree   the family's own compilation
  lore   compiled research with no reference
  wall   tried, and it did not answer — recorded so nobody pays to retry it

Each row also carries `url` — the address of the thing itself. Twelve of the
twenty-five have one. The thirteen that do not are exactly one group, the
indexes the family tree cites and this archive has never opened, and they are
left empty ON PURPOSE: a link would say the collection had been reached, and
the group's own heading says it has not.

  data/sources.tsv  ->  site/src/data/sources.json
"""
import csv, json, os, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(HERE, ".."))

SEEN = {"act", "index", "tree", "lore", "wall"}
rows = list(csv.DictReader(open("data/sources.tsv", encoding="utf-8"),
                           delimiter="\t"))
bad = [r for r in rows if (r.get("seen") or "").strip() not in SEEN]
if bad:
    for r in bad:
        print(f"  FAIL  «{r.get('source')}»: seen «{r.get('seen')}» is not one "
              f"of {sorted(SEEN)}")
    sys.exit(1)

groups, order = collections.OrderedDict(), []
for r in rows:
    g = (r.get("group") or "—").strip()
    if g not in groups:
        groups[g] = []
        order.append(g)
    # `url` and `note` added 21 September 2026. They were first written
    # straight into the JSON, which this script then overwrote on the next
    # build — the sources gate caught it, reporting 25 of 25 unreachable an
    # hour after twelve had been filled in. A generated file is not a place
    # to put a fact.
    groups[g].append({k: (r.get(k) or "").strip()
                      for k in ("source", "what", "usedFor", "seen", "url", "note")
                      if (r.get(k) or "").strip() or k != "url" and k != "note"})

counts = collections.Counter((r.get("seen") or "").strip() for r in rows)
json.dump({"groups": [{"group": g, "rows": groups[g]} for g in order],
           "counts": dict(counts), "total": len(rows)},
          open("site/src/data/sources.json", "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)

print(f"{len(rows)} sources in {len(order)} groups — "
      + ", ".join(f"{v} {k}" for k, v in sorted(counts.items())))
for g in order:
    print(f"  {g}  ({len(groups[g])})")
