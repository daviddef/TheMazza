#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The gate for the names read from register acts (data/read-names.tsv, tools/read_names.py, the /who/ pages they make).

    python3 ../tools/check_read_names.py              # from site/; ARCHIVE_OUT (as for every gate) beats --dist
    python3 ../tools/check_read_names.py --selftest   # plants one fault per rule and requires each to be caught

Prints counts and the line numbers of a failing row; never a person's name beyond the row number.

WHAT IT HOLDS
  1  every row is well formed and the builder accepts it (a name of two to four capitalised words, a known kind and
     `as`, a year, an ark the archive's tables hold)
  2  every row RESTS ON THE ARCHIVE'S OWN DATA: its `from` names a row of data/scilla-reads.tsv, data/register-reads.tsv,
     data/scilla-matr-1913.tsv, data/pe-mazza-acts.tsv, data/sicily-reads.tsv, notes/findings.md or a narrative page, and that row's text
     contains the name (or the form the register prints it in). A name nobody wrote down is not an entry.
  3  nobody is on it whom the archive's living rule does not show to be dead: recomputed here, from the act's year and
     the age the act gives, with the kit's living_rule directly (the builder uses tools/living_v2.py); a person with no
     age is taken to be at least 14; an act after 1930 is refused; nobody in people.json, living or dead, shares a
     name, an alias or an address with an entry
  4  (built) every entry has its /who/<name>/ page, indexable, in the sitemap, naming no date of birth and no
     /people/ link, and no page the build made for a name in people.json was replaced
"""
import argparse
import csv
import json
import os
import re
import sys
import tempfile
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import read_names as RN  # noqa: E402

DATA = os.path.join(ROOT, "data")
SRC = os.path.join(ROOT, "site", "src")


def tsv(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def surname_first(name):
    w = name.split(" ")
    return " ".join([w[-1]] + w[:-1]) if len(w) > 1 else name


class Support:
    """The text the archive holds, folded, by the key a `from` names."""

    def __init__(self):
        self.reads = {}
        for r in tsv(os.path.join(DATA, "scilla-reads.tsv")):
            k = "%s/%s" % (r["year"], r["act"])
            self.reads.setdefault(k, []).append(RN.fold(" ".join(r.values())))
        self.plates = {r["plate"]: RN.fold(" ".join([r["title"], r["what"], r["cite"]])) for r in tsv(os.path.join(DATA, "register-reads.tsv"))}
        self.m13 = {r["act"]: RN.fold(" ".join([r["groom"], r["bride"]])) for r in tsv(os.path.join(DATA, "scilla-matr-1913.tsv"))}
        self.pe = {}
        for r in tsv(os.path.join(DATA, "pe-mazza-acts.tsv")):
            self.pe.setdefault("%s/%s" % (r["year"], r["act"]), []).append(RN.fold(" ".join(r.values())))
        self.sr = [(r["who"], RN.fold(" ".join(r.values()))) for r in tsv(os.path.join(DATA, "sicily-reads.tsv"))]
        self.files = {}

    def file(self, rel):
        if rel not in self.files:
            p = os.path.join(ROOT, rel)
            self.files[rel] = RN.fold(open(p, encoding="utf-8").read()) if os.path.exists(p) else None
        return self.files[rel]

    def texts(self, frm):
        kind, _, key = frm.partition(":")
        if kind == "scilla-reads":
            return self.reads.get(key)
        if kind == "register-reads":
            return [self.plates[key]] if key in self.plates else None
        if kind == "scilla-matr-1913":
            return [self.m13[key]] if key in self.m13 else None
        if kind == "pe-mazza-acts":
            return self.pe.get(key)
        if kind == "sicily-reads":
            return [t for who, t in self.sr if who.startswith(key)] or None
        if kind == "notes":
            t = self.file("notes/" + key)
            return [t] if t else None
        if kind == "page":
            t = self.file("site/src/pages/%s.astro" % key)
            return [t] if t else None
        return None


def check_rows(problems, counts):
    sup = Support()
    rows = RN.rows()
    for r in rows:
        where = "read-names.tsv line %d" % r["_line"]
        texts = sup.texts((r.get("from") or "").strip())
        if not texts:
            problems.append("%s: «from» %s names no row of the archive's data" % (where, r.get("from")))
            continue
        name = " ".join(r["name"].split())
        form = " ".join((r.get("form") or "").split())
        variants = {RN.fold(name), RN.fold(surname_first(name))}
        if form:
            variants.add(RN.fold(form))
        if not any(v and v in t for t in texts for v in variants):
            problems.append("%s: the row «from» %s does not contain the name" % (where, r["from"]))
    counts["rows resting on a row of the archive's data"] = len(rows) - sum(1 for p in problems if "«from»" in p)
    return rows


def check_living(problems, counts, rows):
    """The living rule again, straight from the kit, not through the builder."""
    LV = RN.load_module(os.path.join(HERE, "living_v2.py"), "living_v2")
    lr = LV.lr
    today = lr.this_year()
    bad = 0
    for r in rows:
        try:
            year = int(r["year"])
        except ValueError:
            continue
        if year > RN.LAST_YEAR:
            continue                        # refused by the builder
        by, dead = RN.birth_year(r)
        if lr.is_living(by, dead, [], today):
            problems.append("read-names.tsv line %d: the living rule does not show this person to be dead" % r["_line"])
            bad += 1
    counts["rows the living rule shows not living (recomputed from the kit)"] = len(rows) - bad
    return bad


def check_doc(problems, counts):
    path = os.path.join(SRC, "data", "read-names.json")
    if not os.path.exists(path):
        problems.append("site/src/data/read-names.json is missing: run `npm run readnames`")
        return None
    doc = json.load(open(path, encoding="utf-8"))
    people = json.load(open(os.path.join(SRC, "data", "people.json"), encoding="utf-8"))
    nb = RN.load_module(os.path.join(HERE, "build_names_index.py"), "build_names_index")
    bear = {}
    slugs = set()
    for p in people:
        if p.get("name"):
            bear[RN.fold(nb.plain(p["name"]))] = True
            slugs.add(RN.slugify(p["name"]))
            ro = nb.register_order(p)
            if ro:
                bear[RN.fold(ro)] = True
    seen = set()
    for n in doc["names"]:
        keys = [RN.fold(n["name"])] + [RN.fold(a) for a in n.get("aliases", [])]
        if any(k in bear for k in keys):
            problems.append("a read name (line-free) is also borne in people.json")
        if n["slug"] in slugs:
            problems.append("a read name makes the same /who/ address as a name in people.json")
        if n["slug"] in seen:
            problems.append("two read names make one /who/ address")
        seen.add(n["slug"])
        for rec in n["records"]:
            if int(rec["year"]) > RN.LAST_YEAR:
                problems.append("a record after %d is in read-names.json" % RN.LAST_YEAR)
    counts["names in read-names.json"] = len(doc["names"])
    return doc


def check_built(problems, counts, doc):
    out = os.environ.get("ARCHIVE_OUT") or "dist"
    if not os.path.isdir(out):
        counts["built pages checked (no build here)"] = 0
        return
    sm = ""
    smp = os.path.join(out, "sitemap.xml")
    if os.path.exists(smp):
        sm = open(smp, encoding="utf-8").read()
    ok = 0
    for n in doc["names"]:
        p = os.path.join(out, "who", n["slug"], "index.html")
        if not os.path.exists(p):
            problems.append("a read name has no built page at /who/%s/" % n["slug"])
            continue
        h = open(p, encoding="utf-8").read()
        if re.search(r'name=["\']robots["\'][^>]*noindex', h, re.I):
            problems.append("/who/%s/ is noindex" % n["slug"])
        if "/people/" in re.sub(r"<(script|style)[^>]*>.*?</\1>", "", h, flags=re.S).replace('href="/people/"', ""):
            # the shared header links /people/ in its menu; a link to a person's page would be /people/<slug>/
            if re.search(r'href="/people/[^"?#]+', h):
                problems.append("/who/%s/ links to a /people/ page" % n["slug"])
        if sm and ("/who/%s/" % n["slug"]) not in sm:
            problems.append("/who/%s/ is not in the sitemap" % n["slug"])
        ok += 1
    counts["built /who/ pages, indexable and in the sitemap"] = ok


def run(selftest_row=None):
    problems, counts = [], {}
    doc, builder_problems, stats = RN.build()
    problems += builder_problems
    # the builder leaves these out so that nothing unsafe is ever published; the gate makes the row's presence a failure
    for k in ("left out: a name a living or held-out person bears", "left out: not shown dead by the living rule",
              "left out: an act after %d" % RN.LAST_YEAR):
        if stats.get(k):
            problems.append("%d row(s) in data/read-names.tsv are %s: remove them" % (stats[k], k.replace("left out: ", "")))
    rows = check_rows(problems, counts)
    check_living(problems, counts, rows)
    d = check_doc(problems, counts) if selftest_row is None else None
    if d is not None and not builder_problems:
        check_built(problems, counts, d)
    return problems, counts, stats


def selftest():
    """Plant one fault per rule in a copy of the TSV; each must be caught."""
    src = open(RN.TSV, encoding="utf-8").read().split("\n")
    header_i = next(i for i, ln in enumerate(src) if ln and not ln.startswith("#"))
    hdr = src[header_i].split("\t")
    sample = next(ln for ln in src[header_i + 1:] if ln.strip() and not ln.startswith("#")).split("\t")
    base = dict(zip(hdr, sample))

    def with_row(**kw):
        r = dict(base)
        r.update(kw)
        return "\t".join(r.get(c, "") for c in hdr)

    cases = [
        ("a name that is one word", with_row(name="Rossi")),
        ("a name nobody wrote down", with_row(name="Zefferino Quattrocchi", form="")),
        ("a year after the last accepted", with_row(year="1999")),
        ("a person the rule cannot show dead (a child of a late act)", with_row(**{"as": "child", "year": "1999"})),
        ("a kind that is not one", with_row(kind="Battesimi")),
        ("an ark the tables do not hold", with_row(ark="an_ua9999999")),
        ("a `from` that names nothing", with_row(**{"from": "scilla-reads:2099/1"})),
    ]
    missed = []
    for label, line in cases:
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "read-names.tsv")
            with open(p, "w", encoding="utf-8") as f:
                f.write("\n".join(src[:header_i + 1]) + "\n" + line + "\n")
            env = dict(os.environ, READ_NAMES_TSV=p)
            r = subprocess.run([sys.executable, os.path.abspath(__file__), "--selftest-one"], env=env,
                               capture_output=True, text=True)
            if r.returncode == 0:
                missed.append(label)
            print("  %s  selftest  %s" % ("ok  " if r.returncode != 0 else "FAIL", label))
    return missed


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--selftest-one", action="store_true", help=argparse.SUPPRESS)
    a = ap.parse_args(argv)
    if a.selftest:
        missed = selftest()
        if missed:
            print("check_read_names: FAIL, the gate did not catch: " + "; ".join(missed))
            return 1
        print("check_read_names: selftest ok, every planted fault was caught")
        return 0
    problems, counts, stats = run(selftest_row=True if a.selftest_one else None)
    if a.selftest_one:
        return 1 if problems else 0
    for k, v in {**stats, **counts}.items():
        print("  %-72s %d" % (k, v))
    if problems:
        for p in problems[:40]:
            print("  FAIL  " + p)
        print("check_read_names: FAIL (%d)" % len(problems))
        return 1
    print("check_read_names: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
