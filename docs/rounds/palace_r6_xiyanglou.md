# palace_r6_xiyanglou: deep research on the Xiyang Lou 西洋楼 (the European palaces), building by building, ready for detailed models

You are working in `/opt/data/workspace/000_Dev/palace-beijing-yaga-sh`, the reconstruction of the Old Summer Palace (圆明园 Yuanmingyuan) before 1860. Read these first:
- `CLAUDE.md` (the rulebook: confidence, copyright, layout, rebuild order)
- `docs/METHOD.md` (pitfalls)
- `research/README.md`
- the catalogues: `research/photos/catalog.csv`, `research/evidence/catalog.csv`, `research/reconstructions/catalog.csv`, `research/twins/catalog.csv`
- `scripts/building_pages.py`, `site/reconstruction/panel3d.js`, `tools/check_evidence.py`

Everything is committed (HEAD `3fa83a0`). The template project, `/opt/data/workspace/000_Dev/kostrzyn-yaga-sh`, is read-only: never edit it. Its `models/` folders and their READMEs show what a modelling-ready evidence set looks like (e.g. `models/B03-rathaus/README.md`, `models/V008-marktplatz-115/README.md`).

## What Tomasz asked for
He sent a screenshot of our 3D view of the Xiyang Lou strip in Changchun Yuan: `/opt/data/scripts/rounds_palace/palace_r6_xiyanglou_tomasz_view.png` (open it). It shows:
- 谐奇趣 Xieqiqu, highlighted yellow
- 黄花阵 Huanghua Zhen, the maze as rings of white lines around an octagonal pavilion
- 养雀笼, 方外观, 花园门, 蓄水楼
- 海晏堂 with its reservoir pool
- 远瀛观, 大水法, 观水法
- the 线法山 area and the boxes of 泽兰堂, 宝相寺 and 法慧寺 north of it

All of them are plain boxes with blue roofs.

His words: "I think this part is the most important, because it's the existing one and the most famous. Can you try to find more references about this?"

So: the Xiyang Lou is the part whose ruins survive and that everybody knows. Go deep on it, so the next round can build detailed models of it.

## Where it stands (measured)
- **44 objects** have garden Xiyang Lou or an `XY` id. 13 are main buildings (XY01-XY15); the rest are parts, many unnamed (`XY..-N0x`, `-AX`, `-B`) with no evidence of their own.
- **Pictures:** 26 engravings and 143 photos already touch these ids. All 20 copperplate plates are catalogued (P0041-P0060) with their titles.
- **Sizes are rough,** and several look wrong:
  - 大水法 XY10 is recorded as 20 × 3 m
  - 线法山 XY12 and 方河 XY14 have none
  - 海晏堂 XY08 is 19 × 44 m
- **Odd row:** XY04-N02 has parent CC22, which needs checking.
- **Existing coverage to build on, not repeat:**
  - reconstructions: e.g. the ISPRS 2015 谐奇趣 model, Tsinghua via mhymy, and the full-scale replicas 圆明新园 at 珠海 and 横店, in `reconstructions/catalog.csv`
  - European twins in `twins/catalog.csv`

## Deliverables
1. **A dossier per main building:** `research/xiyanglou/<ID>-<slug>/README.md` for XY01-XY15. Each holds:
   - **What it was:** dates, the designer (Castiglione, Benoist, the 如意馆 painters), function, and what happened in 1860 and after (stone removed, later damage), with sources
   - **Evidence by side:** for each façade (N, E, S, W) and for the roof, every picture that shows it, with id, date, which part is visible, and how reliable it is. The engraving gives the 1780s state; ruin photos give the stone parts and dimensions.
   - **A dimension sheet:** `dimensions.json` plus a readable table in the README: overall footprint, bays, storey and cornice heights, stair and terrace sizes, the pools. Each figure comes with its method and confidence:
     - (a) a published survey or measured drawing (cite it)
     - (b) measured from the plan or ruin footprint (`research/georef/` and OSM ruin polygons; satellite imagery for reading only, never saved into git)
     - (c) read from an engraving by perspective: vanishing lines plus a known module such as a door height or the bay rhythm. Record the scale and the error.
     - (d) estimated from a ruin photo with a known object in it
     - (e) typology (C)

     Agreement and conflict between methods go into `questions.md`.
   - **The materials and colours of the 1780s state:** stone, glazed tiles (the colours in the court paintings and the surviving shards), the shell and floral ornament, the fountains. Sources: Jesuit descriptions and the 西洋楼 tile and stone fragments in museums.
   - **The surviving fragments:** what lies on site, and what was moved and where it is now. For example columns and stones at 北京大学 / 燕园, 中山公园, 颐和园 and elsewhere in Beijing; pieces abroad (Fontainebleau and others); the bronze zodiac heads of the 海晏堂 water clock, factually (which ones survive and where; see the sensitivity rule in `CLAUDE.md`).
   - **The best views** for modellers: the top five pictures, and why.
   - **A wishlist and open questions.**
