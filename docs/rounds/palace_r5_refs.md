# palace_r5_refs: more pictures (surviving twins, old photo collections) and other people's reconstructions, for every building

You are working in `/opt/data/workspace/000_Dev/palace-beijing-yaga-sh`, the reconstruction of the Old Summer Palace (圆明园 Yuanmingyuan) before 1860.

Read these first:
- `CLAUDE.md`, the rulebook: confidence, copyright, layout, rebuild order
- `docs/METHOD.md`, especially the pitfalls
- `research/README.md`
- `research/photos/README.md`, plus the head of `research/photos/catalog.csv` and of `research/evidence/catalog.csv`
- `scripts/building_pages.py`, `site/reconstruction/panel3d.js`, `tools/serve_local.py` and `tools/check_evidence.py`

Everything is committed (HEAD `5fbd637`). The template project, `/opt/data/workspace/000_Dev/kostrzyn-yaga-sh`, is read-only: never edit it.

## Why this round
Tomasz looked at the panels: "most of those places are just sketches."

That's expected, and it's the truth of the place:
- No photograph of Yuanmingyuan standing exists. Beato's three "before the burning" prints of 1860 show 清漪园, which the catalogue already records.
- The timber halls burned to their platforms, so the old photos show mostly the stone Xiyang Lou ruins.

Two things can still put more real images on the panels, and he asked for both:
1. **Surviving twins and comparables:**
   - Qing buildings that still stand and were copies of a Yuanmingyuan building, its sisters, or its models.
   - Buildings of the same court, decades and style. Photos of these show what the lost building looked like.
2. **Reconstructions by other people.** He asked: "Would you find reconstructions done by other people? You already have those reconstruction authors, so you will collect them?"
   - **Answer: yes.** Collect them systematically, with author and institution on every one.
   - Round 3 found 32 entries already: `kind=reconstruction` in `research/evidence/catalog.csv`, for example Tsinghua/郭黛姮 via 梦回圆明园 mhymy.com, 贺艳's 再现·圆明园 series, CAFA videos, the ISPRS 谐奇趣 paper, Yan Chen's 万方安和 paper and the park's own studies.

## Deliverables

### A. Twins and comparables
- **A new catalogue,** `research/twins/catalog.csv`: one row per pairing (T001...). Fields:
  - `object_id` (ours), `twin_name_zh`, `twin_name_en`, `twin_place`, `relation`, `evidence_for_relation` (sources), `still_standing` (yes / rebuilt + year / partly), `confidence`, `what_it_tells` (form, roof, bays, setting), `notes`
  - `relation` is one of: copy of (ours copied it), copied from ours, sister (built together, same design), same design family, comparable (same court, era, type)
- **Verify every pairing from a source** before using it. Leads to check, not facts:
  - 文源阁 ↔ 天一阁 (Ningbo, its model) and its sister libraries 文津阁 (Chengde), 文溯阁 (Shenyang), 文渊阁 (Forbidden City)
  - 长春园 狮子林 ↔ 苏州 狮子林, and the Chengde copy 文园狮子林
  - 如园 ↔ 南京 瞻园
  - 安澜园 ↔ 海宁 陈园 (隅园)
  - 小有天园 ↔ 杭州 汪氏小有天园
  - 鉴园 / 茜园 / 思永斋 if sources give models
  - 舍卫城 and 同乐园 against comparable court buildings
  - 方壶胜境 against 承德 and 颐和园 forms
  - 正大光明 against the Forbidden City and Chengde audience halls (澹泊敬诚殿)
  - the Xiyang Lou against European models (the Jesuit designs; Castiglione, Benoist), with care
  - **Same-court comparables:** 避暑山庄 Chengde (same emperors, same decades, 卷棚 and grey tiles), the 颐和园 rebuilt after 1886 (say so: a rebuild, not original), 静宜园 and 静明园 remains, the 宁寿宫花园 (乾隆花园) in the Forbidden City, and 恭王府 and 北海 for garden forms

  A pairing without a source stays out, or goes in as `comparable` with confidence C and its reason.
