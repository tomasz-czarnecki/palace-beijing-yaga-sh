# Typology for the boxes

`scripts/build_r1.py` already applies this: it gives every footprint a `hall_class`, and takes stated sizes from `by_name` and `xiyang_lou` in `params.json`. Three `by_name` entries are not bound to a row: 同乐园南楼, 淳化轩戏台, 吕祖亭.

Defaults for the box-and-roof round. Numbers are in `params.json`. Every number here comes from a source below or from a script run: `scripts/typology_rules.py` (rule arithmetic, writes `rules_out.json`) and `scripts/typology_scale_check.py` (plan scale, writes `scale_check.json`).

**Unit:** 1 营造尺 chi = 0.32 m (S105, and the conversions in S111, S113, S114 use it).

## 1. How to use this

1. A stated size in `by_name` wins.
2. Otherwise measure the hall on S01 and convert with the **hall scale**: frontage = px / 4.2, depth = px / 3.3. Count the bays on S01; the count is reliable.
3. Take heights, roof and bay split from the class.
4. Place buildings with the **ground scale**, 4.77 px/m. Do not use 3.9 px/m for anything except a rough check.

## 2. Scale check of S01

**The stated 1:1300 (3.94 px/m, S02 p.231) does not hold for the ground.** An affine fit on 8 surviving features gives **4.77 px/m (x 4.785, y 4.764), about 1:1073, rotated 7.85 degrees, RMS 17.9 m** (S01 against S03). This is a quick check on 8 points with polygon centroids and one OSM point. The georeference has replaced it: 4.77 px/m and 7.2 degrees on 111 points, locally 3.7 to 5.55 px/m (`research/georef/princeton-1920s.json`).

Halls are drawn smaller than the ground scale, and depth much smaller than frontage.

| Hall | Plan x / y | Axis | px | Stated m | px/m | What the metres are | Source |
|---|---|---|---|---|---|---|---|
| 正大光明殿 Zhengda Guangming | x 3230.6-3382 | frontage | 151.4 | 39.32 | 3.85 | foundation, 129 ft, measured by Malone | S02 p.75 |
| 正大光明殿 月台 | x about 3234-3385 | frontage | 151 | 38.40 | 3.93 | 面阔 12丈 | S119 |
| 大宫门 Da Gongmen | x 3247.9-3346.4 | frontage | 98.5 | 21.57 | 4.57 | 台基 | S102 |
| 观澜堂 Guanlan Tang | x 8107.9-8205.6 | frontage | 97.7 | 23.36 | 4.18 | bays and porches | S111 |
| 文源阁 Wenyuan Ge | x 3473.5-3597.4 | frontage | 123.8 | 22.72 | 5.45 | 丈尺册 | S105 |
| 藏密楼 Cangmi Lou | x 7144-7186.5 | frontage | 42.6 | 8.96 | 4.75 | three bays | S111 |
| 舍卫城南门 墩台 | x 4585.2-4643.5 | frontage | 58.3 | 15.40 | 3.79 | excavated | S107 |
| 正大光明殿 | y 5415-5472.5 | depth | 57.5 | 19.20 | 2.99 | foundation, 63 ft | S02 p.75 |
| 正大光明殿 月台 | y 5472-5547 | depth | 74.5 | 14.82 | 5.03 | 深 4丈6尺3寸 | S119 |
| 大宫门 | y 5920.9-5947.4 | depth | 26.5 | 11.33 | 2.34 | 台基 | S102 |
| 观澜堂 | y 3682.9-3765.5 | depth | 82.6 | 26.49 | 3.12 | 3 rolls and porches | S111 |
| 文源阁 | y 1445.9-1502 | depth | 56.1 | 14.72 | 3.81 | 丈尺册 | S105 |
| 松风阁 Songfeng Ge | y 1576.5-1617 | depth | 40.5 | 6.40 | 6.33 | core and porches | S111 |
| 万字房 arm | y 3274-3297.5 | depth | 23.5 | 7.04 | 3.34 | room and porches | S113 |
| 舍卫城南门 墩台 | y 2106.5-2148 | depth | 41.5 | 12.60 | 3.29 | excavated | S107 |

Frontage median **4.18** (3.79-5.45, n=7). Depth median **3.31** (2.34-6.33, n=8). Ground 4.77. Single-feature checks: 海晏堂 central strip 130 px against the 锡海 tank 27.36 m = 4.75 (S109, identification inferred); 后湖 4.72 E-W and 4.27 N-S; 方河 4.34 and 5.62 (S03).

