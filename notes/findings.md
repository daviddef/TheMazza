# Findings

## 10 September 2026 — the archive established

Built from `sources/mazza-myheritage.ged`, exported from MyHeritage on 9 September 2026:
614 individuals, 212 families, 39 cited sources, 133 photographs.

### The shape of the family

Michael Rocco Mazza (b. 29 July 1988) is the proband; the archive is anchored on his two children,
**Mia Josephine (2017)** and **Rocco Francesco (2019)**. He is David Defranceski's brother-in-law
through the D'Arcy sisters — David married Cristina D'Arcy, Michael married Stefanie D'Arcy.

**Four grandparents, three towns:**

| | Born | Town | Line depth | Reaches |
|---|---|---|---|---|
| Sebastiano Mazza | 22 Oct 1920 | Piedimonte Etneo, Catania | 4 gen | 1879 |
| Domenica Prostamo | 3 May 1928 | Briatico, Vibo Valentia | **9 gen** | **1697** |
| Rocco Arena | 12 Oct 1924 | Scilla, Reggio Calabria | 6 gen | 1821 |
| Angela Polistena | 22 Jan 1925 | Scilla, Reggio Calabria | 4 gen | 1851 |

**The family takes its name from its shallowest line.** The Mazza descent runs out after four
generations at a Rosario Mazza with no dates at all. The deepest line is the **Prostamo of Briatico**,
eight generations, and it enters through a grandmother.

### The export is not one tree

It is **14 disconnected components**. The largest holds 479 people. The second holds
**111 Piedimonte Etneo Mazza** — a complete kindred with its own marriages and cousins — **joined to
the family by nothing at all**. This is the archive's top open question.

### A merge rule that had to be rewritten

The first build merged records on **name alone**. It fused four undated Rosario Mazza into one man
and produced an **eleven-generation Mazza descent no record supports** — a pedigree manufactured by a
bug. The rule now requires corroboration beyond the name: the **same birth year**, or the **same
position in the family** (same parents, or same spouse and children).

Result: **15 genuine duplicates merged** (including the whole of Frank Mazza's household, which the
tree holds twice as `@F153@` and `@F157@`), and **58 shared names deliberately left standing apart**.

### Two emigrations, fifty years apart

- **1894–1926, to America.** Fillipo Melluso, Domenica Anile and Concetta Anile came off the same
  ship at New York on **2 August 1906**; Michele Donato into New Orleans, 11 March 1908, out of
  Palermo; Rocco Arena into New York, 12 September 1913, out of Messina.
  FindMyPast's index of the NYC book indexes names the **ship *Napoli*** for Filippo Melluso, 1906
  (NARA T612, film 1463603) — *not yet confirmed against the manifest date*.
- **1949–1957, to Australia.** Every single one out of **Genoa**. Angela and Antonino Polistena to
  Brisbane 17 June 1949; Sebastiano Mazza to Fremantle 4 October 1949; Michael Antonio Polistena
  28 May 1950; Domenica Prostamo March 1951 with an infant son; Mariano Cavallaro May 1951;
  Venera and Luciano Cavallaro 6 October 1953; Rocco Arena December 1953; Francessco Prostamo,
  aged 56, 10 October 1957. Classic chain migration, readable straight off the dates.
- **A third destination: Buenos Aires.** A Prostamo branch, 23 Argentine events 1903–1962, and not
  one crossing recorded.
- **And one before all of them.** Michele Mazza, born Catania 1909, landed Fremantle 21 April 1925
  aged about sixteen, and died in Queensland in 1926.

---

## 10 September 2026 — the Nudgee register read

Source: **Brisbane Catholic Cemeteries deceased register**, via the endpoint recorded in the Falco
archive's `australian-records-method`. Nudgee is run by the Archdiocese, not the city council, so it
is absent from the Brisbane City Council grave search.

18 surnames swept → **90 register rows** → **19 matched** to this archive with plot, register number,
date of birth, date of death and date of interment.

### The four quarters lie in four consecutive plots

| Plot | | |
|---|---|---|
| **V-1026** | Sebastiano Mazza | 22 Oct 1920 – 2 Apr 2002 |
| **V-1027** | Domenica Prostamo *(entered as Domenica Mazza)* | 3 May 1928 – 29 Jan 2010 |
| **V-1028** | Angela Polistena *(entered as Angelina Arena)* | 22 Jan 1925 – 18 Sep 2018 |
| **V-1029** | Rocco Arena | 12 Oct 1924 – 29 Oct 1999 |

Two married couples, side by side, buried in the order they died — Rocco 1999, Sebastiano 2002,
Domenica 2010, Angela 2018. **Nineteen years between the first burial and the last, and the plots
were held.** Three towns six hundred kilometres apart, four separate sailings, four adjacent graves.

### Six corrections to the tree

| Person | Field | Tree said | Register says |
|---|---|---|---|
| Domenica Prostamo | born | March 1928 | **3 May 1928** |
| Angela Polistena | born | 23 January 1925 | **22 January 1925** |
| Antonio Micale | born | 1923 | **1 March 1924** |
| Giovanna Polistena | born | 12 December 1918 | **13 December 1918** |
| Venera Cavallaro | died | 9 June 2013 | **6 September 2013** |
| Rocco Bova | died | 2000 | **28 May 2002** |

**Venera Cavallaro's is not an error but a format**: 9/6 against 6/9 — a date written day-first and
read month-first. The commonest single error in transcribed genealogy. Check any date in this archive
that looks a month or two out.

### Method notes

- **Women are in the register under their married names.** Domenica Prostamo is Domenica Mazza;
  Angela Polistena is Angelina Arena; Angelina Pagano is Angelina Armanno. A maiden-name search
  returns nothing. The matcher therefore accepts the spouse's surname as well as the person's own.
- **Prostamo, Melluso, Anile, Trungadi, Mazzitelli and Calarco return zero** at Nudgee — the Calabrian
  maiden names simply are not there, for the reason above.
- Adjacent plot numbers are a reliable signal of a married pair: V-0394/V-0395 (Cavallaro),
  V-0718/V-0719 (Armanno), V-1038/V-1039 (Bova), V-0116/V-0117 (Mazza), CHAP-207-CL/CR (Micale).

---

## Access notes, 10 September 2026

- **FamilySearch: blocked.** Site-wide `Error 15 — Access Denied` from the in-app browser, on the
  homepage as well as on search URLs, naming the proxy IP. Not a login problem. The full-text
  endpoint in `familysearch-fulltext-method` could not be reached at all this session.
- **Antenati: blocked.** 403 to curl, to WebFetch and to the in-app browser, including the home page.
  The Falco notes record Antenati rate-limiting to a blanket 403 "for roughly half an hour" after
  heavy use; this looks like the same behaviour, at a longer interval. **Retry before assuming it is
  permanent** — the endpoints in `antenati-method` are the right ones.
- **FindMyPast: works**, on a trial that ends 16 September 2026. Consistent with the Falco verdict,
  its Italian holdings are the FamilySearch index re-hosted. Its US passenger indexes are usable and
  gave the *Napoli*.
- **Brisbane Catholic Cemeteries: works**, no login, POST form. The single most productive source of
  the day.

---

## 10 September 2026 — the ships

Source: **National Archives of Australia, passenger arrivals index 1898–1972** (`PassengerSearch.aspx`),
read as a guest, no login. The index is arranged by **voyage**: one item is one ship on one date, and
every passenger aboard shares the item number.

18 surnames swept, then 18 targeted name searches. **Nine of the eighteen crossings now have a named
vessel.**

| Date | Who | Ship | From | To | NAA item |
|---|---|---|---|---|---|
| 21 Apr 1925 | Michele Mazza | ***Palermo*** | Messina | **Brisbane** | 12260784 |
| 8 May 1949 | Carmelo Armanno | ***Napoli*** | Naples | Australia | 9245202 |
| 17 Jun 1949 | Antonino Polistena | ***Surriento*** | **Naples** | Australia | 9245788 |
| 4 Oct 1949 | Sebastiano Mazza | ***Toscana*** | Genoa | Melbourne | 9243236 |
| 13 May 1951 | Mariano Cavallaro | ***Ravello*** | **Messina** | **Brisbane** | 30133235 |
| 23 Sep 1953 | Venera Cavallaro | ***Surriento*** | Italy | **Fremantle** | 30133845 |
| 23 Sep 1953 | Luciano Cavallaro | ***Surriento*** | Italy | **Fremantle** | 30133845 |
| 27 Dec 1953 | Rocco Arena | ***Sydney*** | Genoa | Fremantle | 32967991 |
| 10 Oct 1957 | Francessco Prostamo | ***Roma*** | Genoa | Fremantle | 30132189 |

### The Surriento lesson

The tree has Venera and Luciano Cavallaro arriving at **Brisbane on 6 October 1953**. The index has
them at **Fremantle on 23 September 1953**, on one item. **Both are true.** A ship out of Italy made
Fremantle first and worked round the coast; a family remembers the day they got off, not the day the
ship first touched Australia. Neither date is wrong and the archive keeps both — the same reconciliation
applies to Rocco Arena (Fremantle 27 Dec 1953, Brisbane "December 1953") and probably to Mariano
Cavallaro.

### Corrections

- **Michele Mazza** — the tree says Fremantle, from "Italy". The index says **Brisbane**, from
  **Messina**, on the *Palermo*. He arrived at the port his family would settle in twenty-four years
  later, which makes the "was he the reason?" question sharper, not weaker.
