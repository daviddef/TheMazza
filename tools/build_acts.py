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
# The plates and the parent couple are part of this dataset, not a later
# afterthought — an earlier version wrote them in a separate step and this
# script silently deleted them on the next run.
PLATES = {
 "act164-mazza-antonino.jpg": "Act 164, 1877 — the birth of Antonino Mazza to Pasquale Mazza, 48, and Concetta Greco, of via Cappello Campagna",
 "act168-mazza-orazio.jpg": "Act 168, 1877 — the birth of Orazio Mazza to Rosario Mazza, 31, and Leonarda",
 "act168-rosario-lower.jpg": "Act 168 continued — via Grotta Nicodemo, and the 1927 marriage annotation",
 "act167-mazza-rosaria.jpg": "Act 167, 1879 — the birth of Rosaria Mazza, Via Terremorte",
 "act205-mazza-venerio.jpg": "Act 205, 1879 — the birth of Venerio Mazza to Salvatore Mazza, 34, and Concetta Sciacca",
 "act66-mazza-gaetano.jpg": "Act 66, 1880 — the birth of Gaetano Mazza to Rosario Mazza, 32, Via S. Basile",
 "act3-salvatore-mazza.jpg": "Act 3, 1873 — THE BIRTH OF SALVATORE MAZZA, 5 January 1873, Contrada Terremorte, to «Rosario Mazza di Mariano», 28, and Leonarda Bonanno di Gaetano",
 "matr1876-act5-mazza-sciacca.jpg": "Marriage act 5, 16 January 1876 — Salvatore Mazza, son of Innocenzio and Domenica Cavallaro, marries Concetta Sciacca",
 "matr1874-act26-mazza-raiti.jpg": "Marriage act 26, 19 July 1874 — Antonino Mazza, «figlio d'Innocenzio… e di Domenica Cavallaro», marries Rosa Raiti",
 "matr1876-act5-father-detail.jpg": "Act 5 of 1876, magnified: «…o di Senzio…» — the contraction of Innocenzio that this archive first misread as Venerio",
 "act34-nicotra-maria-1875.jpg": "Act 34, 1875 — a Maria Nicotra of Piedimonte Etneo, daughter of Alfio Nicotra and Angela Previtera. NOT Salvatore's wife; a different woman of the same name.",
}
PARENTS = {
 "father": "Innocenzio Mazza", "mother": "Domenica Cavallaro",
 "sons": [
   {"name": "Salvatore Mazza", "born": "c. 1841", "age": "34 in January 1876",
    "wife": "Concetta Sciacca", "act": "Matrimoni 1876, atto 5"},
   {"name": "Antonino Mazza", "born": "c. 1843", "age": "31 in July 1874",
    "wife": "Rosa Raiti", "act": "Matrimoni 1874, atto 26"}],
}
import os as _os
plates = [{"f": k, "t": v} for k, v in PLATES.items()
          if _os.path.exists("site/public/plates/" + k)]
json.dump({"acts": rows, "households": out, "plates": plates, "parents": PARENTS},
          open("site/src/data/sicilian-acts.json", "w"), indent=1, ensure_ascii=False)
print(f"{len(plates)} plates")
print(f"{len(rows)} acts read, {len(out)} households reconstructed\n")
for h in out:
    print(f"  {h['father']} ({h['fatherBorn']}) x {h['mother']}")
    print(f"     {' / '.join(h['streets'])}")
    for c in h["children"]:
        print(f"     - {c['name']}, {c['date']} (act {c['act']}/{c['year']})")
