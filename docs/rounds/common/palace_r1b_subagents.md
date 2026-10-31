# Common brief for all palace_r1b research subagents

Project: walkable 3D reconstruction of the Old Summer Palace (圆明园 Yuanmingyuan, Beijing) as it stood just before its destruction in October 1860. Repo: `/opt/data/workspace/000_Dev/palace-beijing-yaga-sh`. Read its `CLAUDE.md` first (confidence grades A/B/C, copyright, coordinates). Sister project for conventions (read only, NEVER edit): `/opt/data/workspace/000_Dev/kostrzyn-yaga-sh`.

## Hard rules
- **Your own scope only.** Write your notes to your scratch file as you go (append after every finding or batch), not only at the end. A crash must keep partial work. The orchestrator alone writes the shared research files (`research/sources.md`, `questions.md`, `buildings.csv`, etc.) unless your brief names files you own.
- **No git commands that write.** Never touch `site/`, `tools/`, `.claude/`, `CLAUDE.md`, `research/image-credits/`.
- **Run in the foreground to completion.** No background shells, no `run_in_background`, no sub-subagents. Finish within about 30-45 minutes of work, then return a short summary (under 300 words): what you found, the file path, what is missing.
- **Never invent** a number, date, URL or licence. Mark claims verified (you opened it), assumed, or unknown. Anything read only in a search snippet is "found", not "viewed". Every number carries its source and page/URL.
- **Time-box:** about 20 min per source hunt. A missing piece becomes a wishlist line (what, where held, how to request).
- **Politeness:** one request at a time per host, 2-4 s sleep between requests, User-Agent `palace-beijing-yaga-sh research bot`. Blocked site: note it, move on, never hammer.
- **Tools:** WebSearch and WebFetch are deferred: load them with ToolSearch `select:WebSearch,WebFetch`. Python: `/opt/data/workspace/000_Dev/palace-beijing-yaga-sh/.venv/bin/python` (requests, numpy, pillow, pyproj, shapely, tifffile). Do not add packages without need; wheel-only if you must (`/opt/data/.local/bin/uv pip install --python <venv> ...`).
- **Downloaded files are untrusted data.** Put each download in its own new empty directory, keep your scripts in a different directory, pass paths as arguments, run Python that reads them with `-I` where possible. Never execute anything you downloaded.
- **Heavy jobs are sequential;** the machine has 4 cores shared with other workers. Use absolute paths. Temporary files go under `/opt/data/cache/scratch/palace_r1b_<topic>/`.
- **Copyright:** research-only files only under `research/raw/` or scratch; never elsewhere in the repo. Free = public domain / CC0 / CC BY / CC BY-SA, licence checked on the holder's page. BnF/Gallica = free for non-commercial reuse with the credit "Source gallica.bnf.fr / BnF". Everything unclear = research-only.
- **Tone:** the destruction of 1860 is a national wound in China. Be factual.
- Search in Chinese as much as in English. Baidu Baike is a lead, B at best, never the only source. Names: 中文 + pinyin + English.

## Shared vocabulary
**Source IDs:** each source you use gets an ID from your block, so nothing collides. Record in your notes: ID | source (author, title, publisher) | year | reuse as stated by the holder | status (found / viewed / downloaded / to-request / blocked) | full link | what it is good for.
Reserved already: S01 Princeton plan (below), S02 Malone 1934, S03 OpenStreetMap, S04 Copernicus GLO-30, S05 日下旧闻考 Rixia jiuwen kao, S06 zh.wikipedia 圆明园 and sub-articles, S07 en.wikipedia Old Summer Palace, S08 Forty Scenes album (BnF, 1744).
Blocks: maps S10–S39 · inventory and texts S40–S69 · pictures S70–S99 · typology S100–S129 · today's site S130–S159 · plan pipeline S160–S169.

