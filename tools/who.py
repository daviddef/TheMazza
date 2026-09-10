import sys, re
sys.path.insert(0, "tools")
from ged import parse, kid, kids, val

R = parse()
I = {x: v for x, v in R.items() if v["tag"] == "INDI"}
F = {x: v for x, v in R.items() if v["tag"] == "FAM"}

def name(x):
    n = kid(I[x], "NAME")
    return re.sub(r"\s+", " ", (n["val"] if n else "?").replace("/", " ")).strip()

def ev(i, tag):
    e = kid(i, tag)
    if not e: return ""
    d, p = val(e, "DATE"), val(e, "PLAC")
    return " ".join(x for x in (d, p) if x)

def line(x, ind=0, seen=None, maxd=12):
    if seen is None: seen = set()
    if x in seen or ind > maxd: return
    seen.add(x)
    i = I[x]
    b, d = ev(i, "BIRT"), ev(i, "DEAT")
    bits = " · ".join(f for f in (f"b {b}" if b else "", f"d {d}" if d else "") if f)
    print("  " * ind + f"{name(x)}  [{x}]  {bits}")
    fc = kid(i, "FAMC")
    if not fc: return
    fam = F.get(fc["val"])
    if not fam: return
    for role in ("HUSB", "WIFE"):
        h = kid(fam, role)
        if h and h["val"] in I:
            line(h["val"], ind + 1, seen, maxd)

q = " ".join(sys.argv[1:]) or "Michael Mazza"
hits = [x for x in I if q.lower() in name(x).lower()]
print(f"== matches for '{q}': {len(hits)}")
for h in hits:
    i = I[h]
    print(f"\n--- {name(h)} [{h}] b:{ev(i,'BIRT')} d:{ev(i,'DEAT')}")
    line(h)
