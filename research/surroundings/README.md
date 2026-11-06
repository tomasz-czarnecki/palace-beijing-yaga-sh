# Surroundings

What stood and ran round the three gardens in 1860, Round 20. The layer is `layers/surroundings_1860` (WGS84), written by `scripts/surroundings1860.py` from `surroundings/features.csv` and `surroundings/geometry.geojson`. The view draws it from `site/reconstruction/data/around_1860.json` with `site/reconstruction/around3d.js`. The public page is `site/around/` (`scripts/around_page.py`, text in `surroundings/about.json`). The check is `tools/check_surroundings.py`, which writes `surroundings/check.json`.

## Extent

- **The ring:** about 2 km beyond the walls, the box 39.972-40.035 N, 116.232-116.345 E. It reaches 玉泉山 in the west, the 清河 in the north, the railway line of 1909 in the east and 海淀 and 巴沟 in the south.
- **Beyond the ring:** 静宜园 on 香山, the Western Hills, 乐善园 by 高梁桥, the 长河 below 绣漪桥, 健锐营 and 外火器营. These are one-line entries in this README, a label in the view, or nothing.
- **The ground:** the ring is drawn at 20 m (`scripts/ground_outer1860.py`). Beyond it a backdrop of 200 m cells from the DEM reaches the Western Hills.

## How it was made

Four readers worked on the round: gardens, water, camps and maps. Their rows, sources and notes stay in scratch (`palace_r20_surroundings_*`). `docs/rounds/common/palace_r20_merge.py` merged them once into the sheet, and from Round 20 on the sheet is edited by hand.

- **Ids:** OW001-OW124, in the order of the merge table. They are never renumbered.
- **The rows S01 draws outside the walls** (garden 'outside the walls' in `buildings.csv`, the Z- ids) are carried into the layer under their own ids. OW051-OW054 are the four labelled ones (船坞, 黄木厂, ?家木, ?旗房). Their boxes and pages stay those of `buildings.csv`.
- **Two grades:**
  - `confidence` is for the object: that it was there and what it was. A means a Qing text or an eyewitness of 1860 names it.
  - `pos_confidence` is for where it stood. A position taken from a surviving village name stands for today's village, so it is C. A map read with a fit, a surviving structure or a plan row is B.
  - The view tints by the weaker of the two.
- **`assumed`:** true where the place itself is a guess. Every house, barrack row and hall the massing generates is assumed, whatever the grade of its object.

## Counts (run)

| | |
|---|---|
| Objects | 138: 124 OW and 14 Z- rows. 77 A, 42 B, 19 C as objects; positions 42 B, 96 C; 55 marked assumed |
| By kind | 27 villages, 1 town, 20 temples, 15 neighbouring gardens, 11 banner camps, 3 offices, 4 storehouses, 8 canals, 1 river, 7 sluices, 7 bridges, 6 roads, 4 paddies, 2 lakes, 1 spring, 2 far hills, 19 other (the drill ground, the review tower, the Z- rows, the lines of October 1860) |
| Massing | 4,233 blocks: 1,165 double barrack rows, 450 houses of 海淀, 660 village houses, 872 wall pieces, 59 halls of temples, gardens and offices as plain blocks, 7 explicit parts; 3 office halls drawn as simple halls with a platform and roof; 56 tinted patches; 15 bands for roads and water; 2 lakes; 93 labels. 10 generated blocks a lake's outline crossed were dropped. The view draws 240,308 triangles for all of it |
| Joins | five, all 0 m after the snap: the inflow canal at the sluice G30 (0.51 m before), the outflow at G20 (0.40 m), the causeway at the end of the stone road YMC-001 (26.5 m) and on the east-west road, the stone road from the city on the east-west road |

The full numbers are in `surroundings/report.json` (the generator) and `surroundings/check.json` (the check).

## The neighbouring gardens

