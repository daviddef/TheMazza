#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The prose gate for living people: run the kit's checkprose.py over what this archive's authors type.

    python3 ../tools/check_prose.py                  # from site/ (what `npm run check:prose` and the build run)
    python3 ../tools/check_prose.py --require-tree   # a run without the export is a FAILURE, even in CI

checkprose.py (kit/tools) fails when a hand-written page, a hand-edited data file or a note puts a year, a date or
a life-event word beside a living person's name, or when a JSON record naming a living person carries a field
beyond the standard (name, relationships, full town and country). check_living_v2.py guards the BUILT pages and
the generated data; this guards what somebody typed.

THE FEED. Who is living is the archive's question, answered by tools/build_checkprose_feed.py with the kit's
living_rule.py over the private MyHeritage export. The feed holds names, so it lives in private/ (gitignored) or at
$CHECKPROSE_FEED, and is rebuilt on every run so it is never stale.

EXIT CODES. 0 passed. 1 failed. 2 NOT RUN: the export is not on this machine, so nobody can say who is living, and
"cannot say" is not "nobody is". On David's machine that stops the build. In CI (the environment variable CI is set:
GitHub Actions sets it; the export is private and is not in the repository) the build goes on and the log says, in
capitals, that this gate did not run and that this is not a pass; --require-tree turns that into a failure there
too, as it must for any run that is meant to count.

WHICH FILES (see HAND_EDITED and GENERATED below). The kit reads, by default, site/src/pages, site/src/content,
notes/, docs/ and the top-level markdown; this adds the hand-EDITED data files and the components, layouts and
helpers (a sentence can be typed there). A data file that is in neither list FAILS the gate, so that a new file has
to be classified by someone who knows whether a person edits it or a script writes it.

