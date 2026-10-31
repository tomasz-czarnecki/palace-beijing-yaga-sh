# Yuanmingyuan 圆明园 (Old Summer Palace), Beijing: 3D Reconstruction

## Goal

Rebuild the Old Summer Palace, the Qing imperial garden-palace north-west of Beijing, as it stood before Anglo-French troops looted and burned it in October 1860. The result is a map and a 3D model that people can walk through in the browser.
The complex is three gardens: Yuanming Yuan 圆明园, Changchun Yuan 长春园 (with the European palaces, Xiyang Lou 西洋楼) and Qichun Yuan 绮春园 (later Wanchun Yuan 万春园).

**Sister project and template:** `/opt/data/workspace/000_Dev/kostrzyn-yaga-sh` (Küstrin c. 1913). Same structure, same research rules, same management of buildings. Read its `CLAUDE.md`, `research/README.md`, `research/sources.md`, `research/questions.md` and `research/buildings.csv` to see how a thing was done there. **Never edit that repo.**

## Status

Started 2026-10-31. Round 1 done: base plan S01 georeferenced, `research/buildings.csv` and `research/layers/*_1860` built, rebuild order in `research/README.md`, open points in `research/questions.md`. Round 2: the 2D dev map and the buildings as boxes in a 3D preview. Homepage: a simple placeholder.

Decided:
- **Target state:** the gardens just before the destruction of October 1860 (Xianfeng reign). Earlier evidence (the Forty Scenes album of 1744, the Xiyang Lou engravings of the 1780s) counts for that state wherever nothing later contradicts it. Q1 in `research/questions.md` tracks this.
- **Purpose:** a showcase of the skill and the project, not a one-to-one reconstruction. Approx is OK where evidence is missing: guess, mark it C with a one-line reason, move on. Time-box research at about 30 min per object and write a wishlist of what would replace the biggest guesses.

## The place

- **Where:** the plain north-west of old Beijing, in Haidian, between Haidian town and the Western Hills (S02). Centre about 40.008 N, 116.300 E. Today a ruin park (S03).
- **Size:** the wall rings on the plan enclose 335 ha (run), against 331–350 ha stated (S145, S146, S147). Yuan Ming Yuan 183 ha, Changchun Yuan 69 ha, Qichun Yuan 78 ha (run). About 116 ha of it is water (run, S01).
- **Yuan Ming Yuan 圆明园, "Garden of Perfect Brightness":** the 大宫门 Da Gongmen and the audience hall 正大光明 Zhengda Guangming on the south axis (S05, S02). Behind them the nine islands round the 后湖 Back Lake, the core, with the emperor's apartments on 九洲清晏 Jiuzhou Qingyan (S02). To the east the near-square 福海 Fuhai, "Sea of Blessings", 26–28 ha (runs, S01, S03), with 蓬岛瑶台 Pengdao Yaotai on its islets (S05). The Forty Scenes are named from here (S05, S08).
- **Changchun Yuan 长春园, "Garden of Long Spring":** lakes around 含经堂 Hanjing Tang (S05, S143). The Xiyang Lou 西洋楼, the European palaces, stand in a strip along its north edge, 860 m long (S149), built under Castiglione and Benoist (S02).
- **Qichun Yuan 绮春园,** later 万春园 Wanchun Yuan: small gardens merged (S49, S06). Its 正觉寺 Zhengjue Si is the only building that survives (S145).
- **Building:** mostly grey tile and rolled ridges 卷棚, unlike the Forbidden City, with glazed exceptions such as 安佑宫 Anyou Gong and 方壶胜境 Fanghu Shengjing (S08, S06, S122). Sampled on two album leaves only (`research/typology/halls.md`).
- **Evidence:** S01 is Malone's "Official Map" or his tracing of it (S02 pp.231–232): every hall, by bays, in a state of about Daoguang to Xianfeng (Q2, Q3). It is the base for positions and footprints. The map reads to about ±10–20 m in Changchun Yuan and on the Xiyang Lou, ±30–40 m around the lakes and in Qichun Yuan, ±75 m in the west (Q7).
- **Today:** farmland and digging removed most hills and filled most water from the 1940s to the 1970s (S145). Lakes re-dug and lined; 福海 and 后湖 keep their shape (S146, S148).

## Timeline

- 1707–09: Kangxi grants the land to Prince Yinzhen, the later Yongzheng (S06, S42, S05, S02; Q21).
- 1725: Yongzheng builds the audience hall and offices on the south side (S05, S02).
- 1737: painted map of the garden by Castiglione and five others, lost (S02 p.62).
- 1744: the Forty Scenes named and painted (S05, S02). Album in the BnF since 1862 (S02).
- c. 1745–51: Changchun Yuan built (S45, S02; Q22). From 1747 the Xiyang Lou, until 1783 with 远瀛观 Yuanying Guan (S02, S42; Q24). The 20 engravings by 1786 (S02, S56).
- 1770–74: Qichun Yuan joins the gardens (S49, S06, S02; Q23). 1774: 文源阁 Wenyuan Ge (S05).
- 1793: Macartney's gifts stand in 正大光明殿 (S02).
- 1809–17: Qichun rebuilt at full size (S49, S47). 1831: 慎德堂 Shende Tang (S41). 1836: fire on the 九洲清晏 axis (S41). 1855: last dated addition found, 同道堂 Tongdao Tang's theatre (S43).
- 1860, 6–8 October: French and British troops take the gardens, and they are looted (S02 pp.179–183). 18–19 October: burned on Elgin's order by British troops under Michel; the French refuse to join (S02 pp.187–188).
- 1873: Tongzhi's repair stops (S02, S06).
- 1900: further damage; who did it is disputed (S06, S07; Q28).
- Republic: the ruin is used as a quarry for rock and brick (S02 p.218, S06).
- 1950s–70s: farmland and further removal; over 200 hills dug 1967–73 (S145).
- 1976: management office. 1988: national protected site, park opens (S06, S54).