- **清漪园 Qingyi Yuan (OW001):**
  - It lay "西二里许" from 圆明园 (S05 j84). It was laid out from 1750 round the lake, which was dug and enlarged in 1749-50 (S02 p.109), and round 万寿山.
  - In 1860 it had no wall round its lake. The wall came with the Guangxu work (S02 p.199).
  - Looted from 6 October, burned 18-19 October 1860 by British troops (S02 pp.188-189; S1207 quoting the memorials).
  - **Outline:** today's 颐和园 boundary (OSM way 29228773, 301 ha, run): B for the extent of 1860 at best. The view draws the garden's ground only within 350 m of the lake, since today's outline runs a corridor west towards 玉泉山.
  - **Massing:** four C blocks on 万寿山's south slope for the temple group and its tower, and the 智慧海 on the top. Their places are read off today's summit, not surveyed.
  - **Pictures:** Beato's photographs of October 1860, P0180-P0182 (NGA, CC0), and P0823 (十七孔桥, attributed to Beato, LACMA, public domain).
- **The lake (OW016, `water_1860` W0901):**
  - The outline is today's water inside today's 颐和园 boundary. 团城湖 is left out, as a modern reservoir (Q264).
  - Its level is the DEM's median inside the outline, which reads today's water surface.
- **静明园 Jingming Yuan (OW002):**
  - The hill and its springs; it burned 18-19 October 1860 (S02).
  - The outline is today's wood on the hill (C), with a wall (the AMS sheet draws one, S20) and the pagoda 玉峰塔 as one block (C height).
  - Picture: P0824.
- **畅春园 Changchun Yuan (OW003):**
  - Its wall was 1,060 丈 (about 3.39 km, S05 j76).
  - It had decayed by the Daoguang reign, and its timber was pulled down from 1856. 明善's memorial lists 恩佑寺, 恩慕寺 and 清溪书屋 as burned (S1207).
  - **Outline (C):** the wall line of Song 2021 (S685, CC BY), anchored on the surviving gate of 恩佑寺 and scaled to the 1,060 丈: 65.6 ha (run).
  - Malone's sketch (S02 p.22) gives about 970 x 730 m, zh.wikipedia 1000 x 600 m (Q265).
- **西花园 (OW004):** west of 畅春园; C polygon of 34.4 ha.
- **The princely gardens:**
  - 蔚秀园 (OW008, 奕譞), 朗润园 (OW010, 奕䜣), 淑春园 (OW009, 睿亲王 仁寿), 鸣鹤园 (OW012, 绵愉), 镜春园 (OW011, crown after 1860), 承泽园 (OW007, 额驸 景寿), 熙春园 / 清华园 (OW014, 奕誴, spared in 1860), 近春园 (OW015). Holders are from 何瑜 2021 and the universities' pages (`sources.md`, Round 20).
  - Positions are points or today's campus outlines, mostly C. Whether 近春园, 淑春园 and 鸣鹤园 burned in 1860 or were pulled down later is open (Q266).
