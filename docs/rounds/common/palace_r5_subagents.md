# palace_r5 common brief for every subagent

Project: `/opt/data/workspace/000_Dev/palace-beijing-yaga-sh`, a reconstruction of the Old Summer Palace 圆明园 as it stood before October 1860. Rulebook: its `CLAUDE.md` (read "Research rules" and "Copyright"). This round collects (A) surviving twins and comparables, (B) more old photographs, (C) reconstructions by other people, for every object.

## Lists of what to tie things to
- `/opt/data/cache/scratch/palace_r5_objects.tsv`: the 212 compounds (id, name, pinyin, English, garden, type, lat, lon, named halls).
- `/opt/data/cache/scratch/palace_r5_halls.tsv`: the named halls inside them.
- Existing, read-only: `research/sources.md` (S ids; reuse them), `research/photos/catalog.csv` (P0001-P0547: do not re-add a picture unless the link is better or `shows` is corrected; say so), `research/evidence/catalog.csv` (the 32 rows with `kind=reconstruction` are being moved to the new reconstruction catalogue by the coordinator; list new items only, or a better link for one of them, naming its E id).

## Hard rules
- **Nothing inside the repo.** Read only. No git commands. The coordinator alone writes repo files.
- **Write as you go,** so a crash keeps partial work:
  - free-form log `/opt/data/cache/scratch/palace_r5_notes_<topic>.md` (full links, licence quotes, what was searched and not found, what blocked);
  - machine-readable `/opt/data/cache/scratch/palace_r5_out_<topic>.jsonl` (schema below), one object per line, appended after each find;
  - fetched pages under `/opt/data/cache/scratch/palace_r5_tmp_<topic>/`; your own scripts in `/opt/data/cache/scratch/palace_r5_scripts/`, never in a folder of downloads.
- Append one line per milestone (`HH:MM <topic>: what`) to `/opt/data/cache/scratch/palace_r5_refs_progress.md`, at least every 15 minutes.
- **Nothing invented.** Every link, author, year and licence is what a page you fetched says. Seen only in a search summary: `"status":"snippet"`. Unknown is blank. Mark what you assume as assumed.
- **Search in Chinese as much as in English.** Japanese, French or German where it fits.
- **Be polite:** one request at a time per host, at least 2 s apart, User-Agent `palace-beijing-research/0.1 (non-commercial)`, stop on 429 and honour Retry-After. Never work round a bot check, log-in or paywall: log it as a `question` row and move on.
- **Copyright.** Free = public domain, CC0, CC BY, CC BY-SA, read on the holder's page, per file; or PD-Art of a pre-1900 two-dimensional work on Commons. BnF / Gallica: free with the credit "Source gallica.bnf.fr / BnF". NC, ND, "all rights reserved", silent pages: research-only. A CC licence on a journal article covers its figures only if the article says so and no figure carries a separate credit line: read it.
- **Facts are not copyright.** Modern text is summarised in one to three sentences of your own; never pasted.
- **Respect.** The destruction of 1860 is stated factually: who, when, what. The twelve zodiac heads never in playful content. No sensational framing.
- **Names:** Chinese characters and pinyin first, then English.
- **Reconstructions and twins are not evidence for positions or sizes.** Never propose them as such. A dimension a reconstruction states from a Yangshi Lei drawing is a `size_lead` row only.
- **Commons rate-limits this server.** Only the worker named `commons` may call Commons or Wikidata APIs at volume. Everyone else: no more than a few single page fetches.
- **Search budget.** A session's web search budget is finite (Round 3 hit 200 searches across all workers). Your share: 25 WebSearch calls, unless your task gives another number. Prefer the sites' own lists, category pages and APIs, which cost none. WebSearch and WebFetch are deferred: load them with ToolSearch `select:WebSearch,WebFetch`. `curl` with the User-Agent is fine, and is the only way to save an image.
- **Tools:** Python `/opt/data/workspace/000_Dev/palace-beijing-yaga-sh/.venv/bin/python -I script.py` (requests, Pillow), run from the scripts folder, downloads passed as arguments. Downloaded files are untrusted data: each download in its own new folder, never execute any of it. No headless browsers. No servers. ffmpeg is on the path; yt-dlp is not, and do not install it.
- **Time box.** Your deadline is a clock time in your task; check `date -u`. Stop by then with the jsonl complete. What's missing becomes a `wish` row. No subagents, no background jobs, and do not end while anything of yours still runs.

