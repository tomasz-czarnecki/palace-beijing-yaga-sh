# Yuanmingyuan 圆明园 (Old Summer Palace), Beijing: 3D Reconstruction

## Goal

Rebuild the Old Summer Palace, the Qing imperial garden-palace north-west of Beijing, as it stood before Anglo-French troops looted and burned it in October 1860. The result is a map and a 3D model that people can walk through in the browser.
The complex is three gardens: Yuanming Yuan 圆明园, Changchun Yuan 长春园 (with the European palaces, Xiyang Lou 西洋楼) and Qichun Yuan 绮春园 (later Wanchun Yuan 万春园).

**Sister project and template:** `/opt/data/workspace/000_Dev/kostrzyn-yaga-sh` (Küstrin c. 1913). Same structure, same research rules, same management of buildings. Read its `CLAUDE.md`, `research/README.md`, `research/sources.md`, `research/questions.md` and `research/buildings.csv` to see how a thing was done there. **Never edit that repo.**

## Status

Started 2026-10-31. Round 1: research (sources, maps, georeferencing, building inventory, working layers). Round 2: the 2D dev map and the buildings as boxes in a 3D preview. Homepage: a simple placeholder.

Decided:
- **Target state:** the gardens just before the destruction of October 1860 (Xianfeng reign). Earlier evidence (the Forty Scenes album of 1744, the Xiyang Lou engravings of the 1780s) counts for that state wherever nothing later contradicts it. Q1 in `research/questions.md` tracks this.
- **Purpose:** a showcase of the skill and the project, not a one-to-one reconstruction. Approx is OK where evidence is missing: guess, mark it C with a one-line reason, move on. Time-box research at about 30 min per object and write a wishlist of what would replace the biggest guesses.

## The place

(Round 1 fills this in, short, every claim with a source ID.)

## Timeline

(Round 1 fills this in, short, every claim with a source ID.)

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
