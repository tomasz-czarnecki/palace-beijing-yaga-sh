# Yuanmingyuan 圆明园 (Old Summer Palace), Beijing: 3D Reconstruction

## Goal

Rebuild the Old Summer Palace, the Qing imperial garden-palace north-west of Beijing, as it stood before October 1860, when French and British troops looted it and British troops, on Elgin's order, burned it. The result is a map and a 3D model that people can walk through in the browser.
The complex is three gardens: Yuanming Yuan 圆明园, Changchun Yuan 长春园 (with the European palaces, Xiyang Lou 西洋楼) and Qichun Yuan 绮春园 (later Wanchun Yuan 万春园).

**Sister project and template:** `/opt/data/workspace/000_Dev/kostrzyn-yaga-sh` (Küstrin c. 1913). Same structure, same research rules, same management of buildings. Read its `CLAUDE.md`, `research/README.md`, `research/sources.md`, `research/questions.md` and `research/buildings.csv` to see how a thing was done there. **Never edit that repo.**

**Read next:**
- `research/README.md`: every file, field, id scheme and catalogue, and the full rebuild order.
- `docs/METHOD.md`: the reusable playbook for the next historical site.
- `docs/rounds/README.md`: what each round was asked, what it delivered and what went wrong; the briefs beside it.
- `research/questions.md`: open points. `research/wishlist.md`: what would replace the biggest guesses.

## Status

Started 2026-10-31. Round 1 done: base plan S01 georeferenced, `research/buildings.csv` and `research/layers/*_1860` built, rebuild order in `research/README.md`, open points in `research/questions.md`. Round 2 done: the 2D dev map and every building as a box in a 3D preview (`site/reconstruction/`), one page per building. Round 3 done: pictures, drawings and texts for every object, shown in the panel (`research/evidence/`, `research/photos/`, `tools/check_evidence.py`). Round 4 done: this rulebook, `research/README.md`, `docs/`. Round 5 done: surviving twins and comparables, more old photographs, reconstructions by other people, all in the panel (`research/twins/`, `research/reconstructions/`). Round 6 done: the Xiyang Lou in depth, a dossier and dimension sheet per main building (`research/xiyanglou/`), corrected boxes, pictures by side in the panel, and a public page (`site/xiyanglou/`). Round 7 done: every other scene and compound the same way, 81 dossiers with dimension sheets (`research/scenes/`), the Dimensions block and dossier link in their panels, a hub and ten public scene pages (`site/scenes/`). Round 8 done: a blind check set of 22 points frozen before any fit (`research/georef/check_points.json`); the placement, honestly: median 19.7 m, 90% within 38.7 m, worst 46 m, foundations in place 2-8 m, re-dug shores 14-46 m; a refit region by region that gained under 0.4 m anywhere, YM west and east keeping the Round 1 fit; the Xiyang Lou walls off the ruins (Q64) and 大水法's court sunk (Q71); a placement-accuracy layer on the dev map. Next: detailed models, 谐奇趣 XY01 first (`research/xiyanglou/README.md`), then 正大光明 YM01 with 大宫门, 含经堂 CC02 and the axis of 九洲清晏 YM03 (`research/scenes/README.md`); at 九洲清晏, S01 and the Tongzhi plans carry names of 1873 (Q36): model from the 1855 sheets where they can be read. Homepage: a simple page (EN, zh draft) that leads to the 3D view, the Xiyang Lou page and the scene hub.

Decided:
- **Target state:** the gardens just before the destruction of October 1860 (Xianfeng reign). Earlier evidence (the Forty Scenes album of 1744, the Xiyang Lou engravings of the 1780s) counts for that state wherever nothing later contradicts it. Q1 in `research/questions.md` tracks this.
- **Purpose:** a showcase of the skill and the project, not a one-to-one reconstruction. Approx is OK where evidence is missing: guess, mark it C with a one-line reason, move on. Time-box research at about 30 min per object and write a wishlist of what would replace the biggest guesses.

## The place

