#!/usr/bin/env python3
"""The whole 1913 Scilla marriage index, transcribed.

Antenati's Scilla marriage series runs 1905-1913 only. 1913 is the year the
archive could reach without spending page loads -- the volume's container was
already in hand, and IIIF images are not rate-limited the way the HTML portal
is, so all eleven index openings came down for free.

Fifty-eight marriages. The value is as much in the absences as the presences:
no Arena, no Donato, no Polistena and no Mazza married at Scilla in 1913. That
closes a search rather than opening one, which is worth writing down.
"""
import csv, json, collections

rows = list(csv.DictReader(open("data/scilla-matr-1913.tsv"), delimiter="\t"))

def surname(full):
    return full.split()[0]

names = collections.Counter()
for r in rows:
    names[surname(r["groom"])] += 1
    names[surname(r["bride"])] += 1

WANTED = ("Arena", "Donato", "Polistena", "Mazza", "Vita", "Bueti", "Sofi")
hits = {w: [r for r in rows
            if surname(r["groom"]) == w or surname(r["bride"]) == w]
        for w in WANTED}

out = {
    "year": 1913,
    "container": "5K7arD3",
    "count": len(rows),
    "rows": rows,
    "surnames": names.most_common(),
    "wanted": {w: len(v) for w, v in hits.items()},
}
json.dump(out, open("site/src/data/scilla-matr-1913.json", "w"),
          indent=1, ensure_ascii=False)

print(f"{len(rows)} marriages, {len(names)} surnames")
for w in WANTED:
    n = len(hits[w])
    print(f"  {w:12s} {n}" + ("" if n else "   -- absent"))
print("  most common:", ", ".join(f"{n} {c}" for n, c in names.most_common(8)))
