/* THE RESEARCH MENU: one list, read by the header menu (layouts/Base.astro), the drawer, the hub page /research/ and the group
   pages. 12 November 2026 (the research-menu trial, wave 4, after Defranceski, Booyzen, Luwinski and Lerena): "Evidence" and
   "Investigations" became one "Research" menu with three groups, and a small fourth group, Checks, for the audit of negatives. Nothing
   is renamed or removed: every item keeps the address it had, and the labels of the eight pages the estate's Evidence canon names
   (kit data/evidence-menu.json) are unchanged. `asks` is the canon's question for those pages. The three long studies (the Sicilian
   registers, the Queensland register, the test of the 1697) are deep dives under Sources & method, and are linked from /sources/ too.
   Checks is its own group so it is easy to fold elsewhere (into Sources & method, or into What's new) if the trial prefers. */
export const RESEARCH = [
  { id: "to-do", head: "To do", href: "/research/to-do/",
    dek: "What is not known yet, what has been asked of other people, and what is being worked on.",
    items: [
      { href: "/open-questions/", label: "Open Questions", asks: "What is not known, and what would settle it?" },
      { href: "/errands/", label: "Errands", asks: "What has been asked of other people, or needs someone standing in a place?" },
      { href: "/worklist/", label: "The work list", asks: "What is being done, by whom, since when?" },
    ] },
  { id: "whats-new", head: "What's new", href: "/whats-new/",
    dek: "What was read, found and taken back lately, newest first, and the same record in full.",
    items: [
      { href: "/searched/", label: "What Has Been Read", asks: "What was looked at, and what did it not turn up?" },
      { href: "/corrections/", label: "Corrections", asks: "What did this archive get wrong?" },
      { href: "/changes/", label: "What changed", asks: "What happened, most recent first?" },
    ] },
  { id: "sources-and-method", head: "Sources & method", href: "/research/sources-and-method/",
    dek: "What this archive stands on, how it reads a register, the documents themselves, and the long studies that sit beside them.",
    items: [
      { href: "/sources/", label: "Sources", asks: "What does this stand on, and where do I check?" },
      { href: "/method/", label: "Method", asks: "What would make you believe or not believe this?" },
      { href: "/documents/", label: "Documents", asks: "Which papers and images does this stand on, and can I see them?" },
      { sub: "Deep dives", id: "deep-dives",
        note: "Long studies, each of one set of registers or one proposition. They are linked from the Sources page too.",
        items: [
          { href: "/register-1879/", label: "The Sicilian Registers" },
          { href: "/queensland/", label: "The Queensland Register" },
          { href: "/briatico-tested/", label: "Testing the 1697" },
        ] },
    ] },
  { id: "checks", head: "Checks", href: "/research/checks/",
    dek: "The archive checking itself: every negative it has written, audited.",
    items: [
      { href: "/audit/", label: "The audit of negatives", asks: "Which of this archive's \"not found\" statements hold up when they are tested?" },
    ] },
];
/* the header menu's shape: [group, ...] with { head, href, items: [[href, label] | { sub }] } */
export const navGroups = RESEARCH.map((g) => ({
  head: g.head, href: g.href,
  items: g.items.flatMap((x) => x.sub ? [{ sub: x.sub }, ...x.items.map((y) => [y.href, y.label])] : [[x.href, x.label]]),
}));
