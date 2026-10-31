# palace_r1_research: full research round for the Yuanmingyuan reconstruction (sources, maps, georeferencing, buildings, working layers)

You are working in `/opt/data/workspace/000_Dev/palace-beijing-yaga-sh`, a new repo for a walkable 3D reconstruction of the Old Summer Palace (圆明园 Yuanmingyuan, Beijing) as it stood just before its destruction in October 1860.

Read `CLAUDE.md` in this repo first: it is the project rulebook (confidence grades, copyright, coordinates, layout). Its rules win.

## What Tomasz asked for (his words, lightly cleaned)
"Use what we did for kostrzyn-yaga-sh as reference: the folder structure, the homepage, the map preview, how we manage the buildings and all the stuff. Spawn a full-blown hardcore research on what we can get about this place: the map, any pictures of it, how it looked before, whatever we can find. Start the research the same way as Küstrin:
1. a map of the whole palace before destruction;
2. the old buildings, at the beginning as boxes, the same structure as Küstrin.
Same research type, same management. Gather as much publicly available information as possible."
Starting source he gave: https://en.wikipedia.org/wiki/Old_Summer_Palace

This round is **the research and the data**. Round 2, after you, builds the 2D dev map and the 3D boxes from your files. So your GeoJSON and CSV are its hand-off: make them complete, consistent and documented.

## The template: Küstrin
`/opt/data/workspace/000_Dev/kostrzyn-yaga-sh` is the same kind of project, a week further on. **Read it, never edit it** (other workers are running there).
- Its `CLAUDE.md` and `research/README.md`: conventions.
- Skim the heads of `research/sources.md`, `research/questions.md`, `research/buildings.csv`, `research/photos/README.md` and `research/photos/catalog.csv`.
- Its first commit shows how that project started: `git -C /opt/data/workspace/000_Dev/kostrzyn-yaga-sh show --stat ea085a6`.

Copy the conventions:
- source IDs S01..., question IDs Q1..., confidence A/B/C
- one CSV row per building with sources and confidence
- GeoJSON layers as the hand-off
- control points for every georeferenced map
- a photo catalog with `rights_class` (free / research-only) and `shows` (`ID:sure|likely|guess`)

Adapt the IDs and fields to this place and document them in `research/README.md`.

## Deliverables

1. **`research/README.md`:** files, conventions, IDs, field definitions, public vs private, rebuild order of the scripts.

2. **`research/sources.md`:** the catalogue, in the Küstrin table format (ID, source, year, reuse, status, link / note).
   - Aim for breadth and quality: every overall plan, every album, the engravings, photo collections, texts, modern surveys, data sets (OSM, DEMs, declassified imagery), scholarly works, digital projects.
   - Each source gets an honest status (found / viewed / downloaded / to-request / blocked) and its reuse terms as stated by the holder.

3. **`research/questions.md`:** open questions and conflicts between sources. Q1 is the target state (1860, see CLAUDE.md): note what each key source dates to, and what changed between 1744, the 1780s and 1860.

