#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Roots & Routes: the tree page for this archive, built from this archive's own committed data.

    python3 tools/build-tree-page.py            # rebuild data/tree-page/ (tree.json, atlas-data.json, roots.html, roots.embed.html)
    python3 tools/build-tree-page.py --check    # exit 1 if the page is older than the data it was built from

WHERE THE PEOPLE COME FROM. There is no committed GEDCOM (the MyHeritage export carries every living person in full and stays out of the repo). The people are
the ones site/src/data/people.json holds with `living: false`. That file is written by tools/build.py from the tree under the estate's living-people standard v2
(tools/living_v2.py: living = 80 or younger by year, no death or burial recorded, no public-source citation; held out = a possible minor). A living person is
in people.json as a name, a relationship and a town, and NOTHING of hers or his is read here: the filter below drops them before a single field is looked at, and a
held-out person is not in people.json at all. `presumedLiving` is gone from this archive (tools/living_v2.py says why); this builder does not read it.
The non-living people are turned into a small GEDCOM (data/tree-page/people.ged, not committed) and handed to the family-tree-page skill's converter, vendored in
tools/tree-page/ so CI and other sessions do not depend on ~/.claude. The converter then adds its own, stricter floor: nobody with no death recorded and a birth
year in the last 110 years is drawn.

DATES. `born` / `died` are years where the tree gives one. A birth the register or the tree writes "c. 1809" or "about 1772" is drawn with the year and marked
estimated ("c. 1809"). A death written "before ..." is a death with no year (drawn "1809-?"); "after ..." and "alive at ..." are NOT deaths and are not read as one.

COLOUR is the Record Atlas surname catalogue's family (scripts/surname_variants.py lookup, read only), and where the catalogue does not hold a surname, the surname
as the archive writes it with typography only folded. This archive keeps no list of spellings: which spellings are one name is the Atlas's to say.

