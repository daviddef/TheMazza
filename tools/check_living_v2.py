#!/usr/bin/env python3
"""The living-people gate, version 2 (David, 16 October 2026): the estate standard.

WHAT IT ENFORCES (and why each part can fail)

  A living person is named, with their relationships and their town and country,
  and nothing more. A possible minor is not published at all. A named person has
  a page. This reads the COMMITTED data and the BUILT output, which is what the
  public gets, and it decides who is living with the kit's `living_rule.py`, not
  with anything the generator computed.

  1  an empty build is refused            (no pages, no people, nobody living,
                                           no ordinary page to compare against)
  2  nobody is published as dead who the rule makes living
                                          (a non-living record with a birth year
                                           80 years ago or less, no death, no
                                           public source). With the private
                                           GEDCOM present (locally, never in CI)
                                           the whole classification is recomputed
                                           from the GEDCOM and compared, both ways
  3  a living record shows only name, relationships and town and country
                                          (any other field set on a row flagged
                                           living, in ANY data file; no year, no
                                           digit and no institution in the place)
  4  a living person's page is noindex, is not in the sitemap or the search index,
     has no Person (or any) JSON-LD, no table, no image, and no year of their own;
     a name page whose every bearer is living is noindex and names no canonical
  5  a held-out person appears nowhere: not by id in any data file, not as a page,
     not by name in a built page or data file (the name test needs the GEDCOM, so
     it runs locally; the id test runs everywhere). Held out is ONLY an undated
     person with a living parent; a child with a known birth year is published.
  6  every person the archive names has a page (each relationship edge resolves to
     a record, and each record has a built page)
  7  NO BIRTH YEAR OF A PERSON WITH NO DEATH IS PUBLISHED ANYWHERE (25 October 2026):
     not in any data row, built page or data file, whatever the row's `living` flag
     says (rule7_years). It also refuses a row that names a living person by slug or
     id and carries a life field, flagged living or not.

  RULE 2 AND PUBLIC SOURCES. The kit's `living_rule.is_living` lets any public-source
  citation (the NAA passenger index, FamilySearch...) make a person 80 or younger "not
  living". A man born in 1948 with no death was published as dead, with his year, parents,
  spouse and children, on exactly that. This gate therefore does NOT pass citations to the
  kit's rule for anyone with a birth year: year and absence of death decide, alone. (Kit gap,
  reported: the exemption belongs in the kit's rule, not in each archive.)

  POSITIVE CONTROLS. A check that can only pass proves nothing, so the gate also
  proves the opposite on ordinary pages: a non-living person's page is indexable,
  is in the sitemap and carries JSON-LD. If none of those hold, rule 4 is passing
  because everything is noindex, and that fails.

  `--selftest` plants one fault per rule in a COPY of the build and requires the
  gate to catch each, so a gate that has quietly stopped looking cannot pass.

  Planted values are ones no living person can have (the year 1799, a street
  number). No real person's value is written in this file.
"""
import argparse
import json
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import living_v2 as LV  # noqa: E402
lr = LV.lr
sys.path.insert(0, LV.KIT_TOOLS)
import outdir as _outdir  # noqa: E402

PLANT_YEAR = 1799                       # no living person can have this
CHILD_AGE = 18                          # a child is under 18 by year (estate standard)
YEAR = re.compile(r"\b(1[5-9]\d\d|20\d\d)\b")
NOINDEX = re.compile(r'<meta[^>]+name=["\']robots["\'][^>]*noindex', re.I)
LDJSON = re.compile(r'application/ld\+json', re.I)
CANON = re.compile(r'<link[^>]+rel=["\']canonical["\'][^>]*href=["\']([^"\']+)', re.I)

# What a row flagged living may carry. Anything else, set, is a leak.
ALLOWED_KEYS = {"id", "slug", "name", "given", "surname", "sex", "living", "comp",
                "birthPlace", "parents", "children", "spouses", "siblings",
                # derived rows (spine, ancestors, components...) carry these as
                # presentation, never as data about the person:
                "gen", "href", "via", "n", "fromRegister",
                # a living person's spouse is a relationship:
                "spouse", "spouseSlug", "spouseNote"}
# Keys that are about the person's life. Set on a living row, they fail.
FORBIDDEN_KEYS = {"born", "died", "bornText", "diedText", "events", "sources",
                  "records", "corrections", "photos", "photoSize", "deathPlace",
                  "burialPlace", "trade", "registerNote", "registerSources",
                  "onSpine", "ancGen", "datesHidden", "presumedLiving", "note",
                  "bornNote", "birth", "death", "dates", "reach", "spouseBorn",
                  "married", "alt"}
# THE FAMILY STORY (site/src/data/story.json, kit/docs/story.md) draws the living as a ribbon card and a tree node, and the
# kit's contract gives those a few presentation fields: where the card's chapter is, which outline the card's origin takes,
# the town written as "of Brisbane", a link to the person's own page (which exists, with no dates), and «minor», which makes
# the kit show initials only. None of them is about the person's life. They are allowed in that one file and nowhere else;
# «years» and «atYear» are NOT among them, so a date on a living card still fails here, and every string is still read for a
# year below. kit/tools/checkfamilystory.py (npm run check:story) holds the same rows to the living rule a second time.
STORY_KEYS = {"origin", "originGrade", "spouseOrigin", "atPlace", "chapter", "person", "spousePerson", "spouseLiving",
              "title", "minor"}


