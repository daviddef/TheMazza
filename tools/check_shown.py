#!/usr/bin/env python3
"""Data a page holds and does not show.

WHY THIS EXISTS. Three times in a fortnight this archive researched something,
wrote it correctly into a TSV, built it correctly into JSON, and then did not
put it on the page a reader would look for it on:

  * data/trove-gazette.tsv had no builder and no page at all; seven
    naturalisation entries lived inside two prose paragraphs.
  * /nicotra/ carried a hand-typed «Eight Nicotra households» against thirteen.
  * MASCALI'S OWN DEATH SWEEP — 21 rows, 9 read, 7 Nicotra deaths — was
    reachable from /nicotra/ and /worklist/ and NOT from /mascali/, because the
    page asked byComuneSeries["Mascali"]["Matrimoni"] and never asked for Morti.

EVERY GATE IN THIS BUILD CHECKS THAT THE DATA IS CONSISTENT. None of them asked
whether a page is showing what it has. That is a different question and it is
the one that kept going wrong — each time it surfaced because David asked, not
because the build complained.

THE TEST. For every comune that has sweep rows, and every series within it, at
least one of those rows' own notes must appear in that comune's built page. A
note is this archive's own prose about that year, so it is distinctive: if none
of a series' notes is on the page, the page is not rendering the series.

It deliberately does NOT require every row — a page may legitimately summarise,
and the Riposto page shows births and marriages in two separate tables with
different framing. One row proving the series reached the reader is the bar.

  ARCHIVE_OUT=dist-verify python3 tools/check_shown.py
"""
import html, json, os, re, sys

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DIST = os.path.join("site", os.environ.get("ARCHIVE_OUT", "dist"))

# comune -> the page that owns it. A comune with no page of its own is not a
# fault: say so and move on, rather than inventing a requirement.
PAGE = {"Mascali": "mascali", "Giarre": "giarre", "Riposto": "riposto",
        "Piedimonte Etneo": "piedimonte-etneo"}


