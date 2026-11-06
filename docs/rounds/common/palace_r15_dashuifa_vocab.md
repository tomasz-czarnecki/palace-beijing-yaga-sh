# 大水法 Dashuifa (XY10) and 观水法 Guanshuifa (XY11): key-point vocabulary for the readers (Round 15)

The two face each other across the sunken fountain court of the Xiyang Lou, on one north-south axis: 大水法 at the north edge (its front faces south), 观水法 at the south edge (its front faces north). 远瀛观 XY09 stands on its raised terrace right behind (north of) 大水法.

**大水法 XY10** (plate 15 = P0055, seen from the south; west is the left of the picture):
- The **niche** on the axis: a tall frame with a square-headed opening (the recess of the cascade, a lion mask near its top), two side posts, and over them a heavy **arch head** (a semicircular hood with scrolls at its shoulders); above the head a **crest** with a shell. Today the head stands broken at its crown and the crest is gone (P0641); in 1873 the crest was whole (P0776).
- Either side of the niche, after a gap where vases stood, a great square **pier** with a crowning cornice (an entablature block) and, in the 1780s, a tall vase-like **finial**; the pier's lower part flares out in concave **console** scrolls to its foot on the stepped base.
- Beyond each pier, a **stair** runs from the court up and back to the 远瀛观 terrace; its outer parapet is the ribbed band of plate 15 ending at its foot in a great **volute** (the "great scroll" of the ruin photographs; the volutes now lie loose, re-laid in 1978-83).
- Below the niche, the cascade's stepped **base courses**, then the lobed **basin** with its rim, a **stag** in the middle and **hounds** round it.
- Left and right, the two **towers** (pyramids of tiers) on square carved **pedestals**, each in its own lobed **tower basin** ringed with jets. The two tiered "columns" in plate 15's foreground are clipped trees (Q212): not read.

**观水法 XY11** (plate 16 = P0056, seen from the north looking south; **east is the left of the picture**):
- The **screen**: a concave wall of five carved **panels** (numbered C in the middle, then 1 and 2 outward, E or W) with pilasters between, a **socle** (base) below with relief panels, a main **cornice** above, a **crest** with finials over it; a taller **end pier** at each end.
- Before the screen the round **throne platform** with its curved **steps** (five today, P0344) and, in the 1780s, the **throne** on it, a low balustrade with trophies, two **trophy pedestals** at its front corners and two **obelisks** beyond them.
- Left and right, the two **side gates** in the garden wall, up a flight of steps from the court; clipped hedges and the plain **back wall** between them.

## Points (name: definition)

### 大水法 XY10
Niche
- `niche_crest_top`: top of the crest (the shell ornament over the arch head) on the axis. 1780s plate and 1873 only.
- `niche_head_top`: top of the arch head's outer curve on the axis (where the crest sits; read on a ruin only where the head is whole there, else skip).
- `niche_head_W`, `niche_head_E`: the outermost point of the arch head's shoulder scroll, W (left) and E (right).
- `niche_open_top`: the top of the niche opening (the underside of the head or lintel) on the axis.
- `niche_open_foot_W`, `niche_open_foot_E`: the bottom corners of the niche opening, where its sides meet the sill.
- `niche_post_cap_W`, `niche_post_cap_E`: the outer top corner of the niche frame's side post, at the level where the head springs.
- `cascade_top`: the lion mask's mouth (where the cascade leaves the niche's back), plate 15 only.

Piers
- `pier_W_cap_SW`, `pier_W_cap_SE`, `pier_E_cap_SW`, `pier_E_cap_SE`: the front (south) corners at the top of the pier's crowning cornice, W pier (left) and E pier (right).
- `pier_W_finial_top`, `pier_E_finial_top`: the top of the finial over the pier (1780s, 1873 only).
- `pier_W_flare_S`, `pier_E_flare_S`: on the pier's front face, at mid-width, the point where the straight shaft starts to flare into the console foot.
- `pier_W_foot_S`, `pier_E_foot_S`: the bottom of the pier's console foot at mid-width of the front, where it sits on the stepped base course.

Stairs and volutes (plate 15, P0776 only: the volutes have been moved since)
- `scroll_W_end`, `scroll_E_end`: the outermost, lowest point of the great volute at the stair's foot.
- `scroll_W_top`, `scroll_E_top`: the highest point of the ribbed parapet at its inner end, where it meets the pier.
- `stair_W_rail_low`, `stair_W_rail_high` (and `_E_`): the tops of the lower and upper end posts of a stair balustrade, if a picture shows one (P0776 left).