**How faithful is the bay grid?**
- **Bay counts are right.** 正大光明殿 7 + porch (S02), 大宫门 5 (S102), 观澜堂 5 x 3 rolls with the east 围房 (S111), 文源阁 6 with the narrow west bay visible, 安佑宫 9 (S122), 澹怀堂 5. S01 and the excavation report as quoted in S112 agree on five for 澹怀堂; S06's 九楹 is wrong or refers to something else.
- **Single bay widths are not.** They wander by up to 30% and are not symmetrical. 正大光明殿: 13.9, 20.6, 22.9, 22.5, 20.5, 19.9, 17.1 px. The central bay is usually among the widest but not always.
- **S01 repeats drawing errors.** At 田字房 it draws wells of 43.5 px and rooms of 24.5 px. The 2022 excavation found wells of 3.8 m and rooms of 4.48 m, and says the Yangshi Lei drawing was wrong here (S104). Treat internal layouts on S01 as schematic. Open point: 33 rooms need a 7 x 7 grid with wells two rooms wide, which does not fit a 3.8 m well; S104 is a newspaper report, so the excavation report should settle it.
- **万字房 may carry borrowed numbers.** S113 gives it 33 rooms of 4.48 m, the same figures S104 gives 田字房. On S01 its rooms are about 14 px against 24.5 px at 田字房, so one of the two is off. Keep the 万字房 figures as provisional.
- **The brief's position for 正大光明 was off.** Plan (3300, 4700) is 九洲清晏 (labels 圆明园殿, 七间殿, 承恩堂). The label 正大光明 is at about (3305, 5510).
- **S01 at 谐奇趣:** the main block is a plain double-line rectangle without bays (x 8816-8942, y 1465-1506, read in round 1). The maze is labelled 黄花灯.

## 3. Class table

Heights above ground. Eave = platform + column (box top). The roof edge sits 0.5 x overhang lower.

| Class | Bays | Frontage m | Bay m, central / side | Depth m | Platform m | Eave m | Ridge m | Roof | Pitch | Conf. |
|---|---|---|---|---|---|---|---|---|---|---|
| grand_hall 七至九间正殿 | 7 | 33-40 | 5.17 / 4.83 / 4.32 (Round 11) | 15-19 | 0.59 (Round 11) | 4.76 | 10.77 | 卷棚歇山, grey | 34.8 | B |
| main_hall 五间殿 | 5 | 17-24 | 4.16 / 3.84 | 8-12 | 0.70 | 4.40 | 7.83 | 卷棚歇山 or 悬山, grey | 33.4 | B |
| side_hall 三间配殿 | 3 | 10-14 | 3.84 / 3.52 | 6-8 | 0.54 | 3.64 | 6.26 | 卷棚硬山 or 歇山, grey | 33.1 | C |
| small_house 小式三间 | 3 | 8-12 | 3.20 / 2.88 | 5.5-7 | 0.45 | 3.20 | 5.34 | 卷棚硬山 or 悬山, grey | 31.3 | B |
| gallery 游廊 | row | by S01 | 2.88 | 1.8-2.6 | 0.30 | 2.70 | 3.75 | 卷棚悬山, grey | 35 | C |
| pavilion_square 方亭 | 1 | 4.5-8 | 4.48 | 4.5-8 | 0.48 | 3.68 | 6.59 | 攒尖, 重檐 for some | 35 | B |
| pavilion_polygon 六方 / 八方亭 | 1 | 5-9 | 3.20 | 5-9 | 0.50 | 3.50 | 6.60 | 攒尖 | 35 | C |
| storeyed_hall 二层楼 | 3-5 | 9-23 | 3.20 / 2.88 | 3.5-8 | 0.45 | 3.65 / 5.95 | 8.10 | 卷棚歇山 or 硬山 | 31.3 | B |
| gate_hall 门殿 | 5 | 15-22 | 4.48 / 3.84 | 8-11.5 | 0.77 | 4.47 | 7.95 | 卷棚歇山, grey | 36.9 | B |
| temple_hall 祀庙正殿 | 9 | 30-44 | 5.12 / 4.48 | 14-18 | 1.40 | 7.00 | 15.5 double eave | 重檐歇山, yellow | 35.5 | C |
| tower 三层阁 | 3 | 12-17 | 5 / 4.5 | 12-17 | 0.50 | tiers | 23.94 | 三重檐 | 32 | C |

B applies to frontage, bays and platform where a named hall gives them. **Every ridge height is rule-derived, so C**, except 清音阁 23.94 m (S103). Round 11 changed the grand_hall row (Q182, Q183): section 10. A three-roll hall (三卷, 勾连搭) repeats the main_hall section, each roll 7.55 m deep (观澜堂, S111).

