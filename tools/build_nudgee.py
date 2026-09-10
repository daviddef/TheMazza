#!/usr/bin/env python3
"""Turn the cemetery matches into a documented evidence layer.

The family tree is not edited. The register is a SEPARATE, better source, and
where the two disagree the site shows both and says which it believes and why.
That is what "superseded" means in the method, and it is the whole point of
keeping the export and the evidence apart.
"""
import json, re

M = json.load(open("data/nudgee-matched.json"))
P = {p["id"]: p for p in json.load(open("site/src/data/people.json"))}

def yr(s):
    m = re.match(r"(\d{4})-", s or "")
    return int(m.group(1)) if m else None

def yr_of_text(s):
    m = re.search(r"\b(1[6-9]\d\d|20\d\d)\b", s or "")
    return int(m.group(1)) if m else None

def pretty(iso):
    if not iso or not re.match(r"\d{4}-\d{2}-\d{2}", iso):
        return iso or ""
    y, mo, d = iso.split("-")
    months = ["", "January", "February", "March", "April", "May", "June", "July",
              "August", "September", "October", "November", "December"]
    return f"{int(d)} {months[int(mo)]} {y}"

out, corrections = [], []
for m in M["matched"]:
    r = m["row"]
    rec = {
        "slug": m["slug"], "name": m["name"], "id": m["id"],
        "registerName": f"{r['given']} {r['surname']}".strip(),
        "plot": r["plot"], "cemetery": r["cemetery"], "regno": r["regno"],
        "birth": pretty(r["birth"]), "death": pretty(r["death"]),
        "interment": pretty(r["interment"]),
        "treeBorn": m["treeBorn"], "treeDied": m["treeDied"],
    }
    # Compare at the precision the TREE actually offers. "MAR 1928" against a
    # register's 3 May 1928 is a real correction even though the year agrees,
    # and comparing years alone would silently swallow it.
    person = P.get(m["id"], {})
    def tree_date(tag):
        for e in person.get("events", []):
            if e.get("tag") == tag and e.get("date"):
                return e["date"]
        return ""
    MON = ["", "January", "February", "March", "April", "May", "June", "July",
           "August", "September", "October", "November", "December"]
    def conflicts(tree_str, iso):
        if not tree_str or not iso:
            return False
        ty = yr_of_text(tree_str)
        ry, rm, rd_ = int(iso[:4]), int(iso[5:7]), int(iso[8:10])
        if ty and ty != ry:
            return True
        for i, name in enumerate(MON):
            if i and re.search(name, tree_str, re.I) and i != rm:
                return True          # tree names a different month
        m2 = re.match(r"^(\d{1,2})\s", tree_str)
        if m2 and int(m2.group(1)) != rd_:
            return True              # tree names a different day
        return False

    for field, tag, iso in (("birth", "BIRT", r["birth"]), ("death", "DEAT", r["death"])):
        ts = tree_date(tag)
        if conflicts(ts, iso):
            corrections.append({**rec, "field": field, "was": ts, "now": pretty(iso)})
    out.append(rec)

# The four quarters, and whether they lie together
quarters = json.load(open("site/src/data/quarters.json"))
qslugs = {q["grandparent"]["slug"]: q["grandparent"]["name"] for q in quarters}
row = sorted([o for o in out if o["slug"] in qslugs], key=lambda o: o["plot"])

json.dump({"burials": sorted(out, key=lambda o: o["plot"]),
           "corrections": corrections,
           "quarterRow": row},
          open("site/src/data/nudgee.json", "w"), indent=1, ensure_ascii=False)

print(f"{len(out)} documented burials, {len(corrections)} corrections to the tree\n")
print("THE FOUR QUARTERS:")
for o in row:
    print(f"  {o['plot']:<10} {o['name']:<24} {o['birth']:<20} – {o['death']}")
print("\nCORRECTIONS:")
for c in corrections:
    print(f"  {c['name']:<24} {c['field']}: tree said {c['was']} → register says {c['now']}")
