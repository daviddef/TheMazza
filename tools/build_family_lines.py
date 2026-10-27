#!/usr/bin/env python3
"""The data behind the family ribbons (the kit's FamilyRibbon), written to site/src/data/family-lines.json.

David, 27 October 2026: every family page carries the mini horizontal tree the story draws, that family's own
generations, and under it HOW OUR LINE CONNECTS: one small block for each place the direct line touches the family.
The contract is the kit's (kit/docs/family-ribbon.md); the gate is kit/tools/checkfamilyribbon.py (npm run
check:familyribbon). Nothing here is typed: every card and every block is read from the archive's own data, so the
ribbons cannot drift from the pages they sit on.

THE FAMILY PAGES are the ones the menu lists (site/src/lib/familylist.js) except /mazza/: the Mazza name line IS our
line, and the story's own ribbon draws it. Arena and Nicotra are hand-built pages, the others come from [family].astro.

THE CARDS. One documented chain of the family's own generations, earliest first:
  * the bearers of the surname (or a spelling familylist.js groups with it) who are direct ancestors of the two
    children: the walk up the parent links from the four grandparents (quarters.json), the walk lib/families.js and
    tools/build_lines.py already make;
  * from the bearer nearest the children (a bearer whose ancestor child is not a bearer), up through the parent who
    bears the name. Where the family is a lane of /lines/ (lines.json), the lane's own order is followed; otherwise the
    longest such chain. A family with two or more chains is drawn by one of them, and the others are counted;
  * name and years as people.json holds them (the years the person's own page prints); "from" is the birth place,
    or "place not known"; the spouse is the other parent of the next generation down (for the last card, of the
    ancestor child, or the one spouse the data names), with "spouse not named in the records" where the data names
    none; "at <place>, <year>" is the place of death where it differs from the birth place.
  * THE OUTLINE is the evidence for "from": documented (solid) only where a register act for the person's own birth
    has been read (a register-only person, or a birth record that says "born", or a "Nati <year>" act of their own
    birth year); otherwise the family's tree (dotted). Where the story's ribbon names the person as a wife of our
    line, the story's place is used (it was read from the act: Maria Nicotra was born at Mascali, not Piedimonte).
  * nobody living is drawn: a family page names no living person (David, 16 October 2026; tools/check_familypages.py
    rule 4). The build stops if a living person is on a chain.

THE STATUS of a family is the lines page's rule (tools/build_lines.py) applied to the family's own chain.

HOW OUR LINE CONNECTS. Our line is src/data/direct-line.json, made by the kit from the story's ribbon (the Mazza name
line). A touch is one step from a person on it: the spouse (married), a parent (son of / daughter of), or a parent of
the spouse (shown as the marriage, with the spouse's parent named under the spouse). The family is the touched
person's surname. A touch whose either party is living is not drawn on a family page (the rule above) and is counted.
  * grade of a marriage: documented when a doc paragraph of our person's chapter in the story says they married, or a
    record both people carry names the other as wife or husband; otherwise the story card's own grade;
  * grade of a parent link: its `via` (read: documented; index: inferred; tree or none: the family's tree);
  * grade of a spouse's parent: the weaker of the marriage and her parent link.
A family that no deceased person of our line touches gets notConnected, and its `why` is worked out from the data:
which quarter it comes in through and how far from the name line.

Run from site/: python3 ../tools/build_family_lines.py (npm run familylines). --check compares instead of writing.
Reads only committed files, so CI can run it.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SITE = os.path.join(ROOT, "site")
D = os.path.join(SITE, "src", "data")
OUT = os.path.join(D, "family-lines.json")
STORY_BASE = "/story/"
RANK = {"doc": 3, "inf": 2, "lore": 1}
VIA_GRADE = {"read": "doc", "index": "inf", "tree": "lore"}


def load(name):
    return json.load(open(os.path.join(D, name), encoding="utf-8"))


def families_from_menu():
    """familylist.js, read the way tools/check_familypages.py reads it: hand-built and data-built, in menu order."""
    src = open(os.path.join(SITE, "src", "lib", "familylist.js"), encoding="utf-8").read()
    hand = src[src.index("export const HAND_BUILT"):src.index("export const BUILT")]
    built = src[src.index("export const BUILT"):src.index("export const FAMILY_MENU")]
    out = []
    for m in re.finditer(r'\{\s*slug:\s*"([^"]+)",\s*surname:\s*"([^"]+)",\s*href:\s*"([^"]+)"', hand):
        out.append({"slug": m.group(1), "surname": m.group(2), "also": [], "page": m.group(3)})
    for m in re.finditer(r'\{\s*slug:\s*"([^"]+)",\s*surname:\s*"([^"]+)",\s*also:\s*\[([^\]]*)\]', built):
        out.append({"slug": m.group(1), "surname": m.group(2), "also": re.findall(r'"([^"]+)"', m.group(3)),
                    "page": "/%s/" % m.group(1)})
    return out


def head(place):
    return (place or "").split(",")[0].strip()


def year_in(s):
    m = re.search(r"\b(1[5-9]\d\d|20\d\d)\b", str(s or ""))
    return m.group(1) if m else ""


def born_part(p):
    bt = str(p.get("bornText") or "")
    if p.get("born"):
        return ("c. " if re.match(r"(c\b|c\.|about)", bt) else "") + str(p["born"])
    if re.match(r"about", bt) and year_in(bt):
        return "c. " + year_in(bt)
    if re.match(r"before", bt) and year_in(bt):
        return "before " + year_in(bt)
    return ""


def died_part(p):
    dt = str(p.get("diedText") or "")
    if re.match(r"(alive|living)", dt, re.I):
        return ""                                   # a sighting, not a death
    if p.get("died"):
        return str(p["died"])
    if re.match(r"before", dt) and year_in(dt):
        return "before " + year_in(dt)
    if re.match(r"after", dt) and year_in(dt):
        return "after " + year_in(dt)
    return ""


def years_of(p):
    if p.get("living"):
        return ""
    b, d = born_part(p), died_part(p)
    if b and d:
        return ("%s – %s" if (" " in b or " " in d) else "%s–%s") % (b, d)
    if b:
        return "b. " + b
    if d:
        return "d. " + d
    return ""


def why_of(p):
    """The lane's own words for a person (tools/build_lines.py why_of)."""
    bits = []
    b = " ".join(x for x in (head(p.get("birthPlace")), str(p.get("bornText") or p.get("born") or "")) if x)
    if b:
        bits.append("born " + b)
    d = p.get("diedText") or p.get("died")
    if d and re.match(r"(alive|living)", str(d), re.I):
        bits.append(str(d))
    elif d:
        bits.append("died " + " ".join(x for x in (head(p.get("deathPlace")), str(d)) if x))
    return "%s: %s" % (p["name"], "; ".join(bits) if bits else "no date and no place in the archive")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="compare with the committed file instead of writing it")
    a = ap.parse_args()

    people = load("people.json")
    quarters = load("quarters.json")
    lines = load("lines.json")
    walls = load("walls.json")
    story = load("story.json")
    direct = load("direct-line.json")
    by_id = {p["id"]: p for p in people}
    by_slug = {p["slug"]: p for p in people}
    wall_names = {w["person"] for w in walls}
    ribbon = story["ribbon"]["cards"]
    chapters = {c["id"]: c for c in story.get("chapters", [])}
    story_spouse = {c["spousePerson"]: c for c in ribbon if c.get("spousePerson")}

    def reads(p):
        # the lines page's rule: a record has been read about the person (or a wall names them)
        return bool(p.get("fromRegister") or p.get("records") or p["name"] in wall_names)

    def birth_read(p):
        """A register act for the person's OWN birth has been read: the only ground for a solid "from"."""
        if p.get("fromRegister"):
            return True
        for r in p.get("records") or []:
            kind, what = str(r.get("kind", "")), str(r.get("what", ""))
            if kind in ("superseded", "flagged", "probable", "cited in the tree"):
                continue
            if "named as the" in what:
                continue
            if kind == "birth register" and re.search(r"\bborn\b", what):
                return True
            m = re.search(r"\bNati (\d{4}),? atto", what)
            if m and p.get("born") and int(m.group(1)) == p["born"]:
                return True
        return False

    def origin_of(p):
        if p["slug"] in story_spouse:                  # the story read it from the act
            so = re.sub(r"^of\s+", "", story_spouse[p["slug"]].get("spouseOrigin") or "")
            if so and so != "place not known":
                return so
        return head(p.get("birthPlace")) or "place not known"

    # ---- the direct ancestors (the walk lib/families.js and build_lines.py make) -------------------------------
    anc = set()
    gp_of = {}
    for q in quarters:
        gp = q["grandparent"]
        stack, seen = [gp["id"]], {gp["id"]}
        while stack:
            i = stack.pop()
            anc.add(i)
            gp_of.setdefault(i, []).append(gp["slug"])
            for par in (by_id.get(i) or {}).get("parents", []):
                if par["id"] not in seen:
                    seen.add(par["id"])
                    stack.append(par["id"])
    anc_slugs = {by_id[i]["slug"] for i in anc if i in by_id}
    lane_of = {}
    for lane in lines.get("lanes", []):
        for n in lane.get("nodes", []):
            if n.get("person"):
                lane_of[n["person"]] = (lane["key"], [x["person"] for x in lane["nodes"] if x.get("person")])

    def anc_children(p):
        return [by_slug[c["slug"]] for c in p.get("children", []) if c["slug"] in anc_slugs and c["slug"] in by_slug]

    def other_parent(child, parent_slug):
        ps = [x for x in child.get("parents", []) if x["slug"] != parent_slug]
        return by_slug.get(ps[0]["slug"]) if len(ps) == 1 else None

    # ---- our line ------------------------------------------------------------------------------------------------
    ours = {p["slug"]: p for p in direct.get("people", [])}
    ours.update({p["slug"]: p for p in direct.get("partners", [])})
    card_of = {c["person"]: c for c in ribbon if c.get("person")}

    def marriage_grade(our, their):
        """(grade, note) for a marriage of a person of our line."""
        card = card_of.get(our["slug"], {})
        ch = chapters.get(card.get("chapter"), {})
        given = their["name"].split()[0]
        for para in ch.get("paragraphs", []):
            t = para.get("text", "")
            if para.get("grade") == "doc" and re.search(r"\b[Mm]arried\b", t) and ("They married" in t or "(person:%s)" % their["slug"] in t):
                ev = (para.get("evidence") or [{}])[0].get("why", "")
                return "doc", re.sub(r"^«|»$", "", ev).strip() or "The story, chapter %s" % ch.get("numeral", "")
        theirs = {r.get("what") for r in their.get("records") or []}
        for r in our.get("records") or []:
            w = r.get("what", "")
            if w in theirs and re.search(r"\b(wife|husband)\b", w, re.I) and given in w:
                return "doc", "%s: %s" % (r.get("kind", "record").capitalize(), w)
        return card.get("originGrade", "lore"), "As the story's ribbon has it."

    PARENT_NOTE = {
        "read": "A register act names %s as %s %s.",
        "index": "An index names %s as %s %s.",
        "tree": "By the family's tree, %s is %s %s.",
    }

    def weaker(a, b):
        return a if RANK[a] <= RANK[b] else b

    def child_word(p):
        return {"M": "son of", "F": "daughter of"}.get(p.get("sex"), "child of")

    touches = {}          # family slug -> [connection]
    left_living = {}      # family slug -> count of touches through a living person
    fam_of_surname = {}
    menu = families_from_menu()
    for f in menu:
        for s in [f["surname"]] + f["also"]:
            fam_of_surname[s] = f["slug"]

    def add(fam, conn, living):
        if not fam:
            return
        if living:
            left_living[fam] = left_living.get(fam, 0) + 1
            return
        key = (conn["ourSlug"], conn["theirSlug"], conn["relation"])
        if any((c["ourSlug"], c["theirSlug"], c["relation"]) == key for c in touches.get(fam, [])):
            return
        touches.setdefault(fam, []).append(conn)

    for slug, e in ours.items():
        our = by_slug.get(slug)
        if not our:
            continue
        gen = e["generation"]
        href = "%s#%s" % (STORY_BASE, e.get("storyChapter", ""))
        our_name = e.get("name") or our["name"]
        # spouses: the story card's spouse first, then the people data's
        sp = []
        card = card_of.get(slug)
        if card and card.get("spousePerson") in by_slug:
            sp.append(by_slug[card["spousePerson"]])
        for s in our.get("spouses", []):
            if s["slug"] in by_slug and by_slug[s["slug"]] not in sp:
                sp.append(by_slug[s["slug"]])
        for s in sp:
            g, note = marriage_grade(our, s)
            fam = fam_of_surname.get(s.get("surname"))
            if fam != "mazza":
                add(fam, {"ourSlug": slug, "ourGeneration": gen, "ourName": our_name, "theirSlug": s["slug"],
                          "theirName": s["name"], "theirOrigin": "of " + origin_of(s) if origin_of(s) != "place not known" else "",
                          "relation": "married", "grade": g, "storyHref": href, "note": note},
                    our.get("living") or s.get("living"))
            # the spouse's parents
            for par in s.get("parents", []):
                pp = by_slug.get(par["slug"])
                if not pp:
                    continue
                pfam = fam_of_surname.get(pp.get("surname"))
                if pfam in (None, "mazza") or pfam == fam:
                    continue
                pg = VIA_GRADE.get(par.get("via"), "lore")
                rel = "mother" if pp.get("sex") == "F" else "father" if pp.get("sex") == "M" else "parent"
                add(pfam, {"ourSlug": slug, "ourGeneration": gen, "ourName": our_name, "theirSlug": s["slug"],
                           "theirName": s["name"], "theirOrigin": "%s %s" % (child_word(s), pp["name"]),
                           "relation": "married", "grade": weaker(g, pg), "storyHref": href,
                           "note": "%s %s" % (PARENT_NOTE.get(par.get("via"), PARENT_NOTE["tree"]) % (pp["name"], "her" if s.get("sex") == "F" else "his", rel),
                                              "The marriage: " + note[0].lower() + note[1:] if note else "")},
                    our.get("living") or s.get("living") or pp.get("living"))
        # parents
        for par in our.get("parents", []):
            pp = by_slug.get(par["slug"])
            if not pp:
                continue
            fam = fam_of_surname.get(pp.get("surname"))
            if fam == "mazza":
                continue
            rel = "mother" if pp.get("sex") == "F" else "father" if pp.get("sex") == "M" else "parent"
            add(fam, {"ourSlug": slug, "ourGeneration": gen, "ourName": our_name, "theirSlug": pp["slug"],
                      "theirName": pp["name"], "theirOrigin": "of " + origin_of(pp) if origin_of(pp) != "place not known" else "",
                      "relation": child_word(our), "grade": VIA_GRADE.get(par.get("via"), "lore"), "storyHref": href,
                      "note": PARENT_NOTE.get(par.get("via"), PARENT_NOTE["tree"]) % (pp["name"], "his" if our.get("sex") == "M" else "her", rel)},
                our.get("living") or pp.get("living"))

    # ---- each family ---------------------------------------------------------------------------------------------
    fams, report = [], []
    for f in menu:
        if f["slug"] == "mazza":
            continue                    # the name line itself: the story's ribbon draws it
        names = set([f["surname"]] + f["also"])
        bears = lambda p: p.get("surname") in names      # noqa: E731
        bearers = [by_id[i] for i in anc if i in by_id and bears(by_id[i])]
        if any(p.get("living") for p in bearers):
            sys.exit("build_family_lines: a living direct ancestor bears %s; a family page names no living person" % f["surname"])

        def up(p, seen=()):
            """the longest chain of bearers from p upward, earliest first"""
            best = []
            for par in p.get("parents", []):
                pp = by_slug.get(par["slug"])
                if pp and bears(pp) and pp["slug"] in anc_slugs and pp["slug"] not in seen:
                    c = up(pp, seen + (p["slug"],))
                    if len(c) > len(best) or (len(c) == len(best) and pp.get("sex") == "M"):
                        best = c
            return best + [p]

        terminals = [p for p in bearers if not any(bears(c) for c in anc_children(p))]
        chains = []
        for t in terminals:
            ch = up(t)
            lk = lane_of.get(t["slug"])
            if lk:                          # follow the lane's own order where the family is a lane of /lines/
                order = lk[1]
                i = order.index(t["slug"])
                lane_ch = []
                for s in reversed(order[:i + 1]):
                    if bears(by_slug[s]):
                        lane_ch.insert(0, by_slug[s])
                    else:
                        break
                if len(lane_ch) >= len(ch):
                    ch = lane_ch
            chains.append(ch)
        chains.sort(key=lambda c: (-len(c), c[-1].get("born") or 9999, c[-1]["slug"]))
        chain = chains[0] if chains else []

        cards = []
        for i, p in enumerate(chain):
            nxt = chain[i + 1] if i + 1 < len(chain) else None
            spouse = None
            if nxt:
                spouse = other_parent(nxt, p["slug"])
            else:
                kids = anc_children(p)
                if len(kids) == 1:
                    spouse = other_parent(kids[0], p["slug"])
                elif not kids:
                    dead_sp = [by_slug[s["slug"]] for s in p.get("spouses", []) if s["slug"] in by_slug]
                    spouse = dead_sp[0] if len(dead_sp) == 1 else None
            origin = origin_of(p)
            dplace = head(p.get("deathPlace"))
            at = dplace if dplace and dplace != origin and not p.get("living") else ""
            card = {
                "name": p["name"], "years": years_of(p), "origin": origin,
                "originGrade": "doc" if birth_read(p) else "lore",
                "spouse": "", "spouseOrigin": "", "atPlace": at, "atYear": str(p["died"]) if at and p.get("died") else "",
                "living": False, "person": p["slug"], "title": why_of(p),
            }
            if spouse and not spouse.get("living"):
                card["spouse"] = spouse["name"]
                so = origin_of(spouse)
                card["spouseOrigin"] = "of " + so if so != "place not known" else so
                card["spousePerson"] = spouse["slug"]
            else:
                card["spouse"] = "spouse not named in the records"
            cards.append(card)

        # status: the lines page's rule, on the family's own chain
        ev = [reads(p) for p in chain]
        first_read = next((i for i, x in enumerate(ev) if x), None)
        if first_read is None:
            status, note = "family-lore", "every generation drawn here rests on the family's tree"
        elif first_read > 0:
            status, note = "inferred", "%d %s above the oldest documented person %s on the family's tree alone" % (
                first_read, "generation" if first_read == 1 else "generations", "is" if first_read == 1 else "are")
        elif chain[0]["name"] in wall_names:
            status, note = "origin-unknown", "the registers stop at %s" % chain[0]["name"]
        else:
            status, note = "documented", "the oldest generation drawn is itself on a document"
        first_year = None
        if first_read is not None:
            for p in chain[first_read:]:
                y = year_in(born_part(p)) or year_in(died_part(p))
                if y:
                    first_year = int(y)
                    break

        fam = {"id": f["slug"], "title": f["surname"], "page": f["page"], "status": status, "statusNote": note}
        if first_year:
            fam["span"] = [first_year, None]
        fam["cards"] = cards
        conns = sorted(touches.get(f["slug"], []), key=lambda c: (c["ourGeneration"], c["relation"], c["theirSlug"]))
        if conns:
            fam["connections"] = conns
        else:
            fam["notConnected"] = {"why": why_not(f, chain, by_slug, anc_slugs, gp_of, by_id, quarters, left_living.get(f["slug"], 0))}
        fams.append(fam)
        report.append((f["slug"], len(cards), len(chains), len(conns), left_living.get(f["slug"], 0), status))

    out = {"_note": ("Made by tools/build_family_lines.py from people.json, quarters.json, lines.json, walls.json, the story and "
                     "direct-line.json; do not edit by hand. The contract is kit/docs/family-ribbon.md."),
           "families": fams}
    text = json.dumps(out, indent=1, ensure_ascii=False) + "\n"
    if a.check:
        cur = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        if cur != text:
            print("familylines: src/data/family-lines.json is not what the data makes; run npm run familylines")
            return 1
        print("familylines: in step (%d families)" % len(fams))
        return 0
    open(OUT, "w", encoding="utf-8").write(text)
    print("familylines: %d families; %s" % (len(fams), "; ".join(
        "%s %d gen%s%s, %d conn%s" % (s, n, "" if n == 1 else "s", " (of %d chains)" % k if k > 1 else "", c,
                                       " (%d through the living, not drawn)" % lv if lv else "")
        for s, n, k, c, lv, st in report)))
    return 0


