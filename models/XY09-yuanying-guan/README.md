# XY09 远瀛观 Yuanyingguan, "View of Distant Seas": the model built from the plate and the photographs (Round 16)

The fifth detailed model of the project, made by the pilot's method (`models/XY01-xieqiqu/README.md`). It covers the hall of the tapestries and its terrace behind 大水法:
- the **terrace** (S603: 35 × about 31 m), 4.3 m above its foot where 大水法's stairs arrive (Round 15, Q232): retaining walls of piers and long rusticated stones on the east, west and north, the paved top, the straight front balustrade with urns, the side balustrades, eight trees in square pits, a stair down at the back (assumed, for reach);
- the **hall** (S603: 28 × 21 m), an inverted 凹 (S310) on a base 1.2 m high: two **wings** with chamfered corners come one bay forward, each with a big window on a carved sill block, a low roof of eight slopes, a deck with a balustrade and a square **lantern** with a clock face on every side;
- between them the **centre block** with the **clock gate**: the door between two carved columns on pedestals (a lion on each, plate 14 only), an entablature block over each standing proud, the door's carved hood, a tall door-like opening either side, and over the cornice the attic with the **clock wheel**, its arched moulding, the crest and the scrolls at its foot;
- the centre's **roofs** in tiers: a fish-scale hipped roof as wide as the block over a low band, the steeper main hipped roof pierced by the attic, a pedestal band with scrolls and the crown;
- the **body** behind under a hipped Chinese roof (assumed form; S603: side bays of two-slope Chinese tile).

It is a showcase of the method, not a one-to-one reconstruction. Every figure is C unless `params.json` says otherwise. The north ranges behind (XY09-N01 to N03) stay the kit's boxes.

