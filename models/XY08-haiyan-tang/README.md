# XY08 海晏堂 Haiyantang, "Hall of the Calm Seas": the model built from the plates (Round 14)

The second detailed model of the project, made by the pilot's method (`models/XY01-xieqiqu/README.md`). It covers the whole complex, west to east:
- the **west block** (XY08, with the south wing XY08-AX001): eleven bays on two storeys, the end pavilions under square hip roofs, the attic with its broken pediment, the single-storey wing rooms with balustraded roofs;
- the **terrace** before the upper door with the cascade's parapet and its two fish;
- the two **stairs**, each an upper flight, a half-way landing and a long lower flight;
- the **water clock** 十二时辰水法 (XY08-02): the pool between the stairs, the twelve seated figures on their plinths, the great shell and the vase fountain;
- the two great **pedestals** and the paved court;
- the arcaded **link**;
- the **water building** 蓄水楼 of thirteen bays (XY08-N01 and XY08-01), with the reservoir 锡海 on its roof between two raised tiers;
- the **east block** with the zig-zag stairs (XY08-N02, N03).

It is a showcase of the method, not a one-to-one reconstruction. Every figure is C unless `params.json` says otherwise.

Files:
- `haiyantang.py` is the generator. It writes `model.glb`, `params.json`, `keypoints.json`, `joints.json` and `summary.json` (`models/README.md`). The façade, balustrade and roof helpers are shared in `scripts/model_parts.py` (lifted from the pilot, which keeps its own copies).
- `measure.py` is the pilot's joint fit of the photographs' cameras and the figures; `measure/measure_photos.json` is its run on Ohlmer's P0774.
- `views.json` lists the model's own views for `tools/plate_overlay.mjs --views` (front, rear, both sides, aerials, details, joints).
- Run: `uv run python models/XY08-haiyan-tang/haiyantang.py`, then `scripts/paths1860.py`, `scripts/kit1860.py`, `scripts/greens1860.py` and `scripts/building_pages.py` (it publishes the GLB). For the test:
  - `tools/plate_overlay.py fit --object XY08 --shots screenshots/r14 --parts 'west=^(blk|end_panel|midroof|attic|colW|wing|terr)_;water=^(wb|wbpav|link)_;east=^(es|wbpav_E)_;clock=^(zod|stair|pool12|shell|vase|ped)_'`
  - `node tools/plate_overlay.mjs --object XY08 --out screenshots/r14 --fits all,stretch,part_west,part_water,part_east,part_clock --views`
  - `tools/plate_overlay.py compose --object XY08 --shots screenshots/r14`
  - finally `tools/check_models.py`.

## Evidence

