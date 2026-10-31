# palace_r3_evidence: find pictures, drawings and descriptions for every building, and show them in the panel

You are working in `/opt/data/workspace/000_Dev/palace-beijing-yaga-sh`, a reconstruction of the Old Summer Palace (圆明园 Yuanmingyuan, Beijing) as it stood before October 1860.

Read `CLAUDE.md` first: it is the project rulebook (confidence, copyright, coordinates). Then read:
- `research/README.md`, `research/sources.md`, `research/questions.md`
- `research/photos/README.md` and `catalog.csv`
- the head of `research/buildings.csv`, and `research/buildings/README.md` plus two building pages
- `scripts/building_pages.py`, and how `site/reconstruction/` shows the panel (`panel*.js` / `3d.js`)

Round 1 (research) and Round 2 (dev map, 3D boxes, building pages) are committed (HEAD `33b3f29`). The template project is `/opt/data/workspace/000_Dev/kostrzyn-yaga-sh`. Read its photo catalogue, its `research/photos/README.md` and a few building pages, e.g. `research/buildings/B03-*` and `V008-*`, to see what "click a building and see something" means there. **Never edit that repo.**

## What Tomasz asked for (his words)
"Run more detail with the research. Try to find any pictures, any reference, any sketch, anything about each building. The same way we did with Küstrin, I would like to be able to click on every building, or the set of buildings if you couldn't find enough information, and see something. Research any information available."

## Where it stands (measured at 19:12 UTC)
- `buildings.csv`: 1824 rows, of which 314 are top level (64 scenes, 111 compounds, ...) and the rest halls, gates, towers and so on.
- `photos/catalog.csv`: 230 pictures (182 free, 48 research-only).
- **Only 58 of the 314 top-level objects** have any picture in `shows`. 1819 of the 1877 panel JSONs have no photos at all. Most panels show only the box size and the typology.

## Goal
**Every clickable object shows real evidence in its panel.**
- That means at least one picture, drawing, plan reference or period description, either its own or its compound's.
- A hall with nothing of its own shows its compound's evidence under a clear heading: "Evidence for the whole compound 九洲清晏 (no picture of this hall found)". That is the "set of buildings" fallback he asked for.
- Wherever a source names or shows the hall itself, the hall gets its own entry.

## Evidence to hunt (per scene and compound first, then the named halls)
1. **Forty Scenes album 圆明园四十景图 (1744, BnF):** one leaf per scene, with the Qianlong poem and preface for that scene (御制圆明园四十景诗). Link every leaf to its scene, and transcribe the preface (Chinese plus a short English summary) into the page notes. Commons has PD-Art copies.
2. **Xiyang Lou copperplate engravings** (20 plates, 1783-86): one per view, linked to the European buildings and fountains they show. PD on Commons.
3. **Other Qing paintings:**
   - 圆明园图咏 (the 1887 woodblock edition of the Forty Scenes)
   - the 唐岱 and 沈源 album
   - 乾隆 paintings of 万方安和 and the like
   - 清明上河-style court scrolls of the gardens
   - Princeton's scrolls, already in `research/raw/plans/`: find out what they are
4. **Yangshi Lei 样式雷 drawings:** look for each scene in online catalogues, e.g. 国家图书馆 数字方志 / 样式雷图档 listings and the 故宫 collection. Record the title, catalogue number and link per drawing. They stay link cards (research-only), but the facts they give (bays, layout) go into the CSV with the source.
5. **Texts:** extract the passage for each scene and compound as a dated description, with chapter and line cited. Sources:
   - 日下旧闻考 Rixia jiuwen kao, chapters 80-87 (on ctext / Kanripo; the earlier round fetched 80-85 into `/opt/data/cache/scratch/palace_r1_inv/` if it still exists)
   - 圆明园记 and the 清宫 records
   - Malone 1934 (archive.org, if it is out of copyright there)
   - 李斯 / 汪荣祖 / Ringmar are modern books: cite them, don't copy them
6. **Photographs of the ruins** (all public domain, 1860-1930s):
   - Ernst Ohlmer (1873, the Xiyang Lou)
   - Thomas Child (1870s)
   - John Thomson
   - Felice Beato (1860, the city; check whether any frame shows the gardens)
   - Théophile Piry, Sidney Gamble (Duke, CC/PD: check), Hedda Morrison (Harvard; check the licence), Osvald Sirén
   - Library of Congress and Commons categories

   Tie each one to a camera position and the object ids it shows.
