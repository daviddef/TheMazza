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
import { loadReceipts } from "@daviddef/archive-kit/lib/receipts.js";
import searched from "../data/searched.json";
import worklist from "../data/worklist.json";
import people from "../data/people.json";

const NEGATIVE = /^(none found|negative|nil\b|not found|both negative)/i;
/* The nil reading is carried in a field that is NOT enumerable, and the kit is told to read the outcome from it first (`fields.outcome`).
   A row's identity for the Record Atlas receipts is the hash of the row exactly as it sits in searched.json (kit/lib/receipts.js, rowkey),
   so the row must not change: a copy with `outcome: "nil"` written into it would hash to a different key than the Atlas holds, and about
   three rows in ten (308 of 1,076 on 12 Nov 2026) would read "Not sent yet" for ever. A non-enumerable property is read by the kit and
   not by the hash. */
const rows = searched.map((r) => {
  if (!(r.outcome === "done" && NEGATIVE.test(String(r.result || "").trim()))) return r;
  const c = { ...r };
  Object.defineProperty(c, "outcomeShown", { value: "nil", enumerable: false });
  return c;
});

export const pulse = buildPulse({
  searched: rows, worklist,
  fields: { outcome: ["outcomeShown", "outcome", "status"] },
  counts: { people: people.length },
  /* the Record Atlas's receipts for this archive (id "mazza"): null on any failure, so a build never fails on the Atlas being down */
  receipts: await loadReceipts("mazza"),
});
