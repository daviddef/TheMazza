#!/usr/bin/env python3
"""Check the people the registers prove and the family tree does not hold.

data/documented-additions.tsv is the one file here that does not come from
Michael's export, so nothing else validates it. Its parents are written as
plain NAMES rather than slugs, which is how this archive's oldest failure gets
in: a name that matches two people, and a claim attached to the wrong one.

So this checks by arithmetic what attention keeps missing:

  * no two rows may share a name -- a duplicate name makes every father= and
    mother= that points at it ambiguous, and ambiguity is how the wrong
    Domenico Prostamo, the wrong Mariano Mazza and the wrong Angela were
    nearly written into the line;
  * a parent named in this file must be older than the child, and must not
    have died before the child was born;
  * a parent's generation must be exactly one above the child's;
  * a parent link must not close a loop;
  * a gen must agree with the export's ancGen wherever the export has one;
  * a row whose person IS in the export no longer belongs here, because the
    premise of the file is that the tree lacks them.

Exit 1 on a failure, 0 on a clean run, so the build can refuse to publish.
"""
import csv, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(HERE, ".."))

rows = list(csv.DictReader(open("data/documented-additions.tsv", encoding="utf-8"), delimiter="\t"))
people = json.load(open("site/src/data/people.json", encoding="utf-8"))
fails, notes = [], []

BLANK = {"", "—", "-", "?"}

def norm(s):
    """Fold a name for comparison, so 'Fragalà' and 'Fragala' are one person
    and 'de Amico' and 'De Amico' are too."""
    s = (s or "").strip().lower()
    for a, b in (("à","a"),("á","a"),("è","e"),("é","e"),("ì","i"),("í","i"),
                 ("ò","o"),("ó","o"),("ù","u"),("ú","u")):
        s = s.replace(a, b)
    # KEEP THE DIGITS. This used to strip them, and «Antonio Arena (b. New York
    # 1896)» and «Antonio Arena (b. New York 1902)» then folded to one string --
    # so the duplicate-name check reported two real brothers as one ambiguous
    # name. The parentheses are how this file disambiguates namesakes and the
    # year inside them is usually the only thing that differs.
    return re.sub(r"[^a-z0-9 ]", " ", s).split()

def key(s):
    return " ".join(norm(s))

def bare(s):
    """The name without a disambiguating parenthesis -- 'Filippo Arena (the
    younger)' and 'Giovanni Arena (b. 1854)' are how this file already tells
    two namesakes apart, and the bare name is what an act would have said."""
    return key(re.sub(r"\s*\(.*?\)", "", s or ""))

def year(s):
    """A year and how firm it is. These fields are prose -- 'c. 1790s',
    'before January 1815', 'alive at Briatico, June 1849' -- so read the
    qualifier as well as the digits, and refuse to reason on 'Not yet sought'."""
    s = (s or "").strip()
    if s in BLANK or not s:
        return None, 0
    m = re.search(r"\b(1[5-9]\d\d)(s\b)?", s)
    if not m:
        return None, 0
    y, slack = int(m.group(1)), 0
    if m.group(2):          # '1790s' -- a decade, so the middle of it
        y, slack = y + 5, 6
    if re.search(r"\bc\.|\babout\b|\bcirca\b", s, re.I):
        slack = max(slack, 3)
    if re.search(r"\bbefore\b|\bby\b", s, re.I):
        return y, -1        # an upper bound, not a date
    if re.search(r"\bafter\b|\balive\b", s, re.I):
        return y, -2        # a lower bound
    return y, slack

def gen(r):
    m = re.match(r"^\s*(\d+)\s*$", r.get("gen") or "")
    return int(m.group(1)) if m else None

# --- one name, one person -------------------------------------------------
seen = {}
for i, r in enumerate(rows, start=2):
    k = key(r["name"])
    if k in seen:
        fails.append(f"two rows are both named «{r['name']}» (lines {seen[k]} and {i}) — "
                     f"every father= and mother= pointing at that name is now ambiguous; "
                     f"disambiguate one the way «Filippo Arena (the younger)» is")
    seen[k] = i

# --- and the export does not already hold them -----------------------------
export = {}
for p in people:
    export.setdefault(key(p["name"]), []).append((p["slug"], p.get("ancGen")))
by_slug = {p["slug"]: p for p in people}
for r in rows:
    claim = (r.get("inTree") or "—").strip()
    hit = export.get(key(r["name"])) or export.get(bare(r["name"])) or []
    spine = [x for x in hit if x[1] is not None]
    hit = hit if len(hit) == 1 else spine

    if claim not in BLANK:
        # the row says the tree HAS this person: the slug must be real, and the
        # note must not still be telling readers the opposite
        if claim not in by_slug:
            fails.append(f"{r['name']}: inTree «{claim}» is not a slug in the export")
        if re.search(r"not in the (family )?tree|absent from the family tree", r["note"], re.I) \
           and not re.search(r"is in the family tree|IN THE FAMILY TREE", r["note"]):
            fails.append(f"{r['name']}: inTree says {claim}, but the note still tells the reader "
                         f"they are not in the tree")
    elif len(hit) == 1:
        # the row claims absence and a namesake exists: the note must address it
        if re.search(r"not in the (family )?tree|absent from the family tree", r["note"], re.I) \
           and not re.search(r"namesake|different people|nothing to do with|two men|two different",
                             r["note"], re.I):
            fails.append(f"«{r['name']}» claims to be absent, yet {hit[0][0]} in the export answers "
                         f"to the name — either set inTree, or say in the note why they are "
                         f"two different people")

