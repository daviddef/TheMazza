#!/usr/bin/env python3
"""Check the two files that say what the records corrected.

data/corrections.tsv is the largest hand-written file in this archive and until
now nothing validated a line of it. Its sibling check_additions.py found six
published falsehoods within an hour of existing, and this file carries the same
risks and a few of its own:

  * a confidence label the page has no legend for. The reader is told how to
    read `documented`, `inferred`, `candidate` and `flagged`; the data also used
    `certain` and `probable`, which mean nothing to anybody outside the row.
    The vocabulary is READ OUT OF THE PAGE rather than restated here, so the two
    cannot drift apart again.
  * a slug that does not exist, or a row that names a slug while still telling
    the reader the person is not in the tree.
  * a row claiming absence when the export answers to the name -- the exact
    error that put six people on the wrong page.
  * an empty `who`, `recordSays` or `source`. A correction with no source is an
    assertion, which is what this archive exists not to publish.

data/documented-joins.tsv merges two records into one person, which is the most
destructive edit here, so its ids and its `basis` are checked too.

Exit 1 on a failure, 0 on a clean run.
"""
import csv, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(HERE, ".."))

people = json.load(open("site/src/data/people.json", encoding="utf-8"))
by_slug = {p["slug"]: p for p in people}
fails, notes = [], []
BLANK = {"", "—", "-", "?"}

def key(s):
    s = (s or "").strip().lower()
    for a, b in (("à","a"),("á","a"),("è","e"),("é","e"),("ì","i"),("í","i"),
                 ("ò","o"),("ó","o"),("ù","u"),("ú","u")):
        s = s.replace(a, b)
    return " ".join(re.sub(r"[^a-z ]", " ", s).split())

by_name = {}
for p in people:
    by_name.setdefault(key(p["name"]), []).append(p)

# --- the vocabulary is whatever the page explains, not a list kept here ------
PAGE = "site/src/pages/corrections.astro"
LEGEND = set()
if os.path.exists(PAGE):
    src = open(PAGE, encoding="utf-8").read()
    m = re.search(r"How to read the confidence(.*?)</section>", src, re.S)
    if m:
        LEGEND = {t.strip() for t in re.findall(r'<div class="k">([^<]+)</div>', m.group(1))}
if not LEGEND:
    fails.append("corrections: the page no longer explains any confidence levels — "
                 "the legend is what this check reads, so it cannot be removed")

# --- data/corrections.tsv ---------------------------------------------------
seen = {}
for i, r in enumerate(csv.DictReader(open("data/corrections.tsv", encoding="utf-8"),
                                     delimiter="\t"), start=2):
    who = (r.get("who") or "").strip()
    where = f"corrections line {i}" + (f" ({who})" if who else "")
    for f in ("who", "recordSays", "source"):
        if (r.get(f) or "").strip() in BLANK:
            fails.append(f"{where}: no {f}"
                         + ("  — a correction without a source is an assertion" if f == "source" else ""))
    conf = (r.get("confidence") or "").strip()
    if LEGEND and conf not in LEGEND:
        fails.append(f"{where}: confidence «{conf}» is not explained on the page, which offers "
                     + ", ".join(sorted(LEGEND)))
    slug = (r.get("slug") or "").strip()
    tree = (r.get("treeSays") or "")
    if slug not in BLANK:
        if slug not in by_slug:
            fails.append(f"{where}: slug «{slug}» is not in the export")
        elif re.search(r"\bnot in the tree\b", tree, re.I):
            fails.append(f"{where}: names slug {slug} and still tells the reader "
                         f"they are «{tree.strip()}»")
    elif re.search(r"\bnot in the tree\b", tree, re.I):
        hits = by_name.get(key(who), [])
        spine = [p for p in hits if p.get("ancGen") is not None]
        pick = hits if len(hits) == 1 else spine
        if len(pick) == 1:
            fails.append(f"{where}: claims «not in the tree», yet {pick[0]['slug']} in the export "
                         f"answers to the name — set the slug, or say why they are two people")
    k = (slug or key(who), (r.get("kind") or "").strip())
    if k in seen and k[0] not in BLANK:
        notes.append(f"{where}: a second «{k[1]}» for the same person as line {seen[k]} — "
                     f"check one has not superseded the other")
    seen[k] = i

# --- data/documented-joins.tsv ---------------------------------------------
JOIN_BASIS = {"documented", "export"}
for i, r in enumerate(csv.DictReader(open("data/documented-joins.tsv", encoding="utf-8"),
                                     delimiter="\t"), start=2):
    keep, drop = (r.get("keep") or "").strip(), (r.get("drop") or "").strip()
    where = f"documented-joins line {i} ({(r.get('who') or '').strip()})"
    for v, n in ((keep, "keep"), (drop, "drop")):
        if not re.fullmatch(r"@I\d+@", v):
            fails.append(f"{where}: {n} «{v}» is not an export id like @I23@")
    if keep and keep == drop:
        fails.append(f"{where}: keep and drop are the same record")
    if (r.get("basis") or "").strip() not in JOIN_BASIS:
        fails.append(f"{where}: basis «{r.get('basis')}» is not one of " + ", ".join(sorted(JOIN_BASIS)))
    if (r.get("evidence") or "").strip() in BLANK:
        fails.append(f"{where}: no evidence — a merge is the most destructive edit here")

for n in notes:
    print("  note  ", n)
for f in fails:
    print("  FAIL  ", f)
print(f"  {'ok   ' if not fails else 'FAIL '} corrections — {len(fails)} problem"
      f"{'' if len(fails)==1 else 's'}, {len(notes)} note{'' if len(notes)==1 else 's'}")
sys.exit(1 if fails else 0)