Files:
- `yuanyingguan.py`, the generator. It writes `model.glb`, `params.json`, `keypoints.json`, `joints.json` and `summary.json` (`models/README.md`), on `scripts/model_site.py` (frame, ground, footings, files; from Round 16 also the terrace as a **deck**) and `scripts/model_parts.py` (openings, pilasters, entablatures, balustrades, urns, hip roofs).
- The frame: the hall's box XY09-M44 gives the turn and the front; the origin moves 0.72 m along the front onto 大水法's axis (the two boxes stand that far apart, within the ruin readings' 3-4 m; plate 14 and S01 draw one axis). The terrace's front and the heads of 大水法's stairs are read from 大水法's model (`models/XY10-da-shuifa/summary.json`, `joints.json`), so the two models meet without a gap.
- Run: `uv run python models/XY09-yuanying-guan/yuanyingguan.py`, then `scripts/paths1860.py`, `scripts/kit1860.py`, `scripts/greens1860.py` and `scripts/building_pages.py`. The test: `tools/plate_overlay.py fit --object XY09 --shots screenshots/r16`, `node tools/plate_overlay.mjs --object XY09 --fits all,stretch --only --out screenshots/r16` (`--only`: 大水法's niche stands between every camera and the hall), `tools/plate_overlay.py compose --object XY09 --shots screenshots/r16`, then `tools/check_models.py`.

## Evidence

Every picture named here is free (public domain or CC on Wikimedia Commons, the Östasiatiska museet's free records, Teng Gu's book of 1933 on Commons), as `research/photos/catalog.csv` records. The research-only items (P0213, P0723, P0778, Durand's figures R0139, R0143) are only cited.

**South front**
- **Plate 14** (P0054, 1783-86, the Palace Museum impression): the whole composition from high over 大水法's niche. The wings with their chamfers, windows and lanterns, the centre block's rhythm (window, column, door, column, window), the lions, the clock attic, the fish-scale roof, the main roof, the crown, the forecourt's trees, steps and balustrades. 59 key points (reader 1).
- **Ohlmer's photograph of 1873** (P0183): the clock gate whole: the columns, the entablature blocks, the attic with the wheel, the arched moulding and the crest, the scrolls, the side openings' jambs. 16 key points (1 skip). The order here is taller against its spacing than the plate draws it.
- **Piry's photograph of 1876** (P0190, by its file name): the same front nearer; the attic already fallen (so after P0183). 7 key points.
- **The ruin photographs of 1900-1927** (P0179, its second print P0772, P0216, P0291, P0719): the W carved column, its pedestal, the entablature block, the door's crown, the W side opening; the E column fell before 1900 (its drum lies by the door on P0216 and P0291). 4 + (4 skip) + 9 + 5 + 4 key points (reader 2).
- **Today** (P0757 of 2007, P0341 of 2013): the W column whole with its pedestal and block, the jambs and the lintel. 4 + 4 key points.
- **Ohlmer's photograph of 大水法** (P0776, 1873): the clock gate above and behind the niche; 3 points, too few for a camera; its scale disagrees (Q240).

**North**
- **P0780** (2007, from the terrace's north): the column's block from behind, rough-tooled, no carving on the back. 1 key point (3 skip); too few for a camera.

**Plan, survey and texts**
- **Durand's survey** (S603, B): the terrace 35 × about 31 m, the hall 21 × 28 m from its post grid (which way not stated: Q67), the terrace's retaining walls of monolithic piers and long rusticated stones, five roofs each on its own post system (p.133).
- **S310** (B, a search extract): 南向西洋钟楼式大殿 on a high terrace, an inverted 凹 in plan, 17 rooms.
- **S02 p.155** (B): grey brick with carved white marble round the doors and windows, two carved pillars before the door. **S153** (A, the abstract): the 2016 dig found a glazed roof's many fittings; the colours are not stated.
- **The ruin on the imagery** (S850, B): the rubble core 28.4 m W-E and 20.1 m N-S.
- **Reading aids only**, never a figure: R0003, R0092, R0123, R0133, R0134, R0139, R0140, R0143, R0314.

## How it was built

1. **v1 from the dossier.** The module of Round 6's plate reading (the 'centre bays 4 m', a column spacing of 4.2 m), the heights the box held (crown 12.6 m above the terrace), the plan's 28 × 21 m.
2. **Readers, in parallel** (`docs/rounds/common/palace_r16_yuanying_vocab.md`): one on plate 14 and the photographs of 1873-76, one on the ruin photographs since 1900 (the third on 方外观). Their form notes changed the model more than the points: the wings' chamfers and their one-bay projection, the order taller than the plate draws it, the side openings door-like and further out, the floor 1.2 m above the pedestals' foot, the lions gone by 1873, the attic fallen between 1873 and 1876.
3. **The module.** Plate 14's own ratios (the centre 431 px, the columns 228 px apart, the wings' fronts 200 px) against S603's 28 m, and P0216's door at the plate's 2.0 m, both put the columns 6.0 m apart; at 4.2 m the whole front would be 18 m. The photographs then set the order (capital 1.19 S, cornice 1.34 S, door head 0.90 S above the pedestals' foot, P0183) and the attic (1.61, 1.81, 1.95 S, where plate and photograph agree to 0.01 S); plate 14 sets the roofs, scaled by the attic.
4. **Fits.** `tools/plate_overlay.py fit` with the readers' camera priors (`research/xiyanglou/photo_viewpoints.csv`; the eye above the ground model, which has no terrace: 4.3 m added).
5. **Overlays** (`screenshots/r16/overlay_*`), rendered with `--only` (大水法's niche hidden).

## Iteration log

| Version | What changed | Plate 14 | P0183 | P0216 | P0190 | P0291 | P0719 | P0757 |
|---|---|---|---|---|---|---|---|---|
| kit (Round 11) | the stone kit's hall: one block with arches, a pediment, a balustrade | no points of this vocabulary | | | | | | |
| v1 | the dossier's figures at the 4.2 m module | 1.09 m | 0.27 m | 0.34 m | 0.07 m | 0.17 m | 0.26 m | 0.16 m |
| v2 | the 6.0 m module; chamfered wings one bay forward; the order from the photographs, the roofs from the plate; the floor at 1.2 m; three flights | 0.77 m | 0.40 m | 0.56 m | 0.20 m | 0.34 m | 0.56 m | 0.13 m |
| v3 | the side openings 0.85 m further out (all three photographs), so the centre 13.6 m and the wings 7.2 m; the wing windows on a sill block at the floor; a low band under the fish-scale roof; the attic's scrolls ending at the cornice; P0772 skipped (the same negative as P0179) | 0.74 m | 0.14 m | 0.18 m | 0.20 m | 0.24 m | 0.26 m | 0.13 m |
| v4 (final) | the body's assumed roof lowered from 12.0 to 10.2 m (it competed with the centre's tiers on the overlay); the door's hood a segmental cartouche (P0183) | 0.74 m | 0.14 m | 0.18 m | 0.20 m | 0.24 m | 0.26 m | 0.13 m |

The photographs fit v1 well too: a free camera absorbs the scale of one front. Plate 14, which holds the whole hall, is the test of the module.

## Final fit (v4, `research/xiyanglou/plate_fit_XY09.csv`)

| Picture | Fit | Points | rms px | median px | rms at the object | max | Camera |
|---|---|---|---|---|---|---|---|
| Plate 14 (P0054) | all | 59 | 28.8 | 23.6 | 0.74 m | 1.32 m | f 1331 px, 21.7 m up, 32 m before the wings: over 大水法's niche, as the dossier read it |
| Plate 14 | stretch | 59 | 28.2 | 24.5 | 0.73 m | 1.30 m | k 1.01: at the 6.0 m module the plate draws heights and widths alike |
| P0183, 1873 | all | 16 | 10.2 | 5.2 | 0.14 m | 0.28 m | f 2365 px, moved 22.5 m back from the prior: the points lie nearly in one plane and the print is cropped, so distance trades against the focal length; the pixels hold, the place does not |
| P0190, 1876 | all | 7 | 18.0 | 16.6 | 0.20 m | 0.35 m | f 868 px, 2.5 m from the prior |
| P0216, 1922 | all | 9 | 12.6 | 7.6 | 0.18 m | 0.46 m | f 2099 px |
| P0291 | all | 5 | 15.3 | 12.3 | 0.24 m | 0.40 m | from the south-east |
| P0719 | all | 4 | 17.8 | 10.3 | 0.26 m | 0.46 m | |
| P0179 | all | 4 | 9.2 | 6.3 | 0.06 m | 0.10 m | four points: weak |
| P0757, 2007 | all | 4 | 12.1 | 2.8 | 0.13 m | 0.26 m | 1.4 m from the prior |
| P0341, 2013 | all | 4 | 20.6 | 7.0 | 0.22 m | 0.43 m | a long lens from the south-west |

Largest residuals on plate 14: the wings' window sills and heads (1.2-1.7 m: the plate draws the wing on a higher base than the photographs give the centre), the fish-scale roof's eave tips (1.2 m), the pedestals' tops (1.1 m: the plate draws the order short, as reader 1 measured), the attic's scrolls and the front rail (1.0 m: the plate's forecourt is deeper than 8.7 m). None was tuned away.

## Joints (`joints.json`, `tools/check_models.py`)

- 28 joints: the terrace's corners and the foot of every retaining pier, the back stair's foot: none floats (highest 0.05 m into the ground), deepest 0.15 m. v1 had 5.
- **大水法's stairs** arrive on the terrace with no gap: the terrace's front is 大水法's own `zt` (z 8.69 m in this frame), its top 4.30 m above this frame's zero, the landings' top (4.63 m above the court, 0.33 m lower) the same: 0.00 m in plan and in height.
- **The ways:** S01's way from the hall's door down the recess (CCX-026) ended 4.24 m below the door in v3: the ways lie on the ground of Round 10, which has no terrace. From Round 16 a model declares the terrace as a **deck** (`scripts/model_site.py`, `joints.json` `decks`, `models.json`); the view lays the ways that cross it on it, and `tools/check_models.py` measures there: 0.00 m.

## Where the model and the pictures disagree

- **The module (Q239).** The dossier's 4.2 m column spacing (from the plate at the old module) gives an 18 m front; S603's 28 m and the plate's own ratios give 6.0 m, and so the order and the roofs are 1.4 times taller than the box held (crown 15.5 m above the terrace, not 12.6). The box's heights now follow the model (`research/xiyanglou/boxes.csv`).
- **Plate 14 against the photographs on the order.** The plate draws the columns short (capital 1.00 S against 1.19 S on P0183, the entablature 1.11 against 1.34) and the pier between column and side opening narrow (0.12 S against 0.27 S); the attic agrees. The photographs win: they show the stone as built.
- **The lions** stand on the pedestals on plate 14 only; none of the photographs of 1873 and after shows them. Modelled (the 1780s state; their removal is not dated).
- **P0776's scale (Q240).** On Ohlmer's view of 大水法 (1873) the clock gate is 2.5 times larger than the Round 15 camera allows at a 4.2 m spacing (1.75 times at 6.0 m): either the camera stood nearer or the gate is larger still. Three points only: no camera of its own.
- **The forecourt's depth.** The plate's front rail fits 1.0 m off with the terrace's front at 大水法's face: the plate's forecourt reads deeper than 8.7 m. The terrace's front stays where 大水法 meets it.