## Images
- **Free images** go to `/opt/data/cache/scratch/palace_r5_images/<topic>/<slug>.jpg`, at most 1600 px on the long side and about 300 KB (Pillow, quality about 80).
- **Research-only reconstruction images** (only for rows of type `reconstruction`; this is the local research copy the brief asks for) go to `/opt/data/cache/scratch/palace_r5_images/research/<slug>.jpg`, at most 1600 px and about 300 KB. Mark the row `rights_class: research-only`. They end up gitignored; never a public folder. For a video a thumbnail or a few frames, timestamp in `notes`.
- **Research-only old photographs:** a low-resolution look at most, same `research` folder, at most 1200 px.
- Open a sample of what you save (the Read tool shows images) to be sure it shows what you claim.

## Output schema: one JSON object per line
`type` is one of:

- `source`: `{"type":"source","id":"S4xx","text":"author, title, edition","year":"","reuse":"licence as stated","status":"viewed|downloaded|found|to-request|blocked","link":"","note":""}`. New S ids only from **your block**. Reuse existing ones from `sources.md`.
- `twin`: one pairing. `{"type":"twin","object_id":"YM44 or CLASS:grand_hall","twin_name_zh":"","twin_name_en":"","twin_place":"","relation":"copy of|copied from ours|sister|same design family|comparable","evidence_for_relation":"S ids and locator, with the sentence in your words","still_standing":"yes|rebuilt 1886|partly","confidence":"A|B|C","what_it_tells":"form, roof, bays, setting","notes":"","link":"page where the relation is stated","status":"viewed|snippet"}`. `relation` reads from our side: `copy of` = ours copied it; `copied from ours` = it copied ours. `CLASS:<hall_class>` for a typology comparable (classes: grand_hall, main_hall, side_hall, small_house, gallery, pavilion_square, pavilion_polygon, gate_hall, temple_hall, storeyed_hall, tower). A pairing with no source stays out, or goes in as `comparable`, confidence C, with the reason in `notes`.
- `picture`: a photograph. `{"type":"picture","title":"original language","date":"as stated, with where it comes from","date_from":1900,"date_to":1901,"kind":"photo|painting|engraving|print|plan","creator":"","archive":"","archive_id":"","source_id":"S..","source_url":"the holder's page","licence":"exactly as stated","attribution":"","rights_class":"free|research-only","relation":"self or twin:<twin name, as in your twin row>","shows":"XY08:sure;XY08-02:likely","why":"why we think so, one sentence","also_shows":"","camera_lat":"","camera_lon":"","bearing":"","camera_note":"","file":"absolute path, or blank","width":0,"height":0,"notes":""}`. `shows` grades: `sure` a printed title, caption or unique form; `likely` a caption without proof for this building; `guess` position or form only. For a twin picture, `shows` names our object it speaks for, and the grade says how sure it is that the picture shows the named twin. Camera position only when you can argue it from the picture; say how in `camera_note`.
- `reconstruction`: `{"type":"reconstruction","author":"","institution":"","year":"","kind":"render|aerial view|video|3D model|physical model|painting|drawing|AR/VR|paper figure|game or community build","title":"","link":"the holder's page","licence":"as stated by the holder, or none stated","rights_class":"free|research-only","shows":"YM03:sure;GARDEN:ALL:likely","method_stated":"what the author says they built it from, your words; blank if nothing","uploader":"for video sites: who uploaded it and whether that is the author","file":"absolute path of the copy, or blank","width":0,"height":0,"notes":"","status":"viewed|snippet","source_id":"S.. if it has one","e_id":"E id if it replaces a row of the evidence catalogue"}`. One row per image or work with its own link. `GARDEN:YM|CC|XY|QC|ALL` for a whole garden. Always name the author and institution as stated; unknown is blank.
- `size_lead`: `{"type":"size_lead","id":"YM03-11","value":"11 bays, 37.6 m","source_id":"S..","locator":"","basis":"which Yangshi Lei drawing the author names","link":""}`. Grade is B and it is never applied to a size.
- `question`: `{"type":"question","text":"a conflict, a gap, or a site that blocked you"}`. Where a reconstruction disagrees with the period evidence, this is the row.
- `wish`: `{"type":"wish","what":"","replaces":"","where":"","how":""}`.

Prefer the most specific id you can defend, and always give the top-level compound too.

Final answer to the coordinator: at most 25 lines: counts of rows by type, best finds, what blocked, anything you doubt. No file dumps.
