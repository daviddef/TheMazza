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
