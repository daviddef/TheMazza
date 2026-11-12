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
     The name    had sixteen entries and keeps two (The Name, The Mazza). The other fourteen are family pages and are Places & families >
                 Families. There is no /families/ index in this archive, so none of the fourteen can leave the menu in this change.
   The family pages come from lib/familylist.js (FAMILY_MENU); "The Mazza" is its first entry and stays under The name.
   Carried over from the old Base.astro: the landing page at defranceski.com built its chips for this archive from the family pages in
   the menu, so a family page that is not in the menu did not appear there. They are in the menu still, under Places & families > Families. */
import { navGroups } from "./research-menu.js";
import { FAMILY_MENU } from "./familylist.js";

/* the family pages other than The Mazza, which belongs with The Name */
const [MAZZA, ...OTHER_FAMILIES] = FAMILY_MENU;

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
    { head: "Drawn", items: [
      ["/tree/", "Our line, drawn"], ["/trees/", "The trees"], ["/roots/", "Roots & Routes"], ["/timeline/", "The Timeline"],
      ["/bloodline/", "Blood relatives, drawn"],
    ] },
  ]],
  ["Places & families", [
    { head: "The families", items: [
      ["/lines/", "The Four Quarters"], ["/the-hundred-and-ten/", "The Hundred and Ten"], ["/components/", "The Pieces"],
    ] },
    { head: "Places", items: [
      ["/places/", "Places"], ["/atlas/", "The Atlas"], ["/nudgee/", "Nudgee"], ["/piedimonte-etneo/", "Piedimonte Etneo"],
      ["/briatico/", "Briatico"], ["/scilla/", "Scilla"], ["/brisbane/", "Brisbane"],
    ] },
    { head: "Families", items: OTHER_FAMILIES },
  ]],
  ["The name", [
    ["/name/", "The Name"], MAZZA,
  ]],
  ["Research", navGroups],
];
