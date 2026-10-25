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
import sys, os, re, json, collections, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ged import parse, kid, kids, val, cont
import living_v2 as LV
lr = LV.lr          # the kit's living_rule.py: the estate's one definition

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
    """Any DEAT or BURI node, a bare flag included. For the LIVING test use death_kind(x)."""
    return bool(kid(I[x], "DEAT") or kid(I[x], "BURI"))

def death_kind(x):
    """"record" (a date, place, age, source or a burial), "flag" (`DEAT Y` and nothing behind it) or None."""
    return LV.ged_death_kind(I[x])

# ---------------------------------------------------------------------------
# WHO IS LIVING (David, 16 October 2026; the estate's living-people standard v2)
#
# One definition, and it is not in this file: tools/living_v2.py hands each
# person's facts to the kit's `living_rule.py`, which decides.
#
#   living   80 or younger by year, no death or burial recorded (in the tree OR
#            in anything this archive has read), and no citation from a public
#            record source (FamilySearch, MyHeritage records, Findmypast...).
#            A person with no birth year cannot be shown to be 80 or younger, so
#            is not living by this test.
#   held out a possible minor: an undated person with a living parent (the kit's
#            test), or (David, 25 October 2026, tools/living_v2.py possible_minors)
#            a person under 18 by year with no death recorded, or an undated person
#            whose parent was born in 1975 or later. Not published at all: no page,
#            no name as anyone's relative, no photograph. The 16 October ruling that
#            a child with a KNOWN birth year follows the living standard and has a
#            page is superseded; the kit's rule still carries it (kit gap, reported).
#
# This replaces `datesHidden` (the 80-year test on the tree alone, which began
# here on 10 September), `presumedLiving` (true of 280 plainly dead people
# because the tree gives them no dates) and the 100-year bound in fetch_photos.
# A living person is BUILT from name, relationships and town and country only:
# their dates, events, sources, records, notes and photographs never enter any
# file this script writes, because every committed file in this repository is
# public. See record() below.
# ---------------------------------------------------------------------------
THIS_YEAR = lr.this_year()

# ------------------------------------------------------ duplicates & components

def norm_name(x):
    return re.sub(r"[^a-z]", "", nm(x).lower())

def name_key(x):
    """Surname plus FIRST forename — middle names and initials dropped.

    "Joseph A Polistena" and "Joseph Polistena" are one man: same wife, same
    death date, same grave at Arneytown. An exact-name rule cannot see that,
    because a single middle initial makes the two strings differ. So names are
    compared at this looser key as well — and a match on the looser key demands
    correspondingly stronger corroboration below.
    """
    toks = [t for t in re.sub(r"[^A-Za-z ]", " ", given(x)).split() if len(t) > 1]
    return (re.sub(r"[^a-z]", "", surname(x).lower()),
            re.sub(r"[^a-z]", "", toks[0].lower()) if toks else "")

def death_date_str(x):
    """A full death date — day, month and year — or empty. Highly specific."""
    e = kid(I[x], "DEAT")
    d = val(e, "DATE") if e else ""
    ok = d and re.search(r"\d{4}", d) and re.search(r"[A-Za-z]{3}", d)
    return d.strip().upper() if ok else ""

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

def same_person_loose(a, b):
    """Same surname and first forename, differing only in middle names.

    Because the name test is weaker here, the corroboration has to be stronger
    than for an exact-name match. One of:
      * an identical FULL death date — day, month and year;
      * identical parents AND identical spouse;
      * the same birth year AND either identical parents or identical spouse.
    A shared surname and forename on their own prove nothing at all.
    """
    if norm_name(a) == norm_name(b):
        return False                         # the exact rule already owns this
    ka, kb = name_key(a), name_key(b)
    if not (ka[0] and ka[1]) or ka != kb:
        return False
    da, db = death_date_str(a), death_date_str(b)
    pa, pb = _fam_names(a, "up"), _fam_names(b, "up")
    sa, sb = _fam_names(a, "down"), _fam_names(b, "down")
    ya, yb = birth_year(a), birth_year(b)
    same_par = bool(pa) and pa == pb
    same_sp = bool(sa) and sa == sb
    if da and db and da == db:
        return True
    if same_par and same_sp:
        return True
    if ya and yb and ya == yb and (same_par or same_sp):
        return True
    return False

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

LOOSE_WHY = {}

