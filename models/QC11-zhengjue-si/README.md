# QC11 正觉寺 Zhengjue Si: the Tibetan Buddhist temple of 绮春园, a detailed model (Round 28)

The fifteenth detailed model and the eighth of a Chinese compound. 正觉寺 Zhengjue Si, "Temple of Perfect Enlightenment", was finished in 1773 outside the west wall of 绮春园 Qichun Yuan and joined to it by a back gate (S228). It was the only temple of the three gardens kept by lamas (E0681, E0683). When British troops burned 绮春园 on 18 October 1860, the temple was spared (E0680, E0451), and it came through 1900 as well (S228). In the Republic it became a private villa, then staff housing of Tsinghua; 三圣殿 was gone by 1933, and factories used the site from the 1970s. The gate, 文殊亭, the east and west 五佛殿, the side halls, the west corner rooms and the west 顺山殿 were repaired in 2002-03; 天王殿, 三圣殿 and 最上楼 were rebuilt in 2009-11, and the temple opened in July 2011 (S228, E0679).

The model draws the whole walled temple in its state before October 1860, from the south:

- the gate 山门 Shanmen with a screen wall either side and a side gate in the wall beyond each;
- the bell tower 钟楼 and the drum tower 鼓楼;
- 天王殿 Tianwang Dian, "Hall of the Heavenly Kings", of five bays in the second cross wall, with a small gate either side;
- the front court with the side halls 配殿 of five bays;
- 三圣殿 Sansheng Dian, "Hall of the Three Saints", of seven bays with its terrace 月台 and its rear annex 后庑殿, in the first cross wall;
- the inner court: the raised walk on the axis, the octagonal pavilion 文殊亭 Wenshu Ting, "Manjusri Pavilion", with double eaves, and the ranges along the sides with the two-storey 五佛殿 Wufo Dian, "Hall of the Five Buddhas", in their middles;
- 最上楼 Zuishang Lou, "Topmost Tower", of seven bays and two storeys with its balcony, and the three-bay 顺山殿 Shunshan Dian at its ends;
- the strip behind it to the back gate 后门 on the north wall.

