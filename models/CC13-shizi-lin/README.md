# CC13 狮子林 Shizi Lin, "Lion Grove": the rockery garden of 长春园, a detailed model (Round 29)

The sixteenth detailed model and the ninth of a Chinese compound. 狮子林 Shizi Lin stood in the north-east of 长春园 Changchun Yuan, east of 丛芳榭. Qianlong had it built in 1772 after the Suzhou garden of that name, then owned by a 黄 family, and after 倪瓒 Ni Zan's scroll of 1373, with rockwork piled by Suzhou craftsmen (S05 j83:13b-15b; E0203). He named eight scenes in 1772 and eight more after (E0203, E0218), sixteen in all, and kept his copy of Ni Zan's painting in 清閟阁 (E0223). Jiaqing and Daoguang wrote on the sixteen scenes again; it was partly rebuilt in 1828, and the last dated entries are of 1858 (E0221). It is not among the buildings left standing after 1860 (E0451), so it burned when British troops set fire to the gardens on 18-19 October 1860 (S02 pp.187-188). Today there are scattered remains; the rainbow bridge and the water gate were re-erected on their sites (P0415, P0416, P0500, 2013).

The model draws the garden in its state before October 1860:

- **the west garden**: 清閟阁 Qingbi Ge, "Pavilion of Pure Seclusion", of seven bays and two storeys on the pool 曲池; the rockery 假山 round 纳景堂 Najing Tang with its paved court, a summit with a stone stair 磴道, two caves and standing peaks; the winding stone bridge under its wisteria frame 藤架; the rainbow bridge 虹桥 over the pool's west arm, landing at a doorway in the west wall; the channel along the south wall to the water gate 水门;
- **the north side**: the climbing gallery 云廊 up to 探真书屋 Tanzhen Shuwu on its rock terrace, the gallery west to 丛芳榭, the covered way north to the one-bay tower 小香幢 Xiao Xiangchuang;
- **the court between the rockeries** with 清淑斋 Qingshu Zhai;
- **the east garden** in its curved wall: the stream 溪 with 横碧轩 Hengbi Xuan, an open hall, and a bow-shaped bridge before it; the peak with the four-column pavilion 占峰亭 Zhanfeng Ting and its stair; 延景楼 Yanjing Lou of two storeys on the north wall; the stone room 云林石室 Yunlin Shishi; the rock masses.

Generator: `shizilin.py` (`uv run python models/CC13-shizi-lin/shizilin.py`, after `scripts/ground1860.py` and `scripts/boxes1860.py`), on `scripts/hall_parts.py` (the hall kit in Python, Round 17), `scripts/model_site.py` and 文源阁's rock-garden helpers (Round 25: `lump`, `rock_mass`, `flight`, `wall_run`). Its own parts: `arch_faces()` (a stilted semicircular arch: faces, ring proud of the face, barrel, jambs), `hongqiao()`, `watergate()`, `open_hall()` (an open hall 敞轩 with a seat rail), `square_pavilion()`, `rock_steps()` (a stair of rough stone), `rock_bank()` (piled-stone shores), `door_in_wall()`, `kit_hall()` (a hall by `HallKit.hall` with its key points). Hand-edited sheet: `plan_readings.csv` (every line read on S01, in plan pixels). It writes `model.glb`, `params.json`, `keypoints.json`, `joints.json`, `summary.json` and `report.json`. Two switches in the environment exist only for the sweeps below, never for a run of step 6: `CC13_HQ` (the rainbow bridge: span, jambs, ring, width) and `CC13_SM` (the water gate: span, ring).

## Evidence

By part, in the order of authority the brief sets: the dossier (`research/scenes/CC13-shizi-lin/`), the plan and the texts, the photographs of today, the comparables and the reconstructions of others as reading aids only.

- **The plan (B):** S01, re-read in Round 29 on 3x, 4x and 5x crops with a 10 px grid (`plan_readings.csv`). It gives:
  - the west line (x 11901) against 丛芳榭, the south line along the lake (y 1700-1705) and the east line (x 12060-12067) of the west garden, about 39 x 49 m;
  - 清閟阁's range of seven cells (x 11902-12037, about 33 m) with its rows, the label 清閟阁 written on the washed band before it;
  - the washed band and the strip west of the rockery: the pool (below);
  - the rockery's outline drawn with rock strokes round a hall of four cells (纳景堂 here) and a plain rectangle south of it;
  - two lines across the pool's west arm from the west line to the rockery: 虹桥;
  - the half-round at the south-east corner where the lake's lobe reaches the wall: the water gate (Round 1's box F0359);
  - 探真书屋's court (x 11825-11893, y 1388-1424) with its two cells, and the narrow double line stepping down from it to the range's back: the climbing gallery;
  - the strip north from the range's east end with two cells at its north end, the label 小香幢 on the hill beyond;
  - the court between the rockeries (x 12063-12115, y 1555-1620) with its inner rectangle;
  - the east garden's wall, curved on the east; three cells on its north wall; three small cells among the rocks; a mountain sign; a hall of four cells; a narrow winding double line (the stream) ending in a small closed outline (the pond); rock strokes.
