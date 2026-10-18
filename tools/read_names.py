#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""People who were READ from a register act and are in no family file: the data layer for their /who/ name pages.

WHY THIS EXISTS. On 18 October 2026 David looked at https://mazza.defranceski.com/scilla/ and said there were still
"loads of names with no links ("Bruno", "Donato", ...)". The names he meant are people the registers name and the
family file never held: the mother of Michele Donato, a sindaco, the witnesses to an act. They are in
data/scilla-reads.tsv (and the other act tables), they have no /people/ page, and /who/ listed only people.json.
So the linker had nothing to link to.

THE MODEL. data/read-names.tsv is one row per (name, act): a person-name, the act it was read in, the role it
was read in, and `from`, the row of the archive's own data that says so. A /who/<name>/ page is made for each
DISTINCT NAME, listing every act the name was read in. A /who/ page is a name page: it never says two acts are one
man, and the estate's oldest rule (never merge on a name alone) is kept by saying so on the page. Nobody here is
given a /people/ page, a date or a family: name, role, record.

WHO MAY BE ON IT. Only a person the archive's own living rule (kit living_rule, through tools/living_v2.py) says is
not living, from a birth year this module can SHOW from the act: the year of the act minus the age the act gives,
else minus 14 (nobody is a parent, a spouse or a witness younger); a child named in a birth act is born that year;
a person named in a death act has a recorded death. Anyone the rule cannot show to be dead is left out and
counted. Acts after 1930 are not accepted at all. A name that anyone in people.json bears (a living person
included) already has a page, or is held out, and is left out: this file adds pages, it does not add bearers to
somebody else's.

  python3 ../tools/read_names.py            from site/ (what `npm run readnames` runs): writes site/src/data/read-names.json
  python3 ../tools/read_names.py --counts   prints the counts and what was left out (never a name), writes nothing
