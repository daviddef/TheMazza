/* STORY MODE FOR THE PEOPLE PAGES (PERSON-PAGE-SPEC.md section 2a): every person who is not living and whose story holds something is told on a timeline, and not drawn as a chart.

   NOTHING HERE WRITES A WORD ABOUT A PERSON. The stops are the kit's (lib/personstory.js storyOf): «Where they came from» (parents, grandparents, and the line of fathers up to the
   earliest person the archive holds), Birth (brothers and sisters), What they left behind (children). The only prose this archive holds about a person is the note it wrote on
   reading a register (`registerNote`, shown until now as «Why this person is here»); it is moved, unchanged, into the story's last and quiet stop («About this record»), cut into
   chapters by the kit's chaptersOf at the bold leads the author wrote, and is not drawn a second time. A person whose story has nothing beyond «no parent is named» (hasStory)
   keeps the chart page.

   THE LIVING RULE IS THE KIT'S. Every relative is drawn through the kit's isLiving / isHeldOut (famNode): a living relative is a name and a relationship and nothing else; a relative
   the rule holds out is not drawn at all. people.json holds no birth year for a living person, so those people (and only those) carry `saidLiving`, the archive's own statement
   (tools/living_v2.py), exactly as src/lib/personpage.js does for the chart. A living person's own page is never in story mode (the kit does not allow it, and the page does not ask).

   THE ROW THE KIT READS (personstory.js, «the tree shape»): { id, given, sur, sex, by, bye, dy, dye, bp, line, href, father, mother, kids[], spouse[], saidLiving }. Father and mother are the
   parent of recorded sex M and F (every parent in people.json has a recorded sex, so no sex is inferred); a person with no recorded sex is drawn with the words «Brother or sister»,
   «Child» and «Married to», which do not say. */
import people from "../data/people.json";
import PS from "@daviddef/archive-kit/data/public-sources.json";
import { familyOf, ancestryOf, chaptersOf, storyOf, hasStory } from "@daviddef/archive-kit/lib/personstory.js";
import { deadRecorded } from "./personpage.js";

const RULE = { now: new Date().getFullYear(), sources: PS };
const EST = /^\s*(c\.|ca\.?|circa|about|abt)\b/i;
const href = (p) => `/people/${p.slug}/`;
const byRec = new Map(people.map((p) => [p.id, p]));

function row(p) {
  const ps = (p.parents || []).map((r) => byRec.get(r.id)).filter(Boolean);
  const father = ps.find((q) => q.sex === "M"), mother = ps.find((q) => q.sex === "F");
  const parts = String(p.name || "").split(" ");
  const base = { id: p.id, given: p.given || "", sur: p.surname || "", sex: p.sex === "M" || p.sex === "F" ? p.sex : "", href: href(p),
                 father: father && father.id, mother: mother && mother.id, kids: (p.children || []).map((r) => r.id), spouse: (p.spouses || []).map((r) => r.id),
                 line: p.onSpine ? 0 : 1 };
  /* a living person: a name and the archive's own word that they are living; no year of any kind (people.json holds none) */
  if (p.living) return { ...base, saidLiving: true };
  return { ...base, by: Number.isInteger(p.born) ? p.born : null, bye: EST.test(p.bornText || "") || undefined, dy: Number.isInteger(p.died) ? p.died : null,
           bp: p.birthPlace || "", dead: deadRecorded(p) || undefined };
}
export const TREE = Object.fromEntries(people.map((p) => [p.id, row(p)]));
/* the thread up the line of fathers (and each mother's father) is drawn only through parents of recorded sex, which is every parent here; the second map keeps that explicit */
export const STRICT = Object.fromEntries(Object.entries(TREE).map(([id, r]) => [id, { ...r,
  father: r.father && TREE[r.father].sex === "M" ? r.father : undefined, mother: r.mother && TREE[r.mother].sex === "F" ? r.mother : undefined }]));

/* what the archive holds for the PERSON (a mark on the card), as the chart's caption already says: a record read about them, or the family tree alone */
const markOf = (id) => { const r = byRec.get(id); if (!r || r.living) return null;
  return (r.records && r.records.length) || r.fromRegister ? { tier: "doc", label: "Documented" } : { tier: "tree", label: "Family" }; };
/* what a LINK rests on, only where the archive has said how it knows it: a register act read (via read), or the family tree (via tree). An index entry is neither, and has no mark. */
const linkOf = (p, id) => { for (const b of ["parents", "children", "spouses"]) { const e = (p[b] || []).find((x) => x.id === id);
  if (e && e.via === "read") return { relation: "", grade: "doc" }; if (e && e.via === "tree") return { relation: "", grade: "tree" }; } return null; };

/* the story of one person, or null when the page stays a chart. */
export function storyOfPerson(p) {
  if (p.living) return null;
  const fam = familyOf(TREE, p.id, RULE);
  if (!fam) return null;
  for (const list of [fam.parents, fam.grand, fam.siblings, fam.children, fam.spouses]) for (const n of list) { if (!n || n.unknown) continue; n.ev = markOf(n.id); const l = linkOf(p, n.id); if (l) n.link = l; }
  const threads = ancestryOf(STRICT, p.id, null, RULE);
  for (const t of threads) for (const n of [t.parent, t.earliest, ...t.between]) if (n && !n.unknown) n.ev = markOf(n.id);
  const chapters = p.registerNote ? chaptersOf(p.registerNote, "") : [];
  const born = Number.isInteger(p.born) ? p.born : null, died = Number.isInteger(p.died) ? p.died : null;
  const r = { b: born ? (EST.test(p.bornText || "") ? `c. ${born}` : born) : null, d: died };
  /* every note this archive writes about a person is about how it read a register: it goes last and quiet */
  const stages = storyOf(chapters, fam, [], r, threads, { metaRx: /[\s\S]/ });
  return hasStory(stages) ? { stages, fam } : null;
}