- **The texts (A for what they say, by the hand of the man who built it):** the 1772 prefaces and poems on the first eight scenes (S05 j83:13b-15b, E0203) and the second eight (E0218), the yearly poems of 1773-1786 (S361, E0225-E0266), the list in 日下旧闻考 (E0220). For the model:
  - 清閟阁: 臨曲池面假山 (by a winding pool, facing the rockery); 清閟小閣置近臨活水 (E0203);
  - 虹桥: 跨水為小橋 ... 其下可舟通 (a small bridge over the water, boats pass under it, E0203); 卧波上者形如半，印水觀來體忽圓 (on the waves a half, in the water's reflection a whole circle, E0227);
  - 假山: 吳下髙手堆塑 (piled by Suzhou masters, E0203); 房山石似洞庭 (Fangshan stone like Taihu's, E0240);
  - 藤架: 紫藤引架垂隂 ... 可十數武於石橋宛轉 (a purple wisteria frame over a winding stone bridge of a dozen paces, E0203); 石橋上置藤蘿架 (E0237);
  - 磴道 and 占峰亭: 循巖陟磴 (E0240); 峰頂一笠 ... 歷艱陟頂得稍平，四柱小亭翼然據 (on the summit, a small four-column pavilion, E0243);
  - 探真书屋: 雲廊拾級上 (up the cloud gallery by steps, E0252);
  - 小香幢: 一間樓 (a one-bay tower, E0218); 石磴玲瓏倚翠幢，上為佛室 (stone steps, a shrine above, E0249);
  - 延景楼: 詭石玲瓏棧徑通 ... 拾級望遙 (E0255); 云林石室: 三間十笏惟容膝 (three small bays, E0258);
  - 横碧轩: 文軒築溪上，溪水如帶横 (E0261); 有橋如弓彎 ... 過橋坐敞軒 (a bow-shaped bridge, an open hall, E0262);
  - 清淑斋: 就樹得佳隂 ... 溪聲清以沉 (E0246);
  - 水门: 牆界林園水作門 (E0264); 跨水為牆下置門 (a wall across the water with a gate below, E0265); 跨波門徑上騎牆，歷歷人行來往航 (a path on the wall's top over the waves, boats coming and going, E0266);
  - the pines young in 1772 (稚松皆新種, E0218).
- **The photographs of today (free, B for the re-erected arches' form):** P0415 (the rainbow bridge re-erected on its site, 2013: the ring of voussoirs, the straight jambs, the deck over the crown, a beast's head on the haunch, steps at its end); P0416 and P0500 (the water gate's ring re-erected on its site, from outside and from inside, 2013); P0417 (the same ring, 2022); P0443 and P0802 (the ruins of the east part, 2013); P0442 (the marble slab with the 1772 poem of the water gate). No picture of the garden standing is known.
- **Comparables (not this garden, reading aids for forms):** the Suzhou garden (T073; P0557-P0559, P0649, P0650) for the piled rock, the standing peaks, the caves and the white walls; the Chengde copy 文园狮子林 (T072; P0560, P0561).
- **Reconstructions by others (reading aids, never used):** R0028, R0122.

## What the model draws, and on what

- **The pool (B place, C course):** Round 29's water W0368 (`research/plan/water_manual.json` RM004), at the lake's level, its banks of piled rock (`rock_bank`, C): the band before 清閟阁, the west arm, the channel along the south wall to the water gate and out to the lake's lobe (Q306).
- **清閟阁 (B bays, C form and heights):** seven bays (4.32, 4.48, 4.64, 4.96, 4.64, 4.48, 4.32 m: 31.84 m against S01's 33 m between its end lines), 8.32 m deep (a front porch of 1.60 m on the pool, the rooms 5.12 m, a gallery of 1.60 m behind: S01's rows), two storeys (閣): its platform 0.50 m, the upper floor 3.70 m, the eave 7.10 m, the ridge 9.60 m above its ground; a rolled 歇山 in grey tile; lattice doors in the three middle bays, windows elsewhere, a back door to the climbing gallery; the plaque under the upper eave. Its front is the pool's bank (Q310).
- **藤架 (A form, C course):** a stone bridge of three turns across the pool from the 明间 to the rockery, 1.60 m wide, its deck 0.45 m above the water on piers, low stone rails; a timber frame of posts, beams and purlins 2.60 m over the deck carrying green wisteria with purple racemes hanging; a step down from the porch.
- **虹桥 (A form, B line, C size):** on S01's line across the west arm: one stone arch, a half circle 1.60 m across on straight jambs 1.10 m above the water, its ring 0.28 m proud of the face in two tones, a beast's head on the crown, the barrel 2.40 m wide (S01); the deck level over the whole arch 2.32 m above the water, seven steps down to the doorway in the west wall and ten to the rockery's bank. The size from a sweep on P0415 (below).
- **水门 (A form, B place, C size):** a stone arch 3.00 m across through the east wall where the channel leaves, its springings on the banks' rock 1.37 m above the water, its ring 0.48 m, the wall 1.40 m thick over it with a walk on its top 4.50 m above the water between low white parapets (門徑上騎牆); the marble slab with the 1772 poem over the arch on the garden's face (P0442; its place C, Q309).
- **The rockery (B outline, C form):** irregular blocks on S01's outline, stacked in tiers no taller than their width, each set off the one below (the Suzhou manner, C), from 1.4 to 3.4 m and up to 5.2 m at the summit north-east of 纳景堂; sixteen standing peaks 2.6-4.2 m of narrow stacked stone; the summit pad 4.3 m above the ground with a rough stone stair from the court; two caves the paths run through with lintel stones; rock banks on the water. The footprints are the masses drawn in by 1.2 m, so the planting of Round 12 (pines and bamboo, E0218) stands at their edges.
- **纳景堂 (B place, C form):** three bays (3.84, 4.48, 3.84 m) with a front porch, a rolled 歇山, on a paved court a step above the ground on S01's rectangle.
- **The north side (B lines, C forms):** the climbing gallery 2.0 m wide from 清閟阁's back door up 1.80 m in steps over its first 16 m to 探真书屋's court on its rock terrace; 探真书屋 two bays (7.04 m), a 硬山; the gallery west to 丛芳榭; the covered way north to 小香幢, one bay (3.52 m) and two storeys with a 歇山.
- **清淑斋 and its court (B court, C hall):** the court's wall on S01's rectangle with doorways west (through the west garden's east wall) and east; three bays facing south.
- **The east garden (B lines, C forms):** its wall on S01's curve; the stream (Round 29's water W0369, RM005) and its pond with rock banks; 横碧轩 an open hall of three bays (10.24 m) on red columns with a seat rail, facing the stream, a rolled 歇山; the bow bridge, a small stone arch 1.8 m across on the hall's axis; 占峰亭 on S01's mountain sign, its floor 5.1 m above the ground on a rock pad, four columns (2.6 m apart), a seat rail, a pyramid roof, a stair of rough stone from the south (Q311); 延景楼 three bays and two storeys facing south; 云林石室 three small bays (7.52 m), a 硬山; rock masses on S01's strokes.
- **The walls (B lines, C form):** white with a grey tiled coping, 3.0 m (2.7 m round the court), the Suzhou garden's manner (C); doorways where 虹桥 lands and into the court.
- **Level and clear:** `level` over the west garden, the court and the east garden (no generated hill of Round 10 inside: H2039 and H2048 stood there); the court before 纳景堂 and the court of 清淑斋 `clear`; `rockeries` CC13 (Round 12's rockeries there give way).

## Match check

Two photographs fitted with `tools/plate_overlay.py fit --object CC13 --sheets research/scenes/CC13-shizi-lin` (`plate_keypoints.csv`, `photo_viewpoints.csv`; results in `plate_fit.csv`, `plate_cameras.json`). Both show arches re-erected on their sites in 2013: they test the arches' form, not their places.

- **P0415 (虹桥):** 9 points (the near face's jambs at the water, springings, the ring's crown inside and out, its feet, and the west jamb's foot at the far face), **14.3 px rms, 0.08 m at the object** (median 0.06 m, max 0.13 m); the camera 0.9 m from its prior on the rockery's bank, a 64° lens. The first fit, with S01's proportions (span 2.4 m on 0.55 m jambs), gave 25 px with the camera collapsed onto the arch's face (all eight points on one plane); with the far jamb's point added, 44.7 px with the lens pulled to 252 px. A sweep (`CC13_HQ`): span 2.4 / jambs 0.55: 44.7 px; 1.8 / 0.55: 38.4; 1.6 / 0.6 (width 2.0): 32.8; 2.0 / 0.9: 25.4; 1.6 / 0.9: 17.6; 1.8 / 1.0: 18.8; 1.8 / 1.2: 16.9; 2.0 / 1.2: 19.9; 1.6 / 1.0, ring 0.32: 16.2; **1.6 / 1.1: 14.3**; 1.4 / 1.0: 12.7 (with sane lenses, 1,000-1,080 px). The proportion is settled (jambs about 0.7 of the span, the ring about 0.18), the absolute size rests on the assumed lens (Q308).
- **P0416 (水门):** 8 points on the ring's outer and inner edges (crown, haunches, the south leg's feet), **19.3 px rms, 0.16 m** (median 0.10 m, max 0.32 m: the south leg's outer foot); the camera's eye given as the bank's height plus 1.6 m (its prior stands over the lake's lobe, where the walk surface is the lake's bed: left at 1.6 m above that, the fit sank the camera under the water with the principal point 249 px off). A sweep (`CC13_SM`) of the span from 2.4 to 3.4 m gives 18.2-21.2 px: the photograph does not settle the span (Q309); the model keeps the channel's 3.0 m.
- **Not fitted:** P0500 and P0417 (the gate's ring from inside, 2013 and 2022: its edges against the snow and the soffit are not readable to a few pixels); they stand beside the model's view from inside in `screenshots/r29/`.

Overlays: `screenshots/r29/overlay_P0415_CC13_all_*`, `overlay_P0416_CC13_all_*` (both pictures are free).

## Iteration log

1. **The water first.** Round 1 left the pool land: its wash was not closed. Traced as RM004 (W0368) with its arm and channel, joined to the lake's lobe at the water gate so that it takes the lake's level; the stream of the east garden as RM005 (W0369), its own level. The generated hills after H2035 renumbered by one (one free-land knoll in the pool's place), as they did in Round 28.
2. **First run** (40,694 triangles): the layout from S01, the halls by the kit, the arches with S01's proportions; rock blocks of 文源阁's kind.
3. **The rocks read as crystal shards** on the close views (tall blocks with a fan to a point): the cap is now shallow and the masses are stacked in tiers no taller than their width, each set off the one below.
4. **P0415:** the arch's proportions swept to 1.6 m on 1.1 m jambs (above); the deck runs level over the whole arch as the photograph shows, the steps beyond.
5. **P0416:** its camera sank under the water from a prior over the lake's lobe; the eye is now given above the bank.
6. **The rockery too low and too even** for a garden famous for its stones (獅林以石勝): raised to 1.4-3.4 m with a 5.2 m summit and sixteen standing peaks; the court before 纳景堂 lowered from a 0.25 m slab to a step.

## Joints and ways

- **Ground joints** (`tools/check_models.py`): 118 (walls' feet, platforms' corners, the arches' and the water gate's feet, the bridges' ends, flights' feet, the terraces); the highest 0.16 m above the ground, the deepest 0.20 m in. Before the fix, 清閟阁's four platform corners were measured at the pool's bed (2.0-2.9 m in); each corner now stands on its own ground.
- **Ways:** 5 of Round 9 end at the model's boxes, 0 more than 0.5 m from an entry. The reach way to the water gate's box (RC-CC13-01) ended 8.1 m from any entry; the gate now has a stair of rough stone up to its walk and a few flagstones from the way's end to the stair's foot.
- **Joints on the decks** (`report.json` `deck_joints`): 4, every one at 0.00 m (before: 藤架's north end measured on the bridge instead of the porch, 1.53 m; 清淑斋's west door on its hall's platform, -0.46 m; 占峰亭's stair head over 横碧轩's platform, 4.23 m: the entry moved, the door moved south, the stair turned to come up from the south-west).
- **Footprints:** platforms, flights, walls, the bridges, the stairs, the rock masses drawn in by 1.2 m. **Decks:** the bridges, the court before 纳景堂, the summit pads, 探真书屋's court. **Level:** the west garden, the court of 清淑斋, the east garden. **Clear:** the court before 纳景堂, the court of 清淑斋.

## Where the model and the sources disagree

- **The pool's channel (Q306):** S01 draws rocks in the band the model makes water.
- **Which hall is which (Q307):** the model's names for S01's unnamed halls are readings.
- **The rainbow bridge's size (Q308)** and **the water gate's span and the slab's place (Q309).**
- **清閟阁 (Q310):** 清閟小閣 in the preface against S01's seven-bay range.
- **占峰亭 (Q311):** the east garden's mountain sign against the west rockery's summit.
- **S01's halls of four cells** (纳景堂, 横碧轩): drawn with three bays (an odd count, Qing practice; C).
