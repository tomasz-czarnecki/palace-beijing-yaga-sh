# palace_r3 common brief for every evidence subagent

Project: `/opt/data/workspace/000_Dev/palace-beijing-yaga-sh`, a reconstruction of the Old Summer Palace 圆明园 as it stood before October 1860. Rulebook: its `CLAUDE.md` (read "Research rules" and "Copyright"). Goal of this round: every clickable object in the 3D view shows real evidence (picture, drawing, plan reference or period description), its own or its compound's. Breadth first, then depth on the famous ones.

## Lists of what to tie evidence to
- `/opt/data/cache/scratch/palace_r3_objects.tsv`: the 314 top-level objects (id, name, pinyin, garden, type, lat, lon, named children).
- `/opt/data/cache/scratch/palace_r3_halls.tsv`: the 900-odd named halls inside them.
- Existing: `research/sources.md` (S-ids, already known sources; reuse them), `research/photos/catalog.csv` (230 pictures, P0001–P0230; do not re-add a picture that is already there unless you add a better, verified link or a corrected `shows`; say so in notes), `research/questions.md`.
- Earlier fetched material: `/opt/data/cache/scratch/palace_r1_inv/` (日下旧闻考 j80-85 as `kr_0NN.txt` with leaf markers), `palace_r1_site/raw`, `palace_r1_typo`, `palace_photos`, `palace_r1_notes_*.md`, `palace_r1_photos.csv`.

## Hard rules
- **Do not write anything inside the repo.** Read only. No git commands. The coordinator alone writes repo files.
- Write incrementally so a crash keeps partial work:
  - free-form log `/opt/data/cache/scratch/palace_r3_notes_<topic>.md` (full links, licence quotes, ids, what was searched and not found);
  - machine-readable `/opt/data/cache/scratch/palace_r3_out_<topic>.jsonl` (schema below), appended as you go;
  - temporary files and fetched pages under `/opt/data/cache/scratch/palace_r3_tmp_<topic>/`; your own scripts in `/opt/data/cache/scratch/palace_r3_scripts/`, never in a folder of downloads.
- Append one line per milestone (`HH:MM <topic>: what`) to `/opt/data/cache/scratch/palace_r3_evidence_progress.md`, at least every 15 minutes.
- **Nothing invented.** Every quote is copied from a page you actually fetched (keep the fetched text in your tmp folder). Every catalogue number, title, date and licence is what the holder's page says. If you only saw a search snippet, say `"status":"snippet"`. Unknown is blank.
- **Search in Chinese as much as in English** (also Japanese/French/German where relevant).
- **Be polite:** one request at a time per host, at least 1-2 s between, a real User-Agent (`palace-beijing-research/0.1 (non-commercial; tomasz_czarnecki research)`), no hammering. Bot checks, log-ins and paywalls are never worked around: log the block in the jsonl as a `question` row and move on.
- **Copyright** (rulebook): free = PD, CC0, CC BY, CC BY-SA with the licence checked on the holder's page, or PD-Art of a pre-1900 2D work on Commons. BnF/Gallica: free with the credit "Source gallica.bnf.fr / BnF". Everything else research-only: **link card, no copy** (do not download research-only images, except a low-res look in tmp if needed). No NC or ND licence counts as free.
- **Texts:** Qing texts are public domain, quote them in full where short. Modern works: only a short summary in your own words (1-3 sentences), with citation; never paste their text.
- **Respect:** the destruction of 1860 is stated factually (who, when, what). No sensational framing. The twelve zodiac heads never in playful content.
- **Names:** Chinese characters and pinyin first, then English.
- Python: `/opt/data/workspace/000_Dev/palace-beijing-yaga-sh/.venv/bin/python -I yourscript.py` (Pillow available? check; `uv` at `/opt/data/.local/bin/uv`). Run scripts from the scripts folder, pass downloaded files as arguments. Tools `WebSearch` and `WebFetch` are deferred: load them with ToolSearch `select:WebSearch,WebFetch` first. curl with the User-Agent is fine too. No headless browsers unless you must (shared 4-core machine); ports only 8800-8809.
- **Time box:** look at `date -u` regularly. Stop by your deadline, with the jsonl complete. A missing piece becomes a `wish` row, never a stall. Do not spawn subagents, do not run background jobs that outlive you, and do not end before your own work is finished.

