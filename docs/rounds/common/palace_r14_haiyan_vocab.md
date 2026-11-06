# 海晏堂 Haiyantang (XY08): key-point vocabulary for the readers (Round 14)

The building, west to east (the plates: 10 = P0050 west front, 11 = P0051 north side, 12 = P0052 east end, 13 = P0053 south side):
- **West block**: two storeys, eleven bays on the west front; the two end pavilions (two bays each) have their own square hip roofs (higher ridge); a long middle roof between them; over the centre three bays a panelled **attic** with a broken pediment and a crowning ornament on the axis. Before the end pavilions, single-storey **wings** with flat roofs and balustrades (the "balconies" of plate 10). Free **columns** flank the upper centre door.
- In front (west): a **terrace** at the upper floor's level before the centre door, with a balustrade over the cascade (fish-and-shell group); two broad **stairs** run diagonally from the terrace's ends down and outward to the court, with a half-way **landing**; their inner walls embrace the **pool**; on a **plinth** along each inner wall sit **six seated figures** with animal heads (the water clock), numbered 1 (at the back, by the terrace) to 6 (at the front, nearest the viewer of plate 10). In the pool on the axis: the great **shell** and in front of it a tiered **vase fountain**. Two great **pedestals** stand at the court's front corners.
- Behind the west block: a low arcaded **link** with a balustraded roof, then the **water building** of thirteen bays on its N and S fronts (3 + 7 + 3, the end sections slightly forward), one tall storey with a balustrade on the roof; on the roof at each end a **raised tier** (small hall with its own hip roof): the west tier (wbpav_W) and the east tier (wbpav_E; on plate 12 it is the hall seen over the stairs).
- The **east block** with the zig-zag stairs (plate 12): flight 1 rises from the court beside the central arched door outward to the lowest landings at the outer ends (L1); flight 2 back inward to the middle landing over the door (L2); flight 3 outward again to the top (L3 at the outer ends, the top platform behind).

Compass: N is the left side of plate 10 and the right of plate 12; on plate 11 west is right, on plate 13 west is left. "W end" of the water building is its end next to the west block.

## Points (name: definition)

West block
- `blk_foot_NW`, `blk_foot_SW`, `blk_foot_NE`, `blk_foot_SE`: foot of the west block's corner (outer corner of the plinth on the pavement). NE/SE are the corners at the block's rear (east), seen on plates 11 and 13.
- `blk_cornice_NW`, `..._SW`, `..._NE`, `..._SE`: outer end of the main cornice's top at that corner (where the roof's tiles sit on it).
- `blk_eave_NW`, `..._SW`, `..._NE`, `..._SE`: tip of the end pavilion's upturned eave at that corner.
- `blk_ridge_N`, `blk_ridge_S`: the outer end of the north (south) end pavilion's short ridge (below the ridge ornament).
- `midroof_ridge_N`, `midroof_ridge_S`: where the long middle roof's ridge meets the end pavilion's roof, north and south.
- `attic_top_N`, `attic_top_S`: outer top corner of the attic block's cornice (the attic over the centre bays), N and S.
- `blk_ped_apex_W`: top of the attic's broken pediment where the crowning ornament starts. `attic_crest_top`: top of that ornament.
- `blk_door_W_head`: top of the upper centre door's opening (inner edge of its frame).
- `colW_N_cap`, `colW_S_cap`: top of the capital of the free column N (left on plate 10) and S of the upper door.
- `end_panel_N`, `end_panel_S`: centre of the great framed panel on the upper storey of the block's north (south) end face (plates 11, 13).
- `wing_rail_NW`, `wing_rail_SW`: top of the wing's (balcony's) balustrade at its outer front corner (north wing on the left of plate 10).

Terrace, stairs, water clock
- `blk_stair_land_W`: top of the terrace's front parapet on the axis (base of the cascade group).
- `terr_rail_N`, `terr_rail_S`: top of the end post of the balustrade along the terrace's front, north and south ends.
- `stair_N_landing`, `stair_S_landing`: top of the post at the front (lower) end of the half-way landing, on the stair's inner balustrade (the one above the figures).
- `stair_N_foot`, `stair_S_foot`: the outer corner of the stair's lowest step on the court.
- `zod_N1_head`, `zod_N6_head`, `zod_S1_head`, `zod_S6_head`: top of the head of figure 1 (back) and figure 6 (front) of the north (left on plate 10) and south rows.
- `zod_plinth_N6_front`, `zod_plinth_S6_front`: the plinth's top corner at its front end, on the pool side.
- `pool12_rim_W`: top of the pool's front rim on the axis. `pool12_rim_L`, `pool12_rim_R`: the left- and right-most points of the front rim's outer edge as seen.
- `shell_top`: top edge of the great shell on the axis. `vase_top`: top of the vase fountain (where its jet leaves it).
- `ped_N_top`, `ped_S_top`: middle of the top of the great pedestal's cornice (below its crown), N (left on plate 10) and S.

Link, water building, raised tiers
- `link_rail_N`, `link_rail_S`: top of the link's roof balustrade at its corner against the west block (north, south side).
- `wb_foot_NW`, `wb_foot_NE`, `wb_foot_SW`, `wb_foot_SE`: foot of the water building's outer corner (the end section's corner) on that front, W end and E end.
- `wb_cornice_NW` ... `_SE`: outer end of the cornice's top at those corners.
- `wb_rail_NW` ... `_SE`: top of the roof balustrade's corner post at those corners.
- `wb_door_NW_head`, `wb_door_NC_head`, `wb_door_NE_head` (and `_S..`): top (crown) of the arched door in the W end section, the centre, the E end section, on the N (S) front.
- `wbpav_W_eave_NW`, `_NE`, `_SW`, `_SE`; `wbpav_E_eave_NW` ... : the raised tier's roof eave corner tips. `wbpav_W_ridge`, `wbpav_E_ridge`: middle of that tier's ridge (below any ornament).
- `tank_top_W`: the reservoir's parapet top at its west end, on the axis (only if a picture shows it).

East block (plate 12)
- `es_door_head`: crown of the central arched door. `es_foot_N`, `es_foot_S`: foot of flight 1 beside the door (lowest step's corner at the door side), N (right on plate 12) and S (left).
- `es_corner_NE_foot`, `es_corner_SE_foot`: foot of the block's outer east corner.
- `es_L1_rail_N`, `es_L1_rail_S`: top of the corner post of the lowest landing's balustrade at the block's outer east corner.
- `es_L2_rail_C`: top of the middle landing's balustrade over the door, on the axis.
- `es_L3_rail_N`, `es_L3_rail_S`: top of the corner post of the top level's balustrade at the outer end (front corner).
- `es_top_rail_C`: top of the top level's balustrade on the axis (behind the middle landing).

## How to read
- Pixel x, y in the copy `research/photos/images/<photo_id>.jpg` at its native size (plates 2400 px wide). Origin top left.
- `sure`: 1 sharp and unambiguous; 2 good; 3 rough (hidden by a tree, worn, ruin edge). A point you cannot find: leave it out. A reading that is not quite the defined point: write it with `use` = `skip: <reason>`.
- Check every reading: draw a small cross at it on a fresh crop (Python PIL, `/opt/data/workspace/000_Dev/palace-beijing-yaga-sh/.venv/bin/python`), look at the crop, correct, and say in the note what you saw.
- Ruin photographs (1873-1920): the roofs are gone. Read only what still stands as built (cornices, door heads, balustrades, feet). Never guess a vanished part.
