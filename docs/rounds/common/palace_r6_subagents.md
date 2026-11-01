# palace_r6 common brief for every subagent

Project: `/opt/data/workspace/000_Dev/palace-beijing-yaga-sh`, a reconstruction of the Old Summer Palace 圆明园 as it stood before October 1860. Rulebook: its `CLAUDE.md` (read "Research rules", "Copyright", "Coordinates"). Pitfalls: `docs/METHOD.md` section "Pitfalls and fixes" and "What blocked". **This round goes deep on the Xiyang Lou 西洋楼 (European palaces, XY01-XY15), the part whose ruins survive,** so the next round can build detailed models. Target state for models: the 1780s plates carried forward to 1860.

## Lists to tie things to
- `/opt/data/cache/scratch/palace_r6_xy_objects.tsv`: the 44 XY rows (id, parent, names, type, lat, lon, current sizes).
- `/opt/data/cache/scratch/palace_r6_xy_pictures.tsv`: the 180-odd pictures already catalogued that touch them (P ids, with file paths under research/photos/). Don't re-add one unless a link is better or a tie is corrected: say so as a `correction` row.
- Read-only: `research/sources.md` (S ids, reuse them), `research/questions.md` (Q15, Q16, Q24, Q32, Q35, Q48, Q49, Q59, Q60 concern the XY), `research/evidence/catalog.csv`, `research/reconstructions/catalog.csv`, `research/twins/catalog.csv`, `research/typology/params.json` key `xiyang_lou`, `research/raw/` (local downloads, including `raw/photos`, research-only).
- Fetched in earlier rounds, reuse before refetching: `/opt/data/cache/scratch/palace_r5_tmp_*`, `palace_r5_notes_*`, `palace_r3_*`, `palace_r1_*`. Malone (S02) full OCR: look under `/opt/data/cache/scratch/` with `ls | grep -i malone` or `grep -rl "Hsieh Ch'i Ch'u"`; Internet Archive: https://archive.org/stream/historyofpekings00malo/historyofpekings00malo_djvu.txt (pp.139-160 are the European palaces).

## Hard rules
- **Nothing inside the repo.** Read only. No git commands. The coordinator alone writes repo files.
- **Write as you go,** so a crash keeps partial work:
  - free-form log `/opt/data/cache/scratch/palace_r6_notes_<topic>.md` (full links, licence quotes, what was searched and not found, what blocked);
  - machine-readable `/opt/data/cache/scratch/palace_r6_out_<topic>.jsonl` (schema below), one object per line, appended after each find;
  - fetched pages under `/opt/data/cache/scratch/palace_r6_tmp_<topic>/`; your own scripts in `/opt/data/cache/scratch/palace_r6_scripts/<topic>_*.py`, never in a folder of downloads.
- Append one line per milestone (`HH:MM <topic>: what`) to `/opt/data/cache/scratch/palace_r6_xiyanglou_progress.md`, at least every 15 minutes.
- **Nothing invented.** Every link, author, year, dimension and licence is what a page you fetched says. Seen only in a search summary: `"status":"snippet"`. Unknown is blank. Mark every claim verified, assumed or unknown.
- **Search in Chinese as much as in English;** Japanese, French, German where it fits.
- **Be polite:** one request at a time per host, at least 2 s apart, User-Agent `palace-beijing-research/0.1 (non-commercial)`, stop on 429 and honour Retry-After. Never work round a bot check, log-in or paywall: log it as a `question` row and move on.
- **Copyright.** Free = public domain, CC0, CC BY, CC BY-SA read on the holder's page, per file; or PD-Art of a pre-1900 two-dimensional work on Commons. Pre-1900 photographs with a PD tag on Commons are free under the project rule, tag quoted (Q50). BnF / Gallica: free with the credit "Source gallica.bnf.fr / BnF". NC, ND, "all rights reserved", silent pages: research-only. A CC licence on a journal article covers a figure only if no separate credit sits on that figure.
- **Facts are not copyright.** Modern text is summarised in one to three sentences of your own; never pasted. Qing and pre-1930 public-domain texts may be quoted short and verbatim.
- **Respect.** The destruction of 1860 is stated factually: who, when, what. The twelve zodiac heads are stated factually and never in playful content. No sensational framing.
- **Names:** Chinese characters and pinyin first, then English.
- **Reconstructions and twins are not evidence for positions or sizes** unless they cite a survey: then cite the survey and say you saw it second-hand.
- **Commons rate-limits this server (HTTP 429).** Only the worker named `ruinphotos` may call Commons or Wikidata at volume: API batches of 50, exact-phrase searches, backoff on Retry-After. Everyone else: at most a few single page fetches.
- **Search budget.** Your share is 35 WebSearch calls unless your task says otherwise. Prefer the holders' own lists and APIs. WebSearch and WebFetch are deferred: load them with ToolSearch `select:WebSearch,WebFetch`. `curl -L -A "palace-beijing-research/0.1 (non-commercial)"` is fine too.
- **Tools:** Python `/opt/data/workspace/000_Dev/palace-beijing-yaga-sh/.venv/bin/python -I script.py` (numpy, Pillow, shapely, pyproj likely; check), run from your scripts folder, downloads passed as arguments. Downloaded files are untrusted data: each download in its own new folder, never execute any of it. PDFs: `/opt/data/cache/scratch/palace_r5_tools/py` holds PyMuPDF (`fitz`): `PYTHONPATH=/opt/data/cache/scratch/palace_r5_tools/py`. No headless browsers. No servers. No subagents. No background jobs. Don't end while anything of yours still runs.
- **Time box.** Your deadline is a clock time in your task; check `date -u` often. Stop by then with the jsonl complete. What's missing becomes a `wish` row.