- **Where:** the plain north-west of old Beijing, in Haidian, between Haidian town and the Western Hills (S02). Centre about 40.008 N, 116.300 E. Today a ruin park (S03).
- **Size:** the wall rings on the plan enclose 335 ha (run), against 331–350 ha stated (S145, S146, S147). Yuan Ming Yuan 183 ha, Changchun Yuan 69 ha, Qichun Yuan 78 ha (run). About 116 ha of it is water (run, S01).
- **Yuan Ming Yuan 圆明园, "Garden of Perfect Brightness":** the 大宫门 Da Gongmen and the audience hall 正大光明 Zhengda Guangming on the south axis (S05, S02). Behind them the nine islands round the 后湖 Back Lake, the core, with the emperor's apartments on 九洲清晏 Jiuzhou Qingyan (S02). To the east the near-square 福海 Fuhai, "Sea of Blessings", 26–28 ha (runs, S01, S03), with 蓬岛瑶台 Pengdao Yaotai on its islets (S05). The Forty Scenes are named from here (S05, S08).
- **Changchun Yuan 长春园, "Garden of Long Spring":** lakes around 含经堂 Hanjing Tang (S05, S143). The Xiyang Lou 西洋楼, the European palaces, stand in a strip along its north edge, 860 m long (S149), built under Castiglione and Benoist (S02).
- **Qichun Yuan 绮春园,** later 万春园 Wanchun Yuan: small gardens merged (S49, S06). Its 正觉寺 Zhengjue Si is the only building that survives (S145).
- **Building:** mostly grey tile and rolled ridges 卷棚, unlike the Forbidden City, with glazed exceptions such as 安佑宫 Anyou Gong and 方壶胜境 Fanghu Shengjing (S08, S06, S122). Sampled on two album leaves in Round 1 (`research/typology/halls.md`); Round 7 read all forty leaves hall by hall (`research/scenes/halls.csv`): glazed roofs at 蓬岛瑶台, 方壶胜境, 安佑宫, 广育宫 and the front hall of 镂月开云, grey tile elsewhere.
- **Evidence:** S01 is Malone's "Official Map" or his tracing of it (S02 pp.231–232): every hall, by bays, in a state of about Daoguang to Xianfeng (Q2, Q3), except 九洲清晏, whose labels are of 1873 or later (Q36). It is the base for positions and footprints. The map reads to about ±10–20 m in Changchun Yuan and on the Xiyang Lou, ±30–40 m around the lakes and in Qichun Yuan, ±75 m in the west (Q7).
- **Today:** farmland and digging removed most hills and filled most water from the 1940s to the 1970s (S145). Lakes re-dug and lined; 福海 and 后湖 keep their shape (S146, S148).

## Timeline

- 1707–09: Kangxi grants the land to Prince Yinzhen, the later Yongzheng (S06, S42, S05, S02; Q21).
- 1725: Yongzheng builds the audience hall and offices on the south side (S05, S02).
- 1737: painted map of the garden by Castiglione and five others, lost (S02 p.62).
- 1744: the Forty Scenes named and painted (S05, S02). Album in the BnF since 1862 (S02).
- c. 1745–51: Changchun Yuan built (S45, S02; Q22). From 1747 the Xiyang Lou, until 1783 with 远瀛观 Yuanying Guan (S02, S42; Q24). The 20 engravings by 1786 (S02, S56).
- 1770–74: Qichun Yuan joins the gardens (S49, S06, S02; Q23). 1774: 文源阁 Wenyuan Ge (S05).
- 1793: Macartney's gifts stand in 正大光明殿 (S02).
- 1809–17: Qichun rebuilt at full size (S49, S47). 1831: 慎德堂 Shende Tang (S41). 1836: fire on the 九洲清晏 axis (S41). 1855: last dated addition found, 同道堂 Tongdao Tang's theatre (S43).
- 1860, 6–8 October: French and British troops take the gardens, and they are looted (S02 pp.179–183). 18–19 October: burned on Elgin's order by British troops under Michel; the French refuse to join (S02 pp.187–188).
- 1873: Tongzhi's repair stops (S02, S06).
- 1900: further damage; who did it is disputed (S06, S07; Q28).
- Republic: the ruin is used as a quarry for rock and brick (S02 p.218, S06).
- 1950s–70s: farmland and further removal; over 200 hills dug 1967–73 (S145).
- 1976: management office. 1988: national protected site, park opens (S06, S54).

