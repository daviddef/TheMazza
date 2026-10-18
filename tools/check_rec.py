#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The gate for citations that can be followed (components/Rec.astro) and scans beside their passage (PlateFig.astro).

    python3 ../tools/check_rec.py                 # from site/; ARCHIVE_OUT (as for every gate) beats --dist
    python3 ../tools/check_rec.py --write-floor   # lock in the current counts (refuses to write while any rose)
    python3 ../tools/check_rec.py --selftest      # plants one fault per rule in a copy of /scilla/ and requires each to be caught

WHY. On 18 October 2026 /scilla/ named an act, a volume or an ark in 96 passages and linked none of them. A passage
that cites a record now carries a link to it, and this keeps it so.

WHAT IT HOLDS (counts only, stdlib only, so it runs in CI as it does here)
  1  every <a data-rec> in the build goes where it says it does: an Antenati ark that is one of the archive's own
     (site/src/data/records.json), a FamilySearch ark of the right shape, a page of this archive that is built, the
     National Archives of Australia, or this archive's repository; and it has text. Nothing else.
  2  every <figure class="platefig"> shows a plate the manifest declares (site/src/data/reads.json) and that is in the
     build, with a link to the full scan and, if it is in a gallery, to that gallery entry.
  3  THE RATCHET. For each page listed in site/.recfloor.json, the number of passages that cite a record and carry no
     link to a record may only go down. A "passage" is the audit's: a paragraph, list item or labelled row (not a table
     cell, heading or figure caption) that quotes an act ("atto 63", "act 63 of 1888", "Nati 1861"), an ark, a
     manifest, a census, a burial or a register image. "A link to a record" is an <a data-rec>, or a link to Antenati,
     FamilySearch, the NAA, Trove, /sources/, /documents/, /searched/ or a plate.
  4  a page in the floor must carry at least one <a data-rec>: a check that examined nothing has not passed.