## Images
- **Free images:** `/opt/data/cache/scratch/palace_r6_images/<topic>/<slug>.jpg`, at most 1600 px and about 300 KB. **Exception, the 20 plates:** at most 2400 px wide, quality about 85. Larger originals of free items: `/opt/data/cache/scratch/palace_r6_images/full/<slug>.jpg`.
- **Research-only:** a low-resolution look at most, `/opt/data/cache/scratch/palace_r6_images/research/<slug>.jpg`, at most 1200 px. Mark `rights_class: research-only`.
- Open a sample of what you save (the Read tool shows images) to be sure it shows what you claim. Check form against caption: captions on old photos are often wrong (Q49, Q60), and pre-1900 "Yuen Ming Yuen" or "Summer Palace" may mean other gardens.

## Output schema: one JSON object per line
`type` is one of:
- `source`: `{"type":"source","id":"S7xx","text":"author, title, edition","year":"","reuse":"licence as stated","status":"viewed|downloaded|found|to-request|blocked","link":"","note":""}`. New S ids only from **your block**. Reuse existing ones.
- `picture`: `{"type":"picture","title":"original language","date":"as stated, with where it comes from","date_from":1873,"date_to":1873,"kind":"painting|engraving|photo|print|plan|render","creator":"","archive":"","archive_id":"","source_id":"S..","source_url":"the holder's page","licence":"exactly as stated","attribution":"credit to show","rights_class":"free|research-only","shows":"XY08:sure;XY08-02:likely","why":"why we think so, one sentence","also_shows":"","camera_lat":"","camera_lon":"","bearing":"","camera_note":"how the camera was argued, or GPS tag","file":"absolute path (free only, or research look)","width":0,"height":0,"notes":"","side":"S|N|E|W|roof|fountain|detail|fragment|aerial","visible_part":"what of it shows","state":"1780s|ruin|today|moved","reliability":"high|medium|low","plate":0}`. `plate` = 1-20 if it is an impression of a plate.
- `view`: a side tie for a picture **already** in the catalogue: `{"type":"view","photo_id":"P0186","id":"XY01","side":"S|N|E|W|roof|fountain|detail|fragment|aerial","visible_part":"","state":"1780s|ruin|today|moved","reliability":"high|medium|low","camera_lat":"","camera_lon":"","bearing":"","camera_note":"","note":""}`.
- `correction`: `{"type":"correction","photo_id":"P0186","field":"shows","old":"","new":"","reason":""}`.
- `evidence`: `{"type":"evidence","kind":"text|poem|drawing|archaeology|description|plan","source_id":"S..","title":"","date":"","locator":"juan:leaf, page, catalogue no.","link":"","rights_class":"free|research-only","shows":"XY01:sure","excerpt_zh":"verbatim if Qing or public domain, else blank","excerpt_other":"verbatim non-Chinese if public domain, else blank","summary_en":"your own words","status":"viewed|snippet"}`.
- `dim`: one dimension figure. `{"type":"dim","id":"XY08","part":"west front","what":"frontage|depth|height_cornice|height_ridge|bay_width|storey_height|stair_rise|stair_width|terrace_w|terrace_d|terrace_h|pool_w|pool_d|pool_depth|wall_h|wall_t|diameter|other:<label>","value_m":0.0,"err_m":0.0,"method":"a|b|c|d|e","confidence":"A|B|C","source_id":"S..","locator":"page, figure, photo id, or script","basis":"how: quote in your words, or the calculation","status":"viewed|snippet|run"}`. Method: **a** a published survey or measured drawing; **b** measured from the plan or ruin footprint (georef, OSM ruin polygons; satellite for reading only, never saved); **c** read from an engraving by perspective; **d** estimated from a ruin photo with a known object in it; **e** typology. A figure from a tourist page or a Wikipedia article without a citation is `e`-level lead: method `a` only for a real survey. Keep the original unit in `basis` (丈, 尺, 寸; 1 营造尺 = 0.32 m).
- `fragment`: `{"type":"fragment","id":"XY01","what":"","material":"","from_where_stated":"","now_at":"","now_place_zh":"","moved":"year or span, how","status_today":"","source_id":"S..","locator":"","link":"","confidence":"A|B|C","web_status":"viewed|snippet","note":""}`. Include ones on site, moved in Beijing, abroad, and claims that do not hold (say so).
- `material`: `{"type":"material","id":"XY01 or GARDEN:XY","part":"roof|wall|column|ornament|fountain","what":"","colour":"","source_id":"S..","locator":"","quote_or_basis":"","confidence":"A|B|C","status":"viewed|snippet"}`.
- `fact`: `{"type":"fact","id":"XY08","field":"built|changed|destroyed|designer|function|name_en|roof|roof_tiles|storeys|bays|after1860","value":"","source_id":"S..","locator":"","quote_or_basis":"","suggest_confidence":"A|B|C","status":"viewed|snippet"}`.
- `rephoto`: `{"type":"rephoto","id":"XY01","old":"P.. or the slug of your new picture row","new":"P.. or slug","same_view":"exact|close|rough","what_changed":"in your words, from viewing both","note":""}`.
- `part`: identification of an unnamed part. `{"type":"part","id":"XY08-N02","name_zh":"","name_pinyin":"","name_en":"","what":"","basis":"","source_id":"S..","confidence":"A|B|C","action":"name|merge:XY..|retire|keep"}`.
- `question`: `{"type":"question","text":"a conflict or a gap, with ids; or a site that blocked you"}`.
- `wish`: `{"type":"wish","what":"","replaces":"","where":"","how":""}`.