def text_of(path):
    s = open(path, encoding="utf-8", errors="ignore").read()
    s = re.sub(r"(?s)<script.*?</script>", " ", s)
    s = re.sub(r"(?s)<style.*?</style>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s)))


def norm(s):
    return re.sub(r"\s+", " ", html.unescape(s or "")).strip()


nic = json.load(open("site/src/data/nicotra.json", encoding="utf-8"))
problems, notes = [], []

if not os.path.isdir(DIST):
    print(f"  --    shown      not run: no build at {DIST}")
    sys.exit(0)

pages, checked = {}, 0
for comune, series in sorted(nic["byComuneSeries"].items()):
    slug = PAGE.get(comune)
    if not slug:
        notes.append(f"  note  {comune} has sweep data and no page of its own — not a fault, "
                     f"but nothing here can check it reaches a reader")
        continue
    page = os.path.join(DIST, slug, "index.html")
    if not os.path.exists(page):
        problems.append(f"  FAIL  {comune} has sweep data and /{slug}/ is not built")
        continue
    if slug not in pages:
        pages[slug] = text_of(page)
    body = pages[slug]
    for name, rows in sorted(series.items()):
        checked += 1
        # the row notes are this archive's own words about that year; a page
        # rendering the series will carry at least one of them verbatim.
        hits = sum(1 for r in rows if norm(r.get("note"))[:60]
                   and norm(r.get("note"))[:60] in body)
        if not hits:
            read = sum(1 for r in rows if r.get("entries") != "—")
            problems.append(
                f"  FAIL  /{slug}/ does not show its {name} sweep — {len(rows)} row(s), "
                f"{read} read, and not one of their notes is on the page. The data is in "
                f"nicotra.json under byComuneSeries[{comune!r}][{name!r}]")

# A household found at a comune should reach that comune's page or the line page.
# ---------------------------------------------------------------------------
# PROSE KEYED TO A NUMBER THAT MOVES.
#
# The sweep check above asks whether a page shows its own rows. This section
# asks a narrower question that cost three live faults on /components/ alone:
# when a page carries a paragraph ABOUT one particular piece of the graph,
# does that paragraph still reach a reader?
#
# Component numbers are assigned by a graph walk and they move between builds.
# A rebuild on 8 October 2026 shuffled comp 3 to 10 and 9 to 4 with nobody's
# parentage changing. Two notes on /components/ were keyed `comp === 3` and
# `comp === 5`; both silently stopped rendering, and one of them described a
# fragment that had since been joined into the main tree. A third read
# `comps[1]` and captioned the New York Mazzitelli as a Piedimonte Etneo
# kindred — directly above the page's own heading saying New York.
#
# These are canaries, not a theory: one distinctive phrase per paragraph that
# must survive on the built page. A canary cannot prove a page is right. It
# proves a paragraph still renders, which is the failure that actually keeps
# happening. ADD ONE whenever you write prose about a specific component,
# household, or series — if the phrase is worth writing, it is worth proving a
# reader can see it.
CANARIES = [
    ("components", "Mazzitelli of New York",
     "the note on the unjoined New York piece, once keyed comp === 3"),
    ("components", "born at Buenos Aires",
     "the Argentine branch, once keyed comp === 5 as a separate fragment"),
    ("components", "argued onto the line",
     "the lede's correction of the Piedimonte caption that read comps[1]"),
    ("piedimonte-etneo", "component numbers move",
     "the page that documents this exact bug class"),
]

for slug, phrase, why in CANARIES:
    page = os.path.join(DIST, slug, "index.html")
    if not os.path.exists(page):
        problems.append(f"  FAIL  canary for /{slug}/ cannot run — the page is not built")
        continue
    if slug not in pages:
        pages[slug] = text_of(page)
    if phrase not in pages[slug]:
        problems.append(f"  FAIL  /{slug}/ no longer says «{phrase}» — {why}. Prose that selects "
                        f"a component by number or position stops rendering when the graph walk "
                        f"renumbers; select it by who is in it")

# THE PEDIGREE MUST COUNT WHAT THE ARCHIVE HAS READ, NOT ONLY WHAT THE FILE SAYS.
#
# /ancestors/ counted ancestors.json — the GEDCOM — and nothing else, so it
# reported 59 people where this archive can name 91, and 15.6% at the sixth
# generation where it can show 34.4%. Sixteen proved parents of people already
# on the chart were missing from it, four of them the Nicotra and Cassaniti
# grandparents read out of Piedimonte Matrimoni 1872 atto 20. /tree/ had drawn
# them for months. The pedigree page simply never imported the file.
#
# The invariant: for every generation, the count the page prints must equal the
# export's count PLUS the documented parents this archive has proved at that
# generation. If someone drops the import again, these numbers disagree and the
# build stops.
anc_page = os.path.join(DIST, "ancestors", "index.html")
if os.path.exists(anc_page):
    body = pages.setdefault("ancestors", text_of(anc_page))
    anc = json.load(open("site/src/data/ancestors.json", encoding="utf-8"))
    dp = json.load(open("site/src/data/documented-parents.json", encoding="utf-8"))
    docgen = {}
    for v in dp["byName"].values():
        g = str(v.get("gen", ""))
        if g.isdigit():
            docgen[int(g)] = docgen.get(int(g), 0) + 1
    shown = {int(g): int(n) for g, n in re.findall(r"Generation (\d+) · (\d+) of \d+", body)}
    if not shown:
        problems.append("  FAIL  /ancestors/ prints no «Generation N · X of Y» label — the check "
                        "below cannot read the pedigree's own counts")
    for r in anc["generations"]:
        g = r["gen"]
        want = r["found"] + docgen.get(g, 0)
        got = shown.get(g)
        if got is None:
            problems.append(f"  FAIL  /ancestors/ draws no generation {g} at all")
        elif got != want:
            problems.append(
                f"  FAIL  /ancestors/ generation {g} counts {got}, and the archive holds {want} — "
                f"{r['found']} in the family's file plus {docgen.get(g, 0)} proved from a register. "
                f"The page is counting ancestors.json alone; it must also count "
                f"documented-parents.json, as /tree/ does")
    if docgen and "from a register" not in body:
        problems.append("  FAIL  /ancestors/ never says «from a register», so it is not "
                        "distinguishing the people it proved from the people the export gave it")

# Every non-singleton piece must appear on /components/ under its own heading.
comps_page = os.path.join(DIST, "components", "index.html")
if os.path.exists(comps_page):
    comps = json.load(open("site/src/data/components.json", encoding="utf-8"))
    want = [c for c in comps if c.get("n", 0) > 1]
    if slug_body := pages.get("components") or text_of(comps_page):
        shown = len(re.findall(r"Component \d+", slug_body))
        if shown < len(want):
            problems.append(f"  FAIL  /components/ draws {shown} component heading(s) and the data "
                            f"has {len(want)} piece(s) of more than one person")
        for c in want:
            if c.get("towns") and c["towns"][0]["name"] not in slug_body:
                problems.append(f"  FAIL  /components/ does not name «{c['towns'][0]['name']}», the "
                                f"principal place of a {c['n']}-person piece")

line = text_of(os.path.join(DIST, "nicotra", "index.html")) \
    if os.path.exists(os.path.join(DIST, "nicotra", "index.html")) else ""
for comune, houses in sorted(nic.get("housesByComune", {}).items()):
    slug = PAGE.get(comune)
    body = pages.get(slug, "")
    for h in houses:
        who = norm(h.get("father"))
        if who.startswith("—") or not who:
            continue
        if who not in body and who not in line:
            problems.append(f"  FAIL  the household «{who}» of {comune} is on no page — "
                            f"neither /{slug}/ nor /nicotra/")

print(f"  {checked} comune/series pair(s) checked against their own pages, "
      f"{len(nic.get('households', []))} household(s)")
for n in notes:
    print(n)
for p in problems:
    print(p)
if problems:
    print(f"  FAIL  shown      {len(problems)} problem(s) — data this archive holds and does not show")
    sys.exit(1)
print("  ok    shown      every comune page renders every series its own data holds")
