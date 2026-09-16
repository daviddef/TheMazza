#!/usr/bin/env python3
"""Mark, per person, what the archive has actually READ about them.

Most relationships in this archive still come from Michael Mazza's family tree
with no record behind them — that is the most important caveat on the site, and
the person pages have to say it rather than imply otherwise by drawing a
confident chart. But it is no longer true of everyone, and saying it of someone
it is not true of is its own kind of lie.

WHICH IS WHAT THIS SCRIPT USED TO DO. It gathered records from four places —
the Nudgee burial register, the NAA passenger index, the sources the tree cites,
and read-people.tsv — and from nowhere else. It never looked at
`documented-additions.tsv` or `corrections.tsv`, the two files where most of the
archive's evidence actually lives. So ANTONINO PROSTAMO, whose death at two in
the morning on the last night of 1837 is documented four times over in the
additions, had a page reading "No record has been read for this person. What is
known of them is what the tree asserts, and it is unverified." Twelve people were
in that position. The estate's landing page caught it.

So both files are read here too, keyed the way each one keys a person:
`documented-additions.tsv` by its `inTree` column, `corrections.tsv` by `slug`.
A citation goes to `records`; the prose goes to `corrections`, under the heading
the person page already has for it — "What a register says about this person,
which the tree does not."

THIS DOES NOT APPLY ANYTHING. The chart still draws the export as it stands, and
the person page still says so underneath. The disagreement between the files is
deliberate; being silent about it was not.
"""
import csv, json

BLANK = {"", "—", "-", "–"}

PATH = "site/src/data/people.json"
P = json.load(open(PATH))
by_slug = {p["slug"]: p for p in P}

READS = {}
for r in csv.DictReader(open("data/read-people.tsv"), delimiter="\t"):
    READS.setdefault(r["slug"], []).append(r)

# The two files where most of this archive's evidence lives. Each keys a person
# differently: additions by `inTree` (the row is ABOUT someone the export has),
# corrections by `slug`. Rows with neither are about people the export lacks and
# belong only on /corrections/.
ADDS = {}
for r in csv.DictReader(open("data/documented-additions.tsv"), delimiter="\t"):
    slug = (r.get("inTree") or "").strip()
    if slug not in BLANK:
        ADDS.setdefault(slug, []).append(r)

FIXES = {}
for r in csv.DictReader(open("data/corrections.tsv"), delimiter="\t"):
    slug = (r.get("slug") or "").strip()
    if slug not in BLANK:
        FIXES.setdefault(slug, []).append(r)

nudgee = {b["slug"]: b for b in json.load(open("site/src/data/nudgee.json"))["burials"]}
ships = {s["slug"]: s for s in json.load(open("site/src/data/ships.json"))}
anc = json.load(open("site/src/data/ancestors.json"))
spine = {x["id"] for g in anc["generations"] for x in g["people"]} | {a["id"] for a in anc["anchors"]}
gen_of = {}
for g in anc["generations"]:
    for x in g["people"]:
        gen_of[x["id"]] = g["gen"]

for p in P:
    recs = []
    if p["slug"] in nudgee:
        b = nudgee[p["slug"]]
        recs.append({"kind": "burial register",
                     "what": f"Brisbane Catholic Cemeteries register — plot {b['plot']}",
                     "href": "/nudgee"})
    if p["slug"] in ships:
        s = ships[p["slug"]]
        recs.append({"kind": "passenger index",
                     "what": f"NAA passenger arrivals index — the {s['ship'].title()}, {s['naaDate']}",
                     "href": "/crossings"})
    for src in p.get("sources", []):
        recs.append({"kind": "cited in the tree", "what": src, "href": "/sources"})
    for r in READS.get(p["slug"], []):
        recs.append({"kind": r["kind"], "what": r["what"], "href": r["href"]})
    for r in ADDS.get(p["slug"], []):
        recs.append({"kind": "documented addition", "what": r["source"],
                     "href": "/corrections"})
    for r in FIXES.get(p["slug"], []):
        recs.append({"kind": r["confidence"], "what": r["source"],
                     "href": "/corrections"})

    # a citation can reach a person by more than one route — the same act read
    # and also cited in the tree — and the page lists them one per line
    seen, unique = set(), []
    for r in recs:
        k = (r["kind"], r["what"], r["href"])
        if k not in seen:
            seen.add(k)
            unique.append(r)
    p["records"] = unique

    fixes = [r["correction"] for r in READS.get(p["slug"], []) if r["correction"]]
    fixes += [r["note"] for r in ADDS.get(p["slug"], []) if (r.get("note") or "").strip()]
    fixes += [f'{r["kind"]} — {r["recordSays"]}' for r in FIXES.get(p["slug"], [])
              if (r.get("recordSays") or "").strip()]
    p["corrections"] = fixes
    p["onSpine"] = p["id"] in spine
    p["ancGen"] = gen_of.get(p["id"])

json.dump(P, open(PATH, "w"), indent=1, ensure_ascii=False)
print(f"{sum(1 for p in P if p['records'])} people carry a record that has been read; "
      f"{sum(1 for p in P if p['onSpine'])} are ancestors of Mia and Rocco; "
      f"{sum(1 for p in P if p['corrections'])} carry a correction the registers forced")
