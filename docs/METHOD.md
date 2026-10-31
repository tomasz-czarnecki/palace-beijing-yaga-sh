# How to reconstruct a lost historical site

The playbook drawn from this project, the Old Summer Palace before 1860, and its sister Küstrin c. 1913 (`/opt/data/workspace/000_Dev/kostrzyn-yaga-sh`). Follow it for any town, palace or fortress. The result is a public website with a walkable 3D view in which every object opens a page showing its evidence.

**How to read the figures.** All times are UTC on 2026-10-31, from `docs/rounds/README.md`, the git log and the progress logs. Times per worker come from the modified time of its notes file, so they are approximate. Counts are as of commit 0bb4f81, except phase 11 and what cites Round 5.

**The whole run:** six hours by the clock, from the rulebook at 15:04 to the commit of Round 3 at 20:56, and about $178 as reported by the rounds' result rows. It took one failed run. It went this fast because Küstrin already gave the structure; expect longer without a template.

## The shape of it

| # | Phase | Inputs | Outputs | Scripts | Time here |
|---|---|---|---|---|---|
| 1 | Rulebook | the brief, a sister project | `CLAUDE.md`, `.gitignore` | none | not recorded; committed 15:04 |
| 2 | Homepage | rulebook, sister site, one free image | `site/` with credits and placeholder | none | 8 min |
| 3 | Research | rulebook | `research/sources.md`, `questions.md`, `wishlist.md`, notes | `scripts/fetch_osm.py`, `scripts/clip_dem.py` | 25–32 min per worker, pictures 102 min |
| 4 | Georeferencing | base plan, today's map, imagery | `research/plan/`, `research/georef/` | `scripts/mosaic_plan.py`, `scripts/trace_plan.py`, `scripts/georef.py` | tracing 31 min, control points 37 min |
| 5 | Inventory | texts, plan, control points | `research/buildings.csv`, `research/layers/` | `scripts/build_r1.py` | texts 25 min, plan readers 19 min, merge 10 min |
| 6 | Typology | building rules, stated sizes | `research/typology/params.json` | `scripts/typology_rules.py`, `scripts/typology_scale_check.py` | 30 min |
| 7 | Dev map | the layers | `site/reconstruction/index.html`, `app.js`, public layers | `scripts/publish_layers.py`, `tools/serve_local.py` | 11 min, shared with phase 8's data |
| 8 | Boxes in 3D | layers, typology, DEM levels | `3d.html`, `3d.js`, `halls3d.js`, `data/halls_1860.geojson`, `generated/` | `scripts/scene1860.py`, `scripts/ground1860.py`, `scripts/boxes1860.py` | 3 min for the view after that |
| 9 | Building pages | rows, boxes | `research/buildings/`, `data/buildings/`, `panel3d.js` | `scripts/building_pages.py`, `tools/check_pages.py` | 9 min |
| 10 | Evidence hunt | every object as a list | `research/photos/catalog.csv`, `research/evidence/` | `scripts/photos_catalog.py`, `scripts/apply_facts.py`, `tools/check_evidence.py` | 102 min |
| 11 | Twins and others' reconstructions | every object, its evidence | `research/twins/`, `research/reconstructions/` | `scripts/building_pages.py`, `tools/check_evidence.py`, `tools/serve_local.py` | 101 min |

Phases 3 to 6 ran together as one round, 142 min. Phases 7 to 9 ran as one round, 30 min. Next come detailed models, which here have not started (`models/README.md`).

## The phases

### 1. Rulebook

Write `CLAUDE.md` before anything else, because every later worker starts from it. Fix the following:
- the **target state**, one date, and what evidence counts towards it;
- the **purpose**: here a showcase, so approximate is fine where evidence is missing, marked C, with research time-boxed per object;
- **confidence grades**, **evidence order**, **copyright classes**, **coordinate rules**;
- the **layout**, with what is never public;
- **who commits** and which ports are whose;
- the **tone**, if the subject is sensitive.

Copy the shape of the sister project, then rewrite each rule for the new place. Do not copy a fact.

### 2. Homepage

