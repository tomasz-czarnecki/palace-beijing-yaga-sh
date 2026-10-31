# palace_home: a simple homepage for the Yuanmingyuan reconstruction

You are working in `/opt/data/workspace/000_Dev/palace-beijing-yaga-sh`, a new repo for a walkable 3D reconstruction of the Old Summer Palace (圆明园 Yuanmingyuan, Beijing) as it stood before October 1860. Read `CLAUDE.md` in this repo first; it is the project rulebook.

## What Tomasz asked for
"In the meantime you can spawn a very simple homepage." The project copies the structure of his sister project, `/opt/data/workspace/000_Dev/kostrzyn-yaga-sh` (Küstrin 1913, live at https://kostrzyn-yaga-sh.vercel.app). Read its `site/index.html`, `site/styles.css`, `site/main.js`, `site/credits.html`, `site/vercel.json` and `site/.vercelignore` and its CLAUDE.md section "Layout and website". **Never edit anything in that repo.**

## Deliverables (all under `site/`, plus one credits file)
1. `site/index.html`: a simple, good-looking one-page homepage in the same family style as the Küstrin homepage (same structure, typography and the yaga.sh family bar at the top, copied and adapted). Keep it short:
   - A hero with the title (圆明园 Yuanmingyuan, "The Old Summer Palace before 1860"), one or two lines on what the project is, and a button "Enter the reconstruction" linking to `reconstruction/`.
   - A small "research in progress" tag.
   - Three short sections:
     - **What it was:** the three gardens, the Qing emperors' main residence, Chinese gardens plus the European palaces.
     - **What happened:** looted and burned by British and French troops on 18–19 October 1860, during the Second Opium War. Factual, sober, no adjectives for effect.
     - **How we rebuild it:** Qing site plans, the Forty Scenes album, the Xiyang Lou engravings and today's lakes and hills, every building traced to a source, guesses marked.
   - A footer with a link to the credits.
   - Verify every fact you write (Wikipedia: https://en.wikipedia.org/wiki/Old_Summer_Palace is the starting point) and keep it to things a source states.
2. `site/zh/index.html`: the same page in simplified Chinese, marked as a draft in an HTML comment. Natural Chinese, not word-for-word.
3. **Hero image (optional):** one leaf of the Forty Scenes album (圆明园四十景图, 1744) or one Xiyang Lou engraving from Wikimedia Commons, if its file page shows a public-domain licence (PD-Art / PD-old). Download a web-sized copy (max ~1600 px wide, compressed) into `site/assets/img/`. Credit it on `site/credits.html` and in `research/image-credits/CREDITS.md` (create only that one file under `research/`; another worker owns the rest of `research/`). No image without a checked licence.
4. `site/credits.html`: short, in the Küstrin style: image credits and "sources will follow as the research grows".
5. `site/styles.css`, `site/main.js`, `site/assets/` (fonts copied from the Küstrin site if it uses local fonts, a simple SVG favicon and mark), `site/vercel.json` (cleanUrls like Küstrin's), `site/.vercelignore`.
6. `site/reconstruction/index.html`: a tiny placeholder ("Map and 3D view in progress", back link to the homepage) in the site's style. Round 2 replaces it with the dev map.

**Colour:** take the Küstrin palette as the base, but give this site its own accent fitting a Qing garden (for example a muted cinnabar red or the grey-blue of the roof tiles). Avoid teal plus cream: Tomasz dislikes that combination.

## Rules
- Links must work on a plain static server and on Vercel: `reconstruction/`, `credits.html`, `zh/`, `../`. Nothing under `site/` may reference a file outside `site/`.
- Write only these files: `site/**`, `research/image-credits/CREDITS.md`. **Another Claude Code worker is doing research in this repo at the same time.** Never touch `research/` (except that one file), `scripts/`, `CLAUDE.md`, `pyproject.toml`, `tools/`.
- **No git commands that write** (no add, commit, stash, checkout, restore, reset). Read-only git is fine. Lily commits.
- **Ports:** test with `python3 -m http.server 8791 --bind 127.0.0.1 -d site` (8791–8792 are yours). Never use 8790: it is the live preview and already serves `site/`. Stop your servers when done.

## Verification
- Headless screenshots (Playwright; the Küstrin repo's `tools/` shows how it ran there; `npm install` into `/opt/data/cache/scratch/palace_home_tools/` if you need it, not into this repo) of EN and ZH at desktop 1440×900 and mobile 390×844.
- Save them to `screenshots/home/` (gitignored).
- Open every screenshot yourself and fix what looks off: overflow, broken fonts, missing image, Chinese text rendering.
- No console errors, no 404s in the network log.
- Log one timestamped line per milestone to `/opt/data/cache/scratch/palace_home_progress.md`.

## Final message
Lead with what the page says and looks like. Then list:
- the files you made
- the image and its licence
- what you verified, and what is not verified (e.g. Vercel behaviour)
- the defaults Tomasz can swap (accent colour, title wording, hero image)

Do not ask questions. Work only in this repo, plus the scratch files named above.
