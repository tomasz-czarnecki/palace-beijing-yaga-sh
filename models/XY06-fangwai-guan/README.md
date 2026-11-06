# XY06 方外观 Fangwaiguan, "A Look Abroad": the model built from the plate and the photographs (Round 16)

The sixth detailed model of the project, made by the pilot's method (`models/XY01-xieqiqu/README.md`). It covers the small two-storey pavilion of the Xiyang Lou:
- the rusticated **podium** (the 'low room under the terrace', S258) with its end panels of stacked blocks, the two **oval windows** with grilles in carved frames, the **porch** with the door and its shell hood, three round steps;
- the walk on the podium's top with its **balustrade** before the side windows and the **balcony** over the porch with urn pairs;
- the **upper storey** set back behind the walk: three tall round-headed windows to the floor with scrolled broken pediments, carved corner strips, a frieze of rosettes, the cornice; a window with a small balcony on each end;
- the **double-eaved Chinese roof**: a skirt from the cornice, the upper hipped roof with a short ridge, the crest cartouche and the ridge-end ornaments;
- the two **curved stairs**: from feet at the front 3.4 m beyond the podium's corners, out to 4.6 m and back to landings in the north half of the ends, solid walls under them, a wave-scroll parapet, a volute at the foot;
- a paved apron before the front.

It is a showcase of the method, not a one-to-one reconstruction. Every figure is C unless `params.json` says otherwise. The scrolled bridges of the axial walk (XY06-N01) and the kiosk at the left of plate 8 (XY06-B0151) are not part of it.

Files:
- `fangwaiguan.py`, the generator, on `scripts/model_site.py` and `scripts/model_parts.py`; it writes `model.glb`, `params.json`, `keypoints.json`, `joints.json` and `summary.json`.
- The frame: origin at the front middle of the hall's box XY06-M27 (the podium's front face), x east, y up, z south.
- Run: `uv run python models/XY06-fangwai-guan/fangwaiguan.py`, then `scripts/paths1860.py`, `scripts/kit1860.py`, `scripts/greens1860.py`, `scripts/building_pages.py`. The test: `tools/plate_overlay.py fit --object XY06 --shots screenshots/r16`, `node tools/plate_overlay.mjs --object XY06 --fits all,stretch --out screenshots/r16`, `tools/plate_overlay.py compose --object XY06 --shots screenshots/r16`, `tools/check_models.py`.

## Evidence

Every picture named here is free, as `research/photos/catalog.csv` records. The research-only items (P0211, P0220, P0720, Durand's figures R0141, R0142, Jin Xun's plan R0144) are only cited.

**South front and ends**
- **Plate 8** (P0048, 1783-86, the Palace Museum impression): the whole front: the podium, the porch, the ovals, the upper storey, the balustrades, both roofs, the crest, both stairs. 38 key points, 1 skip (reader 3).
- **Ohlmer's photograph of 1873** (P0773, Teng Gu 1933): the roof still on; the end face with its window and balcony, the stair's wave-scroll parapet rising to a landing north of that window, the front's windows and an oval. 9 key points, 5 skip. Read here as the **east** end from the south-east (Q238).
- **1914-1922** (P0212 of 1922, P0296, P0304, P0295 of the album bought 1914-20): the porch's piers, the door, the ovals whole in their frames, the stairs' walls. 6 + 2 + 2 + 2 key points (the last three too few for a camera).
- **Today** (P0355 of 2013): the porch's piers on the axis. 4 key points.

**Plan, survey and texts**
- **Durand's survey** (S603, B): 14 × 7 m without the stairs, 13 m high; the roof by hypothesis (p.131).
- **The plan S01** (B): the hall 13.85 m, with both stairs 24.6 × 13.3 m.
- **S258** (B): the low room under the terrace with a door and two grilled ovals. **S02 pp.147-148** (B): curved stairs from the second floor at both sides; the bridge's carved scroll balustrades.
- **S838, S828** (B): the Chinese-style roof kept after 1860 (photographs of the 1870s); Choutzé's 'seul pavillon' with violet and green tile in 1876, tied to this one by inference (Q69).
- **Reading aids only**, never a figure: R0004, R0042, R0093, R0139, R0141, R0142, R0144.

## How it was built