"""
import csv
import importlib.util
import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
TSV = os.environ.get("READ_NAMES_TSV") or os.path.join(ROOT, "data", "read-names.tsv")   # the env var is for the gate's self-test
DATA = os.path.join(ROOT, "site", "src", "data")
LAST_YEAR = 1930                                      # an act after this is never accepted
AS = {"child", "deceased", "groom", "bride", "parent", "witness", "official", "declarant", "other"}
KINDS = {"Nati", "Matrimoni", "Morti", "Pubblicazioni", "Processetti", "Tavola", "Indice"}
PAGES = {                                             # narrative page -> how a sentence names it ("Discussed on the Scilla page")
    "/scilla/": "the Scilla page", "/crossings/": "the Crossings page", "/briatico/": "the Briatico page",
    "/mazza/": "the Mazza page", "/giarre/": "the Giarre page", "/queensland/": "the Queensland Register page",
    "/mascali/": "the Mascali page", "/nicotra/": "the Nicotra page", "/register-1879/": "the Sicilian Registers page",
    "/the-name-line/": "the Mazza Name Line page", "/riposto/": "the Riposto page", "/piedimonte-etneo/": "the Piedimonte Etneo page",
}
PARTICLES = {"de", "di", "del", "della", "dei", "da", "la", "le", "lo", "li"}


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def fold(name):
    s = unicodedata.normalize("NFKD", " ".join(str(name or "").split()))
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.replace("'", "").replace("’", "").replace("‘", "").replace("-", " ").replace("‐", " ").replace("‑", " ")
    return " ".join(s.casefold().split())


def slugify(s):
    s = unicodedata.normalize("NFD", str(s)).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()


def good_name(n):
    """Two to four words, each a capitalised word, or a particle between them."""
    ws = n.split(" ")
    if len(ws) < 2 or len(ws) > 4:
        return False
    for i, w in enumerate(ws):
        if w.lower() in PARTICLES and 0 < i < len(ws) - 1:
            continue
        if not re.match(r"^[A-ZÀ-Þ][A-Za-zÀ-ÿ'’`]*$", w):
            return False
    return True


def rows():
    """The TSV, comment lines (#) skipped. Each row gets `_line` for messages."""
    out = []
    with open(TSV, encoding="utf-8") as f:
        text = [ln for ln in f.read().split("\n")]
    header = None
    for i, ln in enumerate(text, 1):
        if not ln.strip() or ln.startswith("#"):
            continue
        cells = ln.split("\t")
        if header is None:
            header = cells
            continue
        cells += [""] * (len(header) - len(cells))
        r = dict(zip(header, cells))
        r["_line"] = i
        out.append(r)
    return out


def known_arks():
    reg = os.path.join(DATA, "records.json")
    if not os.path.exists(reg):
        return None
    return set(json.load(open(reg, encoding="utf-8"))["ark"])


def citation(r):
    if r.get("cite"):
        return r["cite"]
    s = "%s, %s %s" % (r["comune"], r["kind"], r["year"])
    no = (r.get("no") or "").strip()
    if re.fullmatch(r"\d+", no):
        s += ", atto " + no
    elif no:
        s += ", " + no
    return s


def birth_year(r):
    """(birth year the act lets us SHOW, dead_recorded). The latest the person can have been born."""
    year = int(r["year"])
    if r["as"] == "deceased":
        return None, True
    if r["as"] == "child":
        return year, False
    if (r.get("age") or "").strip().isdigit():
        return year - int(r["age"]), False
    return year - 14, False


def build(verbose=True):
    """-> (doc, problems, stats). doc is what site/src/data/read-names.json holds."""
    nb = load_module(os.path.join(HERE, "build_names_index.py"), "build_names_index")
    LV = load_module(os.path.join(HERE, "living_v2.py"), "living_v2")
    lr = LV.lr
    people = json.load(open(os.path.join(DATA, "people.json"), encoding="utf-8"))
    arks = known_arks()
    problems = []
    stats = {}

    # everything people.json already calls anyone, as a name and as a slug
    bear_fold, bear_slug = set(), set()
    for p in people:
        if p.get("name"):
            bear_fold.add(fold(nb.plain(p["name"])))
            bear_slug.add(slugify(p["name"]))
            ro = nb.register_order(p)
            if ro:
                bear_fold.add(fold(ro))
    living_fold = set()
    for p in people:
        if p.get("living"):
            living_fold.add(fold(nb.plain(p["name"])))
    # the private export's living and held-out names, when this machine has it (never in CI)
    fb = load_module(os.path.join(HERE, "build_checkprose_feed.py"), "build_checkprose_feed")
    feed, why = fb.build(None)
    export = feed is not None
    if export:
        for x in feed["living"]:
            for n in x["names"]:
                living_fold.add(fold(nb.plain(n)))
                parts = nb.plain(n).split(" ")
                if len(parts) >= 2:
                    living_fold.add(fold(" ".join([parts[-1]] + parts[:-1])))
    stats["private export read (living and held-out names)"] = 1 if export else 0

    data = rows()
    stats["rows"] = len(data)
    today = lr.this_year()
    keep, left_out = [], {"a name people.json already bears": 0, "a name a living or held-out person bears": 0,
                          "not shown dead by the living rule": 0, "an act after %d" % LAST_YEAR: 0}
    for r in data:
        where = "read-names.tsv line %d" % r["_line"]
        for col in ("name", "as", "role", "comune", "kind", "year", "from"):
            if not (r.get(col) or "").strip():
                problems.append("%s: «%s» is empty" % (where, col))
        if problems and problems[-1].startswith(where):
            continue
        name = " ".join(r["name"].split())
        if not good_name(name):
            problems.append("%s: «name» is not a person's name of two to four capitalised words" % where)
            continue
        if r["as"] not in AS:
            problems.append("%s: «as» %s is not one of %s" % (where, r["as"], ", ".join(sorted(AS))))
            continue
        if r["kind"] not in KINDS:
            problems.append("%s: «kind» %s is not one of %s" % (where, r["kind"], ", ".join(sorted(KINDS))))
            continue
        if not re.fullmatch(r"\d{4}", r["year"]):
            problems.append("%s: «year» is not a year" % where)
            continue
        if r["page"] and r["page"].split("#")[0] not in PAGES:
            problems.append("%s: «page» %s is not one of the narrative pages" % (where, r["page"]))
            continue
        if (r.get("age") or "").strip() and not r["age"].strip().isdigit():
            problems.append("%s: «age» is not a number" % where)
            continue
        for a in re.findall(r"\ban_ua\d+\b", r.get("ark") or ""):
            if arks is not None and a not in arks:
                problems.append("%s: ark %s is in none of the archive's ark tables" % (where, a))
        if (r.get("ark") or "").strip() and not re.fullmatch(r"an_ua\d+", r["ark"].strip()):
            problems.append("%s: «ark» must be one Antenati ark (an_ua...) or empty" % where)
            continue
        form = " ".join((r.get("form") or "").split())
        if form and not good_name(form):
            problems.append("%s: «form» is not a name" % where)
            continue
        if int(r["year"]) > LAST_YEAR:
            left_out["an act after %d" % LAST_YEAR] += 1
            continue
        by, dead = birth_year(r)
        pid = "r%d" % r["_line"]
        living, held = LV.classify({pid: {"by": by, "dead": dead, "cites": [], "parents": []}}, today)
        if pid in living or pid in held:
            left_out["not shown dead by the living rule"] += 1
            continue
        if by is not None and today - by <= lr.LIVING_YEARS:
            left_out["not shown dead by the living rule"] += 1
            continue
        keys = {fold(name)} | ({fold(form)} if form else set())
        if any(k in living_fold for k in keys):
            left_out["a name a living or held-out person bears"] += 1
            continue
        if fold(name) in bear_fold or slugify(name) in bear_slug or (form and fold(form) in bear_fold):
            left_out["a name people.json already bears"] += 1
            continue
        r["name"], r["form"] = name, form
        keep.append(r)
    stats.update({"left out: " + k: v for k, v in left_out.items()})
    if problems:
        return None, problems, stats

    # THE TEXT BESIDE A NAME. A record says whom the act is about ("mother of Giovanni Polistena (the child)"). If that
    # name is also borne by somebody living, the page would name a living person's name beside an act of 1883, so the
    # name is withheld there and the role says only what it can. Counted, never printed.
    def names_in(text):
        w = re.findall(r"[A-ZÀ-Þ][A-Za-zÀ-ÿ'’`-]*", text or "")
        for n in (2, 3, 4):
            for i in range(len(w) - n + 1):
                yield fold(" ".join(w[i:i + n]))
    withheld = 0
    for r in keep:
        if any(k in living_fold for k in names_in(r.get("of"))):
            r["of"] = "the act" if r["role"].rstrip().endswith(" to") else "the person the act concerns"
            withheld += 1
    stats["records whose text named somebody who shares a living person's name (withheld)"] = withheld
    by_name = {}
    for r in keep:
        k = fold(r["name"])
        e = by_name.setdefault(k, {"name": r["name"], "forms": [], "records": []})
        if r["form"] and r["form"] not in e["forms"]:
            e["forms"].append(r["form"])
        e["records"].append({
            "as": r["as"], "role": r["role"].strip(), "of": (r.get("of") or "").strip(),
            "comune": r["comune"], "kind": r["kind"], "year": r["year"], "no": (r.get("no") or "").strip(),
            "act": citation(r), "ark": (r.get("ark") or "").strip(), "age": (r.get("age") or "").strip(),
            "trade": (r.get("trade") or "").strip(), "page": (r.get("page") or "").strip(),
        })
    names = []
    taken_alias = set(by_name)
    n_alias, n_alias_dropped = 0, 0
    for k, e in sorted(by_name.items(), key=lambda kv: slugify(kv[1]["name"])):
        aliases = []
        for f in e["forms"]:
            fk = fold(f)
            if fk == k or fk in taken_alias or fk in bear_fold or fk in living_fold:
                n_alias_dropped += 1
                continue
            taken_alias.add(fk)
            aliases.append(f)
            n_alias += 1
        e["records"].sort(key=lambda x: (int(x["year"]), x["kind"], x["no"]))
        names.append({"name": e["name"], "slug": slugify(e["name"]), "aliases": aliases, "records": e["records"]})
    slugs = [n["slug"] for n in names]
    if len(slugs) != len(set(slugs)):
        problems.append("two read names make one /who/ address")
        return None, problems, stats
    stats["distinct names (one /who/ page each)"] = len(names)
    stats["records (a name in an act)"] = sum(len(n["records"]) for n in names)
    stats["register-order aliases kept"] = n_alias
    stats["register-order aliases dropped (another name or alias is the same)"] = n_alias_dropped
    doc = {"_why": ["Written by tools/build_read_names.py from data/read-names.tsv. People READ from a register act who are in no "
                    "family file: one /who/ name page each. Name, role, record; never a date, a family or a /people/ page."],
           "pages": PAGES, "names": names}
    return doc, problems, stats


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    doc, problems, stats = build()
    for k, v in stats.items():
        print("  %-72s %d" % (k, v))
    if problems:
        for p in problems[:40]:
            print("  FAIL  " + p)
        if len(problems) > 40:
            print("  ... and %d more" % (len(problems) - 40))
        return 1
    if "--counts" in argv:
        return 0
    out = os.path.join(DATA, "read-names.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("read-names: %d name page(s) from %d record(s) written to site/src/data/read-names.json"
          % (len(doc["names"]), sum(len(n["records"]) for n in doc["names"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
