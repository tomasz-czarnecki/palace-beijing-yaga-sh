# XY10 大水法 Dashuifa, "the Great Fountain": the model built from the plate and the photographs (Round 15)

The third detailed model of the project, made by the pilot's method (`models/XY01-xieqiqu/README.md`). It covers the fountain set at the north edge of the sunken court, before 远瀛观:
- the **niche**: its frame, two posts, a deep arch head with shoulder scrolls, the shell crest, the recess with the lion mask and the seven water steps, the sill at the terrace's level;
- the two great **piers**: console feet, shafts with sunk fields and drops, crowning cornice blocks, vase finials, a vase on a pedestal in each gap by the niche;
- the two **stairs** up to the terrace of 远瀛观, whose court-side parapets are the "great scrolls": a balustrade on each, a volute at the foot and a curl at the pier;
- the plinth and the stepped **base courses**, the lobed **basin** with its low rail, the potted trees on pedestals, two urn fountains, the **stag** on its rock and ten **hounds** (simple forms) with their jets;
- the two **towers** (XY10-N01, N02): carved pedestals and pyramids of ten tiers in lobed basins, about forty jets each;
- the **court**'s floor: paved bands and four parterres (XY10's court box M45, 110 × 60 m, 1.30 m below the gardens, S603).

It is a showcase of the method, not a one-to-one reconstruction. Every figure is C unless `params.json` says otherwise.

Files:
- `dashuifa.py`, the generator. It writes `model.glb`, `params.json`, `keypoints.json`, `joints.json` and `summary.json` (`models/README.md`). The façade, balustrade and roof helpers are in `scripts/model_parts.py`; the frame, the ground and the files in `scripts/model_site.py` (new in Round 15, shared with 观水法).
- Run: `uv run python models/XY10-da-shuifa/dashuifa.py`, then `scripts/paths1860.py`, `scripts/kit1860.py`, `scripts/greens1860.py` and `scripts/building_pages.py` (it publishes the GLB). The test: `tools/plate_overlay.py fit --object XY10 --shots screenshots/r15`, `node tools/plate_overlay.mjs --object XY10 --fits all,stretch --out screenshots/r15`, `tools/plate_overlay.py compose --object XY10 --shots screenshots/r15`, then `tools/check_models.py`.

## Evidence

