# Roots & Routes (the tree page)

Ten views of everyone in the archive who has died and whose life can be drawn: hourglass, fan, whole-tree and close-family maps, Atlas map, movements, kinship,
place lanes, eras, lifespans, an Orphans tab, and the five animated views (Night sky, Ink ledger, Household, Generations, Where they lived). It is served at `/roots/`.

| File | What it is | Edit by hand? |
|---|---|---|
| `tree.json` | people, parent links, years, places, routes | no, generated |
| `place_map.json` | each place string with coordinates, country and Record Atlas id | no, generated |
| `place-additions.json` | `places`: strings decided by hand, each with its reason; `refused`: strings deliberately not placed, each with its reason | yes, with a reason |
| `atlas-data.json` | the Record Atlas slice: outlines, regimes, flags, events, collections | no, generated |
| `roots.html`, `roots.embed.html` | the page, whole and as a fragment for the site layout | no, generated |
| `tree.report.json` | counts, the people whose dates are not one life, the places not placed and why | read it |
| `people.ged`, `slugs.json` | intermediates, not committed (gitignored) | no |

## Rebuild

```bash
python3 tools/build-tree-page.py           # rebuild everything and run the page's own checks
python3 tools/build-tree-page.py --check   # exit 1 if the page is older than the data it was built from
```

Needs the Record Atlas checkout (`RECORD_ATLAS`, default `~/Projects/Family Projects/Record Atlas`), read only, and `npm ci` in `site/` (it reads the kit's gazetteer, as
`tools/build_era.py` does). The skill's scripts are vendored in `tools/tree-page/` (the family-tree-page skill, template 1.7.0), so CI and other sessions do not depend
on `~/.claude`.

## What is and is not on the page

- **No living person.** The people are the 688 in `site/src/data/people.json` with `living: false`; the 132 living are never read (the builder filters them out before it
  looks at a single field), and the 25 held out as possible minors are not in `people.json` at all. `presumedLiving` is gone from this archive and is not read. The
  converter then adds its own, stricter floor: nobody with no death recorded and a birth year in the last 110 years, or no birth year at all, is drawn (208 people: no death recorded, and a birth that is after 1916 or
  that not even a relative's dates can place). The page's own check fails the build on a living person's name.
- **Colour is the Record Atlas surname catalogue's family**, read only (`surname_variants.py` lookup), and, where the catalogue has no entry for a surname, the surname as
  the archive writes it with typography folded. Today the catalogue holds Mazza, Polistena and Morabito; Nicotra, Prostamo, Arena, Donato, Anile and the rest are colours
  by their written surname and are not in the catalogue. Nothing here lists spellings.
- **Places are never guessed.** 40 place strings are placed: 36 where `data/era-ground.tsv` has a row, the archive's gazetteer (the kit's, `data/gazetteer-local.json`,
  `data/place-spellings.tsv`) holds the same name with an `exact` match, and the Atlas's `geo.country_of` agrees with the country the string names; 4 decided by hand in
  `place-additions.json` (Nudgee, Lismore twice, Murwillumbah: each with its reason). Seven strings are refused on purpose (a country, a state, an island, or
  several places) and three have no answer (see `tree.report.json`, `places`). A person with no placed birth place is drawn at a relative's birth place, which the page
  says, or not drawn.
- **Dates**: "c. 1809" is a birth the register or tree writes as circa/about, or one estimated from a parent, child or spouse; "1809-?" is a death not recorded. "before ..."
  on a death is a death with no year; "after ..." and "alive at ..." are not deaths.
- **Two lives that cannot be one** (died more than 110 years after birth) are not drawn and are listed in `tree.report.json` under `conflicts`.
- **The death place is the place the record states.** The converter takes a later residence as the death place; `keep_death_place` puts the recorded one back. A person with
  a burial place and no death place is placed at the burial place.
- **A route** (three or more places) is carried whole only where every stop between birth and death is a dated arrival or residence in the archive: four people (Fremantle,
  then Brisbane). A stop with no year is never guessed into the order.
- **Unrecorded sex.** 106 of the 448 people drawn have no sex recorded in the archive (170 men, 172 women). They are drawn as `u`: the page says parent, child, spouse,
  sibling, "uncle or aunt" for them, and no sex is inferred from a given name. The GEDCOM written from `people.json` carries a `SEX` line only where the archive has one.
