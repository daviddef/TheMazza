#!/usr/bin/env python3
"""A nil that does not say what the instrument could have reached.

WHY THIS EXISTS. The Lerena archive published four nulls and only one survived
scrutiny. The one that survived did so for a reason that is not visible on the
results page: its control had established that the parish books were indexed
and dated. The other three read identically -- same empty page, same confident
sentence -- and were facts about the instrument rather than about the family.

This archive learned the same thing the expensive way on 21 September, three
hours apart. «Cassaniti returns nothing» went into searched.tsv as a
control-tested real negative; by the afternoon the same afternoon's reading had
found CASSANITI GAETANO in a Piedimonte birth Tavola and VENERA CASSANITI in
two acts. Piedimonte and Mascali are not name-indexed. The nil was true and
carried no information about anybody.

SO THE PART OF A NIL THAT AGES WELL IS NOT THE QUERY AND NOT THE COUNT. It is
the sentence saying WHAT THE INSTRUMENT COULD HAVE REACHED -- which comune,
which years, which record types the index actually covers. Without it a reader
a week later cannot tell a searched family from an unsearched source, and
neither can this archive.

Coverage fails in three places and all three render the same empty page:
  at the COLLECTION  -- the corpus does not hold that record type at all
  at the QUERY SHAPE -- a compound or variant name exact matching cannot reach
  at a SINGLE FIELD  -- a value the source failed to parse, which then excludes

Only the third kind is ever evidence about a family, and only once the first
two are excluded.

This flags searched rows that ASSERT A NIL without any reachability sentence.
It cannot judge whether the sentence is true -- only a person who checked the
coverage knows that. It makes the gap visible and finite instead of invisible.

Advisory by default; `--strict` exits 1.
"""
import csv, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(HERE, ".."))

# Phrases that assert emptiness. Deliberately narrow: this should catch rows
# that CLAIM a nil, not every row that happens to contain the word «no».
#
# THE FIRST VERSION OF THIS REGEX OVER-REPORTED AND THE NUMBER WAS PUBLISHED
# BEFORE IT WAS TESTED. «not one» matched «NOT ONE AT NUDGEE» inside a Find a
# Grave row that reports ELEVEN BURIALS -- a row full of findings, flagged as an
# unreachable nil. A checker written to catch unfalsifiable claims must not make
# one itself.
NIL = re.compile(
    r"\b(returns? nothing|returned nothing|not in the index|no results?\b|"
    r"nessun risultat|a real negative|complete negative|"
    r"is not there|are not there|no [a-z]+ (?:whatever|at all))\b", re.I)

# Sentences that say what the instrument could have reached. A nil accompanied
# by any of these has at least been ASKED the right question.
#
# ALSO WIDENED AFTER TESTING. Three flagged rows turned out to state their reach
# perfectly well in prose this did not recognise: «BT 26 and BT 27 cover UK
# PORTS ONLY», «CIVIL REGISTRATION IN THE PROVINCE OF MESSINA BEGINS IN 1820»,
# and a listing whose volume counts per year were given outright. The rule those
# three share is that they name a BOUNDARY -- of place, of date, or of record
# type -- so the patterns below look for boundaries rather than for the word
# «coverage».
REACH = re.compile(
    r"\b(indexed|not name-indexed|name index covers|coverage|"
    r"covers?\b[^.]{0,40}\bonly\b|\bonly\b[^.]{0,40}\bcovers?\b|"
    r"holds? (?:only|no)\b|does not (?:hold|cover|reach)|"
    r"begins? in \d{4}|starts? (?:in|with) \d{4}|stops? (?:at|in) \d{4}|"
    r"runs? (?:from|to) \d{4}|reach(?:es)? back|"
    r"control[- ]test|controlled against|in the same breath against|"
    r"which returns \d|the facets?\b|facet total|whole holding|not a sample|"
    r"read (?:entire|in full|end to end)|every entry|all \d+ |"
    r"structural rather than|were always unlikely|was always unlikely|"
    r"and nothing else|nothing before \d{4}|could never have (?:held|reached)|"
    r"says? nothing about|a fact about the (?:index|comune|instrument|source))\b",
    re.I)

rows = list(csv.DictReader(open("data/searched.tsv", encoding="utf-8"),
                           delimiter="\t"))

flagged, ok, nonil = [], 0, 0
for r in rows:
    blob = " ".join((r.get(k) or "") for k in ("scope", "result"))
    if not NIL.search(blob):
        nonil += 1
        continue
    if REACH.search(blob):
        ok += 1
        continue
    flagged.append(r)

print(f"  {len(rows)} searched rows — {nonil} assert no nil, {ok} assert a nil "
      f"AND say what the instrument could reach")

if not flagged:
    print("  ok    every nil on record says what the instrument could have reached")
    sys.exit(0)

print(f"  note  {len(flagged)} row(s) assert a nil with no reachability sentence — "
      f"each may be sound, and none of them can be checked by a reader:")
for r in flagged:
    print(f"        {(r.get('source') or r.get('key') or '?')[:96]}")
    print(f"            {r.get('key')}   [{r.get('status')}]")

sys.exit(1 if "--strict" in sys.argv else 0)
