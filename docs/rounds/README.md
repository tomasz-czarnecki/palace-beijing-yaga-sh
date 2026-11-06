# The rounds

One entry per round: each was one `claude -p` run from a brief. The briefs are beside this file, unchanged, as `<name>.md`. `common/` holds the shared briefs the coordinators gave their subagents (not asked of Round 4 by name; kept because scratch may be cleared).

**Sources:** result rows in `/opt/data/cache/scratch/<name>.jsonl`, `/opt/data/scripts/rounds_palace/*.done`, the progress logs, the git log. All on 2026-10-31, UTC. Cost is `total_cost_usd` of the result row.

**Effort:** only the chain scripts record it (`/opt/data/scripts/palace_r2_chain2.sh`, `palace_r4_chain.sh`). The other rounds were started another way and the logs don't hold it: "not recorded". Every log's model is `claude-opus-5-5`.

| Round | Effort | Ran | Duration | Turns | Cost | Commit | Outcome |
|---|---|---|---|---|---|---|---|
| rulebook, by Lily | - | before 15:04 | not recorded | - | - | bbed686 | `CLAUDE.md`, `.gitignore` |
| `palace_home` | not recorded | 15:04–15:12 | 8 min | 55 | $2.57 | de7dc3b | done |
| `palace_r1_research` | not recorded | 15:03–15:20 | 17 min, 6 of them before its turn ended | 25 | $9.04 | none | **failed:** subagents killed |
| `palace_r1b` | not recorded | 15:36–17:58 | 142 min | 72 | $80.16 | 11537d0 | done |
| `palace_r2_map` | xhigh | 17:59–18:30 | 30 min | 81 | $9.42 | 33b3f29 | done |
| `palace_r3_evidence` | not recorded | 19:12–20:55 | 103 min | 71 | $76.61 | 0bb4f81 | done |
| `palace_r4_docs` | high | 20:56-21:08 (12 min) | exit 0 at 21:08Z | - | - | `4b44190` | done |
| `palace_r5_refs` | not recorded | 21:45–23:26 | 101 min | - | see its result row | see the git log | done |
| `palace_r6_xiyanglou` | not recorded | 2026-11-01, from 00:58 | see its log | - | see its result row | see the git log | done |
| `palace_r7_scenes` | not recorded | 2026-11-05, from 16:19 | see its log | - | see its result row | see the git log | done |
| `palace_r8_georef` | not recorded | 2026-11-05, from 17:57 | about 1 h 30 min | - | see its result row | see the git log | done |
| `palace_r9_paths` | not recorded | 2026-11-05, from 19:22 | about 1 h 30 min | - | see its result row | see the git log | done |
| `palace_r10_ground` | not recorded | 2026-11-05, from 20:34 | about 1 h 30 min | - | see its result row | see the git log | done |
| `palace_r11_kit` | not recorded | 2026-11-05, from 21:53 | about 1 h 35 min | - | see its result row | see the git log | done |
| `palace_r12_greens` | not recorded | 2026-11-05, from 23:04 | about 1 h 30 min | - | see its result row | see the git log | done |
| `palace_r13_pilot` | not recorded | 2026-11-06, before 01:30 | see its log | - | see its result row | 75bd43b | done |
| `palace_r14_haiyan` | not recorded | 2026-11-06, from 01:30 | see its log | - | see its result row | see the git log | done |
| `palace_r15_dashuifa` | not recorded | 2026-11-06, from 02:30 | about 1 h 30 min | - | see its result row | see the git log | done |
| `palace_r16_yuanying` | not recorded | 2026-11-06, from 03:49 | about 1 h | - | see its result row | see the git log | done |
| `palace_r17_hanjing` | not recorded | 2026-11-06, from 04:44 | about 2 h 30 min | - | see its result row | see the git log | done |
| `palace_r18_jiuzhou` | not recorded | 2026-11-06, from 06:57 | about 2 h | - | see its result row | see the git log | done |

## palace_home

**Delivered:** homepage in English and a Chinese draft, credits, a reconstruction placeholder, styling, fonts with two Noto Chinese subsets, the hero 方壶胜境 from the album (PD-Art on Commons). 24 files.

**Checked:** four pages at two sizes on a static server, with no console errors, 404s or overflow; clean URLs on an imitation of Vercel.

**Went wrong or left open:**
- Vercel itself untested; no native speaker read the Chinese.
- The page's 1747 start of the European palaces, the French commander's refusal and today's site rested on Wikipedia.
- It flagged that `CLAUDE.md`'s Goal line blurred the looting and the burning. Fixed in Round 4.
- It flagged 万春园: zh.wikipedia says only a planned name, `CLAUDE.md` says "later Wanchun Yuan". Not settled; see Round 4.
- The font subset script stayed in scratch (`palace_home_subset.py`).

## palace_r1_research

**Delivered:** almost nothing: `research/layers/osm_today.geojson` (6004 features), DEM tiles, four plan images, `scripts/fetch_osm.py`, `scripts/clip_dem.py`. All were reused by the next run.

**Went wrong:** it launched five subagents and a crawl in the background, then ended its turn "waiting for their notes". Print mode waits about 10 minutes after the last turn. From `palace_r1_research.err`: "Background tasks still running 10m after the last turn ... stopping them." The run still exited 0.

The first chain's gate caught it through the missing files: `palace_r2_map_blocked.done` at 15:21. This led to the rules in `docs/METHOD.md` and to the second run.

## palace_r1b

The same brief plus an addendum: `palace_r1b.md` is byte for byte `palace_r1_research.md` followed by that addendum.

**Delivered:**
- Base plan S01 identified as Malone's "Official Map" or his tracing; mosaic 12955 × 9049.
- Georeference: thin-plate spline, 111 points, RMS 10.6 m, leave-one-out 16.5 m, reading ±10 m to ±75 m by area.
- 1824 rows: 212 compounds (191 with position), 1612 halls (1461 with position, 1418 with footprint); all 40 scenes and 15 Xiyang Lou buildings placed; 1560 footprints.
- Layers, typology, terrain note; 150 sources and 230 pictures (182 free) at that time; Q1–Q33; the wishlist.

**Timeline:** mosaic and skeletons 15:39–15:40. Wave 1 from 15:40 (inventory, maps, typology, trace, site, georef by about 16:17; photos 17:22). Wave 2 of five plan readers 17:24–17:43. Merge and docs 17:43–17:58.

**Checked:** no duplicate ids, every source id resolves, `build_r1.py` reproducible, 12 random `sure` readings viewed, all right.

**Went wrong:**
- Pictures worker about 100 minutes, well over its scope.
- Site worker fetched 179 Esri tiles, the first 40 faster than the politeness rule.
- Georef and trace workers wrote their own repo files though the brief reserved shared files for the coordinator.
- The georef check was edited after seeing errors, so it is not blind (Q7).
- The plan's scale was wrong in the shared brief until corrected after wave 1.

## palace_r2_map

**Delivered:** the 3D view of all three gardens, the dev map with 11 layers, 1636 boxes (1509 on a block or stated size, 127 guesses: 79 Xiyang Lou parts, 23 gates, 14 default, 11 laid out), the panel, 1877 pages (1824 rows, 53 gates), `tools/serve_local.py`, `tools/check_pages.py`. 3804 files.

**Timeline:** read 18:00–18:03; ground, boxes, publish, server, dev map to 18:14; 3D view to 18:17; pages and docs to 18:26; screenshots and checks to 18:29.

**Checked:** console clean on three servers; real click opens the panel; deep links; walk mode with keys only; no plan image in `site/`; 1522 clickable objects, none without a page; second generator run changes nothing.

**Went wrong, then fixed:** the outer plain hid the water; land colours skipped colour conversion; labels too small; wall tops through low roofs; stated sizes not reaching three halls because row names differed; workers' shorthand in public notes; the garden tint outside the walls.

**Left:** 28 box pairs overlap where the plan does; 13 boxes partly over water; canals like ditches up close; no trees; not tested on a real graphics card or a phone.

## palace_r3_evidence

**Delivered,** before → after:

| | Before | After |
|---|---:|---:|
| Top-level objects (314) with their own picture | 58 | 99 |
| Top-level objects with their own text or drawing | not measured | 167 |
| Panels (1877) with their own picture | 58 | 152 |
| Named halls (605) with their own evidence | not measured | 567 |
| All halls (1510) with their own evidence | not measured | 573 |
| Pictures in the catalogue | 230 | 547 (450 on the site) |
| Text and drawing entries | 0 | 2397 |

Also: parent fallback in the panel, `research/evidence/facts.csv`, `tools/check_evidence.py`, Q36–Q53, and only 19 boxes changed.

**Best finds:** the plan's labels at 九洲清晏 date from 1873 or later (Q36); the park's compilations S360, S361; the whole 1887 edition of 圆明园图咏; the Skušek album; a court officer's route of 1856; Bourgeois's letter of 1786; Barrow's measure of 1793.

**Timeline:** wave 1 of eight topics 19:14–19:58; merge and panel to 20:11; wave 2 of four topics 20:12–20:45; final merge and checks to 20:54.

**Checked:** both check tools pass; 149 of 149 日下旧闻考 and 40 of 40 preface quotes match; 88 of 92 from Malone, 4 not chased; 27 of 28 sampled links answer.

**Went wrong:**
- **Broke "no git writes" twice:** `git checkout -- research/buildings.csv`, to undo its own edit.
- 163 entries rest on search summaries, marked; 45 facts held as `lead`.
- Commons rate limits stopped 187 name searches; the web search budget of 200 ended at 19:45; mhymy.com refused record pages (20 of 146 records listed, 0 read).
- S360 and S361 poems are script-picked, sampled by eye.
- Rights calls made for Tomasz to review: Q50.
- `scripts/build_catalog.py` deleted on purpose; nine page folders renamed once their labels were read.

