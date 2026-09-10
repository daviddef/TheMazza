#!/usr/bin/env python3
"""Places, surnames, crossings, burials — the derived layers of the archive."""
import json, collections, re, os

OUT = "site/src/data"
P = json.load(open(f"{OUT}/people.json"))
dead = [p for p in P if not p["living"]]
by_id = {p["id"]: p for p in P}

# ------------------------------------------------------------------ places
place = collections.defaultdict(lambda: {"born": 0, "died": 0, "buried": 0,
                                         "lived": 0, "first": None, "last": None, "who": []})
for p in dead:
    for e in p.get("events", []):
        if not e["place"]:
            continue
        d = place[e["place"]]
        k = {"born": "born", "died": "died", "buried": "buried"}.get(e["what"], "lived")
        d[k] += 1
        y = e["year"]
        if y:
            d["first"] = y if d["first"] is None else min(d["first"], y)
            d["last"] = y if d["last"] is None else max(d["last"], y)
        if len(d["who"]) < 40:
            d["who"].append(p["slug"])
places = [{"name": k, **v, "n": v["born"] + v["died"] + v["buried"] + v["lived"]}
          for k, v in place.items()]
places.sort(key=lambda x: -x["n"])
json.dump(places, open(f"{OUT}/places.json", "w"), indent=1, ensure_ascii=False)

# ---------------------------------------------------------------- surnames
sur = collections.defaultdict(lambda: {"n": 0, "dead": 0, "living": 0,
                                       "first": None, "last": None, "places": collections.Counter()})
for p in P:
    s = p["surname"] or "?"
    d = sur[s]
    d["n"] += 1
    d["living" if p["living"] else "dead"] += 1
    if not p["living"]:
        for y in (p.get("born"), p.get("died")):
            if y:
                d["first"] = y if d["first"] is None else min(d["first"], y)
                d["last"] = y if d["last"] is None else max(d["last"], y)
        if p.get("birthPlace"):
            d["places"][p["birthPlace"]] += 1
families = [{"surname": k, "n": v["n"], "dead": v["dead"], "living": v["living"],
             "first": v["first"], "last": v["last"],
             "places": [p for p, _ in v["places"].most_common(4)]}
            for k, v in sur.items() if k != "?"]
families.sort(key=lambda x: -x["n"])
json.dump(families, open(f"{OUT}/families.json", "w"), indent=1, ensure_ascii=False)

# --------------------------------------------------------------- crossings
cross = []
for p in dead:
    for e in p.get("events", []):
        if e["what"] in ("arrival", "departure"):
            cross.append({"who": p["name"], "slug": p["slug"], "what": e["what"],
                          "date": e["date"], "year": e["year"], "place": e["place"],
                          "born": p.get("born"), "from": p.get("birthPlace", "")})
def pair(rows):
    """Marry each departure to the arrival it belongs to."""
    byp = collections.defaultdict(dict)
    for r in rows:
        byp[r["slug"]][r["what"]] = r
    out = []
    for slug, d in byp.items():
        a, dep = d.get("arrival"), d.get("departure")
        base = a or dep
        out.append({"who": base["who"], "slug": slug, "born": base["born"],
                    "from": base["from"],
                    "left": dep["place"] if dep else "", "leftDate": dep["date"] if dep else "",
                    "arrived": a["place"] if a else "", "arrivedDate": a["date"] if a else "",
                    "year": (a or dep)["year"]})
    return sorted(out, key=lambda r: (r["year"] or 9999))
crossings = pair(cross)
json.dump(crossings, open(f"{OUT}/crossings.json", "w"), indent=1, ensure_ascii=False)

# ----------------------------------------------------------------- burials
bur = [{"who": p["name"], "slug": p["slug"], "place": p["burialPlace"],
        "born": p.get("born"), "died": p.get("died")}
       for p in dead if p.get("burialPlace")]
bur.sort(key=lambda r: (r["place"], r["died"] or 0))
json.dump(bur, open(f"{OUT}/burials.json", "w"), indent=1, ensure_ascii=False)

# -------------------------------------------------------------- households
hh = []
for p in P:
    if not p["children"]:
        continue
    sp = p["spouses"][0]["name"] if p["spouses"] else None
    name = f"{p['name']} & {sp}" if sp else p["name"]
    hh.append({"name": name, "head": p["slug"], "headId": p["id"],
               "spouse": p["spouses"][0] if p["spouses"] else None,
               "children": p["children"],
               "place": p.get("birthPlace", ""), "born": p.get("born")})
seen, uniq = set(), []
for h in hh:
    key = tuple(sorted([h["headId"]] + [c["id"] for c in h["children"]]))
    if key in seen:
        continue
    seen.add(key)
    uniq.append(h)
uniq.sort(key=lambda h: (h["born"] or 9999))
json.dump(uniq, open(f"{OUT}/households.json", "w"), indent=1, ensure_ascii=False)

# ------------------------------------------------------------------- living
living = sorted([{"name": p["name"], "surname": p["surname"], "slug": p["slug"]}
                 for p in P if p["living"]], key=lambda r: (r["surname"], r["name"]))
json.dump(living, open(f"{OUT}/living.json", "w"), indent=1, ensure_ascii=False)

# -------------------------------------------------------------------- stats
audit = json.load(open("data/audit.json"))
stats = audit["stats"]
stats.update({"places": len(places), "surnames": len(families),
              "crossings": len(crossings), "burials": len(bur),
              "households": len(uniq),
              "nudgee": sum(1 for b in bur if "Nudgee" in b["place"])})
json.dump(stats, open(f"{OUT}/stats.json", "w"), indent=1)
json.dump(audit.get("unresolved", []), open(f"{OUT}/unresolved.json", "w"), indent=1, ensure_ascii=False)

print(f"places {len(places)}  surnames {len(families)}  crossings {len(crossings)}  "
      f"burials {len(bur)} (Nudgee {stats['nudgee']})  households {len(uniq)}  living {len(living)}")
print("\ntop places:", [(p['name'], p['n']) for p in places[:8]])
print("\ncrossings:")
for c in crossings:
    print(f"  {c['year'] or '····'}  {c['who']:26s} {c['left'] or '—':22s} -> {c['arrived']}  {c['arrivedDate']}")