- **Antonino Polistena** — embarked at **Naples**, not Genoa.
- **Mariano Cavallaro** — **Brisbane**, from **Messina**, not Fremantle from Genoa.
- **Francessco Prostamo** — date, port and embarkation all confirmed exactly. A **Francesca Prostamo**
  is on the same voyage and is **not in the family tree**.

### Not found

**Domenica Prostamo**, March 1951, is not in the index under Prostamo *or* under Mazza. She travelled
as a married woman with a son under three; the index is transcribed from handwritten manifests and
she is probably under a misspelling. **Search the voyage, not the person** — find the Genoa sailing
reaching Fremantle in March 1951 and read the manifest for the family group.

### Method note

`PassengerSearch.aspx` POSTs to an interstitial `PleaseWait.aspx`, whose body auto-submits an empty
form to `PassengerSearch_Result.aspx`. So a scripted sweep is: GET the form for its `__VIEWSTATE`,
POST the search, then POST empty to `PassengerSearch_Result.aspx` and parse. Session cookies carry
the query. Results are paginated at 20, so a bare surname sweep truncates — use given names for
anything specific.

---

## 10 September 2026 — the publication rules changed, and the focus sharpened

**Living-person suppression switched off.** The inherited Falco rule (a living person is named and
carries nothing else) was catching **416 of 599 people**, including the whole undated Piedimonte
Etneo cluster, because its test reads "no death recorded" as "possibly alive". In a tree reaching
1697 that is wrong far more often than it is right — only **69 people** in this tree have a death
recorded anywhere. It is now a switch (`SUPPRESS_LIVING`), not a deletion.

**Replaced by a date rule.** *Dates are withheld for anyone who would be 80 or younger today and
whose death is not recorded* — **134 people**. Names, places, families, photographs and records are
all published; only dates are held back, and they are stripped in the build rather than hidden by the
page, so they are not in the HTML. Anyone the tree records as dead keeps their dates: Mary Rosa Mazza
died at sixteen, and an archive that will not say so is not telling the truth about this family.
Boundary verified — born 1946 (age 80) withheld, born 1945 (age 81) shown, zero leaks in the JSON.

### The ancestors of Mia and Rocco, counted

62 people across 10 generations, against 2,046 possible:

| Gen | Who | Found | Possible | % |
|---|---|---|---|---|
| 1 | parents | 2 | 2 | 100 |
| 2 | grandparents | 4 | 4 | 100 |
| 3 | great-grandparents | 4 | 8 | 50 |
| 4 | 2× great | 8 | 16 | 50 |
| 5 | 3× great | 15 | 32 | 47 |
| 6 | 4× great | 12 | 64 | 19 |
| 7 | 5× great | 7 | 128 | 5.5 |
| 8 | 6× great | 6 | 256 | 2.3 |
| 9 | 7× great | 2 | 512 | 0.4 |
| 10 | 8× great | 2 | 1024 | 0.2 |

Half of the missing half at generation 3 is the **D'Arcy** side, through the children's mother,
carried here only as far as her parents — that family has its own research and is not duplicated.

### The names, compared

**Mazza — 120 bearers, 6 descent groups, no record joining them.**

| Group | People | Component | Span | Town |
|---|---|---|---|---|
| 1 | 26 | 1 | 1879–1952 | Brisbane / Piedimonte Etneo — **the line to the children** |
| 2 | **86** | 2 | 1850–1885 | Piedimonte Etneo — headed by a **Rosario Mazza b. 1850** |
| 3 | 5 | 2 | undated | — |
| 4–6 | 1 each | 8, 9, 10 | undated | fragments joined to nothing |

**Arena — 39 bearers, ONE unbroken family**, 1821–1937, all of Scilla.

That contrast is the finding. It is not that the Arena were better recorded: *Arena* entered this
archive through one household somebody had worked on, and *Mazza* entered as a surname. **The name a
family is known by tells you least about it** — and group 2's Rosario Mazza, born 1850 in the same
small town as Salvatore, remains the highest-value join in the archive.

---

## 10 September 2026 — two more merge bugs, found from a grave in New Jersey

Chasing the three Polistena buried at **Arneytown, New Jersey** turned up a duplicate the build had
refused to merge:

