#!/usr/bin/env python3
"""Turn the MyHeritage export into the archive's data layer.

Every rule here exists because the export cannot be trusted as-is:

  * It carries 39 duplicate people, including the whole of Frank Mazza's
    household twice. Duplicates are detected, and the fuller copy wins.
  * It is split into 14 disconnected pieces. The largest holds the family;
    the second holds 111 Piedimonte Etneo Mazza who are almost certainly
    cousins but are joined to nothing. Component membership is recorded so
    the site can say which is which instead of implying one tree.
  * MyHeritage does not mark the living. Anyone without a death record who
    would not yet be 100 is treated as living, and carries NAME ONLY —
    following the rule David set for the Falco archive on 10 September 2026.
"""
import sys, os, re, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ged import parse, kid, kids, val, cont

OUT = "site/src/data"
R = parse()
I = {x: v for x, v in R.items() if v["tag"] == "INDI"}
F = {x: v for x, v in R.items() if v["tag"] == "FAM"}
S = {x: v for x, v in R.items() if v["tag"] == "SOUR"}

# ---------------------------------------------------------------- names, dates

def raw_name(x):
    n = kid(I[x], "NAME")
    return n["val"] if n else ""

def nm(x):
    return re.sub(r"\s+", " ", raw_name(x).replace("/", " ")).strip() or "[unnamed]"

def surname(x):
    s = val(I[x], "NAME", "SURN")
    if s:
        return s.strip()
    m = re.search(r"/([^/]*)/", raw_name(x))
    return (m.group(1).strip() if m else "")

def given(x):
    g = val(I[x], "NAME", "GIVN")
    return g.strip() if g else re.sub(r"/[^/]*/", "", raw_name(x)).strip()

MONTHS = {m: i for i, m in enumerate(
    "JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC".split(), 1)}

def year_of(s):
    m = re.search(r"\b(1[5-9]\d\d|20\d\d)\b", s or "")
    return int(m.group(1)) if m else None

def pretty_date(s):
    """'8 APR 1948' -> '8 April 1948'; keeps ABT/BEF/AFT as words."""
    if not s:
        return ""
    s = s.strip()
    out = s
    for k, v in MONTHS.items():
        out = re.sub(r"\b" + k + r"\b",
                     ["", "January", "February", "March", "April", "May", "June", "July",
                      "August", "September", "October", "November", "December"][v], out, flags=re.I)
    out = re.sub(r"^ABT\b", "about", out, flags=re.I)
    out = re.sub(r"^BEF\b", "before", out, flags=re.I)
    out = re.sub(r"^AFT\b", "after", out, flags=re.I)
    return re.sub(r"\s+", " ", out).strip()

# ------------------------------------------------------------------- places

def tidy_place(p):
    """The export spells one town five ways. Normalise, but never invent."""
    if not p:
        return ""
    p = re.sub(r"\s+", " ", p.strip().strip(","))
    fix = [
        (r"^piedimonte etneo.*$", "Piedimonte Etneo, Catania, Sicily"),
        (r"^briatico.*$", "Briatico, Vibo Valentia, Calabria"),
        (r"^potenzoni.*$", "Potenzoni (Briatico), Vibo Valentia, Calabria"),
        (r"^mandaradoni.*$", "Mandaradoni (Briatico), Vibo Valentia, Calabria"),
        (r"^scilla.*$", "Scilla, Reggio Calabria"),
        (r"^san costantino.*$", "San Costantino Calabro, Vibo Valentia, Calabria"),
        (r"^pizzo.*$", "Pizzo, Vibo Valentia, Calabria"),
        (r"^mascali.*$", "Mascali, Catania, Sicily"),
        (r"^giarre.*$", "Giarre, Catania, Sicily"),
        (r"^catania.*$", "Catania, Sicily"),
        (r"^catanzaro, calabria.*$", "Catanzaro, Calabria"),
        (r"^nudgee.*$", "Nudgee, Brisbane, Queensland"),
        (r"^brisbane.*$", "Brisbane, Queensland"),
        (r"^gold coast.*$", "Gold Coast, Queensland"),
        (r"^toowoomba.*$", "Toowoomba, Queensland"),
        (r"^tully.*$", "Tully, Queensland"),
        (r"^sydney.*$", "Sydney, New South Wales"),
        (r"^melbourne.*$", "Melbourne, Victoria"),
        (r"^fremantle.*$", "Fremantle, Western Australia"),
        (r"^(manhattan|brooklyn|new york).*$", "New York, New York"),
        (r"^buenos aires.*$", "Buenos Aires, Argentina"),
        (r"^gen(o|oa|ova).*$", "Genoa, Liguria"),
        (r"^naples.*$", "Naples, Campania"),
        (r"^palermo.*$", "Palermo, Sicily"),
        (r"^messina.*$", "Messina, Sicily"),
        (r"^milano.*$", "Milan, Lombardy"),
        (r"^arneytown.*$", "Arneytown, Burlington County, New Jersey"),
        (r"^italy$|^italia$", "Italy"),
        (r"^sicilia, italy$", "Sicily"),
    ]
    for pat, rep in fix:
        if re.match(pat, p, re.I):
            return rep
    return p