## Research rules

- **Nothing goes into the model without a source.** Every source has an ID (S01, S02, ...) in `research/sources.md`. Every row in a CSV or GeoJSON file cites its source IDs (`S03;S12`).
- **Confidence:**
  - A = shown on a source made while the gardens stood (Qing site plans, Yangshi Lei 样式雷 drawings, the Forty Scenes, the Xiyang Lou engravings, pre-1860 texts), or measured on remains that survive unchanged (lake shores, ruins in place).
  - B = a later source (photos of the ruins after 1860, 20th-century surveys, modern scholarly reconstructions), or a written description only.
  - C = inferred (typology, symmetry, a guess). Every guess is C.
  - S01 counts as B, not A, until Q2 is settled, so no position is A today. How the grades apply to rows: `research/README.md`.
- **Evidence order:** Qing site plans win on positions and footprints. Paintings and engravings give forms, roofs, trees and bridges. Today's lakes, islands and hills anchor the georeferencing, because much of the landscape survives. Modern reconstructions (Tsinghua's Digital Yuanmingyuan and others) are B: cite their facts, never copy their images.
- **Source status:** found → viewed → downloaded (copy in `research/raw/`); also to-request (offline, must be ordered) and blocked (site refused automated access).
- **Numbers come from runs.** Every figure (areas, widths, heights, RMS) comes from a script run on the repo data.
- Online sources only for now; books and archive items are recorded as to-request.

## Research