1. **v1 from the dossier and reader 3's notes**: the 14 m module on plate 8 (47.6 px/m), the podium 3.8 m, the upper storey 4.9 m set in 0.55 m at the ends and 1.0 m behind the walk (assumed), the roofs' tiers, half-circle stairs landing in the north half of the ends (P0773, P0295).
2. **Fits** with the reader's camera priors. P0773 fitted badly as a view from the south-west (1.47 m, the oval 1.7 m off): its front recedes to the left of the near corner and its end face, with the balcony, lies to the right, which only a view from the south-east (or a mirrored print) gives. Relabelled W to E with the prior mirrored across the axis, the building's points fit within 0.7 m (Q238).
3. **v2-v3** from the residuals: the walk's balustrade ends 5.0 m out and turns back to the wall (plate 8), deeper round steps, the stairs' outermost point at mid-height, the ovals 1.0 × 1.8 m (P0212: the stone as it stood, against the plate's 1.4 m), and two flaws found on the shots (the footing skirts covered the door and the ovals; the oval frame's centre covered its glass).

## Iteration log

| Version | What changed | Plate 8 | P0212 | P0355 | P0773 |
|---|---|---|---|---|---|
| kit (Round 11) | the stone kit's block of 14 × 7 m with arches and a pediment | no points of this vocabulary | | | |
| v1 | the dossier's and the reader's figures | 0.50 m | 0.53 m | 0.26 m | 1.47 m (as the west end) |
| v2 | P0773 read as the east end; the balustrade's runs to 5.0 m; round steps 0.5 m deep; the stairs' outermost point at mid-height | 0.31 m | 0.53 m | 0.26 m | 0.77 m |
| v3 (final) | ovals 1.0 × 1.8 m; the skirts off the door and the ovals; the oval frames as rings | 0.32 m | 0.51 m | 0.26 m | 0.74 m |

## Final fit (v3, `research/xiyanglou/plate_fit_XY06.csv`)

| Picture | Fit | Points | rms px | median px | rms at the object | max | Camera |
|---|---|---|---|---|---|---|---|
| Plate 8 (P0048) | all | 38 | 15.1 | 9.3 | 0.32 m | 0.95 m | f 3958 px, 50 m back from the prior, the eye at the ground: a near-elevation, drawn with almost no perspective |
| Plate 8 | stretch | 38 | 15.0 | 9.4 | 0.32 m | 0.96 m | k 1.00 |
| P0212, 1922 | all | 6 | 24.8 | 14.3 | 0.51 m | 0.94 m | the podium's corner 0.9 m off: six points |
| P0355, 2013 | all | 4 | 17.7 | 14.8 | 0.26 m | 0.42 m | |
| P0773, 1873 | all | 9 | 38.0 | 11.4 | 0.74 m | 1.68 m | as the east end from the south-east; the stair's top and the far cornice corner off (Q238) |

Largest residuals on plate 8: the stair's outermost post (0.95 m: the plate draws it higher), the round steps' foot (0.7 m), the stairs' tops (0.45-0.6 m).

## Joints (`joints.json`, `tools/check_models.py`)

- 13 joints: the podium's corners, the porch's, the round steps, the stairs' feet and their walls: none floats (highest 0.05 m into the ground), deepest 0.15 m; v1's 15 the same.
- The way to the door ends at the round steps' foot: 0 off.

## Where the model and the pictures disagree

- **P0773's side (Q238).** Catalogued as the south-west corner; the geometry says the east end from the south-east, or a mirrored print. The model is symmetric, so the fit cannot tell the two apart; the MIT copy of the same negative (P0720, research-only) could.
- **The end face's depth (Q238).** On P0773 the far cornice corner and the end window sit 0.8-1.2 m further back than Durand's 7 m allows. One photograph against a survey: 7 m is kept.
- **The stairs.** The plate draws S-scrolls between posts on the outer parapet; P0773 one continuous wave-scroll band (modelled). P0773's rail top at the landing sits 1.7 m off the model's, most of it in height: the rail may end lower and the landing post rise above it.
- **The ovals.** Plate 8 1.4 m high, P0212 and P0296 about 1.9 m: the photographs win (1.8 m).
- **The roof's colour.** S06's blue (through the box's row, C); violet and green if Choutzé's pavilion of 1876 is this one (Q69).