PLACES are resolved through data/tree-page/place_map.json, never guessed. A place string is placed only when (1) data/era-ground.tsv has decided it (every place string
in the data has a row there), (2) the gazetteer this archive already uses (the kit's, data/gazetteer-local.json, data/place-spellings.tsv: tools/build_era.py) holds the
SAME name with an `exact` match, and (3) the Atlas's geo.country_of agrees with the country the string names. A string that is only a country, a state or an island,
one that is several places, or one whose gazetteer answer is a different place is listed in data/tree-page/place-additions.json under `refused`, with the reason, and
the person is drawn at a relative's birth place (said on the page) or not at all. The few decided by hand are in the same file under `places`, each with its reason.

A ROUTE (three or more places) is carried whole where the archive records dated arrivals or residences: birth place, each dated arrival/residence in year order, death
place. A stop with no year is never guessed into the order, so a person with an undated arrival has no route.
"""
import argparse, collections, hashlib, io, json, math, os, re, subprocess, sys, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "site", "src", "data")
OUT = os.path.join(ROOT, "data", "tree-page")
TP = os.path.join(ROOT, "tools", "tree-page")
EXT = os.path.join(TP, "painted-lines.ext.html")
HOST = "mazza.defranceski.com"
FOCUS = "I2"   # who the page opens on: Sebastiano Mazza, the grandparent where the four quarters meet (not living; if he is ever not drawn the converter falls back to the best-connected person)
KIT_TOOLS = os.path.join(ROOT, "site", "node_modules", "@daviddef", "archive-kit", "kit", "tools")
ATLAS_CANDIDATES = [os.environ.get("RECORD_ATLAS", ""), os.path.expanduser("~/Projects/Family Projects/Record Atlas"),
                    os.path.join(os.path.dirname(ROOT), "Record Atlas")]
INPUTS = ["people.json"]
INPUT_FILES = [os.path.join(ROOT, "data", n) for n in ("era-ground.tsv", "gazetteer-local.json", "place-spellings.tsv")]

def jl(path): return json.load(io.open(path, encoding="utf-8"))
def run(args):
    print("$", " ".join(os.path.relpath(a, ROOT) if os.path.isabs(a) and a.startswith(ROOT) else a for a in args)); r = subprocess.run(args)
    if r.returncode: sys.exit(r.returncode)
def inputs_hash():
    h = hashlib.sha1()
    for n in INPUTS: h.update(io.open(os.path.join(DATA, n), "rb").read())
    for f in INPUT_FILES: h.update(io.open(f, "rb").read())
    for n in ("tree-views.template.html", "painted-lines.ext.html", "gedcom_to_tree.py"): h.update(io.open(os.path.join(TP, n), "rb").read())
    h.update(io.open(os.path.abspath(__file__), "rb").read())
    pa = os.path.join(OUT, "place-additions.json")
    if os.path.exists(pa): h.update(io.open(pa, "rb").read())
    return h.hexdigest()[:16]
def atlas_path():
    for c in ATLAS_CANDIDATES:
        if c and os.path.exists(os.path.join(c, "data", "places.json")): return c
    sys.exit("Record Atlas checkout not found (set RECORD_ATLAS)")

def fold(s): return re.sub(r"[^a-z0-9]+", " ", unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().lower()).strip()
def km(a, b, c, d):
    p = math.pi / 180; x = math.sin((c - a) * p / 2) ** 2 + math.cos(a * p) * math.cos(c * p) * math.sin((d - b) * p / 2) ** 2
    return 12742 * math.asin(math.sqrt(x))

# ---------------------------------------------------------------- people.json -> a small GEDCOM
def est_text(t): return bool(re.match(r"^\s*(c\.|ca\.?|circa|about|abt)\b", t or "", re.I))
def write_ged(people, path):
    ids = {p["id"] for p in people}
    by_id = {p["id"]: p for p in people}
    out = ["0 HEAD", "1 CHAR UTF-8"]
    fams, fam_of_child, fam_of_spouse = {}, {}, collections.defaultdict(list)
    def fam(h, w):
        k = (h or "", w or "")
        if k not in fams: fams[k] = "@F%d@" % (len(fams) + 1)
        return fams[k]
    for p in people:
        par = [r["id"] for r in p.get("parents") or [] if r.get("id") in ids]
        f = next((i for i in par if by_id[i].get("sex") == "M"), None)
        m = next((i for i in par if by_id[i].get("sex") == "F"), None)
        rest = [i for i in par if i not in (f, m)]   # a parent of unrecorded sex takes the place left open, in the order the tree lists them
        if not f and rest: f = rest.pop(0)
        if not m and rest: m = rest.pop(0)
        if f or m: fam_of_child[p["id"]] = fam(f, m)
        for s in p.get("spouses") or []:
            sid = s.get("id")
            if sid not in ids: continue
            a, b = sorted((p["id"], sid))   # one family per couple, whichever of the two lists the other
            if (by_id[a].get("sex") == "F" and by_id[b].get("sex") != "F") or (by_id[b].get("sex") == "M" and by_id[a].get("sex") != "M"): a, b = b, a
            k = fam(a, b)
            if k not in fam_of_spouse[p["id"]]: fam_of_spouse[p["id"]].append(k)
    for p in people:
        out += ["0 %s INDI" % p["id"], "1 NAME %s /%s/" % (p.get("given") or "", p.get("surname") or "")]
        if p.get("sex") in ("M", "F"): out.append("1 SEX %s" % p["sex"])
        yb = p.get("born") if isinstance(p.get("born"), int) else None
        if yb is None and est_text(p.get("bornText")):
            m_ = re.search(r"(1[5-9]\d\d)", p.get("bornText") or ""); yb = int(m_.group(1)) if m_ else None
        if yb or p.get("birthPlace"):
            out.append("1 BIRT")
            if yb: out.append("2 DATE %s" % yb)
            if p.get("birthPlace"): out.append("2 PLAC %s" % p["birthPlace"])
        yd = p.get("died") if isinstance(p.get("died"), int) else None
        before = (p.get("diedText") or "").lower().startswith("before")
        if yd or p.get("deathPlace") or before:
            out.append("1 DEAT")
            if yd: out.append("2 DATE %s" % yd)
            if p.get("deathPlace"): out.append("2 PLAC %s" % p["deathPlace"])
        elif p.get("burialPlace"):
            out += ["1 BURI", "2 PLAC %s" % p["burialPlace"]]
        for e in p.get("events") or []:
            if e.get("what") in ("lived", "arrival") and e.get("place"):
                out += ["1 RESI"] + (["2 DATE %s" % e["year"]] if e.get("year") else []) + ["2 PLAC %s" % e["place"]]
        if p["id"] in fam_of_child: out.append("1 FAMC %s" % fam_of_child[p["id"]])
        for fx in fam_of_spouse.get(p["id"], []): out.append("1 FAMS %s" % fx)
    for (h, w), fx in fams.items():
        out.append("0 %s FAM" % fx)
        if h: out.append("1 HUSB %s" % h)
        if w: out.append("1 WIFE %s" % w)
        for cid, f in fam_of_child.items():
            if f == fx: out.append("1 CHIL %s" % cid)
    out.append("0 TRLR")
    io.open(path, "w", encoding="utf-8").write("\n".join(out) + "\n")

# ---------------------------------------------------------------- places
def head_of(s):
    s = re.sub(r"\([^)]*\)", "", s.split(",")[0]).strip()
    return s

def seed_place_map(atlas, strings):
    """Place every string the people carry, or say why not (tree.report.json, place-additions.json `refused`). See the module docstring for the three conditions."""
    sys.path.insert(0, os.path.join(atlas, "scripts")); import geo
    sys.path.insert(0, KIT_TOOLS); sys.path.insert(0, os.path.join(ROOT, "tools")); import build_era
    rows, gaz, fixes = build_era.ground(), build_era.gazetteer(), build_era.spellings()
    cj = jl(os.path.join(atlas, "data", "countries.json"))["countries"]
    pj = jl(os.path.join(atlas, "data", "places.json"))["places"]
    byname = collections.defaultdict(list)
    for x in pj:
        for nm in [x["name"]] + [n["n"].split(",")[0] for n in x.get("names", [])]: byname[fold(nm)].append(x)
    country_names = {fold(v.get("name", "")): k for k, v in cj.items()}
    add = jl(os.path.join(OUT, "place-additions.json")) if os.path.exists(os.path.join(OUT, "place-additions.json")) else {"places": {}, "refused": {}}
    pm, report = {}, {"from_gazetteer": 0, "from_additions": 0, "refused": {}, "unplaced": {}}
    for raw in sorted(strings):
        if raw in add["places"]:
            pm[raw] = add["places"][raw]; report["from_additions"] += 1; continue
        if raw in add.get("refused", {}):
            report["refused"][raw] = add["refused"][raw]; continue
        if raw not in rows:
            report["unplaced"][raw] = "no row in data/era-ground.tsv"; continue
        hit = build_era.locate(raw, gaz, fixes, rows)
        if not hit or hit.get("conf") != "exact" or not isinstance(hit.get("lat"), (int, float)):
            report["unplaced"][raw] = "the gazetteer has no exact answer (%s)" % ((hit or {}).get("conf") or "none"); continue
        h = head_of(raw); h = head_of(fixes.get(raw, raw)) if raw in fixes else h
        mh = head_of(hit.get("matched", ""))
        if fold(h) != fold(mh) and fold(h) not in fold(hit.get("matched", "")):
            report["unplaced"][raw] = "the gazetteer answers with a different place (%s)" % hit.get("matched", "")[:60]; continue
        lat, lon = float(hit["lat"]), float(hit["lon"])
        iso = geo.country_of(lat, lon)
        last = fold(raw.split(",")[-1])
        if not iso or (last in country_names and country_names[last] != iso):
            report["unplaced"][raw] = "the point's country (%s) is not the one the string names" % iso; continue
        name = h
        near = next((x for x in byname.get(fold(name), []) if x.get("country") == iso and km(lat, lon, x["lat"], x["lon"]) <= 15), None)
        pm[raw] = {"name": name, "lat": lat, "lon": lon, "country": cj.get(iso, {}).get("name", iso), "iso": iso, "atlas_id": near["id"] if near else None,
                   "how": "data/era-ground.tsv has a row; the archive's gazetteer holds this name (exact: %s); country by the Atlas's geo.country_of" % hit.get("matched", "")[:70]}
        report["from_gazetteer"] += 1
    io.open(os.path.join(OUT, "place_map.json"), "w", encoding="utf-8").write(json.dumps(pm, indent=1, ensure_ascii=False))
    print("place_map: %d placed (%d from the gazetteer, %d decided by hand), %d refused, %d not placed" % (
        len(pm), report["from_gazetteer"], report["from_additions"], len(report["refused"]), len(report["unplaced"])))
    return report

def surname_family_lookup(atlas):
    """Read-only: the Atlas surname catalogue's family for a surname form, or None."""
    sys.path.insert(0, os.path.join(atlas, "scripts")); import surname_variants as sv
    cat = sv.load(os.path.join(atlas, "data", "surname-families.json"))
    def look(sur):
        r = sv.lookup(cat, sur) if sur else None
        return (r[0]["id"], r[0]["name"]) if r and r[2] == "member" else None
    return look

def build(a):
    os.makedirs(OUT, exist_ok=True)
    allp = jl(os.path.join(DATA, "people.json"))
    people = [p for p in allp if p.get("living") is False]          # living people are never looked at
    held = len(allp) - len(people) - sum(1 for p in allp if p.get("living") is True)
    assert held == 0, "people.json carries a person who is neither living nor not living"
    ged = os.path.join(OUT, "people.ged"); write_ged(people, ged)
    slugs = {p["id"].strip("@"): p["slug"] for p in people}
    io.open(os.path.join(OUT, "slugs.json"), "w", encoding="utf-8").write(json.dumps(slugs, ensure_ascii=False))
    strings = set()
    for p in people:
        for k in ("birthPlace", "deathPlace", "burialPlace"):
            if p.get(k): strings.add(p[k])
        for e in p.get("events") or []:
            if e.get("what") in ("lived", "arrival") and e.get("place"): strings.add(e["place"])
    atlas = atlas_path(); prep = seed_place_map(atlas, strings)
    tree, pm = os.path.join(OUT, "tree.json"), os.path.join(OUT, "place_map.json")
    cmd = [sys.executable, os.path.join(TP, "gedcom_to_tree.py"), ged, "--out", tree, "--place-map", pm, "--atlas", atlas, "--living", "omit",
           "--lines", "8", "--focus", FOCUS, "--slugs", os.path.join(OUT, "slugs.json"), "--title", "Roots & Routes",
           "--subtitle", "Explore the family tree ten ways: by generation, place, era and relationship. Click anyone and every view follows."]
    run(cmd)
    t = jl(tree)
    src = {p["id"].strip("@"): p for p in people}
    # colour: the Atlas catalogue's family for the surname; where it holds none, the surname as written with typography folded
    look = surname_family_lookup(atlas)
    def fam_key(p):
        sur = p.get("sur") or ""
        r = look(sur)
        return (r[0], r[1], True) if r else ("~" + fold(sur).replace(" ", ""), sur, False)
    keyed = {p["id"]: fam_key(p) for p in t["people"]}
    cnt = collections.Counter(k[0] for k in keyed.values() if k[0] != "~")   # a person with no surname shares the last colour
    order = [k for k, _ in sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0]))][:7]
    label = {}
    for k in keyed.values(): label.setdefault(k[0], k[1])
    for p in t["people"]:
        k = keyed[p["id"]]
        p["line"] = order.index(k[0]) if k[0] in order else 7
        if k[2]: p["sk"] = k[0]
        p["page"] = "/people/%s/" % slugs[p["id"]] if p["id"] in slugs else None
        if p["page"] is None: p.pop("page")
        s = src.get(p["id"]) or {}
        if est_text(s.get("bornText")): p["bye"] = True
    t["lines"] = [{"sur": label[k], "host": HOST} for k in order] + [{"sur": "Other", "host": HOST}]
    t["meta"].update({"rowLabel": "Family line", "lineLabel": "Family line"})
    drop_conflicts(t, tree)
    keep_death_place(t, people)
    add_routes(t, people)
    io.open(tree, "w", encoding="utf-8").write(json.dumps(t, ensure_ascii=False, separators=(",", ":")))
    rep_path = os.path.join(OUT, "tree.report.json"); rep = jl(rep_path)
    rep["places"] = prep
    rep["people_json"] = {"in_file": len(allp), "living_not_read": len(allp) - len(people), "not_living_read": len(people)}
    rep["catalogue"] = {"people_coloured_by_a_catalogued_family": sum(1 for k in keyed.values() if k[2]), "catalogue_families_present": sorted(k for k in cnt if not k.startswith("~")), "colours": [{"name": label[k], "from_catalogue": not k.startswith("~"), "people": cnt[k]} for k in order]}
    io.open(rep_path, "w", encoding="utf-8").write(json.dumps(rep, indent=1, ensure_ascii=False))

