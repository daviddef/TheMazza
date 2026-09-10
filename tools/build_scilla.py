#!/usr/bin/env python3
"""What the Scilla registers have given up so far.

The Bourbon-era (Stato civile della restaurazione) annual index at Scilla is
laid out very differently from the post-1866 Italian one, and much better:
its columns are  N. d'ord | Cognomi e Nomi dei nati | Patria | Professione |
NOMI E COGNOMI DEI GENITORI | giorno della nascita.

The index names the parents. For a surname sweep that is worth an enormous
amount — a whole year's Arena households can be read off one opening without
opening a single act.
"""
import csv, json
rows = list(csv.DictReader(open("data/scilla-reads.tsv"), delimiter="\t"))
json.dump(rows, open("site/src/data/scilla-reads.json", "w"), indent=1, ensure_ascii=False)
print(f"{len(rows)} Scilla index reads")
for r in rows:
    print(f"  {r['year']}/{r['act']:>4}  {r['name']:20s} f:{r['father']:18s} m:{r['mother']:22s} [{r['status']}]")
