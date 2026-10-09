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
ppl = json.load(open("site/src/data/people.json", encoding="utf-8"))
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

# THE PEDIGREE MUST COUNT WHAT THE ARCHIVE HAS READ, AND EVERY ONE OF THEM
# MUST BE REACHABLE.
#
# /ancestors/ counted the GEDCOM and nothing else, so it reported 59 people
# where the archive could name 91, and 15.6% at the sixth generation where it
# can show 34.4%. On 9 October 2026 the register-proved people became people:
# people.json carries them, so build_focus.py's walk reaches them and
# ancestors.json counts them by itself.
#
# Which moves the risk. The count is now structural and cannot drift, but a
# register-proved ancestor could stop being MARKED — and then the page would
# quietly assert that the family's file names 91 people, which is the opposite
# falsehood and a worse one. So: every generation's register people must be
# marked on the page, and each of them must have the person page this archive
# now promises them.
anc_page = os.path.join(DIST, "ancestors", "index.html")
if os.path.exists(anc_page):
    body = pages.setdefault("ancestors", text_of(anc_page))
    anc = json.load(open("site/src/data/ancestors.json", encoding="utf-8"))
    reg = [x for r in anc["generations"] for x in r["people"] if x.get("fromRegister")]
    shown = {int(g): int(n) for g, n in re.findall(r"Generation (\d+) · (\d+) of \d+", body)}
    for r in anc["generations"]:
        got = shown.get(r["gen"])
        if got is None:
            problems.append(f"  FAIL  /ancestors/ draws no generation {r['gen']} at all")
        elif got != r["found"]:
            problems.append(f"  FAIL  /ancestors/ generation {r['gen']} prints {got} and "
                            f"ancestors.json holds {r['found']}")
    if reg and body.count("from a register") < 2:
        problems.append(f"  FAIL  /ancestors/ carries {len(reg)} register-proved ancestor(s) and "
                        f"does not mark them. Unmarked, the page asserts that the family's file "
                        f"names all {anc['total']} of these people, which it does not")
    for x in reg:
        page = os.path.join(DIST, "people", x["slug"], "index.html")
        if not os.path.exists(page):
            problems.append(f"  FAIL  «{x['name']}» is counted on the pedigree and has no person "
                            f"page at /people/{x['slug']}/ — the archive is counting someone a "
                            f"reader cannot open")
        elif x["name"] not in text_of(page):
            problems.append(f"  FAIL  /people/{x['slug']}/ does not name «{x['name']}»")

# A FINISHED SWEEP MUST NOT LEAVE A «STILL UNREAD» BEHIND IT.
#
# Three pages said so after the sweeps they described were finished this week:
# /riposto/ «Four Riposto years remain unread» with none unread, /giarre/
# «1835, 1836 and 1837 are still unread» with all three read, and /nicotra/
# «Of Giarre's, only 1840 and 1844 have been read» with all ten read. Each was
# true when typed. Each was falsified by the archive's own progress, which is
# the one direction nobody checks, because finishing a search feels like the
# end of the work rather than the beginning of a stale sentence.
# THE PHRASE MUST BE ABOUT A YEAR. On 9 October 2026 this clause failed the
# build over a note on /mascali/ reading «ACT 4, NICOTRA MARIANO, IS STILL
# UNREAD» — which is TRUE: the sweep reads annual indexes, and an individual
# act inside a read year can perfectly well still be unread. The check was
# written to stop a page claiming YEARS are outstanding when the sweep is
# finished, and it cannot do that by matching two words alone. Rewording
# honest prose to get past a gate is the wrong repair; making the gate say
# what it means is the right one.
UNREAD_WORDS = ("still unread", "remain unread", "remains unread", "are unread")
# WHAT MAKES THE SENTENCE WRONG is that it names or counts YEARS as
# outstanding. The two real faults read «Four Riposto years remain unread» and
# «1835, 1836 and 1837 are still unread» — a count followed by «years», or a
# list of four-figure years. The true sentence that tripped this clause reads
# «ACT 4, NICOTRA MARIANO, IS STILL UNREAD», where the 4 is an act number. So
# the subject is what is tested, not the words alone.
SUBJECT_IS_YEARS = re.compile(
    r"(1[78]\d{2}\D{0,12}$)"                      # ...1837 are / 1837, and
    r"|((?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|"
    r"thirteen|fourteen|fifteen|twenty|thirty)\s+\S{0,14}?\s*years?\b\D{0,12}$)",
    re.I)
