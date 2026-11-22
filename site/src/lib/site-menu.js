/* 23 NOVEMBER 2026 (the estate clean-up). Three changes, all in this file's groups and none of them removes a page from reach:
     People > Drawn      was a column of five links (Our line drawn, The trees, Roots & Routes, The Timeline, Blood relatives drawn); it is ONE link
                         to the hub /drawn/ (lib/drawn.js), which lists the four that stay with a line each, and The Spine. Roots & Routes was removed
                         (/roots/ redirects to /trees/).
     Families            was the hub link and fifteen family pages; it is the hub link /families/ ("All the families") and four named families: the
                         archive's own line first (Mazza), then Arena, Nicotra and Prostamo, A to Z. /families/ links all fifteen (it reads lib/familylist.js,
                         as the menu did), so the eleven that left the menu are one click away; docs/menu-reach.md proves it.
     Research > Deep dives  is a link to /research/deep-dives/ (lib/research-menu.js).
   THE FAMILIES THAT STAY NAMED, and why these: the three pages written by hand, each with its own argument (Mazza, Arena, Nicotra), and the first of
   the data-built pages in familylist.js, which that file orders by direct-line ancestors and published people (Prostamo). David's 12 Nov rule holds:
   own line first, then A to Z.
   THE 12 NOVEMBER NOTE, kept below. */
/* THE WHOLE MENU, one list. 12 November 2026 (the menu regroup, PR A, menu only): the five groups other than Research are five again,
   but filled differently, and Research (lib/research-menu.js, unchanged) is the sixth. The header menu and the drawer read THIS list
   (layouts/Base.astro does), so there is one place to change a label or move a page. No page was renamed, no page was merged and no
   address changed: every href below is a page that was already built, only the group it is listed in moved.
     a menu is  [label, items]
     items     either a flat list of [href, label]            (a short menu: one column)
               or a list of groups { head, href?, items }   (a group is a column; `href` makes its heading a link; an item is [href, label])
   What moved:
     Start       had ten entries and keeps three (Home, The story, About). The trees, Our line drawn, Roots & Routes and The Timeline are
                 now People > Drawn; The Atlas and The Four Quarters are Places & families; What's new left Start and is the What's new
                 group of Research (it is also the pulse button), so it was not lost.
     The families (The Marriages, The Hundred and Ten, The Pieces): The Marriages is People > Lists; the other two are Places & families.
     People & places is split: the five lists and Blood relatives are People; Places and the five place pages are Places & families.
     The name    had sixteen entries and keeps one (The Name). Mazza joined the family entries (Places & families > Families, first, as
                 "Mazza"); the other fourteen are family pages there too. There is no /families/ index in this archive, so none of the
                 fifteen can leave the menu. The family labels are the bare surname and the order is Mazza, then A to Z (12 November 2026).
     Places      is a link as well as a sub-head, so the list no longer repeats "Places" under itself.
   The family pages come from lib/familylist.js (FAMILY_MENU).
   (The old Base.astro said the landing page at defranceski.com builds its chips for this archive from the family pages in the menu. It does
   not: those chips are fixed links on a hand-written page, so no menu group name or order matters to it.) */
import { navGroups } from "./research-menu.js";
import { FAMILY_MENU } from "./familylist.js";

/* 13 November 2026: the Families group began with a link to the new /families/ index (every family page, own line first, then A to Z). 23 November 2026:
   the entries after it are cut to the four NAMED below; the index links every family page, so none is out of reach. */
/* THE FAMILY ENTRIES (the family-menu rule, David, 12 November 2026: "own line first then A to Z"): the label is the bare surname (Arena,
   not The Arena), the archive's own line (Mazza) comes first, and the other surnames follow A to Z. familylist.js keeps its own labels
   ("The Arena") for the pages that use them; only the menu reads them bare. */
const bare = ([href, label]) => [href, label.replace(/^The /, "")];
const NAMED = ["/mazza/", "/arena/", "/nicotra/", "/prostamo/"];   /* the archive's own line first; the rest A to Z */
const [MAZZA, ...REST] = FAMILY_MENU.map(bare).filter(([href]) => NAMED.includes(href));
const FAMILIES = [["/families/", "All the families"], MAZZA, ...REST.sort((a, b) => a[1].localeCompare(b[1], "en", { sensitivity: "base" }))];

export const MENU = [
  ["Start", [
    ["/", "Home"], ["/story/", "The story"], ["/about/", "About"],
  ]],
  ["Our line", [
    ["/direct-line/", "The Spine"], ["/ancestors/", "The Ancestors"], ["/the-name-line/", "The Mazza Name Line"], ["/crossings/", "The Crossings"],
  ]],
  ["People", [
    { head: "Lists", items: [
      ["/people/", "The People"], ["/who/", "Every Name"], ["/register/", "The Register"], ["/households/", "Households"],
      ["/marriages/", "The Marriages"],
    ] },
    { head: "Drawn", href: "/drawn/", items: [] },
  ]],
  ["Places & families", [
    { head: "The families", items: [
      ["/lines/", "The Four Quarters"], ["/the-hundred-and-ten/", "The Hundred and Ten"], ["/components/", "The Pieces"],
    ] },
    { head: "Places", href: "/places/", items: [
      ["/atlas/", "The Atlas"], ["/nudgee/", "Nudgee"], ["/piedimonte-etneo/", "Piedimonte Etneo"],
      ["/briatico/", "Briatico"], ["/scilla/", "Scilla"], ["/brisbane/", "Brisbane"],
    ] },
    { head: "Families", items: FAMILIES },
  ]],
  ["The name", [
    ["/name/", "The Name"],
  ]],
  ["Research", navGroups],
];
