# The ways of 1860: roads, paths, galleries, landings and boat routes

Round 9 (2026-11-05). Tomasz asked: "Do we have any information about roads and walking paths?" Before this round the answer was only bridges, gates, water and today's OSM paths. This folder holds what the sources say, the traced lines, and how they became the layers `paths_1860`, `landings_1860` and `routes_1860`. Field lists are in `research/README.md`; the method for the next site is in `docs/METHOD.md`.

Marks below: **verified** (seen on the page, the plan or the leaf), **assumed** (our inference), **unknown** (not found). Every figure comes from a run of `scripts/paths1860.py` or `tools/check_paths.py` on the repo.

## What the sources say

### Qing plans

- **The base plan S01** (Malone's "Official Map" or his tracing, B until Q2 is settled). Verified by five readers on crops, region by region (`traces.csv`, their notes in `docs/rounds/common/palace_r9_notes/`): it draws halls as bay rows, court walls as single lines, gates as short bay rows or gaps in a wall, **galleries 游廊** as narrow one-bay rows joining halls (the long rows at 含经堂, the curved arms of 谐奇趣, the octagonal ring at 思永斋), **steps** as bracket marks (三出 flights at 安佑宫, the double stairs of 海晏堂 and 方外观), **bridges** as short strips with flared ends, **dikes and causeways** as strips of land between two waters. It draws a few **roads** outright: the double line of the 辇道 south of 大宫门 (about 5 m wide) meeting an east-west road labelled **石路**; the same at 绮春园宫门; the street of 舍卫城 (two lines about 3 m apart); the shop lane of 铺面房; the riding track labelled **马道** at 山高水长 and the open ground **撒马道** before 含晖楼. Dotted lines at 文源阁, 杏花春馆, 紫碧山房, 泽兰堂 and in the maze 黄花阵 read as paths (they could be tree rows: a doubt each reader noted). **Paths across open courts are not drawn**: the court and its axis are. One boat dock is labelled 船坞 north of 洞天深处; S01 draws no 码头 on 福海.
- **Yangshi Lei 样式雷 ground plans** (research-only, mostly unseen; remains worker): plans that draw 甬道, 游廊, 踏跺 and 码头 exist, the best leads 如园地盘全样 (样385-0015), 长春园全图准底 (1835-58) and the Guimet plan (about 1858-60, E0551); no 甬道 or 码头 width in 丈尺 was found online. The 1835 presentation plan of 泽兰堂 records removing a gallery (E0188). Wishlist.
- **The 1920s and 1933 plans:** the 1933 survey of the ruins (S15, 1:2,000) draws hills, water, bridges and buildings by the press reports; whether it draws paths is **unknown** (no scan). The Princeton 1920s plan is S01 itself.

### The Forty Scenes leaves (1744) and the Xiyang Lou plates (1780s)

All forty leaves P0001-P0040 and the twenty plates P0041-P0060 were read for circulation (`album.csv`, 364 rows: 174 high, 139 medium, 51 low; verified on the images, ties to halls assumed by name and position). What they draw: paved ways in courts as light stone strips (正大光明's court axis, 洞天深处's grid of lanes), covered galleries joining halls, steps to halls and up hills, red-railed bridges, landings with white steps into the water, shore paths, dikes (夹镜鸣琴, 多稼如云). How a scene was reached, where the leaf shows it: **by boat only** 蓬岛瑶台 (white landing steps rise from 福海 into the front gate); **by boat and by land** 方壶胜境, 上下天光, 四宜书屋 (two roofed boats moored by a boat house: the album's only clear drawing of moored boats), 澡身浴德, 平湖秋月, 澹泊宁静, 万方安和; **by land** 正大光明 (road, one bridge, the gate, the paved axis) and most others, over a bridge in the foreground or along a shore path. The plates show the Xiyang Lou's east-west axis through 养雀笼 and the gates of 线法山, and the north-south axis 观水法 - 大水法 - 远瀛观. Limits: bird's-eye paintings, not plans; trees hide where galleries end; paths on lawns are mostly not drawn (山高水长, 澹泊宁静). A traced line that a leaf shows (same scene, same kind, an end in common, reading high or medium) is graded A: 75 lines.

### Texts

From `research/evidence/catalog.csv`, the Round 7 text copies and S360 read in full (`texts.csv`, 140 rows: 119 verified, 16 assumed, 4 unknown). The Chinese terms and where each is attested are rows TX-115 to TX-131; 爬山廊, 抄手游廊, 垂花门, 踏跺 and 御路 occur in no text searched (the dig of 如园 uses 垂带踏跺, 抄手踏跺, 云步踏跺).
- **The emperor's daily way.** The daily audience 御园听政 was held at 勤政殿 (养吉斋丛录 j5, S202; 勤政殿诗 with preface, 日下旧闻考 j80:18a, S05; S360), summer in the hall, spring and autumn in its 东书房 (竹叶亭杂记 j1, S211); the great audiences at 正大光明. **No Qing text says how he crossed the 前湖** from 九洲清晏 (unknown). The 1860 witnesses walked: Swinhoe "a pebbled path leading over a bridge… a semicircular sweep of half the water" (S241), M'Ghee the lake "bridged at each end" (S242). In 1856 the emperor came "从内乘船" by boat to 山高水长 (蕉轩随录, S210). 日下旧闻考 calls both the water before 大宫门 and the lake behind 正大光明 前湖 (j80:7b, j80:20b).
- **The processional way.** "大宫門前輦道東西皆有湖" (j80:7b): the carriage road before the gate, between waters. 大宫门 has 朝房 of five bays each side; 出入贤良门 stands behind three stone bridges over a moon-shaped stream (驾石桥三), memorials in by the east 罩门, the kitchen eunuchs by the west (j80:9a-b); the central bridge's hump was flattened in 1839 (S211). At ceremonies the ranks filled the courts in order, the highest in the hall's galleries (S360). In mourning in 1797 the emperor came in by the west gate, not 出入贤良门 (S211).
- **Boats.** 蓬岛瑶台 was reached only by boat, landing at 镜中阁, its south gate (S360, 1772). The dragon-boat races of 端午 on 福海 were watched from 望瀛洲 (Qianlong; the empress dowager at 蓬岛瑶台), under Jiaqing from 澄虚榭 (S202 j14, S201, S205). Boats named: 卧游书室, 平安月镜居, 如坐天上 (1856), 安济航, 浮汉槎. Routes "from X by boat to Y": 流香渚 to 如园 (1856), 狮子林 to 玉玲珑馆, 云锦墅 to 蓬岛瑶台, 圆明园南湖 to 凤麟洲 and others (S360). Nine docks 船坞 (S42).
- **The 1856 day** (玉明, 侍游御园记, in 蕉轩随录, S210; E1524): officials in by 西南门 to 山高水长; the emperor by boat, then all on horseback: 藻园 - 汇芳书院 - 紫碧山房 - 鱼跃鸢飞 - 蕊珠宫门 - 黄花磴 (tea) - 海晏堂 - 转马台 - a small corner gate - 狮子林 (a meal) - 宝相寺 - 法慧寺 - 谐奇趣 - 明春门 - the landing at 雷峰夕照 - the boat 如在天上 on 福海 - a landing (name garbled) - 丽春门 - along the east wall past 敷春堂 - 西大堤 and 汉城关 - dismount at 含晖楼. They rode: the main ways were wide enough for horses. 转马台 is probably 线法山's hill (assumed).
- **Widths.** No text gives the width of a way, a gallery or a dike (unknown). Bays: 淳化轩's galleries 12 楹 each side (日下旧闻考), 谐奇趣's curved galleries nine bays; Attiret's boat 24 ft wide.

### Today's park

`tools/osm_paths.py` judged every OSM way of the kinds walked in the park inside the walls (`osm_judged.csv`): 452 ways, 49.4 km. **Modern**: 184 ways, 19.6 km, a quarter or more of their length over the water of 1860 (fill) or through a hall. **Plausibly on an old alignment**: 26 ways, 1.1 km, within 5 m of an A or B way traced here for 60% of their length, or along a shore or on a dike of 1860 for 70%. **Undecided**: 242 ways, 28.7 km. Plausible means only that it lies where a way lay or could lie, never that it is that way: **no OSM line went into `paths_1860`**.

### Archaeology

`remains.csv`, 64 rows. No dig has published the width of a path or a 甬道 (unknown; the reports are books or paywalled: S143, S990, S316). What is known:
- **如园 延清堂** (dug 2016-17, S362, read in full): the landing 码头 north of the north terrace, 5.1 × 3.35 m, 1.1 m below it, the main way in under Daoguang and Xianfeng; front steps 垂带踏跺 4.6 × 2.1 m, four treads 0.16 × 0.416 m; side steps on both terraces; aprons of thin stone slabs; the garden roads reddened by the fire. Grades CCX-062 and CCX-063 A.
- **长春园宫门** (dug 2001-04, S316, E0007): the axis screen wall - 宫门 - 牌楼门 - 澹怀堂 - 众乐亭, 220 m, and stone steps into the lake north of 众乐亭, read as the imperial landing. Grades CCX-034 to CCX-043 A.
- **文源阁** (2024, S134): flagstone paths with Y-forks not on any plan, a 御路, steps; which traced line they are is unknown, so the grade stays B.
- Also: 紫碧山房 a semicircular landing and a stone bridge (S132); 澹泊宁静 steps and pebble aprons (S137); 舍卫城 a processional road through the south gate (S46); 大宫门 roads, a square and the 金水桥 (2012-18, no widths found); 正觉寺 a road base before the gate (S155); bridge abutments of granite 条石 at 南大桥, 如意桥, 碧澜桥, 鸣玉溪桥, at 万方安和 and 碧桐书院, and timber piles elsewhere (S992). Malone saw circular paths up 线法山 and paved paths at the Xiyang Lou (S02 pp.142-159).

## How the layers were made

1. **Traced** (`traces.csv`, the readers' lines in plan pixels): through the plan transform in use (Round 8) into scene metres; each end snapped to what it joins. Ends: median 2.4 m, 90% 11.4 m, worst 25.5 m from what they meet before snapping (1031 ends); a misread id more than 25 m off (40 m on the Xiyang Lou, whose boxes stand on the ruins) is dropped and the end joins the nearest thing.
2. **Doors:** the mid-point of a box's side, 0.6 m out, the one with the least detour, the front preferred. Gates, terraces, courts and the halls a garden wall stops at are walked through.
3. **Nothing floats or crosses:** a line through a box, a wall or water is rerouted round it on a 0.75 m grid, kept near the trace (116 lines, at most 36.9 m off). What cannot be is listed in `exceptions.csv` with the reason.
4. **Landings** to the shore, 0.3 m inside the land (median 2.2 m moved); 17 stand more than 1 m from the traced water, where the water layer lacks a pond (Q191).
5. **Bridges:** each end with no way within 1 m gets a C approach to the nearest way, door or gate within 60 m; 66 of 73 bridges are reached at both ends, the rest have the reason in `bridge_ends.csv`. BR006 and BR047 were read along their decks in Round 1: their spans now cross the stream and the moat (`research/plan/readings/`). The readers' candidate bridges not on the layer are Q193.
6. **Minimal C links:** in each compound a hall no way reaches gets one line from its door to the nearest way, or to the compound's entry (`RC-`); a traced end that meets nothing gets one to the nearest way within 40 m (`DL-`); a route whose waypoints the network does not join gets one where the pieces come nearest (`RL-`). All `assumed: true`, basis `reach`.
7. **Routes** (`routes.csv`): the shortest way through the network between waypoints chosen from the sources, A and B ways preferred, a hall walked through by its doors.

## The numbers (`tools/check_paths.py`)

1348 lines, 34.1 km: 527 traced (18.8 km), 62 bridge approaches, 759 links (747 `RC-` and `RL-`, 12 `DL-`). A 85 (2.4 km: 75 from a leaf, 10 from a dig), B 175 (6.3 km), C 1088 (25.4 km; 267 traced and inferred, 821 links). Landings 74 and docks 11 (A 6, B 22, C 57). 137 scenes and compounds have traced ways. After snapping, every end of an A or B line meets something within 0.5 m except the six in `exceptions.csv`.

## Assumed, and what the sources could not tell

- **Assumed (C):** every court axis the plan does not draw (the 甬道 between a gate and the hall in line with it), every reach link, the line of every boat route on the water, the order of the 福海 tour, the 如意桥 crossing on the emperor's way, every width without a drawn one (`WIDTH` in `scripts/paths1860.py`), every surface (`SURFACE`, except where a dig is cited).
- **Not known:** how the emperor crossed the 前湖 (Q194); the width of any 甬道 (Q196); the course of the maze's path (the boxes' maze walls stand for the plan, Q195); whether the 1933 survey draws paths; the third and second bridges of 出入贤良门 (one drawn, three in the text, Q193).
- **Wishlist:** `research/wishlist.md`, the Round 9 rows.

## Files

| File | What | Written by |
|---|---|---|
| `traces.csv` | the plan readers' lines, one per way, landing or dock | Round 9 readers, then by hand |
| `album.csv` | the leaves and plates read for circulation | Round 9, then by hand |
| `texts.csv` | what the texts say of routes, galleries, boats, landings, terms | Round 9, then by hand |
| `remains.csv` | digs, surveys and Qing plans of paths | Round 9, then by hand |
| `grades.csv` | a dig or a text that raises a trace or adds a source | hand |
| `routes.csv` | the named tours and axes as waypoints and stops | hand |
| `exceptions.csv` | an A or B line that may cross or end in the air, with the reason | hand |
| `bridge_ends.csv`, `dangling.csv`, `unreached.csv` | what has no way, and why | `scripts/paths1860.py` |
| `osm_judged.csv` | today's park paths, judged | `tools/osm_paths.py` |

How they were first merged from the workers' files: `docs/rounds/common/palace_r9_merge.py`, a record.