# ---------------------------------------------------------------------------
# DOCUMENTED JOINS
#
# The automatic rules above merge only on evidence found INSIDE the export.
# Some identifications rest on evidence from outside it — a register act, a
# marriage proclamation — and those cannot be derived, only declared. They are
# declared here, one line per join, each carrying its citation, and they are
# applied last so they can override the automatic caution.
#
# This is deliberately a separate mechanism. An automatic merge is a rule; a
# documented join is an ARGUMENT, and the archive publishes the argument.
# See data/documented-joins.tsv and /the-hundred-and-ten.
# ---------------------------------------------------------------------------
DOCUMENTED_JOINS = []
_dj = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "documented-joins.tsv")
if os.path.exists(_dj):
    import csv as _csv
    for _r in _csv.DictReader(open(_dj), delimiter="\t"):
        DOCUMENTED_JOINS.append(_r)

# ---------------------------------------------------------------------------
# HOW EACH PARENT LINK IS KNOWN
#
# The tree asserts a great many parents; this archive has READ the act behind
# only some of them. data/parent-links.tsv grades the links it knows about, so
# the blood-relatives chart can draw a register-backed parent differently from
# one the tree merely claims. The grades are the kit's: read, index, line, tree
# — and anything ungraded falls through to "tree", which is drawn dashed.
#
# A grade of "drop" REMOVES the link, both from the child's parents and from
# the parent's children. That is for the cases where the export gives somebody
# two complete sets of parents and only one of them can be right: the reason is
# written on the row, and the person it is taken away from keeps it nowhere.
# ---------------------------------------------------------------------------
PARENT_VIA = {}
_pl = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "parent-links.tsv")
if os.path.exists(_pl):
    import csv as _csv
    for _r in _csv.DictReader(open(_pl, encoding="utf-8"), delimiter="\t"):
        PARENT_VIA[(_r["child"].strip(), _r["parent"].strip())] = _r["via"].strip()

# second pass: names that differ only by a middle name or initial
loose = collections.defaultdict(list)
for x in I:
    k = name_key(x)
    if k[0] and k[1]:
        loose[k].append(x)
for k, xs in loose.items():
    if len(xs) < 2:
        continue
    for a_i in range(len(xs)):
        for b_i in range(a_i + 1, len(xs)):
            if same_person_loose(xs[a_i], xs[b_i]):
                a2, b2 = xs[a_i], xs[b_i]
                da, db = death_date_str(a2), death_date_str(b2)
                pa, pb = _fam_names(a2, "up"), _fam_names(b2, "up")
                sa, sb = _fam_names(a2, "down"), _fam_names(b2, "down")
                bits = []
                if da and db and da == db:
                    bits.append(f"the same full death date ({pretty_date(da)})")
                if pa and pa == pb:
                    bits.append("the same parents")
                if sa and sa == sb:
                    bits.append("the same spouse")
                if birth_year(a2) and birth_year(a2) == birth_year(b2):
                    bits.append(f"the same birth year ({birth_year(a2)})")
                LOOSE_WHY[frozenset((a2, b2))] = (
                    "names differing only by a middle name or initial — "
                    + ", ".join(bits))
                union(a2, b2)

# third pass: joins argued from records outside the export
for _j in DOCUMENTED_JOINS:
    a2, b2 = _j["keep"], _j["drop"]
    if a2 in I and b2 in I:
        LOOSE_WHY[frozenset((a2, b2))] = "documented join — " + _j["evidence"][:160] + "…"
        union(a2, b2)

# The unresolved list above was computed BEFORE the documented joins ran, so it
# still named both sides of merges that have since been made — «Giuseppa
# Melluso» was listed as an open question when her whole cluster was the two ids
# a documented join had already united. Recompute it now that every merge, rule
# and argument alike, has been applied.
_before = len(unresolved)
_re = []
for _u in unresolved:
    _roots = sorted({find(i) for i in _u["ids"] if i in I})
    if len(_roots) > 1:
        _re.append({**_u, "copies": len(_roots), "ids": _roots})
if len(_re) != _before:
    print(f"  unresolved shared names: {_before} -> {len(_re)} after the documented joins")
unresolved = _re

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
                           "why": next(
                               (w for pair, w in LOOSE_WHY.items() if pair <= set(xs)),
                               "same name and same birth year" if birth_year(best)
                               else "same name and the same family around them")})

# Components are computed on the CANONICAL graph, after merging. A merge is a
# claim that two records are one person, so it necessarily rejoins whatever
# those records were attached to — and the component count has to reflect that
# or the site would go on calling the family two families after the archive had
# argued they are one.
adj = collections.defaultdict(set)
for fx, f in F.items():
    mem = [canonical.get(k["val"], k["val"]) for k in f["kids"]
           if k["tag"] in ("HUSB", "WIFE", "CHIL") and k["val"] in I]
    for a in mem:
        for b in mem:
            if a != b:
                adj[a].add(b)
