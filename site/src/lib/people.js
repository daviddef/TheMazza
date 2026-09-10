/* The people of the archive, and how a name resolves to one of them.
 *
 * Built by tools/build.py from the MyHeritage export. Two rules carry over
 * from The Falco Archive and are the reason this file exists at all:
 *
 *  1. A LIVING PERSON HAS A NAME AND NOTHING ELSE. No date, no place, no
 *     record, no photograph. The build never emits those fields for them,
 *     so there is nothing here to leak.
 *  2. A SHARED NAME IS NOT AN IDENTIFICATION. The export holds four men
 *     called Rosario Mazza and four called Giuseppe Arena, most without a
 *     single date. Where the archive cannot tell them apart it says so and
 *     sends the reader to a list, rather than picking one.
 */
import people from "../data/people.json";

export const norm = (s) =>
  String(s || "")
    .replace(/\s*\(.*?\)\s*/g, " ")
    .replace(/[’‘]/g, "'")
    .replace(/[«»"]/g, "")
    .replace(/\s+/g, " ")
    .trim()
    .toLowerCase();

export { people };
export const bySlug = new Map(people.map((p) => [p.slug, p]));
export const byId = new Map(people.map((p) => [p.id, p]));

export const dead = people.filter((p) => !p.living);
export const living = people.filter((p) => p.living);

/* Which names more than one person answers to. */
const slugByName = new Map();
const shared = new Set();
for (const p of people) {
  const k = norm(p.name);
  if (!k || k === "[unnamed]") continue;
  if (slugByName.has(k)) shared.add(k);
  else slugByName.set(k, p.slug);
}
export { slugByName, shared };

export function findByName(name) {
  const n = norm(name);
  return people.filter((p) => norm(p.name) === n);
}

/** A person's dates as the archive would print them: "1920–2002". */
export function span(p) {
  if (p.living) return "";
  const b = p.born ? String(p.born) : "";
  const d = p.died ? String(p.died) : "";
  if (b && d) return `${b}–${d}`;
  if (b) return `b. ${b}`;
  if (d) return `d. ${d}`;
  return "";
}

/** Where the archive would say they belong. */
export function homeOf(p) {
  return p.birthPlace || p.deathPlace || p.burialPlace || "";
}
