#!/usr/bin/env python3
"""The ribbons' mini flags live in their own generated files, not in story.json or family-lines.json.

    python3 ../tools/build_ribbon_flags.py            # from site/: copy the ribbon cards into story-flags.json, family-flags.json
    python3 ../tools/build_ribbon_flags.py --check    # each copy's cards (less their flags) are the source's, in order

WHY SEPARATE FILES. The kit's ribbon flags (kit/docs/ribbon-flags.md) are written by kit/tools/ribbonflags.py into each
ribbon card's `flags`. But in kit 1fa6b54 the kit's own contracts do not know that field: checkfamilystory.py
(`npm run check:story`) fails a story card that has it, and checkfamilyribbon.py (`npm run check:familyribbon`) fails a
family card that has it. So story.json stays exactly as its author wrote it, family-lines.json exactly as
tools/build_family_lines.py makes it, and this tool copies their ribbon cards, field for field, into

    src/data/story-flags.json    {ribbon: {cards}}               story.json's ribbon cards
    src/data/family-flags.json   {families: [{id, cards}]}       family-lines.json's cards, family by family

which `npm run ribbonflags` then writes the flags into. src/pages/story.astro and src/components/FamilyLine.astro give
each card its flags from these, only from the copy of ITSELF (same name, person or slug, and places).
`npm run check:ribbonflags` runs --check first, so a source changed after the copy fails the build instead of drawing a
flag for the wrong place. When the kit's contracts take `flags`, this tool and the two files can go.

Written indent 2, as ribbonflags.py writes them, so the two writers agree and a rebuild makes no churn.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), "site", "src", "data")
NOTE = ("Made by tools/build_ribbon_flags.py from %s, then given each card's `flags` by the kit's ribbonflags.py "
        "(npm run ribbonflags); do not edit by hand. %s reads the flags from here.")


def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return json.load(f)


def wanted():
    """{file name: the document it should hold, without flags}."""
    story = load("story.json")
    fl = load("family-lines.json")
    return {
        "story-flags.json": {
            "_note": NOTE % ("story.json's ribbon cards", "src/pages/story.astro"),
            "ribbon": {"cards": [dict(c) for c in ((story.get("ribbon") or {}).get("cards") or [])]}},
        "family-flags.json": {
            "_note": NOTE % ("family-lines.json's cards", "src/components/FamilyLine.astro"),
            "families": [{"id": f.get("id"), "cards": [dict(c) for c in (f.get("cards") or [])]} for f in fl.get("families", [])]},
    }


def unflagged(doc):
    cards = list(((doc.get("ribbon") or {}).get("cards")) or [])
    for f in doc.get("families") or []:
        cards += f.get("cards") or []
    for c in cards:
        c.pop("flags", None)
    return doc


def main(argv):
    want = wanted()
    if "--check" in argv:
        bad = 0
        for name, doc in want.items():
            try:
                have = unflagged(load(name))
            except (OSError, ValueError) as e:
                print("ribbonflagfiles: src/data/%s cannot be read (%s); run npm run ribbonflags" % (name, e))
                bad += 1
                continue
            if have != doc:
                print("ribbonflagfiles: src/data/%s is not a copy of its source's ribbon cards; run npm run ribbonflags" % name)
                bad += 1
        if not bad:
            print("ribbonflagfiles: in step (story-flags.json, family-flags.json)")
        return 1 if bad else 0
    for name, doc in want.items():
        with open(os.path.join(DATA, name), "w", encoding="utf-8") as f:
            f.write(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")
    print("ribbonflagfiles: %d story card(s), %d family card(s) copied" % (
        len(want["story-flags.json"]["ribbon"]["cards"]),
        sum(len(f["cards"]) for f in want["family-flags.json"]["families"])))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
