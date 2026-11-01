"""Round 6: first version of research/xiyanglou/boxes.csv, the massing of the strip, and of the size and position facts. A record: boxes.csv and research/evidence/facts.csv are edited by hand from here on.

  uv run python docs/rounds/common/palace_r6_boxes_seed.py

Positions and footprints: footprints worker's box rows (the ruin, the plan at ground scale, S603). Heights: dim rows of the plates (method c), C, unless a survey is named. Derived parts are laid out from those by offset, along (a, forward along the facing bearing) and across (c, to the right of it).
"""

import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
rows = {r["id"]: r for r in csv.DictReader(open(ROOT / "research/buildings.csv", encoding="utf-8", newline=""))}
worker = [json.loads(l) for l in open("/opt/data/cache/scratch/palace_r6_out_footprints.jsonl") if '"type": "box"' in l]
LAT_M, LON_M = 111034.0, 85276.0  # metres per degree at 40.01 N


def off(lat, lon, deg, a, c):
    th = math.radians(deg)
    north = a * math.cos(th) - c * math.sin(th)
    east = a * math.sin(th) + c * math.cos(th)
    return round(lat + north / LAT_M, 6), round(lon + east / LON_M, 6)


def wb(bid, part_word):
    for b in worker:
        if b["id"] == bid and part_word in b["part"]:
            return b
    raise KeyError((bid, part_word))


FIELDS = ["building_id", "part", "lat", "lon", "orientation_deg", "frontage_m", "depth_m", "platform_m", "eave_m", "ridge_m", "roof", "tiles", "shape", "double", "stand_m", "over_water", "confidence", "assumed", "sources", "basis"]
out = []


def add(bid, part, lat, lon, deg, f, d, pl, eave, ridge, roof="hip", tiles="glazed", shape="", double=False, stand=0.0, over_water=False, conf="C", assumed=True, sources="S01", basis=""):
    out.append(dict(building_id=bid, part=part, lat=lat, lon=lon, orientation_deg=deg, frontage_m=f, depth_m=d, platform_m=pl, eave_m=eave, ridge_m=ridge, roof=roof, tiles=tiles, shape=shape, double="yes" if double else "", stand_m=stand or "", over_water="yes" if over_water else "", confidence=conf, assumed="yes" if assumed else "", sources=sources, basis=basis))


G = 173.8  # grid of 谐奇趣 and the maze on the ruin, S850

# 谐奇趣 XY01
b = wb("XY01", "main block")
la, lo = b["lat"], b["lon"]
add("XY01", "main block, three levels", la, lo, G, 27.2, 14.0, 1.0, 15.1, 18.3, sources="S01;S850;S108;S71", basis="Footprint: plan and plate 1, depth read on the ruin, S108. Top eave and ridge: plates 1 and 2 agree, 15.1 and 18.3 m. Roof fish-scale on plates 1-2.")
for bid, word, side in (("XY01-01", "west octagon", -1), ("XY01-N01", "east octagon", 1)):
    o = wb(bid, word)
    add(bid, "octagonal music pavilion, two storeys", o["lat"], o["lon"], G, 8.7, 8.7, 0.5, 9.3, 12.5, roof="pyramid", shape="octagon", sources="S01;S850;S71", basis="Rubble at the corridor's end, plan 40 px; plate 1 body 8.9 m. Eave and crown from plate 1.")
    # the curved corridor: flat-roofed, 9 bays (S108), a straight run here from the block's corner to the pavilion
    ca, co = off(la, lo, G, -5, side * 12)
    dn, de = (o["lat"] - ca) * LAT_M, (o["lon"] - co) * LON_M
    length = max(math.hypot(dn, de) - 3, 6)
    bearing = (math.degrees(math.atan2(de, dn)) + 90) % 360
    add(bid, "corridor, 9 bays, curved on the plates; a straight run here", round((ca + o["lat"]) / 2, 6), round((co + o["lon"]) / 2, 6), round(bearing, 1), round(length, 1), 4.0, 0.3, 8.8, 9.6, sources="S108;S71", basis="Cornice on plate 2 8.8 m; S108 says the cornices of block, corridor and octagon are level, within 2 cm.")
