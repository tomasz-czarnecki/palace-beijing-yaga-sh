# Open questions

Close a question by moving it to "Resolved" with the answer and the source.

## Open

### The target state and the base plan

- **Q1. Target state.** Just before October 1860 (`CLAUDE.md`). What each key source dates to:
  - Forty Scenes album (S08), 1744: album finished 1746–47 per S41. Woodcuts 1745 (S76).
  - 日下旧闻考 (S05): the 1780s.
  - Xiyang Lou plates (P0041–60): by 1786 (S02, S56).
  - Yangshi Lei plans (S10–S13): mostly Daoguang to Tongzhi, sheet by sheet; not seen.
  - S18 《圆明园匾额略节》: late Xianfeng, closest to 1860; not seen.
  - S01: state about Daoguang to Xianfeng, see Q3.
  - S15 survey: 1933, ruins, with some Tongzhi works never built.

  **1744 → 1780s:** 涵虚朗鉴 moved from the west to the east shore of 福海 (S05 j82:21b); 四宜书屋 became 安澜园 c. 1762–64 (S05 j82:9a); west of 清晖阁: pines burnt 1763 (S41), 松云楼 and others 1765 (S05 j80:24a); 杏花春馆's beds became 春雨轩 1755 (S41); rice fields behind 水木明瑟 became 文源阁 1774 (S02 p.89); new, not in the album: 藻园 1751, Changchun Yuan, the Xiyang Lou, 前湖 south of the gate 1763 (S05 j80:8a).

  **1780s → 1860:** at 九洲清晏, 慎德堂 1831 replaced 乐安和 and 怡情书史 (S41, S43), and the axis halls changed after the 1836 fire (S41); 天然图画's pool filled c. 1831 (S41); 上下天光 rebuilt (S41, S42); 观鱼跃 → 观澜堂 c. 1817 (S51, S52); 洞天深处 four courts → two (S41); theatres 桃花坞 1811, 同道堂 1837 and 1855 (S43); 乐奏钧天 1814 (S43); nearly all of Qichun Yuan, with 敷春堂 reworked 1821 (S43), 惠济祠 and 河神庙 1813–17 (S47).

  **Rule used:** where S41 lists a scene as differing on later plans (16 scenes), the album row is B, not A, and S01 wins on layout. The list: 勤政亲贤, 九洲清晏, 杏花春馆, 天然图画, 上下天光, 日天琳宇, 碧桐书院, 慈云普护, 月地云居, 武陵春色, 曲院风荷, 洞天深处, 别有洞天, 接秀山房, 多稼如云, 濂溪乐处.

- **Q2. What is S01: the original or the tracing?** Malone bought both (S02 p.231). The museum's "1920s" is its own cataloguing and rests on the provenance line. Evidence for the tracing (the maps worker's inference, medium to high confidence, not proven): his plates p.72 and p.99 (S23) show a flap folded over the Back Lake and dark washes on the water; our mosaic shows no flap and only a pale wash (the trace found it faintly on all three scrolls, green in Changchun); "1920s" fits a tracing. Against: a real pasted slip exists on this copy at the 海晏堂 west stairs (x 9618–9760, y 980–1257). **Decision:** positions from S01 are B, not A, until this is settled. Wishlist: ask Princeton. Grades rise to A if it is shown to be the Qing original, or if a Yangshi Lei plan agrees.
- **Q3. Which state does S01 draw?** About Daoguang to Xianfeng; no firm upper date, and no single reign can be assigned.
  - Later than: 文源阁 1774 (drawn); 观澜堂 c. 1817 (drawn and labelled, 5×3, S52, S111); 河神庙 1813–17 (S47); 大宫门 of Qichun 1809 (lead only). 接秀山房's old names are absent, as in Daoguang–Xianfeng records (S111).
  - After 1831 **if** B0835, the largest hall on the west of the 九洲清晏 island, is 慎德堂: it stands where Malone p.80 puts it, 5 bays × 3 rolls, but it has no label.
  - Before: the Tongzhi works of 1873 (no 天地一家春; writes 清夏斋).
  - Names not in the texts, undated: 同顺堂, 承恩堂, 恩?堂, 福寿仁恩, 七间殿 (九洲清晏); 集禧堂, 永春堂 (Qichun, where the texts put 敷春堂); 延清堂 (如园); 知?堂, 水云居, 都罡殿, 三世佛殿, 乐道堂. These are the next dating clues (wishlist). 同道堂 (Xianfeng) is not written: its stated place is labelled 福寿仁恩.
