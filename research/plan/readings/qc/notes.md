# Plan reader notes: qc (Qichun Yuan 绮春园)

All positions are S01 mosaic px. Polygon overlay check: `tiles/check_polys.jpg`.

## Coverage
- Tiles at 1x over the whole box, plus zoomed crops of every label (`tiles/m*.jpg`, `z_a*.jpg`).
- The garden proper runs about x 5820-10550, y 4720-8650. The rest of the box is Changchun (澹怀堂, 如园, its gate) or blank.
- No Malone blue numbers appear on Qichun Yuan, so `malone_no` is empty throughout.
- `QC30`, `QC32`, `QC36` have an empty polygon on purpose: they stand inside `QC04` and a polygon would overlap it.
- 42 blocks stay outside every polygon. They are bridges already rejected, or scattered unlabelled small halls.

## The slip: not in Qichun Yuan
- Malone's sentence "The Official Map shows a new and presumably later arrangement of the buildings on a paper pasted over the old one" is the end of the footnote on the **Ju I Kuan (如意馆), group 40**, not on Qichun Yuan. The next footnote is the one about Qichun Yuan. They sit together on p. 96, which explains the mix-up.
- Malone App. II confirms: pasted paper "in more than one place ... as in Number Forty". The other place he names is the 九洲清晏 island (p. 72).
- I looked for a slip here all the same: 1x tiles, a local-brightness map and a red-blue tint map of the whole box. There is no cut paper edge and no patch whose ink differs. SL3 can close as "not present on this copy, and no text says it should be".
- Things that are not slips:
  - the diagonal band (6260,4700)-(5380,6740): a tonal band in blank paper with no ink affected, so a fold or repair
  - a horizontal crease at y about 5850, x 5300-5730
  - a faint pencil rectangle at x 10180-10400, y 4660-4940
  - grey lines beside the double wall at y about 4660-4710

## Dating evidence
Drawn, so the plan is later than:
- 河神庙 and its twin temple: 1813-17 (S47)
- 大宫门, the "new gate": 1809 (lead 5910f5)
- 西爽村 and 含晖 parts: merged in Jiaqing 4 and 16 (lead 5910f5)
- 招凉榭 and 凌虚亭: named among the later additions after the thirty scenes (lead 5910f5)

Before the Tongzhi works (1873):
- The plan writes 清夏斋, not 清夏堂.
- No 天地一家春 anywhere.

So the names are late Jiaqing or later and pre-Tongzhi. Nothing in this area narrows it further to one reign.

**Possible Daoguang sign, an inference only:**
- There is no 敷春堂 label. The palace block reads 集禧堂, 永春堂, 问月楼.
- 敷春堂 was rebuilt in 1821 for the Empress Dowager, and its stage was turned into a hall (yuanmingyuanpark report, `palace_r1_site/raw/...4483509`). The plan shows no stage shape in the block, which fits.
- I found no text giving 集禧堂 or 永春堂. Wishlist: Yangshi Lei plans of 敷春堂, which would settle whether these are renamed halls.

Named in the texts but not labelled on the plan:
- 敷春堂, 庄严法界, 展诗应律, 卧云轩, 延英论道, 龙王庙
- 19 names have `read=not_found`, most of them thirty-scene names such as 鉴德书屋, 竹林院, 般若观. Those were probably names of single halls or plaques; the plan labels fewer of them.
- Lead 5910f5 also lists 烟雨楼; no such label either.

## Conflicts between plan and text
- **河神庙:** S47 says it stands west of 惠济祠. On the plan it is the east half of the pair, and the west half reads ?神天?. Either S47 or my match of the west half to 惠济祠 is wrong.
- **生冬室:** the inventory says 7 bays. I count 3 plus porch on the main hall, with long side galleries.
- **凌虚阁 / 凌虚亭:** the plan says 亭.
- **淙玉轩:** the first char may be 涼 on the plan.
- **G22 in gates.json** ("绮园门") reads 蒨园门: the Changchun 茜园 side.
- **别有洞天 at (7121,7385)** is a gate label inside Qichun Yuan. It is not YM34 (pred 7956,4333). Do not merge them.

## Reading problems
- Characters left as `?` and the readings I considered are in each row's note. Worst: 翠???? (9815,6820), ?神天?, ?吟楼, ??斋, ?流 at (10185,7720).
- ?流 has no row in `named.csv` because no hall stands next to it; it may be a stream name.
- Faint pencil characters stand beside some ink labels: 雨 at 喜雨山房, 翰 at 翰林花园, 待 at 待旭轩, 眺 at ?吟楼, one below 松路??. A later hand was probably checking or copying them. The 眺 is my only reason to suspect that label starts with 眺.
- 石路 appears at (9570,8080), (9095,8020) and (6620,8780) and is a road label only.
- Three yards east of the wall read 地 plus a ditto mark, or 池. Unresolved.
- No water, island or hill names are written in this garden, so `water_name` and `hill_name` are empty. The 天心水面 island name is from text only.

## Weak matches to treat with care
- `QC16` 湛清轩, `QC20` 展诗应律, `QC49` 水心榭: guesses from position or form only (C).
- `QC26` 天心水面 is a stronger match: S42's four-sides-water and hills NE/SW/SE both fit the island.
- `QC10` 仙人承露台: rests on the platform form and its position between 涵秋馆 and 凤麟洲.
- `QC04` polygon is sure as a block, but the name 敷春堂 on it comes from text order only. `QC04-01` (the largest hall) is a guess.
- Unlabelled names in `named.csv` are in parentheses and come from text order or form, for example the halls of 正觉寺.

## Schematic areas
- Rows of identical plain halls: 西住所, 东住所, the service courts east of the palace block, 四局.
- 翰林花园 shows only ponds and hills with no building.
- 撒马道 is open ground.
- The garden halls otherwise look surveyed, with varied bay counts. 正觉寺's central 7 bays of 最上楼 match the text.

## Source note
"lead 5910f5" is `/opt/data/cache/scratch/palace_r1_typo/dl_b_5910f5/page.txt`, an unattributed web page used as a lead only. "S42 nnnnn" is mhymy.com dasl page nnnnn in `palace_r1_site/raw/`.
