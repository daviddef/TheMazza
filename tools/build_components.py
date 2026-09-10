#!/usr/bin/env python3
"""The fourteen pieces the export is actually made of.

A family-tree program draws every person on one canvas and lets you believe
you are looking at one family. You are not. This file reports each connected
component separately — who is in it, where they were, and whether anything at
all joins it to the line that reaches Mia and Rocco.
"""
import json, collections

P = {r["id"]: r for r in json.load(open("site/src/data/people.json"))}
anc = json.load(open("site/src/data/ancestors.json"))
spine = {x["id"] for g in anc["generations"] for x in g["people"]} | {a["id"] for a in anc["anchors"]}

groups = collections.defaultdict(list)
for r in P.values():
    groups[r.get("comp", 0)].append(r)

out = []
for comp, members in sorted(groups.items(), key=lambda kv: -len(kv[1])):
    years = [m["born"] for m in members if m.get("born")]
    towns = collections.Counter(m["birthPlace"] for m in members if m.get("birthPlace"))
    surs = collections.Counter(m["surname"] for m in members if m["surname"])
    on_spine = [m for m in members if m["id"] in spine]
    members_sorted = sorted(members, key=lambda m: (m.get("born") or 9999, m["name"]))
    out.append({
        "comp": comp, "n": len(members),
        "earliest": min(years) if years else None,
        "latest": max(years) if years else None,
        "dated": len(years),
        "towns": [{"name": t, "n": n} for t, n in towns.most_common(4)],
        "surnames": [{"name": s, "n": n} for s, n in surs.most_common(8)],
        "onSpine": len(on_spine),
        "people": [{"slug": m["slug"], "name": m["name"], "surname": m["surname"],
                    "born": m.get("born"), "died": m.get("died"),
                    "datesHidden": m.get("datesHidden", False),
                    "birthPlace": m.get("birthPlace", "")}
                   for m in members_sorted],
    })

json.dump(out, open("site/src/data/components.json", "w"), indent=1, ensure_ascii=False)
print(f"{len(out)} components")
for c in out:
    print(f"  comp {c['comp']:2d}: {c['n']:3d} people, {c['dated']:3d} dated, "
          f"{c['earliest'] or '····'}–{c['latest'] or '····'}, "
          f"spine {c['onSpine']:2d}, "
          f"{', '.join(s['name'] for s in c['surnames'][:3])} @ "
          f"{c['towns'][0]['name'] if c['towns'] else 'nowhere'}")
