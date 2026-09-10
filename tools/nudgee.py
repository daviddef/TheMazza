#!/usr/bin/env python3
"""Query the Brisbane Catholic cemeteries register for this family's surnames.

Nudgee is run by the Archdiocese, not the city council, so it is absent from the
Brisbane City Council grave search. Its own portal takes a POST and returns a
plain HTML grid with the plot number — which is the one thing the family tree
does not have for any of its thirteen Nudgee burials.

Endpoint recovered from the Falco archive's research notes.
"""
import re, json, html, urllib.parse, urllib.request, sys, time

URL = "https://search.cemsearch.com.au/mapguide/BrisbaneRCA/Private/query.php?type=Deceased"
SURNAMES = ["Mazza", "Prostamo", "Arena", "Polistena", "Nicotra", "Cavallaro",
            "Armanno", "Micale", "Melluso", "Pagano", "Anile", "Donato",
            "Bova", "Trungadi", "Mazzitelli", "Coco", "Napoli", "Calarco"]

def query(surname):
    data = urllib.parse.urlencode({
        "type": "Deceased", "CemeteryCode": "%", "SectionCode": "%",
        "Surname": surname, "GivenNames": "",
    }).encode()
    req = urllib.request.Request(URL, data=data, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "Content-Type": "application/x-www-form-urlencoded",
    })
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", "replace")

def rows(page):
    m = re.search(r'<table[^>]*id="grid".*?</table>', page, re.S | re.I)
    if not m:
        return []
    out = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", m.group(0), re.S | re.I):
        cells = [html.unescape(re.sub(r"<[^>]+>", " ", c)).strip()
                 for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S | re.I)]
        cells = [re.sub(r"\s+", " ", c) for c in cells]
        if any(cells):
            out.append(cells)
    return out

all_rows, header = [], None
for s in SURNAMES:
    try:
        page = query(s)
    except Exception as e:
        print(f"{s}: ERROR {e}", file=sys.stderr)
        continue
    rs = rows(page)
    if rs and not header:
        header = rs[0]
    body = [r for r in rs[1:]] if rs else []
    print(f"{s:12s} {len(body):3d} rows")
    for r in body:
        all_rows.append({"surname": s, "cells": r})
    time.sleep(0.6)

print("\nHEADER:", header)
json.dump({"header": header, "rows": all_rows},
          open("data/nudgee-search.json", "w"), indent=1, ensure_ascii=False)
print(f"\ntotal {len(all_rows)} rows -> data/nudgee-search.json")