seen, comps = set(), []
for x in {canonical.get(z, z) for z in I}:
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

# MEMBERSHIP IS DECIDED HERE; THE NUMBERS ARE HANDED OUT LATER.
# The walk above visits a set, so it discovers the pieces in whatever order
# this interpreter's hash seed produces. That is harmless for membership — who
# is in a piece does not depend on when it was found — but it must not be
# allowed to reach the numbers, so numbering waits until the slug ledger is
# read and can supply a frozen tie-break. See «component numbers» below.

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

def siblings(x):
    """Everyone sharing a parent-family with x, x excluded."""
    fc = kid(I[x], "FAMC")
    if not fc or fc["val"] not in F:
        return []
    f = F[fc["val"]]
    return [c["val"] for c in kids(f, "CHIL") if c["val"] in I and c["val"] != x]

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

# A PERSON'S URL IS MINTED ONCE AND NEVER RECOMPUTED.
#
# This used to derive the slug on every run: namesakes disambiguated first by
# BIRTH YEAR, then by a counter. Both move. This archive corrects birth years
# constantly — that is most of what its research does — and the first
# correction changes the person's URL under anyone who cited it. The counter
# is worse, because it depends on iteration order, so one new namesake
# renumbers the rest.
#
# It is not hypothetical. The Blazevic archive minted the same way and six
# men swapped URLs with each other between two commits in September; this
# archive has been lucky in the ordering, not protected.
#
# site/src/data/person-slugs.json is the ledger: read first, used unchanged,
# appended to only for an id never seen before. Never edited, never deleted —
# a published URL is a promise, and the number must not pass to another person.
_LEDGER = os.path.join(ROOT, "site", "src", "data", "person-slugs.json") \
    if "ROOT" in dir() else os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         "..", "site", "src", "data", "person-slugs.json")
try:
    _ledger_doc = json.load(open(_LEDGER, encoding="utf-8"))
except Exception:
    _ledger_doc = {"_why": ["Written by tools/build.py"], "slugs": {}}

people_ids = [x for x in I if canonical[x] == x]
slug_of = {x: _ledger_doc["slugs"][x] for x in people_ids if x in _ledger_doc["slugs"]}
used = collections.Counter()
_minted = []
for x in sorted(people_ids, key=lambda z: (nm(z), birth_year(z) or 9999)):
    if x in slug_of:
        continue
    base = kebab(nm(x))
    y = birth_year(x)
    taken = set(slug_of.values()) | set(_ledger_doc["slugs"].values())
    cand = base
    if cand in taken:
        cand = f"{base}-{y}" if y else f"{base}-{used[base] + 1}"
        while cand in taken:
            cand += "-2"
    used[base] += 1
    slug_of[x] = cand
    _minted.append((x, cand))

# ---- THE SECOND SOURCE -------------------------------------------------------
# People proved from a register that the export never held. They are minted
# from the SAME ledger by the SAME rule, because a register-proved person's URL
# is exactly as much of a promise as an exported one's, and because the two
# share one namespace: there is already an export «Rosario Nicotra» (the child
# of 1883) and a register «Rosario Nicotra» (the bracciante of Mascali, his
# grandfather's generation), and whichever is minted second must be the one
# that takes a suffix. Sorting by row name makes that deterministic.
import register_source as _reg
_REG_ROWS = _reg.rows()
_REG_NEW = _reg.to_create(_REG_ROWS)
_REG_SEX = _reg.sexes(_REG_ROWS)
reg_pid = {r["name"].strip(): "@R" + kebab(_reg.clean(r["name"])) + "@"
           for r in _REG_NEW}
# An id must be stable across runs or the ledger grows a second slug for the
# same person. Two rows whose names differ only inside the parenthesis would
# kebab to one id, so the clash is resolved here and recorded, never guessed.
_seen_pid = {}
# LEDGER-AWARE NUMBERING (18 October 2026). Clash ids used to be numbered by NAME
# ORDER alone, so every new namesake had to be given a parenthesis that sorted AFTER its
# namesakes or it shifted a published page address: eleven renames in a week. A name the
# ledger already owns now keeps its id; only NEW names take the next free number, in name
# order. The guard below still fails the build if an id's owner ever changes.
_owned = {v: k for k, v in (_ledger_doc.get("names") or {}).items()}
for r in _REG_NEW:
    _nm = r["name"].strip()
    _pid = _owned.get(_nm)
    if _pid and _pid.startswith(reg_pid[_nm][:-1]):
        reg_pid[_nm] = _pid
        _seen_pid[_pid] = _nm
