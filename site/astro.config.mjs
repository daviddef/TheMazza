import { defineConfig } from 'astro/config';

// GitHub Pages project site. To serve from a custom domain later,
// set base to '/' and site to that domain.
export default defineConfig({
  site: 'https://daviddef.github.io',
  base: '/TheMazza',
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
  redirects: { '/families': '/TheMazza/marriages',
    /* 9 October 2026: the estate's address for this page is /changes/. */
    '/what-changed': '/TheMazza/changes/' },
});
