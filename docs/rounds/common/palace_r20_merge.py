"""Round 20: the one-off merge of the four readers' rows (gardens, water, camps, maps; scratch files palace_r20_surroundings_rows_<topic>.csv, _geo_, _sources_) into the hand-edited sheets of research/surroundings/.

A record of how the sheet was first made, like docs/rounds/common/palace_r12_merge.py. From Round 20 on research/surroundings/features.csv and geometry.geojson are edited by hand; rerunning this overwrites them.

  uv run python docs/rounds/common/palace_r20_merge.py <scratch dir>

The editor's decisions are the table PICK below: which reader's row stands for an object (the others become its cross-checks, their sources and positions added to the note), the id it gets (OW###, in the order of the table, never renumbered once committed), its kind, how its shape is given and how the view masses it.
New sources get S1200 on (research/sources.md, section "Round 20"); a reader's source that names an existing S-id keeps it.
"""

import csv
import json
import math
import re
import sys
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import LineString, Polygon, mapping, shape
from shapely.ops import polygonize, unary_union

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
from scene1860 import to_xz  # noqa: E402

SC = Path(sys.argv[1] if len(sys.argv) > 1 else "/opt/data/cache/scratch")
OUT = ROOT / "research/surroundings"
TOPICS = ("gardens", "water", "camps", "maps")
FIRST_S = 1200

