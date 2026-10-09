#!/usr/bin/env python3
"""An ark is a citation. Two acts must not cite one image.

WHY THIS EXISTS. On 9 October 2026 every image this archive holds was hashed
for the first time, after a question about two photographs that looked alike.
The photographs were the same photograph; so were three others; and one
MyHeritage stock graphic turned out to be filed 22 times under 22 names as the
portrait of 11 different people, nine of whom had no other image.

Nothing had ever looked at the bytes, and nothing had ever looked at the arks
either. 2,601 of them, in eight files, and they are the citations under most of
what this archive claims about an Italian register. A duplicate ark is the
citation-level version of the same fault: two different acts pointing at one
scan, which would make one of them a footnote to the wrong page.

They came back clean, and this keeps them that way.

WHAT IS CHECKED, AND WHY EACH ONE

  * The FORM of an ark. «an_ua37932358» is an ark; «an_ua87718 ff.» is a base
    ark for a sequential run and is the file's own documented shorthand, so it
    is allowed — but only with a note, because the note is where the formula
    lives («ark(Y) = an_ua87718 + (Y - 1816)») and a range without its rule is
    not a citation, it is a gesture. Three rows use it and all three carry one.

  * ONE ARK, ONE REGISTER. If two rows share an ark they must be the same
    register — same series and same years — listed in two files. Three Zambrone
    volumes are deliberately cross-listed in briatico-arks.tsv, labelled
    «napoleonico — ZAMBRONE», because Zambrone's registers sit inside
    Briatico's holdings. That is honest and stays a note. An ark shared by two
    DIFFERENT registers is a false citation and fails.

  * The container id, where one has been fetched. 2,246 of the 2,601 rows have
    none, which is not rot: an ark-to-container lookup is rate limited to about
    25 before Antenati starts returning 403, so the backlog is the throttle and
    not a gap in the data. It is counted so that it can be watched rather than
    assumed.
"""
import collections, csv, glob, os, re, sys

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

ARK = re.compile(r"^an_[A-Za-z0-9]+$")
RANGE = re.compile(r"^an_[A-Za-z0-9]+ ff\.$")
CONTAINER = re.compile(r"^[A-Za-z0-9]{7}$")
BLANK = {"", "—", "-", "?"}

rows = []
for path in sorted(glob.glob("data/*arks*.tsv")):
    with open(path, encoding="utf-8") as fh:
        for i, r in enumerate(csv.DictReader(fh, delimiter="\t"), start=2):
            r["_file"] = os.path.basename(path)
            r["_line"] = i
            rows.append(r)

problems, notes = [], []


def register(r):
    """What this row is a citation FOR: a series and a span of years."""
    return ((r.get("tipologia") or "").strip(),
            (r.get("year") or r.get("years") or "").strip())


def label(r):
    return (r.get("serie") or r.get("fondo") or "").strip()


# ---- the form of each ark
for r in rows:
    a = (r.get("ark") or "").strip()
    if a in BLANK:
        continue
    if RANGE.match(a):
        if (r.get("note") or "").strip() in BLANK:
            problems.append(f"  FAIL  {r['_file']} line {r['_line']}: «{a}» is a base ark for a "
                            f"run and carries no note, so the rule that turns a year into an ark "
                            f"is written down nowhere")
        continue
    if not ARK.match(a):
        problems.append(f"  FAIL  {r['_file']} line {r['_line']}: «{a}» is not an ark. An ark is "
                        f"an_ followed by letters and digits, or that plus « ff.» for a run")

# ---- one ark, one register
by_ark = collections.defaultdict(list)
for r in rows:
    a = (r.get("ark") or "").strip()
    if a not in BLANK:
        by_ark[a].append(r)
crosslisted = 0
for a, rs in sorted(by_ark.items()):
    if len(rs) < 2:
        continue
    regs = {register(r) for r in rs}
    if len(regs) == 1:
        crosslisted += 1
        where = ", ".join(sorted({r["_file"] for r in rs}))
        notes.append(f"  note  {a} is listed {len(rs)} times for one register "
                     f"({register(rs[0])[0]} {register(rs[0])[1]}) in {where} — "
                     f"{label(rs[0]) or 'unlabelled'}")
    else:
        detail = "; ".join(f"{r['_file']} line {r['_line']} {register(r)[0]} {register(r)[1]}"
                           for r in rs)
        problems.append(f"  FAIL  one ark cited for {len(regs)} different registers — {a} — so at "
                        f"least one of them points at the wrong scan: {detail}")

# ---- containers
bad_c = [r for r in rows
         if (r.get("container") or "").strip() not in BLANK
         and not CONTAINER.match((r.get("container") or "").strip())]
for r in bad_c[:6]:
    problems.append(f"  FAIL  {r['_file']} line {r['_line']}: container "
                    f"«{(r.get('container') or '').strip()}» is not a 7-character id")
have_c = sum(1 for r in rows if (r.get("container") or "").strip() not in BLANK)

print(f"  {len(rows)} ark(s) in {len(set(r['_file'] for r in rows))} files · {have_c} with a "
      f"container fetched, {len(rows) - have_c} still behind the rate limiter · "
      f"{crosslisted} deliberately cross-listed")
for n in notes:
    print(n)
for p in problems:
    print(p)
if problems:
    print(f"  FAIL  arks       {len(problems)} problem(s)")
    sys.exit(1)
print("  ok    arks       every ark well formed, and no ark cited for two different registers")
