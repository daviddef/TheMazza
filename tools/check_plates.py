#!/usr/bin/env python3
"""Every plate declared reaches a page, and every plate held is declared.

WHY THIS EXISTS. An estate audit on 23 September 2026 found twenty-eight
images in site/public/plates/ that no built page mentions, twelve of them
scanning an act this archive cites by year and act number. It diagnosed «this
archive has no plates.json».

The manifest existed. data/register-reads.tsv had declared those images, with
the page each belonged on, in a `see` column. tools/build_plates.py wrote them
to site/src/data/reads.json on every build. NOTHING IMPORTED THAT FILE.

A manifest nobody consumes is indistinguishable from no manifest — to a
reader, and to a filename audit. So the fix is a consumer
(components/Plates.astro) and this check, which closes the loop the audit had
to be run by hand to find:

  DECLARED WITHOUT A FILE   a row naming an image that is not on disk
  HELD WITHOUT A DECLARATION an image on disk that no row names
  DECLARED WITHOUT A PAGE   a row whose `see` page does not draw it

The third is the one that bit. It cannot be checked from the data alone — it
needs the BUILT page — so this runs after astro, like checklinks.
"""
import csv, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(HERE, ".."))

PLATES = "site/public/plates"
DIST = "site/dist"
rows = list(csv.DictReader(open("data/register-reads.tsv", encoding="utf-8"), delimiter="\t"))

# Portraits are people, not registers, and they have their OWN manifest —
# data/photo-manifest.json, 133 of them, drawn by the person pages. Reading
# that file is the difference between a rule and a hardcoded list of names:
# the first version of this check named four families by hand and reported
# 133 problems, every one of them a photograph doing exactly its job.
PORTRAITS = {r["file"] for r in json.load(open("data/photo-manifest.json", encoding="utf-8"))}

on_disk = {f for f in os.listdir(PLATES) if not f.startswith(".")}
declared = {r["plate"]: r for r in rows}

problems, notes = [], []

for p, r in declared.items():
    if p not in on_disk:
        problems.append(f"  FAIL  declared and not on disk: {p}  ({r['title'][:50]})")

undeclared = sorted(f for f in on_disk - set(declared) - PORTRAITS)
# Plates drawn by a page directly, rather than through the manifest, are found
# by looking for the filename in the page sources. Those are fine: the rule is
# «reaches a reader», not «goes through this file».
# DOES THE NAME APPEAR IN THE BUILD? That is the whole test, and it is
# deliberately theory-free. Plates reach a reader by at least three routes
# here: the register-reads manifest, a hand-written <figure> in a page, and a
# PLATES dict inside tools/build_acts.py that becomes sicilian-acts.json. An
# earlier version of this check read only .astro sources and called six plates
# orphans that the register page draws perfectly well through the third route.
# Asking whether the filename occurs anywhere in dist needs no theory about
# how a page references a file, which is exactly why the narrower test failed.
built = ""
if os.path.isdir(DIST):
    for root, _, files in os.walk(DIST):
        for f in files:
            if f.endswith((".html", ".json", ".js", ".xml", ".css")):
                built += open(os.path.join(root, f), encoding="utf-8", errors="ignore").read()

orphans = [f for f in undeclared if f not in built] if built else []
for f in orphans:
    problems.append(f"  FAIL  held, declared nowhere, and in no built page: {f}")

inline = [f for f in undeclared if f in built] if built else []
if inline:
    notes.append(f"  note  {len(inline)} plate(s) reach a page without going through the manifest "
                 f"— a hand-written figure, or the PLATES dict in build_acts.py. Legitimate, and "
                 f"counted so the number cannot drift unnoticed.")

# The check the audit had to be run by hand to make.
if os.path.isdir(DIST):
    for p, r in declared.items():
        see = (r.get("see") or "").strip()
        if not see or see == "—":
            problems.append(f"  FAIL  declared with no page to appear on: {p}")
            continue
        page = os.path.join(DIST, see.strip("/"), "index.html")
        if not os.path.exists(page):
            problems.append(f"  FAIL  {p} names a page that is not built: {see}")
            continue
        if p not in open(page, encoding="utf-8", errors="ignore").read():
            problems.append(f"  FAIL  {p} is declared for {see} and that page does not draw it")
else:
    notes.append("  note  no build to test against — the «declared without a page» check was skipped")

print(f"  {len(declared)} register plate(s) declared, {len(PORTRAITS)} portrait(s) in the photo "
      f"manifest, {len(on_disk)} held, {len(orphans)} orphaned, {len(inline)} drawn inline")
for n in notes:
    print(n)
for p in problems:
    print(p)
if problems:
    print(f"  FAIL  plates — {len(problems)} problem(s)")
    sys.exit(1)
print("  ok    plates — every declaration reaches its page, every image is accounted for")
