# The rounds

One entry per round: each was one `claude -p` run from a brief. The briefs are beside this file, unchanged, as `<name>.md`. `common/` holds the shared briefs the coordinators gave their subagents (not asked of Round 4 by name; kept because scratch may be cleared).

**Sources:** result rows in `/opt/data/cache/scratch/<name>.jsonl`, `/opt/data/scripts/rounds_palace/*.done`, the progress logs, the git log. All on 2026-10-31, UTC. Cost is `total_cost_usd` of the result row.

**Effort:** only the chain scripts record it (`/opt/data/scripts/palace_r2_chain2.sh`, `palace_r4_chain.sh`). The other rounds were started another way and the logs don't hold it: "not recorded". Every log's model is `claude-opus-5-5`.

| Round | Effort | Ran | Duration | Turns | Cost | Commit | Outcome |
|---|---|---|---|---|---|---|---|
| rulebook, by Lily | - | before 15:04 | not recorded | - | - | bbed686 | `CLAUDE.md`, `.gitignore` |
| `palace_home` | not recorded | 15:04–15:12 | 8 min | 55 | $2.57 | de7dc3b | done |
| `palace_r1_research` | not recorded | 15:03–15:20 | 17 min, 6 of them before its turn ended | 25 | $9.04 | none | **failed:** subagents killed |
| `palace_r1b` | not recorded | 15:36–17:58 | 142 min | 72 | $80.16 | 11537d0 | done |
| `palace_r2_map` | xhigh | 17:59–18:30 | 30 min | 81 | $9.42 | 33b3f29 | done |
| `palace_r3_evidence` | not recorded | 19:12–20:55 | 103 min | 71 | $76.61 | 0bb4f81 | done |
| `palace_r4_docs` | high | from 20:56 | see the `.done` marker | - | - | the commit named "Docs: ..." made by the chain after it exits | this round |

## palace_home

**Delivered:** homepage in English and a Chinese draft, credits, a reconstruction placeholder, styling, fonts with two Noto Chinese subsets, the hero 方壶胜境 from the album (PD-Art on Commons). 24 files.

**Checked:** four pages at two sizes on a static server, with no console errors, 404s or overflow; clean URLs on an imitation of Vercel.

**Went wrong or left open:**
- Vercel itself untested; no native speaker read the Chinese.
- The page's 1747 start of the European palaces, the French commander's refusal and today's site rested on Wikipedia.
- It flagged that `CLAUDE.md`'s Goal line blurred the looting and the burning. Fixed in Round 4.
- It flagged 万春园: zh.wikipedia says only a planned name, `CLAUDE.md` says "later Wanchun Yuan". Not settled; see Round 4.
- The font subset script stayed in scratch (`palace_home_subset.py`).

## palace_r1_research

**Delivered:** almost nothing: `research/layers/osm_today.geojson` (6004 features), DEM tiles, four plan images, `scripts/fetch_osm.py`, `scripts/clip_dem.py`. All were reused by the next run.

**Went wrong:** it launched five subagents and a crawl in the background, then ended its turn "waiting for their notes". Print mode waits about 10 minutes after the last turn. From `palace_r1_research.err`: "Background tasks still running 10m after the last turn ... stopping them." The run still exited 0.

The first chain's gate caught it through the missing files: `palace_r2_map_blocked.done` at 15:21. This led to the rules in `docs/METHOD.md` and to the second run.

## palace_r1b

The same brief plus an addendum: `palace_r1b.md` is byte for byte `palace_r1_research.md` followed by that addendum.

**Delivered:**
- Base plan S01 identified as Malone's "Official Map" or his tracing; mosaic 12955 × 9049.
- Georeference: thin-plate spline, 111 points, RMS 10.6 m, leave-one-out 16.5 m, reading ±10 m to ±75 m by area.
- 1824 rows: 212 compounds (191 with position), 1612 halls (1461 with position, 1418 with footprint); all 40 scenes and 15 Xiyang Lou buildings placed; 1560 footprints.
- Layers, typology, terrain note; 150 sources and 230 pictures (182 free) at that time; Q1–Q33; the wishlist.

**Timeline:** mosaic and skeletons 15:39–15:40. Wave 1 from 15:40 (inventory, maps, typology, trace, site, georef by about 16:17; photos 17:22). Wave 2 of five plan readers 17:24–17:43. Merge and docs 17:43–17:58.

**Checked:** no duplicate ids, every source id resolves, `build_r1.py` reproducible, 12 random `sure` readings viewed, all right.