def drop_conflicts(t, tree):
    """A person whose recorded death comes before their birth, or more than 110 years after it, is not one life. They are not drawn, they are named in tree.report.json (conflicts)
    for the research to settle, and every relation to them is removed so the page stays symmetric."""
    bad = {p["id"] for p in t["people"] if p.get("dy") is not None and not 0 <= p["dy"] - p["by"] <= 110}
    rep_path = os.path.splitext(tree)[0] + ".report.json"; rep = jl(rep_path)
    rep["conflicts"] = [{"id": p["id"], "slug": p.get("slug"), "born": p["by"], "died": p["dy"]} for p in t["people"] if p["id"] in bad]
    io.open(rep_path, "w", encoding="utf-8").write(json.dumps(rep, indent=1, ensure_ascii=False))
    if not bad: return
    t["people"] = [p for p in t["people"] if p["id"] not in bad]
    for p in t["people"]:
        for k in ("father", "mother"):
            if p.get(k) in bad: p[k] = None
        p["spouse"] = [x for x in p["spouse"] if x not in bad]; p["kids"] = [x for x in p["kids"] if x not in bad]
    if t.get("focus") in bad: t["focus"] = t["people"][0]["id"]
    print("conflicts: %d people whose death is before their birth are not one life (died before born, or over 110 years) and are not drawn" % len(bad))