for comune, series in sorted(nic["byComuneSeries"].items()):
    slug = PAGE.get(comune)
    if not slug or slug not in pages:
        continue
    left = sum(1 for rows in series.values() for r in rows if r.get("entries") == "\u2014")
    if left:
        continue
    body = pages[slug]
    low = body.lower()
    said = []
    for w in UNREAD_WORDS:
        for m in re.finditer(re.escape(w), low):
            before = low[max(0, m.start() - 60):m.start()]
            if SUBJECT_IS_YEARS.search(before):
                said.append(w)
                break
    if said:
        problems.append(
            f"  FAIL  /{slug}/ says «{said[0]}» and every {comune} year in nicotra-sweeps.tsv is "
            f"read. The sweep it describes is finished; count the unread years instead of naming "
            f"them, or the sentence goes false the day the last one is read")

# A PAGE MAY NOT CLAIM MORE PROVENANCE THAN ITS OWN EDGES CARRY.
#
# /bloodline/ read «620 people joined by what this archive has read» above a
# chart in which 719 of 830 links are marked, correctly, as the family tree
# asserting a relationship with no record behind it. The eyebrow claimed the
# opposite of what the drawing showed. It had not always been false — when the
# archive held no read edges the sentence was wrong the other way, and then
# parent-links.tsv grew 99 «read» edges and the sentence drifted past true
# without anyone noticing.
#
# So the page now counts, and this checks the count it printed against the
# edges in people.json. A typed number goes stale silently; a counted one
# cannot, and this is what makes sure it stays counted.
bl = os.path.join(DIST, "bloodline", "index.html")
if os.path.exists(bl):
    body = pages.setdefault("bloodline", text_of(bl))
    edge = {}
    for r in ppl:
        for e in r.get("parents") or []:
            edge[f"{r['slug']}>{e['slug']}"] = e.get("via") or "tree"
        for e in r.get("children") or []:
            edge.setdefault(f"{e['slug']}>{r['slug']}", e.get("via") or "tree")
    links = len(edge)
    proved = sum(1 for v in edge.values() if v in ("read", "index"))
    if f"{proved} of the {links}" not in body:
        problems.append(
            f"  FAIL  /bloodline/ does not state «{proved} of the {links}» — people.json holds "
            f"{links} parent-and-child links and {proved} of them are proved by a record "
            f"({100 * proved / links:.1f}%). The page must count its own edges rather than "
            f"describe them, or the sentence drifts past true as read edges are added")
    if "joined by what this archive has read" in body:
        problems.append(
            "  FAIL  /bloodline/ still claims its people are «joined by what this archive has "
            f"read». {links - proved} of its {links} links are the family tree asserting a "
            "relationship with no record behind it, which is what their colour says on the chart")

# A register-proved person must say so on their own page, or the page implies
# the export held them. 104 people are in that position; the export has none
# of them, and the person page's component sentence is about the export alone.
regppl = [p for p in ppl if p.get("fromRegister")]
unmarked, nopage = [], []
for pr in regppl:
    page = os.path.join(DIST, "people", pr["slug"], "index.html")
    if not os.path.exists(page):
        nopage.append(pr["slug"])
        continue
    t = text_of(page)
    if "not in the family's file" not in t:
        unmarked.append(pr["slug"])
if nopage:
    problems.append(f"  FAIL  {len(nopage)} register-proved person(s) have no page: "
                    f"{', '.join(nopage[:4])}{' …' if len(nopage) > 4 else ''}")
if unmarked:
    problems.append(f"  FAIL  {len(unmarked)} register-proved person(s) have a page that does not "
                    f"say the family's file never held them: {', '.join(unmarked[:4])}"
                    f"{' …' if len(unmarked) > 4 else ''}")
if regppl and not nopage and not unmarked:
    notes.append(f"  note  {len(regppl)} register-proved people, every one with a page that says "
                 f"the export never held them")

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