## Research rules

- **Nothing goes into the model without a source.** Every source has an ID (S01, S02, ...) in `research/sources.md`. Every row in a CSV or GeoJSON file cites its source IDs (`S03;S12`).
- **Confidence:**
  - A = shown on a source made while the gardens stood (Qing site plans, Yangshi Lei 样式雷 drawings, the Forty Scenes, the Xiyang Lou engravings, pre-1860 texts), or measured on remains that survive unchanged (lake shores, ruins in place).
  - B = a later source (photos of the ruins after 1860, 20th-century surveys, modern scholarly reconstructions), or a written description only.
  - C = inferred (typology, symmetry, a guess). Every guess is C.
- **Evidence order:** Qing site plans win on positions and footprints. Paintings and engravings give forms, roofs, trees and bridges. Today's lakes, islands and hills anchor the georeferencing, because much of the landscape survives. Modern reconstructions (Tsinghua's Digital Yuanmingyuan and others) are B: cite their facts, never copy their images.
- **Source status:** found → viewed → downloaded (copy in `research/raw/`); also to-request (offline, must be ordered) and blocked (site refused automated access).
- **Numbers come from runs.** Every figure (areas, widths, heights, RMS) comes from a script run on the repo data.
- Online sources only for now; books and archive items are recorded as to-request.

## Copyright

- **Free** (may be committed and published, credited): public domain, CC0, CC BY, CC BY-SA, with the licence checked on the holder's page. PD-Art reproductions of pre-1900 two-dimensional works on Wikimedia Commons count as public domain.
- **BnF / Gallica:** reuse is free for non-commercial purposes with the credit "Source gallica.bnf.fr / BnF"; commercial use needs a licence. Publishable only with that credit, and the project stays non-commercial (open question for Tomasz).
- **Research-only:** everything else. That covers Yangshi Lei scans from the National Library of China, the Palace Museum or books; modern maps and plans; Tsinghua renders; figures from papers; and photos with an unclear licence.
  - Keep them in `research/raw/`, never commit them, never show them on the site.
  - The site shows them only as a link card ("View at ..."). Their facts can be used with a citation.
- **Basemap and satellite tiles** (Esri, Google, Bing, Amap, Baidu, Tianditu) are never saved into git. They are used only as a dev-map basemap, under the provider's terms.
- **OpenStreetMap** data needs ODbL attribution.

## Coordinates

- Store everything in WGS84 (EPSG:4326) in GeoJSON. Do metric work in UTM zone 50N (EPSG:32650).
- **Chinese map services use shifted datums.** Amap/Gaode, Tencent, and Google's road tiles inside China use GCJ-02, offset by a few hundred metres. Baidu uses BD-09.
  - Never mix them with WGS84 without converting.
  - Record the datum of every control point.
  - OSM and Esri World Imagery are WGS84 (check them against each other).

## Layout (mirrors kostrzyn-yaga-sh)

```
site/                     the public website, the only thing a host serves (Root Directory = site, static, no build)
  index.html, zh/, credits.html, styles.css, main.js, assets/
  reconstruction/         index.html (2D dev map, Leaflet), 3d.html (three.js preview, the way in), data/ (public layers, buildings/ = panel pages), vendor/
research/                 README.md, sources.md, questions.md, buildings.csv, buildings/ (one page per building), layers/ (GeoJSON working copies),
                          georef/ (control points), photos/ (catalog.csv), typology/, image-credits/CREDITS.md, raw/ and overlays/ (gitignored)
scripts/                  the Python pipeline (uv, pyproject.toml); writes into research/ and site/reconstruction/data/
tools/                    serve_local.py (local preview with the private layers under /_local/), screenshot scripts
models/                   later: detailed models, one folder per building (models/<ID>-<slug>/summary.json), as in Küstrin
```

- Nothing under `site/` may reference a file outside `site/`. No `package.json`, no Python and no folder named `public` under `site/`.
- Links inside `site/` must work on a plain static server too (`reconstruction/3d.html`, `credits.html`, `zh/`).
- **Never public:** `research/raw/`, `research/overlays/`, `scripts/`, this file.

## Website and git

- Preview on this server: port 8790 serves `site/` (Tomasz forwards it in VS Code). Workers use their own ports, never 8790.
- No GitHub remote and no Vercel project yet. Never push. Workers never commit; Lily makes the commits.

## Working rules

- **Keep history accurate and respectful.** The destruction of 1860 is a national wound in China. State it factually (who, when, what). No sensational or cute framing, and the twelve zodiac heads stay out of any playful content.
- **Names:** Chinese characters and pinyin first, then the English translation (正大光明 Zhengda Guangming, "Upright and Bright").
- **Work order:** garden walls, water, islands and hills first; then the scenic compounds; then single halls.