p = wb("XY01-02", "pool")
add("XY01-02", "scalloped fountain pool", p["lat"], p["lon"], G, 26.0, 13.0, 0.5, 0.5, 0.5, shape="pool", sources="S01;S850", basis="Centre on today's bank; size as the plan draws it, 26 x 13 m, because the bank (35.6 x 16.2 m) may have spread when re-dug.")
# 蓄水楼 XY02: 5 bays plus a 3-bay north wing, facing east
b = wb("XY02", "five-bay")
deg = 83.8
a1, o1 = off(b["lat"], b["lon"], deg, 0, 3.65)
a2, o2 = off(b["lat"], b["lon"], deg, 0, -6.4)
add("XY02", "reservoir house, two storeys, 5 bays", a1, o1, deg, 12.8, 6.6, 0.5, 7.3, 10.1, sources="S01;S850;S71;S02", basis="Plate 3: whole east front 20.1 m = plan's range, block 12.8 m, cornice 7.3, ridge 10.1. Position from the plan, offset interpolated, err 15 m.")
add("XY02", "north wing, one storey, 3 bays", a2, o2, deg, 7.3, 6.6, 0.3, 4.1, 5.8, sources="S01;S71;S02", basis="Plate 3: wing 7.3 m, cornice 4.1 m, rail top 5.8 m. S02 p.143.")
# 花园门 XY03
b = wb("XY03", "gate")
add("XY03", "south gate of the maze", b["lat"], b["lon"], G, 7.9, 4.2, 0.3, 6.7, 9.0, sources="S01;S850;S71", basis="South gate of today's rebuilt maze; width plan 7.85 m and plate 4 7.8 m. Height plate 4; P0184 reads lower (cornice 4.5 m), Q68.")
# 黄花阵 XY04: 58.56 x 88.64 (S310); walls 1.2 x 0.6; two inner rings stand for the plan, not traced
b = wb("XY04", "maze")
cla, clo = b["lat"], b["lon"]
W, H = 58.56, 88.64
# Outer wall on the block. Two rings stand for the plan and stop short of the hall at the north, whose court today's maze keeps open.
for hw, y0, y1 in ((W / 2, -H / 2, H / 2), (W / 2 - 8, -H / 2 + 8, 26), (W / 2 - 16, -H / 2 + 16, 18)):
    mid, span = (y0 + y1) / 2, y1 - y0
    for a, c, ff, dg in ((y1, 0, 2 * hw, G), (y0, 0, 2 * hw, G), (mid, -hw, span, (G + 90) % 360), (mid, hw, span, (G + 90) % 360)):
        ma, mo = off(cla, clo, G, a, c)
        add("XY04", "maze wall, 1.2 x 0.6 m; outer wall and two rings stand for the plan, not traced", ma, mo, round(dg, 1), round(ff, 2), 0.6, 0.0, 1.2, 1.2, shape="wall", tiles="stone", sources="S310;S850;S109", basis="Block 88.64 x 58.56 m (S310) = today's rebuilt maze as measured (57 x 89 m). Whether the rebuild kept the old wall line is open, Q66.")