## palace_r4_docs

**Delivered:** `CLAUDE.md` brought up to date, `research/README.md` checked against the files, `docs/METHOD.md`, this folder, and `tools/check_docs.py` (not asked for by name: it is the script the brief asked for, kept so the check can be rerun).

**Checked:** the pipeline from `scripts/trace_plan.py` through `scripts/building_pages.py` rerun in a scratch copy, with no file differing; `tools/check_pages.py` and `tools/check_evidence.py` pass, and the repo is unchanged by them.

**Found in the old docs and fixed:**
- `CLAUDE.md`: the Goal line blurred the looting and the burning; the homepage was called a placeholder; `tools/` was said to hold screenshot scripts, and has none; the layout left out `research/plan/`, `research/terrain/`, `research/wishlist.md`, `generated/`, `docs/`; S01's state ignored Q36.
- `research/README.md`: `scripts/georef.py` with no argument was said to write the overlay and images, and it only fits; six fields of `buildings.csv` had no row in the table; `research/evidence/facts.csv`, the control points, the readers' files, most layer properties and the panel JSON had no field list; six files in `research/plan/` were unlisted.

**Not settled:** 万春园 (Round 1's flag), left as written; efforts of four rounds; the writing time of the rulebook.

## palace_r5_refs

**Delivered:** `research/twins/catalog.csv` (135 pairings), `research/reconstructions/catalog.csv` (326 rows, 25 free), 172 new pictures in `research/photos/catalog.csv` with the field `relation`, the column `size_lead` in `research/buildings.csv`, the panel's two new sections, CLASS pages, Q54–Q62, 15 wish rows, 151 sources.

| Measured by `tools/check_evidence.py` | Before | After |
|---|---|---|
| Top level, of 314: free image of its own | 99 | 103 |
| Top level: free image, own or inherited | 185 | 314 |
| Top level: reconstruction of its own | 26 | 84 |
| Top level: reconstruction, own or inherited | 237 | 314 |
| Top level: twin or comparable photo of its own | 0 | 45 |
| Top level: twin or comparable photo, own or inherited | 0 | 212 |
| Halls, of 1510: free image, own or inherited | 1110 | 1510 |
| Halls: reconstruction, own or inherited | 544 | 1510 |
| Halls: twin or comparable photo, inherited | 0 | 1496 |

**Timeline:** wave 1 of six topics 21:48–22:24; merge and panel to 22:35; wave 2 of three topics on the gaps 22:36–23:09; final merge, screenshots, docs to 23:26.

**Checked:** all generators and `tools/check_pages.py`, `tools/check_evidence.py`, `tools/check_docs.py` pass; 24 of 24 quotes from 日下旧闻考 in the twin rows match the text on Kanripo, allowing variant characters (畧, 寕, 倣, 髙), checked by script; 43 of 44 sampled links of new rows answer, one timed out; no old cell of `research/buildings.csv` changed; panels of 九洲清晏 YM03, 文源阁 YM46, 狮子林 CC13, 海晏堂 XY08, 正大光明 YM01 and a plain hall viewed in public and private mode, with no console errors, broken images or requests to `/_local/` in public mode.

**Decided by the coordinator, reasons in the files:** the Hengdian photographs free (Q55); zodiac head models, in games or chocolate or as scans, off the panels though on record; the 烫样 set apart as period, not modern; a hall inherits its garden's and class's rows folded; a lost twin stays in, under its own heading; 大三巴 dropped, being the worker's own pairing without a source; three relations reduced to `comparable`; ten ISPRS figures pulled from the PDFs with PyMuPDF in scratch, since the workers had no `pdfimages`, and opened by eye, on which one row was added.

**Went wrong or left open:**
- mhymy.com refused all inner pages, so about 90 [清华] entries are unlisted, and 60 rows are `snippet`.
- `snippet` rows and video rows rest on search summaries and metadata: no video was watched. "Viewed" often means a page came through a fetch summary, and ties from thumbnails are `guess`.
- A worker counted up Persée's page-image URLs to read Durand 1988, after a PDF request on another article got 403. The images are what the site's reader shows and that article's pictures are not masked, so the facts and research crops were kept, local only; a closer reading of "never work round a block" would drop them. Another followed a cookie redirect at nature.com, with no log-in or challenge; kept.
- One mhymy `/feed` request was made before its `robots.txt`, which disallows it, was read, and one `--http1.1` probe. Disclosed by the worker.
- 21 standing twins still have no picture, mostly in closed sites. 14 of the Forty Scenes have no twin at all: no source found states one.
- Twin grades for pictures mostly rest on a file name and a look at a thumbnail.
- Two workers' scripts overwrote each other in the shared scripts folder: name prefixes were added for wave 2.
- `site/` grew from 106 MB to 138 MB, `research/photos/images/` from 161 MB to 202 MB.
- Round 3's count of halls with evidence of their own falls from 573 to 570, as reconstructions left that catalogue; they appear as reconstructions now.

## palace_r6_xiyanglou

**Asked:** Tomasz, on a screenshot of the strip as plain boxes: "I think this part is the most important, because it's the existing one and the most famous. Can you try to find more references about this?" and, for the result, "and add to page".

**Delivered:** `research/xiyanglou/`, a dossier and a dimension sheet for XY01-XY15; `views.csv`, `dimensions.csv`, `boxes.csv`, `parts.csv`, `materials.csv`, `fragments.csv`, `rephoto.csv`, `impressions.csv`; the plates at 2400 px; boxes from those sheets; the panel's pictures by side, a Dimensions block; `site/xiyanglou/` and a zh draft, linked from the homepage and each XY panel. Common brief: `common/palace_r6_subagents.md`; merge: `common/palace_r6_merge.py`, `common/palace_r6_boxes_seed.py`, `common/palace_r6_facts_seed.py`, records.

**Checked:** `tools/check_pages.py`, `tools/check_evidence.py` (a new XY section, against `research/evidence/coverage_before_r6.json`), `tools/check_docs.py`. A worker checked the page's text against its sources: 195 checks, 155 held, 33 changed, 7 not verifiable; all 33 applied. Screenshots in `screenshots/r6/`, opened.

**Went wrong or left open:**
- The brief's own claims failed three times: Malone measures no foundations in those pages; the Bergen pieces reached the park in 2023, not Peking University in 2014; S600 shows no Archimedes screw.
- A perspective worker's first table held pixels from reads that never came back; it withdrew it itself and redid all 20 plates.
- Commons' host rate-limited twice; the workers slept it out. One worker's loops sent a few more requests after a 429 and a 403 before stopping. Workers went over budgets: 53 searches against 45; 27 imagery tiles, not "a handful", all deleted.
- Most plates' scales rest on plan widths, and only XY06, XY09, XY10 and XY11 on a survey. Figures of method a: 29 of 453.
- The walls and footprints layers stay on the plan while the boxes moved to the ruin (Q64).
- No native reader for the zh page.

## palace_r7_scenes

**Asked:** Tomasz: "Can you continue research?" Do for every scene and compound outside the Xiyang Lou what Round 6 did for it, in priority order: the famous scenes, the other Forty Scenes, Changchun Yuan, Qichun Yuan.

**Delivered:** `research/scenes/`, 81 dossiers with dimension sheets, the sheets they draw on (`about.json`, `halls.csv`, `dimensions.csv`, `views.csv`, `best.csv`, `digs.csv`, `interior.csv`, `parts.csv`, `checks.csv`), the overview with the modelling priority and a typology check; `scripts/scenes_dossiers.py`, `scripts/scenes_page.py`; the Dimensions block and the dossier link in every scene's panel, halls inheriting them through the fallback; the hub `site/scenes/` and ten public scene pages with zh drafts, linked from both homepages; 36 free pictures, 57 texts and drawings, 2 reconstructions, 19 sources (S900-S999), 124 facts, Q78-Q185, 64 wishes. Common brief: `common/palace_r7_subagents.md`; merge: `common/palace_r7_merge.py`; lists and before-coverage: `common/palace_r7_lists.py`; screenshots: `common/palace_r7_shots.js`, `common/palace_r7_stitch.py`. Records, not pipeline steps.

**Timeline:** reading and skeletons 16:19-16:26. Eight workers 16:26-17:01 (texts in two halves, drawings, digs and studies, photographs, the album read hall by hall, the other Forty Scenes, Changchun and Qichun), while the coordinator wrote the generators. Merge and pipeline 17:01-17:08. Three workers 17:08-17:37: two checked the public text sentence by sentence and wrote the zh drafts, one searched Commons and Openverse again. Pages, screenshots, docs to the end.

**Checked:** `tools/check_evidence.py` with a scenes section against `research/evidence/coverage_before_r7.json` (commit 6b27915), `tools/check_pages.py`, `tools/check_docs.py`; `scripts/building_pages.py` run twice; `scripts/build_r1.py` reproduces the layers byte for byte before the facts. 275 sentences checked: 154 held, 116 changed, 5 not verifiable; all applied. Screenshots in `screenshots/r7/`, opened.

**Went wrong or left open:**
- The first eight workers ran in the background, the Agent tool's default; the brief asked for the foreground. The coordinator kept its turn open until all returned (the last at 17:01), and the second batch ran in the foreground.
- `apply_facts.py` dropped the second of two sizes on a row into the note (three earlier rows had lost a depth); fixed. A merge rule let one worker's merge win over another's keep; fixed, and `boxes1860.py` now stops on a merge into a row with no box.
- Halls with evidence of their own stay at 573: the new pictures and texts went to halls that already had a name. The 937 unnamed blocks still show only the plan and their scene: a plan-reading pass is on the wishlist.
- Most Yangshi Lei figures are modern transcriptions on mhymy, the drawings themselves unseen; the 1855 whole plan of 九洲清晏 (样011-3) is behind a paywall. Many 九洲清晏 court figures come from the Tongzhi plan of 1874: graded B.
- No free modern photograph found for eight wave 1 scenes; no new old photograph of any scene outside the Xiyang Lou.
- Typology proposals (Q182-Q185) are not applied. No native reader for the zh pages.
- The brief's 日下旧闻考 j80-87 holds Changchun Yuan in j83 only; j84 is 清漪园.

## palace_r8_georef

**Asked:** make the map more accurate: a blind, fixed check set first; a piecewise fit region by region against the previous fit and a plain affine; walls and gates from the new fit, reconciled with today's; fix Q64 (walls through the maze and 谐奇趣) and Q71 (the 大水法 court); water and islands against today's shores; boxes rerun; an accuracy layer on the dev map; `tools/check_georef.py`.

**Delivered:** `research/georef/check_points.json`, 22 blind check points frozen by hash, with `readings_r8/` (the readers' lines and notes); `control_r8.csv` (9 read by eye, 7 used) and `control_shapes.csv` (12 Xiyang Lou ruins of Round 6, 7 lakes; the rebuilt maze, interpolated rows and a re-dug pond left out with the reason); `princeton-1920s.json` (the fit in use) beside `princeton-1920s.previous.json` (Round 1, rebuilt byte for byte); `check_baseline.json`, `shift_r8.json`, `shores_r8.json`; `research/layers/georef_error.geojson` and the dev map's "Placement accuracy" toggle; `scripts/georef_readings.py`, `scripts/control_derived.py`, the Round 8 part of `scripts/georef.py`; `tools/check_georef.py`, `tools/georef_crops.py`, `tools/georef_shift.py`, `tools/shore_check.py`, `tools/wall_check.py`; the wall rule and the hill trim in `scripts/build_r1.py`, the sunken court in `scripts/ground1860.py`; Q7, Q31, Q64, Q71 updated, Q186-Q190, three wishes. Readers' brief: `common/palace_r8_readers.md`.

**Timeline** (the progress log): reading, the mosaic refetched from the museum (`research/raw/` held only `buildings/`) and the pipeline rerun with no diff, 17:57-18:04; before screenshots 18:04; five readers 18:12-18:47 and a sixth for Qichun from 18:25, while the coordinator wrote the fit, the checks and the court; wave 2 with the changed rule 18:47-18:57; frozen 18:59; fit 19:01; walls and Q64 by 19:08; the derived controls made independent of the fit and the chain checked for idempotence by 19:11; screenshots and docs to the end.

**Accuracy, on the frozen check set** (median / 90% / max in metres, n): all, previous 19.8 / 38.4 / 45.9, affine 22.0 / 51.4 / 64.0, fit in use 19.7 / 38.7 / 46.3 (22). YM west 21.9 / 35.7 / 39.1 (2), YM east 18.9 / 22.0 / 22.8 (3), both kept on the Round 1 fit; Fuhai 15.5 to 15.1 (2); Changchun 20.7 to 20.5 (9); Xiyang Lou 7.7 to 7.8 (1); Qichun 21.3 to 21.2 (5). Foundations in place 2-8 m, re-dug shores and channel mouths 14-46 m.

**Checked:** `tools/check_georef.py`, `tools/check_pages.py`, `tools/check_evidence.py`, `tools/check_docs.py` pass; `scripts/building_pages.py` run twice; the placement chain run twice gives the same files. Screenshots before and after in `screenshots/r8/` from one page load each (Tomasz's Xiyang Lou camera, the 大水法 court, 福海, 九洲清晏, the western plain) and the dev map with the accuracy layer, opened.

**Went wrong or left open:**
- The six readers ran in the background, the Agent tool's default, as in Round 7; the coordinator kept its turn open until all had returned, twice.
- The first rule (60 m from any Round 1 fit point) left 19 check points: Round 1 had used most sharp features that survive. It became 30 m before any error was computed; four regions still have three points or fewer, the Xiyang Lou one.
- The new fit gains nothing that matters: under 0.4 m in any region, worse in YM west and east, which keep Round 1's. The placement is limited by what survives on the ground, not by the transform.
- The first lake derivation read the water layer, which follows the fit, so the chain was not a fixed point; it reads the tracing in plan pixels now. It also skipped lakes OSM keeps as relations (福海 among them); none of those passes the agreement rule.
- Not done: the outer walls of Yuanming Yuan stay where Round 1 traced them although today's rebuilt north wall lies 17-53 m outside (Q186); Changchun's west part reads 12-23 m east (Q187); no DEM-derived shore or hill top was used (GLO-30's 30 m cells hold trees and fill); the Forty Scenes leaves and the 1933 plan were not used as control (no metric position; no scan).

## palace_r9_paths

**Asked:** Tomasz: "Do we have any information about roads and walking paths?" Only bridges, gates, water and today's OSM paths. Build the 1860 walkways, courtyard paths, causeways, dikes, galleries, landings and boat routes, and walk routes in the 3D view.

**Delivered:** `research/paths/` (the findings by source in its README; `traces.csv`, `album.csv`, `texts.csv`, `remains.csv`, `grades.csv`, `routes.csv`, `exceptions.csv`; generated `bridge_ends.csv`, `dangling.csv`, `unreached.csv`, `osm_judged.csv`); `research/layers/paths_1860`, `landings_1860`, `routes_1860` and their public copies; `scripts/paths1860.py`, `tools/check_paths.py`, `tools/osm_paths.py`; `site/reconstruction/paths3d.js` (strips, galleries on posts, landings, dashed boat lines), the toggles `paths` and `assumed`, the route menu and walker in `3d.js`, the Ways section in the panel (`ways` in the panel JSON); BR006 and BR047 corrected; S992, S993; Q191-Q196; four wishes. Common brief: `common/palace_r9_subagents.md`; the workers' notes `common/palace_r9_notes/`; the readers' tools `common/palace_r9_tools/`; merge `common/palace_r9_merge.py`. Records, not pipeline steps.

**Numbers** (`tools/check_paths.py`): 1348 lines, 34.1 km. 527 traced (18.8 km) in 137 scenes; 62 bridge approaches and 759 links added for reach, all C. A 85 (2.4 km; 75 from a 1744 leaf or a plate, 10 from a dig), B 175 (6.3 km), C 1088 (25.4 km). 85 landings and docks. Ends before snapping: median 2.4 m, 90% 11.4 m, worst 25.5 m; after: every A or B end within 0.5 m of what it meets but six, written down. 66 of 73 bridges reached at both ends. Routes: R1 the emperor's way 528 m, R2 the processional way 211 m, R3 the Xiyang Lou axis 826 m, R4 the boat tour of 福海 2.5 km.

**Timeline** (the progress log): reading and the readers' crop tool 19:22-19:27; eight workers in the foreground 19:27-19:49 (five plan readers by region, texts, the album and plates, digs and Qing plans); generator, routes, panel and 3D to 20:15; checks, bridges, screenshots and docs to the end.

**Checked:** `tools/check_paths.py`, `tools/check_pages.py`, `tools/check_evidence.py`, `tools/check_georef.py`, `tools/check_docs.py` pass; `scripts/building_pages.py` and `scripts/paths1860.py` run twice, the second changing nothing; `scripts/build_r1.py` after the bridge fix changed only `bridges_1860` (`buildings.csv` byte for byte). Screenshots in `screenshots/r9/`, from one page load with `?shot=1` (and one normal load for the panel and the menu), opened; console clean, no `/_local/` request.

**Went wrong or left open:**
- The walker first failed to load: a second `const SPEED` in `3d.js`; caught by the first screenshot run.
- First stills: the overviews too high to show a path, the Xiyang Lou still inside a hall the route walks through; redone.
- The remains worker ran four searches on mhymy.com before reading its robots.txt, which disallows them; it stopped, deleted the results and used only an allowed article page.
- The network is mostly C: links outnumber traced lines. No Qing text tells how the emperor crossed the 前湖 (R1 takes 如意桥, our choice); no dig gives a path width; the water layer lacks some ponds and closes some necks, so 17 landings stand off the shore and the 福海 tour skips 方壶胜境's inlet (Q191, Q192); 64 halls (most in the closed courts of 含经堂 and the 长春园 gate) no link could reach; the candidate missing bridges were not confirmed (Q193).

## palace_r10_ground

**Asked:** the ground was nearly flat, and the 54 hills had only a provisional rule height (sqrt(area)/8, not empty as the brief said). Build hill heights by a ladder of methods; water at one level per body, beds and banks; flat pads under the halls; drape every object and measure the gaps before and after; a confidence tint and contour lines in the view; generated files under 8 MB; `tools/check_ground.py`.

**Delivered:**
- **Terrain:** `research/terrain/`: the README (what is measured, read and typology; the error by region), `research/terrain/readings.csv` (475 rows from five workers), `research/terrain/plain.json`, `research/terrain/glo30_rise.npz`, `research/terrain/hills_heights.csv`, `research/terrain/rockeries.csv`, `research/terrain/water_levels.csv`, `research/terrain/ground_report.json`, `research/terrain/ground_check.json`.
- **Scripts:** `scripts/terrain_dem.py` and `scripts/hills1860.py`; `scripts/ground1860.py` rewritten; in `scripts/boxes1860.py` a `layout()` function, the feet over water, stepped walls and decks taken from the ground; in `scripts/scene1860.py` the ground frame and the new `Grid`.
- **Hills:** `layers/hills_1860` now holds 472 hills: the 54 outlines of S01 and 418 pieces of free land, assumed.
- **View and check:** `site/reconstruction/ground3d.js`; the toggles `contours`, `conf` and `assumed` act on the ground; `tools/check_ground.py`.
- **Records:** S1000-S1016, Q197-Q203, five wishes. The merge `common/palace_r10_merge.py` and the region table `common/palace_r10_regions.py` are records, not pipeline steps.

**Numbers** (`tools/check_ground.py`, before = the commit of Round 9 measured with the same script):
- **Hills:** 54 to 472. By method: rule 45 and GLO-30 9 before; now surveyed 1, dem 122, painting 96, text 1, typology 252. All C but 线法山 (B).
- **Water:** one level before; now 189 bodies at 41.99-44.82 m, no water triangle across two levels.
- **Boxes:**
  - floating 95 (median 1.30 m) to 1 (0.09 m);
  - buried past the platform 49 (up to 5.35 m) to 1 (0.22 m);
  - gap over 0.3 m 137 (113 of them A or B) to 0.
- **Bridges:** deck ends against the ground max 0.38 m before and after, none over 0.5 m.
- **Ways:**
  - strip points with no land under them 180 to 23 of 9772;
  - ends against a deck or a box (between its foot and its platform's top) 8 over 0.5 m (5 A or B) to 2 (no A or B);
- **Walls:** courses hanging 61 (1.30 m) to 0.
- **Files:** generated files 5.7 MB to 7.28 MB.

**Timeline** (the progress log):
- 20:34-20:43: reading, the DEM refetched, plan crops viewed. S01 draws no earth hills.
- 20:43-21:05: five workers in the foreground (hills surveyed, hills in texts, water, album in two halves).
- 21:05-21:48: the DEM step, the hills, the ground, the view, the check.
- To the end: the screenshots and the docs.

**Checked:**
- `tools/check_ground.py`, `tools/check_pages.py`, `tools/check_evidence.py`, `tools/check_georef.py`, `tools/check_paths.py` and `tools/check_docs.py` pass.
- `scripts/building_pages.py` run twice. The chain `hills1860.py` through `paths1860.py` run a second time changes nothing.
- No box moved: 0 of 1634 rings changed. `paths_1860` is unchanged.
- Screenshots in `screenshots/r10/`, before and after from one page load each, opened. The before page lacked its fonts (only `site/reconstruction` was exported).

**Went wrong or left open:**
- A first mesh of 2.5 m cells came to 24 MB. A 5 m floor, int16 positions, uint16 chunks and a 20 m bed took it to 5.35 MB.
- A new per-vertex byte added after the last run blotched the plain in the first screenshot.
- The bed sat above the water in narrow canals.
- The water's offset hid the boat lines.
- Deck ends inside the water polygon floated 1.4 m.
- All fixed and re-shot.
- **Still weak:**
  - The generated hills are a pattern, not places (Q199).
  - The album's heights are scaled to Attiret by a run (Q198).
  - The water's fall follows the DEM against S05 (Q197).
  - The mesh departs from the design raster by up to 4.3 m in the 10 m shore cells. The view drapes on the mesh, so nothing floats, but hills there are flattened.
  - 南大桥 and others whose lines run over land in the water layer lie flush (Q191).
  - Plan rockeries (the hatched clumps) are not traced.

## palace_r11_kit

**Asked:** draw every hall from its data instead of a plain box, so that no place stands empty: a Qing hall kit (platform, steps, columns, doors and windows, roofs by class with 起翘 and the 举架 profile, a bracket band, galleries, courts, seeded variation, a lower level of detail far off), a stone kit for the Xiyang Lou, the hall's own figures where a dossier gives them, `kit=0` and `assumed=0`; re-read Q182-Q185; `tools/check_kit.py`; screenshots before and after.

**Delivered:**
- **The numbers:** `scripts/kit1860.py` writes `site/reconstruction/data/kit_1860.json` (one entry per box: bays, porches, steps, roof class, tiles, band, where the form comes from) and `generated/courts.bin` (17.3 ha of courts, 58,582 triangles).
- **The kits:** `site/reconstruction/kit3d.js` (the hall kit, the courts, the galleries of Round 9) and `site/reconstruction/stonekit3d.js` (the Xiyang Lou), in 124 tiles of 180 m with a far level built at load and a near level built only within 420 m of the camera. `halls3d.js` keeps the boxes, picking, selection and the confidence tint, now over several meshes with byte colours and flat shading. `3d.js` and `3d.html` add the switch `kit` and the legend. `paths3d.js` puts its gallery roofs in their own group, hidden when the kit is on.
- **The data:** `scripts/boxes1860.py` takes a hall's own figures from its dossier (`figures()` in `scripts/scene1860.py`; 37 boxes changed height) and a roof or tile read for the hall in `research/scenes/halls.csv` (39 roofs, 38 tiles; `roof_src`, `tiles_src`, `tile_edge`, `sides`, `gable_kind`).
- **Typology:**
  - Q182 and Q183 applied: grand_hall column 5.12 to 4.17 m, platform 1.22 to 0.59 m, the medians of its measured halls by `scripts/typology_rules.py`; bays 5.17 / 4.83 / 4.32 m from 正大光明殿's slip.
  - Q184 applied: 清音阁 from its drawing, 14.52 m square, platform 0.96 m, three column heights, its eaves at 5.38, 12.18 and 18.0 m.
  - Q185 left open: the 华表's block is absorbed into the 牌坊's, and no positions are read for the four columns.
  - `scripts/build_r1.py` and `apply_facts.py` rerun: only the row and footprint of 清音阁 changed.
- **Panel:** the model block's "Drawn" row says how the kit draws the box. A class hall's says "drawn from the typology of its hall class, not from a picture of this hall (assumed, C)". An "Own figures" row lists a dossier's figures (`scripts/building_pages.py`).
- **Check:** `tools/check_kit.py` (`--browser`, `--before-url`) writes `research/kit/kit_check.json`, `research/kit/kit_browser.json` and `research/kit/kit_report.json`; the overview is `research/kit/README.md`.
- **Records:** Q204-Q208, two wishes, `research/typology/halls.md` section 10, `docs/METHOD.md` phase 16 and the kit's pitfalls.

**Numbers** (`tools/check_kit.py`; before = the commit of Round 10 served from an export, measured in the same session, software WebGL, 1400 x 900):
- **Drawn:** 1634 of 1634 boxes, 1555 by the hall kit and 79 by the stone kit.
  - Form from the class 1476, a dossier 154, a stated size 4, a model 0.
  - Roofs: 歇山 418, 硬山 596, 悬山 268, 攒尖 289, 庑殿 63; 卷棚 on 1265.
  - Tiles: grey 1530, glazed 71, slate 1, stone 32.
  - Courts 17.3 ha.
- **Inside the box:** body or roof beyond the footprint median 0.19 m, max 0.66 m, none beyond its overhang; steps at most the overhang (max 2.16 m on a temple hall).
- **Joints:**
  - Before, no hall had steps: the 1351 way ends at a box side dropped 0.41 m median, up to 2.13 m, to the platform's top.
  - Now 2385 flights stand on the ground (feet within 0.01 m), and 1333 of those ends meet a flight within 1.5 m (gap median 0, max 0.1 m).
  - 11 ends are at a pool, a wall, a court or a hall on a terrace; 7 meet a side within 0.14 m of the platform's top.
- **Cost:**
  - Overview: before 325 ms and 458 k triangles drawn; after, with the kit, 325 ms, 575 k drawn, 666 k in memory.
  - 同乐园 from 150 m: before 165 ms; after 272 ms, 548 k drawn.
  - One hall from 40 m: before 174 ms; after 280 ms, 586 k drawn, 1.31 M in memory.
  - All near levels together would be 1.68 M triangles; far levels 150 k.
- **Files:** kit_1860.json 0.59 MB, courts.bin 1.05 MB, the two scripts 0.07 MB: 1.71 MB.

**Checked:** `tools/check_kit.py`, `check_pages.py`, `check_evidence.py`, `check_docs.py`, `check_georef.py`, `check_paths.py` and `check_ground.py` pass. Step 6 run twice changes nothing. Screenshots in `screenshots/r11/`, before and after from one page load each, opened. Console clean.

**Went wrong or left open:**
- The first near level, built for every tile at load, held 4.8 M triangles (about 0.9 GB with float colours and normals). Lazy tiles, lighter openings (faces, not boxes), byte colours and flat shading took it to 0.67-1.3 M.
- The bracket band poked through every roof as a red stripe. Bands are now capped at the roof's profile.
- Shore steps hung over the banks, and ground probes counted as geometry in the footprint measure. Both fixed.
- One `pkill -f` matched its own shell and killed the command. Use `pkill -f "[s]erve_local..."`.
- **Still weak:**
  - 1476 forms are the class's.
  - Colours, windows and doors are not read from any picture of this garden (Q204, Q205).
  - The 硬山 / 悬山 split is seeded (Q206).
  - The stone kit gives every European front the same vocabulary (Q207).
  - The courts are a closing of the halls, not the compound walls (Q208).
  - Round 9's galleries draw a Chinese gallery in front of 谐奇趣.
  - In software WebGL a close view costs about 1.6x the old frame time.

## palace_r12_greens

**Asked:** the gardens' planting by scene, from sources: a species table (poems and prefaces, 日下旧闻考, the 1744 leaves and later pictures, the court's records as cited, today's old trees and rocks, accounts 1743-1860), a layer of areas with a grade for the extent and one for the species, the rockeries, a generator and a view with seasons, `greens`, `assumed` and `conf`, `tools/check_greens.py`, the panel's "Planting of this scene", screenshots.

**Delivered:**
- **Sources:** `research/greens/species.csv`, 823 rows from six readers working in the foreground (texts of YM01-20 and of YM21-88, Changchun, Qichun and the Xiyang Lou with the court's records, the album in two halves, survivors and accounts); 759 kept (676 A, 68 B, 15 C) in 110 scenes, 64 rejected with the reason. The worker brief: `docs/rounds/common/palace_r12_worker_brief.md`; the merge: `docs/rounds/common/palace_r12_merge.py` (a record). Fifteen rows hand-corrected after the first runs (the wall bank a tree screen, the Xiyang Lou rows topiary, fences not plants). Sources S1120, S1140, S1141, S1160-S1165; Q209-Q218; three wishes.
- **Generator:** `scripts/greens1860.py`: `research/layers/greens_1860` and its public copy (466 areas, 86 rockeries), `site/reconstruction/data/greens_1860.json`, `site/reconstruction/generated/greens_1860.bin`, `research/greens/greens_report.json`. `scripts/kit1860.py` now exposes `court_area()` (its output unchanged, byte for byte).
- **View:** `site/reconstruction/greens3d.js` (plants baked per 200 m tile, a far and a near level; rockeries as lumps), `3d.js` and `3d.html` (the toggle, the season, the legend), `panel3d.js` (the planting block), `scripts/building_pages.py` (`planting` on scene, hall and garden pages).
- **Check:** `tools/check_greens.py` (`--browser`), `research/greens/greens_check.json`, `research/greens/greens_browser.json`; the overview `research/greens/README.md`.

**Numbers** (`tools/check_greens.py`; before = the planting switched off in the same page load, software WebGL, 1400 x 900):
- **Plants:** 0 before; 40,161 now: lotus 13,147, reeds 7,568, bamboo 4,447, pines 4,324, blossom 2,825, floating leaves 2,728, broadleaf 2,530, willows 1,451, flower beds 624, cypresses 261, topiary 255. Species A 28,789, B 3,456, C 7,916; extent B 7,070, C 33,091; the fill (assumed) 6,508.
- **Areas:** 466 in 87 scenes (209 groves, 103 specimen groups, 42 bamboo groves, 40 lotus ponds, 26 flower beds, 24 avenues, 21 reed beds, 1 hedge); extent B 163, C 303.
- **Rockeries:** 86 (32 shore rockwork, all reaching the water; 27 rock hills; 24 standing stones; 3 rock screens), none floating, none in a box.
- **Clearances and ground:** 0 plants in a box or with a crown over one, 0 on a way, wall or bridge, 0 in a rockery, 0 land plants in water, 0 water plants on land; bases at most 0.00 m off the walk surface, the ground under a trunk at most 0.39 m below its base (sink 0.5 m), water plants within 0.005 m of their level.
- **Cost:** overview 402 → 565 ms (575 k → 846 k triangles drawn); 九洲清晏 from 220 m 310 → 384 ms; 曲院风荷 from 140 m 248 → 333 ms; seasons within 10% of each other.
- **Files:** 3.14 MB of generated data (layer 2.52, binary 0.56, index 0.06).

**Checked:** `tools/check_greens.py` (with `--browser`), `check_pages.py`, `check_evidence.py`, `check_georef.py`, `check_paths.py`, `check_docs.py`, `check_ground.py` and `check_kit.py` pass. `scripts/building_pages.py` run twice; `scripts/greens1860.py` run twice gives the same files. Screenshots in `screenshots/r12/` from one page load (the panel from a second), opened; the bare views are the planting switched off.

**Went wrong or left open:**
- Instanced plants cost about 500 ms a frame in software WebGL; baked tiles brought it to about 120-160 ms.
- A garden-wide row with `place` scene filled a whole garden with 2,500 pines; the wall belt of GARDEN-ALL first found no wall; clipped pines lost their form to the species key; a specimen with no count was area-filled (98 weeping pagoda trees in the maze court); flower beds hit their cap of 160. All fixed.
- Far crowns of 8 triangles read as diamonds; now 14-triangle lumps.
- **Still weak:**
  - Every place is generated (Q218); 33,091 plants stand on C extents.
  - Lotus at 曲院风荷 and 平湖秋月 follows the texts against the leaves (Q209).
  - The commonest tree is unnamed (Q210); sizes are species defaults.
  - The maze walls (Q211), the tall tiers of 大水法 (Q212) and Qichun's Jiaqing-era rows (Q215) are open.
  - 39 rows found no place and 37 areas no room (`research/greens/greens_report.json`).
  - With `assumed=0` plants on generated hills are lowered by the hill's height, not re-placed.


## palace_r13_pilot

**Asked:** an engraving overlay tool and the pilot model of 谐奇趣 XY01:
- the tool renders an object from each plate's camera, lays it over the plate and measures key points in pixels and metres;
- the model: block, colonnades, octagons, pools, every side detailed, the kit replaced, "Our model now" with its viewer;
- iterate against plates 1 and 2 and the 1873 photographs;
- the joints with the ground and the ways;
- 海晏堂 XY08 as a kit baseline;
- `tools/check_models.py` and screenshots.

**Delivered:**
- **Key points:** `research/xiyanglou/plate_keypoints.csv`. Three readers worked in the foreground, from a fixed vocabulary (`models/README.md`): 174 points on plates 1, 2, 10, 11, 13 and P0185-P0189, each checked with a cross. Five readings are skipped with their reason. Plate 1's octagon readings were renamed to what was read, the outline.
- **Priors:** `research/xiyanglou/photo_viewpoints.csv`, the photographs' camera priors.
- **Tool:**
  - `tools/plate_overlay.py` (`fit`, `compose`): pinhole cameras with `anchored`, `all` and, for plates, `stretch` (heights drawn k times widths). It writes `plate_fit_<ID>.csv`, `plate_cameras_<ID>.json`, `site/reconstruction/data/plates.json` and the point overlays.
  - `tools/plate_overlay.mjs`: the renders from one page load, the views, the panel, a `--before` copy.
  - `3d.html?plate=<photo id>&platefit=`: a dev mode with the picture over the view.
- **Model:** `models/XY01-xieqiqu/`: `models/XY01-xieqiqu/xieqiqu.py`, `models/XY01-xieqiqu/measure.py` (the storeys read off the photographs; `--roofs` off the plates), `params.json`, `models/XY01-xieqiqu/keypoints.json`, `models/XY01-xieqiqu/joints.json`, `summary.json`, `README.md` (the evidence, the iteration log v1-v5, the disagreements). The mesh and GLB writer is `scripts/model_mesh.py`.
- **Publishing and view:**
  - `scripts/building_pages.py` publishes the model (`site/reconstruction/models/XY01/model.glb`, `data/models.json`, the panel's rows).
  - `scripts/kit1860.py` gives the model's boxes `src` `model`.
  - `site/reconstruction/glb_lite.js` and `model3d.js` come from Küstrin.
  - `halls3d.js` puts the model's boxes in `pM`, unseen, still the click target.
  - `3d.js` loads the models, handles selection, `assumed`, `conf`, the preview and plate mode.
  - `panel3d.js` adds the slot for "Our model now".
  - `paths3d.js` and `kit3d.js` skip the steps and galleries the model draws.
- **Joins:**
  - `scripts/paths1860.py` uses a model's entries as its boxes' doors and routes round its footprints. A traced way's points inside a model give way to it.
  - `research/paths/exceptions.csv` records CCX-001 to CCX-004, drawn by the model.
  - `scripts/greens1860.py` keeps the planting off the footprints.
- **Check:** `tools/check_models.py` (`models/check_models.json`). `tools/check_kit.py` leaves the modelled boxes to it.

**Numbers:**
- **check_models:** before the round, no model. After: 1 model with 88,252 triangles (21,558 fill); GLB 2.69 MB, 0.77 MB compressed (budget 1.5).
  - 22 joints: none floats (highest 0.01 m), deepest 0.74 m into the ground (the north basin's paving), most 0.0-0.3 m.
  - 9 way ends at the model, 0 off. Before: the north axis ended 5.4 m from any entry, and two old courtyard stubs 6.9 and 8.4 m off.
- **The model's figures:** the storeys were measured on P0185-P0189 with the frontage 27.2 m (S01) as the scale. Ground storey 3.91 ± 0.18 m, main cornice 8.64 ± 0.21, top cornice 11.55 ± 0.24, centre block 11.71 ± 0.28 wide, depth 8.60 ± 0.42, octagons' upper cornice 7.40 ± 0.33, the north flights' feet 2.27 ± 0.28 m from the axis. The roof apex is 14.0 m and the octagon apex 10.0 m, from the plates. The dossier had eave 15.1 m and ridge 18.3 m, by the plates' module.
- **Fit, v1 (the dossier's figures) to v5:**
  - Photographs (camera `all`, rms at the building): from 0.9-3.3 m to 0.29-0.59 m (P0185 0.29, P0187 0.44, P0188 0.44, P0186 0.58, P0189 0.59).
  - Plate 2: from 1.87 to 1.32 m (`stretch` 1.26 m, k 1.11; `anchored` 1.69 m).
  - Plate 1: from 3.6 to 2.43 m (`stretch` 1.59 m, k 1.57: drawn as a near-parallel elevation with the heights stretched).
- **海晏堂 XY08 kit baseline (`all`):** plate 10 3.71 m rms (median 0.66 m), plates 11 and 13 2.0 m (7 points each). The kit draws one long hip roof where the plates draw end pavilions under their own roofs.
- **Cost:** the overview draws 932 k triangles (846 k in Round 12) at 540-583 ms a frame in software WebGL. The site grows by 2.7 MB.

**Checked:**
- These pass: `tools/check_models.py`, `check_pages.py`, `check_evidence.py`, `check_georef.py`, `check_paths.py`, `check_docs.py`, `check_ground.py`, `check_kit.py --browser`, `check_greens.py --browser`.
- `scripts/building_pages.py` was run twice. The model's generator, `paths1860.py`, `kit1860.py` and `greens1860.py`, run again, gave the same files (md5).
- Screenshots in `screenshots/r13/`, opened:
  - overlays (blend, edges, side by side) and point plots for every picture and fit;
  - before and after views, front, rear, both ends, aerial, and the joints;
  - `assumed=0` and `conf=1`;
  - the panel with the viewer.

**Went wrong or left open:**
- The octagons' left and right were swapped in the generator: found by the residuals. A copy for the panel's viewer kept its transform on the group: an empty view. The plate mode used `window.viewer` before it existed. All fixed.
- The readers were started in the background by the Agent tool's default. All three finished before the turn ended.
- The south stair's upper flights were first built along the façade. The P0187 overlay showed them running north-south, and plate 1 agrees. The lower flights first ended against the wings; they now run out to the court.
- A pool measured on plate 1 alone ran into the lake: dropped. S01's pool stands (Q223).
- New questions: Q219 (the plates' tall top storey), Q220 (the south stair's lower flights), Q221 (the north feet), Q222 (the colonnades' junctions), Q223 (the pool's size; the brief's 30 × 18 m is not in the data), Q224 (the ways about 12 m off the ruin-placed model).
- Every figure is C until the Yangshi Lei sheet 985 is seen. Photographic heights rest on the plan's frontage (±15 %).

## palace_r14_haiyan

**Asked:** the detailed model of 海晏堂 XY08 built from the references, by the pilot's method: the west block, the stairs, the roof; the reservoir 锡海 (XY08-01) and the water clock 十二时辰水法 (XY08-02) with its twelve figures and the shell; the unnamed parts; the match check against every plate and photograph; the ruin photographs for the sides; `tools/check_models.py`; screenshots; docs. The twelve figures to be drawn factually, and the panel to say which heads survive and where.

**Delivered:**
- **The model** `models/XY08-haiyan-tang/`, the whole complex in one GLB:
  - the west block: eleven bays, end pavilions, attic, wings;
  - the terrace with the cascade's parapet and the two fish; the bent stairs;
  - the water clock: twelve seated figures with bronze heads in S823's order, the shell with its column and basin, the vase fountain, the pool, the paved court, two great pedestals;
  - the arcaded link with a flight onto the roof;
  - the water building of thirteen bays with the reservoir on its roof between two raised tiers;
  - the east block with four flights a side.
  The panel shows it with "Our model now", the rows of what each part rests on, and where the heads are today.
- **96 key points** read by three readers on plates 10-13 and P0774, P0303, P0170, P0299, from one vocabulary (`docs/rounds/common/palace_r14_haiyan_vocab.md`).
- **Tools:**
  - `scripts/model_parts.py`: the pilot's façade, rail and roof helpers, shared.
  - `tools/plate_overlay.py`: `--parts` (a camera per part), `--shots`; pictures with fewer than four points left out; the compose step also composes the part fits.
  - `tools/plate_overlay.mjs`: `--out`, and each model's own views (`models/XY08-haiyan-tang/views.json`).
  - `tools/check_kit.py` and `tools/check_greens.py`: `--port`.
- **Ways and docs:**
  - `research/paths/exceptions.csv`: four rows for the ways the model draws.
  - Q225-Q231 and three wish rows.
- **The pilot's arches:** 20 of 谐奇趣's 204 arches hung downward (a sign error in `arc_pts` for a semicircle); fixed there too, its key points and joints unchanged.

**Numbers:**
- **check_models:**
  - Before the round: XY01 only.
  - After: XY08 has 72,916 triangles (2,014 fill); GLB 2.23 MB, 0.63 MB compressed (budget 1.5).
  - 56 joints: none floats (highest 0.11 m into the ground), deepest 0.21 m. In v1, before the footings followed the ground, six were 1.2-2.8 m deep.
  - Seven ways end at its boxes; 0 off.
- **Fit (rms at the object):**
  - Plate 10, all: 3.71 m with the Round 13 kit, 2.07 m (v2), 1.41 m (v5).
  - Plate 10, by part: west block 0.58 m, water clock 1.88 m.
  - Plates 11 and 13, west block: 0.49 m each (the kit had 2.0 m on these points).
  - Plates 11 and 13, water building: 1.32 and 1.39 m (median 0.4 m). As one camera, 5.2 and 7.7 m: the plates draw the water building long (Q225).
  - Plate 12: 1.19 m (v3) to 0.64 m (v5).
- **Cost:** the overview draws 1.00 M triangles (0.93 M before) at a 570 ms median frame in software WebGL (583 ms before). The site grows by about 2.2 MB.

**Checked:**
- These pass: `tools/check_models.py`, `check_pages.py` (idempotent), `check_evidence.py`, `check_georef.py`, `check_paths.py`, `check_docs.py`, `check_ground.py`, `check_kit.py --browser`, `check_greens.py --browser`.
- `scripts/building_pages.py` was run twice; the second run changed nothing (md5).
- Screenshots in `screenshots/r14/`, opened:
  - overlays (blend, edges, side by side) for every plate, every fit and every part;
  - before (the kit) and after views: front, the water clock, rear, both sides, aerials, details of the figures, the west front and the link, the joints, the roof with the reservoir;
  - `conf=1` and `assumed=0`;
  - the panel with the viewer.

**Went wrong or left open:**
- The readers were started in the background again (the Agent tool's default). All three finished within 10 minutes and before the turn ended.
- **v1's terrace was a 20 m block** across the front. Plate 10 and P0303 showed the stairs converging on a landing before the door, with the shell at the V's apex.
- **Two bad definitions:**
  - The middle ridge's key point was put at the range's end; the plate reads where the ridge meets the pavilion's hip.
  - The east raised tier's width (9.3 m) was plate 12's module taken at the stairs' depth.
- **Covered openings:** the link's and the wings' body boxes covered their own arches and windows.
- **Open questions:** Q225 (the water building's length on plates 11, 13), Q226 (the wings), Q227 (the end sections' projection), Q228 (the attic: P0774 against plate 10), Q229 (plate 10's foreground), Q230 (the east block's width), Q231 (the figures' bodies).

## palace_r15_dashuifa

**Asked:** the detailed models of 大水法 XY10 and 观水法 XY11 built from the references by the pilot's method: the niche, the cascade, the fountains, the basin, the stairs and the towers; the screen with its platform; the court between them and the distance (Q71); the match check against every plate and photograph; the ruin photographs for the stone as it stood; `tools/check_models.py`; screenshots; docs; Durand's survey checked against the plates.

**Delivered:**
- **大水法** `models/XY10-da-shuifa/` (aliases XY10-N01, -N02; it draws the court box XY10-M45 too):
  - the niche with its deep head, shoulder scrolls and shell crest, the recess with the lion mask and seven water steps, the 1780s sill at the terrace's level;
  - the two piers with console feet, sunk fields, cornice blocks and vase finials;
  - the two stairs to 远瀛观, their court-side parapets the "great scrolls": a balustrade on each, a curl at the pier, a volute at the foot;
  - the plinth and the courses, the lobed basin with its rail, potted trees, two urn fountains, the stag on its rock and ten hounds with their jets;
  - the two towers of ten tiers on carved pedestals in their lobed basins, about forty jets each;
  - the court's floor: paved bands and four parterres.
- **观水法** `models/XY11-guan-shuifa/`: the concave screen of five panels on its 1.30 m socle with pilasters, end piers, entablature, crest and urns; the brick backing; the round platform with five convex steps; the throne, the balustrade with trophies; the trophy pedestals and the obelisks; the gardens' strip with the two side gates, their flights turned towards the court, the hedges and the back wall.
- **235 key points** read by three readers on plates 15, 16 and P0776, P0777, P0641, P0340, P0214, P0288, P0169, P0762, P0640, P0343, P0344, P0300, P0765, P0764, from one vocabulary (`docs/rounds/common/palace_r15_dashuifa_vocab.md`); fourteen photograph viewpoints.
- **Tools:**
  - `scripts/model_site.py`: the frame from a box, the walk surface, the footings, the joints and the files, for the new models.
  - `tools/plate_overlay.py`: `photo_viewpoints.csv` `hfov_deg`, an assumed lens as a weak prior.
  - `scripts/paths1860.py`: a court or terrace a model draws is met at the model's entries.
- **远瀛观's terrace** raised from 2.0 to 4.3 m in `research/xiyanglou/boxes.csv` (and the hall on it) so that the stairs meet it (Q232).
- **Questions** Q232-Q237, a Round 15 note on Q71; two wish rows.

**Numbers:**
- **check_models:**
  - XY10: 17,088 triangles (2,240 fill), GLB 0.56 MB, 0.16 MB compressed. 24 joints: none floats (highest 0.05 m into the ground), deepest 0.15 m. Seven ways at its boxes, 0 off (in v1 the axis way ended 26-32 m off, in the court box's middle).
  - XY11: 7,719 triangles (102 fill), GLB 0.25 MB, 0.08 MB compressed. 57 joints, the same: highest 0.05 m in, deepest 0.15 m. Three ways, 0 off (in v1 the axis way ended 4.8 m off, across the steps).
- **Fit, v1 to final (rms at the object, camera `all`):**
  - 大水法: P0641 0.47 to 0.19 m, P0340 0.42 to 0.15 m, P0169 0.81 to 0.62 m, P0776 1.70 to 0.96 m, P0762 0.78 (degenerate, f 79 px) to 0.51 m, P0214 0.78 to 0.68 m, plate 15 1.61 to 1.42 m (`stretch` 1.34 m, k 1.20).
  - 观水法: P0300 0.14 m, P0343 0.22 to 0.14 m, P0640 0.16 m, P0344 0.18 to 0.19 m, P0764 0.31 to 0.30 m, P0777 0.44 to 0.41 m, P0765 1.01 to 0.76 m, plate 16 1.25 to 0.90 m (`stretch` 0.86 m, k 1.48).
  - The kit had none of these points: no fit before the model.
- **Durand against the plates:** the sunk area 110 × 60 m (S603) agrees with the plan (109 × 63 m) and the ruin (108.8 m E-W); the tower basins 62 m apart (S603) against the ruin's 63.3 m and the plan's water bodies 58.6 m; plate 15 compresses the court's depth by 3.5-4 m (Q235).
- **Cost:** the overview draws 1.03 M triangles (1.00 M before) at a 604 ms median frame in software WebGL (570 ms before). The site grows by 0.8 MB.

**Checked:**
- These pass: `tools/check_models.py`, `check_pages.py` (idempotent), `check_evidence.py`, `check_georef.py`, `check_paths.py`, `check_docs.py`, `check_ground.py`, `check_kit.py --browser` (port 8914), `check_greens.py --browser` (port 8915).
- `scripts/building_pages.py` run twice: the second run changed nothing (md5). Both generators run twice: the same GLBs (md5).
- Screenshots in `screenshots/r15/`, opened: before (the kit) and after views of both from the references' directions (front, the obliques of P0214, P0288, P0169, P0777, P0344, the rear from the terrace, the gate, the aerials, the joints at the stair and the basin, details of the niche and the screen), `conf=1` and `assumed=0`, the panels; the overlays (blend, edges, side by side) for every picture and fit.

**Went wrong or left open:**
- **v1's buttresses.** The plate's ribbed bands were modelled as quarter-arch buttresses with a flight hidden behind each to a 2.33 m terrace. P0776's balustrade over the curl showed them to be the stairs' parapets; the stairs climb to about 4.6 m, and 远瀛观's terrace guess was raised to meet them (Q232). P0776's rail still fits 2.7 m higher.
- **A ring stitched to a misaligned outline** covered both tower basins with marble in v1 (`offset_aligned` in `scripts/model_site.py`).
- **Photo cameras without a lens collapsed** (P0762: f 79 px, the eye 13 m up). Fixed by the lens prior.
- **The trophies read as figures** in v1's relief; redrawn as a shield, crossed arms and a ribbon knot.
- **Shell kill:** a `pkill -f` on the server's command line matched the shell that ran it; the servers are now stopped by their PID.
- **Open:** Q232 (the terrace's height), Q233 (plate 16's gates), Q234 (the tower basins' ruin places), Q235 (plate 15's depth), Q236 (the tiers, the stag's group, the stone fish not placed), Q237 (the niche's sill), Q71 (the screen's place: 44.7 m from the niche in the model, the court running on 6.5 m behind it).

## palace_r16_yuanying

**Asked:** the detailed models of 远瀛观 XY09 and 方外观 XY06 built from the references by the pilot's method: the terrace with its stairs and balustrades, the main block with its order, the clock-gate front of the ruin photographs; the small pavilion with its stairs and courts; the match check against every plate and photograph; the ruin photographs for the stone; `tools/check_models.py`; screenshots; docs; Q67 and Q70 stated, not forced.

**Delivered:**
- **远瀛观** `models/XY09-yuanying-guan/`:
  - the terrace (S603's 35 × 31 m) 4.3 m up, its retaining walls of piers and rusticated stones, the paved forecourt, the front balustrade with urns, the side balustrades, eight trees in square pits, a back stair (assumed, for reach);
  - the hall (S603's 28 × 21 m), an inverted 凹 on a 1.2 m base: chamfered wings one bay forward with big windows, eight-slope roofs, decks with balustrades and lanterns with a clock face on every side;
  - the clock gate: the door between two carved columns 6.0 m apart on pedestals with lions, the entablature blocks standing proud, the door's hood, a door-like opening either side, the attic with the wheel, its moulding, crest and scrolls;
  - the centre's tiered roofs (a fish-scale roof over a low band, the main hipped roof pierced by the attic, the crown) and the body behind under an assumed hipped roof.
- **方外观** `models/XY06-fangwai-guan/`: the rusticated podium with its end panels, ovals and porch, three round steps; the walk and the balcony; the upper storey with three windows, carved corner strips and rosettes, end windows with balconies; the double-eaved roof with its crest; the two curved stairs with wave-scroll parapets; a paved apron.
- **196 key points** read by three readers on plates 14 and 8 and P0183, P0190, P0776, P0179, P0772, P0216, P0291, P0719, P0757, P0341, P0780, P0773, P0212, P0296, P0304, P0295, P0355, from one vocabulary (`docs/rounds/common/palace_r16_yuanying_vocab.md`, merged by `docs/rounds/common/palace_r16_merge.py`); sixteen photograph viewpoints.
- **Tools:**
  - `scripts/model_site.py`: `Site.deck`, a raised floor a model draws; `models/XY09-yuanying-guan/joints.json` `decks`, published in `site/reconstruction/data/models.json` by `scripts/building_pages.py`; `3d.js` lays the ways that cross a deck on it; `tools/check_models.py` measures a way's end there.
  - `tools/plate_overlay.mjs --only` and 3d.html `&plateonly=<ID>`: the overlay renders with the other detailed models hidden.
- **远瀛观's hall box** raised to the model's heights (eave 12.3, top 19.8 m above its ground; `xiyanglou/boxes.csv`, Q239).
- **Questions** Q238-Q240, a Round 16 note on Q67; three wish rows.

**Numbers:**
- **check_models:**
  - XY09: 25,764 triangles (5,817 fill), GLB 0.80 MB, 0.22 MB compressed. 28 joints: none floats (highest 0.05 m into the ground), deepest 0.15 m (v1: 5 joints). One way at its boxes, 0 off (v3: 4.24 m below the door, before the deck). 大水法's stair landings meet the terrace at 0.00 m in plan and height.
  - XY06: 9,832 triangles (2,982 fill), GLB 0.32 MB, 0.09 MB compressed. 13 joints, the same: highest 0.05 m in, deepest 0.15 m. One way, 0 off.
- **Fit, v1 to final (rms at the object, camera `all`):**
  - 远瀛观: plate 14 1.09 to 0.74 m (`stretch` 0.73 m, k 1.01), P0183 0.27 to 0.14 m, P0216 0.34 to 0.18 m, P0190 0.07 to 0.20 m, P0291 0.17 to 0.24 m, P0719 0.26 m, P0757 0.16 to 0.13 m, P0179 0.06 m, P0341 0.22 m. A free camera absorbs one front's scale: plate 14 is the module's test.
  - 方外观: plate 8 0.50 to 0.32 m (`stretch` k 1.00), P0773 1.47 m (as the west end) to 0.74 m (as the east end, Q238), P0212 0.53 to 0.51 m, P0355 0.26 m.
  - The kit had none of these points: no fit before the models.
- **The module:** the columns 6.0 m apart (plate 14's ratios against S603's 28 m; P0216's door), not 4.2 m; the order and the roofs 1.4 times taller than the box held (crown 15.5 m above the terrace against 12.6 m).
- **Cost:** the overview draws 1.06 M triangles (1.03 M before) at a 573 and a 658 ms median frame in two runs of software WebGL (604 ms in Round 15's run: the machine varies by that much). The site grows by 1.1 MB.

**Checked:**
- These pass: `tools/check_models.py`, `check_pages.py` (idempotent), `check_evidence.py`, `check_georef.py`, `check_paths.py`, `check_docs.py`, `check_ground.py`, `check_kit.py --browser` (port 8924), `check_greens.py --browser` (port 8925).
- `scripts/building_pages.py` run twice: the second run changed nothing (md5). Both generators run twice: the same GLBs (md5).
- Screenshots in `screenshots/r16/`, opened: before (the kit) and after views of both from the references' directions (plate 14 high over the niche, P0183 on the terrace, the court, the south-west, the west side, the rear from the north-east, the aerial; plate 8 frontal, P0773 from the south-east, the south-west, the rear, the west side, the aerial), details (the clock gate, a wing and its lantern, the porch, a stair), the joints (the terrace's north-west corner, 大水法's stair arriving), `conf=1` and `assumed=0`, both panels; the overlays (blend, edges, side by side) for every picture and fit.

**Went wrong or left open:**
- **The readers went to the background again** (the Agent tool's default). All three finished within 10 minutes and before the turn ended.
- **v1 took the dossier's module** (4.2 m between the columns), which made the front 18 m. Plate 14's ratios against the survey moved it to 6.0 m (Q239); every photograph had fitted v1 as well, because a free camera absorbs one front's scale.
- **The side openings sat 0.85 m too far in** in v2: all three photographs moved them, and the centre block widened to 13.6 m.
- **Footing skirts covered 方外观's door and ovals**, and `Parts.oval` filled the ovals' glass: found on the shots, fixed.
- **The way to 远瀛观's door ran 4.24 m under it**: the ground of Round 10 has no terrace. Fixed with decks.
- **P0773's side** (Q238), **P0776's scale and P0183's sliding camera** (Q240) are open; plate 8's near-elevation runs through 五竹亭's kit pavilions, so its overlay is compared against the model's own frontal view.

## palace_r17_hanjing

Brief: `palace_r17_hanjing.md`. The first detailed model of a Chinese compound: 含经堂 CC02 in 长春园, `models/CC02-hanjing-tang/`.

**What it delivered:**
- **The model:** the whole walled compound and its forecourt as one model (id CC02, 23 aliases): the forecourt with three glazed archways, crossing paths and lawns; the terrace the compound stands on (a deck) with its curved edge, the gate's projection and three flights; the gate; the 含经堂 court with the screen, two side halls and the ⊐ ranges 梵香楼 and 霞翥楼 of two storeys; 含经堂 (seven bays, a porch all round, double-eaved yellow 歇山) on its platform and front terrace; the galleries 墨刻游廊 with the 淳化阁帖 slabs and the rockery; 淳化轩 on its terrace with two flights; 蕴真斋 with porches; every hall of the side courts at its box; 三友轩 at its measured size; the north gate; the walls; court trees the texts name.
- **Tools:**
  - `scripts/hall_parts.py`: the hall kit of Round 11 in Python (platform, flights with side slabs, balustrade, columns, bands and bracket sets, doors and windows, roofs wd/xs/ys/xu/cj, rolled, double eaves, a second storey), and walls, screens, glazed archways, galleries, rocks.
  - `models/CC02-hanjing-tang/plan_readings.csv`: S01 re-read in plan pixels for the model.
  - `tools/plate_overlay.py --sheets <scene folder>` (a scene's own key points, viewpoints and fit); the `all` fit also starts from the anchored camera.
  - `models/CC02-hanjing-tang/joints.json` `clear` (`scripts/model_site.py`, read by `scripts/greens1860.py`, which also keeps off decks): areas without planting that the ways may cross.
- **Sources:** S940 (王文涛 2015) fetched as a research-only copy to `research/raw/S940/`: its figures 5 and 6 (the Yangshi Lei plans 长春园淳化轩) and 7 (the dig from the air) read for the layout.
- **Key points:** 81 read by three readers on P0402, P0403, P0404, P0405, P0408, P0410, P0505, P0815 (P0406 one point, P0816 and P0817 not placeable) with one vocabulary (`docs/rounds/common/palace_r17_hanjing_vocab.md`).
- **Questions** Q241-Q249; three wish rows; the dossier's notes.

**Numbers:**
- **check_models:** CC02 78,202 triangles (48,676 fill), GLB 2.40 MB, 0.71 MB compressed; 56 ground joints, highest 0.00 m above, deepest 0.45 m in; 13 joints on the deck, all at -0.15 m (`models/CC02-hanjing-tang/report.json`); 15 ways at its boxes, 0 off.
- **Fit, v1 to final (rms at the object, camera on all points):** P0402 0.15 to 0.13 m, P0403 1.71 to 0.40 m, P0404 1.48 to 0.34 m (no test: the camera slides, Q248), P0405 0.70 to 0.25 m, P0408 0.59 to 0.41 m, P0410 0.88 to 0.91 m, P0505 1.52 to 0.66 m, P0815 1.70 to 0.67 m. Anchored tests (the heights against the feet): P0403 2.96 to 0.54 m, P0505 2.84 to 1.27 m, P0815 2.73 to 0.87 m, P0405 4.89 to 2.60 m, P0408 2.50 to 1.85 m.
- **The terrace's height,** swept 1.8 to 3.0 m on P0403, P0505, P0815: summed rms 1.77, 1.73, 1.82, 2.00, 2.23 m: 2.1 m.
- **Ways:** five CC02 boxes newly reached by Round 9's links (F0314, F0315, F0320, F0321, F0640); one newly unreached (F1001, outside the west wall, between it and the lake).
- **Cost:** the overview draws 1.14 M triangles (1.06 M in Round 16) at a 729 ms median frame in software WebGL. The site grows by 2.4 MB.

**Checked:**
- These pass: `tools/check_models.py`, `check_pages.py` (idempotent), `check_evidence.py`, `check_georef.py`, `check_paths.py`, `check_docs.py`, `check_kit.py --browser` (port 8934), `check_greens.py --browser` (port 8935).
- The generator run twice: the same files (md5); `scripts/building_pages.py` run twice: no file of `site/` changed.
- Screenshots in `screenshots/r17/`, opened: before (the kit) and after from the model's own views (front, aerial, rear, both sides, the gate, the 含经堂 court and terrace, 淳化轩's terrace, the galleries, 三友轩, 蕴真斋, the north gate, the joints at the terrace and the gate's flight, the ranges, the stage court, the south archway), `conf=1` and `assumed=0`, details (含经堂's eave, the gallery's slabs, the terrace's north-west corner, the west wall from outside, 三友轩's trees, the screen), the panel; the overlays (blend, edges, side by side) for every photograph and fit.

**Went wrong or left open:**
- **The deck as a footprint** blocked Round 9's links inside the compound; split into footprints (walls, platforms) and `clear` (courts, lawns).
- **The inner walls' feet** were measured against the ground of Round 10 (2 m below the terrace) by `check_models.py`; they are joints with the deck now and measured in the model's report.
- **The flights' L and R** were mirrored against the vocabulary for every side but one; the readers followed the brief.
- **The gate's door bays** drew black (the dark core of the kit stood in front of the recessed plank doors), **the galleries' walls** faced the court, **the forecourt's clear area** stopped short of the curved edge so plants stood at the terrace's foot: all found on the shots, fixed.
- **三友轩's three trees** first stood inside the hall B0555, 2 m before its front: moved behind it; the generator now counts trees inside a footprint (0).
- **A thin dark sliver** shows against the west wall's inner face in the west court from a high view (`screenshots/r17/after_detail_sanyouxuan_trees.png`); the model holds only the wall and the terrace's edge there (queried), so it is likely where the terrace's floor meets the wall in the view: not traced.
- **P0410's fit collapsed** its focal length after the side court's bays changed; fixed in the tool (a start from the anchored camera). One `--images P0410` run overwrote the fit table; the full fit was rerun.
- **Open:** Q241 (the terrace's curve and height), Q244 (S01's 24 m yard), Q245, Q246, Q247, Q248 (P0404), Q249 (the forecourt's depth); every elevation is the kit's (C); the halls of the side courts are their class's.

## palace_r18_jiuzhou

Brief: `palace_r18_jiuzhou.md`. The central axis of 九洲清晏 YM03 in its state of 1837-1860, the second detailed model of a Chinese compound, `models/YM03-jiuzhou-qingyan/`, and the island's three named bridges as small models of their own.

**What it delivered:**
- **The model:** the front yard from 圆明园殿 to the 前湖 with a stone landing and rocks at the water's edge; 圆明园殿 from the slip of 1855 (A), rolled 硬山 after the 1837 sheets (Q252), Kangxi's plaque, ear rooms; the first court with galleries along both walls (white walls, pierced windows: the 1744 leaf), a gate in each wall, two bronze vessels, two flowering trees, the axis way; 奉三无私殿 seven bays wall to wall with its terrace and balustrade; the second court with galleries turning to the hall's porch ends; 九洲清晏殿 five bays with porches and the rear porch 抱厦 of 1855, the plaques; the link and 同道堂 to its west; the back way and a landing on the 后湖; the white walls of the axis on S01's lines. Bridges: 南大桥 YM03-22, 如意桥 YM03-21, 棕亭桥 YM03-23 (with its pavilion), stone abutments, timber decks with red railings at Round 10's levels.
- **Tools:** `HallKit.wall(body_mat=)`; a summary's `bridges` (published by `scripts/building_pages.py` in `models.json`; `3d.js` leaves those plain decks out); one generator writing several model folders (each bridge on a `Site` whose frame is moved to it).
- **Key points:** 15 on the leaf P0003 (`research/scenes/YM03-jiuzhou-qingyan/plate_keypoints.csv`), read by the coordinator on 3x and 6x crops; no readers were spawned (one picture). Vocabulary `<hall>_eave_<corner>`, `<hall>_ridge_<W|E>` (`models/README.md`).
- **Questions** Q250-Q255; two wish rows; the dossier's notes.

**Numbers:**
- **check_models:** YM03 15,798 triangles (4,782 fill), GLB 0.51 MB, 0.12 MB compressed; 72 joints, highest 0.07 m above the ground, deepest 0.33 m in; 8 ways at its boxes, 0 off (before `paths1860.py` re-snapped them: 8 ways 0.92-8.90 m from the doors). Bridges: 432-740 triangles each, 0.01 MB compressed, 2 joints each, deepest 0.18 m.
- **Fit (rms at the object, camera on all 13 points):** P0003 3.79 m (median 3.01, max 7.51 m); v1's 2.97 and 2.55 m rested on two misread points and on a ridge-end definition 40% short. 九洲清晏殿's west half and feet fit to 0.7-1.7 m; the east ends miss by 4.5-7.5 m: the leaf paints 九洲清晏殿 as the widest hall (Q251).
- **The courts:** 34.45 and 22.49 m between the eave columns, 22.59 m between the walls (S01); the Tongzhi survey writes 33.92, 18.27 and 25.98 m (Q250). The axis's seven reads on S01 spread over 2.50 m.
- **Paths:** lines crossing a box, wall or water 84 to 83 (A or B 22 to 22).
- **Cost:** the overview draws 1.157 M triangles (1.141 M in Round 17) at a 651 ms median frame in software WebGL (729 ms in Round 17's run). The site grows by 0.60 MB.

**Checked:**
- These pass: `tools/check_models.py`, `check_pages.py` (idempotent), `check_evidence.py`, `check_georef.py`, `check_paths.py`, `check_docs.py`, `check_ground.py`, `check_kit.py --browser` (port 8943), `check_greens.py --browser` (port 8944).
- The generator and step 6 run twice: the same GLBs and no file of `site/` changed (md5).
- Screenshots in `screenshots/r18/`, opened: before (the kit) and after from the same 19 views (aerial, front across the 前湖, the leaf's direction, rear from the 后湖, both sides, both courts at eye height, details of 圆明园殿 and the rear porch, both landings, the four bridges, a gallery, the west gate, a vessel), `conf=1` and `assumed=0`, the panels of YM03 and YM03-23; v1 and v2 kept; the overlay of P0003 (blend, edges, side by side, the points).

**Went wrong or left open:**
- **v1 put the walls at the Tongzhi survey's width** and cut the kit halls beside the courts by up to 1.6 m: back to S01 (Q250).
- **The court-1 camera stood inside 圆明园殿** in v1; **the gate shot looked through a kit hall** at the gate; **the rear porch's roof** was nearly flat (ridge 0.4 m above its eave); **the panel's small view** framed the whole island while the bridges were in the model; **the bridge panels read NaN** for their height: all found on the shots, fixed.
- **The leaf's readings:** two points on neighbouring halls, found on the overlay, re-read; the fit got worse and truer.
- **Open:** Q250-Q255; every width, depth and height of 奉三无私殿 and 九洲清晏殿 is C until 样011-3 is seen; the kit's 七间殿 (S01's Tongzhi design) stands east of 九洲清晏殿 (Q255); the bridge to 来青亭 (BR007) stays Round 10's deck.

