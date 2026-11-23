/* The people who share a name, as the pages draw them (see namesets.js for which people, and why).
   A living person is a name and a town or country and nothing else, as the name pages drew them; nobody else has a field here that
   the name page did not show. */
import people from "../data/people.json";
import { nameSets, othersOf, byAge, firstBearer, isShared, slugify, SECTION_ID } from "./namesets.js";
import { u } from "./url.js";
import { span } from "./people.js";

export const SETS = nameSets(people);
export { SECTION_ID, slugify, isShared, firstBearer, byAge };

/* one entry per person: the name, the page, the life span and place the name page showed */
export const entry = (q) => q.living
  ? { name: q.name, slug: q.slug, href: u(`/people/${q.slug}/`), life: "", where: q.birthPlace || q.deathPlace || q.burialPlace || "", note: "", living: true }
  : {
      name: q.name, slug: q.slug, href: u(`/people/${q.slug}/`),
      /* A register-proved person's dates are usually a BOUND, so born/died are null: the register's own words are the better of the
         two facts that tell two bearers apart (there are two Rosario Nicotras, a child of 1883 and a bracciante of Mascali alive in 1872) */
      life: span(q) || [q.bornText, q.diedText].filter(Boolean).join(" – "),   // "1875–1950", "b. 1875", "d. 1971": never a bare year
      where: q.birthPlace || q.deathPlace || q.burialPlace || "",
      note: q.comp == null ? "" : `component ${q.comp}`,
      living: false,
    };

/* the other people of p's name, oldest first: [] when nobody shares it */
export const othersFor = (p) => othersOf(p, SETS).map(entry);

/* every bearer of a name set, oldest first, for the Every Name list */
export const bearersOf = (set) => set.people.slice().sort(byAge).map(entry);