- **Q4. The pasted slips.** Malone names slips at 九洲清晏 (p.72 caption, p.80 note) and 如意馆, group 40 (p.96 note; App. II). A footnote nearby was first read as being about Qichun: it is not. **None is on this copy at those places.** One slip is seen, at 海晏堂 (Q2). If the flat paper hides a slip, or if the tracing copied only one layer, the drawing at 九洲清晏 and 如意馆 may be either layer; compare S23 p.72 at higher resolution. `plan/slips.json` keeps the first candidates.
- **Q5. Scale of S01.** Malone's "about 1 to 1300" (S02 p.231) gives 3.94 px/m if the mosaic spans the 253 cm. Ground measured: 4.77 px/m, about 1:1070, turned about 7.2° (111 points, `georef/princeton-1920s.json`). Local scale 3.7–5.55. Halls are drawn at a median 4.18 px/m frontage and 3.31 depth (n = 7, 8; `typology/halls.md`), with wide scatter. Unexplained: why the buildings are drawn at another scale; a hall size from the plan is therefore an estimate, ±30% in the check.
- **Q6. Rights of S01. For Tomasz.** The museum "supports free access to images of works in the Public Domain", offers the download, flags no restriction on this object (a work under copyright reads "Restricted Download - Under Copyright" in the same field), requests the credit "Image courtesy of the Princeton University Art Museum". There is no formal licence, and the general terms say "limited non-commercial, educational, and personal use". **Decision for now:** traced geometry is public with credit; the plan image and overlay stay local. If he wants the plan shown on the site: fine by the museum's words while the project stays non-commercial. If the project goes commercial, ask the museum. Also see Q2: a hand tracing adds no authorship of its own (our reasoning, not legal advice).
- **Q7. Accuracy of the georeference, honestly.** LOO RMS 16.5 m, block cross-validation 19.8 m, but the check against independent labels is not blind: the georef worker edited its check set after seeing errors (first pass median 52 m, kept set 31 m; the JSON keeps both). Second check, on the final data (`plan/coverage.json`): plan position of a compound against OSM's hand-placed point: Yuan Ming Yuan median 41 m, p90 164 m (n = 36); Xiyang Lou median 15 m, p90 37 m (n = 10). OSM's points carry their own error, and a compound is 100 m wide, so this is an upper bound. No check at all in Changchun and for the walls; one only in Qichun. Unanchored: plain x 700–1500, y 3500–5600, the NW fields, the NW and SW corners. A step of about 25 m at the seam x≈8640 (N-S) can't be excluded.
- **Q8. Known errors of S01.**
  - 谐奇趣 stands too far south (S02 p.232, about two inches). The plan's distance 黄花阵 centre to 谐奇趣 is 174 m at ground scale; the ruins give 117 m. **Applied:** the transform is anchored on the ruin, and `build_r1.py` moves the XY01 group a further 17 m to the OSM ruin's centre. So the strip between the maze and 谐奇趣 (蓄水楼, the court) is stretched: treat as ±50 m.
  - 田字房: wells drawn too large; the 2022 dig says the Yangshi Lei drawing is wrong here (S104). Bay counts stand, sizes do not.
  - 山高水长 and the west plain are schematic. 正觉寺 is drawn narrow, 鉴碧亭's island round.
- **Q9. Bay counts, plan against text.** They agree at 廓然大公, 蓬岛瑶台, 别有洞天, 观澜堂, 宫门, 远瀛观, 方外观. They differ: 澹怀堂 5 (plan, excavation via S112) vs 9 (S06); 含经堂 about 9 vs 7 (S05) vs 5 (S06); 正谊明道 about 8 vs 5 (S05) vs 7 (S48); 长春仙馆 7 vs 5; 茹古涵今 6 vs 5; 九洲清晏殿 5 vs 7; 勤政殿 4 vs 5; 上下天光 9 cells vs 3; 保合太和 9×3 vs 3; 鱼跃鸢飞 6×5 vs 5; 文源阁 5 (plan as read) vs 6 (S05, excavation); 生冬室 3 plus porch vs 7 (S06). `bays` keeps the text, `bays_plan` the plan.

### Compounds and halls

