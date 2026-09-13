#!/usr/bin/env python3
"""One flat index over every page this archive builds.

Built from the rendered HTML rather than from the data files, for two reasons:
the narrative pages carry prose that exists in no JSON, and a page that
noindexes itself can be skipped here by reading the same tag a search engine
would read — so the index can never disagree with the archive's own privacy
rule.

Runs after a build and writes into site/public, so the NEXT build ships it.
A brand new page is therefore missed on its first build and caught on the
second; the deploy runs build, index, build.

Diacritics are folded both ways, so Blazevic finds Blažević and Scilla finds
Scilla however it is typed.
"""
import json, os, re, unicodedata, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "site", "dist")
OUT = os.path.join(ROOT, "site", "public", "searchindex.json")

NOINDEX = re.compile(r'name=["\']robots["\'][^>]*noindex', re.I)
TITLE = re.compile(r"<title>(.*?)</title>", re.S | re.I)
DESC = re.compile(r'<meta name="description" content="(.*?)"', re.S | re.I)
STRIP = re.compile(r"<(script|style|nav|header|footer)[^>]*>.*?</\1>", re.S | re.I)
TAGS = re.compile(r"<[^>]+>")
WS = re.compile(r"\s+")


def fold(s):
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.replace("đ", "d").replace("Đ", "D").lower()


def kind(path):
    if path.startswith("/people/"):
        return "Person"
    if path.startswith("/places/") or path.startswith("/place/"):
        return "Place"
    if path.startswith("/documents") or path.startswith("/register"):
        return "Record"
    if path.startswith("/corrections"):
        return "Correction"
    return "Page"


rows, skipped = [], 0
for dp, _, fns in os.walk(DIST):
    if "index.html" not in fns:
        continue
    src = os.path.join(dp, "index.html")
    raw = open(src, encoding="utf-8", errors="ignore").read()
    if NOINDEX.search(raw[:4000]) or 'http-equiv="refresh"' in raw[:400]:
        skipped += 1
        continue
    rel = os.path.relpath(dp, DIST).replace(os.sep, "/")
    path = "/" if rel == "." else f"/{rel}/"

    t = TITLE.search(raw)
    title = html.unescape(WS.sub(" ", TAGS.sub("", t.group(1)))).strip() if t else path
    title = re.sub(r"\s*[—·|]\s*The .*Archive\s*$", "", title).strip() or path

    d = DESC.search(raw)
    sub = html.unescape(WS.sub(" ", d.group(1))).strip()[:120] if d else ""

    body = TAGS.sub(" ", STRIP.sub(" ", raw))
    body = WS.sub(" ", html.unescape(body)).strip()[:2600]

    q = fold(f"{title} {sub} {body}")
    rows.append({"k": kind(path), "t": title, "s": sub, "h": path, "q": q})

rows.sort(key=lambda r: (r["k"], r["t"]))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(rows, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print(f"searchindex: {len(rows)} rows, {skipped} withheld -> site/public/searchindex.json")
