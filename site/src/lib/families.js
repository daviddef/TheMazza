/* A FAMILY PAGE, BUILT FROM WHAT THE ARCHIVE ALREADY HOLDS.
 *
 * /mazza/, /arena/ and /nicotra/ are written by hand because each has its own
 * argument. The other surnames of the direct line had no page at all, and a
 * hand-written page for each would have meant writing research the archive has
 * not got. So this builds one from the data and says only what the data says:
 *
 *   * who bears the name, counted from people.json (the dead, by their own
 *     pages; the living only as a COUNT, see below);
 *   * where and when, from those people's own recorded places and years;
 *   * which of them are direct ancestors, and through which of the four
 *     grandparents, walked up the parent links the archive already draws;
 *   * which bearers are joined to which, by parent, child or marriage link
 *     (the rule build_focus.py uses for the Mazza and the Arena: a descent
 *     group is NEVER merged with another until a record joins them);
 *   * which other surnames those links reach;
 *   * how many of the links rest on a register act this archive has read and
 *     how many on the family tree alone;
 *   * what the archive's own work list, open questions, corrections and walls
 *     already say about the name, quoted and never added to.
 *
 * Nothing here is a claim about origin, meaning or kinship that the archive
 * does not already make. The one sentence about what a name means is quoted
 * from /name/, word for word, and tools/check_familypages.py fails when the
 * quotation and the page it came from stop agreeing.
 *
 * THE LIVING (David, 16 October 2026): a living person is a name, a
 * relationship and a town and country, on their own page, which is noindex.
 * A family page is indexed, so it must not make anyone easier to find than
 * their own page does. It therefore NAMES NO LIVING PERSON, and no place that
 * would locate one: the living are counted, and the reader is sent to the
 * roster. Who is living is decided in tools/living_v2.py and arrives here as
 * `living` on each row; nothing in this file decides it.
 */
import people from "../data/people.json";
import quarters from "../data/quarters.json";
import walls from "../data/walls.json";
import questions from "../data/questions.json";
import worklist from "../data/worklist.json";
import corrections from "../data/corrections.json";
import nameEvidence from "../data/name-evidence.json";
import spellings from "../data/place-spellings.json";
import atlas from "../../public/atlas-data.json";
import { PAGE_OF } from "./familylist.js";

const BY_ID = new Map(people.map((p) => [p.id, p]));

/* The places the archive draws a page for, and the comune pages it has written. */
const TOWN = {
  scilla: "/scilla/", briatico: "/briatico/", "piedimonte-etneo": "/piedimonte-etneo/",
  mascali: "/mascali/", giarre: "/giarre/", riposto: "/riposto/", brisbane: "/brisbane/",
  nudgee: "/nudgee/",
};
const PLACE_PAGE = new Map();
for (const p of atlas.places) {
  const k = p.name.toLowerCase();
  if (p.slug && !PLACE_PAGE.has(k)) PLACE_PAGE.set(k, p.slug);
}
const FIX = new Map(spellings.filter((s) => s.kind === "part").map((s) => [s.asWritten.toLowerCase(), s.corrected]));

/** "Scilla, Reggio Calabria" -> "Scilla"; a keyboard slip the archive already corrects is corrected. */
export function placeHead(s) {
  const head = String(s || "").split(",")[0].trim();
  if (!head) return "";
  return FIX.get(head.toLowerCase()) || head;
}

/* What /name/ says about each name, word for word (tools/check_familypages.py keeps this honest). */
export const NAME_NOTES = {
  Prostamo: `<strong>Rare, and concentrated.</strong> Almost the whole Italian distribution sits in a few Calabrian comuni around Vibo Valentia. A rare surname in one small place is the best gift a genealogist gets: two Prostamo of Briatico almost certainly <em>are</em> related.`,
  Polistena: `A <strong>toponymic</strong> — from the town of Polistena in the province of Reggio Calabria. It marks a family that moved <em>from</em> there, and was named for having done so.`,
  Anile: `Calabrian and uncommon, clustered in the Vibo Valentia area.`,
  Donato: `From the personal name Donato — "given". Common everywhere in the south.`,
  Melluso: `Southern, both Sicilian and Calabrian; probably from <em>mele</em>, honey, or a diminutive of a personal name.`,
};

