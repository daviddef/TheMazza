"""Parse the MyHeritage GEDCOM into a workable in-memory model.
Imported by the other tools; run directly for a summary."""
import re, sys, json, os

GED = os.path.join(os.path.dirname(__file__), "..", "sources", "mazza-myheritage.ged")

def parse(path=GED):
    recs, stack = {}, []
    root = None
    with open(path, encoding="utf-8-sig") as fh:
        for raw in fh:
            line = raw.rstrip("\r\n")
            if not line.strip():
                continue
            m = re.match(r"^(\d+)\s+(?:(@[^@]+@)\s+)?(\S+)(?:\s(.*))?$", line)
            if not m:
                continue
            lvl, xref, tag, val = int(m.group(1)), m.group(2), m.group(3), m.group(4) or ""
            node = {"tag": tag, "val": val, "xref": xref, "kids": []}
            if lvl == 0:
                root = node
                if xref:
                    recs[xref] = node
                stack = [node]
            else:
                while len(stack) > lvl:
                    stack.pop()
                if stack:
                    stack[-1]["kids"].append(node)
                stack.append(node)
    return recs

def kid(n, tag):
    for k in n["kids"]:
        if k["tag"] == tag:
            return k
    return None

def kids(n, tag):
    return [k for k in n["kids"] if k["tag"] == tag]

def val(n, *path):
    cur = n
    for t in path:
        cur = kid(cur, t) if cur else None
    return (cur["val"].strip() if cur else "")

def cont(n):
    """CONC/CONT continuation text under a node."""
    out = n["val"]
    for k in n["kids"]:
        if k["tag"] == "CONC":
            out += k["val"]
        elif k["tag"] == "CONT":
            out += "\n" + k["val"]
    return out.strip()

if __name__ == "__main__":
    r = parse()
    I = [v for v in r.values() if v["tag"] == "INDI"]
    F = [v for v in r.values() if v["tag"] == "FAM"]
    S = [v for v in r.values() if v["tag"] == "SOUR"]
    print(f"INDI {len(I)}  FAM {len(F)}  SOUR {len(S)}")
    tags = {}
    for i in I:
        for k in i["kids"]:
            tags[k["tag"]] = tags.get(k["tag"], 0) + 1
    print("INDI tags:", dict(sorted(tags.items(), key=lambda x: -x[1])))
    ftags = {}
    for f in F:
        for k in f["kids"]:
            ftags[k["tag"]] = ftags.get(k["tag"], 0) + 1
    print("FAM tags:", dict(sorted(ftags.items(), key=lambda x: -x[1])))