A small public page first: it fixes the look, the credits page and the deploy shape, and the 3D view gets an "Enter" button to land behind. Check the licence of the one image on its holder's page. Keep claimed numbers out until a script has produced them. Test on a plain static server and on one imitating the host's clean URLs (`tools/serve_local.py`).

### 3. Research

Fan out by topic, one foreground worker each: **maps and plans, the text inventory, pictures, building typology, today's site and archaeology.** Reserve an S-id block per worker so ids never collide. Have each write notes as it goes, with a coordinator alone writing the shared files.

Before launching, write a skeleton of every deliverable. Give the workers a shared brief; `docs/rounds/common/` holds the two used here.

**The main decision is the base plan.** One plan drawn with every building, at a known date, turns everything after it into reading rather than guessing. Hunt it first and record what it is, when it dates to and how sure you are (Q2, Q3).

**Date the base plan against the texts straight away.** Here the check came two rounds late: the labels at 九洲清晏 turned out to be names of a decree of 1873 (Q36), after the boxes were built on them.

### 4. Georeferencing

1. Stitch scans into **one pixel grid** and never change it: all plan coordinates refer to it (`research/georef/princeton-mosaic.json`).
2. Trace the plan by script, with manual inputs as small files that give a reason for each entry (`research/plan/*_manual.*`). Keep it deterministic: rerunning here gives identical files.
3. Pick control points on **what survives unchanged**: shores, ruins, islands. Record the datum per point. Here 159 points: 59 shore, 51 ruin, 20 island, 15 wall, 14 junction.
4. Compare transforms by leave-one-out RMS, in a metric projection. Here thin-plate spline, 16.5 m, beat similarity at 33.6 m, affine at 28.7 m and polynomial at 22.0 m.
5. Hold out independent check points **and write them down before looking at errors**. Report by area what the plan reads to, not one number: here ±10 m to ±75 m (`per_area_verdict`).
6. Measure the plan's scale; don't trust the stated one. Here 1:1070 against a stated 1:1300, and buildings are drawn at another scale from the ground.

### 5. Inventory

Merge two lists: what the **texts** name and what the **plan** draws.
- A worker extracts rows from the texts, with quotes (`research/plan/inventory_texts.csv`).
- Detect buildings on the plan by script: `research/plan/blocks.csv`, 1453 blocks, precision about 0.92 and recall about 0.85 by eye on three crops.
- Plan readers, one per area, tie labels to blocks by viewing crops: `research/plan/readings/`, with `read` as `sure`, `likely` or `guess`, and adding or rejecting blocks.
- One script merges it all, `scripts/build_r1.py`. It holds the decisions as constants and prints its counts. Spot-check at random: here 12 `sure` rows viewed, 12 right.

An unnamed block gets a row. Something with no position gets a row and no invented position.

### 6. Typology

Defaults by class of building for what no source states: heights, roofs, bays. Each number has a source and a grade (`research/typology/params.json`). A stated size in `by_name` always wins. Rule arithmetic and the scale check are scripts, so the numbers come from runs. State how narrow the basis is: here roofs rest on two album leaves and a modern summary of the rules.

### 7. Dev map

A Leaflet page with one toggle per layer, doubling as the legend, with popups, for checking the data. `noindex`, reached only from a small button in the 3D view. On localhost it also offers the plan as an overlay, from `/_local/`. `scripts/publish_layers.py` makes the public copies and drops working fields. Vendor the libraries.

### 8. Boxes in 3D

Every building as a box before any detail: a whole site is what impresses, and it exposes data errors that a table hides.
- One shared frame, `scripts/scene1860.py`: scene metres, base levels.
- `scripts/ground1860.py`: land cut to the water layer. Use the DEM for base levels only, because it holds today's trees and fill.
- `scripts/boxes1860.py`: one feature per box, with `basis` saying what it stands on and `assumed: true` for a guess. It prints checks: overlaps, boxes in water, walls through boxes.
- Merged meshes with picking in the browser. URL switches for screenshots: `?b=`, `?shot=1`, `?conf=1`.

### 9. Building pages

One page per row and per gate, written by a script, with a hand-written `## Notes` the script never touches, and two JSON copies: public, and local with the private fields. `scripts/building_pages.py` asserts what may be public, by key. `tools/check_pages.py` proves every clickable object has a page, and that a second run changes nothing.

