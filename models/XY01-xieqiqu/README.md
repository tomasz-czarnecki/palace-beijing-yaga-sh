# XY01 谐奇趣 Xieqiqu, "Harmonious Strange and Pleasant": the pilot model (Round 13)

The first detailed model of the project. It covers the main block with its south and north stairs, the two curved colonnades, the two octagonal music pavilions 八角奏乐亭 (XY01-01, XY01-N01), the scalloped pool 海棠形喷水池 (XY01-02) and the north basin. It is a showcase of the method, not a one-to-one reconstruction. Every figure is C until the Qing drawing 样式雷 985 is seen (Q72).

Files:
- `xieqiqu.py` is the generator. It writes `model.glb`, `params.json` (every figure with its source, grade and note), `keypoints.json` (named points for `tools/plate_overlay.py`), `joints.json` (where the model meets the ground; its entries, which the ways of Round 9 snap to; its footprints, which the ways and the planting keep clear of) and `summary.json` (what the site reads; see `models/README.md`).
- `measure.py` reads the figures off the 1873 photographs: one least-squares over every photograph's camera and the figures. With `--roofs` it reads the roof heights off plates 1 and 2.
- `measure/measure.json` and `measure/measure_roofs.json` hold its results.
- Run: `uv run python models/XY01-xieqiqu/xieqiqu.py`, then `scripts/building_pages.py` (it publishes the GLB). For the test: `tools/plate_overlay.py fit --object XY01`, `node tools/plate_overlay.mjs --object XY01`, `tools/plate_overlay.py compose --object XY01`. Finally `tools/check_models.py`.

## Evidence

Every picture named here is free: the public domain on Wikimedia Commons, as `research/photos/catalog.csv` records. The research-only items are only cited.

- **Plates 1 and 2** of the copperplate set, 1783-86 (P0041 south front, P0042 north front; the Palace Museum impression on Commons). They give the scheme: 7, 7 and 3 bays, the stairs, the colonnades, the octagons, the pool, the roofs. Read with 47 and 36 key points.
- **Ohlmer's photographs of 1873** (S89, S90): P0186 (south, far), P0187 (south-east), P0188 (east end), P0189 (north), P0185 (the east octagon and colonnade). They give the storeys and widths as built, measured with 64 key points.
- **The plan S01** gives the frontage of 27.2 m, the scale of everything. It also gives the colonnades' traces (CCX-001, CCX-002), the pool (27.3 × 13.2 m) and the north stairs (23 m wide, 8.8 m deep).
- **The ruin's footprint** (S850, B) places the octagons 61.76 m apart. The boxes of Round 6 (`research/xiyanglou/boxes.csv`) place the block, the octagons and the pool.
- **S108** (Gao, Piao, Guo 2015, cited, not copied) says the cornices of the main block, the colonnades and the octagons stand at one level (Fig. 8), and gives the bays. **S310** gives the north basin's 4.5 m and agrees on the bays.
- **The fish 翻尾石鱼** of the south pool: 1.65 m long (S840, B).
- **Colours** come from the unfinished watercolour of plate 1 (S700, research-only, C): a yellow-ochre roof with an orange-red edge, buff frames, grey panels, blue-green windows.
- **Reading aids only**, never a figure: the Tsinghua and park reconstructions (R0004, R0042, R0097-R0099).

## How it was built (method)

1. **Key points.** Three readers worked from a fixed vocabulary (the point names in `keypoints.json`). They read the plates and photographs in the pixels of the 2400 px copies and wrote `research/xiyanglou/plate_keypoints.csv`, with `sure` 1-3, 174 points in all including 海晏堂. Each reading was checked with a cross on a fresh crop. A reading that is not a point of the model carries `use: skip` and its reason, and stays in the table.
2. **Cameras.** `tools/plate_overlay.py` fits a pinhole camera to each picture (position, bearing, pitch, focal length, principal point; no roll), starting from the viewpoint in `viewpoints.csv` or `photo_viewpoints.csv`. Each picture gets two fits, `anchored` (on the points the plan places) and `all`. A plate also gets `stretch`, which adds k, the plate's heights drawn k times its widths.
3. **Measure, then test.** The photographs are true perspectives, so the storeys come from them (`measure.py`, run twice until stable). The plates are then tested against that model, not tuned to it. The roofs, which no photograph shows, come from the plates.
4. **Overlays.** `tools/plate_overlay.mjs` renders the 3D view from every fitted camera (`3d.html?plate=<id>`). The composite step lays the render over the picture, as a 50 % blend, as red edges and side by side, and writes them to `screenshots/r13/`.

