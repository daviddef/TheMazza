/* WHICH SURNAMES HAVE A FAMILY PAGE, in the order the menu shows them.
 *
 * Kept apart from lib/families.js (which builds a page's content from the whole
 * of the people data) so that the layout can read the list for the menu without
 * pulling the builder into every page.
 *
 * TWO KINDS OF FAMILY PAGE LIVE IN THIS ARCHIVE.
 *   Hand-built, one file each, because each has its own argument to make:
 *   /mazza/, /arena/, /nicotra/. They stay exactly as they are.
 *   Data-built, one template (src/pages/[family].astro) fed by this list and by
 *   people.json, for the surnames of the direct line that had no page.
 *
 * THE RULE FOR A FAMILY TO BE IN `BUILT` (17 October 2026). A surname is core
 * when a direct-line ancestor bears it, or at least eight people are published
 * under it, or the archive's own research files treat it as a family under
 * investigation. Of the core surnames that had no page, the twelve with a
 * direct-line ancestor and the most published people are here, in that order.
 * The rest are listed in the audit that accompanied this change; to add one,
 * add a row here and nothing else.
 *
 *   slug      the address: /<slug>/
 *   surname   the surname as people.json spells it
 *   also      other spellings of the same surname that people.json carries as
 *             separate surnames. Grouped for this page ONLY, and the page says
 *             so; no person is renamed and no two people are merged.
 */
export const HAND_BUILT = [
  { slug: "mazza", surname: "Mazza", href: "/mazza/" },
  { slug: "arena", surname: "Arena", href: "/arena/" },
  { slug: "nicotra", surname: "Nicotra", href: "/nicotra/" },
];

export const BUILT = [
  { slug: "prostamo", surname: "Prostamo", also: ["Prostamo Di Maio"] },
  { slug: "polistena", surname: "Polistena", also: ["Polistina"] },
  { slug: "donato", surname: "Donato", also: [] },
  { slug: "melluso", surname: "Melluso", also: [] },
  { slug: "anile", surname: "Anile", also: [] },
  { slug: "costa", surname: "Costa", also: [] },
  { slug: "arlotta", surname: "Arlotta", also: [] },
  { slug: "pontillo", surname: "Pontillo", also: [] },
  { slug: "ventrice", surname: "Ventrice", also: [] },
  { slug: "sofi", surname: "Sofi", also: [] },
  { slug: "barbuto", surname: "Barbuto", also: [] },
  { slug: "russo", surname: "Russo", also: [] },
];

/* The menu entries for every family page, hand-built first. */
export const FAMILY_MENU = [
  ...HAND_BUILT.map((f) => [f.href, "The " + f.surname]),
  ...BUILT.map((f) => ["/" + f.slug + "/", "The " + f.surname]),
];

/* Surname (any spelling in `also` included) -> the address of its family page. */
export const PAGE_OF = (() => {
  const m = new Map();
  for (const f of HAND_BUILT) m.set(f.surname, f.href);
  for (const f of BUILT) {
    m.set(f.surname, "/" + f.slug + "/");
    for (const a of f.also) m.set(a, "/" + f.slug + "/");
  }
  return m;
})();
