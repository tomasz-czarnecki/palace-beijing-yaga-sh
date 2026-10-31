"""palace_r5: merges the workers' jsonl into the repo's catalogues. Rerunnable: it starts from the catalogues at 5fbd637 and keeps ids in palace_r5_idmap.json.

  python r5_merge.py        (from the scratch scripts folder; `git show` is read-only)

Writes research/twins/catalog.csv, research/reconstructions/catalog.csv and images, research/raw/reconstructions, research/photos/catalog.csv and images, research/evidence/catalog.csv, research/evidence/facts.csv, research/sources.md. After this round the catalogues are edited by hand; this script is kept as the record of how they were made.
"""

import csv, glob, hashlib, io, json, os, re, shutil, subprocess, sys
from pathlib import Path
from PIL import Image

S = Path("/opt/data/cache/scratch")
R = Path("/opt/data/workspace/000_Dev/palace-beijing-yaga-sh")
BASE = "5fbd637"
IDMAP = S / "palace_r5_idmap.json"
csv.field_size_limit(10**8)


def git_csv(path):
    text = subprocess.run(["git", "show", f"{BASE}:{path}"], cwd=R, capture_output=True, check=True).stdout.decode("utf-8")
    rd = csv.DictReader(io.StringIO(text, newline=""))
    return rd.fieldnames, list(rd)


def load():
    rows = []
    for f in sorted(glob.glob(str(S / "palace_r5_out_*.jsonl"))):
        topic = f.split("palace_r5_out_")[1][:-6]
        for line in open(f, encoding="utf-8"):
            if line.strip():
                d = json.loads(line)
                d["_t"] = topic
                rows.append(d)
    return rows


idmap = json.load(open(IDMAP)) if IDMAP.exists() else {"P": {}, "R": {}, "T": {}}


def new_id(kind, key, start):
    table = idmap[kind]
    if key not in table:
        used = [int(v[1:]) for v in table.values()]
        n = max(used, default=start) + 1
        table[key] = f"{kind}{n:04d}" if kind != "T" else f"T{n:03d}"
    return table[key]


def web_copy(src, dst, max_px=1600, max_bytes=300_000):
    dst.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(src).convert("RGB")
    im.thumbnail((max_px, max_px), Image.LANCZOS)
    for q in (82, 74, 66, 58, 50):
        im.save(dst, "JPEG", quality=q, optimize=True, progressive=True)
        if dst.stat().st_size <= max_bytes:
            break
    return im.size