b = wb("XY04-01", "central")
add("XY04-01", "round stair base", b["lat"], b["lon"], G, 21.0, 21.0, 0.0, 1.0, 1.0, shape="octagon", tiles="stone", sources="S01;S71", basis="Ring base 21 m on the plan, 23.5 m on plate 5.")
add("XY04-01", "central pavilion, timber with a glazed roof", b["lat"], b["lon"], G, 7.7, 7.7, 0.2, 3.5, 7.0, roof="pyramid", shape="octagon", stand=1.0, sources="S71;S109", basis="Body 7.7 m on plate 5, eaves 13.5 m wide; height a guess. Today's stone pavilion is a redesign of 1987-89.")
b = wb("XY04-N01", "north hall")
add("XY04-N01", "two-storey hall at the back of the maze", b["lat"], b["lon"], G, 18.7, 11.4, 0.5, 6.5, 9.0, sources="S01;S850;S02", basis="Open court of today's maze 18 m wide = plan block. Plate 5 reads 22.8 m. Height a guess, S02 p.145 two storeys.")
# 养雀笼 XY05
b = wb("XY05", "gate block")
add("XY05", "gate block, three gates to the west, a European arch to the east", b["lat"], b["lon"], 263.8, 13.9, 11.6, 0.5, 6.2, 8.5, sources="S01;S850;S71;S02", basis="Plates 6 and 7 both 13.9 m; cornice 5.8 and 6.2; central ridge 8.5, finial 10.1. Plan position, err 15 m: pulled down about 1924, no ruin.")
# 方外观 XY06
h = wb("XY06", "hall")
t = [x for x in worker if x["id"] == "XY06" and "porch" in x["part"]][0]
add("XY06", "hall, porch and curved stairs, as the plan draws them", t["lat"], t["lon"], 175.3, 24.6, 13.3, 0, 1.0, 1.0, shape="terrace", sources="S01;S850", basis="Plan x 9335-9454. Replaces the 'terrace' 44 x 24 m of Round 2: that OSM polygon follows the moat bank.")
add("XY06", "hall, two storeys, 3 bays, double eaves", h["lat"], h["lon"], 175.3, 14.0, 7.0, 0.2, 8.9, 13.0, tiles="blue", double=True, conf="B", assumed=False, sources="S603;S850;S71", basis="L 14, l 7, H 13 m without its stairs (S603, survey). Lower eave 8.9 m on plate 8. Roof colour is S06's blue; a witness of 1876 has violet and green on one pavilion, unnamed: Q69.")
# 五竹亭 XY07: a U open to the north, plate 9 (Q15): back pavilion on the axis, middle pair at 21.5 m between centres, end pair 54.5 m, joined by galleries. The depth of the U is a guess
r = rows["XY07"]
la, lo = float(r["lat"]), float(r["lon"])
deg = 354.0
pav = [(0, 0, 7.0, 6.7, 11.2), (6, -10.75, 7.0, 6.7, 11.2), (6, 10.75, 7.0, 6.7, 11.2), (14, -27.25, 6.8, 7.4, 12.3), (14, 27.25, 6.8, 7.4, 12.3)]
for a, c, w, e, rd in pav:
    ma, mo = off(la, lo, deg, a, c)
    add("XY07", "pavilion, double eaves, bamboo-faced", ma, mo, deg, w, w, 0.3, e, rd, roof="pyramid", double=True, sources="S71;S258;S02", basis="Plate 9: U open to the north, not a row. Pavilion widths and spacings from the plate, scale from an eye height, wide error. The U's depth a guess. Not drawn on S01 (Q15).")
chain = [pav[3], pav[1], pav[0], pav[2], pav[4]]
for (a1, c1, *_), (a2, c2, *_) in zip(chain, chain[1:]):
    ma, mo = off(la, lo, deg, (a1 + a2) / 2, (c1 + c2) / 2)
    add("XY07", "gallery, 18 bays in all, curved on the plate; straight here", ma, mo, round((deg + 90 + math.degrees(math.atan2(a2 - a1, c2 - c1)) * -1) % 360, 1), round(max(math.hypot(a2 - a1, c2 - c1) - 7, 3), 1), 2.4, 0.2, 2.6, 3.2, roof="gable", sources="S71;S310", basis="One-tier galleries joining the pavilions on plate 9; 18 bays in all, S310 (search extract).")