## 4. The Qing rules

**Primary text read directly.** 《工程做法》 1734, scan at S100. The OCR is unusable, so I read the page images.
- Contents pages show one juan per building type, for example 卷五 柒檩转角, 卷十四 柒檩三滴水歇山正楼, 卷二十 柒檩硬山库房, 卷二十一 叁檩垂花门, 卷二十二 方亭, 卷二十三 圆亭, 卷二十四 柒檩小式, 卷二十五 陆檩小式, 卷二十六 伍檩小式. Juan 1-4, 7-8 and 27 were not read clearly.
- 27 types in juan 1-27: found in a search snippet of the Nagoya paper (S126), whose PDF returned 503. The contents pages fit it.
- 卷二十, folio image: 「凡檐柱以面阔拾分之捌定高低径寸。如面阔壹丈肆尺，得柱高壹丈壹尺贰寸，径壹尺壹寸贰分。如次间稍间面阔比明间窄小者，其柱檩枋等木径寸仍照明间。至面阔临期酌夺地势定尺寸。」 So H = 0.8 bay. The diameter here is 0.08 bay. And bay widths were to be set on site according to the ground, which supports not expecting a fixed bay.

**Rules below come from S101, a modern summary, not checked page by page against 1734.** S125 warns that 工程做法, 营造算例 and 清式营造则例 are different texts that get mixed up, and S101 does cite both 则例 and 算例, so treat these as working rules. Liang's books (S127) were not reachable.

| Item | Rule | Source |
|---|---|---|
| Column, 小式 6-7 purlins | H = 0.8 bay; diameter 0.07 bay ("面阔一丈一尺，得柱高八尺八寸，径七寸七分") | S101, S100 |
| Column, 小式 4-5 purlins | H = 0.7 bay | S101 |
| Column, 大式 | 70 doukou including plate and brackets; 56-58 net, 60 in Liang as quoted by S101 | S101 |
| Bay, 大式 | 11 doukou per bracket set; central bay 6 sets + 2 half | S101 |
| Side bay | central less one set, or 0.8 central | S101 |
| 小式 depth | up to five purlins, four steps; seven purlins by adding porches | S101 |
| Step 步架 | 4-5 purlin diameters | S101 |
| Overhang 上出 | 0.3 H without brackets; with brackets 21 doukou + bracket reach (3, 6, 9) | S101 |
| Platform edge 下出 | 0.8 上出 小式, 0.75 大式 | S101 |
| Platform 台明 | H/5 or 2 diameters 小式; 1/4 of platform top to beam underside 大式 | S101 |
| 举架 | eave step 五举; 5 purlins 五 / 七; 7 purlins 五 / 六五 / 八五; 大式 五 / 六五 / 七五 / 九; ridge step at most 八五 小式, 十 大式 | S101 |
| 卷棚 | even purlin count, two ridge purlins. Top step 1/5 of the 四架梁 span, sides 2/5; between 2 and 3 diameters | S101 |
| 歇山 | gable set in one purlin diameter from the side eave purlin | S101 |
| 庑殿 | 推山: each step reduced by one tenth, except the first | S101 |

Roof ranks: 重檐庑殿 > 重檐歇山 > 庑殿 > 歇山 > 悬山 > 硬山, 卷棚 below their sharp-ridged forms. This order is general knowledge, not checked in a source I opened; **assumed**, and not used for any number. Evidence below sets the forms hall by hall.

**Worked arithmetic (`scripts/typology_rules.py`).**
- 卷二十: bay 14 chi = 4.48 m; H 11.2 chi = 3.584 m; diameter 1.12 chi = 0.358 m.
- 小式 7 purlin: bay 11 chi = 3.52 m; H 8.8 chi = 2.816 m; diameter 0.77 chi = 0.246 m.
- 大式, doukou 2.5 cun = 0.08 m: central bay 7 x 11 x 0.08 = 6.16 m; next 6 x 11 x 0.08 = 5.28 m; column + plate + brackets 70 x 0.08 = 5.60 m, net 14.3 chi = 4.58 m; overhang (21 + 6) x 0.08 = 2.16 m.
- small_house, 6 purlin rolled, depth 6.40, porch 1.28: inner 3.84 = 2 x 1.48 + top 0.89. Rise = 1.28 x 0.5 + 1.48 x 0.7 = 1.67. Ridge = 0.45 + 2.75 + 1.67 + 0.22 + 0.25 = 5.34.
- main_hall, 8 purlin rolled, depth 9.60, porch 1.60: inner 6.40 = 4 x 1.39 + top 0.83. Rise = 1.60 x 0.5 + 1.39 x 0.65 + 1.39 x 0.85 = 2.89. Ridge = 0.70 + 3.70 + 2.89 + 0.29 + 0.25 = 7.83.
- grand_hall, 10 purlin rolled, depth 16.74, porch 1.70: inner 13.34 = 6 x 2.02 + top 1.21. Rise = 1.70 x 0.5 + 2.02 x (0.6 + 0.75 + 0.9) = 5.40. Ridge = 1.22 + 5.12 + 5.40 + 0.39 + 0.25 = 12.38. The 0.6 step, the 0.6 top-step ratio and the 0.25 m for boards and tile are my assumptions.