## Iteration log

| Version | What changed | Plate 1 (all) | Plate 2 (all) | Photographs (all, rms at the building) |
|---|---|---|---|---|
| v1 | The dossier's figures: storeys 5.0 / 10.0 / 15.1 m, ridge 18.3 m, depth 10 m (the box 14 m), colonnades as quarter circles | 84 px, 3.6 m | 48 px, 1.9 m | 0.9-3.3 m |
| v1 fix | The octagons' face points had left and right swapped (a bug in the generator) | 62 px, 2.7 m | 35 px, 1.1 m | P0185 3.0 → 0.4 m |
| v1 fix | The north stair: plate 2 and P0189 both show the lower flights running back towards the axis | | | |
| v1 fix | The colonnades as quarter ellipses from 1.4 m south of the flanks' middle (S01's traces) | | | |
| v2 | The storeys measured on P0185-P0189: H1 3.9, H2 8.7, top cornice 11.6, centre block 11.7, depth 8.6, octagon cornice 7.4, north feet 2.3 m. Roof 14.0 m, octagon apex 10.0 m from the plates | 62 px, 2.6 m | 43 px, 1.3 m | 0.3-0.6 m |
| v3 | The south stair's upper flights run north-south beside the landing, not along the façade: P0187's overlay showed it, and plate 1's treads agree on a second look. Landing 8 m (the outer pier at 0.45 of the half-frontage, P0186, P0187) | | | P0187 0.44 m |
| v4 | Plate 1's octagon readings were outline extremes, not face ends; they were renamed `oct?_lowout_*`, `oct?_upout_*` (the reader's notes say so) | 58 px, 2.4 m | 43 px, 1.3 m | unchanged |
| v4 | The `stretch` fit: plate 1's heights are drawn 1.57 times its widths, plate 2's 1.11 times | 37 px, 1.6 m (stretch) | 40 px, 1.3 m (stretch) | |
| tried, dropped | The pool's width and place measured on plate 1 alone: the pool ran 35 m into the lake, because the plate's depth is too compressed. S01's pool kept (Q223) | | | |
| v5 | The south stair's lower flights run out to the court at the terrace's ends, instead of ending against the wings. The model's entries and footprints are exported for the ways and the planting | 58 px, 2.4 m | 43 px, 1.3 m | 0.3-0.6 m |

## Final fit (v5, `research/xiyanglou/plate_fit_XY01.csv`)

| Picture | Points | Fit | rms px | median px | rms at the building | max | Camera |
|---|---|---|---|---|---|---|---|
| P0186, 1873, south, far | 15 | all | 9.5 | 9.0 | 0.58 m | 0.90 m | f 1610 px; 70 m off the catalogue's guess, from the south-east |
| P0187, 1873, south-east | 15 | all | 25.0 | 14.8 | 0.44 m | 0.84 m | f 1563 px |
| P0188, 1873, east end | 7 (+1 skipped) | all | 25.8 | 6.7 | 0.44 m | 1.11 m | f 1973 px |
| P0189, 1873, north | 21 | all | 21.2 | 22.2 | 0.59 m | 1.10 m | f 1128 px |
| P0185, 1873, east octagon | 6 | all | 13.5 | 7.3 | 0.29 m | 0.62 m | f 1687 px |
| Plate 2, north | 36 | all | 42.5 | 33.5 | 1.32 m | 3.05 m | f 1398 px, 8.9 m from the viewpoint |
| Plate 2 | 36 | stretch, k 1.11 | 40.1 | 30.8 | 1.26 m | 2.67 m | |
| Plate 2 | 36 | anchored | 53.5 | 37.5 | 1.69 m | 4.55 m | 8 m from the viewpoint |
| Plate 1, south | 43 (+4 skipped) | all | 57.7 | 42.9 | 2.43 m | 4.62 m | f 5877 px, 192 m back: a near-parallel projection |
| Plate 1 | 43 | stretch, k 1.57 | 36.8 | 27.2 | 1.59 m | 3.53 m | |
| Plate 1 | 43 | anchored | 111.5 | 97.2 | 4.89 m | 8.25 m | the viewpoint's camera, 18 m off |