> **Joseph A Polistena** (b. 1917) and **Joseph Polistena** (b. 1916) — same parents (Giuseppi
> Polistena & Giuseppa D'Ascoli), same wife (Santa Polistena), **the same full death date,
> 15 February 2012**, and the same grave. One man.

The merge rule keyed on the **exact normalised name**, so a **single middle initial** defeated it
entirely. The same bug was hiding **Michael Mazza / Michael Rocco Mazza** — same parents, both born
1988 — which is the very duplicate that was spotted by hand on the first pass of this archive and
then quietly refused by the code.

**The fix.** Names are compared a second time at a looser key — *surname plus first forename*, middle
names and initials dropped. Because that test is weaker, the corroboration required is stronger:

- an identical **full** death date (day, month and year); **or**
- identical parents **and** identical spouse; **or**
- the same birth year **plus** identical parents or identical spouse.

A shared surname and forename alone still prove nothing. Dry-run across all 614 exported individuals,
the widened rule finds **exactly two** further people — the two above — and no false positives.
Duplicates merged: 15 → **17**. People: 599 → **597**.

**The lesson worth keeping**: the first rule was written to stop over-merging, and it did. It then
under-merged in the one shape it could not see. Both failures come from treating *the name string* as
the unit — the unit is the person, and the evidence for identity is the family and the dates around
them.

---

## 10 September 2026 — the 1879 register read, and a useful null

**Antenati came back.** Method note first, because it has changed since the Falco work:

- The **HTML pages remain Cloudflare-blocked to curl** (403), so search and record pages need the browser.
- The **IIIF images now serve directly to curl** with a `Referer: https://antenati.cultura.gov.it/`
  header. The Falco note recorded them as blocked from curl *and* the browser, readable only inside
  the Mirador viewer. They are not any more. **Reading a register is now an ordinary download.**
- **Rate limiting is severe and it is on the HTML, not the images.** Eight rapid same-origin fetches
  produced a blanket 403 across the whole site — including the home page — that took well over
  twenty minutes to clear, and a second burst re-triggered it. Navigate slowly; fetch images freely.

### Piedimonte Etneo has no name index

`/search-nominative/?cognome=Mazza&localita=Piedimonte Etneo` returns *"Nessun risultato trovato"*
with the explanation that only part of the registers are indexed. Same as Arienzo. Images only.

### The volume

**Piedimonte Etneo, Stato civile italiano, Nati 1879** — Archivio di Stato di Catania, segnatura
8956, ark **`an_ua83492`**, **81 images**. Two acts to an image (act 126 on image 54, act 167 on
image 74), an **alphabetical Indice Annuale on pages 72–73** (images 79–80), back cover on 81.
A **supplement volume** exists: segnatura 8957 suppl. 2, ark **`an_ua83493`** — not yet read.

### The finding: a null

The M section of the annual index carries twenty-three entries and **exactly two Mazza**:

> **Mazza Rosaria — act 167** · **Mazza Venerio — act 205**

**There is no Salvatore Mazza in the 1879 births of Piedimonte Etneo.**

The index covers the whole year including acts filed in the supplement, which is why act 205 appears
there although the main volume stops around act 175.

### Act 167, transcribed

> L'anno milleottocentosettanta**nove**, addì **ventinove** di **Ottobre**, a ore antimeridiane nove
> e minuti venticinque… è comparso **Mazza Pasquale**, di anni **cinquanta**, **bracciante**,
> domiciliato in Piedimonte Etneo… alle ore antimeridiane sei e minuti trenta del dì **ventotto**…
> nella casa posta in **Via Terremorte** al numero senza, da **Greco Concetta, industriosa, sua
> moglie, seco lui convivente**… è nato un bambino di sesso femminino… a cui dà il nome di **Rosaria**.

A marginal note added in 1903: she **married Giuseppe Monforte, son of the late Salvatore, on
26 April 1903**.

So there is a **second Mazza household at Piedimonte Etneo**: **Pasquale Mazza** (b. c. 1829, a
day-labourer) and **Concetta Greco**, of **Via Terremorte**. It is not Rosario's, and it does not
join the line — but it is the **first Italian record this archive has read for any Mazza**.

### What the null means

Salvatore Mazza's birth — "1879, Piedimonte Etneo" — is now **disputed**: asserted in the family
record, unsupported by the register that should contain it. Three live possibilities, in order:

1. **The year is wrong.** The tree's 1879 carries no source. 1875–1885 are all digitised.
2. **The town is wrong.** He died at *Catania*; the family also appears at **Mascali** and **Giarre**.
3. **He is in the supplement**, `an_ua83493`, which holds the late and irregular registrations.

Until one of those is settled the head of the Mazza line stays where it was — a man called Rosario
about whom exactly one thing is known.

---

## 10 September 2026 — all three follow-ups run, all three empty

David asked for the three routes out of the 1879 null to be taken together. They were, and none of
them found Salvatore Mazza.

### 1. The 1879 supplement — act 205 read

**`an_ua83493`**, segnatura 8957 suppl. 2, **18 images**, acts ~183–218 at two to an image. The main
volume ran out of pages around act 175; the annual index covers both books, which is why act 205 is
indexed in one and written in the other.

> **Act 205.** L'anno milleottocento **settantanove**, addì **quattordici** di **Dicembre**… è
> comparso **Mazza Salvatore**, di anni **trentaquattro**, **bracciante**, domiciliato in Piedimonte
> Etneo… del dì **dodici**… nella casa posta in **Via Terremorte** al numero senza, da **Greco
> Concetta, industriosa, sua moglie**… è nato un bambino di sesso mascolino… a cui dà il nome di
> **Venerio**.
> Witnesses: **Mazza Antonino**, 35, bracciante; **Morabito Angelo**, 38, bracciante.
> Marginal note: married **Rosaria Greco di Carmelo**, 16 November 1908.

### 2. The surrounding years at Piedimonte Etneo

| Year | Ark | Mazza births in the annual index |
|---|---|---|
| 1877 | an_ua83490 | **Antonino** (act 164), **Grazia** (act 168) |
| 1878 | an_ua83491 | **none** |
| 1879 | an_ua83492 / 83493 | **Rosaria** (167), **Venerio** (205) |
| 1880 | an_ua83494 | **Gaetano** (act 66) |
| 1881 | an_ua83495 | **none** |

### 3. The neighbouring comuni

- **Mascali 1879** (`an_ua81758`, 85 images) — **no Mazza in the index at all.**
- **Giarre 1879** (`an_ua80924`, 128 images) — **no Mazza in the index at all.**

### What was found instead: three Mazza men on one street

The two 1879 acts, read in full, document a Mazza kindred of **day-labourers on Via Terremorte**:

| | Born about | Trade |
|---|---|---|
| **Mazza Pasquale**, 50 in Oct 1879 | c. 1829 | bracciante |
| **Mazza Salvatore**, 34 in Dec 1879 | c. 1845 | bracciante |
| **Mazza Antonino**, 35 in Dec 1879 (witness) | c. 1844 | bracciante |

**None of them is Rosario.**

### An oddity left standing

Pasquale (50) and Salvatore (34) each declare a child born on **Via Terremorte** to a wife named
**Greco Concetta**, **six weeks apart** — 28 October and 12 December 1879. One woman cannot have
borne both. Either they are two women of the same very common name married to two Mazza men on one
street (brothers or cousins — entirely ordinary in a Sicilian town), or one act has been misread.
Both plates are published so anyone can check.

### The live hypothesis now

There **is** a Salvatore Mazza of Piedimonte Etneo, a bracciante of Via Terremorte born about
**1845** — but he is a *father* in 1879, not a newborn. The tree may have a **generation
compressed**. What would settle it is a **marriage act**, which names both fathers.

Remaining: PE 1875, 1876 and 1882 onward; the PE marriage registers; the acts behind index entries
164, 168 and 66; and Catania, where Salvatore died in 1929.

### Method addendum

Nine indexes across three comuni cost **~14 browser navigations and no register read-throughs**,
because every volume carries an alphabetical *Indice Annuale* in its last pages. The working recipe:

1. Browser once per volume to lift the container id from the live DOM.
2. `tools/manifest.py <container>` — the manifest serves fine to **curl**.
3. `tools/index_sheet.py <imageId>` — crops the four index columns server-side via IIIF `pct:` and
   stacks them into one readable sheet. The index is normally at **n−2** or **n−3**.
4. Calibrate act → image on any one page (**two acts per image**), then crop the act.

**Watch for conservation sheets.** Several of these scans have a black card laid over half the
opening, hiding whole columns — 1878's M section is only readable because it falls on the *other*
index page.

---

## 10 September 2026 — items 1–5: Rosario found, and a generation above him

David asked for the five Piedimonte Etneo follow-ups to be run together. Salvatore is still missing.
Everything else changed.

### The key act: marriage 5 of 1876

**Piedimonte Etneo, Matrimoni 1876, atto 5** (`an_ua83397`, image 7) — 16 January 1876, 7.05 p.m.

> 1° **Mazza Salvatore**, di anni **trentaquattro**; **bracciante**, nato in Piedimonte Etneo,
> residente in Piedimonte Etneo, **figlio di Venerio**, residente in Piedimonte Etneo, **e di
> Cavallaro Domenica**…
> 2° **Sciacca Concetta**, di anni **diciannove**; contadina, nata in Piedimonte Etneo, **figlia del
> fu Antonino**… **e di Greco Rosaria**.

**VENERIO MAZZA × DOMENICA CAVALLARO** — a couple of the 1810s–20s, the earliest Mazza this archive
can name from a document, and **entirely absent from Michael Mazza's family tree**.

It also explains a name: three years later Salvatore's son is christened **Venerio**. In Sicily the
first son takes the paternal grandfather's name. **The custom and the document agree.**

### Rosario Mazza, documented at last

| | |
|---|---|
| **Rosario Mazza** | aged **31** in Oct 1877, **32** in May 1880 → born **c. 1846–48**, *bracciante* |
| wife | **Leonarda Bonaccorso** (contadina / industriosa) |
| sons | **Orazio**, 21 Oct 1877 (act 168) · **Gaetano**, 5 May 1880 (act 66) |
| streets | via Grotta Nicodemo (1877) · Via S. Basilio (1880) |

The archive carried Rosario as a name with one asserted fact. He now has an age, a trade, a wife,
two sons and two streets.

### Three households, from six acts

| Father | Born | Wife | Children | Streets |
|---|---|---|---|---|
| **Pasquale Mazza** | c. 1829 | **Concetta Greco** | Antonino (1877/164), Rosaria (1879/167) | via Cappello Campagna → Via Terremorte |
| **Salvatore Mazza** | c. 1841–45 | **Concetta Sciacca** | Venerio (1879/205) | Via Terremorte |
| **Rosario Mazza** | c. 1846–48 | **Leonarda Bonaccorso** | Orazio (1877/168), Gaetano (1880/66) | via Grotta Nicodemo, Via S. Basilio |

Plus **Mazza Antonino, 35** (b. c.1844) witnessing act 205 — a fourth adult Mazza man. Pasquale,
Antonino, Salvatore and Rosario were born c.1829, c.1844, c.1845 and c.1846: **the last three within
two years of each other, which is what brothers look like.**

### The join to the hundred and ten

The tree's second component is headed by **Rosario Mazza b. 1850**, and among his children it lists
an **Orazio**. The register gives **Rosario Mazza b. c.1846–48** of the same town whose son is
**Orazio**. Right man, right decade, right town, right child's name — **far stronger than a shared
surname, and still not proof**: the tree dates Orazio to 1883, the register to 1877.

**What closes it: Rosario's own marriage act.** If his parents are Venerio Mazza and Domenica
Cavallaro, he and Salvatore are brothers and the whole kindred is one family. **Not in the 1875 or
1876 marriage registers** — both read — so **1874 or earlier**.

### Two corrections

1. **The index is not the act.** The 1877 index lists act 168 as *Mazza Grazia*; the act says
   **Orazio**, a boy. An index is a clerk's abstract and it can be wrong.
2. **A misreading of mine, caught by a second document.** From act 205 alone this archive gave
   Salvatore's wife as *Greco Concetta*, producing an absurdity — two women of that name on one
   street bearing children six weeks apart. The 1876 marriage index settles it: Salvatore married
   **Concetta Sciacca**. Pasquale is the one married to Concetta Greco, confirmed twice.
   **The absurdity was the tell.**

### Also found

- **1882**: Mazza Pietro (act 24) and Mazza Santo (act 75) — fathers not yet read.
- Marriage volumes exist at Piedimonte Etneo from **1866** (`an_ua83386` onward).

### Method

Volumes run **two acts per image at 1879 but three at 1877** (two on the left page, one on the
right), so the act→image mapping must be **calibrated per volume** — `tools/act_locate.py` stacks
the left margins of four images so one look establishes the offset. `tools/build_acts.py` turns the
transcribed acts into households; key households on **names only**, since a clerk may call the same
woman *contadina* one year and *industriosa* the next.

---

## 10 September 2026 (later) — the father named, and a correction

**Correction first.** The previous entry gave Salvatore Mazza's father as **Venerio**, read from
atto 5 of 1876, and inferred that Salvatore's son *Venerio* (1879) was named for his paternal
grandfather in the ordinary Sicilian way. **Both were wrong.**

**Matrimoni 1874, atto 26** (`an_ua83395`, image 24), 19 July 1874, spells the name out in full:

> …sono comparsi **Antonino Mazza**, di anni **trentuno**, bracciante, qui nato, domiciliato e
> residente, **figlio d'Innocenzio**, bracciante, **e di Domenica Cavallaro**, industriosa, ivi
> domiciliata — e **Rosa Raiti**, di anni **venti**, industriosa, qui nata… figlia di **Giuseppe**,
> bracciante, e di **Agata Pennisi**, industriosa.
> Witnesses: **Angelo Russo fu Venero**, 40, bracciante; **Felice Russo fu Angelo**, 60, bracciante.

Magnified, atto 5 of 1876 reads **«…o di Senzio…»** — the standard Sicilian contraction of
**Innocenzio**, not *Venerio*. The two acts agree; the first reading did not.

**The naming inference is withdrawn.** Where the name *Venerio* comes from is now open — the
Cavallaro side, a godparent, or a generation nobody has reached.

### What is now established

**INNOCENZIO MAZZA × DOMENICA CAVALLARO**, a couple of the 1810s–20s, both recorded as living at
Piedimonte Etneo in the 1870s. Two documented sons:

| Son | Age at marriage | Born | Married | Act |
|---|---|---|---|---|
| **Salvatore Mazza** | 34, Jan 1876 | c. 1841 | **Concetta Sciacca**, 19, *fu Antonino Sciacca × Rosaria Greco* | Matrimoni 1876, atto 5 |
| **Antonino Mazza** | 31, Jul 1874 | c. 1843 | **Rosa Raiti**, 20, *Giuseppe Raiti × Agata Pennisi* | Matrimoni 1874, atto 26 |

**Salvatore and Antonino are brothers** — two independent acts, two years apart, naming the same
mother. This is the first proved sibling relationship in the Sicilian line.

Note also **Raiti**: a surname that appears in the tree's unjoined 110-person cluster.

### Rosario is still unattached

Rosario Mazza (b. c. 1846–48, × Leonarda Bonaccorso) does **not** appear in the marriage indexes for
**1873, 1874, 1875 or 1876** — 1874 has only Antonino, 1876 only Salvatore. So either he married
**1872 or earlier**, or **in his bride's comune**, which is the commoner practice. Bonaccorso is a
Catania-area name; Fiumefreddo, Calatabiano, Linguaglossa and Castiglione are the neighbours to try.

**Alternative route:** Rosario's own **death act** would name his parents, and death registers carry
the same alphabetical annual index. That is probably cheaper than sweeping six comuni of marriages.

### Method note

**Conservation cards are the real obstacle**, not Cloudflare. Black cards laid across an opening hide
whole columns in the 1873 and 1874 index scans and in several act pages. The workaround is to crop
the *other* half of the opening: act 26's left column is buried, but the same text runs again in the
right-hand column, and `pct:52,44,46,40` recovered it in full.

**And magnify before trusting a forename.** «Senzio» at full-page scale looked like «Venerio». One
IIIF crop at `pct:40,17,34,10` settled it.

---

## 10 September 2026 — the Queensland register: Michele was his brother

**Source: `familyhistory.bdm.qld.gov.au`** — the Registry's historical index. Free, no account,
deaths to 1996, marriages to 1951, births to 1926. **Every birth and death entry names both parents,
and the form will search on a PARENT'S name.** That makes it a reconstruction tool rather than a
lookup: search the father, get the children.

### Michele Mazza, answered

> **Michali Mazza** · death registration **14 November 1926** · **1926/C/3983** ·
> father **Salvatori Mazza** · mother **Maria Lecota**

*Lecota* is the index's rendering of **Nicotra**. The same father-search returns:

> **Rosario Mazza**, born **1899** · died **19 March 1986** · **1986/2455** ·
> father **Salvatore Mazza** · mother **Maria Concetta Nicotra**

Same couple, spelled properly. So **Michele Mazza was a son of Salvatore Mazza and Maria Nicotra —
Sebastiano's elder brother.** He came out alone at sixteen, on the *Palermo*, and was dead within
nineteen months. **Twenty-four years later the family followed him to the port he had landed at.**
The registration code **C** means a country event: he did not die in Brisbane.

### Three more confirmations

| Registration | What it proves |
|---|---|
| **Maria Nicotra Mazza**, d. 24 Sep 1963, 1963/B/61348, father **John Nicotra**, mother **Venera Cassaneti** | The tree's parentage for her, exactly. Matches her Nudgee interment of 25 Sep 1963, plot V-0044. |
| **Mary Rosa Mazza**, d. 3 Aug 1968, 1968/B/936, father **Sebastiano Mazza**, mother **Domenica Postamo** | Sebastiano × Domenica, and their daughter, who was sixteen. Matches Nudgee V-0165. |
| **Maria Mazza** m. **Rosario Coco**, 2 Dec 1939, 1939/C/4207 | Closes this archive's Nudgee identification of "Maria Coco, 1922–2012" as Maria Mazza. |

Also **Rosario Mazza m. Annie Vergina Di Mauro, 8 Jan 1949** (1949/B/20688) — not in the tree, and
unresolved against the Angela buried beside him at Nudgee.

### Salvatore Mazza and Maria Concetta Nicotra — the household now documented

| Child | Born | Died |
|---|---|---|
| **Rosario** | 1899 | 19 Mar 1986, Brisbane |
| **Michele** | c. 1909 | 14 Nov 1926, Queensland |
| **Sebastiano** | 1920 | 2 Apr 2002, Brisbane |
| **Maria** | 1922 | m. Rosario Coco 1939; d. 2012 |

### And the way in to Salvatore's own birth

Salvatore is still absent from six years of the Piedimonte Etneo register. But **Rosario was born in
1899**, and an Italian birth act states the declaring father's **age**. Find **Piedimonte Etneo,
Nati 1899, the Rosario Mazza act** and it dates Salvatore to within a year or two — turning a blind
sweep into a single lookup. **That is the next Antenati target.**

### Method

Search the **parent**, not the person, when hunting siblings. The index spells names as the clerk
wrote them — *Michali*, *Salvatori*, *Lecota*, *Postamo* — so search loosely and expect the surname
you want to be mangled. Images are paid; none were bought, and none were needed.

---

## 10 September 2026 — Arneytown: one soldier, one grave

**Source: the VA's Nationwide Gravesite Locator** (`gravelocator.cem.va.gov`). Free. The search form
POSTs to `/ngl/result` with `lastName`, `firstName`, `middleName`, each with an `…Opt` matching mode,
plus optional `cemetery` and birth/death month and year — so it can be driven directly.

The family tree places **three** Polistena at the Brigadier General William C. Doyle Veterans
Memorial Cemetery, Wrightstown, New Jersey. The register holds **two people in one plot**:

> **POLISTENA, JOSEPH** — **PFC US ARMY**, **World War II** — 29 January 1917 – 15 February 2012 —
> **Section O3, Site 8647**
> **POLISTENA, SANTA** — 17 December 1920 – 8 September 2008 — **Section O3, Site 8647** —
> *"WIFE OF POLISTENA, JOSEPH"*

**Joseph Polistena served as a Private First Class in the United States Army in the Second World
War.** That is the service that earned the plot; Santa is buried with him as his wife.

### Two things it settles

1. **The tree's "Joseph A Polistena" and "Joseph Polistena" are one man** — which is exactly what
   this build's middle-initial merge rule concluded from the shared full death date, *before* the VA
   confirmed it. The rule was right, and now it is corroborated by an independent record.
2. **Santa's death is 8 September 2008, not 9 August.** The tree read the American **09/08/2008**
   day-first. **That is the second date-format error found in this archive today**, after Venera
   Cavallaro's 9 June / 6 September. Both are the same failure in opposite directions, and both were
   caught by a second source rather than by inspection.

**Standing warning for this archive:** it draws on Australian, Italian and American records at once,
and those three traditions write dates differently. Any date that looks a month or two out is a
transposition until proved otherwise.

---

## 10 September 2026 (later still) — eight years clear, and the wall

### PE births 1875 and 1876 read

| Year | Mazza births |
|---|---|
| 1875 | **Mazza Giovanni** (act 64) |
| 1876 | **Mazza Grazia** (41), **Mazza Domenica** (142) |

**No Salvatore.** With 1877–1882 already read, that is **eight consecutive years of the Piedimonte
Etneo birth register with no Salvatore Mazza in them**, plus Mascali and Giarre for 1879.

*Caution on the 1876 "Grazia":* the 1877 index miscopied an **Orazio** as *Grazia*. Index readings of
that name are not safe until the act is read.

### The wall: what Antenati does NOT hold for Piedimonte Etneo

| Series | Coverage |
|---|---|
| Nati, *Stato civile della restaurazione* | 1860–1865 (an_ua72404+) |
| Nati, *Stato civile italiano* | 1866–1885 (an_ua83479+) |
| **Matrimoni** | **1866–1893 only** (an_ua83386–83414) |
| Nati 1898–1900 | **not digitised** — "Nessun risultato trovato" |

**This closes both of the good routes.** Salvatore married Maria Concetta Nicotra about **1897**;
their son Rosario was born **1899**. Either act states Salvatore's age. **Neither is on Antenati.**
They must be ordered from the **Archivio di Stato di Catania** or requested from the **comune of
Piedimonte Etneo**.

### A negative worth recording: the 1875 Maria Nicotra is someone else

The 1875 index carries **Nicotra Maria, act 34**, and the tree gives Salvatore's wife as Maria
Nicotra born 1875 at Piedimonte Etneo. The act was read:

> …è comparso **Alfio Nicotra**, di anni **sessantotto**; bracciante… nella casa posta in **via San
> Basile**… da **Angela Previtera sua moglie**, giornaliera… è nato un bambino di sesso femminino…
> a cui dà il nome di **Maria**.
> Margin: married **Giuseppe Nicito fu Vincenzo**, 19 July 1911.

Daughter of **Alfio Nicotra (b. c. 1807) and Angela Previtera** — not of **John Nicotra and Venera
Cassaneti**, whom the Queensland death register names as our Maria's parents. **Different woman.**
Two Maria Nicotra born in one small town within a few years is exactly what this archive keeps
running into.

Worth noting anyway: the Nicotra of act 34 lived on **via San Basile** — the same street as Rosario
Mazza in 1880.

### Where this leaves it

The Sicilian line is now **documented back to Innocenzio Mazza × Domenica Cavallaro** through
Salvatore (b. c.1841) and Antonino (b. c.1843) — but **the Salvatore who married Maria Nicotra and
fathered Rosario (1899), Michele (c.1909), Sebastiano (1920) and Maria (1922) is a different, younger
man**, and he is in none of the digitised registers.

**The tree's dates are the weak link, not the search.** This archive has now corrected the tree on
Domenica Prostamo's birth, Antonio Micale's, Venera Cavallaro's death and Santa Polistena's death.
A birth year with no source behind it is a family estimate until a record says otherwise — and
"Salvatore Mazza, born 1879" has no source behind it.

---

## 10 September 2026 — SALVATORE FOUND. The Mazza name line goes back to Mariano.

**FamilySearch came back**, and its full-text search over Piedimonte Etneo did in twenty minutes what
eight Antenati registers could not.

### Why Antenati alone could never have found him

FamilySearch holds Piedimonte Etneo material Antenati does not: **parish registers** (Baptism,
Marriage, Death Certificate, Confirmation — undated series), **marriage proclamations 1896**, and
civil series running **1909–1924, 1911–1920, 1912–1921, 1921–1929, 1922–1929**. Antenati's marriages
stop at 1893 and its births at 1885.

Endpoint, exactly as `familysearch-fulltext-method` records it:

```
/service/search/fulltext/search?count=25&m.defaultFacets=on&m.queryRequireDefault=on
  &offset=0&q.anyPlace=Piedimonte%20Etneo&q.text=Mazza%20Nicotra
```

Each hit returns `content.textDocument` — the full machine transcription of the page. Mine it with a
regex and keep the context.

### Three records that converged

**1. The parish marriage, 25 April 1898** (Latin):

> …pro matrimonio contrahendo inter **Salvatore Mazza filium Rosarii et Leonarda Bonanno** sponsum ex
> una parte et inter **Maria Nicotram filiam Joannis et Venera** … sponsam ex altera.

**2. The civil death act, Piedimonte Etneo, Morti 1929, atto 9**, declared 20 September 1929:

> …è morto **Mazza Salvatore di anni cinquantasei**, contadino, residente in questa Frazione **Vena**,
> **nato in questo Comune**, **da fu Rosario** già contadino… **e da Bonanno Leonarda**, contadina…
> **Marito di Nicotra Maria**. — in **Contrada Grotta Nicodemo**.
> Declarants: Pennisi Michele, 62, of Linguaglossa; **Mazza Giovanni, 54** — almost certainly the
> Mazza Giovanni of the 1875 index, act 64, and therefore Salvatore's brother.

Aged 56 on 19 September 1929 ⇒ born **late 1872 or early 1873**. That is what pointed at the volume.

**3. THE BIRTH ACT — Piedimonte Etneo, Nati 1873, atto 3** (`an_ua83486`, images 3–4):

> L'anno milleottocentosettantatre nel giorno **sei** [Gennaro]… è comparso **Rosario Mazza DI
> MARIANO**, di anni **ventotto**, bracciante, qui domiciliato… un bambino di sesso maschile… nato
> **il giorno cinque corrente Gennaro** alle ore sette antemeridiane, dalla di lui moglie **Leonarda
> Bonanno di Gaetano**… **Contrada Terremorte**… al quale figlio dichiara di dare il nome di
> **Salvadore**.
> Witnesses: Pasquale Pagano di Natale, 21; Salvadore Calì fu Rosario, 23, braccianti.

### The Mazza name line, as it now stands

| Gen | | |
|---|---|---|
| 1 | **Mariano Mazza** | b. c. 1815–20. Named only as Rosario's father. |
| 2 | **Rosario Mazza** | b. c. 1844–45 (28 in Jan 1873, 31 in Oct 1877, 32 in May 1880) × **Leonarda Bonanno di Gaetano** |
| 3 | **Salvatore Mazza** | **b. 5 January 1873**, Contrada Terremorte — **d. 19 September 1929**, frazione Vena × **Maria Nicotra**, m. 25 Apr 1898 |
| 4 | **Sebastiano Mazza** | b. 22 Oct 1920 – d. 2 Apr 2002. The *Toscana*, 1949. |
| 5–7 | Frank · Michael Rocco · **Mia and Rocco Francesco** | dates withheld |

**Four generations this morning, seven tonight**, and every Sicilian step is a document.

### Two corrections to the family tree

- **Salvatore was born 1873, not 1879** — six years out, which is exactly why eight consecutive
  registers came back empty.
- **He died at Piedimonte Etneo, not Catania.**

### A correction to THIS archive

The mother's surname. My direct readings of the 1877 and 1880 birth acts gave **Bonaccorso**. The
1873 birth act, the 1898 parish marriage and the 1929 death act all give **Bonanno**. Three sources
against two readings: **Bonanno is probably right and I misread twice.** Recorded as Bonanno with the
variance stated.

### What it does to the hundred and ten

The tree's unjoined cluster is headed by a **Rosario Mazza b. 1850** and contains a **Mariano Mazza**.
The register gives **Rosario b. c. 1844 whose father was Mariano**. That is a *second* independent
correspondence on top of the Orazio one. **Still not the joining document** — that would be Rosario's
own marriage act, naming Mariano with an age and a wife.

### Method

**Work from a different record, not a deeper sweep.** Eight registers were read on the strength of one
undocumented year in a family tree. What broke it was the Queensland death index → the parish marriage
→ the civil death act, each naming Salvatore's parents, until three records converged on a birth year
and the register could be opened at the right page.

---

## 10 September 2026 — THE HUNDRED AND TEN, JOINED

The archive's largest open question, closed the day it opened.

### The five records

| Record | What it says |
|---|---|
| **Nati 1873, atto 3** | Salvatore Mazza b. 5 Jan 1873, Contrada Terremorte, to **«Rosario Mazza DI MARIANO», 28**, and **Leonarda Bonanno di Gaetano** |
| **Marriage proclamation 1898** | Mazza Salvatore, **25**, son of **Rosario, 53**, and **Bonanno Leonarda** — marries Nicotra Maria, 22, daughter of Giovanni, 50, and **Monti Venera** |
| **Marriage proclamation 1902** | Mazza **Giovanni, 27**, son of **Rosario, 55**, and **Bonanno Leonarda** — marries Costanzo Maria, 20 |
| **Marriage proclamation 1910** | Mazza **Ignazio, 23**, son of **Rosario, 65**, and **Bonanno Leonarda** — *both parents present and consenting* — marries Strano Concetta, 21 |
| **Nati 1877 atto 168 · Nati 1880 atto 66 · parish baptism** | **Orazio** (1877), **Gaetano** (1880) and **Santo** (c. 1882) to the same couple |

Rosario's age across six records: **28 (1873), 31 (1877), 32 (1880), 53 (1898), 55 (1902), 65 (1910)**
— one man, born about **1845**.

### The match

The tree's unattached **Rosario Mazza b. 1850** has a wife called **Leonarda** with no surname, and
three sons: **Orazio, Ignazio, Giovanni**. The register gives **Rosario × Leonarda Bonanno** six sons,
three of them **Orazio, Giovanni, Ignazio** — and a fourth, **Salvatore**, who is Michael Mazza's
great-great-grandfather.

**And the name that seals it:** Salvatore's act calls his father *«Rosario Mazza di Mariano»*. The
tree's hundred and ten contain a **Mariano Mazza** — a **son of Orazio**. Under the Sicilian naming
custom that is exactly what Orazio's boy would be called if Orazio's grandfather was Mariano.
*(This time the reading was checked twice; the «Venerio» inference earlier today was withdrawn for
exactly this reason.)*

### What it did to the archive

- Components: **14 → 10**. Main component: **479 → 581 people**.
- Mazza descent groups: **6 → 3**; the largest is now **110 people, 1850–1952, Piedimonte Etneo to Brisbane**.
- **106 of the 110 descend from Orazio alone.**
- They are the families of **Michael Rocco Mazza's great-great-uncles**.

### The mechanism: documented joins

The automatic merge rules require evidence **inside** the export — a shared birth year, or the same
family standing around a person. They would never have made this join, and they were right not to:
an earlier build fused four undated Rosario Mazza on the name alone and manufactured a pedigree.

So this join is **declared**, in `data/documented-joins.tsv`, with its citation, applied after the
automatic rules as an explicit override, and published in full.
**An automatic merge is a rule; a documented join is an argument, and an argument has to be
published so it can be attacked.**

**What would overturn it:** Rosario's own marriage or death act naming a father who is not Mariano —
or a second Rosario Mazza of Piedimonte Etneo, born about 1845, married to a second Leonarda Bonanno,
with sons of the same four names.

### A loose end

The 1898 proclamation gives Maria Nicotra's mother as **Monti Venera**; the Queensland death register
gives **Venera Cassaneti**. One of them is wrong, or she is recorded under two names. Unresolved.

### Also worth chasing

- **Gaetano (1880)** and **Santo (c. 1882)** are Rosario's sons and are **not in the family tree at all**.
- **Mazza Veneranda, daughter of Salvatore and Maria Nicotra, married Mariano Cavallaro on 1 October
  1920** — another sibling of Sebastiano, and very likely the link to the Brisbane Cavallaro.

---

## 10 September 2026 — items 2, 1, 4 and 5

### 2. THE 1697 AUDITED — and it does not survive

The archive's largest claim was **nine generations of Prostamo to 1697**. FamilySearch's Briatico
full text (1880–1910, Catanzaro collection **2043789**; Calabria collections **M9J1-9RW** deaths,
**M9J1-S99** births, **M9J1-SHC** marriages) documents **two generations and no more**:

> **Marriage proclamation, 16 January 1886 / marriage, 21 May 1887, Briatico.**
> è comparso **Prostamo Alfonso**, di anni **ventiquattro**, **MARINARO**, residente in Briatico,
> **figlio del fu Domenico**, Marinaro, residente in vita in Briatico, e di **Ventrice Giovanna**,
> Filatrice… È pure comparsa **Melluso Caterina**, di anni **ventuno**, contadina, figlia di **Leone**…
> «la copia dell'atto di morte di **Prostamo Domenico**, genitore dello sposo»… «È altresì comparsa la
> genitrice dello sposo **Ventrice Giovanna**, la quale dona il suo pieno consenso».

| Gen | | Standing |
|---|---|---|
| 1697 Franco Antonino · 1726 Antonino · 1760 Pasquale · 1785 Antonino | | **UNTESTED — no source at all** |
| **Domenico Prostamo** | *marinaro*, dead before Jan 1886, × Giovanna Ventrice | **DOCUMENTED** |
| **Alfonso Prostamo** | b. **c. 1862** (24 in Jan 1886, 25 in May 1887), *marinaro*, × Caterina Melluso 21 May 1887 | **DOCUMENTED — tree says 1858, four years out** |

**They were sailors, not farmers** — both Alfonso and Domenico are *marinari*, which the tree does not
record and which is exactly what a Tyrrhenian coastal family should be.

**The four generations above Domenico are not merely unproved — they are not testable online.**
Civil registration starts 1809; FamilySearch's Briatico corpus starts 1880; and the **1783 Calabrian
earthquake** destroyed archives across the province. The site now says
*documented to Domenico Prostamo, asserted for four generations above him.*

### 1. MARIANO — done, from a death act rather than a marriage

> **Piedimonte Etneo, Morti, 15 November 1924, frazione Presa.** …è morto **Mazza Rosario di anni
> settantanove**, contadino… Contrada **S. Basilio**… **da fu Mariano già contadino**… **e da fu
> Catalano Maria già casalinga**… **Marito di Bonanno Leonarda**.

**MARIANO MAZZA × MARIA CATALANO** — generation one now has a couple, both dead by 1924.
**Rosario Mazza: b. c. 1845, d. 15 November 1924, aged 79.** His age is now attested **seven** times
— 28 (1873), 31 (1877), 32 (1880), 53 (1898), 55 (1902), 65 (1910), 79 (1924) — and every one agrees.

I went looking for his marriage; his death act gave the same information and his own death besides.
**Worth remembering: a death act names parents too, and is often easier to find than a marriage.**

### 4. SCILLA — FamilySearch does not hold it; Antenati does

Four searches place-matched to Scilla returned **zero** records whose `recordPlace` contains Scilla —
the apparent 1866–1928 coverage was the region flooding in through weak place-weighting, exactly as
`familysearch-fulltext-method` warns. **FamilySearch's Calabrian full text is concentrated on
Catanzaro / Vibo Valentia, not Reggio Calabria.**

**Antenati does hold Scilla**: Archivio di Stato di Reggio Calabria, **57 volumes**, 39 in the Stato
civile italiano series, births from **1850** (`an_ua2002898` onward). The Arena and Polistena sweep is
therefore an Antenati job and remains to be done. Targets: Giuseppe Arena b.1892, Giovanni Arena
b.1870, Rocco Arena b.1861, Orazio Arena b.1821; Giovanni Polistena b.1883, Antonio Polistena,
Giovanna Pontillo; Michele Donato b.1851.

### 5. THE SHIPS — blocked

NAA RecordSearch returned *Session expired* and an exception page on every entry point tried. Nine
crossings remain unnamed. FindMyPast still has until **16 September**.

### Method: the collection filter is what makes full text usable

Without `c.collectionId=on&f.collectionId=<CID>` the `q.anyPlace` term is only weakly weighted and
results flood with the whole region — Ganzirri, Nicotera, Limbadi, Torre di Faro. Get the IDs from
the response's own `facets[0].facets`, each carrying a ready-made `params` string.

---

## 10 September 2026 — Scilla opened

**FamilySearch does not hold Scilla** (four place-matched searches, zero records; its Calabrian full
text is Catanzaro/Vibo Valentia). **Antenati does**: Archivio di Stato di Reggio Calabria, **57
volumes**, births from **1850**. Scilla *marriages* on Antenati run **1905–1913 only**.

### The Bourbon index names the parents

The pre-unification *Stato civile della restaurazione* annual index at Scilla is laid out far better
than the Italian one that replaced it:

> **N. d'ord · Cognomi e Nomi dei nati · Patria · Professione · NOMI E COGNOMI DEI GENITORI ·
> giorno della nascita**

**A whole year's households of one surname can be read off a single opening, with parentage, without
opening any act.** That makes a Scilla surname sweep dramatically cheaper than the Sicilian one —
and it is the single most useful thing learned about these registers today.

### First read: Scilla, Nati 1861 (`an_ua2002933`, 134 images)

| Act | Child | Father | Mother |
|---|---|---|---|
| **228** | **Arena Rocco** | **Giuseppe Arena** | **Grazia Zirilli** |
| 209 | Arena Domenica | Santo Arena | Gioffrè (forename unclear) |

**A candidate, not a join.** The tree gives Rocco Arena b.1861 as the son of **Orazio** Arena and
**Giovana Zirilli**. The index gives **Giuseppe** and **Grazia Zirilli**. The mother's surname —
**Zirilli**, not a common name — matches; both forenames do not. Either the tree has the forenames
wrong, which it has done repeatedly today, or this is a different Rocco Arena. **Read the act itself
before joining.** After the Venerio episode this archive does not merge on a partial match.

### Rate limiting

Antenati now trips at roughly **three page loads**, and takes 15–20 minutes to clear — noticeably
tighter than earlier in the day, which suggests a cumulative daily budget rather than a burst limit.
Images remain unlimited. Plan the whole sweep before starting it: **one page load per volume**, and
do everything else from `tools/manifest.py` and `tools/index_sheet.py` offline.

There is no ark→container resolver: `dam-antenati/.../resolve`, `/ark/`, and `?ark=` all 404, and the
WordPress JSON is behind the same block. The container id has to come from the record page's live DOM.

---

## 10 September 2026 — Scilla act 228, and the index that lied

### The act

**Scilla, Nati 1861, atto 228** (`an_ua2002933`, image 117), declared 23 December 1861:

> …Comune di **Scilla**, Distretto di **Reggio**, Provincia della Prima Calabria Ulteriore, è comparso
> **Francesco Antonio Arena**, **figli di Filippo**, di anni **quarantadue**, di professione
> **marinaro**, domiciliato in Scilla… è nat[o] da **Serafina Arlotta**, di anni **ventotto**…
> nel giorno **venti** del mese di Dicembre… il nome di **Rocco**.
> Witnesses: Giuseppe Idone, 64; Francesco Antonio Polì, 70, proprietario. Parish note: baptised 23rd.

**Three generations**: **Filippo Arena** → **Francesco Antonio Arena** (b. c. 1819, *marinaro*) →
**Rocco Arena** (b. 20 Dec 1861). Sailors, like the Prostamo of Briatico — both coastal families the
tree records as neither.

### THE CORRECTION: the index's parents column was misaligned

Earlier today this archive read the 1861 index as giving Rocco Arena's parents as
**«Giuseppe e Zirilli Grazia»**, and noted that the rare surname *Zirilli* agreed with the tree's
*Giovana Zirilli* while both forenames did not. **It was filed as a candidate, not a join**, with the
words *"read the act itself before joining"*.

**The act says Francesco Antonio Arena and Serafina Arlotta.** The parents column had slipped by one
row: the Scilla index is a wide ruled table photographed across a gutter, and once the columns are
cropped apart with `index_sheet.py`, **the row a name sits on is not reliably the row its parents sit
on**.

**Never read parentage off a cropped index column. Use the index to get the act number, then read the
act.** The parents column is a finding aid, not evidence.

That caution is the only reason the archive does not now carry a wrong set of great-great-grandparents
— and it is the same mistake as the *Venerio* reading earlier the same day, caught this time because
the entry was flagged instead of merged.

### An unresolved conflict

| | |
|---|---|
| **Tree** | Rocco Arena b. 1861, son of **Orazio Arena** and **Giovana Zirilli** — no source |
| **Register** | Rocco Arena b. **20 December 1861**, son of **Francesco Antonio Arena**, marinaro, and **Serafina Arlotta** — atto 228 |

The 1861 register holds **exactly one Rocco Arena** and **neither parent matches**. Either the tree's
parents are wrong or its birth year is. Given the tree has already proved six years out on Salvatore
Mazza and six on Orazio Mazza, **the year is the likelier error** — but that is a hypothesis, and the
Arena line stays where it is until a record settles it.

### Method: Scilla scans are low resolution

Native size is **1934 × 1410** for a full opening — roughly half the Sicilian scans, and the IIIF
server refuses any request above 100%: *"Requests for scales in excess of 100% are not allowed."*
Ask for `/full/` on a `pct:` region rather than naming a width, and check `info.json` before
requesting a size. Two acts per image; act = 210 + 2 × (image − 108) in the 1861 volume.

---

## 10 September 2026 — Scilla, act 206: the Polistena documented, and a trade

### Scilla, Nati 1883, atto 206 (`an_ua16601246`, image 73)

> L'anno milleottocento ottant**atre**, addì **diciassette** di **Settembre**, a ore antimeridiane
> nove… Avanti di me **Minasi Raffaele, Assessore, pel Sindaco assente**, Uffiziale dello Stato Civile
> del Comune di **Scilla**, è comparso **Camillo Antonio Polistena**, di anni **quarantotto**,
> **pescatore**, domiciliato in questo Comune… alle ore pomeridiane nove e minuti trenta, del dì
> **sedici** del corrente mese, nella casa posta in **Via Grotte** al numero **quarantasette**, da
> **Giovanna Romano** sua moglie, **filatrice**, seco lui convivente… è nato un bambino di sesso
> maschile… a cui dà il nome di **Giovanni**.

**Giovanni Polistena — Angela Polistena's father — born 16 September 1883, Via Grotte 47, Scilla**,
that is, in **Chianalea**, the lane of houses standing in the water.

| | Tree | Register |
|---|---|---|
| Father | Antonio Polistena | **Camillo Antonio Polistena**, 48 → b. c. **1835**, *pescatore* ✓ agrees |
| Mother | Giovanna **Pontillo** | **Giovanna Romano**, *filatrice* ✗ **conflicts** |

The tree also gives its Giovanna Pontillo two parents **both surnamed Pontillo**, which reads like an
error in the tree rather than a second marriage. **Giovanna Romano** is the documented mother.

### The finding that runs across all of it: they were sea families

| Where | Who | Trade |
|---|---|---|
| Scilla, 1861 | **Francesco Antonio Arena** | *marinaro* — sailor |
| Scilla, 1883 | **Camillo Antonio Polistena** | *pescatore* — fisherman |
| Briatico, 1886 | **Alfonso Prostamo** and his father **Domenico** | *marinari* — sailors |

**Two provinces, three families, one trade — and the family tree records none of them as anything.**
The Sicilian Mazza, up on the mountain, are *braccianti* and *contadini* to a man. Until today this
archive could not say what a single one of these people did for a living.

### The Scilla index format, again

The post-1866 Scilla index is **«Casato e Nome» + «di [father's forename]»** — *"Polistena Giovanni
di Camillo Ant.°"*. That half-parentage sits on the same line as the name and is reliable, unlike the
Bourbon-era index's separate parents column, which is not. Use it to confirm you have the right
person before pulling the act.

Three acts per image in this volume: act = 202 + 3 × (image − 72).

---

## 10 September 2026, evening — the Scilla sweep pays off

### Scilla, Nati 1892, atto 230 (`an_ua16601257`, container `5Yb6no7`, image 79)

The single most useful act this archive has read at Scilla.

> L'anno mille-ottocento-novant**adue**, addì **nove** di **Ottobre**, a ore ante meridiane **dieci**
> e minuti **quindici**… Avanti di me **Minasi Luigi, assessore funzionante da Sindaco**… Comune di
> **Scilla** è comparso **Giovanni Arena**, di anni **trentatré**, **pescatore**, domiciliato in
> Scilla, il quale mi ha dichiarato che alle ore ante meridiane **undici** e minuti **trenta** del dì
> **sei** del corrente mese, nella casa posta in **Via Grotte** al numero **settantacinque**, da
> **Concetta Russo** sua moglie, **filatrice**, seco lui convivente… è nato un bambino di sesso
> maschile… a cui dà il nome di **Giuseppe**. Testimoni: **Perina**…

**Confirms** Giuseppe Arena b. 1892 (now with a day: **6 October**) and his mother **Concetta Russo**.
**Corrects** his father: Giovanni Arena is **33** in October 1892, so born about **1859**, where the
tree says 1870 — eleven years out. **Adds** Giovanni's trade (**pescatore**) and the address,
**Via Grotte 75** — the same lane where Giovanni Polistena was born in 1883 at number 47.

### Scilla, Nati 1870, atto 81 (`an_ua16601232`, container `wWqVnPB`, image 19)

Read *before* act 230, as the obvious way to reach Giovanni Arena. The 1870 index gave three Arena
births — Camillo di Antonio (53), **Domenico-Giovanni-Camillo di Giuseppe (81)**, Antonino di
Giuseppe (257) — and only one carried the name Giovanni.

> …è comparso **Giuseppe Arena di Domenico**, di anni **trenta**, **cordaio**, domiciliato e
> residente in Scilla… dalla di lui moglie **Serafina Vita di Giovanni**, di anni **venti**, donna di
> casa… in questo Comune, **Centro Acquagrande**, al quale figlio dichiara dare i nomi di
> **Domenico-Giovanni-Camillo**. Testimoni: Giuseppe Idone fu Rocco, 72; Candeloro Ciccone di
> Domenico, 30, servienti. *La parola interlineata Domenico deve leggersi Giuseppe.*
>
> ANNOTAZIONE: *…Arena Domenico… nel dì **trenta novembre milleottocentonovantanove**, nel Comune di
> Scilla, contrasse matrimonio con **Arena Maria**, ivi nata nel **1869**, N.° 166, e N.° 62 Registro
> dei matrimonii. — Reggio Cal. 23 Gennajo 1900.*

**It is the wrong man.** The margin calls him **Arena Domenico** and marries him to **Arena Maria**,
not Concetta Russo; naming custom agrees (Domenico = father's father, Giovanni only mother's father);
and act 230 then settles it by making the tree's Giovanni eleven years older. **It was tempting** —
the tree's Giovanni named his first son Giuseppe, exactly as custom predicts if his father were a
Giuseppe — which is precisely why it was held as a candidate and not merged.

Three Arena generations regardless: **Domenico → Giuseppe (b. c.1840, *cordaio*) →
Domenico-Giovanni-Camillo (b. 24 April 1870, Centro Acquagrande)**.

**The mother's surname is VITA, not Sita.** Confirmed independently by the 1913 marriage index, which
carries three Vita entries (acts 27, 10, 15) and no Sita at all. *Method note: when a surname read
from a single act looks doubtful, the same comune's index for another year is a free second opinion.*

### Scilla, Matrimoni 1913 — the entire index transcribed (`an_ua16594965`, container `5K7arD3`)

Antenati's Scilla marriages run **1905–1913 only**. The images are **not rate-limited** (only the
HTML is), so all eleven index openings, images 75–85, came down for nothing. **58 marriages,
77 surnames**, in `data/scilla-matr-1913.tsv`.

**The negatives are the finding: no Arena, no Donato, no Polistena, no Mazza married at Scilla in
1913.** The Polistena × Donato marriage this archive wanted — four of Angela Polistena's grandparents
in one act — is either outside 1905–13 or was not celebrated at Scilla. Eight volumes left in the
window.

Commonest surnames: Bueti 6, Catalano 4, Oliveri 4, Bellantoni 3, Cambareri 3, Infantino 3,
Ciccone 3, Scarfone 3.

**One index entry read as a possible *Mazza* bride** (no. 32) — which would have put the Sicilian
surname in Calabria. The act itself (atto 31, 20 September 1913) says **Muzzi**: Majori Carmelo, 27,
*falegname*, born Gallico, of Vincenzo and Morelli Caterina, married **Muzzi Santa Maria**, 24,
*casalinga*, of Scilla, daughter of Carmelo and Marino Maria. **Read the act, not the index** —
the third time that rule has earned its keep here.

### Method: how to get an Antenati ark without guessing

The volume page carries a link `search-registry/?tipologia=Nati&serie=<id>` that lists **every**
volume in the series with its ark. Scilla, Stato civile italiano, Nati = **serie 16594786**, 39
volumes. The listing's year facet gives the doubled years — **1866 (2), 1875 (2), 1884 (2),
1885 (2)** — so the ark is computable exactly:

    ark(Y) = an_ua16601229 + (Y - 1867) + (doubled years in [1867, Y-1])

Checked against two known volumes: 1883 → 1246 ✓, 1870 → 1232 ✓. Predicted 1892 → **1257**, and the
page confirmed *Registro: 1892*. **Two page loads for the whole series instead of one per year.**

### Scilla, Nati 1851 (`an_ua2002901`, container `LeJQDD6`, 131 images, index at 123–131)

The Bourbon-era *Tavola annuale alfabetica de' Nati* — the index that names both parents.
**No Donato in it.** The D block runs entries **65–75**: seven Di Franco, two Dormì, one De Marco,
one De Alessandro. Entry 64 is the last C, entry 76 begins the F, so the block is complete.

**Michele Donato is not born at Scilla in 1851.** His eldest son was born 1878, so his birth sits
somewhere around 1848–1858. Given the tree has now been six years out twice and **eleven years out
on Giovanni Arena**, the year is the likelier error.

The A section of the same index holds **one** Arena birth — Arena Maria, of Pasquale. The Scilla
Arena were not a numerous family in the 1850s.

**Technical note: these scans are small.** About **1034 × 1473** and **1991 × 1480**, against
4659 × 3741 for the Italian-era volumes. The IIIF request must ask for `/full/` (or `pct:` +
`/full/`), never a width — a width larger than native returns **403 Forbidden**. Check `info.json`
first. This low resolution is also why the 1861 index's parents column misled this archive earlier.

### The queue this leaves

1. **Scilla, Nati ~1859 — Giovanni Arena.** The best lead in the archive: the Bourbon index names
   parents, so one opening gives his father and mother outright. The restaurazione arks are **not**
   computable — that series interleaves Nati, Morti and Matrimoni, so consecutive Nati years jump by
   2–4 — meaning one portal page load per year.
2. **Scilla, Nati 1845–1860 — a Donato.** Same index, same method.
3. **Scilla, Matrimoni 1899, atto 62** — Arena Domenico × Arena Maria, named in act 81's margin.
4. **Scilla, Matrimoni 1905–1912** — eight volumes; Polistena × Donato is not in 1913.

### Scilla, Nati 1859, atto 46 (`an_ua2002928`, container `5vEYzey`, image 156)

Opened looking for **Giovanni Arena**, whom act 230 of 1892 had just relocated from 1870 to about
1859. **He is not there.** The A section holds exactly three Arena births:

| act | child | parents | date |
|---|---|---|---|
| 46 | Arena **Domenico** | **Orazio e Zirilli Giovanna** | 10 February |
| 111 | Arena Maria | Giosafatto e Longordo Rosaria | 1 May |
| 205 | Arena Annunziato | Santo e Gioffrè Giovanna | 15 September |

**Act 46 is worth more than the act that was wanted.** Orazio Arena and Giovanna Zirilli are the
couple the tree names as Rocco Arena's parents, and until now the archive had found **neither of
them in any register**. The 1861 act said Francesco Antonio Arena and Serafina Arlotta, and the
honest reading for a day was that the tree might have invented them. **It did not.** They were at
Scilla and having children.

This does **not** make Rocco their son — 1861 holds exactly one Rocco Arena and he is Francesco
Antonio's. What it does is move the likely error from the *parents* to the *year*, which is now a
bounded, findable thing.

*(Note: the 1892 birth index carries an Arena Giovanna **di Annunziato** at act 222 — probably this
act-205 boy's daughter, thirty-three years on.)*

### A tree duplicate, flagged and deliberately not merged

The export gives Orazio Arena **two wives**: `@I374@` Giovanna Zirilli b. 1827, mother of Guiseppe;
`@I455@` Giovana Zirilli, undated, mother of Rocco. Same husband record. That is the classic
signature of an accidental duplicate, and act 46 shows a single couple.

**Not merged.** Surname endogamy at Scilla is an observed fact, not a theory: the 1913 marriage index
alone has **Bueti × Bueti, Cambareri × Cambareri, Larizza × Larizza and Vizzari × Vizzari**. A second
wife of the same surname is exactly the sort of thing that happens here. The test is Rocco Arena's
actual birth act, which will name his mother.

### Method: getting every ark in a series in ONE page load

The `search-registry` listing has a hidden page-size control, `#search_size`, with a **100** option.
Setting it and dispatching a `change` event navigates to the same URL plus **`&s_size=100`** — so a
55-volume series comes back on one page instead of six.

    https://antenati.cultura.gov.it/search-registry/?tipologia=Nati&serie=<id>&s_size=100

Scilla series ids: **Stato civile italiano, Nati = 16594786** (39 vols, 1866–1904);
**Stato civile della restaurazione, Nati = 2002440** (55 vols, 1816–1865).
All 55 restaurazione arks are now in **`data/scilla-arks.tsv`** — they are *not* computable from the
year, because that series interleaves Nati, Morti and Matrimoni and the gaps run 2–4.

**This is the single most useful Antenati technique this archive has found**, given that the portal
rate-limits at roughly three page loads: it turns "one load per year" into "one load per series".

---

## 13 September 2026 — the children's acts

A method that should have been obvious three days ago: **when a man cannot be found, read his
children's birth acts.** An Italian birth act names the declaring father *with an age*. Two men who
had resisted a direct search fell out of volumes that were already open.

### Scilla, Nati 1892, atto 162 — Annunziata Donato (`an_ua16601257`, container `5Yb6no7`, image 56)

Cost **zero** extra portal page loads: the 1892 volume was already in hand for act 230.

> …è comparso **Michele Donato**, di anni **trentasei**, **pescatore**, domiciliato in **Scilla**…
> alle ore pomeridiane **quattro** e minuti **trenta** del dì **sei** del corrente mese, nella casa
> posta in **Via Grotte** al numero **trentuno**, da **Maria Sofi** sua moglie, **filatrice**, seco
> lui convivente… a cui dà i nomi di **Annunziata**. Testimoni: **Arlotta Giuseppe**, 56, pescatore;
> **Ponte Antonio**, 38, pescatore.

- **Michele Donato is 36 in July 1892 → born about 1856, not 1851.** That is exactly why the 1851
  index had no Donato in it. Five years out, the same shape of error as everywhere else in this tree.
- **Maria Sofi confirmed** as the tree has her.
- **Trade: pescatore** — the tree records none.
- The marginal annotation gives a death **the tree does not have at all**: Annunziata Donato
  **died at Scilla on 26 August 1975**, death act 30 of that year, aged 83. Her daughters Angela and
  Giovanna Polistena are in the Nudgee register in Brisbane. **Their mother never left.**
- Witness **Arlotta** is the surname of Rocco Arena's mother in act 228 of 1861 — thirty-one years
  and two families apart, on the same few hundred metres of shore.

### Scilla, Nati 1893, atto 22 — Anna Arena (`an_ua16601258`, container `w9WVxa9`, image 9)

The ark was **computed** from the series rule, not looked up; the title page confirmed *Registro: 1893*.

> …è comparsa **Giovanna Zumbo**, di anni **sessanta**, **levatrice**… nella casa posta in **Via
> Acquagrande** al numero **quarantuno**, da **Costa Generosa**, **filatrice**, moglie di **Arena
> Rocco**, **marinaro**, ambedue domiciliati in Scilla… a cui dà il nome di **Anna**.

**The trick fails here, and the first line says why**: the declarant is the **midwife**, not the
father, and a midwife's declaration carries no parental ages. Rocco Arena's birth year is still open.

What it does give:
- Anna Arena's date **17 January 1893** and her mother **Generosa Costa** — both exactly as the tree.
- Rocco Arena's trade: **marinaro**.

**That last point cuts against the archive's own hypothesis and is recorded as such.** The Rocco
Arena of act 228 of 1861 is the son of **Francesco Antonio Arena, also a marinaro**, and trades
passed father to son. Weak evidence — but it points *away* from "tree's parents right, year wrong"
and *toward* "tree's year right, parents wrong". Both can be true at once: Orazio Arena and Giovanna
Zirilli are certainly real (act 46 of 1859) **and** Rocco may simply not be their son.

### Two Arena households, two quarters

| street | man | trade | year |
|---|---|---|---|
| **Via Grotte 75** | Giovanni Arena | *pescatore* | 1892 |
| **Via Acquagrande 41** | Rocco Arena | *marinaro* | 1893 |
| **Centro Acquagrande** | Giuseppe Arena | *cordaio* | 1870 |

Giuseppe Arena of Via Grotte and Anna Arena of Via Acquagrande married each other. Both are
great-grandparents in this archive.

And **Via Grotte** now carries three of the four Calabrian quarters: Polistena at no. 47 (1883),
Donato at no. 31 (1892), Arena at no. 75 (1892). They were neighbours in Chianalea.

### A correction to a correction

The previous entry said act 230 "confirmed the year and gave the day" for Giuseppe Arena. That was
too generous. **The tree says 10 June 1892; the register says 6 October 1892** — the year agrees and
the date does not. The 1892 index holds only one Arena Giuseppe and his mother is Concetta Russo, so
it is certainly the same child. Corrected on the page and on his person page.

### Scilla, Nati 1856 — the year the Tavola is a separate volume

1856 has **two** arks, and they are not two halves of the year: `an_ua2002917` (container `wR8JBDp`,
107 images) holds the **acts**, running to act 200 on 8 November with **no index at all**;
`an_ua2002920` (container `04rZDNY`, **34 images**) is the **Tavola annuale**, at images 26–32.
Worth knowing before spending a page load looking for an index that is not there.

**A section, complete (nine entries):** Arena Francesca (28, *Giosafatto e Longordo Rosaria* — the
same couple as act 111 of 1859), Arlotta Maria Concetta (75), Arlotta Rocco (83), Arbitrio Domenico
(128), Arbitrio Francesco (141), Amendola Francesco (158), **Arena Domenico (180, *Orazio e Zirilli
Giovanna*, 3 September)**, Arbitrio Domenico (175), Alfonzetti Concetta (238).

- **Orazio Arena and Giovanna Zirilli have a SECOND son Domenico**, three years before act 46 of
  1859. The first almost certainly died in infancy and the name was reused — ordinary practice, and
  further confirmation that this couple was real and reproducing at Scilla through the 1850s.
- **No Rocco Arena of any parentage in 1856**, and none in 1859. Orazio's Rocco is in neither.

### The Donato are not at Scilla in the 1850s

Three complete D blocks, each bounded by the last C above and the first F below:

| year | D entries | Donato? |
|---|---|---|
| 1851 | 65–75 — seven Di Franco, two Dormì, De Marco, De Alessandro | **none** |
| 1856 | 24–235 — Denisi, six Difranco, two Dormì, D'Elia, De Nava, De Marco | **none** |
| 1859 | 73–275 — six De Franco, two Dormì, De Ciccio, De Elia, D'Ignoto | **none** |

Meanwhile the **1892** index has *two* Donato households: **Donato Annunziata di Michele** (162) and
**Donato Domenico di Rocco** (38).

**The question has changed shape.** Not *"which year was Michele Donato born at Scilla?"* but
**"when did the Donato come to Scilla, and from where?"** On this evidence the surname arrives
between 1859 and 1892, and Michele was probably born in another comune. His sailing from **Palermo**
in 1908 is at least consistent with a mobile family.

Three sampled years is not a proof — 1852–55, 1857, 1858 and 1860–65 are unread. But the next move is
his **marriage**, not his birth: a marriage act names the groom's *comune of birth* outright. His
eldest son was born 1878, so the marriage is about 1875–77 — **outside** Antenati's Scilla marriage
series, which begins at 1905. That means the Reggio Calabria *processetti* or another comune.