for r in sorted(_REG_NEW, key=lambda z: z["name"]):
    if r["name"].strip() in _seen_pid.values():
        continue
    base_pid = reg_pid[r["name"].strip()]
    if base_pid in _seen_pid:
        n = 2
        while f"{base_pid[:-1]}-{n}@" in _seen_pid:
            n += 1
        base_pid = f"{base_pid[:-1]}-{n}@"
    _seen_pid[base_pid] = r["name"].strip()
    reg_pid[r["name"].strip()] = base_pid

# THE GUARD THAT THE COMMENT ABOVE NEEDED. «An id must be stable across runs» was a
# promise and nothing enforced it. Clash ids are numbered by NAME ORDER, so a new
# namesake whose name sorts BETWEEN two existing ones renumbers the later one: on
# 17 October 2026 a third Alfio Nicotra, «(of Salvadore and Maria Barbagallo)»,
# sorted between «(of Rosa Pappalardo)» and «(of Santa Previtera)», the 1869
# man's id moved from -2 to -3, and the ledger handed his slug to the NEW child.
# The ledger itself never changed, which is why nothing noticed: it maps id to
# slug, and it was the person behind the id that moved. THE FIX I TRIED FIRST,
# numbering by file order, passed a ledger-only test and then swapped the birth
# years of two other namesake pairs (Mariano Mazza, Filippo Arena), because those
# ids had been minted under name order. So the rule is NOT changed. What is
# recorded is who owns each id, and a build where an id now belongs to a
# different name FAILS instead of silently moving a page address.
_names_doc = _ledger_doc.setdefault("names", {})
_cur_names = {v: k for k, v in reg_pid.items()}
_drift = [(i, _names_doc[i], _cur_names[i]) for i in _cur_names
          if i in _names_doc and _names_doc[i] != _cur_names[i]]
if _drift:
    for _i, _was, _now in _drift:
        print(f"  FAIL  slug ledger: id {_i} was «{_was}» and is now «{_now}» — its slug "
              f"{_ledger_doc['slugs'].get(_i, '?')} would silently move to a different person")
    print("        Clash ids are numbered by NAME ORDER. Give the new row a name that sorts "
          "AFTER its namesakes, or the ids of people already published will shift.")
    sys.exit(1)
for _i, _n in _cur_names.items():
    _names_doc.setdefault(_i, _n)
_ledger_doc["names"] = dict(sorted(_names_doc.items()))
for r in sorted(_REG_NEW, key=lambda z: z["name"]):
    x = reg_pid[r["name"].strip()]
    if x in _ledger_doc["slugs"]:
        slug_of[x] = _ledger_doc["slugs"][x]
        continue
    base = kebab(_reg.clean(r["name"]))
    y = _reg.year(r.get("born") or "") or _reg.year(r.get("died") or "")
    taken = set(slug_of.values()) | set(_ledger_doc["slugs"].values())
    cand = base
    if cand in taken:
        cand = f"{base}-{y}" if y else f"{base}-{used[base] + 1}"
        while cand in taken:
            cand += "-2"
    used[base] += 1
    slug_of[x] = cand
    _minted.append((x, cand))

# Written EVERY run, deterministically, so a stamp or an orphan check can
# account for it: a file that is only sometimes written looks exactly like a
# file whose generator has been deleted.
for _pid, _sl in _minted:
    _ledger_doc["slugs"].setdefault(_pid, _sl)
_ledger_doc["slugs"] = dict(sorted(_ledger_doc["slugs"].items()))
open(_LEDGER, "w", encoding="utf-8").write(
    json.dumps(_ledger_doc, ensure_ascii=False, indent=1) + "\n")
if _minted:
    print(f"  person-slugs.json: {len(_minted)} new slug(s) frozen")

# --------------------------------------------------------- component numbers
#
# A NUMBER MAY NOT DEPEND ON THE ORDER THE GRAPH WALK HAPPENED TO FIND THINGS.
#
# The pieces were found above by a walk over a set, so their discovery order
# changes with the interpreter's hash seed. Sorting by size alone does not fix
# that: `sort` is stable, so same-size pieces keep the order they arrived in,
# and this export is mostly same-size pieces — eight of the ten are a single
# person each. Two builds of identical data therefore renumbered them freely:
# 7 became 8 and 9 became 3 with nobody's parentage changing, and the notes on
# /components/ that were keyed to a number stopped rendering. check_shown.py
# carries the canaries that caught it.
#
# So: largest piece first, and ties broken by the alphabetically first slug in
# the piece. Size first because every page that lists the pieces leads with the
# biggest, and the slug because it is the one name for a person this archive
# promises never to recompute — person-slugs.json freezes it at birth. Breaking
# the tie on a birth year or a display name would hand the numbering straight
# back to the research, which corrects both constantly; breaking it on the
# GEDCOM id would be stable but arbitrary, and would order the singles table
# @I1@, @I10@, @I100@, @I2@. Ordering by slug makes that table's numbers climb
# with the names beside them.
#
# This is still a number assigned by a build, and it still moves when the data
# moves: join two pieces and everything below them shifts up. It is stable
# across runs, not across findings — so prose must go on selecting a piece by
# who is in it, exactly as the comment at the top of components.astro insists.
comps.sort(key=lambda c: (-len(c), min(slug_of.get(x, "\uffff") for x in c)))
comp_of = {}
for idx, c in enumerate(comps, 1):
    for x in c:
        comp_of[x] = idx
