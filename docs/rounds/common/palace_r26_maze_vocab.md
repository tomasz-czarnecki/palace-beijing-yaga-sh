# 黄花阵 Huanghua Zhen (XY04) and 养雀笼 Yangque Long (XY05): key-point vocabulary for the readers (Round 26)

Read points on the free copies in `research/photos/images/<photo id>.jpg`, in **that file's own pixels** (plates are 2400 px wide; x right, y down, from the top-left corner). Write one CSV row per point:

`plate,photo_id,object,point,x,y,sure,use,note`

- `plate`: 5, 6 or 7 for a plate, empty for a photograph. `object`: XY04 or XY05.
- `sure`: 1 (the point is sharp and certainly the named one, within about 3 px), 2 (within about 8 px), 3 (a guess at where it is, about 15 px; hidden, worn, or the engraver's line is vague).
- `use`: empty; or `skip: <reason>` for a point you read but that should not enter a fit (it is a line, not a point; the plate draws it inconsistently).
- `note`: what exactly you clicked, in a few words.
- Read only what you can see. A point hidden by a tree is not read. Do not guess a point from symmetry.
- L and R are **as seen in the picture** (the picture's left and right).

## 黄花阵 XY04, plate 5 = P0045 (花园正面, the maze from the south, high up)

The maze block: a rectangle of low carved-brick walls seen from the south, high above, the long side running away from the viewer. The **outer wall** rings it; the south (near) wall runs across the bottom with the **south gate** on the axis (two piers with pineapple finials, an arched panel behind: that is 花园门 XY03, do not read the gate itself). At the middle of the west and east sides, a **side gate**: two piers with pineapple finials and iron gate leaves (the west one at the picture's left, with a small bridge over the stream outside). In the middle, the **drum**: a round podium with carved panels; before it a short straight flight and two **curved flights** that climb round the drum behind a curved **parapet** with a balustrade, posts with urns at the flights' front ends; on the drum the **octagonal pavilion**: columns at its corners, an arch in each large face, an entablature, a tiled skirt roof, a ribbed dome, a small open lantern, a ball finial. Behind it, at the north end, the **north hall** (Chinese tiled roof, finials on the ridge ends) with terraces and balustrades either side. Four big weeping trees (umbrella-shaped) stand in the maze. Clipped three-tier trees stand on the walls (do not read them).

### Points
- `owall_foot_SW`, `owall_foot_SE`: the outer wall's outer corner at the bottom left and bottom right of the block (south-west and south-east corners), where the wall meets the ground outside it. `owall_top_SW`, `owall_top_SE`: the same corners at the wall's top (the top outer edge of the coping).
- `owall_top_NW`, `owall_top_NE`: the far (north) corners of the outer wall at its top, outer edge.
- `swall_top_gate_L`, `swall_top_gate_R`: the near (south) outer wall's top outer edge where it stops at the south gate (the gate's left and right side).
- `wgate_finial_L`, `wgate_finial_R`: the top of the pineapple finial on the west side gate's left and right pier (as seen). `wgate_pier_top_L`, `wgate_pier_top_R`: the top of that pier's cap (under the finial), its front middle. Same `egate_` for the east side gate (the picture's right side).
- `front_step_foot_C`: the bottom edge of the lowest step of the straight flight before the drum, on the axis.
- `drum_foot_C`: the foot of the drum's front face on the axis (where it meets the landing above the straight flight).
- `drum_top_C`: the top edge of the drum's front (its cornice under the pavilion's floor), on the axis.
- `ring_post_L_top`, `ring_post_R_top`: the top of the post (with an urn: read the urn's top) at the front end of the left and right curved flight's parapet.
- `ring_rail_L_out`, `ring_rail_R_out`: the parapet's balustrade top at its outermost point to the left and right (the extreme of the curve as seen).
- `pav_col_SW_foot`, `pav_col_SE_foot`: the foot of the two columns at the corners of the pavilion's front (south) face, where they stand on the drum. `pav_col_SW_cap`, `pav_col_SE_cap`: the top of their capitals.
- `pav_ent_top_C`: the top of the pavilion's entablature (cornice) on the front face's middle.
- `pav_arch_head_S`: the crown of the arch of the front face's opening.
- `pav_eave_L`, `pav_eave_R`: the tiled skirt roof's eave at its outermost left and right.
- `pav_dome_top`: the top of the dome where the lantern stands on it. `pav_lantern_top`: the top of the lantern's roof (under the ball). `pav_finial_top`: the top of the ball finial.
- `hall_eave_SW`, `hall_eave_SE`: the north hall's front eave corners (the roof's lower front corners), left and right. `hall_ridge_W`, `hall_ridge_E`: the ends of its main ridge (at the ridge, not the finial). `hall_finial_W`, `hall_finial_E`: the top of the finials on the ridge ends.
- `tree_SW_top`, `tree_SE_top`, `tree_NW_top`, `tree_NE_top`: the top of the four big weeping trees' crowns (SW = front left, NE = back right).

## 养雀笼 XY05, west front: plate 6 = P0046 (养雀笼西面)

A gate building seen from the west on its axis. In the middle, a **portico** of two tall round **central columns** under a Chinese tiled roof with two tall finials on the ridge ends and a scrolled ornament between them; behind the columns, the **door**: an arched opening in a carved frame with doors. Either side, a **wing** a little lower: columns in front and Chinese tiled roofs with finials; between the columns, the **cage walls** drawn as a net (a mesh) with a fan-headed arched window in each; before them, two **statues** on lotus pedestals flanking the door. Beyond each wing a still lower roof joins the walls. Left (as seen) is north.

### Points
- `w_col_C_L_foot`, `w_col_C_R_foot`: the foot of the left and right central column's shaft (the top of its base or pedestal), front middle. `w_col_C_L_cap`, `w_col_C_R_cap`: the top of their capitals (under the beam), front middle.
- `w_roof_C_eave_L`, `w_roof_C_eave_R`: the central roof's front eave corners (the tips), left and right. `w_ridge_C_L`, `w_ridge_C_R`: its ridge ends. `w_finial_C_L`, `w_finial_C_R`: the top of the two tall finials. `w_crest_C_top`: the top of the scrolled ornament on the ridge's middle.
- `w_door_head`, `w_door_sill`: the crown and the threshold of the door's opening, inside the carved frame.
- `w_wing_L_col_out_foot`, `w_wing_R_col_out_foot`: the foot of the outermost column of the left and right wing. `w_wing_L_col_out_cap`, `w_wing_R_col_out_cap`: the top of its capital.
- `w_wing_L_eave_out`, `w_wing_R_eave_out`: the outer front eave tip of the left and right wing's roof. `w_wing_L_ridge_out`, `w_wing_R_ridge_out`: the outer end of that roof's ridge.
- `w_cagewin_L_head`, `w_cagewin_R_head`: the crown of the fan-headed arched window in the left and right cage wall. `w_cagewin_L_sill`, `w_cagewin_R_sill`: the bottom of that window's opening.
- `w_statue_L_top`, `w_statue_R_top`: the top of the left and right statue.

## 养雀笼 XY05, east front: plate 7 = P0047 (养雀笼东面) and the photographs P0192, P0175, P0178, P0168

A European gate front seen from the east. Its plan is **concave**: the two **end pavilions** come forward, each with two round columns and a pier on pedestals, the main cornice over them, a balustrade on top with three tall **finials** on each end; between each end pavilion and the centre, a **niche** with a shell head and a fountain (a vase over a shell basin); the **centre bay** between two piers: a tall **arch** with an iron gate (plate) or an empty opening (photographs), a big scrolled cartouche over it reaching into the balustrade, lattice panels either side of it; a single finial over each of the two piers next to the centre. The balustrade curves with the plan and rises to a **crest** (scrolls and a shell) over the centre. Left (as seen) is south. On the photographs the stone is a ruin: read only what stands; the lower parts may be cut off by the frame or buried in rubble (P0192's base is cut).

### Points
- `e_arch_head`: the crown of the central arch's opening (the intrados, inside the moulded frame). `e_arch_foot_L`, `e_arch_foot_R`: the bottom of the arch's opening at its left and right jamb (the threshold level). `e_impost_L`, `e_impost_R`: the top of the jambs' capitals where the arch springs (inside edge of the opening).
- `e_pier_C_L_cap`, `e_pier_C_R_cap`: the top of the capital of the pier (pilaster) just left and right of the arch, front middle.
- `e_col_L_out_foot`, `e_col_R_out_foot`: the foot of the shaft of the outermost round column on the left and right end pavilion (top of its pedestal), front. `e_col_L_out_cap`, `e_col_R_out_cap`: the top of its capital.
- `e_cornice_L_end`, `e_cornice_R_end`: the top of the main cornice at the outer front corner of the left and right end pavilion.
- `e_rail_L_end`, `e_rail_R_end`: the top of the balustrade's pedestal at the outer front corner of the left and right end (under the finial).
- `e_finial_L_out`, `e_finial_R_out`: the top of the outermost finial on the left and right end. `e_finial_L_in`, `e_finial_R_in`: the top of the finial over the pier next to the centre bay.
- `e_crest_top`: the top of the crest over the centre.
- `e_niche_L_head`, `e_niche_R_head`: the crown of the left and right niche's opening (under the shell head's frame). `e_niche_L_basin`, `e_niche_R_basin`: the top of the front of the shell basin at the niche's foot.
- `e_foot_L_out`, `e_foot_R_out`: the foot of the façade (its plinth meeting the ground or the pavement) at the outer front corner of the left and right end pavilion.
