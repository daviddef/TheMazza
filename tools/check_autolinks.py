#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The namesake gate for the build-time name linker: every link the pass added must be to the one person who bears that name.

    python3 ../tools/check_autolinks.py [--dist dist]          # from site/ (ARCHIVE_OUT, as for every gate, beats --dist)

kit/tools/checklinks.py holds the pass to its index and to a ratchet. This holds the INDEX to the data. It reads every
`<a href data-autolink>` in the built pages and people.json, and fails when:

  * a link to a person is to a page whose person is living, or whose name (or register-order form, "Family Given") is
    not the link text, or whose name another person also bears (a namesake: the pass would have to send it to the roster);
  * a link to the roster (`/people/?q=`) is for a name that fewer than two people bear, any of them living, or whose
    address names a different name from the link text;
  * a link to a person sits against a word that makes a longer name the data holds ("Mary" + a link on "Rosa Mazza"
    where "Mary Rosa Mazza" is a person): the text names somebody else. A roster link is exempt: it lists every bearer
    of the shorter name, the longer one included;
  * the pass added nothing (it did not run).

Names are compared folded for case, accents, apostrophes and hyphens. Prints counts, and for a failure the page and the
text of a link to a person who is NOT living; it never prints the text of a link to a living one.
"""
import os
import re
import sys
import json
import html
import argparse
from urllib.parse import unquote

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import build_names_index as B  # noqa: E402  (plain, fold, register_order: the index's own rules)

PEOPLE = os.path.join(ROOT, "site", "src", "data", "people.json")
LINK = re.compile(r'<a href="([^"]*)" data-autolink>(.*?)</a>', re.S)
TAG = re.compile(r"<[^>]+>")
WORD = re.compile(r"[^\W\d_][\w'’\-]*")


def pages(dist):
    for d, ds, fs in os.walk(dist):
        ds[:] = [x for x in ds if x not in ("_astro", "node_modules", ".git")]
        for f in sorted(fs):
            if f.endswith(".html"):
                yield os.path.join(d, f)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dist", default="dist")
    a = ap.parse_args(argv)
    dist = os.environ.get("ARCHIVE_OUT") or a.dist
    if not os.path.isdir(dist):
        print("check_autolinks: FAIL, no build at %s" % dist)
        return 1
    with open(PEOPLE, encoding="utf-8") as f:
        people = json.load(f)
    by_key, by_slug = {}, {}
    for p in people:
        by_key.setdefault(B.fold(p["name"]), []).append(p)
        by_slug[p["slug"]] = p
    names = set(by_key)

    # the committed floor must not name a person: a page's address under /people/ or /who/ is a name
    floor = os.path.join(ROOT, "site", ".linkfloor.json")
    if os.path.exists(floor):
        with open(floor, encoding="utf-8") as f:
            fl = json.load(f).get("pages", {})
        named = [k for k in fl if k.startswith(("/people/", "/who/"))]
        if named:
            print("check_autolinks: FAIL, site/.linkfloor.json lists %d page(s) under /people/ or /who/, whose "
                  "addresses are names (some are living people's). Write it with tools/write_linkfloor.py." % len(named))
            return 1

    n = n_person = n_search = n_alias = 0
    problems = []                       # (page, kind, text or None)
    for path in pages(dist):
        page = "/" + os.path.relpath(os.path.dirname(path), dist).replace(os.sep, "/") + "/"
        with open(path, encoding="utf-8", errors="surrogateescape") as f:
            t = f.read()
        for m in LINK.finditer(t):
            n += 1
            href = html.unescape(m.group(1))
            text = html.unescape(TAG.sub("", m.group(2)))
            k = B.fold(text)
            if href.startswith("/people/?q="):
                n_search += 1
                bs = by_key.get(k, [])
                if len(bs) < 2:
                    problems.append((page, "search link for a name fewer than two people bear", text))
                elif any(b["living"] for b in bs):
                    problems.append((page, "search link for a name a living person bears", None))
                elif B.fold(unquote(href.split("?q=", 1)[1])) != k:
                    problems.append((page, "search link whose address names another name", text))
                continue
            n_person += 1
            p = by_slug.get(unquote(href.rstrip("/").split("/")[-1])) if href.startswith("/people/") else None
            if p is None:
                problems.append((page, "link to an address that is not a person", text))
                continue
            if p["living"]:
                problems.append((page, "link to a living person", None))
                continue
            alias = B.register_order(p)
            own = k == B.fold(p["name"])
            if not own and not (alias and k == B.fold(alias)):
                problems.append((page, "link text is not the person's name", text))
                continue
            if not own:
                n_alias += 1
                if k in by_key:
                    problems.append((page, "register-order form is another person's name", text))
                    continue
            if len(by_key[B.fold(p["name"])]) != 1:
                problems.append((page, "link to one person for a name several bear", text))
                continue
            # a longer name the data holds, written against this one
            pre = WORD.findall(TAG.sub(" ", t[max(0, m.start() - 160):m.start()]))[-2:]
            post = WORD.findall(TAG.sub(" ", t[m.end():m.end() + 160]))[:2]
            ext = []
            if pre:
                ext.append(pre[-1] + " " + text)
            if len(pre) > 1:
                ext.append(pre[-2] + " " + pre[-1] + " " + text)
            if post:
                ext.append(text + " " + post[0])
            if len(post) > 1:
                ext.append(text + " " + post[0] + " " + post[1])
            if any(B.fold(e) in names for e in ext):
                problems.append((page, "link on part of a longer name", text))
    print("check_autolinks: %d links read (%d to one person, %d of them by the register-order form; %d to the roster)"
          % (n, n_person, n_alias, n_search))
    if n == 0:
        print("check_autolinks: FAIL, the pass added no link: it did not run, or the index is empty")
        return 1
    if problems:
        print("check_autolinks: FAIL (%d)" % len(problems))
        for page, what, text in problems[:40]:
            print("  - %s: %s%s" % (page, what, (" [%s]" % text) if text else ""))
        return 1
    print("check_autolinks: ok, every link is to the one person who bears the name, or to the roster of those who do")
    return 0


if __name__ == "__main__":
    sys.exit(main())