# 海晏堂 XY08
b = wb("XY08", "west block")
add("XY08", "west block, two storeys, 11 bays on the west front", b["lat"], b["lon"], 261.7, 47.2, 22.7, 1.0, 13.2, 15.7, sources="S01;S850;S109;S71", basis="Plan moved 7.8 m onto the ruin. 11 bays (S109) at 4.3 m on plate 10. Eaves and ridge from plate 10; the crown 17.2 m. Note plate 11 reads a lower cornice (9.3 m), Q70.")
b = wb("XY08", "link")
add("XY08", "link to the west machine house", b["lat"], b["lon"], 171.7, 19.0, 9.4, 0.5, 9.0, 10.8, sources="S01;S850;S71", basis="Plan x 9876-9967. Cornice 8.6-9.3 m, rail 10.2-10.8 m on plates 11 and 13.")
b = wb("XY08-N01", "west machine house")
add("XY08-N01", "west waterwheel house 西水车房, taller", b["lat"], b["lon"], 261.7, 25.8, 13.4, 0.5, 9.3, 14.5, sources="S01;S850;S71;S02", basis="Plan x 9967-10031; label 西水?房. Taller part on plate 11, crown 14.5 m. S02 p.155.")
b = wb("XY08-01", "long block")
add("XY08-01", "long block carrying the tank 锡海", b["lat"], b["lon"], 171.7, 27.4, 11.1, 0.5, 9.3, 10.8, sources="S310;S06;S593;S850;S71", basis="Tank 27.36 x 5.92 x 1.44 m (Lei figures through S310, S06; S600 for the depth); core 11 m wide on the ruin, today 6.3-7.2 m high (S593, S110). Upper level as plates 11, 13.")
b = wb("XY08-N02", "east block")
add("XY08-N02", "east block with the zig-zag stairs, N and S parts", b["lat"], b["lon"], 81.7, 26.1, 23.1, 0.5, 10.3, 13.6, sources="S01;S850;S71", basis="Plan x 10154-10264. Plate 12 26.1 m. Hall eaves 10.3, ridge 13.6 m.")
b = wb("XY08-02", "pool")
add("XY08-02", "pool of the twelve hours", b["lat"], b["lon"], 261.7, 15.3, 18.8, 0.5, 0.5, 0.5, shape="pool", sources="S01;S850", basis="Midpoint of the two horseshoe stairs on the ruin; size from the plan's slip, 15.3 N-S, 18.9 W-E.")
# 远瀛观 XY09
b = wb("XY09", "terrace")
add("XY09", "terrace", b["lat"], b["lon"], 172.5, 31.0, 35.0, 0, 2.0, 2.0, shape="terrace", conf="B", assumed=False, sources="S603;S850;S71", basis="35 x c.31 m (S603, survey), order not stated; taken 31 W-E, 35 N-S (plate 14 32.9 m W-E). Replaces the OSM polygon 59 x 51 m, which holds 大水法's niche too. Height a guess.")
b = wb("XY09", "hall")
add("XY09", "hall, five roofs, on the terrace", b["lat"], b["lon"], 172.5, 28.0, 21.0, 0.2, 9.7, 14.6, double=True, stand=2.0, conf="B", assumed=False, sources="S603;S850;S71", basis="21 x 28 m from the post grid (S603), order not stated; taken 28 W-E, against the plan's 20.8 m for 5 bays, Q67. Clock-storey eave 9.7, centre apex 12.4, crown 14.6 m on plate 14.")
# 大水法 XY10
b = wb("XY10", "sunken")
add("XY10", "sunken fountain area, 1.30 m below the gardens (not cut into the ground here)", b["lat"], b["lon"], 172.5, 110.0, 60.0, 0, 0.3, 0.3, shape="court", tiles="stone", conf="B", assumed=False, sources="S603;S850", basis="110 x 60 m, 1.30 m down (S603, survey). Confirmed W-E on the ruin at 109 m.")
b = wb("XY10", "shell pool")
add("XY10", "shell pool", b["lat"], b["lon"], 172.5, 29.0, 19.0, 0.5, 0.5, 0.5, shape="pool", sources="S01;S850;S03", basis="Plan 29.5 x 21 m, ruin 28 x 16.5 m. It lies 14 m south of the row; Round 2 had it on the row.")
b = wb("XY10", "niche")
add("XY10", "niche building", b["lat"], b["lon"], 172.5, 21.2, 4.4, 0.5, 14.3, 14.3, shape="wall", tiles="stone", sources="S01;S850;S71", basis="Plan arc x 10511-10611; plate 15 21.2 m. Pier finials 14.3 m, crown 16.7 m on plate 15.")
for bid in ("XY10-N01", "XY10-N02"):
    b = wb(bid, "round pool")
    add(bid, "round basin, quatrefoil on S603's plan", b["lat"], b["lon"], 172.5, 18.0, 18.0, 0.5, 0.5, 0.5, shape="basin", conf="B", assumed=False, sources="S603;S850", basis="Quatrefoil basins 18 m across, 62 m apart between centres (S603); arcs on the ruin 63 m.")
    b = wb(bid, "pyramid")
    add(bid, "pyramid fountain tower", b["lat"], b["lon"], 172.5, 4.6, 4.2, 0.3, 5.0, 21.2, roof="pyramid", tiles="stone", over_water=True, sources="S01;S71;S02", basis="Base on the plan and plate 15, 4.6 m. Pedestal 5.0, finial 21.2 m on plate 15. S02 p.156 'tall pyramidal fountains'.")