- **Q10. 涵虚朗鉴.** YM36 stands on the east shore of 福海 (雷峰夕照 labelled there, S05). The same four characters are written clearly under B0355 at the 花神庙 group (2593,1993), in the north of Yuan Ming Yuan: row `YM23-N05`. Same name twice, or another plaque? YM36 stays on 福海.
- **Q11. Qichun Yuan's thirty scenes.** 19 of them have no label on S01 and no position (QC09 庄严法界, QC21, QC24, QC28, QC29, QC33, QC34, QC37, QC40–42, QC44–48, QC50–52). They are probably names of single halls or plaques; the plan labels fewer. S05 and Malone do not describe this garden, and the inventory rests on S06 and a blog (S49). Primary source: S58 仁宗 poems. CC21 林渊锦镜 and YM43 水闸 also have no position. Not guessed: Round 2 builds nothing for them.
- **Q12. 敷春堂.** No such label. The palace block QC04 reads 集禧堂, 永春堂, 问月楼. Renamed, or a state we can't date? `QC04-01` is a guess.
- **Q13. Weak identifications.** YM21 映水兰香: main hall not found, placed on the islet by Malone's 21. YM04 etc.: `read` says which. 蒨园 CC03: no labels at all, all guess. 丛芳榭 CC12: placed by its neighbour 琴清斋. 得全阁, 平畴交远风, 转湘帆, 七孔闸: unlabelled, guess. QC16, QC20, QC49: from form or position only.
- **Q14. A label names which hall?** The readers found a working rule: a label in a court names the hall north of it (同顺堂, 含经堂, 澹怀堂 ...). Where halls stand on both sides it is an assumption. Applies to many `likely` rows.
- **Q15. 五竹亭 (XY07) is not drawn.** S01 has only its beds and pool as in plate 9, at (9360–9424,1173–1201). XY07 is placed there, C. Gone before the drawing, or skipped? No date for its loss; don't read it as gone by 1860.
- **Q16. 海晏堂's east half and the plan's working names.** S01 writes 黄花灯 (黄花阵), 转马台 (线法山), 线法画 (线法墙), 西水?房. Its 海晏堂 has three parts that map poorly onto the plates' single mass. 线法画 has 6 walls per side on S01, Malone says 5, `params.json` 7 pairs.
- **Q17. Halls in the texts and not on the plan.** 寿山殿, 上下天光's hexagon pavilions 饮和 and 奇赏, 大影壁, 文昌阁, 方壶胜境坊, 线法桥, etc. They have rows but no position. Gone by the drawing's date, or not drawn?
- **Q18. Plan labels vs text names at 藻园, 月地云居, 日天琳宇 etc.** See `plan/readings/ym_west/notes.md`. 藏密楼 and 君子轩 share one block; 关帝庙 is far from where the text puts it.
- **Q19. Blocks.** 1560 boxes. Detection: precision about 0.92, recall about 0.85 on three test crops, by eye, before readers fixed what they saw. Spot check of the readers: 12 random `sure` named rows viewed on the plan, label and hall agree on all 12 (seed 1860). "Unnamed" rows may hide named halls; rows of service rooms (如意馆, docks, 买卖街) are schematic.

### Conflicts between written sources

Keep the first of each unless noted.

