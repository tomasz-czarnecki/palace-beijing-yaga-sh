# YM17 鸿慈永祜 Hongci Yonghu: the ancestral temple 安佑宫 Anyou Gong with its gates, moats and archways, a detailed model (Round 27)

The fourteenth detailed model and the sixth of a Chinese compound. 鸿慈永祜 is the imperial ancestral temple in the north-west of the garden. Qianlong built it in 1742-43 on the model of 寿皇殿 (S05 j81:19b-21b, E1556), and there the portraits of Kangxi and Yongzheng were kept. On 18-19 October 1860 its halls were burned with the rest of the garden by British troops on Elgin's order (S02 pp.187-188). The masonry stood as a ruin until it was pulled down under the Republic (S02 p.218). Its 华表, its qilin and one ramp stone survive at Peking University and before the old National Library (S943, S980).

The model draws the whole precinct as S01 draws it, from the south:
- the four marble 华表 round the glazed archway 鸿慈永祜坊 (YM17-01, -02);
- 致孚殿 in its yard (YM17-05);
- the outer moat 月河 with five marble bridges (YM17-04);
- the forecourt with the three timber archways 三坊 (YM17-03) and the two stone qilin;
- the outer wall with five gates (YM17-N01, -AW012, -AW013) and a north gate;
- between the walls: the waiting rooms 朝房 (YM17-09), the well pavilions (YM17-08), the inner moat with five bridges (YM17-07), the corner yards with their ranges (YM17-B0156, -B0158);
- 安佑门 on its terrace in the inner wall (YM17-06);
- the inner court: the side halls 配殿 (YM17-11), the stele pavilions 碑亭 (YM17-12), the green-glazed burners (YM17-13);
- 安佑宫 (YM17-10) on its marble terrace with five flights, the ramp stone, the bronzes.

Generator: `anyougong.py` (`uv run python models/YM17-hongci-yonghu/anyougong.py`, after `scripts/kit1860.py` has run once). It builds on `scripts/hall_parts.py` (the hall kit in Python, Round 17), `scripts/model_parts.py` and `scripts/model_site.py`.
- Hand-edited sheet: `plan_readings.csv`, every line read on S01 in plan pixels.
- `anyougong.py --moats` writes the two moats' rectified points into `research/plan/water_manual.json` (see "The shear"). Run it once after a change to `plan_readings.csv`, then `scripts/build_r1.py`.
- It writes `model.glb`, `params.json`, `keypoints.json`, `joints.json` (with `level`, new in Round 27), `summary.json` and `report.json`.

## Evidence

In the order of authority the brief sets: the dossier (`research/scenes/YM17-hongci-yonghu/`), the plan and the texts, the pictures, the surviving pieces. Reconstructions by others are reading aids only (R0082, R0083: not used).

- **The plan S01 (B)**, re-read in Round 27 on 2.5-6x crops with a 5 px grid (`plan_readings.csv`):
  - the hall's ten column lines and four rows: nine bays, 2.97-3.53 m, 29.8 m between the end columns; spans of 4.15, 7.19 and 2.59 m back to front, 13.96 m. These ten by four lines are Malone's forty pillars;
  - its platform and the 月台 as one T-shaped outline (39.6 x 19.6 m and 25.1 x 13.7 m);
  - five flights, three at the front and one on each side of the 月台;
  - the stele pavilions' octagons, the side halls' and waiting rooms' five cells, the burners' and wells' squares;
  - the inner wall (72 x 70 m) and the outer wall (96 x 100 m once rectified) with their gates;
  - the inner moat, a moon river with five breaks where S01 draws its bridges;
  - the U-shaped outer moat with five breaks;
  - the three bars of the timber archways, the two squares of the qilin;
  - 致孚殿's yard with its west door and three cells;
  - the glazed archway's bar (13.4 m) and the four 华表 on a square of 29-32 m (Malone: about 100 ft).