## Images
Free images only. Save to `/opt/data/cache/scratch/palace_r3_images/<topic>/<short-slug>.jpg`, at most 1600 px on the long side and about 300 KB (Pillow, quality about 80). Commons: the API `action=query&prop=imageinfo&iiprop=url|extmetadata|size&iiurlwidth=1920` gives the thumb and the licence (`LicenseShortName`, `Artist`, `Credit`, `ImageDescription`, `DateTimeOriginal`, `GPSLatitude`); quote `LicenseShortName` in `licence` as stated; thumb widths other than the standard steps (960, 1280, 1920) may be refused. Open a sample of what you download (Read tool shows images) to be sure it shows what you claim.

## Output schema: one JSON object per line in `palace_r3_out_<topic>.jsonl`
`type` is one of:

- `source`: `{"type":"source","id":"S2xx","text":"author, title, edition","year":"","reuse":"licence as stated","status":"viewed|downloaded|found|to-request|blocked","link":"","note":""}`. Allocate new S-ids only from **your block** (given in your task). Reuse existing S-ids where the source is already in `sources.md`.
- `picture`: `{"type":"picture","title":"original language","date":"as stated, with where it comes from","date_from":1873,"date_to":1873,"kind":"painting|engraving|photo|print|plan|render","creator":"","archive":"","archive_id":"","source_id":"S..","source_url":"the holder's page","licence":"exactly as stated","attribution":"","rights_class":"free|research-only","shows":"XY08:sure;XY08-02:likely","why":"why we think so, one sentence","also_shows":"","camera_lat":"","camera_lon":"","bearing":"","camera_note":"","file":"absolute path in palace_r3_images (free only, blank otherwise)","width":0,"height":0,"notes":""}`. `shows` confidence: `sure` printed title/caption/unique form; `likely` caption without proof for this building; `guess` position or form only. Camera position: only when you can argue it from the picture; say how in `camera_note`; blank otherwise.
- `evidence`: non-image evidence. `{"type":"evidence","kind":"text|poem|drawing|archaeology|reconstruction|description|plan","source_id":"S..","title":"","date":"date of the text or drawing","locator":"juan:leaf, chapter, page, catalogue no.","link":"","rights_class":"free|research-only","shows":"YM03:sure;YM03-11:sure","excerpt_zh":"verbatim text if Qing/public domain, else blank","excerpt_other":"verbatim non-Chinese text if public domain, else blank","summary_en":"short English summary in your own words","status":"viewed|snippet"}`. Yangshi Lei entries are `drawing`, with title, catalogue number and link. Modern books/papers/reports are `archaeology` or `reconstruction` or `description` with summary only and `rights_class":"research-only`.
- `fact`: something that improves a row of `research/buildings.csv`: `{"type":"fact","id":"YM03-11","field":"bays|built|changed|destroyed|name_en|roof|roof_tiles|storeys|frontage_m|depth_m","value":"","source_id":"S..","locator":"","quote_or_basis":"","suggest_confidence":"A|B|C"}`.
- `question`: `{"type":"question","text":"a conflict or a gap, with source ids; or a site that blocked you"}`.
- `wish`: `{"type":"wish","what":"","replaces":"","where":"archive","how":"how to request"}`.

Use real ids from the two lists in `shows`; several ids separated by `;`. Prefer the most specific id you can defend, and always give the top-level compound too. If an item covers a whole garden: `also_shows` for a picture; for evidence write `shows` with the garden tag `GARDEN:YM`, `GARDEN:CC`, `GARDEN:XY`, `GARDEN:QC` or `GARDEN:ALL`.

Final answer to the coordinator: at most 25 lines: counts of rows by type, best finds, what was blocked, anything you doubt. No file dumps.