**Went wrong:**
- Pictures worker about 100 minutes, well over its scope.
- Site worker fetched 179 Esri tiles, the first 40 faster than the politeness rule.
- Georef and trace workers wrote their own repo files though the brief reserved shared files for the coordinator.
- The georef check was edited after seeing errors, so it is not blind (Q7).
- The plan's scale was wrong in the shared brief until corrected after wave 1.

## palace_r2_map

**Delivered:** the 3D view of all three gardens, the dev map with 11 layers, 1636 boxes (1509 on a block or stated size, 127 guesses: 79 Xiyang Lou parts, 23 gates, 14 default, 11 laid out), the panel, 1877 pages (1824 rows, 53 gates), `tools/serve_local.py`, `tools/check_pages.py`. 3804 files.

**Timeline:** read 18:00–18:03; ground, boxes, publish, server, dev map to 18:14; 3D view to 18:17; pages and docs to 18:26; screenshots and checks to 18:29.

**Checked:** console clean on three servers; real click opens the panel; deep links; walk mode with keys only; no plan image in `site/`; 1522 clickable objects, none without a page; second generator run changes nothing.

**Went wrong, then fixed:** the outer plain hid the water; land colours skipped colour conversion; labels too small; wall tops through low roofs; stated sizes not reaching three halls because row names differed; workers' shorthand in public notes; the garden tint outside the walls.

**Left:** 28 box pairs overlap where the plan does; 13 boxes partly over water; canals like ditches up close; no trees; not tested on a real graphics card or a phone.

## palace_r3_evidence

**Delivered,** before → after:

| | Before | After |
|---|---:|---:|
| Top-level objects (314) with their own picture | 58 | 99 |
| Top-level objects with their own text or drawing | not measured | 167 |
| Panels (1877) with their own picture | 58 | 152 |
| Named halls (605) with their own evidence | not measured | 567 |
| All halls (1510) with their own evidence | not measured | 573 |
| Pictures in the catalogue | 230 | 547 (450 on the site) |
| Text and drawing entries | 0 | 2397 |

Also: parent fallback in the panel, `research/evidence/facts.csv`, `tools/check_evidence.py`, Q36–Q53, and only 19 boxes changed.

**Best finds:** the plan's labels at 九洲清晏 date from 1873 or later (Q36); the park's compilations S360, S361; the whole 1887 edition of 圆明园图咏; the Skušek album; a court officer's route of 1856; Bourgeois's letter of 1786; Barrow's measure of 1793.

**Timeline:** wave 1 of eight topics 19:14–19:58; merge and panel to 20:11; wave 2 of four topics 20:12–20:45; final merge and checks to 20:54.

**Checked:** both check tools pass; 149 of 149 日下旧闻考 and 40 of 40 preface quotes match; 88 of 92 from Malone, 4 not chased; 27 of 28 sampled links answer.

**Went wrong:**
- **Broke "no git writes" twice:** `git checkout -- research/buildings.csv`, to undo its own edit.
- 163 entries rest on search summaries, marked; 45 facts held as `lead`.
- Commons rate limits stopped 187 name searches; the web search budget of 200 ended at 19:45; mhymy.com refused record pages (20 of 146 records listed, 0 read).
- S360 and S361 poems are script-picked, sampled by eye.
- Rights calls made for Tomasz to review: Q50.
- `scripts/build_catalog.py` deleted on purpose; nine page folders renamed once their labels were read.

## palace_r4_docs

**Delivered:** `CLAUDE.md` brought up to date, `research/README.md` checked against the files, `docs/METHOD.md`, this folder, and `tools/check_docs.py` (not asked for by name: it is the script the brief asked for, kept so the check can be rerun).

**Checked:** the pipeline from `scripts/trace_plan.py` through `scripts/building_pages.py` rerun in a scratch copy, with no file differing; `tools/check_pages.py` and `tools/check_evidence.py` pass, and the repo is unchanged by them.

**Found in the old docs and fixed:**
- `CLAUDE.md`: the Goal line blurred the looting and the burning; the homepage was called a placeholder; `tools/` was said to hold screenshot scripts, and has none; the layout left out `research/plan/`, `research/terrain/`, `research/wishlist.md`, `generated/`, `docs/`; S01's state ignored Q36.
- `research/README.md`: `scripts/georef.py` with no argument was said to write the overlay and images, and it only fits; six fields of `buildings.csv` had no row in the table; `research/evidence/facts.csv`, the control points, the readers' files, most layer properties and the panel JSON had no field list; six files in `research/plan/` were unlisted.

**Not settled:** 万春园 (Round 1's flag), left as written; efforts of four rounds; the writing time of the rulebook.
