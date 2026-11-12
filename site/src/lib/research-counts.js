/* One sentence for each Research page: what it asks, and a number the archive can state from its own data. Counted at build time, so
   it cannot go stale. 12 November 2026 (the research-menu trial, wave 4). */
import questions from "../data/questions.json";
import errands from "../data/errands.json";
import worklist from "../data/worklist.json";
import searched from "../data/searched.json";
import corrections from "../data/corrections.json";
import book from "../data/book.json";
import { RESEARCH } from "./research-menu.js";

const nf = (n) => n.toLocaleString("en-GB");
const wl = worklist.rows || [];
const open = wl.filter((r) => r.state === "next" || r.state === "running").length;
const COUNT = {
  "/open-questions/": `${nf(questions.length)} questions`,
  "/errands/": `${nf((errands.doors || []).length)} offices to write to`,
  "/worklist/": `${nf(open)} still open, ${nf(wl.filter((r) => r.state === "done").length)} done`,
  "/searched/": `${nf(searched.length)} searches`,
  "/corrections/": `${nf(corrections.count)} claims taken back`,
};
const parts = book.parts || [];
const BLURB = Object.fromEntries(
  parts.flatMap((p) => p.chapters || []).map((c) => [c.path, c.blurb]));
const ASKS = Object.fromEntries(RESEARCH.flatMap((g) => g.items).filter((x) => x.asks).map((x) => [x.href, x.asks]));

export const blurbOf = (x) => {
  const asks = ASKS[x.href] || BLURB[x.href] || "";
  const n = COUNT[x.href];
  return [asks, n ? `<em>${n}.</em>` : ""].filter(Boolean).join(" ");
};
