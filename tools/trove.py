#!/usr/bin/env python3
"""Trove API v3 — Australian newspapers and the Commonwealth Gazette.

WHY AN API AND NOT THE SITE. Work-list row 79 tried Trove's search page and it
will not run in this session's browser: the single-page app throws inside its
own vendor bundle on a storage API the pane does not provide, echoes the query
back, and never paints a result list. That is a tool failure, not a source
failure, and it blocked the source for eight days. The API needs no JavaScript.

THE KEY IS A SECRET AND THIS REPOSITORY IS PUBLIC. It is read from .env, which
is gitignored (.gitignore line 9). It is never printed, never written into a
data file, and never passed on a command line where `ps` would show it. If it
is missing this script says so and stops rather than searching anonymously and
reporting an empty result as a finding — which is exactly the false zero this
archive has catalogued three shapes of.

  python3 tools/trove.py search "Prostamo" [--category newspaper] [--n 100]
  python3 tools/trove.py sweep                # every surname, to a TSV
"""
import json, os, sys, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(HERE, ".."))

API = "https://api.trove.nla.gov.au/v3/result"


def key():
    k = os.environ.get("TROVE_API_KEY")
    if not k and os.path.exists(".env"):
        for line in open(".env", encoding="utf-8"):
            line = line.strip()
            if line.startswith("TROVE_API_KEY="):
                k = line.split("=", 1)[1].strip()
    if not k:
        sys.exit("  FAIL  no TROVE_API_KEY in the environment or .env — refusing to search "
                 "anonymously, because an unauthenticated zero looks exactly like a real one.")
    return k


def get(params, k):
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"X-API-KEY": k, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def article(aid, k=None):
    """The OCR text of one article. The search result does NOT carry it —
    `include=articletext` on /result is silently ignored and returns an empty
    `snippet`, which reads exactly like an article with no text. It has to be
    asked for per article, on /newspaper/<id>."""
    import re
    k = k or key()
    url = f"https://api.trove.nla.gov.au/v3/newspaper/{aid}?include=articletext&encoding=json"
    req = urllib.request.Request(url, headers={"X-API-KEY": k, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        d = json.load(r)
    t = d.get("articleText") or ""
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def text(aid):
    """The OCR of one article, from the public article page.

    THE API DOES NOT CARRY IT for Government Gazette Notices. `include=articletext`
    is accepted and silently ignored on both /result and /newspaper/<id>, and the
    `snippet` field comes back empty — which reads exactly like an article with no
    text rather than like a field the endpoint will not serve. The page at
    nla.gov.au/nla.news-article<id> renders the OCR as ordinary HTML.

    AND THE OCR IS TWO COLUMNS READ ACROSS. A naturalisation list prints
    «Surname, Given Names» down each column; flattened it becomes
    «... Prineas, Panagiotis Prostamo, Angela Prostamo, Antonmo Giacomo Przybylo,
    Jozef ...», so the given name after a surname belongs to the NEXT person.
    Read the pairs, not the sequence. `m` for `in` is the usual OCR slip here:
    Antonmo is Antonino.
    """
    import re, html as _html
    url = f"https://nla.gov.au/nla.news-article{aid}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        h = r.read().decode("utf-8", "ignore")
    h = re.sub(r"(?s)<script.*?</script>", " ", h)
    h = re.sub(r"(?s)<style.*?</style>", " ", h)
    return re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", " ", h))).strip()


def search(q, category="newspaper", n=100, cap=400):
    """Every hit for q, paged through Trove's cursor. Returns (total, articles)."""
    k, out, s, total = key(), [], "*", None
    while True:
        d = get({"q": q, "category": category, "n": min(n, 100), "s": s,
                 "encoding": "json", "reclevel": "full"}, k)
        cat = (d.get("category") or [{}])[0]
        rec = cat.get("records") or {}
        if total is None:
            total = rec.get("total", 0)
        got = rec.get("article") or rec.get("work") or []
        out.extend(got)
        s = rec.get("nextStart")
        if not s or not got or len(out) >= min(total or 0, cap):
            break
        time.sleep(0.4)
    return total, out


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "search"
    if cmd == "search":
        q = sys.argv[2]
        cat = sys.argv[sys.argv.index("--category") + 1] if "--category" in sys.argv else "newspaper"
        total, arts = search(q, cat)
        print(f"{q!r} in {cat}: {total} result(s), {len(arts)} fetched")
        for a in arts[:40]:
            t = a.get("heading") or a.get("title") or "—"
            print(f"  {a.get('date','—')}  {(a.get('title') or {}).get('title','—')[:34]:36s} {t[:60]}")
