# Menu regroup, PR A (menu only): reach proof

12 November 2026. Compared: the build of `main` (bf3fc0d) against the build of this change, both from the same full build chain.

## Counts

| | before | after |
|---|---|---|
| menus (Research included) | 6 | 6 |
| entries outside Research | 44 | 43 |
| Start | 10 | 3 |
| Our line | 4 | 4 |
| The families (The Marriages, The Hundred and Ten, The Pieces) | 3 | gone: The Marriages is in People, the other two in Places & families |
| People & places | 11 | gone: split into People (10, with the five drawn pages) and Places & families |
| People | – | 10 (Lists 5, Drawn 5) |
| Places & families | – | 24 (The families 3, Places 7, Families 14) |
| The name | 16 | 2 (The Name, The Mazza) |
| Research | 14 | 14, unchanged |

The one entry fewer is What's new, which left Start: it is the What's new group of Research (and the pulse button), so it is still in the menu.

## What reaches what

**No address left the menu.** Every address that was in a menu before is in a menu now (`menu-a-moves.md`: "0 address(es) were in the menu and are in none now"). So the reach rule (an address may leave a menu only if an index or hub page that stays reaches it) was not needed for any page, and nothing is listed as removed.

The 14 family pages (Arena, Nicotra, Prostamo, Polistena, Donato, Melluso, Anile, Costa, Arlotta, Pontillo, Ventrice, Sofi, Barbuto, Russo) are the ones the proposal wanted to move out of the menu altogether behind a `/families/` index. This archive has no such index, and creating one is outside this change, so **all fourteen stay in the menu**, now under Places & families > Families. Facts about how they are reached today, from the built pages (main's `<main>` text, header and menu not counted):

- `/name/` (still in The name) links all 14 of them.
- `/lines/` (The Four Quarters, now in Places & families) links 3 of them.
- `/places/`, `/components/`, `/people/`, `/who/`, `/sources/`, `/research/` and `/whats-new/` link none of them.

So `/name/` is already a working hub for all fourteen. When David decides about a `/families/` index (PR B), that page, or `/name/`, is the place that carries them and the menu entries can then be trimmed.

## Checks run

- `menu_inventory.py compare` (kit, through `scripts/menu-inventory-kit.py`): NOTHING LOST. 60 in-scope addresses, every one answers, every text block still stands on the new site.
- `menu_inventory.py sitediff`: 1,881 pages before, 1,881 after; none gone, none new; no page changed outside its menu (the header and drawer are not part of a page).
- `scripts/menu-moves.py`: the table in `menu-a-moves.md`.

## A fix to the inventory wrapper

The kit's `compare` builds its "where does this text now stand" index without any page under `/person/`, `/people/` or `/who/`. That was written for archives where those are directories of person pages. In this archive `/people/` and `/who/` are menu pages in scope, so the unmodified kit reported 1,104 blocks of those two pages as lost, even when the baseline build was compared with itself. `scripts/menu-inventory-kit.py` now keeps the two index pages in the index (their sub-pages are still skipped) and asserts the kit line it patches is still there. The kit itself is untouched.

## Not in this change

No page content, no page merge, no redirect, no new page, no edit to an index page. The overlaps noted in the review (`/components/` and `/marriages/` against `/people/`; `/corrections/` against `/nicotra/`) are left for a set test. The three long studies (The Sicilian Registers, The Queensland Register, Testing the 1697) were already Research > Sources & method > Deep dives, and the audit is already under Checks, so nothing moved there.