Every picture named here is free (public domain or CC on Wikimedia Commons, the Östasiatiska museet's free records, Teng Gu's book of 1933 on Commons), as `research/photos/catalog.csv` records. The research-only items (P0215, P0310, P0723, P0778, Durand's plans R0139, R0140) are only cited.

**South front (the court's side)**
- **Plate 15** (P0055, 1783-86, the Palace Museum impression): the whole composition. The niche with its head and crest, the piers and finials, the vases in the gaps, the stairs' parapets with their balusters (the "ribbed bands"), the cascade, the basin with its rail, pedestals and urns, the stag and the hounds, both towers in their basins with their jets, the paving and the parterres. 44 key points.
- **Ohlmer's photograph of 1873** (P0776, Teng Gu 1933): the niche with its head and shell crest whole, the W pier to its cornice (the finials gone), the balustrade over the W stair's curl, 远瀛观's clock gate behind. 13 key points (2 skip).
- **The ruin photographs of 1902-1922**: P0169 (from the south-west, the head whole, a brick back wall in the niche), P0214 (south-east, 1922), P0288 (east, 1921-23): the depth of the piers and of the head, the head a deep hood whose shoulder scrolls run back as drums. 8 + 4 + 3 key points.
- **Today**: P0641 (2019) and P0340 (2025), frontal: the proportions of the niche frame, the opening, the posts, the piers, the console feet, the plinth and the courses. 14 key points each (2 skip each: today's opening runs to the plinth).

**North (the terrace's side)**
- **P0762** (2007, from the 远瀛观 terrace): the back of the head and the posts, the opening's back sill at the terrace's level. 8 key points (the `_N` names).

**Plan and texts**
- **The plan S01** (B): the niche's arc, 21.2 m (the span over the piers); the hatched stairs at its ends (CCX-023, 024); the lobed pool with ten small rectangles in a ring round a middle one (the hounds and the stag); the two round pools with square towers; the cross-shaped ways.
- **Durand's survey** (S603, B): the sunk area 110 × 60 m, 1.30 m below the gardens; the tower basins 18 m across, quatrefoil, 62 m apart, symmetric about the axis.
- **The ruin on the imagery** (S850, B): the basin's width 28.4 m, its depth 16.4 m (C), the tower bases' places.
- **S310** (B, a search extract): the seven-step water curtain; the "13-step" towers (Q236).
- **S02 p.157** (B): white marble; **S817** (B): the stone fish, not placed (Q236).
- **Reading aids only**, never a figure: R0003, R0133, R0193, R0262, R0270 and the others in the dossier.

## How it was built

1. **v1 from the dossier and the plan.** The pier span from S01's arc, the niche and the opening from the plate's and P0641's ratios, the heights from P0641 with the pier's width as the scale. Footings follow the walk surface of Round 10 (`skirt`); the tower basins cover the ground's own water bodies (S01).
2. **Readers, in parallel** (`docs/rounds/common/palace_r15_dashuifa_vocab.md`): one on plate 15 and P0776, one on the ruin photographs, one on 观水法. Their form notes changed the model more than the points did: the "ribbed bands" are the stairs' balustrades; the head is narrower than the posts' caps; the piers are deep; ten tiers, not thirteen.
3. **Fits.** `tools/plate_overlay.py fit` with the readers' camera priors (`research/xiyanglou/photo_viewpoints.csv`). Without a lens prior, P0762's eight nearly coplanar points shrank the focal length to 79 px; Round 15 added `hfov_deg`, an assumed lens as a weak prior.
4. **Overlays** (`screenshots/r15/overlay_*`): blend, edges, side by side, from each fitted camera.

## Iteration log

| Version | What changed | Plate 15 (all / stretch) | P0776 | P0641 | P0340 | P0169 | P0762 |
|---|---|---|---|---|---|---|---|
| kit (Round 11) | the stone kit's niche: one box with an arch, a triangle crest | no points of this vocabulary | | | | | |
| v1 | the dossier's figures; quarter-arch buttresses against the piers; a flight behind each to a terrace 2.33 m above the court | 1.61 m | 1.70 m (max 5.5) | 0.47 m | 0.42 m | 0.81 m | 0.78 m (f 79 px: degenerate) |
| v2 | lens priors; the "great scrolls" are the stairs' parapets: diagonal flights to a terrace 4.63 m above the court (XY09's box raised, Q232), a volute at the foot, a curl at the pier; the niche's sill at the terrace's level, a solid face below (Q237); the lion mask 1.4 m lower | 1.45 / 1.37 m | 1.01 m | 0.46 m | 0.43 m | 0.81 m | 0.62 m |
| v3 | the head 0.95 m inside the frame each side (four photographs agreed); the recess's back face drawn; a lighter crest | 1.42 / 1.34 m | 0.96 m | 0.19 m | 0.15 m | 0.62 m | 0.51 m |

## Final fit (v3, `research/xiyanglou/plate_fit_XY10.csv`)

| Picture | Fit | Points | rms px | median px | rms at the object | max | Camera |
|---|---|---|---|---|---|---|---|
| Plate 15 | all | 44 | 41.6 | 20.0 | 1.42 m | 4.11 m | f 1969 px, 34 m up: a raised, near-parallel view |
| Plate 15 | stretch | 44 | 40.3 | 16.6 | 1.34 m | 4.33 m | k 1.20: heights drawn 1.2 times the widths |
| P0776, 1873 | all | 13 | 22.7 | 12.0 | 0.96 m | 2.81 m | the W stair's rail (Q232); without it 0.5 m |
| P0641, 2019 | all | 12 | 4.8 | 4.4 | 0.19 m | 0.29 m | f 664 px, 21 m |
| P0340, 2025 | all | 12 | 3.5 | 3.1 | 0.15 m | 0.24 m | |
| P0169, 1902 | all | 8 | 18.6 | 16.7 | 0.62 m | 1.00 m | |
| P0214, 1922 | all | 4 | 25.6 | 14.0 | 0.68 m | 1.21 m | four points, eight unknowns: not a test |
| P0762, 2007 | all | 8 | 43.7 | 22.4 | 0.51 m | 0.85 m | the back; nearly one plane |
| P0288 | | 3 | | | | | too few for a camera |

The photographs' distances rest on assumed lenses (`hfov_deg`), so their fits test the model's proportions, not its absolute size: the size is the plan's (21.2 m).

## Where the model and the pictures disagree, and which is likely right

- **The court's depth** (Q235). Plate 15 draws the basin's front 3.7 m and the tower basins' fronts 3.5-4.1 m nearer the niche than the ruin and the plan. The ruin is taken as right: the plate compresses the court to show it whole.
- **The towers' height.** With one camera the plate wants the pyramids 2.3 m taller; with its stretch (k 1.2) they fit. The model keeps the plate's ratio to the pedestal (2.4) and does not tune the stretch in.
- **The terrace and the stairs** (Q232). The stairs' top follows plate 15 (the curl at the piers' flare) and P0762; P0776's balustrade fits 2.7 m higher still.
- **The niche's opening** (Q237): the 1780s sill, not today's opening to the plinth.
- **The tower basins' places** (Q234): S603's symmetry, against the ruin readings' 5.6 m.

## Joints (tools/check_models.py, models/check_models.json)

- **24 contacts with the walk surface:** the plinth's corners, the basin rim's foot, the tower kerbs, the stairs' and volutes' feet. None floats (the highest 0.05 m into the ground), the deepest 0.15 m in.
- **The ways.** Seven end at the model's boxes, none off: the axis way to 观水法 (CCX-022) leaves the basin's front, the cross way (CCX-021) and the ways beyond (CCX-020, 029) meet the tower basins' sides, the stairs (CCX-023, 024) their feet and tops. Before Round 15 the axis way ended in the court box's middle (a walk-through box); `scripts/paths1860.py` now meets a court or terrace a model draws at the model's entries.

## Assumed (C, carried round, `~fill` in the GLB: hidden with `?assumed=0`, pale with `?conf=1`)

- The stairs' treads and their far-side parapets (the plate shows only the court side; the treads behind the parapet nowhere).
- The towers' pedestals on their north and outer faces.
- About 2,240 of 17,100 triangles are fill.

## Next for this model

- The 远瀛观 dig's section (S153) for the terrace's height (Q232); 西洋楼水法图 (E0544) for the cascade and the jets.
- Durand's 1987 plan of the fountain area (R0140, 128 surveyed points) at scale: the basin's outline, the stairs' plan.
