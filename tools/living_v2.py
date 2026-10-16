"""Mazza's adapter to the estate's one definition of who is living.

The DEFINITION is not here. It is the kit's `living_rule.py` (David, 16 October
2026), imported from the pinned kit, and this file only supplies what that rule
needs and this archive alone can say: where a person's citations are, and what
counts in THIS archive as a recorded death or burial.

  LIVING   80 or younger by year, no death or burial recorded, and no citation
           from a public record source (FamilySearch, MyHeritage records,
           Findmypast...). Someone with no birth year is not living by this test.
  HELD OUT an undated person with a living parent (they might be a child): not
           recorded dead, no public source, no birth year. Not published at all.
           A child with a KNOWN birth year is NOT held out (David, 16 October 2026):
           they are living, like anyone else 80 or younger, and have a page.

This replaces three older tests, none of which survives:
  * `datesHidden`    (80 or younger, no death in the TREE) - it ignored a burial
                     register, a public source, and everything the archive had read;
  * `presumedLiving` (the tree cannot show they died) - true of 280 plainly dead
                     people, who are ordinary pages and stay so;
  * the 100-year bound in tools/fetch_photos.py.
"""
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
KIT_TOOLS = os.path.join(ROOT, "site", "node_modules", "@daviddef", "archive-kit", "kit", "tools")
if KIT_TOOLS not in sys.path:
    sys.path.insert(0, KIT_TOOLS)
import living_rule as lr  # noqa: E402  (the estate's one definition)

BLANK = {"", "—", "-", "–", "no"}


def _rows(path):
    p = os.path.join(ROOT, path)
    if not os.path.exists(p):
        return []
    return list(csv.DictReader(open(p, encoding="utf-8"), delimiter="\t"))


def _blank(v):
    return (v or "").strip() in BLANK


NAA = re.compile(r"\bNAA\b|National Archives of Australia", re.I)


def with_addresses(cites):
    """Add the public address a citation stands for, where the archive writes only a name.

    The archive cites "NAA ..." and the kit's list matches the National Archives
    of Australia by its address (naa.gov.au, added in kit 6cefc79), so the address
    is stated once here instead of the list being widened. Same function for the
    generator and the gate.
    """
    cites = list(cites or [])
    if any(NAA.search(str(c)) for c in cites):
        cites.append("recordsearch.naa.gov.au")
    return cites


def evidence():
    """What the ARCHIVE has read about a person, keyed by slug.

    cites : the citation strings (a provider, a URL or a title) to hand to
            living_rule.public_source
    dead  : slugs for whom the archive holds a recorded death or burial that the
            family tree itself lacks (a burial register, a death record, a dated
            death in a documented addition)
    """
    import json
    cites, dead = {}, set()

    def add(slug, *strings):
        slug = (slug or "").strip()
        if _blank(slug):
            return
        cites.setdefault(slug, []).extend(s for s in strings if s)
        # An NAA citation is a citation of the National Archives of Australia, whose
        # public RecordSearch address is on the kit's public-source list (6cefc79).
        # The archive writes it as "NAA ..." and the list matches the address, so
        # the address is stated here, once, rather than the list being widened.
        cites[slug] = with_addresses(cites[slug])

    for r in _rows("data/read-people.tsv"):
        add(r["slug"], r["kind"], r["what"], r["href"])
        if re.search(r"burial|death|internment|funeral|grave", r["kind"], re.I):
            dead.add(r["slug"].strip())
    for r in _rows("data/documented-additions.tsv"):
        add(r["inTree"], r["source"])
        if not _blank(r["inTree"]) and not _blank(r["died"]):
            dead.add(r["inTree"].strip())
    for r in _rows("data/corrections.tsv"):
        add(r["slug"], r["source"])
        if not _blank(r["slug"]) and re.match(r"death|burial", r["kind"], re.I) \
                and not re.search(r"RETRACTED|not known|missing entirely", r["kind"], re.I):
            dead.add(r["slug"].strip())
    for r in _rows("data/qld-bdm.tsv"):
        add(r["who"], r["type"] + " " + r["reg"])
        if r["type"].strip().lower() == "death" and not _blank(r["who"]):
            dead.add(r["who"].strip())
    for r in _rows("data/naa-ships.tsv"):
        add(r["slug"], "NAA passenger arrivals index item " + r["itemId"])
    nud = os.path.join(ROOT, "site", "src", "data", "nudgee.json")
    if os.path.exists(nud):
        for b in json.load(open(nud, encoding="utf-8")).get("burials", []):
            dead.add(b["slug"])          # a burial register line: a recorded burial
            add(b["slug"], "Brisbane Catholic Cemeteries register")
    return {"cites": cites, "dead": dead}


def classify(people, today_year=None):
    """people: {id: {"by": int|None, "dead": bool, "cites": [str], "parents": [id]}}

    Returns (living, held_out) as sets of ids. Living is computed first, because
    a possible minor with no birth year is defined by a living parent.
    """
    y = today_year or lr.this_year()
    living = {i for i, p in people.items()
              if lr.is_living(p["by"], p["dead"], p["cites"], y)}
    held = set()
    for i, p in people.items():
        pl = any(q in living for q in p["parents"])
        if lr.is_held_out(i, p["by"], p["dead"], p["cites"], pl, (), y):
            held.add(i)
    return living, held


# ---- the town and country of a living person --------------------------------
# Not a street, an address-like string or an institution. A place that looks like
# one is cut back to the town and country, and the cut is COUNTED by the caller.
INSTITUTION = re.compile(
    r"\b(hospital|clinic|nursing|aged care|care home|rest home|hospice|infirmary|"
    r"sanatorium|asylum|prison|jail|school|college|university|church|convent|"
    r"cemetery|barracks|camp|hotel|station)\b", re.I)
STREETISH = re.compile(
    r"\d|\b(street|st\.|road|rd\.|avenue|ave\.|lane|drive|dr\.|court|crescent|"
    r"place|pde|parade|highway|hwy|boulevard|blvd|terrace|way|po box|unit|apt)\b",
    re.I)


def town_country(place, country_of):
    """Reduce a recorded place to 'Town, Region, Country'; return (text, how)

    how: "" when the place was already a town, "cut" when an institution or an
    address-like leading part was dropped, "nocountry" when no country could be
    found for it. A place with no usable town returns ("", "none").
    """
    place = re.sub(r"\s+", " ", (place or "").strip().strip(","))
    if not place:
        return "", "none"
    parts = [p.strip() for p in place.split(",") if p.strip()]
    how = ""
    kept = []
    for i, part in enumerate(parts):
        if INSTITUTION.search(part) or STREETISH.search(part):
            how = "cut"
            continue
        kept.append(part)
    if not kept:
        return "", "none"
    # "USA" beside the country it abbreviates is the same word twice
    kept = [k for k in kept if k.upper() not in ("USA", "U.S.A.", "US")] or kept
    text = ", ".join(kept)
    c = country_of(text)
    if c and c.lower() not in text.lower():
        text += ", " + c
    if not c and not any(k in text.lower() for k in ("australia", "italy", "argentina",
                                                      "united states", "united kingdom")):
        how = how or "nocountry"
    return text, how
