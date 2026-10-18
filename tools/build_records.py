#!/usr/bin/env python3
"""The records registry: where a citation on a page can be followed to the record.

    python3 ../tools/build_records.py            # from site/ (what `npm run records` runs)

Writes site/src/data/records.json, which the <Rec> component (site/src/components/Rec.astro) reads.

WHY THIS EXISTS. On 18 October 2026 David looked at /scilla/ and said it names acts, volumes and arks in nearly
every paragraph and links none of them: "Scilla, Matrimoni 1888, atto 63 ... Antenati an_ua16595010, img 33" was
plain text. The arks were in the archive all along (data/*arks*.tsv, data/scilla-reads.tsv, data/pe-mazza-acts.tsv),
in files no page read. This is the one place they are turned into addresses.

WHAT IT HOLDS
  vol   "Comune|Kind|Year" -> [ark, ...]   the volume(s) the archive has listed for that comune, kind and year,
        from the ark tables. Kind is the archive's own word: Nati, Matrimoni, Morti, Pubblicazioni, Processetti.
        One ark: <Rec c k y> resolves to it. Several (a year whose acts and index are bound apart): <Rec> must
        be given the ark, because choosing between them would be a guess.
  ark   every ark the archive holds, anywhere, with where it comes from. <Rec ark="..."> may name only these:
        a link to an ark nobody wrote down is not a citation, it is a typing mistake.

A link goes to the volume's landing page on Antenati. It is a link, never an embedded copy.
"""
import csv
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "site", "src", "data", "records.json")

ARK = re.compile(r"\ban_ua\d+\b")

# which comune a table belongs to. The Briatico table lists the Zambrone and Pizzo volumes it sits beside; the
# column that says so is `note`, and a volume is filed under Briatico here because that is what the table calls it.
COMUNE = {
    "scilla-arks.tsv": "Scilla", "scilla-arks-italiano.tsv": "Scilla", "scilla-arks-nati-italiano.tsv": "Scilla",
    "pe-arks.tsv": "Piedimonte Etneo", "briatico-arks.tsv": "Briatico", "zambrone-arks.tsv": "Zambrone",
    "giarre-arks.tsv": "Giarre", "mascali-arks.tsv": "Mascali", "riposto-arks.tsv": "Riposto",
    "macchia-arks.tsv": "Macchia",
}
KIND = {
    "nati": "Nati", "matrimoni": "Matrimoni", "morti": "Morti",
    "matrimoni-processetti": "Processetti", "matrimoni processetti": "Processetti",
    "matrimoni-pubblicazioni": "Pubblicazioni", "matrimoni pubblicazioni": "Pubblicazioni",
    "matrimoni, processetti": "Processetti", "matrimoni, pubblicazioni": "Pubblicazioni",
}


def rows(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def main():
    vol, ark = {}, {}
    for path in sorted(glob.glob(os.path.join(DATA, "*arks*.tsv"))):
        fn = os.path.basename(path)
        comune = COMUNE.get(fn)
        for r in rows(path):
            a = (r.get("ark") or "").strip()
            if not ARK.fullmatch(a):
                continue
            tip = (r.get("tipologia") or "").strip()
            year = (r.get("year") or r.get("years") or "").strip()
            ark.setdefault(a, {"from": fn, "comune": comune or "", "tipologia": tip, "year": year})
            kind = KIND.get(tip.lower())
            if comune and kind and re.fullmatch(r"\d{4}", year):
                vol.setdefault("%s|%s|%s" % (comune, kind, year), [])
                if a not in vol["%s|%s|%s" % (comune, kind, year)]:
                    vol["%s|%s|%s" % (comune, kind, year)].append(a)
    # arks the archive wrote down in its own evidence: the act tables (the volume an act was read in), the register-reads
    # manifest (the citation under each plate), the searches and the documented additions (the citation of each person)
    for fn in ("scilla-reads.tsv", "pe-mazza-acts.tsv", "register-reads.tsv", "searched.tsv", "documented-additions.tsv"):
        p = os.path.join(DATA, fn)
        if not os.path.exists(p):
            continue
        for r in rows(p):
            for cell in r.values():
                for a in ARK.findall(cell or ""):
                    ark.setdefault(a, {"from": fn, "comune": "", "tipologia": "", "year": (r.get("year") or "").strip()})
    out = {"vol": dict(sorted(vol.items())), "ark": dict(sorted(ark.items()))}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1, sort_keys=False)
        f.write("\n")
    multi = sum(1 for v in vol.values() if len(v) > 1)
    print("records: %d volumes keyed by comune, kind and year (%d with more than one ark), %d arks in all"
          % (len(vol), multi, len(ark)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
