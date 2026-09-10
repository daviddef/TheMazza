#!/usr/bin/env python3
"""The Scilla people the archive needs from the Reggio Calabria registers.

Antenati rate-limits hard on its HTML pages — three navigations was enough to
trip it on 10 September 2026 — so the sweep has to be planned before it starts
and executed with as few page loads as possible. This lists exactly who is
wanted, in which volume, and what the act would prove.
"""
import json

TARGETS = [
 {"who":"Rocco Arena","born":1861,"ark":"an_ua2002933","kind":"Nati",
  "proves":"His father ORAZIO ARENA (b. 1821 per the tree) with an age and a trade, and his mother GIOVANA ZIRILLI. Two generations of Arena in one act."},
 {"who":"Giovanni Arena","born":1870,"ark":"?","kind":"Nati",
  "proves":"Names his parents; the tree gives none above him. He is Giuseppe Arena's father and Rocco Arena (1924)'s grandfather."},
 {"who":"Giovanni Polistena","born":1883,"ark":"?","kind":"Nati",
  "proves":"His father ANTONIO POLISTENA and mother GIOVANNA PONTILLO, both undated in the tree. He is Angela Polistena's father."},
 {"who":"Giuseppe Arena","born":1892,"ark":"?","kind":"Nati",
  "proves":"His father GIOVANNI ARENA with an age, and his mother CONCETTA RUSSO. He is Rocco Arena (1924)'s father."},
 {"who":"Michele Donato","born":1851,"ark":"?","kind":"Nati",
  "proves":"His father DOMENICO DONATO and mother ANNUNZIATA SOFI. He emigrated to New Orleans in 1908."},
 {"who":"Giovanni Polistena x Nunziata Donato","born":None,"ark":"?","kind":"Matrimoni 1910-1913",
  "proves":"FOUR grandparents of Angela Polistena in one act, each with an age. Scilla marriages on Antenati run 1905-1913 only, so this is worth trying first if the marriage falls in that window."},
]
json.dump(TARGETS, open("data/scilla-targets.json","w"), indent=1, ensure_ascii=False)
print(f"{len(TARGETS)} Scilla targets")
for t in TARGETS:
    print(f"  {t['who']:38s} {t['born'] or '':>6}  {t['kind']:20s} {t['ark']}")
