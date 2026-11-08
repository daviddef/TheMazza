#!/usr/bin/env python3
"""The negative-results page: what was searched, and what it did not turn up.

A source that returned nothing is evidence too — it is the difference between
"we have not looked" and "it is not there". data/searched.tsv is the record;
this writes it out for the site.

THE `key` COLUMN IS NOT DECORATION. The work-list gate counts outstanding
searches against the work list and needs an exact, stable identifier for each
row. Keys added to searched.json by hand were wiped the first time this script
ran, and the gate then reported "nothing outstanding" for an archive with
twenty-four outstanding searches. The key lives in the TSV, which is the
record, and is passed through untouched — never recomputed, so editing a scope
or a result cannot move it, and never reused when a row is retired.
"""
import csv, json, os, re
from collections import Counter

# the build runs this from site/, so anchor on the repo root
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
rows = list(csv.DictReader(open("data/searched.tsv", encoding="utf-8"), delimiter="\t"))

# THE FIELDS THE RECORD ATLAS TRACKER READS (scripts/import-research-sessions.py there).
# The TSV stays the record; these are derived into searched.json only, and only
# where the TSV already says it. Nothing here is invented:
#   when     ISO day, from the TSV's «20 Sep 2026». A row with no day stays blank:
#            all of them are `outstanding` / `not-yet`, work that has not happened,
#            and the importer drops a date from such a row on purpose.
#   outcome  the status, with `wall` read as `blocked` (the importer's word).
#   url      the provider's own front page, from the key's source prefix, and only
#            for sources the Atlas has a provider for. Not a deep link: the TSV
#            holds none, and a guessed one would be a claim.
#   tags     the family surnames (people.json, three or more people) the row's own
#            text names; Mazza when it names none.
#   waypoint / pages / walked are NOT derived. Nothing in the TSV states them.
MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}
DMY = re.compile(r"^(\d{1,2})\s+([A-Za-z]{3,9})\.?\s+((?:19|20)\d{2})$")
PROVIDERS = [  # key prefix after `src/` -> provider front page (Atlas data/providers.json)
    ("antenati-", "https://antenati.cultura.gov.it/"),
    ("naa-", "https://recordsearch.naa.gov.au/"),
    ("national-archives-of-austr", "https://recordsearch.naa.gov.au/"),
    ("familysearch-", "https://www.familysearch.org/"),
    ("myheritage-", "https://www.myheritage.com/"),
    ("trove-", "https://trove.nla.gov.au/"),
    ("find-a-grave-", "https://www.findagrave.com/"),
    ("geneanet-", "https://www.geneanet.org/"),
    ("findmypast-", "https://www.findmypast.co.uk/"),
    ("nara-", "https://catalog.archives.gov/"),
    ("cemla-", "https://search.cemla.com"),
    ("brisbane-catholic-", "https://search.cemsearch.com.au/mapguide/BrisbaneRCA/"),
]
_names = Counter(p["surname"] for p in json.load(open("site/src/data/people.json")) if p.get("surname"))
FAMILIES = sorted((n for n, c in _names.items() if c >= 3 and len(n) > 3), key=len, reverse=True)
FAMILY_RE = re.compile(r"\b(" + "|".join(re.escape(n) for n in FAMILIES) + r")\b")


def iso(when):
    m = DMY.match(when.strip())
    mo = m and MONTHS.get(m.group(2)[:3].lower())
    return f"{m.group(3)}-{mo:02d}-{int(m.group(1)):02d}" if mo else ""


for r in rows:
    r["when"] = iso(r["when"])
    r["outcome"] = "blocked" if r["status"] == "wall" else r["status"]
    tail = r["key"].split("/", 1)[-1]
    r["url"] = next((u for pre, u in PROVIDERS if tail.startswith(pre)), "")
    text = " ".join([r["source"], r["scope"], r["result"]])
    r["tags"] = list(dict.fromkeys(FAMILY_RE.findall(text))) or ["Mazza"]
json.dump(rows, open("site/src/data/searched.json", "w"), indent=1, ensure_ascii=False)
done = [r for r in rows if r["status"] == "done"]
print(f"{len(rows)} searches: {len(done)} done, {len(rows)-len(done)} outstanding")
