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
import csv, hashlib, json, os, struct, sys

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
    # A byte-identical twin that IS drawn is not a loss, and needs no prose to
    # say so. build.py deduplicates a person's photographs by content after
    # canonicalising the xref, so when the export attached one image to a person
    # AND to a duplicate of that person, one of the two filenames stops being
    # drawn. Nothing is missing: the same bytes reach the reader under the other
    # name. Requiring a hand-written reason for that would be asking someone to
    # annotate an automatic, correct and entirely explainable absence.
    _by_hash = {}
    for _m in json.load(open("data/photo-manifest.json", encoding="utf-8")):
        if os.path.exists(_m.get("path", "")):
            _by_hash.setdefault(
                hashlib.sha256(open(_m["path"], "rb").read()).hexdigest(), []).append(_m["file"])
    def _twin_is_drawn(f):
        for _h, _files in _by_hash.items():
            if f in _files:
                return any(g != f and g in built for g in _files)
        return False
    lost = sorted(f for f in PORTRAITS
                  if f not in built and f not in declared_absent and not _twin_is_drawn(f))
    twins = sorted(f for f in PORTRAITS
                   if f not in built and f not in declared_absent and _twin_is_drawn(f))
    if twins:
        notes.append(f"  note  {len(twins)} portrait(s) are not drawn because the identical image "
                     f"is already drawn for the same person under another name: {', '.join(twins)}")
    held = sorted(f for f in PORTRAITS if f not in built and f in declared_absent)
    if held:
        notes.append(f"  note  {len(held)} portrait(s) held and deliberately not shown, each with "
                     f"its reason in the manifest: {', '.join(held)}")
    if lost:
        problems.append(f"  FAIL  {len(lost)} portrait(s) are in data/photo-manifest.json, reach no "
                        f"built page, and say nothing about why. Either they should be drawn, or "
                        f"the row should carry «notShown» with the reason: {', '.join(lost[:4])}"
                        f"{' …' if len(lost) > 4 else ''}")

# THE REGISTER PLATES, HASHED AND MEASURED.
#
# The portraits turned out to hold one stock graphic filed 22 times and four
# photographs held twice, none of which any gate could see, because nothing
# had ever looked at the BYTES. The plates are evidence rather than
# decoration — a plate standing for the wrong act is a false citation with a
# picture attached — so they get the same treatment, permanently.
#
# All 53 were checked by hand on 9 October 2026 and were sound: no duplicate,
# no blank, no truncation, widths from 1006 to 2960. Two scored 0.94 on a
# whole-image correlation and turned out to be Scilla marriage acts 73/74 and
# 85/86 — different openings of the same pre-printed form, which is why a
# correlation test is NOT run here. On a printed register form the ink that
# differs between two acts is a few percent of the page, so «looks alike» is
# the normal case and only an exact match means anything.
def _jpeg_dims(b):
    i = 2
    while i < len(b) - 9:
        if b[i] != 0xFF:
            i += 1
            continue
        mk = b[i + 1]
        if mk in (0xC0, 0xC1, 0xC2, 0xC3):
            return struct.unpack(">HH", b[i + 5:i + 9])[::-1]
        if mk in (0xD8, 0xD9) or 0xD0 <= mk <= 0xD7:
            i += 2
            continue
        try:
            i += 2 + struct.unpack(">H", b[i + 2:i + 4])[0]
        except Exception:
            return None
    return None

_plate_hash, _broken, _widths = {}, [], []
for _f in sorted(on_disk - PORTRAITS):
    _b = open(os.path.join(PLATES, _f), "rb").read()
    _d = _jpeg_dims(_b)
    if _b[:2] != b"\xff\xd8" or _b[-2:] != b"\xff\xd9" or not _d:
        _broken.append(_f)
    else:
        _widths.append(_d[0])
    _plate_hash.setdefault(hashlib.sha256(_b).hexdigest(), []).append(_f)
if _broken:
    problems.append(f"  FAIL  {len(_broken)} register plate(s) are truncated or cannot be measured, "
                    f"which is what a half-finished download looks like: {', '.join(_broken[:4])}")
for _h, _fs in sorted(_plate_hash.items()):
    if len(_fs) > 1:
        problems.append(f"  FAIL  one image is standing for {len(_fs)} different plates — identical "
                        f"bytes under {len(_fs)} names, so at least one act is illustrated by "
                        f"another act's page: {', '.join(_fs)}")
if _widths:
    notes.append(f"  note  {len(_widths)} register plate(s) hashed and measured, "
                 f"{min(_widths)}px to {max(_widths)}px wide, no duplicate and none truncated")

# THE STOCK GRAPHIC MUST NEVER BE DRAWN AS SOMEBODY'S PHOTOGRAPH.
#
# One MyHeritage collection graphic — a greyscale montage of a generic
# passenger manifest, watermarked — arrived 22 times under 22 rins for 11
# people, and nine of them had no other image, so their entire «Photographs»
# section was stock art captioned with their name and dates. It is identified
# by content, not by filename, because it came in under 22 different names and
# would come in under a 23rd.
_STOCK = "9459994d854efa27e137bf92d3a13cd1546d57f210ea5aded69c7b5b1166c7f1"
_stock_undeclared = []
for _m in json.load(open("data/photo-manifest.json", encoding="utf-8")):
    if not os.path.exists(_m.get("path", "")):
        continue
    if hashlib.sha256(open(_m["path"], "rb").read()).hexdigest() == _STOCK \
            and not _m.get("notShown"):
        _stock_undeclared.append(_m["file"])
if _stock_undeclared:
    problems.append(f"  FAIL  {len(_stock_undeclared)} row(s) hold the MyHeritage stock collection "
                    f"graphic and do not say so, so it will be drawn as a photograph of a named "
                    f"person: {', '.join(_stock_undeclared[:4])}"
                    f"{' …' if len(_stock_undeclared) > 4 else ''}")

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
