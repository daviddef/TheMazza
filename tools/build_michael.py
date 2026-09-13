#!/usr/bin/env python3
"""Regenerate notes/for-michael.md from the two TSVs it summarises.

The head of the document is written by hand; everything below "Missing people"
is generated, so the deliverable can never drift from data/corrections.tsv and
data/documented-additions.tsv.
"""
import csv, collections, datetime

corr = list(csv.DictReader(open("data/corrections.tsv"), delimiter="\t"))
adds = list(csv.DictReader(open("data/documented-additions.tsv"), delimiter="\t"))
documented = sum(1 for r in corr if r["confidence"] == "documented")

ORDER = ["Missing people — TWO NEW GENERATIONS", "Parentage", "Birth year", "Birth date",
         "Death date", "Death -- missing entirely", "Marriage -- missing entirely",
         "Parents -- missing entirely", "Missing people", "Relationship", "Duplicate record",
         "Generation — a lead, RETRACTED", "Crossing date", "Crossing -- ship named",
         "Crossing -- missing entirely", "Port", "Trade -- missing entirely"]
groups = collections.OrderedDict()
for k in ORDER:
    g = [r for r in corr if r["kind"] == k]
    if g:
        groups[k] = g
for r in corr:                                   # anything not in ORDER
    if r["kind"] not in groups:
        groups[r["kind"]] = [x for x in corr if x["kind"] == r["kind"]]

HEAD = open("notes/for-michael.head.md", encoding="utf-8").read().rstrip("\n")
out = [HEAD.replace("{N}", str(len(corr))).replace("{D}", str(documented))
           .replace("{A}", str(len(adds)))]

for kind, rows in groups.items():
    out.append(f"\n## {kind}\n")
    for r in rows:
        out.append(f"### {r['who']}\n")
        out.append(f"- **The tree says:** {r['treeSays']}")
        out.append(f"- **The record says:** {r['recordSays']}")
        out.append(f"- **Source:** {r['source']}\n")

out.append("\n---\n")
out.append("Full reasoning is on the site — **The Arena** and **Scilla** for the Calabrian registers,")
out.append("**The Mazza** for Piedimonte Etneo, **The Crossings** for the manifests and censuses,")
out.append("**Nudgee** for the burials.")
out.append("Where the archive has been *wrong*, that is on **Method**.\n")
out.append("https://daviddef.github.io/TheMazza/corrections/\n")
out.append(f"_Generated {datetime.date.today().strftime('%-d %B %Y')}._")

open("notes/for-michael.md", "w", encoding="utf-8").write("\n".join(out) + "\n")
print(f"for-michael.md: {len(corr)} items, {documented} documented, {len(adds)} missing people")
