# XY11 观水法 Guanshuifa, "View of the Fountains": the model built from the plate and the photographs (Round 15)

The fourth detailed model, made by the pilot's method (`models/XY01-xieqiqu/README.md`). It covers the emperor's seat at the south edge of the sunken court, facing 大水法:
- the concave **screen**: five carved marble panels of European arms on their plinth blocks, a socle with relief panels, four pilasters, double end piers, the entablature with a frieze of drops, a low openwork crest with a cartouche on the axis, eight urns; the brick backing behind;
- the round **platform** with five convex steps, the **throne** with its canopy, the low **balustrade** with trophies;
- the two **trophy pedestals** before the end piers and the two **obelisks** beyond them;
- the gardens' **strip** behind and beside the screen, 1.30 m above the court, with the **side gates**, their flights down into the court, the clipped **hedges** and the plain **back wall**.

It is a showcase of the method, not a one-to-one reconstruction. Every figure is C unless `params.json` says otherwise. The panels stand where the park set them in 1977 ("on their old spot", S817); the platform survives in place (S603 p.129). The trophies are drawn as plain raised forms (a shield, crossed arms, a knot of ribbon), not copied.

Files:
- `guanshuifa.py`, the generator (outputs as `models/README.md`), with `scripts/model_parts.py` and `scripts/model_site.py`.
- Run: `uv run python models/XY11-guan-shuifa/guanshuifa.py`, then `scripts/paths1860.py`, `scripts/kit1860.py`, `scripts/greens1860.py` and `scripts/building_pages.py`. The test: `tools/plate_overlay.py fit --object XY11 --shots screenshots/r15`, `node tools/plate_overlay.mjs --object XY11 --fits all,stretch --out screenshots/r15`, `tools/plate_overlay.py compose --object XY11 --shots screenshots/r15`, then `tools/check_models.py`.

## Evidence

Every picture named here is free (Wikimedia Commons, the Slovenian collection's free licence, Teng Gu 1933 on Commons). The research-only items (P0323, P0724, the Tsinghua reconstruction R0025) are only cited.

**North face (the court's side)**
- **Plate 16** (P0056, 1783-86): the whole face. The screen's five panels, pilasters, end piers, cornice, crest and finials; the platform, its steps, the throne, the balustrade with trophies, the trophy pedestals, the obelisks; the two gates with their flights, the hedges, the back wall, the court's curved bands. 33 key points.
- **Ohlmer's photograph of 1873** (P0777): the concave screen from the north-east with its cornice and crest, worn. 16 key points.
- **P0300** (1914-20): the panels still in their brick backing, the plain slabs between. 8 key points.
- **Today**: P0640, P0343, P0764 (on the axis or near it), P0344, P0765 (from the north-west): the panels, the socle, the end piers, the five convex steps, the round platform, the obelisks on their bases. 9 + 10 + 17 + 9 + 16 key points (5 skip: the obelisks' tops are cut, and an unsure reading).

**The gates**
- **P0193** (Thomas Child, 1870s; P0194 the same negative): a side gate on its steps, its proportions (height 1.06 times the width), the arch, the carved piers, the bell-shaped cornice with its shell crest.

**South (the gardens' side)**: no picture. The screen's brick back, the wall's south face and the gates' backs are carried round (fill).

**Plan and texts**
- **The plan S01** (B): the arc of the screen with the platform before it, 14.46 m; the two gates as skewed squares 33.86 m apart.
- **Durand** (S603, B): the socle 1.30 m, the court's drop the same; the platform in place without its balustrades.
- **S02 pp.157-159** (B): a brick screen holding five marble panels of European arms, a throne with a canopy, two gateways; **S817** (B): the panels and the obelisks taken to 朗润园 about 1910 and set back in 1977.

## Iteration log

| Version | What changed | Plate 16 (all / stretch) | P0777 | P0764 | P0343 | P0765 |
|---|---|---|---|---|---|---|
| kit (Round 11) | the stone kit's screen: one box with framed panels; the platform a box | no points of this vocabulary | | | | |
| v1 | the dossier's figures, the photographs' socle and panels | 1.25 m | 0.44 m | 0.31 m | 0.22 m | 1.01 m |
| v2 | the cornice 0.5 m higher (P0777 and today's end piers agreed); the gates 5.5 m by P0193's proportion; the flights turned 40° towards the court's middle | 0.90 / 0.86 m | 0.41 m | 0.30 m | 0.14 m | 0.76 m |

## Final fit (v2, `research/xiyanglou/plate_fit_XY11.csv`)

| Picture | Fit | Points | rms px | median px | rms at the object | max | Camera |
|---|---|---|---|---|---|---|---|
| Plate 16 | all | 33 | 49.0 | 26.9 | 0.90 m | 2.40 m | f 4130 px, far: a near-parallel elevation; the max is the gates (Q233) |
| Plate 16 | stretch | 33 | 46.2 | 26.6 | 0.86 m | 2.40 m | k 1.48 |
| P0777, 1873 | all | 16 | 19.9 | 15.3 | 0.41 m | 0.69 m | |
| P0300, 1914-20 | all | 8 | 13.3 | 10.1 | 0.14 m | 0.25 m | |
| P0640 | all | 9 | 13.9 | 12.3 | 0.16 m | 0.31 m | |
| P0343 | all | 10 | 10.9 | 8.8 | 0.14 m | 0.27 m | |
| P0344 | all | 9 | 15.4 | 2.7 | 0.19 m | 0.49 m | |
| P0764 | all | 17 | 19.4 | 13.3 | 0.30 m | 0.64 m | |
| P0765 | all | 16 | 66.0 | 20.1 | 0.76 m | 2.03 m | the steps' ends, read by eye on the oblique (sure 3) |

## Where the model and the pictures disagree, and which is likely right

- **The gates' height** (Q233): P0193, a photograph, over plate 16.
- **The court's south edge** (Q71): the court in the ground runs on 6.5 m behind the screen; the model raises the gardens' strip there. The plate draws a concave edge from the gates to the platform.
- **The socle.** Today the socle is 0.58 of a panel; the plate draws it 0.35-0.38. The model follows today's stones (S603's 1.30 m), re-erected in 1977 but in their old place.

## Joints (tools/check_models.py)

- **57 contacts:** the platform's outline, the steps, the trophy pedestals, the obelisks' bases, the strip's retaining face, the gates' flights. None floats (the highest 0.05 m into the ground), the deepest 0.15 m in.
- **The ways.** Three end at the model, none off: the axis way from 大水法 at the steps' foot (CCX-022; before Round 15 it ended in the platform box's middle and crossed the steps), the two ways from the gates (CCX-027, 028).

## Assumed (C, `~fill`)

- The screen's brick back, the wall's south face, the gates' backs: about 100 of 7,700 triangles. The throne's colours (the plate is not coloured).

## Next for this model

- Durand's plan of the area (R0140) at scale and the 1977 re-erection's record: the screen's arc and its place (Q71).
- A photograph of a gate's flight from the court.
