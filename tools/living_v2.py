"""Mazza's adapter to the estate's one definition of who is living.

The DEFINITION is not here. It is the kit's `living_rule.py` (David, 16 October
2026), imported from the pinned kit, and this file only supplies what that rule
needs and this archive alone can say: where a person's citations are, and what
counts in THIS archive as a recorded death or burial.

  LIVING   80 or younger by year, no death or burial recorded, and no citation
           from a public record source (FamilySearch, MyHeritage records,
           Findmypast...). Someone with no birth year is not living by this test.
  HELD OUT a possible minor: not published at all (no page, no name, no photograph).
           Two tests, both held here and NOT in the kit (David, 25 October 2026):
             * the kit's: an undated person with a living parent (not recorded dead,
               no public source, no birth year);
             * ours, `possible_minors` below: a person under 18 by year (born
               this_year - 18 or later) with no death recorded, or an UNDATED person
               with a parent born 1975 or later and no death recorded.
           David ruled on 16 October that a child with a KNOWN birth year follows the
           standard of any living person and has a page; on 25 October he ruled that
           possible minors are not published at all. The kit's living_rule.possible_minor
           still carries the 16 October exemption and cannot be edited from here, so the
           supplement is this archive's and is reported as a kit gap.

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


def ged_death_kind(indi):
    """What a GEDCOM INDI node holds about a death: "record", "flag" or None (the kit's death_kind).

    record : a DEAT with a date, a place, an age at death or a source, or any BURI (a burial).
    flag   : a DEAT that is only the yes-flag (`1 DEAT Y`, at most a note): the tree's belief with nothing
             behind it. For a person born in the window it is NOT a death (they stay living); for an
             undated person it means dead (kit living_rule, 25 October 2026).
    The node shape is tools/ged.py's: {"tag", "val", "kids"}. One function for the generator, the
    prose feed and the gate, so a flag is classed the same way everywhere.
    """
    def kid_val(n, tag):
        k = next((c for c in n.get("kids", []) if c["tag"] == tag), None)
        return (k["val"] or "").strip() if k else ""
    deat = [n for n in indi.get("kids", []) if n["tag"] == "DEAT"]
    buri = [n for n in indi.get("kids", []) if n["tag"] == "BURI"]
    return lr.death_kind(
        died=next((kid_val(n, "DATE") for n in deat if kid_val(n, "DATE")), None),
        death_place=next((kid_val(n, "PLAC") for n in deat if kid_val(n, "PLAC")), None),
        dead_flag=bool(deat),
        # a burial is a register line that records a death, undated or not (the word "buried" alone would read as a flag)
        death_recorded=bool(buri) or any(c["tag"] in ("AGE", "SOUR") for n in deat for c in n.get("kids", [])))


def youngest_child_years(people):
    """{parent id: birth year of that parent's youngest child with a known birth year}.

    Taken from the archive's own parent edges (people[id]["parents"]), so a child's year counts
    for each parent the archive records. A child with no birth year counts for nothing.
    """
    out = {}
    for _id, p in people.items():
        if p["by"] is None:
            continue
        for q in p["parents"]:
            if q not in out or p["by"] > out[q]:
                out[q] = p["by"]
    return out


def cites_for_living(p):
    """The citations the LIVING test may see for a person.

    ROOT CAUSE of the 25 October 2026 leak (a man born 1948, 78 years old, no death, published
    as dead with his year, parents, spouse and children): the kit's `living_rule.is_living`
    returns False for ANY person with a public-source citation, whatever their birth year, on
    the reasoning that "what that source says may be shown". A passenger-index line (the
    National Archives of Australia, which the kit lists as public) was enough to make a person
    80 or younger "not living". A public source can show that someone was born or arrived; it
    cannot show that they are dead, and David's rule is 80 or younger with no death recorded.

    So for a person WITH a birth year the citations are not passed: the year and the absence
    of a death decide, alone. An UNDATED person is unchanged (a public source still releases
    the recent-child inference, which is only an inference). The kit is not edited; the gap in
    its rule is reported. Same function for the generator and the gate.
    """
    return [] if p["by"] is not None else p["cites"]


# ---- possible minors (David, 25 October 2026): NOT PUBLISHED AT ALL -----------------------------
MINOR_AGE = 18               # under 18 by year: born this_year - 18 or later (2008 in 2026)
PARENT_YEAR_FLOOR = 1975     # an undated person whose parent was born in or after this year may be a child


def minor_cutoff_year(today_year=None):
    """Born in this year or later is a possible minor (2008 in 2026); one derived number, never typed."""
    return int(today_year or lr.this_year()) - MINOR_AGE


def possible_minors(people, today_year=None):
    """Ids of the possible minors: held out whatever the kit's rule says.

    people: the same {id: {"by", "dead", "undated_dead", "parents", ...}} classify() takes.

    ROOT CAUSE of the 25 October 2026 leak (eight children, each with a known birth year, were published by
    name with a page, and two of them were the anchors the whole archive was built on): the kit's
    `living_rule.possible_minor` holds out only an UNDATED person with a living parent, and says in
    so many words that a child with a known birth year follows the living standard (David, 16
    October). That ruling was superseded on 25 October. Here the test is the child's own year, or,
    for an undated person, the parent's: born 2008 or later, or undated with a parent born 1975 or
    later. A recorded death takes a person out of it (a dead child is an ordinary page), and so
    does an undated bare death flag (the kit's own reading: for the undated it means dead).
    """
    y = today_year or lr.this_year()
    floor = minor_cutoff_year(y)
    out = set()
    for i, p in people.items():
        if p["dead"]:
            continue
        if p["by"] is not None:
            if p["by"] >= floor:
                out.add(i)
        elif not p.get("undated_dead", False):
            for q in p["parents"]:
                qy = people.get(q, {}).get("by")
                if qy is not None and qy >= PARENT_YEAR_FLOOR:
                    out.add(i)
                    break
    return out


def classify(people, today_year=None):
    """people: {id: {"by": int|None, "dead": bool, "cites": [str], "parents": [id], "undated_dead": bool}}

    "dead" is a death RECORD only (a date, a place, a burial, a register line). "undated_dead" is the
    tree's bare death FLAG (kit living_rule, 25 October 2026): it frees nobody born in the window.

    Returns (living, held_out) as sets of ids. Living is computed first, because
    a possible minor with no birth year is defined by a living parent. The kit's held-out set is
    then widened by `possible_minors` (25 October 2026), and those people are not living here:
    they are not published, so nothing downstream may treat them as a living person.

    RECENT CHILD (17 October 2026, kit living_rule 26a4cba): an UNDATED person with no recorded
    death and no public source whose youngest child with a known birth year was born 60 years ago
    or less is an adult parent, so LIVING (name, relationships, town and country; not held out).
    The year comes from the archive's own parent edges (youngest_child_years).
    """
    y = today_year or lr.this_year()
    yc = youngest_child_years(people)
    living = {i for i, p in people.items()
              if lr.is_living(p["by"], p["dead"], cites_for_living(p), y, yc.get(i),
                              undated_dead=p.get("undated_dead", False))}
    held = set()
    for i, p in people.items():
        pl = any(q in living for q in p["parents"])
        if lr.is_held_out(i, p["by"], p["dead"], p["cites"], pl, (), y, yc.get(i),
                          undated_dead=p.get("undated_dead", False)):
            held.add(i)
    held |= possible_minors(people, y)
    return living - held, held


def selfcheck(today_year=2026):
    """Planted cases for the recent-child rule, on invented people (no private data, so it runs in CI).
    Returns a list of what is wrong; empty when every case holds."""
    bad = []
    pub = ["a public record"]

    def P(by=None, dead=False, cites=(), parents=(), flag=False):
        return {"by": by, "dead": dead, "cites": list(cites), "parents": list(parents), "undated_dead": flag}

    def run(people):
        return classify(people, today_year)

    # an undated parent whose youngest dated child is 20 years old is living, and not held out
    L, H = run({"p": P(), "k": P(today_year - 20, parents=["p"])})
    if "p" not in L or "p" in H:
        bad.append("an undated parent of a recent child is not living")
    # the child's year is the youngest: a 70-year-old child and a 30-year-old child, the younger counts
    L, H = run({"p": P(), "old": P(today_year - 70, parents=["p"]), "k": P(today_year - 30, parents=["p"])})
    if "p" not in L:
        bad.append("the youngest child's year was not the one used")
    # a child born 61 years ago (60 is the bound) leaves the parent not living
    L, H = run({"p": P(), "k": P(today_year - 61, parents=["p"])})
    if "p" in L:
        bad.append("a child born more than 60 years ago made an undated parent living")
    L, H = run({"p": P(), "k": P(today_year - 60, parents=["p"])})
    if "p" not in L:
        bad.append("a child born exactly 60 years ago did not make an undated parent living")
    # no child, or a child with no birth year: nothing changes (the default)
    L, H = run({"p": P(), "k": P(None, parents=["p"])})
    if "p" in L:
        bad.append("an undated child made an undated parent living")
    # a public source does NOT make a dated person 80 or younger with no death "not living" (25 October 2026)
    L, H = run({"p": P(today_year - 78, cites=pub + ["FamilySearch", "recordsearch.naa.gov.au"])})
    if "p" not in L:
        bad.append("a public-source citation made a person aged 78 with no death not living")
    L, H = run({"p": P(today_year - 80, cites=pub)})
    if "p" not in L:
        bad.append("a person aged exactly 80 with a public source is not living")
    L, H = run({"p": P(today_year - 81, cites=pub)})
    if "p" in L:
        bad.append("a person aged 81 was made living")
    L, H = run({"p": P(today_year - 78, dead=True, cites=pub)})
    if "p" in L:
        bad.append("a recorded death did not override the 80-year rule")
    # a recorded death, or a public source on an UNDATED person, still means not living
    L, H = run({"p": P(dead=True), "k": P(today_year - 20, parents=["p"])})
    if "p" in L:
        bad.append("a recorded death did not override the recent-child rule")
    L, H = run({"p": P(cites=pub + ["FamilySearch"]), "k": P(today_year - 20, parents=["p"])})
    if "p" in L:
        bad.append("a public source did not override the recent-child rule")
    # an undated parent of a recent child whose own parent is OLD (born before 1975) is an adult: living, NOT a possible minor
    L, H = run({"g": P(today_year - 70), "p": P(parents=["g"]), "k": P(today_year - 5, parents=["p"])})
    if "p" not in L or "p" in H:
        bad.append("an undated parent of a recent child with an old living parent was held out, not made living")
    # but an undated person whose parent was born in 1975 or later is a possible minor whatever else is known (25 Oct 2026)
    L, H = run({"g": P(today_year - 50), "p": P(parents=["g"]), "k": P(today_year - 5, parents=["p"])})
    if "p" not in H or "p" in L:
        bad.append("an undated person with a parent born in 1975 or later was published (a possible minor)")
    # an undated person with a living parent and no child is still a possible minor
    L, H = run({"g": P(today_year - 50), "p": P(parents=["g"])})
    if "p" not in H or "p" in L:
        bad.append("an undated person with a living parent and no child is no longer held out")
    # a bare death FLAG (the tree says "deceased", nothing behind it) frees nobody born in the window
    # (kit living_rule, 25 October 2026); it still means dead for an undated person and for anyone older
    L, H = run({"p": P(today_year - 78, flag=True)})
    if "p" not in L:
        bad.append("a bare death flag made a person aged 78 not living")
    L, H = run({"p": P(today_year - 80, flag=True)})
    if "p" not in L:
        bad.append("a bare death flag made a person aged exactly 80 not living")
    L, H = run({"p": P(today_year - 81, flag=True)})
    if "p" in L:
        bad.append("a person aged 81 with a death flag was made living")
    L, H = run({"p": P(flag=True), "k": P(today_year - 20, parents=["p"])})
    if "p" in L or "p" in H:
        bad.append("an undated person with a death flag was made living or held out")
    L, H = run({"p": P(today_year - 78, flag=True, dead=True)})
    if "p" in L:
        bad.append("a death record beside a flag did not make a person aged 78 not living")
    # the GEDCOM classing of a death: a bare yes-flag is a flag, a date or place or any burial is a record
    def node(tag, val="", kids=()):
        return {"tag": tag, "val": val, "kids": list(kids)}
    for nodes, want in (([node("DEAT", "Y")], "flag"),
                        ([node("DEAT", "Y", [node("NOTE", "Spanish Flu")])], "flag"),
                        ([node("DEAT", "Y", [node("DATE", "1918")])], "record"),
                        ([node("DEAT", "Y", [node("PLAC", "Scilla")])], "record"),
                        ([node("DEAT", "Y", [node("AGE", "70y")])], "record"),
                        ([node("BURI", "", [node("PLAC", "Scilla")])], "record"),
                        ([node("BURI")], "record"),
                        ([], None)):
        if ged_death_kind({"kids": nodes}) != want:
            bad.append(f"a GEDCOM death of {[n['tag'] for n in nodes]} was not classed {want}")
    # a dated person is judged by their own year alone
    L, H = run({"p": P(today_year - 90), "k": P(today_year - 20, parents=["p"])})
    if "p" in L:
        bad.append("a dated person was made living by a child's year")
    # POSSIBLE MINORS (David, 25 October 2026): not published at all, a known birth year or not
    cut = minor_cutoff_year(today_year)
    L, H = run({"p": P(today_year - 40), "k": P(cut, parents=["p"])})
    if "k" not in H or "k" in L:
        bad.append("a child born in the cutoff year was published")
    L, H = run({"p": P(today_year - 40), "k": P(cut - 1, parents=["p"])})
    if "k" in H or "k" not in L:
        bad.append("a person born the year before the cutoff was held out (an adult is living)")
    L, H = run({"p": P(today_year - 40), "k": P(today_year - 8, parents=["p"], flag=True)})
    if "k" not in H:
        bad.append("a bare death flag freed a dated child")
    L, H = run({"p": P(today_year - 40), "k": P(today_year - 8, dead=True, parents=["p"])})
    if "k" in H:
        bad.append("a child with a recorded death was held out (a dead child is an ordinary page)")
    L, H = run({"p": P(PARENT_YEAR_FLOOR), "k": P(parents=["p"], cites=pub + ["FamilySearch"])})
    if "k" not in H:
        bad.append("an undated child of a parent born in the floor year was published (a public source frees nobody here)")
    L, H = run({"p": P(today_year - 130), "k": P(parents=["p"])})
    if "k" in H:
        bad.append("an undated person whose parent was born long before the floor year was held out as a minor")
    L, H = run({"p": P(PARENT_YEAR_FLOOR), "k": P(parents=["p"], flag=True)})
    if "k" in H:
        bad.append("an undated person with a death flag was held out as a minor")
    return bad


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
