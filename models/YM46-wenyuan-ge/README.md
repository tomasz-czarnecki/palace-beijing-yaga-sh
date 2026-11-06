# YM46 文源阁 Wenyuan Ge: the library of the Four Treasuries in its walled rock garden, a detailed model (Round 25)

The eleventh detailed model and the fifth of a Chinese compound. 文源阁 was built in 1774 (S05 j81:36a) a little west of north of 水木明瑟, to hold one of the sets of the 四库全书 with 文渊阁 in the palace and 文津阁 at Chengde. Qianlong's 文源阁记, cut on a stele in a pavilion east of the library, says he took the form of 天一阁, the Fan family's library at Ningbo (S05 j81:36b-37a, E2194); his poem of 1776 says the library copies 文津阁, built first, with its terrace 月台 and its piled rocks (此即肖文津, E2186). The library and its books burned in October 1860 with the garden (S02 pp.187-188). The stele and the rock 玲峰 survived the fire (S02 p.89).

The model draws the whole walled court as S01 draws it: the library with its two storeys outside, the terrace 月台 on the pool, the pool with 玲峰 on its stone terrace, the stele pavilion, the rockeries round the court and behind the south gate with the pavilion 趣亭, the court's wall of rubble with its two gates, and a small pond in the north-east corner.

Generator: `wenyuange.py` (`uv run python models/YM46-wenyuan-ge/wenyuange.py`, after `scripts/kit1860.py` has run once), on `scripts/hall_parts.py` (the hall kit in Python, Round 17) and `scripts/model_site.py`. Hand-edited sheet: `plan_readings.csv` (every line read on S01, in plan pixels). The storeys' heights come from `measure.py` (writes `measure.json`). The generator writes `model.glb`, `params.json`, `keypoints.json`, `joints.json`, `summary.json` and `report.json`.

## Evidence

By part, in the order of authority the brief sets: the dossier (`research/scenes/YM46-wenyuan-ge/`), the period plan and texts, the dig, the pictures, and the readings of others as reading aids only. **No picture of 文源阁 standing or of its ruin is known** (Q122: the Commons file captioned 'Wenyuan Pavilion' of 1910 is another library; Q125: no geotagged photograph of the site). The pictures used are of its sisters, and they give form and proportion only, never a place or a size of 文源阁's own.

- **The plan (B):** S01, re-read in Round 25 on 4x, 5x and 6x crops (`plan_readings.csv`). It gives:
  - the court's wall, 48 x 68 m;
  - the library's grid of five cells, the west one wide (the stair bay drawn with its neighbour), with its gallery lines front and back: 23.5 x 14.3 m against the 丈尺册's 22.72 x 14.72 m;
  - the 明间, third cell from the west, in line with the south gate's middle cell and the north gate (the axis reads 0.59-1.13 m across the frame);
  - the rectangle before the library holding the label (the 月台, 25.1 x 8.1 m);
  - the stele pavilion's square, the pool with its rock banks, 玲峰's oval terrace in it;
  - the rock bands inside the wall, the masses in the corners and behind the gate;
  - two small circles and two small squares in the south part;
  - the south gate of three cells astride the wall, the north gate's small arch;
  - the double line south of the gate with a gap in line with it.
- **The library's sizes (B):** the Guangxu 丈尺册 quoted by S105 (note [4]):
  - the 明间 16 尺 (5.12 m), four 次间 of 12.5 尺 (4.00 m), the west stair bay 5 尺 (1.60 m): 71 尺, 22.72 m;
  - the middle 24 尺 (7.68 m) and the galleries front and back 11 尺 (3.52 m): 46 尺, 14.72 m.

  The 丈尺册 is of the Guangxu reign, after 1860, so B. S05's 上下各六楹 (A) gives the bays; the 2024 dig confirmed six bays (S133).
