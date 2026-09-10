#!/usr/bin/env python3
"""Mark, per person, what the archive has actually READ about them.

Every relationship in this archive comes from Michael Mazza's family tree and
none of them has yet been proved by a record — that is the single most important
caveat on the site, and the person pages have to say it rather than imply
otherwise by drawing a confident chart.

What CAN be marked is the small set of people for whom a record has been read:
the nineteen in the Nudgee burial register, the nine in the NAA passenger index,
and the eleven the tree itself cites a source for. This writes that back onto
people.json so the chart can show it.
"""
import csv, json

PATH = "site/src/data/people.json"
P = json.load(open(PATH))
by_slug = {p["slug"]: p for p in P}

READS = {}
for r in csv.DictReader(open("data/read-people.tsv"), delimiter="\t"):
    READS.setdefault(r["slug"], []).append(r)

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
    p["records"] = recs
    p["corrections"] = [r["correction"] for r in READS.get(p["slug"], []) if r["correction"]]
    p["onSpine"] = p["id"] in spine
    p["ancGen"] = gen_of.get(p["id"])

json.dump(P, open(PATH, "w"), indent=1, ensure_ascii=False)
print(f"{sum(1 for p in P if p['records'])} people carry a record that has been read; "
      f"{sum(1 for p in P if p['onSpine'])} are ancestors of Mia and Rocco; "
      f"{sum(1 for p in P if p['corrections'])} carry a correction the registers forced")