- **The texts (A):**
  - S05 j81:19b-21b (E1556): the glazed archway with its faces 鸿慈永祜 and 燕翼長詒, the stone 华表, the three archways round it with their six faces named, the moon-river bridge, 致孚殿 of three bays facing west, the gate 安佑门 of five bays behind three white marble bridges, the well pavilions, the waiting rooms of five bays, the double-eaved hall of nine bays, the side halls of five bays, the stele and burner pavilions.
  - The preface of 1744 (S05 j81:24a): tall pines all round the wall.
- **Malone, 1934 (B, S02 pp.83-88, E1561-E1563):**
  - the four marble pillars about 20 ft high, about 100 ft apart at the corners of a square, round a glazed pailou of four short walls and three gates, 'in a small hollow between hills';
  - the moat crossed by five marble bridges, the middle one for the emperor alone;
  - three pailou as a screen before the gates, two stone qilin guarding the three middle gates;
  - five gates in a red wall with yellow glazed coping;
  - between the walls the waiting rooms, a second moat with three bridges and two side bridges, two covered wells, and a marble terrace with the inner gate;
  - inside, two green glazed burners, pines, two double-roofed pavilions over marble steles;
  - the hall on a marble terrace with five stairs, the middle one carved with dragons; incense burners and bronze birds and animals; ten pillars across the front and forty in all; a double roof of yellow glazed tile.
- **S360 (E1560, B):** nine bays, 重檐歇山, yellow glazed tile. **S361 (E1564, B):** bronze deer and cranes before the hall.
- **The leaf of 1744 (S08 P0017, A for 1744):**
  - the hall double-eaved 歇山 in yellow tile, red columns and lattice, green-blue beams under both eaves;
  - the octagonal stele pavilions with double eaves; the side halls' yellow 歇山 roofs;
  - the gate hall with a white terrace and balustrade before it;
  - the vermilion walls; the three arched glazed gates with red doors and the side gates with yellow roofs;
  - the timber archways with red diagonal props;
  - the three white arched bridges with balustrades and red railings along the banks;
  - 致孚殿 in a red-walled yard;
  - the glazed archway's three gates between four red walls with round glazed panels.

  Read on the 1300 px copy (`/opt/data/cache/scratch/palace_r7_tmp_album/ym17.jpg`, registered to P0017.jpg at NCC 0.90).
- **The surviving pieces (B):**
  - the 华表 about 8 m on octagonal bases 1.24 m high (S980, S818; P0809-P0813 today; P0196, about 1882, on the site with its dragon, dew plate and beast);
  - the qilin 1.74 m on bases 0.98 m high, 1.41 x 1.95 m (S943);
  - the ramp stone 3.15 x 1.30 m with a relief 1.00 m wide (S943).
- **Not seen:** the Yangshi Lei sheet 安佑宫供器尺寸及殿底样 (E1566, Xianfeng) and the 初编 plates pp.362-386 (E1565): research-only and not on disk. No dig has been published (Q119).

## What the model draws, and on what

- **The axis.** The frame's z runs along S01's axis from the hall's terrace and 安佑门 to the middle of the four 华表 and the forecourt's south archway. The middles S01 draws on it spread over 3.32 m (`report.json` `axis_reads`); the axis-borne parts are centred on their mean.
- **The shear.** In this frame the fit in use (`research/georef/`) turns S01's north-south lines within 0.8° of the axis, but its east-west lines fall 7.4° to the east (k = -0.129 on the four long walls). So S01's rectangles came out as parallelograms, and the outer wall 113 m deep for about 100 m. The temple is rectilinear, so every reading is rectified about the axis: z' = z - k (x - x_axis). Points on the axis do not move; the outer wall's corners move 5.9-6.4 m. The moats are traced water, and their points in `research/plan/water_manual.json` are rectified the same way, so that they stay between the walls (Q295).
- **安佑宫:**
  - S01's grid, centred on the axis (B);
  - a porch in the front span, red lattice doors in all nine bays (the leaf, A), windows at the back, red walls at the ends (C);
  - double eaves on the kit's 重檐 with the bracket band (大式, C), 歇山 in yellow tile (A);
  - the column 4.6 m, the lower eave 7.35 m and the ridge 14.25 m above the court (C);
  - the plaque 安佑宫 under the upper eave (S05; the board C).