Every picture named here is free (public domain on Wikimedia Commons, or the Slovenian collection's free licence, as `research/photos/catalog.csv` records). The research-only items are only cited.

**West front**
- **Plate 10** (P0050, 1783-86, the Palace Museum impression): the eleven bays, the end pavilions and their roofs, the attic, the free columns at the upper door, the wings' balconies, the terrace and its cascade, the stairs, the twelve figures, the shell, the vase fountain, the pedestals, the court. 37 key points.
- **Ohlmer's photograph of 1873** (P0774, Teng Gu 1933): the front on the axis, roofs gone, walls to the attic. 4 key points behind trees.
- **The ruin photograph of about 1914-20** (P0303): the shell with its column and basin, between the stair walls. 3 key points, too few for a camera.

**North and south sides**
- **Plates 11 and 13** (P0051, P0053): the water building's thirteen bays (3 + 7 + 3, doors in the middle bay of each end section and on the axis, oval cartouches over the windows), the roof balustrade, the two raised tiers, the link's three arches, the west block's end faces and rear, the east block's side. 25 key points each.
- **P0299** (about 1914-20, from the south-east): the south face of the water building and the east block. 1 usable point.
- **P0775** (Ohlmer, 1873): a corner of the west block; which corner is not settled (south-west as printed), so not read.

**East end**
- **Plate 12** (P0052): the four flights a side, the passage door and its crest, the raised hall over the stairs. 13 key points.
- **P0170** (before or in 1902, from the north-east): the east end section's door and corner, the brick masses on the roof. 2 key points, too few for a camera.

**Plan and texts**
- **The plan S01** (B): the positions and the footprints. These are the west block's 47.2 m frontage (the scale of everything), the H hall before the upper door (7.54 m wide), the wing block B0154, the stair blocks, the pool's slip, the link (9.4 m), the water building's middle strip (19.1 m) and the east block (26.1 m).
- **The ruin's footprint** (S850, B): it places the pool and the reservoir block, and so the model's axis.
- **S310** (B): eleven bays on both levels, flat-roofed wing rooms with balustrades, peacock-green tiles with yellow ridges.
- **S310, S06, S109** (B): the reservoir, 27.36 x 5.92 m. **S600** (A, a Qing drawing at second hand): its depth, 1.44 m.
- **S604 via S415** (B): thirteen bays with two slight projections.
- **S849** (B): the bronze heads, about 0.5 m high.
- **S823** (C): the figures' order. South side 鼠 虎 龙 马 猴 狗, north side 牛 兔 蛇 羊 鸡 猪.
- **S822, S823, S817** (B): where the heads are today.
- **Reading aids only**, never a figure: the Tsinghua reconstructions (R0047, R0071) and the others in the dossier.

## How it was built

1. **v1 from the dossier.** The figures came from the plates' module (`dimensions.json`) and the boxes' places; the axis is the line through the ruin-placed pool and reservoir. Every footing follows the walk surface of Round 10 along its edges (`skirt`), so nothing floats and nothing sinks deep.
2. **Readers, in parallel.** Three readers worked from one vocabulary (`docs/rounds/common/palace_r14_haiyan_vocab.md`; the names in `models/README.md`): west (plate 10, P0774, P0303), sides (plates 11 and 13, P0299, P0775) and east (plate 12, P0170). They wrote 96 rows into `research/xiyanglou/plate_keypoints.csv`, each checked with a cross on a crop. Their notes on the form changed the model more than the points did: the bent stairs, the four flights, the long east tier.
3. **Fits, whole and by part.** Plates 11 and 13 draw the water building about 1.4 times as long against the west block as the plan and the ruin allow (Q225). One camera cannot fit both. `tools/plate_overlay.py --parts` gives each part a camera of its own, which tests each part's heights and widths without tuning the length away.
4. **Overlays.** The view from every fitted camera, as a blend, red edges and side by side (`screenshots/r14/overlay_*`).

## Iteration log

| Version | What changed | Plate 10 (all) | Plates 11 / 13 (west block / water building) | Plate 12 |
|---|---|---|---|---|
| kit (Round 13 baseline) | the stone kit's one long hip roof | 3.71 m | 2.0 m (7 points each, the west block only) | - |
| v1 | the dossier's figures; a terrace 19.8 m wide across the front; straight stairs | - | - | - |
| v2 | plate 10 and P0303: the stairs converge on a small landing before the door (the plan's H hall, 7.54 m); the shell at the V's apex; a paved court over the dip of the ground's own pool basin | 2.07 m | - | - |
| v3 | the readers' notes. The stairs bend: an upper flight outward, a landing, a lower flight forward along the pool, figure 1 by the landing. The wings move to the block's ends (Q226). The end sections project a quarter bay (Q227). The middle ridge's key point is moved to where it meets the pavilion's hip. The east block gets four flights a side. The link gets three arches and a flight up to the roof terrace | 1.65 m | 7.0 / 7.7 m whole; by part 0.49 / 1.5 m | 1.19 m |
| v4 | the water building's doors and windows to 4.2 m (half the storey, plate 11); the east tier a long hall 14.5 m N-S (plates 11-13); the east passage door 4.6 m; L2 4.8 m, L3 6.0 m; the vase 1.5 m, the shell 2.7 m; the pedestals lower and further in | 1.41 m | by part 0.49 / 1.32 and 0.49 / 1.39 m | 0.64 m |
| v5 | no change to the key points: the link's and the wings' faces opened (their own body boxes had covered the arches and windows); the semicircular arches built upward (`arc_pts` could start at -pi, and the outer arches hung downward; the same fix went into the pilot, where 20 of 204 arches hung down); the court among the footprints; the heads' muzzles blunter; plate 12's panels on the flights' walls | 1.41 m | as v4 | 0.64 m |

## Final fit (v5, `research/xiyanglou/plate_fit_XY08.csv`)

| Picture | Fit | Points | rms px | median px | rms at the object | max | Camera |
|---|---|---|---|---|---|---|---|
| Plate 10, west | all | 35 | 68.4 | 28.8 | 1.41 m | 3.07 m | f 4145 px, 60 m behind the viewpoint: a near-parallel elevation |
| Plate 10 | part west block | 18 | 20.6 | 15.6 | 0.58 m | 1.59 m | k 0.90 |
| Plate 10 | part water clock | 17 | 94.6 | 81.6 | 1.88 m | 2.98 m | the foreground, Q229 |
| Plate 11, north | part west block | 8 | 8.0 | 6.9 | 0.49 m | 0.92 m | |
| Plate 11 | part water building | 14 | 29.9 | 11.4 | 1.32 m | 4.46 m | the link's rail end 4.5 m; every other point within 1.5 m |
| Plate 11 | all | 25 | 139.5 | 83.3 | 5.21 m | 13.0 m | one camera cannot hold both parts (Q225) |
| Plate 13, south | part west block | 8 | 7.7 | 6.8 | 0.49 m | 0.82 m | |
| Plate 13 | part water building | 14 | 31.5 | 11.5 | 1.39 m | 4.82 m | the link's rail end 4.8 m |
| Plate 13 | all | 25 | 297.7 | 41.4 | 7.74 m | 22.6 m | as plate 11 |
| Plate 12, east | all | 13 | 39.5 | 24.5 | 0.64 m | 1.24 m | f 2195 px, 11 m from the viewpoint |
| P0774, 1873 | all | 4 | 18.8 | 18.1 | 0.73 m | 0.99 m | four points, eight unknowns: not a test |

**What the evidence allows.** On the plates a reading of sure 1-2 is 3-8 px. At these cameras that is 0.1-0.3 m at the building. The part fits of the west block (0.5-0.6 m) and of plate 12 (0.6 m) are close to that. The water building's median is 0.4 m. What is left is the plates' own drawing, listed below, and is not tuned away.

## Where the model and the pictures disagree, and which is likely right

- **The water building's length** (Q225). The plan and the ruin (38.4 m between the boxes; the reservoir's 27.36 m from the Qing figures) are taken as right. The plates draw the thirteen bays long, to show them all.
- **The wings** (Q226). The model follows plate 10 and P0774 (balconies at the ends) against the plan's B0154, 3.3 m in from the end. A frontal plate is reliable for places along the front; the plan draws a schematic outline here.
- **The end sections' projection** (Q227). The model takes the plates' quarter bay (0.75 m), not the plan's 3.35 m.
- **The attic** (Q228). P0774 gives 1.65 ± 0.42 m above the cornice, plate 10 2.6 m. The model keeps the plate until a second photograph confirms: one photograph of four points does not overrule it, though the plate likely enlarges the crown, as at 谐奇趣 (Q219).
- **Plate 10's foreground** (Q229). The plate draws the rim, the landings and the plinths' fronts 2-3 m further out than the model, and the feet 2 m further in. The model keeps S01's stair blocks.
- **The east block's width** (Q230). The model follows plate 12 and the plan (26.1 m). P0170 shows the east block's north side behind the water building's north front.
- **The east tier.** Plates 11 and 13 draw it as a long hall with its ridge running back; plate 12's fit agrees on about 14.5 m. The dossier's 9.3 m was plate 12's module taken at the stairs' depth.
- **The pavilions' ridges.** Plate 10 draws them about 3 m long; the model's square roofs give 0.8 m. The ridge ends are 1.1-1.6 m off.
- **The brick masses on the roof** (P0170). They stand 0.6-0.7 of a storey above the cornice in 1902, and the east reader saw the east tier's walls in them. The model's reservoir parapet is 1.7 m high, which plates 11 and 13 allow: they show nothing behind the roof balustrade.

## Joints (tools/check_models.py, models/check_models.json)

- **56 contacts with the walk surface of Round 10:** wall feet, the wing rooms, the terrace, the plinths, the stair feet, the pedestals, the court, the link, the water building's sections and the east block's corners. None floats (the highest is 0.11 m into the ground); the deepest is 0.21 m in. Before the change to footings that follow the ground (v1), six contacts were 1.2-2.8 m deep.
- **The ways.** Seven ways end at the model's boxes, none off. Four of them, the stairs CCX-015 and 016 and the link and middle CCX-018 and 019, are drawn by the model and listed in `research/paths/exceptions.csv`.
- **The ground's pool.** Round 10 holds the pool as a water body 1.5 m below the court. The model's pool and its paved court cover it.

## Assumed (C, carried round, `~fill` in the GLB: hidden with `?assumed=0`, pale with `?conf=1`)

- The stairs' outer walls and the bend's outer face; no picture shows them.
- The reservoir's parapet and its tin-lined basin on the roof.
- The west face of the water building against the link, and the faces of the raised tiers turned to the reservoir; the west tier's west face.
- The wings' inner faces.
- The great pedestals' backs.

Only about 2,000 of 72,900 triangles are fill: this building is drawn from all four sides. The twelve figures are simple forms: a stone pedestal, a seated robed body and a bronze head with a short muzzle. No species features are modelled. The heads stand in the plates' and S823's order, which the west reader's identifications on plate 10 agree with, row by row (uncertain).

## Next for this model

- 样式雷 东水车房 底样 (样094-4) and the other 海晏堂 sheets: the east block and the raised tiers.
- A second photograph of the west front: the attic and the storeys (Q228).
- The report of the 2015 dig: the stair blocks and the pool in plan (Q229).