### 10. Evidence hunt

Goal: **no empty panel.** Breadth first, then depth on the famous objects.
1. Give the workers the object lists as TSV, with names, gardens and positions.
2. Wave 1 by kind of source. Here eight topics: dated Qing texts, Malone and Western witnesses, Qichun Yuan, Qing art, old photographs, Yangshi Lei drawings, archaeology, modern photographs.
3. Workers write JSON lines with a fixed schema (`source`, `picture`, `evidence`, `fact`, `question`, `wish`; see `docs/rounds/common/palace_r3_subagents.md`). They write nothing in the repo. The coordinator merges and verifies.
4. Build the panel on the first merge, then measure the gaps with `tools/check_evidence.py`.
5. Wave 2 on the gaps. Here four topics: the park's compilations, exact-phrase search on Commons, the Yangshi Lei site again, and halls and gates still bare.
6. Verify: compare quotes against the fetched text by script, sample links, view screenshots. Here 149 of 149 日下旧闻考 quotes and 40 of 40 prefaces matched, and 88 of 92 from Malone.

Say what was searched. A hall with nothing of its own shows "Evidence for the whole compound ..." and a line of what was searched and not found.

### 11. Twins and other people's reconstructions

The owner's reaction to phase 10 will be "most of those places are just sketches". For a lost site that is true, and two things can still put real images on the panels: **what still stands that is like it,** and **what others have built.** Both are kept apart from the evidence on screen and in the data, and neither ever sets a position or a size.

1. **Twins.** Hunt the **stated relation first**: Qing texts name their models (`S05`: 文源阁 「天一取阁式」, 如园 「略仿瞻园」, 安佑宫 「恭仿寿皇殿之制」). A worker reads the texts and writes pairings; another, the only one on Commons, finds pictures from the same list as it grows. Grade the relation A, B or C; a pairing with no source is `comparable`, C, with its reason. Add **a comparable per class of hall** in a page of its own, so every plain hall reaches a standing building. Say when a twin is a rebuild.
2. **Reconstructions.** Author, institution, year, method as stated, on every row. Note **what state each shows**: here some aim at 1744, and the card models of 1873–74 are period objects, not modern ones. Free images come mainly from **open-access papers**: read the licence on the paper, take only figures with no other credit, open every one.
3. **Keep a record of what stays off the panel.** Here 22 rows: models of the zodiac heads, items of another garden.
4. **Panel order:** period evidence, reconstructions (labelled modern interpretation, not evidence), comparables (labelled not this building), the set of buildings. Compounds' rows reach halls by the same fallback; garden and class come folded.
5. **Measure before and after,** with a file fixed before the round (`research/evidence/coverage_before_r5.json`).

## The data model

**Hand-offs are plain files,** each step reading the last one's output:

```
plan/*, inventory_texts.csv, typology/params.json, georef/*.json
  -> build_r1.py -> buildings.csv, layers/*_1860.geojson
evidence/facts.csv -> apply_facts.py -> buildings.csv
layers/ -> publish_layers.py -> site data
layers/ -> ground1860.py -> generated/
layers/, buildings.csv, params.json, generated/ground_grid.i16 -> boxes1860.py -> halls_1860.geojson
photos/catalog.csv -> photos_catalog.py -> web copies, credits
buildings.csv, catalogues, questions.md, sources.md, halls_1860 -> building_pages.py -> pages, panel JSON
```

**Ids.** S sources, Q questions, P pictures, E evidence, and building ids that say where a thing is: `YM03` a compound, `YM03-11` a hall from the texts, `YM03-N02` first named on the plan, `YM03-B0835` an unnamed block, `Z-B1234` in no compound, `G01` a gate. Ids are never renumbered, because rows cite them. The full table is in `research/README.md`.

**Confidence.** A = shown on a source made while the site stood, or measured on unchanged remains. B = a later source, or a written description. C = inferred, every guess. Grade **what** and **where** apart (`confidence`, `pos_confidence`), and record how the reading was made (`read`). A grade may be held down for a stated reason: S01 stays B until Q2 is settled, so no box is A.

