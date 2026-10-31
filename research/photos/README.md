# Picture catalog

Every picture we know of that shows the gardens before or after 1860, with where it came from, what we may do with it and what it shows. `catalog.csv` is the single source of truth. It is written by `scripts/build_catalog.py` from `../plan/photos_raw.csv`.

## What is where

| Path | What | In git? | Public? |
|---|---|---|---|
| `catalog.csv` | one row per picture (`P0001`...) | yes | no |
| `images/P####.jpg` | **free** images, at most 2000 px | yes | not yet; Round 2 or later copies what the site needs, with credits |
| `../raw/photos/P####.jpg` | **research-only** images, at most 1200 px, local use only | **no** | **never** |

## Numbering

P0001–P0040 the Forty Scenes album (P00NN = YMNN), P0041–P0060 the 20 Xiyang Lou plates (P(40+n) = plate n), P0061–P0100 the 1745 woodcuts, P0101–P0140 the Bertin gouaches, P0141+ other prints, drawings and the photographs.

## catalog.csv

- `photo_id`, `title` (original language), `date` (as stated, with where it comes from), `date_from`, `date_to` (years, blank if none), `kind` (painting, engraving, photo, print, plan, render).
- `creator`, `archive`, `archive_id`, `source_id` (S..), `source_url`.
- `licence` (exactly as the holder states it), `attribution`, `rights_class` (`free` or `research-only`).
- `shows`: `ID:sure|likely|guess;...`, building IDs from `../buildings.csv`. `sure`: a printed title, a caption or a unique form. `likely`: a caption without proof for this building. `guess`: position or form only.
- `why`: why we think so. `also_shows`: things without an ID (the whole garden, the whole Xiyang Lou).
- `camera_lat`, `camera_lon`, `bearing`, `camera_note`: left blank so far; no estimates were made.
- `file`, `width`, `height`, `notes`.

Dates are never invented: blank means nobody has stated one.

## Rights

- **free**: public domain, CC0, CC BY, CC BY-SA, as stated by the holder, or PD-Art of a pre-1900 two-dimensional work on Commons.
- **free, with the Gallica note:** BnF album leaves are public domain on Commons, and `notes` says "non-commercial, Gallica credit required", the project rule from `CLAUDE.md`. The credit is "Source gallica.bnf.fr / BnF". Gallica's own licence page refused automated access and was not read.
- **research-only**: everything else, including no stated holder. All 7 Ohlmer photographs are research-only for that reason: Commons has them as public domain, but no holder has confirmed it. Historical Photographs of China is CC BY-NC-ND, so research-only even when Commons tags a copy PD.

## Attribution traps

- Prints credited to Piry, Child or Ohlmer may be by C. F. Moore: his negatives at the Royal BC Museum were long unattributed (S91).
- Beato's 1860 photographs (P0180–P0182) show Qingyi Yuan, not this garden: they have no building IDs.
- At 2000 px, a painting on a two-page album leaf is about 960 px wide. The masters are about 24000 px: fetch larger crops of the plates needed for modelling.

## Best picture per key compound, for form

| Compound | Pictures |
|---|---|
| 正大光明 YM01 | P0001 album; P0100 woodcut for line |
| 九洲清晏 YM03 | P0003 album; P0089 woodcut for line |
| 谐奇趣 XY01 | P0041, P0042; ruin: Ohlmer rows (research-only) |
| 海晏堂 XY08 | P0050 west, P0051 north, P0052 east, P0053 south |
| 大水法 XY10 | P0055; setting P0056; ruin: Sirén 003718, 003719 (research-only) |

**Largest gap:** there is almost no pre-1860 picture of anything outside the Forty Scenes and the Xiyang Lou. Changchun and Qichun rest on the plan and on later ruin photographs.
