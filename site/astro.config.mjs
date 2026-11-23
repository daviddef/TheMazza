import { defineConfig } from 'astro/config';
import { readFileSync } from 'node:fs';
import { whoRedirects } from './src/lib/namesets.js';

// Custom domain, from 12 October 2026: https://mazza.defranceski.com/
// Served by GitHub Pages from this project repo. `base` is '/' because every
// link here is now site-root relative, and site/public/CNAME is what keeps the
// domain attached across Actions deploys — a CNAME that exists only in dist/ is
// wiped by the next build, which is why a sibling archive with correct DNS still
// serves a 404. The DNS was already right long before this: mazza.defranceski.com
// has pointed at daviddef.github.io and the four GitHub Pages addresses all along,
// and the only thing missing was this file and this line.
/* ONE PAGE PER PERSON (23 November 2026). A name used to have a page, /who/<name>/, beside the person's page. It does not any more:
   every one of those addresses is a static redirect (a meta refresh and a canonical, noindex, not in the sitemap). A name one person
   bears goes to that person's page; a name several bear goes to its first bearer's page at #others-of-this-name, the section that
   lists the others (src/lib/namesets.js: the earliest born who is not living, else slug order). The names READ from register acts and
   held in no family file keep their own page, so they are not here. */
const people = JSON.parse(readFileSync(new URL('./src/data/people.json', import.meta.url), 'utf8'));
const whoRedirect = whoRedirects(people);

export default defineConfig({
  site: 'https://mazza.defranceski.com',
  base: '/',
  /* WHY outDir IS A VARIABLE, and why the default must stay 'dist'.
     Several sessions build this estate at once, and `astro build` EMPTIES its
     outDir before it refills it — so one session's build wipes the tree
     another session's gates are reading, and the gates report a torrent of
     absences that are simply not copied yet. The kit's tools all honour
     ARCHIVE_OUT and, when they refuse a shared build, print «build to a
     directory of your own: ARCHIVE_OUT=...» as the way out. WITHOUT THIS LINE
     THAT HATCH CANNOT BE TAKEN: the variable redirected every reader and
     nothing that writes.
     THE DEFAULT MUST STAY 'dist' — .github/workflows uploads `path: site/dist`,
     so changing it here would publish nothing. */
  outDir: process.env.ARCHIVE_OUT || 'dist',

  build: { format: 'directory' },
  /* /families/ was a census: all 123 surnames with a count against each and no
     claim about any of them. It became a section of /marriages/ and the old address
     redirected there. On 13 November 2026 the address was given to the new /families/
     index (every family page, own line first, then A to Z), so the redirect is gone:
     the census content is still in /marriages/ and is not the index. */
  redirects: {
    /* 9 October 2026: the estate's address for this page is /changes/. */
    '/what-changed': '/changes/',
    /* 23 November 2026: Roots & Routes (the archive's own page at /roots/) was removed; the Tree Canvas on recordatlas.org replaced it
       estate-wide. The old address answers with a redirect to the archive's own trees page, and the redirect is not in the sitemap.
       /roots/view.html is NOT retired: it is the viewer the person pages frame (the Kit's PersonRootsViews), a different file in the
       same folder. */
    '/roots': '/trees/',
    ...whoRedirect },
});
