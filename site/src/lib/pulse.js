/* What is new here, and the archive in numbers: the kit computes it at build time from this archive's own logs (kit/docs/whats-new.md).
   This file is the only Mazza-specific part: which JSON is which, and how this archive's outcome words read.

   searched.json (made by tools/build_searched.py from data/searched.tsv): `outcome` is the TSV status, with wall read as blocked, and for
   a register row `found` when the result opens FOUND. `done` says ONLY that the search was made ("which says only that the search was
   made; the text says how far it got", build_searched.py), so it is NOT mapped to found: that would count a nil as a find. The kit knows
   found, part (partial), blocked and correction. A `done` row is read as a nil only where its own result opens with a plain negative
   (NONE FOUND, NEGATIVE, NIL, Not found); every other `done` row, and superseded / outstanding / not-yet, is left off the timeline and
   stays on /searched/. `when` is the day the work was done (the TSV's date column), never a record year. corrections.json holds undated
   tree-versus-record corrections, not a log of work, so it is not passed (the three `correction` rows of the log become cards). */
import { buildPulse } from "@daviddef/archive-kit/lib/pulse.js";
import searched from "../data/searched.json";
import worklist from "../data/worklist.json";
import people from "../data/people.json";

const NEGATIVE = /^(none found|negative|nil\b|not found|both negative)/i;
const rows = searched.map((r) => (r.outcome === "done" && NEGATIVE.test(String(r.result || "").trim()) ? { ...r, outcome: "nil" } : r));

export const pulse = buildPulse({
  searched: rows, worklist,
  counts: { people: people.length },
});
