import sys, re, collections
sys.path.insert(0, "tools")
from ged import parse, kid, kids, val

R = parse()
I = {x: v for x, v in R.items() if v["tag"] == "INDI"}
F = {x: v for x, v in R.items() if v["tag"] == "FAM"}

def nm(x):
    n = kid(I[x], "NAME")
    return re.sub(r"\s+", " ", (n["val"] if n else "?").replace("/", " ")).strip()
def ev(x, tag, f="DATE"):
    e = kid(I[x], tag)
    return val(e, f) if e else ""

# --- duplicate detection: same name + same birth year
key = collections.defaultdict(list)
for x in I:
    y = re.search(r"\b(1[6-9]\d\d|20\d\d)\b", ev(x, "BIRT"))
    key[(nm(x).lower(), y.group(1) if y else "")].append(x)
dups = {k: v for k, v in key.items() if len(v) > 1 and k[0] != "?"}
print(f"== possible duplicates: {len(dups)}")
for (n, y), xs in sorted(dups.items()):
    print(f"   {n} ({y or 'no year'}): {' '.join(xs)}")

# --- connected components over FAM links
adj = collections.defaultdict(set)
for fx, f in F.items():
    mem = [k["val"] for k in f["kids"] if k["tag"] in ("HUSB","WIFE","CHIL") and k["val"] in I]
    for a in mem:
        for b in mem:
            if a != b: adj[a].add(b)
seen, comps = set(), []
for x in I:
    if x in seen: continue
    stack, comp = [x], []
    seen.add(x)
    while stack:
        c = stack.pop(); comp.append(c)
        for n2 in adj[c]:
            if n2 not in seen: seen.add(n2); stack.append(n2)
    comps.append(comp)
comps.sort(key=len, reverse=True)
print(f"\n== connected components: {len(comps)}  sizes: {[len(c) for c in comps[:12]]}")
print(f"   isolated (size 1): {sum(1 for c in comps if len(c)==1)}")

# --- Mazza males by generation depth
print("\n== all MAZZA individuals, oldest first")
mz = [x for x in I if re.search(r"/Mazza/", kid(I[x],"NAME")["val"] or "", re.I)]
def yr(x):
    m = re.search(r"\b(1[6-9]\d\d|20\d\d)\b", ev(x,"BIRT"))
    return int(m.group(1)) if m else 9999
for x in sorted(mz, key=yr):
    b = kid(I[x],"BIRT"); d = kid(I[x],"DEAT")
    print(f"   {yr(x) if yr(x)<9999 else '····'}  {nm(x):32s} [{x:7s}] {val(b,'PLAC') if b else '':38s} d:{(val(d,'DATE')+' '+val(d,'PLAC')).strip() if d else ''}")