- **The officials' houses:**
  - 集贤院 (OW013, the old 勺园): Parkes and about thirty other prisoners were held there in September 1860.
  - 澄怀园 (OW006, the Hanlin academicians' garden): placed on the plot S01 labels 翰林花园, QC60 (Q267). Its 近光楼 and duty rooms burned in 1860 (S1207).
- **耕织图 (OW005):** inside 清漪园, west of 玉带桥; a C point.
- **Not placed:** 静宜园 (beyond the ring), 乐善园, 自得园, 一亩园 (a place name only), 春熙院, 泉宗庙 (its wall was 394 丈, by 万泉庄, south of the ring) and the 高水湖.

## The water

- **The feed:**
  - Water from 玉泉山 ran by the 玉河 (OW019, along today's 北长河, C) and the 金河 (OW020) to 昆明湖.
  - From 1764 the 二龙闸 (OW033, B, placed C) let 昆明湖's water east (OW023).
  - The springs of 万泉庄 sent the 万泉河 (OW022) north past 畅春园, through its north-west 五空闸 (OW032, C).
  - The two feeds met at the 马厂 and entered Yuanming Yuan by the one-opening sluice east of 藻园门 (OW024; S05 j80:7a; S348 / S1003).
- **The inflow:** confirmed at G30 (B; it was already there as YM43-01). The canal OW024 ends at it, snapped: 0 m.
- **The outflow:**
  - Through the gardens to the east and out by the 七孔闸 to the 清河 (S05 j80:7b, j83:3b). The 七孔闸 is G20 / CC19 (C). The outflow canal OW026 starts there, 0 m.
  - 贾 2024 (S348, abstract only) names four outlets on the east, three of them not placed (Q268). The text says the 七孔闸 had seven openings, S01 draws five.
- **The 清河 (OW027):** today's course from 青龙桥, B as a line.
- **The 长河 (OW021):** from 绣漪桥 south, as the AMS sheet draws it (S20).
- **The sluices on our walls** (G30, G14, G32, G20: OW028-OW031) have no block of their own: the walls carry them.
- **Widths:** none is sourced. Canals are drawn 6-12 m, the 清河 15 m, the 长河 18 m (C).
- **Not placed:** the 扇面湖 Fan Lakes before the gate (dug 1763, S02 p.68; no outline found, Q272), the 丹棱沜, the river outside the west wall (j84:23a), 广源闸, 高梁桥 and the second outlets.

## The roads and 海淀

- **The stone road 圆明园石道 (OW044):**
  - From 西直门, 20 li (S05 j98:1a). Paved before 1721, repaired in 1724.
  - "廣可三間", about three bays wide, in the Korean envoy's account of 1790. That is read as about 10 m (C, Q279).
  - Drawn along today's 中关村大街 and 颐和园路 through the old town. It agrees within 150 m with the AMS sheet's main road (S20).
- **The causeway between the Fan Lakes (OW043):** from the east-west road to the stone road S01 draws before the gate (YMC-001), snapped from 26.5 m.
- **Other roads:**
  - The east-west road north of 海淀 (OW042); the stone road and the causeway end on it.
  - The road west past 清漪园 to 青龙桥 (OW045), described as paved in 1860 (S241, S240).
  - The road along the west wall (OW046, C) and 苏州街 (OW047).
- **海淀 Haidian (OW081):**
  - The market town where officials serving at the court lodged; it had no wall.
  - The outline is the built-up block of the AMS sheet of 1944, traced by eye. 450 houses are generated in it (C; no house count is known).
  - The French marched through it on 6 October 1860 (S245, S241). No source read says the allies burned it (Q276).

## The guard, the offices and the camps

- **The camps:**
  - The 圆明园八旗护军营 was set up in 1724: 1,250 间 per banner, 1,550 after 1747, and 504 间 for the three bondservant banners (S1237, 八旗通志 j116). 日下旧闻考 j99-100 and Malone's sketch (S02 p.54) agree camp by camp.
  - Places are today's village names (C): 镶黄 (OW110) west and 正白 (OW109) east of 树村, 正黄 (OW111) at 萧家河, 正红 (OW112) at 安河桥, 镶红 (OW113) west of 颐和园 (the text's 東四木村 read as 董四墓, C), the large 镶白 camp (OW114) north-east of 长春园 and its small camp (OW115: east in the text, south in Malone and today, Q273), 正蓝 (OW116) at 蓝旗营, 包衣三旗 (OW117) at 三旗.
  - 镶蓝 stood at 蓝靛厂, south of the ring (not placed).
- **What one looked like:** low houses inside a wall eight feet high with a wooden gate (Swinhoe on 6 October 1860, S241 p.286; which camp is C, Q275). No plan of a camp is known (Q274).
- **How the view draws a camp:** a walled rectangle with rows of double houses of ten bays. The number comes from the count of rooms: 14 rows of 11, 154 double houses of ten 间, for 1,540 间. The layout is generated, C.
- **Offices:**
  - The guard's seal office (OW048) beside the 红桥 canal (S05 j99:26b), drawn with the hall kit (C).
  - 东公所 (OW049).
  - The granary 丰益仓 south of 安河桥 (OW050).
  - The drill ground 西厂 (OW055) and its review tower 阅武楼 (OW056: a terrace of 88 ft square and 6 ft high, S02 p.107; burned 1860, S1207).
- **The offices in front of 大宫门:** already in the model of Round 19 (YM41). They are not repeated here.

## Villages, temples, fields

- **Villages:**
  - From the Qing texts, 27 in all: 挂甲屯, 成府, 水磨, 树村, 萧家河, 大有庄, 青龙桥, 骚子营, 二河闸, 卓房, 东柳, 巴沟, 皇庄, 六郎庄 (S05 j99-100).
  - From the maps of about 1886 and 1944 only (C for 1860), a dozen more, some with no Chinese name read.
  - Each is a cluster of 15-40 generated houses within 80 m of today's name. The sizes are not recorded.
- **Temples:** 20 in all.
  - Placed on a surviving building: 一亩园娘娘庙, 延福禅林, 黄庄双关帝庙, 恩佑寺's gate.
  - Placed on a place name: the others. Each is a small walled court with one to four halls (C).
- **Paddies:**
  - Between 昆明湖 and 海淀: the AMS sheet's paddy symbol, outlined (B for 1944; the 1864 plan writes 'Rizières' there, S22).
  - Three paddies the texts name: at 万泉庄, east of 长春园 below the 七孔闸, by 功德寺. Their extents are circles (C).
  - They are in `fields_1860` as FD0901-FD0904 (`outside: true`).
- **The rest of the plain** was dry farmland (the 1864 plan's 'plaines cultivées'). The ground's tint stands for it.

## October 1860

The readers' account, quoted in their notes from the public-domain texts:

- **6 October:** the French, with Pattle's British cavalry, came from the earthen rampart north of the city, through 海淀 on the paved road, over the 红桥 and between the two lakes to the main gate. The cavalry went round the town to the east (S245 p.226, S241 pp.284-288, S240 pp.224-229). The French camped on the square before the gate (OW124). The looting began that day.
- **The Qing side:** the 清实录 records the attack on the 22nd day of the 8th month and that the streets burned (S207).
- **18-19 October:** British troops under Michel burned the gardens on Elgin's order, and with them 清漪园, 静明园, 静宜园 and buildings outside our walls (S02 pp.187-189; S1207). The French refused.
- **In the layer:** the two lines of 6 October are there (OW122, OW123, generalised, C). They are not drawn in the view.

## The ground beyond the walls

See `terrain/README.md` (section "Round 20: beyond the walls") and `terrain/ground_outer_report.json`.

## Where the sources disagree, what is unknown

Q264-Q280 in `questions.md`. The wish rows of Round 20 are in `wishlist.md`. The largest unknowns:

- the outline of any camp, village or princely garden;
- the width of any road;
- three of the eastern sluices;
- the Fan Lakes;
- any free large-scale map north of 40.00 N: the AMS sheet 16/2220 is not at the library, and the map of about 1886 reads to ±0.3-0.8 km.

## Maps read (Round 20)

`research/raw/around/maps/`, fits in scratch (`palace_r20_surroundings_georef_*.json`).

| Map | What it covers | Points | Fit |
|---|---|---|---|
| AMS 1:50,000 Peking sheet 16/2200, 1944 (S20, public domain) | 39°49'-40°00' N | 10 | 95 m rms, max 167 m, leave-one-out 145 m |
| 北京城郊图, about 1886 (Library of Congress, S27) | the whole ring | 8 | 226 m rms, max 427 m |
| Le Tour du monde 1864 (S22) | a sketch of 1860 | 7 | 427 m rms: only what lies where |
