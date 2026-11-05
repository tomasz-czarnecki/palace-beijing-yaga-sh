# palace_r7_scenes: deep research on every scene outside the Xiyang Lou, scene by scene, ready for detailed models

You are working in `/opt/data/workspace/000_Dev/palace-beijing-yaga-sh`, the reconstruction of the Old Summer Palace (圆明园 Yuanmingyuan) before 1860. Read these first:
- `CLAUDE.md` (rulebook: confidence, copyright, layout, rebuild order)
- `docs/METHOD.md` (pitfalls, methods)
- `research/README.md`
- `research/wishlist.md` and `research/questions.md`
- the catalogues: `research/photos/catalog.csv`, `research/evidence/catalog.csv`, `research/reconstructions/catalog.csv`, `research/twins/catalog.csv`
- `scripts/building_pages.py`, `site/reconstruction/panel3d.js`, `tools/check_evidence.py`
- **the model to copy:** the Xiyang Lou round. See `research/xiyanglou/README.md`, one dossier such as `research/xiyanglou/XY08-haiyan-tang/` (README + `dimensions.json`), `scripts/xiyanglou_page.py` and `docs/rounds/palace_r6_xiyanglou.md`.

Everything is committed and pushed (HEAD `6b27915` on `main`). The template project `/opt/data/workspace/000_Dev/kostrzyn-yaga-sh` is read-only: never edit it.

## What Tomasz asked for
"Can you continue research?" The Xiyang Lou now has a dossier and a dimension sheet per building. Everything else (about 1,500 halls in 64 scenes and 111 compounds) mostly shows only its compound's fallback evidence. Do for the rest of the palace what Round 6 did for the Xiyang Lou, in priority order.