for z in I:                      # every original id inherits its canonical's component
    comp_of.setdefault(z, comp_of.get(canonical.get(z, z), 0))

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

# ------------------------------------------------- who is living, who is held out

_EV = LV.evidence()
def _first_year(ids):
    for z in ids:
        y = birth_year(z)
        if y:
            return y
    return None

_status_in = {}
for x in people_ids:
    _orig = [x] + [z for z in I if canonical[z] == x and z != x]
    _status_in[x] = {
        "by": _first_year(_orig),
        # a death RECORD only; a bare `DEAT Y` is undated_dead (kit living_rule, 25 Oct 2026: it frees no one born in the window)
        "dead": any(death_kind(z) == "record" for z in _orig) or slug_of[x] in _EV["dead"],
        "undated_dead": any(death_kind(z) == "flag" for z in _orig),
        "cites": [s for z in _orig for s in src_of(z)] + _EV["cites"].get(slug_of[x], []),
        "parents": sorted({canonical.get(q) for z in _orig for q in parents(z)} - {None, x}),
    }
LIVING, HELD = LV.classify(_status_in, THIS_YEAR)
MINORS = LV.possible_minors(_status_in, THIS_YEAR)      # the part of HELD this archive adds to the kit's test
PUBLIC_SOURCE = {x for x in people_ids if lr.public_source(_status_in[x]["cites"])}
print(f"  living {len(LIVING)}  held out {len(HELD)}  "
      f"(of {len(people_ids)} people; {len(PUBLIC_SOURCE)} carry a public-source citation)")

# A LIVING PERSON'S URL MAY NOT CARRY A BIRTH YEAR. Namesakes were told apart by
# the birth year ("a-name-1799"), which put a living person's year in
# a path, a link and a file name. A living person's slug is re-minted without it
# (name, then the first free number). Their old URLs stop resolving: those pages
# were noindex and are rebuilt under the new slug. The ledger is updated in the
# same run. The hand-kept files that key a person by slug (data/corrections.tsv,
# parent-links.tsv, read-people.tsv) were moved with it.
_YEAR_SLUG = re.compile(r"-(1[5-9]\d\d|20\d\d)$")
_reslug = {}
for x in sorted(LIVING, key=lambda z: slug_of[z]):
    if _YEAR_SLUG.search(slug_of[x]):
        base = _YEAR_SLUG.sub("", slug_of[x])
        taken = set(slug_of.values()) | set(_ledger_doc["slugs"].values())
        n = 2
        while f"{base}-{n}" in taken:
            n += 1
        _reslug[slug_of[x]] = f"{base}-{n}"
        slug_of[x] = f"{base}-{n}"
        _ledger_doc["slugs"][x] = slug_of[x]
if _reslug:
    print(f"  living slugs re-minted without a birth year: {len(_reslug)}")

def is_living(x):
    return x in LIVING

def is_held(x):
    return x in HELD

# -------------------------------------------------------------- photo lookup

