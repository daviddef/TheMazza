#!/usr/bin/env python3
"""Catch a claim attached to the wrong person.

Four times in two days a documented finding was nearly written onto a record
that merely shared a name: domenico-prostamo (a man dead in 1818, not the
spine's), mariano-mazza (a twentieth-century son of the Orazio born 1883),
anna-cavallaro (daughter of a Luciano born in 1945), and angela-mazza (a
living granddaughter). Three were caught by hand. One shipped for a day.

So this checks the joins by arithmetic instead of by attention:

  * every slug and id a data file points at must exist;
  * a parent must be older than the child, where both have years;
  * a parent link must not double back on itself;
  * a Queensland registration must not name a person whose own death year
    is somewhere else;
  * and a person the evidence NAMES must not have a page that denies it.

THE LAST ONE WAS ADDED AFTER THE ESTATE CAUGHT IT. `documented-additions.tsv`
points at a person with `inTree` and `corrections.tsv` with `slug`, but
`build_person_extras.py` read neither, so twelve people carried evidence that
never reached them — and their pages said, in as many words, "No record has been
read for this person. What is known of them is what the tree asserts, and it is
unverified." ANTONINO PROSTAMO, documented four times over and dead at two in the
morning on the last night of 1837, was one of them. A silent build is how that
lasted.

Exit 1 on a failure, 0 on a clean run, so the build can refuse to publish.
"""
import csv, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(HERE, ".."))

people = json.load(open("site/src/data/people.json", encoding="utf-8"))
by_slug = {p["slug"]: p for p in people}
by_id = {p["id"]: p for p in people}
fails, notes = [], []

def year(p, key):
    v = p.get(key)
    return v if isinstance(v, int) else None

def est_born(p, depth=0):
    """A birth year to reason with. Many of these records carry no year at all —
    which is exactly how three wrong joins slipped through — so fall back to a
    generation below the earliest child, and a generation above the parents."""
    y = year(p, "born")
    if y:
        return y
    if depth > 2:
        return None
    kids = [by_slug[c["slug"]] for c in p.get("children", []) if c["slug"] in by_slug]
    ys = [est_born(k, depth + 1) for k in kids]
    ys = [v for v in ys if v]
    if ys:
        return min(ys) - 25
    pars = [by_slug[c["slug"]] for c in p.get("parents", []) if c["slug"] in by_slug]
    ys = [est_born(k, depth + 1) for k in pars]
    ys = [v for v in ys if v]
    if ys:
        return max(ys) + 25
    return None

def ancestors(slug, seen=None):
    seen = seen or set()
    for a in by_slug.get(slug, {}).get("parents", []):
        if a["slug"] in seen:
            continue
        seen.add(a["slug"])
        ancestors(a["slug"], seen)
    return seen

# --- data/parent-links.tsv -------------------------------------------------
if os.path.exists("data/parent-links.tsv"):
    for r in csv.DictReader(open("data/parent-links.tsv", encoding="utf-8"), delimiter="\t"):
        c, pa, via = r["child"].strip(), r["parent"].strip(), r["via"].strip()
        if c not in by_slug:
            fails.append(f"parent-links: no such child slug — {c}")
            continue
        if pa not in by_slug:
            # a documented parent who is simply not in the export is normal;
            # say so once rather than failing, because the row does nothing.
            notes.append(f"parent-links: parent not in the export, row is inert — {c} <- {pa}")
            continue
        if c == pa:
            fails.append(f"parent-links: a person cannot be their own parent — {c}")
        if via == "drop":
            continue
        cb, pb = est_born(by_slug[c]), est_born(by_slug[pa])
        if cb and pb and pb >= cb:
            fails.append(f"parent-links: parent born about {pb} is not older than child born about {cb} — {c} <- {pa}")
        pd = year(by_slug[pa], "died")
        if cb and pd and pd < cb - 1:
            fails.append(f"parent-links: parent died {pd} before child born about {cb} — {c} <- {pa}")
        # and the whole line above the parent must be older than the child too
        for a in ancestors(pa):
            ab = year(by_slug[a], "born")
            if cb and ab and ab >= cb:
                fails.append(f"parent-links: {a}, an ancestor of the proposed parent, was born {ab} — "
                             f"after the child {c} born about {cb}")
        if c in ancestors(pa):
            fails.append(f"parent-links: {pa} already descends from {c} — this would close a loop")

