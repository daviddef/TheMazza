#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the feed the kit's prose gate (kit/tools/checkprose.py) reads: who is living, and who is dead.

    python3 tools/build_checkprose_feed.py                # writes private/checkprose-feed.json
    python3 tools/build_checkprose_feed.py --out PATH     # or $CHECKPROSE_FEED
    python3 tools/build_checkprose_feed.py --counts       # counts only, writes nothing

The feed holds living people's NAMES, so it is never committed: it is written under private/ (gitignored), or
wherever $CHECKPROSE_FEED / --out says, readable by its owner only. This script prints COUNTS only, never a name.

    {"living":    [{"id": "<GEDCOM id>", "names": ["Given Family", ...]}, ...],
     "deadNames": ["Given Family", ...]}

WHO IS LIVING is not decided here. It is the archive's one definition, tools/living_v2.py over the kit's
living_rule.py, applied to the private MyHeritage export (sources/mazza-myheritage.ged: the only place a
person's birth year exists):

  * every person in the export the rule calls living (80 or younger, no death or burial recorded here or in the
    archive's own reading, no public source; an undated parent of a recent child is living too);
  * every possible minor (an undated person with a living parent). They are held out of the archive altogether,
    so a date or a detail beside such a name in a hand-written page is as wrong as for a living one;
  * every row the archive publishes as living (people.json `living`), under whatever spelling it uses, for the
    day the export and the published row disagree.

WHO IS DEAD is decided by IDENTITY, never by "every name that is not a living name" (a living person and an
ancestor who share a name would then cancel each other out of the corpus; the kit skips and counts a name both
have, it does not guess). Dead names come from the archive's own dead rows:

  * every people.json row not flagged living, whose id the rule does not call living or held out, with the
    spellings the export records for that id (the name, the given names with the surname, a married name,
    a bracketed form);
  * every export person the rule calls NOT living and NOT held out, with the same spellings (register people
    have no export record and are in people.json only).

Without the export this script writes nothing and exits 2: "cannot say who is living" is not "nobody is".
"""
import os
import re
import sys
import json
import argparse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import living_v2 as LV                      # the archive's adapter to the kit's living_rule.py
from ged import parse, kid, kids, val       # the parser, not the generator

lr = LV.lr
ROOT = LV.ROOT
DATA = os.path.join(ROOT, "site", "src", "data")
DEFAULT_GED = os.path.join(ROOT, "sources", "mazza-myheritage.ged")
DEFAULT_FEED = os.path.join(ROOT, "private", "checkprose-feed.json")
YEAR = re.compile(r"\b(1[5-9]\d\d|20\d\d)\b")


def feed_path(explicit=None):
    return explicit or os.environ.get("CHECKPROSE_FEED") or DEFAULT_FEED


def gedcom_path(explicit=None):
    p = explicit or os.environ.get("ARCHIVE_GEDCOM") or DEFAULT_GED
    return p if os.path.exists(p) else None


def _clean(n):
    return re.sub(r"\s+", " ", str(n or "").replace("/", " ")).strip()


def record_names(rec):
    """Every recorded spelling of one export person, as plain 'Given Family' strings."""
    out = set()
    for nm in kids(rec, "NAME"):
        out.add(_clean(nm["val"]))
        sub = {}
        for y in nm["kids"]:
            sub.setdefault(y["tag"], []).append(_clean(y["val"]))
        given = (sub.get("GIVN") or [""])[0]
        for s in (sub.get("SURN") or []) + sub.get("_MARNM", []) + sub.get("_AKA", []) \
                + sub.get("_FORMERNAME", []) + sub.get("_RNAME", []):
            if given and s:
                out.add(given + " " + s)
        for nick in sub.get("NICK", []):
            for s in (sub.get("SURN") or []) + sub.get("_MARNM", []):
                if nick and s:
                    out.add(nick + " " + s)
        for alias in sub.get("_AKA", []) + sub.get("_FORMERNAME", []) + sub.get("_RNAME", []):
            if " " in alias:
                out.add(alias)
    return sorted(n for n in out if " " in n)


def classify_export(R, people, year):
    """(living ids, held-out ids, dead ids) for every INDI in the export, by the kit's rule through
    LV.classify, with the same inputs the independent gate (check_living_v2.py) derives."""
    I = {x: v for x, v in R.items() if v["tag"] == "INDI"}
    F = {x: v for x, v in R.items() if v["tag"] == "FAM"}
    slug_of = {p["id"]: p["slug"] for p in people}
    ev = LV.evidence()

    def by_of(x):
        for t in ("BIRT", "CHR", "BAPM"):
            e = kid(I[x], t)
            if e and YEAR.search(val(e, "DATE") or ""):
                return int(YEAR.search(val(e, "DATE")).group(1))
        return None

    def titles(x):
        out = []
        for s in kids(I[x], "SOUR"):
            ref = s["val"]
            if ref in R:
                t = kid(R[ref], "TITL")
                out.append(t["val"] if t else ref)
            elif s["val"]:
                out.append(s["val"])
        return out

    def parents_of(x):
        out = []
        fc = kid(I[x], "FAMC")
        if fc and fc["val"] in F:
            for r in ("HUSB", "WIFE"):
                out += [h["val"] for h in kids(F[fc["val"]], r) if h["val"] in I]
        return out

    info = {}
    for x in I:
        sl = slug_of.get(x)
        info[x] = {"by": by_of(x),
                   "dead": bool(kid(I[x], "DEAT") or kid(I[x], "BURI")) or (sl in ev["dead"]),
                   "cites": titles(x) + ev["cites"].get(sl, []), "parents": parents_of(x)}
    living, held = LV.classify(info, year)
    return living, held, set(I) - living - held, I


def build(gedcom=None, year=None):
    """Return (feed, stats), or (None, reason) when the export is not on this machine."""
    path = gedcom_path(gedcom)
    if not path:
        return None, "the MyHeritage export is not on this machine (sources/mazza-myheritage.ged, or set ARCHIVE_GEDCOM)"
    year = year or lr.this_year()
    with open(os.path.join(DATA, "people.json"), encoding="utf-8") as f:
        people = json.load(f)
    R = parse(path)
    living, held, dead, I = classify_export(R, people, year)
    if len(I) < 300:
        return None, "the export has %d people; refusing to decide who is living from that" % len(I)

    people_by_id = {p["id"]: p for p in people}
    stats = {"export people": len(I), "export living by the rule": len(living),
             "export held out by the rule": len(held), "export not living": len(dead),
             "published rows flagged living": sum(1 for p in people if p.get("living")),
             "published rows flagged living the export does not know": 0}

    names_of = {}                       # id -> set of spellings
    for x in living | held:
        names_of.setdefault(x, set()).update(record_names(I[x]))
    for p in people:
        if p.get("living"):
            if p["id"] not in I:
                stats["published rows flagged living the export does not know"] += 1
            names_of.setdefault(p["id"], set()).add(_clean(p.get("name")))
    live_ids = set(names_of)

    dead_names = set()
    for p in people:
        if p.get("living") or p["id"] in live_ids:
            continue
        dead_names.add(_clean(p.get("name")))
        if p["id"] in I:
            dead_names.update(record_names(I[p["id"]]))
    for x in dead:
        if x in live_ids or (x in people_by_id and people_by_id[x].get("living")):
            continue
        dead_names.update(record_names(I[x]))
    dead_names = sorted(n for n in dead_names if n)
    feed = {"living": [{"id": k, "names": sorted(v)} for k, v in sorted(names_of.items()) if v],
            "deadNames": dead_names}
    stats.update({"living people in the feed": len(feed["living"]),
                  "living names": sum(len(x["names"]) for x in feed["living"]),
                  "dead names": len(dead_names)})
    sys.path.insert(0, LV.KIT_TOOLS)
    try:
        import checkprose as cp
        lp, dp = set(), set()
        for x in feed["living"]:
            lp |= cp.phrases(x["names"])
        for n in dead_names:
            dp |= cp.phrases([n])
        stats["living phrases"] = len(lp)
        stats["living phrases shared with a dead person (skipped by the gate)"] = len(lp & dp)
    except ImportError:
        pass
    return feed, stats


def write_feed(feed, out):
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    fd = os.open(out, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(feed, f, ensure_ascii=False)
    os.chmod(out, 0o600)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Write the living / dead name feed for checkprose.py (counts only are printed).")
    ap.add_argument("--out")
    ap.add_argument("--gedcom")
    ap.add_argument("--counts", action="store_true", help="print counts, write nothing")
    ap.add_argument("--year", type=int, default=lr.this_year())
    a = ap.parse_args(argv)
    feed, stats = build(a.gedcom, a.year)
    if feed is None:
        print("build_checkprose_feed: not run: %s" % stats)
        return 2
    if not feed["living"] or not feed["deadNames"]:
        print("build_checkprose_feed: FAIL, %d living, %d dead names; refusing to write a feed that could pass on nothing" % (
            len(feed["living"]), len(feed["deadNames"])))
        return 1
    for k, v in stats.items():
        print("  %-62s %d" % (k, v))
    if a.counts:
        return 0
    out = feed_path(a.out)
    write_feed(feed, out)
    print("build_checkprose_feed: wrote the feed (names inside; not for commit): %s" % (
        os.path.relpath(out, ROOT) if os.path.abspath(out).startswith(ROOT) else "outside the repo"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
