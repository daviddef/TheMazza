import { defineConfig } from 'astro/config';

// GitHub Pages project site. To serve from a custom domain later,
// set base to '/' and site to that domain.
export default defineConfig({
  site: 'https://daviddef.github.io',
  base: '/TheMazza',
  build: { format: 'directory' },
  /* /families/ was a census: all 123 surnames with a count against each and no
     claim about any of them. It is now a section of /marriages/, where each
     surname is placed by descent and the page can finally say WHY the name is
     here — that a person married a person, and which person. The old address
     has been published, so it redirects rather than 404s. */
  redirects: { '/families': '/TheMazza/marriages' },
});