**The rules tested on real halls of the garden.**

| Hall | Bay | Column | H / bay | Platform | Platform / H | 下出 | Rule 0.24 H | Source |
|---|---|---|---|---|---|---|---|---|
| 春雨轩土地庙 | 3.20 | 2.56 | 0.80 | 0.32 | 0.12 | | | S114 |
| 惠如春 | 3.20 | 2.75 | 0.86 | | | | | S111 |
| 雷峰夕照 | 3.20 | 2.91 | 0.91 | | | | | S111 |
| 藏密楼, lower | 3.20 | 3.20 | 1.00 | 0.32 | 0.10 | | | S111 |
| 万字房 | 4.48 | 3.68 | 0.82 | 0.58 | 0.16 | 0.86 | 0.88 | S113 |
| 观澜堂 | 4.16 | 4.32 | 1.04 | 0.96 | 0.22 | 1.12 | 1.04 | S111 |
| 松风阁 | | 3.10 | | 0.54 | 0.17 | 0.70 | 0.74 | S111 |
| 正大光明殿 | | 5.12 | | 1.22 | 0.24 | | | S106, S02 |

So the 0.8 rule holds for small halls and drifts to about 1.0 on large ones or storeyed halls. The platform is usually lower than H/5, and higher only on the largest. 下出 fits the rule closely. I used the observed values, not the rule, wherever a hall gives them.

## 5. What was typical at Yuanmingyuan

**Grey 卷棚 is the default, checked, with named exceptions.**
- **Viewed directly:** Forty Scenes leaf 正大光明 (S08, file "Hall of Rectitude and Honor"): every roof grey, rolled ridges, gable-hip on the main halls, low platforms, low white walls.
- **Viewed directly:** leaf 方壶胜境 (S08, "Beautiful Scene of the Square Pot"): blue, yellow and green glazed roofs, storeyed halls, high marble terraces with three water pavilions. A grey-roofed side court sits in the same leaf.
- 正大光明殿 is 七间 布瓦卷棚歇山 on the 1744 album and its sister versions (S119). The British embassy views of 1793 (Alexander and others) add a 月台 and four censers, placed between 1775 and 1793 (S119). The 1860 state should have the 月台. The drawn dragon ridges of the British views are called invention in S119.
- Text: "除极少数殿堂外… 多用小式灰瓦、卷棚顶" (S06). I sampled two leaves only, **not all forty**: a full roof count is a job for the pictures round.
- 澹怀堂 five bays 卷棚歇山 with 单翘重昂 brackets; 长春园宫门 and 朝房 grey 卷棚歇山 (S112, quoting the excavation report). So brackets occur even on rolled grey halls.
- 安佑宫: nine bays, double-eave gable-hip, yellow glazed, modelled on 寿皇殿, the highest rank in the garden (S122, S06).
- 蓬岛瑶台 reroofed in glazed tile 1740; 镂月开云 "覆二色瓦" (S118).
- 文源阁: excavation confirms six bays and black glazed roof, with green edging from S105; 硬山 per S105, form still argued.
- Xiyang Lou: glazed roofs (S108, S06). At 谐奇趣, blue and yellow glazed tile and fragments with Chinese or Western patterns turned up in the park's storeroom (S128).
- Roof variety is wide: 勾连搭 of 2-4 rolls, 田 and 万 plans, crescent plan, 4, 6 and 8 sided pavilions (S118).

