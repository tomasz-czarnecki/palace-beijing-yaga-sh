# XY05 养雀笼 Yangque Long, the aviary gate: the model built from the plates and the photographs (Round 26)

The thirteenth detailed model of the project, made by the pilot's method (`models/XY01-xieqiqu/README.md`). It covers the gate between the court behind 谐奇趣 and the east garden, with the bird rooms either side of its passage (S02 p.147; S310):
- the **west front**, a Chinese gate of five roofs: the **portico** of two tall red columns under the highest, shallow roof with its two finials and the scrolled crest, the arched **door** in its carved frame with a carved transom over it; either side a **cage wall** (a net of bars over the opening, a fan-headed window in it, the bird room dark behind); each wing's corner **column** and a second behind it (the open bay), the wings' shallow roofs with finials, the lowest roofs at the ends; two **statues** on lotus pedestals before the cage windows (plate 6);
- the **east front**, a European gate front, **concave**: the end pavilions of two columns on pedestals and a pier, the shell **niches** with their fountain stems over shell basins, the **arch** with its iron gate, the scrolled cartouche over it and the lattice panels, the cornice, the **balustrade** with its finials and the **crest** over the middle; the low walls either side (plate 7; P0192, P0175, P0178, P0168);
- the range's ends with blind arched panels (carried, assumed), the roof terrace, the passage, the paved aprons.

It is a showcase of the method, not a one-to-one reconstruction. Every figure is C unless `params.json` says otherwise. The court north of it (XY05-N01, XY05-AX002) stays the kit's.

Files:
- `yangquelong.py`, the generator, on `scripts/model_site.py` and `scripts/model_parts.py`; it writes `model.glb`, `params.json`, `keypoints.json`, `joints.json` and `summary.json`.
- The frame: origin at the west front's middle (box XY05-M25, which faces west), x south along the west front (to the right seen from the west), y up, z west. The east front lies at z -9.8 (the arch) to -11.6 (the ends).
- `hides`: GB36, the walls layer's gate G36 ('passage through 养雀笼'), left at the plan's place 13 m east of the gate's box when Round 6 moved the box onto the ruin: a phantom of this gate's own passage.
- Run: `uv run python models/XY05-yangque-long/yangquelong.py`, then step 6. The test: `tools/plate_overlay.py fit --object XY05 --shots screenshots/r26`, `node tools/plate_overlay.mjs --object XY05 --fits all --out screenshots/r26`, `tools/plate_overlay.py compose --object XY05 --shots screenshots/r26`, `tools/check_models.py`.

## Evidence

Every picture named here is free, as `research/photos/catalog.csv` records. The research-only items (Sirén's photograph of plate 7, P0210; Moore's view, P0225; the impressions at Manchester, the NYPL, the Getty and the V&A; the reconstructions R0139, R0314 as reading aids) are only cited.

**West front**
- **Plate 6** (P0046, 养雀笼西面, 1783-86): the portico, the door, the cage walls with their windows, the wings' columns and roofs, the lowest roofs, the statues; the hall of XY05-N01 at the left. 25 key points.

**East front**
- **Plate 7** (P0047, 养雀笼东面, 1783-86): the whole east front, the iron gate, the low walls either side, the parterre and the bridge before it. 22 key points.
- **Thomas Child, 1870s** (P0192): the arch, the piers' scrolled capitals, the niches with their fountains, the cartouche, the lattice panels, the cornice and the balustrade as they stood; the base cut by the frame. 9 key points.
- **The ruin, about 1900-1922** (P0175, P0178, P0168): the arch and the niches, the upper parts fallen. 6 key points each.
- **Today** (P0352, P0740, P0353): blocks on the footprint, half-round shell fragments: no form beyond the shell heads.

**Plan and texts**
- **The plan S01** (B): the gate range 13.89 m N-S, 11.65 m with the centre's projection.
- **S02 p.147** (B): from the west almost a Chinese five-roof archway, from the east a European arch of three bays, carved marble fountains either side of the door; peacocks kept until the Jiaqing reign. **S310** (B, search extracts): built 1759; the side rooms for the birds; a small water tower under the arch window outside each front. **S258 p.180** (B): Avril's description.
- **S817, S141** (B): the west gate's four piers returned in 2013; the dig of 2015.

## How it was built

1. **v1** from the dossier's readings (Round 6) and the plates.
2. **Fits** with the readers' 74 points: plate 6 0.53 m, plate 7 0.38 m, the photographs 0.07-0.17 m.
3. **v2 from the readers and the residuals**:
   - plate 6: the columns stand in one line (their feet at one height), the cage walls 2 m behind with no columns before them; the west roofs are **shallow**, like a 牌坊's (the central ridge 4.1 m between eave tips 6.1 m apart): 0.53 to 0.22 m;
   - the east arch a **half circle** (the four photographs) against plate 7's taller head; the piers' capitals one arch-width above the imposts (P0192); the niches' crowns 0.25 m lower (P0192 fitted): P0192 0.13 to 0.05 m.
4. **Found on the shots and fixed**: a blank wall over the west door (now the carved transom of plate 6); blank end walls (now blind arched panels, carried, C); the walls layer's gate box G36 standing before the east front (`hides`).

## The fit

| Picture | Fit | Points | rms | max |
|---|---|---|---|---|
| plate 6 (P0046) | all / stretch (k 1.02) / anchored | 25 | 0.22 / 0.21 / 0.25 m (11.1 px) | 0.52 m |
| plate 7 (P0047) | all / stretch (k 0.94) | 22 | 0.42 / 0.35 m (25.5 px) | 0.86 m |
| Child, 1870s (P0192) | all | 9 | 0.05 m (6.4 px) | 0.09 m |
| P0175 | all | 6 | 0.06 m (4.9 px) | 0.10 m |
| P0178 | all | 6 | 0.13 m (11.4 px) | 0.25 m |
| P0168 | all | 6 | 0.16 m (10.1 px) | 0.34 m |

## Where the model and the pictures disagree

- **Plate 7 draws the arch and the niches taller** than the stone stood: the arch's rise 1.31 times its half-width (the photographs 1.0-1.05), the niches' crowns 0.5 m higher. The photographs win (Q293).
- **The capitals**: plate 7 draws the piers' capitals beside the arch as Corinthian, the photographs show scrolled capitals; the model draws a plain block for both.
- **The concave plan** is faceted in five straight faces; P0192 shows a continuous curve (C).
- **No survey or plan of the gate's own** is in hand (it was pulled down about 1924); the depth of the range, the passage and the rooms are C.

## Iteration log

- v1: 9,761 triangles; plate 6 0.53 m, plate 7 0.38 m, P0192 0.13 m.
- v2: 10,381 triangles (812 fill), GLB 0.34 MB, 0.09 MB compressed; plate 6 0.22 m, plate 7 0.42 m, P0192 0.05 m.