- **Photos of the twins:**
  - free ones from Commons, licence checked per file, web size: into `research/photos/catalog.csv` with a new field `relation` (`self` for the existing rows, or `twin:T###`)
  - each linked to our object, so the panel shows them under **"Surviving comparable buildings (not this building)"**, with the relation and its source
  - aim for at least one twin or comparable photo for every scene and compound where a sourced relation exists, and a typology comparable for every hall class

### B. More old photographs
Sweep the collections Round 3 only touched:
- Sidney D. Gamble (Duke Digital Repository; record his collection's exact licence terms)
- Hedda Morrison (Harvard-Yenching; check the licence)
- Thomas Child (his full Yuanmingyuan set)
- John Thomson (Wellcome Collection, CC BY)
- Ernst Ohlmer (the full 1873 negatives)
- Japanese photo books of about 1900-1910 (e.g. 小川一真; NDL Digital, check public-domain status)
- Boxer-era photos of 1900-1901 (Library of Congress, the Rijksmuseum, Bundesarchiv on Commons)
- Sirén (tie his 1920s views to their scenes; P0201-P0208 exist)
- 1930s Peking postcards

Tie every photo to the objects it shows, with a camera position and bearing where you can tell them.

### C. Reconstructions by others: collect all of them
- **A new catalogue,** `research/reconstructions/catalog.csv`, R0001...:
  - `author`, `institution`, `year`, `kind` (render, aerial view, video, 3D model, physical model, painting, drawing, AR/VR, paper figure, game or community build)
  - `title`, `link`, `licence` (as stated by the holder), `rights_class` (free / research-only)
  - `shows` (our ids, `sure|likely|guess`), `method_stated` (what the author says they built it from), `local_copy` (path or blank), `notes`
  - Move the 32 existing `reconstruction` rows here; keep their E-ids in a column so no link breaks.
- **Where to look:**
  - 梦回圆明园 mhymy.com: the whole 数字复原 section (about 106 entries tagged 数字复原, 90 tagged 清华) and 复原视频 / fysp
  - Tsinghua 数字圆明园 publications and news
  - 郭黛姮 and 贺艳's books (cite them, don't copy)
  - 紫禁城 magazine's 再现·圆明园 series (one article per scene; list each)
  - the park's site yuanmingyuanpark.cn (研究报告)
  - CAFA (中央美术学院)
  - the Shougang 2020 exhibition
  - the AR app 重返圆明园
  - the 2006 documentary 圆明园 (金铁木) and its CGI
  - CCTV and BBC programmes
  - Bilibili and YouTube (record the uploader and whether it's the author)
  - Sketchfab (search 圆明园, Yuanmingyuan, Old Summer Palace, Haiyantang, Xieqiqu, Dashuifa)
  - Commons renders uploaded by their authors
  - open-access papers (ISPRS Annals, Virtual Archaeology Review, Heritage Science, MDPI…) and theses
  - physical scale models (the park's exhibition hall 圆明园沙盘 and others)
  - community builds (Minecraft and others: record them, low weight)
- **Local research copies:** for every reconstruction image or video frame that is reachable, save one web-size research copy (at most 1600 px, about 300 KB) to `research/raw/reconstructions/R####.jpg` (gitignored). For a video, a few key frames are fine, with the timestamp in `notes`. Polite downloading: one request at a time per host, a sleep in between, stop on 429.
- **Free reconstructions** go into the site with a credit, exactly like free photos. These are images whose licence is CC0, CC BY or CC BY-SA, read on the holder's page: open-access paper figures under CC BY, Sketchfab models or renders under CC BY, Commons uploads.
- **Everything else is research-only:**
  - **On the public site:** a link card with author, institution, year, what it shows, and "View at <site>".
  - **On localhost:** in private mode, `tools/serve_local.py` serves the local copy under `/_local/`, the same mechanism Round 3 uses for research photos, labelled "research copy, not public".
  - **Never** copy a research-only file under `site/`, and never hotlink it.

### D. Panel and pages
- Extend `scripts/building_pages.py` and `panel3d.js` so each panel shows, in this order:
  1. Period evidence (as now)
  2. **Reconstructions by others:** separate, labelled "modern interpretation, not evidence", with author and year, free images shown, the rest as link cards (or images on localhost)
  3. **Surviving comparable buildings (not this building)**
  4. The set-of-buildings fallback
- A hall inherits its compound's reconstructions and twins under the fallback heading, the same way as the evidence.
- The generators stay idempotent: a second run changes nothing.
- **Never use a reconstruction or a twin as a source for positions or sizes in `buildings.csv`.** They're B or C interpretations, recorded in `questions.md` where they disagree with the period evidence. Where a reconstruction states a dimension from Yangshi Lei drawings, record it as a lead with that citation, confidence B, and only in a new column `size_lead`.

### E. Checks and docs
- **`tools/check_evidence.py`:**
  - new counts: objects with a reconstruction (own or inherited), with a twin or comparable photo, and with a free image of any kind
  - before and after, for the top-level objects and for the halls
  - asserts that no research-only file is under `site/`, and that every `R`/`T` row has a link and a licence
- **Generators:** run `scripts/building_pages.py` twice (the second run changes nothing), `tools/check_pages.py`, then `tools/check_docs.py` (fix the docs it flags).
- **Screenshots** in `screenshots/r5/`, from one page load, panels open for 九洲清晏 YM03, 文源阁, 狮子林 (Changchun Yuan), 海晏堂 and 正大光明. Two each: `?public=1` and the localhost private view. Open each one yourself and fix what's wrong.
- **Docs:** update `CLAUDE.md`, `research/README.md` and `docs/METHOD.md` with the twins, the reconstruction catalogue, the panel order and what you learned (sources that paid off, sites that blocked). Copy this brief to `docs/rounds/palace_r5_refs.md` and add its row to `docs/rounds/README.md`.

## How to work
- **Subagents in the FOREGROUND only:** several Agent calls in ONE message, never `run_in_background`. Never end your turn while a subagent, crawler or background shell still runs.
  - Split by A, B and C, with C in two or three parts: mhymy and Tsinghua; video and Sketchfab; papers and the rest.
  - Give each subagent a clock deadline (`date -u`, 40 minutes per wave) and have it write its notes incrementally to `/opt/data/cache/scratch/palace_r5_notes_<topic>.md`.
  - You alone write the shared repo files.
- **Commons rate-limits this server** (HTTP 429 in Round 3). Use the API generators with `prop=imageinfo` and batches of 50, exact-phrase searches, at most one Commons subagent at a time, and back off on Retry-After.
- **Search in Chinese as much as in English.**
- **Tools:** Python from the repo `.venv` via `/opt/data/.local/bin/uv run`. Node and Playwright in `/opt/data/cache/scratch/palace_r5_tools/`.
- **Ports** 8810-8819, bound to 127.0.0.1, stopped at the end. Never use 8790.
- **No git commands that write.** Lily commits.
- **Progress:** one line per milestone, at least every 15 minutes, to `/opt/data/cache/scratch/palace_r5_refs_progress.md`.
- Mark every claim verified, assumed or unknown. Never invent a link, a licence, an author or a date.

## Final message
Lead with the numbers from `check_evidence.py`, before and after:
- objects with a free image
- objects with a reconstruction
- objects with a twin

Then list:
- how many reconstructions were collected, by author and institution, and how many are free to show
- the best twins found
- what blocked
- what is verified and what is assumed

Do not ask questions. Work only in this repo, plus the scratch paths named above.
