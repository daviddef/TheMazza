#!/usr/bin/env python3
"""The four quarters, and the descent behind each of them.

Michael Rocco Mazza's four grandparents came from three towns. This writes,
for each of them, the line of ancestors standing behind that grandparent —
so the site can show how far each quarter actually reaches instead of
implying one uniform pedigree.
"""
import json, collections

P = {r["id"]: r for r in json.load(open("site/src/data/people.json"))}
PROBAND = "@I26@"   # Michael Rocco Mazza

def ancestors(start):
    gen, frontier, seen = {}, [(start, 0)], {start}
    while frontier:
        pid, g = frontier.pop(0)
        gen.setdefault(pid, g)
        for par in P.get(pid, {}).get("parents", []):
            if par["id"] not in seen:
                seen.add(par["id"])
                frontier.append((par["id"], g + 1))
    return gen

def chain(start):
    """The single longest ancestral descent behind `start`, oldest first."""
    best = []
    def walk(pid, path):
        nonlocal best
        path = path + [pid]
        pars = P.get(pid, {}).get("parents", [])
        pars = [x for x in pars if x["id"] not in path]
        if not pars:
            if len(path) > len(best):
                best = path
            return
        for x in pars:
            walk(x["id"], path)
    walk(start, [])
    return list(reversed(best))

def row(pid, gen):
    r = P[pid]
    return {"gen": gen, "id": pid, "slug": r["slug"], "name": r["name"],
            "surname": r["surname"], "living": r["living"],
            "born": r.get("born"), "died": r.get("died"),
            "birthPlace": r.get("birthPlace", ""), "deathPlace": r.get("deathPlace", ""),
            "burialPlace": r.get("burialPlace", ""),
            "spouse": (r["spouses"][0]["name"] if r.get("spouses") else "")}

gen = ancestors(PROBAND)
quarters = []
for pid, g in sorted(gen.items(), key=lambda kv: kv[1]):
    if g != 2:
        continue
    ch = chain(pid)
    quarters.append({
        "grandparent": row(pid, g),
        "town": P[pid].get("birthPlace", ""),
        "depth": max((gen[x] for x in ancestors(pid)), default=0),
        "reach": min([P[x]["born"] for x in ancestors(pid) if P.get(x, {}).get("born")] or [None]),
        "line": [row(x, i) for i, x in enumerate(ch)],
    })
json.dump(quarters, open("site/src/data/quarters.json", "w"), indent=1, ensure_ascii=False)

# the spine: the deepest descent in the archive, drawn downward to the children
deepest = max(quarters, key=lambda q: len(q["line"]))

def descend_to_proband(top_id):
    """The path DOWN from an ancestor to Michael Rocco, so the spine ends
    where the family actually is now rather than at his grandmother."""
    path = []
    def walk(pid, seen):
        if pid == PROBAND:
            return [pid]
        for c in P.get(pid, {}).get("children", []):
            if c["id"] in seen:
                continue
            sub = walk(c["id"], seen | {c["id"]})
            if sub:
                return [pid] + sub
        return []
    return walk(top_id, {top_id})

chain_down = descend_to_proband(deepest["line"][0]["id"])
spine = [row(x, len(chain_down) - 1 - i) for i, x in enumerate(chain_down)] \
        if chain_down else deepest["line"] + [row(PROBAND, 0)]
# the two children who carry the name
kids = [c for c in P[PROBAND]["children"]]
json.dump({"quarters": [q["grandparent"]["name"] for q in quarters],
           "spine": spine,
           "children": kids,
           "proband": row(PROBAND, 0)},
          open("site/src/data/spine.json", "w"), indent=1, ensure_ascii=False)

for q in quarters:
    g = q["grandparent"]
    print(f"{g['name']:22s} b{g['born']}  {q['town']:38s} depth {q['depth']}  reaches {q['reach']}  chain {len(q['line'])}")
print("\nspine (deepest descent):")
for r in spine:
    print(f"  {r['name']:30s} {r.get('born') or '····':>6}  {r['birthPlace']}")
print("\nchildren:", [c["name"] for c in kids])
