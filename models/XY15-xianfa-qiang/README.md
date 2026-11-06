# XY15 线法墙 Xianfa Qiang, the perspective walls east of 方河: the model built from plate 20 and the plan (Round 30)

The nineteenth detailed model of the project, made by the pilot's method (`models/XY01-xieqiqu/README.md`). It covers the outdoor stage at the east end of the Xiyang Lou: flats set like the wings of a stage, narrowing towards a back wall, with a European town painted across them, seen from across the water of 方河 (S02 pp.159-160; S01's 线法画; plate 20, 湖东线法画):
- the **two gates** plate 20 draws at its edges, on the first pair of flats nearest the water: piers of **banded rusticated blocks**, an **arch** with radiating voussoirs and a keystone, corbels with figures under the cornice, a **hipped stone cap** with an urn at each end of its short ridge and a **pineapple** on its middle, a **lion** on a ball on a console at each outer corner;
- **five more pairs of flats** on S01's places (six a side in all), each 7.3 m wide, cut to the outline of two painted houses whose eaves fall towards the axis as a street's would, with their gables or hipped roofs, dormers and chimneys, windows in rows and a door in low relief, braced behind with raking posts;
- the **back wall** with a range of hills on it;
- the **landing**: six steps with rounded ends, each wider than the one above, from the stage down into 方河 on the axis.
The two five-bay ranges at the north and south ends (XY15-N01, -N02) stay the kit's.

It is a showcase of the method, not a one-to-one reconstruction. **The painted scenes are lost**: every flat's outline and relief is assumed (C), drawn as the fill; only the gates and the landing are drawn from plate 20.

Files:
- `xianfaqiang.py`, the generator, on `scripts/model_site.py` and `scripts/model_parts.py`; it writes `model.glb`, `params.json`, `keypoints.json`, `joints.json`, `summary.json` and `report.json` (the landing's levels).
- The frame: origin at the back wall's west front's middle (box XY15-M69, which faces west), x south, y up, z west (towards 方河). Each flat stands on its own box of Round 6 (S01's elements, moved 5 m as 方河 is): pair 1 at z 31-32 m, pair 6 at z 5 m.
- The bank: `research/terrain/readings.csv` R10-476 (Round 30) makes 方河's east shore a stone quay (plate 20, A), so that the stage meets the water at the quay's height and the landing's top step at the ground (Round 10 had an earth slope there, 1.3 m down over 12 m).
- Run: `uv run python models/XY15-xianfa-qiang/xianfaqiang.py`, then step 6 (the ground first, for the quay). The test: `tools/plate_overlay.py fit --object XY15 --shots screenshots/r30 --parts 'gL=^gate_L_;gR=^gate_R_'`, `node tools/plate_overlay.mjs --object XY15 --fits all --out screenshots/r30 --port 9162`, `tools/plate_overlay.py compose --object XY15 --shots screenshots/r30`, `tools/check_models.py`.

## Evidence

Every picture used here is free, as `research/photos/catalog.csv` records. The research-only items (the Lei plan 线法墙地样, E0993, E2415, E2418, known by title and an extract; the impressions at Manchester, the NYPL, the Getty and the V&A; the reconstructions R0139, R0182) are only cited.

**West (the stage, seen from the water)**
- **Plate 20** (P0060, 湖东线法画, 1783-86, the Palace Museum's impression): the two gates at the edges, the painted town receding to hills, 方河's east bank with its coping and buttresses and the landing on the axis. 32 key points.

**Backs, ends**
- No picture. The flats' backs and bracing are assumed (C).

**Plan and texts**
- **The plan S01** (B): six elements a side, 7.27 x 1.8 m, stepping in towards a back wall 13.5 m long; the two five-bay ranges; the label 线法画.
- **S02 pp.159-160** (B): houses partly modeled and partly painted on walls, five on each side, set like the wings of a stage, a back wall; Malone's photograph shows walls like wings still standing. **S361 v4 p.121**: pictures hung on the walls. **S310** (extract): a Lei plan with eleven walls in all.

## How it was built

1. **v1** from S01's boxes and a first reading of plate 20: the gates at the plan's 7.3 m (the left gate 7.97 m to its cornice on its own width), the flats cut to a street's eaves falling to the eye's height on the axis, the back wall 6 m, five steps.
2. **Readings at 1.4-1.6x**: the left gate 350 px wide (cornice 7.97 m, ridge 9.62, pineapple 10.8 m); the right gate 300 px wide with its cornice at 9.29 m on its own width: the plate draws the two gates **17% apart in proportion** (Q314). The model takes their mean (cornice 8.6 m, near the dossier's 8.7 m). Six steps, not five.
3. **The bank**: the landing found the water 14 m west of the gates down an earth slope; plate 20 draws a coped stone bank; R10-476 makes it a stone quay and the stage meets it.
4. **The cap**: a hip roof over the flat's 1.65 m depth carries a ridge 6.2 m long; plate 20's ridges are 3.75-3.96 m: the cap is drawn as a trapezoid front and back with steep ends. Each gate on its own camera: 0.64 and 0.87 m before, 0.23 and 0.36 m after.
5. **The whole plate** fits at 1.5 m rms with one camera (0.99 m with the plate's heights stretched 1.29 times): the plate draws the gates nearer the water than the plan has them, and the two gates inconsistently (Q313, Q314). Not tuned.

## The fit

| Picture | Fit | Points | rms | max |
|---|---|---|---|---|
| plate 20 (P0060), the north gate alone | part gL | 14 | 0.23 m (10.8 px) | 0.60 m |
| plate 20 (P0060), the south gate alone | part gR | 14 | 0.36 m (14.9 px) | 0.75 m |
| plate 20 (P0060), the whole | all / stretch (k 1.29) | 32 | 1.51 / 0.99 m | 2.64 m |

## Where the model and the pictures disagree

- **The stage's depth** (Q313): S01 puts 方河's end about 10 m before the first flats, Round 10's water 14 m; plate 20 draws the gates close behind the bank's coping. The plan wins on positions.
- **The two gates** (Q314): the right gate is drawn 17% taller for its width and lower on the sheet than the left, though the plan puts them 1.3 m apart in depth. The model takes the mean of their proportions.
- **The painted scenes**: lost. Plate 20 shows a town of tall houses receding to hills, but how much of it was modelled in relief and how much painted, and on what (S02: modeled and painted on walls; S361: pictures hung on them), is not settled. The flats' outlines and their relief are a guess (C, the fill).
- **The number of flats** (Q16, Q73): six a side as S01 draws them; S02 says five, S361 seven, a Lei plan eleven in all.
