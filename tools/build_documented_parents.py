#!/usr/bin/env python3
"""The documented parents, in the shape the ancestry chart can draw.

/tree/ draws Michael's export and nothing else, so a person whose parents are
named in a register but absent from the tree ends the chart with a card reading
"Before Piedimonte Etneo, 1850". That card reports the TREE's silence and reads
as though the REGISTERS were silent. Rosario Mazza's parents have been in this
archive since his birth act was read: Mariano Mazza, thirty-six, bracciale, and
Maria Catalano, thirty-six, Piedimonte Etneo Nati 1845 atto 64.

The kit already allows for this and says so in as many words — lineage() takes
a parentsOf() from the caller and its comment reads "returning a row that is
not in the file is allowed and is the point: a parent known only as a name on a
register is still a real thing the chart should draw, and refusing it would
quietly shorten the line." So nothing in the kit changes. This emits the map
that /tree/'s own parentsOf() falls back to.

  site/src/data/documented-parents.json
  { "bySlug": { "<export slug>": {"f": "<addition name>", "m": "..."} },
    "byName": { "<addition name>": { name, born, died, birthPlace, sources,
                                     f, m, gen, trade, note } } }

Only additions carrying an `inTree` slug anchor into the export; from there the
chain walks up through the additions' own father/mother names, which is the
same resolution build_documented_line.py uses and deliberately the same rules:
an exact row name first, then the bare name without its disambiguating
parenthesis, and never a guess.
"""
import csv, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(HERE, ".."))

rows = list(csv.DictReader(open("data/documented-additions.tsv", encoding="utf-8"),
                           delimiter="\t"))
people = {p["slug"]: p for p in json.load(open("site/src/data/people.json",
                                              encoding="utf-8"))}
BLANK = {"", "—", "-", "?"}


def key(s):
    s = (s or "").strip().lower()
    for a, b in (("à", "a"), ("á", "a"), ("è", "e"), ("é", "e"), ("ì", "i"),
                 ("í", "i"), ("ò", "o"), ("ó", "o"), ("ù", "u"), ("ú", "u")):
        s = s.replace(a, b)
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", s).split())


def bare(s):
    return key(re.sub(r"\s*\(.*?\)", "", s or ""))


by_name = {}
for r in rows:
    by_name.setdefault(key(r["name"]), r)
    by_name.setdefault(bare(r["name"]), r)


def find(v):
    """A parent named on a row, resolved the way the additions file spells it.

    The parenthesis matters: «Mariano Mazza (b. c. 1809)» and «Orazio Arena
    (b. c. 1770)» are written that way precisely because the tree holds a later
    namesake, so the exact name is tried before the bare one."""
    v = (v or "").strip()
    if v in BLANK:
        return None
    return by_name.get(key(v)) or by_name.get(bare(v))


# A documented person is a scrap the chart draws but cannot link to: no slug,
# so no href, and `sources` non-empty so the chart grades them as documented
# rather than as lore.
QUALIFIED = re.compile(r"\b(before|after|by|not yet|unknown)\b", re.I)


def when(v):
    """A year the chart may print as a date.

    «c. 1809» is a date and prints as 1809. «before 29 March 1790» is a BOUND,
    and a card reading "d. 1790" for a man who was already dead by 1790 would
    be a small lie told in large type. Blank those."""
    v = (v or "").strip()
    return "" if (v in BLANK or QUALIFIED.search(v)) else v


def scrap(r):
    return {
        "__doc": True,
        # The parenthesis is a filing device, not a name. «Mariano Mazza
        # (b. c. 1809)» is written that way so no parent link can resolve to
        # the tree's later namesake; on a chart card it is noise, so the box
        # gets the plain name and the map keeps the full one as its key.
        "name": re.sub(r"\s*\(.*?\)", "", r["name"]).strip(),
        "key": r["name"],
        "born": when(r.get("born")),
        "died": when(r.get("died")),
        "birthPlace": "",
        "living": False,
        "presumedLiving": False,
        "sources": [s.strip() for s in (r.get("source") or "").split(";") if s.strip()],
        "gen": (r.get("gen") or "").strip(),
        "trade": (r.get("trade") or "").strip(),
        "note": (r.get("note") or "").strip(),
        "f": (r.get("father") or "").strip(),
        "m": (r.get("mother") or "").strip(),
    }


by_slug, out_names, seen = {}, {}, set()


def emit(r):
    """Record this addition and everyone documented above it."""
    if r["name"] in seen:
        return
    seen.add(r["name"])
    out_names[r["name"]] = scrap(r)
    for col in ("father", "mother"):
        nxt = find(r.get(col))
        if nxt:
            emit(nxt)


for r in rows:
    slug = (r.get("inTree") or "").strip()
    if slug in BLANK or slug not in people:
        continue
    f, m = find(r.get("father")), find(r.get("mother"))
    if not f and not m:
        continue
    # Only fill a gap. Where the export already gives this person parents the
    # tree wins the drawing, because the chart is a drawing of the tree and an
    # archive that silently redrew it would be lying about its own source.
    if people[slug].get("parents"):
        continue
    by_slug[slug] = {"f": f["name"] if f else None, "m": m["name"] if m else None}
    for x in (f, m):
        if x:
            emit(x)

# The scraps point at their parents by NAME; resolve those to names this file
# actually holds, and blank the ones it does not, so the chart's walk ends
# cleanly instead of on a name it cannot look up.
for v in out_names.values():
    for col in ("f", "m"):
        nxt = find(v[col])
        v[col] = nxt["name"] if nxt and nxt["name"] in out_names else None

json.dump({"bySlug": by_slug, "byName": out_names},
          open("site/src/data/documented-parents.json", "w"),
          indent=1, ensure_ascii=False)

print(f"{len(by_slug)} export people gain documented parents, "
      f"{len(out_names)} documented people drawable")
for s, v in sorted(by_slug.items()):
    print(f"  {people[s]['name']:26s} ({s})  f={v['f']}  m={v['m']}")
