/* THE DESCENT LADDERS, built once and shared.
 *
 * The front page shows ONE tree: the Mazza name line, father to father. The longer lines
 * that come in through the women (Prostamo through Frank's mother; Arena, Polistena and
 * Donato through Michael's) live on their own family pages, the way the Defranceschi
 * archive does it. David, 17 October 2026: «there should only be one».
 *
 * Generation numbers are shared across ladders: a husband and wife are the same
 * generation, so Domenica Prostamo is 2 beside Sebastiano Mazza.
 */
import people from "../data/people.json";
import spineData from "../data/spine.json";
import quarters from "../data/quarters.json";
import sicilySpine from "../data/sicily-spine.json";

const P_BY_SLUG = new Map(people.map((q) => [q.slug, q]));
/* The family tree's years for these two are wrong (it has Salvatore born 1879 and Rosario
   1850); the registers say 1873 and 1845. A kin card must not repeat the tree's error. */
const REGISTER_DATES = { "salvatore-mazza": "1873–1929", "rosario-mazza": "1845–1924" };

const kinCards = (slug, band) => {
  const rec = slug ? P_BY_SLUG.get(slug) : null;
  return ((rec && rec[band]) || []).map((c) => {
    const full = P_BY_SLUG.get(c.slug);
    return {
      name: c.name,
      href: c.slug && full ? `/people/${c.slug}/` : null,
      dates: REGISTER_DATES[c.slug] || (full ? [full.born, full.died].filter(Boolean).join("–") : ""),
    };
  });
};

/* One row from a person's own record. `o` overrides what the record gets wrong. */
const rowOf = (slug, gen, o = {}) => {
  const rec = P_BY_SLUG.get(slug) || {};
  const hers = (rec.spouses || [])[0] || null;
  const born = o.born !== undefined ? o.born : rec.born;
  const died = o.died !== undefined ? o.died : rec.died;
  const spouseName = o.spouse || (hers && hers.name) || "";
  const spouseSlug = o.spouseSlug !== undefined ? o.spouseSlug : hers && hers.slug;
  return {
    gen,
    era: [born, died].filter(Boolean).join(" → ") || undefined,
    name: rec.name || slug,
    href: `/people/${slug}/`,
    living: !!rec.living,
    via: o.via || "",
    born: born ? String(born) : "",
    died: died ? String(died) : "",
    place: o.place || rec.birthPlace || rec.deathPlace || "",
    spouse: spouseName,
    spouseHref: spouseSlug && P_BY_SLUG.get(spouseSlug) ? `/people/${spouseSlug}/` : null,
    children: kinCards(slug, "children"),
    hisSiblings: kinCards(slug, "siblings"),
    herSiblings: kinCards(spouseSlug, "siblings"),
    hisLabel: String(rec.name || slug).split(" ")[0] + "’s",
    herLabel: spouseName ? String(spouseName).split(" ")[0] + "’s" : "Theirs",
    weak: !!o.weak,
    weakNote: o.weak ? "This generation rests on the family tree alone." : "",
  };
};

const yr = (t) => { const m = String(t || "").match(/(c\. )?(1[5-9]\d\d)/); return m ? (m[1] || "") + m[2] : undefined; };
const SICILY = Object.fromEntries(sicilySpine.map((g) => [g.name, g]));
const reg = (n) => ({ born: yr(SICILY[n]?.born), died: yr(SICILY[n]?.died) });

/* THE MAZZA NAME LINE, oldest first. Years from the Piedimonte registers, not the tree. */
export const mazzaRows = [
  rowOf("michael-rocco-mazza", 0),
  rowOf("frank-mazza", 1),
  rowOf("sebastiano-mazza", 2),
  rowOf("salvatore-mazza", 3, { ...reg("Salvatore Mazza"), place: "Piedimonte Etneo, Catania, Sicily" }),
  rowOf("rosario-mazza", 4, { ...reg("Rosario Mazza"), spouse: "Leonarda Bonanno", spouseSlug: "leonarda" }),
  rowOf("mariano-mazza-1809", 5, { ...reg("Mariano Mazza"), spouse: "Maria Catalano", spouseSlug: "maria-catalano" }),
].reverse();

const UNSOURCED = new Set([6, 7, 8, 9]);   /* as /direct-line/: the generations the tree asserts */
export const prostamoRows = spineData.spine
  .filter((g) => g.gen >= 2)
  .map((g) => rowOf(g.slug, g.gen, { weak: UNSOURCED.has(g.gen) }));
export const prostamoWeak = prostamoRows.filter((r) => r.weak).length;

const climb = (surname) => {
  const line = quarters.find((q) => q.grandparent.surname === surname).line;
  return line.map((g, i) => rowOf(g.slug, line.length - 1 - i + 2));
};
/* quarters.json chains run oldest-first and end at the grandparent (generation 2) */
export const arenaRows = climb("Arena");
export const polistenaRows = climb("Polistena");

/* FAMILY PAGES NEVER NAME THE LIVING (tools/check_familypages.py enforces it). The front page
   may show Frank and Michael; a family page may not, so a ladder built for one drops any child
   or sibling who is living, and the page says so. */
const noLiving = (rows) => rows.map((r) => {
  const keep = (cs) => cs.filter((c) => !(P_BY_SLUG.get((c.href || "").split("/")[2]) || {}).living);
  return { ...r, children: keep(r.children), hisSiblings: keep(r.hisSiblings), herSiblings: keep(r.herSiblings) };
});

/* family-page slug -> the ladder it shows, and the sentence that says whose it is */
export const LADDERS = {
  prostamo: { rows: noLiving(prostamoRows), weak: prostamoWeak,
    who: "Domenica Prostamo, mother of the generation that carries the Mazza name, is generation 2 here, beside her husband Sebastiano Mazza. This is the longest descent in the archive." },
  polistena: { rows: noLiving(polistenaRows), weak: 0,
    who: "Angela Polistena is generation 2, grandmother of the youngest generation, through her mother Nunnziata Donato." },
  donato: { rows: noLiving(polistenaRows), weak: 0,
    who: "The Donato come in through Nunnziata Donato, mother of Angela Polistena (generation 2): the same line as on the Polistena page." },
  arena: { rows: noLiving(arenaRows), weak: 0,
    who: "Rocco Arena, grandfather of the youngest generation, is generation 2 here." },
};