Allowances live in checkprose-allow.json: each needs a reason, and an entry that matches nothing fails.
"""
import os
import sys
import json
import argparse
import subprocess
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SITE = os.path.join(ROOT, "site")
KIT_TOOLS = os.path.join(SITE, "node_modules", "@daviddef", "archive-kit", "kit", "tools")
CHECKPROSE = os.path.join(KIT_TOOLS, "checkprose.py")
ALLOW = os.path.join(ROOT, "checkprose-allow.json")

# Where an author types data. Every *.tsv under data/ is typed (or appended to by a research session) and is
# read: a new TSV is scanned without anybody having to remember to list it. JSON is listed by name.
TYPED_DIRS = ("data", "site/src/data")

# JSON a person edits. Each is read by the gate.
HAND_EDITED = {
    "data/gazetteer-local.json",     # coordinates set by hand, each with its reason
    "data/pe-volumes.json",          # register volumes and their arks, filled in by hand as they are found
    "site/src/data/book.json",       # the book's order: part titles, intros and one-line blurbs, written by hand
    "site/src/data/errands.json",    # the letters and orders this archive still needs: written by hand
    "site/src/data/place-spellings.json",   # misspellings of place names, each with a note
    "site/src/data/the-110.json",    # the join of the hundred and ten: a page's text, written by hand
    "site/src/data/trees.json",      # the /trees page: one row per line, each in the words its author chose
    "site/src/data/worklist.json",   # the work list: a research session appends to it
}

# JSON a script writes. Its generator's own scrub gate (check_living_v2.py for people.json and every living row,
# the build's checks for the rest) is the guard; the hand-typed source of each is a TSV in data/ and is read
# above. A fix made here would be undone by the next run of the generator.
GENERATED = {
    "data/ahnentafel.json",          # tools/build_line.py
    "data/audit.json",               # tools/build.py
    "data/held-out.json",            # tools/build.py: ids only
    "data/nudgee-matched.json",      # tools/match_nudgee.py
    "data/nudgee-search.json",       # tools/nudgee.py
    "data/photo-manifest.json",      # tools/fetch_photos.py, tools/build.py
    "data/scilla-targets.json",      # tools/scilla_targets.py
    "data/pe-nati-1879-ids.txt",     # a list of image ids fetched from Antenati
}
GENERATED_PREFIXES = (
    "data/manifests/",               # IIIF manifests fetched from Antenati: container, image ids, page labels
)
GENERATED_SITE = {
    "additions", "ancestors", "arneytown", "audit-negatives", "australia-graves", "briatico-line", "burials",
    "census", "components", "corrections", "coverage", "crossings", "disputed", "documented-line",
    "documented-parents", "ellis", "families", "findmypast", "focus", "holdings", "households", "instruments",
    "living", "mazza-births", "name-evidence", "namefold", "nicotra", "nudgee", "ny-children", "people",
    "person-slugs", "places", "qld-bdm", "quarters", "questions", "read-names", "reads", "records", "scilla-matr-1913", "scilla-reads",
    "searched", "ships", "sicilian-acts", "sicily-reads", "sicily-spine", "sources", "spine", "stats", "trove",
    "unresolved", "walls",
}

# Prose that is typed outside src/pages and notes/*.md: components, layouts and helpers (a sentence can be typed
# there), and the plain-text and markdown notes the archive keeps beside them.
EXTRA_INCLUDE = ["site/src/components/**/*.astro", "site/src/layouts/**/*.astro", "site/src/lib/**/*.js",
                 "notes/**/*.txt", "data/*.tsv"]


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def tracked(prefix, root=ROOT):
    r = subprocess.run(["git", "-C", root, "ls-files", "-z", prefix], capture_output=True, text=True)
    return sorted(f for f in r.stdout.split("\0") if f)


def classify(root=ROOT):
    """Return (hand-edited data files to include, problems)."""
    problems, include = [], []
    seen = set()
    for d in TYPED_DIRS:
        for f in tracked(d + "/", root):
            seen.add(f)
            if f.endswith(".tsv") and f.startswith("data/") and f.count("/") == 1:
                continue                                # covered by the data/*.tsv pattern
            if f in HAND_EDITED:
                include.append(f)
            elif f in GENERATED or f.startswith(GENERATED_PREFIXES):
                continue
            elif f.startswith("site/src/data/") and f.endswith(".json") and f.count("/") == 3 \
                    and os.path.basename(f)[:-5] in GENERATED_SITE:
                continue
            else:
                problems.append("%s is in neither HAND_EDITED nor GENERATED in tools/check_prose.py: say whether "
                                "a person edits it or a script writes it" % f)
    for f in sorted(HAND_EDITED | GENERATED):
        if f not in seen:
            problems.append("tools/check_prose.py lists %s, which is not a tracked file" % f)
    for n in sorted(GENERATED_SITE):
        if "site/src/data/%s.json" % n not in seen:
            problems.append("tools/check_prose.py lists site/src/data/%s.json, which is not a tracked file" % n)
    for f in sorted(HAND_EDITED & GENERATED):
        problems.append("%s is listed as both hand-edited and generated" % f)
    return sorted(include), problems


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--require-tree", action="store_true",
                    help="a run without the export (nobody can say who is living) fails even in CI")
    ap.add_argument("--feed", help="where to write the feed (default: $CHECKPROSE_FEED or private/checkprose-feed.json)")
    ap.add_argument("--gedcom")
    ap.add_argument("--root", default=ROOT, help=argparse.SUPPRESS)
    ap.add_argument("--allow", default=ALLOW, help=argparse.SUPPRESS)
    a = ap.parse_args(argv)

    if not os.path.exists(CHECKPROSE):
        print("checkprose: FAIL, the kit has no checkprose.py at %s (pin the kit at 26a4cba or later)" % CHECKPROSE)
        return 1
    include, problems = classify(a.root)
    if problems:
        print("checkprose: FAIL (%d)" % len(problems))
        for p in problems:
            print("  - " + p)
        return 1

    fb = load_module(os.path.join(HERE, "build_checkprose_feed.py"), "build_checkprose_feed")
    feed, stats = fb.build(a.gedcom)
    if feed is None:
        in_ci = bool(os.environ.get("CI")) and not a.require_tree
        print("checkprose: NOT RUN (%s). The prose gate could not say who is living, so it checked nothing; "
              "this is NOT a pass." % stats)
        if in_ci:
            print("checkprose: NOT RUN in CI, as check_living_v2 does not run its export checks there; it runs "
                  "wherever the private export is (David's machine). The build goes on, and this is not a pass.")
            return 0
        return 2

    if not feed["living"] or not feed["deadNames"]:
        print("checkprose: FAIL, the feed has %d living people and %d dead names; refusing to pass on nothing" % (
            len(feed["living"]), len(feed["deadNames"])))
        return 1
    out = fb.feed_path(a.feed)
    fb.write_feed(feed, out)
    print("checkprose: feed has %d living people (%d names) and %d dead names; %d living phrases, %d skipped as "
          "shared with a dead person" % (
              len(feed["living"]), sum(len(x["names"]) for x in feed["living"]), len(feed["deadNames"]),
              stats.get("living phrases", 0), stats.get("living phrases shared with a dead person (skipped by the gate)", 0)))
    cmd = [sys.executable, CHECKPROSE, "--root", a.root, "--feed", out]
    for inc in include + EXTRA_INCLUDE:
        cmd += ["--include", inc]
    if os.path.exists(a.allow):
        cmd += ["--allow", a.allow]
    return subprocess.run(cmd).returncode


if __name__ == "__main__":
    sys.exit(main())