photos = {}
if os.path.exists("data/photo-manifest.json"):
    # photos stays a list of FILENAMES, because four pages, a gate and the kit's
    # Gallery all index it that way. The measurements go beside it in photoSize,
    # keyed by filename, so nothing that reads photos has to change.
    #
    # THREE RULES, each of which was being broken on 9 October 2026.
    #
    # 1. CANONICALISE THE XREF. This read m["xref"] raw, so a photograph the
    #    export attached to a person who is a DUPLICATE reached nobody: the
    #    duplicate has no record and the surviving person never heard about the
    #    image. Michael Rocco Mazza, who this archive is named for, had no
    #    photograph published while a 3072x2304 one sat in photos/living/
    #    attached to @I20@, a duplicate of his own @I26@.
    #
    # 2. SKIP A ROW THAT SAYS IT SHOULD NOT BE DRAWN. «notShown» carries the
    #    reason in prose. 26 rows have one: 22 are a single MyHeritage stock
    #    collection graphic that arrived under 22 names for 11 people — nine of
    #    whom had no other image, so their whole Photographs section was stock
    #    art captioned with their name — and 4 are one photograph held twice,
    #    proved by decoding both and differing by at most 4 levels of 255.
    #
    # 3. NEVER SHOW ONE PERSON THE SAME FILE TWICE. Canonicalising merges two
    #    xrefs' photographs together, and some of those are byte-identical
    #    copies, so they are deduplicated by content. ACROSS people they are
    #    left alone: one photograph showing two relatives is tagged to both in
    #    the export, and that is correct rather than a fault.
    photo_size = {}
    _seen_hash = {}
    for m in json.load(open("data/photo-manifest.json")):
        if not os.path.exists(m.get("path", "")):
            continue
        if m.get("notShown"):
            continue
        who = canonical.get(m["xref"], m["xref"])
        if who in LIVING or who in HELD:
            continue          # no photograph of a living or a held-out person
        digest = hashlib.sha256(open(m["path"], "rb").read()).hexdigest()
        if digest in _seen_hash.setdefault(who, set()):
            continue
        _seen_hash[who].add(digest)
        photos.setdefault(who, []).append(m["file"])
        if m.get("w") and m.get("h"):
            photo_size[m["file"]] = [m["w"], m["h"]]

# THE MANIFEST NAMES EVERY PHOTOGRAPH AND WHOSE IT IS, and it is a committed file.
# A photograph of a living or held-out person is withdrawn from it here, so
# neither the person nor the picture is listed anywhere that is published.
if os.path.exists("data/photo-manifest.json"):
    _man = json.load(open("data/photo-manifest.json"))
    _keep = [m for m in _man if canonical.get(m["xref"], m["xref"]) not in LIVING | HELD]
    if len(_keep) != len(_man):
        print(f"  photo-manifest.json: {len(_man) - len(_keep)} photograph(s) of living or held-out people withdrawn")
        json.dump(_keep, open("data/photo-manifest.json", "w"), indent=1, ensure_ascii=False)

# ---------------------------------------------------------------- the records

LIVING_PLACE_CUT = collections.Counter()   # how each living person's place was settled

def living_place(x):
    """A living person's TOWN AND COUNTRY: nothing finer, nothing else.

    The birth place if the tree gives one, else a place they are recorded living
    at. Cut back to the town if it names a street, an address-like string or an
    institution (a hospital, a care home), and given its country if it lacks one.
    """
    ev = events(x)
    raw = next((e["place"] for e in ev if e["tag"] == "BIRT" and e["place"]), "") \
        or next((e["place"] for e in ev if e["tag"] == "RESI" and e["place"]), "")
    text, how = LV.town_country(raw, country)
    LIVING_PLACE_CUT[how or ("place" if text else "none")] += 1
    return text

def record(x):
    rec = {
        "id": x, "slug": slug_of[x], "name": nm(x),
        "given": given(x), "surname": surname(x),
        "sex": val(I[x], "SEX"),
        "living": is_living(x),
        "comp": comp_of.get(x, 0),
    }
    if is_living(x):
        # NAME, RELATIONSHIPS (wired below), TOWN AND COUNTRY, AND NOTHING MORE.
        # No dates, no events, no sources, no records, no photographs: they are
        # not hidden by a template, they are never built, so they cannot reach a
        # file this repository publishes.
        rec["birthPlace"] = living_place(x)
        return rec
    ev = events(x)
    rec.update({
        "born": birth_year(x),
        "died": death_year(x),
        "events": ev,
        "birthPlace": next((e["place"] for e in ev if e["tag"] == "BIRT" and e["place"]), ""),
        "deathPlace": next((e["place"] for e in ev if e["tag"] == "DEAT" and e["place"]), ""),
        "burialPlace": next((e["place"] for e in ev if e["tag"] == "BURI" and e["place"]), ""),
        "sources": src_of(x),
        "photos": photos.get(x, []),
        "photoSize": {f: photo_size[f] for f in photos.get(x, []) if f in photo_size},
    })
    return rec

records = [record(x) for x in people_ids if not is_held(x)]
print(f"  living places settled: {dict(LIVING_PLACE_CUT)}")

# The register people join here, BEFORE the relationship wiring, so that every
# rule below applies to them unchanged: the parent grading, the edges a row
# adds that the tree never had, the children seen from the other end.
_reg_slug_by_row = {nm_: slug_of[pid_] for nm_, pid_ in reg_pid.items()}
for r in sorted(_REG_NEW, key=lambda z: z["name"]):
    nm_ = r["name"].strip()
    records.append(_reg.record(r, reg_pid[nm_], _reg_slug_by_row[nm_],
                               _REG_SEX.get(nm_, "")))