# (reader's key, kind or None (the reader's), geom override or None, width_m, massing, joins, layer_id, also (other readers' keys for the same object))
# Order = id order and the order of precedence in the view: sourced and small things first, villages and camps last.
PICK = [
    # --- the neighbouring gardens
    ("G-qingyi", None, None, "", "parts=116.26930 39.99760 18x18x20|116.26930 39.99705 30x16x8|116.26930 39.99650 36x20x6|116.26925 39.99880 20x12x8;within=350;label=1", "", "", "M-ams-yuhe-yihe;M-l86-wanshoushan"),
    ("G-jingming", None, "osm:way/989069291", "", "wall=1;parts=116.24253 39.99275 9x9x30", "", "", "M-ams-jingmingyuan;M-l86-yuquanshan"),
    ("G-changchun", None, None, "", "wall=1", "", "", ""),
    ("G-xihua", None, None, "", "wall=1", "", "", ""),
    ("G-gengzhitu", None, "pt:116.25950 39.99250 r=90", "", "compound=90x70;halls=3", "", "", ""),
    ("G-chenghuai", None, None, "", "compound=110x90;halls=4", "", "", ""),
    ("G-chengze", None, "pt:116.29335 39.99128 r=110", "", "wall=1;compound=120x100;halls=3", "", "", "M-ams-chengzeyuan"),
    ("G-weixiu", None, None, "", "wall=1;compound=150x120;halls=3", "", "", ""),
    ("G-shuchun", None, "pt:116.30325 39.99317 r=260", "", "wall=1", "", "", ""),
    ("G-langrun", None, "pt:116.30450 39.99700 r=130", "", "wall=1;compound=110x90;halls=3", "", "", ""),
    ("G-jingchun", None, "pt:116.30250 39.99500 r=90", "", "wall=1;compound=80x70;halls=2", "", "", ""),
    ("G-minghe", None, "pt:116.30050 39.99550 r=110", "", "wall=1;compound=90x80;halls=2", "", "", ""),
    ("G-jixian", None, "pt:116.29970 39.98988 r=90", "", "wall=1;compound=90x80;halls=3", "", "", ""),
    ("G-xichun", None, "pt:116.31687 40.00173 r=200", "", "wall=1;compound=140x110;halls=4", "", "", ""),
    ("G-jinchun", None, None, "", "wall=1", "", "", ""),
    # --- water
    ("G-kunming", "lake", "geo", "", "", "", "W0901", "W-kunming;M-l86-kunminghu"),
    ("NEW-weiming", "lake", "geo", "", "", "", "W0902", ""),
    ("W-yuquan", None, None, "", "label=1", "", "", ""),
    ("W-yuhe", None, None, "12", "", "", "", ""),
    ("W-jinhe", None, None, "10", "", "", "", ""),
    ("M-ams-canal-changhe", "canal", None, "18", "", "", "", "W-changhe;M-l86-canal-changhe"),
    ("W-wanquan-up", None, None, "8", "", "", "", ""),
    ("W-erlong-canal", None, None, "6", "", "", "", ""),
    ("W-machang", None, None, "8", "", "end@G30", "", ""),
    ("W-honghe", None, None, "8", "", "", "", ""),
    ("W-qikong-out", None, None, "8", "", "start@G20", "", ""),
    ("W-qinghe", "river", None, "15", "", "", "", "M-l86-river-qinghe"),
    ("S-jinshui", None, "pt:116.28477 40.00083", "", "none", "", "", ""),
    ("S-wukong-ym", None, "pt:116.30176 40.01056", "", "none", "", "", ""),
    ("S-yikong-out", None, "pt:116.30150 40.01250", "", "none", "", "", ""),
    ("S-qikong", None, "pt:116.31171 40.01156", "", "none", "", "", ""),
    ("S-ccy-wukong", None, None, "", "w=12", "", "", ""),
    ("S-erlong", None, None, "", "w=10", "", "", ""),
    ("S-qinglong", None, None, "", "none", "", "", ""),
    ("B-hongqiao", None, None, "", "w=16", "", "", "X-hongqiao"),
    ("B-qinglong", None, None, "", "w=18", "", "", ""),
    ("B-xiuyi", None, None, "", "w=20;d=7", "", "", ""),
    ("B-haidian", None, None, "", "w=14", "", "", ""),
    ("X-xiaojiahe-qiao", None, None, "", "w=14", "", "", ""),
    ("X-dashiqiao", None, None, "", "w=14", "", "", ""),
    ("X-anheqiao", None, None, "", "w=14", "", "", ""),
    # --- roads
    ("R-eastwest", None, None, "8", "", "", "", ""),
    ("R-shanmian", None, None, "10", "", "start@R-eastwest;end@YMC-001", "", ""),
    ("R-shidao", None, None, "10", "", "end@R-eastwest", "", "M-tdm-road-haitien-pekin;M-l86-road-ymy-haidian"),
    ("R-qinglong", None, None, "8", "", "", "", "M-tdm-road-haitien-west"),
    ("R-westwall", None, None, "5", "", "", "", ""),
    ("T-suzhoujie", None, None, "6", "", "", "", ""),
    # --- offices, storehouses, the drill ground
    ("C-hq", None, None, "", "compound=60x50;halls=1;kit=1", "", "", ""),
    ("O-dong-gongsuo", None, "pt:116.27990 40.00275", "", "compound=50x40;halls=1;kit=1", "", "", ""),
    ("O-fengyicang", None, None, "", "compound=80x60;halls=4", "", "", ""),
    ("O-S01-huangmuchang", "storehouse", "row:Z-QN06", "", "", "", "", ""),
    ("O-S01-chuanwu", "storehouse", "row:Z-QN03", "", "", "", "", ""),
    ("O-S01-jiamu", "storehouse", "row:Z-QN05", "", "", "", "", ""),
    ("O-S01-qifang", "office", "row:Z-QN07", "", "", "", "", ""),
    ("C-xichang", None, "pt:116.28655 39.99100 r=150", "", "none", "", "", "G-xichang;M-ams-kiaochang"),
    ("C-yuewulou", None, None, "", "parts=116.28660 39.99300 26.8x26.8x1.8|116.28660 39.99300 15x15x9", "", "", ""),
    # --- temples
    ("G-enyou", None, None, "", "compound=40x60;halls=2", "", "", ""),
    ("G-enmu", None, "pt:116.29836 39.99140", "", "compound=40x60;halls=2", "", "", ""),
    ("G-huoshen", None, None, "", "compound=25x35;halls=1", "", "", ""),
    ("G-shenghua", None, None, "", "compound=60x90;halls=3", "", "", ""),
    ("T-niangniangmiao", None, None, "", "compound=35x50;halls=2", "", "", "M-ams-niangniangmiao"),
    ("T-yanfu", None, None, "", "compound=35x50;halls=2", "", "", ""),
    ("T-gongdesi", None, None, "", "compound=80x120;halls=4", "", "", ""),
    ("T-huangzhuang", None, None, "", "compound=35x50;halls=2", "", "", ""),
    ("T-baofusi", None, "pt:116.32426 39.98122", "", "compound=40x60;halls=3", "", "", "M-ams-paofusi"),
    ("T-dashiqiao-guandi", None, "pt:116.31800 40.01060", "", "compound=25x35;halls=1", "", "", ""),
    ("T-erhezha-guandi", None, "pt:116.30660 40.01470", "", "compound=25x35;halls=1", "", "", ""),
    ("T-shucun", None, "pt:116.29620 40.02200", "", "compound=30x40;halls=2", "", "", ""),
    ("T-anheqiao", None, "pt:116.26610 40.00580", "", "compound=30x40;halls=2", "", "", ""),
    ("T-dayouzhuang", None, "pt:116.27540 40.00260", "", "compound=30x40;halls=2", "", "", ""),
    ("T-chengfu", None, "pt:116.30850 39.99430", "", "compound=30x40;halls=2", "", "", ""),
    ("T-dongliu", None, "pt:116.32920 40.00460", "", "compound=30x40;halls=2", "", "", ""),
    ("T-huajiatun", None, "pt:116.29250 39.99490", "", "compound=30x40;halls=2", "", "", ""),
    ("M-ams-laoyemiao", None, None, "", "compound=25x35;halls=1", "", "", ""),
    ("M-ams-sanguanmiao", None, None, "", "compound=25x35;halls=1", "", "", ""),
    ("M-ams-jinshansi", None, None, "", "compound=30x40;halls=2", "", "", ""),
    # --- fields
    ("M-ams-paddy-xiyuan", "paddy", None, "", "", "", "FD0901", "W-paddy;M-tdm-rizieres"),
    ("F-wanquan-paddy", "paddy", "pt:116.28700 39.97500 r=260", "", "", "", "FD0902", ""),
    ("F-east-paddy", "paddy", "pt:116.31900 40.01400 r=220", "", "", "", "FD0903", ""),
    ("F-gongde-paddy", "paddy", "pt:116.25600 40.00000 r=260", "", "", "", "FD0904", ""),
    # --- the town and the villages
    ("T-haidian", "town", None, "", "houses=450", "", "", "V-haidian;M-ams-haidian;M-tdm-haitien;M-l86-haidian-block"),
    ("V-guajiatun", None, None, "", "houses=40", "", "", "M-ams-guajiatun"),
    ("V-chengfu", None, None, "", "houses=40", "", "", "M-ams-chengfu"),
    ("V-shuimo", None, None, "", "houses=30", "", "", ""),
    ("V-shucun", None, None, "", "houses=40", "", "", ""),
    ("V-xiaojiahe", None, None, "", "houses=30", "", "", ""),
    ("V-dayouzhuang", None, None, "", "houses=40", "", "", ""),
    ("V-qinglongqiao", None, None, "", "houses=35", "", "", "M-l86-qinglongqiao;M-tdm-village-w"),
    ("V-saoziying", None, None, "", "houses=25", "", "", ""),
    ("V-erhezha", None, None, "", "houses=20", "", "", ""),
    ("V-zhuofang", None, None, "", "houses=25", "", "", ""),
    ("V-dongliu", None, None, "", "houses=25", "", "", ""),
    ("V-baogou", None, None, "", "houses=30", "", "", "M-ams-bagou"),
    ("V-huangzhuang", None, None, "", "houses=30", "", "", ""),
    ("V-liulangzhuang", None, None, "", "houses=40", "", "", "M-ams-liulangzhuang;M-l86-liulangzhuang"),
    ("M-ams-beiwu", None, None, "", "houses=25", "", "", "M-l86-beiwu"),
    ("M-ams-chapeng", None, None, "", "houses=15", "", "", ""),
    ("M-ams-howyao", None, None, "", "houses=15", "", "", ""),
    ("M-ams-zhongwu", None, None, "", "houses=15", "", "", ""),
    ("M-ams-hulishan", None, None, "", "houses=15", "", "", ""),
    ("M-ams-santsaitang", None, None, "", "houses=15", "", "", ""),
    ("M-ams-paitaan", None, None, "", "houses=15", "", "", ""),
    ("M-ams-kiutienkwan", None, None, "", "houses=15", "", "", ""),
    ("M-ams-wangkochwang", None, None, "", "houses=15", "", "", ""),
    ("M-ams-tungpaita", None, None, "", "houses=15", "", "", ""),
    ("M-ams-pehyenchwang", None, None, "", "houses=15", "", "", ""),
    ("M-l86-malianwa", None, None, "", "houses=20", "", "", ""),
    ("M-l86-hucheng", None, None, "", "houses=15", "", "", ""),
    # --- the banner camps (rows from the count of rooms: 1,550 间 a banner after 1747, ten to a double row-house)
    ("C-zhengbai", None, None, "", "rows=14;per_row=11", "", "", ""),
    ("C-xianghuang", None, None, "", "rows=14;per_row=11", "", "", ""),
    ("C-zhenghuang", None, None, "", "rows=14;per_row=11", "", "", ""),
    ("C-zhenghong", None, None, "", "rows=14;per_row=11", "", "", ""),
    ("C-xianghong", None, None, "", "rows=14;per_row=11", "", "", ""),
    ("C-xiangbai-da", None, None, "", "rows=14;per_row=11", "", "", ""),
    ("C-xiangbai-xiao", None, None, "", "rows=6;per_row=5", "", "", ""),
    ("C-zhenglan", None, None, "", "rows=14;per_row=11", "", "", ""),
    ("C-baoyi", None, None, "", "rows=8;per_row=7", "", "", "M-ams-sanqi"),
    ("C-shiwei", None, None, "", "rows=5;per_row=4", "", "", ""),
    ("C-huoqi", None, None, "", "none", "", "", ""),
    # --- the hills on the horizon (positions from the DEM: the highest cell of each massif, S04)
    ("NEW-xishan", "hill_far", "dem", "", "label=1", "", "", ""),
    ("NEW-wanshoushan", "hill_far", "pt:116.26916 39.99834", "", "label=1", "", "", ""),
    # --- October 1860, in the layer and the panel only
    ("E-1860-french-route", "other", None, "", "none", "", "", ""),
    ("E-1860-cavalry-route", "other", None, "", "none", "", "", ""),
    ("E-1860-french-camp", "other", None, "", "none", "", "", ""),
]

