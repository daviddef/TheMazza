/* THE ADAPTER FROM THIS ARCHIVE'S people.json TO THE KIT'S PERSON OBJECT (PERSON-PAGE-SPEC.md, section 2).
   Used only by src/pages/people/[slug].astro. Pilot of the shared people page on this archive, 17 October 2026.

   WHAT IT DOES NOT DO, deliberately: it sets no `living` or `presumedLiving` flag (the kit does not read
   one), it passes no pre-formatted date (the kit ignores `dates`), it derives no address from a name (every
   `href` is the slug of that very person, from people.json), and it NEVER invents a birth year.

   WHO IS LIVING is decided where it always has been: tools/build.py asks tools/living_v2.py, which asks the
   kit's one definition (kit/tools/living_rule.py), with the private harvest in hand, and writes the answer
   into people.json as `living`. The page cannot recompute it, because people.json holds a living person's
   NAME, RELATIONSHIPS AND PLACE ONLY by design: the birth year the rule needs is not in any committed file.
   So, for exactly those people, the adapter hands the kit rule `saidLiving: true`, which is what that input
   is for: the archive's own statement that someone is living, where the data cannot show it. The kit then
   draws them as living, and never reads a date it was not given. Since kit 02d9aa5 `saidLiving` also keeps a
   living child of a living parent from being held out as a possible minor, so their children are drawn.

   FOR EVERYONE ELSE the adapter passes only fields people.json publishes (born, died, dead, citations and the
   youngest known child's birth year) and `agreeWithGenerator` runs the kit's JavaScript rule over them at
   build time and THROWS if it calls any of them living or held out. A person the generator published as
   not living must be not living by the kit's rule too; if they are not, the build fails instead of drawing
   the wrong page. (tools/check_living_v2.py re-applies the Python rule from the private harvest in CI.) */
import PS from '@daviddef/archive-kit/data/public-sources.json';
import { parseDate, isLiving, isHeldOut } from '@daviddef/archive-kit/lib/person.js';
import { people, bySlug, norm } from './people.js';
import disputed from '../data/disputed.json';
import { u } from './url.js';

export const NOW = new Date().getFullYear();
const RULE = { now: NOW, sources: PS };

/* A date the kit can print, or undefined. people.json holds years as numbers, and the register's own words
   («about 1772», «before 7 January 1834», «alive at Scilla, July 1844») as text. The kit prints an
   unparseable string as written, which would put «before 7 January 1834» where a date goes, so what it
   cannot read stays in the record section as the register wrote it and the header prints none. */
export function kitDate(v) {
  if (v === null || v === undefined || v === '') return undefined;
  if (typeof v === 'number') return String(v);
  const t = String(v).trim();
  return parseDate(t).ok ? t : undefined;
}

const NAA = /\bNAA\b|National Archives of Australia/i;
const DEATHISH = /burial|death|internment|funeral|grave/i;

/* The citation strings tools/living_v2.py hands to the kit's rule for a person, rebuilt from what the page
   publishes: the tree's own sources, and every record this archive has read about them. */
function citationsOf(p) {
  const out = [...(p.sources || [])];
  for (const r of p.records || []) out.push(r.kind, r.what, r.href);
  if (out.some((c) => NAA.test(String(c)))) out.push('recordsearch.naa.gov.au');
  return out.filter(Boolean);
}

/* A recorded death or burial, dated or not: the tree's died or buried event, a death text, a place of death
   or burial, or a record this archive has read of that kind. */
function deadRecorded(p) {
  if (p.died || (p.diedText && !/^alive/i.test(p.diedText)) || p.deathPlace || p.burialPlace) return true;
  if ((p.events || []).some((e) => e.what === 'died' || e.what === 'buried')) return true;
  return (p.records || []).some((r) => DEATHISH.test(String(r.kind || '')));
}

const livingParent = (p) => ['parents'].some((b) => (p[b] || []).some((e) => bySlug.get(e.slug)?.living));
const youngestChildYear = (p) => {
  const ys = (p.children || []).map((e) => bySlug.get(e.slug)?.born).filter((y) => Number.isInteger(y));
  return ys.length ? Math.max(...ys) : undefined;
};