# 观水法 XY11
b = wb("XY11", "throne")
la, lo, deg = b["lat"], b["lon"], 352.5
add("XY11", "throne platform", la, lo, deg, 14.5, 11.5, 0, 1.3, 1.3, shape="terrace", sources="S01;S03;S603", basis="Plan x 10521-10589 on OSM's point. Base 1.3 m, S603 n.17. Err 15 m, under trees: Q71.")
sa, so = off(la, lo, deg, -5.25, 0)
add("XY11", "screen of five marble panels", sa, so, deg, 14.46, 1.0, 0, 5.1, 5.1, shape="wall", tiles="stone", sources="S01;S70;S817", basis="Plan 14.46 m; P0343 14.4 m. Plate 16 draws it 8.4 m. Pier 5.1 m. The panels were re-erected in 1977.")
# 线法山 XY12
b = rows["XY12-02"]
add("XY12-02", "hilltop pavilion", float(b["lat"]), float(b["lon"]), 173.5, 6.9, 6.9, 0.3, 6.2, 12.3, roof="pyramid", shape="octagon", sources="S01;S71", basis="Plate 18: body 6.9 m, eaves 6.2, crown 12.3 m above its platform. Mound in the ground, 42 m across, 8 m high.")
b = rows["XY12-01"]
add("XY12-01", "triple gate", float(b["lat"]), float(b["lon"]), 262.6, 13.6, 2.0, 0.2, 6.1, 6.1, shape="wall", tiles="stone", sources="S01;S71", basis="Gap in the wall 13.6 m; plate 17 13.6 m, cornice 6.1, crown 8.7 m. Depth a guess.")
# 螺蛳牌楼 XY13
b = rows["XY13"]
add("XY13", "east gate, three arches and two side rooms", float(b["lat"]), float(b["lon"]), 262.6, 22.9, 3.0, 0.2, 6.8, 11.0, roof="gable", sources="S01;S71", basis="Plate 19 22.9 m, cornice 6.8, crown 11.0, towers 12.3 m. The plan's figure spans 34-49 m, no check. Depth a guess. Q16.")
# 线法墙 XY15
for x in worker:
    if x["id"] == "XY15" and x["part"].startswith("screen"):
        add("XY15", f"painted screen {x['part'].split()[1]}", x["lat"], x["lon"], 262.6, 7.3, 1.8, 0, 8.7, 8.7, shape="wall", tiles="stone", sources="S01;S03;S71", basis="Plan: N-S elements 7.3 x 1.8 m, moved 5 m as 方河 is. Six a side as on S01 (Q16). Height from plate 20 wall 1, 8.7 m.")
x = wb("XY15", "far wall")
add("XY15", "far wall, painted", x["lat"], x["lon"], 262.6, 13.5, 1.8, 0, 8.7, 8.7, shape="wall", tiles="stone", sources="S01;S02;S03", basis="Plan x 12394-12402. S02: painted back wall.")
for bid, word in (("XY15-N01", "north range"), ("XY15-N02", "south range")):
    x = wb(bid, word)
    add(bid, f"{word}, five bays", x["lat"], x["lon"], x["orientation_deg"], x["frontage_m"], x["depth_m"], 0.8, 7.0, 9.5, sources="S01;S03", basis="Plan, moved 5 m as 方河 is. Heights the strip's default, a guess.")

with open(ROOT / "research/xiyanglou/boxes.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, FIELDS)
    w.writeheader()
    w.writerows(out)
print(len(out), "boxes")