# A register person comes from an act, so is long dead: say so with the same rule
# rather than assume it. If a register row ever described somebody 80 or younger
# with no death, this refuses to build instead of publishing them in full.
for _rp in records:
    if _rp.get("fromRegister"):
        assert not lr.is_living(_rp.get("born"), bool(_rp.get("died") or _rp.get("diedText")), [], THIS_YEAR), \
            "a register person would be living under the standard: " + _rp["id"]

# An act's parentage becomes an edge with via «read» — the value this archive
# already uses for a link a register proved and the tree did not carry. A
# parent whose own row does not exist is skipped and counted, never invented.
_reg_unfiled = []
for kind, child, parent in _reg.edges(_REG_ROWS):
    pslug = _reg_slug_by_row.get(parent)
    if not pslug:
        _reg_unfiled.append(parent)
        continue
    cslug = child if kind == "slug" else _reg_slug_by_row.get(child)
    if cslug:
        PARENT_VIA.setdefault((cslug, pslug), "read")

by_id = {r["id"]: r for r in records}

def link(x):
    c = canonical.get(x)
    r = by_id.get(c)
    return {"id": c, "name": r["name"], "slug": r["slug"], "living": r["living"]} if r else None

for r in records:
    x = r["id"]
    orig = [z for z in I if canonical[z] == x]
    par, ch, sp, sib = [], [], [], []
    for o in orig:
        par += parents(o)
        ch += children(o)
        sp += spouses(o)
        sib += siblings(o)
    def uniq(ids):
        out, s = [], set()
        for i2 in ids:
            c = canonical.get(i2)
            if c and c != x and c not in s:
                s.add(c)
                out.append(link(c))
        return [z for z in out if z]
    r["parents"], r["children"], r["spouses"] = uniq(par), uniq(ch), uniq(sp)
    r["siblings"] = uniq(sib)

# Grade every parent edge, drop the ones a row says are wrong, and ADD the ones
# a record gives that the tree never had — a register names parents the export
# does not always carry. Children are the same edges seen from the other end.
by_slug = {r["slug"]: r for r in records}
for r in records:
    kept = []
    for pa in r["parents"]:
        v = PARENT_VIA.get((r["slug"], pa["slug"]), "tree")
        if v == "drop":
            continue
        pa["via"] = v
        kept.append(pa)
    have = {pa["slug"] for pa in kept}
    for (child, parent), v in PARENT_VIA.items():
        if child != r["slug"] or v == "drop" or parent in have:
            continue
        pr = by_slug.get(parent)
        if pr:
            kept.append({"id": pr["id"], "name": pr["name"], "slug": pr["slug"],
                         "living": pr["living"], "via": v})
    r["parents"] = kept
for r in records:
    kept, have = [], set()
    for c in r["children"]:
        v = PARENT_VIA.get((c["slug"], r["slug"]), "tree")
        if v == "drop":
            continue
        c["via"] = v
        kept.append(c); have.add(c["slug"])
    for (child, parent), v in PARENT_VIA.items():
        if parent != r["slug"] or v == "drop" or child in have:
            continue
        ch = by_slug.get(child)
        if ch:
            kept.append({"id": ch["id"], "name": ch["name"], "slug": ch["slug"],
                         "living": ch["living"], "via": v})
    r["children"] = kept

# HOW AN EDGE IS KNOWN IS A RECORD, and a living person has none on the page: an
# edge with a living end keeps the relationship and loses the grade that says
# which register proved it.
_living_slugs = {r["slug"] for r in records if r["living"]}
for r in records:
    for b in ("parents", "children"):
        for e in r[b]:
            if r["living"] or e["slug"] in _living_slugs:
                e.pop("via", None)

# THE HELD-OUT, BY ID. A possible minor is not published, so the only thing this
# repository may say about them is that a GEDCOM id is withheld: no name, no year,
# no slug. tools/check_living_v2.py reads this file to prove none of them appears
# anywhere, and (with the private GEDCOM, locally) recomputes the list from scratch
# and fails if it differs. `proseMentionsAllowed` is a ratchet on the number of
# built pages that still name a held-out person in prose, and only ever goes down.
_hp = "data/held-out.json"
_prev = json.load(open(_hp)) if os.path.exists(_hp) else {}
json.dump({
    "_why": ["Ids of people the archive does not publish at all: possible minors, under the estate's "
             "living-people standard v2 (16 October 2026) and David's ruling of 25 October 2026. By id and never by name.",
             "A held-out person has no page, is nobody's relative here, and has no entry in "
             "site/src/data/person-slugs.json. Recomputed by tools/living_v2.py on every build."],
    "rule": "not recorded dead, and either (kit) no public-source citation, no birth year and a living parent, or "
            "(minors) born 18 years ago or less, or undated with a parent born in 1975 or later",
    "ids": sorted(HELD),
    "minors": sorted(MINORS),
    "proseMentionsAllowed": _prev.get("proseMentionsAllowed", 0),
}, open(_hp, "w"), indent=1)