7. **Modern photos of today's remains** on Commons (CC BY / BY-SA, with the licence checked), for every compound whose ruins, lake or hill survive: the 正觉寺 survives, plus 鉴碧亭, the Xiyang Lou ruins, and the rebuilt 九洲清晏 foundations.
8. **Modern reconstructions** (Tsinghua 数字圆明园, 郭黛姮's books, the park's own renders): link cards only, no copies.
9. **Archaeology:** the excavation reports of 2001-2020 (含经堂, 九洲清晏, 长春园宫门, 如园, 西洋楼 surveys). Record the facts per compound, with a link.

## Data rules (the Küstrin pattern)
- **Pictures:** every picture is a row in `research/photos/catalog.csv` with `shows` (`ID:sure|likely|guess`) and its `rights_class`.
  - Free images (licence checked on the holder's page): web size, at most 1600 px on the long side and about 300 KB, in `research/photos/images/`. `scripts/photos_catalog.py` (or the existing equivalent) copies them to the site.
  - Research-only images stay in `research/raw/photos/` at most, and are shown only as link cards with a "View at ..." link.
- **Texts and drawings:** non-image evidence (text passages, Yangshi Lei catalogue entries, archaeology facts) gets its own catalogue, e.g. `research/evidence/catalog.csv` (E0001...: kind, source_id, title, date, link, rights_class, shows, excerpt_zh, summary_en). Document it in `research/README.md`.
  - Quotes from Qing texts are public domain; quote them in full where short.
  - Modern works get only a short summary in your own words, with a citation.
- **Generated pages:** extend `scripts/building_pages.py` so each panel shows:
  1. its own pictures
  2. its own texts and drawings
  3. the parent's evidence under the fallback heading
  4. a line saying what was searched and not found

  The generator must stay idempotent: a second run changes nothing. Hand notes go under `## Notes` as before.
- **Sources and facts:**
  - Each new source gets an S-id after the highest one in `sources.md`.
  - Conflicts and gaps go into `questions.md`.
  - A fact that improves a building row (real bays, a hall name, a date) goes into `buildings.csv` with its source and a raised confidence. Never renumber ids.
  - Keep a `research/wishlist.md` of what would fill the remaining gaps (archive, item, how to request).

## How to work
- **Use subagents, in the FOREGROUND only:** several Agent calls in ONE message, never `run_in_background`. Never end your turn while a subagent, crawler or background shell still runs: print mode kills background work about 10 minutes after your last turn, and an earlier round lost everything that way.
  - Split the hunt by evidence type (the list above), in waves of about 30-45 minutes each.
  - Each subagent writes its findings incrementally to `/opt/data/cache/scratch/palace_r3_notes_<topic>.md` (full links, licence quotes, ids), so a crash keeps the partial work.
  - You alone write the shared repo files.
- **Search in Chinese as much as in English.** Be polite to servers: one request at a time per host, short sleeps, a real User-Agent. When a site blocks you, log it in a question instead of hammering it.
- **Time-box** about 20 minutes per scene; a missing piece goes on the wishlist, never a stall. Breadth across all 314 top-level objects comes first, depth on the famous ones second.
- **Python:** the repo `.venv` through `/opt/data/.local/bin/uv run`. **Node:** put Playwright into `/opt/data/cache/scratch/palace_r3_tools/`.
- **Ports:** 8800-8809, bound to 127.0.0.1; stop the servers when you are done. Never use 8790: that is the live preview, and a plain static server already runs there.
- **No git commands that write.** Lily commits.
- Log one line per milestone, at least every 15 minutes, to `/opt/data/cache/scratch/palace_r3_evidence_progress.md`.

## Verification
- **`tools/check_evidence.py`:**
  - prints the counts: top-level objects with their own picture, with their own text or drawing, and with nothing; halls with their own evidence vs the parent fallback only
  - fails if any clickable object ends up with an empty evidence section
  - asserts that no research-only image file or path is in `site/`
- **Generators:** run `scripts/building_pages.py` twice (the second run changes nothing), then `tools/check_pages.py`.
- **Screenshots** in `screenshots/r3/`, from one page load: the panel open for 九洲清晏, 方壶胜境, 海晏堂, a small unnamed hall (to show the fallback) and one Qichun Yuan compound. Open each yourself and fix layout problems (images too big, overflowing text, broken links).
- **Health:** no console errors; `http://127.0.0.1:8790/reconstruction/3d.html?b=YM03` loads.

## Final message
Lead with the coverage numbers from `check_evidence.py`, before and after. Then list:
- the best new finds, three to five, with what they show
- which buildings are still thin, and why
- the wishlist highlights
- what is free and what is link-only
- what is verified and what is assumed

Do not ask questions. Work only in this repo, plus the scratch paths named above.
