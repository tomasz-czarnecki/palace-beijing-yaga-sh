# XY13 螺蛳牌楼 Luosi Pailou, the east gate of the perspective hill: the model built from plate 19 (Round 30)

The eighteenth detailed model of the project, made by the pilot's method (`models/XY01-xieqiqu/README.md`). It covers the gate east of 线法山 that faces west, towards the hill, with 方河 and 线法墙 behind it (plate 19, 线法山东门; S02 p.159: 'three arches, the side passages leading through side rooms, vine ornament carved even over the faces of the pillars'):
- the **west front**: the **arch** between two free **columns**, a square-headed **door** either side under a shell between scrolls, the outer columns, the **end bays** with their sunk panels; the **carved vines** climbing every pier from a vase at its foot and winding round the columns' shafts;
- the **wavy cornice**: higher over the outer columns than over the inner ones, sagging a little between them under the towers, rising in a curve over the arch;
- the **attic** over the centre with its broken scroll pediment and fluted frieze, the **trophy group** on it; trophies of arms over the inner columns and trophies with a **round shield** over the outer ones; urns at the ends;
- a **tower** over each side bay: a body with scrolls and a cartouche, a flared cornice, a concave pyramidal cap, a lantern's plate and an **urn**;
- the east face, the ends, the passages and the side rooms carried round from the west front (assumed, C).

It is a showcase of the method, not a one-to-one reconstruction. Every figure is C unless `params.json` says otherwise.

Files:
- `luosipailou.py`, the generator, on `scripts/model_site.py` and `scripts/model_parts.py`; it writes `model.glb`, `params.json`, `keypoints.json`, `joints.json` and `summary.json`.
- The frame: origin at the west front's middle (box XY13-M56, which faces west), x south along the front (to the right seen from the west), y up, z west. The east face lies at z = -3.0.
- `hides`: GB39, the kit's default gate hall on the walls layer's gate G39 ('wall gap east of 线法山, towards 螺蛳牌楼'), 20 m west of the gate on its axis. S01 draws a gap there with no gate, and plate 19, taken from about 36 m west on the axis, looks through that place and shows paving and clipped trees: a phantom in the plate's view. From Round 30 `scripts/kit1860.py` gives a box a model hides no court either (its apron had stood in the same view).
- Run: `uv run python models/XY13-luosi-pailou/luosipailou.py`, then step 6. The test: `tools/plate_overlay.py fit --object XY13 --shots screenshots/r30`, `node tools/plate_overlay.mjs --object XY13 --fits all --out screenshots/r30 --port 9162`, `tools/plate_overlay.py compose --object XY13 --shots screenshots/r30`, `tools/check_models.py`.

## Evidence

Every picture used here is free, as `research/photos/catalog.csv` records. The research-only items (Moore's negative J-00426, 'Xianfashan east gate' per a blog, not seen, P0225; Sirén's arch P0315, not identified; the impressions at Manchester, the NYPL, the Getty and the V&A; the reconstruction R0139 as a reading aid) are only cited.

**West front**
- **Plate 19** (P0059, 线法山东门, 1783-86, the Palace Museum's impression; Honolulu's of 3780 px is free too): the whole west face, frontal on the axis, water and painted hills seen through the arch, the paved court with clipped trees, rocks and trees either side. 41 key points, read at 1.3-2.2x on the 2400 px copy.

**East face, ends**
- No picture. Carried round from the west front (C).

**Ruin**
- **Moore, 1870s-80s** (S838 Fig. 6, as the dossier records it): the gate standing, with the carved vine on the pillars; the photograph is not in hand (P0225, research-only, not seen). Its later fate is not found.

**Plan and texts**
- **The plan S01** (B): an ornamental figure 34-49 m long north-south with cloud-shaped ends, labelled 螺蛳牌楼: no size for the gate (Q73).
- **S02 p.159** (B): three arches, the side passages through side rooms, vine ornament carved on the pillars.

## How it was built

1. **v1** from a first reading of plate 19 at 1.33x, at the dossier's frontage 22.9 m over x 693-1705 (the dossier's module, the arch taken as 3 m: weak).
2. **The readings at 1.3-2.2x**: the axis at x 1191; the arch 2.82 m (not 2.94), the doors 6.29 m from the axis (not 6.18), their heads 3.55 m, the shells 5.5 m; the cornice is wavy, 6.9 m over the outer columns and 6.6 over the inner ones, 7.36 m on the axis, where v1 had one height over every column and a dip of 0.5 m; the attic 8.5 m and 3.7 m wide (v1 9.2 and 2.8 m), the towers' cornices 9.1 m.
3. **Fits**: 0.21 m rms (all) before the attic's width, 0.19 m after.
4. **Found on the shots and fixed**: the columns, the vases and the lantern urns were drawn twice turned (lathe in a face frame given model coordinates); the default gate hall GB39 and its court in plate 19's view (`hides`, and the kit's rule for courts).

## The fit

| Picture | Fit | Points | rms | max |
|---|---|---|---|---|
| plate 19 (P0059) | all | 41 | 0.19 m (8.3 px) | 0.46 m |
| plate 19 (P0059) | anchored, the tests | 33 | 0.45 m (18.7 px) | 0.89 m |

The plate is drawn frontally and the model was read from it at one scale: the fit tests the model's consistency with the plate, not the gate's size, which rests on the dossier's weak module.

## Where the model and the pictures disagree

- **The size** (Q73): 22.9 m on the dossier's module against S01's ornamental 34-49 m. A door of 1.25 x 3.55 m, an arch of 2.82 x 5.77 m: tall for a garden gate but not impossible. Moore's photograph, with a person or a known course, would settle it.
- **The plate is not quite symmetric**: the south tower stands 287 px from the axis, the north one 267 px; the model is symmetric (the mean).
- **The depth** (3.0 m), the side rooms, the east face and the passages are C: no picture shows them.
