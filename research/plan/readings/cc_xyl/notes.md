# cc_xyl: Changchun Yuan + Xiyang Lou, reading notes (S01; mosaic x 8600-12955, y 0-5100)

Tiles viewed: about 40 (over the 12-30 target; many small zooms to read labels), plus engravings P0049 and P0042. Tiles in `tiles/`. `_build/` holds the source tables and the check script.

## Reading problems
- Labels on the plan name the hall **north of the label** as a rule: 蕴真斋, 淳化轩, 含经堂, 静莲斋, 渊映斋, 思永斋, 澹怀堂, 正谊明道, 琴清斋 all sit in the court south of their hall. Applied that rule where a label stands between two halls (渊映斋: B0557 taken, B0583 is the other candidate). It is a rule from this area, not a certainty.
- Some labels stand on water: 谐奇趣, 流香渚, 海岳开襟, 翠交轩, 静便趣. They name buildings, not the lake.
- Unsure characters left as `?`: 華?馆, ?月亭 (first char like 濃), 西水?房 (third char drawn like 章/車; 西水车房 would fit), 得胜? (third char perhaps 槩), 三?轩 (looks like 有; text 三友轩), 樂奏?天, 狎?亭 (鷗), ?井, ?亭 (楼?) at (9760,3570), ?园门.
- `rect=w,h,angle` follows blocks.csv (w along the angle). Odd forms have their parts listed as x/y ranges in `note`.
- **gates.json G22 reads 绮园门 "likely". At 4x zoom the first char is 艹 over a 青-like shape, no 糸 radical: read 蒨 or similar.** Malone's 3 is just north of it. Lily should check this one by eye.
- Blue numbers: 1 to 8 all found and consistent with Malone pp.98-99. The blue 1 is a faded stroke at (11105,4670).
- Blocks outside the rule: blocks in the box south of the wall line y~4650 (B0883, B0884, B0958, B0959 etc.) are Qichun Yuan side: not read, left for the qc reader. Label under B0958 at (9210,5020) not read for the same reason.

## Xiyang Lou: what the plan draws
- Colloquial names, not the engraving titles: 黄花灯 (黄花阵), 转马台 (线法山), 线法画 (线法墙), 螺蛳牌楼, 西水?房. Inventory ids kept; `name_on_plan` shows what is written.
- Buildings are drawn as outlines; bays only on 方外观, 远瀛观, the maze hall, 海晏堂's east block, the 线法画 ranges. 谐奇趣's main block is an empty rectangle.
- **五竹亭 (XY07) is not drawn.** Its two kidney beds and small round pool, exactly as in engraving 9, are drawn at (9360,1173), (9424,1173), (9396,1201), on 方外观's axis. The strip south of them to the wall is empty. Position inferred, C. The bow-tie figure (9469,1101) off the axis is unexplained; it could be a misplaced or simplified element, but its form does not match engraving 9's straight row.
- 海晏堂 west stairs and pool are on a **pasted slip** (9618-9760, 980-1257) in a denser hand: the only slip seen here. Plan's 海晏堂 is 3 parts: front block, 西水?房 box, long labelled hall (probably 锡海 reservoir), east block (B0181/B0182). That maps poorly onto the engraving's single mass: treat the east part as schematic.
- 线法画: 6 staggered walls per side on the plan; Malone says five. Far wall at (12398,1100-1165). 
- 线法桥 (XY02-01): nothing drawn south of 蓄水楼. Not placed.
- Fountain figure at (8876,1094) is about 290 px north of 谐奇趣's stairs; engraving 2 shows it close to them. The empty court between may be compressed in the engraving or stretched on the plan.

## Plan versus text
- Bay counts agree: 宫门 5, 大东门 7, 朝房 3+3, 花神庙 3, 方外观 3, 远瀛观 5, 思永斋 ~7, 蓄水楼 5.
- Disagree: 澹怀堂 5 cols vs 9; 含经堂 ~9 vs 7; 正谊明道 ~8 vs 5; 云容水态 6 vs 5. Grids here look partly schematic, so bays alone cannot size these halls.
- Rixia names not found or not placed (no label, no clear shape): 理心楼; 蒨园's 青莲朵, 标胜亭, 别有天, 韵天琴, 委宛藏, 梅石碑亭; 罨画溪; 狮子林's 虹桥, 假山, 纳景堂, 藤架, 磴道, 占峰亭, 清淑斋, 延景楼, 云林石室, 横碧轩; 如园's 敦素堂, 冠霞阁, 明漪楼. 小香幢 and 探真书屋 are labelled.
- **丛芳榭 is not labelled.** I put CC12 on the 华?馆/琴清斋 group because 琴清斋 is its text neighbour; the plan calls the hall 华?馆 and the south pavilion ?月亭.
- 平畴交远风, 转湘帆, 得全阁 and its two towers, 七孔闸: all unlabelled, all `guess`. 林渊锦镜: not found.
- 佳处领其要 labels the court the text calls 小有天园. 山色湖光共? labels the octagon court, though the text's 楼 is more likely the north hall.
- New names on the plan, not in the inventory: 静莲斋, 澄波夕照, 华?馆, ?月亭, 迎月亭, 静便趣, 佳处领其要, ?井, 狎?亭, 芥舟, 朝暉亭, 延清堂, 五孔闸, ?幄 (8994,3361).
- Good check of the plan as Malone's map: he says one small pavilion only is not square with the compass, facing north-east, about 100 yards north of 如园 (p.99). B0721 at 51 deg is it. The 4 flights of steps of 海岳开襟 (p.98) are also there.
- Malone p.99 prints "A Portion of the Official Map" with these figures added by him (caption read in the text; figure not seen).

## Dating evidence
- **如园: main hall labelled 延清堂, and 敦素堂, 冠霞阁, 明漪楼 of Rixia (1780s) are not labelled.** The plan therefore shows a state later than Rixia here. From memory, not verified in a source in hand: 如园 was rebuilt under Jiaqing and 延清堂 belongs to that rebuild. This needs a source (wishlist) before it is stated.
- 五竹亭 missing though on the 1780s engravings: it either went before the drawing or was skipped. No date for its loss in the texts I used. Do not read it as "gone by 1860" without a source.
- Pasted slip on 海晏堂: a revision after the first drawing, undated.
- 含经堂 complex is drawn in full, including 三?轩, the theatre 樂奏?天 and the 买卖街 rows, so that group is not a reduced late state.
- Pencil 嶽 by 海岳开襟 is in a later hand, not Qing evidence.
- Which reign: I cannot assign one from this area alone. It is post-Rixia at 如园 and otherwise compatible with Qianlong-to-Xianfeng. No hall here with a firm post-1800 date in the texts I had.

## Schematic areas
Xiyang Lou fronts (outlines, not bays); 海晏堂 east half; 狮子林 rock gardens (halls placed among dense ink rocks, hard to count); 如园 rock courts; 蒨园 (no labels at all, identification weak, all halls guess).