《圆明园内工则例》: not reached. It exists (used by 郭黛姮's team, S128) and 郭黛姮 wrote a review of it (S129). See wishlist.

**Other classes.**
- **亭:** 吕祖亭 6.72 m with surrounding porch (S114); 文源阁 stele pavilion platform 4.48 m (S105); 揽翠亭 单檐六方 (S111); 贻兰庭 重檐四方 (S111).
- **廊:** 正大光明 east 叠落游廊 on the leaf (S08). Attached porches 1.28-1.92 m (S111, S113). Long Corridor 728 m / 273 bays = 2.67 m (S120, comparable).
- **戏台:** 清音阁 3 storeys, 3 bays each face, 23.94 m to ridge; 扮戏楼, 南楼, 正楼 in `by_name` (S103). 畅音阁 20.71 m (S121, comparable). 淳化轩 stage 16 m square, column 4.48 m (S103).
- **舍卫城:** walled court on S01, 墩台 at the south gate 15.4 x 12.6 m, excavated (S107).
- **文源阁:** 22.72 x 14.72 m by the Guangxu 丈尺册, six bays with a narrow west bay. Two storeys outside, three inside (a mezzanine in the waist eave). Much larger than its model 天一阁. S105 also says its plan is close to 文津阁 and 文溯阁, about 26 x 15 m: at 26 m the plan gives 4.76 px/m, right on the ground scale, so the two sizes need settling (S105).
- **牌楼:** 鸿慈永祜 three-bay, six posts, two infill walls (S118). Glazed form and 8 m 华表 (S122). 长春园牌楼门 column 5.12 m (S123).
- **墙:** 虎皮石 (S117), about 2.8 m high, total length of outer wall 11170 m, double on W, N, E with a 12.6 m lane (S116). No thickness found.
- **影壁:** 41.6 m (S102). Malone measured 137 ft x over 5 ft x about 15 ft, then it was torn down (S02 p.69). S01 does not draw it.
- **买卖街:** 3.2 x 4.8 m shops (S115).
- **桥:** forms only (S111), sizes from S01.

## 6. Xiyang Lou 西洋楼

Forms and counts are B where cited. **All boxes are C**, scaled from S01 at 4.77 px/m or guessed from the texts. I did **not** study the 1786 engravings for this: they are not in the local folders and the pictures round holds them. Heights need that pass. See `xiyang_lou` in `params.json`.

| ID | Name | Facts | Suggested box, m | Source |
|---|---|---|---|---|
| XY01 | 谐奇趣 Xieqiqu | Ground 7 bays, second 7, top 3; 9-bay curved corridors; two-storey octagonal pavilions; cornices level within 2 cm | main 28 x 14 x 12; corridors 20 x 4 x 6; octagons d 8 x 11 | S108; S03 39.7 x 38.6 ruin |
| XY02 | 蓄水楼 Xushui Lou | Small, two storeys, one-storey north wing | 10 x 8 x 9 | S02 p.143 |
| XY03 | 花园门 Huayuan Men | Maze south gate | 8 x 3 x 6 | S02, S109 |
| XY04 | 黄花阵 Huanghua Zhen | Walls 1.2 x 0.6 m, 1600 m total | outer 73 x 99; ring d 20; pavilion d 10 | S109, S01 |
| XY05 | 养雀笼 Yangque Long | Gate-like block, engraved | 20 x 10 x 8, guess | S02 |
| XY06 | 方外观 Fangwai Guan | Two storeys, 3 bays each, 重檐 four slopes, blue glaze | 13 x 11 x 11 | S06; S03 44 x 24 ruin |
| XY07 | 五竹亭 Wuzhu Ting | Five bamboo pavilions, galleries | 6 x 6 x 5 each, guess | S06 |
| XY08 | 海晏堂 Haiyan Tang | Two storeys, 11 bays west; 锡海 27.36 x 5.72 x 1.44 m; core 7.2 m high, brick casing 5 m | west 19 x 44 x 13; tank 27 x 10 x 9; east 22 x 26 x 9 | S109, S110; S03 135 x 54 ruin |
| XY09 | 远瀛观 Yuanying Guan | 5 bays, centre 3 set back, three-storey centre, double-eave hip | 21 x 18 x 15, base 2 | S109; S03 59 x 51 ruin |
| XY10 | 大水法 Da Shuifa | Pool, two 13-tier towers; jets about 6 chi | pool 29 x 19; niche 20 x 3 x 9 | S109, S06, S01 |
| XY11 | 观水法 Guan Shuifa | Throne and screen | 12 x 6 x 1 + 15 x 1 x 5, guess | S01 |
| XY12 | 线法山 Xianfa Shan | Round hill, pavilion, plan label 转马台 | d 38, h 8 guess | S01 |
| XY13 | 螺蛳牌楼 Luosi Pailou | Labelled on S01 | 8 x 1.5 x 7, guess | S01 |
| XY14 | 方河 Fang He | Water | 149 x 45 | S03 |
| XY15 | 线法墙 Xianfa Qiang | Paired screens, plan label 线法画 | 6 x 1 x 5 each, guess | S01, S06 |

The maze's stated size conflicts: 89 x 59 m (S06, also en.wikipedia, uncited), about 15000 sq m (S109), S01 about 73 x 99 m. S06's "16 km" of wall is a slip for 1.6 km. Today's white marble pavilion is the 1980s rebuild; S109 says the original was timber with a glazed roof.

## 7. What remains a guess

- All ridge heights except 清音阁.
- Depth at class level, since the plan understates it and few depths are stated.
- 0.25 m roof build-up, the 0.6 top-step ratio, and upper-storey and tower tier heights.
- Galleries: width and column.
- Polygon pavilions: all sizes.
- Wall thickness.
- All Xiyang Lou boxes, except 锡海 and the ruin polygons.
- 安佑宫: size; form is sourced.

## 8. Wishlist

| What | Where | How | Replaces |
|---|---|---|---|
| 《圆明园百景图志》 | book; S111 and others quote it | buy or library | blog quotations of dozens of 丈尺 |
| 《考古》2004-2 含经堂 report; 《圆明园长春园含经堂遗址发掘报告》 and 《圆明园长春园宫门区遗址发掘报告》 | CNKI or library | to-request | 含经堂 and 澹怀堂 sizes |
| 正大光明 and 大宫门 excavation reports (北京市文物研究所, from 2012) | Institute, CNKI | to-request | S02 and S102 secondary numbers |
| 《圆明园内工则例》 in 《清代匠作则例》; 郭黛姮 《〈圆明园内工则例〉评述》 | Wang Shixiang edition; S129 volume | library | grey-roof rule and allowances |
| 梁思成 《清式营造则例》 1934, 《清工部工程做法则例图解》 | book | buy | the S101 summary |
| 工程做法 卷二十二, 卷二十三, 卷二十四 | S100, other volumes, page images | read pages | pavilion rules, 小式 quote at source |
| Adam 1936 *Yuen Ming Yuen*, 东方 / 贺艳 / 王道成 on Xiyang Lou, Tsinghua reports | library | to-request | every XY box |
| 1786 engravings, measured | pictures round | in scope | XY heights |
| Yangshi Lei 烫样 data | Palace Museum, NLC | to-request | roof heights |

## 9. Sources (block S100-S129)

Text from web pages is research-only unless stated. Nothing here copies images.

| ID | Source | Year | Reuse as stated | Status | Link | Good for |
|---|---|---|---|---|---|---|
| S100 | 《工程做法》, 允礼等撰, 北大 scan via CADAL, Internet Archive | 1734 | PD by age | viewed (page images; OCR junk) | https://archive.org/details/02090256.cn and https://archive.org/details/02090263.cn (n76) | primary rule, type list |
| S101 | 曲阜三孔古建, 《中国营造技术知识点——清代建筑的通则》, Sohu | 2020 | unclear, research-only | viewed | https://www.sohu.com/a/390219687_100017881 | Qing rule summary |
| S102 | 《正大光明区域考古勘探报告》, 梦回圆明园 档案 page, free part only | n.d. | unclear, research-only | viewed in part (rest paywalled) | https://www.mhymy.com/dasl/12324.html | 大宫门 台基, 影壁 |
| S103 | 黄赛丰, 《圆明园戏场探微》, 圆明园官网 | 2021 | site reserves rights | viewed | https://www.yuanmingyuanpark.cn/xs/yjbg/202108/t20210831_4483509.html | stages, towers |
| S104 | 李韵, 王笑妃, 《圆明园澹泊宁静遗址发掘获重要成果》, 光明日报 via 中新网 | 2022 | research-only | viewed | https://www.chinanews.com.cn/cul/2022/11-14/9893900.shtml | 田字房 excavated |
| S105 | 杨菁 等, 《圆明园文源阁》, 《圆明园研究》63 | 2022 | site reserves rights | viewed | http://www.yuanmingyuanpark.cn/xs/ktsb/202201/t20220128_4510628.html | chi = 0.32 m, 文源阁 丈尺册 |
| S106 | 单志刚, 《圆明园中的正大光明殿》, 人大清史所 site | 2022 | research-only | viewed | http://iqh.ruc.edu.cn/old/qdhjylyjzx/xszl/lswh/7dca16cf3b144adc892b1d0b14d24e60.htm | 正大光明 column |
| S107 | 《仅存于图纸上的圆明园舍卫城到底什么样》, 腾讯新闻 | 2020 | research-only | viewed | https://view.inews.qq.com/k/20200108A0M0Q400 | 舍卫城 墩台 |
| S108 | Gao Ming et al., Digital restoration ... Xieqiqu, ISPRS Annals II-5/W3 | 2015 | per publisher, check before reuse | viewed | https://doi.org/10.5194/isprsannals-II-5-W3-75-2015 | 谐奇趣 form, method |
| S109 | 刘阳, 《圆明园的故事》 excerpt, 澎湃 | 2017 | research-only | viewed | https://www.thepaper.cn/newsDetail_forward_1750908 | Xiyang Lou facts |
| S110 | 人民网, 海晏堂蓄水楼加固 | 2016 | research-only | viewed | http://house.people.com.cn/n1/2016/0728/c164220-28590471.html | core height, casing |
| S111 | 北平旧梦, 老北京的记忆（125）, blog quoting 《圆明园百景图志》 | 2017 | research-only | viewed | https://blog.sina.com.cn/s/blog_88741e0d0102x6gc.html | 丈尺 of many halls |
| S112 | 北平旧梦, 老北京的记忆（81）, blog quoting the 宫门区 report | n.d. | research-only | viewed | https://blog.sina.com.cn/s/blog_88741e0d0102w60j.html | 澹怀堂, 宫门 |
| S113 | 《万字房的"前世"与"重生"》, 梦回圆明园 | 2023 rev. | research-only | viewed | https://www.mhymy.com/xsjl/14213.html | 万字房 丈尺 |
| S114 | 贾珺, 《圆明三园中的祀庙祠宇建筑探析》, PDF at 故宫博物院 site | n.d. | research-only | viewed | https://www.dpm.org.cn/Uploads/File/2018/06/15/u5b23730ae0e5a.pdf | 土地庙, 吕祖亭 |
| S115 | Article on 买卖街, 人大清史所 site | 2021 post | research-only | viewed | http://iqh.ruc.edu.cn/old/qdhjylyjzx/xszl/hwyj/4115411323ba4429a9ecc9ae5b2bc2e5.htm | shop sizes |
| S116 | 《圆明园围墙历史变迁考》, 圆明园官网 | 2021 | site reserves rights | viewed | https://www.yuanmingyuanpark.cn/xs/yjbg/202108/t20210831_4483376.html | wall |
| S117 | 《圆明园文源阁遗址考古成果发布》, 新华网 | 2025 | research-only | viewed | http://www.news.cn/local/20250113/42158ce447b64aab8b6590fd52fddf3c/c.html | 文源阁 dig, 虎皮石 |
| S118 | Article on the 绢本四十景图, 人大清史所 site; author not shown | 2020 post | research-only | viewed | http://iqh.ruc.edu.cn/old/qdhjylyjzx/xszl/jzys/8eef05885c3e4279ae0132f1a37a13c9.htm | roof and plan variety |
| S119 | 《现存几张正大光明殿图像述评（连载·二）》, 中国圆明园学会 blog | n.d. | research-only | viewed | https://blog.sina.com.cn/s/blog_50feaf600100dc69.html | 正大光明 images, 月台 |
| S120 | Long Corridor text, Visit Beijing | n.d. | research-only | viewed | https://www.visitbeijing.com.cn/article/4JXy25o2h1A | gallery comparable |
| S121 | 畅音阁 texts, 本地宝 and Visit Beijing | n.d. | research-only | viewed | https://m.bendibao.com/show683011.html ; https://www.visitbeijing.com.cn/article/47QtXfWkDiW | tower comparable, height and tile |
| S122 | yaffin, 【圆明园】系列09, blog | n.d. | research-only | viewed | https://blog.sina.com.cn/s/blog_65fec3ab0100sv4p.html | 安佑宫, 月地云居 forms |
| S123 | 长春园 page, 圆明园官网 | 2011 | site reserves rights | viewed | http://www.yuanmingyuanpark.cn/cgll/zyjd/ccy/201101/t20110105_231501.html | 长春园牌楼门 column |
| S125 | 《关于〈工程做法〉若干问题的思考》, 《建筑史学刊》 2026 | 2026 | research-only | viewed abstract only | https://www.jgcm.ac.cn/jah/article/doi/10.12329/20969368.2026.02015 | warning on texts |
| S126 | Paper on 工程做法则例, 名古屋工業大学 repository (year from the filename) | 2002 | research-only | found (503 on fetch) | https://nitech.repo.nii.ac.jp/record/2086/files/bnit2002_185.pdf | 74 juan, 27 types |
| S127 | 梁思成, 《清式营造则例》; 《清工部工程做法则例图解》 | 1934; later | book | to-request | | rule source |
| S128 | 郭黛姮, lecture text 《重返圆明园》, Tsinghua UP sample; Tsinghua news on her team | 2020 | research-only | first viewed, second found | https://www.tup.com.cn/upload/books/yz/089340-01.pdf ; https://www.tsinghua.edu.cn/info/1366/81418.htm | 谐奇趣 glazed tile, 内工则例 used |
| S129 | 郭黛姮, 《〈圆明园内工则例〉评述》, in a volume on 清代则例 (contents list only) | n.d. | book | found | https://pre.iudicium.de/assets/content/programm/isbn-978-3-89129-405-5/iudicium-9783891294055-inhalt-moll-murata-chinese-handicraft-regulations.pdf | 内工则例 lead |

S124 is unused. S02, S01, S03, S06 and S08 are the reserved IDs. The Forty Scenes leaves were read from Wikimedia Commons copies of S08 ("Hall of Rectitude and Honor.jpg", "Beautiful Scene of the Square Pot.jpg").

## 10. Round 11: the class defaults re-read, and the hall kit

**Applied, each against its evidence in `research/scenes/dimensions.csv` (method a):**
- **Q182, grand_hall column and platform.** The Round 1 values (column 5.12 m, platform 1.22 m) were those of 正大光明殿, the audience hall. The class's other measured halls are lower. Columns: 慎德堂 YM03-11 4.35 m, 保合太和殿 YM02-08 4.48 m (S310). Platforms: 慎修思永 YM23-01 column 4.0 m and platform 0.96 m (S310); 慎德堂's platform 0.59 m (S310); 田字殿 YM20-01 column 3.68 m and platform 0.55 m (S139, S137). The class now takes the medians, run by `scripts/typology_rules.py`: **column 4.17 m, platform 0.59 m**, eave 4.76 m, ridge 10.77 m (rule, C). 正大光明殿 keeps 5.12 and 1.22 m in `by_name`.
- **Q183, grand_hall bays.** The yellow slip of NLC 样001-4 for 正大光明殿 gives 明间 1.615 丈, 次间 1.51 丈 and 梢间 1.35 丈 (S310): **5.17 / 4.83 / 4.32 m**. The class was drawn from that hall as its type, so its own drawing replaces the plan-read split 5.50 / 4.70.
- **Q184, 清音阁.** `by_name` takes the Yangshi Lei figures as transcribed on mhymy 7297 (S310): bays 5.50 and 4.51 m, 3 x 3 bays, 14.52 m square (it matches the 中层檐内通见方 of 14.53 m), platform 0.96 m, 下出 1.12 m, columns 4.42, 3.71 and 2.72 m, ridge 23.94 m. `boxes1860.py` puts the three eaves at 5.38, 12.18 and 18.0 m: the top roof keeps the tower class's rise, and the two floor zones share what is left (C).

**Left open:** Q185, 安佑宫's 华表. Its block is absorbed into the 牌坊's. The form is known, the places of the four columns are not.

**Also from Round 11:**
- A hall with its own figures in a dossier takes them over the class: column, platform, ridge (`figures` on the box). Method a or b wins over `by_name` too; c or d only over the class.
- A roof form or tile colour read on the album for that hall (`research/scenes/halls.csv`, Round 7) wins over the class when the reading names one form (`roof_src`, `tiles_src`, `tile_edge`, `sides`). 39 boxes took a roof reading and 38 a tile reading.

**The kit's defaults** (`scripts/kit1860.py`; overview in `research/kit/README.md`):

| Item | Default | Source or reason |
|---|---|---|
| 举架 by class, eave to ridge | grand 五 / 六 / 七五 / 九; temple and tower 五 / 六五 / 七五 / 九; main, side, gate 五 / 六五 / 八五; small house, storeyed hall, gallery 五 / 七; pavilions 五 / 七 / 九 | S101, section 4; the roof's profile |
| Bracket sets 斗拱 as a band | grand_hall, temple_hall, gate_hall, tower | S101 (大式); S112 (澹怀堂, 长春园宫门) |
| Back porch 后廊 | the hall's own figure, else by seed: small house 70 %, main 80 %, grand and temple 100 %, side 30 %, storeyed 60 % | S111 (惠如春, 松风阁: two porches); the shares are C |
| Porch all round 周围廊 | grand_hall, temple_hall over 12 m | S02 (正大光明殿) |
| Steps 踏跺 | 0.15 m rise, tread at most 0.3 m, the flight no longer than the overhang | C |
| Balustrade | grand and temple halls, any platform of 0.95 m or more | C |
| Unread gable on a small house | 硬山 60 %, 悬山 40 % by seed | params.json "卷棚硬山 or 悬山"; Q206 |
| Colours | lacquer red-brown, brick grey, panes dark, the eave band blue-green | chosen for the view; Q204, Q205 |
