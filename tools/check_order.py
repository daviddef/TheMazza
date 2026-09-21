#!/usr/bin/env python3
"""Does the ORDER of a data file decide what this archive says?

WHY THIS EXISTS. On 21 September a peer session added three layers to the Atlas
and its shelf colour was chosen by `cats.setdefault(h, {})["shelf"] = ...` in a
loop over a file with ONE ROW PER SERIES. That is a many-to-one join written
with `=`, so the last row wins. It rendered correctly for all seven comuni on
the day it was written -- THERE WAS NOTHING TO SEE -- and it would have turned
Piedimonte Etneo green the moment somebody appended an `open` row beneath its
`route` one. The failure would have looked like a data update rather than a bug.

The test that separates the two cases is one line and does not require reading
any code: REVERSE THE SOURCE FILE AND RE-RUN. Identical output means the fold
has a rule. Different output means the file's order is deciding what the archive
says, and nobody wrote that rule down.

This runs that test over every builder that turns a data/*.tsv into a
site/src/data/*.json. It reverses the rows (keeping the header), re-runs the
builder, compares the output byte for byte, and restores the file whatever
happens -- including on a crash, which is why the restore is in a `finally`.

A builder that legitimately depends on order should be listed in ORDERED with
the reason, so the exemption is a statement rather than a silence.

Advisory by default; `--strict` exits 1.
"""
import json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
os.chdir(ROOT)

# builder, input TSV, output JSON
PAIRS = [
    ("build_disputed.py",   "data/disputed-edges.tsv",     "site/src/data/disputed.json"),
    ("build_audit.py",      "data/audit-negatives.tsv",    "site/src/data/audit-negatives.json"),
    ("build_coverage.py",   "data/antenati-coverage.tsv",  "site/src/data/coverage.json"),
    ("build_instruments.py","data/instruments.tsv",        "site/src/data/instruments.json"),
    ("build_questions.py",  "data/questions.tsv",          "site/src/data/questions.json"),
    ("build_sources.py",    "data/sources.tsv",            "site/src/data/sources.json"),
    ("build_holdings.py",   "data/pe-arks.tsv",            "site/src/data/holdings.json"),
    ("build_holdings.py",   "data/mascali-arks.tsv",       "site/src/data/holdings.json"),
]

# Builders whose output is ALLOWED to depend on input order, with the reason.
# An entry here is a claim, not a shrug.
ORDERED = {
    # (builder, input): why
}

# A BYTE COMPARISON IS THE WRONG TEST AND THE FIRST VERSION USED ONE. Most of
# these builders emit a LIST in file order, so reversing the input reverses the
# list and the bytes differ for a reason that is presentation, not data loss --
# six of eight pairs "failed" that way and every one was benign. The fault worth
# catching is a FOLD in which one row silently overwrites another, and that
# shows up as a CHANGED VALUE or a VANISHED KEY, never as a reordering.
#
# So both outputs are canonicalised: every list is sorted by its own contents.
# What survives is the set of facts. If those differ, a row was dropped.
def canon(x):
    if isinstance(x, dict):
        return {k: canon(v) for k, v in sorted(x.items())}
    if isinstance(x, list):
        return sorted((canon(v) for v in x),
                      key=lambda v: json.dumps(v, sort_keys=True, ensure_ascii=False))
    return x

def same_facts(a, b):
    try:
        return canon(json.load(open(a, encoding="utf-8"))) == \
               canon(json.load(open(b, encoding="utf-8")))
    except Exception:
        return open(a, "rb").read() == open(b, "rb").read()

def reverse_rows(path):
    with open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")
    trailing = lines[-1] == ""
    body = lines[:-1] if trailing else lines
    out = [body[0]] + list(reversed(body[1:]))
    return "\n".join(out) + ("\n" if trailing else "")

fails, ok, skipped = [], 0, 0
for builder, src, out in PAIRS:
    if not (os.path.exists(src) and os.path.exists(out)):
        skipped += 1
        continue
    if (builder, src) in ORDERED:
        skipped += 1
        continue
    with tempfile.TemporaryDirectory() as td:
        keep_src, keep_out = os.path.join(td, "s"), os.path.join(td, "o")
        shutil.copy(src, keep_src)
        shutil.copy(out, keep_out)
        try:
            # Compute BEFORE opening for write. The first version of this line
            # read the file inside `open(src, "w")`, which truncates it first,
            # so reverse_rows() got an empty file and died on body[0]. The
            # restore in `finally` is the only reason that cost nothing.
            flipped = reverse_rows(src)
            with open(src, "w", encoding="utf-8") as f:
                f.write(flipped)
            r = subprocess.run([sys.executable, os.path.join("tools", builder)],
                               capture_output=True, text=True)
            if r.returncode != 0:
                fails.append((builder, src, "builder exited "
                              f"{r.returncode} on reversed input: "
                              f"{(r.stderr or '').strip().splitlines()[-1:] }"))
            elif not same_facts(out, keep_out):
                fails.append((builder, src,
                              "FACTS CHANGED — a row is silently overwriting "
                              "another, and the file's order decides which wins"))
            else:
                ok += 1
        finally:
            shutil.copy(keep_src, src)
            shutil.copy(keep_out, out)

print(f"  {ok} builder/input pair(s) give identical output on reversed input; "
      f"{skipped} skipped")
if not fails:
    print("  ok    no data file's row order changes what this archive publishes")
    sys.exit(0)

print(f"  note  {len(fails)} pair(s) depend on the order of their input:")
for builder, src, why in fails:
    print(f"        {builder}  <-  {src}")
    print(f"            {why}")
sys.exit(1 if "--strict" in sys.argv else 0)