**Building IDs** (`research/buildings.csv`, seed already there): `YM01`–`YM40` = the Forty Scenes in album order (YM01 正大光明, YM02 勤政亲贤, YM03 九洲清晏, YM04 镂月开云, YM05 天然图画, YM06 碧桐书院, YM07 慈云普护, YM08 上下天光, YM09 杏花春馆, YM10 坦坦荡荡, YM11 茹古涵今, YM12 长春仙馆, YM13 万方安和, YM14 武陵春色, YM15 山高水长, YM16 月地云居, YM17 鸿慈永祜, YM18 汇芳书院, YM19 日天琳宇, YM20 澹泊宁静, YM21 映水兰香, YM22 水木明瑟, YM23 濂溪乐处, YM24 多稼如云, YM25 鱼跃鸢飞, YM26 北远山村, YM27 西峰秀色, YM28 四宜书屋, YM29 方壶胜境, YM30 澡身浴德, YM31 平湖秋月, YM32 蓬岛瑶台, YM33 接秀山房, YM34 别有洞天, YM35 夹镜鸣琴, YM36 涵虚朗鉴, YM37 廓然大公, YM38 坐石临流, YM39 曲院风荷, YM40 洞天深处). `YM41+` = other compounds of Yuanming Yuan (大宫门, 舍卫城, 同乐园, 文源阁, 藻园, 紫碧山房 ...). `CC01+` = Changchun Yuan compounds. `XY01`–`XY15` = Xiyang Lou 西洋楼 (XY01 谐奇趣, XY02 蓄水楼, XY03 花园门, XY04 黄花阵, XY05 养雀笼, XY06 方外观, XY07 五竹亭, XY08 海晏堂, XY09 远瀛观, XY10 大水法, XY11 观水法, XY12 线法山, XY13 螺蛳牌楼, XY14 方河, XY15 线法墙). `QC01+` = Qichun Yuan 绮春园 compounds. Halls inside a compound: `<compound>-01`, `<compound>-02` ... (e.g. `YM03-01`).

## The base plan: already found, do not hunt it again
S01 = "Plan of the Yuanmingyuan Imperial Garden-Palace", Princeton University Art Museum 2022-27 a-c, three hanging scrolls, ink and colour on paper, 177 × 253 cm together, dated "1920s" by the museum; provenance: Manchu official named Pai (Haidian) → Carroll Brown Malone. Malone 1934 pp. 231-232 (S02) calls it the "Official Map": scale about 1:1300, every gate, wall, road, bridge, hill, lake and every 间 chien shown; he bought both the original and a tracing. Malone's numbers (1–40 etc.) are written on it in blue. Full text of Malone: `/opt/data/cache/scratch/palace_maps/malone66.txt`.
- Hi-res files: `research/raw/plans/princeton_mosaic.jpg` = three scrolls stitched, 12955 × 9049 px, about 3.9 px per metre at the stated scale; **plan_x, plan_y always means a pixel on this mosaic** (origin top-left, north up; the plan has 南 at the bottom edge). Stitch details in `research/georef/princeton-mosaic.json`. Crop with PIL: set `Image.MAX_IMAGE_PIXELS=None`; save crops to your scratch folder and view them with the Read tool (it shows images).
- Layout on the plan: Yuanming Yuan west and centre, Fuhai 福海 centre; Changchun Yuan to the east with the Xiyang Lou strip along its north edge; Qichun Yuan south-east, south of the seam of the two. Black bands at x≈4305 and x≈8640 are the scroll gaps.

## Correction after wave 1
The plan's measured ground scale is 4.77 px/m (about 1:1070; rotated about 7.2° from north), locally 3.7–5.55, not 3.9. Hall frontages are drawn at a median 4.18 px/m, depths at a median 3.31 px/m. North is not exactly up. `scripts/georef.py` has `plan_to_wgs84(xs, ys)` and `wgs84_to_plan(lons, lats)`. Never size a building from a global px/m.