**What the evidence allows.** On the photographs, a reading of sure 2 or 3 is 8-15 px. At 15-80 m with these focal lengths that is 0.1-0.7 m, so the model's residuals there are at the readers' noise. On the plates the limit is the engraving: plate 1 is drawn as a near-parallel elevation with its heights stretched, plate 2 nearly as a camera. What is left on them after the stretch (1.3-1.6 m) is the plates' own idealisation, listed below, and is not tuned away.

## Where the model and the pictures disagree, and which is likely right

- **The top storey and the centre block** (Q219). The plates draw them about 1.5 times as tall as P0186, P0187 and P0189 do, and 13.8-14.4 m wide against 11.7 m. The photographs are likely right: three of them from three sides agree, and a photograph does not idealise. The plates, made for the court, enlarge the hall's crown. Overall heights also rest on the frontage of 27.2 m (±15 %, Q72): P0189's porch door comes out 1.6 × 2.6 m at that scale, so the scale is about right.
- **The roof.** No photograph shows it (it burned in 1860). Its height, 14.0 m at the apex, is the plates' proportion of 0.17 of the top storey's width, set on the photographs' storey. A full camera fit on the plates gives 15.6 m, but that number is pulled up by their tall top storey.
- **The south stair** (Q220). The upper flights agree between plate 1 and the photographs. The lower flights' form is the plate's alone.
- **The north stair's feet** (Q221). P0189 puts them at 2.3 m from the axis, plate 2 further out. The model follows the photograph.
- **The colonnades' junctions** (Q222). The model follows S01's traces (B): from 1.4 m south of the flanks' middle to the octagons' north faces. Plate 1 shows the colonnade passing behind the octagon's diagonal face. The four readings at that point are skipped as silhouettes, not points.
- **The pool** (Q223). It is S01's 27.3 × 13.2 m. Plate 1 draws it wider than the block, and today's lined bank is 35.6 × 16.2 m. The 30 × 18 m in the round's brief is not in the data.
- **P0189's top storey** shows two blocks with a gap on the axis. This is plate 2's three-bay storey with its middle bay fallen by 1873: the side windows stand at ±0.59 of the storey's half-width in both. The model is the unbroken storey.

## Joints (tools/check_models.py, models/check_models.json)

- 22 contacts were measured against the walk surface of Round 10: wall feet, plinths, colonnade feet, stair feet, the pool's and the basin's feet. None floats (the highest is 0.01 m above the ground). The deepest sits 0.74 m into the ground: the north basin's paving ring, where the court rises. Most are 0.0-0.3 m in, a foundation course.
- The ways of Round 9 now snap to the model's own entries (`scripts/paths1860.py`, Round 13). The north axis CCX-005 meets the north stair's east foot at 0.0 m in plan and 0.1 m in height. Before, it ended 5.4 m off, against the old box's east flank, and two courtyard stubs of the old straight corridors ended 6.9 and 8.4 m off, on what is now the terrace. Those stubs are gone.
- The steps and galleries the model draws itself (CCX-001 to CCX-004) stay as S01 draws them. They are not drawn in the view and are recorded in `research/paths/exceptions.csv`.
- The planting keeps clear of the model's footprints, as it does of boxes.

## Assumed (C, carried round, `~fill` in the GLB: hidden with `?assumed=0`, pale with `?conf=1`)

- The west end of the main block is a mirror of the east end (P0188).
- The top storey's two ends.
- The rear faces of the colonnades and their rear rails.
- The octagons' north-facing faces and roof slopes.
- 21,558 of 88,252 triangles are fill.

The windows' glazing pattern, the pilasters, the cartouches and the entablature profiles are the plates' vocabulary set on the measured storeys. The urns and the roof ornaments are simplified.

## Next for this model

- The Yangshi Lei sheet 985 would replace most guesses (`research/wishlist.md`).
- The Ohlmer negatives at full resolution would sharpen the key points.
- A tape on site (one door, one riser) would check the scale.
