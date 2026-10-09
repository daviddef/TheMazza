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

# EVERY PORTRAIT IN THE MANIFEST MUST REACH A READER TOO.
#
# The manifest was used here only to EXCLUDE portraits from the orphan check
# above — so a portrait that stopped being drawn was invisible to every gate in
# this build, and /documents/ says in as many words that all of them appear and
# none was lost on the way. That sentence had a typed «133» in it until today,
# beside a counted total, and the completeness half of the claim rested on
# nobody having checked. The page cannot count the manifest itself
# (data/photo-manifest.json is outside Astro's root), so the claim is held here
# where the manifest is already loaded.
if built:
    # A portrait may legitimately not appear — three hang off duplicate xrefs the
    # export merges away. What may NOT happen is that it stops appearing and
    # nobody records why, which is the state this check found the archive in.
    # «notShown» is that record, and it is prose because the reasons differ.
    declared_absent = {r["file"] for r in json.load(
        open("data/photo-manifest.json", encoding="utf-8")) if r.get("notShown")}
    lost = sorted(f for f in PORTRAITS if f not in built and f not in declared_absent)
    held = sorted(f for f in PORTRAITS if f not in built and f in declared_absent)
    if held:
        notes.append(f"  note  {len(held)} portrait(s) held and deliberately not shown, each with "
                     f"its reason in the manifest: {', '.join(held)}")
    if lost:
        problems.append(f"  FAIL  {len(lost)} portrait(s) are in data/photo-manifest.json, reach no "
                        f"built page, and say nothing about why. Either they should be drawn, or "
                        f"the row should carry «notShown» with the reason: {', '.join(lost[:4])}"
                        f"{' …' if len(lost) > 4 else ''}")

# EVERY IMAGE MUST BE MEASURED, AND THE SMALL ONES MUST SAY SO.
#
# The archive held 133 photographs and did not know how big any of them was,
# so the person page stretched each one to fill a 190px grid cell with
# width:100%. Eleven are narrower than that and were being drawn above their
# own resolution — Angela Mazza's lead portrait is 132x161 and was shown
# blurred, which looked like a broken download and was not: it is a complete
# JPEG of a small photograph, and the signed source links expired on 16
# September 2026, so no better copy can be fetched.
#
# A row that cannot be measured is the real worry, because that is what a
# truncated file looks like. So measurement is required, and the undersized
# ones are counted rather than hidden.
_man = json.load(open("data/photo-manifest.json", encoding="utf-8"))
_unmeasured = [m["file"] for m in _man
               if os.path.exists(m.get("path", "")) and not (m.get("w") and m.get("h"))]
if _unmeasured:
    problems.append(f"  FAIL  {len(_unmeasured)} held image(s) carry no w/h in the manifest — a file "
                     f"whose dimensions cannot be read is what a truncated download looks like: "
                     f"{', '.join(_unmeasured[:4])}{' …' if len(_unmeasured) > 4 else ''}")
_tiny = sorted((m["w"], m["file"]) for m in _man if m.get("w") and m["w"] < 190)
if _tiny:
    notes.append(f"  note  {len(_tiny)} image(s) are narrower than the 190px grid cell and are "
                 f"drawn at their own size with «a better scan would help» beside them — "
                 f"smallest {_tiny[0][1]} at {_tiny[0][0]}px")

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
