# Twelve acts this archive cites by number, holds a scan of, and shows nobody

Written 23 September 2026 by the estate session, at David's request, for
whoever next works in this archive. **This is data, not a task.** Nothing has
been changed here; the images and the pages are exactly as they were.

## The finding

Twenty-eight images sit in `site/public/plates/` that no built page mentions.
**Twelve of them scan an act this archive's own prose cites by year and act
number.** The document is read, cited, and on disk; the reader is told about
it and never shown it.

| image | the page that cites the act | what it says |
|---|---|---|
| `pe-matr1836-atto17.jpg` | `/what-changed/` | «Piedimonte Etneo, Matrimoni 1836 atto 17 — Mariano Mazza, 30, bracciale, son of IGNAZIO and GIUSEPPA PULVIRENTI» |
| `pe-nati1843-atto101.jpg` | `/what-changed/` | «Nati 1843 atto 101 — Leonarda Bonanno born…» |
| `pe-nati1845-atto64.jpg` | `/the-name-line/` | «Nati 1845 atto 64; Matrimoni 1871 atto 14; Nati 1873 atto 3; Mor…» |
| `pe-matr1871-atto14.jpg` | `/the-name-line/` | the same sentence — the birth, marriage and death acts of the name line, all three cited, none shown |
| `scilla-nati1854-atto76.jpg` | `/what-changed/` | «Scilla, Nati 1854 atto 76 — Giovanni Arena born 30 April 1854, declared by his grandfather» |
| `scilla-nati1855-atto163.jpg` | `/people/michele-donato/` | «Nati 1855, atto 163 — born 3 October 1855» |
| `scilla-matr1888-atto63.jpg` | `/what-changed/` | «Scilla, Matrimoni 1888 atto 63 — Rocco Arena married» |
| `scilla-matr1885-atto73.jpg` | `/searched/` | «1885 atto 73 and atto 86: two of Rocco's brothers» |
| `scilla-matr1885-atto86.jpg` | `/searched/` | the same sentence |
| `scilla-matr1874-atto62.jpg` | `/searched/` | «Scilla, Matrimoni 1874, atto 62: Michele Donato's brot…» |
| `scilla-matr1899-atto62.jpg` | `/searched/` | «Scilla, Matrimoni 1899, atto 62 — outstanding» |
| `zambrone-matr1824-atto2.jpg` | `/searched/` | «Zambrone Matrimoni 1824, atto 2. FOUND.» |

Sixteen more are held and unshown with no act number in the filename, so this
audit cannot say what they answer:

- **Index pages** — `pe-1878-index`, `pe-1879-index-M`, `pe-1879-index-p72`,
  `mascali-1879-index`, `scilla-1861-index-A`
- **The whole 1844 Scilla processetto n20** — `-copertina`,
  `-donato-nascita`, `-sofi-nascita`, plus `scilla-matr1844-tavola-donato`
- **Three Scilla death acts** — `morti1891-atto22`, `morti1891-atto134`,
  `morti1895-atto133` — and `scilla-pubb1888-no63`
- **Four portraits** — `angela-mazza-1`, `michael-mazza-1`, `nancy-arena-1`

## The mechanism

**This archive has no `plates.json`.** In every other archive that holds
plates, each one is declared in a manifest and every declared plate does
reach a page — checked, and the count of declared-but-absent is zero in all
of them. These twenty-eight are declared nowhere, so nothing lists them and
nothing draws them. It is not a rendering fault and no page is broken.

## How it was measured

Filenames under `site/public/` tested against every `.html`, `.json`, `.js`,
`.xml` and `.css` file in a full build, asking only *does this name appear
anywhere*.

The first version of this audit parsed `src` / `href` / `srcset` attributes
and reported 195 unshown images in another archive. It was wrong: that
archive's plates reach the page through a JSON blob no attribute parser
sees. Asking whether the filename appears at all needs no theory about how a
page references a file, which is exactly why the first version failed. Each
of the twelve acts above was then confirmed by locating the sentence that
cites it, rather than by a pattern agreeing with itself.

## Three things checked and found clean

A list of faults without these would be misleading.

- **No self-contradiction on numbers.** Every built page was tested for two
  places giving different counts of the same noun. «25 sources» against «39
  sources named in the family's own export», and 276 households against «the
  1714 Riveli index 142 households», are different objects correctly stated.
- **No broken image reference anywhere in the build.**
- **`mazza-myheritage.ged` of 10 September is older than everything derived
  from it**, which is the right direction.

## One number for its own sake

90 open work-list items against 89 done, and the oldest running item has been
running thirteen days — the longest in the estate. A cadence observation, not
a criticism.