# THE SLUG LEDGER NAMES EVERYONE IT HAS EVER MINTED FOR, and a held-out person is
# not published, so they cannot stay in a published file by id and name.
for _h in HELD:
    _ledger_doc["slugs"].pop(_h, None)
open(_LEDGER, "w", encoding="utf-8").write(
    json.dumps(_ledger_doc, ensure_ascii=False, indent=1) + "\n")

os.makedirs(OUT, exist_ok=True)
json.dump(records, open(f"{OUT}/people.json", "w"), indent=1, ensure_ascii=False)

# A DUPLICATE OR AN UNRESOLVED NAME IS PUBLISHED IN data/audit.json AND ON /audit,
# by name and year. Where the person is living or held out, the entry is not
# published at all; the COUNT of what was left out is kept.
def _is_nonpublic(i):
    c = canonical.get(i, i)
    return c in LIVING or c in HELD
_dup_all = len(duplicates)
duplicates = [d for d in duplicates
              if not (_is_nonpublic(d["kept"]) or any(_is_nonpublic(z) for z in d["dropped"]))]
_unres_all = len(unresolved)
_un = []
for u in unresolved:
    ids = [i for i in u["ids"] if not _is_nonpublic(i)]
    if len(ids) > 1:                       # still a name two or more PUBLISHED people share
        _un.append({**u, "ids": ids, "copies": len(ids)})
unresolved = _un

stats = {
    "exported": len(I), "people": len(records),
    "duplicates": sum(len(d["dropped"]) for d in duplicates),
    "unresolvedNames": len(unresolved),
    "livingRule": "80 or younger by year, no death or burial recorded",
    "living": sum(1 for r in records if r["living"]),
    "heldOut": len(HELD),
    "written": sum(1 for r in records if not r["living"]),
    "withDeath": sum(1 for r in records if r.get("died")),
    "ageThreshold": lr.LIVING_YEARS,
    "deceased": sum(1 for r in records if not r["living"]),
    "families": len(F), "sources": len(S),
    "components": [len(c) for c in comps],
    "photos": sum(len(v) for v in photos.values()),
    # What the archive HOLDS, as against what it draws. The two differ by the
    # rows carrying «notShown» — the MyHeritage stock graphic and one
    # photograph held twice — plus any byte-identical twin the dedupe above
    # drops. /documents/ needs both numbers or its sentence is a tautology.
    "photosHeld": sum(1 for _m in json.load(open("data/photo-manifest.json"))
                      if os.path.exists(_m.get("path", ""))),
    "earliest": min([r["born"] for r in records if r.get("born")] or [0]),
}
json.dump({"stats": stats, "duplicates": duplicates, "unresolved": unresolved},
          open("data/audit.json", "w"), indent=1, ensure_ascii=False)
print(json.dumps(stats, indent=1))

# ---------------------------------------------------------------------------
# THIS SCRIPT IS STAGE ONE OF FOUR, AND ON ITS OWN IT DESTROYS DATA.
#
# people.json is written here from the export alone. build_spine.py,
# build_more.py and build_person_extras.py then ADD `records`, `corrections`,
# `onSpine` and `ancGen` to the rows. Running build.py by itself rewrites the
# file from scratch and drops all four from every person.
#
# On 22 September 2026 that happened: a commit regenerated people.json with
# this script alone and sixty-eight people lost their `records`, among them a
# Brisbane Catholic Cemetery burial entry. It had to be restored from the
# previous file. Nothing warned, because every later check saw a file that was
# internally consistent.
#
# So the script says so itself, every run. A warning in a memory or a commit
# message is not in front of whoever runs this next.
print("\n  NOTE  build.py is stage one of four. people.json is INCOMPLETE until you run:")
print("          python3 tools/build_spine.py && python3 tools/build_more.py \\")
print("            && python3 tools/build_person_extras.py")
print("        Stopping here drops `records`, `corrections`, `onSpine` and `ancGen`")
print("        from every person. See the comment at the foot of this file.")
