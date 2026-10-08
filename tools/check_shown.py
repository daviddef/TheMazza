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
