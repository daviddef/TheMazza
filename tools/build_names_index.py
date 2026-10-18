#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the two files the kit's build-time name linker (kit/tools/autolink.py) reads.

    python3 ../tools/build_names_index.py            # from site/ (what `npm run names` runs)
    python3 ../tools/build_names_index.py --counts   # counts only, writes nothing

  site/.autolink/names-index.json   the names index: who a name in the prose may be linked to
  private/living.json               the living list: every living or held-out name, alias and address

BOTH ARE GENERATED AT BUILD TIME and neither is committed (both directories are gitignored). This script prints
COUNTS only, never a name.

THE INDEX comes from COMMITTED public data only: site/src/data/people.json, the file that already drives the
public pages. So a build with the private export and a build without it (GitHub Actions) make the SAME index.

  people     a name that exactly ONE person in people.json bears, who is not living (every row not flagged
             living has a published, indexable /people/<slug>/ page; a living person's page is noindex)
  ambiguous  a name that several people bear and nobody living: sent to /people/?q=<name>, the address the
             hand-typed <P n="..."/> helper already uses for a shared name, so a person the author linked by
             hand is not linked a second time
  aliases    the register-order form of a person's own name ("Arena Rocco" for Rocco Arena), built from the
             given and surname fields the page already shows; dropped where another person's name or alias is
             the same string

  Never in the index: a name of one word, a name with a digit or a bracketed note ("Rosa 1 st wife"), a name a
  living person bears (as a name or as an alias), a person who is living. "Bears" is judged on the name folded for
  case, accents, apostrophes and hyphens, so two spellings of one name are one name and are never called unique.

THE LIVING LIST is the archive's authoritative set. With the private export present it is the feed that
build_checkprose_feed.py builds (the kit's living_rule through tools/living_v2.py: every living person, every held-out
person, every published row flagged living, under every spelling the export records), plus the register-order form of
each name and the /people/ and /who/ addresses of the published living rows.

WITHOUT THE EXPORT (CI) the list is built from the committed `living` flags alone. That is what the public build itself
knows. The held-out people (undated, with a living parent) are not in people.json, so their names cannot be known
there; this script says so, in capitals, and exits 0, because the index does not depend on it: with the export, the
run FAILS (exit 1) if any index name or alias is one a living or held-out person bears, so a collision can only ever
reach CI by being introduced after a build on David's machine passed. --require-export makes the missing export a
failure.

EXIT CODES. 0 written. 1 failed (a living collision with the export present, or an empty result). 2 the export is
required (--require-export) and is not on this machine.
"""
import os
import re
import sys
import json
import argparse
import unicodedata
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "site", "src", "data")
OUT_INDEX = os.path.join(ROOT, "site", ".autolink", "names-index.json")
OUT_LIVING = os.path.join(ROOT, "private", "living.json")


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def plain(name):
    """The name as site/src/lib/people.js norm() reads it, without lower-casing: no bracketed note, straight
    apostrophes, no guillemets or double quotes, one space."""
    s = re.sub(r"\s*\(.*?\)\s*", " ", str(name or ""))
    s = s.replace("’", "'").replace("‘", "'")
    s = re.sub(r"[«»\"]", "", s)
    return " ".join(s.split())


PARTICLES = {"de", "di", "del", "della", "dei", "degli", "da", "dal", "dalla", "la", "le", "lo", "li", "van", "von",
             "der", "den", "ten", "ter", "du", "of"}


def canon(name):
    """The name as a page prints it: a word the data holds in lower case ("Mary rosa Mazza") is capitalised, except a
    particle ("de", "di", "la"). The linker matches the case it is given, so without this the prose's "Mary Rosa Mazza"
    would not match, and its last two words, "Rosa Mazza", would be linked to somebody else."""
    out = []
    for i, w in enumerate(plain(name).split(" ")):
        if w.islower() and w.isalpha() and (i == 0 or w not in PARTICLES):
            w = w[:1].upper() + w[1:]
        out.append(w)
    return " ".join(out)


def fold(name):
    """One name, folded for case, accents, apostrophes and hyphens: the key two spellings share."""
    s = unicodedata.normalize("NFKD", plain(name))
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.replace("'", "").replace("-", " ").replace("‐", " ").replace("‑", " ")
    return " ".join(s.casefold().split())


def usable(name):
    """A name the linker may ever be told about: two or more words, letters only (a digit or a stray bracket is a
    note, not a name), no placeholder."""
    s = plain(name)
    w = s.split(" ")
    if len(w) < 2 or any(not x[:1].isalpha() for x in w):
        return False
    if re.search(r"\d|[\[\]]", s) or re.search(r"\b(unknow\w*|unnamed|unnamed child|wife|husband)\b", s, re.I):
        return False
    return True


def register_order(p):
    """'Family Given' for a person whose name is exactly 'Given Family' (the form a register prints). None when the
    record does not carry both parts or the name is not simply given + surname."""
    given, sur = plain(p.get("given")), plain(p.get("surname"))
    if not given or not sur:
        return None
    if fold(p.get("name")) != fold(given + " " + sur):
        return None
    alias = canon(sur + " " + given)
    return alias if usable(alias) else None


def build_public(people):
    """(index, living, stats) from people.json alone."""
    stats = {"people rows": len(people), "rows flagged living": sum(1 for p in people if p.get("living"))}
    named = [p for p in people if p.get("slug") and usable(p.get("name"))]

    # everything any person is called, by folded key: the name, and the register-order form
    bearers = {}                                    # folded key -> set of person ids
    for p in people:
        if not p.get("slug") or not plain(p.get("name")):
            continue
        bearers.setdefault(fold(p["name"]), set()).add(p["id"])
    alias_of = {}                                   # person id -> alias text
    alias_keys = {}                                 # folded alias -> set of person ids that would own it
    for p in named:
        a = register_order(p)
        if a:
            alias_of[p["id"]] = a
            alias_keys.setdefault(fold(a), set()).add(p["id"])

    living_ids = {p["id"] for p in people if p.get("living")}
    living_keys = set()
    for p in people:
        if p.get("living"):
            living_keys.add(fold(p["name"]))
            a = register_order(p)
            if a:
                living_keys.add(fold(a))

    groups = {}                                     # folded key -> [person]
    for p in named:
        groups.setdefault(fold(p["name"]), []).append(p)

    people_rows, ambiguous_rows = [], []
    n_alias = n_alias_clash = n_living_group = 0
    for k, rows in sorted(groups.items()):
        if k in living_keys or any(p["id"] in living_ids for p in rows):
            n_living_group += 1
            continue
        # a name another person bears under a different folding is not seen by `groups` (unusable name): count it too
        if len(bearers.get(k, ())) != len(rows):
            n_living_group += 1
            continue
        if len(rows) == 1:
            p = rows[0]
            entry = {"name": canon(p["name"]), "url": "/people/%s/" % p["slug"]}
            aliases = []
            if plain(p["name"]) != entry["name"]:
                aliases.append(plain(p["name"]))                    # the spelling the data holds, so both read
            a = alias_of.get(p["id"])
            if a:
                ak = fold(a)
                clash = (bearers.get(ak, set()) - {p["id"]}) or (alias_keys.get(ak, set()) - {p["id"]}) or ak in living_keys
                if clash:
                    n_alias_clash += 1
                else:
                    aliases.append(a)
                    n_alias += 1
            if aliases:
                entry["aliases"] = aliases
            people_rows.append(entry)
        else:
            # the several: one address per distinct spelling (the linker matches the case it is given)
            # one address per case-folded spelling; the spellings that differ only in case share it
            canons = {}
            for p in rows:
                canons.setdefault(canon(p["name"]).casefold(), canon(p["name"]))
            raws = {plain(p["name"]) for p in rows} | set(canons.values())
            for r in sorted(raws):
                best = canons[r.casefold()]
                ambiguous_rows.append({"name": r, "url": "/people/?q=" + quote(best)})
            # the register-order form for the several is skipped: it would need the same care for each bearer
    index = {"people": people_rows, "ambiguous": ambiguous_rows}
    stats.update({"index people": len(people_rows), "index ambiguous": len(ambiguous_rows),
                  "index aliases": n_alias, "aliases dropped (another person's name or alias)": n_alias_clash,
                  "names left out (a living person bears them, or the data disagrees)": n_living_group})

    living_terms, living_urls = set(), set()
    for p in people:
        if not p.get("living"):
            continue
        living_terms.add(plain(p["name"]))
        a = register_order(p)
        if a:
            living_terms.add(a)
        if p.get("slug"):
            living_urls.add("/people/%s/" % p["slug"])
            living_urls.add("/who/%s/" % slugify(p["name"]))
    return index, {"names": living_terms, "urls": living_urls}, stats


def slugify(s):
    s = unicodedata.normalize("NFD", str(s)).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()


def quote(s):
    from urllib.parse import quote as q
    return q(s, safe="")


def write_json(path, obj, private=False):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600 if private else 0o644)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, sort_keys=False, indent=0 if private else 1)
        f.write("\n")
    os.chmod(path, 0o600 if private else 0o644)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--gedcom")
    ap.add_argument("--index", default=OUT_INDEX)
    ap.add_argument("--living", default=OUT_LIVING)
    ap.add_argument("--counts", action="store_true", help="print counts, write nothing")
    ap.add_argument("--require-export", action="store_true",
                    help="a run without the private export (nobody can name the held-out people) fails")
    a = ap.parse_args(argv)

    with open(os.path.join(DATA, "people.json"), encoding="utf-8") as f:
        people = json.load(f)
    index, living, stats = build_public(people)

    fb = load_module(os.path.join(HERE, "build_checkprose_feed.py"), "build_checkprose_feed")
    feed, why = fb.build(a.gedcom)
    export = feed is not None
    if export:
        extra = set()
        for x in feed["living"]:
            for n in x["names"]:
                extra.add(plain(n))
                parts = plain(n).split(" ")
                if len(parts) >= 2:
                    extra.add(" ".join([parts[-1]] + parts[:-1]))       # the register-order form of the same name
        living["names"] |= extra
        stats["living terms (public rows + export + held out)"] = len(living["names"])
        keys = {fold(n) for n in living["names"]}
        hits = 0
        for row in index["people"]:
            if fold(row["name"]) in keys or any(fold(x) in keys for x in row.get("aliases", [])):
                hits += 1
        for row in index["ambiguous"]:
            if fold(row["name"]) in keys:
                hits += 1
        stats["index entries a living or held-out person also bears"] = hits
    else:
        stats["living terms (public rows only)"] = len(living["names"])
        hits = 0

    for k, v in stats.items():
        print("  %-66s %d" % (k, v))
    if hits:
        print("names: FAIL, %d index entr%s a living or held-out person also bears. The index is faulty; "
              "nothing was written." % (hits, "y is one" if hits == 1 else "ies are ones"))
        return 1
    if not index["people"]:
        print("names: FAIL, the index is empty")
        return 1
    if not export:
        msg = ("names: the private export is not on this machine (%s). The living list holds the published living rows "
               "only; the held-out people and the export's other spellings were NOT checked against the index. "
               "The index itself comes from committed data and is the same one a build with the export makes." % why)
        if a.require_export:
            print(msg)
            return 2
        print(msg.upper() if os.environ.get("CI") else msg)
    if a.counts:
        return 0
    write_json(a.index, index)
    write_json(a.living, {"names": sorted(living["names"]), "urls": sorted(living["urls"])}, private=True)
    print("names: wrote the index (%d people, %d ambiguous) and the living list (%d terms, %d addresses; names inside, "
          "not for commit)" % (len(index["people"]), len(index["ambiguous"]), len(living["names"]), len(living["urls"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