**Catalogues are sources of truth.** `research/photos/catalog.csv` and `research/evidence/catalog.csv` are hand-edited after the round that builds them. Both tie to objects the same way: `shows` = `ID:sure|likely|guess;...`, a garden tag for a whole garden. `rights_class` is `free` or `research-only`. Evidence also has `status`: `viewed`, or `snippet` if seen only in a search summary, and the panel says so.

**Facts apart from rows.** A fact goes in `research/evidence/facts.csv` with its source, quote and a `decision`: `apply`, `name`, `note`, `gate` or `lead`. A script applies it, so a conflict stays visible rather than being overwritten, and a `lead` waits for someone to read it.

**The panel JSON.** `site/reconstruction/data/buildings/<ID>.json`; its keys are in `research/README.md`. Order on screen: own pictures, own texts and drawings, the plan as a link, what was searched, reconstructions by others, surviving comparables, what speaks for the set of buildings.

**Parent fallback ("set of buildings").** Most buildings of a lost site have no picture of their own: here 937 of 1510 halls show only the plan and their compound's evidence. So a page holds a reference, not a copy: `fallback` = `[{kind, id, name}]`, `kind` being compound, nearest (with the distance) or garden. The panel fetches that page, so nothing is written twice, and the heading says plainly that this is evidence for the compound. `GARDEN-*.json` holds what speaks for a garden.

**Boxes state their basis.** `basis` = `plan`, `stated`, `xiyang`, `layout`, `default`, `gate`; `assumed: true` for a guess. `?conf=1` colours by confidence.

## The copyright model

| Class | What | In git | On the site |
|---|---|---|---|
| Free | public domain, CC0, CC BY, CC BY-SA, licence checked on the holder's page; PD-Art of pre-1900 two-dimensional works on Commons | yes | yes, credited |
| Free with a condition | BnF / Gallica: non-commercial, credit "Source gallica.bnf.fr / BnF" | yes | yes, so the project stays non-commercial |
| Research-only | everything else, and every NC or ND licence | no copy, `research/raw/` at most | a link card: title, date, holder, what it shows, "View at ..."; on localhost the local copy, marked |
| Tiles | Esri, Google and others | never | dev-map basemap only |
| Traced geometry | our tracing of a plan with no copyright on it, credited | yes | yes |

**Rules that held up:**
- **Facts are not copyright.** A research-only source can be cited for a fact in our words.
- **Quote only the public domain.** Qing texts are quoted; modern work is summarised in one to three sentences of our own.
- **Licence as stated, per file.** Album leaves on Commons here carry different tags. Quote the tag in `licence`.
- **One way in.** Web copies reach `site/` only through `scripts/photos_catalog.py`, which refuses to run on a research-only picture in a public folder or a public picture with no credit.
- **Checks, not care.** `tools/check_evidence.py` fails on a research-only image, a missing file or copied research-only text. `site/.vercelignore` and `.gitignore` are a second lock.
- **Unsettled calls go on a list for the owner:** Q6 and Q50 here.

## Source strategy

**What gave most:**

| Kind | Here | What it gave |
|---|---|---|
| Measured plan | S01, Princeton | every position and footprint: 1560 boxes. Nothing else comes close |
| Compilations of period texts | S360, S361, the park's own PDFs | 1445 of 2397 evidence rows, dated poems hall by hall |
| Period gazetteer | S05 日下旧闻考, on Kanripo | the scene-by-scene inventory, 150 rows |
| The standard monograph | S02 Malone 1934 | the plan's identity, measured foundations, 96 rows |
| Painted albums and engravings | S08, the woodcuts S76, the gouaches S77, the 20 plates | form and roofs: the free core of the pictures, but only for the Forty Scenes and the Xiyang Lou |
| Later editions | S260, lithograph of 1887 | 80 free pictures and text pages for all 40 scenes |
| Old photographs | S86 Östasiatiska, S280 Skušek, Commons | ruins in form; captions often wrong |
| Drawing archives | S13, S310 Yangshi Lei | what stood by date, but research-only and often search summaries only |
| Archaeology | reports and press | measured sizes, as facts only; 48 rows |
| OSM and imagery | S03, S160 | the anchors of the georeference; hints for names, with errors (Q32) |
| DEM | S04 | base levels only |
| Wikipedia | S06, S07 | leads and a first timeline; B at best |
| Open-access papers | S108, S590–S594, S605, S606 | the free reconstructions: 17 of the 23 on the site, some by the Tsinghua team itself under CC BY |
| Qing texts, read for models | S05 | 14 of the 15 relations at grade A |
| Commons, patiently | S440, S640 | 153 twin pictures, at about 15 calls between 429s |
| A modern monograph that weighs the claims | S415, Rabreau 2022 | what about the European models holds, which is little |
| Old photo collections at holders | S460, S465, S654 | five free ruin plates and much correction; most captions are wrong (Q60) |

