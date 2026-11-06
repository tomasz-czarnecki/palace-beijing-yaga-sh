"""Round 16: merge the readers' key points into research/xiyanglou/plate_keypoints.csv and their camera priors into photo_viewpoints.csv. Run once; a second run adds nothing.

  python docs/rounds/common/palace_r16_merge.py /opt/data/cache/scratch/palace_r16_yuanying_kp_reader*.csv
"""
import csv
import sys
from pathlib import Path

XY = Path(__file__).resolve().parents[3] / "research/xiyanglou"
kp = XY / "plate_keypoints.csv"
rows = list(csv.DictReader(open(kp, encoding="utf-8")))
fields = list(rows[0].keys())
have = {(r["photo_id"], r["object"], r["point"]) for r in rows}
added = 0
for f in sys.argv[1:]:
    for r in csv.DictReader(open(f, encoding="utf-8")):
        r = {k: (r.get(k) or "").strip() for k in fields}
        if not r["photo_id"] or not r["point"]:
            continue
        key = (r["photo_id"], r["object"], r["point"])
        if key in have:
            print("dup kept old", key)
            continue
        r["x"] = str(int(round(float(r["x"]))))
        r["y"] = str(int(round(float(r["y"]))))
        rows.append(r)
        have.add(key)
        added += 1
w = csv.DictWriter(open(kp, "w", newline="", encoding="utf-8"), fieldnames=fields)
w.writeheader()
w.writerows(rows)
print("key points added", added)

# The readers' priors (notes in /opt/data/cache/scratch/palace_r16_yuanying_notes_reader*.md, summed up in models/XY09-yuanying-guan/README.md and
# models/XY06-fangwai-guan/README.md). eye_m is above the ground model at the camera: for 远瀛观 the readers gave the eye above the terrace's floor, and the ground
# model has no terrace (Round 10 draws the plain; the terrace is the model's), so 4.3 m is added.
T = 4.3
PRIORS = [
    ("P0183", "XY09", 40.012244, 116.306596, 352.5, 11, 4, 3.0 + T, 1.5, "Round 16 reader 1: on the axis (door, clock and columns' midpoint on one x), level camera; the frame 2.0 column spacings wide; the eye 3 m above the terrace (the horizon row high: cropped, a rising front or rubble).", 42),
    ("P0190", "XY09", 40.012262, 116.306593, 352.5, 9, 3, 3.0 + T, 1.5, "Round 16 reader 1: on the axis, nearer than P0183; the attic already fallen (after P0183).", 45),
    ("P0179", "XY09", 40.012209, 116.306566, 352, 15, 6, 1.5 + T, 1.0, "Round 16 reader 2: the W column near the frame's centre, about 3 m west of the axis; grass in front.", 45),
    ("P0772", "XY09", 40.012209, 116.306566, 352, 15, 6, 1.5 + T, 1.0, "Round 16 reader 2: the same negative as P0179 at two thirds the scale; not a second camera.", 45),
    ("P0216", "XY09", 40.012123, 116.306593, 352, 24, 8, 2.5 + T, 1.5, "Round 16 reader 2: frontal, the door axis 150 px right of the centre (about 2 m west of the axis); the rubble seen from above: a heap or a rising front.", 45),
    ("P0291", "XY09", 40.012173, 116.306703, 330, 22, 8, 1.5 + T, 1.0, "Round 16 reader 2: from the south-east: the door's W reveal and the block's E face show.", 45),
    ("P0719", "XY09", 40.012206, 116.306579, 355, 15, 6, 1.0 + T, 1.0, "Round 16 reader 2: near frontal, about 2 m west of the axis, looking up a little.", 45),
    ("P0341", "XY09", 40.012062, 116.306509, 6, 32, 12, -1.5 + T, 2.0, "Round 16 reader 2: from the south-west with a long lens; a rubble bank hides the pedestal's foot, the eye at or below the terrace's floor.", 25),
    ("P0757", "XY09", 40.012236, 116.306562, 352, 12, 4, 1.6 + T, 0.5, "Round 16 reader 2: the W column near the frame's centre, frontal; standing on today's paving at the pedestals' level.", 60),
    ("P0780", "XY09", 40.012497, 116.306493, 185, 19, 8, 1.6 + T, 0.8, "Round 16 reader 2: from the north on the terrace, west of the axis (大水法's niche 21 degrees left of the column); one usable point.", 60),
    ("P0773", "XY06", 40.011818, 116.303427, 69, 26, 9, 1.5, 1.0, "Round 16 reader 3: from the south-west, the west end wide and the front pinched (about bearing 240 from the west end); 21 m from the west end's middle.", 45),
    ("P0212", "XY06", 40.011625, 116.303565, 25, 32, 8, 0.5, 1.0, "Round 16 reader 3: about 30 degrees west of the axis; the far horizon just above the porch's foot: the photographer stands low.", 45),
    ("P0296", "XY06", 40.011700, 116.303690, 5, 20, 8, 1.5, 1.0, "Round 16 reader 3: frontal, a little west of the axis; rough.", 45),
    ("P0304", "XY06", 40.011680, 116.303770, 345, 22, 9, 1.5, 1.0, "Round 16 reader 3: frontal, a little east of the axis; rough.", 45),
    ("P0295", "XY06", 40.011751, 116.304032, 300, 30, 12, 1.0, 1.0, "Round 16 reader 3: from the south-east, rough.", 45),
    ("P0355", "XY06", 40.011733, 116.303742, 355, 17, 4, 1.0, 0.7, "Round 16 reader 3: on the axis, on the walk below the platform; the porch's piers 333 px for about 5.1-5.7 m with a 66-degree lens.", 66),
]
vp = XY / "photo_viewpoints.csv"
vrows = list(csv.DictReader(open(vp, encoding="utf-8")))
vfields = list(vrows[0].keys())
vhave = {r["photo_id"] for r in vrows}
vadded = 0
for pid, oid, lat, lon, b, d, e, eye, sd, basis, hfov in PRIORS:
    if pid in vhave:
        continue
    vrows.append({"photo_id": pid, "id": oid, "lat": f"{lat:.6f}", "lon": f"{lon:.6f}", "bearing": f"{b:g}", "dist_m": f"{d:g}", "err_m": f"{e:g}", "eye_m": f"{eye:g}", "eye_sd": f"{sd:g}", "basis": basis, "hfov_deg": f"{hfov:g}"})
    vadded += 1
w = csv.DictWriter(open(vp, "w", newline="", encoding="utf-8"), fieldnames=vfields)
w.writeheader()
w.writerows(vrows)
print("viewpoints added", vadded)