const strip = (s) => String(s || "").replace(/\*\*/g, "").replace(/\s+/g, " ").trim();
const wordRe = (names) =>
  new RegExp("(^|[^A-Za-zÀ-ÿ])(" + names.map((n) => n.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|") + ")(?![A-Za-zÀ-ÿ])", "i");

/** A person's dates as the archive prints them, preferring the register's own wording. */
export function lifeOf(p) {
  if (p.living) return "";
  const b = p.bornText || (p.born ? String(p.born) : "");
  const d = p.diedText || (p.died ? String(p.died) : "");
  if (b && d) return `${b} – ${d}`;
  if (b) return `b. ${b}`;
  if (d) return `d. ${d}`;
  return "";
}

export function buildFamily(spec) {
  const names = [spec.surname, ...(spec.also || [])];
  const nameSet = new Set(names);
  const bears = (p) => nameSet.has(p.surname);

  const all = people.filter(bears);
  const dead = all.filter((p) => !p.living);
  const livingCount = all.length - dead.length;
  const ids = new Set(all.map((p) => p.id));

  /* ---- the four quarters, and who is an ancestor through which --------------
     quarters.json names the four grandparents. Walking UP the parent links the
     archive already draws gives each quarter's ancestors. The same walk is how
     the Four Quarters page was built; nothing here is inferred. */
  const quarterOf = new Map(); // person id -> [quarter labels]
  const Q = quarters.map((q) => ({
    label: `${q.grandparent.surname} quarter`,
    grandparent: q.grandparent.name,
    grandparentSlug: q.grandparent.living ? "" : q.grandparent.slug,
    town: String(q.town).split(",")[0],
    id: q.grandparent.id,
  }));
  for (const q of Q) {
    const seen = new Set([q.id]);
    const stack = [q.id];
    while (stack.length) {
      const id = stack.pop();
      const p = BY_ID.get(id);
      if (!p) continue;
      if (!quarterOf.has(id)) quarterOf.set(id, []);
      if (!quarterOf.get(id).includes(q.label)) quarterOf.get(id).push(q.label);
      for (const par of p.parents || []) if (!seen.has(par.id)) { seen.add(par.id); stack.push(par.id); }
    }
  }

  /* ---- descent groups among the bearers (the rule in tools/build_focus.py) --- */
  const adj = new Map(all.map((p) => [p.id, new Set()]));
  for (const p of all)
    for (const k of ["parents", "children", "spouses"])
      for (const e of p[k] || [])
        if (ids.has(e.id)) { adj.get(p.id).add(e.id); adj.get(e.id).add(p.id); }
  const seenG = new Set();
  const comps = [];
  for (const p of [...all].sort((a, b) => a.slug.localeCompare(b.slug))) {
    if (seenG.has(p.id)) continue;
    const comp = [];
    const stack = [p.id];
    seenG.add(p.id);
    while (stack.length) {
      const x = stack.pop();
      comp.push(x);
      for (const n of adj.get(x)) if (!seenG.has(n)) { seenG.add(n); stack.push(n); }
    }
    comps.push(comp.map((i) => BY_ID.get(i)));
  }
  const yearsOf = (list) => list.flatMap((p) => [p.born, p.died]).filter((y) => Number.isInteger(y));
  const isAnc = (p) => Number.isInteger(p.ancGen) && p.ancGen > 0;
  let groups = comps
    .map((c) => ({ dead: c.filter((p) => !p.living), living: c.filter((p) => p.living).length }))
    .filter((g) => g.dead.length)
    .sort((a, b) =>
      b.dead.filter(isAnc).length - a.dead.filter(isAnc).length ||
      b.dead.length - a.dead.length ||
      a.dead[0].slug.localeCompare(b.dead[0].slug));
  const livingOnlyGroups = comps.filter((c) => c.every((p) => p.living)).length;
  const LETTER = (i) => (i < 26 ? String.fromCharCode(65 + i) : String(i + 1));
  const groupOf = new Map();
  groups = groups.map((g, i) => {
    const ys = yearsOf(g.dead);
    const places = new Map();
    for (const p of g.dead) { const h = placeHead(p.birthPlace); if (h) places.set(h, (places.get(h) || 0) + 1); }
    const top = [...places.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])).slice(0, 2).map((x) => x[0]);
    const out = {
      letter: LETTER(i), n: g.dead.length,
      first: ys.length ? Math.min(...ys) : null, last: ys.length ? Math.max(...ys) : null,
      places: top, ancestors: g.dead.filter(isAnc).length,
      withRecord: g.dead.filter((p) => (p.records && p.records.length) || p.fromRegister).length,
    };
    for (const p of g.dead) groupOf.set(p.id, out.letter);
    return out;
  });

  /* ---- the people, oldest first, undated last -------------------------------- */
  const rows = [...dead]
    .sort((a, b) => (a.born ?? 9999) - (b.born ?? 9999) || a.name.localeCompare(b.name) || a.slug.localeCompare(b.slug))
    .map((p) => ({
      name: p.name, slug: p.slug, life: lifeOf(p), place: placeHead(p.birthPlace) || placeHead(p.deathPlace) || placeHead(p.burialPlace),
      ancestor: isAnc(p), group: groupOf.get(p.id) || "",
      documented: !!((p.records && p.records.length) || p.fromRegister),
      spelling: p.surname !== spec.surname ? p.surname : "",
    }));

  /* ---- the direct line --------------------------------------------------------- */
  const line = dead.filter(isAnc)
    .sort((a, b) => b.ancGen - a.ancGen || a.slug.localeCompare(b.slug))
    .map((p) => ({
      name: p.name, slug: p.slug, gen: p.ancGen, life: lifeOf(p), place: placeHead(p.birthPlace),
      quarters: quarterOf.get(p.id) || [],
      documented: !!((p.records && p.records.length) || p.fromRegister),
      contradicted: (p.corrections || []).length,
    }));
  const quarterCount = new Set(line.flatMap((r) => r.quarters)).size;

  /* ---- places ------------------------------------------------------------------ */
  const pl = new Map();
  const note = (head, how, p) => {
    if (!head) return;
    if (!pl.has(head)) pl.set(head, { place: head, born: 0, other: 0, seen: new Set(), ys: [] });
    const r = pl.get(head);
    r[how] += 1; r.seen.add(p.id);
    for (const y of [p.born, p.died]) if (Number.isInteger(y)) r.ys.push(y);
  };
  for (const p of dead) {
    note(placeHead(p.birthPlace), "born", p);
    const dh = placeHead(p.deathPlace), bh = placeHead(p.burialPlace);
    if (dh) note(dh, "other", p);
    if (bh && bh !== dh) note(bh, "other", p);
  }
  const places = [...pl.values()]
    .map((r) => {
      const slug = PLACE_PAGE.get(r.place.toLowerCase()) || "";
      return { place: r.place, born: r.born, other: r.other, people: r.seen.size,
        first: r.ys.length ? Math.min(...r.ys) : null, last: r.ys.length ? Math.max(...r.ys) : null,
        href: slug ? "/places/" + slug + "/" : "", town: TOWN[slug] || "" };
    })
    .sort((a, b) => b.people - a.people || a.place.localeCompare(b.place));

  /* ---- the families it joins ---------------------------------------------------
     Parent, child and marriage links from a dead bearer to a DEAD person of another
     surname. A living neighbour is left out entirely (not named, not counted as a
     name); the counts say what is shown. */
  const join = new Map();
  const touch = (key, kind, a, b) => {
    if (!join.has(key)) join.set(key, { surname: key, marriage: [], parent: [], child: [] });
    join.get(key)[kind].push([a, b]);
  };
  const seenPair = new Set();
  for (const p of dead) {
    for (const [field, kind] of [["spouses", "marriage"], ["parents", "parent"], ["children", "child"]]) {
      for (const e of p[field] || []) {
        const o = BY_ID.get(e.id);
        if (!o || o.living || ids.has(o.id)) continue;
        const key = (o.surname || "").trim();
        if (!key) continue;
        const pair = [kind, [p.id, o.id].sort().join("|")].join("|");
        if (seenPair.has(pair)) continue;
        seenPair.add(pair);
        touch(key, kind, p, o);
      }
    }
  }
  const WORD = { marriage: "married", parent: "child of", child: "parent of" };
  const joined = [...join.values()]
    .map((j) => ({
      surname: j.surname, href: PAGE_OF.get(j.surname) || "",
      marriages: j.marriage.length, parents: j.parent.length, children: j.child.length,
      total: j.marriage.length + j.parent.length + j.child.length,
      pairs: ["marriage", "parent", "child"].flatMap((k) =>
        j[k].map(([a, b]) => ({ kind: WORD[k], a: { name: a.name, slug: a.slug }, b: { name: b.name, slug: b.slug } }))),
    }))
    .sort((a, b) => b.total - a.total || a.surname.localeCompare(b.surname));

  /* ---- how we know ---------------------------------------------------------------
     Every relationship that touches a dead bearer, once. "Proved" is the archive's
     own word for a link a register act or index it has read supports (via read or
     index); the rest come from the family tree. */
  const edge = new Map();
  for (const p of dead)
    for (const k of ["parents", "children", "spouses"])
      for (const e of p[k] || []) {
        const o = BY_ID.get(e.id);
        if (!o || o.living) continue;
        const key = k === "spouses" ? "s|" + [p.id, o.id].sort().join("|")
          : "c|" + (k === "parents" ? [o.id, p.id] : [p.id, o.id]).join("|");
        const proved = e.via === "read" || e.via === "index";
        edge.set(key, (edge.get(key) || false) || proved);
      }
  const links = edge.size;
  const proved = [...edge.values()].filter(Boolean).length;
  const withRecord = dead.filter((p) => (p.records && p.records.length) || p.fromRegister).length;
  const contradicted = dead.filter((p) => (p.corrections || []).length).length;

  /* ---- shared names ------------------------------------------------------------ */
  const byName = new Map();
  for (const p of dead) {
    const k = p.name.trim().toLowerCase();
    byName.set(k, (byName.get(k) || []).concat(p));
  }
  const sharedNames = [...byName.values()].filter((l) => l.length > 1)
    .sort((a, b) => b.length - a.length || a[0].name.localeCompare(b[0].name))
    .map((l) => ({ name: l[0].name, n: l.length,
      who: "/who/" + String(l[0].name).normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[^A-Za-z0-9]+/g, "-").replace(/^-+|-+$/g, "").toLowerCase() + "/" }));

  /* ---- what the archive's own research files already say ------------------------ */
  const re = wordRe(names);
  const wallRows = walls.filter((w) => re.test(w.quarter || "") || re.test(w.person || "")).map((w) => ({
    who: w.person, town: w.town, reason: w.reason, established: w.established }));
  const qRows = questions.filter((q) => re.test(q.q)).map((q) => ({ n: q.n, q: strip(q.q), state: q.state }));
  const wlRows = (worklist.rows || []).filter((r) => re.test(r.what || "")).map((r) => ({
    n: r.n, what: strip(r.what), state: r.state }));
  const corrRows = (corrections.groups || []).flatMap((g) => g.rows || []).filter((r) => re.test(r.who || ""));
  const evidenceNotes = Object.entries(nameEvidence)
    .filter(([k]) => re.test(k))
    .map(([k, v]) => ({ name: k, text: v }));

  const allYears = yearsOf(dead);
  const topPlaces = places.slice(0, 3).map((p) => p.place);
  return {
    spec, names, surname: spec.surname, also: spec.also || [],
    total: all.length, dead: dead.length, living: livingCount,
    first: allYears.length ? Math.min(...allYears) : null,
    last: allYears.length ? Math.max(...allYears) : null,
    topPlaces, places, rows, line, quarterCount, groups, livingOnlyGroups,
    joined, links, proved, withRecord, contradicted, sharedNames,
    wallRows, qRows, wlRows, corrCount: corrRows.length, evidenceNotes,
    variantCounts: (spec.also || []).map((a) => [a, dead.filter((p) => p.surname === a).length]),
    note: NAME_NOTES[spec.surname] || "",
  };
}