NEW = {
    "NEW-weiming": dict(kind="lake", name_zh="未名湖", name_pinyin="Weiming Hu", name_en="the lake of 淑春园 (today's 未名湖)", sources="S03", confidence="B", assumed="false", state_1860="in 淑春园, held by 睿亲王 仁寿 (see 淑春园)",
                        size="", position_basis="today's lake, osm relation 21716245 (outer ring); its shape in 1860 is C", note="The lake of 淑春园; today's 未名湖 of Peking University. Whether its outline is that of 1860 is not known (C)."),
    "NEW-xishan": dict(kind="hill_far", name_zh="西山", name_pinyin="Xi Shan", name_en="the Western Hills", sources="S04;S02", confidence="B", assumed="false", state_1860="the hills the gardens' views borrowed",
                       size="", position_basis="the highest cell of the GLO-30 DEM west of 116.22 E between 39.95 and 40.05 N (run)", note="The ridge on the western horizon, with 香山 and its garden 静宜园 (burned 18-19 October 1860, S02 pp.188-189). Drawn from today's DEM as a low ridge in the fog."),
    "NEW-wanshoushan": dict(kind="hill_far", name_zh="万寿山", name_pinyin="Wanshou Shan", name_en="Longevity Hill", sources="S03;S04;S02", confidence="B", assumed="false", state_1860="the hill of 清漪园; its buildings burned 18-19 October 1860 (S02 pp.188-189)",
                            size="", position_basis="today's summit, osm node 559277840", note="Named 万寿山 in 1751 (S02). The ground takes its form from today's DEM, which includes the rebuilding of the 1880s and today's trees (research/terrain/ground_outer_report.json)."),
}


