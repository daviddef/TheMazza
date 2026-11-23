/* WHO SHARES A NAME (one page per person; 23 November 2026).
 *
 * Until now a NAME had a page of its own, /who/<name>/ ("Everyone in this archive called ..."), beside the PERSON's page at
 * /people/<slug>/. David's rule: one page per person, and each person's page links to the other people who carry the same name.
 * The name pages are gone; their addresses redirect (astro.config.mjs reads whoRedirects below) and this file is the one place that
 * says which people share a name.
 *
 * THE SET IS THE ONE THE NAME PAGES USED. It is the old /who/[slug].astro getStaticPaths, moved here unchanged in what it counts:
 * every row of people.json that has a name and a slug, grouped on the slug of its name (accents and case folded, every run of other
 * characters a hyphen). So the people listed under "Others of the same name" are exactly the people /who/ listed.
 * Names READ from register acts and held in no family file (read-names.json) have no person page, so they keep a name page:
 * they are not in these sets.
 *
 * PURE: no imports, so astro.config.mjs can use it (it reads people.json itself) and so can the pages and lib/families.js.
 */
export const slugify = (s) => String(s ?? "").normalize("NFD").replace(/[̀-ͯ]/g, "")
  .replace(/[^A-Za-z0-9]+/g, "-").replace(/^-+|-+$/g, "").toLowerCase();

/* @param people  people.json
   @returns Map nameSlug -> { key, name, people } in people.json order (the order the old name pages were made in) */
export function nameSets(people) {
  const by = new Map();
  for (const p of people) {
    if (!p.name || !p.slug) continue;
    const k = slugify(p.name);
    if (!by.has(k)) by.set(k, { key: k, name: p.name, people: [] });
    by.get(k).people.push(p);
  }
  return by;
}

/* the first four-digit year of the birth year as people.json holds it (a number, or null) */
export const yearOf = (p) => { const m = /\b(1[0-9]{3}|20[0-9]{2})\b/.exec(String(p.born ?? "")); return m ? Number(m[1]) : null; };

/* oldest first (the year born), those with no year after, then slug order */
export const byAge = (a, b) => (yearOf(a) ?? 99999) - (yearOf(b) ?? 99999) || (a.slug < b.slug ? -1 : a.slug > b.slug ? 1 : 0);

/* THE FIRST BEARER of a set: the one a shared name's old address lands on. Someone who is not living comes first (the page a search
   engine may show), then the earliest born, one with no year after those with one, then slug order. */
export function firstBearer(set) {
  const rank = (p) => [p.living ? 1 : 0, yearOf(p) ?? 99999, p.slug];
  return [...set.people].sort((a, b) => {
    const x = rank(a), y = rank(b);
    return x[0] - y[0] || x[1] - y[1] || (x[2] < y[2] ? -1 : x[2] > y[2] ? 1 : 0);
  })[0];
}

export const isShared = (set) => set.people.length > 1;

export const SECTION_ID = "others-of-this-name";

/* A person's page draws the section for everyone but a living person: the kit's PersonPage gives a living person their name, their
   relationships and their town and country and no other section, so there is no section to land on. */
export const hasSection = (set, p) => isShared(set) && !p.living;

/* the old address of every name page -> where it goes now: a name one person bears -> that person's page; a name several bear ->
   its first bearer's page, at the section that lists the others (when that page draws one) */
export const whoTargets = (people, base = "") => [...nameSets(people)].map(([key, set]) => {
  const to = firstBearer(set);
  return { key, slug: to.slug, to: `${base}/people/${to.slug}/` + (hasSection(set, to) ? `#${SECTION_ID}` : "") };
});

/* astro.config.mjs `redirects`: every old /who/<name>/ address, a person whose slug carries an accent included (Astro writes that
   target percent-encoded, and the Kit's gates read it decoded since TheArchiveKit #22 and #25). */
export const whoRedirects = (people, base = "") => Object.fromEntries(
  whoTargets(people, base).map((t) => [`/who/${t.key}`, t.to]));

/* the other people of p's name: not p, oldest first */
export function othersOf(p, sets) {
  const set = sets.get(slugify(p.name));
  return set ? set.people.filter((q) => q !== p).sort(byAge) : [];
}