**How to search:**
- **In the site's language as much as in English,** then the languages of those who were there: French and English eyewitnesses here. The best material was never in English.
- **Go to the catalogues,** not only the search engine: Commons API with category and `deepcat` searches, Internet Archive full text, Kanripo's GitHub for Chinese texts, K-samsök for Swedish holdings, national library portals, the site's own administration.
- **Read the standard monograph early.** Malone pp.231–232 identified the plan as the "Official Map" and gave its scale and history.
- **Name by name once you have an inventory.** Then a list of unnamed blocks is honest about why nothing can be found.
- **Check form against caption.** Several captions were overruled by the plate of the same building (Q49).

**What blocked** (Q33), and what to do about it: never work round a bot check, log-in or paywall. Log it, add a wishlist line, move on.
- mhymy.com drops every record page, so 87 Yangshi Lei rows rest on search summaries.
- yuanmingyuanpark.cn answers in bursts, then times out.
- ctext.org has a security check; Kanripo's GitHub text served instead.
- Gallica's licence page refuses automated access.
- Commons and Wikisource rate-limit at about 9–14 requests a minute on a shared address: 187 name searches did not run, so "no picture found" there is not proof.
- A session's web search budget ended at 200 searches, at 19:45 in Round 3. Keep some back for the last wave. Round 5 gave each worker a share and stayed within it, at about 170.
- Round 5: Duke, Harvard's API, Gallica's SRU, the Library of Congress, Getty, and most of mhymy.com. Q62 has the full list; `research/wishlist.md` says who could open them by hand.

**The wishlist is a deliverable.** What, what it would replace, where it is held, how to ask (`research/wishlist.md`).

## What was specific to China

- **Shifted datums.** Amap/Gaode, Tencent and Google's road tiles inside China use GCJ-02, a few hundred metres off (540 m here); Baidu uses BD-09. This project used only OSM and Esri, which are WGS84, and checked them against each other: 2.7 m E, 1.8 m N over 54 outlines. Record the datum of every control point.
- **Catalogues in Chinese,** with holders that rarely state a licence: so most modern Chinese material is research-only, and its facts are cited. Yangshi Lei drawings are expensive in print and hard to read online.
- **Reign dates.** Some records convert them wrongly (Q51): use the reign date as stated.
- **Name variants.** One place has several written forms and plaques moved (Q20). Keep them in the row and don't merge on spelling alone.
- **The topic is a national wound.** State who, when and what. No sensational or cute framing, and the twelve zodiac heads stay out of any playful content. The Küstrin speech bubble and sway were removed from the homepage for this reason. Keep looting and burning apart, as the sources do; the first draft of this rulebook blurred them.
- **Chinese fonts** are large. The site uses subsets of the characters in use, and a new character falls back to a system font until the subset is rebuilt.
- **No native reader yet.** The `zh/` page is a draft.

## From Küstrin: what carried over and what differed

**Carried over:**
- the layout: `site/` as the only public folder, `research/`, `scripts/`, `tools/`, `models/`;
- S, Q and P ids; grades A, B, C; source status;
- the picture catalogue with `rights_class` and `shows`; link cards for research-only pictures;
- generated pages with a hand-written `## Notes`, `%% private %%`, and public and local JSON;
- `tools/serve_local.py` with `/_local/`, `?public=1`, `?b=`; `tools/check_pages.py`; `site/.vercelignore`;
- the dev map behind a small button, with the 3D view as the way in;
- the `summary.json` shape for detailed models;
- the homepage's look and fonts.

**Differed:**