def why_not(f, chain, by_slug, anc_slugs, gp_of, by_id, quarters, through_living):
    """Why a family is not connected, from the data: which quarter it comes in through, and how."""
    last = chain[-1] if chain else None
    if not last:
        return "The archive holds no direct ancestor of this name."
    gps = sorted(set(gp_of.get(last["id"], [])))
    if not gps:
        return "The archive holds no direct ancestor of this name."
    gp = by_slug[gps[0]]
    # the descent from the last of the name down to the grandparent of that quarter
    path, cur = [], last
    while cur["slug"] != gp["slug"]:
        kids = [by_slug[c["slug"]] for c in cur.get("children", []) if c["slug"] in by_slug and gps[0] in gp_of.get(by_slug[c["slug"]]["id"], [])]
        if not kids:
            break
        cur = kids[0]
        path.append(cur)
    link = "%s is " % last["name"]
    steps = []
    prev = last
    for p in path:
        steps.append("the %s of %s" % ("mother" if prev.get("sex") == "F" else "father" if prev.get("sex") == "M" else "parent", p["name"]))
        prev = p
    where = (link + ", ".join(steps) + ". ") if steps else ""
    spouse = next((by_slug[s["slug"]] for s in gp.get("spouses", []) if s["slug"] in by_slug), None)
    S = f["surname"]
    if through_living:
        return ("The %s meet the Mazza name line only in its living generations, which a family page does not name. %s" % (S, where)).strip()
    none = "No %s married a man of the Mazza name line or was a parent of one or of his wife" % S
    if spouse is not None and not spouse.get("living") and spouse.get("surname") == "Mazza":
        return ("%s: the %s come into the children's descent further back. %s%s married %s." % (
            none, S, where, gp["name"], spouse["name"])).strip()
    return ("%s: the %s come into the children's descent through %s, whose side meets that line only in its living "
            "generations. %s" % (none, S, gp["name"], where)).strip()


if __name__ == "__main__":
    sys.exit(main())
