#!/usr/bin/env python3
"""The ancestors the charts cannot draw.

Every chart on this site is drawn from Michael's export, so the fifty-four
people in data/documented-additions.tsv — proved by an act, absent from the
tree — cannot appear on any of them. /bloodline/ shows Domenico Donato as a
dead end while this archive knows his father, his mother, and the act that
names them.

This closes that gap without touching the export or the shared kit. For every
addition that carries an `inTree` slug, it walks UP through the additions'
own father/mother names and emits the documented chain standing above that
export person — so a page can say how much further the record reaches than the
picture does.

  site/src/data/documented-line.json
  { "<export slug>": { "anchor": "...", "up": [ {name, rel, gen, born, died,
                                                 trade, source, note}, ... ] } }
"""
import csv, json, os, re, collections

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(HERE, ".."))

rows = list(csv.DictReader(open("data/documented-additions.tsv", encoding="utf-8"), delimiter="\t"))
people = {p["slug"]: p for p in json.load(open("site/src/data/people.json", encoding="utf-8"))}
BLANK = {"", "—", "-", "?"}

def key(s):
    s = (s or "").strip().lower()
    for a, b in (("à","a"),("á","a"),("è","e"),("é","e"),("ì","i"),("í","i"),
                 ("ò","o"),("ó","o"),("ù","u"),("ú","u")):
        s = s.replace(a, b)
    return " ".join(re.sub(r"[^a-z ]", " ", s).split())

def bare(s):
    return key(re.sub(r"\s*\(.*?\)", "", s or ""))

by_name = {}
for r in rows:
    by_name.setdefault(key(r["name"]), r)
    by_name.setdefault(bare(r["name"]), r)

def walk(row, rel, depth, seen):
    """Everyone documented above this person, breadth-first, fathers then
    mothers — so the chain reads the way a pedigree does."""
    out = []
    for col, word in (("father", "father"), ("mother", "mother")):
        v = (row.get(col) or "").strip()
        if v in BLANK:
            continue
        nxt = by_name.get(key(v)) or by_name.get(bare(v))
        if not nxt or nxt["name"] in seen:
            continue
        seen.add(nxt["name"])
        label = f"{word} of {row['name']}" if depth else word
        out.append({"name": nxt["name"], "rel": label, "depth": depth + 1,
                    "gen": nxt.get("gen", ""), "born": nxt.get("born", ""),
                    "died": nxt.get("died", ""), "trade": nxt.get("trade", ""),
                    "source": nxt.get("source", ""), "note": nxt.get("note", "")})
        out += walk(nxt, word, depth + 1, seen)
    return out

out = {}
for r in rows:
    slug = (r.get("inTree") or "").strip()
    if slug in BLANK or slug not in people:
        continue
    up = walk(r, "", 0, {r["name"]})
    if up:
        out[slug] = {"anchor": r["name"], "exportName": people[slug]["name"],
                     "ancGen": people[slug].get("ancGen"), "up": up}

json.dump(out, open("site/src/data/documented-line.json", "w"), indent=1, ensure_ascii=False)
total = sum(len(v["up"]) for v in out.values())
print(f"{len(out)} anchors into the export, {total} documented ancestors above them")
for s, v in sorted(out.items(), key=lambda kv: -(kv[1]["ancGen"] or 0)):
    print(f"  {v['exportName']:24s} ({s})  +{len(v['up'])}: " +
          ", ".join(x["name"] for x in v["up"]))