"""
import argparse
import html
import json
import os
import re
import sys
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "site", "src", "data")
FLOOR = os.environ.get("REC_FLOOR") or os.path.join(ROOT, "site", ".recfloor.json")      # the env var is for the self-test

SKIP = {"script", "style", "nav", "header", "footer", "svg", "noscript", "template"}
BLOCK = {"p", "li", "div", "section", "tr", "td", "th", "figure", "figcaption", "ul", "ol", "table", "blockquote",
         "dd", "dt", "dl", "article", "h1", "h2", "h3", "h4", "h5", "h6", "br", "thead", "tbody", "aside", "details",
         "summary"}
VOID = {"br", "hr", "img", "input", "meta", "link", "area", "base", "col", "embed", "source", "track", "wbr"}
ACT = re.compile(r"(\b(?:atto|acts?|no\.)\s*(?:n\.?\s*)?\d+\b|\b(?:Nati|Matrimoni|Morti|Pubblicazioni|Births?|Marriages?|Deaths?)\s+(?:of\s+)?1[6-9]\d\d\b|\bact\s+\d+\s+of\s+1[6-9]\d\d|\b1[6-9]\d\d,?\s+(?:atto|act)\s+\d+)", re.I)
ARK = re.compile(r"\b(an_ua\d+|img\.?\s*\d+|image\s+\d+|film\s+\d+|frame\s+\d+|ark:)", re.I)
MAN = re.compile(r"\b(manifest|passenger (?:index|list)|Ellis Island|NAA\b|naturali[sz]ation|ship's list|sailing list)", re.I)
CEN = re.compile(r"\b(census|electoral rolls?|Trove\b|BDM\b|death certificate|probate|burial register|Nudgee\b.*?plot)", re.I)
BAP = re.compile(r"\b(baptis[mt]|baptised|parish (?:book|register)|Riveli|catasto)", re.I)
STRICT = re.compile(r"(antenati|familysearch|recordsearch\.naa|trove\.nla|findmypast|familyhistory\.bdm|nationalarchives|"
                    r"ancestry|myheritage|libertyellis|statueofliberty|gravelocator|/sources|/documents|/searched|/plates/|#plates)", re.I)
ARK_URL = re.compile(r"^https://antenati\.cultura\.gov\.it/ark:/12657/(an_ua\d+)$")
FS_URL = re.compile(r"^https://www\.familysearch\.org/ark:/61903/[0-9]:[0-9]:[0-9A-Z]{3,5}(-[0-9A-Z]{1,5}){1,3}$")


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_main = 0
        self.skip = 0
        self.stack = []                      # open non-void tags
        self.tab = self.head = self.fig = 0
        self.cur = []
        self.hrefs = []
        self.rec = 0
        self.blocks = []                     # (text, hrefs, rec, tab, head, fig)
        self.recs = []                       # (href, data-rec, text, nested)
        self.figs = []                       # (img src, [hrefs in the caption])
        self._a = None
        self._a_depth = 0
        self._fig = None

    def flush(self):
        t = re.sub(r"\s+", " ", "".join(self.cur)).strip()
        if t:
            self.blocks.append((t, list(self.hrefs), self.rec, self.tab > 0, self.head > 0, self.fig > 0))
        self.cur, self.hrefs, self.rec = [], [], 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "main":
            self.in_main += 1
        if tag not in VOID:
            self.stack.append(tag)
        if not self.in_main:
            return
        if tag in SKIP:
            self.skip += 1
        if self.skip:
            return
        if tag in BLOCK:
            self.flush()
        if tag == "table":
            self.tab += 1
        if tag in ("h1", "h2", "h3", "h4"):
            self.head += 1
        if tag == "figcaption":
            self.fig += 1
        if tag == "figure" and "platefig" in (a.get("class") or ""):
            self._fig = {"img": None, "hrefs": []}
        if tag == "img" and self._fig is not None:
            self._fig["img"] = a.get("src")
        if tag == "a":
            if self._a is not None and (not self._a.get("plain") or "data-rec" in a):
                self.recs.append(("NESTED", "", "", True))         # a citation link in a link, or a link in one
            h = a.get("href") or ""
            self.hrefs.append(h)
            if self._fig is not None:
                self._fig["hrefs"].append(h)
            if "data-rec" in a:
                self.rec += 1
                self._a = {"href": h, "via": a.get("data-rec"), "text": [], "title": a.get("title") or ""}
            else:
                self._a = {"plain": True}
        if tag == "br":
            self.flush()

    def handle_endtag(self, tag):
        if tag in self.stack:
            while self.stack:
                x = self.stack.pop()
                if x == tag:
                    break
        if tag == "main":
            self.in_main = max(0, self.in_main - 1)
        if not self.in_main:
            return
        if tag in SKIP:
            self.skip = max(0, self.skip - 1)
            return
        if self.skip:
            return
        if tag == "a" and self._a is not None:
            if not self._a.get("plain"):
                self.recs.append((self._a["href"], self._a["via"], "".join(self._a["text"]).strip(), False))
            self._a = None
        if tag in BLOCK:
            self.flush()
        if tag == "table":
            self.tab = max(0, self.tab - 1)
        if tag in ("h1", "h2", "h3", "h4"):
            self.head = max(0, self.head - 1)
        if tag == "figcaption":
            self.fig = max(0, self.fig - 1)
        if tag == "figure" and self._fig is not None:
            self.figs.append(self._fig)
            self._fig = None

    def handle_data(self, data):
        if not self.in_main or self.skip:
            return
        self.cur.append(data)
        if self._a is not None and not self._a.get("plain"):
            self._a["text"].append(data)

    def close(self):
        super().close()
        self.flush()


def read(path):
    p = Page()
    with open(path, encoding="utf-8", errors="replace") as f:
        p.feed(f.read())
    p.close()
    return p


def passages(p):
    """(passages that cite a record, how many of them carry a link to one)"""
    tot = linked = 0
    for text, hrefs, rec, tab, head, fig in p.blocks:
        if tab or head or fig:
            continue
        if not (ACT.search(text) or MAN.search(text) or CEN.search(text) or BAP.search(text) or ARK.search(text)):
            continue
        tot += 1
        if rec or any(STRICT.search(h) for h in hrefs):
            linked += 1
    return tot, linked


def pages_of(dist):
    for d, ds, fs in os.walk(dist):
        ds[:] = [x for x in ds if x not in ("_astro", "node_modules", ".git", "plates")]
        if "index.html" in fs:
            rel = "/" + os.path.relpath(d, dist).replace(os.sep, "/") + "/"
            yield ("/" if rel == "/./" else rel), os.path.join(d, "index.html")


def selftest(dist):
    """One planted fault per rule, in a copy of the built /scilla/ page; each must make the gate fail."""
    import shutil
    import subprocess
    import tempfile
    src = os.path.join(dist, "scilla", "index.html")
    if not os.path.exists(src):
        print("check_rec: selftest FAIL, no built /scilla/ page in %s" % dist)
        return 1
    page = open(src, encoding="utf-8").read()
    anchor = re.compile(r'<a class="reclink"[^>]*>(.*?)</a>', re.S)
    cases = [
        ("every citation link removed (a passage cites a record and links none)", anchor.sub(lambda m: m.group(1), page)),
        ("a citation link to an ark the archive never wrote down", re.sub(r'ark:/12657/an_ua\d+', "ark:/12657/an_ua0000001", page, count=1)),
        ("a scan beside a passage that the manifest does not declare", page.replace('/plates/scilla-nati1855-atto163.jpg', '/plates/not-declared.jpg')),
        ("a citation link with no text", anchor.sub('<a class="reclink" href="https://antenati.cultura.gov.it/ark:/12657/an_ua2002913" data-rec="antenati" title="x"></a>', page, count=1)),
        ("a citation link inside another link", page.replace('<a class="reclink"', '<a href="/x/"><a class="reclink"', 1)),
    ]
    missed = []

    def stubs(td, html_):
        """the pages the page's own citation links point at, as empty pages, so only the planted fault is in play"""
        for h in re.findall(r'data-rec="own"[^>]*>|<a class="reclink" href="(/[^"#?]*)"', html_):
            pass
        for m in re.finditer(r'<a class="reclink" href="(/[^"]*)" data-rec="own"', html_):
            tgt = m.group(1).split("#")[0].split("?")[0].strip("/")
            os.makedirs(os.path.join(td, tgt), exist_ok=True)
            open(os.path.join(td, tgt, "index.html"), "w", encoding="utf-8").write("<html></html>")

    for label, html_ in cases:
        with tempfile.TemporaryDirectory() as td:
            os.makedirs(os.path.join(td, "scilla"))
            open(os.path.join(td, "scilla", "index.html"), "w", encoding="utf-8").write(html_)
            stubs(td, page)
            shutil.copytree(os.path.join(dist, "plates"), os.path.join(td, "plates"), dirs_exist_ok=True) if os.path.isdir(os.path.join(dist, "plates")) else None
            fl = os.path.join(td, "floor.json")
            json.dump({"pages": {"/scilla/": 0}}, open(fl, "w"))
            env = dict(os.environ, ARCHIVE_OUT=td, REC_FLOOR=fl)
            r = subprocess.run([sys.executable, os.path.abspath(__file__)], env=env, capture_output=True, text=True)
            caught = r.returncode != 0
            print("  %s  selftest  %s" % ("ok  " if caught else "FAIL", label))
            if not caught:
                missed.append(label)
    # and the untouched page passes
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, "scilla"))
        open(os.path.join(td, "scilla", "index.html"), "w", encoding="utf-8").write(page)
        stubs(td, page)
        shutil.copytree(os.path.join(dist, "plates"), os.path.join(td, "plates"), dirs_exist_ok=True) if os.path.isdir(os.path.join(dist, "plates")) else None
        fl = os.path.join(td, "floor.json")
        json.dump({"pages": {"/scilla/": 0}}, open(fl, "w"))
        r = subprocess.run([sys.executable, os.path.abspath(__file__)], env=dict(os.environ, ARCHIVE_OUT=td, REC_FLOOR=fl), capture_output=True, text=True)
        if r.returncode != 0:
            missed.append("the untouched page was refused")
            print("  FAIL  selftest  the untouched page was refused: " + r.stdout.strip().split("\n")[-1])
    if missed:
        print("check_rec: selftest FAIL, not caught: " + "; ".join(missed))
        return 1
    print("check_rec: selftest ok, every planted fault was caught")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dist", default="dist")
    ap.add_argument("--write-floor", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    dist = os.environ.get("ARCHIVE_OUT") or a.dist
    if a.selftest:
        return selftest(dist)
    if not os.path.isdir(dist):
        print("check_rec: FAIL, no build at %s" % dist)
        return 1
    arks = set(json.load(open(os.path.join(DATA, "records.json"), encoding="utf-8"))["ark"])
    plates = {r["plate"]: r for r in json.load(open(os.path.join(DATA, "reads.json"), encoding="utf-8"))}
    problems = []
    n_rec = n_fig = 0
    now = {}
    with_rec = {}
    for page, path in pages_of(dist):
        p = read(path)
        for href, via, text, nested in p.recs:
            if href == "NESTED":
                problems.append("%s: a citation link inside another link" % page)
                continue
            n_rec += 1
            if not text:
                problems.append("%s: a citation link with no text" % page)
            ok = False
            if via == "antenati":
                m = ARK_URL.match(href)
                ok = bool(m and m.group(1) in arks) or href.startswith("https://antenati.cultura.gov.it/search-registry/")
            elif via == "familysearch":
                ok = bool(FS_URL.match(href))
            elif via == "naa":
                ok = href.startswith("https://recordsearch.naa.gov.au/")
            elif via == "bdm":
                ok = href.startswith("https://www.familyhistory.bdm.qld.gov.au/")
            elif via == "trove":
                ok = href.startswith("https://trove.nla.gov.au/")
            elif via == "repository":
                ok = href.startswith("https://github.com/daviddef/")
            elif via == "own":
                tgt = href.split("#")[0].split("?")[0]
                ok = os.path.exists(os.path.join(dist, tgt.strip("/"), "index.html")) or tgt in ("/", "")
            if not ok:
                problems.append("%s: a citation link goes somewhere the archive does not hold (%s)" % (page, via))
        for fg in p.figs:
            n_fig += 1
            src = fg["img"] or ""
            fn = src.rsplit("/", 1)[-1]
            if fn not in plates:
                problems.append("%s: a scan beside a passage is a plate the manifest does not declare (%s)" % (page, fn))
            elif not os.path.exists(os.path.join(dist, "plates", fn)):
                problems.append("%s: a scan beside a passage is not in the build (%s)" % (page, fn))
            if not any(h.endswith(fn) for h in fg["hrefs"]):
                problems.append("%s: a scan beside a passage does not link to the full scan (%s)" % (page, fn))
        tot, lk = passages(p)
        now[page] = tot - lk
        with_rec[page] = len(p.recs)
    floor = {}
    if os.path.exists(FLOOR):
        floor = json.load(open(FLOOR, encoding="utf-8")).get("pages", {})
    if a.write_floor:
        # the narrative pages only: an address under /people/ or /who/ is a name, and a committed file does not list names
        new = {pg: now[pg] for pg in sorted(now) if with_rec.get(pg) and not pg.startswith(("/people/", "/who/"))}
        rose = [pg for pg in new if pg in floor and new[pg] > floor[pg]]
        if rose:
            print("check_rec: refusing to write the floor, %d page(s) rose" % len(rose))
            return 1
        with open(FLOOR, "w", encoding="utf-8") as f:
            json.dump({"version": 1, "note": "Per page: passages that cite a record and carry no link to one. A page may only go down. "
                       "Written by check_rec.py --write-floor; raise a number only by hand, in a commit that says why.",
                       "pages": new}, f, indent=1)
            f.write("\n")
        print("check_rec: wrote the floor for %d page(s)" % len(new))
    for pg in floor:
        if pg.startswith(("/people/", "/who/")):
            problems.append("the floor names a page under /people/ or /who/, whose address is a name: rewrite it with --write-floor")
    for pg, cap in sorted(floor.items()):
        if pg not in now:
            problems.append("%s is in the floor and not in the build" % pg)
            continue
        if now[pg] > cap:
            problems.append("%s: %d passage(s) cite a record with no link to it (the floor is %d)" % (pg, now[pg], cap))
        if not with_rec.get(pg):
            problems.append("%s is in the floor and carries no citation link: the check examined nothing" % pg)
    print("check_rec: %d citation links and %d scans beside a passage read; %d page(s) in the floor, %d passage(s) cite a record "
          "without a link on them" % (n_rec, n_fig, len(floor), sum(now[pg] for pg in floor if pg in now)))
    if n_rec == 0:
        problems.append("no citation link in the build: Rec.astro did not run")
    if problems:
        for pr in problems[:40]:
            print("  FAIL  " + pr)
        print("check_rec: FAIL (%d)" % len(problems))
        return 1
    print("check_rec: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