All evidence lives in `research/` (conventions in `research/README.md`).
- **Working map:** `site/reconstruction/index.html` + `app.js`, Leaflet vendored. A development preview (`noindex`), reached only from the small DEV MAP button in the 3D view. Run with the `site` entry in `.claude/launch.json` (`tools/serve_local.py`, port 8796): on localhost it also offers the plan S01 under `/_local/`; `?public=1` shows what a visitor sees. The preview on :8790 has no overlay.
- **Placement (Round 8):** `research/georef/`: the fit in use `princeton-1920s.json`, the Round 1 fit kept as `princeton-1920s.previous.json`, the blind check set `check_points.json` (frozen by hash: never edit it; a doubt goes in `annotations`), control points `princeton-1920s.csv` (Round 1), `control_r8.csv` (read by eye, from `readings_r8/` by `scripts/georef_readings.py`), `control_shapes.csv` (lakes and Xiyang Lou ruins, `scripts/control_derived.py`). `scripts/georef.py fit` keeps the previous fit in any region where the new one does worse on the check set. `tools/check_georef.py` fails if the check set changes, a region's median gets worse than `check_baseline.json`, or the rows don't follow the fit; after a deliberate refit run it with `--write-baseline`. The readers' crop tool: `tools/georef_crops.py` (tiles and crops in scratch only). What moved: `tools/georef_shift.py`; shores and walls against today's: `tools/shore_check.py`, `tools/wall_check.py`. The accuracy layer `research/layers/georef_error.geojson` (`scripts/georef.py accuracy`), public, on the dev map as "Placement accuracy".
- **Boxes:** `scripts/boxes1860.py` writes `data/halls_1860.geojson`, one feature per box. `basis` says what it stands on; `assumed: true` is a guess, C. Ground: `scripts/ground1860.py`, levels from today's ground, not a survey of 1860. Q34, Q35.
- **3D view:** `site/reconstruction/3d.html`, `3d.js`, `halls3d.js`, `panel3d.js`, three.js vendored, the way in. A preview: it does not decide the final engine. URL: `?b=<ID>` opens that page and frames its object, `?shot=1` hides the panels and animates nothing, `?conf=1` colours by confidence.
- **Others' work:** `research/twins/catalog.csv` (T..: standing buildings that are copies, sisters, models or comparables, with the relation's source and grade) and `research/reconstructions/catalog.csv` (R..: author, institution, year, method). **Never a source for a position or a size.** A dimension one states goes only in the column `size_lead` of `research/buildings.csv`, through `research/evidence/facts.csv`, grade B. Disagreements go in `research/questions.md`. In the panel they stand after the period evidence and before the set of buildings, labelled modern interpretation, not evidence, and not this building.
- **Evidence:** pictures in `research/photos/catalog.csv` (web copies in `site/reconstruction/photos/`, by `scripts/photos_catalog.py`), texts, drawings and reports in `research/evidence/catalog.csv`, facts for the rows in `research/evidence/facts.csv` (`scripts/apply_facts.py`). `tools/check_evidence.py` counts coverage, before and after Round 5, and fails on an empty panel, a research-only image on the site, or an R or T row with no link or licence.
- **Building pages:** `research/buildings/<ID>-<slug>/index.md`, one per row of `buildings.csv` and per gate; list in `research/buildings/README.md`. `scripts/building_pages.py` writes the block between the markers, `data/buildings/<ID>.json` (public; `GARDEN-*.json` what speaks for a garden) and `research/raw/buildings/<ID>.json` (local, with the plan readers' notes, the plan crop and research-only copies). **To edit:** write under `## Notes`, then run the script; it never touches that part. Notes go on the public site, except what stands below a line holding only `%% private %%`. `tools/check_pages.py` proves every clickable object has a page.
- **Xiyang Lou:** `research/xiyanglou/README.md` is the overview. Per building `research/xiyanglou/<ID>-<slug>/README.md` and `dimensions.json`, written by `scripts/xiyanglou_dossiers.py` from the hand-edited sheets beside them: `views.csv` (each picture's side), `dimensions.csv` (every figure, method a survey, b ruin or plan, c engraving by perspective, d photograph, e typology), `boxes.csv` (what the 3D boxes take, read by `scripts/boxes1860.py`), `parts.csv`, `materials.csv`, `fragments.csv`, `rephoto.csv`, `impressions.csv`, `about.json` (the text, EN and a zh draft). The panel heads XY pictures by side and adds a Dimensions block; other gardens' panels are untouched. Stone positions today are not evidence for 1860 (S821, Q75).
- **The page:** `site/xiyanglou/index.html`, `site/zh/xiyanglou/index.html` (clean URL `/xiyanglou`), generated by `scripts/xiyanglou_page.py`, never hand-edited. After changing its Chinese text, run `tools/font_subset.py <repo> xy` from a folder holding the full Noto files (`site/xiyanglou/fonts.css`, `noto-*-sc-xy.woff2`).
- **Scenes (Round 7):** `research/scenes/README.md` is the overview, with the modelling priority and the typology check. Per scene `research/scenes/<ID>-<slug>/README.md` and `dimensions.json`, written by `scripts/scenes_dossiers.py` from the hand-edited sheets beside them: `about.json` (the text, EN, and zh drafts for the public scenes; `public` marks the ten with a page), `halls.csv` (each hall as a source states it), `dimensions.csv` (methods a to e as for the Xiyang Lou, c read from a painting by module, with the scale used; 1 营造尺 = 0.32 m), `views.csv`, `best.csv`, `digs.csv`, `interior.csv`, `parts.csv` (read by `scripts/boxes1860.py`), `checks.csv` (the sentence check of the public text). The script also measures each scene's outline, islands and water on the traced layers (method b, `run`). A figure from a plan of the Tongzhi repair (1873-74) is B for 1860, never A.
- **The scene pages:** `site/scenes/index.html` (the hub: every dossier, the panel links to its anchors), `site/scenes/<ID>/index.html` for the public ones, `site/zh/scenes/`, generated by `scripts/scenes_page.py`, never hand-edited. After changing their Chinese text, run `tools/font_subset.py <repo> scenes` from a folder holding the full Noto files (`site/scenes/fonts.css`, `noto-*-sc-scenes.woff2`).
- **Detailed models:** next, `models/<ID>-<slug>/summary.json`, see `models/README.md`. No model and no publishing step exist yet.

## Pipeline and rebuild order

Run from the repo root with `uv run python <script>`. Fields, inputs and outputs of each step: `research/README.md`.

1. **Fetch and stitch (needs `research/raw/`):** `scripts/fetch_osm.py` (network), `scripts/clip_dem.py`, `scripts/mosaic_plan.py` (the four images from the museum's IIIF server, `https://media.artmuseum.princeton.edu/iiif/3/collection/PUAMANX23_6398` and `_6397`, `_6395`, `_6391`, `/full/max/0/default.jpg`).
2. **Read the plan and place it:** `scripts/trace_plan.py`; `scripts/georef.py previous`, `scripts/georef_readings.py`, `scripts/control_derived.py`, `scripts/georef.py` (`fit` by default; `freeze` once, `accuracy`, `overlay` and `images` as separate commands).
3. **Typology:** `scripts/typology_rules.py`, `scripts/typology_scale_check.py`.
4. **Inventory and layers:** `scripts/build_r1.py`, then `scripts/apply_facts.py`.
5. **Review images:** `scripts/render_r1.py`, `scripts/coverage_chart.py`.
6. **Public data:** `scripts/georef.py accuracy`, `scripts/publish_layers.py`, `scripts/ground1860.py`, `scripts/boxes1860.py`, `scripts/photos_catalog.py`, `tools/plan_crops.py` (local only), `scripts/xiyanglou_dossiers.py`, `scripts/scenes_dossiers.py`, `scripts/building_pages.py`, `scripts/xiyanglou_page.py`, `scripts/scenes_page.py`.
7. **Checks:** `tools/check_pages.py`, `tools/check_evidence.py`, `tools/check_docs.py`, `tools/check_georef.py`. Each exits non-zero on a failure.

`scripts/scene1860.py` is imported, not run. After a change to `buildings.csv`, `layers/`, `typology/params.json`, `research/xiyanglou/`, `research/scenes/` or a catalogue, rerun step 6 and step 7; they take seconds. After a change to `research/evidence/facts.csv`, rerun `scripts/build_r1.py` and `scripts/apply_facts.py` first, so the rows start clean. Never edit generated rows: `buildings.csv` comes from `scripts/build_r1.py` plus `research/evidence/facts.csv`, which can `correct` a figure. `research/photos/catalog.csv`, `research/evidence/catalog.csv`, `research/twins/catalog.csv` and `research/reconstructions/catalog.csv` are edited by hand.

## Public and private

| What | In git | On the site |
|---|---|---|
| `site/` | yes | yes, only this folder is served |
| Geometry traced from S01 (`*_1860`), with credit | yes | yes (Q6) |
| The plan S01 as an image, `research/overlays/`, `research/raw/` | no | never (localhost only, `/_local/`) |
| Free pictures and reconstructions | `research/photos/images/`, `research/reconstructions/images/` | smaller copies, through `scripts/photos_catalog.py` only |
| Research-only pictures, reconstructions and texts | no copy; `research/raw/photos/`, `research/raw/reconstructions/` locally | link card only; on localhost the local copy, marked |
| `research/` otherwise, `scripts/`, `tools/`, `docs/`, `models/`, this file | yes | no |

Rights calls still waiting for Tomasz: Q6 (plan image), Q50 (Malone quotes, Sirén, Skušek, pre-1900 photographs), Q55 (the Hengdian photographs, CC BY figures of the Tsinghua teams, Licence Ouverte postcards), Q77 (the Rylands set of the plates, CC BY-NC, the best scan and the only period colour image).

## Ports and processes

| Port | What |
|---|---|
| 8790 | preview of `site/`, `/opt/data/scripts/palace_preview_server.py`, forwarded by Tomasz. No overlay. Never for workers |
| 8796 | `tools/serve_local.py`, the `site` entry in `.claude/launch.json`: with `/_local/`; `--public` turns it off |
| own port | anything else a worker starts; stop it before ending the turn. Rounds used 8797, 8800–8809, 8810–8819, 8820–8829, 8830–8839 and 8840–8849 |

Markers and chains live outside the repo: `/opt/data/scripts/rounds_palace/<name>.done`, `/opt/data/scripts/palace_r*_chain*.sh`. Logs: `/opt/data/cache/scratch/<name>.jsonl`, `<name>_progress.md`. Scratch may be cleared, so nothing of value stays only there.

## Copyright

- **Free** (may be committed and published, credited): public domain, CC0, CC BY, CC BY-SA, with the licence checked on the holder's page. PD-Art reproductions of pre-1900 two-dimensional works on Wikimedia Commons count as public domain.
- **BnF / Gallica:** reuse is free for non-commercial purposes with the credit "Source gallica.bnf.fr / BnF"; commercial use needs a licence. Publishable only with that credit, and the project stays non-commercial (open question for Tomasz).
- **Research-only:** everything else. That covers Yangshi Lei scans from the National Library of China, the Palace Museum or books; modern maps and plans; Tsinghua renders; figures from papers; and photos with an unclear licence.
  - Keep them in `research/raw/`, never commit them, never show them on the site.
  - The site shows them only as a link card ("View at ..."). Their facts can be used with a citation.
- **Basemap and satellite tiles** (Esri, Google, Bing, Amap, Baidu, Tianditu) are never saved into git. They are used only as a dev-map basemap, under the provider's terms.
- **OpenStreetMap** data needs ODbL attribution.

## Coordinates

- Store everything in WGS84 (EPSG:4326) in GeoJSON. Do metric work in UTM zone 50N (EPSG:32650).
- **Chinese map services use shifted datums.** Amap/Gaode, Tencent, and Google's road tiles inside China use GCJ-02, offset by a few hundred metres. Baidu uses BD-09.
  - Never mix them with WGS84 without converting.
  - Record the datum of every control point.
  - OSM and Esri World Imagery are WGS84 (check them against each other).

## Layout (mirrors kostrzyn-yaga-sh)

```
site/                     the public website, the only thing a host serves (Root Directory = site, static, no build)
  index.html, zh/, credits.html, styles.css, main.js, assets/
  xiyanglou/              index.html, keyplan.svg, fonts.css: the European palaces, generated; zh/xiyanglou/ its Chinese draft
  scenes/                 index.html (the hub), <ID>/index.html (ten public scenes), keyplan.svg, fonts.css: generated; zh/scenes/ the Chinese drafts
  reconstruction/         index.html (2D dev map, Leaflet), 3d.html (three.js preview, the way in), data/ (public layers, buildings/ = panel pages), generated/ (ground, walls and bridges), photos/ (free pictures), vendor/
research/                 README.md, sources.md, questions.md, wishlist.md, buildings.csv, buildings/ (one page per building), layers/ (GeoJSON working copies),
                          plan/ (what was read off S01), georef/ (control points, the blind check set, the fits), photos/ (catalog.csv), evidence/ (catalog.csv, facts.csv), twins/ (catalog.csv), reconstructions/ (catalog.csv, images/), xiyanglou/ (the European palaces: dossiers, sheets), scenes/ (every other scene: dossiers, sheets), typology/, terrain/, image-credits/CREDITS.md, raw/ and overlays/ (gitignored)
scripts/                  the Python pipeline (uv, pyproject.toml); writes into research/ and site/reconstruction/data/
tools/                    serve_local.py (local preview with the private layers under /_local/), plan_crops.py, check_pages.py, check_evidence.py, check_docs.py
docs/                     METHOD.md (the playbook), rounds/ (briefs and what each round did); never public
screenshots/              review images, gitignored
models/                   later: detailed models, one folder per building (models/<ID>-<slug>/summary.json), as in Küstrin
```

- Nothing under `site/` may reference a file outside `site/`. No `package.json`, no Python and no folder named `public` under `site/`.
- Links inside `site/` must work on a plain static server too (`reconstruction/3d.html`, `credits.html`, `zh/`, `xiyanglou/`, `scenes/`). From a folder's index.html, start every link with `../`, which holds with or without the trailing slash.
- **Never public:** `research/raw/`, `research/overlays/`, `scripts/`, `docs/`, this file.

## Website and git

- Preview on this server: port 8790 serves `site/` (Tomasz forwards it in VS Code). Workers use their own ports, never 8790.
- No GitHub remote and no Vercel project yet. Never push. Workers never commit; Lily makes the commits.

## Working rules

- **Keep history accurate and respectful.** The destruction of 1860 is a national wound in China. State it factually (who, when, what). No sensational or cute framing, and the twelve zodiac heads stay out of any playful content.
- **Names:** Chinese characters and pinyin first, then the English translation (正大光明 Zhengda Guangming, "Upright and Bright").
- **Work order:** garden walls, water, islands and hills first; then the scenic compounds; then single halls.
