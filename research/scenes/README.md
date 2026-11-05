# 圆明园 Yuanmingyuan: the scenes, one by one

Round 7 did for every scene and compound outside the Xiyang Lou what Round 6 did for the European palaces: one dossier each, so the next rounds can model them. 81 dossiers, in four waves: the famous scenes of Yuanming Yuan; the other Forty Scenes and six compounds; Changchun Yuan; Qichun Yuan. Each is `<ID>-<slug>/README.md` with its sheet `<ID>-<slug>/dimensions.json`, written by `scripts/scenes_dossiers.py` from the hand-edited sheets beside this file (`about.json`, `halls.csv`, `dimensions.csv`, `views.csv`, `best.csv`, `digs.csv`, `interior.csv`, `parts.csv`; fields in `research/README.md`). The public pages, for the best-documented scenes only, and the hub listing all of them: `site/scenes/`, by `scripts/scenes_page.py`.

**How to read a dossier.** What it was; the leaf of 1744 with Qianlong's preface and poem; how later sources differ; the halls one by one, from `buildings.csv` with what each source states beside it; the evidence per hall; interior and setting; what survives and the digs; reconstructions by others (never a source for a size); the best views; the dimension sheet with a method per figure; the gaps. A hall with nothing of its own shows the plan and its scene's evidence: the dossier says how many.

