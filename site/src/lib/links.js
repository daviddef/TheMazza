/* Turning a name in the prose into a link — or honestly into nothing.
 *
 * Carried over from The Falco Archive, where the rule was set: A LINK NEVER
 * CLAIMS MORE THAN THE ARCHIVE KNOWS. Three destinations, in order:
 *
 *   1. a person page — only when exactly ONE person of that name is recorded.
 *   2. the roster, pre-filtered — when the name is shared, so the reader
 *      chooses and the archive does not choose for them.
 *   3. nothing — a dead link is worse than no link.
 */
import { people, norm, slugByName, shared } from "./people.js";
import { u } from "./url.js";

export function bare(name) {
  return String(name || "")
    .replace(/\s*\(.*?\)\s*/g, " ")
    .replace(/[«»"'’]/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

export function personLink(name) {
  const n = norm(name);
  if (!n || n === "[unnamed]") return null;

  if (slugByName.has(n) && !shared.has(n)) {
    const p = people.find((q) => norm(q.name) === n);
    if (p && p.living) {
      return { href: u("/people/") + "?q=" + encodeURIComponent(bare(name)), kind: "living",
               title: "A living relative — this archive publishes their name and nothing else" };
    }
    return { href: u("/people/" + slugByName.get(n)), kind: "person",
             title: `${name} — their page in this archive` };
  }
  if (shared.has(n)) {
    const many = people.filter((p) => norm(p.name) === n).length;
    return { href: u("/people/") + "?q=" + encodeURIComponent(bare(name)), kind: "several",
             title: `${many} people of this name are recorded — the archive does not decide which is which` };
  }
  return null;
}