Basin
- `basin_rim_S`: the top of the basin's front rim on the axis (the front-most point of the lobed outline as drawn).
- `basin_rim_W`, `basin_rim_E`: the left-most and right-most points of the basin rim's outer edge as seen.
- `base_course_C`: the top front edge of the highest base course on the axis, below the niche opening (today's stepped courses: the highest one in front of the niche).
- `stag_top`: top of the stag's antlers. `stag_foot`: foot of the stag's base at the water.

Towers
- `tower_W_ped_top_SW`, `tower_W_ped_top_SE`, `tower_E_ped_top_SW`, `tower_E_ped_top_SE`: the front corners at the top of the pedestal's cornice (W tower at the left).
- `tower_W_ped_foot_SW`, `tower_W_ped_foot_SE` (and `_E_`): the pedestal's front corners at its foot.
- `tower_W_top`, `tower_E_top`: the top of the pyramid's finial, below any jet.
- `twbasin_W_rim_L`, `twbasin_W_rim_R`, `twbasin_W_rim_S` (and `_E_`): the left-most and right-most points of the tower basin's outer rim as seen, and its front-most point (nearest the viewer).

### 观水法 XY11 (east = the picture's left on plate 16)
Screen
- `scr_cornice_E`, `scr_cornice_W`: the outer top corner of the screen's main cornice at its end (over the end pier).
- `scr_endpier_top_E`, `scr_endpier_top_W`: the top front outer corner of the end pier as it stands (today's tops may be broken: write sure 3 and say so, or skip).
- `pan_C_top`, `pan_C_foot`: the middle of the centre panel frame's top and bottom edges.
- `pan_E1_top`, `pan_W1_top`, `pan_E2_top`, `pan_W2_top`, `pan_E2_foot`, `pan_W2_foot`: the same for the inner (1) and outer (2) panels.
- `socle_top_C`: the top of the socle under the panels, on the axis, on its front face.
- `socle_foot_E`, `socle_foot_W`: the foot of the socle at its outer ends (front corner).
- `crest_top_C`: the top of the central crest or finial over the cornice on the axis (plate, 1873).
- `finial_E_top`, `finial_W_top`: the top of the outermost finial over the end pier.

Platform
- `plat_front_C`: the top front edge of the platform (the top step's front edge) on the axis.
- `steps_foot_C`: the front edge of the lowest step on the axis.
- `steps_foot_E`, `steps_foot_W`: the outer ends of the lowest step (where the curve meets the socle or the side).
- `throne_top`: the top of the throne's back (plate only).
- `trophy_E_ped_top`, `trophy_W_ped_top`: the front middle of the top of the pedestal under the trophy at the platform's front corner.
- `obel_E_top`, `obel_W_top`: the obelisk's top. `obel_E_foot`, `obel_W_foot`: the middle of its front face at the foot.

Gates and wall (plate only unless a photograph shows them)
- `gate_E_top`, `gate_W_top`: the top of the side gate's crest.
- `gate_E_jamb_in`, `gate_W_jamb_in`: the foot of the gate's inner jamb (the side nearer the screen) at the threshold.
- `gate_E_steps_foot`, `gate_W_steps_foot`: the middle of the front edge of the lowest step of the gate's flight, on the court.
- `wall_top_E`, `wall_top_W`: the top of the back wall where it meets the gate.

## How to read
- Pixel x, y in the copy `research/photos/images/<photo_id>.jpg` (or `research/raw/photos/<photo_id>.jpg` for a research-only picture) at its native size (plates 2400 px wide). Origin top left.
- `sure`: 1 sharp and unambiguous; 2 good; 3 rough (hidden by a tree, worn, a ruin's edge). A point you cannot find: leave it out. A reading that is not quite the defined point: write it with `use` = `skip: <reason>`.
- Check every reading: draw a small cross at it on a fresh crop (Python PIL, `/opt/data/workspace/000_Dev/palace-beijing-yaga-sh/.venv/bin/python`), look at the crop, correct, and say in the note what you saw.
- Ruin photographs (1873-today): read only what still stands as built. Never guess a vanished part. The volutes and many basin stones were moved: skip them on photographs after 1873 unless they plainly stand in place.
- The columns of 远瀛观 seen behind 大水法 are another building: never read them as 大水法.