- **Q20. Name variants.** 九洲清晏 / 九州清晏 / 九州清宴; 蒨园 (S05) / 茜园 (S06); 麴院风荷 (S05) / 曲院风荷; 如园 (S05) / 茹园 (S06); 澹怀堂 / 淡怀堂; 黄花阵 / 万花阵 / 花园 / 黄花灯; 涵远斋 / 涵远楼; 含韵斋 / 含韵轩; 鱼跃鸢飞 / 鱼跃莺飞; 清夏斋 / 清夏堂; 湛清轩 / 湛清斋 / 湛静斋; 凌虚阁 (S06) / 凌虚亭 (S49, S01); 淳化轩 / 淳化閣. 澹泊宁静: S01's third character looks like 清.
- **Q21. Start of the garden.** 1707 (S06, S07, S42) or 1709 (S05, S02). Grant versus building?
- **Q22. Changchun Yuan.** Start 1738 (S06), c. 1745 (S45, S49); done 1749 (S06), 1751 (S02, S49).
- **Q23. Qichun Yuan.** 1770 (S49), 1772 (S06), 1774 (S02). The 1769 in the brief: no source found.
- **Q24. Xiyang Lou.** 1745–59 (S56), 1747–59 (S06), 1747–83 (S42). 远瀛观 at 1783 explains the gap.
- **Q25. Other dates.** 方壶胜境 1740 (S02) / 1738 (S06). 慎德堂 1830 (S54, S50) / 1831 (S41, S43). 安佑宫 stele 庚午, likely misprint for 庚申 (S05 j81:23b). 清晖阁 demolished early Daoguang (S55) / listed (S42). 长春园宫门 reopened 2009 (S136) / 2016 (S142). 绮春园宫门 survived 1860 (S06, S49) / rebuilt after (S02 p.97).
- **Q26. Forms.** 安佑宫 pillars: two (S05 j81:20a), four (S02 p.85, S01), a pair at each of two pailou (S06). 山高水长 九楹 (S05) / two-storey 五楹 (S06). 慈云普护楼 三楹 / 三层. 思永斋 七楹 / 工字殿十七楹. 长桥 13 / 10 spans. 谐奇趣 3 / 2 storeys. 出入贤良门 bridges three (S05) / one (S02). 得全阁 separate (S05) / middle floor (S48). 深柳读书堂 two places or one (S05). 文昌阁 at 天然图画 (S43) / south of 万方安和 (S06). 文源阁 22.72 m / about 26 m. Water inlet SW (S05) / NW (S06). Two 前湖 (S05).
- **Q27. 万字房.** S113 gives 33 rooms of 4.48 m, the same figures S104 gives 田字房; rooms on S01 differ. Possibly borrowed; demoted to C.
- **Q28. 1860 and after, for the site's text.** Main account: 6 Oct French marines at the outer gate of 大宫门, 7–8 Oct looting, 18–19 Oct burning ordered by Elgin and done by 3500 British troops under Michel, French refused (S02 pp.179–188). S06 reports 王闿运 and 李慈铭 blaming local looters first: needs a stronger source before any use. 1900 damage: Eight-Nation forces (S07) / no evidence, local bannermen (S06, S42): state neutrally. 1873 survivors list: S06 alone.

### Today's site and evidence

- **Q29. Hills.** Many hills on S01 are hatched rock, not outlines, so `hills_1860` (55) undercounts. "Over 250 hills, tallest about 15 m" has no source; do not cite it. Attiret gives 20–60 ft (S157). Heights are C. Better: the 1933 and 1963 surveys.
- **Q30. Water.** Class by eye for large regions, automatic (C) for most small ones, unsure on the stained NW bands. 稻田 fields look like ponds (`fields_1860`). R0103, R0117, R0188, R0196, R0448, R0650 may be wrong. Lake surfaces are drawn; widths of narrow canals are as drawn, schematic. Check: 福海 26.4 ha traced vs 28.2 ha OSM today.
- **Q31. Walls.** Rings enclose 335 ha (183 + 69 + 78; run), against 331 ha (S145, S147), 350 ha (S146 352.13). Outer perimeter 9954 m by my polyline vs 11170 m stated (S136); Qing 丈尺 in S11 not yet tested. The modern wall is a rebuild of 1983–2009. Double-wall lane 12.6 m (S116) is not modelled as two lines.
- **Q32. OSM errors.** 线法画 (west of 方河), 养雀笼, possibly 映水兰香; 蓄水楼 point at 116.3055 is 海晏堂's reservoir, not XY02; 谐奇趣's point is 23 m from the ruin. Used only as a hint. Positions come from S01 for all but rows noted `S03`.
- **Q33. Blocked sites.** Try in a browser: gallica.bnf.fr, loc.gov, geographicus, hgl.harvard.edu, maps.princeton.edu, earthworks.stanford.edu, repository.duke.edu (Gamble), hpcbristol.net search, baike.baidu.com, m2m.cr.usgs.gov. mhymy.com and yuanmingyuanpark.cn answered at first, then refused; mhymy reports are partly paywalled. artmuseum.princeton.edu refuses curl; WebFetch worked.

## Resolved

- **Malone's numbers 30 and 36** are swapped on the plan: 36 stands by 澄虚榭 (YM30), 30 off 雷峰夕照 (YM36). Read from the labels.
- **G22** reads 蒨园门, the Changchun side, not 绮园门. Two readers.
- **Datum.** OSM is true WGS84: 2.7 m E, 1.8 m N against Esri over 54 outlines; GLO-30's flat 福海 fits at 0 m E, 4 m N. GCJ-02 here would be 540 m. `north` and `west` in `site_glo30.npz` are cell centres.
- **SL3.** No slip in Qichun Yuan: Malone's footnote is about 如意馆.
- **别有洞天 in Qichun** at (7121,7385) is a gate label, not YM34.