def keep_death_place(t, people):
    """The converter takes a later residence as the place of death (a move). A death place the record states and the place map resolves is the place of death."""
    by = {p["id"].strip("@"): p for p in people}
    pm = jl(os.path.join(OUT, "place_map.json"))
    n = 0
    for p in t["people"]:
        src = by.get(p["id"]); r = pm.get((src or {}).get("deathPlace") or "")
        if r and r.get("lat") is not None and r.get("name") and r["name"] != p["dp"]: p["dp"] = r["name"]; n += 1
    print("death places: %d put back to the recorded place of death" % n)

def add_routes(t, people):
    """A route of three or more places, where every stop between birth and death is a dated arrival or residence the archive records, in year order."""
    by = {p["id"].strip("@"): p for p in people}
    pm = jl(os.path.join(OUT, "place_map.json"))
    ok = lambda k: pm.get(k) and pm[k].get("lat") is not None and pm[k].get("name")
    n = 0
    for p in t["people"]:
        src = by.get(p["id"])
        if not src: continue
        mid = [e for e in src.get("events") or [] if e.get("what") in ("lived", "arrival") and e.get("place")]
        if not mid or any(not e.get("year") for e in mid) or any(not ok(e["place"]) for e in mid): continue
        mid.sort(key=lambda e: e["year"])
        stops = [[p["bp"], None, 0]]
        for e in mid:
            nm = pm[e["place"]]["name"]
            if nm != stops[-1][0]: stops.append([nm, int(e["year"]), 1 if re.search(r"before|after|about|circa|\bc\.", e.get("date") or "", re.I) else 0])   # 1 = the year is only an estimate
        if p["dp"] != stops[-1][0]: stops.append([p["dp"], None, 0])
        if len({s[0] for s in stops}) < 3: continue
        if any(b[1] is not None and a[1] is not None and b[1] < a[1] for a, b in zip(stops, stops[1:])): continue
        p["route"] = stops; n += 1
    print("routes: %d people carry a whole route" % n)

