#!/usr/bin/env python3
"""One table: comune × record type × years × how much of it this archive can open.

WHY THIS EXISTS. Work-list row 37, written on 13 September: «four towns, four
record types, a hundred and fifty years, and the answers are scattered across
briatico-arks.tsv, scilla-arks.tsv, zambrone-arks.tsv, searched.tsv and my own
memory». Every sweep since has begun by re-deriving the same facts — which years
exist, which volume holds them, whether a container has been bought, whether
there is an annual index — and twice this week a search was planned around a
listing that turned out to be a quarter of the holding.

It reads the ark banks, which are the archive's own record of what it has
listed, and counts rather than asserts:

  volumes   rows in the bank for that comune and type
  bought    rows with a container, so openable without a rate-limited page load
  indexed   rows whose `tavola` column says an annual index was seen

`indexed` is only known where a bank carries that column, which today is Scilla's
restauration series alone. A blank is «not recorded», never «no index» — the
distinction the rest of this archive keeps and which a coverage table is exactly
the wrong place to lose.

  data/*-arks.tsv  ->  site/src/data/holdings.json
"""
import csv, json, os, re, collections

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(HERE, ".."))

# file, comune, the column that holds the year(s), a fondo to force.
# scilla-arks-italiano.tsv carries the numeric series id in its `serie` column
# rather than a fondo name, and a coverage table that printed «16594786» at a
# reader would be a table nobody uses twice.
BANKS = [
    ("data/scilla-arks.tsv",          "Scilla, Reggio Calabria",        "year",  None),
    ("data/scilla-arks-italiano.tsv", "Scilla, Reggio Calabria",        "year",  "italiano"),
    ("data/pe-arks.tsv",              "Piedimonte Etneo, Catania",      "year",  None),
    ("data/briatico-arks.tsv",        "Briatico, Vibo Valentia",        "years", None),
    ("data/zambrone-arks.tsv",        "Zambrone, Vibo Valentia",        "years", None),
    # Opened 21 September, off the 1872 marriage act that put Giovanni Nicotra
    # «domiciliato e residente a MASCALI». Its 46 Palermo volumes are RIVELI,
    # not civil registration, and they reach back to 1616 -- a century before
    # Piedimonte's earliest.
    ("data/mascali-arks.tsv",         "Mascali, Catania",               "year",  None),
    # The sixth town, opened 21 September off the words «nato a GIARRE» in
    # Giovanni Nicotra's 1872 publication certificate. The largest comune in
    # this archive, and the only one that holds TWO COPIES OF EVERY YEAR.
    ("data/giarre-arks.tsv",          "Giarre, Catania",                "year",  None),
    # The seventh town. Giarre's registers do not hold Giovanni Nicotra although
    # his own certificate says «nato a Giarre», and RIPOSTO registers separately
    # from 1821 -- so a man from the lower town could say Giarre and be entered
    # here. Unlike Giarre it has ORDINARY Nicotra households, not only a Don.
    ("data/riposto-arks.tsv",         "Riposto, Catania",               "year",  None),
]

# The bank files name a series in whichever column came first; normalise the
# fondo so «napoleonico» and «Stato civile napoleonico» are one row.
def fondo(v):
    v = (v or "").strip().lower()
    for key, out in (("napoleon", "napoleonico"), ("restaur", "restaurazione"),
                     ("italiano", "italiano"), ("deputazione", "deputazione del Regno"),
                     ("riveli", "deputazione del Regno")):
        if key in v:
            return out
    return v or "—"

# «Nati, esposti», «Matrimoni, processetti» and «Matrimoni» are different books
# and are kept apart; the bare type is what a searcher looks up.
def tipo(v):
    return (v or "—").strip()

def years(v):
    return [int(m) for m in re.findall(r"\b(1[6-9]\d\d|20\d\d)\b", v or "")]

rows = collections.defaultdict(lambda: {"volumes": 0, "bought": 0,
                                        "indexed": 0, "noindex": 0,
                                        "first": None, "last": None})

for path, comune, ycol, force in BANKS:
    if not os.path.exists(path):
        continue
    for r in csv.DictReader(open(path, encoding="utf-8"), delimiter="\t"):
        ser = force or r.get("serie") or r.get("fondo")
        k = (comune, fondo(ser), tipo(r.get("tipologia")))
        d = rows[k]
        d["volumes"] += 1
        if (r.get("container") or "").strip():
            d["bought"] += 1
        tav = (r.get("tavola") or "").strip()
        if tav:
            # the column is prose, so read it rather than trusting its presence
            if re.search(r"\bno\b|NO |nessun|not in the last", tav, re.I):
                d["noindex"] += 1
            else:
                d["indexed"] += 1
        for y in years(r.get(ycol)):
            d["first"] = y if d["first"] is None else min(d["first"], y)
            d["last"] = y if d["last"] is None else max(d["last"], y)

out = []
for (comune, ser, typ), d in sorted(rows.items(),
                                    key=lambda kv: (kv[0][0], kv[0][1], kv[0][2])):
    out.append({"comune": comune, "fondo": ser, "type": typ,
                "from": d["first"], "to": d["last"],
                "volumes": d["volumes"], "bought": d["bought"],
                "indexed": d["indexed"], "noindex": d["noindex"]})

tot = {"volumes": sum(r["volumes"] for r in out),
       "bought": sum(r["bought"] for r in out),
       "indexed": sum(r["indexed"] for r in out),
       "noindex": sum(r["noindex"] for r in out),
       "comuni": len({r["comune"] for r in out})}

# What Antenati has indexed BY NAME, which outranks any volume index: where it
# exists the annual Tavola does not matter. Row 135's first pass, kept here so
# the two coverage questions are answered in one place.
NAMED = [
    {"comune": "Scilla, Reggio Calabria",   "type": "Morti",  "from": 1911, "to": 1943},
    {"comune": "Pizzo, Vibo Valentia",      "type": "Nati",   "from": 1868, "to": 1903},
    {"comune": "Catania",                   "type": "Morti",  "from": 1911, "to": None},
]
NOT_NAMED = ["Piedimonte Etneo, Catania", "Briatico, Vibo Valentia",
             "Zambrone, Vibo Valentia", "San Costantino Calabro, Vibo Valentia",
             "Potenzoni (Briatico), Vibo Valentia",
             # Both opened 21 September and NEITHER is name-indexed, which is why
             # «Cassaniti» returns nothing for the whole of Italy while this
             # archive was reading the family in Piedimonte and Mascali acts.
             "Mascali, Catania", "Giarre, Catania", "Riposto, Catania"]

json.dump({"rows": out, "total": tot, "named": NAMED, "notNamed": NOT_NAMED},
          open("site/src/data/holdings.json", "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)

print(f"{tot['volumes']} volumes across {tot['comuni']} comuni — "
      f"{tot['bought']} openable now, {tot['indexed']} with an index seen, "
      f"{tot['noindex']} known to have none")
last = None
for r in out:
    if r["comune"] != last:
        print(f"  {r['comune']}")
        last = r["comune"]
    span = f"{r['from']}–{r['to']}" if r["from"] else "—"
    print(f"    {r['fondo']:22s} {r['type']:42s} {span:12s} "
          f"{r['volumes']:4d} vol  {r['bought']:4d} bought")
