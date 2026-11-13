# Mazza Family

## Record Atlas

The shared map lives at `../Record Atlas`. Research done here is only
useful to the next person if it gets there.

Invoke the `record-atlas-feedback` skill whenever you finish a search,
open a register, write to an archive, or find a source the atlas does
not list — as you do it, not in a sweep at the end. Record the
FamilySearch waypoint, not just the film number; the skill explains why.

## Surname spellings

Surname spellings come only from the Record Atlas catalogue: run `terms` before searching, `cover` before any nil, `add` for every new spelling, `publish` once at the end. Keep no variants list here.

## Given names and old place names

Given-name forms (Ivan = Johann = Giovanni = Zuane = Joannes) and a place's name in the year of the record (Salisbury before 1982, Fiume before 1945) come only from the Record Atlas catalogues, as surnames do: invoke the user-level `name-variants` skill, run `given_name_variants.py terms` / `place_names.py at PLACE YEAR` before searching, `cover` before any nil, `add` (with evidence) for every new form, `publish` once at the end. Keep no table of given-name forms or old place names here. Nothing about a person goes in the catalogues; `lead` is never a finding.

## Found rows say who they are for (from 15 Nov 2026)

Every new row in `searched.json` that reads as found (outcome found / yield / hit) must carry EITHER `"for": [["/person/slug/", "Name"], ...]` OR `"nobody": true`, never both. Each `for` path must be a BUILT page of this archive that is that person's own page, with the name that page uses, each page once per row, and only people the finding is really about. `"nobody": true` means the pages were read and no new person came out of them (the reason may go in `what`). A found row also names the page(s) it updated in `ev` or says `"logOnly": true`. The gate is `check:row-pages` (kit `check_row_pages.py`, switched on by `docs/row-pages.json` `peopleFrom`).

- Living people: only people this archive already publishes can be listed. Never add a page or a name for a living person to satisfy the gate; the presumed-living people are not to be named.
- Old rows are not backfilled and no existing row is edited: editing a row changes its Atlas key and it reads "Not sent yet" until the next publish.
- Nothing about the people goes to the Atlas; receipts hold only the row key.
- Most rows here are `part` or nil and need neither field; the rule bites only when a row is a find.
