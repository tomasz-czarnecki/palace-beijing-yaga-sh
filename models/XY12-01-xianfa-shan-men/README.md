# XY12-01 线法山门 Xianfa Shan Men, the west gate of the perspective hill: the model built from plate 17 (Round 30)

The seventeenth detailed model of the project, made by the pilot's method (`models/XY01-xieqiqu/README.md`). It covers the gate in the west wall of the enclosure round 线法山 (the plan's 转马台), where the walk from 方外观 and 海晏堂 enters the hill's grounds (S02 p.159: 'a triple gate like a triumphal arch'):
- the **west front**: the **arch** in the middle with its moulded ring, its jambs' carved panels and a shell on the keystone; a square-headed **door** either side in a beaded frame under a scrolled hood and a **shell**; four **pilasters** on pedestals carved with a running chain of ornament, capitals with dentils and a carved dosseret; the **entablature** over the whole front with the frieze's long panels;
- the **crests**: the attic over the centre with its broken pediment, a cartouche and a shell, the **garland** with its crossed ribbons over it; crests of back-to-back scrolls with a garland ring over each side bay; **lyre finials** over the four pilasters; vases at the cornice's ends;
- the **scrolled buttresses** at the ends' feet; the **walls** north and south of the gate, panelled between pilasters under a coping, with two **urns** on pedestals before each next to the gate;
- the east face, the ends and the passages carried round from the west front (assumed, C).

It is a showcase of the method, not a one-to-one reconstruction. Every figure is C unless `params.json` says otherwise. The hill 线法山 (XY12) and its pavilion (XY12-02) stay the kit's and Round 10's.

Files:
- `xianfashanmen.py`, the generator, on `scripts/model_site.py` and `scripts/model_parts.py` (Round 30 added `shell`, `wreath`, `slab`, `scroll`, `rusticated` there); it writes `model.glb`, `params.json`, `keypoints.json`, `joints.json` and `summary.json`.
- `measure.py`: the walls read as lines on plate 17 by the camera fitted to the gate's own points; writes `measure.json`.
- The frame: origin at the west front's middle (box XY12-M55, which faces west), x south along the front (to the right seen from the west), y up, z west. The east face lies at z = -2.0.
- `level` (`joints.json`): the forecourt west of the gate, 75 x 32 m, where Round 10 had grown a hill of free land 4.3 m high north-west of the gate; plate 17 draws it level and planted with rows of clipped trees (Round 12's planting stays).
- Run: `uv run python models/XY12-01-xianfa-shan-men/xianfashanmen.py`, then step 6. The test: `tools/plate_overlay.py fit --object XY12-01 --shots screenshots/r30`, `node tools/plate_overlay.mjs --object XY12-01 --fits all --out screenshots/r30 --port 9162`, `tools/plate_overlay.py compose --object XY12-01 --shots screenshots/r30`, `uv run python models/XY12-01-xianfa-shan-men/measure.py`, `tools/check_models.py`. `XY12_WALLS=splay` (a test only, never in step 6) draws the walls at plate 17's vote.

## Evidence

Every picture used here is free, as `research/photos/catalog.csv` records. The research-only items (the clip frame P0717 of a 'newly found' photograph named 线法门; Sirén's arch P0315; the impressions at Manchester, the NYPL, the Getty and the V&A; the reconstructions R0133, R0139, R0182 as reading aids) are only cited.

**West front**
- **Plate 17** (P0057, 线法山门正面, 1783-86, the Palace Museum's impression): the whole west face, frontal on the axis, the walls either side, the forecourt of clipped trees and the paved walk. 33 key points (`research/xiyanglou/plate_keypoints.csv`), read at 2-3x on the 2400 px copy.

**East face, ends**
- No picture. Carried round from the west front (C).

**Ruin and today**
- No secure photograph of the gate standing or of its ruin is known (the dossier). The Giles photograph (P0768, the 1920s, CC BY) shows an arched gate between piers with vase finials and a carved crest in rubble walls; the holder queries the place, and it does not match plate 17 (one arch, no side doors, square panels on the piers, no attic): **not used**. P0717 (a clip frame, rights unclear) shows pilastered frames and fallen entablature blocks; the arch is not visible: not used.
- Today (P0362, P0767, P0361): the mound and the walk; nothing of the gate.

**Plan and texts**
- **The plan S01** (B): the gap in the hill's west wall, 13.58 m (b): the gate's width and place. The walls north and south of it, straight, about 30 m each to the strip's long walls.
- **S02 p.159** (B): Malone: the triple gate like a triumphal arch at the west of the hill. **S258 pp.184-185**: the plates' descriptions.

## How it was built

1. **v1** from a first reading of plate 17 at 1.5x, at the plan's 13.6 m over the body's width (57.9 px/m, the plate drawn frontally): 61 key points, the walls splayed towards the west at 24°.
2. **The readings at 2-3x** moved the arch (2.4 to 2.08 m wide, its crown 4.06 to 4.25 m), the doors' heads (2.42 to 2.65 m), the cornice (5.96 to 6.03 m), the attic and the crest; the first fit: 0.15 m rms (all), 0.23 m (anchored tests).
3. **The residuals**: the cornice projected 0.45 m beyond the body where the plate ends it 0.24 m out; the vases and the side crests stood 0.1-0.15 m in; the scrolls' tops 0.15 m in: fixed, 0.09 m rms.
4. **The walls as lines** (`measure.py`): the copings' samples on plate 17 against the projected coping for splay angles from -40 to 80° and heights 2.4-3.3 m. The plate's camera stands high (a bird's-eye view of the clipped trees, the eye 4.8-6.5 m up), and the copings vote for walls bending back **east** at 20-30°, 2.4 m high (4.9-6.5 px rms), not forward: S01's straight line fits at 17.4-17.8 px. But the plate's panels grow towards the sheet's edges as if the walls came forward. The plate's perspective is constructed here; the plan wins on positions: the walls stand on S01's straight line (Q312).
5. **The urns**: two a side on plate 17 (one in v1); placed 1.4 and 2.55 m along the wall from the gate (0.9 m off at first, the ground then 1.2 m higher on the north).
6. **Found on the shots and fixed**: a generated hill of Round 10 (4.3 m, free land, assumed) in the forecourt north-west of the gate, the north urns and walls standing on its slope: `level` over the forecourt.

## The fit

| Picture | Fit | Points | rms | max |
|---|---|---|---|---|
| plate 17 (P0057) | all / stretch (k 1.00) | 33 | 0.14 m (8.1 px) | 0.40 m |
| plate 17 (P0057) | anchored, the tests | 27 | 0.20 m (11.5 px) | 0.49 m |
| plate 17, the walls' copings as lines (`measure.py`) | straight (S01) / bending back east 20-30° | 9 samples | 17.4-17.8 px / 4.9-6.5 px | 26 / 11-14 px |

The fit tests the model against the plate it was read from, frontally, at one scale: it measures how consistently the readings became the model, not the gate's size, which rests on S01's gap.

## Where the model and the pictures disagree

- **The walls** (Q312): S01 draws them straight; plate 17's copings lean back east, its panels the other way. The model keeps the plan.
- **The pavilion on the hill** (XY12-02, the kit's) stands over the gate in the fitted camera's view; plate 17 draws only trees behind the gate. Plate 18 shows the pavilion; plate 17 may leave it out, or the pavilion's height (12.3 m over its platform, plate 18 on a weak module) is too much. Not tuned here.
- **The depth** (2.0 m), the east face and the passages are C: no picture shows them.
