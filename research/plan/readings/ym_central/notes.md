# ym_central notes (S01 plan reading, x 1700-4350, y 2900-6300)

## Reading convention I used
A label in a court names the hall on the **north** of that court (the hall facing south onto it). Test: 同顺堂 has only a 3-bay gate south of its court, 圆明园殿 has only the lake, 韶景轩 is the 5x5 hall north of its label. Halls chosen this way are assumptions where the row on the other side is also a hall (前殿, 洞明堂, 飞云轩).

Labels come in two inks. Dark ones are easy. On 茹古涵今 and in the 长春仙馆 ?香? court they are pale; they read after a contrast stretch only.

## Slip SL1 and Malone
Malone p.72 caption (S02): a slip showing a later alteration of the Emperor's private apartments is **folded up over the Back Lake** in his photograph. Note p.80: such a slip on this island, shown on map p.72.

On this scan I find **no slip**: no paper edge, no shadow, nothing over 后湖. Measured median grey in this run: axis courts 196 and 198; other courts on this and other islands 191-200 (后殿 193, 承恩堂 200, 勤政殿 200, 茹古涵今 191); 后湖 water 199. So the brightness argument in `slips.json` SL1 does not separate this court. The faint characters in both axis courts look like pale labels, the last char like 殿, unreadable: they resemble the pale labels of 茹古涵今, which is not on a slip. I rate SL1 as not supported.

Open: the slip may be lost, or may lie flat, glued down. If flat, what we see is the later state. I cannot tell from this scan. Comparing with Malone's photo on p.72 would settle it.

## Dating evidence
- **慎德堂, 1831 (date from the brief, not checked by me):** no label. B0835, 5 bays x 3 rolls, by far the largest footprint on the west of the island, is the only hall on the large west court, which is where Malone p.80 puts 慎德堂. If right, the west of the island shows the state after 1831. Reliable only as far as that identification.
- **Labels 同顺堂, 承恩堂, ?顺堂, 福寿仁恩, 七间殿, 前殿, 后殿** replace the 1744-era names of the text in the east and west of the island. None of 乐安和, 清晖阁, 露香斋, 茹古堂, 松云楼, 涵德书屋, 天地一家春 is written. So these parts differ from the 日下旧闻考 text and are later than it, or use another naming; I have no date for those labels.
- **同道堂 (Xianfeng, per S42;S43):** not written. Its stated position, 3 bays west of 九洲清晏殿, is drawn, but labelled 福寿仁恩. Theatres 壶天仙籁 and 同道堂戏台 are not recognisable. No positive Xianfeng marker in my area.
- **五福五代堂** on 天然图画: the inventory has 五福堂. I recall the longer name as late Qianlong (1780s); assumed, not checked. So the plan is later than that here.
- **保合太和** 9 x 3 cells against the text's 3 bays: the plan shows something much larger. Date unknown.
- **Missing but in the text:**
  - 寿山殿 (YM01-10): behind 正大光明 only rock ridges and blank ground
  - 上下天光's two hexagon pavilions 饮和 and 奇赏: nothing on the lake but a small 3-cell pier
  - 大影壁 (YM41-12): not drawn, at least to y 6650
  - 文昌阁 (YM05-08): not found

**Which reign:** after 1831 if B0835 is 慎德堂, and otherwise after about the 1780s. I cannot narrow it inside Daoguang to Xianfeng, nor exclude a later copy of an earlier survey. The hand is uniform across the island.

## Conflicts between plan and text
- **藤影花丛:** inventory has it as the 正殿 of 长春仙馆. On the plan it is its own far-west court, with 林虚桂静 in the next court and 长春仙馆 at the east. The order matches the text's 含碧堂/林虚桂静/古香斋 being west of the main court, so I read the inventory as wrong on this point.
- **Shifted terms:** where the text has 朝房 (forecourt) the plan says 配殿; where the text has 配殿 (main court) the plan says 穿堂.
- **Two gates on the road** read 东水?门 and 西水?门. By position they could be the text's 东西如意门, but the second char does not look like 如 (compare the clear 如 in 如意桥 and 如祈应祷).
- **Both small gates by 大宫门** read 左门.
- **?静斋** stands where the text has 竹深荷净.
- **Bay counts:** see `named.csv`; main differences 长春仙馆 7 against 5, 茹古涵今 6 against 5, 九洲清晏殿 5 against 7, 勤政殿 4 against 5, 上下天光 9 cells against 3.
- **知鱼亭:** kiosk in the NW pond cell, text says 东北.

## Not identified on the plan (no row in named.csv)
Text names with no label and no good position: YM01-04 军机处, YM01-07 翻书房 (NEW-07 is a candidate), YM01-10; YM03-04 to -10, -12, -14 to -20; YM05-02, -06, -08; YM09-03, -08; YM10-02, -05, -06, -07; YM12-04, -08, -09, -10; YM13-02 to -09 (arm names); YM14-03, -04, -06 to -13; YM41-03, -10, -11, -12.

## Outside or at the edge
- **YM15 山高水长:** not in my box. `pred` 1974,5613 is blank land and a stream. B0826 at x 1569 fits. West reader decides.
- **抱朴草堂 (YM44-07):** label at about (4300,2905), hall B0510 just north of my box.
- **天神坛:** label at about (3040,2870), north of my box.
- **B0528 (1979,3002):** small hall on a lobe west of 全璧堂, in no polygon; unnamed.
- **South of my box:** 石路 and a timber-fence label 栊?木 at about (3640,6530); fence lines x 2950 and x 3660.

## Schematic areas
South of the road (膳房, 清茶房, 银库, 南书房, the two large plots) is blank cells with labels only: no buildings drawn. 十三所 is repetitive. The nine islands and 勤政亲贤 are drawn bay by bay.

## Class notes
`features.csv` has water_fix rows. The cells north of the 大宫门 wall line are classed outside but lie inside the gate. The 坦坦荡荡 pond cells are classed land or court; the north-east pond cell had no region at my test point (2620,4130).

Tiles and my helper scripts are in `tiles/` and `tools_own/`; rerun `tools_own/write_*.py` to regenerate the CSVs.
