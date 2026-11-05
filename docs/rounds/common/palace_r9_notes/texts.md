# Round 9, texts worker: how people moved through 圆明园 before 1860

Started 19:28 UTC. Deadline 20:12.

## Method
- Repo first: research/evidence/catalog.csv grepped for 舟 船 码头/马头 船坞 廊..楹 甬道 御路 听政 贤良 朝房 竞渡 龙舟 黄花 (58 rows with a hit, list in scratch palace_r9_texts_work/hits2.txt), plus all rows of the Western accounts S157 S240-S246 S251 S911.
- Local copies from Round 7 in scratch (read, not re-fetched): 日下旧闻考 j80-84 (Kanripo KR2k0036, palace_r7_tmp_texts_a/kanripo, palace_r7_tmp_w34), 养吉斋丛录 S202, 蕉轩随录 S210, 竹叶亭杂记 S211, 檐曝杂记, IA OCR of Wolseley S240, Swinhoe S241, M'Ghee S242, Hérisson S246, Malone S02.

## (f) 1856 guard officer's route (E0381 / E1524, S210)
Verified in the repo row E1524 (full quote). See TX rows. Notes:
- The emperor comes "从内乘船" (by boat from inside, i.e. from the residence area) to 山高水长 and lands at "后阁扇" (rear pavilion steps / door leaves?) : boat from the 后湖/residence to 山高水长 (YM? west). Then all ride (上乘马). So in 1856 the emperor moved by boat and by horse inside the garden.
- Landings named: 雷峰夕照马头 (马头 = 码头), 渊氵亭镜澈马头 (garbled in the corpus: likely 涵虚朗鉴/雷峰夕照's opposite? not resolved), boat 如在天上船.
- XY leg (TX-007): 蕊珠宫门 → 黄花磴 (tea) → 海晏堂 → 转马台 → 小角门 → 狮子林 清淑斋 (meal) → 宝相寺 → 法慧寺 → 谐奇趣 → 明春门 → 雷峰夕照马头. Positions from buildings.csv make this a loop: east along the strip, south-east to 狮子林, back west by the temples. 转马台 = probably the spiral ramp on 线法山 XY12 (assumed). 黄花磴 vs 黄花阵 unresolved.
- They RODE (上乘马, 七臣随行) from 山高水长 onward: horses inside the gardens in 1856, so the main ways were wide enough to ride.

## Rows written 19:33 (TX-001..TX-077), CSV palace_r9_texts.csv
Topics covered from repo + local copies: (a) Swinhoe/Wolseley/M'Ghee walk from 正大光明 to 九洲清晏, 勤政殿 as the place of 御门听政 (S202 j5), Jiaqing/Daoguang notes; (b) 辇道/causeway, 大宫门 朝房, 出入贤良门 three bridges and 罩门 rules (S05 j80:9a-b), 如意门 for the Grand Council (S202 j4), bridge flattened 1839 (S211); (c) 端午 viewing places (S202 j14), docks (S05 j82, j83), boat trips in poems; 同乐园 by boat (S202 j13); (e) galleries by bays (淳化轩 12+12 楹; QC 游廊 6间), 规月桥 行廊, 复道 at 如园.

## Doubts
- 前湖: 日下旧闻考 j80:7b puts 前湖 on both sides of the 辇道 BEFORE 大宫门; modern usage (and our dossiers) call the water between 正大光明/寿山 and 九洲清晏 前湖. Keep the two apart (TX row on 辇道).
- No Qing text found that says how the emperor crossed from 九洲清晏 to 勤政殿/正大光明 (bridge or boat). 1856: "上从内乘船" to 山高水长 shows boats used inside; the 1860 walkers went on foot round half the pond over a bridge (Swinhoe). The two bridges 南大桥/如意桥 fit M'Ghee's "bridged at each end".
- Malone's lantern procession with the fleet at a marble terrace is 颐和园 (after 1888): excluded (row says so).
- Hérisson's boat-house (p.323) is low trust: graded C.

## S360 (百景史事分景汇编) downloaded to scratch and read as text (palace_r9_texts_dl/s360.txt; PyMuPDF from palace_r7_tools)
Grep 乘船/乘舟/泛舟…至/船名/龙舟/肩舆/骑马. New rows TX-078 onward:
- 蓬岛瑶台 only by boat (往来祇藉舟相通), landing at 镜中阁 = its south gate (1772).
- Boat names: 卧游书室 (1741), 平安月镜居 (moon boat, 1765), 月波舻? (1855), 如坐天上 (1856; = 玉明's 如在天上), 安济(航) (1829), 浮汉槎 (1857).
- Boat routes "from X to Y": 凭流亭→春雨轩; 北远山村→芰荷香/耕云堂/天宇空明; 云锦墅→蓬岛瑶台; 狮子林→玉玲珑馆; 流香渚→如园; 圆明园南湖→凤麟洲 (绮春园).
- Yongzheng 1726 decree: the gazette's dragon-boat tour 由东海至西海 (Chinese behind Malone p.51); 1725 rule: officials come at dawn.
- 端午: 1756 races on 1st/4th/5th at 望瀛洲; 1823 empress dowager at 蓬岛瑶台.
- Sedan chair on the dikes at 含辉楼 (1819); riding track there.

## Correction 19:39
- 前湖: j80:20b says 正大光明後有湖亦稱前湖, 湖正北為圓明園殿. So the Qing text uses 前湖 for BOTH waters (before 大宫门 and behind 正大光明). Row on 辇道 corrected.
- Searched for a Qing text naming how the emperor crossed 前湖 (bridge or boat) to 勤政殿/正大光明: none found in S05 j80, S202, S360 (309 pages grepped), web (2 searches). The answer stays: on foot round the lake by the bridges at each end (1860 witnesses, B) or by boat (1856 "上从内乘船" to 山高水长, B); not resolved.

## Other added rows (TX-102..TX-135)
- 正大光明 ceremony: ranks by court (S360 pp.27, 77, 98, 101): high ranks at the hall steps / galleries, ministers inside 出入贤良门, lower ranks outside it and at 大宫门. 1849: emperor stayed at 慎德堂.
- Gates watched in 1815: main gate (barrier 档木), 西南门, 藻园门, 福园门 (S360 p.105).
- Measured landing: 如园 延清堂 码头 5.1 x 3.35 m, 1.1 m below the terrace (S362 dig).
- 藻园 built round a 船坞 (S156). 九洲清晏 656 rooms + gallery bays (S151).
- 黄花阵 Mid-Autumn lantern game: no source found (row with status unknown).
- Terms rows (topic term): meanings ours (assumed), with where each term is attested; 爬山廊, 抄手游廊, 垂花门, 踏跺, 御路 not found in the texts searched.

## Added 19:40 (TX-136..TX-140)
- 竹叶亭杂记 (S211) line 25: 召见 at 勤政殿; summer in the hall, spring/autumn in 东书房. Lines 84-87 (1797): in mourning the emperor came back NOT by 出入贤良门 but by the west gate to 长春仙馆: the usual way in was through 出入贤良门.
- 蕉轩随录 (S210): officials' 直庐 at the garden; 肃顺 took his chair at the 内阁直庐 (1859).
- 藏舟坞 YM53: survived 1860; sits by 山高水长 on our plan (fits the 1856 boat landing: assumed). E1877 seems to put it SE of 方壶胜境: doubt for the coordinator.

## Grading note
- I gave A only to: 1744/1755/1764 imperial prefaces/poem notes printed in S05 or S201 that describe a specific form (规月桥 行廊, 万方安和 galleries, 安澜园 曲廊, 慈云普护 path between lakes, 碧桐书院 flat bridge, 蓬岛瑶台 yearly viewing), the excavated 如园 landing (S362), the 藻园 dock survey (S156) and 谐奇趣 galleries (engraving). The coordinator may lower the text ones to B (the brief's "a pre-1860 text that draws it").
- Everything from S360/S361 (modern compilations of Qing records and poems) graded B.

## Not found / not reached
- No Qing text names the emperor's daily crossing from 九洲清晏 to 勤政殿/正大光明 (bridge 南大桥/如意桥 or boat). 
- No source for the 黄花阵 Mid-Autumn lantern game.
- No 1860 account of walking the Xiyang Lou.
- No width of any way, gallery or dike in a text; widths only from digs: 如园 landing 5.1 x 3.35 m; Attiret's boat 24 ft (7.3 m) wide; 1860 first court c.100 x 80 yards (M'Ghee).
- Not read: 日下旧闻考 j81-82 fully for 堤 (grepped only), the S361 volumes (only rows already in the catalogue), Macartney's own journal (only Barrow via the repo), M'Ghee/Wolseley beyond the repo rows and keyword greps. Web: 4 searches used, none useful.
- 爬山廊, 抄手游廊, 垂花门, 踏跺, 御路 not attested in the texts searched.
Finished 19:41 UTC.
