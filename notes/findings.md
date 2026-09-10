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