- **The terrace:** S01's T-shaped outline as one marble terrace, 1.6 m above the court (C). It has a balustrade (the leaf), open along its back on the inner wall.
  - The five flights are S01's, with their runs (4.4 m in the middle); risers are about 0.15 m, so the treads are 0.40-0.44 m.
  - The ramp stone 御路 is 1.30 m wide (S943), with raised blocks for its carving (C).
  - The bronzes: two censers, two cranes, two deer (B for their being there, C for their places and forms).
- **The inner court:**
  - the side halls of five bays in yellow 歇山 against the inner wall (A, B; heights C);
  - the stele pavilions on S01's octagons: red walls with four arched doors, a lower eave, a red drum, an octagonal upper roof, a stele inside (C forms);
  - two green-glazed burners (C form);
  - a marble way on the axis (C);
  - the court is earth, with the cypresses and pines of the planting (GS-0634, GS-0143).
- **安佑门:**
  - five bays, 12.3 m between the end columns and 6.3 m deep as S01 draws it (B);
  - single-eave 歇山 in yellow tile with plank doors (A);
  - on a marble terrace 1.2 m high carried 2.5 m before it, with a balustrade and three flights (Malone, the leaf; sizes C).
- **The walls:** red with yellow glazed coping (Malone, B), the inner 4.2 m and the outer 4.4 m high (C). A small gate either side of 安佑门 (S01, the leaf). The outer wall's five gates: three arched glazed gates (5.0, 3.6, 3.6 m) with glazed frames, friezes, yellow 歇山 roofs, red doors with gilt studs, the middle one with a plaque board (the leaf; sizes C), and a smaller gate each side. A gate of three bays on the north side (S01; form C).
- **The two moats:** Round 10's water on the traced channels, lined with stone and a marble coping. The inner moat has marble rails (C); the outer has red timber railings (the leaf).
  - Inner moat: five bridges at S01's breaks, three arched in the middle (the middle one 3.2 m wide) and two flat at the sides (C).
  - Outer moat: five bridges, three arched with white balustrades (the leaf; the middle one 4.2 m wide, Malone's emperor's bridge) and two flat at the ends (C).
  - The widths: S01's breaks are 1.3-3.9 m, read between the ink. The bridges are drawn 2.4-4.2 m wide (C).
- **The forecourt:** paved between the side archways (the leaf, C).
  - The qilin on their bases at S01's squares (S943's sizes, B; the beast standing, C).
  - The three timber archways of four posts and three roofs, with clasp stones and the red props both ways (the leaf, A; S01's widths, 9.4-9.9 m, B; heights C, the ridge 7.95 m).
- **致孚殿:** three bays facing west, yellow 歇山, in its red-walled yard with a door on the west (S05, the leaf, S01; heights C).
- **The glazed archway:** 13.4 m (S01; S01's bar lies 2.2 m west of the square's middle, the model centres it on the square as Malone puts it). Four short red walls with glazed discs and small roofs, three open gates with glazed posts, friezes and yellow roofs, the middle one higher with a plaque (the leaf, Malone; heights C).
- **The four 华表:** at S01's squares. Each has the octagonal sumeru base 1.24 m (B), an octagonal shaft with a dragon coiled one and a half turns (P0196), a cloud board, a dew plate and a seated beast, 8.0 m in all (S980, B; the parts' sizes C).
- **The ground:** the walled compound, the forecourt, 致孚殿's yard and the 华表 square are `level` in `joints.json`: no generated hill of Round 10 stands there (`scripts/hills1860.py`). Before, hills up to 4.5 m stood in the forecourt and 5.9 m inside the square of 华表. The planting keeps its trees in the courts. Hills generated outside the square now flank it, Malone's hollow.