/* What the kit's rule needs from a person who is NOT living, all of it published. `born` and `died` are what
   the chart and the header print; `birthYear` is what only the rule reads. */
function ruleFields(p) {
  const bornText = kitDate(p.born) ?? kitDate(p.bornText);
  const diedText = kitDate(p.died) ?? kitDate(p.diedText);
  return {
    born: bornText, died: diedText,
    birthYear: Number.isInteger(p.born) ? p.born : undefined,
    dead: deadRecorded(p) || undefined,
    citations: Number.isInteger(p.born) ? [] : citationsOf(p),   // a public source never releases a DATED person (tools/living_v2.py cites_for_living)
    parentLiving: livingParent(p) || undefined,
    youngestChildYear: youngestChildYear(p),
  };
}

/* Does the page say anything about WHERE the person's own kin come from? Person-level, as before: this
   archive marks the PERSON, not the link (the chart's caption says so: edgeLevel={false}). */
const wordOf = (rec) => ((rec.records && rec.records.length) || rec.fromRegister ? 'read' : 'tree');

const BANDS = ['parents', 'spouses', 'children', 'siblings'];

/* One relative, as the kit's PersonChart takes it. On a LIVING person's page no relative carries a date:
   this archive's gate fails any year on such a page, because a dead parent's life span beside a living
   child's name is the child's age worked backwards, and the kit's chart would print a dead relative's years
   there. So born and died are dropped and `birthYear` stays, which only the rule reads. */
function row(e, page, { quiet }) {
  const rec = bySlug.get(e.slug);
  const href = u('/people/' + e.slug);
  if (rec.living) return { id: rec.id, name: rec.name, href, saidLiving: true, source: 'tree' };
  const f = ruleFields(rec);
  const dis = !page.living && (disputed[page.slug] || {})[e.slug];
  return {
    id: rec.id, name: rec.name, href,
    ...f, ...(quiet ? { born: undefined, died: undefined } : {}),
    source: dis ? 'disputed' : wordOf(rec),
    line: !!rec.onSpine,
    disputed: dis ? true : undefined,
  };
}

/* The kit's person object for one record of people.json. */
export function kitPerson(p, { lede = '' } = {}) {
  const live = !!p.living;
  const relations = {};
  for (const b of BANDS) relations[b] = (p[b] || []).map((e) => row(e, p, { quiet: live }));
  if (live) {
    return { id: p.id, name: p.name, saidLiving: true, place: p.birthPlace || '', relations };
  }
  const events = (p.events || []).filter((e) => e.place || (e.what !== 'lived' && e.date));
  return {
    id: p.id, name: p.name, lede,
    ...ruleFields(p),
    gen: p.ancGen || undefined,         // the chart prints «generation N»; the sentence under the name says «above them»
    line: !!p.onSpine,
    birthPlace: p.birthPlace || undefined, deathPlace: p.deathPlace || undefined,
    relations, events,
    sources: [...(p.records || []).map((r) => r.what), ...(p.registerSources || [])],
  };
}

/* The safety net described at the top. Throws; never returns a verdict to be ignored. */
export function agreeWithGenerator(p, person) {
  if (p.living) {
    if (!isLiving(person, RULE)) throw new Error(`personpage.js: the generator says ${p.id} is living but the kit's rule does not`);
    if (isHeldOut(person, { ...RULE, heldIds: [] })) throw new Error(`personpage.js: the kit's rule holds out living ${p.id}, yet the generator publishes them`);
    return;
  }
  /* A DATED person is judged by their year and their death alone: the kit's rule lets any public-source
     citation make a person 80 or younger "not living", which is how a man born in 1948 was published as dead
     (25 October 2026). The net therefore strips citations and sources from anyone with a birth year, exactly as
     tools/living_v2.py cites_for_living does for the generator. */
  const bare = Number.isInteger(p.born) ? { ...person, citations: [], sources: [] } : person;
  if (isLiving(bare, RULE))
    throw new Error(`personpage.js: people.json publishes ${p.id} as not living but the kit's rule calls them living; fix the data or the generator, do not draw this page`);
  if (isHeldOut(person, { ...RULE, heldIds: [], parentLiving: person.parentLiving === true }))
    throw new Error(`personpage.js: the kit's rule holds out ${p.id}, yet people.json publishes them`);
}

export { norm };