def country(p):
    for k, c in (("Queensland", "Australia"), ("New South Wales", "Australia"),
                 ("Victoria", "Australia"), ("Western Australia", "Australia"),
                 ("Australia", "Australia"), ("Argentina", "Argentina"),
                 ("New Jersey", "United States"), ("New York", "United States"),
                 ("USA", "United States"), ("United States", "United States"),
                 ("Louisiana", "United States"), ("Florida", "United States"),
                 ("Sicily", "Italy"), ("Calabria", "Italy"), ("Campania", "Italy"),
                 ("Liguria", "Italy"), ("Lombardy", "Italy"), ("Italy", "Italy"),
                 ("Great Britain", "United Kingdom")):
        if k.lower() in (p or "").lower():
            return c
    return ""

# ------------------------------------------------------------------- events

EVENT_LABEL = {"BIRT": "born", "DEAT": "died", "BURI": "buried",
               "BAPM": "baptised", "CHR": "christened", "RESI": "lived"}

def events(x):
    i, out = I[x], []
    for tag in ("BIRT", "BAPM", "CHR", "RESI", "DEAT", "BURI"):
        for e in kids(i, tag):
            d, p = val(e, "DATE"), tidy_place(val(e, "PLAC"))
            if not (d or p):
                continue
            out.append({"what": EVENT_LABEL.get(tag, tag.lower()), "tag": tag,
                        "date": pretty_date(d), "year": year_of(d), "place": p})
    for e in kids(i, "EVEN"):
        t = val(e, "TYPE") or "event"
        d, p = val(e, "DATE"), tidy_place(val(e, "PLAC"))
        out.append({"what": t.lower(), "tag": "EVEN", "date": pretty_date(d),
                    "year": year_of(d), "place": p})
    return out

def birth_year(x):
    for t in ("BIRT", "CHR", "BAPM"):
        e = kid(I[x], t)
        if e and year_of(val(e, "DATE")):
            return year_of(val(e, "DATE"))
    return None

def death_year(x):
    for t in ("DEAT", "BURI"):
        e = kid(I[x], t)
        if e and year_of(val(e, "DATE")):
            return year_of(val(e, "DATE"))
    return None

def has_death(x):
    return bool(kid(I[x], "DEAT") or kid(I[x], "BURI"))

CENTENARY = 1926  # anyone born after this and not recorded dead is treated as living

def is_dead(x):
    if has_death(x):
        return True
    y = birth_year(x)
    return bool(y and y < CENTENARY)

# ------------------------------------------------------ duplicates & components

def norm_name(x):
    return re.sub(r"[^a-z]", "", nm(x).lower())

def richness(x):
    """How much the export actually knows about this copy of a person."""
    i = I[x]
    return (len(kids(i, "FAMC")) * 3 + len(kids(i, "FAMS")) * 2 +
            len(i["kids"]) + (2 if birth_year(x) else 0) +
            (3 if kid(i, "DEAT") else 0) + len(kids(i, "OBJE")))

def _fam_names(x, role):
    """The names around x: their parents, or their spouses and children."""
    out = set()
    if role == "up":
        for k in kids(I[x], "FAMC"):
            f = F.get(k["val"])
            if f:
                for r in ("HUSB", "WIFE"):
                    for h in kids(f, r):
                        if h["val"] in I:
                            out.add(norm_name(h["val"]))
    else:
        for k in kids(I[x], "FAMS"):
            f = F.get(k["val"])
            if f:
                for r in ("HUSB", "WIFE", "CHIL"):
                    for h in kids(f, r):
                        if h["val"] in I and h["val"] != x:
                            out.add(norm_name(h["val"]))
    return out