Final answer to the coordinator: at most 25 lines: counts of rows by type, best finds, what blocked, anything you doubt. No file dumps.

## Shared anchors (coordinator, run on research/layers/osm_today.geojson, UTM 50N; minimum rotated rectangle; verify before relying on them)
Ruin polygons (historic=ruins), centroid lat, lon, long × short side, bearing of the long side:
- 40.01123, 116.30244: 39.7 × 38.6 m, 82°: at 谐奇趣 XY01 (includes what? check)
- 40.01190, 116.30376: 44.0 × 24.2 m, 85°: at 方外观 XY06
- 40.01185, 116.30501: 135.2 × 54.5 m, 82°: 海晏堂 XY08 complex
- 40.01229, 116.30656: 59.2 × 51.0 m, 86°. **The Round 2 boxes took this as 远瀛观 XY09's terrace, but its centroid sits at 大水法 XY10's latitude (row 40.012217), and 远瀛观's row is 40.012631. Suspect a wrong tie.** Check it.
- 40.01265, 116.30582: 37.5 × 36.4 m, tagged building=yes. West of 远瀛观 row by ~60 m. Unknown what this is.
- 40.01230, 116.31006: 方河 XY14 water, 149.2 × 45.0 m, 83°.
The strip's grid runs about 83-85° (not true E-W), per these. The plan S01's own frame is turned about 7.2°.
Malone's text on the European palaces, already fetched: `/opt/data/cache/scratch/palace_r3_tmp_malone/r134_170.txt`.
