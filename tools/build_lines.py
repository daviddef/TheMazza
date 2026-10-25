#!/usr/bin/env python3
"""The data behind the lines drawing on /lines/ (the kit's BranchRivers), written to site/src/data/lines.json.

THE LANES ARE THE FOUR QUARTERS. quarters.json already says which direct chain each grandparent's quarter
follows (the deepest line the archive can name), and /lines/ already prints those chains as lists. This draws
the same chains as lanes, one per quarter, and adds what the kit's contract asks of a lane:

  nodes    every person of the chain (q.line), linked to the person's own page. A node rests on `read` when the
           person's page says so (a register act in `fromRegister` or `records`: the rule personpage.js
           applies, so a dot and the page it links to cannot disagree), or when walls.json names the person: a
           wall is established by reading, and the wall person is the last one the registers reach. Otherwise
           `tree`, which the drawing draws hollow.
  span     [first documented year, null]: the year of the oldest node that rests on a document.
  status   from the lane's own evidence and nothing else:
             inferred        generations of the chain stand ABOVE the oldest documented one, on the family tree
                             alone (Briatico: Pasquale Prostamo is the wall, the two above him are the chart's);
             origin-unknown  the oldest documented person is named by walls.json: the registers stop at him
                             (the Donato wall at Scilla);
             documented      otherwise: the top of the chain is itself on a document.
           These are PROPOSALS read from walls.json and the person pages. A status is a research decision;
           the file says which rule gave each one (`statusWhy`, not drawn) so David can overrule it.
  members  the other dead direct ancestors of the grandparent (the walk up the parent links that
           lib/families.js already uses to say which quarter a person is an ancestor of), so each lane counts
           its people. No person is an ancestor of two quarters (the build stops if one is).

THE PENS are what is on no lane, and they are the archive's own pieces (the /components/ page counts them the
same way, with the same union-find):

  register-alone   people proved by a register act and absent from the export (people.json comp is null) who sit
                   in small groups that no parent, child or marriage link joins to anyone in the export:
                   real people, not yet placed on a line.
  tree-only        the Mazzitelli of New York: entered in the same tree and attached to this family by nothing
                   (the /components/ page's own words): kept apart until an act joins them.

NOBODY LIVING IS EVER LISTED. A living person has no node, no member and no pen entry here; the gate
(checklines.py --living) fails the build if one gets in. The numbers in every note are counted here from the data,
never typed.

Run from site/: python3 ../tools/build_lines.py   (npm run lines). Reads only committed files, so CI can run it.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
D = os.path.join(ROOT, "site", "src", "data")


def load(name):
    return json.load(open(os.path.join(D, name), encoding="utf-8"))


# The words the page prints beside a lane. Source for each: the archive's own evidence pages, named here so a
# reader can check the note against its source (the numbers in them are counted below, never typed).
LANE_META = [
    # key, colour, the grandparent whose quarter it is (quarters.json), the page the quarter is argued on
    # (book.json: the quarter's group), read-text
    ("piedimonte-etneo", "var(--accent)", "sebastiano-mazza", "/mazza/", "The Mazza page →"),
    ("briatico", "var(--st-running)", "domenica-prostamo", "/prostamo/", "The Prostamo page →"),
    ("scilla-arena", "var(--terra)", "rocco-arena-1924", "/arena/", "The Arena page →"),
    ("scilla-polistena", "var(--ochre)", "angela-polistena", "/polistena/", "The Polistena page →"),
]
# What stands at the top of each lane and where the archive says so. Reasons only: the tier is derived below.
TOP_NOTE = {
    "piedimonte-etneo": "to Simone Nicotra, named in his son's death act (documented-line.json, Mascali Morti 1890 atto 35)",
    "briatico": "the generations above Pasquale Prostamo are the family tree's alone (walls.json; /briatico-tested/)",
    "scilla-arena": "to Filippo Arena, named in his son Orazio's death act (documented-line.json, Scilla Morti 1830 atto 64)",
    "scilla-polistena": "Candeloro Donato's own birth and marriage pre-date Scilla's registers (walls.json)",
}
# Short forms of the notes as the page prints them (the status line is limited to 100 characters).
PRINT_NOTE = {
    "piedimonte-etneo": "to Simone Nicotra, named in his son's death act",
    "briatico": "the generations above Pasquale are the family tree's alone",
    "scilla-arena": "to Filippo, named in his son Orazio's death act",
    "scilla-polistena": "Candeloro's birth and marriage pre-date Scilla's registers",
}


def head(place):
    return (place or "").split(",")[0].strip()


def main():
    people = load("people.json")
    quarters = load("quarters.json")
    walls = load("walls.json")
    comps = load("components.json")
    by_id = {p["id"]: p for p in people}
    by_slug = {p["slug"]: p for p in people}
    wall_names = {w["person"] for w in walls}

    def reads(p):
        # the person page's own rule (site/src/lib/personpage.js wordOf), plus the wall person
        return bool(p.get("fromRegister") or p.get("records") or p["name"] in wall_names)

    def year_of(p):
        if not p.get("born"):
            return ""
        return ("c. " if str(p.get("bornText") or "").startswith("c") else "") + str(p["born"])

    def why_of(p):
        bits = []
        b = " ".join(x for x in (head(p.get("birthPlace")), str(p.get("bornText") or p.get("born") or "")) if x)
        if b:
            bits.append("born " + b)
        d = p.get("diedText") or p.get("died")
        if d and re.match(r"(alive|living)", str(d), re.I):
            bits.append(str(d))                      # «alive at Scilla, July 1844»: a sighting, not a death
        elif d:
            bits.append("died " + " ".join(x for x in (head(p.get("deathPlace")), str(d)) if x))
        return "; ".join(bits) if bits else "no date and no place in the archive"

    lanes, used = [], {}
    for q, (key, colour, gp_slug, href, read) in zip(quarters, LANE_META):
        gp = q["grandparent"]
        if gp["slug"] != gp_slug:
            sys.exit("build_lines: quarters.json lists %s where the lane %s expects %s" % (gp["slug"], key, gp_slug))
        chain = [by_slug[r["slug"]] for r in q["line"]]
        if any(p["living"] for p in chain):
            sys.exit("build_lines: a living person is on the chain of %s; the lines drawing never lists one" % key)
        nodes = []
        prev_surname = None
        for p in chain:
            # the label over the dot: the given name, and the surname only where it changes along the lane (eight full
            # names do not fit a lane); the full name is the link's own page and the reading panel's text
            given = p["name"].split()[0] if p["name"] else ""
            label = given if prev_surname is None or p.get("surname") == prev_surname else given + " " + (p.get("surname") or "")
            prev_surname = p.get("surname")
            nodes.append({"place": label, "year": year_of(p), "why": "%s: %s" % (p["name"], why_of(p)),
                          "person": p["slug"], "evidence": "read" if reads(p) else "tree"})
        first_read = next((i for i, n in enumerate(nodes) if n["evidence"] == "read"), None)
        wall_top = first_read is not None and chain[first_read]["name"] in wall_names
        if first_read is None:
            sys.exit("build_lines: nothing on the %s chain rests on a document" % key)
        if first_read > 0:
            status, rule = "inferred", "%d generation(s) above the oldest documented person are on the family tree alone" % first_read
        elif wall_top:
            status, rule = "origin-unknown", "the oldest person on the chain is the person a wall in walls.json names"
        else:
            status, rule = "documented", "the oldest person on the chain is itself on a document and no wall names them"
        first_year = next((int(re.search(r"\d{4}", n["year"]).group(0)) for n in nodes
                           if n["evidence"] == "read" and re.search(r"\d{4}", n["year"])), None)

        # members: the other direct ancestors of the grandparent, dead only
        seen, stack = {gp["id"]}, [gp["id"]]
        while stack:
            p = by_id.get(stack.pop())
            for par in (p or {}).get("parents", []):
                if par["id"] not in seen:
                    seen.add(par["id"])
                    stack.append(par["id"])
        node_slugs = {n["person"] for n in nodes}
        members = sorted((by_id[i] for i in seen if i in by_id and not by_id[i]["living"] and by_id[i]["slug"] not in node_slugs),
                         key=lambda p: (p.get("born") or 9999, p["name"], p["slug"]))
        for p in members:
            if p["slug"] in used:
                sys.exit("build_lines: %s is an ancestor of two quarters (%s and %s); decide which lane holds them (sharedAllowed)" % (p["slug"], used[p["slug"]], key))
            used[p["slug"]] = key

        lane = {"key": key, "colour": colour,
                "label": "%s — %s" % (head(q["town"]), gp["name"]),
                "href": href, "read": read,
                "status": status, "statusNote": PRINT_NOTE[key],
                "span": [first_year, None] if first_year else None,
                "statusWhy": "%s: %s. Source: %s" % (rule, status, TOP_NOTE[key]),
                "members": [p["slug"] for p in members],
                "nodes": nodes, "ends": []}
        if lane["span"] is None:
            del lane["span"]
        lanes.append(lane)

    # ---- the pens: the pieces the /components/ page counts, with the same union-find ----
    parent = {p["id"]: p["id"] for p in people}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for p in people:
        for k in ("parents", "children", "spouses"):
            for o in p.get(k, []):
                if o["id"] in parent:
                    parent[find(p["id"])] = find(o["id"])
    root_has_comp = {find(p["id"]) for p in people if p.get("comp") is not None}
    reg_alone = [p for p in people if p.get("comp") is None and find(p["id"]) not in root_has_comp]
    groups = {}
    for p in reg_alone:
        groups[find(p["id"])] = groups.get(find(p["id"]), 0) + 1
    singles = sum(1 for n in groups.values() if n == 1)
    alone = sorted((p for p in reg_alone if not p["living"]), key=lambda p: (p["name"], p["slug"]))
    for p in alone:
        if p["slug"] in used:
            sys.exit("build_lines: %s is on a lane and in the register-alone pen" % p["slug"])
        used[p["slug"]] = "register-alone"

    ny = next((c for c in comps if any(s["name"] == "Mazzitelli" for s in c.get("surnames", []))), None)
    ny_people = sorted((by_slug[x["slug"]] for x in (ny or {}).get("people", []) if x["slug"] in by_slug and not by_slug[x["slug"]]["living"]),
                       key=lambda p: (p.get("born") or 9999, p["name"], p["slug"]))
    for p in ny_people:
        if p["slug"] in used:
            sys.exit("build_lines: %s is in two places" % p["slug"])
        used[p["slug"]] = "tree-only"

    pens = []
    if alone:
        pens.append({
            "id": "register-alone", "kind": "not-yet-placed",
            "head": "Proved by a register, in groups joined to nothing",
            "note": ("A register act this archive has read names each of them, and none is joined by a parent, child or marriage link to anyone "
                     "in the export. They sit in %d small groups, %d of them one person. They are real people the archive has not yet placed, "
                     "and none is drawn on a line until an act joins them to one." % (len(groups), singles)),
            "members": [p["slug"] for p in alone], "count": len(alone)})
    if ny_people:
        ys = [p["born"] for p in ny_people if p.get("born")]
        pens.append({
            "id": "tree-only", "kind": "different-stock",
            "head": "Entered in the same tree, attached to nothing",
            "note": ("The Mazzitelli of %s: %d people%s, joined to this family by nothing but having been typed into the same tree. "
                     "Kept apart until an act joins them." % (head((ny.get("towns") or [{"name": "New York"}])[0]["name"]), len(ny_people),
                                                                (", born %d to %d" % (min(ys), max(ys))) if ys else "")),
            "members": [p["slug"] for p in ny_people], "count": len(ny_people)})

    out = {
        "title": "The lines of descent, and the people who are on none of them",
        "caption": ("Each lane is the deepest chain of one grandparent's quarter. The line under its title says how far back its evidence reaches: "
                    "a dotted lead-in is an origin inferred, a dashed one ends in an open ring where the origin has not been found, and a hollow dot is a "
                    "person the archive holds on the family tree alone. "
                    "Under the lanes, the people who are on none of them."),
        "lanes": lanes, "pens": pens, "bridges": [],
    }
    path = os.path.join(D, "lines.json")
    json.dump(out, open(path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    open(path, "a").write("\n")
    print("lines: %d lanes (%s), %d lane members, %d pens (%s)" % (
        len(lanes), ", ".join("%s %s" % (l["key"], l["status"]) for l in lanes), sum(len(l["members"]) for l in lanes),
        len(pens), "; ".join("%s %d" % (p["id"], p["count"]) for p in pens)))


if __name__ == "__main__":
    main()