def same_person(a, b):
    """Is this the same human being twice, or two people who share a name?

    A shared name is NOT evidence. In these three towns the same fifteen
    forenames circulate for two centuries: the export holds four men called
    Rosario Mazza and four called Giuseppe Arena, none with a date. Merging
    them on the name alone would invent a pedigree — an earlier draft of this
    file did exactly that, and manufactured an eleven-generation descent for
    Michael Rocco Mazza out of four unrelated stubs.

    So a merge needs corroboration beyond the name: either both copies give
    the SAME BIRTH YEAR, or they sit in the same place in the family — the
    same parents, or the same spouse and children. Anything less is recorded
    as an open question and left as two people.
    """
    if norm_name(a) != norm_name(b) or not norm_name(a):
        return False
    ya, yb = birth_year(a), birth_year(b)
    if ya and yb:
        return ya == yb                      # both dated: the date decides
    if ya or yb:
        return False                         # one dated, one not: not proven
    return bool(_fam_names(a, "up") & _fam_names(b, "up")) or \
           bool(_fam_names(a, "down") & _fam_names(b, "down"))

# union-find over pairs that pass same_person
parent_uf = {x: x for x in I}
def find(x):
    while parent_uf[x] != x:
        parent_uf[x] = parent_uf[parent_uf[x]]
        x = parent_uf[x]
    return x
def union(a, b):
    ra, rb = find(a), find(b)
    if ra != rb:
        parent_uf[rb] = ra

by_name = collections.defaultdict(list)
for x in I:
    if norm_name(x):
        by_name[norm_name(x)].append(x)

unresolved = []
for n, xs in by_name.items():
    if len(xs) < 2:
        continue
    for a_i in range(len(xs)):
        for b_i in range(a_i + 1, len(xs)):
            if same_person(xs[a_i], xs[b_i]):
                union(xs[a_i], xs[b_i])
    # anything still separate under a shared name is an open question
    roots = {find(x) for x in xs}
    if len(roots) > 1:
        unresolved.append({"name": nm(xs[0]), "copies": len(roots),
                           "ids": sorted(roots),
                           "why": "same name, no shared date and no shared family — left as separate people"})

clusters = collections.defaultdict(list)
for x in I:
    clusters[find(x)].append(x)

canonical, duplicates = {}, []
for root, xs in clusters.items():
    best = max(xs, key=richness)
    for x in xs:
        canonical[x] = best
    if len(xs) > 1:
        duplicates.append({"name": nm(best), "year": birth_year(best),
                           "kept": best, "dropped": [x for x in xs if x != best],
                           "why": "same name and same birth year" if birth_year(best)
                                  else "same name and the same family around them"})

adj = collections.defaultdict(set)
for fx, f in F.items():
    mem = [k["val"] for k in f["kids"] if k["tag"] in ("HUSB", "WIFE", "CHIL") and k["val"] in I]
    for a in mem:
        for b in mem:
            if a != b:
                adj[a].add(b)
seen, comps = set(), []
for x in I:
    if x in seen:
        continue
    st, comp = [x], []
    seen.add(x)
    while st:
        c = st.pop()
        comp.append(c)
        for n2 in adj[c]:
            if n2 not in seen:
                seen.add(n2)
                st.append(n2)
    comps.append(comp)
comps.sort(key=len, reverse=True)
comp_of = {}
for idx, c in enumerate(comps, 1):
    for x in c:
        comp_of[x] = idx

# ------------------------------------------------------------------ families

def spouse_of(x, fx):
    f = F[fx]
    for role in ("HUSB", "WIFE"):
        k = kid(f, role)
        if k and k["val"] in I and k["val"] != x:
            return k["val"]
    return None

def parents(x):
    fc = kid(I[x], "FAMC")
    if not fc or fc["val"] not in F:
        return []
    f = F[fc["val"]]
    return [k["val"] for r in ("HUSB", "WIFE") for k in kids(f, r) if k["val"] in I]