| | Küstrin | Here |
|---|---|---|
| The base | several plans; a 1913 plan with an address book, house by house | one plan drawing every building |
| The ground | a terrain scan, with today's rubble taken out | a flat base from a coarse DEM, with land cut to the traced water |
| Georeferencing | `georef.py` of 92 lines | spline over 111 points, by area, `scripts/georef.py` of 708 lines |
| Reading the plan | lot numbers by OCR and by eye | a tracer, then area readers viewing crops |
| Object count | 447 rows | 1824 rows, so everything is a generator |
| Rows | landmarks and houses | compounds with halls under them (`parent_id`) |
| Non-image evidence | in facts and notes | its own catalogue and `facts.csv`, new here |
| Bare objects | a page with what it has | parent fallback, new here |
| How it grew | 184 commits, feature by feature | five rounds from written briefs |
| Dev map library | a CDN | vendored |
| Plan image | local | local (Q6); traced geometry public |
| Grade A means | seen on a source of 1900–1914 | a source made while the gardens stood; S01 held at B |

## Pitfalls and fixes

**Running the agents:**
- **A research round launched its subagents in the background, ended its turn "waiting", and print mode killed them after 10 minutes.** It exited 0 with almost nothing delivered ($9, 17 min). Fix: foreground subagents only, several Agent calls in one message; `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0` in the chain; and chains gated on deliverables, not on the exit code alone.
- **Partial work lost in a crash.** Skeletons of every deliverable first; workers append notes as they go.
- **A worker overruns.** The pictures worker ran about 100 minutes against a 30–45 minute scope. Give a deadline by the clock (`date -u`), and turn what's missing into a wish row.
- **Rules broken under pressure.** One worker ran `git checkout` twice despite "no git writes"; others wrote shared files; one fetched tiles too fast. Say so in the final message; those reports are in `docs/rounds/README.md`.
- **Late shared facts.** The plan's scale was corrected after wave 1, so the correction was added to the common brief before wave 2. Keep that brief a living file.
- **Workers in one scripts folder.** Two overwrote each other's contact-sheet script. Fix: a prefix per worker.
- **Workers' "can't".** The brief said skip without `pdfimages`, so ten free rows came back with no image. A small library in scratch fixed it in minutes. Check what a worker skipped before accepting it.
- **Valuable tools left in scratch.** Round 3's merge scripts sat outside the repo. Catalogues are the truth, so a rebuild doesn't need them, but they can't be rerun from a clone. Copy what's reusable into `tools/`, as was done with the font subsetter (`tools/font_subset.py`).

**Reading evidence:**
- **A check that isn't blind.** The georeference worker edited its check set after seeing errors: first pass median 52 m, kept set 31 m. Both stay in the JSON, and Q7 says it plainly. Fix the check set first.
- **The stated scale was wrong** (1:1300 against 1:1070), and buildings are drawn at another scale again. Measure; never size a building from a global px/m.
- **Things that look like what they aren't.** Labelled 稻田 rice fields look like ponds. Read labels before classing regions.
- **Dating the base plan by feel.** See Q36. Test plan labels against dated decrees early.
- **Wrong people, wrong place.** Beato's photographs of 1860 show Qingyi Yuan, not this garden. Prints credited to Piry, Child or Ohlmer may be by C. F. Moore. Skušek's album names are unreliable (Q49).
- **Same thing twice.** Parallel workers gave one item two source ids, and two names can be one place (QC40 = QC25). Keep ids; note the identity.
- **Snippets posing as sources.** Mark them `snippet`, hold their facts as `lead`, and let the panel say so.
- **A caption's place name.** Before 1900, "Yuen Ming Yuen" and "Summer Palace" name other gardens too: Favier, Thomson and Beato at the holders themselves. Check form, always.
- **Viral claims.** "Photographs of the garden before the fire" come with no holder and no picture named. Test them, write down the test, and leave them out.
- **A twin's chain of repeats.** 海晏堂 follows the Trianon comes from one book of 1971 and fills the web. Find a work that weighs the claim.
- **Confidence inflation.** "On a source" here means position and footprint; heights and roofs still come from the typology. Say that where the number is quoted.