2. **Sources to hunt** (search in Chinese as much as in English; Getty / BnF / Commons first):
   - **Every impression of the 20 plates:** BnF; the Getty Research Institute (check whether it is Open Content: then a full-resolution download is free); Musée Guimet; Harvard; the Library of Congress; the Staatsbibliothek; the Palace Museum. Record the best free high-resolution copy of each plate (at most 2400 px wide committed, the full size in `research/raw/`), and the differences between impressions.
   - **Yangshi Lei 样式雷 drawings of the Xiyang Lou:** 西洋楼 地盘, 立样, 海晏堂 and 远瀛观 drawings; catalogue numbers and links (research-only).
   - **Measured surveys:**
     - 中国营造学社 in the 1930s (汇刊 articles on 圆明园 / 西洋楼)
     - Tsinghua's measured drawings
     - the park's surveys
     - the archaeology of the 2000s-2010s (远瀛观, 海晏堂, 谐奇趣 and others; reports, 考古 journals, the park's site)
     - modern papers with plans and elevations (the ISPRS 谐奇趣 paper, Virtual Archaeology Review, Heritage Science, Chinese theses on CNKI abstracts)
   - **Jesuit and European texts:** Attiret's letter of 1743 (it describes the Chinese gardens, but check it), Benoist's letters on the fountains, the *Lettres édifiantes et curieuses*, and studies of the European models (Le Pautre, Pozzo, Borromini motifs) by Thiriez (*Barbarian Lens*, 1998: cite, don't copy), Kleutghen and others.
   - **Ruin photos of the Xiyang Lou, all of them, 1860-1949:** Ohlmer 1873 (the full set of about 12 negatives), Child, Thomson, Piry, de Semallé, the 1900-1901 Boxer photos, Sirén, Hedda Morrison, Gamble, Japanese photo books, postcards. Each tied to an id and a façade, with the camera position and bearing.
   - **Modern photos of the ruins on Commons:** one free photo per surviving element and façade at least, licence checked per file.
   - **Rephotography:** pairs of the same view in 1873 and today, wherever both exist. They show what has been lost or moved since.
3. **Fix the inventory:**
   - Identify or merge the unnamed `XY..-N0x`, `-AX` and `-B` parts from the plans and engravings: the octagonal pavilions, wings, water towers and the walls of the 线法 theatre.
   - Correct the wrong sizes, with their sources.
   - Check the parent of XY04-N02.
   - Never renumber existing ids; retire them with a note if needed.
   - Rerun the boxes generator so the 3D view picks up the new sizes, and check the boxes still sit where the ruins are.
4. **Panel:**
   - For XY objects, group the pictures by side ("South façade", "North façade" …, "Roof and fountains", "Ruins today").
   - Add a "Dimensions" block from `dimensions.json`, with method and confidence per figure.
   - The parts inherit their building's dossier under the fallback heading.
   - Keep the other gardens' panels unchanged.
   - The generators stay idempotent.
5. **`research/xiyanglou/README.md`:** the overview. Cover the layout of the strip, the order of building (1747-1783), the water system (the reservoirs of 蓄水楼 and 海晏堂, the pumps), the plates and their viewpoints on a key plan (an image of our own layers with arrows, public-safe), what survives, and the modelling priority with reasons (which building has the best evidence for a first detailed model).
5b. **A public page on the site (Tomasz: "and add to page"):** `site/xiyanglou/index.html` (clean URL `/xiyanglou`), in the homepage's style, with EN text and a zh draft at `site/zh/xiyanglou/index.html`.
   - **Content:**
     - a short intro, then the key plan with the plates' viewpoints
     - one section per building (XY01-XY15): the engraving, the ruin photos then and now (rephotography pairs side by side where they exist), its side-by-side views, the dimension table with method and confidence, what survives, and where the fragments are now
     - each section links to its object in the 3D view (`../reconstruction/3d.html?b=<ID>`)
   - **Copyright:** free images only, credited on the page and in `site/credits.html` and `research/image-credits/CREDITS.md`. Research-only material appears as link cards.
   - **Generated, not hand-written:** a script (`scripts/xiyanglou_page.py`) builds the page from the dossiers, so it stays in step. A second run changes nothing.
   - **Links:** from the homepage (a "The European palaces" section or card, EN and zh), and from the panel of every XY object ("Read the full Xiyang Lou dossier").
   - **Images:** lazy-load them and keep them web-size, because the page must load well on a phone.
   - **Screenshots:** desktop and mobile in `screenshots/r6/`; open them yourself and check them.
6. **Checks and docs:**
   - **Checks:** extend `tools/check_evidence.py` with an XY section (pictures per façade, dimension figures by method), with before and after. Run `scripts/building_pages.py` twice (the second run changes nothing), `tools/check_pages.py` and `tools/check_docs.py`.
   - **Screenshots** in `screenshots/r6/`, from one page load:
     - Tomasz's camera on the Xiyang Lou, before and after the size fixes
     - the panels of 海晏堂, 谐奇趣, 远瀛观 and 大水法, public and private

     Open each one yourself and fix what's wrong.
   - **Docs:** update `CLAUDE.md`, `research/README.md` and `docs/METHOD.md` (method: deep-dive dossiers and dimension sheets, perspective reading of engravings). Copy this brief to `docs/rounds/palace_r6_xiyanglou.md` and add its row to `docs/rounds/README.md`.

## How to work
- **Subagents in the FOREGROUND only:** several Agent calls in ONE message, never `run_in_background`. Never end your turn while a subagent, crawler or background shell still runs.
  - Split them by topic: plates and impressions; surveys, Yangshi Lei and archaeology; ruin photos and rephotography; fragments, Jesuit texts and materials; dimensions (perspective and footprints).
  - Give each one a clock deadline (`date -u`, 40 minutes per wave) and incremental notes in `/opt/data/cache/scratch/palace_r6_notes_<topic>.md`.
  - You alone write the shared repo files.
- **Commons rate-limits this server** (HTTP 429): use API batches of 50, exact-phrase searches, at most one Commons subagent at a time, and back off on Retry-After.
- **Copyright exactly as in `CLAUDE.md`:**
  - Free images are committed at web size.
  - Research-only images go to `research/raw/` and appear as link cards (images on localhost).
  - Figures from modern papers are summarised, or used as images only when the licence is CC BY or CC BY-SA.
- **Tools:** Python from the repo `.venv` via `/opt/data/.local/bin/uv run`. Node and Playwright in `/opt/data/cache/scratch/palace_r6_tools/`.
- **Ports** 8820-8829, bound to 127.0.0.1, stopped at the end. Never use 8790.
- **No git commands that write.** Lily commits.
- **Progress:** one line per milestone, at least every 15 minutes, to `/opt/data/cache/scratch/palace_r6_xiyanglou_progress.md`.
- Mark every claim verified, assumed or unknown. Never invent a link, a licence, a dimension or a date.

## Final message
Lead with what Tomasz gets for the Xiyang Lou:
- the new page (its URL, its sections, how many images)
- pictures per building and per façade, before and after
- how many dimension figures, by method
- the best new finds (three to five)
- which building is best documented and should be modelled first, and why

Then list:
- the sizes you corrected
- what blocked
- what is verified and what is assumed

Do not ask questions. Work only in this repo, plus the scratch paths named above.
