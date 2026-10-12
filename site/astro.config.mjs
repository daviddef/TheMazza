import { defineConfig } from 'astro/config';

// Custom domain, from 12 October 2026: https://mazza.defranceski.com/
// Served by GitHub Pages from this project repo. `base` is '/' because every
// link here is now site-root relative, and site/public/CNAME is what keeps the
// domain attached across Actions deploys — a CNAME that exists only in dist/ is
// wiped by the next build, which is why a sibling archive with correct DNS still
// serves a 404. The DNS was already right long before this: mazza.defranceski.com
// has pointed at daviddef.github.io and the four GitHub Pages addresses all along,
// and the only thing missing was this file and this line.
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
     claim about any of them. It is now a section of /marriages/, where each
     surname is placed by descent and the page can finally say WHY the name is
     here — that a person married a person, and which person. The old address
     has been published, so it redirects rather than 404s. */
  redirects: { '/families': '/marriages',
    /* 9 October 2026: the estate's address for this page is /changes/. */
    '/what-changed': '/changes/' },
});