**Building it:**
- **Stated sizes not reaching boxes,** because a row's name differed from the key: 文源阁, 大宫门, 雷峰夕照. Print what didn't bind.
- **Workers' shorthand in public text.** Clean notes by rule and view real panels. File names as titles, and the same work tied twice at two grades, showed up only in screenshots.
- **Boxes fighting the plan.** At full hall scale 315 pairs overlap. Reduce towards the drawn size first, then move at most 2 m, and report what is left (Q34).
- **Views that look wrong:** the outer plain hid the water, land colours skipped colour conversion, labels too small, wall tops through low roofs. Only viewing screenshots catches these.
- **Generators that must be idempotent.** `scripts/building_pages.py` writes only if changed, and `tools/check_pages.py` runs it twice and compares.
- **Clean URLs break relative links.** With `trailingSlash: false`, `/reconstruction` has no slash: links need to work on both.
- **Size.** `site/` is 106 MB, `research/photos/images/` 161 MB, `.git` 267 MB. Round 3 cut new images to 1600 px and about 300 KB. Check the host's limits before setting one up.
- **Docs that drift.** `tools/check_docs.py` compares field names and paths with the files. Round 4 found `research/README.md` claiming `scripts/georef.py` alone writes the overlay, and `CLAUDE.md` listing screenshot scripts that aren't there.

## Running it as rounds

Each round is one `claude -p` run from a written brief, with its own log and marker. A chain waits for the marker, gates on deliverables, commits, starts the next:

```bash
export CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0
while [ ! -f "$R/prev.done" ]; do sleep 60; done
[ "$(($(wc -l < research/buildings.csv) - 1))" -ge 30 ] || block "too few rows"
[ -s research/sources.md ] || block "no sources"
git add -A && git commit -q -m "..."
claude -p "$(cat "$R/next_brief.md")" --model opus --effort xhigh --permission-mode acceptEdits \
  --allowedTools 'Read,Write,Edit,Bash,WebFetch,WebSearch,Agent' --add-dir "$S" --add-dir "$SISTER" \
  --output-format stream-json --verbose > "$S/next.jsonl" 2> "$S/next.err"
echo "exit $? at $(date -u +%H:%MZ)" > "$R/next.done"
```

**What goes in a brief** (examples in `docs/rounds/`): the owner's words; where it stands, measured; the deliverables with their gates; data rules; how to work; verification; what the final message must lead with. Workers don't ask questions: they decide, write the reason down, and report. Workers don't commit.

## Checklist for the next project

**Before any work:**
- [ ] Create the repo; add it to `000_Dev/CLAUDE.md`.
- [ ] Pick the sister project; name it read-only in the rulebook.
- [ ] Write `CLAUDE.md`: target state, purpose, grades, evidence order, copyright, coordinates, layout, tone, ports, who commits.
- [ ] Copy `.gitignore`, `site/.vercelignore`, `site/vercel.json`, `pyproject.toml`; run `uv sync`.
- [ ] Reserve a preview port and a `/opt/data/scripts/rounds_<name>/` folder.
- [ ] Check for local datum trouble and which map services are safe.
- [ ] Ask whether the project stays non-commercial; it decides what is free.

**Round by round:**
- [ ] Homepage, one checked image, credits.
- [ ] Find and date the base plan. Test its labels against dated texts now.
- [ ] Research fan-out, foreground, with skeletons, deadlines, S-id blocks, a common brief.
- [ ] Mosaic, trace, control points, a check set fixed in advance, accuracy per area.
- [ ] Text inventory, plan readers, merge script, random spot check.
- [ ] Typology with a source per number.
- [ ] Dev map, then boxes, then pages. View the screenshots.
- [ ] Evidence wave by kind, panel, measure gaps, wave on the gaps, verify quotes by script.
- [ ] Twins by stated relation, typology comparables, reconstructions by others with their period and method; before and after counted.
- [ ] `tools/check_pages.py`, `tools/check_evidence.py`, `tools/check_docs.py` pass.
- [ ] Rebuild in a scratch copy: every committed file comes out the same.
- [ ] Wishlist and rights questions written for the owner.
- [ ] Docs round: rulebook, research README, a round log, and copies of the briefs.
- [ ] Measure the site's size against the host's limits before the first deploy.