- **The stele pavilion's platform (B):** 1丈4尺 square, 4.48 m (the 丈尺册, S105 note [2]; Q110). S01's square is 5.5 x 5.3 m.
- **The texts (A):**
  - S05 j81:35b-39a: 文源閣上下各六楹 ... 閣前石為玲峯刋御製文源閣詩 ... 閣東亭内石碣刋御製文源閣記; the plaques 文源閣 and 汲古觀瀾 in Qianlong's hand;
  - the poem of 1776 (E2186): the 月臺 and the strange stones heaped into peaks (詭石堆竒岫), copied from 文津阁.
- **The dig of 2024 (B):** 北京市考古研究院, August to November (S133, S134, S942):
  - the gate, the north gate, the library's and the stele pavilion's foundations, a terrace, 趣亭, walls of 虎皮石 rubble, paths of unworked flagstones;
  - black glazed tiles (and green: S942's photograph), six bays;
  - two ponds, one south of the hall and one in the north-east corner (S942; S133 says east of the library), five culverts, three of them under the rockery behind the gate;
  - the yard raised a little, the ground inside higher than outside;
  - the base of 玲峰 of long slabs tied with iron dovetails.

  Sizes in metres are not yet published.
- **Malone, 1934 (B):** S02 pp.89-90 (E2198):
  - a pool before the library with water-worn rock round it;
  - the monolith 'rising 12 or 15 feet from a stone terrace in the middle of the pool', pierced with many holes, with inscriptions;
  - the stele standing;
  - glazed tiles with a wave design in white and green.
- **S105 (2022, B):** the survey of the ruin before the dig:
  - galleries front and back, 硬山, black glazed tile with green edging, grey brick walls, dark green columns;
  - a lower floor with the study and the west stair, a mezzanine, a top floor of shelves;
  - 玲峰 over 6 m;
  - the dispute over the roof (Q111).
- **The sisters (twins, form and proportion only):**
  - P0555, 文渊阁's south front (T056, Commons, CC BY-SA 4.0): the storeys are measured on it (below);
  - P0551, 文津阁 (T055, CC BY 3.0): the skirt roof ending against grey brick end piers, red window frames, a standing rock before the pool;
  - P0550, 文津阁's rockery (CC0): a small pavilion on the rockery beyond the pool, yellow tile.
- **Reconstructions by others (reading aids, never used):** R0109 and R0110 (玲峰's virtual restoration, 2025), R0154, R0266.

## What the model draws, and on what

- **The court (C):** its floor is a deck 0.10 m above the library's box ground (Round 10's pad). The dig says the yard was raised; its level is C. The floor is earth; Round 9's flagstone ways lie on it. The whole court is `clear` of the planting.
- **The library:**
  - the 丈尺册's bays and depths (B), centred on S01's grid;
  - the platform 0.75 m (C), with flights at the 明间 front (to the 月台) and back;
  - the ground storey: outer columns at the galleries' edge, the doors (明间) and windows behind at the inner columns, the gallery's hanging lattice and low rails (after 文渊阁, C);
  - grey brick gable walls 硬山 (S105), carried forward as end piers under the skirt roof's ends (after 文津阁, P0551);
  - the skirt roof 腰檐 front and back, black with the green edge;
  - the upper storey over the whole depth: plaster below short windows (P0555), dark green columns (S105), red frames (the sisters);
  - the plaque 文源閣 under the upper eave (S05; its board C);
  - the 硬山 roof, black glazed with green trim (the dig, S105), its barge bands, the ridges green with white crests for Malone's waves (form C).
- **The storeys (C, a twin's proportion):** measured on P0555 by `measure.py`, in 文源阁's bays, above the gallery floor:
  - the columns' tops 2.51 m;
  - the skirt roof's drip 3.34 m;
  - the upper windows 5.08-6.15 m;
  - the top eave's drip 7.26 m.

  The ridge stands 12.33 m above the floor and 13.08 m above the court. The roof's rise (0.58 of its half depth) is the storeyed hall class's.
- **The 月台 (B outline, C height):** S01's rectangle, 0.45 m above the court, flagged, its south face standing in the pool, a flight at each end.
- **The pool (B):** Round 10's water W0230 (348 m², its level 1.49 m below the library's ground), sunk 1.59 m below the court. Its face is drawn from the water to the court, with rock along its banks (Malone).
- **玲峰 (B for the rock and its terrace, C for the form):**
  - an oval stone terrace 5.55 x 5.03 m (S01's oval), 0.60 m above the water;
  - a pierced standing rock 4.10 m high (Malone's 12 to 15 feet), narrow at the waist and broad at the head, with two blocks side by side at three tiers so that light passes;
  - the poem's panel cut on its south face (S05).
- **The stele pavilion (B platform, C form):**
  - the 4.48 m platform centred on S01's square;
  - four dark green columns, a pyramid roof in black with green trim (C);
  - inside, the marble stele on its base with its inscribed face (S05, Malone).
- **The rockeries (S01's outlines B, form C):** 274 blocks in ten masses, from 0.7-1.7 m along the walls to 1.8-3.4 m behind the gate. They are piled blocks of irregular tops, kept off Round 9's ways.
- **趣亭 (C):** a small square pavilion with a yellow pyramid roof and green trim (the sister's, P0550) on a rock pad 2.60 m above the court, on the middle of the south rockery, with a rock stair down to the way along the pool.
- **The small things S01 draws (C):** two standing stones (the circles) and two stone pedestals (the squares).
- **The pond in the north-east corner (C):** a sunk basin among the rocks (the dig names it, S942; S01 does not draw it).
- **The wall and the gates:**
  - the wall: rubble 3.0 m above the court (S133; height C), its feet on the land outside;
  - the south gate: three bays (3.40, 3.84, 3.40 m, C) on S01's cells, the kit's gate;
  - the north gate: a door in the wall (C);
  - the forecourt outside the south gate is open ground to the gap in the double line, kept `clear` of generated hills and planting.

## Match check

No plate, leaf or ruin photograph of 文源阁 exists to fit (the dossier's views are empty). The model was tested against the plan and against its sister's photograph.

- **The plan:**
  - S01's library grid is 23.53 x 14.28 m against the 丈尺册's 22.72 x 14.72 m: within 0.8 m and 0.4 m;
  - the 明间 stands 0.35 m from S01's middle cell;
  - the axis (the 明间, both gates, 玲峰) spreads over 0.54 m;
  - the stele pavilion's square (5.4-5.6 m) is drawn at the 丈尺册's 4.48 m (Q110).
- **The storeys, measured (`measure.py`, `measure.json`):** P0555 (文渊阁's south front) was read on 2x crops (`research/scenes/YM46-wenyuan-ge/plate_keypoints.csv`): four ground-storey columns (feet and tops), and the lines of the skirt roof's drip, the top eave's drip and the upper windows' frames.
  - A camera fitted jointly with five heights, 文源阁's bays the scale, gives 8 points and 16 line readings at 5.0 px rms (max 15.2 px).
  - Moving the skirt's reach from 1.0 to 2.0 m and the eave's from 1.0 to 1.5 m moves the drips by 0.12 m at most.
  - 文渊阁's side bay against its 明间 is 0.78 on the picture, 文源阁's 4.00 / 5.12 = 0.78.
- **The fit (`tools/plate_overlay.py fit --sheets research/scenes/YM46-wenyuan-ge`):** P0555, with a virtual viewpoint before the model (`photo_viewpoints.csv`: the picture is not of this place), fitted on 13 true points (eight column feet and tops, three upper column tops, the plaque's top and bottom).
  - Result: **0.20 m rms at the object** (14.9 px), median 0.18 m, max 0.36 m (the plaque's bottom).
  - The line readings are `skip` there, as points they sit 0.33-0.41 m off along their lines.
  - The overlay (`screenshots/r25/overlay_P0555_YM46_all_*`) lines up the columns, the skirt roof's band, the short upper windows, the top eave and the plaque.
  - The roof above the eave differs: 文渊阁 is 歇山, the model 硬山 (Q111).

  This tests the proportion against the sister, not 文源阁's own heights (Q287).
- **The first guess:** the class guessed columns of 4.2 m and a top eave at 9.3 m, 1.3 to 1.7 times the sister's proportion. It was replaced by the measurement.

## Iteration log

1. **First run (typology heights):** the library at the class's storeys (columns 4.2 m, eave 9.3 m). The gallery's hanging lattice read as a black beam. The plaque was a wide board. The rocks were tall flat-topped blocks like tombstones. 玲峰 was a stack of boxes. 趣亭's 歇山 on a square plan broke (the kit's 歇山 ridge needs a longer side).
2. **The water at the gate:** the south gate opened onto water. Round 1 had classed the ring between the court's wall and the double lines round it as water (W0047, an automatic wash call of +1.5, grade C); the ring's tint on S01 equals the court's and the land's. S01 draws the gate opening on open ground and a gap in the double line in line with it. The ring is land now (`research/plan/water_removed.json`; `scripts/build_r1.py` keeps the number W0047 taken so that no other id moves). The double lines themselves, ditches round the rice fields, are not traced as water (Q289).
3. **趣亭's first place**, S01's small circle at the south rockery's north edge, put its pad across the way YMW-022 (`tools/check_paths.py`: a B way across a box). The circle is read as a standing stone beside the way, and 趣亭 stands on the rockery's middle (C).
4. **A generated hill in the forecourt:** once the ring was land, Round 10's typology raised a free-land hill of 1.9 m before the south gate. The forecourt is now `clear`, and `scripts/hills1860.py` keeps the hills off it.
5. **The storeys measured** on P0555 and carried in (above). Red frames on dark green columns after the sisters, the lattice and rails green.
6. **The south gate** was set on its middle cell, not the middle of its outline: 0.5 m west, in line with the 明间.
7. **The planting's 玲峰:** Round 12 placed the rock (GS-0295, R10-079, R10-080) as a generated standing stone on land north of the pool (GR-083). The model declares the scene's rockeries its own (`joints.json` `rockeries`), and `scripts/greens1860.py` places none for YM46, keeping the number GR-083 taken.

## Joints and ways

- **Ground joints** (`tools/check_models.py`): 32: the wall's feet on the land outside, the pool's face at the water, 玲峰's terrace and the 月台's south corners in the pool. None stands above the ground; the deepest is 0.27 m in.
- **Ways:** 3 of Round 9 end at the model's boxes, 0 more than 0.5 m from an entry.
- **Joints on the decks** (`report.json` `deck_joints`): 11, every one at 0.00 m. They are the gates' inner feet, the 月台's flights, the library's front (on the 月台) and back flights, the stele pavilion's flight and 趣亭's stair.
- **Footprints** for the ways and the planting: the platforms, flights, rocks, pond, pedestals and wall. **Decks:** the court in two pieces and the 月台. **Clear:** the court and the forecourt.

## Where the model and the pictures disagree

- **The roof form (Q111):** 歇山 by 金勋's memory and a late-Qing sheet (E2204, possibly an unbuilt design); 硬山 by the poem's 'copies 文津阁' and S105's reading. The model keeps 硬山 (C).
- **玲峰's height (Q288):** Malone's 12-15 ft (3.7-4.6 m, taken 4.10 m) against S105's 'over 6 m'. The model keeps Malone, who saw it standing.
- **The heights (Q287):** taken from 文渊阁's proportion. 文津阁's photograph (P0551) is oblique and its front mostly hidden by trees; looked at by eye, its ground storey seems taller against its bays than 文渊阁's, but it was not measured. Both are twins; the dig's report or the 丈尺册's full text would settle it.
- **The stele pavilion:** S01's square is 1 m wider each way than the 丈尺册's platform; the 丈尺册 is kept (Q110).
- **The pool's size:** the brief's '15 by 7 zhang' is in no source the repo holds. The pool is S01's and Round 10's, 348 m².
