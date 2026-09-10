#!/usr/bin/env python3
"""Two things the archive is FOR.

1. The ancestors of Mia and Rocco Francesco Mazza — every one the tree can
   reach, by generation, with the gaps counted rather than glossed. A pedigree
   that does not say how much of itself is missing is a advertisement.

2. The Mazza and the Arena as SURNAMES — every bearer in the tree, sorted into
   the descent groups they actually belong to, and honest about which of those
   groups are joined to the family and which merely share a name.
"""
import json, collections

P = {r["id"]: r for r in json.load(open("site/src/data/people.json"))}
BY_SLUG = {r["slug"]: r for r in P.values()}
ANCHORS = ["@I363@", "@I364@"]           # Mia Josephine, Rocco Francesco

def brief(pid):
    r = P[pid]
    return {"id": pid, "slug": r["slug"], "name": r["name"], "surname": r["surname"],
            "born": r.get("born"), "died": r.get("died"),
            "datesHidden": r.get("datesHidden", False),
            "birthPlace": r.get("birthPlace", ""), "comp": r.get("comp", 0)}

# ---------------------------------------------------------------- ancestors
def ancestry(start):
    """{generation: [ids]} above `start`. Gen 1 = parents."""
    gens, frontier, seen = collections.defaultdict(list), [(start, 0)], {start}
    while frontier:
        pid, g = frontier.pop(0)
        for par in P.get(pid, {}).get("parents", []):
            if par["id"] in seen:
                continue
            seen.add(par["id"])
            gens[g + 1].append(par["id"])
            frontier.append((par["id"], g + 1))
    return gens

gens = ancestry(ANCHORS[0])
rows = []
for g in sorted(gens):
    people = [brief(i) for i in gens[g]]
    people.sort(key=lambda r: (r["surname"], r["name"]))
    towns = collections.Counter(r["birthPlace"] for r in people if r["birthPlace"])
    rows.append({
        "gen": g, "possible": 2 ** g, "found": len(people),
        "people": people,
        "towns": [{"name": t, "n": n} for t, n in towns.most_common()],
    })

total_found = sum(r["found"] for r in rows)
json.dump({"anchors": [brief(a) for a in ANCHORS],
           "generations": rows,
           "total": total_found,
           "deepest": max(rows, key=lambda r: r["gen"])["gen"]},
          open("site/src/data/ancestors.json", "w"), indent=1, ensure_ascii=False)

print(f"ancestors of Mia & Rocco: {total_found} across {len(rows)} generations")
for r in rows:
    pct = 100 * r["found"] / r["possible"]
    print(f"  gen {r['gen']:2d}: {r['found']:3d} of {r['possible']:4d} possible ({pct:5.1f}%)  "
          f"{', '.join(t['name'].split(',')[0] for t in r['towns'][:3])}")

# ------------------------------------------------------- surnames as families
spine_ids = {i for gl in gens.values() for i in gl} | set(ANCHORS)

def descent_groups(surname):
    """Sort every bearer of a surname into the descent group they sit in.

    A group is the set of people reachable from one another through parent and
    child links *among bearers of this name and their spouses* — in practice,
    one family. Groups are reported separately and never merged: two Mazza
    groups in one town are two groups until a record joins them.
    """
    members = [r for r in P.values() if (r["surname"] or "").lower() == surname.lower()]
    ids = {r["id"] for r in members}
    adj = collections.defaultdict(set)
    for r in members:
        for kind in ("parents", "children", "spouses"):
            for o in r.get(kind, []):
                if o["id"] in ids:
                    adj[r["id"]].add(o["id"])
                    adj[o["id"]].add(r["id"])
    seen, groups = set(), []
    for r in members:
        if r["id"] in seen:
            continue
        stack, comp = [r["id"]], []
        seen.add(r["id"])
        while stack:
            c = stack.pop()
            comp.append(c)
            for n in adj[c]:
                if n not in seen:
                    seen.add(n)
                    stack.append(n)
        groups.append(comp)
    out = []
    for comp in groups:
        ppl = [brief(i) for i in comp]
        years = [p["born"] for p in ppl if p["born"]]
        towns = collections.Counter(p["birthPlace"] for p in ppl if p["birthPlace"])
        ppl.sort(key=lambda r: (r["born"] or 9999, r["name"]))
        out.append({
            "n": len(ppl),
            "earliest": min(years) if years else None,
            "latest": max(years) if years else None,
            "towns": [t for t, _ in towns.most_common(3)],
            "component": collections.Counter(p["comp"] for p in ppl).most_common(1)[0][0],
            "onSpine": sorted({p["name"] for p in ppl if p["id"] in spine_ids}),
            "people": ppl,
        })
    out.sort(key=lambda gset: (-len(gset["onSpine"]), -gset["n"]))
    return out

focus = {}
for sn in ("Mazza", "Arena"):
    groups = descent_groups(sn)
    focus[sn] = {
        "surname": sn,
        "total": sum(g["n"] for g in groups),
        "groups": groups,
    }
    print(f"\n{sn}: {focus[sn]['total']} bearers in {len(groups)} descent groups")
    for i, g in enumerate(groups, 1):
        mark = f"  ← ON THE SPINE ({', '.join(g['onSpine'])})" if g["onSpine"] else ""
        print(f"   group {i:2d}: {g['n']:3d} people, comp {g['component']}, "
              f"{g['earliest'] or '····'}–{g['latest'] or '····'}, "
              f"{g['towns'][0] if g['towns'] else 'no place'}{mark}")

json.dump(focus, open("site/src/data/focus.json", "w"), indent=1, ensure_ascii=False)
