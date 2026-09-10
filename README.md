# The Mazza Archive

An evidence-first family archive for the **Mazza** family of **Piedimonte Etneo** (province of
Catania, Sicily) — and of **Briatico** and **Scilla** in Calabria, of New York and Buenos Aires,
and of Brisbane.

> The family takes its name from its **shallowest** line. The Mazza of Piedimonte Etneo can be
> followed back four generations before the record stops at a man with no dates at all. The line
> that reaches furthest — **nine generations, to 1697** — is the Prostamo of Briatico, and it comes
> in through a grandmother. **A surname is a poor guide to where a family actually comes from.**

Built from a MyHeritage tree contributed by **Michael Mazza**, exported 9 September 2026.
Sister archive to [The Falco Archive](https://github.com/daviddef/TheFalco).

## What is here

- **599 people** (183 recorded, 416 living), 280 households,
  42 places, 123 surnames.
- **The four quarters.** Michael Rocco Mazza's four grandparents were born 1920–1928 in three towns
  that had no connection to each other, and all four were in Queensland by 1954. The lines behind
  them reach 1875, 1697, 1821, 1851 respectively.
- **Eleven generations** from Franco Antonino Prostamo, born at Briatico about 1697, to two children
  born in Brisbane in 2017 and 2019.
- **Two emigrations, fifty years apart.** Briatico and Scilla went to **New York** from 1906 — three
  of them off the same ship on 2 August 1906. Their relatives went to **Fremantle and Brisbane**
  1949–1957, every one of them out of Genoa. A third branch went to **Buenos Aires**.
- **Thirteen burials at Nudgee**, Brisbane — the same Catholic cemetery that holds five of the Falco.
- **133 family photographs**, downloaded before the MyHeritage links expired on 16 September 2026.
  The 73 belonging to the dead are published; the 60 belonging to the living are not.

## What it refuses to claim

The export is **not one tree**. It is **14 disconnected components**: one of
479 people, one of **111 Piedimonte Etneo Mazza joined to the rest
by nothing at all**, and twelve fragments. Whether those 111 are the same family is the highest-value
open question in the archive — and the single document that would settle it is named on the
[open questions](https://daviddef.github.io/TheMazza/open-questions/) page.

The build merges two records only on **evidence** — the same birth year, or the same parents, or the
same spouse and children. A shared name is not evidence: this tree holds four undated men called
Rosario Mazza and four called Giuseppe Arena. 15 genuine duplicates were merged;
**58 shared names were left standing apart** rather than invent a descent.

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

**Living people are named and nothing more** — no dates, no places, no records, no photographs.
Those fields are dropped by the build, not hidden by the page. A removal request is honoured within
days, without argument and without requiring a reason.

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