## Scope and order (time-boxed: about 25 minutes per scene; breadth first)
1. **Wave 1, the famous scenes:**
   - 九洲清晏 YM03 (the emperor's residence: Nine Continents, 奉三无私, 天地一家春, 圆明园殿 and the rest)
   - 正大光明 YM01 and 勤政亲贤 YM02, with the 大宫门 and 出入贤良门
   - 蓬岛瑶台 (YM32) with 福海 and its islands and shore pavilions
   - 方壶胜境 (YM29)
   - 文源阁 YM46, 舍卫城 YM45, 同乐园 and 买卖街 (the shopping street)
   - 山高水长 YM15
   - 澹泊宁静 (田字房) and 万方安和 (the swastika-plan hall)
   - 杏花春馆, 武陵春色, 平湖秋月, 曲院风荷, 坐石临流 and 接秀山房
   - Look up the exact ids in `research/buildings.csv` before you start; note any mismatch with these names.
2. **Wave 2:** the other Forty Scenes of Yuanming Yuan.
3. **Wave 3, Changchun Yuan:** 含经堂 (the Buddhist complex), 淳化轩, 玉玲珑馆, 思永斋, 海岳开襟, 狮子林, 如园, 鉴园, 映清斋, 宝相寺, 法慧寺, 泽兰堂.
4. **Wave 4, Qichun / Wanchun Yuan:** 绮春园 / 万春园 main compounds: 敷春堂, 鉴碧亭, 涵秋馆, 清夏斋, 正觉寺 (it survives), 大宫门, 迎辉殿, 春泽斋.
5. If time is short, wave 4 and the tail of wave 2 become wishlist rows. Never skip the famous ones to finish the tail.

## Deliverables (per scene and compound)
1. **`research/scenes/<ID>-<slug>/README.md`**, in the Xiyang Lou dossier shape, adapted to a Chinese garden compound:
   - **What it was:** dates, the emperors who used or rebuilt it, function, a short layout (courts, axes, lake edge, hills), and the fate in 1860 and after. Cite every claim.
   - **The scene itself:**
     - the Forty Scenes leaf (1744) with its Qianlong poem and preface, quoted and summarised
     - how later paintings, texts and plans differ: Rixia jiuwen kao (1774+), the 圆明园图咏 (1887), the Yangshi Lei plans, and changes under Jiaqing, Daoguang and Xianfeng
   - **Building by building:** a table of every named hall and gate with plaque name, bays, roof form, number of storeys, orientation, the relation to its neighbours, and the sources for each. Reconcile with `research/buildings.csv`.
   - **Evidence for each hall:** every picture, drawing, plan reading and text that shows it, with ids from the catalogues.
   - **Interior and setting:** the interior (when the Qing inventories or 活计档 / 陈设档 list furniture, paintings, plaques), the garden around it (rocks, trees, water, bridges), the colour scheme and tiles, the plaques and couplets.
   - **What survives today:** foundations, rocks, lakes. Cite the excavation reports (park or 北京市考古研究院), with their findings and links.
   - **Modern reconstructions:** link the ones already in `research/reconstructions/catalog.csv` and add the new ones you find. Say what each says it was built from. **Never use them as a source for sizes or positions.**
   - **The best views** for modellers (top five) and why. **Gaps and a wishlist.**
2. **`dimensions.json` per dossier,** in the Xiyang Lou format: every figure has `value`, `unit`, `method` (published survey / measured on the plan or ruin / read from a painting by module / estimated from a photo / typology), `confidence`, `source` and `error`. Use the Qing module where a source gives it: bays (间) × the 营造尺 of about 0.32 m, purlin counts (檩), and the 举架 roof pitch. Record the scale used.
3. **A drop-in typology check:** after each wave, compare the dossier figures with `research/typology/params.json`. Where the evidence disagrees with the defaults for a hall class, add a question and propose a corrected default with its sources.
4. **Fix the inventory:** merge or name unnamed halls where a plan or text names them, and correct wrong sizes and orientations in `buildings.csv`, with the source. Never renumber ids; retire them with a note.
5. **Panel:** a "Dimensions" block (method and confidence per figure) and a link to the dossier summary for every object in a dossier, as for XY. The halls inherit the scene's dossier under the fallback heading. The generators stay idempotent: a second run changes nothing.
6. **Public pages: only for the ten best-documented scenes.**
   - Generated by `scripts/scenes_page.py`, in the style of `/xiyanglou`, at `site/scenes/<ID>/index.html` plus a hub at `site/scenes/index.html` listing every dossier, with a zh draft at `site/zh/scenes/`.
   - Free images only, credited in `site/credits.html` and `research/image-credits/CREDITS.md`. Research-only material appears as link cards.
   - **Keep the site growth under 30 MB in total**, with web-size lazy-loaded images, and link the hub from the homepage (EN and zh).
7. **`research/scenes/README.md`:** the overview table: every scene and compound with its dossier status, pictures, texts, dimension figures by method, and the modelling priority with reasons (which three scenes should be modelled first after 谐奇趣, and why).
8. **Checks and docs:**
   - **Checks:** extend `tools/check_evidence.py` with a scenes section, before and after. Run `scripts/building_pages.py` twice (the second run changes nothing), `tools/check_pages.py` and `tools/check_docs.py`.
   - **Screenshots** in `screenshots/r7/`, from one page load: the panels for 九洲清晏, 方壶胜境 and 文源阁, a scene page on desktop and mobile, and the hub. Open each one yourself and fix what is wrong. Public pages must show no research-only image.
   - **Docs:** update `CLAUDE.md`, `research/README.md` and `docs/METHOD.md` (what paid off, what blocked). Copy this brief to `docs/rounds/palace_r7_scenes.md` and add its row to `docs/rounds/README.md`.

## Sources to hunt (Chinese as much as English)
- **Texts:**
  - 日下旧闻考 chapters 80-87
  - 圆明园四十景图咏 (the Qianlong poems and prefaces)
  - 国朝宫史续编, 清宫内务府造办处档案总汇 and the 活计档
  - 圆明园 archives (《圆明园——清代档案史料》)
  - 清实录 passages on the gardens
  - Wang Taoxin (Attiret 1743) and the 1860 accounts of the looting (Swinhoe, Loch, Wolseley, Hugo's letter)
- **Plans and drawings:** Yangshi Lei plans per scene (catalogue numbers, links, the facts they give), the 1887 圆明园图咏 woodblocks and the 1744 leaves on Commons and Gallica.
- **Studies and reports:** 郭黛姮's 圆明园 volumes, 贺艳's articles (one per scene), the park's research reports (`yuanmingyuanpark.cn` 研究报告), the archaeology reports, and theses and papers on single scenes.
- **Today's remains:** free Commons photos per scene (the lakes and rocks survive), and reconstructions by others (add to `research/reconstructions/catalog.csv`).
- **Browser-only sources** (Duke, Harvard, Royal BC Museum) that refuse automated access: note them in `research/wishlist.md` and `questions.md`. Do not hammer them.

## How to work
- **Subagents in the FOREGROUND only:** several Agent calls in ONE message, never `run_in_background`. Never end your turn while a subagent, crawler or background shell still runs.
  - Split by wave and topic: texts, plans and drawings, reports, remains and photos, then the merge.
  - Give each one a clock deadline (`date -u`, 40 minutes per wave) and incremental notes in `/opt/data/cache/scratch/palace_r7_notes_<topic>.md`.
  - You alone write the shared repo files.
- **Commons rate-limits this server** (HTTP 429): API batches of 50, exact-phrase searches, at most one Commons subagent at a time, and back off on Retry-After. Be polite to every host: one request at a time, short sleeps.
- **Copyright exactly as in `CLAUDE.md`:** free images are committed at web size, research-only images go to `research/raw/` and appear as link cards (images on localhost). Papers, books and the 郭黛姮 / 贺艳 works are summarised in your own words with a citation.
- **Tools:** Python from the repo `.venv` via `uv run` (`/opt/data/.local/bin/uv`). Node and Playwright in `/opt/data/cache/scratch/palace_r7_tools/`.
- **Ports** 8830-8839, bound to 127.0.0.1, stopped at the end. Never use 8790.
- **No git commands that write.** The chain commits and pushes.
- **Progress:** one line per milestone, at least every 15 minutes, to `/opt/data/cache/scratch/palace_r7_scenes_progress.md`.
- Mark every claim verified, assumed or unknown. Never invent a link, a licence, a dimension, a plaque name or a date.

## Final message
Lead with the numbers, before and after:
- scenes and compounds with a dossier
- halls with their own evidence
- dimension figures by method

Then list:
- the best new finds (three to five)
- the three scenes to model first after 谐奇趣, and why
- the typology defaults you propose to change
- what blocked, and the new wishlist items
- what is verified and what is assumed

Do not ask questions. Work only in this repo, plus the scratch paths named above.