# --- and the gen column means what the export means by it ------------------
# This column was silently carrying two scales: the Arena, Arlotta and Russo rows
# counted the way the export's ancGen does, and the whole Briatico block counted
# three lower. Nothing complained, because nothing compared them.
anc = {}
for p in people:
    if p.get("ancGen") is not None:
        anc.setdefault(key(p["name"]), set()).add(p["ancGen"])
for r in rows:
    g, hit = gen(r), anc.get(key(r["name"]))
    if g is not None and hit and len(hit) == 1 and g != next(iter(hit)):
        fails.append(f"{r['name']} is gen {g} here and ancGen {next(iter(hit))} in the export — "
                     f"the column has to mean one thing")

# --- resolve the parents ---------------------------------------------------
by_name, by_bare = {}, {}
for r in rows:
    by_name.setdefault(key(r["name"]), []).append(r)
    by_bare.setdefault(bare(r["name"]), []).append(r)

def parent_of(r, col):
    """Resolve a parent written as a plain name, in the order that keeps two
    namesakes apart.

    Exact row first: «Filippo Arena» means the row written «Filippo Arena», not
    the one written «Filippo Arena (the younger)».

    Then the EXPORT, before any loose matching. Maria Donato's father is written
    «Michele Donato» and means the man in the tree, born at Scilla in 1855 — not
    his uncle of the same name born at Messina, who has a row here. Skipping this
    step silently re-hung a documented daughter on the wrong man.

    Only then the bare name, and never when the export answers to it too."""
    v = (r.get(col) or "").strip()
    if v in BLANK:
        return None
    hits = by_name.get(key(v))
    if hits:
        return hits[0] if len(hits) == 1 else None
    ex = export.get(key(v), [])
    if len(ex) == 1 or len([x for x in ex if x[1] is not None]) == 1:
        return None                      # a person the tree already holds
                                         # (three Giovanni Arena in the export, one on the spine —
                                         #  this file records ancestors, so the spine one is meant)
    loose = by_bare.get(bare(v), [])
    if loose and export.get(bare(v)):
        fails.append(f"{r['name']}: {col} «{v}» could be {loose[0]['name']} in this file or "
                     f"{export[bare(v)][0][0]} in the export — spell out which")
        return None
    if len(loose) > 1:
        fails.append(f"{r['name']}: {col} «{v}» matches {len(loose)} rows in this file — "
                     f"which one is the parent cannot be told from the name")
        return None
    if loose:
        return loose[0]
    # Nobody. Usually fine -- most parents named in an act have no row. But a
    # near-miss is not fine: renaming «Maria Paladino» to «Marta Paladino»
    # silently orphaned her son's mother= and nothing said a word.
    w = bare(v).split()
    if len(w) >= 2:
        def close(a, b):        # Maria / Marta share three letters; Paolo / Maria share none
            n = min(len(a), len(b), 3)
            return n == 3 and a[:3] == b[:3]
        near = [x for x in rows
                if bare(x["name"]).split()[-1:] == w[-1:]
                and bare(x["name"]) != bare(v)
                and x is not r
                and close(bare(x["name"]).split()[0], w[0])]
        if len(near) == 1:
            fails.append(f"{r['name']}: {col} «{v}» matches no row, but «{near[0]['name']}» "
                         f"shares the surname — a rename that left this link behind?")
    return None

def chain(r, seen=None):
    seen = seen or set()
    for col in ("father", "mother"):
        p = parent_of(r, col)
        if p and key(p["name"]) not in seen:
            seen.add(key(p["name"]))
            chain(p, seen)
    return seen

for r in rows:
    cb, cslack = year(r["born"])
    cg = gen(r)
    for col in ("father", "mother"):
        p = parent_of(r, col)
        if not p:
            continue
        if key(p["name"]) == key(r["name"]):
            fails.append(f"{r['name']} is given as their own {col}")
            continue
        if key(r["name"]) in chain(p):
            fails.append(f"{p['name']} already descends from {r['name']} — "
                         f"naming them {r['name']}'s {col} closes a loop")
            continue
        pb, pslack = year(p["born"])
        if cb and pb and pslack != -2 and cslack != -1:
            slack = (pslack if pslack > 0 else 0) + (cslack if cslack > 0 else 0)
            if pb - slack >= cb:
                fails.append(f"{r['name']} born {r['born']} — but {col} {p['name']} is born "
                             f"{p['born']}, which is not earlier")
        pd, pdq = year(p["died"])
        if cb and pd and pdq != -2 and cslack not in (-1,) and pd < cb - 1 - (cslack if cslack > 0 else 0):
            fails.append(f"{r['name']} born {r['born']} — but {col} {p['name']} died {p['died']}")
        pg = gen(p)
        if cg is not None and pg is not None and pg != cg + 1:
            fails.append(f"generations disagree: {r['name']} is gen {cg}, so {col} {p['name']} "
                         f"should be gen {cg+1} and is gen {pg}")
    if cg is None and (r.get("gen") or "").strip() not in BLANK:
        fails.append(f"{r['name']}: gen «{r['gen']}» is not a number")

seen_msg = set()
fails = [f for f in fails if not (f in seen_msg or seen_msg.add(f))]

for n in notes:
    print("  note  ", n)
for f in fails:
    print("  FAIL  ", f)
print(f"  {'ok   ' if not fails else 'FAIL '} {len(rows)} documented additions — "
      f"{len(fails)} problem{'' if len(fails)==1 else 's'}, {len(notes)} note{'' if len(notes)==1 else 's'}")
sys.exit(1 if fails else 0)