Generator: `zhengjuesi.py` (`uv run python models/QC11-zhengjue-si/zhengjuesi.py`), on `scripts/hall_parts.py` (the hall kit in Python, Round 17) and `scripts/model_site.py`. Its own parts: `masonry()` (the gate, 天王殿, the towers' lower storeys, the small gates), `lou()` (the two-storey halls), `octagon_pavilion()` with `oct_roof()` (文殊亭). Hand-edited sheet: `plan_readings.csv` (every line read on S01, in plan pixels). It writes `model.glb`, `params.json`, `keypoints.json`, `joints.json`, `summary.json` and `report.json`. Two switches in the environment exist only for the tests below, never for a run of step 6: `QC11_SS_ROOF` (wd or xs), `QC11_SS_COL` and `QC11_SS_DEPTH`.

## Evidence

By part, in the order of authority the brief sets: the dossier (`research/scenes/QC11-zhengjue-si/`), the plan and the texts, the photographs, today's buildings, the rebuilds and the readings of others as reading aids only.

- **The plan (B):** S01, re-read in Round 28 on 3x, 4x and 6x crops with a 5 and 10 px grid (`plan_readings.csv`). It gives:
  - the outer wall, about 66 x 150 m (10,169 m² inside its line; S228 gives the site as 14,300 m² with the yard east of it);
  - the gate's three cells (10.1 x 5.7 m), the two elongated cells either side of it (the screen walls), the two three-cell side gates on the south wall, the road south to the river;
  - the two towers' double-lined squares (about 5.9 m), two small squares south of them;
  - the second cross wall with 天王殿's five cells (16.1 x 6.6 m) and a small three-cell gate either side;
  - the east side hall of the front court (five cells, 5.1 x 17.9 m) against the east wall, and none against the west wall (Q305);
  - 三圣殿's grid of seven bays (23.3 m between the end columns), its rows, its rear annex of three bays and its 月台 (19.0 x 6.2 m); the first cross wall meeting the hall on its front eave row;
  - the inner court's ranges along both sides (eleven cells each), the west one with a projection on its middle five bays; the inner lines south of them with a door each;
  - the raised walk on the axis (12.4 m wide) from the annex to 最上楼, and on it two concentric octagons (文殊亭);
  - 最上楼's seven bays with its façade and porch lines, the three-bay 顺山殿 at its ends;
  - the back gate's three cells on the north wall.

  The axis's middles (gate, 天王殿, 三圣殿, 月台, annex, walk, octagon, 最上楼) spread over 1.22 m. The distances along the axis agree with today's buildings within 3% (OSM: 天王殿 to 最上楼 99.4 m against S01's 102 m).
- **The texts (B):** S221 section 四 and its section on the halls, quoting 金勋's 成府村志 (E0681, research-only, facts cited): the gate of three bays, 筒瓦歇山, with the splayed screen wall 八字明壁 by it, the west one surviving; the bell and drum towers; 天王殿 five bays; 三圣殿 seven bays, 三进深, galleries front and back, a three-bay rear annex, side halls of five bays with 歇山 roofs; 文殊亭 octagonal with double eaves under Qianlong; 最上楼 seven bays with three-bay 顺山殿 east and west, the west one surviving. S228 (E0679): what survived and what was rebuilt, and that the rebuild drew on photographs and a Yangshi Lei ground plan (not seen).
- **The photographs before the losses (B):**
  - **P0177**, Osvald Sirén, 1918-35 (Östasiatiska museet, CC0, S86): 三圣殿 from the south-west through pines, the only picture of the hall before it was lost. It shows seven bays, lattice doors in the middle three and lattice windows over plain sill walls in the others, the lattice on the eave columns, a low stone platform with a terrace and flights before it, a stone base before the east flight, and a single-eave roof whose main ridge is short, with no gable triangle at the west end: a hip roof 庑殿 (the fit, below; Q299).
  - **P0173**, Bundesarchiv Bild 137-000605, about 1900 (CC BY-SA 3.0 de, S88): 文殊亭 with two eaves, its four-leaf lattice doors on two faces, its brackets and upper drum, two men before it; at the right a two-storey hall with a porch of tall columns, a balcony on a painted beam and lattice fronts (which hall it is: Q302); at the left a one-storey range.
- **The surviving buildings today (B for their form as repaired, C where repaired or rebuilt):**
  - **P0427** (2013, CC BY-SA 3.0, S70): the gate from the forecourt: red walls on a grey stone course, the round-arched door in a stone frame, the round windows in stone rings, the plaque, the band of green-blue painted beams, the grey 歇山 roof; the screen walls with framed panels and medallions; the towers' upper storeys and roofs behind.
  - **P0430** (2013, CC BY-SA 3.0, S70): 文殊亭 as repaired with two eaves in 2003 (four-leaf door on the south face, windows over grey brick sill walls on the diagonals, its court raised on a rubble face); at the right the east 五佛殿: two storeys, red columns through both, a balcony rail, a 硬山 with red gables rising over a one-storey range.
  - **P0453** (2013): the north side: the rubble outer wall with its grey coping, the back gate, 最上楼's solid red back wall and its 硬山.
  - **OSM** footprints of today (ODbL; `research/layers/osm_today.geojson`): roof outlines, a cross-check only (README below, Q300).
- **The rebuilds (reading aids only, C):** P0428 (三圣殿 with double eaves: not followed), P0429 (天王殿: red masonry fronts with arched doors, 歇山), P0431 (最上楼: 硬山, red gables, the porch columns through both storeys, the balcony).
- **Reconstructions by others (reading aids, never used):** R0005, R0045, R0064, R0065 (`research/reconstructions/catalog.csv`).

## What the model draws, and on what

- **The gate (B form, its heights read on P0427):** 10.1 x 5.6 m (S01's cells; the depth C) on a platform 0.50 m above the forecourt with three steps front and back; a grey stone course 0.76 m; the red wall 2.70 m to the beam band; the round-arched door 1.2 m wide, its crown 1.75 m above the floor, in a stone frame, red plank doors with gilt studs set in; a round window 1.6 m across in a stone ring with a stone grille either side, centred 2.86 m from the door; the plaque above the door; the painted beam band; the 歇山 in grey tile, its ridge 5.50 m above the floor. The back repeats the front (C).
- **The screen walls (B):** on S01's cells, red with a grey-green framed panel, a medallion and corner pieces on both faces, a stone base, a small tiled coping (P0427); heights C.
- **The small gates (C):** the side gates on the south wall, the two in the second cross wall and the back gate: masonry with one arched door and a small 歇山.
- **The towers (C):** on S01's squares: a red masonry lower storey with an arched door turned to the axis, a skirt roof, an upper storey with an arched window each side, a 歇山 roof (P0427 shows their tops); the bell tower west and the drum tower east (C: S221 does not say which).
- **天王殿 (C):** five bays (S221) in the second cross wall (S01): red masonry fronts with three arched doors and two small arched windows, the beam band with brackets, a 歇山 in grey tile: the form of the rebuild (P0429).
- **The side halls (B bays and roof, C form):** five bays, single-eave 歇山 in grey tile with a porch (S221); the east one on S01's cell, the west one mirrored (Q305); the depth 6.4 m between S01's 5.3 m and today's roof outline (9.3 m).
- **三圣殿 (B form from P0177, C heights):**
  - seven bays (3.20, 3.36, 3.36, 3.68, 3.36, 3.36, 3.20 m: 23.52 m against S01's 23.25 m between the end columns), 14.0 m deep between the eave columns (S01's rows; Q300);
  - the platform 0.95 m (P0177's six risers), its edge 0.9 m;
  - lattice doors in the three middle bays, lattice windows over sill walls in the others, at the eave columns (P0177);
  - the bracket band, the plaque;
  - a single-eave **hip roof 庑殿** in grey tile with a ridge (P0177's fit, Q299), its column 4.6 m and its ridge 11.1 m above the court (the sweep below; C);
  - the 月台 (S01's outline) one riser lower than the hall, from the hall's platform to S01's front line, with three flights at its front (P0177) and a stone base before the east flight;
  - the rear annex 后庑殿 (S221; S01's three cells), a rolled 歇山 (C), its back door onto the walk.
- **The raised walk (B outline, C height):** S01's two lines, 0.75 m above the court, faced with rubble as the court round 文殊亭 and 最上楼's terrace are today (P0430, P0431), with two flights on each side; a deck the ways lie on.
- **文殊亭 (B form, C size and heights):** on the walk, its own octagonal platform 0.30 m higher with two steps south and north; eight red columns on S01's inner octagon (face 2.65 m, 6.4 m across); four-leaf lattice doors 隔扇 on every face (P0173 shows two faces; carried round, C); the beam band and brackets; the lower eave from its tip at 4.50 m to the upper drum; the drum with small lattice windows between red columns, 5.25-6.40 m; the upper eave from 7.10 m to the apex at 8.60 m; a gourd finial to 9.80 m (heights above its floor, from P0173's proportions to the face). The roofs are concave by the pavilion's 举架 with lifted corners (`oct_roof`).
- **The ranges (B cells, C form):** eleven bays along each side of the inner court on S01's cells; three bays at each end of one storey, 硬山 in grey tile; the middle five bays the **五佛殿**, two storeys with a porch of columns through both storeys, a balcony and a 硬山 with red gables (as the east one stands today, P0430; Q303), its porch on S01's projection (the west one) and carried over (the east one), on a platform 0.45 m with a flight.
- **最上楼 (B front from P0173, C back and heights):** seven bays (3.52, 3.68, 3.84, 4.16, 3.84, 3.68, 3.52 m: 26.24 m against S01's 26.7 m), on its terrace at the walk's level with a flight at each end of its front; the porch columns running up to the upper eave, the ground storey's doors (three middle bays) and windows at the façade line, the balcony 平座 on its painted floor beam with its rail (P0173), the upper storey's windows; the solid red back wall, the red gable walls 硬山 with grey corbels and barge bands, the grey roof (the rebuild, P0431, P0453: C); the ground columns 3.8 m, the balcony's floor 4.3 m, the eave beam 7.9 m, the ridge 11.8 m above its floor (C).
- **The 顺山殿 (B bays, C form):** three bays on S01's cells at the tower's ends, one storey, 硬山 with a porch.
- **The walls (B lines, C heights):** the outer wall of rubble with a grey coping, 3.0 m (P0453 shows it today); the cross walls and the inner lines red with grey copings, 3.4 and 3.0 m; the doors in the inner lines left open; the short walls closing the corner yards of the north range.
- **The courts:** earth, their old trees the planting of Round 12 (Q213); `level` in `joints.json` keeps the generated hills of Round 10 out of the whole temple (four stood there, up to the inner court's middle); the forecourt before the gate is `clear` (open ground, no hill, no planting: the dig of 2005 found a road base and a carriageway there, E0685).

## Match check

Three photographs fitted with `tools/plate_overlay.py fit --object QC11 --sheets research/scenes/QC11-zhengjue-si` (`plate_keypoints.csv`, `photo_viewpoints.csv`; results in `plate_fit.csv`, `plate_cameras.json`):

- **P0177 (三圣殿, Sirén):** 12 points (the front columns' feet and tops, the ridge's ends, the east eave corner), **0.44 m rms at the object** (25.1 px), median 0.27 m, max 1.14 m (the ridge's east end); anchored test 0.75 m. The camera is held in the court between 天王殿 and the hall (prior 29 m off, 0.5 m; eye 1.5 ± 0.3 m): left free, it ran 64 m back behind 天王殿 with a long lens (0.28 m), a place from which the hall cannot be seen, so that fit is not used. It settles 30 m off with a 49° lens and its eye 0.5 m up: a low tripod, or a platform a little higher than drawn.
  - **The roof form:** with a 歇山 the ridge's ends stand 1.84 and 3.87 m off (1.25 m rms); with a 庑殿 0.27 and 1.14 m (0.44 m). The model draws the 庑殿 (Q299). The blend (`screenshots/r28/overlay_P0177_QC11_all_blend.jpg`) lays the hips, the eaves and the ridge on the photograph's.
  - **A sweep** (columns 4.0, 4.6, 5.2 m; depths 11 and 14 m; the same camera prior): all points 0.51/0.43, 0.53/0.46, 0.65/0.62 m (depth 11/14); anchored 0.87/0.91, 0.60/0.77, 0.82/1.02 m. The depth of S01 fits better at every column and the anchored test is least at 4.6 m: a shallow curve, kept C.
- **P0173 (文殊亭, about 1900):** 11 points on the octagon (columns' feet and tops, both eaves' tips), **0.18 m rms** (9.8 px), max 0.3 m. The octagon cannot tell its reading from its mirror (camera south-west or south-east: both 0.18-0.19 m); the sheet takes the south-west, which puts the four-leaf door on the south face as today. The two-storey hall at the right fits neither 最上楼 at S01's place (the camera then stands inside 三圣殿, 4.5 m up, 0.54 m) nor the east 五佛殿 (0.98-1.35 m); its points are `skip` (Q302).
- **P0427 (the gate today):** 11 points, **0.15 m rms** (6.0 px), max 0.22 m. The first fit at the box's 9.6 m drew the wall's ends 0.2 m inside the photograph's and the ridge 0.5 m low: the gate is now S01's 10.1 m and its ridge 5.5 m.

Overlays: `screenshots/r28/overlay_P0177_QC11_all_*`, `overlay_P0173_*`, `overlay_P0427_*` (the three pictures are free).

## Iteration log

1. **First run:** the layout from S01; 三圣殿 with the dossier's single-eave 歇山, galleries front and back and the platform's edge 1.1 m; 文殊亭 with doors on two faces and the kit's pyramid; the 五佛殿 a one-storey hall with a porch.
2. **The water at the gate:** the gate and the west screen wall stood at the edge of a pond: Round 1's region R0251 (W0069), an automatic wash call of +1.6, grade C, between the gate's road south and the temple's wall line running south-west. S01 draws open ground and the road to the river; the dig of 2005 found the road's base there (E0685). It is land now (`research/plan/water_removed.json`; W0069 stays taken).
3. **Generated hills in the courts:** Round 10's free land held four hills inside the temple (H2259, H2261, H2267, H2376, one across the inner court). `level` over the whole temple keeps them out and leaves the trees.
4. **The flights inside a frame:** the masonry halls' flights were first drawn inside the hall's pushed frame and so placed twice over (their feet landed on other halls' floors in `report.json`); they are drawn after the frame is popped.
5. **P0177's hall:** the lattice stands on the eave columns, not behind a gallery, and the platform's edge is narrow; the first fit then gave 1.31 m with the ridge 190 px off, and its camera ran 64 m back (held in the court since, below): the 'ornament' read as the west ridge end was a pine's broken top, and the roof is a hip roof (above).
6. **The gate on P0427:** 9.6 to 10.1 m wide, the ridge 5.0 to 5.5 m: 0.25 to 0.15 m.
7. **P0177's camera:** a free camera ran behind 天王殿 with a long lens (the overlay showed 天王殿's back wall); held in the middle court the fit is 0.44 m and the roof's vote stands (1.25 m for a 歇山).
8. **文殊亭's eaves:** the kit's pyramid and skirt drew thick dark bands; `oct_roof` draws them concave with lifted corners and a 0.2 m fascia. Doors on every face after P0173.
9. **The 五佛殿:** P0430 shows the surviving east one as a two-storey 硬山 hall rising over the range; drawn so (Q303).
10. **The decks:** the walk, the 月台 and 最上楼's terrace were first footprints too, so the way QC-013 (B) from 文殊亭 to 最上楼 crossed 23 m of 'box' (`tools/check_paths.py`); they are decks only.

## Joints and ways

- **Ground joints** (`tools/check_models.py`): 172 (walls' feet, platforms' and terraces' corners, flights' feet, pedestals). None stands above the ground; the deepest is 0.40 m in.
- **Ways:** 13 of Round 9 end at the model's boxes, 0 more than 0.5 m from an entry.
- **Joints on the decks** (`report.json` `deck_joints`): 31, every one at 0.00 m: the gates' and halls' steps onto their floors, the 月台's three flights, 三圣殿's step onto the 月台, the annex's step onto the walk, the walk's four flights, 文殊亭's steps, 最上楼's terrace flights, the 五佛殿's flights.
- **Footprints:** platforms, flights, walls, pedestals. **Decks:** the walk, the 月台, 最上楼's terrace. **Level:** the whole temple. **Clear:** the forecourt.

## Where the model and the sources disagree

- **三圣殿's roof (Q299):** a hip roof on P0177 against Round 7's 歇山 reading and the rebuild's double-eaved 歇山.
- **三圣殿's depth (Q300):** S01's 14.0 m against today's roof outline (13.6 m deep, so 10-11 m between columns).
- **The Manjusri image (Q301):** 9.6 m in 金勋's memory against an 8.6 m pavilion.
- **P0173's right-hand hall (Q302):** not reconciled with S01's distances.
- **The 五佛殿's upper storey (Q303)** and **the west side hall (Q305)**.
- **Today's footprints (OSM) against S01:** 三圣殿 29.8 x 13.6 m, 最上楼 30.7 x 11.9 m, 天王殿 19.3 x 10.4 m, the side halls 20.2-22.9 x 9.2-9.3 m (roof outlines); S01's columns 23.3, 26.7 and 16.1 m and its side hall 17.9 m long fit inside them with eaves of 1.3-2.0 m, except 最上楼 (S01 about 2 m shorter). OSM sits about 6 m west of the georeferenced S01 here, inside the fit's error (Q7).
