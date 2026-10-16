#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The family pages: do they exist, do they show every dead bearer, and do they name no living person?

    python3 ../tools/check_familypages.py [--dist DIR]        # from site/ (what `npm run check:familypages` runs)
    python3 ../tools/check_familypages.py --selftest          # plants a fault per rule in a COPY and requires each caught

The family pages /prostamo/, /polistena/ ... are one template (site/src/pages/[family].astro) fed by
site/src/lib/familylist.js and site/src/lib/families.js. What can go wrong, and what this refuses:

  1  a family in familylist.js has no built page, or its page is noindex, has no canonical, or is not in the sitemap
  2  a family page is missing from the menu ("The name" group, which the landing page builds its chips from)
  3  a page does not link every DEAD bearer of the name (people.json: the surname or a listed spelling, not living)
  4  a page links a LIVING person's page, or prints a living person's full name that no dead person shares.
     A family page is indexed; a living person's own page is not. The page may count the living and never name one.
  5  the sentence a page quotes about what a name means is not word for word what /name/ says
     (site/src/pages/name.astro), so a quotation cannot drift from its source

Who is living is NOT decided here: it is the `living` flag the archive's one definition (tools/living_v2.py) wrote
into people.json. This reads that flag, never a date.

Exit 0 clean, 1 on a fault, 2 when there is nothing to read (no build, no people): "could not look" is not a pass.
"""
import argparse
import html
import json
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SITE = os.path.join(ROOT, "site")
sys.path.insert(0, os.path.join(SITE, "node_modules", "@daviddef", "archive-kit", "kit", "tools"))
try:
    import outdir as _outdir
except Exception:           # the kit not installed: fall back to --dist / dist
    _outdir = None


def families():
    src = open(os.path.join(SITE, "src", "lib", "familylist.js"), encoding="utf-8").read()
    built = src[src.index("export const BUILT"):src.index("export const FAMILY_MENU")]
    out = []
    for m in re.finditer(r'\{\s*slug:\s*"([^"]+)",\s*surname:\s*"([^"]+)",\s*also:\s*\[([^\]]*)\]', built):
        out.append((m.group(1), m.group(2), re.findall(r'"([^"]+)"', m.group(3))))
    return out


def text_of(page):
    s = open(page, encoding="utf-8").read()
    m = re.search(r"<main.*?</main>", s, re.S)
    body = m.group(0) if m else s
    body = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", body, flags=re.S)
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body)))


def norm(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s))).strip()


def run(dist, quiet=False, namesrc_path=None):
    fails = []
    fam = families()
    people = json.load(open(os.path.join(SITE, "src", "data", "people.json"), encoding="utf-8"))
    if not fam or not people or not os.path.isdir(dist):
        print("  NOT RUN  familypages  nothing to read (families %d, people %d, dist %s)" % (len(fam), len(people), os.path.isdir(dist)))
        return 2, []
    dead_names = {p["name"].strip().lower() for p in people if not p.get("living")}
    living = [p for p in people if p.get("living")]
    living_slugs = {p["slug"] for p in living}
    living_only_names = {p["name"].strip() for p in living if p["name"].strip().lower() not in dead_names and len(p["name"].split()) >= 2}
    sitemap = open(os.path.join(dist, "sitemap.xml"), encoding="utf-8").read() if os.path.exists(os.path.join(dist, "sitemap.xml")) else ""
    namepage = ""
    np = os.path.join(dist, "name", "index.html")
    if os.path.exists(np):
        namepage = open(np, encoding="utf-8").read()
    home = open(os.path.join(dist, "index.html"), encoding="utf-8").read() if os.path.exists(os.path.join(dist, "index.html")) else ""

    for slug, surname, also in fam:
        page = os.path.join(dist, slug, "index.html")
        if not os.path.exists(page):
            fails.append("%s: no built page at /%s/" % (surname, slug))
            continue
        raw = open(page, encoding="utf-8").read()
        if re.search(r'<meta[^>]+name=["\']robots["\'][^>]*noindex', raw, re.I):
            fails.append("%s: the page is noindex" % surname)
        if not re.search(r'<link[^>]+rel=["\']canonical["\']', raw, re.I):
            fails.append("%s: the page has no canonical" % surname)
        if "/%s/</loc>" % slug not in sitemap:
            fails.append("%s: /%s/ is not in the sitemap" % (surname, slug))
        for where, doc in (("menu on the home page", home), ("menu on /name/", namepage)):
            if 'href="/%s/"' % slug not in doc:
                fails.append("%s: /%s/ is not in the %s" % (surname, slug, where))
        names = {surname, *also}
        dead = [p for p in people if p.get("surname") in names and not p.get("living")]
        links = set(re.findall(r'href="/people/([^"/?#]+)/?"', raw))
        for p in dead:
            if p["slug"] not in links:
                fails.append("%s: dead bearer %s is not linked" % (surname, p["slug"]))
        for s in sorted(links & living_slugs):
            fails.append("%s: links a living person's page (%s)" % (surname, s))
        body = text_of(page)
        for n in sorted(living_only_names):
            if re.search(r"(?<![A-Za-zÀ-ÿ])" + re.escape(n) + r"(?![A-Za-zÀ-ÿ])", body):
                fails.append("%s: prints the name of a living person (a name no dead person bears)" % surname)
                break

    # 5: the quoted sentence equals what /name/ says
    lib = open(os.path.join(SITE, "src", "lib", "families.js"), encoding="utf-8").read()
    block = lib[lib.index("export const NAME_NOTES"):lib.index("};", lib.index("export const NAME_NOTES"))]
    namesrc = norm(open(namesrc_path or os.path.join(SITE, "src", "pages", "name.astro"), encoding="utf-8").read())
    notes = re.findall(r"(\w+):\s*`([^`]*)`", block)
    if not notes:
        fails.append("NAME_NOTES could not be read from lib/families.js")
    for surname, quoted in notes:
        if norm(quoted) not in namesrc:
            fails.append("%s: the quoted note is not word for word what name.astro says" % surname)
    if not quiet:
        print("  %-5s familypages  %d family pages, %d dead bearers linked, %d living slugs checked, %d quoted notes"
              % ("FAIL" if fails else "ok", len(fam),
                 sum(1 for _, s, a in fam for p in people if p.get("surname") in {s, *a} and not p.get("living")),
                 len(living_slugs), len(notes)))
        for f in fails[:40]:
            print("        " + f)
    return (1 if fails else 0), fails


def selftest(dist):
    """One planted fault per rule, in a copy of the build. Each must be caught, and the untouched copy must pass."""
    fam = families()
    people = json.load(open(os.path.join(SITE, "src", "data", "people.json"), encoding="utf-8"))
    slug, surname, also = fam[0]
    living_slug = next(p["slug"] for p in people if p.get("living"))
    living_name = next(p["name"] for p in people if p.get("living")
                       and p["name"].strip().lower() not in {q["name"].strip().lower() for q in people if not q.get("living")}
                       and len(p["name"].split()) >= 2)
    dead = next(p for p in people if p.get("surname") == surname and not p.get("living"))
    results = []

    def trial(label, mutate):
        tmp = tempfile.mkdtemp(prefix="familypages-selftest-")
        try:
            cp = os.path.join(tmp, "dist")
            shutil.copytree(dist, cp)
            mutate(cp)
            code, fails = run(cp, quiet=True)
            results.append((label, code == 1 and bool(fails)))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def edit(path, fn):
        s = open(path, encoding="utf-8").read()
        t = fn(s)
        assert t != s, "the planted change did nothing to " + path
        open(path, "w", encoding="utf-8").write(t)

    pg = lambda cp: os.path.join(cp, slug, "index.html")
    code, _ = run(dist, quiet=True)
    results.append(("untouched build passes (control)", code == 0))
    trial("page removed", lambda cp: shutil.rmtree(os.path.join(cp, slug)))
    trial("page made noindex", lambda cp: edit(pg(cp), lambda s: s.replace("</head>", '<meta name="robots" content="noindex"></head>', 1)))
    trial("page dropped from the sitemap", lambda cp: edit(os.path.join(cp, "sitemap.xml"), lambda s: s.replace("/%s/</loc>" % slug, "/x-%s/</loc>" % slug)))
    trial("page dropped from the menu", lambda cp: edit(os.path.join(cp, "index.html"), lambda s: s.replace('href="/%s/"' % slug, 'href="/x/"')))
    trial("a dead bearer not linked", lambda cp: edit(pg(cp), lambda s: re.sub(r'href="/people/%s/?"' % re.escape(dead["slug"]), 'href="/people/x"', s)))
    trial("a living person's page linked", lambda cp: edit(pg(cp), lambda s: s.replace("</main>", '<a href="/people/%s/">x</a></main>' % living_slug, 1)))
    trial("a living person's name printed", lambda cp: edit(pg(cp), lambda s: s.replace("</main>", "<p>%s</p></main>" % living_name, 1)))
    ok = all(r[1] for r in results)
    for label, caught in results:
        print("  %-5s selftest  %s" % ("ok" if caught else "FAIL", label))
    # the quotation rule needs the source changed, so it is proved against a temporary copy of name.astro
    orig = open(os.path.join(SITE, "src", "pages", "name.astro"), encoding="utf-8").read()
    assert "Calabrian and uncommon" in orig, "the planted change needs a sentence that name.astro holds"
    tmpf = tempfile.NamedTemporaryFile("w", suffix=".astro", delete=False, encoding="utf-8")
    try:
        tmpf.write(orig.replace("Calabrian and uncommon", "Calabrian and common", 1))
        tmpf.close()
        code, fails = run(dist, quiet=True, namesrc_path=tmpf.name)
        caught = code == 1 and any("word for word" in f for f in fails)
    finally:
        os.unlink(tmpf.name)
    print("  %-5s selftest  a quoted note that no longer matches /name/" % ("ok" if caught else "FAIL"))
    return 0 if ok and caught else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dist", default=None)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    dist = a.dist or "dist"
    if _outdir:
        dist = _outdir.resolve(dist)          # ARCHIVE_OUT beats --dist, as everywhere in this kit
    if not os.path.isabs(dist):
        dist = os.path.join(SITE, dist)
    if a.selftest:
        sys.exit(selftest(dist))
    code, _ = run(dist)
    sys.exit(code)


if __name__ == "__main__":
    main()