def write_csv(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as h:
        w = csv.DictWriter(h, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


rows = load()
buildings = {r["id"] for r in csv.DictReader(open(R / "research/buildings.csv", encoding="utf-8", newline=""))}
GARDEN_OK = {"YM", "CC", "XY", "QC", "ALL"}
CLASSES = {"grand_hall", "main_hall", "side_hall", "small_house", "gallery", "pavilion_square", "pavilion_polygon", "gate_hall", "temple_hall", "storeyed_hall", "tower"}


GRADE = {"sure": 0, "likely": 1, "guess": 2}


def clean_title(text):
    """A Commons file name is not a title."""
    text = re.sub(r"^File:", "", text or "")
    text = re.sub(r"\.(jpe?g|png|tiff?|webm)$", "", text.strip(), flags=re.I)
    return re.sub(r"\s*-\s*panoramio$", "", text).strip()


def clean_date(text):
    return re.sub(r"(\d{4}-\d{2}-\d{2}) \d{2}:\d{2}:\d{2}", r"\1", text or "")


def clean_summary(text):
    text = re.sub(r"^Link card to (a |an |the )?", lambda m: "", text or "")
    text = re.sub(r";? ?the page itself was not reachable today\.?", ".", text)
    return text[:1].upper() + text[1:] if text else text


def clean_shows(text):
    out = []
    for it in (text or "").split(";"):
        it = it.strip()
        if not it:
            continue
        b = it.split(":")
        if b[0] == "GARDEN":
            assert b[1] in GARDEN_OK and b[2] in ("sure", "likely", "guess"), it
        elif b[0] == "CLASS":
            assert b[1] in CLASSES, it
        else:
            assert b[0] in buildings and b[1] in ("sure", "likely", "guess"), it
        if it not in out:
            out.append(it)
    # one tie per object: the firmest
    best = {}
    for it in out:
        key, conf = it.rsplit(":", 1)
        if key not in best or GRADE[conf] < GRADE[best[key]]:
            best[key] = conf
    return ";".join(f"{k}:{v}" for k, v in best.items())


# ---------- twins ----------
DROP_TWINS = {("GARDEN:XY", "大三巴牌坊")}  # the worker's own pairing, no source, and it says so
TWIN_TEXT = {
    ("YM46", "柳浪闻莺"): {"relation": "comparable", "what_it_tells": "An archway of 1763 near 文源阁 took its name from this West Lake scene (S418): a copy of a scene in the grounds, not of the library. Hangzhou's site is a modern park."},
    ("YM46", "青芝岫"): {"relation": "comparable"},  # a rock from the same quarry, not a building built together
    ("CC04", "小有天 (颐和园 万寿山西麓)"): {"relation": "comparable"},  # S400 offers the link as an inference
    ("YM01", "太和殿"): {"evidence_for_relation": "No source pairs them. Reason: the audience hall of the Forbidden City, against which the plainness of ours can be read (S08, S06 on grey tile and rolled ridges)."},
    ("CLASS:gate_hall", "东宫门 (颐和园)"): {"evidence_for_relation": "Search summary: 东宫门 is the former 大宫门; rebuilt under Guangxu. Bays not seen. Reason: the one standing garden gate hall of the court that could be tied to a source."},
}


def norm(s):
    return re.sub(r"\(.*?\)|（.*?）|[\s·/,、;]", "", s or "")


twins = []
for r in rows:
    if r["type"] != "twin" or (r["object_id"], r["twin_name_zh"]) in DROP_TWINS:
        continue
    r = {**r, **TWIN_TEXT.get((r["object_id"], r["twin_name_zh"]), {})}
    dup = next((t for t in twins if t["object_id"] == r["object_id"] and norm(t["twin_name_zh"]) == norm(r["twin_name_zh"])), None)
    if dup:
        if dup["_t"] == "commons" and r["_t"] != "commons":  # the sourced row wins
            twins[twins.index(dup)] = r
        continue
    twins.append(r)


def twin_match(obj, name):
    n = norm(name)
    for t in twins:
        if t["object_id"] != obj:
            continue
        m = norm(t["twin_name_zh"])
        if m == n or n in m or m in n or m[:3] == n[:3]:
            return t
    return None


# twin pictures whose pairing no worker wrote: a comparable, C, with the reason
pictures = [r for r in rows if r["type"] == "picture"]
for p in pictures:
    if not p.get("relation", "").startswith("twin:"):
        continue
    name = p["relation"][5:]
    for it in p["shows"].split(";"):
        obj = ":".join(it.split(":")[:-1])
        if not twin_match(obj, name):
            twins.append({"type": "twin", "object_id": obj, "twin_name_zh": name, "twin_name_en": "", "twin_place": "", "relation": "comparable", "evidence_for_relation": f"No source pairs them; chosen for form only. {p['why']}", "still_standing": "yes", "confidence": "C", "what_it_tells": "form only", "notes": "Added at the merge: a picture was tied to this object with no pairing row.", "link": p["source_url"], "status": "viewed", "_t": "merge"})

link_by_twin = {}
for p in pictures:
    if p.get("relation", "").startswith("twin:"):
        for it in p["shows"].split(";"):
            t = twin_match(":".join(it.split(":")[:-1]), p["relation"][5:])
            if t:
                link_by_twin.setdefault(id(t), p["source_url"])
                t.setdefault("_photos", []).append(p)

source_reuse = {}
for line in (R / "research/sources.md").read_text(encoding="utf-8").splitlines():
    m = re.match(r"\| (S\d+) \| (.*)", line)
    if m:
        cols = [c.strip() for c in m[2].rstrip(" |").split(" | ")]
        source_reuse[m[1]] = cols[2] if len(cols) > 2 else ""
for r in rows:
    if r["type"] == "source":
        source_reuse[r["id"]] = r["reuse"]

KANRIPO = "https://github.com/kanripo/KR2k0036/blob/master/KR2k0036_0{}.txt"
RANK = {"YM": 0, "CC": 1, "XY": 2, "QC": 3, "GA": 4, "CL": 5}
twins.sort(key=lambda t: (RANK.get(t["object_id"][:2], 9), t["object_id"], t["twin_name_zh"]))
out_twins = []
for t in twins:
    ev = t.get("evidence_for_relation") or ""
    if not ev:
        ev = "No source pairs them; chosen for form only, as a building of the same court, decades or type."
    link = t.get("link") or link_by_twin.get(id(t), "")
    if not link:
        m = re.search(r"S05 j\.?(\d+)", ev)
        link = KANRIPO.format(m[1]) if m else ""
    if not link:
        print("TWIN WITHOUT LINK, dropped:", t["object_id"], t["twin_name_zh"])
        continue
    first = re.search(r"\bS\d+\b", ev)
    if first and first[0] == "S05":
        lic = "Qing text, public domain; our summary"
    elif first and source_reuse.get(first[0]):
        lic = source_reuse[first[0]][:120]
    elif "commons.wikimedia" in link:
        lic = "the pairing is ours; the linked picture as its file page states"
    else:
        lic = "facts only; our summary"
    tid = new_id("T", f"{t['object_id']}|{norm(t['twin_name_zh'])}", 0)
    t["_id"] = tid
    out_twins.append({"twin_id": tid, "object_id": t["object_id"], "twin_name_zh": t["twin_name_zh"], "twin_name_en": t.get("twin_name_en", ""), "twin_place": t.get("twin_place", ""), "relation": t["relation"], "evidence_for_relation": ev, "still_standing": t["still_standing"], "confidence": t["confidence"], "what_it_tells": t.get("what_it_tells", ""), "notes": t.get("notes", ""), "link": link, "licence": lic, "status": t.get("status", "viewed")})
out_twins.sort(key=lambda t: t["twin_id"])
write_csv(R / "research/twins/catalog.csv", "twin_id,object_id,twin_name_zh,twin_name_en,twin_place,relation,evidence_for_relation,still_standing,confidence,what_it_tells,notes,link,licence,status".split(","), out_twins)

# ---------- photos ----------
fields, photo_rows = git_csv("research/photos/catalog.csv")
fields = fields + ["relation"] if "relation" not in fields else fields
by_pid = {p["photo_id"]: p for p in photo_rows}
for p in photo_rows:
    p["relation"] = "self"

# corrections from the sweep of the old collections
for n in range(201, 210):
    p = by_pid[f"P{n:04d}"]
    if p["kind"] == "photo":
        p["kind"] = "print"
    p["notes"] = (p["notes"] + " A photograph of a painted Forty Scenes leaf, not a view of the site (Round 5).").strip()
by_pid["P0164"]["shows"] = re.sub(r"YM37:\w+", "YM37:guess", by_pid["P0164"]["shows"])
by_pid["P0164"]["notes"] = (by_pid["P0164"]["notes"] + " G. E. Morrison's album heads the same print WAN-SHOU-SHAN in English and 圓明園 in Chinese, so the tie is a guess until the bridge is placed (S461, Round 5).").strip()
if not by_pid["P0315"]["shows"]:
    by_pid["P0315"]["shows"] = "XY12-01:guess;XY13:guess"
by_pid["P0191"]["shows"] = by_pid["P0191"]["shows"].replace("XY01:likely", "XY01:sure")
by_pid["P0191"]["notes"] = (by_pid["P0191"]["notes"] + " The holder's page title now names 谐奇趣 (S464, Round 5).").strip()
by_pid["P0174"]["notes"] = (by_pid["P0174"]["notes"] + " Leaf of Favier, Péking, c. 1897, facing p. 270 (S460, Round 5).").strip()

grouped = {}
for p in pictures:
    key = (p["source_url"], p["title"])
    if key in grouped and p.get("relation", "").startswith("twin:"):
        g = grouped[key]
        g["shows"] = ";".join(dict.fromkeys((g["shows"] + ";" + p["shows"]).split(";")))
        g.setdefault("_names", [g["relation"][5:]]).append(p["relation"][5:])
        continue
    if key in grouped and p["_t"] == "oldphotos2":  # the second pass read it better: the plate of Favier
        p = {**grouped[key], **{k: v for k, v in p.items() if v not in ("", None)}}
    grouped[key] = p
pictures_all = pictures
pictures = list(grouped.values())

NOT_ADDED = re.compile(r"^(RUINES DU PALAIS|GRAND PONT|TOUR VERNISS|Gezicht op de ru|Sirén|Ruins of Xieqiqu|Yuen Ming Yuen, Pechili|View of the Lake|Print of Afong|Bronze Temple)")
known_urls = {p["source_url"] for p in photo_rows}
added = set()
new_photos = 0
images = R / "research/photos/images"
raw_photos = R / "research/raw/photos"
for p in pictures:
    if NOT_ADDED.search(p["title"]) or p["source_url"] in known_urls:
        continue
    if not p.get("file") and p.get("relation", "") == "self" and not p.get("shows"):
        continue
    pid = new_id("P", f"{p['source_url']}|{p['title']}", 547)
    row = {k: p.get(k, "") for k in fields}
    row["photo_id"], row["crop"] = pid, ""
    row["date_from"], row["date_to"] = str(p.get("date_from") or ""), str(p.get("date_to") or "")
    row["shows"] = clean_shows(p["shows"]) if not p.get("relation", "").startswith("twin:") else p["shows"]
    row["title"], row["date"] = clean_title(row["title"]), clean_date(row["date"])
    if p.get("relation", "").startswith("twin:"):
        ts = []
        for it in p["shows"].split(";"):
            for name in p.get("_names", [p["relation"][5:]]):
                t = twin_match(":".join(it.split(":")[:-1]), name)
                if t and t.get("_id") and t["_id"] not in ts:
                    ts.append(t["_id"])
        row["relation"] = "twin:" + ";".join(ts)
    else:
        row["relation"] = "self"
    if p.get("file"):
        dst = (images if p["rights_class"] == "free" else raw_photos) / f"{pid}.jpg"
        w, h = web_copy(p["file"], dst)
        row["file"], row["width"], row["height"] = str(dst.relative_to(R)), w, h
    if p["rights_class"] == "free" and not row["attribution"]:
        row["attribution"] = row["creator"] or row["archive"]
    photo_rows.append(row)
    new_photos += 1
write_csv(R / "research/photos/catalog.csv", fields, photo_rows)

# ---------- reconstructions ----------
e_fields, e_rows = git_csv("research/evidence/catalog.csv")
old_recon = [e for e in e_rows if e["kind"] == "reconstruction"]
write_csv(R / "research/evidence/catalog.csv", e_fields, [e for e in e_rows if e["kind"] != "reconstruction"])
E_META = {  # author, institution, year, kind; only what the row's own title or summary states
    "E0364": ("周秋彤", "北京大学考古文博学院; 圆明园管理处 posted it", "2024", "paper figure"),
    "E0365": ("周秋彤", "北京大学考古文博学院; 圆明园管理处 posted it", "2024", "paper figure"),
    "E0555": ("数字圆明园 team", "清华大学; 圆明园管理处", "2010", "3D model"),
    "E0556": ("张恩荫", "", "2017", "paper figure"),
    "E0557": ("郭黛姮 team", "清华大学", "2020", "AR/VR"),
    "E0559": ("", "北京理工大学", "", "AR/VR"),
    "E0560": ("", "清华大学 heritage institute", "", "AR/VR"),
    "E0562": ("郭黛姮, 贺艳 and team", "清华大学; 清城睿现", "", "3D model"),
    "E0563": ("郭黛姮 team", "清华大学", "", "AR/VR"),
    "E0564": ("数字圆明园 team", "", "", "3D model"),
    "E0565": ("", "梦回圆明园, Tsinghua tag", "", "render"),
    "E0690": ("", "", "", "paper figure"),
    "E0936": ("M. Gao, W. Piao, J. Guo", "Re-Yuanmingyuan Company", "2015", "paper figure"),
    "E0984": ("", "圆明园管理处; 北京大学考古文博学院", "2025", "3D model"),
    "E1178": ("", "", "after 2024", "paper figure"),
    "E1459": ("", "梦回圆明园", "2023 rev.", "paper figure"),
}
NO_MERGE = {"E0936", "E0557", "E0365", "E0364", "E0689", "E1177"}  # the worker's rows are figures or parts of it: they stay apart
EXPAND = {"E1177", "E0689"}  # the worker's rows replace this one
recon = [r for r in rows if r["type"] == "reconstruction" and r.get("link")]  # 《远逝的辉煌》 alone has no page to link: it stays S61 and a wish
# a row of the 2015 paper the workers skipped, seen by eye in the PDF
base = next(r for r in recon if r["link"].endswith("II-5-W3/351/2015/"))
recon.append({**base, "title": 'Fig. 4, rehabilitation of "Jian bi" Pavilion 鉴碧亭', "shows": "QC08:sure", "file": "", "notes": base["notes"], "_t": "merge"})

# figures the coordinator pulled from the PDFs and looked at
FIG = S / "palace_r5_images/recon_papers"
FILES = {
    ("isprs-annals.copernicus.org/articles/II-5-W3/75/2015/", "Fig. 13"): "gao2015_xieqiqu_fig13.jpg",
    ("isprs-annals.copernicus.org/articles/II-5-W3/75/2015/", "Fig. 12"): "gao2015_element_fig12.jpg",
    ("isprs-annals.copernicus.org/articles/II-5-W3/75/2015/", "Fig. 14"): "gao2015_xieqiqu_hologram_fig14.jpg",
    ("isprs-annals.copernicus.org/articles/II-5-W3/131/2015/", "Figs 2"): "jindan2015_liuxiangzhu_fig3.jpg",
    ("isprs-archives.copernicus.org/articles/XL-5-W7/43/2015/", "Figs 10"): "bing2015_plants_fig11.jpg",
    ("isprs-annals.copernicus.org/articles/II-5-W3/351/2015/", "Fig. 5"): "xiaoqi2015_gate_fig5.jpg",
    ("isprs-annals.copernicus.org/articles/II-5-W3/351/2015/", "Fig. 4"): "xiaoqi2015_jianbi_fig4.jpg",
    ("isprs-archives.copernicus.org/articles/XL-5-W7/465/2015/", "Fig. 3"): "yanqiu2015_haiyan_fig3.jpg",
    ("isprs-archives.copernicus.org/articles/XLII-2-W5/335/2017/", "Fig. 6"): "he2017_haiyan_fig6.jpg",
    ("isprs-archives.copernicus.org/articles/XLII-2-W5/335/2017/", "Fig. 12"): "he2017_rocks_fig12.jpg",
}
CREDIT = [
    ("II-5-W3/75/2015", "Gao, Piao and Guo 2015, ISPRS Annals II-5/W3, 75, CC BY 3.0"),
    ("II-5-W3/131/2015", "Jindan, Junsong and Jiujun 2015, ISPRS Annals II-5/W3, 131, CC BY 3.0"),
    ("XL-5-W7/43/2015", "Bing, Guxin and Gongli 2015, ISPRS Archives XL-5/W7, 43, CC BY 3.0"),
    ("II-5-W3/351/2015", "Xiaoqi 2015, ISPRS Annals II-5/W3, 351, CC BY 3.0"),
    ("XL-5-W7/465/2015", "Yanqiu, Jinliang and Hai 2015, ISPRS Archives XL-5/W7, 465, CC BY 3.0"),
    ("XLII-2-W5/335/2017", "He, Ma and Zhang 2017, ISPRS Archives XLII-2/W5, 335, CC BY 4.0"),
    ("s40494-024-01213-5", "Li, He, Xiao, Jia and Qin 2024, Heritage Science, doi 10.1186/s40494-024-01213-5, CC BY 4.0"),
    ("rs-1747129", "Zhang, Xi, Huang and Liang 2022, Research Square, doi 10.21203/rs.3.rs-1747129/v1, CC BY 4.0"),
    ("sketchfab.com", None),
    ("Hengdian_Yingshicheng", "Yumeto, CC BY-SA 4.0, via Wikimedia Commons"),
    ("Gartenplan_der_Xiyang_Lou", "Maximilian Dörrbecker (Chumwa), CC BY-SA 2.5, via Wikimedia Commons"),
]

for r in recon:
    for (link, fig), name in FILES.items():
        if link in r["link"] and r["title"].startswith(fig):
            r["file"] = str(FIG / name)
            r["notes"] = re.sub(r"NOT EXTRACTED,? ?(PDF only\.)?( Not opened by eye\.)?", "Pulled from the PDF and opened by eye.", r.get("notes") or "")
    # the replica at Hengdian: a photograph under CC BY-SA on Commons, by the rulebook free; the replica is credited to its builder
    if r["title"].startswith("20240112"):
        r["rights_class"] = "free"
        r["licence"] = "CC BY-SA 4.0 (Commons, the photograph)"
        r["author"] = "Hengdian World Studios (replica); Yumeto (photograph)"
    if r["title"].startswith("Fig. 12, More than 1500"):
        r["shows"] = "YM46:likely;GARDEN:ALL:likely"
        r["notes"] = (r.get("notes") or "") + " The paper's text says the rocks are those of the garden behind 文源阁."

# rows that are not reconstructions of the garden, kept on record, off the panels
ZODIAC = re.compile(r"Head|首铜像|马首|生肖|zodiac|猪首|YPM ANT|诛仙", re.I)
OFF_PANEL = re.compile(r"畅春园")
for r in recon:
    if ZODIAC.search(r["title"]) or OFF_PANEL.search(r["title"]):
        r["notes"] = f"Off the panels, shows was: {r['shows']}. " + (r.get("notes") or "")
        r["shows"] = ""
        r["file"] = ""

# the same work found by two workers: (keep, drop), by title start
SAME = [
    ("《圆明园四十景数字化复原及应用》", "《圆明园四十景数字化复原及应用》"),
    ("“飞跃圆明园四十景”", "飞跃圆明园四十景"),
    ("Re-relic/Yuanmingyuan: an effective", "Re-relic/Yuanmingyuan: an effective"),
    ("Reconstruction of the Old Summer Palace, Beijing", "Reconstruction of the Old Summer Palace, Beijing"),
    ("Figures 1-7, vegetation restoration", "Study on vegetation restoration"),
    ("Replica of the Forty Scenes album", "Replica of 《圆明园四十景图》"),
    ("圆明新园 New Yuanmingyuan", "横店圆明新园, built replica"),
    ("18-minute digital restoration video shown", "18-minute digital restoration video, 正觉寺"),
    ("圆明园毁灭前景观3D复原图", "7:50 3D reconstruction video"),
    ("海晏堂 digital reconstruction, immersive", "海晏堂 immersive exhibition"),
    ("三维立体视频", "Stereo 3D film"),
    ("Exhibition at the Shougang Industrial Park", "Digital 圆明园 display at 首钢园"),
    ("“再现圆明园” 数字导览系统", "再现圆明园, tablet guide"),
]
drop = set()
for keep_t, drop_t in SAME:
    hits = [r for r in recon if r["title"].startswith(keep_t) and id(r) not in drop]
    others = [r for r in recon if r["title"].startswith(drop_t) and (not hits or r is not hits[0])]
    if not hits or not others:
        print("SAME not found:", keep_t, len(hits), len(others))
        continue
    k = hits[0]
    for o in others:
        drop.add(id(o))
        k["shows"] = ";".join(dict.fromkeys(x for x in (k["shows"] + ";" + o["shows"]).split(";") if x))
        k["notes"] = (k.get("notes") or "") + f" Also found at {o['link']}."
        k["method_stated"] = k.get("method_stated") or o.get("method_stated", "")
        k["file"] = k.get("file") or o.get("file", "")
recon = [r for r in recon if id(r) not in drop]
# exact duplicates
seen = {}
uniq = []
for r in recon:
    key = (r["link"], norm(r["title"]))
    if key in seen:
        k = seen[key]
        k["shows"] = ";".join(dict.fromkeys(x for x in (k["shows"] + ";" + r["shows"]).split(";") if x))
        k["file"] = k.get("file") or r.get("file", "")
        continue
    seen[key] = r
    uniq.append(r)
recon = uniq


def caveat(r):
    t, a, n, i = r["title"], r.get("author", ""), r.get("notes", ""), r.get("institution", "")
    k = r["kind"]
    if re.search(r"样式房|雷氏", a + i) or t.startswith("烫样") or "样式雷烫样" in t:
        return "Made for the repair of 1873–74, so later than the state of 1860: a period model, not a modern one."
    if re.search(r"\bAI\b|\bAI[+高]|token|Meshy|AI 大模型", t):
        return "Made with AI tools: not evidence for form."
    if "Hengdian" in t or "横店" in t + i or "珠海" in t + i or "Hengdian" in i:
        return "A built replica away from the site, not on it."
    if "镂月开云" in t and "央美" in t:
        return "As its page warns, seen in a search extract: made without visiting the site, and its rockery, pavilion and terrain depart from the record."
    if "中央美术学院" in i and re.search(r"四十景", t):
        return "Aims at about 1744, not at the state of 1860."
    if re.match(r"《圆明园新证》|《一幅样式雷|《“样式雷”图与圆明园》|从《春和园|三幅样式雷|张恩荫", t):
        return "A reading of Qing plans, not a reconstruction."
    if "中央美术学院" in i and re.search(r"Forty Scenes|四十景", t):
        return "Aims at about 1744, not at the state of 1860."
    if "实测图" in t or "survey map" in t:
        return "A survey of the ruins, not a reconstruction."
    if "Wanfang Anhe" in t and "s40494" in r["link"]:
        return "The surviving rockery as surveyed, not the state of 1860."
    if "in 1933" in t or "1860-1933" in t or "Transfer Map" in t:
        return "A later state, for comparison."
    if k == "3D model" and "sketchfab" in r["link"] and re.search(r"scan|photogramm|ruin|remains|Reality Capture", (n + r.get("method_stated", "")), re.I):
        return "A scan of today's remains, not a reconstruction of 1860."
    if "金勋" in a or "Jin Xun" in a:
        return "A modern reconstruction drawing, not a Qing document."
    if k == "game or community build":
        return "A community build: low weight."
    return ""


out_recon = []
used_e = set()
by_e = {}
for r in recon:
    if r.get("e_id"):
        by_e.setdefault(r["e_id"], []).append(r)


def recon_row(r, e=None):
    key = f"{r.get('link') or e['link']}|{norm(r.get('title') or e['title'])}"
    rid = new_id("R", key, 0)
    out = {"recon_id": rid, "evidence_id": r.get("_eids", ""), "source_id": r.get("source_id", ""), "author": r.get("author", ""), "institution": r.get("institution", ""), "year": r.get("year", ""), "kind": r["kind"], "title": clean_title(r["title"]), "link": r["link"], "licence": r.get("licence") or "none stated", "attribution": "", "rights_class": r["rights_class"], "shows": clean_shows(r.get("shows")), "method_stated": r.get("method_stated", ""), "summary_en": clean_summary(r.get("summary_en", "")), "uploader": r.get("uploader", ""), "caveat": caveat(r), "status": r.get("status", "viewed"), "local_copy": "", "width": "", "height": "", "notes": r.get("notes", "")}
    out["era"] = "period" if out["caveat"].startswith("Made for the repair") else "modern"
    if r["rights_class"] == "free":
        for needle, credit in CREDIT:
            if needle in r["link"]:
                out["attribution"] = credit or f"{r.get('author')}, {r.get('licence')}, via Sketchfab"
        assert out["attribution"], ("free without credit", r["title"])
    if r.get("file"):
        folder = R / ("research/reconstructions/images" if r["rights_class"] == "free" else "research/raw/reconstructions")
        dst = folder / f"{rid}.jpg"
        w, h = web_copy(r["file"], dst)
        out["local_copy"], out["width"], out["height"] = str(dst.relative_to(R)), w, h
    return out


merged_e = {}
for e in old_recon:
    eid = e["evidence_id"]
    workers = by_e.get(eid, [])
    if eid in EXPAND:
        for w in workers:
            w["_eids"] = eid
            w["summary_en"] = e["summary_en"]
        continue
    if eid == "E0364":  # the same study as E0365
        continue
    if len(workers) == 1 and eid not in NO_MERGE:
        w = workers[0]
        w["_eids"] = eid
        w["summary_en"] = e["summary_en"]
        w["source_id"] = w.get("source_id") or e["source_id"]
        if e["status"] == "viewed":
            w["status"] = "viewed"
        continue
    author, inst, year, kind = E_META[eid] if eid in E_META else ("", "", "", "render")
    if eid not in E_META:
        print("E row without meta:", eid, e["title"])
    r = {"_eids": "E0364;E0365" if eid == "E0365" else eid, "source_id": e["source_id"], "author": author, "institution": inst, "year": year, "kind": kind, "title": e["title"], "link": e["link"], "licence": "none stated", "rights_class": "research-only", "shows": e["shows"], "method_stated": "", "summary_en": e["summary_en"], "status": e["status"], "notes": "From the evidence catalogue of Round 3."}
    if eid == "E0936":
        r["licence"] = "CC BY 3.0 on the paper; Figs 2, 4b, 5, 7, 8a, 10 and 11 credited elsewhere; the free figures have their own rows"
    recon.insert(0, r)
for r in recon:
    if r.get("file") and not os.path.exists(r["file"]):
        print("MISSING FILE", r["file"])
        r["file"] = ""
    out_recon.append(recon_row(r))
WIDEN = {"E1178": "YM26:likely;YM30:likely;YM33:likely;YM50:likely;YM51:likely", "VISIT": "YM35:likely;YM45:likely"}
for r in out_recon:
    if r["evidence_id"] == "E1178":
        r["shows"] = ";".join(dict.fromkeys((r["shows"] + ";" + WIDEN["E1178"]).split(";")))
    if "visitbeijing.com.cn" in r["link"] and r["evidence_id"] == "E0564":
        r["shows"] = ";".join(dict.fromkeys((r["shows"] + ";" + WIDEN["VISIT"]).split(";")))
for r in out_recon:
    r["institution"] = r["institution"].replace("(team link from the brief, not confirmed from a page)", "(team link not confirmed)")
out_recon.sort(key=lambda r: r["recon_id"])
assert len({r["recon_id"] for r in out_recon}) == len(out_recon)
R_FIELDS = "recon_id,evidence_id,source_id,author,institution,year,kind,era,title,link,licence,attribution,rights_class,shows,method_stated,summary_en,uploader,caveat,status,local_copy,width,height,notes".split(",")
write_csv(R / "research/reconstructions/catalog.csv", R_FIELDS, out_recon)
wanted = {Path(r["local_copy"]).name for r in out_recon if r["local_copy"]}
for folder in (R / "research/reconstructions/images", R / "research/raw/reconstructions"):
    for f in folder.glob("*.jpg") if folder.exists() else []:
        if f.name not in wanted:
            f.unlink()

# ---------- size leads ----------
f_fields, f_rows = git_csv("research/evidence/facts.csv")
for r in rows:
    if r["type"] != "size_lead" or r["id"] == "XY02" or r["id"].startswith("GARDEN"):  # XY02 is a form lead, no dimension: it stays in that row's notes
        continue
    assert r["id"] in buildings, r["id"]
    f_rows.append({"id": r["id"], "field": "size_lead", "value": r["value"], "source_id": r["source_id"], "locator": r.get("locator", ""), "basis": r.get("basis", ""), "suggest_confidence": "B", "decision": "size_lead", "reason": "Stated in a reconstruction or modern study: a lead for a check, never a size in the row"})
write_csv(R / "research/evidence/facts.csv", f_fields, f_rows)

# ---------- sources ----------
sources = (subprocess.run(["git", "show", f"{BASE}:research/sources.md"], cwd=R, capture_output=True, check=True).stdout.decode("utf-8")).rstrip("\n")
have = set(re.findall(r"^\| (S\d+) \|", sources, re.M))
SECTIONS = [("twins", "Round 5: twins and comparables"), ("commons", "Round 5: Commons"), ("oldphotos", "Round 5: old photograph collections"), ("recon_mhymy", "Round 5: reconstructions, Tsinghua, the park, 贺艳"), ("recon_video", "Round 5: reconstructions, video, 3D models, AR"), ("recon_papers", "Round 5: reconstructions, papers and books"), ("commons2", "Round 5: Commons, second pass"), ("oldphotos2", "Round 5: old photographs, second pass"), ("recon_scenes", "Round 5: reconstructions, scene by scene")]
extra = []
for topic, title in SECTIONS:
    part = [r for r in rows if r["type"] == "source" and r["_t"] == topic and r["id"] not in have]
    if not part:
        continue
    extra += ["", f"## {title}", "", "| ID | Source | Year | Reuse | Status | Link / note |", "|---|---|---|---|---|---|"]
    for r in sorted(part, key=lambda r: int(r["id"][1:])):
        clean = lambda s: (s or "").replace("|", "/").replace("\n", " ").strip()
        extra.append(f"| {r['id']} | {clean(r['text'])} | {clean(r['year'])} | {clean(r['reuse'])} | {clean(r['status'])} | {clean(r['link'])}. {clean(r.get('note'))} |")
        have.add(r["id"])
(R / "research/sources.md").write_text(sources + "\n" + "\n".join(extra) + "\n", encoding="utf-8")

json.dump(idmap, open(IDMAP, "w"), ensure_ascii=False, indent=0)
print(f"twins {len(out_twins)}; photos +{new_photos} = {len(photo_rows)}; reconstructions {len(out_recon)} (free {sum(r['rights_class'] == 'free' for r in out_recon)}, with a copy {sum(bool(r['local_copy']) for r in out_recon)}); evidence {len(e_rows) - len(old_recon)}; facts {len(f_rows)}; new sources {len(have)}")
missing = sorted({s for r in out_recon for s in (r["source_id"] or "").replace(",", ";").split(";") if s.strip() and s.strip() not in have}, key=str)
print("sources cited and not listed:", missing)
print("recon without a link:", [r["recon_id"] for r in out_recon if not r["link"]][:20])
print("caveats:", {c: sum(r["caveat"] == c for r in out_recon) for c in {r["caveat"] for r in out_recon}})
print("off panel:", sum(not r["shows"] for r in out_recon))