4. **The map of the whole palace before destruction (Tomasz's step 1):**
   - **Find every overall plan of the three gardens available online.** For each, record where it is held, its date, resolution and licence. Download what can legally be downloaded into `research/raw/` (gitignored). Include:
     - the Yangshi Lei 样式雷 general plans (圆明园地盘全图, 三园总平面图 and similar)
     - Qing and Republican-era maps of the Haidian area
     - 1930s–1940s surveys and military maps (US Army Map Service sheets of Peiping are US-government works, often public domain; check)
     - declassified CORONA imagery of the 1960s–70s (USGS EarthExplorer, public domain), if you can find a frame of the site; it shows the lakes before modern changes
     - modern archaeological and park plans (research-only, but useful to read positions from)
   - **Pick the best base plan and georeference it.** Use control points on features that survive today: lake shores, islands, the canal network, the Xiyang Lou ruins (Dashuifa 大水法, Haiyantang 海晏堂 base, Yuanyingguan 远瀛观), the garden walls and gates, old roads.
     - Take the control points from OpenStreetMap (Overpass: the park boundary, water, islands, ruins, paths, names) and check them against WGS84 imagery.
     - Write `research/georef/<plan>.json` (control points with datum, transform, RMS in metres, per-point residuals) and `scripts/georef.py`.
     - Put the warped overlay image in `research/overlays/` (gitignored if the plan is research-only).
     - Report the accuracy honestly per area.
   - **Working layers** in `research/layers/` (WGS84 GeoJSON; every feature carries `id`, names zh/pinyin/en where known, `sources`, `confidence`, `note`):
     - `walls_1860`: the garden walls and gates of the three gardens and the Xiyang Lou strip
     - `water_1860`: lakes, ponds, canals, streams
     - `islands_1860`
     - `hills_1860`: artificial hills, outlines, with a height estimate and how it was got
     - `bridges_1860`: the major ones
     - `scenes_1860`: the scenic compounds / 景区, one polygon each
     - `footprints_1860`: single halls as rectangles where a plan shows them, with `orientation_deg`, `frontage_m`, `depth_m`
     - `osm_today`: today's park from OSM, ODbL
   - **Ground:** get the best open DEM for the area (Copernicus GLO-30 or better if open), clip it to the site into `research/raw/`, and note its limits in `research/terrain/README.md`. Hills are small, so say what the DEM can and cannot tell.

5. **The buildings (Tomasz's step 2, the input for the boxes):** `research/buildings.csv`, one row per scenic compound and one per known hall or structure inside it.
   - **Fields** (adapt as needed, document them): `id`, `parent_id`, `name_zh`, `name_pinyin`, `name_en`, `garden`, `type`, `built`, `destroyed`, `sources`, `confidence`, `lat`, `lon`, `pos_source`, `footprint_id`, `bays` (间 count), `frontage_m`, `depth_m`, `storeys`, `roof` (庑殿 / 歇山 / 硬山 / 悬山 / 卷棚 / 攒尖 ...), `roof_tiles`, `notes`.
   - **Coverage target:**
     - all Forty Scenes of Yuanming Yuan
     - the main compounds of Changchun Yuan, with every Xiyang Lou building (谐奇趣, 黄花阵, 养雀笼, 方外观, 海晏堂, 远瀛观, 大水法, 观水法, 线法山, 线法墙 ...)
     - the main compounds of Qichun Yuan
     - the gates and the main audience halls (大宫门, 正大光明, 勤政亲贤 ...)
   - Put the halls inside each compound wherever a plan shows them. Prefer fewer, well-sourced rows over many guessed ones, but every compound must at least be a row with a position.
   - **Building pages** are Round 2's job; you only make the CSV and layers.

6. **Typology for the boxes:** `research/typology/halls.md` plus a machine-readable `research/typology/params.json` with sources. Cover:
   - Qing official-style halls: bay widths, depth by purlin count, platform heights, column heights, eave and ridge heights by hall size, roof forms and pitches (举架)
   - what was typical in Yuanmingyuan (many informal 卷棚 roofs and grey tiles, unlike the Forbidden City; check this, don't assume it)
   - the Xiyang Lou buildings' European forms and their dimensions where the engravings or ruins give them
   - the Qing Gongbu Gongcheng Zuofa 工部工程做法 (1734) is an old text; cite what you use

   Round 2 builds each hall as a box on a platform with a simple roof from these numbers, so give defaults by hall class with confidence.

7. **Pictures:** `research/photos/catalog.csv` (P0001...) with `README.md`, in the Küstrin format.
   - **Cover:**
     - the Forty Scenes album (40 leaves)
     - the 20 Xiyang Lou copperplate engravings (1780s)
     - other Qing paintings of the gardens
     - the earliest photographs of the ruins (Ernst Ohlmer 1873, Thomas Child 1870s, others)
     - later photos up to the 1930s
     - key modern reconstructions (link only)
   - **Files:** copy free images (checked licence, web size) to `research/photos/images/`. Research-only images go to `research/raw/photos/` at most, with a link in the catalog.
   - **`shows`:** what each picture shows, by building id.

8. **`CLAUDE.md`:** fill in only the sections "The place" and "Timeline" (short, sourced, together under ~40 lines), and update "Status" in one or two lines. Leave every other section as it is.

9. **Review images** in `screenshots/r1/` (gitignored):
   - the georeferenced plan over today's map, local only
   - a public-safe render of your layers without any research-only plan
   - a coverage chart: which compounds have positions, footprints and halls

   Open every image yourself and fix what is wrong before you finish.

## How to work
- **Parallelise the research with subagents** (the Agent / Task tool), for example:
  - (a) maps and plans
  - (b) the inventory of scenes and halls
  - (c) pictures and their licences
  - (d) typology and dimensions
  - (e) today's site: OSM, DEM, ruins, archaeology

  Each subagent writes its notes to `/opt/data/cache/scratch/palace_r1_notes_<topic>.md` with full links. You alone write the shared research files, so nothing gets overwritten.
- **Search in Chinese as much as in English:** 圆明园 地盘全图, 样式雷 圆明园, 圆明园四十景图, 西洋楼 铜版画, 长春园, 绮春园 万春园, 圆明园遗址 考古, 圆明园 测绘, 九州清晏, 福海.
  - Good starting places:
    - zh.wikipedia, en.wikipedia
    - Wikimedia Commons categories on the Old Summer Palace, the Forty Scenes and the Xiyang Lou engravings
    - Gallica (BnF holds the Forty Scenes album)
    - the National Library of China's Yangshi Lei material, the Palace Museum
    - the official park site, Tsinghua's Digital Yuanmingyuan publications
    - papers (abstracts and open PDFs)
    - archive.org, the David Rumsey and Library of Congress map collections, the Harvard and Cornell Chinese map collections
  - Baidu Baike is B at best: use it for leads, not as the only source.
- **Be polite to servers:** one request at a time per host, a short sleep between requests, a real User-Agent. Record blocked sites in a question (as Küstrin's Q12 does) instead of hammering them.
- **Python:** use uv at `/opt/data/.local/bin/uv` with a `pyproject.toml` in this repo and a local `.venv`. Keep dependencies minimal and wheel-only (requests, pillow, numpy, shapely, pyproj; tifffile or rasterio only if a wheel installs). Nothing that builds from source.
- **Time:** this is a long round, and that is fine. Time-box any single object or source hunt at about 30 min; a missing piece becomes a question plus a wishlist entry (`research/wishlist.md`: what, where held, how to request), never a stall.
- Log one timestamped line per milestone to `/opt/data/cache/scratch/palace_r1_research_progress.md`.

## Rules
- **Another worker is building the homepage under `site/` right now.** Never touch:
  - `site/`, `tools/`, `.claude/`
  - `research/image-credits/CREDITS.md` (that worker owns it)
  - `CLAUDE.md` except the three sections named above

  You write `research/**`, `scripts/**`, `pyproject.toml`, `uv.lock`, `.venv/`, `screenshots/r1/`.
- **No git commands that write** (no add, commit, stash, checkout, restore, reset). Read-only git is fine. Lily commits.
- Copyright exactly as in `CLAUDE.md`: never put a research-only file outside `research/raw/` or `research/overlays/`.
- If you need a local HTTP server, use ports 8793–8795, bound to 127.0.0.1, and stop it when done. Never use 8790.
- Mark every claim verified, assumed or unknown. Never invent a number, a date, a URL or a licence.

## Final message
Lead with the answers to Tomasz's two steps:
1. how good the map of the whole palace before 1860 is (which plan, its accuracy in metres, by area)
2. how many compounds and halls have a position and a footprint (counts from a script)

Then list:
- the best sources found, and which ones are free to show on the site
- the biggest gaps, with the wishlist
- what Round 2 needs to know to build the dev map and the boxes (file names, fields, defaults)
- what is verified and what is assumed

Do not ask questions. Work only in this repo, plus the scratch files named above.


# ADDENDUM: this is the second run of this round (palace_r1b). Read this before anything else.

## Why there is a second run
The first run (palace_r1_research, 15:03-15:20 UTC) launched its five research subagents **in the background**, then ended its turn "waiting for their notes". In print mode the CLI waits only about 10 minutes for background tasks after the last turn, then kills them and exits. Every subagent died before writing its notes, so the round delivered almost nothing.

**Rules for this run (they override "How to work" above where they differ):**
- **Run subagents in the foreground only:** several Agent calls in ONE message, never `run_in_background`. Never end your turn while any subagent, crawler or background shell is still running. Your turn ends only when every deliverable is written and checked.
- **Before launching the subagents,** write a skeleton of every deliverable file with what you already know. Have each subagent write its notes to its scratch file as it goes, not only at the end, so a crash keeps partial work.
- **Give each subagent a scope it can finish in about 30-45 minutes.** Run a second wave of subagents if a topic needs more.
- **Log a progress line** to `/opt/data/cache/scratch/palace_r1b_progress.md` (not the file named above) at every milestone, at least every 15 minutes.

## What the first run left (reuse it, don't fetch it again)
In the repo (untracked, keep it):
- `research/layers/osm_today.geojson`: 6004 OSM features of today's park.
- `scripts/fetch_osm.py`, `scripts/clip_dem.py`, `pyproject.toml`, `uv.lock`, `.venv/`.
- `research/raw/dem/`: Copernicus GLO-30 tiles N39/N40 E116, plus `site_glo30.npz` and `site_glo30_shade.png` clipped to the site.
- `research/raw/osm/overpass.json`.
- `research/raw/plans/`: four Princeton University Art Museum images (2022-27): a 1920s plan of Yuanmingyuan and three scrolls. Check what they are, their dates and licence, and record them as sources.

The half-finished downloads of the killed subagents are in scratch. They are leads, not finished notes, and nothing in them is verified:
- `/opt/data/cache/scratch/palace_maps/`: Princeton manifests, Malone 1934 metadata (Carroll Brown Malone, "History of the Peking Summer Palaces under the Ch'ing Dynasty", 1934, likely has plans), Library of Congress and other search results.
- `/opt/data/cache/scratch/palace_r1_inv/`: Wikipedia dumps (zh and en: 圆明园, 四十景, 长春园, 绮春园, 西洋楼), and 日下旧闻考 Rixia jiuwen kao chapters 80-85 (the Qianlong-era description of the Yuanmingyuan, scene by scene) from ctext and Kanripo.
- `/opt/data/cache/scratch/palace_photos/`: started picture catalogue (images, meta).
- `/opt/data/cache/scratch/palace_r1_site/`: PDFs and tools about today's site and the archaeology.
- `/opt/data/cache/scratch/palace_r1_typo/`: crawl logs for the typology hunt.

## Gate
The orchestrator now checks your deliverables, not your exit code. Round 2 starts only if all of these exist:
- `research/buildings.csv` with rows for the scenes
- `research/sources.md`
- `research/questions.md`
- at least five layers in `research/layers/`
- a georef file in `research/georef/`
- `research/typology/params.json`
