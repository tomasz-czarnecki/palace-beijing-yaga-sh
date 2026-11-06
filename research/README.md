# Research

Evidence base for the 3D reconstruction of the Old Summer Palace (圆明园 Yuanmingyuan), target state just before October 1860.
Rule: nothing goes into the model without a source.

Field names here are checked against the real files by `tools/check_docs.py`. Counts are as of Round 5; the checks and generators print the current ones.

## Files

| Path | What | Written by | In git |
|---|---|---|---|
| `sources.md` | catalogue of every source | hand; first by the coordinators | yes |
| `questions.md` | open questions and conflicts between sources; Q1 is the target state | hand | yes |
| `wishlist.md` | what would replace the biggest guesses, where it is held, how to ask | hand | yes |
| `buildings.csv` | one row per compound and per hall or structure inside it | `scripts/build_r1.py`, then `scripts/apply_facts.py`. Change their inputs, not the rows | yes |
| `layers/` | working GeoJSON in WGS84, the hand-off to the 3D round | `scripts/build_r1.py`; `osm_today` from `scripts/fetch_osm.py`, `osm_ring_today` from `scripts/fetch_osm.py --ring` (Round 20); `surroundings_1860` from `scripts/surroundings1860.py` | yes |
| `plan/` | everything read off the base plan S01, in plan pixels | see below | yes |
| `georef/` | how the plan is tied to the ground | see below | yes |
| `typology/` | `halls.md`, `params.json` (defaults by hall class, each with a source and a confidence), `rules_out.json`, `scale_check.json` | hand and `scripts/typology_*.py` | yes |
| `terrain/` | Round 10, the ground: `terrain/README.md` (what is measured, read and typology, the error by region, what the DEM can and cannot tell), `terrain/readings.csv` (the workers' rows) and the files below | hand (the README, the readings); `scripts/terrain_dem.py`, `scripts/hills1860.py`, `scripts/ground1860.py`, `tools/check_ground.py` | yes |
| `kit/` | Round 11, the hall kit and the stone kit: `kit/README.md` (what is drawn, from which numbers, what is sourced, the cost), `kit/kit_check.json`, `kit/kit_browser.json`, `kit/kit_report.json` | hand (the README); `tools/check_kit.py` | yes |
| `greens/` | Round 12, the planting: `greens/README.md` (what the sources say, what the view draws, the numbers, what is weak), `greens/species.csv` (the rows), `greens/greens_report.json`, `greens/greens_check.json`, `greens/greens_browser.json` | hand (the README, the rows); `scripts/greens1860.py`, `tools/check_greens.py` | yes |
| `surroundings/` | Round 20, what stood and ran round the gardens: `surroundings/README.md` (the sources by topic, where they disagree, the extent), `surroundings/features.csv` and `surroundings/geometry.geojson` (the sheet), `surroundings/about.json` (the public page's text), `surroundings/report.json`, `surroundings/check.json` | hand (the README, the sheet, the text); `scripts/surroundings1860.py`, `tools/check_surroundings.py`; first made by `docs/rounds/common/palace_r20_merge.py` | yes |
| `photos/` | the picture catalogue and free images, see `photos/README.md` | hand | yes |
| `evidence/` | what is not an image, see below; `evidence/coverage_before_r5.json` the coverage before Round 5, which `tools/check_evidence.py` compares with | hand | yes |
| `twins/catalog.csv` | surviving buildings that are copies, sisters, models or fair comparables of ours, see below | hand, from Round 5 | yes |
| `reconstructions/catalog.csv` | reconstructions by other people, see below | hand, from Round 5 | yes |
| `xiyanglou/` | Round 6, the European palaces in depth: one dossier per main building, the sheets they draw on. See below | hand; `scripts/xiyanglou_dossiers.py` | yes |
| `paths/` | Round 9, the ways of 1860: the readers' traces, the sources read, grades, routes, exceptions. See below | hand; `scripts/paths1860.py`, `tools/osm_paths.py` | yes |
| `scenes/` | Round 7, every other scene and compound: one dossier each, the sheets they draw on, the typology check. See below | hand; `scripts/scenes_dossiers.py` | yes |
| `reconstructions/images/` | free reconstructions, at most 1600 px and about 300 KB | by hand with the catalogue | yes |
| `buildings/` | one page per row of `buildings.csv` and per gate; `buildings/README.md` the list | `scripts/building_pages.py`, except each page's `## Notes` | yes |
| `image-credits/CREDITS.md` | the credit of every public picture | `scripts/photos_catalog.py`, between markers | yes |
| `raw/` | downloaded originals and local builds | `plans/`, `dem/`, `osm/`, `photos/` (research-only), `reconstructions/` (research-only copies), `buildings/`, `plancrops/`, `plates/` (the 20 plates at full size) | **never** |
| `overlays/` | `princeton-1920s.jpg` + `.json` (bounds for a Leaflet imageOverlay) | `scripts/georef.py overlay` | **never** |

### plan/

| File | What | Written by |
|---|---|---|
| `bridges_manual.json`, `classes_manual.csv`, `walls_manual.json`, `gates_manual.json`, `slips_manual.json` | manual inputs of the tracer, picked by eye | hand |
| `regions.json`, `regions_classified.csv`, `blocks.csv`, `walls.json`, `gates.json`, `slips.json`, `trace_summary.json` | traced regions, detected hall rectangles, walls, gates, pasted slips | `scripts/trace_plan.py` |
| `readings/<area>/` | five readers (`ym_west`, `ym_central`, `ym_east`, `cc_xyl`, `qc`): `compounds.csv`, `named.csv`, `blocks_fix.csv`, `features.csv`, `notes.md` | hand |
| `inventory_texts.csv` | rows from the texts, with the quotes in `rel_position` | hand, Round 1 |
| `osm_points.csv`, `hills_texts.csv` | OSM's hand-placed points; hills named in the texts | hand, Round 1 |
| `photos_raw.csv` | what the picture catalogue started from in Round 1; no longer used | hand, Round 1 |
| `new_ids.csv`, `coverage.json` | ids given to compounds read on the plan only; the counts | `scripts/build_r1.py` |

Columns:
- `blocks.csv`: `block_id`, `cx`, `cy`, `w_px`, `h_px`, `angle_deg`, `cells`, `ncols`, `nrows`, `score`, `note`.
- `classes_manual.csv`: `x`, `y`, `class`, `name_zh`, `confidence`, `note`, `seen_as`. `regions_classified.csv`: `region_id`, `class`, `name_zh`, `confidence`, `note`.
- `readings/*/compounds.csv`: `id`, `name_on_plan`, `read`, `plan_x`, `plan_y`, `polygon_px`, `malone_no`, `note`.
- `readings/*/named.csv`: `id`, `parent_id`, `name_on_plan`, `read`, `block_ids`, `plan_x`, `plan_y`, `ncols`, `nrows`, `orientation_note`, `note`.
- `readings/*/blocks_fix.csv`: `block_id`, `action` (add, reject, resize, `merge:B####`), `x`, `y`, `w_px`, `h_px`, `angle_deg`, `note`.
- `readings/*/features.csv`: `kind` (bridge, gate, water_fix, water_name, hill, hill_name, island_name, slip), `id`, `name_on_plan`, `read`, `x1`, `y1`, `x2`, `y2`, `region_id`, `note`.
- `inventory_texts.csv`: the name, date and form columns of `buildings.csv`, with `sources` and `confidence`.
- `hills_texts.csv`: `name_zh`, `name_pinyin`, `lat`, `lon`, `height_est_m`, `height_method`, `sources`, `confidence`, `note`.
- `osm_points.csv`: `osm_id`, `name`, `lat`, `lon`, `kind`, `proposed_building_id`, `trust`, `note`.
- `new_ids.csv`: `reader_id`, `id`.
- `photos_raw.csv`: the columns of `photos/catalog.csv` without `crop`.

### georef/

- `princeton-mosaic.json`: how the three scrolls are stitched.
- `princeton-1920s.json`: **the fit in use (Round 8)**: the transform, the candidates' leave-one-out by region (`comparison`), the smoothing per region (`chosen`), the frozen check set's errors under the previous fit, a plain affine, the new fit and the fit in use (`check`: `by_model`, `points`), what each region keeps (`decisions`), block cross-validation, `per_region_verdict`, the control points excluded near a check point, per-point residuals. Every figure comes from `scripts/georef.py fit`, which also exposes `plan_to_wgs84(xs, ys)` and `wgs84_to_plan(lons, lats)`.
- `princeton-1920s.previous.json`: the Round 1 fit, kept as `previous`; `scripts/georef.py previous` rebuilds it byte for byte from `princeton-1920s.csv`.
- `princeton-1920s.csv`: the control points of Round 1, see below.
- `control_r8.csv`: Round 8's control points read by eye, same columns; `control_shapes.csv`: Round 8's control points derived by `scripts/control_derived.py` (lakes that keep their outline, laid on today's by a shift; the Xiyang Lou blocks on their ruins). In both, `use` is `fit` or `excluded`, and a point within 60 m of a check point never enters a fit.
- `check_points.json`: **the blind check set**, frozen: `rule`, `datum`, `exclusion_m`, `points` (`id`, `region`, `reader_region`, `kind`, `feature`, `lon`, `lat`, `plan_x`, `plan_y`, `plan_read`, `ground_from`, `unchanged_because`, `sources`, `note`), `not_admitted` (broke the readers' rule, with the `reason`, set aside before any error was computed), `annotations` (doubts written after freezing; the points never change), `sha256`, `frozen`. Written by `scripts/georef_readings.py` from `readings_r8/`, frozen by `scripts/georef.py freeze`.
- `readings_r8/*.jsonl`: the readers' own lines, one point each, as they wrote them (`set` check or control; the fields of the check set).
- `check_baseline.json`: the check set's figures by region when the fit was last made on purpose; `tools/check_georef.py` fails if a region's median gets worse.
- `shift_r8.json`: what the refit of Round 8 moved (`tools/georef_shift.py`); `shores_r8.json`: today's lakes against the traced water, before and after (`tools/shore_check.py`).

### georef/princeton-1920s.csv

159 rows: 111 `fit`, 17 `check`, 14 `check-first-pass` (kept so the unedited first check stays visible, Q7), 17 `rejected`.

| Field | Meaning |
|---|---|
| `id` | point id |
| `plan_x`, `plan_y` | pixel on the mosaic |
| `lat`, `lon` | WGS84 |
| `datum` | how WGS84 was reached: `WGS84 via Esri` or `WGS84 via OSM` |
| `feature`, `kind` | what it is; `kind` is shore, ruin, island, wall or junction |
| `area` | YM-west, YM-fuhai, YM-houhu, QC, CC-lakes, XYL, walls |
| `quality` | 1 or 2; quality 2 points fit at half weight |
| `use` | `fit`, `check`, `check-first-pass`, `rejected` |
| `note` | the reason, for every rejected point |

## Rebuild order

```
uv run python scripts/fetch_osm.py            # research/raw/osm, layers/osm_today (network)
uv run python scripts/fetch_osm.py --ring     # Round 20: research/raw/osm/overpass_ring.json, layers/osm_ring_today (the ring round the gardens, network)
uv run python scripts/clip_dem.py             # research/raw/dem/site_glo30.npz (needs the tiles in raw/dem)
uv run python scripts/terrain_dem.py          # terrain/plain.json, terrain/glo30_rise.npz: the plain, today's rises (needs raw/dem)
uv run python scripts/mosaic_plan.py          # raw/plans/princeton_mosaic.jpg, georef/princeton-mosaic.json
uv run python scripts/trace_plan.py           # plan/regions.json, blocks.csv, walls.json, gates.json, ... (needs scipy)
uv run python scripts/georef.py previous      # georef/princeton-1920s.previous.json: the Round 1 fit, from princeton-1920s.csv alone
uv run python scripts/georef_readings.py      # georef/check_points.json (refuses to change a frozen set), georef/control_r8.csv, from georef/readings_r8/
uv run python scripts/control_derived.py      # georef/control_shapes.csv (needs the layers built with the fit in use)
uv run python scripts/georef.py               # the same as `fit`: georef/princeton-1920s.json, scored on the frozen check set
uv run python scripts/georef.py overlay       # overlays/princeton-1920s.jpg + .json
uv run python scripts/georef.py images        # screenshots/r8/georef_residuals.png (no plan image), georef_overlay.jpg (local)
uv run python scripts/typology_rules.py       # typology/rules_out.json
uv run python scripts/typology_scale_check.py # typology/scale_check.json
uv run python scripts/build_r1.py             # buildings.csv, layers/*_1860, plan/coverage.json, plan/new_ids.csv
uv run python scripts/apply_facts.py          # buildings.csv: what evidence/facts.csv adds to the rows
uv run python scripts/render_r1.py            # screenshots/r1/layers_public.png, public-safe
uv run python scripts/coverage_chart.py       # screenshots/r1/coverage.png
uv run python scripts/georef.py accuracy      # layers/georef_error.geojson: expected error by region and 200 m cell, from the check set
uv run python scripts/hills1860.py            # layers/hills_1860 (heights; the free land's hills), terrain/hills_heights.csv, terrain/rockeries.csv; reads the last run's boxes and ways
uv run python scripts/surroundings1860.py     # Round 20: layers/surroundings_1860, the lakes and paddies outside the walls into water_1860 and fields_1860 (`outside`), data/around_1860.json, surroundings/report.json
uv run python scripts/publish_layers.py       # site/reconstruction/data/: the public layers, buildings_1860, labels_1860, georef_error
uv run python scripts/ground1860.py           # site/reconstruction/generated/: ground.json, ground.bin, ground_grid.i16, ground_level.u8; terrain/water_levels.csv, ground_report.json (imports the box layout of boxes1860.py)
uv run python scripts/ground_outer1860.py     # Round 20: generated/ground_outer.json and .bin, the ring and the backdrop beyond the inner ground; terrain/ground_outer_report.json (needs raw/dem)
uv run python scripts/boxes1860.py            # data/halls_1860.geojson, generated/structures.json (walls, bridges); prints its checks
uv run python models/XY01-xieqiqu/xieqiqu.py  # Round 13: the detailed model of 谐奇趣 (model.glb, params, keypoints, joints, summary); reads the boxes
uv run python models/XY08-haiyan-tang/haiyantang.py  # Round 14: the detailed model of 海晏堂, the same files; reads the boxes and the ground (its footings follow it)
uv run python models/XY10-da-shuifa/dashuifa.py    # Round 15: 大水法 (with its court's floor), on scripts/model_site.py
uv run python models/XY11-guan-shuifa/guanshuifa.py # Round 15: 观水法 with the gates and the gardens' strip
uv run python models/XY09-yuanying-guan/yuanyingguan.py # Round 16: 远瀛观 with its terrace (a deck the ways lie on), on 大水法's axis
uv run python models/XY06-fangwai-guan/fangwaiguan.py   # Round 16: 方外观 with its curved stairs
uv run python models/CC02-hanjing-tang/hanjingtang.py   # Round 17: 含经堂, the walled compound on its terrace (a deck; `clear` for the planting), on scripts/hall_parts.py and model_site.py; reads plan_readings.csv, the boxes, the kit's entries (kit_1860.json, so after kit1860.py once) and the ground
uv run python models/YM03-jiuzhou-qingyan/jiuzhouqingyan.py   # Round 18: 九洲清晏's axis (圆明园殿, 奉三无私殿, 九洲清晏殿 with the 1855 rear porch, courts, galleries, landings), and the bridges YM03-21, -22, -23 as their own models; reads plan_readings.csv, the boxes, structures.json (the bridges' decks) and the ground
uv run python models/YM01-zhengda-guangming/zhengdaguangming.py   # Round 19: 正大光明's approach (大宫门 with its terrace and lions, the inner court, the canal and its bridge, 出入贤良门, the court, 正大光明殿 on its terrace), and 勤政殿 YM02-01 and the spirit wall YM41-12 as their own models; reads plan_readings.csv, the boxes, kit_1860.json, ground.json and water_1860 (W0364)
uv run python models/YM29-fanghu-shengjing/fanghushengjing.py   # Round 24: 方壶胜境 (the lower terrace on the inlet with its bastions, the upper terrace, nine two-storey towers in three ranges, the galleries, the causeway with its archways, 迎薰亭 and the two cruciform terraces with their pavilions), on scripts/hall_parts.py and model_site.py; reads plan_readings.csv and the water level of W0365 (research/terrain/water_levels.csv)
uv run python models/YM46-wenyuan-ge/wenyuange.py   # Round 25: 文源阁 (the walled court: the library from the 丈尺册's bays with its galleries, skirt roof and upper storey, the 月台 on the pool, 玲峰 on its terrace, the stele pavilion, the rockeries with 趣亭, the wall and gates; the court a deck); its storeys from measure.py (run by hand: a camera and the heights fitted together on the sister 文渊阁's photograph P0555, measure.json)
uv run python scripts/paths1860.py            # layers/paths_1860, landings_1860, routes_1860 and their copies in data/; paths/bridge_ends.csv, dangling.csv, unreached.csv; prints its checks
uv run python scripts/kit1860.py              # data/kit_1860.json (how the kit draws each box), generated/courts.bin (the courts); reads the boxes, the ways and the dossiers
uv run python scripts/greens1860.py           # layers/greens_1860 and data/greens_1860.geojson (areas, rockeries), data/greens_1860.json, generated/greens_1860.bin (one record per plant), greens/greens_report.json; reads species.csv, the boxes, ways, walls, courts and the ground
uv run python tools/osm_paths.py              # paths/osm_judged.csv: today's park paths judged, never evidence
uv run python scripts/photos_catalog.py       # site/reconstruction/photos/, credits (from photos/catalog.csv)
uv run python tools/plan_crops.py             # raw/plancrops/<ID>.jpg, local only; needs the mosaic
uv run python scripts/xiyanglou_dossiers.py   # research/xiyanglou/<ID>-<slug>/README.md, dimensions.json, the tables of research/xiyanglou/README.md
uv run python scripts/scenes_dossiers.py      # research/scenes/<ID>-<slug>/README.md, dimensions.json, typology_check.json, the tables of research/scenes/README.md
uv run python scripts/building_pages.py       # research/buildings/, data/buildings/<ID>.json, raw/buildings/<ID>.json
uv run python scripts/xiyanglou_page.py       # site/xiyanglou/index.html, site/zh/xiyanglou/index.html, site/xiyanglou/keyplan.svg
uv run python scripts/scenes_page.py          # site/scenes/index.html (the hub), site/scenes/<ID>/index.html for the public scenes, site/scenes/keyplan.svg, the same under site/zh/scenes/
uv run python scripts/around_page.py          # Round 20: site/around/index.html, site/zh/around/index.html, site/around/plan.svg
uv run python tools/check_pages.py            # every clickable object has a page; public copy clean; generator idempotent
uv run python tools/check_evidence.py         # coverage; no empty evidence section; no research-only image on the site
uv run python tools/check_docs.py             # these docs match the files
uv run python tools/check_georef.py           # the frozen check set against the fit in use, by region; the rows follow the fit
uv run python tools/check_paths.py            # the ways: counts, joint gaps, crossings, bridge approaches, routes
uv run python tools/check_ground.py           # the ground: hills by method, one level per body, every object's gap and joint; --before <dir> measures an older export
uv run python tools/check_surroundings.py     # Round 20: counts by kind and grade; sources; joins at the gates and sluices; no overlap with walls, halls, water; the step where the grounds meet; sizes
uv run python tools/check_greens.py           # the planting: counts by kind, grade and species; no plant in a box, on a way, wall or bridge, in water (but lotus and reeds) or off the ground; rockeries grounded; --browser measures the view
uv run python tools/check_kit.py              # the kit: every box drawn, roofs from the data, inside the box, steps on the ground and met by the ways; --browser measures the view first (Node and Playwright outside the repo)
```

**Round 12:** `greens1860.py` reads the last run's boxes, ways, walls, bridges, landings, courts (`kit1860.court_area`) and the ground (`generated/ground.json`, `ground.bin`, `ground_grid.i16`): rerun it after any change to those or to `greens/species.csv`. A second run changes nothing.

Everything from `hills1860.py` down needs only `buildings.csv`, `layers/`, `paths/`, `terrain/readings.csv`, `greens/species.csv`, `terrain/plain.json`, `terrain/glo30_rise.npz`, `typology/params.json`, `xiyanglou/`, `scenes/` and the four catalogues. After any change to those, rerun those steps in order. `photos/catalog.csv` and `evidence/catalog.csv` are sources of truth, edited by hand from Round 3 on; `twins/catalog.csv` and `reconstructions/catalog.csv` from Round 5 on. How they were first merged: `docs/rounds/common/palace_r5_merge.py`, a record, not a pipeline step.

**Round 10:** `hills1860.py` and `ground1860.py` read the box and way positions of the last run (`site/reconstruction/data/halls_1860.geojson`, `layers/paths_1860`, `boxes1860.layout()`); positions never depend on the ground, so the chain is a fixed point: `hills1860.py` through `paths1860.py` run a second time change nothing.

**Round 8:** the placement chain (`georef_readings.py`, `control_derived.py`, `georef.py fit`, `build_r1.py`, `apply_facts.py`, `georef.py accuracy`, `publish_layers.py`, `ground1860.py`, `boxes1860.py`) run a second time gives the same files, and `georef.py previous` rebuilds the Round 1 fit byte for byte. The mosaic was refetched from the museum's IIIF server (`research/raw/` had been cleared) and `mosaic_plan.py` rebuilt the same stitch (`georef/princeton-mosaic.json` unchanged).

**Tested on 2026-10-31 (Round 4), in a scratch copy, in three batches, each compared with the repo:** `build_r1.py` through `building_pages.py` (without `render_r1.py`, `coverage_chart.py`, `plan_crops.py`); `typology_rules.py`, `typology_scale_check.py`, `georef.py`; `trace_plan.py --no-review`. They reproduce every committed file byte for byte. `trace_plan.py` took 45 s, each of the others at most 4 s. Not rerun: `fetch_osm.py` (today's OSM would differ), `clip_dem.py` and `mosaic_plan.py` (they write into `raw/`), `plan_crops.py`.

## Ids

| Id | What | Where it lives |
|---|---|---|
| `S01`, ... | a source. Blocks: S01–S09 core, S10–S39 maps, S40–S69 texts, S70–S99 pictures, S100–S129 typology, S130–S159 today's site, S160+ georeferencing, S200+ Round 3 (see the head of `sources.md`). 503 ids, S993 the last; S400 and above are Round 5, S700 and above Round 6, S900 and above Round 7, S1000 Round 10, S1100-S1179 Round 12 (blocks at the head of its section in `sources.md`). Some items have two ids; all stay valid | `sources.md` |
| `Q1`, ... | an open question. Q1–Q218; Q78–Q185 found in Round 7, Q186–Q190 in Round 8, Q191–Q196 in Round 9, Q197–Q203 in Round 10, Q204–Q208 in Round 11, Q209–Q218 in Round 12 | `questions.md` |
| `P0001`, ... | a picture; `P00NN` = `YMNN` for the album. Numbering in `photos/README.md`. P0822 the last | `photos/catalog.csv` |
| `E0001`, ... | a text, poem, drawing or report. Stable only once committed. E2497 the last; 32 ids moved to the reconstruction catalogue in Round 5 and stay there as `evidence_id` |
| `T001`, ... | a pairing of one of ours with a standing building. A twin named for two objects has two ids | `twins/catalog.csv` |
| `R0001`, ... | a reconstruction by other people | `reconstructions/catalog.csv` |
| `CLASS-grand_hall`, ... | a panel page of what speaks for a class of hall: a twin in the catalogue with `object_id` `CLASS:grand_hall` | `data/buildings/` | `evidence/catalog.csv` |
| `YM01`–`YM40` | the Forty Scenes in album order | `buildings.csv` |
| `YM41`–`YM55`, `CC01`–`CC21`, `QC01`–`QC52` | other compounds from the texts | `buildings.csv` |
| `YM56`–`YM88`, `CC22`–`CC30`, `QC53`–`QC82` | compounds read on the plan only | `plan/new_ids.csv` |
| `XY01`–`XY15` | the Xiyang Lou | `buildings.csv` |
| `YM03-11` | a hall from the texts (506 rows) | `buildings.csv` |
| `YM03-N02` | a hall first named on the plan (170) | `buildings.csv` |
| `YM03-B0835` | an unnamed block; the number is its `block_id` in `plan/blocks.csv` (781) | `buildings.csv` |
| `YM03-AE012` | an unnamed block a reader added; second letter is the reader's area: C, W, E, X, Q (50) | `buildings.csv` |
| `Z-B1234`, `Z-AW004`, `Z-QN03` | a block, an added block or a named place in no compound (102, with no `parent_id`) | `buildings.csv` |
| `G01`–`G53` | a gate | `layers/walls_1860`, `plan/gates.json` |
| `YMC-001`, `YMW-`, `YMF-`, `CCX-`, `QC-`, `R9-001` | a traced way, landing or dock: the reader's region and number (Round 9); the id of its line in `paths_1860` or its point in `landings_1860` | `paths/traces.csv` |
| `RC-YM01-01`, `BA-BR002-1`, `DL-YMC-082-2`, `RL-R3-01` | a C line added by `scripts/paths1860.py`: a link inside a compound, a bridge approach, a link at a dangling end, a link a route needed | `layers/paths_1860` |
| `R1`–`R4` | a route | `paths/routes.csv`, `layers/routes_1860` |
| `GS-0001` | a row of the planting (Round 12) | `greens/species.csv` |
| `GA-0001`, `GR-001` | an area of planting, a rockery, as the generator numbers them: stable only while the rows stay | `layers/greens_1860` |
| `TX-001`, `AL-001`, `RM-001` | a row of the texts, the album and the remains read in Round 9 | `paths/` |
| `GARDEN-YM`, `-CC`, `-XY`, `-QC`, `-ALL` | what speaks for a whole garden; in `shows` as `GARDEN:YM` | `data/buildings/` |
| `F0123` | a footprint; `XY01-M03` a Xiyang Lou part, `L002` a laid-out box, `D001` a default box, `GB02` a gate box | `footprints_1860`, `halls_1860` |
| `W01`, `W0001`, `I001`, `H0001`, `BR001`, `FD0001` | layer features: wall, water, island, hill, bridge, field | `layers/` |
| `OW001`, ... | an object outside the walls (Round 20), never renumbered: OW001-OW124 | `surroundings/features.csv`, `layers/surroundings_1860` |
| `W0901`, `FD0901` | water and fields outside the walls (Round 20, `outside: true`): the id the sheet's `layer_id` gives | `layers/water_1860`, `layers/fields_1860` |

## Conventions

**Source IDs.** Each source in `sources.md` has an ID; every row cites one or more, separated by `;` (`S03;S12`).

**Source status** in `sources.md`: found, viewed, downloaded, to-request, blocked, some with a qualifier ("viewed on Commons").

**Confidence** (`buildings.csv`, GeoJSON), as in `CLAUDE.md`: A = shown on a source made while the gardens stood, or measured on remains unchanged. B = a later source, or a written description only. C = inferred, every guess. How it is applied here:
- `confidence` = the row: does this thing, in this form, belong to the state of 1860? Album scenes are A unless S41 says later plans differ (then B). A hall named from the texts is B. A block drawn on S01 with no name is B: a building stood here, name unknown. An identification marked `guess` is C. Rows: 59 A, 1639 B, 126 C.
- `pos_confidence` = the position. **S01 counts as B, not A, until Q2 is settled:** it may be a 1920s tracing. `guess` readings and OSM points are C. Blank = no position.
- `read` = how the plan reader identified it. `sure` (label legible beside it, or Malone's number with matching buildings), `likely`, `guess`, `not_found`. Blank = an unnamed block.
- Boxes: 1383 B, 253 C, none A.

**plan_x, plan_y** always mean pixels on `raw/plans/princeton_mosaic.jpg`, 12955 × 9049, origin top-left. The plan is turned about 7.2° from true north. Ground scale 4.77 px/m, locally 3.7–5.55: never size a building from it.

**Blank cells** mean unknown or not read.

**Pinyin.** Names from the texts carry the inventory's pinyin. Names first read on the plan are romanised by `pypinyin` and not checked by a person; a name with an unread `?` has none.

**Ties,** in `shows` of both catalogues: `ID:sure|likely|guess;...`. `sure`: a printed title, a caption or a unique form. `likely`: a caption without proof for this building. `guess`: position or form only.

## buildings.csv

1824 rows: 314 top level (212 compounds and 102 in no compound), 1510 with a `parent_id`. 1652 have a position, 1473 a footprint.

| Field | Meaning |
|---|---|
| `id` | see Ids |
| `parent_id` | the compound; blank at top level |
| `name_zh`, `name_pinyin`, `name_en` | from the texts; `name_en` is Malone's where he gives one |
| `name_on_plan` | as written on S01, `?` per unread character. It may differ from `name_zh`, and that is evidence (Q3) |
| `read` | how the plan reader identified it, see Conventions |
| `garden` | Yuanming Yuan, Changchun Yuan, Xiyang Lou, Qichun Yuan, outside the walls |
| `type` | scene, compound, audience hall, residence, temple, library, theatre, pavilion, gallery, gate, bridge, tower, european, hall (unnamed block), other (the text states no function) |
| `hall_class` | key into `typology/params.json` `classes`, by name ending and size; blank where no footprint |
| `built`, `changed`, `destroyed` | as stated; `destroyed` is 1860 unless a source says more (Q47) |
| `sources`, `confidence`, `pos_confidence` | see Conventions |
| `lat`, `lon`, `pos_source` | WGS84 through the plan transform; `S01 sure` etc. or `S03 OSM point, not found on S01` |
| `plan_x`, `plan_y` | pixel on the mosaic |
| `footprint_id` | `F0123;F0124` into `footprints_1860` |
| `bays`, `bays_plan` | 间 as the text gives them, else from the plan; `5x3` = plan cells, frontage × depth |
| `frontage_m`, `depth_m`, `size_source` | a stated size wins; else drawn px / hall scale (4.18 and 3.31 px/m, `typology/halls.md`) |
| `orientation_deg`, `orientation_assumed` | compass bearing the front faces, through the plan transform. A reader's note wins; default: long E-W faces south, long N-S faces east, and a hall never faces along its long axis |
| `storeys`, `roof`, `roof_tiles` | only where a source states them; else from the class |
| `rel_position` | quote from the texts giving the position |
| `notes` | inventory notes, then `plan:` the reader's note |
| `size_lead` | a dimension a reconstruction or a modern study states, with its citation, grade B, from `evidence/facts.csv`. Only a lead: never a size, a position or a source of the row. Most name no Yangshi Lei drawing; `basis` in `evidence/facts.csv` says which do |

## evidence/catalog.csv

One row per text, poem, drawing or report. 2365 rows: 1734 free, 631 research-only; 146 snippet. The 32 `reconstruction` rows moved to `reconstructions/catalog.csv` in Round 5, so the kind is no longer used here.

| Field | Meaning |
|---|---|
| `evidence_id` | E + number |
| `kind` | `text`, `poem`, `description`, `drawing` (Yangshi Lei), `plan`, `archaeology` |
| `source_id` | S.. in `sources.md` |
| `title`, `date`, `locator`, `link` | the date is the text's; the locator is juan and leaf (`j80:9a`), page, or catalogue number |
| `rights_class` | `free`: Qing texts and other public domain, quoted. `research-only`: `excerpt_*` stay blank, the panel shows a card and a link |
| `status` | `viewed`: the page was fetched. `snippet`: only a search summary; the panel says so. For S360 and S361 poems, `viewed` means the PDF page was fetched and the poem picked by script from the compilers' section, and only sampled by eye |
| `shows` | ties, see Conventions; `GARDEN:YM`, `CC`, `XY`, `QC`, `ALL` for a whole garden; `G..` for a gate |
| `excerpt_zh`, `excerpt_other`, `summary_en` | verbatim where free; the summary is ours |

## evidence/facts.csv

What the evidence adds to a row of `buildings.csv`. 575 rows. Applied by `scripts/apply_facts.py`, whose docstring gives the rules for a field already filled and for raising a grade.

| Field | Meaning |
|---|---|
| `id` | the row of `buildings.csv`, or a gate |
| `field` | built, bays, changed, destroyed, name_en, name_zh, roof, depth_m, frontage_m, lat, lon, storeys, roof_tiles, size_lead |
| `value` | what it adds. `built` values "by 1759 (first dated item)" are a latest date, not a building date |
| `source_id`, `locator`, `basis` | where it comes from; `basis` is the quote or the reasoning |
| `suggest_confidence` | A, B or C, as the finder proposes |
| `decision` | `apply`; `name` (a label the plan leaves unread, settled by a text; Q38); `correct` (a figure of ours shown wrong, replaced, the old one kept in `notes`: frontage_m, depth_m, lat, lon; Round 6); `note` (kept in `notes`: it measures something else, or conflicts with what the row has); `gate` (for `layers/walls_1860`, waits for that layer's next build); `lead` (seen only in a search summary: not applied); `size_lead` (stated in a reconstruction or a modern study: goes to the column `size_lead` and nowhere else) |
| `reason` | why that decision |

## photos/catalog.csv

719 rows, 634 free, 85 research-only, 612 on the site; 153 of them show a twin. Fields and rights: `photos/README.md`. Columns: `photo_id`, `title`, `date`, `date_from`, `date_to`, `kind`, `creator`, `archive`, `archive_id`, `source_id`, `source_url`, `licence`, `attribution`, `rights_class`, `shows`, `why`, `also_shows`, `camera_lat`, `camera_lon`, `bearing`, `camera_note`, `file`, `width`, `height`, `notes`, `crop`, `relation`.

## xiyanglou/

The European palaces, Round 6. Overview: `xiyanglou/README.md`. `<ID>-<slug>/README.md` is a dossier, written by `scripts/xiyanglou_dossiers.py`, with a hand-written `## Notes` below the markers; `<ID>-<slug>/dimensions.json` is its sheet: `by_method`, `figures` (`id`, `part`, `what`, `label`, `value`, `err`, `unit`, `method`, `confidence`, `source`, `locator`, `snippet`, `key`), `model` (what the boxes take). The csv files are hand-edited from Round 6 on; `docs/rounds/common/palace_r6_merge.py` shows how they were first made.

| File | Fields |
|---|---|
| `about.json` | text by building, EN and a zh draft: `slug`, `zh`, `pinyin`, `en` (Malone's), `plates`, `what_en`, `after_en`, `survives_en`, `what_zh`, `after_zh`, `survives_zh`, `sources`; `_overview` for the page's lead. Checked sentence by sentence against the sources in Round 6 |
| `views.csv` | one row per picture and object: `photo_id`, `id`, `side` (S, N, E, W, roof, fountain, aerial, detail, fragment), `visible_part`, `state` (1780s, ruin, today, moved), `reliability` (high, medium, low: for a modeller), `camera_lat`, `camera_lon`, `bearing`, `camera_note`, `note` |
| `dimensions.csv` | every figure: `id`, `part`, `what`, `value_m` (or as `other:` says: area, volume), `err_m`, `method` (a published survey or measured drawing; b measured on the plan or ruin footprint; c read from an engraving by perspective; d a ruin photo with a known object; e typology, or a figure with no survey behind it), `confidence`, `source_id`, `locator`, `basis`, `status` (viewed, snippet, run) |
| `boxes.csv` | one row per 3D box: `building_id`, `part`, `lat`, `lon`, `orientation_deg`, `frontage_m`, `depth_m`, `platform_m`, `eave_m`, `ridge_m`, `roof`, `tiles`, `shape`, `double`, `stand_m`, `over_water`, `confidence`, `assumed`, `sources`, `basis`. First made by `docs/rounds/common/palace_r6_boxes_seed.py` |
| `parts.csv` | the unnamed rows, identified: `id`, `name_zh`, `name_pinyin`, `name_en`, `what`, `basis`, `source_id`, `confidence`, `action` (name, `merge:<row>`, retire, keep) |
| `materials.csv` | `id`, `part`, `what`, `colour`, `source_id`, `locator`, `quote_or_basis`, `confidence`, `status` |
| `fragments.csv` | `id`, `what`, `material`, `from_where_stated`, `now_at`, `now_place_zh`, `moved`, `status_today`, `source_id`, `locator`, `link`, `confidence`, `web_status`, `note`. Claims that do not hold are kept, and say so |
| `facts.csv` | as found, by building: `id`, `field` (built, changed, designer, function, name_en, roof, bays, after1860), `value`, `source_id`, `locator`, `quote_or_basis`, `suggest_confidence`, `status` |
| `rephoto.csv` | `id`, `old`, `new`, `same_view` (exact, close, rough), `what_changed`, `note` |
| `best.csv` | the top views for modellers: `id`, `rank`, `photo_id`, `why` |
| `impressions.csv` | every impression of the plates found: `plate`, `title`, `date`, `creator`, `archive`, `archive_id`, `source_id`, `source_url`, `licence`, `attribution`, `rights_class`, `width`, `height`, `notes`. P0041-P0060 stay the panel's plates |
| `viewpoints.csv` | where each plate was drawn from, estimated: `plate`, `photo_id`, `id`, `lat`, `lon`, `bearing`, `dist_m`, `err_m`, `basis` |
| `photo_viewpoints.csv` | Round 13: where a photograph was taken from, as the prior of its camera fit: `photo_id`, `id`, `lat`, `lon`, `bearing`, `dist_m`, `err_m`, `eye_m` (the eye above the ground), `eye_sd`, `basis`, `hfov_deg` (Round 15: an assumed lens, the horizontal field of view in degrees; a weak prior on the focal length, so that a flat set of points cannot shrink it to nothing; empty for none) Round 16: for a photograph taken on a terrace a model draws, `eye_m` still counts from the ground of Round 10 under it (远瀛观: the terrace's 4.3 m added) |
| `plate_keypoints.csv` | Round 13 (谐奇趣, 海晏堂's kit baseline), Round 14 (海晏堂's model: 96 more rows on plates 10-13, P0774, P0303, P0170, P0299; the vocabulary in `docs/rounds/common/palace_r14_haiyan_vocab.md`), Round 15 (大水法 and 观水法: 235 rows on plates 15, 16 and fourteen photographs; `docs/rounds/common/palace_r15_dashuifa_vocab.md`; a point read on a back view carries `_N`), hand-edited: named points read on a plate or a photograph, in the pixels of its copy in `research/photos/images/` (or `research/raw/photos/`): `plate` (empty for a photograph), `photo_id`, `object`, `point` (the vocabulary: `models/README.md`), `x`, `y`, `sure` (1 within about 3 px, 2 about 8 px, 3 rough), `use` (empty, or `skip: reason`: kept in the table, left out of every fit), `note` Round 16 (远瀛观 and 方外观: 196 rows on plates 14, 8 and fifteen photographs; `docs/rounds/common/palace_r16_yuanying_vocab.md`, merged by `docs/rounds/common/palace_r16_merge.py`; P0773 read as the east end, Q238; P0772 skipped as P0179's second print) |
| `plate_fit_<object>.csv` | Round 13, written by `tools/plate_overlay.py fit`: a row per point, picture and fit: `image`, `plate`, `object`, `fit` (anchored, all, stretch; from Round 14 `part_<name>`, a camera of its own for one part of a complex, `--parts`), `point`, `sure`, `role` (anchor: placed by the plan or the ruin; test; skipped), `in_fit`, `x_img`, `y_img` (the reading), `x_model`, `y_model` (the model's point through the fitted camera), `dx`, `dy`, `err_px`, `depth_m` (along the camera's axis), `err_m` (`err_px` times `depth_m` over the focal length) |
| `plate_cameras_<object>.json` | Round 13, the same run: each picture's prior, its fitted cameras (position, `yaw_deg`, `pitch_deg`, `f_px`, `du_px`, `dv_px`, `k_vertical` for `stretch`, `eye_above_ground_m`, `moved_from_prior_m`) and their statistics; the free pictures' cameras are copied to `site/reconstruction/data/plates.json` |

## scenes/

Every scene and compound outside the Xiyang Lou, Round 7: 81 dossiers, wave 1 the famous scenes, wave 2 the other Forty Scenes and six compounds of Yuanming Yuan, waves 3 and 4 Changchun and Qichun. Overview: `scenes/README.md`. `<ID>-<slug>/README.md` is a dossier, written by `scripts/scenes_dossiers.py`, with a hand-written `## Notes` below the markers; `<ID>-<slug>/dimensions.json` is its sheet: `by_method`, `figures` (the keys of the Xiyang Lou sheet plus `scale`). The figures are the rows of `dimensions.csv` and, measured by the script on the traced layers (status `run`), the scene's outline, its islands and the water inside it. `typology_check.json`: the measured figures against `typology/params.json`, by hall class. The csv files and `about.json` are hand-edited from Round 7 on; `docs/rounds/common/palace_r7_merge.py` shows how they were first made.

| File | Fields |
|---|---|
| `about.json` | text by scene: `slug`, `zh`, `pinyin`, `en` (Malone's translation where he gives one, else ours), `role_en` (Malone's description), `wave`, `public` (a page of its own on the site), `what_en`, `scene_en`, `later_en`, `interior_en`, `setting_en`, `survives_en`, `recons_en`, `best_en`, `gaps_en`, `summary_en` (the hub's lines), and for the public pages `what_zh`, `scene_zh`, `survives_zh`, `summary_zh`; `sources`; `_overview` for the hub's lead |
| `halls.csv` | each hall as one source states it: `id` (a row of `buildings.csv`, or `NEW` for a hall the texts name that has no row yet), `scene`, `plaque_zh`, `pinyin`, `en`, `bays`, `depth`, `purlins`, `roof`, `storeys`, `tiles`, `faces`, `relation` (its place among its neighbours), `built`, `changed`, `source_id`, `locator`, `basis` (the words that say it), `confidence`, `status` |
| `dimensions.csv` | every figure: `id`, `part`, `what`, `value_m` (or m², as `what` says), `err_m`, `method` (a a published survey, excavation report or measured drawing, or a Qing drawing or text that writes the figure; b measured on the plan or a ruin footprint; c read from a painting or woodcut by module; d a photograph with a known object; e typology, or a figure with no survey behind it), `confidence`, `source_id`, `locator`, `scale` (the module or scale used: 营造尺 0.32 m, the hall scale, metres as printed), `basis` (the original figure and unit), `status` (viewed, snippet, run) |
| `views.csv` | how a picture serves a modeller: `photo_id`, `id`, `view` (album, woodcut, gouache, 1887, yangshilei, tangyang, ruin, today, aerial, detail), `visible_part`, `state` (1744, 1745, 1750-92, 1887, Qing plan, ruin, today), `reliability` (high, medium, low), `note` |
| `best.csv` | the top views for modellers: `id`, `rank`, `ref` (a P, E or R id), `why` |
| `digs.csv` | excavations and surveys of the remains: `id`, `year`, `by`, `what_found`, `source_id`, `link`, `status`, `confidence` |
| `interior.csv` | furniture, paintings, plaques, couplets, objects; rocks, trees, water, bridges, colours, tiles: `id`, `kind`, `what`, `source_id`, `locator`, `quote_or_basis`, `confidence`, `status` |
| `checks.csv` | the check of the public pages' text before they went up, sentence by sentence, by workers who did not write it: `id`, `field`, `sentence`, `verdict` (held, changed, not verifiable), `source`, `note`, `fix`. 275 sentences: 154 held, 116 changed, 5 not verifiable |
| `parts.csv` | unnamed rows identified, as in `xiyanglou/parts.csv`: `id`, `name_zh`, `name_pinyin`, `name_en`, `what`, `basis`, `source_id`, `confidence`, `action` (name, `merge:<row>`, retire, keep); read by `scripts/boxes1860.py` |

Round 17: a scene with a detailed model keeps its picture sheets in its own folder, read by `tools/plate_overlay.py fit --sheets research/scenes/<ID>-<slug>` (so far `CC02-hanjing-tang/`, `YM03-jiuzhou-qingyan/`, `YM01-zhengda-guangming/`): `plate_keypoints.csv` (the fields of `xiyanglou/plate_keypoints.csv`; hand-edited, merged from the readers' sheets), `photo_viewpoints.csv` (the fields of `xiyanglou/photo_viewpoints.csv`; the readers' camera on the model's plan, turned into `lat`, `lon` and a compass bearing), and, written by the fit, `research/scenes/CC02-hanjing-tang/plate_fit.csv` (a row per point, picture and fit) and `research/scenes/CC02-hanjing-tang/plate_cameras.json`. The raw reading of the plan for the model is `models/CC02-hanjing-tang/plan_readings.csv`. Round 18 added `YM03-jiuzhou-qingyan/` (the leaf P0003, a painting, with a weak prior on purpose: `photo_viewpoints.csv` eye 70 m, sd 50 m) and `models/YM03-jiuzhou-qingyan/plan_readings.csv`. A model's `summary.json` may list `bridges` (ids of `generated/structures.json`) that it draws itself: `scripts/building_pages.py` checks them and copies them into `site/reconstruction/data/models.json`, and `3d.js` leaves their plain decks out. Round 25 added `YM46-wenyuan-ge/`: no picture of 文源阁 exists, so `plate_keypoints.csv` holds points read on a photograph of its sister 文渊阁 (P0555), and `photo_viewpoints.csv` gives that picture a virtual viewpoint before the model (its `basis` says the picture is of another place). The lines (drips, window sills and heads) are `skip` for the point fit and are read as lines by `models/YM46-wenyuan-ge/measure.py`, which fits a camera jointly with the storeys' heights (`models/YM46-wenyuan-ge/measure.json`).

## paths/

The ways of 1860, Round 9. Overview, findings by source and method: `paths/README.md`. The sheets are hand-edited from Round 9 on; `docs/rounds/common/palace_r9_merge.py` shows how they were first made.

| File | Fields |
|---|---|
| `traces.csv` | `key`, `region` (ymc, ymw, ymf, ccx, qc, r9), `scene`, `kind` (as in `paths_1860`, plus `landing`, `dock`), `name_zh`, `from_id`, `to_id` (a row, a gate G.., a bridge BR.., another key), `points_px` (`x y;x y`, plan pixels on the mosaic), `in_box_row` (a gallery whose bay row is a box of its own), `water` (a landing's water), `drawn_on_s01` (what on the plan shows it), `confidence` (the reader's: B drawn, C inferred), `leaf` (album keys that show it: A), `evidence`, `width_m` (only a drawn width), `sources`, `note` |
| `album.csv` | `key`, `scene`, `photo_id`, `kind`, `from_name`, `to_name`, `from_id`, `to_id`, `what_is_shown`, `where_in_leaf`, `reading` (high, medium, low), `note` |
| `texts.csv` | `key`, `topic` (route, gallery, boat, landing, dock, dike, road, steps, term, ceremony), `scene_ids`, `what`, `from_name`, `to_name`, `source_id`, `locator`, `quote_zh`, `summary_en`, `width_m`, `confidence`, `status` (verified, assumed, unknown), `link` |
| `remains.csv` | `key`, `topic` (dig, survey, qing_plan, plan_1933, term), `scene_ids`, `what`, `where`, `lat`, `lon`, `year`, `by`, `source_id`, `locator`, `summary_en`, `width_m`, `confidence`, `status`, `link` |
| `grades.csv` | `key`, `confidence` (blank: kept), `basis` (dig, text), `sources` (added to the line's), `note` |
| `routes.csv` | `id`, `name_en`, `name_zh`, `mode` (walk, boat), `waypoints` (rows with a box, gates, bridges, landings or keys, in order), `stops`, `sources`, `confidence`, `note` |
| `exceptions.csv` | `key`, `check` (joint, cross), `reason`: an A or B line `tools/check_paths.py` lets pass |
| `bridge_ends.csv` | `bridge`, `end` (1, 2), `approach` (the lines that meet it), `reason` (why none) |
| `dangling.csv` | `path`, `end`, `reason`: a traced end no link could join |
| `unreached.csv` | `scene`, `box`, `reason`: a hall no link could reach |
| `osm_judged.csv` | `osm_id`, `highway`, `name`, `length_m`, `over_water`, `through_box`, `near_way`, `on_shore` (shares of its length), `class` (modern, old_alignment_plausible, undecided) |

## twins/catalog.csv

One row per pairing of one of ours with a standing or named building. 135 rows on 66 objects and classes: 13 `copy of`, 6 `sister`, 7 `same design family`, 3 `copied from ours`, 106 `comparable`; 15 A, 60 B, 60 C. **Never a source for a position or a size in `buildings.csv`.** A pairing with no source stays out, or is `comparable`, C, with the reason in `evidence_for_relation`.

| Field | Meaning |
|---|---|
| `twin_id` | T + number |
| `object_id` | ours: a building id, `GARDEN:XY`, or `CLASS:grand_hall` for a typology comparable |
| `twin_name_zh`, `twin_name_en`, `twin_place` | the other building |
| `relation` | read from our side: `copy of` (ours copied it), `copied from ours`, `sister` (built together, same design), `same design family`, `comparable` (same court, era or type) |
| `evidence_for_relation` | the source and locator, with the sentence in our words; for a C, the reason |
| `still_standing` | `yes`, `rebuilt 1886` and the like (say so: a rebuild, not the original), `partly`, `no`. A lost twin stays in, under its own heading in the panel |
| `confidence` | of the relation: A a Qing text states it, B a later source, C our judgement |
| `what_it_tells` | form, roof, bays, setting |
| `notes`, `status` | working notes, not public; `viewed` or `snippet` |
| `link`, `licence` | where the relation is stated; how that source may be reused. Required (`tools/check_evidence.py`) |

## reconstructions/catalog.csv

One row per image or work with its own link. 326 rows: 25 free, 23 of them on the site; 120 with a local copy. **Modern interpretation, not evidence; never a source for a position or a size.** Where one disagrees with the period evidence, the row goes in `questions.md` (Q56, Q57).

| Field | Meaning |
|---|---|
| `recon_id` | R + number |
| `evidence_id` | the E id or ids it had in the evidence catalogue, so no link breaks |
| `source_id` | S.. in `sources.md` |
| `author`, `institution`, `year`, `uploader` | as stated. `uploader` for a video site: who uploaded it and whether that is the author |
| `kind` | render, aerial view, video, 3D model, physical model, painting, drawing, AR/VR, paper figure, game or community build |
| `era` | `modern`, or `period` for the card models 烫样 of the repair of 1873–74, which the panel sets apart |
| `title`, `link` | the holder's page |
| `licence`, `attribution`, `rights_class` | licence as the holder states it; the credit to show; `free` or `research-only`. A CC licence on a paper counts for a figure only with no other credit on that figure |
| `shows` | ties, as in `photos/catalog.csv`, with `GARDEN:ALL` etc. Blank = kept on record, off the panels: 22 rows, the zodiac head models and items not of this garden |
| `method_stated`, `summary_en` | what the author says they built it from, in our words; else what it is |
| `caveat` | one public line where it matters: 1744 not 1860, a replica, a scan of today's remains, made with AI, a community build |
| `status` | `viewed`, or `snippet` if seen only in a search summary; the panel says so |
| `local_copy`, `width`, `height` | `research/reconstructions/images/R####.jpg` if free; `research/raw/reconstructions/R####.jpg` if research-only, served on localhost only |
| `notes` | working notes, not public |

## terrain/

The ground of 1860, Round 10. Overview, what is measured, read and typology, the error by region: `terrain/README.md`.

| File | Fields |
|---|---|
| `terrain/readings.csv` | hand-edited from Round 10 on: `id` (R10-###), `worker`, `kind` (hill_height, hill_position, hill_profile, bank, rockery, water_level, water_depth, water_fall, sluice, survey, none_found), `ref` (a hill id), `scene_id`, `name_zh`, `where`, `lat`, `lon`, `value_m`, `value_text` (the source's words; for a bank its kind: stone_quay, rock_faced, earth_slope, mixed), `conversion`, `method` (survey, dem, painting, text, typology, dig), `error_m`, `state_date` (1744, 1860, a later year, today), `sources`, `source_title`, `source_url`, `page`, `grade`, `verified` (verified, snippet, unknown), `note` |
| `terrain/hills_heights.csv` | `id`, `basis`, `group`, `scene_id`, `area_m2`, `height_est_m`, `error_m`, `method`, `height_method`, `sources`, `confidence`, `assumed`, `readings`, `dem_note` |
| `terrain/rockeries.csv` | `reading`, `scene_id`, `where`, `what`, `sources`, `grade`, `state_date` |
| `terrain/water_levels.csv` | `body`, `water_ids`, `names`, `area_m2`, `level_m_egm2008`, `depth_m`, `method`, `sources`, `confidence` |
| `terrain/plain.json` | `a`, `bx`, `bz` (y = a + bx x/1000 + bz z/1000, EGM2008), `fall_m_per_km`, `falls_towards_deg`, `fit_cells`, `rms_m`, `lakes_today`, `lakes_fall_today` |
| `terrain/glo30_rise.npz` | `rise_dm` (int16, -32768 water today), `north`, `west`, `step`: today's height above the local low ground |
| `terrain/ground_report.json` | `bodies`, `levels_m`, `shore_m` by kind, `shore_grade_A_m`, `hills_modelled` (each hill's modelled peak), `pads`, `mesh`, `bridge_joints`, `highest_m` |
| `terrain/ground_check.json` | what `tools/check_ground.py` measured: `hills`, `water`, `boxes`, `bridges`, `ways`, `walls`, `landings` |

## kit/

The hall kit and the stone kit, Round 11. Overview, what each hall's form comes from, the cost: `kit/README.md`.

| File | Fields |
|---|---|
| `site/reconstruction/data/kit_1860.json` | `name`, `note` (the keys), `credit`, `gallery` (`bay_m`, `platform_m`, `column_m`, `eave_m`, `ridge_m`, `overhang_m`, `ju`), `courts` (`file`, `triangles`, `area_m2`, `cell_m`, `scale_xz_m`, `scale_y_m`, `lift_m`, `sources`, `confidence`, `assumed`, `basis`), `halls`: per box id `k` (hall, gate, pailou, pavilion, gallery, tower, stone, stoneshape, shape), `b` (bay widths along the frontage at the column line), `bs` (where the bays come from), `d` (widths across, front to back), `pf`, `pb`, `ps` (porches front, back, all round), `e` (下出), `o` (上出), `col`, `dia`, `st` (sides with steps), `so` (offsets of extra flights where a way arrives), `bal`, `rf` (`wd` 庑殿, `xs` 歇山, `ys` 硬山, `xu` 悬山, `cj` 攒尖), `gk` (stated, seeded or class: how a gable's kind was chosen), `rl`, `db`, `sd`, `ju`, `t`, `te`, `bd` (`br` bracket sets, `bm` a beam), `dr` (door bays), `rr` (`w` or `d`), `sh` (shades), `v` (curve, lift), `src` (model, dossier, stated, class), `a` (assumed), `g` (the form's grade), `fig` (the figures used); the stone kit also `sto` (storeys), `nb`, `ns` (bays front and side), `ped`, `stair`, `k2` (arcade, obelisk, niche, screen, hedgewall, gatewall), `tiers`, `cascade`, `jet`, `bamboo` |
| `site/reconstruction/generated/courts.bin` | int16 triples, three per triangle: x and z in 0.2 m, y in cm above the datum |
| `kit/kit_check.json` | `counts`, `drawn`, `beyond_box_m`, `joints`, `cost`, `files_mb`, `fails` |
| `kit/kit_browser.json` | `spec_hash`, `measured_utc`, `after`, `before` (`url`, `load_s`, `views`, `errors`) |
| `kit/kit_report.json` | `boxes` (per box `rf`, `k`, `tris`, `out`, `steps`), `tiles`, `near_triangles_all`, `far_triangles`, `gallery_near_triangles`, `court_triangles`, `lod_m`, `tile_m`, `max_near_tiles` |

## greens/

The planting of 1860, Round 12. Overview, the sources, the numbers and what is weak: `greens/README.md`. First made from the six readers' rows by `docs/rounds/common/palace_r12_merge.py` (a record); hand-edited from Round 12 on.

| File | Fields |
|---|---|
| `greens/species.csv` | `id` (GS-0001), `scene_id` (a scene, a hall, or `GARDEN-YM`, `-CC`, `-QC`, `-ALL`), `plant_zh` (as the source names it), `latin`, `name_en` (the reader's identification), `role` (avenue, grove, specimen, hedge, lotus, reed, lawn, bamboo, rockery_plant, flower_bed, orchard, climber, aquatic, field, potted), `form` (how the view draws it: pine, cypress, willow, broad, blossom, bamboo, shrub, topiary, hedge, lotus, floating, reed, rock; none for what is not drawn), `place` (scene, north, south, east, west, front_court, rear_court, court, around_hall, shore, island, hill, hill_foot, dike, along_way, pond, lake_edge, bridge, rockery, field, outside_wall), `place_text` (the source's words or the reading), `season`, `height_m` (blank: the species default), `source_kind` (poem, preface, text, leaf, archive, survivor, account, study, typology), `sources`, `locator`, `quote` (verbatim for public-domain texts only), `confidence`, `status` (verified, snippet), `use` (keep, reject), `reject_reason`, `note`, `worker` |
| `site/reconstruction/data/greens_1860.json` | `name`, `credit`, `note` (the record's layout), `record_bytes`, `count`, `domain`, `datum_m`, `trunk_sink_m`, `species` (`key`, `form`, `h`, `c`, `bloom`, `autumn`, `latin`, `en`), `areas` (id, scene, kind, species, extent grade, species grade, assumed), `rocks` (`id`, `scene`, `k` the kind, `ring` in dm from the domain's corner, `y0` base and `y1` top in cm, `g` grade, `ge` the place's grade, `s` seed) |
| `site/reconstruction/generated/greens_1860.bin` | 14 bytes a plant: x, z uint16 in dm from the corner; y int16 cm above the datum (the walk surface, or the water's level); area uint16; species, height (dm), crown (dm), flags (1 assumed, 2-4 species grade, 8-16 extent grade, 32 on a generated hill, 64 on the water), lift (dm: what the generated hills add there) uint8; a pad byte |
| `greens/greens_report.json` | the generator's counts: `rows`, `kept`, `drawn_rows`, `rock_rows`, `areas`, `areas_by_kind`, `areas_sourced`, `areas_fill`, `plants`, `by_form`, `assumed_plants`, `rockeries`, `rockeries_unplaced`, `areas_skipped` (a row with no land or water for its place), `areas_empty` (an area that got no plant), `files_mb` |
| `greens/greens_check.json` | what `tools/check_greens.py` measured: `plants`, `by_form`, `by_species`, `trees_confidence`, `extent_confidence`, `assumed`, `on_generated_hills`, `areas`, `placement`, `rockeries`, `files_mb`, `browser` |
| `greens/greens_browser.json` | `data_hash`, `measured_utc`, `url`, `load_s`, `views` (frame times and triangles with the planting off and on, by season), `report` (the view's own: tiles, far and near triangles), `errors` |

## surroundings/

What stood and ran round the gardens in 1860, Round 20. Overview, the sources by topic, the extent: `surroundings/README.md`.

| File | Fields |
|---|---|
| `surroundings/features.csv` | hand-edited: `id` (OW###), `kind` (neighbour_garden, town, village, banner_camp, office, workshop, storehouse, temple, road, canal, river, sluice, bridge, field, paddy, orchard, tomb, hill_far, lake, spring, other), `name_zh`, `name_pinyin`, `name_en`, `geom` (how its shape is given: `pt:<lon> <lat>`, with ` r=<m>` an assumed round extent; `geo` (`surroundings/geometry.geojson`); `osm:way/<id>` (`layers/osm_ring_today`); `row:<Z-id>`; `plan:<x> <y>`), `width_m` (roads and canals; C unless a source gives it), `size` (as a source states it), `state_1860`, `sources`, `confidence` (the object: that it was there, what it was), `pos_confidence` (where it stood), `assumed`, `position_basis` (what the position stands on), `joins` (`start@<id>` or `end@<id>`: a gate, a way of `paths_1860` or an earlier line the line's end is snapped to), `massing` (how the view draws it, `k=v;...`: `houses`, `rows`, `per_row`, `wall`, `compound` (`<w>x<d>`), `halls`, `kit`, `parts` (`<lon> <lat> <w>x<d>x<h>|...`), `within` (a garden's ground drawn only this far from its lakes), `w`, `d`, `rot`, `level`, `label`, `none`), `layer_id` (the id a lake or paddy takes in `water_1860` or `fields_1860`), `reader` (which reader's rows it came from, `topic:key;...`), `note` |
| `surroundings/geometry.geojson` | hand-edited: one feature per `geo` row, `id`, `basis` (what the line or outline was drawn from) |
| `surroundings/about.json` | the public page's text: `title_*`, `desc_*`, `eyebrow_*`, `h1_*`, `lead_*`, `plan_cap_*`, `cam`, `sections` (`id`, `h_*`, `en`, `zh`, `pictures`), `unknown_*`, `draft_zh` |
| `surroundings/report.json` | the generator's counts: `features`, `by_kind`, `by_confidence`, `assumed`, `made`, `joins` (`id`, `target`, `end`, `gap_before_m`, `gap_m`, `confidence`), `overlaps`, `overlap_worst`, `blocks`, `halls`, `patches`, `strips`, `view_bytes` |
| `surroundings/check.json` | what `tools/check_surroundings.py` measured: `by_kind_confidence`, `joins`, `loose_ends`, `overlaps`, `overlap_worst_m`, `join` (the step where the grounds meet), `block_fall_m`, `sizes_bytes`, `round_site_mb`, `massing`, `fails` |
| `site/reconstruction/data/around_1860.json` | the view's massing in scene metres: `features` (`id`, `kind`, names, `conf` the weaker grade, `assumed`), `patches` (`id`, `kind`, `ring`, `holes`), `strips` (`id`, `kind`, `w`, `pts`), `waters` (`id`, `ring`, `level`), `blocks` (`id`, `x`, `z`, `w`, `d`, `h`, `rot`, `roof`, `tint`, `assumed`), `halls` (the hall kit: `cls`, `bays`), `labels`, `meta` |

## Layers

Every feature carries `id`, names where known (`name_zh`, `name_pinyin`), `sources`, `confidence`, `note`. Working copies in `layers/`; `scripts/publish_layers.py` copies them to `site/reconstruction/data/` without the working fields `block`, `source_kind`, `drawn_m`, `ncols`, `nrows` of the footprints, `region_id` and `height_method`.

- `footprints_1860` (1560): one rectangle per box, as drawn on the plan and warped. **Use its centre with `orientation_deg`, `frontage_m`, `depth_m`, `hall_class`,** not its outline: halls are drawn smaller than the ground scale, so the true size is larger than the outline. `building_id` links to the row, `parent_id` to the compound. Also `orientation_assumed`, `block`, `source_kind`, `drawn_m`, `ncols`, `nrows`.
- `scenes_1860` (188): one polygon per compound, drawn by the readers round its island or court. `garden`, `name_en`, `name_on_plan`, `read`, `malone_no`, `area_m2`. Not a boundary known from a source.
- `water_1860` (366: W0001-W0365 in the gardens less W0047, and 昆明湖 and 未名湖 outside since Round 20): `kind` lake, pond or canal; holes are islands. `region_id`, `area_m2`. The polygons come to 116 ha in UTM 50N; `area_m2` sums to 118 ha. `islands_1860` (62): land enclosed by the water layer closed by 45 px (about 9 m), plus Malone's nine islands from their scene polygons; `scene_ids`. Round 19: `research/plan/water_manual.json` adds what the tracer could not close (a canal drawn as two ink lines a few px apart), traced by hand in plan pixels and numbered after the traced bodies: W0364, the moon-shaped canal before 出入贤良门 (`build_r1.py`). Round 24: W0365, the inlet before 方壶胜境 (S01's region R0018, classed land by default, taken whole, with the ink band of the flights round 迎薰亭's terrace; Q191). Round 25: `research/plan/water_removed.json` takes out traced water a later reading finds to be land, keeping its number taken so that no other id moves (`build_r1.py`): W0047, the ring between 文源阁's wall and the double lines round it, classed water by an automatic wash call (C); S01 draws the gate opening on it (Q289). The islands are numbered by area, so I040 (文源阁's court) went and the islands after it moved up one.
- `hills_1860` (472, Round 10): `kind`, `area_m2`, `height_est_m` (the height above the ground round it), `height_method` (the method and what it read: surveyed, dem, painting, text, typology), `error_m`, `sources`, `confidence`, `assumed`, `basis` (plan: the 54 outlines of S01; free_land: H2001 on, generated, assumed), `group` (the piece of land a hill belongs to: one mound per group), `scene_id`, `readings` (rows of `terrain/readings.csv`), `dem_note` (what GLO-30 shows where it gave no height). Written by `scripts/build_r1.py` (the plan's outlines) and then `scripts/hills1860.py` (heights, free land). Undercounts on the plan: Q29, Q199. A hill gives way to a surveyed sunken court of the Xiyang Lou (`scripts/build_r1.py`, `clear_of_courts`): H0015, wholly inside 大水法's court, is dropped (Q71); ids are not renumbered. Round 19: 462; the free land's hills keep off every court, yard and terrace a detailed model paves (`models/*/joints.json` `clear` and `decks`, `hills1860.model_courts()`): a generated hill of 7 m stood in the court of 正大光明, five more in 含经堂's forecourt and courts.
- `bridges_1860` (73): lines between the two ends; `building_id`, `read`. The drawn width is not recorded.
- `walls_1860` (58): `garden`, `read`; `kind` outer_wall, separating_wall (lines) and gate (53 points). Read by eye, 10–20 px off the ink, Qichun 20–40 px. Since Round 8 the west side of Changchun Yuan north of the plan's y 1900, which lies in a scroll seam, stands 15.2 m west of the traced line, off the Xiyang Lou ruins, with the sluice G43 (Q64; `WALL_SEAM_RUN` in `scripts/build_r1.py`). How the walls meet today's park outline: `tools/wall_check.py`, Q31, Q186. Round 19: W01 goes round the gate court of 正大光明 (the 大宫门 line and the inner court's ranges) between x 3000 and 3900, where it ran along the canal (Q259); edited in `plan/walls.json` and `plan/walls_manual.json` alike, the plan not re-traced.
- `fields_1860` (10): the labelled 稻田 rice fields; `kind`, `region_id`, `area_m2`. Round 20 adds the paddies outside the walls (FD0901-FD0904): `outside` true, `surroundings_id` (the object in `surroundings_1860`); the same in `water_1860` for the lakes outside the walls (W0901 昆明湖, W0902 未名湖), which may carry `level_m`. `scripts/ground1860.py` gives an `outside` water its own body, never merged with the gardens' water.
- `surroundings_1860` (138, Round 20, `scripts/surroundings1860.py`): what stood and ran round the gardens; `id` (OW### or the Z- id of a row S01 draws outside the walls, then `row_id`), `kind`, the names, `sources`, `confidence`, `pos_confidence`, `assumed`, `state_1860`, `size`, `position_basis`, `note`; `width_m` (roads, canals), `joins`, `extent_r_m` and `extent_assumed` (a point given a round extent). Points, lines, outlines.
- `osm_ring_today` (Round 20, `scripts/fetch_osm.py --ring`): today's water, canals, main roads, parks and names in the ring, ODbL; a reference, never 1860.
- `osm_today` (6004 here, 2507 on the site): today's park, ODbL. Keeps OSM's tags.
- `paths_1860` (Round 9, `scripts/paths1860.py`): one LineString per way. `id`, `kind` (paved_way 甬道, gallery 游廊, mountain_gallery 爬山廊, causeway, dike 堤, bridge_approach, steps, courtyard_path, imperial_road, service_path, boat_route), `name_zh`, `scene`, `width_m`, `width_source` (drawn on S01, or typology), `surface` (typology unless a dig is cited), `from_id`, `to_id` (as traced), `from_at`, `to_at` (what the end met: `F0123:front` a box's door, `through` a box walked through, `bridge`, `gate`, `landing`, `path`, `free: ...` the nearest thing when the id was missing or misread), `gap_before_m` (the two ends' distances before snapping), `sources`, `confidence`, `pos_confidence` (B traced on S01, C made here), `assumed` (C), `basis` (s01, leaf, dig, typology, reach), `leaf` (the pictures that show it), `in_box` (a box it may run inside), `drawn` (what the plan shows), `rerouted_m` (how far the reroute strays from the trace), `blocked_before_m`, `blocked_m` (length across a box, wall or water before and after), `length_m`, `note`.
- `landings_1860` (Round 9): one Point per landing or dock, on the shore 0.3 m inside the land. `id`, `kind` (landing, dock), `name_zh`, `scene`, `serves` (the rows), `water`, `water_id`, `facing_deg` (towards the water), `gap_before_m` (moved to the shore), `sources`, `confidence`, `pos_confidence`, `assumed`, `basis`, `leaf`, `drawn`, `note`.
- `routes_1860` (Round 9): one LineString per route. `id`, `name_en`, `name_zh`, `mode` (walk, boat), `path_ids` (the lines and bridges in order), `via` (the boxes walked through), `stops` (`id`, `name`, `along_m`, `off_m`), `length_m`, `sources`, `confidence`, `note`.
- `greens_1860` (Round 12, `scripts/greens1860.py`): the areas of planting and the rockeries; the plants themselves are in `generated/greens_1860.bin`. An area: `id` (GA-), `scene`, `kind` (grove, avenue, specimen_tree, bamboo_grove, lotus_pond, reed_bed, flower_bed, hedge), `species` (the plant's key; the fill gives its mix), `latin`, `form`, `place`, `pattern` (groves, avenue, pair, single, grid, clumps, fill), `count` (plants placed), `density` (plants per ha), `height_m` (the species default unless the row gives one), `season`, `extent_confidence` (B a leaf or a survivor shows that side of the scene; C a text only, the whole scene, or a fallback), `trees_confidence` (the rows' best grade; C for the fill), `assumed` (the fill: no source names planting there), `generated` (what is generated: places; extent and places; extent, species and places), `rows` (GS ids), `sources`, `hall` (the hall it is placed by), `note` (the sources' words, or the fill's basis). A rockery: `id` (GR-), `scene`, `kind` rockery, `rock` (standing, screen, shore, hill), `base_m` and `top_m` (EGM2008), `height_m` (above the highest ground under it), `confidence`, `extent_confidence`, `trees_confidence` (blank), `assumed`, `generated`, `rows` (GS ids and R10 readings), `sources`, `hall`, `note`. Public, byte-identical in `site/reconstruction/data/`.
- `georef_error` (Round 8, `scripts/georef.py accuracy`): how far a position taken from the plan may stand from where it stood, from the blind check set. `kind` `region` (the six regions: `region`, `name`, `n_check`, `median_m`, `p90_m`, `max_m`, `previous_median_m`, `previous_p90_m`, `previous_max_m`, `fit` new or previous, `typical_m`), `cell` (a 200 m grid: `expected_m`, the inverse-distance mean of the four nearest check points of the same region, an estimate between points; `nearest_check_m`) and `check_point` (`feature`, `point_kind`, `dist_m`, `dE_m`, `dN_m`, `previous_dist_m`). Public: our readings of S01 and of today's imagery, coordinates only. The dev map's toggle "Placement accuracy".

Only on the site:
- `buildings_1860` (1652): one point per row with a position: `id`, `parent_id`, the names, `garden`, `type`, `built`, `sources`, `confidence`, `pos_confidence`.
- `labels_1860.json`: names for the 3D view (`zh`, `en`, `lon`, `lat`, `rank`).

## The boxes and the ground (Round 2)

Constants with their sources stand at the top of `scripts/boxes1860.py` and `scripts/ground1860.py`, levels in `scripts/scene1860.py`.

- **`halls_1860`** (1634): one feature per box, `basis` says what it stands on: `plan` (a block drawn on S01; 1500), `stated` (a size in a source; 9), `xiyang` (79), `layout` (11), `default` (14), `gate` (21) (these four `assumed: true`, C). Round 8: GB35 is gone, because gate G35 (花园门) now falls within 6 m of the XY03 box, which counts as the gate itself. Size comes down from the hall scale towards the drawn size where a neighbour or water needs it (`fit`), and may move a little (`moved_m`). Q34.
- **Its other properties:** `assumed`, `id`, `building_id`, `parent_id`, `name`, `garden`, `hall_class`, `frontage_m`, `depth_m`, `orientation_deg`, `sources`, `confidence`; `platform_m`, `eave_m`, `ridge_m`, `mid_eave_m`, `tiers_m` (storeyed roofs); `roof` (gable, hip_gable, pyramid, hip), `rolled`, `double`, `rolls`, `tiles`; `ground_m`, `foot_m`, in metres on the datum; `over_water` (13); `also` (other rows this box stands for); `shape` (wall, octagon, pool, terrace; court and basin on the Xiyang Lou), `european`, `part` (what a guessed part is), `stand` (a base height). Round 11: `figures` (the hall's own figures taken from its dossier: `column_h`, `platform_h`, `height_ridge`, each as value, method, grade, source), `roof_src` (where a roof read for this hall comes from: `buildings.csv` or `halls.csv` with source and grade), `tiles_src`, `tile_edge` (the edge colour 剪边 a leaf shows), `sides` (6 or 8 for a polygonal 攒尖), `gable_kind` (`yingshan` 硬山 or `xuanshan` 悬山 where a source names it). The file also has `shared_rows`: rows sharing another row's box.
- **Heights and roofs:** `typology/params.json` by `hall_class`; a stated hall in `by_name` wins. A hall deeper than 1.5 x its class's depth takes parallel rolls (`rolls`). Round 11: the hall's own figures in its dossier (`scenes/*/dimensions.json`, `xiyanglou/*/dimensions.json`, picked by `figures()` in `scripts/scene1860.py`: method a, b, c, d in that order, then grade) win over the class, and those of method a or b over `by_name` too; a roof or tile read for the hall in `scenes/halls.csv` wins over the class where it names one form.
- **Xiyang Lou:** massing from `xiyanglou/boxes.csv`, each box with its position, size, sources and reason: on the ruin where one can be read, at the plan's ground scale, with heights from the plates (Q64, Q65). `assumed` is off where a survey gives the footprint. Rows that a part merges into share the target's box (`shared_rows`), and a retired row has none (`xiyanglou/parts.csv`). The layers `footprints_1860` and `walls_1860` stay on the plan.
- **No box:** rows with no position, labelled plots, the 寿山 ridge, water, docks, sluices (reasons in `boxes1860.py`).
- **Ground (Round 10, `scripts/ground1860.py`, `terrain/README.md`):** the plain from the DEM as a plane (`terrain/plain.json`); 189 water bodies, each at one level 1.5 m under the plain along its shore, the land pulled to that near the water; beds 1.5-2.3 m down; earth, stone and rock banks (`terrain/readings.csv` and two rules); the hills of `hills_1860`, one smooth mound per `group`, the peak at most 0.45 x its half-width + 0.3 m; pads under the boxes of one compound, blended out over 6 m; 大水法's sunken court 1.30 m down (S603, Q71); paddy 0.25 m down. A 2.5 m design raster; a quadtree mesh of 20, 10 and 5 m cells, 2:1 balanced, cut exactly to the water. The surface the view walks on is that mesh rasterised. A box on uneven ground stands on its highest land. Q34.
- **Generated files:** `generated/ground.json` (frame, plain, `bodies` with level and depth, `bridges` with their decks, `codes`, offsets of the chunked parts; positions int16: x and z in decimetres from the domain's corner, y in centimetres; indices uint16), `ground.bin` (land with `code` and `hill` bytes and `yalt` without the assumed hills, skirt, bed, water, paddy, court), `ground_grid.i16` (2.5 m lattice over walls, boxes and ways: the land mesh in cm; water -20000 + the bed; bridge decks as land), `ground_level.u8` (10 m cells: 1 + the water body), `structures.json` (`wall` in stepped courses, `bridges` from `ground.json`).
- **Bridges, Round 9:** BR006 and BR047 had been read along their decks; their spans now cross the stream and the moat (`plan/readings/ym_central/features.csv`, `cc_xyl/features.csv`), ids unchanged.
- **Walls:** `walls_1860` with height 2.8 m and thickness 0.8 m (`params.json`). A wall stops at a hall standing in its line (53 boxes), and opens 6 m at a gate with no hall. A gate point within 14 m of a wall line counts as in it.

## The panel JSON

`site/reconstruction/data/buildings/<ID>.json`, one per page: 1612 `hall`, 212 `compound`, 53 `gate`, 5 `garden`, 11 `class`. Keys:

| Key | What |
|---|---|
| `id`, `kind`, `title`, `subtitle` | who it is |
| `object`, `position`, `model` | what stands in the 3D view: `{kind, count}`, `[lon, lat]`, `{line, rows}` for the panel's text |
| `parent`, `children` | the compound; `[id, name]` pairs of its halls |
| `facts` | `{label, value, sources, confidence}` |
| `notes_html` | the page's `## Notes`, above `%% private %%` |
| `photos`, `photos_inside` | its own pictures; pictures tied to its halls (on a compound). A research-only one has `link_only: true` and no `image` or `thumb` |
| `evidence` | its own texts and drawings; a research-only one has no excerpt |
| `reconstructions` | by other people, shaped like a picture, with `era`, `caveat`, `status` added: a free one has `image` and `thumb`, a research-only one `link_only: true` and neither |
| `twins` | `{id, name, place, relation, standing, confidence, tells, basis, link, status, photos}`, `photos` shaped as above |
| `plan_ref` | the plan S01 as a link: `{text, link, source_id}` |
| `fallback` | what speaks for the set of buildings: `[{kind, id, name, heading}]`, `kind` being compound, nearest (with `metres`), garden or class. With `refs_only` it brings only that page's reconstructions and twins, folded. The panel fetches that page, so nothing is written twice |
| `searched` | a line saying what was searched and not found; blank when it has its own picture and text |
| `questions`, `sources` | `{id, title}`; the cited sources with licence and link |
| `dimensions`, `dossier` | Xiyang Lou: the figures of `dimensions.json` (a building has all of them, a part its own); the link to its section of the public page. A scene with a dossier (Round 7): the scene has all its figures, a hall only its own (it sees the scene's under its fallback); `dossier` links to the scene's page if it has one, else to its summary on the hub `scenes/#<ID>`; `GARDEN-YM`, `-CC`, `-QC`, `-ALL` link to the hub. A scene's figures also carry `scale` |
| `planting` | Round 12, a scene, a hall with its own rows, a garden: `sourced` (the kept rows the view draws: `id`, `plant`, `latin`, `en`, `role`, `place`, `where`, `season`, `kind` the kind of source, `confidence`, `sources`, `quote` (public-domain texts only), `drawn` the plants placed), `not_drawn` (fields, lawns, climbers, potted plants), `rejected` (with the reason in `where`), `rocks` (`id`, `rock`, `height_m`, `confidence`, `extent`, `sources`, `where`). The panel's "Planting of this scene" |
| `ways` | Round 9: `reached` (the lines, landings and docks that touch it, a compound those of its halls, at most 40: `id`, `kind`, `label`, `other` (what the other end meets), `confidence`, `assumed`, `sources`, `length_m`) and `routes` (`id`, `name`, `confidence`, `sources`, `stop`: a stop of the route). The panel's Ways section, "Reached from" and "On the route", with a button that walks the route |

**Parent fallback,** `fallback_of()` in `scripts/building_pages.py`:
- a hall leans on its compound, and on the garden too if the compound has no picture or text;
- a gate leans on its garden;
- a top-level object with its own picture has no fallback;
- one with text only, or no position, leans on the garden;
- anything else leans on the nearest named compound, with the distance, and the garden.

A row also gets, with `refs_only`, its garden if the fallback does not already hold it, and for a hall its class (`refs_of()`). So a hall inherits its compound's reconstructions and twins under the compound's heading, the way it inherits the evidence.

**On the Xiyang Lou** a picture also has `side_group`, `visible` and `reliability`, and the panel heads its pictures by side, the front first, with "Ruins today" last, instead of by period. The Dimensions block follows the plan's link. A part's fallback brings its building's figures. Other gardens' pages have none of these keys.

**In the panel,** in this order: own pictures, own texts and drawings, the plan as a link card (image only on localhost), the `searched` line; **Reconstructions by others**, labelled modern interpretation, not evidence, free images first; **Surviving comparable buildings, not this building**, with relation and source; then what speaks for the set of buildings. Pictures with a `guess` tie are marked and sort last.

`research/raw/buildings/<ID>.json` has the same keys, with the plan readers' notes, plan pixels, the plan crop and research-only copies in them, for `tools/serve_local.py`. `scripts/building_pages.py` stops on any public key outside its lists (`PUBLIC_KEYS` and the four beside it).

## Public and private

- **Public, with credit** ("Image courtesy of the Princeton University Art Museum"): geometry traced from S01, that is, every `*_1860` layer and the positions, in `site/reconstruction/data/` through `scripts/publish_layers.py`, which drops the readers' working fields. The museum's data treats S01 as not under copyright, and its pages say so (S01 in `sources.md`, Q6).
- **Local for now:** the plan image and the overlay. The museum's terms would allow showing them, but they carry a non-commercial clause and Tomasz has not decided (Q6). So `research/raw/` and `research/overlays/` stay out of git and off the site; `tools/serve_local.py` serves the overlay on localhost under `/_local/`, as Küstrin does. It marks its answers with `X-Palace-Local`, so a page on a plain static server (the preview on :8790, a host) never asks for `/_local/`. `?public=1` shows what a visitor sees.
- **Building pages:** `data/buildings/<ID>.json` holds names, garden, dates, sources, confidence, the note as facts with citations, the box, the evidence (free pictures with images, research-only ones as link cards; Qing texts quoted, modern work summarised). Only `raw/buildings/<ID>.json` has the plan readers' notes, plan pixels, the plan crop, research-only copies and any other quote.
- **Pictures:** `photos/images/` and `reconstructions/images/` hold free images only; research-only ones stay in `raw/photos/` and `raw/reconstructions/`. Web copies reach `site/reconstruction/photos/` only through `scripts/photos_catalog.py`, with their credits in `site/credits.html`. BnF album leaves need the credit "Source gallica.bnf.fr / BnF".
- **`research/plan/inventory_texts.csv`** quotes 日下旧闻考 (public domain) and states facts from research-only articles; it is not published as a file. Facts go to the site with a citation only.
- OSM data needs ODbL attribution. Esri tiles are never saved in the repo.
- **Second lock:** `.gitignore` and `site/.vercelignore` leave overlays, `raw/` and any CSV out of the site even if copied there by hand.
