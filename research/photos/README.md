# Picture catalog

Every picture we know of that shows the gardens before or after 1860, with where it came from, what we may do with it and what it shows. `catalog.csv` is the single source of truth, edited by hand since Round 3. `scripts/photos_catalog.py` makes the web copies and the credits from it.

## What is where

| Path | What | In git? | Public? |
|---|---|---|---|
| `catalog.csv` | one row per picture (`P0001`...) | yes | no |
| `images/P####.jpg` | **free** images: at most 2000 px up to P0230, at most 1600 px and about 300 KB from then | yes | smaller copies are |
| `../../site/reconstruction/photos/P####.jpg`, `_t.jpg` | free pictures that show an object, 1000 px and 400 px | yes | yes |
| `../raw/photos/P####.jpg` | **research-only** images, at most 1200 px, local use only | **no** | **never** |

## Numbering

P0001–P0040 the Forty Scenes album (P00NN = YMNN), P0041–P0060 the 20 Xiyang Lou plates (P(40+n) = plate n), P0061–P0100 the 1745 woodcuts, P0101–P0140 the Bertin gouaches, P0141+ other prints, drawings and the photographs. Round 3 from P0231, in the order of its hunts: Qing pictures (with the 1887 lithograph, picture and text page per scene), old photographs, today's photographs.

## catalog.csv

- `photo_id`, `title` (original language), `date` (as stated, with where it comes from), `date_from`, `date_to` (years, blank if none), `kind` (painting, engraving, photo, print, plan, render).
- `creator`, `archive`, `archive_id`, `source_id` (S..), `source_url`.
- `licence` (exactly as the holder states it), `attribution`, `rights_class` (`free` or `research-only`).
- `shows`: `ID:sure|likely|guess;...`, building IDs from `../buildings.csv`. `sure`: a printed title, a caption or a unique form. `likely`: a caption without proof for this building. `guess`: position or form only.
- `why`: why we think so. `also_shows`: things without an ID (the whole garden, the whole Xiyang Lou).
- `camera_lat`, `camera_lon`, `bearing`, `camera_note`: blank where nobody could argue one.
- `file`, `width`, `height`, `notes`.
- `crop`: fractions `x0,y0,x1,y1` the web copy is cut to. The album's bifolios show the painting on the site, the file keeps the whole leaf.
- `camera_lat` etc. are estimates by eye from form and footprints for old photographs, or a Commons GPS tag: `camera_note` says which.

Dates are never invented: blank means nobody has stated one.

## Rights

- **free**: public domain, CC0, CC BY, CC BY-SA, as stated by the holder, or PD-Art of a pre-1900 two-dimensional work on Commons.
- **free, with the Gallica note:** BnF album leaves are public domain on Commons, and `notes` says "non-commercial, Gallica credit required", the project rule from `CLAUDE.md`. The credit is "Source gallica.bnf.fr / BnF". Gallica's own licence page refused automated access and was not read.
- **research-only**: everything else. Historical Photographs of China is CC BY-NC-ND, so research-only even when Commons tags a copy PD.
- **Changed in Round 3:** pre-1900 photographs whose Commons file carries a PD tag are free under the rulebook's PD-Art rule, with the tag quoted: all 7 Ohlmer, Piry P0190, Child P0192–94, de Semallé P0196, and Zumbrun P0197 (1920, d. 1941 or 1949). No holder has confirmed them (Q50).
- A `guess` tie is the site today by GPS tag, or form only: it is not evidence for a building, and the panel says `guess`.

## Attribution traps

- Prints credited to Piry, Child or Ohlmer may be by C. F. Moore: his negatives at the Royal BC Museum were long unattributed (S91).
- Beato's 1860 photographs (P0180–P0182) show Qingyi Yuan, not this garden: they have no building IDs.
- At 2000 px, a painting on a two-page album leaf is about 960 px wide. The masters are about 24000 px: fetch larger crops of the plates needed for modelling.

## Best picture per key compound, for form

| Compound | Pictures |
|---|---|
| 正大光明 YM01 | P0001 album; P0100 woodcut for line; the 1887 lithograph |
| 九洲清晏 YM03 | P0003 album; P0089 woodcut for line |
| 谐奇趣 XY01 | P0041, P0042; ruin: Ohlmer rows (research-only) |
| 海晏堂 XY08 | P0050 west, P0051 north, P0052 east, P0053 south |
| 大水法 XY10 | P0055; setting P0056; ruin: Sirén 003718, 003719 (research-only) |

**Largest gap:** there is almost no pre-1860 picture of anything outside the Forty Scenes and the Xiyang Lou. Changchun and Qichun rest on the plan, on texts, on later ruin photographs and on the site today.