## Match check

- **The leaf P0017** (`research/scenes/YM17-hongci-yonghu/plate_keypoints.csv`, `photo_viewpoints.csv`, `plate_fit.csv`, `plate_cameras.json`):
  - 29 points on the hall, the pavilions, the gate, the walls, the outer gates, the three white bridges and the glazed archway; read on the 1300 px copy and mapped to P0017.jpg;
  - fitted with `tools/plate_overlay.py fit --object YM17 --sheets research/scenes/YM17-hongci-yonghu`: **3.96 m rms at the object** (19.9 px), median 2.36 m, max 9.99 m;
  - the camera sits about 1 km away with a long lens, as for the leaves P0001 (3.6 m), P0003 (3.79 m) and P0029 (2.97 m);
  - the hall's eight points lie 1.0-2.9 m off;
  - the worst: the inner wall's south-east corner (9.99 m: the leaf's inner court is wider, or the corner was misread), the archway's east gate (7.1 m: the leaf spreads the archway), the outer wall's west side gate (8.6 m), the outer gates' ridges 4.2-6.1 m below where the leaf paints them.
  - Overlays: `screenshots/r27/overlay_P0017_YM17_all_*.jpg`, `render_P0017_YM17_all.png`, `points_P0017_YM17.jpg`.
- **The leaf does not settle the heights:** a sweep of the hall's column 4.0-5.8 m and the upper roof's rise 5.9-7.9 m moves the hall's eight points only between 1.69 and 2.15 m rms and the whole fit between 3.85 and 3.90 m (`docs/rounds/README.md`, palace_r27_anyou). The model keeps 4.6 and 6.9 m (C; Q296).
- **The plan:** the axis spreads 3.32 m; the hall's middle on S01 lies 0.45 m off it. The 华表 square on S01 measures 29.3 x 31.8 m once rectified, Malone's 100 ft (30.5 m).

## Iteration log

1. **First run:** the outer wall came out 113 m deep, and every off-axis reading moved by the plan's shear. Found by measuring S01's walls in the frame; rectified (above) and the moats retraced through `--moats`.
2. **The ground:** generated hills of Round 10 stood in the compound: behind the hall, in the inner court, in the forecourt (4.5 m) and in the square of 华表 (5.9 m, burying the columns' bases). The `level` key was added (`scripts/model_site.py`, `scripts/hills1860.py`): the courts keep their trees but no hill.
3. **Water:** the moats were land on S01's trace, drawn as closed pieces with breaks at the bridges. They are traced as water now (RM002, RM003, `islands` false so that island I004 and the ids after it stay). The strip between the walls on the east side was water (W0152, an automatic wash call, C); it is land now (`research/plan/water_removed.json`).
4. **Found on the shots and fixed:** a grey band between the hall's eaves (the leaf paints it: now red with the bracket band); the plaque on the lower eave (now under the upper); 安佑门's terrace 3.5 m deep crowding the inner bridges (now 2.5 m); the archways' clasp stones 1.1 x 1.4 m (now 0.84 m square); two cameras inside a roof and a tree.
5. **Checks:** a way through the south archway's box ended 1.58 m from its entries. The archway was centred on the mean axis, 1.2 m east of S01's bar; it now stands where S01 draws it, with an entry in its middle bay. The terrace's three flights of S01 (YMW-057..059) are drawn by the model (`research/paths/exceptions.csv`).

## Where the model and the evidence disagree, or are silent

- Every height (Q296); the hall's size, S01's grid being small for its rank (Q298).
- S05's two 华表 against Malone's and S01's four (Q179): four drawn.
- The leaf's grey-green copings against Malone's yellow glaze (yellow drawn, Malone saw the ruin's tiles).
- The bridges' widths from S01's breaks (Q297).
- The form of the qilin (no photograph on disk) and of the bronzes.
- What the corner ranges were (S05 names none): C.
