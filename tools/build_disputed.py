#!/usr/bin/env python3
"""Edges the family tree asserts and a record contradicts — TSV to JSON.

`PersonTree.astro` draws a parent link differently, and says so in words, when
`disputed.json` holds that edge. The JSON has been on the site since it was
written and, like the audit, NOTHING REGENERATED IT — so a new disputed edge
added to `data/disputed-edges.tsv` would have been drawn as an ordinary one.

  data/disputed-edges.tsv  ->  site/src/data/disputed.json
  { "<slug>": { "<other slug>": {"short": "...", "why": "..."} } }

Columns: a, b, short, why.

THE EDGE IS WRITTEN BOTH WAYS, and that is not tidiness. `PersonTree.astro`
looks the edge up as `disputed[p.slug][other.slug]` and applies it to parents AND
children, so an edge stored only as child->parent is drawn as disputed on the
child's page and as an ordinary link on the parent's. The hand-written JSON this
tool replaces knew that; a first version of this tool did not, and would have
quietly un-disputed three edges on Orazio Arena's and Giovanna Pontillo's pages.
A slug that is not in the export is refused rather than written, because an edge
keyed on a slug nothing answers to is an edge nobody will ever see.
"""
import csv, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(HERE, ".."))

rows = list(csv.DictReader(open("data/disputed-edges.tsv", encoding="utf-8"),
                           delimiter="\t"))
people = {p["slug"] for p in json.load(open("site/src/data/people.json",
                                            encoding="utf-8"))}

out, fails = {}, []
for r in rows:
    a, b = (r.get("a") or "").strip(), (r.get("b") or "").strip()
    if a not in people:
        fails.append(f"  FAIL  «{a}» is not a slug in the export (row a)")
        continue
    if b not in people:
        fails.append(f"  FAIL  «{b}» is not a slug in the export (row b, under {a})")
        continue
    edge = {"short": (r.get("short") or "").strip(),
            "why": (r.get("why") or "").strip()}
    out.setdefault(a, {})[b] = edge
    out.setdefault(b, {})[a] = edge

if fails:
    print("\n".join(fails))
    sys.exit(1)

json.dump(out, open("site/src/data/disputed.json", "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)

print(f"{len(rows)} disputed edges, written both ways, touching {len(out)} people")
for r in rows:
    print(f"  {r['a']:24s} -/- {r['b']:24s} {r['short']}")