# --- data/qld-bdm.tsv ------------------------------------------------------
if os.path.exists("data/qld-bdm.tsv"):
    for r in csv.DictReader(open("data/qld-bdm.tsv", encoding="utf-8"), delimiter="\t"):
        who = (r.get("who") or "").strip()
        if not who or who in ("—", ""):
            continue
        if who not in by_slug:
            fails.append(f"qld-bdm: no such slug — {who}")
            continue
        if r.get("type") == "death":
            reg = "".join(ch for ch in (r.get("date") or "") if ch.isdigit())[-4:]
            dd = year(by_slug[who], "died")
            if reg.isdigit() and dd and abs(int(reg) - dd) > 1:
                fails.append(f"qld-bdm: registration of {reg} against a person who died {dd} — {who}")
            if reg.isdigit() and not dd:
                fails.append(f"qld-bdm: a DEATH registration of {reg} hung on {who}, who has no recorded "
                             f"death at all — check it is the same person and not a namesake")

# --- data/documented-joins.tsv --------------------------------------------
if os.path.exists("data/documented-joins.tsv"):
    for r in csv.DictReader(open("data/documented-joins.tsv", encoding="utf-8"), delimiter="\t"):
        k, dr = r["keep"].strip(), r["drop"].strip()
        if k not in by_id and dr not in by_id:
            fails.append(f"documented-joins: neither {k} nor {dr} survives — the row does nothing")
        elif k not in by_id:
            notes.append(f"documented-joins: the build kept {dr} rather than the declared {k} — "
                         f"richness decides, and the row's wording should not claim otherwise")

# Every person the evidence names must carry it. This is a check on the BUILD,
# not on the data: the rows are fine, it is build_person_extras.py that has to
# pick them up, and when it stops doing so the page actively denies the record.
BLANK = {"", "\u2014", "-", "\u2013"}
named = {}
for row in csv.DictReader(open("data/documented-additions.tsv", encoding="utf-8"),
                          delimiter="\t"):
    slug = (row.get("inTree") or "").strip()
    if slug not in BLANK:
        named.setdefault(slug, set()).add("documented-additions")
for row in csv.DictReader(open("data/corrections.tsv", encoding="utf-8"),
                          delimiter="\t"):
    slug = (row.get("slug") or "").strip()
    if slug not in BLANK:
        named.setdefault(slug, set()).add("corrections")

for slug, files in sorted(named.items()):
    person = by_slug.get(slug)
    if person is None:
        continue                      # the slug checks above already caught it
    if not person.get("records") and not person.get("corrections"):
        fails.append(
            f"{slug} is named in {' and '.join(sorted(files))} and their page carries "
            f"neither a record nor a correction — it will tell the reader nothing has "
            f"been read about them. build_person_extras.py is not picking the row up")

for n in notes:
    print("  note ", n)
# THE FOUR-STAGE GUARD. people.json is written by build.py and then COMPLETED
# by build_spine.py, build_more.py and build_person_extras.py. Running stage
# one alone rewrites the file and silently drops these four keys from every
# row; it happened on 22 September 2026 and sixty-eight people lost their
# `records`, a burial register entry among them. Nothing caught it, because a
# stripped file is still internally consistent — every other check passed.
#
# A file that has been through all four stages carries all four keys. A file
# that has not, does not. That is the whole test, and it belongs in a gate
# rather than in a comment nobody reads at the moment they need it.
STAGES = {"records": "build_spine.py", "corrections": "build_spine.py",
          "onSpine": "build_more.py", "ancGen": "build_person_extras.py"}
for key, stage in STAGES.items():
    missing = sum(1 for r in people if key not in r)
    if missing:
        fails.append(f"people.json is missing «{key}» on {missing} of {len(people)} rows — "
                     f"build.py was run without {stage}. Run the full four-stage chain: "
                     f"build.py, build_spine.py, build_more.py, build_person_extras.py")

for f in fails:
    print("  FAIL ", f)
print(f"  {'ok   ' if not fails else 'FAIL '} {len(people)} people — "
      f"{len(fails)} broken link{'' if len(fails)==1 else 's'}, {len(notes)} inert row{'' if len(notes)==1 else 's'}")
sys.exit(1 if fails else 0)
