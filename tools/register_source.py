#!/usr/bin/env python3
"""The second source: people this archive proved from a register.

data/documented-additions.tsv holds people who exist in an act and have never
existed in the family's file. Until 9 October 2026 they were a parallel world.
They were drawn on /tree/ as cards, listed on /lines/, and counted on
/ancestors/ only after that page was taught to add them — and they had no
person page, no entry in /who/, no row in the search index, and no node in the
bloodline graph, because every one of those things is built from people.json
and people.json was the export.

So the archive could say «Rosario Nicotra, bracciante of Mascali, father of
Giovanni, named in Piedimonte Matrimoni 1872 atto 20» on four pages and still
answer a search for Rosario Nicotra with the 1883 child of the same name, the
only one the export happened to carry.

This module turns those rows into records of the same shape build.py makes from
the GEDCOM, so that everything downstream treats them as what they are: people.
build.py owns the slug ledger and the relationship wiring and calls in here; the
records are marked «fromRegister» so that no page can imply the export held
them. The export and the registers stay distinguishable at every point. That
distinction is the archive's subject, and merging the two silently would destroy
exactly the thing it exists to show.

WHAT IS DELIBERATELY NOT DONE HERE:

  * No row is invented. A parent named on an act whose own row does not exist
    gets no record and no edge — fifteen names are in that position, and they
    are named in an act and nowhere else. Creating them would be the archive
    asserting a person it has not filed.
  * A parent name is matched to a row EXACTLY, never by resemblance. «Orazio
    Arena» and «Orazio Arena (b. c. 1751)» may well be one man; the archive
    does not attach on «may well be», and build_documented_parents.py's bare()
    fallback is not reused here for that reason.
  * A qualified date is not flattened into a year. «before 7 October 1872» is
    a bound, not a date, and 66 of these dates are bounds. born/died carry an
    integer ONLY for a date that states one; the text is always kept, and the
    pages show the text. Setting died=1872 for a man who died before 1872
    would publish a fact the act does not support, and the age checks would
    compute from it.
"""
import csv, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
TSV = os.path.join(HERE, "..", "data", "documented-additions.tsv")

# Surname particles: «Maria de Amico» is an Amico of the de Amico, and her
# surname is «de Amico». Taking the last word alone would file her under A.
PARTICLES = {"de", "di", "da", "del", "della", "dello", "la", "le", "lo", "li"}


def blank(v):
    return (v or "").strip() in ("", "—")


def clean(name):
    """The name without its filing parenthesis.

    build_documented_parents.py settled this already: «the parenthesis is a
    filing device, not a name». «Mariano Mazza (b. c. 1809)» is distinguished
    from the tree's later namesake for the file's sake, not the reader's. The
    full row name stays on the record as «key», because it is the identifier
    the additions file and parent-links use.
    """
    return re.sub(r"\s*\(.*?\)", "", name or "").strip()


def year(s):
    """A four-figure year if the string states one, else None."""
    m = re.search(r"\b(1[5-9]\d{2}|20\d{2})\b", s or "")
    return int(m.group(1)) if m else None


def exact(s):
    """True when the date is a date, not a bound or an estimate.

    «1848» and «25 November 1819» state a year. «before 1779», «after 16 April
    1871», «c. 1841» and «alive at Scilla, July 1844» do not, and an integer
    taken from them would read on the page as though they did.
    """
    s = (s or "").strip()
    if blank(s):
        return False
    return not re.match(r"^\s*(before|after|c\.|circa|about|by|alive)\b", s, re.I)


def rows():
    """Every addition row, in file order."""
    with open(TSV, encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def to_create(allrows=None):
    """The rows that are not already a person in the family's file.

    A row with «inTree» names an export person and is a statement ABOUT them —
    their parents, their trade, their act. Those rows must not become a second
    copy of a person who already has a page.
    """
    return [r for r in (allrows or rows()) if blank(r.get("inTree"))]


def surname_of(name):
    parts = clean(name).split()
    if len(parts) < 2:
        return parts[-1] if parts else ""
    if len(parts) >= 3 and parts[-2].lower() in PARTICLES:
        return " ".join(parts[-2:])
    return parts[-1]


def sexes(allrows=None):
    """{row name: "M"|"F"} for anyone named as a father or a mother.

    Inferred from the role an act gives them and nothing else. A person named
    in no parental role gets no sex, because the row does not say.
    """
    out = {}
    for r in (allrows or rows()):
        if not blank(r.get("father")):
            out.setdefault(r["father"].strip(), "M")
        if not blank(r.get("mother")):
            out.setdefault(r["mother"].strip(), "F")
    return out


def record(r, pid, slug, sex=""):
    """One person, in the shape build.py's record() makes from the GEDCOM."""
    name = clean(r["name"])
    born_t = "" if blank(r.get("born")) else r["born"].strip()
    died_t = "" if blank(r.get("died")) else r["died"].strip()
    place = "" if blank(r.get("place")) else r["place"].strip()
    trade = "" if blank(r.get("trade")) else r["trade"].strip()
    srcs = [s.strip() for s in re.split(r";\s*", r.get("source") or "") if s.strip()]

    events = []
    if born_t or place:
        events.append({"what": "born", "tag": "BIRT",
                       "date": born_t if exact(born_t) else "",
                       "year": year(born_t) if exact(born_t) else None,
                       "place": place, "text": born_t})
    if died_t:
        events.append({"what": "died", "tag": "DEAT",
                       "date": died_t if exact(died_t) else "",
                       "year": year(died_t) if exact(died_t) else None,
                       "place": "", "text": died_t})

    return {
        "id": pid,
        "slug": slug,
        "name": name,
        "key": r["name"].strip(),
        "given": clean(r["name"]).split()[0] if clean(r["name"]) else "",
        "surname": surname_of(r["name"]),
        "sex": sex,
        "living": False,
        "presumedLiving": False,
        # NO COMPONENT. /components/ is about the pieces the EXPORT arrived in
        # and this person was never in it. build_components.py skips them and
        # the person page must not say «component N of the export» of someone
        # the export never held.
        "fromRegister": True,
        "datesHidden": False,
        "born": year(born_t) if exact(born_t) else None,
        "died": year(died_t) if exact(died_t) else None,
        "bornText": born_t,
        "diedText": died_t,
        "events": events,
        "birthPlace": place,
        "deathPlace": "",
        "burialPlace": "",
        "trade": trade,
        "sources": [],
        "registerSources": srcs,
        "registerNote": "" if blank(r.get("note")) else r["note"].strip(),
        "registerGen": r.get("gen", "").strip(),
        "photos": [],
    }


def edges(allrows=None):
    """(child row name or export slug, parent row name) pairs the acts state.

    Two kinds, and both matter:
      * an addition's own parents, which is how the Arena chain climbs from
        Francesco Antonio to Filippo to Orazio to Filippo the elder;
      * an EXPORT person's parents, from a row whose «inTree» names them —
        this is the join that was missing, and it is why /ancestors/ drew
        «John Nicotra — —» and then began the next generation without him.
    """
    out = []
    for r in (allrows or rows()):
        child = r["inTree"].strip() if not blank(r.get("inTree")) else r["name"].strip()
        kind = "slug" if not blank(r.get("inTree")) else "name"
        for col in ("father", "mother"):
            if not blank(r.get(col)):
                out.append((kind, child, r[col].strip()))
    return out
