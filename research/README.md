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
| `layers/` | working GeoJSON in WGS84, the hand-off to the 3D round | `scripts/build_r1.py`; `osm_today` from `scripts/fetch_osm.py` | yes |
| `plan/` | everything read off the base plan S01, in plan pixels | see below | yes |
| `georef/` | how the plan is tied to the ground | see below | yes |
| `typology/` | `halls.md`, `params.json` (defaults by hall class, each with a source and a confidence), `rules_out.json`, `scale_check.json` | hand and `scripts/typology_*.py` | yes |
| `terrain/README.md` | what the DEM can and cannot tell | hand | yes |
| `photos/` | the picture catalogue and free images, see `photos/README.md` | hand | yes |
| `evidence/` | what is not an image, see below; `evidence/coverage_before_r5.json` the coverage before Round 5, which `tools/check_evidence.py` compares with | hand | yes |
| `twins/catalog.csv` | surviving buildings that are copies, sisters, models or fair comparables of ours, see below | hand, from Round 5 | yes |
| `reconstructions/catalog.csv` | reconstructions by other people, see below | hand, from Round 5 | yes |
| `xiyanglou/` | Round 6, the European palaces in depth: one dossier per main building, the sheets they draw on. See below | hand; `scripts/xiyanglou_dossiers.py` | yes |
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
- `princeton-1920s.json`: the chosen transform, RMS, leave-one-out, block cross-validation, seam test, per-point residuals, `per_area_verdict`. Every figure comes from `scripts/georef.py fit`, which also exposes `plan_to_wgs84(xs, ys)` and `wgs84_to_plan(lons, lats)`.
- `princeton-1920s.csv`: the control points, see below.

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
uv run python scripts/clip_dem.py             # research/raw/dem/site_glo30.npz (needs the tiles in raw/dem)
uv run python scripts/mosaic_plan.py          # raw/plans/princeton_mosaic.jpg, georef/princeton-mosaic.json
uv run python scripts/trace_plan.py           # plan/regions.json, blocks.csv, walls.json, gates.json, ... (needs scipy)
uv run python scripts/georef.py               # the same as `fit`: georef/princeton-1920s.json
uv run python scripts/georef.py overlay       # overlays/princeton-1920s.jpg + .json
uv run python scripts/georef.py images        # screenshots/r1/georef_*
uv run python scripts/typology_rules.py       # typology/rules_out.json
uv run python scripts/typology_scale_check.py # typology/scale_check.json
uv run python scripts/build_r1.py             # buildings.csv, layers/*_1860, plan/coverage.json, plan/new_ids.csv
uv run python scripts/apply_facts.py          # buildings.csv: what evidence/facts.csv adds to the rows
uv run python scripts/render_r1.py            # screenshots/r1/layers_public.png, public-safe
uv run python scripts/coverage_chart.py       # screenshots/r1/coverage.png
uv run python scripts/publish_layers.py       # site/reconstruction/data/: the public layers, buildings_1860, labels_1860
uv run python scripts/ground1860.py           # site/reconstruction/generated/: ground.json, ground.bin, ground_grid.i16
uv run python scripts/boxes1860.py            # data/halls_1860.geojson, generated/structures.json (walls, bridges); prints its checks
uv run python scripts/photos_catalog.py       # site/reconstruction/photos/, credits (from photos/catalog.csv)
uv run python tools/plan_crops.py             # raw/plancrops/<ID>.jpg, local only; needs the mosaic
uv run python scripts/xiyanglou_dossiers.py   # research/xiyanglou/<ID>-<slug>/README.md, dimensions.json, the tables of research/xiyanglou/README.md
uv run python scripts/scenes_dossiers.py      # research/scenes/<ID>-<slug>/README.md, dimensions.json, typology_check.json, the tables of research/scenes/README.md
uv run python scripts/building_pages.py       # research/buildings/, data/buildings/<ID>.json, raw/buildings/<ID>.json
uv run python scripts/xiyanglou_page.py       # site/xiyanglou/index.html, site/zh/xiyanglou/index.html, site/xiyanglou/keyplan.svg
uv run python scripts/scenes_page.py          # site/scenes/index.html (the hub), site/scenes/<ID>/index.html for the public scenes, site/scenes/keyplan.svg, the same under site/zh/scenes/
uv run python tools/check_pages.py            # every clickable object has a page; public copy clean; generator idempotent
uv run python tools/check_evidence.py         # coverage; no empty evidence section; no research-only image on the site
uv run python tools/check_docs.py             # these docs match the files
```

Everything from `publish_layers.py` down needs only `buildings.csv`, `layers/`, `typology/params.json`, `xiyanglou/`, `scenes/` and the four catalogues. After any change to those, rerun those steps in order. `photos/catalog.csv` and `evidence/catalog.csv` are sources of truth, edited by hand from Round 3 on; `twins/catalog.csv` and `reconstructions/catalog.csv` from Round 5 on. How they were first merged: `docs/rounds/common/palace_r5_merge.py`, a record, not a pipeline step.

**Tested on 2026-10-31 (Round 4), in a scratch copy, in three batches, each compared with the repo:** `build_r1.py` through `building_pages.py` (without `render_r1.py`, `coverage_chart.py`, `plan_crops.py`); `typology_rules.py`, `typology_scale_check.py`, `georef.py`; `trace_plan.py --no-review`. They reproduce every committed file byte for byte. `trace_plan.py` took 45 s, each of the others at most 4 s. Not rerun: `fetch_osm.py` (today's OSM would differ), `clip_dem.py` and `mosaic_plan.py` (they write into `raw/`), `plan_crops.py`.

## Ids

| Id | What | Where it lives |
|---|---|---|
| `S01`, ... | a source. Blocks: S01–S09 core, S10–S39 maps, S40–S69 texts, S70–S99 pictures, S100–S129 typology, S130–S159 today's site, S160+ georeferencing, S200+ Round 3 (see the head of `sources.md`). 501 ids, S991 the last; S400 and above are Round 5, S700 and above Round 6, S900 and above Round 7 (blocks at the head of its section in `sources.md`). Some items have two ids; all stay valid | `sources.md` |
| `Q1`, ... | an open question. Q1–Q185; Q78 and on found in Round 7 | `questions.md` |
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
| `GARDEN-YM`, `-CC`, `-XY`, `-QC`, `-ALL` | what speaks for a whole garden; in `shows` as `GARDEN:YM` | `data/buildings/` |
| `F0123` | a footprint; `XY01-M03` a Xiyang Lou part, `L002` a laid-out box, `D001` a default box, `GB02` a gate box | `footprints_1860`, `halls_1860` |
| `W01`, `W0001`, `I001`, `H0001`, `BR001`, `FD0001` | layer features: wall, water, island, hill, bridge, field | `layers/` |

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

## Layers

Every feature carries `id`, names where known (`name_zh`, `name_pinyin`), `sources`, `confidence`, `note`. Working copies in `layers/`; `scripts/publish_layers.py` copies them to `site/reconstruction/data/` without the working fields `block`, `source_kind`, `drawn_m`, `ncols`, `nrows` of the footprints, `region_id` and `height_method`.

- `footprints_1860` (1560): one rectangle per box, as drawn on the plan and warped. **Use its centre with `orientation_deg`, `frontage_m`, `depth_m`, `hall_class`,** not its outline: halls are drawn smaller than the ground scale, so the true size is larger than the outline. `building_id` links to the row, `parent_id` to the compound. Also `orientation_assumed`, `block`, `source_kind`, `drawn_m`, `ncols`, `nrows`.
- `scenes_1860` (188): one polygon per compound, drawn by the readers round its island or court. `garden`, `name_en`, `name_on_plan`, `read`, `malone_no`, `area_m2`. Not a boundary known from a source.
- `water_1860` (363): `kind` lake, pond or canal; holes are islands. `region_id`, `area_m2`. The polygons come to 116 ha in UTM 50N; `area_m2` sums to 118 ha. `islands_1860` (62): land enclosed by the water layer closed by 45 px (about 9 m), plus Malone's nine islands from their scene polygons; `scene_ids`.
- `hills_1860` (55): `kind`, `height_est_m`, `height_method`; all C. Undercounts: Q29.
- `bridges_1860` (73): lines between the two ends; `building_id`, `read`. The drawn width is not recorded.
- `walls_1860` (58): `garden`, `read`; `kind` outer_wall, separating_wall (lines) and gate (53 points). Read by eye, 10–20 px off the ink, Qichun 20–40 px.
- `fields_1860` (10): the labelled 稻田 rice fields; `kind`, `region_id`, `area_m2`.
- `osm_today` (6004 here, 2507 on the site): today's park, ODbL. Keeps OSM's tags.

Only on the site:
- `buildings_1860` (1652): one point per row with a position: `id`, `parent_id`, the names, `garden`, `type`, `built`, `sources`, `confidence`, `pos_confidence`.
- `labels_1860.json`: names for the 3D view (`zh`, `en`, `lon`, `lat`, `rank`).

## The boxes and the ground (Round 2)

Constants with their sources stand at the top of `scripts/boxes1860.py` and `scripts/ground1860.py`, levels in `scripts/scene1860.py`.

- **`halls_1860`** (1636): one feature per box, `basis` says what it stands on: `plan` (a block drawn on S01; 1500), `stated` (a size in a source; 9), `xiyang` (79), `layout` (11), `default` (14), `gate` (23) (these four `assumed: true`, C). Size comes down from the hall scale towards the drawn size where a neighbour or water needs it (`fit`), and may move a little (`moved_m`). Q34.
- **Its other properties:** `assumed`, `id`, `building_id`, `parent_id`, `name`, `garden`, `hall_class`, `frontage_m`, `depth_m`, `orientation_deg`, `sources`, `confidence`; `platform_m`, `eave_m`, `ridge_m`, `mid_eave_m`, `tiers_m` (storeyed roofs); `roof` (gable, hip_gable, pyramid, hip), `rolled`, `double`, `rolls`, `tiles`; `ground_m`, `foot_m`, in metres on the datum; `over_water` (13); `also` (other rows this box stands for); `shape` (wall, octagon, pool, terrace; court and basin on the Xiyang Lou), `european`, `part` (what a guessed part is), `stand` (a base height). The file also has `shared_rows`: rows sharing another row's box.
- **Heights and roofs:** `typology/params.json` by `hall_class`; a stated hall in `by_name` wins. A hall deeper than 1.5 x its class's depth takes parallel rolls (`rolls`).
- **Xiyang Lou:** massing from `xiyanglou/boxes.csv`, each box with its position, size, sources and reason: on the ruin where one can be read, at the plan's ground scale, with heights from the plates (Q64, Q65). `assumed` is off where a survey gives the footprint. Rows that a part merges into share the target's box (`shared_rows`), and a retired row has none (`xiyanglou/parts.csv`). The layers `footprints_1860` and `walls_1860` stay on the plan.
- **No box:** rows with no position, labelled plots, the 寿山 ridge, water, docks, sluices (reasons in `boxes1860.py`).
- **Ground:** flat base land 45 m and one water level 43.5 m (EGM2008), from `terrain/README.md`; islands +0.8 m, hills as mounds from `hills_1860`, 线法山 from `params.json`. No DEM cell is used as a height: it holds today's trees and fill. Land is cut exactly to `water_1860`, with a bank down to the water. Q34.
- **Generated files:** `generated/ground.json` (frame, levels, offsets), `ground.bin` (positions and indices per part), `ground_grid.i16` (5 m raster for walk mode and `boxes1860.py`), `structures.json` (`wall`, `bridges`).
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
