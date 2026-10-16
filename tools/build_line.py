#!/usr/bin/env python3
"""The spine: every ancestor of the two children who carry the name.

The archive is anchored on Mia Josephine Mazza (2017) and Rocco Francesco
Mazza (2019) — not on an ancestor. A pedigree drawn downwards decides in
advance which line matters; drawn upwards from the living it simply reports
who is actually behind them, and how far each line reaches before it stops.
"""
import json, collections, re

P = {r["id"]: r for r in json.load(open("site/src/data/people.json"))}
ANCHORS = ["@I363@", "@I364@"]      # Mia and Rocco Francesco
PROBAND = "@I26@"                   # Michael Rocco Mazza

def up(start):
    """Ahnentafel walk. Returns {id: (generation, [paths])}."""
    gen, frontier, seen = {}, [(start, 0)], {start}
    while frontier:
        pid, g = frontier.pop(0)
        gen.setdefault(pid, g)
        for par in P.get(pid, {}).get("parents", []):
            if par["id"] not in seen:
                seen.add(par["id"])
                frontier.append((par["id"], g + 1))
            gen.setdefault(par["id"], g + 1)
    return gen

gen = up(PROBAND)
anc = [P[i] for i in gen if i in P]
print(f"ancestors of Michael Rocco Mazza (incl. self): {len(anc)}, max depth {max(gen.values())}")

# --- which surname line reaches furthest, and where each one sits
lines = collections.defaultdict(list)
for i, g in gen.items():
    r = P.get(i)
    if not r:
        continue
    lines[r["surname"] or "?"].append((g, r))
print("\nline                depth  n   earliest birth   home town")
rows = []
for sn, xs in sorted(lines.items(), key=lambda kv: -max(g for g, _ in kv[1])):
    depth = max(g for g, _ in xs)
    births = [r["born"] for _, r in xs if r.get("born")]
    towns = collections.Counter(r["birthPlace"] for _, r in xs if r.get("birthPlace"))
    town = towns.most_common(1)[0][0] if towns else ""
    rows.append((sn, depth, len(xs), min(births) if births else None, town))
    print(f"{sn:20s} {depth:5d} {len(xs):3d}   {min(births) if births else '····':>12}   {town}")

# --- the four quarters (grandparents of Michael Rocco)
print("\n=== the four quarters ===")
def path_names(pid):
    return P[pid]["name"] if pid in P else pid
for i, g in sorted(gen.items(), key=lambda kv: kv[1]):
    if g == 2 and i in P:
        r = P[i]
        print(f"  {r['name']:26s} b {r.get('born') or '····'}  {r.get('birthPlace','')}")

json.dump({"gen": gen, "proband": PROBAND, "anchors": ANCHORS},
          open("data/ahnentafel.json", "w"), indent=1)

# --- the deepest single descent, written out
deepest = max(gen.items(), key=lambda kv: kv[1])
print(f"\ndeepest ancestor: {P[deepest[0]]['name']} — generation {deepest[1]}")
def chain_to(target):
    """Any path from proband up to target."""
    parent_of = {i: [p["id"] for p in P[i]["parents"]] for i in P}
    stack = [(PROBAND, [PROBAND])]
    while stack:
        cur, path = stack.pop()
        if cur == target:
            return path
        for p in parent_of.get(cur, []):
            if p not in path:
                stack.append((p, path + [p]))
    return []
ch = chain_to(deepest[0])
for n, pid in enumerate(ch):
    r = P[pid]
    print(f"  {n}: {r['name']:30s} {r.get('born') or '':>5}  {r.get('birthPlace','')}")
