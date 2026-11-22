# Menu clean-up, 23 November 2026: reach proof

Compared: the build of `origin/main` (2c5d52e) against the build of this branch, both from a clean `site/dist` and the full build chain.
`menu_inventory.py snapshot` was taken of the old build; `compare` was run against the new one.

## Links in the header menu (the pages a reader can open from it, group headings that are links included)

| Group | before | after |
|---|---|---|
| Start | 3 | 3 |
| Our line | 4 | 4 |
| People | 10 (Lists 5, Drawn 5) | 6 (Lists 5, **Drawn** 1) |
| Places & families | 26 | 15 (The families 3, Places 7, Families 5: All the families + Mazza, Arena, Nicotra, Prostamo) |
| The name | 1 | 1 |
| Research | 17 | 18 (13 pages in the canon's groups and Deep dives, plus the four group headings and the Deep dives heading, which is now a link) |
| **Total** | **61** | **47** |

## What left a menu, and what reaches it now

| Left the menu | Reached from |
|---|---|
| `/roots/` (Roots & Routes) | removed on purpose; `/roots/` redirects to `/trees/`. `/roots/view.html` stays (person-page panels) |
| `/tree/`, `/trees/`, `/bloodline/`, `/timeline/` | the new hub `/drawn/`, one line each (`/direct-line/` is listed there too and also stays in Our line) |
| `/anile/`, `/arlotta/`, `/barbuto/`, `/costa/`, `/donato/`, `/melluso/`, `/pontillo/`, `/polistena/`, `/russo/`, `/sofi/`, `/ventrice/` (eleven family pages) | `/families/` ("All the families"), which links all fifteen family pages and reads the same list (`lib/familylist.js`) as the menu did; also `/name/` links all of them |
| nothing else | |

The four families that stay named: the archive's own line first (Mazza), then Arena, Nicotra (the other two hand-written family pages) and Prostamo (the first data-built page in `familylist.js`, ordered by direct-line ancestors and published people), A to Z.

Added: `/drawn/` and `/research/deep-dives/` (the Deep dives heading in Research links to it; it lists the three studies and the audit of negatives).
Both are indexable, in the sitemap, in the search index and in the book (`/research/deep-dives/` as a chapter, `/drawn/` outside the chapters like `/families/`).

## `menu_inventory.py compare` against the old build

Every old address still answers. `/roots/` answers with a redirect to `/trees/` (its 71 text blocks are not on the new site: the page was removed on purpose).
All other pages keep every block. Two list pages, `/people/` and `/who/`, print about 2,000 "LOST" row hashes: this is the tool, not the site,
because the same `compare` of the old snapshot against the *old* build prints the same 1,258 lines (the 1,329 problems of the real comparison are those 1,258 plus the 71 of `/roots/`).
