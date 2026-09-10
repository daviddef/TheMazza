#!/usr/bin/env python3
"""The Sicilian acts this archive has actually read, and the households they build."""
import csv, json, collections
rows = list(csv.DictReader(open("data/pe-mazza-acts.tsv"), delimiter="\t"))
hh = collections.defaultdict(lambda: {"children": [], "streets": set(), "ages": [], "occ": set()})
for r in rows:
    if r["kind"] != "birth":
        continue
    # The mother is written with her occupation, and a clerk may call the same
    # woman contadina one year and industriosa the next. Key on the NAMES only,
    # or one couple becomes two households.
    import re as _re
    mother_name = _re.sub(r"\s*\(.*?\)", "", r["mother"]).strip()
    key = (r["father"], mother_name)
    h = hh[key]
    h["children"].append({"name": r["subject"], "date": r["date"], "act": r["act"],
                          "year": r["year"], "ark": r["ark"], "note": r["note"]})
    if r["street"] != "—":
        h["streets"].add(r["street"])
    om = __import__("re").search(r"\((.*?)\)", r["mother"])
    if om:
        h["occ"].add(om.group(1))
    if r["fatherAge"] not in ("—", ""):
        h["ages"].append((int(r["year"]), int(r["fatherAge"])))
out = []
for (f, m), h in hh.items():
    born = [y - a for y, a in h["ages"]]
    out.append({"father": f, "mother": m,
                "occupations": sorted(h["occ"]),
                "fatherBorn": f"c. {min(born)}–{max(born)}" if born and min(born) != max(born)
                              else (f"c. {born[0]}" if born else ""),
                "streets": sorted(h["streets"]),
                "children": sorted(h["children"], key=lambda c: c["year"])})
out.sort(key=lambda h: h["fatherBorn"])
json.dump({"acts": rows, "households": out},
          open("site/src/data/sicilian-acts.json", "w"), indent=1, ensure_ascii=False)
print(f"{len(rows)} acts read, {len(out)} households reconstructed\n")
for h in out:
    print(f"  {h['father']} ({h['fatherBorn']}) x {h['mother']}")
    print(f"     {' / '.join(h['streets'])}")
    for c in h["children"]:
        print(f"     - {c['name']}, {c['date']} (act {c['act']}/{c['year']})")
