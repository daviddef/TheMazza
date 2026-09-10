#!/usr/bin/env python3
"""Match the Brisbane Catholic cemetery register against the family tree.

A cemetery row is only attached to a person when the archive can defend the
identification: the surname must match the person's own OR their spouse's
(women are buried under the married name), and a recorded year must agree.
Everything else is listed as a near-miss rather than quietly claimed.
"""
import json, re, unicodedata

P = json.load(open("site/src/data/people.json"))
by_id = {p["id"]: p for p in P}
reg = json.load(open("data/nudgee-search.json"))

def norm(s):
    s = unicodedata.normalize("NFD", (s or "").lower())
    return re.sub(r"[^a-z]", "", s)

def yr(s):
    m = re.match(r"(\d{4})-", s or "")
    return int(m.group(1)) if m else None

GIVEN_ALIAS = {  # the register anglicises and shortens
    "angelina": {"angela", "angelina"}, "angela": {"angela", "angelina"},
    "josephine": {"giuseppa", "giuseppina", "josephine"},
    "mary": {"maria", "mary"}, "maria": {"maria", "mary"},
    "guiseppe": {"giuseppe", "guiseppe", "joseph"},
    "joseph": {"giuseppe", "guiseppe", "joseph"},
}

rows = []
for r in reg["rows"]:
    c = (r["cells"] + [""] * 9)[:9]
    rows.append({"regno": c[0], "cemetery": c[1], "surname": c[2], "given": c[3],
                 "birth": c[4], "death": c[5], "interment": c[6], "plot": c[7]})

def candidates(row):
    g = norm(row["given"])
    forms = GIVEN_ALIAS.get(g, {g})
    out = []
    for p in P:
        if p["living"]:
            continue
        pg = norm(p.get("given") or p["name"].split()[0])
        # the person's own given name, or one of its parts, must match
        parts = {norm(x) for x in (p.get("given") or "").split()} | {pg}
        if not (forms & parts):
            continue
        # surname: their own, or a spouse's (married name in the register)
        sur = {norm(p["surname"])}
        for s in p.get("spouses", []):
            sp = by_id.get(s["id"])
            if sp:
                sur.add(norm(sp["surname"]))
        if norm(row["surname"]) not in sur:
            continue
        out.append(p)
    return out

matched, nearmiss = [], []
for row in rows:
    rb, rd = yr(row["birth"]), yr(row["death"]) or yr(row["interment"])
    for p in candidates(row):
        pb, pd = p.get("born"), p.get("died")
        agree, why = 0, []
        if rb and pb:
            if abs(rb - pb) == 0: agree += 2; why.append(f"birth year {rb} agrees")
            elif abs(rb - pb) <= 1: agree += 1; why.append(f"birth year {rb} vs tree {pb}")
        if rd and pd:
            if abs(rd - pd) == 0: agree += 2; why.append(f"death year {rd} agrees")
            elif abs(rd - pd) <= 1: agree += 1; why.append(f"death year {rd} vs tree {pd}")
        rec = {"row": row, "slug": p["slug"], "name": p["name"], "id": p["id"],
               "treeBorn": pb, "treeDied": pd, "score": agree, "why": "; ".join(why)}
        (matched if agree >= 2 else nearmiss).append(rec)

# one row -> best person only
best = {}
for m in matched:
    k = m["row"]["regno"] + m["row"]["given"] + m["row"]["surname"]
    if k not in best or m["score"] > best[k]["score"]:
        best[k] = m
matched = sorted(best.values(), key=lambda m: m["row"]["plot"])

json.dump({"matched": matched, "rows": rows}, open("data/nudgee-matched.json", "w"),
          indent=1, ensure_ascii=False)

print(f"{len(matched)} confident matches of {len(rows)} register rows\n")
print(f"{'plot':<18}{'register name':<28}{'archive name':<28}{'born':<12}{'died':<12}corrections")
print("-"*130)
for m in matched:
    r = m["row"]
    corr = []
    if yr(r["birth"]) and m["treeBorn"] and yr(r["birth"]) != m["treeBorn"]:
        corr.append(f"born {m['treeBorn']}→{r['birth']}")
    elif r["birth"] and m["treeBorn"]:
        corr.append(f"exact birth {r['birth']}")
    if yr(r["death"]) and m["treeDied"] and yr(r["death"]) != m["treeDied"]:
        corr.append(f"died {m['treeDied']}→{r['death']}")
    elif r["death"] and m["treeDied"]:
        corr.append(f"exact death {r['death']}")
    print(f"{r['plot']:<18}{(r['given']+' '+r['surname']):<28}{m['name']:<28}"
          f"{r['birth'] or '—':<12}{r['death'] or '—':<12}{'; '.join(corr)}")
