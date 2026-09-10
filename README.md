# The Mazza Archive

An evidence-first family archive for the **Mazza** family of **Piedimonte Etneo** (province of
Catania, Sicily) — and of **Briatico** and **Scilla** in Calabria, of New York and Buenos Aires,
and of Brisbane.

> The Mazza name reached back **four generations** when this archive opened, stopping at a man with
> no dates at all. One day in the Sicilian registers took it to **seven generations** and
> **Mariano Mazza and Maria Catalano**, and joined **a hundred and ten cousins** to the line —
> every Sicilian step a document.
>
> The same day cost the archive its other headline. The Calabrian **Prostamo of Briatico** were said
> to run nine generations to **1697**. Audited, they are **documented to Domenico Prostamo, a sailor
> dead before 1886**, and **asserted for four generations above him** by a tree already shown to be
> six years out on two Sicilian births. **A surname is a poor guide to where a family comes from —
> and an undated pedigree is a poor guide to anything.**

Built from a MyHeritage tree contributed by **Michael Mazza**, exported 9 September 2026.
Sister archive to [The Falco Archive](https://github.com/daviddef/TheFalco).

## What is here

- **599 people**, 280 households, 63 places, 123 surnames.
  Only **69** of them have a death recorded anywhere — a measure of how undated this
  tree still is, not of who is alive.
- **The ancestors of Mia and Rocco.** 62 people across 10 generations, counted
  against the 2,046 there ought to be: **complete** for grandparents, **50%** at the third generation,
  **5.5%** at the seventh, **0.2%** at the tenth. What survives that far is one thread.
- **The Mazza name line runs seven generations** — from **Mariano Mazza**, born about 1815 and named
  only in his grandson's act of birth, to two children born in Brisbane. It was four generations deep,
  ending at an undated Rosario, on the morning the archive was built.
- **The four quarters.** Michael Rocco Mazza's four grandparents were born 1920–1928 in three towns
  that had no connection to each other, and all four were in Queensland by 1954.
- **Four plots in a row.** Those same four grandparents lie in **consecutive plots V-1026 to V-1029**
  at Nudgee, buried in the order they died — nineteen years between the first and the last.
- **Nine ships, named.** The tree recorded eighteen crossings and no vessel. The NAA passenger index
  gave nine: the *Toscana* out of Genoa for Sebastiano Mazza, 4 October 1949; the *Surriento*; the
  *Roma*; the *Palermo* that landed a sixteen-year-old Michele Mazza at Brisbane in 1925.
- **The Mazza and the Arena as names.** 120 Mazza in **6
  descent groups that no record joins**; 39 Arena in **one unbroken family**.
  The surname the archive is named for is the most fragmented thing in it.
- **Two emigrations, fifty years apart** — New York from 1906, Fremantle and Brisbane 1949–1957 —
  and a third branch to **Buenos Aires**.
- **133 family photographs**, downloaded before the MyHeritage links expired on 16 September 2026.

## The hundred and ten, joined

The export arrived as **fourteen disconnected components**: one of 479 people, one of **110
Piedimonte Etneo Mazza attached to this family by nothing at all**, and twelve fragments. Closing
that gap was the archive's largest open question, and it was closed on the day it opened.

**Piedimonte Etneo, Nati 1873, atto 3** names Salvatore Mazza's father as **«Rosario Mazza di
Mariano», aged 28**, and his mother as **Leonarda Bonanno di Gaetano**. Marriage proclamations of
**1898, 1902 and 1910** give Rosario's age again (53, 55, 65) and name three more sons —
**Salvatore, Giovanni, Ignazio** — with birth acts adding **Orazio** (1877), **Gaetano** (1880) and
**Santo** (c. 1882). The tree's unattached Rosario has a wife called **Leonarda** and sons
**Orazio, Ignazio and Giovanni**. One man.

All hundred and ten are the families of **Michael Rocco Mazza's great-great-uncles**. The main
component is now **581 people**.

The join is **declared**, not inferred: automatic merges here require evidence inside the export,
and this argument comes from outside it. It lives in `data/documented-joins.tsv` with its citation,
and is published in full at
[/the-hundred-and-ten](https://daviddef.github.io/TheMazza/the-hundred-and-ten/) so it can be
attacked.

The build still merges two records only on **evidence** — the same birth year, or the same parents,
or the same spouse and children. A shared name is not evidence: this tree holds four undated men
called Rosario Mazza and four called Giuseppe Arena. **58 shared names are still left
standing apart** rather than invent a descent.

## Method

| | |
|---|---|
| **Documented** | A named source with a reference, and where possible the scan. |
| **Inferred** | A reasoned conclusion from documented facts, with the reasoning written out so it can be overturned. |
| **Superseded** | Asserted in the family record, and now displaced by a document that says otherwise. |
| **Disputed** | Asserted in the family record but unsupported, or contradicted, by what can be seen. |
| **Family lore** | Told, remembered, not corroborated. Kept because it is precious; labelled because pretending otherwise is how family myths become family history. |

Most of this archive currently sits at a fourth level the Falco archive did not need: **asserted by
the family tree**. Converting those assertions into documents is the work.

**Dates are withheld for anyone 80 or younger.** Everyone in the tree is written
up in full — name, places, family, photographs, records — but the **134 people** who
would be 80 or younger today, and whose death is not recorded, have their dates held
back. Those dates are stripped in the build, not hidden by the page: they are not in the HTML and not
recoverable from the published site. People the tree records as dead keep their dates.

The blunter Falco rule — living people named and nothing else — is a switch
(`SUPPRESS_LIVING` in `tools/build.py`) and is currently **off**, because the test underneath it
treated 416 of 599 people as possibly alive in a family reaching back to
1697. A removal request is honoured within days, without argument and without requiring a reason.

## Running it

```bash
cd site
npm install
npm run dev      # http://localhost:4324
npm run build    # static output in site/dist
```

Deploys to GitHub Pages on every push to `main`.

## Layout

```
sources/mazza-myheritage.ged     the export everything is built from
tools/                           ged.py, build.py, build_more.py, build_spine.py, fetch_photos.py
data/                            audit.json, photo-manifest.json, ahnentafel.json
photos/deceased/                 published;  photos/living/ is gitignored
site/src/data/                   people, quarters, spine, places, families, crossings, burials
site/src/pages/                  the archive itself
```

## The work

No Italian civil register has been read for this family yet. The Antenati portal of the Italian
state archives holds the *stato civile* from 1809 for **Catania** (Piedimonte Etneo),
**Catanzaro / Vibo Valentia** (Briatico) and **Reggio Calabria** (Scilla), and it is free.
That, the National Archives of Australia passenger records that would name the ships, and the
Nudgee burial register are the next three things.