def jload(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def rows_in(obj):
    """Every dict anywhere in a parsed JSON document."""
    stack = [obj]
    while stack:
        o = stack.pop()
        if isinstance(o, dict):
            yield o
            stack.extend(o.values())
        elif isinstance(o, list):
            stack.extend(o)


def strip_chart_and_footer(html):
    """The page minus what legitimately shows other people's years."""
    h = re.sub(r"(?is)<script.*?</script>|<style.*?</style>", " ", html)
    h = re.sub(r"(?is)<footer.*?</footer>", " ", h)
    h = re.sub(r'(?is)<figure class="ptree".*?</figure>', " ", h)
    # the namesake list names OTHER people and their dates
    h = re.sub(r'(?is)<section class="blk">\s*<h2[^>]*>Others of the same name.*?</section>', " ", h)
    return h


class Gate:
    def __init__(self, dist, data_dir, root, ged=None, today=None, min_pages=300):
        self.dist, self.data, self.root, self.ged = dist, data_dir, root, ged
        self.today = today or lr.this_year()
        self.min_pages = min_pages
        self.fails = []
        self.info = {}

    def fail(self, rule, msg):
        self.fails.append((rule, msg))

    # ---------------------------------------------------------------- loading
    def load(self):
        self.people = jload(os.path.join(self.data, "people.json"))
        self.by_slug = {p["slug"]: p for p in self.people}
        self.by_id = {p["id"]: p for p in self.people}
        self.living = [p for p in self.people if p.get("living")]
        self.dead = [p for p in self.people if not p.get("living")]
        hp = os.path.join(self.root, "data", "held-out.json")
        self.held = jload(hp) if os.path.exists(hp) else {"ids": []}
        self.held_ids = set(self.held.get("ids", []))
        self.pages = {}
        if os.path.isdir(self.dist):
            for dp, _, fns in os.walk(self.dist):
                for fn in fns:
                    if fn == "index.html":
                        rel = os.path.relpath(dp, self.dist).replace(os.sep, "/")
                        self.pages["" if rel == "." else rel] = os.path.join(dp, fn)

    def page(self, rel):
        p = self.pages.get(rel)
        return open(p, encoding="utf-8", errors="replace").read() if p else None

    # ----------------------------------------------------------------- rule 1
    def rule1_empty(self):
        n = len(self.pages)
        if n < self.min_pages:
            self.fail(1, f"only {n} built page(s) under {self.dist} (need at least {self.min_pages}): "
                         "the build is empty or unfinished, and a gate that saw nothing passes nothing")
        if not self.people:
            self.fail(1, "people.json holds nobody")
        if not self.living:
            self.fail(1, "nobody is flagged living in people.json: either the archive holds no living "
                         "person, which is not true of this one, or the flag has stopped being written")
        if not self.dead:
            self.fail(1, "nobody is flagged as not living")
        sm = os.path.join(self.dist, "sitemap.xml")
        if not os.path.exists(sm):
            self.fail(1, "no sitemap.xml in the build, so 'not in the sitemap' cannot be shown")
        self.info["pages"] = n

    # ----------------------------------------------------------------- rule 2
    def cites_of(self, p):
        c = list(p.get("sources") or [])
        c += [r.get("what", "") for r in (p.get("records") or [])]
        c += list(p.get("registerSources") or [])
        return LV.with_addresses(c)

    def dead_recorded(self, p):
        if p.get("died"):
            return True
        return any(e.get("what") in ("died", "buried") or e.get("tag") in ("DEAT", "BURI")
                   for e in (p.get("events") or []))

    def rule2_classification(self):
        # (i) nobody published as not living who the rule makes living
        bad = []
        # an undated parent is living when their youngest child with a known birth year is 60 or less
        # (17 October 2026). A living child's year is not published, so this half sees only the children
        # whose year is; the GEDCOM half below sees them all.
        kid_year = {}
        for q in self.people:
            if q.get("born"):
                for e in (q.get("parents") or []):
                    kid_year[e.get("id")] = max(kid_year.get(e.get("id"), 0), q["born"])
        for p in self.dead:
            # a dated person is judged without their citations (see the header: public sources)
            if lr.is_living(p.get("born"), self.dead_recorded(p),
                            [] if p.get("born") else self.cites_of(p), self.today,
                            kid_year.get(p["id"])):
                bad.append(p["id"])
        if bad:
            self.fail(2, f"{len(bad)} person(s) are published as not living but the rule makes them "
                         f"living (80 or younger by year, no death, no public source): ids {bad[:6]}")
        self.info["published_as_dead_but_living_by_rule"] = len(bad)
        # (ii) with the private GEDCOM, recompute the whole classification
        if not self.ged or not os.path.exists(self.ged):
            self.info["ged"] = "absent (the GEDCOM is private; this half runs locally only)"
            return
        sys.path.insert(0, HERE)
        from ged import parse, kid, kids, val   # the parser, not the generator
        R = parse(self.ged)
        I = {x: v for x, v in R.items() if v["tag"] == "INDI"}
        F = {x: v for x, v in R.items() if v["tag"] == "FAM"}
        yr = lambda s: (lambda m: int(m.group(1)) if m else None)(re.search(r"\b(1[5-9]\d\d|20\d\d)\b", s or ""))

        def by_of(x):
            for t in ("BIRT", "CHR", "BAPM"):
                e = kid(I[x], t)
                if e and yr(val(e, "DATE")):
                    return yr(val(e, "DATE"))
            return None

        def titles(x):
            out = []
            for s in kids(I[x], "SOUR"):
                ref = s["val"]
                if ref in R:
                    t = kid(R[ref], "TITL")
                    out.append(t["val"] if t else ref)
                elif s["val"]:
                    out.append(s["val"])
            return out

        def name_key(x):
            n = kid(I[x], "NAME")
            return re.sub(r"[^a-z]", "", (n["val"] if n else "").lower())

        twins = {}
        for x in I:
            twins.setdefault(name_key(x), []).append(x)
        ev = LV.evidence()

        def parents_of(x):
            out = []
            fc = kid(I[x], "FAMC")
            if fc and fc["val"] in F:
                for r in ("HUSB", "WIFE"):
                    out += [h["val"] for h in kids(F[fc["val"]], r) if h["val"] in I]
            return out

        def death_kind(x):
            # re-derived here from the kit's own death_kind, not from the generator's helper: a DEAT with a
            # date, a place, an age or a source, or any BURI, is a record; a bare `DEAT Y` is a flag
            d = kid(I[x], "DEAT")
            return lr.death_kind(
                died=val(d, "DATE") if d else None,
                death_place=val(d, "PLAC") if d else None,
                dead_flag=d is not None,
                death_recorded=bool(kid(I[x], "BURI") or (d and (kid(d, "AGE") or kid(d, "SOUR")))))

        slug_of = {p["id"]: p["slug"] for p in self.people}
        info = {}
        for x in I:
            sl = slug_of.get(x)
            dk = death_kind(x)
            info[x] = {"by": by_of(x),
                       "dead": dk == "record" or (sl in ev["dead"]),
                       "flag": dk == "flag",
                       "cites": titles(x) + ev["cites"].get(sl, []), "parents": parents_of(x)}
        # the youngest child with a known birth year, from the export's own family records (17 October 2026)
        young = {}
        for x, i in info.items():
            if i["by"] is not None:
                for q in i["parents"]:
                    young[q] = max(young.get(q, 0), i["by"])
        living_now = {x for x, i in info.items()
                      if lr.is_living(i["by"], i["dead"], [] if i["by"] is not None else i["cites"],
                                      self.today, young.get(x), undated_dead=i["flag"])}
        held_now = set()
        for x, i in info.items():
            pl = any(q in living_now for q in i["parents"])
            if lr.is_held_out(x, i["by"], i["dead"], i["cites"], pl, (), self.today, young.get(x),
                              undated_dead=i["flag"]):
                held_now.add(x)
        self.recent_parent_ids = sorted(x for x in living_now if info[x]["by"] is None)
        self.no_twin = {x for x in I if len(twins.get(name_key(x), [])) == 1}
        exempt = mism = 0
        for p in self.people:
            x = p["id"]
            if x not in I:
                continue                      # a register person: not in the GEDCOM
            want = x in living_now
            if want != bool(p.get("living")):
                # A merged duplicate may carry the death or the year, so a name twin explains a
                # mismatch, but only where the published record SHOWS the explanation: a death, or a
                # birth year more than 80 years ago. A twin with neither is not an explanation (a
                # blanket exemption is how a man born in 1948 was published as dead).
                explained = self.dead_recorded(p) or (p.get("born") and self.today - int(p["born"]) > lr.LIVING_YEARS)
                if len(twins.get(name_key(x), [])) > 1 and (explained or not want):
                    exempt += 1
                else:
                    mism += 1
                    self.fail(2, f"{x}: the rule says living={want}, the data says {bool(p.get('living'))}")
        # A CHILD WITH A KNOWN BIRTH YEAR IS NOT HELD OUT (David, 16 October 2026): every
        # child under 18 by year follows the same standard as any living person, so is
        # published with a page. Only an undated person with a living parent is held out.
        kids = {x for x in living_now if info[x]["by"] and self.today - info[x]["by"] < CHILD_AGE}
        self.child_ids = sorted(kids)
        for x in sorted(kids):
            if x not in self.by_id:
                self.fail(6, f"{x} is a dated child (under 18 by year) with no record: a known child "
                             "is published like any living person, not held out")
            elif not self.by_id[x].get("living"):
                self.fail(2, f"{x} is a dated child but is not flagged living")
        for x in sorted(self.held_ids - held_now):
            self.fail(5, f"{x} is recorded as held out but the rule publishes them "
                         "(held out is only an undated person with a living parent)")
        undated_held = [x for x in held_now if not info[x]["by"]]
        if len(undated_held) != len(held_now):
            self.fail(5, "a person with a birth year is held out by the rule: only the undated are")
        self.info["dated_children_published"] = len([x for x in kids if x in self.by_id])
        rp = [x for x in self.recent_parent_ids if x in self.by_id]
        self.info["undated_parents_living_by_recent_child"] = len(rp)
        for x in rp:
            if not self.by_id[x].get("living"):
                self.fail(2, f"{x} is an undated parent of a child born 60 years ago or less, so living "
                             "by the rule, but is published as not living")
            if x in self.held_ids:
                self.fail(5, f"{x} is an undated parent of a recent child, so an adult and not held out, "
                             "but is recorded as held out")
        leaked = [x for x in held_now if x in self.by_id]
        for x in leaked:
            self.fail(5, f"{x} is held out by the rule but is published in people.json")
        missing = held_now - self.held_ids
        if missing:
            self.fail(5, f"{len(missing)} held-out id(s) are not recorded in data/held-out.json: {sorted(missing)[:6]}")
        self.held_names = [re.sub(r"\s+", " ", re.sub(r"/", " ", kid(I[x], "NAME")["val"])).strip()
                           for x in held_now if kid(I[x], "NAME")]
        # kept for rule 7: who the export says is 80 or younger with no death, by name and year
        self.window = []
        for x, i in info.items():
            if i["by"] is not None and not i["dead"] and self.today - i["by"] <= lr.LIVING_YEARS:
                n = kid(I[x], "NAME")
                nm = re.sub(r"\s+", " ", (n["val"] if n else "").replace("/", " ")).strip()
                if len(nm.split()) >= 2:
                    self.window.append((x, nm, i["by"]))
        self.info["ged"] = (f"recomputed from the GEDCOM: {len(living_now)} living, {len(held_now)} held out, "
                            f"{mism} mismatch(es), {exempt} explained by a name twin")

    # ----------------------------------------------------------------- rule 3
    def rule3_fields(self):
        n_rows = 0
        for fn in sorted(os.listdir(self.data)):
            if not fn.endswith(".json"):
                continue
            try:
                doc = jload(os.path.join(self.data, fn))
            except Exception as e:
                self.fail(3, f"{fn} could not be read ({str(e)[:60]}): the gate cannot know who is in it")
                continue
            for r in rows_in(doc):
                if r.get("living") is not True:
                    continue
                n_rows += 1
                for k, v in r.items():
                    if v in (None, "", "\u2014", [], {}, False, 0):
                        continue
                    if k in FORBIDDEN_KEYS:
                        self.fail(3, f"{fn}: a living row carries «{k}»")
                    elif k not in ALLOWED_KEYS and not (fn == "story.json" and k in STORY_KEYS):
                        self.fail(3, f"{fn}: a living row carries the field «{k}», which is not name, "
                                     "relationship or place")
                    elif k in ("birthPlace", "place") and isinstance(v, str):
                        if re.search(r"\d", v) or LV.STREETISH.search(v) or LV.INSTITUTION.search(v):
                            self.fail(3, f"{fn}: a living person's place is address-like or an institution")
                    elif isinstance(v, str) and k not in ("id", "slug", "name", "given", "surname", "href"):
                        if YEAR.search(v):
                            self.fail(3, f"{fn}: a living row has a year in «{k}»")
        for p in self.living:
            if YEAR.search(p["slug"]):
                self.fail(3, f"a living person's slug carries a year: /people/{p['slug']}/")
        # the photograph manifest names every photograph and whose it is; none may be a
        # living or a held-out person's
        mp = os.path.join(self.root, "data", "photo-manifest.json")
        bad_ph = 0
        if os.path.exists(mp):
            living_ids = {p["id"] for p in self.living}
            for m in jload(mp):
                if m.get("xref") in living_ids or m.get("xref") in self.held_ids:
                    bad_ph += 1
                    self.fail(3, "data/photo-manifest.json lists a photograph of a living or held-out person")
                    break
        self.info["photos_of_living_in_manifest"] = bad_ph
        self.info["living_rows_checked"] = n_rows
        pl = sum(1 for p in self.living if p.get("birthPlace"))
        self.info["living_with_place"] = pl
        self.info["living_without_place"] = len(self.living) - pl

    # ----------------------------------------------------------------- rule 4
    def sitemap_urls(self):
        sm = os.path.join(self.dist, "sitemap.xml")
        t = open(sm, encoding="utf-8").read() if os.path.exists(sm) else ""
        return set(re.findall(r"<loc>([^<]+)</loc>", t))

    def search_paths(self):
        out = set()
        for cand in (os.path.join(self.dist, "searchindex.json"),):
            if os.path.exists(cand):
                try:
                    for r in jload(cand):
                        out.add(r.get("u") or r.get("p") or r.get("path") or "")
                except Exception:
                    pass
        return out

    def rule4_pages(self):
        sm = self.sitemap_urls()
        sidx_raw = ""
        sp = os.path.join(self.dist, "searchindex.json")
        if os.path.exists(sp):
            sidx_raw = open(sp, encoding="utf-8").read()
        counts = dict(noindex=0, in_sitemap=0, in_search=0, jsonld=0, tables=0, images=0, years=0, missing=0)
        for p in self.living:
            rel = f"people/{p['slug']}"
            h = self.page(rel)
            if h is None:
                counts["missing"] += 1
                self.fail(6, f"no built page for /people/{p['slug']}/")
                continue
            if NOINDEX.search(h[:6000]):
                counts["noindex"] += 1
            else:
                self.fail(4, f"/people/{p['slug']}/ is a living page without noindex")
            if any(u.rstrip("/").endswith("/" + rel) for u in sm):
                counts["in_sitemap"] += 1
                self.fail(4, f"/people/{p['slug']}/ is in the sitemap")
            if f"/{rel}/" in sidx_raw:
                counts["in_search"] += 1
                self.fail(4, f"/people/{p['slug']}/ is in the search index")
            if LDJSON.search(h):
                counts["jsonld"] += 1
                self.fail(4, f"/people/{p['slug']}/ carries JSON-LD")
            body = strip_chart_and_footer(h)
            m = re.search(r"(?is)<main.*?</main>", h)
            main = strip_chart_and_footer(m.group(0)) if m else body
            if re.search(r"<table", h, re.I):
                counts["tables"] += 1
                self.fail(4, f"/people/{p['slug']}/ has a table")
            if re.search(r"<img\b", h, re.I) or re.search(r"/plates/", h):
                counts["images"] += 1
                self.fail(4, f"/people/{p['slug']}/ has an image")
            if YEAR.search(re.sub(r"<[^>]+>", " ", main)):
                counts["years"] += 1
                self.fail(4, f"/people/{p['slug']}/ shows a year in its own content")
            # the self node of the chart must carry no date
            mnode = re.search(r'(?is)<div class="node me">(.*?)</div>', h)
            if mnode and YEAR.search(re.sub(r"<[^>]+>", " ", mnode.group(1))):
                counts["years"] += 1
                self.fail(4, f"/people/{p['slug']}/ has a date on its own chart node")
        self.info["living_pages"] = dict(counts, total=len(self.living))
        # name pages: every bearer living -> noindex and no canonical elsewhere
        by_name = {}
        for p in self.people:
            by_name.setdefault(_slugify(p["name"]), []).append(p)
        allliving = [k for k, ps in by_name.items() if ps and all(q.get("living") for q in ps)]
        bad = 0
        for k in allliving:
            h = self.page(f"who/{k}")
            if h is None:
                self.fail(6, f"no name page for /who/{k}/")
                continue
            c = CANON.search(h)
            if not NOINDEX.search(h[:6000]):
                bad += 1
                self.fail(4, f"/who/{k}/ names only living people and is not noindex")
            if c and not c.group(1).rstrip("/").endswith("/who/" + k):
                bad += 1
                self.fail(4, f"/who/{k}/ names a canonical elsewhere")
        self.info["name_pages_all_living"] = len(allliving)
        self.info["name_pages_all_living_bad"] = bad
        # POSITIVE CONTROL: the same checks on ordinary pages give the opposite
        ok_idx = ok_map = ok_ld = 0
        sample = [p for p in self.dead if p.get("born")][:200]
        for p in sample:
            h = self.page(f"people/{p['slug']}")
            if h is None:
                continue
            ok_idx += 0 if NOINDEX.search(h[:6000]) else 1
            ok_ld += 1 if LDJSON.search(h) else 0
            ok_map += 1 if any(u.rstrip("/").endswith(f"/people/{p['slug']}") for u in sm) else 0
        self.info["control_dead_pages"] = dict(sampled=len(sample), indexable=ok_idx,
                                               in_sitemap=ok_map, with_jsonld=ok_ld)
        if sample and (ok_idx == 0 or ok_map == 0 or ok_ld == 0):
            self.fail(4, "the positive control failed: ordinary pages are not indexable, not in the "
                         f"sitemap, or carry no JSON-LD (indexable {ok_idx}, in sitemap {ok_map}, "
                         f"JSON-LD {ok_ld} of {len(sample)}), so the living checks prove nothing")

    # ----------------------------------------------------------------- rule 5
    def rule5_held(self):
        hits = []
        if not self.held_ids:
            self.fail(5, "data/held-out.json records no held-out id: the archive holds back at least the "
                         "possible minors, so an empty list means the file is not being read")
        pat = [re.compile(re.escape(i) + r"(?![0-9])") for i in sorted(self.held_ids)]
        scanned = 0
        for fn in sorted(os.listdir(self.data)):
            if fn.endswith(".json"):
                t = open(os.path.join(self.data, fn), encoding="utf-8").read()
                scanned += 1
                for i, rx in zip(sorted(self.held_ids), pat):
                    if rx.search(t):
                        hits.append((fn, i))
        for rel, path in self.pages.items():
            pass
        for fn, i in hits[:8]:
            self.fail(5, f"held-out id {i} appears in {fn}")
        # the tsv/json outside site/src/data that is committed
        for sub in ("data",):
            d = os.path.join(self.root, sub)
            for fn in sorted(os.listdir(d)) if os.path.isdir(d) else []:
                if fn == "held-out.json" or not fn.endswith((".json", ".tsv")):
                    continue
                t = open(os.path.join(d, fn), encoding="utf-8", errors="replace").read()
                for i, rx in zip(sorted(self.held_ids), pat):
                    if rx.search(t):
                        self.fail(5, f"held-out id {i} appears in data/{fn}")
        # the ledger names everyone it ever minted for
        led = os.path.join(self.data, "person-slugs.json")
        if os.path.exists(led):
            ids = set(jload(led).get("slugs", {}))
            for i in self.held_ids & ids:
                self.fail(5, f"held-out id {i} is still in person-slugs.json")
        # by name, where the GEDCOM lets us know the names
        names = getattr(self, "held_names", None)
        prose = 0
        if names:
            dead_names = {re.sub(r"\s+", " ", p["name"]).lower() for p in self.people}
            phr = [n for n in names if len(n.split()) >= 2 and n.lower() not in dead_names]
            if phr:
                rx = re.compile("|".join(re.escape(n) for n in sorted(phr, key=len, reverse=True)), re.I)
                for rel, path in self.pages.items():
                    t = open(path, encoding="utf-8", errors="replace").read()
                    if rx.search(re.sub(r"<[^>]+>", " ", re.sub(r"(?is)<script.*?</script>", " ", t))):
                        prose += 1
                # and the data the site ships: committed JSON and the JSON in the build
                shipped = 0
                files = [os.path.join(self.data, f) for f in os.listdir(self.data) if f.endswith(".json")]
                for dp, _, fns in os.walk(self.dist):
                    files += [os.path.join(dp, f) for f in fns if f.endswith((".json", ".xml", ".txt"))]
                for path in files:
                    t = open(path, encoding="utf-8", errors="replace").read()
                    if rx.search(t):
                        shipped += 1
                        self.fail(5, f"a held-out person's name appears in {os.path.relpath(path, os.path.dirname(self.data))}")
                self.info["held_name_in_shipped_json"] = f"{shipped} file(s) of {len(files)}"
                allowed = int(self.held.get("proseMentionsAllowed", 0))
                self.info["held_name_in_built_pages"] = f"{prose} page(s) (ratchet {allowed})"
                if prose > allowed:
                    self.fail(5, f"a held-out person's name appears on {prose} built page(s); the recorded "
                                 f"ceiling is {allowed}")
        else:
            self.info["held_name_in_built_pages"] = "not checked (needs the private GEDCOM; runs locally)"
        self.info["held_ids"] = len(self.held_ids)

    # ----------------------------------------------------------------- rule 6
    def rule6_pages_for_named(self):
        slugs = set(self.by_slug)
        dangling = 0
        for p in self.people:
            for b in ("parents", "children", "spouses", "siblings"):
                for e in p.get(b) or []:
                    if e.get("slug") not in slugs or e.get("id") not in self.by_id:
                        dangling += 1
                        self.fail(6, f"{p['slug']} names a {b[:-1] if b != 'siblings' else 'sibling'} "
                                     f"({e.get('slug')}) who has no record")
        missing = [p["slug"] for p in self.people if f"people/{p['slug']}" not in self.pages]
        for s in missing[:8]:
            self.fail(6, f"no built page for /people/{s}/")
        self.info["named_without_page"] = dangling + len(missing)


    # ----------------------------------------------------------------- rule 7
    BORN_KEYS = ("born", "birth", "birthYear", "bornYear")
    DEATH_KEYS = ("died", "death", "diedText", "buried", "deathYear")

    def _allow(self):
        """Snippets that may carry an in-window year because the person has a recorded death.
        data/living-year-allow.json: {"allow": [{"text": "...", "why": "..."}]}. Kept by hand,
        so each entry is a decision."""
        ap = os.path.join(self.root, "data", "living-year-allow.json")
        if not os.path.exists(ap):
            return []
        return [a["text"] for a in jload(ap).get("allow", []) if a.get("text")]

    def rule7_years(self):
        """No birth year of a person with no death is published anywhere (25 October 2026).

        The fault this closes: a man born in 1948 was published as dead, and his year turned up
        on the namesake lists, in derived data files that only some generators regenerate, and in
        hand-written prose, none of which the living checks read because they all started from a
        row flagged living. Here nothing starts from the flag.
          7a  a data row (any file, source or built) that names a living person by slug or id
              must carry no life field, whatever its own `living` says
          7b  a data row with a birth year in the 80-year window and no death field, and not
              flagged living, is a person published as dead on a year that makes them living
          7c  a built page or data file with «b. YYYY» in the window, or a namesake line whose
              year is in the window and is not a death year, is a year with no death beside it
          7d  (needs the private export) a person the export says is 80 or younger with no death,
              followed by their own birth year in any built page or data file
        """
        cut = self.today - lr.LIVING_YEARS
        window = lambda y: isinstance(y, int) and y >= cut and y <= self.today
        living_keys = {p["slug"] for p in self.living} | {p["id"] for p in self.living}
        allow = self._allow()
        json_files = [os.path.join(self.data, f) for f in sorted(os.listdir(self.data)) if f.endswith(".json")]
        text_files = []
        for dp, _, fns in os.walk(self.dist):
            for fn in fns:
                path = os.path.join(dp, fn)
                if fn.endswith(".json"):
                    json_files.append(path)
                if fn.endswith((".html", ".json", ".xml", ".txt")):
                    text_files.append(path)
        n_rows = 0
        for path in json_files:
            try:
                doc = jload(path)
            except Exception:
                continue
            rel = os.path.relpath(path, os.path.dirname(self.data) if path.startswith(self.data) else self.dist)
            for r in rows_in(doc):
                key = r.get("slug") if isinstance(r.get("slug"), str) else None
                ident = r.get("id") if isinstance(r.get("id"), str) else None
                is_living_row = r.get("living") is True
                if not is_living_row and (key in living_keys or ident in living_keys):
                    n_rows += 1
                    bad = [k for k in FORBIDDEN_KEYS if r.get(k) not in (None, "", [], {}, False, 0)]
                    if bad:
                        self.fail(7, f"{rel}: a row that names a living person carries {sorted(bad)[:3]} "
                                     "and is not flagged living (a derived file that was not regenerated?)")
                born = next((r[k] for k in self.BORN_KEYS if isinstance(r.get(k), int)), None)
                if window(born) and not is_living_row \
                        and not any(r.get(k) not in (None, "", [], {}, False) for k in self.DEATH_KEYS):
                    self.fail(7, f"{rel}: a row with a birth year in the 80-year window, no death and no "
                                 f"living flag ({r.get('slug') or r.get('id') or r.get('name') or 'unnamed'})")
        self.info["rows_naming_living_checked"] = n_rows
        # 7c / 7d: text
        dead_fmt = set()
        for q in self.dead:
            if q.get("died"):
                dead_fmt.add("–".join(str(x) for x in (q.get("born"), q.get("died")) if x))
        B = re.compile(r"\bb\.\s*(\d{4})\b")
        NS = re.compile(r"(?is)Others of the same name(.*?)</section>")
        ITEM = re.compile(r"—\s*(\d{4}(?:\s*–\s*\d{4})?)")
        names = {}
        for x, nm, by in getattr(self, "window", []):
            names.setdefault(re.sub(r"\s+", " ", nm), set()).add(by)
        name_rx = None
        if names:
            name_rx = re.compile("|".join(r"\s+".join(re.escape(t) for t in n.split())
                                          for n in sorted(names, key=len, reverse=True)))
        hits_b = hits_ns = hits_nm = 0
        for path in text_files:
            t = open(path, encoding="utf-8", errors="replace").read()
            for a in allow:
                t = t.replace(a, " ")
            rel = os.path.relpath(path, self.dist)
            plain = re.sub(r"<[^>]+>", " ", re.sub(r"(?is)<script.*?</script>|<style.*?</style>", " ", t)) \
                if path.endswith(".html") else t
            for m in B.finditer(plain):
                if window(int(m.group(1))):
                    hits_b += 1
                    self.fail(7, f"{rel}: «b. {m.group(1)}» is a birth year in the 80-year window with no death shown")
            if path.endswith(".html"):
                for seg in NS.findall(t):
                    for m in ITEM.finditer(re.sub(r"<[^>]+>", " ", seg)):
                        first = int(re.match(r"\d{4}", m.group(1)).group(0))
                        tok = re.sub(r"\s+", "", m.group(1))
                        if window(first) and tok not in dead_fmt:
                            hits_ns += 1
                            self.fail(7, f"{rel}: a namesake line shows a year in the 80-year window that is "
                                         "not a recorded death")
            if name_rx:
                for m in name_rx.finditer(plain):
                    nm = re.sub(r"\s+", " ", m.group(0))
                    tail = plain[m.end(): m.end() + 100]
                    fm = re.search(r"\d{4}", tail)
                    if fm and re.fullmatch(r"[^\d]*", tail[:fm.start()]) and int(fm.group(0)) in names.get(nm, ()):
                        hits_nm += 1
                        self.fail(7, f"{rel}: a person the export gives as 80 or younger with no death is "
                                     "followed by their own birth year")
        self.info["year_text_hits"] = f"b. {hits_b} · namesake {hits_ns} · name+year {hits_nm}" + \
            ("" if names else " (name+year needs the private export; runs locally)")

    def run(self):
        self.load()
        self.rule1_empty()
        if self.people and self.pages:
            self.rule2_classification()
            self.rule3_fields()
            self.rule4_pages()
            self.rule5_held()
            self.rule6_pages_for_named()
            self.rule7_years()
        return self.fails


def _slugify(s):
    import unicodedata
    s = unicodedata.normalize("NFD", str(s or ""))
    s = re.sub(r"[̀-ͯ]", "", s)
    return re.sub(r"^-+|-+$", "", re.sub(r"[^A-Za-z0-9]+", "-", s)).lower()


def report(g, quiet=False):
    if g.fails:
        seen = {}
        for rule, msg in g.fails:
            seen.setdefault(rule, []).append(msg)
        print(f"  FAIL  living-v2   {len(g.fails)} problem(s) across rule(s) {sorted(seen)}")
        for rule, msgs in sorted(seen.items()):
            for m in msgs[:5]:
                print(f"          rule {rule}: {m}")
            if len(msgs) > 5:
                print(f"          rule {rule}: ... and {len(msgs) - 5} more")
        return 1
    if not quiet:
        i = g.info
        lp = i.get("living_pages", {})
        print(f"  ok    living-v2   {len(g.living)} living people, {len(g.dead)} not living, "
              f"{i.get('held_ids', 0)} held out (by id)")
        print(f"        living pages: {lp.get('total')} built · noindex {lp.get('noindex')} · in sitemap "
              f"{lp.get('in_sitemap')} · in search index {lp.get('in_search')} · JSON-LD {lp.get('jsonld')} · "
              f"tables {lp.get('tables')} · images {lp.get('images')} · years {lp.get('years')}")
        print(f"        with a town and country {i.get('living_with_place')} · no place {i.get('living_without_place')} "
              f"· all-living name pages {i.get('name_pages_all_living')} (noindex, none canonical elsewhere)")
        print(f"        control (not-living pages sampled): {i.get('control_dead_pages')}")
        print(f"        classification: {i.get('published_as_dead_but_living_by_rule')} published as dead but "
              f"living by rule · GEDCOM: {i.get('ged')}")
        print(f"        dated children (under 18 by year) published with a page: "
              f"{i.get('dated_children_published', 'not checked (needs the private GEDCOM)')}")
        print(f"        undated parents of a recent child, living by the rule: "
              f"{i.get('undated_parents_living_by_recent_child', 'not checked (needs the private GEDCOM)')}")
        print(f"        no birth year of a person with no death (rule 7): rows naming a living person "
              f"{i.get('rows_naming_living_checked')} · text hits {i.get('year_text_hits')}")
        print(f"        named without a page: {i.get('named_without_page')} · held-out name in built pages: "
              f"{i.get('held_name_in_built_pages')} · in shipped json: {i.get('held_name_in_shipped_json', 'not checked (needs the private GEDCOM; runs locally)')}")
    return 0


# ------------------------------------------------------------------- self-test

def selftest(dist, data_dir, root, ged):
    """Plant one fault per rule in a copy of the build; the gate must catch each."""
    tmp = tempfile.mkdtemp(prefix="living-v2-selftest-")
    try:
        d2 = os.path.join(tmp, "dist")
        s2 = os.path.join(tmp, "data")
        r2 = os.path.join(tmp, "root")
        shutil.copytree(dist, d2)
        shutil.copytree(data_dir, s2)
        os.makedirs(os.path.join(r2, "data"))
        for fn in ("held-out.json", "photo-manifest.json", "living-year-allow.json"):
            if os.path.exists(os.path.join(root, "data", fn)):
                shutil.copy(os.path.join(root, "data", fn), os.path.join(r2, "data"))

        base = Gate(d2, s2, r2, ged, min_pages=300)
        base.run()
        if base.fails:
            print("  FAIL  living-v2 selftest: the unmodified copy does not pass, so no fault can be judged")
            report(base)
            return 1
        wrong = LV.selfcheck(lr.this_year())
        if wrong:
            print("  FAIL  living-v2 selftest: the recent-child rule's planted cases do not hold: " + "; ".join(wrong))
            return 1
        people = jload(os.path.join(s2, "people.json"))
        living = [p for p in people if p.get("living")]
        dead = [p for p in people if not p.get("living") and p.get("born")]
        L, D = living[0], dead[0]
        # a living person with a parent, for the dangling-edge fault
        held = sorted(jload(os.path.join(r2, "data", "held-out.json"))["ids"])[0]
        yr_young = lr.this_year() - 30            # a runtime value, never a literal in a file

        undo = []                      # (path, original bytes or None, was_dir_backup)

        def write(path, text):
            if not any(u[0] == path for u in undo):
                undo.append((path, open(path, "rb").read() if os.path.exists(path) else None, None))
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)

        def remove(path):
            """Move a file or directory aside (fast, same filesystem); restored after the fault."""
            bk = os.path.join(tmp, "moved-%d" % len(undo))
            os.rename(path, bk)
            undo.append((path, None, bk))

        def restore():
            while undo:
                path, orig, bk = undo.pop()
                if bk is not None:
                    if os.path.exists(path):
                        shutil.rmtree(path, ignore_errors=True) if os.path.isdir(path) else os.remove(path)
                    os.rename(bk, path)
                elif orig is None:
                    if os.path.exists(path):
                        os.remove(path)
                else:
                    with open(path, "wb") as f:
                        f.write(orig)

        def pp(): return os.path.join(s2, "people.json")
        def lp(p): return os.path.join(d2, "people", p["slug"], "index.html")

        def edit_people(fn):
            doc = jload(pp()); fn(doc); write(pp(), json.dumps(doc, ensure_ascii=False))

        def f_empty_build():
            for name in os.listdir(d2):
                remove(os.path.join(d2, name))
        faults = []

        def add(rule, name, plant, ged_only=False):
            faults.append((rule, name, plant, ged_only))

        add(1, "an emptied build", f_empty_build)
        add(1, "nobody flagged living", lambda: edit_people(lambda d: [x.__setitem__("living", False) for x in d]))
        add(2, "a living-by-rule person published as dead",
            lambda: edit_people(lambda d: next(x for x in d if x["id"] == D["id"]).update(
                {"born": yr_young, "died": None, "events": [], "sources": [], "records": []})))
        Lflip = next((p for p in living if p["id"] in getattr(base, "no_twin", set())), L)
        add(2, "a dated living-by-rule person with a public source published as dead (the 1948 fault)",
            lambda: edit_people(lambda d: next(x for x in d if x["id"] == D["id"]).update(
                {"born": yr_young, "died": None, "events": [], "sources": ["FamilySearch"],
                 "records": [{"kind": "passenger index", "what": "NAA passenger arrivals", "href": "/crossings"}]})))
        add(2, "a living flag flipped (GEDCOM recompute)",
            lambda: edit_people(lambda d: next(x for x in d if x["id"] == Lflip["id"]).update({"living": False})), True)
        add(3, "a death year on a living row",
            lambda: edit_people(lambda d: next(x for x in d if x["id"] == L["id"]).update({"died": PLANT_YEAR})))
        add(3, "a source list on a living row",
            lambda: edit_people(lambda d: next(x for x in d if x["id"] == L["id"]).update({"sources": ["planted"]})))
        add(3, "a photograph on a living row",
            lambda: edit_people(lambda d: next(x for x in d if x["id"] == L["id"]).update({"photos": ["planted.jpg"]})))
        add(3, "a photograph of a living person in the manifest",
            lambda: write(os.path.join(r2, "data", "photo-manifest.json"),
                          json.dumps(jload(os.path.join(r2, "data", "photo-manifest.json")) + [{"xref": L["id"], "file": "planted.jpg"}])))
        add(3, "an address-like place",
            lambda: edit_people(lambda d: next(x for x in d if x["id"] == L["id"]).update(
                {"birthPlace": "12 Planted Street, Town, Country"})))
        add(3, "an institution as the place",
            lambda: edit_people(lambda d: next(x for x in d if x["id"] == L["id"]).update(
                {"birthPlace": "Planted Hospital, Town, Country"})))
        add(3, "a year in a living slug",
            lambda: edit_people(lambda d: next(x for x in d if x["id"] == L["id"]).update(
                {"slug": L["slug"] + f"-{PLANT_YEAR}"})))
        add(4, "a living page without noindex",
            lambda: write(lp(L), re.sub(r'<meta[^>]*name="robots"[^>]*>', "", open(lp(L), encoding="utf-8").read())))
        add(4, "a living page in the sitemap",
            lambda: write(os.path.join(d2, "sitemap.xml"),
                          open(os.path.join(d2, "sitemap.xml"), encoding="utf-8").read().replace(
                              "</urlset>", f"<url><loc>https://x.invalid/people/{L['slug']}/</loc></url></urlset>")))
        add(4, "a living page in the search index",
            lambda: write(os.path.join(d2, "searchindex.json"),
                          json.dumps(jload(os.path.join(d2, "searchindex.json")) + [{"k": "Person", "t": "x", "u": f"/people/{L['slug']}/"}])))
        add(4, "Person JSON-LD on a living page",
            lambda: write(lp(L), open(lp(L), encoding="utf-8").read().replace(
                "</head>", '<script type="application/ld+json">{"@type":"Person"}</script></head>')))
        add(4, "a table on a living page",
            lambda: write(lp(L), open(lp(L), encoding="utf-8").read().replace("</main>", "<table><tr><td>x</td></tr></table></main>")))
        add(4, "an image on a living page",
            lambda: write(lp(L), open(lp(L), encoding="utf-8").read().replace("</main>", '<img src="/plates/planted.jpg"></main>')))
        add(4, "a year on a living page",
            lambda: write(lp(L), open(lp(L), encoding="utf-8").read().replace("</main>", f"<p>Born {PLANT_YEAR}</p></main>")))
        add(4, "a date on a living chart node",
            lambda: write(lp(L), open(lp(L), encoding="utf-8").read().replace(
                '<div class="node me">', f'<div class="node me"><span class="dt">{PLANT_YEAR}</span>', 1)))

        def f_who_noindex():
            by = {}
            for p in people:
                by.setdefault(_slugify(p["name"]), []).append(p)
            k = next((k for k, ps in by.items() if all(q.get("living") for q in ps)), None)
            if not k:
                raise RuntimeError("no all-living name page to plant a fault in")
            path = os.path.join(d2, "who", k, "index.html")
            write(path, re.sub(r'<meta[^>]*name="robots"[^>]*>', "", open(path, encoding="utf-8").read()))
        add(4, "an all-living name page without noindex", f_who_noindex)
        add(4, "the control broken: every ordinary page noindexed",
            lambda: [write(lp(x), open(lp(x), encoding="utf-8").read().replace("<head>", '<head><meta name="robots" content="noindex">', 1))
                     for x in dead[:200] if os.path.exists(lp(x))])
        def f_plant_rows(rows):
            return lambda: write(os.path.join(s2, "planted-rows.json"), json.dumps(rows))
        add(7, "a derived data row for a living person that kept the year and a dead flag",
            f_plant_rows([{"slug": L["slug"], "name": "Planted", "born": yr_young, "died": None, "living": False}]))
        add(7, "a data row with a birth year in the window, no death and no living flag",
            f_plant_rows([{"slug": "planted-nobody-here", "name": "Planted", "born": yr_young}]))
        add(7, "a «b. YYYY» in the window on a built page",
            lambda: write(os.path.join(d2, "about", "index.html"),
                          open(os.path.join(d2, "about", "index.html"), encoding="utf-8").read().replace(
                              "</main>", f"<p>Planted Person (b. {yr_young})</p></main>")))
        add(7, "a namesake line with a birth year in the window on a built page",
            lambda: write(os.path.join(d2, "about", "index.html"),
                          open(os.path.join(d2, "about", "index.html"), encoding="utf-8").read().replace(
                              "</main>", '<section class="blk"><h2>Others of the same name</h2><ul><li>'
                              f'<a href="/x/">Planted</a><span> \u2014 {yr_young}, Town</span></li></ul></section></main>')))
        def f_name_year():
            x, nm, by = base.window[0]
            path = os.path.join(d2, "about", "index.html")
            write(path, open(path, encoding="utf-8").read().replace("</main>", f"<p>{nm} {by}</p></main>"))
        add(7, "a living person's name followed by their birth year (GEDCOM)", f_name_year, True)
        add(5, "a held-out id in a data file",
            lambda: write(os.path.join(s2, "stats.json"),
                          open(os.path.join(s2, "stats.json"), encoding="utf-8").read()[:-1] + f', "planted": "{held}"}}'))
        add(5, "a held-out id back in the slug ledger",
            lambda: write(os.path.join(s2, "person-slugs.json"),
                          json.dumps({"slugs": {**jload(os.path.join(s2, "person-slugs.json")).get("slugs", {}), held: "planted-name"}})))
        add(5, "a held-out person published (id in people.json)",
            lambda: edit_people(lambda d: d.append({**d[0], "id": held, "slug": "planted-held"})))

        def f_held_name():
            # The held-out name check skips a name that a published person also bears, and
            # held_names comes from iterating a SET, so [0] was a different name every run and
            # sometimes one the check does not scan: the fault was "not caught" about one run in
            # three. Plant a name the check really looks for.
            _dead = {re.sub(r"\s+", " ", p["name"]).lower() for p in base.people}
            nm = next(n for n in sorted(base.held_names)
                      if len(n.split()) >= 2 and n.lower() not in _dead)
            path = os.path.join(d2, "about", "index.html")
            write(path, open(path, encoding="utf-8").read().replace("</main>", f"<p>{nm}</p></main>"))
        add(5, "a held-out name on a built page (GEDCOM)", f_held_name, True)
        def f_held_name_json():
            # The held-out name check skips a name that a published person also bears, and
            # held_names comes from iterating a SET, so [0] was a different name every run and
            # sometimes one the check does not scan: the fault was "not caught" about one run in
            # three. Plant a name the check really looks for.
            _dead = {re.sub(r"\s+", " ", p["name"]).lower() for p in base.people}
            nm = next(n for n in sorted(base.held_names)
                      if len(n.split()) >= 2 and n.lower() not in _dead)
            write(os.path.join(s2, "stats.json"),
                  open(os.path.join(s2, "stats.json"), encoding="utf-8").read()[:-1] + f', "planted": "{nm}"}}')
        add(5, "a held-out name in a shipped data file (GEDCOM)", f_held_name_json, True)
        def kid_ids():
            ids = getattr(base, "child_ids", [])
            if not ids:
                raise StopIteration
            return ids[0]
        add(5, "a known child wrongly held out (GEDCOM)",
            lambda: write(os.path.join(r2, "data", "held-out.json"),
                          json.dumps({**jload(os.path.join(r2, "data", "held-out.json")),
                                      "ids": jload(os.path.join(r2, "data", "held-out.json"))["ids"] + [kid_ids()]})), True)
        add(6, "a dated child with no page (GEDCOM)",
            lambda: edit_people(lambda d: [d.remove(x) for x in [next(y for y in d if y["id"] == kid_ids())]]), True)
        def recent_parent():
            ids = [x for x in getattr(base, "recent_parent_ids", []) if x in getattr(base, "no_twin", set())
                   and x in base.by_id]
            if not ids:
                raise StopIteration
            return ids[0]
        add(2, "an undated parent of a recent child published as not living (GEDCOM)",
            lambda: edit_people(lambda d: next(x for x in d if x["id"] == recent_parent()).update({"living": False})), True)
        add(5, "an undated parent of a recent child recorded as held out (GEDCOM)",
            lambda: write(os.path.join(r2, "data", "held-out.json"),
                          json.dumps({**jload(os.path.join(r2, "data", "held-out.json")),
                                      "ids": jload(os.path.join(r2, "data", "held-out.json"))["ids"] + [recent_parent()]})), True)
        add(5, "an empty held-out list",
            lambda: write(os.path.join(r2, "data", "held-out.json"), json.dumps({"ids": []})))
        add(6, "a relationship to nobody",
            lambda: edit_people(lambda d: next(x for x in d if x["id"] == L["id"]).setdefault("parents", []).append(
                {"id": "@PLANTED@", "name": "Planted", "slug": "planted-nobody", "living": False})))
        add(6, "a person with no built page",
            lambda: remove(os.path.dirname(lp(D))))

        caught = missed = skipped = 0
        by_rule = {}
        for rule, name, plant, ged_only in faults:
            if ged_only and not (ged and os.path.exists(ged)):
                skipped += 1
                print(f"        skip  rule {rule}  {name}: needs the private GEDCOM (local only)")
                continue
            try:
                plant()
            except StopIteration:
                print(f"  FAIL  living-v2 selftest: could not plant «{name}» (no suitable row)")
                missed += 1
                restore()
                continue
            g = Gate(d2, s2, r2, ged, min_pages=300)
            g.run()
            restore()
            if g.fails and (any(r == rule for r, _ in g.fails)):
                caught += 1
                by_rule[rule] = by_rule.get(rule, 0) + 1
            else:
                missed += 1
                print(f"  FAIL  living-v2 selftest: rule {rule} did NOT catch «{name}» "
                      f"(rules that fired: {sorted({r for r, _ in g.fails})})")
        total = len(faults)
        if missed:
            print(f"  FAIL  living-v2 selftest: {missed} of {total} planted fault(s) were not caught")
            return 1
        print(f"  ok    living-v2 selftest: {caught} of {total - skipped} runnable planted faults caught "
              f"({skipped} need the private GEDCOM), by rule {dict(sorted(by_rule.items()))}; "
              "the unmodified copy passes")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dist", default="dist")
    ap.add_argument("--data", default="src/data")
    ap.add_argument("--root", default="..")
    ap.add_argument("--ged", default=None)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    a.dist = _outdir.resolve(a.dist)
    ged = a.ged or os.path.join(ROOT, "sources", "mazza-myheritage.ged")
    if not os.path.isdir(a.dist):
        print(f"check_living_v2: no {a.dist} - build first")
        return 1
    if a.selftest:
        return selftest(a.dist, a.data, a.root, ged)
    g = Gate(a.dist, a.data, a.root, ged)
    g.run()
    return report(g, a.quiet)


if __name__ == "__main__":
    sys.exit(main())
