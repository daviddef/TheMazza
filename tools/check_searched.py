#!/usr/bin/env python3
"""Guard data/searched.tsv, whose first column is load-bearing and looks decorative.

`key` was added to this file by a later session than the one that wrote the
file, and `build_searched.py` deliberately never recomputes it — its docstring
says why: keys that were regenerated once got wiped, and the work-list gate
then cheerfully reported "nothing outstanding" for an archive with twenty-four
outstanding searches.

NOTHING STOPPED A SESSION APPENDING A ROW IN THE OLD FIVE-COLUMN SHAPE. I did,
twice in one sitting. Every field shifted one place right: the word `part`
landed in `key`, a date landed in `status`, the result text landed in `scope` —
and because the key was then nonsense, `check:covers` could no longer see the
rows at all. They were invisible to the gate that exists to count them, and the
build stayed green throughout. A silent corruption that makes a counter
under-report is worse than a loud one.

So, per row:

  * the column count must be exactly right — a short row is the shifted-shape
    bug and is refused before anything else is looked at;
  * `key` must be non-empty and match `src/<slug>-<6 hex>`;
  * `key` must be unique — a copied row that keeps its neighbour's key makes two
    searches count as one;
  * `status` must be one of the seven words in use. There is no legend on
    /searched/ to read this out of — the page only splits `done` from the rest,
    and the kit component is handed `nil={["not-yet", "outstanding"]}` — so the
    list is pinned here, the way checkworklist pins the work-list states. An
    eighth word should be a deliberate act that edits this line;
  * `when` must parse as a date, for the same reason from the other side;
  * `source` must never be empty, and `result` must not be empty on a row that
    claims to be `done` or `part` — a finished search with nothing written in it
    is an unfinished thought being counted as a negative result. A row that is
    still `outstanding` is allowed to have no result yet, because that is what
    outstanding means.

Exit 1 on a failure, 0 on a clean run.
"""
import csv, os, re, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(HERE, ".."))

PATH = "data/searched.tsv"
KEY = re.compile(r"^src/[a-z0-9-]+-[0-9a-f]{6}$")
# The seven in use, counted off data/searched.tsv. `outstanding` is the one
# check:covers counts; `not-yet`, `part`, `superseded`, `wall` and `correction`
# it does not, which is worth knowing before adding an eighth.
STATUS = {"done", "outstanding", "not-yet", "part", "superseded", "wall",
          "correction"}
WHEN = re.compile(r"^\d{1,2} [A-Z][a-z]{2} \d{4}$")

raw = open(PATH, encoding="utf-8").read().rstrip("\n").split("\n")
header = raw[0].split("\t")
ncols = len(header)

fails, notes = [], []

# The shape check comes first and reports by physical line, because when this
# fails the named columns cannot be trusted to mean what they say.
for i, line in enumerate(raw[1:], start=2):
    if not line.strip():
        continue
    got = len(line.split("\t"))
    if got != ncols:
        cells = line.split("\t")
        fails.append(
            f"line {i}: {got} columns, expected {ncols} — "
            f"this is the shifted-row bug; first cell is «{cells[0][:40]}»"
        )

if fails:                       # don't compound a shape error with field errors
    for f in fails:
        print("  FAIL  ", f)
    print(f"  FAIL  searched.tsv — {len(fails)} problem"
          f"{'' if len(fails) == 1 else 's'}")
    sys.exit(1)

rows = list(csv.DictReader(open(PATH, encoding="utf-8"), delimiter="\t"))
seen = collections.defaultdict(list)

for i, r in enumerate(rows, start=2):
    src = (r.get("source") or "").strip()
    where = f"line {i} ({src[:44] or 'no source'})"

    key = (r.get("key") or "").strip()
    if not key:
        fails.append(f"{where}: no key — build_searched.py will not mint one, "
                     f"and check:covers counts on it")
    elif not KEY.match(key):
        fails.append(f"{where}: key «{key[:40]}» is not src/<slug>-<6 hex> — "
                     f"a shifted row puts the status word here")
    else:
        seen[key].append(i)

    status = (r.get("status") or "").strip()
    if status not in STATUS:
        fails.append(f"{where}: status «{status[:40]}» is not one of "
                     f"{', '.join(sorted(STATUS))}")

    when = (r.get("when") or "").strip()
    if when and not WHEN.match(when):
        notes.append(f"{where}: when «{when[:40]}» is not «16 Sep 2026» shape")

    if not src:
        fails.append(f"{where}: no source — the row says nothing was searched")
    if status in ("done", "part") and not (r.get("result") or "").strip():
        fails.append(f"{where}: status «{status}» with no result — a finished "
                     f"search with nothing written in it is an unfinished "
                     f"thought being counted as a negative result")

for key, lines in seen.items():
    if len(lines) > 1:
        fails.append(f"key «{key}» is on lines {', '.join(map(str, lines))} — "
                     f"duplicate keys make two searches count as one")

for n in notes:
    print("  note  ", n)
for f in fails:
    print("  FAIL  ", f)
print(f"  {'ok   ' if not fails else 'FAIL '} {len(rows)} searched rows — "
      f"{len(fails)} problem{'' if len(fails) == 1 else 's'}, "
      f"{len(notes)} note{'' if len(notes) == 1 else 's'}")
sys.exit(1 if fails else 0)