def write_roots_links(tree):
    """site/public/roots-links.json: the people Roots & Routes DRAWS (one id each). A person page in story mode offers 'Where they lived' only for those."""
    ids = sorted(p["id"] for p in jl(tree)["people"])
    out = {"note": "The people Roots & Routes draws, by person id. Made by tools/build-tree-page.py; do not edit by hand.", "people": ids}
    io.open(os.path.join(ROOT, "site", "public", "roots-links.json"), "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, separators=(",", ":")))
    print("roots-links: %d people" % len(ids))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.check:
        try: have = jl(os.path.join(OUT, "tree.json"))["meta"]["inputs"]
        except Exception: print("tree page: not built yet. python3 tools/build-tree-page.py"); sys.exit(1)
        if have != inputs_hash(): print("tree page is STALE: the people, place decisions or builder changed since it was built.\n  python3 tools/build-tree-page.py"); sys.exit(1)
        print("tree page is current"); return
    build(a)
    tree = os.path.join(OUT, "tree.json"); pm = os.path.join(OUT, "place_map.json"); ad = os.path.join(OUT, "atlas-data.json"); page = os.path.join(OUT, "roots.html")
    run([sys.executable, os.path.join(TP, "build_atlas_data.py"), "--atlas", atlas_path(), "--tree", tree, "--place-map", pm, "--out", ad])
    t = jl(tree); t["meta"]["inputs"] = inputs_hash()
    io.open(tree, "w", encoding="utf-8").write(json.dumps(t, ensure_ascii=False, separators=(",", ":")))
    write_roots_links(tree)
    tpl = os.path.join(TP, "tree-views.template.html")
    run([sys.executable, os.path.join(TP, "build_page.py"), "--template", tpl, "--tree", tree, "--atlas-data", ad, "--out", page, "--ext", EXT])
    embed = os.path.join(OUT, "roots.embed.html")
    run([sys.executable, os.path.join(TP, "build_page.py"), "--template", tpl, "--tree", tree, "--atlas-data", ad, "--out", embed, "--embed", "--ext", EXT])
    run([sys.executable, os.path.join(TP, "check_tree_page.py"), "--tree", tree, "--atlas-data", ad, "--page", page])
    run([sys.executable, os.path.join(TP, "check_tree_page.py"), "--tree", tree, "--atlas-data", ad, "--page", embed])

if __name__ == "__main__": main()