**Dimension methods,** as for the Xiyang Lou with c adapted: a, a published survey, excavation report or measured drawing, or a Qing drawing or text that writes the figure (a Yangshi Lei slip in 丈尺 is a); b, measured on the plan or a ruin footprint (the rows marked `run` are measured by the script on our traced layers: a scene's outline, its islands and water); c, read from a painting or woodcut by module; d, a photograph with a known object; e, typology, or a figure with no survey behind it. 1 营造尺 = 0.32 m throughout; each figure records the scale it used.

## Modelling priority

Decision, with the counts in the table below as of this round. After 谐奇趣 XY01 (`research/xiyanglou/README.md`):

1. **正大光明 YM01, with 大宫门 YM41 and 出入贤良门 YM01-01: first.** The main hall has a full set of figures from a Qing drawing: the yellow slip of 样001-4 gives each bay in 丈尺 (明间 5.17 m, 次间 4.83 m, 梢间 4.32 m), the hall 35.95 × 16.0 m with its porches (S310), inside Malone's measured platform of 39.32 × 19.2 m (S02, `typology/params.json`). Barrow measured the room inside in 1793 (S251). The 1744 leaf shows the court; the dig at 大宫门 found the gate hall, the wing gates, the 金水桥 and the channel (S132, E2120); witnesses of 1860 describe the hall. Few, large, axial buildings: a fast and honest model, and the way into the garden in the 3D view. Weak: no dig of the hall itself; the roof form rests on the leaf and the typology.
2. **含经堂 CC02: second.** The best ground truth outside the Xiyang Lou: dug in 2001-02 and laid out for visitors, its foundations show the courts, the steps and the column positions (S143, S990), and 王文涛 2015 gives the bays and roofs hall by hall, with 三友轩 measured on the ruin at 11.1 × 7.2 m (S940). 12 free photographs of the foundations came in this round (P0799-P0801, P0814-P0822), 22 free pictures in all. Weak: the full dig report is not online, so most hall sizes still come from the plan; 300 × 200 m is a large group.
3. **九洲清晏 YM03, its central axis: third.** The emperor's residence, with more figures than any other scene: 圆明园殿 from the slip of 样007-9-1 (1855: bays, depth, column height, platform), 慎德堂 from its fit-out drawings (5 × 3 bays under three rolls, 23.36 × 26.49 m), and the 1855 whole-scene plan 样011-3 known by number. Model the three axis halls and 慎德堂 first, the side courts as massing. Risk: the plan S01 shows Tongzhi's names of 1873 here (Q36), and many court figures come from the Tongzhi plan 故1299 of 1874, so they are B for 1860; 样011-3 itself sits behind a paywall (wishlist).

Next in line: 方壶胜境 YM29 (its stone platform survives, glazed roofs on the leaf, but no figure yet), 文源阁 YM46 (the library's 丈尺册 gives every bay; a dig of 2024), 正觉寺 QC11 (the gate, 文殊亭 and four side halls stand and could be measured on site; nothing published found).

**The ten public pages** are the best-documented scenes by the score in the table, among those with at least one free picture and at least 2,500 characters of text: 如园 CC18 has no free picture yet, 濂溪乐处 YM23 too little text. 方壶胜境 and 坐石临流 YM38 tied (44.2 and 44.3 at the time of the choice); 方壶胜境 was taken for its surviving platform. Every sentence of their text was checked against its sources by a worker who did not write it: `checks.csv`.

## Typology: what the dossiers say about the defaults

Measured figures against `typology/params.json`, in the generated table below. Four proposals, none applied, since each would change many boxes (Q182-Q185 in `research/questions.md`):

- **grand_hall, heights:** column 5.12 → 4.2 m and platform 1.22 → 0.7 m for the class; 正大光明殿 keeps 5.12 and 1.22 through `by_name`. The residential and office halls measured all fall below the default: 慎德堂 4.35 and 0.59, 保合太和殿 4.48, 慎修思永 4.0 and 0.96, 田字殿 3.68 and 0.55 (S310, S139, S137). The default came from the audience hall, the one hall of the class built higher.
- **grand_hall, bays:** central 5.5 → 5.17 m, side 4.7 → 4.83 and 4.32 m, from the slip of 样001-4 (S310).
- **清音阁 YM44-02** is classed as a storeyed hall, but its drawing gives a ridge of 23.94 m and a middle storey 14.53 m square: the tower class. A `by_name` entry would put it right.
- **石华表 YM17-02**, the columns of 安佑宫 (about 8 m on a 1.24 m base, S980), stand as a square pavilion box: a column shape, or no box.

Where the defaults hold: the side halls (三友轩 11.1 × 7.2 m within 10-14 × 6-8 m), the main halls' frontage (圆明园殿 19.52 m, 延清堂 22.85 m), 圆明园殿's column (3.84 against 3.7 m) and platform (0.70 against 0.70 m). Deep halls such as 延清堂 (19.97 m) and 慎德堂 (26.49 m) are three-roll halls, which the rule for rolls already covers. The roofs: the album shows grey tile and rolled ridges almost everywhere, with glazed roofs at 蓬岛瑶台, 方壶胜境, 安佑宫, 广育宫 and the front hall of 镂月开云 (album worker, `halls.csv`), in line with `typology/halls.md`.

<!-- generated:start (scripts/scenes_dossiers.py): do not edit between these markers -->

## Every scene and compound, as measured here

Halls: rows inside it; own: with a picture or text of their own. Pictures: tied to the scene or its halls (free). Read: pictures read for a modeller in `views.csv`. Texts: evidence rows (drawings). Digs: excavations or surveys of the remains. Figures by method a b c d e, with the new ones from research in brackets (the rest measured here on the traced layers). Prose: sections written, of 8. Score: how well documented, used to pick the public pages (texts/10 + free pictures × 2 + digs × 4 + new a-figures × 2 + read pictures + sections × 3).

| Id | Name | Wave | Halls | Own | Pictures | Read | Texts | Digs | a | b | c | d | e | Prose | Score | Public | Dossier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| YM03 | 九洲清晏 Jiuzhou Qingyan | 1 | 73 | 27 | 17 (15) | 9 | 131 (23) | 1 | 36 (36) | 7 | 0 | 0 | 0 | 8 | 152.1 | yes | [YM03-jiuzhou-qingyan](YM03-jiuzhou-qingyan/README.md) |
| YM01 | 正大光明 Zhengda Guangming | 1 | 23 | 13 | 11 (10) | 7 | 68 (2) | 0 | 13 (13) | 4 | 1 (1) | 0 | 2 (2) | 8 | 83.8 | yes | [YM01-zhengda-guangming](YM01-zhengda-guangming/README.md) |
| YM02 | 勤政亲贤 Qinzheng Qinxian | 1 | 28 | 11 | 5 (5) | 4 | 58 (4) | 0 | 6 (6) | 4 | 0 | 0 | 0 | 4 | 43.8 |  | [YM02-qinzheng-qinxian](YM02-qinzheng-qinxian/README.md) |
| YM41 | 大宫门 Da Gongmen | 1 | 17 | 13 | 1 (0) | 0 | 34 (0) | 0 | 5 (5) | 3 | 0 | 0 | 0 | 4 | 25.4 |  | [YM41-da-gongmen](YM41-da-gongmen/README.md) |
| YM32 | 蓬岛瑶台 Pengdao Yaotai | 1 | 11 | 8 | 12 (10) | 7 | 31 (0) | 0 | 2 (2) | 7 | 0 | 0 | 0 | 6 | 52.1 | yes | [YM32-pengdao-yaotai](YM32-pengdao-yaotai/README.md) |
| YM54 | 福海 Fu Hai | 1 | 0 | 0 | 5 (5) | 2 | 40 (0) | 0 | 1 (1) | 3 | 0 | 0 | 0 | 2 | 24.0 |  | [YM54-fu-hai](YM54-fu-hai/README.md) |
| YM29 | 方壶胜境 Fanghu Shengjing | 1 | 25 | 8 | 12 (10) | 7 | 22 (3) | 0 | 0 | 4 | 1 (1) | 0 | 0 | 6 | 47.2 | yes | [YM29-fanghu-shengjing](YM29-fanghu-shengjing/README.md) |
| YM46 | 文源阁 Wenyuan Ge | 1 | 6 | 4 | 0 (0) | 0 | 35 (4) | 1 | 7 (7) | 7 | 0 | 0 | 1 (1) | 6 | 39.5 |  | [YM46-wenyuan-ge](YM46-wenyuan-ge/README.md) |
| YM45 | 舍卫城 Shewei Cheng | 1 | 38 | 7 | 3 (1) | 1 | 29 (0) | 0 | 2 (2) | 3 | 0 | 0 | 1 (1) | 4 | 21.9 |  | [YM45-shewei-cheng](YM45-shewei-cheng/README.md) |
| YM44 | 同乐园 Tongle Yuan | 1 | 23 | 8 | 1 (1) | 0 | 39 (5) | 0 | 19 (19) | 3 | 0 | 0 | 1 (1) | 5 | 58.9 | yes | [YM44-tongle-yuan](YM44-tongle-yuan/README.md) |
| YM15 | 山高水长 Shangao Shuichang | 1 | 10 | 2 | 6 (6) | 4 | 31 (4) | 0 | 1 (1) | 3 | 0 | 0 | 0 | 6 | 39.1 |  | [YM15-shangao-shuichang](YM15-shangao-shuichang/README.md) |
| YM20 | 澹泊宁静 Danbo Ningjing | 1 | 16 | 15 | 6 (6) | 5 | 50 (1) | 0 | 12 (12) | 7 | 0 | 0 | 0 | 6 | 64.0 | yes | [YM20-danbo-ningjing](YM20-danbo-ningjing/README.md) |
| YM13 | 万方安和 Wanfang Anhe | 1 | 11 | 10 | 7 (6) | 5 | 33 (5) | 1 | 3 (3) | 4 | 0 | 0 | 0 | 6 | 48.3 | yes | [YM13-wanfang-anhe](YM13-wanfang-anhe/README.md) |
| YM09 | 杏花春馆 Xinghua Chunguan | 1 | 17 | 10 | 9 (9) | 6 | 37 (3) | 0 | 0 | 7 | 0 | 0 | 0 | 5 | 42.7 |  | [YM09-xinghua-chunguan](YM09-xinghua-chunguan/README.md) |
| YM14 | 武陵春色 Wuling Chunse | 1 | 33 | 15 | 5 (5) | 4 | 53 (2) | 0 | 0 | 7 | 0 | 0 | 0 | 5 | 34.3 |  | [YM14-wuling-chunse](YM14-wuling-chunse/README.md) |
| YM31 | 平湖秋月 Pinghu Qiuyue | 1 | 13 | 7 | 7 (7) | 5 | 39 (2) | 0 | 0 | 4 | 0 | 0 | 0 | 6 | 40.9 |  | [YM31-pinghu-qiuyue](YM31-pinghu-qiuyue/README.md) |
| YM39 | 曲院风荷 Quyuan Fenghe | 1 | 18 | 8 | 8 (7) | 5 | 16 (2) | 0 | 0 | 4 | 1 (1) | 0 | 0 | 5 | 35.6 |  | [YM39-quyuan-fenghe](YM39-quyuan-fenghe/README.md) |
| YM38 | 坐石临流 Zuoshi Linliu | 1 | 7 | 1 | 9 (9) | 6 | 23 (3) | 0 | 0 | 4 | 0 | 0 | 0 | 6 | 44.3 |  | [YM38-zuoshi-linliu](YM38-zuoshi-linliu/README.md) |
| YM33 | 接秀山房 Jiexiu Shanfang | 1 | 11 | 8 | 7 (7) | 5 | 30 (3) | 0 | 0 | 7 | 0 | 0 | 0 | 5 | 37.0 |  | [YM33-jiexiu-shanfang](YM33-jiexiu-shanfang/README.md) |
| YM04 | 镂月开云 Louyue Kaiyun | 2 | 9 | 3 | 8 (6) | 4 | 27 (0) | 0 | 0 | 7 | 0 | 0 | 0 | 6 | 36.7 |  | [YM04-louyue-kaiyun](YM04-louyue-kaiyun/README.md) |
| YM05 | 天然图画 Tianran Tuhua | 2 | 21 | 9 | 8 (6) | 4 | 31 (2) | 0 | 0 | 7 | 0 | 0 | 0 | 5 | 34.1 |  | [YM05-tianran-tuhua](YM05-tianran-tuhua/README.md) |
| YM06 | 碧桐书院 Bitong Shuyuan | 2 | 22 | 4 | 6 (6) | 4 | 10 (0) | 0 | 0 | 7 | 0 | 0 | 0 | 5 | 32.0 |  | [YM06-bitong-shuyuan](YM06-bitong-shuyuan/README.md) |
| YM07 | 慈云普护 Ciyun Puhu | 2 | 8 | 5 | 9 (8) | 4 | 14 (1) | 0 | 0 | 7 | 0 | 0 | 0 | 4 | 33.4 |  | [YM07-ciyun-puhu](YM07-ciyun-puhu/README.md) |
| YM08 | 上下天光 Shangxia Tianguang | 2 | 5 | 4 | 8 (8) | 4 | 19 (4) | 1 | 1 (1) | 7 | 0 | 0 | 0 | 4 | 39.9 |  | [YM08-shangxia-tianguang](YM08-shangxia-tianguang/README.md) |
| YM10 | 坦坦荡荡 Tantan Dangdang | 2 | 15 | 8 | 7 (7) | 4 | 34 (4) | 1 | 0 | 7 | 0 | 0 | 0 | 5 | 40.4 |  | [YM10-tantan-dangdang](YM10-tantan-dangdang/README.md) |
| YM11 | 茹古涵今 Rugu Hanjin | 2 | 15 | 5 | 6 (6) | 4 | 21 (3) | 0 | 0 | 7 | 0 | 0 | 0 | 3 | 27.1 |  | [YM11-rugu-hanjin](YM11-rugu-hanjin/README.md) |
| YM12 | 长春仙馆 Changchun Xianguan | 2 | 20 | 12 | 9 (9) | 4 | 75 (3) | 0 | 0 | 3 | 0 | 0 | 0 | 5 | 44.5 |  | [YM12-changchun-xianguan](YM12-changchun-xianguan/README.md) |
| YM16 | 月地云居 Yuedi Yunju | 2 | 23 | 8 | 5 (5) | 4 | 23 (4) | 0 | 0 | 7 | 0 | 0 | 0 | 5 | 31.3 |  | [YM16-yuedi-yunju](YM16-yuedi-yunju/README.md) |
| YM17 | 鸿慈永祜 Hongci Yonghu | 2 | 18 | 13 | 14 (13) | 9 | 25 (2) | 0 | 7 (7) | 9 (2) | 0 | 0 | 0 | 6 | 69.5 | yes | [YM17-hongci-yonghu](YM17-hongci-yonghu/README.md) |
| YM18 | 汇芳书院 Huifang Shuyuan | 2 | 14 | 9 | 6 (5) | 4 | 41 (3) | 0 | 0 | 4 | 0 | 0 | 0 | 4 | 30.1 |  | [YM18-huifang-shuyuan](YM18-huifang-shuyuan/README.md) |
| YM19 | 日天琳宇 Ritian Linyu | 2 | 20 | 15 | 5 (5) | 4 | 16 (2) | 0 | 0 | 3 | 0 | 0 | 0 | 4 | 27.6 |  | [YM19-ritian-linyu](YM19-ritian-linyu/README.md) |
| YM21 | 映水兰香 Yingshui Lanxiang | 2 | 8 | 6 | 5 (5) | 4 | 22 (2) | 0 | 0 | 6 | 0 | 0 | 0 | 3 | 25.2 |  | [YM21-yingshui-lanxiang](YM21-yingshui-lanxiang/README.md) |
| YM22 | 水木明瑟 Shuimu Mingse | 2 | 5 | 2 | 5 (5) | 4 | 15 (3) | 0 | 5 (5) | 4 | 0 | 0 | 0 | 4 | 37.5 |  | [YM22-shuimu-mingse](YM22-shuimu-mingse/README.md) |
| YM23 | 濂溪乐处 Lianxi Lechu | 2 | 18 | 16 | 6 (5) | 4 | 43 (2) | 0 | 10 (10) | 4 | 0 | 0 | 0 | 4 | 50.3 |  | [YM23-lianxi-lechu](YM23-lianxi-lechu/README.md) |
| YM24 | 多稼如云 Duojia Ruyun | 2 | 7 | 3 | 5 (5) | 4 | 14 (1) | 0 | 0 | 3 | 0 | 0 | 0 | 3 | 24.4 |  | [YM24-duojia-ruyun](YM24-duojia-ruyun/README.md) |
| YM25 | 鱼跃鸢飞 Yuyue Yuanfei | 2 | 12 | 5 | 6 (5) | 4 | 14 (1) | 0 | 0 | 3 | 0 | 0 | 0 | 3 | 24.4 |  | [YM25-yuyue-yuanfei](YM25-yuyue-yuanfei/README.md) |
| YM26 | 北远山村 Beiyuan Shancun | 2 | 15 | 7 | 5 (5) | 4 | 27 (3) | 0 | 0 | 3 | 0 | 0 | 0 | 4 | 28.7 |  | [YM26-beiyuan-shancun](YM26-beiyuan-shancun/README.md) |
| YM27 | 西峰秀色 Xifeng Xiuse | 2 | 16 | 8 | 5 (5) | 4 | 39 (3) | 0 | 0 | 4 | 0 | 0 | 0 | 4 | 29.9 |  | [YM27-xifeng-xiuse](YM27-xifeng-xiuse/README.md) |
| YM28 | 四宜书屋 Siyi Shuwu | 2 | 28 | 11 | 5 (5) | 4 | 42 (1) | 0 | 0 | 4 | 0 | 0 | 0 | 4 | 30.2 |  | [YM28-siyi-shuwu](YM28-siyi-shuwu/README.md) |
| YM30 | 澡身浴德 Zaoshen Yude | 2 | 21 | 9 | 7 (6) | 4 | 42 (0) | 0 | 0 | 7 | 0 | 0 | 0 | 3 | 29.2 |  | [YM30-zaoshen-yude](YM30-zaoshen-yude/README.md) |
| YM34 | 别有洞天 Bieyou Dongtian | 2 | 22 | 10 | 9 (9) | 4 | 32 (2) | 0 | 0 | 4 | 0 | 0 | 0 | 4 | 37.2 |  | [YM34-bieyou-dongtian](YM34-bieyou-dongtian/README.md) |
| YM35 | 夹镜鸣琴 Jiajing Mingqin | 2 | 15 | 11 | 7 (7) | 4 | 13 (2) | 0 | 1 (1) | 7 | 0 | 0 | 0 | 2 | 27.3 |  | [YM35-jiajing-mingqin](YM35-jiajing-mingqin/README.md) |
| YM36 | 涵虚朗鉴 Hanxu Langjian | 2 | 14 | 9 | 7 (7) | 4 | 22 (2) | 0 | 0 | 4 | 0 | 0 | 0 | 4 | 32.2 |  | [YM36-hanxu-langjian](YM36-hanxu-langjian/README.md) |
| YM37 | 廓然大公 Kuoran Dagong | 2 | 19 | 14 | 9 (8) | 4 | 42 (5) | 0 | 0 | 4 | 0 | 0 | 0 | 3 | 33.2 |  | [YM37-kuoran-dagong](YM37-kuoran-dagong/README.md) |
| YM40 | 洞天深处 Dongtian Shenchu | 2 | 63 | 8 | 5 (5) | 4 | 27 (4) | 0 | 0 | 4 | 0 | 0 | 0 | 4 | 28.7 |  | [YM40-dongtian-shenchu](YM40-dongtian-shenchu/README.md) |
| YM47 | 藻园 Zao Yuan | 2 | 19 | 10 | 1 (1) | 0 | 71 (2) | 2 | 2 (2) | 3 | 0 | 0 | 0 | 3 | 30.1 |  | [YM47-zao-yuan](YM47-zao-yuan/README.md) |
| YM48 | 紫碧山房 Zibi Shanfang | 2 | 16 | 11 | 1 (1) | 0 | 65 (1) | 2 | 0 | 4 | 0 | 0 | 0 | 3 | 25.5 |  | [YM48-zibi-shanfang](YM48-zibi-shanfang/README.md) |
| YM49 | 若帆之阁 Ruofan zhi Ge | 2 | 9 | 4 | 0 (0) | 0 | 18 (3) | 0 | 0 | 3 | 0 | 0 | 0 | 1 | 4.8 |  | [YM49-ruofan-zhi-ge](YM49-ruofan-zhi-ge/README.md) |
| YM50 | 三潭印月 Santan Yinyue | 2 | 8 | 5 | 1 (1) | 0 | 12 (1) | 0 | 0 | 4 | 0 | 0 | 0 | 1 | 6.2 |  | [YM50-santan-yinyue](YM50-santan-yinyue/README.md) |
| YM51 | 课农轩 Kenong Xuan | 2 | 6 | 1 | 0 (0) | 0 | 13 (2) | 0 | 0 | 3 | 0 | 0 | 0 | 2 | 7.3 |  | [YM51-kenong-xuan](YM51-kenong-xuan/README.md) |
| YM55 | 后湖 Hou Hu | 2 | 0 | 0 | 4 (4) | 0 | 6 (0) | 0 | 0 | 3 | 0 | 0 | 0 | 2 | 14.6 |  | [YM55-hou-hu](YM55-hou-hu/README.md) |
| CC02 | 含经堂 Hanjing Tang | 3 | 33 | 17 | 22 (22) | 14 | 88 (2) | 3 | 22 (22) | 7 | 0 | 0 | 0 | 7 | 143.8 | yes | [CC02-hanjing-tang](CC02-hanjing-tang/README.md) |
| CC14 | 玉玲珑馆 Yulinglong Guan | 3 | 14 | 7 | 1 (1) | 0 | 37 (1) | 0 | 3 (3) | 7 | 0 | 0 | 0 | 3 | 20.7 |  | [CC14-yulinglong-guan](CC14-yulinglong-guan/README.md) |
| CC04 | 思永斋 Siyong Zhai | 3 | 18 | 4 | 5 (5) | 0 | 26 (0) | 0 | 0 | 6 | 0 | 0 | 0 | 3 | 21.6 |  | [CC04-siyong-zhai](CC04-siyong-zhai/README.md) |
| CC06 | 海岳开襟 Haiyue Kaijin | 3 | 6 | 1 | 4 (4) | 1 | 26 (0) | 0 | 0 | 7 | 0 | 0 | 1 (1) | 4 | 23.6 |  | [CC06-haiyue-kaijin](CC06-haiyue-kaijin/README.md) |
| CC13 | 狮子林 Shizi Lin | 3 | 18 | 14 | 7 (7) | 2 | 67 (0) | 0 | 0 | 3 | 0 | 0 | 0 | 4 | 34.7 |  | [CC13-shizi-lin](CC13-shizi-lin/README.md) |
| CC18 | 如园 Ru Yuan | 3 | 19 | 5 | 0 (0) | 0 | 41 (2) | 2 | 25 (25) | 4 | 0 | 0 | 0 | 6 | 80.1 |  | [CC18-ru-yuan](CC18-ru-yuan/README.md) |
| CC16 | 鉴园 Jian Yuan | 3 | 8 | 4 | 0 (0) | 0 | 22 (0) | 1 | 0 | 4 | 0 | 0 | 0 | 3 | 15.2 |  | [CC16-jian-yuan](CC16-jian-yuan/README.md) |
| CC15 | 映清斋 Yingqing Zhai | 3 | 8 | 1 | 0 (0) | 0 | 11 (1) | 0 | 0 | 7 | 0 | 0 | 0 | 2 | 7.1 |  | [CC15-yingqing-zhai](CC15-yingqing-zhai/README.md) |
| CC09 | 宝相寺 Baoxiang Si | 3 | 8 | 4 | 0 (0) | 0 | 9 (1) | 0 | 0 | 3 | 0 | 0 | 0 | 2 | 6.9 |  | [CC09-baoxiang-si](CC09-baoxiang-si/README.md) |
| CC08 | 法慧寺 Fahui Si | 3 | 7 | 4 | 0 (0) | 0 | 12 (1) | 0 | 0 | 3 | 0 | 0 | 1 (1) | 2 | 7.2 |  | [CC08-fahui-si](CC08-fahui-si/README.md) |
| CC10 | 泽兰堂 Zelan Tang | 3 | 6 | 5 | 0 (0) | 0 | 14 (1) | 0 | 0 | 4 | 0 | 0 | 0 | 2 | 7.4 |  | [CC10-zelan-tang](CC10-zelan-tang/README.md) |
| CC01 | 澹怀堂 Danhuai Tang | 3 | 12 | 7 | 5 (5) | 0 | 19 (0) | 2 | 1 (1) | 4 | 0 | 0 | 0 | 1 | 24.9 |  | [CC01-danhuai-tang](CC01-danhuai-tang/README.md) |
| CC03 | 蒨园 Qian Yuan | 3 | 17 | 10 | 0 (0) | 0 | 30 (1) | 0 | 0 | 4 | 0 | 0 | 0 | 2 | 9.0 |  | [CC03-qian-yuan](CC03-qian-yuan/README.md) |
| CC05 | 得全阁 Dequan Ge | 3 | 3 | 2 | 2 (2) | 0 | 9 (0) | 0 | 0 | 3 | 0 | 0 | 0 | 2 | 10.9 |  | [CC05-dequan-ge](CC05-dequan-ge/README.md) |
| CC07 | 流香渚 Liuxiang Zhu | 3 | 2 | 2 | 1 (1) | 0 | 5 (0) | 0 | 0 | 3 | 0 | 0 | 0 | 2 | 8.5 |  | [CC07-liuxiang-zhu](CC07-liuxiang-zhu/README.md) |
| CC12 | 丛芳榭 Congfang Xie | 3 | 5 | 1 | 0 (0) | 0 | 10 (0) | 0 | 0 | 3 | 0 | 0 | 0 | 1 | 4.0 |  | [CC12-congfang-xie](CC12-congfang-xie/README.md) |
| CC17 | 东宫门 Dong Gongmen | 3 | 3 | 3 | 0 (0) | 0 | 8 (0) | 0 | 0 | 3 | 0 | 0 | 0 | 2 | 6.8 |  | [CC17-dong-gongmen](CC17-dong-gongmen/README.md) |
| QC04 | 敷春堂 Fuchun Tang | 4 | 23 | 7 | 4 (4) | 0 | 57 (11) | 0 | 0 | 3 | 0 | 0 | 0 | 5 | 28.7 |  | [QC04-fuchun-tang](QC04-fuchun-tang/README.md) |
| QC08 | 鉴碧亭 Jianbi Ting | 4 | 0 | 0 | 6 (6) | 2 | 17 (0) | 1 | 0 | 7 | 0 | 0 | 0 | 2 | 25.7 |  | [QC08-jianbi-ting](QC08-jianbi-ting/README.md) |
| QC07 | 涵秋馆 Hanqiu Guan | 4 | 2 | 0 | 2 (2) | 0 | 17 (1) | 1 | 1 (1) | 4 | 0 | 0 | 0 | 2 | 17.7 |  | [QC07-hanqiu-guan](QC07-hanqiu-guan/README.md) |
| QC05 | 清夏斋 Qingxia Zhai | 4 | 7 | 0 | 0 (0) | 0 | 30 (3) | 0 | 0 | 4 | 0 | 0 | 0 | 4 | 15.0 |  | [QC05-qingxia-zhai](QC05-qingxia-zhai/README.md) |
| QC11 | 正觉寺 Zhengjue Si | 4 | 11 | 5 | 14 (13) | 4 | 16 (1) | 1 | 0 | 4 | 0 | 0 | 1 (1) | 4 | 47.6 | yes | [QC11-zhengjue-si](QC11-zhengjue-si/README.md) |
| QC01 | 绮春园宫门 Qichun Yuan Gongmen | 4 | 2 | 1 | 5 (5) | 1 | 12 (2) | 0 | 0 | 3 | 0 | 0 | 1 (1) | 2 | 18.2 |  | [QC01-qichun-yuan-gongmen](QC01-qichun-yuan-gongmen/README.md) |
| QC02 | 迎晖殿 Yinghui Dian | 4 | 3 | 0 | 1 (1) | 0 | 12 (1) | 0 | 0 | 3 | 0 | 0 | 0 | 2 | 9.2 |  | [QC02-yinghui-dian](QC02-yinghui-dian/README.md) |
| QC17 | 春泽斋 Chunze Zhai | 4 | 9 | 0 | 0 (0) | 0 | 18 (0) | 0 | 0 | 4 | 0 | 0 | 0 | 2 | 7.8 |  | [QC17-chunze-zhai](QC17-chunze-zhai/README.md) |
| QC12 | 澄心堂 Chengxin Tang | 4 | 7 | 1 | 0 (0) | 0 | 15 (3) | 0 | 0 | 7 | 0 | 0 | 0 | 2 | 7.5 |  | [QC12-chengxin-tang](QC12-chengxin-tang/README.md) |
| QC13 | 含晖楼 Hanhui Lou | 4 | 8 | 1 | 0 (0) | 0 | 29 (0) | 0 | 0 | 4 | 0 | 0 | 0 | 3 | 11.9 |  | [QC13-hanhui-lou](QC13-hanhui-lou/README.md) |
| QC14 | 畅和堂 Changhe Tang | 4 | 7 | 3 | 0 (0) | 0 | 14 (0) | 0 | 0 | 7 | 0 | 0 | 0 | 1 | 4.4 |  | [QC14-changhe-tang](QC14-changhe-tang/README.md) |
| QC19 | 四宜书屋 (绮春) Siyi Shuwu (Qichun) | 4 | 15 | 0 | 1 (1) | 0 | 18 (2) | 1 | 5 (5) | 4 | 0 | 0 | 0 | 2 | 23.8 |  | [QC19-siyi-shuwu-qichun](QC19-siyi-shuwu-qichun/README.md) |
| QC06 | 凤麟洲 Fenglin Zhou | 4 | 2 | 0 | 4 (4) | 0 | 31 (0) | 1 | 2 (2) | 7 | 0 | 0 | 0 | 2 | 25.1 |  | [QC06-fenglin-zhou](QC06-fenglin-zhou/README.md) |

Dossiers: 81, public pages 10. Figures in all: 588 (a 192, b 384, c 3, d 0, e 9); from research 206 (a 192, b 2, c 3, d 0, e 9), measured here on the layers 382. Halls with evidence of their own: 529 of 1174.

## Typology check

Measured figures (methods a and d) on a hall with a class, against `research/typology/params.json`: a range for frontage and depth, ±15% round a single default. A hall's overall depth stands for its depth where both are given; a room's inside is left out. `typology_check.json` holds every item. Proposals stand in the hand-written part above and in `research/questions.md`.

| Class | Figures | Within | Outside | Outside: row, what, value against default |
|---|---|---|---|---|
| gate_hall | 2 | 1 | 1 | YM45-03 山门 platform_h 1.25 vs 0.77 |
| grand_hall | 18 | 5 | 13 | YM03-11 慎德堂 column_h 4.35 vs 5.12; YM03-11 慎德堂 platform_h 0.59 vs 1.22; YM03-11 慎德堂 frontage 23.36 vs [33, 40]; YM03-11 慎德堂 depth 26.49 vs [15, 19]; YM02-08 保合太和殿 frontage 32 vs [33, 40]; YM02-08 保合太和殿 depth 11.52 vs [15, 19] |
| main_hall | 10 | 4 | 6 | YM03-01 圆明园殿 depth 7.04 vs [8, 12]; CC02-13 乐奏钧天戏台 frontage 16 vs [17, 24]; CC02-13 乐奏钧天戏台 depth 16 vs [8, 12]; CC18-N01 延清堂 platform_h 1 vs 0.7; CC18-N01 延清堂 platform_h 1 vs 0.7; CC18-N01 延清堂 depth 19.968 vs [8, 12] |
| pavilion_square | 3 | 0 | 3 | YM20-11 静香屋 frontage 3.2 vs [4.5, 8]; YM17-02 石华表 height_ridge 8 vs 6.59; YM17-02 石华表 platform_h 1.24 vs 0.48 |
| side_hall | 4 | 4 | 0 |  |
| small_house | 5 | 2 | 3 | YM22-01 水木明瑟殿 depth 4.48 vs [5.5, 7]; YM22-01 水木明瑟殿 column_h 3.2 vs 2.75; CC02-15 买卖街 frontage 135.65 vs [8, 12] |
| storeyed_hall | 10 | 2 | 8 | YM46-01 文源阁阁 depth 14.72 vs [3.5, 8]; YM44-02 清音阁 frontage 32 vs [9, 23]; YM44-02 清音阁 platform_h 0.96 vs 0.45; YM44-02 清音阁 column_h 4.42 vs [3.2, 2.3]; YM44-02 清音阁 height_ridge 23.94 vs 8.1; YM44-02 清音阁 platform_h 0.96 vs 0.45 |

<!-- generated:end -->
