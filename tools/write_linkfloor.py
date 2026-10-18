#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Write site/.linkfloor.json (the ratchet for the build-time name linker) WITHOUT the names of people.

    npm run build, then, from site/:   python3 ../tools/write_linkfloor.py

kit/tools/checklinks.py --write-floor lists every built page by address, and the address of a person's page is the
person's name: /people/<slug>/ and /who/<slug>/ include LIVING people, whose names never go in a tracked file. This runs
checklinks.py --write-floor and then removes those two prefixes from the file. They are not lost: a page that is not in
the floor is "new", and a new page passes while it counts no more than three (--new-page-max), which the pages under
those prefixes (no running text of their own that the pass touches: they are data-no-autolink) always do.
tools/check_autolinks.py fails the build if the committed floor names a person.
"""
import os
import sys
import json
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(os.path.dirname(HERE), "site")
KIT = os.path.join(SITE, "node_modules", "@daviddef", "archive-kit", "kit", "tools", "checklinks.py")
FLOOR = os.path.join(SITE, ".linkfloor.json")
PRIVATE_PREFIXES = ("/people/", "/who/")


def prune(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    pages = data.get("pages", {})
    keep = {k: v for k, v in pages.items() if not k.startswith(PRIVATE_PREFIXES)}
    data["pages"] = keep
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")
    return len(pages) - len(keep), len(keep)


def main():
    cmd = [sys.executable, KIT, "--dist", "dist", "--index", ".autolink/names-index.json",
           "--living", "../private/living.json", "--allow-prefix", "/people/", "--floor", ".linkfloor.json", "--write-floor"]
    r = subprocess.run(cmd, cwd=SITE)
    if r.returncode:
        return r.returncode
    gone, kept = prune(FLOOR)
    print("write_linkfloor: kept %d pages, left out %d under %s (a person's address is a name)" % (kept, gone, " and ".join(PRIVATE_PREFIXES)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