def rd(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def link_key(link):
    m = re.search(r"https?://[^\s;,)]+", link or "")
    return m[0].rstrip("/.").lower() if m else None


def main():
    rows, geo, srcs = {}, {}, []
    for t in TOPICS:
        for r in rd(SC / f"palace_r20_surroundings_rows_{t}.csv"):
            r["topic"] = t
            rows[r["key"]] = r
        gp = SC / f"palace_r20_surroundings_geo_{t}.geojson"
        if gp.exists():
            for f in json.load(open(gp, encoding="utf-8"))["features"]:
                geo[f["properties"]["key"]] = f
        for s in rd(SC / f"palace_r20_surroundings_sources_{t}.csv"):
            s["topic"] = t
            srcs.append(s)

    # Sources: an existing id stays; new ones get S1200 on, the same link once.
    smap, new_sources, by_link = {}, [], {}
    n = FIRST_S
    for s in srcs:
        ex = [x for x in re.split(r"[;,\s]+", s["existing_S"]) if re.fullmatch(r"S\d+", x)]
        if ex:
            smap[s["tmp_id"]] = ex[0] if len(ex) == 1 else ";".join(ex)
            continue
        k = link_key(s["link"])
        if k and k in by_link:
            smap[s["tmp_id"]] = by_link[k]
            continue
        sid = f"S{n}"
        n += 1
        smap[s["tmp_id"]] = sid
        if k:
            by_link[k] = sid
        new_sources.append((sid, s))

    def map_sources(text):
        out = []
        for x in re.split(r"[;,\s]+", text or ""):
            if not x:
                continue
            y = smap.get(x, x)
            for z in y.split(";"):
                if z not in out:
                    out.append(z)
        return ";".join(out)

    # The ring's lakes: today's water inside today's 颐和园 boundary (团城湖 left out: Q264), and 未名湖.
    osm = {f["properties"]["id"]: f for f in json.load(open(ROOT / "research/layers/osm_ring_today.geojson", encoding="utf-8"))["features"]}
    park = shape(osm["osm-way-29228773"]["geometry"])
    park = Polygon(park.coords) if park.geom_type == "LineString" else park
    waters = []
    for f in osm.values():
        p = f["properties"]
        if p.get("natural") != "water" or p["id"] == "osm-relation-68324":
            continue
        g = shape(f["geometry"])
        if g.geom_type == "LineString" and g.is_ring:
            g = Polygon(g.coords)
        elif g.geom_type == "MultiLineString":
            g = unary_union(list(polygonize(g)))
        elif g.geom_type != "Polygon":
            continue
        if g.intersects(park):
            waters.append(g.intersection(park.buffer(0.0003)))
    kun = unary_union(waters).buffer(0.00002).buffer(-0.00002).simplify(0.00003)
    kun = max(getattr(kun, "geoms", [kun]), key=lambda p: p.area) if kun.geom_type == "MultiPolygon" else kun
    rel = json.load(open(ROOT / "research/raw/osm/overpass_ring.json", encoding="utf-8"))
    wm = next(e for e in rel["elements"] if e["type"] == "relation" and e["id"] == 21716245)
    outer = [LineString([(q["lon"], q["lat"]) for q in m["geometry"]]) for m in wm["members"] if m.get("role") == "outer" and m.get("geometry")]
    weiming = unary_union(list(polygonize(unary_union(outer))))
    geo["G-kunming"] = {"type": "Feature", "properties": {"key": "G-kunming", "basis": "today's water inside today's 颐和园 boundary (osm way 29228773), 团城湖 left out"}, "geometry": mapping(kun)}
    geo["NEW-weiming"] = {"type": "Feature", "properties": {"key": "NEW-weiming", "basis": "osm relation 21716245, outer ring"}, "geometry": mapping(weiming)}

    # The Western Hills' label: the DEM's highest cell west of 116.22.
    import tifffile
    t40 = tifffile.imread(ROOT / "research/raw/dem/Copernicus_DSM_COG_10_N40_00_E116_00_DEM.tif")
    t39 = tifffile.imread(ROOT / "research/raw/dem/Copernicus_DSM_COG_10_N39_00_E116_00_DEM.tif")
    full = np.vstack([t40, t39])
    i0, i1 = int((41 - 40.05) * 3600), int((41 - 39.95) * 3600)
    j0, j1 = int((116.05 - 116) * 3600), int((116.22 - 116) * 3600)
    sub = full[i0:i1, j0:j1]
    ii, jj = np.unravel_index(int(np.argmax(sub)), sub.shape)
    xs_lat, xs_lon = 41 - (i0 + ii + 0.5) / 3600, 116 + (j0 + jj + 0.5) / 3600
    NEW["NEW-xishan"]["position_basis"] += f": {xs_lat:.5f} N, {xs_lon:.5f} E, {float(sub[ii, jj]):.0f} m"

    key_id = {p[0]: f"OW{k:03d}" for k, p in enumerate(PICK, 1)}
    tmp_re = re.compile(r"\b(?:gardens|water|camps|maps)-\d+\b")

    def map_text(text):
        """The readers' temporary source keys inside a text become S-ids."""
        return tmp_re.sub(lambda m: smap.get(m[0], m[0]).split(";")[0], text or "")
    out, outgeo = [], []
    for k, (key, kind, gover, width, massing, joins, layer_id, also) in enumerate(PICK, 1):
        oid = f"OW{k:03d}"
        r = dict(NEW[key]) if key in NEW else dict(rows[key])
        if key in NEW:
            r.update(key=key, geom="", lon="", lat="")
        others = [rows[a] for a in filter(None, also.split(";")) if a in rows]
        src = map_sources(";".join([r["sources"]] + [o["sources"] for o in others]))
        note = r["note"]
        for o in others:
            bit = f"{o['position_basis'] or 'cross-check'}" + (f" ({o['name_en'] or o['name_zh']})" if (o["name_en"] or o["name_zh"]) else "")
            if o["lon"] and r.get("lon"):
                try:
                    d = math.dist(to_xz(float(o["lon"]), float(o["lat"])), to_xz(float(r["lon"]), float(r["lat"])))
                    bit += f", {d:.0f} m from the point used"
                except ValueError:
                    pass
            note += f" Also: {bit}."
        if gover == "dem":
            geom = f"pt:{xs_lon:.5f} {xs_lat:.5f}"
        elif gover:
            geom = gover
        elif r["geom"].startswith("see geo") or key in ("G-kunming", "NEW-weiming"):
            geom = "geo"
        elif r["geom"].startswith("osm way"):
            geom = "osm:way/" + r["geom"].split()[2]
        elif r["geom"].startswith("osm relation"):
            geom = "osm:relation/" + r["geom"].split()[2]
        elif r["lon"] and r["lat"]:
            geom = f"pt:{float(r['lon']):.5f} {float(r['lat']):.5f}"
            kk = kind or r["kind"]
            if kk in ("village", "neighbour_garden", "town"):
                geom += f" r={ {'village': 80, 'town': 300, 'neighbour_garden': 120}[kk] }"
        else:
            raise SystemExit(f"{key}: no position")
        if geom == "geo":
            g = geo[key]
            outgeo.append({"type": "Feature", "properties": {"id": oid, "basis": g["properties"].get("basis", "")}, "geometry": g["geometry"]})
        if geom.startswith("osm:") and ("osm-" + geom[4:].replace("/", "-")) not in osm:
            raise SystemExit(f"{key}: {geom} not in osm_ring_today")
        assumed = r["assumed"].strip().lower() == "true"
        basis = r["position_basis"] or ""
        # A position from a surviving place name stands for today's village, not the place of 1860: C. A map read with a fit, a surviving structure, a plan row: B.
        pos_c = "C" if assumed or "place name" in basis or re.search(r"(^C\b|, C\b|\(C\)|C:)", basis) else "B"
        conf = r["confidence"]
        if r.get("topic") == "maps" and (kind or r["kind"]) in ("village", "temple"):
            conf, pos_c = "C", "C"  # known from the maps of about 1886 and 1944 only: there in 1860 is inferred
            r["note"] = (r["note"] + " On the maps of 1886 or 1944 only: that it stood in 1860 is inferred (C).").strip()
        if geom.startswith("row:"):
            pos_c = "B"
        out.append({"id": oid, "kind": kind or r["kind"], "name_zh": r["name_zh"], "name_pinyin": r["name_pinyin"], "name_en": r["name_en"], "geom": geom, "width_m": width, "size": map_text(r["size"]), "state_1860": map_text(r["state_1860"]),
                    "sources": src, "confidence": conf, "pos_confidence": pos_c, "assumed": "true" if assumed else "false", "position_basis": map_text(r["position_basis"]), "joins": ";".join(f"{e}@{key_id.get(t, t)}" for e, t in (j.split("@") for j in joins.split(";") if j)), "massing": massing, "layer_id": layer_id,
                    "reader": f"{r.get('topic', 'coordinator')}:{key}" + "".join(f";{o['topic']}:{o['key']}" for o in others), "note": map_text(note.strip())})

    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "features.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    (OUT / "geometry.geojson").write_text(json.dumps({"type": "FeatureCollection", "note": "hand-edited from Round 20: the lines and outlines features.csv names as geo (WGS84)", "features": outgeo}, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
    used = {x for o in out for x in o["sources"].split(";")}
    table = []
    for sid, s in new_sources:
        if sid not in used:
            continue
        link = s["link"].replace("|", "/")
        note = re.sub(r"\s*;?\s*local (?:scratch|/opt)[^;|]*", "", s["note"]).replace("|", "/").strip()
        status = s["status"] if s["status"] in ("found", "viewed", "downloaded", "to-request", "blocked") else "viewed"
        table.append(f"| {sid} | {s['title'].replace('|', '/')} | {s['year']} | {s['reuse'].replace('|', '/')} | {status} | {re.sub(r' ; local .*', '', link)}{'. ' + note if note else ''} |")
    (SC / "palace_r20_surroundings_sources_table.md").write_text("\n".join(table) + "\n", encoding="utf-8")
    (SC / "palace_r20_surroundings_source_map.json").write_text(json.dumps(smap, ensure_ascii=False, indent=0), encoding="utf-8")
    print(f"{len(out)} rows, {len(outgeo)} geometries; {len(table)} new sources (S{FIRST_S}-S{n - 1} assigned, {len(table)} used); Western Hills top {xs_lat:.5f} {xs_lon:.5f} {float(sub[ii, jj]):.0f} m")
    left = sorted(set(rows) - {p[0] for p in PICK} - {a for p in PICK for a in p[7].split(";")})
    print("not taken:", left)


if __name__ == "__main__":
    main()