def children(x):
    out = []
    for k in kids(I[x], "FAMS"):
        f = F.get(k["val"])
        if f:
            out += [c["val"] for c in kids(f, "CHIL") if c["val"] in I]
    return out

def spouses(x):
    out = []
    for k in kids(I[x], "FAMS"):
        s = spouse_of(x, k["val"])
        if s:
            out.append(s)
    return out

# -------------------------------------------------------------------- slugs

def kebab(s):
    s = re.sub(r"[^\w\s-]", "", (s or "").lower())
    return re.sub(r"[\s_]+", "-", s).strip("-") or "unknown"

people_ids = [x for x in I if canonical[x] == x]
slug_of, used = {}, collections.Counter()
for x in sorted(people_ids, key=lambda z: (nm(z), birth_year(z) or 9999)):
    base = kebab(nm(x))
    y = birth_year(x)
    cand = base
    if used[base]:
        cand = f"{base}-{y}" if y else f"{base}-{used[base] + 1}"
        while cand in slug_of.values():
            cand += "-2"
    used[base] += 1
    slug_of[x] = cand

# ------------------------------------------------------------------- sources

def src_of(x):
    out = []
    for s in kids(I[x], "SOUR"):
        ref = s["val"]
        if ref in S:
            t = kid(S[ref], "TITL")
            out.append(cont(t) if t else ref)
        elif s["val"]:
            out.append(cont(s))
    return out

# -------------------------------------------------------------- photo lookup

photos = {}
if os.path.exists("data/photo-manifest.json"):
    for m in json.load(open("data/photo-manifest.json")):
        if m.get("dead") and os.path.exists(m.get("path", "")):
            photos.setdefault(m["xref"], []).append(m["file"])

# ---------------------------------------------------------------- the records

def record(x):
    dead = is_dead(x)
    rec = {
        "id": x, "slug": slug_of[x], "name": nm(x),
        "given": given(x), "surname": surname(x),
        "sex": val(I[x], "SEX"), "living": not dead,
        "comp": comp_of.get(x, 0),
    }
    if not dead:
        return rec  # NAME ONLY. No dates, no places, no records, no photographs.
    ev = events(x)
    rec.update({
        "born": birth_year(x), "died": death_year(x),
        "events": ev,
        "birthPlace": next((e["place"] for e in ev if e["tag"] == "BIRT" and e["place"]), ""),
        "deathPlace": next((e["place"] for e in ev if e["tag"] == "DEAT" and e["place"]), ""),
        "burialPlace": next((e["place"] for e in ev if e["tag"] == "BURI" and e["place"]), ""),
        "sources": src_of(x),
        "photos": photos.get(x, []),
    })
    return rec

records = [record(x) for x in people_ids]
by_id = {r["id"]: r for r in records}

def link(x):
    c = canonical.get(x)
    r = by_id.get(c)
    return {"id": c, "name": r["name"], "slug": r["slug"], "living": r["living"]} if r else None

for r in records:
    x = r["id"]
    orig = [z for z in I if canonical[z] == x]
    par, ch, sp = [], [], []
    for o in orig:
        par += parents(o)
        ch += children(o)
        sp += spouses(o)
    def uniq(ids):
        out, s = [], set()
        for i2 in ids:
            c = canonical.get(i2)
            if c and c != x and c not in s:
                s.add(c)
                out.append(link(c))
        return [z for z in out if z]
    r["parents"], r["children"], r["spouses"] = uniq(par), uniq(ch), uniq(sp)

os.makedirs(OUT, exist_ok=True)
json.dump(records, open(f"{OUT}/people.json", "w"), indent=1, ensure_ascii=False)

stats = {
    "exported": len(I), "people": len(records),
    "duplicates": sum(len(d["dropped"]) for d in duplicates),
    "unresolvedNames": len(unresolved),
    "living": sum(1 for r in records if r["living"]),
    "deceased": sum(1 for r in records if not r["living"]),
    "families": len(F), "sources": len(S),
    "components": [len(c) for c in comps],
    "photos": sum(len(v) for v in photos.values()),
    "earliest": min([r["born"] for r in records if r.get("born")] or [0]),
}
json.dump({"stats": stats, "duplicates": duplicates, "unresolved": unresolved},
          open("data/audit.json", "w"), indent=1, ensure_ascii=False)
print(json.dumps(stats, indent=1))
