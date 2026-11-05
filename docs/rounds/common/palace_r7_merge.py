"""Round 7 merge: the workers' JSON lines into the repo's sheets and catalogues. A record, kept in docs/rounds/common/palace_r7_merge.py.

Rerunnable: catalogues, sources, questions, wishlist and facts are rebuilt from their HEAD version (git show, read only) plus what the workers found; the sheets in research/scenes/ (except about.json) are rewritten from the workers' rows; about.json only fills fields that are empty, so hand edits stay. Ids are given in a fixed order (worker files sorted, rows in file order), so a rerun gives the same ids.

  .venv/bin/python /opt/data/cache/scratch/palace_r7_scripts/coord_merge.py [topic ...]
"""

import csv
import io
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image

ROOT = Path("/opt/data/workspace/000_Dev/palace-beijing-yaga-sh")
S = Path("/opt/data/cache/scratch")
SC = ROOT / "research/scenes"
TOPICS = ["texts_a", "texts_b", "plans", "digs", "photos", "album", "w2", "w34", "w234photos", "verify_a", "verify_b"]
ABOUT_FIELDS = {"what": "what_en", "scene": "scene_en", "later": "later_en", "interior": "interior_en", "setting": "setting_en", "survives": "survives_en", "recons": "recons_en", "best": "best_en", "gaps": "gaps_en"}
FACT_FIELDS = {"built", "changed", "destroyed", "bays", "roof", "roof_tiles", "storeys", "name_en", "name_zh"}
HALL_COLS = ["id", "scene", "plaque_zh", "pinyin", "en", "bays", "depth", "purlins", "roof", "storeys", "tiles", "faces", "relation", "built", "changed", "source_id", "locator", "basis", "confidence", "status"]
DIM_COLS = ["id", "part", "what", "value_m", "err_m", "method", "confidence", "source_id", "locator", "scale", "basis", "status"]
VIEW_COLS = ["photo_id", "id", "view", "visible_part", "state", "reliability", "note"]
BEST_COLS = ["id", "rank", "ref", "why"]
DIG_COLS = ["id", "year", "by", "what_found", "source_id", "link", "status", "confidence"]
INT_COLS = ["id", "kind", "what", "source_id", "locator", "quote_or_basis", "confidence", "status"]
PART_COLS = ["id", "name_zh", "name_pinyin", "name_en", "what", "basis", "source_id", "confidence", "action"]
SKIP = set()  # (topic, line number) of rows the coordinator rejected, with the reason in REJECT
REJECT = {}
FIX = {}  # (topic, line number) -> {field: value}: the coordinator's corrections, each with its reason in a comment


def head(path):
    return subprocess.run(["git", "-C", str(ROOT), "show", f"HEAD:{path}"], capture_output=True, encoding="utf-8", check=True).stdout


def csv_rows(text):
    r = csv.DictReader(io.StringIO(text))
    return r.fieldnames, list(r)


def write_csv(path, fields, rows):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in fields})


def load(topics):
    out = []
    for t in topics:
        p = S / f"palace_r7_out_{t}.jsonl"
        if not p.exists():
            continue
        for n, line in enumerate(open(p, encoding="utf-8"), 1):
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                print("bad json", t, n)
                continue
            if (t, n) in SKIP:
                continue
            d.update(FIX.get((t, n), {}))
            d["_topic"], d["_n"] = t, n
            out.append(d)
    return out


def s(v):
    return "" if v is None else str(v).strip()

# The coordinator's own text, from viewed catalogue rows only: what the workers left empty on a public page, and the hub's lead.
HAND = {
    "_overview": {
        "lead_en": "圆明园 Yuanmingyuan was not one palace but a great number of compounds, halls, courts and small gardens set round lakes and hills: 212 compounds in our inventory. Every scene and compound outside the European palaces now has a dossier: what it was, the album leaf of 1744 where there is one, how it changed before October 1860, its halls one by one, what survives, and what is known of its size, each figure with how it was got.",
        "how_en": "The ten best-documented scenes have a page of their own; the others are summarised below and open in the 3D view with all their evidence. Most sizes come from the Qing plan and from the Yangshi Lei drawings, a few from excavations. On the plan, the names at 九洲清晏 are those of the Tongzhi repair of 1873, not of 1860.",
        "lead_zh": "圆明园不是一座宫殿，而是环绕湖山布置的殿宇、庭院与园林，我们的清单中共有212组。西洋楼以外的每一景、每一组建筑现在都有一份专题资料：概况，1744年四十景图（如有），1860年10月以前的变化，逐座建筑，现存遗迹，以及已知尺寸和每个数字的得出方法。",
        "how_zh": "资料最丰富的十景另有专页；其余各景列于下方，可在三维视图中查看全部证据。尺寸多来自清代地盘图和样式雷图档，少数来自考古发掘。地盘图上九洲清晏一带的名称属同治十二年（1873年）重修，并非1860年的状况。",
    },
    "YM01": {
        "summary_en": "The garden's audience hall at the head of the south axis, behind the Great Palace Gate and the gate 出入贤良门: a plain seven-bay hall used for audiences, banquets and examinations into the 1850s (E1000; E1023; E1557). Looted with the rest on 6-8 October 1860; troops had been quartered in it and the lodges before it, so these were among the last buildings the British troops burned, on 19 October (E2111; E1028).",
        "summary_zh": "正大光明殿是圆明园南部中轴上的听政正殿，1860年10月6日至8日遭英法联军抢掠；因军队曾驻扎于殿内及其前的值房，这些建筑是英军最后焚毁的一批，时在10月19日（E1000；E2111；E1028）。",
        "survives_en": "The site of the audience hall is open lawn today, with a few stones in rows, and the rocky hill 寿山 Shoushan behind it still stands (P0363); the front lake 前湖 keeps a low stone edge (P0396). A survey report describes three courts from 大宫门 Da Gongmen to 正大光明殿, 370 m from north to south (S102, E1017). The dig at 大宫门, one of the campaigns since 2012, found the gate hall, its east and west wing gates, the 金水桥 bridge and the channel, and the area was to be conserved and shown (E0363, S132, E2120).",
        "survives_zh": "正大光明殿遗址今为草地，残存成行石块，殿后寿山假山尚存（P0363）；前湖保留低矮石岸（P0396）。勘探报告称自大宫门至正大光明殿为三进院落，南北长370米（S102，E1017）。2012年以来的发掘中，大宫门遗址发现门殿、东西配门、金水桥及河道，计划保护展示（E0363，S132，E2120）。",
    },
    "YM29": {
        "survives_en": "The stepped stone platform survives at the lake edge: dressed stone bastions project into the water at different lengths, with broken marble blocks stacked on them (P0383, P0787, P0788). Under the Republic the gardens' ruins were quarried for stone and brick (S02 p.218). No excavation report of this scene was found (S946).",
        "survives_zh": "方壶胜境临水的阶梯状石台基尚存：长短不一的条石台墩伸入水中，上面堆放着残破的汉白玉构件（P0383，P0787，P0788）。民国时期园中遗址曾被拆取石料和砖（S02 p.218）。未见此景的考古发掘报告（S946）。",
    },
    "YM13": {
        "survives_en": "The cross-shaped 卍 platform stands in its pond, restored: its arms are paved terraces with stone edges at one level, with channels between them (P0381). A dig of 2003 found the original stone trough of the 响水 'sounding water' cascade on the west shore, where a Yangshi Lei drawing writes 响水; the cascade was repaired and set running again, smaller than the drawing shows (S944).",
        "survives_zh": "卍字形台基仍立于水中，经过修整：各臂为同一高度、石砌边缘的铺装平台，臂间有水道（P0381）。2003年发掘在西岸发现原有的石砌“响水”水槽，样式雷图上此处注有“响水”；此后水景修复重新放水，规模小于图样所示（S944）。",
    },
    "YM32": {
        "survives_en": "The islands of 蓬岛瑶台 survive in 福海 Fuhai, whose shape is kept (S146, S148). Modern structures stand on them: seen from the shore, a glazed pyramidal pavilion roof and a white-walled hall with a grey roof on a rock base (P0791, P0387). No excavation report of the islands was found (S946).",
        "survives_zh": "蓬岛瑶台诸岛仍在福海之中，福海保持原有轮廓（S146，S148）。岛上今有新建建筑：从岸上可见一座琉璃攒尖亭顶，以及一座建在石基上的白墙灰瓦殿宇（P0791，P0387）。未见诸岛的考古发掘报告（S946）。",
    },
}

# Totals the source itself states, which the worker kept only in its basis: 文源阁's 丈尺册 (S105 note [4]).
HAND_DIMS = [
    {"type": "dim", "id": "YM46-01", "part": "文源阁 library, the whole front", "what": "frontage", "value_m": 22.72, "err_m": 0.05, "method": "a", "confidence": "B", "source_id": "S105", "locator": "note [4] (光绪朝《圆明园慎修思永及文源阁丈尺册》)", "scale": "营造尺 0.32 m", "basis": "total 71 尺 = 22.72 m, as the source sums it: 明间 16 尺, four 次间 of 12.5 尺, the stair bay 5 尺; the 丈尺册 is of the Guangxu reign, so B", "status": "viewed"},
    {"type": "dim", "id": "YM46-01", "part": "文源阁 library, the whole depth", "what": "other:overall_depth", "value_m": 14.72, "err_m": 0.05, "method": "a", "confidence": "B", "source_id": "S105", "locator": "note [4] (光绪朝《圆明园慎修思永及文源阁丈尺册》)", "scale": "营造尺 0.32 m", "basis": "total 46 尺 = 14.72 m: 中进深 24 尺 and two galleries of 11 尺", "status": "viewed"},
]
# The typology check (research/scenes/typology_check.json): where the measured halls disagree with params.json, a proposal for the owner.
HAND_WISHES = [
    {"type": "wish", "what": "Old photographs (1900-1940) of the Chinese scenes outside the Xiyang Lou: 正觉寺, 舍卫城, 文源阁 and 石玲峰, 福海 and its islands, 大宫门, 绮春园宫门, 含经堂, in Sidney Gamble (Duke), Hedda Morrison (Harvard-Yenching) and C. F. Moore (Royal BC Museum)", "replaces": "Round 7 found no new old photograph of any Yuanming Yuan scene outside the Xiyang Lou; every candidate on Commons was catalogued already", "where": "repository.duke.edu/dc/gamble; hollis.harvard.edu; Royal BC Museum MS-3171", "how": "A person in a browser: the three refuse automated access (Q33, Q62); not tried again this round, as the brief asked"},
    {"type": "wish", "what": "A plan-reading pass that ties the album's halls (research/scenes/halls.csv, source S08) and the Yangshi Lei hall names to the plan's 937 unnamed blocks", "replaces": "937 halls that show only the plan and their scene's evidence; Round 7 tied pictures and texts only to rows that already had a name", "where": "S01 crops (research/raw/plancrops, local) with the album leaves and the hall rows", "how": "One plan reader per garden, as in Round 1, reading crops against the leaf"},
]
HAND_QUESTIONS = [
    {"type": "question", "text": "Typology, grand_hall heights: proposal column_m 5.12 -> 4.2 and platform_m 1.22 -> 0.7 for the class, keeping 5.12 and 1.22 for 正大光明殿 alone through by_name. The measured residential and office halls of the class all fall below the default: 慎德堂 YM03-11 column 4.35, platform 0.59 (S310, mhymy 7342); 保合太和殿 YM02-08 column 4.48 (S310, NLC 样002-17); 慎修思永 YM23-01 column 4.0, platform 0.96 (S310, NLC 样027-11-1); 田字殿 YM20-01 eave column 3.68, platform 0.55 (S139, S137). Median column 4.2 m, platform about 0.6-0.7 m. The default came from the audience hall, the one hall of the class built higher. Not applied: every grand_hall box would change"},
    {"type": "question", "text": "Typology, grand_hall bays: proposal bay_m central 5.5 -> 5.17 and side 4.7 -> 4.83 (次间) and 4.32 (梢间), from the yellow slip of NLC 样001-4 正大光明白差准底 as transcribed on mhymy (S310): 明间 一丈六尺一寸五, 次间 一丈五尺一寸, 梢间 一丈三尺五寸, hall 35.95 x 16.0 m with porches, inside Malone's platform of 39.32 x 19.2 m (S02). Not applied"},
    {"type": "question", "text": "Typology, 清音阁 YM44-02: the row's class is storeyed_hall, but its Yangshi Lei figures (S310, mhymy 7297: ridge 23.94 m, middle storey 14.53 m square, platform 0.96 m, bays 5.50 and 4.51 m) are those of the tower class, whose ridge default is the same 23.94 m. Proposal: a by_name entry for 清音阁 with the tower's form and these figures. 养吉斋丛录 gives the stage 'about ten 丈' deep and wide (S202, E2148): 32 m, much more than the drawing, so it may count the whole stage court. Not applied"},
    {"type": "question", "text": "Typology, 石华表 YM17-02: the four marble columns of 安佑宫, about 8 m high on an octagonal base of 1.24 m (S980, S818), stand in the 3D view as a square pavilion box. Proposal: a column shape, or no box, in boxes1860.py. Not applied"},
]

QING_SRC = {"S05", "S200", "S201", "S202", "S207", "S208", "S210", "S211"}
QUOTE = re.compile(r"^([\u3400-\u9fff\uf900-\ufaff\u3000-\u303f\uff01-\uff5e …\.]{4,})")


def add_tie(row, key, conf):
    have = dict(x.rsplit(":", 1) if ":" in x else (x, "likely") for x in filter(None, row["shows"].split(";")) if not x.startswith("GARDEN"))
    if key in have:
        return False
    row["shows"] = ";".join(filter(None, [row["shows"], f"{key}:{conf}"]))
    return True


def retie(by, buildings, photos, evidence, efields, enxt):
    """Each hall gets the pictures, drawings and texts that show it: the album leaf the album reader placed it on, the rows a worker cites for it, and the 日下旧闻考 passage that names it (a new row where the catalogue holds none)."""
    pics = {p["photo_id"]: p for p in photos}
    evs = {e["evidence_id"]: e for e in evidence}
    n = {"picture": 0, "cited": 0, "matched": 0, "new": 0}
    items = [d for d in by.get("hall", []) + by.get("dim", []) + by.get("interior", []) if s(d.get("id")) in buildings and buildings[s(d.get("id"))]["parent_id"]]
    for d in items:
        hid = s(d.get("id"))
        text = " ".join(s(d.get(k)) for k in ("locator", "basis", "relation", "quote_or_basis"))
        conf = "likely" if s(d.get("confidence")) in ("A", "B") else "guess"
        if d["type"] == "hall" and s(d.get("source_id")).startswith("S08"):
            for pid in re.findall(r"P\d{4}", s(d.get("locator"))):
                if pid in pics and add_tie(pics[pid], hid, conf):
                    n["picture"] += 1
        for eid in re.findall(r"E\d{4}", text):
            if eid in evs and add_tie(evs[eid], hid, "likely"):
                n["cited"] += 1
    for d in by.get("hall", []):
        hid = s(d.get("id"))
        if hid not in buildings or s(d.get("source_id")) not in QING_SRC or d.get("status") != "viewed" or re.search(r"E\d{4}", s(d.get("basis")) + s(d.get("locator"))):
            continue
        names = [x for x in (s(d.get("plaque_zh")), buildings[hid]["name_zh"]) if len(x) >= 3 and x not in ("圓明園", "圆明园", "長春園", "长春园", "綺春園", "绮春园")]  # a name short enough to stand in other passages, or the garden's, ties nothing
        scene = buildings[hid]["parent_id"]
        match = [e for e in evidence if e["source_id"].split(";")[0] == s(d.get("source_id")) and scene in e["shows"] and any(x in e["excerpt_zh"] for x in names)]
        if match:
            for e in match[:2]:
                if add_tie(e, hid, "sure"):
                    n["matched"] += 1
                    print("  tie", e["evidence_id"], hid, names)
            continue
        m = QUOTE.match(s(d.get("basis")))
        if not m or not any(x in m[1] for x in names):
            continue
        quote = m[1].strip(" .")
        e = {k: "" for k in efields}
        e.update(evidence_id=f"E{enxt:04d}", kind="text", source_id=s(d.get("source_id")), title=f"{s(d.get('plaque_zh')) or buildings[hid]['name_zh']}: the passage that names it", date="1780s" if s(d.get("source_id")) == "S05" else "", locator=s(d.get("locator")), link="", rights_class="free", status="viewed", shows=f"{hid}:sure", excerpt_zh=quote, summary_en=("; ".join(x for x in (f"{s(d.get('bays'))} bays" if s(d.get("bays")) else "", s(d.get("relation"))) if x))[:300])
        enxt += 1
        evidence.append(e)
        n["new"] += 1
    print("hall ties:", n)


def main():
    topics = sys.argv[1:] or TOPICS
    rows = load(topics) + [dict(d, _topic="coordinator", _n=i) for i, d in enumerate(HAND_DIMS + HAND_QUESTIONS + HAND_WISHES)]
    by = {}
    for d in rows:
        by.setdefault(d.get("type", ""), []).append(d)
    print({k: len(v) for k, v in by.items()})
    buildings = {r["id"]: r for r in csv_rows(head("research/buildings.csv"))[1]}  # the rows before this round's facts
    about = json.load(open(SC / "about.json", encoding="utf-8"))

    # sources: a new section, new ids only from the workers' blocks
    src_text = head("research/sources.md")
    known = set(re.findall(r"^\| (S\d+) \|", src_text, flags=re.M))
    new_src = []
    for d in by.get("source", []):
        sid = s(d.get("id"))
        if not re.match(r"^S9\d\d$", sid) or sid in known or sid in {x[0] for x in new_src}:
            if sid not in known:
                print("source id outside the blocks or twice:", sid, d["_topic"])
            continue
        new_src.append((sid, f"| {sid} | {s(d.get('text')).replace('|', '/')} | {s(d.get('year'))} | {s(d.get('reuse')).replace('|', '/')} | {s(d.get('status'))} | {s(d.get('link'))}{('. ' + s(d.get('note')).replace('|', '/')) if s(d.get('note')) else ''} |"))
    new_src.sort(key=lambda x: int(x[0][1:]))
    if new_src:
        src_text = src_text.rstrip("\n") + "\n\n## Round 7: the scenes (S900-S909 and S910-S919 texts, S920-S939 plans, S940-S964 digs and studies, S965-S979 pictures, S980-S989 the other Forty Scenes, S990-S999 Changchun and Qichun)\n\n| ID | Source | Year | Reuse | Status | Link / note |\n|---|---|---|---|---|---|\n" + "\n".join(x[1] for x in new_src) + "\n"
    (ROOT / "research/sources.md").write_text(src_text, encoding="utf-8")
    known |= {x[0] for x in new_src}

    # pictures: P ids from the next free one; free images to research/photos/images, research-only looks to research/raw/photos
    fields, photos = csv_rows(head("research/photos/catalog.csv"))
    nxt = max(int(p["photo_id"][1:]) for p in photos) + 1
    slug_to_pid, seen_url = {}, {p["source_url"]: p["photo_id"] for p in photos}
    for d in by.get("picture", []):
        url = s(d.get("source_url"))
        if url in seen_url:
            print("picture already catalogued:", seen_url[url], url[:80])
            slug_to_pid[Path(s(d.get("file"))).stem] = seen_url[url]
            continue
        pid = f"P{nxt:04d}"
        nxt += 1
        seen_url[url] = pid
        f = s(d.get("file"))
        dest = ""
        if f and Path(f).exists():
            free = d.get("rights_class") == "free"
            folder = ROOT / ("research/photos/images" if free else "research/raw/photos")
            folder.mkdir(parents=True, exist_ok=True)
            with Image.open(f) as im:
                im = im.convert("RGB")
                im.thumbnail((1600, 1600))
                im.save(folder / f"{pid}.jpg", quality=82, optimize=True)
                d["width"], d["height"] = im.size
            dest = f"research/photos/images/{pid}.jpg" if free else f"research/raw/photos/{pid}.jpg"
        slug_to_pid[Path(f).stem] = pid
        row = {k: s(d.get(k)) for k in fields}
        row.update(photo_id=pid, file=dest, relation="self", crop="", notes=(s(d.get("notes")) + f" Round 7, {d['_topic']}.").strip())
        photos.append(row)
        if d.get("view"):
            by.setdefault("view", []).append({"type": "view", "photo_id": pid, "id": next(iter(s(d.get("shows")).split(":")), ""), "view": d.get("view"), "visible_part": d.get("why", ""), "state": d.get("state", ""), "reliability": d.get("reliability", ""), "note": "", "_topic": d["_topic"], "_n": d["_n"]})
    for c in by.get("correction", []):
        ref = s(c.get("photo_id"))
        for p in photos:
            if p["photo_id"] == ref and c.get("field") in p and (not s(c.get("old")) or p[c["field"]] == s(c.get("old"))):
                p[c["field"]] = s(c.get("new"))
                p["notes"] = (p["notes"] + f" Round 7: {c['field']} corrected, {s(c.get('reason'))}").strip()
    photo_ids = {p["photo_id"] for p in photos}

    # evidence
    efields, evidence = csv_rows(head("research/evidence/catalog.csv"))
    enxt = max(int(e["evidence_id"][1:]) for e in evidence) + 1
    for d in by.get("evidence", []):
        row = {k: s(d.get(k)) for k in efields}
        if row["rights_class"] != "free":
            row["excerpt_zh"] = row["excerpt_other"] = ""
        row["evidence_id"] = f"E{enxt:04d}"
        enxt += 1
        evidence.append(row)
    for c in by.get("correction", []):
        ref = s(c.get("photo_id"))
        for e in evidence:
            if e["evidence_id"] == ref and c.get("field") in e:
                e[c["field"]] = s(c.get("new"))
    retie(by, buildings, photos, evidence, efields, enxt)
    write_csv(ROOT / "research/photos/catalog.csv", fields, photos)
    write_csv(ROOT / "research/evidence/catalog.csv", efields, evidence)

    # reconstructions
    rfields, recons = csv_rows(head("research/reconstructions/catalog.csv"))
    rnxt = max(int(r["recon_id"][1:]) for r in recons) + 1
    have = {r["link"] for r in recons}
    for d in by.get("recon", []):
        if s(d.get("link")) in have:
            continue
        have.add(s(d.get("link")))
        row = {k: s(d.get(k)) for k in rfields}
        row["recon_id"] = f"R{rnxt:04d}"
        rnxt += 1
        f = s(d.get("file"))
        if f and Path(f).exists():
            free = d.get("rights_class") == "free"
            folder = ROOT / ("research/reconstructions/images" if free else "research/raw/reconstructions")
            folder.mkdir(parents=True, exist_ok=True)
            with Image.open(f) as im:
                im = im.convert("RGB")
                im.thumbnail((1600, 1600))
                im.save(folder / f"{row['recon_id']}.jpg", quality=82, optimize=True)
                row["width"], row["height"] = im.size
            row["local_copy"] = f"research/{'reconstructions/images' if free else 'raw/reconstructions'}/{row['recon_id']}.jpg"
        row["notes"] = f"Round 7, {d['_topic']}."
        row["licence"] = row["licence"] or "none stated"
        recons.append(row)
    for c in by.get("correction", []):
        ref = s(c.get("photo_id"))
        for r in recons:
            if r["recon_id"] == ref and c.get("field") in r:
                r[c["field"]] = s(c.get("new"))
    write_csv(ROOT / "research/reconstructions/catalog.csv", rfields, recons)

    # facts for buildings.csv
    ffields, facts = csv_rows(head("research/evidence/facts.csv"))
    nf = 0
    for d in by.get("fact", []):
        bid, field = s(d.get("id")), s(d.get("field"))
        if bid not in buildings:
            print("fact on an unknown row:", bid, d["_topic"])
            continue
        if d.get("status") == "snippet":
            decision, reason = "lead", "Round 7: seen in a search summary only"
        elif field == "name_zh":
            decision, reason = ("name", "Round 7: a text names a block the plan leaves unnamed or unread") if not buildings[bid]["name_zh"] else ("note", "Round 7: the row has a name already; kept in the note")
        elif field in FACT_FIELDS:
            decision, reason = "apply", f"Round 7, {d['_topic']}"
        else:
            decision, reason = "note", f"Round 7: {field} has no column; kept in the note"
        if decision == "name" and not re.match(r"^[一-鿿]", s(d.get("value"))):
            decision = "note"
        if decision == "note" and field not in FACT_FIELDS:
            value = f"{field}: {s(d.get('value'))}"
        else:
            value = s(d.get("value"))
        if field == "storeys" and decision == "apply" and not value.isdigit():  # the boxes read a number; the words go to the note
            m = re.match(r"^(\d+)", value)
            facts.append(dict(id=bid, field="storeys", value=value, source_id=s(d.get("source_id")), locator=s(d.get("locator")), basis=s(d.get("quote_or_basis")), suggest_confidence=s(d.get("suggest_confidence")), decision="note", reason="Round 7: storeys in words, kept in the note"))
            if not m:
                continue
            value = m[1]
        facts.append(dict(id=bid, field=field if field in FACT_FIELDS else "changed" if decision == "lead" else field, value=value, source_id=s(d.get("source_id")), locator=s(d.get("locator")), basis=s(d.get("quote_or_basis")), suggest_confidence=s(d.get("suggest_confidence")), decision=decision, reason=reason))
        nf += 1
    for d in by.get("part", []):
        if d.get("action") == "name" and s(d.get("id")) in buildings and s(d.get("name_zh")):
            facts.append(dict(id=d["id"], field="name_zh", value=f"{re.sub(r'\s*\(.*\)$', '', s(d.get('name_zh')))} {s(d.get('name_pinyin'))}".strip(), source_id=s(d.get("source_id")), locator="", basis=s(d.get("basis")), suggest_confidence=s(d.get("confidence")), decision="name", reason="Round 7: research/scenes/parts.csv"))
            nf += 1
    # sizes: a hall's overall frontage and depth where a survey, a dig or a Qing drawing gives them (method a, seen); apply_facts lets a stated size win over the plan's estimate only
    picked = {}
    for d in by.get("dim", []):
        bid = s(d.get("id"))
        if bid not in buildings or not buildings[bid]["parent_id"] or d.get("method") != "a" or d.get("status") != "viewed":
            continue
        if "街" in buildings[bid]["name_zh"] or "inside" in s(d.get("part")) or "clear" in s(d.get("what")):
            continue
        what = s(d.get("what"))
        field = "frontage_m" if what == "frontage" else "depth_m" if what in ("depth", "other:overall_depth") else None
        if not field:
            continue
        rank = (what == "other:overall_depth" or what == "frontage", {"A": 2, "B": 1}.get(s(d.get("confidence")), 0))
        if field not in picked.get(bid, {}) or rank > picked[bid][field][0]:
            picked.setdefault(bid, {})[field] = (rank, d)
    nsize = 0
    for bid, fs in sorted(picked.items()):
        for field, (_, d) in sorted(fs.items()):
            facts.append(dict(id=bid, field=field, value=f"{float(d['value_m']):g}", source_id=s(d.get("source_id")), locator=s(d.get("locator")), basis=f"{s(d.get('part'))}: {s(d.get('basis'))}"[:400], suggest_confidence=s(d.get("confidence")), decision="apply", reason="Round 7: research/scenes/dimensions.csv, method a; replaces the plan's estimate, else kept in the note"))
            nsize += 1
    # fronts: a text that says which way a hall faces, where the row's front is assumed and points the other way
    card = {"N": 0, "E": 90, "S": 180, "W": 270}
    nori = 0
    for d in by.get("hall", []):
        bid, faces = s(d.get("id")), s(d.get("faces")).upper()[:1]
        if bid not in buildings or faces not in card or d["_topic"] == "album" or d.get("status") != "viewed" or s(d.get("confidence")) not in ("A", "B"):
            continue
        r = buildings[bid]
        if r["orientation_assumed"] != "True" or not r["orientation_deg"]:
            continue
        deg = float(r["orientation_deg"])
        turn = (card[faces] - deg + 540) % 360 - 180
        if abs(abs(turn) - 180) <= 45 and not any(f["id"] == bid and f["field"] == "orientation_deg" for f in facts):
            facts.append(dict(id=bid, field="orientation_deg", value=f"{(deg + 180) % 360:g}", source_id=s(d.get("source_id")), locator=s(d.get("locator")), basis=f"faces {faces}: {s(d.get('basis'))}"[:300], suggest_confidence=s(d.get("confidence")), decision="correct", reason="Round 7: the text says the front faces the other way; the plan's local turn kept"))
            nori += 1
    print(f"size facts {nsize}; fronts turned {nori}")
    write_csv(ROOT / "research/evidence/facts.csv", ffields, facts)

    # the sheets of research/scenes/
    def sheet(name, cols, items, key=None):
        out = []
        for d in items:
            r = {c: s(d.get(c)) for c in cols}
            out.append(r)
        if key:
            out.sort(key=key)
        write_csv(SC / name, cols, out)
        return out

    halls = [d for d in by.get("hall", []) if s(d.get("scene")) in about or s(d.get("id")).split("-")[0] in about]
    last = {}
    for i, d in enumerate(halls):  # the album worker refined some readings in a later row: the later one stands (its notes list them)
        if d["_topic"] == "album" and s(d.get("id")) not in ("", "NEW"):
            last[s(d.get("id"))] = i
    halls = [d for i, d in enumerate(halls) if not (d["_topic"] == "album" and s(d.get("id")) in last and last[s(d.get("id"))] != i)]
    for d in halls:
        if not s(d.get("scene")):
            d["scene"] = s(d.get("id")).split("-")[0]
        if s(d.get("id")) not in buildings:
            d["basis"] = (f"[given as {d.get('id')}] " if s(d.get("id")) not in ("", "NEW") else "") + s(d.get("basis"))
            d["id"] = "NEW"
    sheet("halls.csv", HALL_COLS, halls)
    dims = []
    for d in by.get("dim", []):
        if s(d.get("id")) not in buildings:
            if s(d.get("id")) != "GARDEN-YM":  # the plans worker's wall lengths of the whole garden: kept in its question row on the walls
                print("dim on an unknown row:", d.get("id"), d["_topic"])
            continue
        try:
            float(d.get("value_m"))
        except (TypeError, ValueError):
            print("dim without a number:", d.get("id"), d.get("value_m"), d["_topic"])
            continue
        if not d.get("scale"):
            d["scale"] = ""
        text = " ".join(s(d.get(k)) for k in ("locator", "basis", "part"))
        if d.get("confidence") == "A" and re.search(r"1873|1874|同治|Tongzhi|故1299|样1203", text):  # a plan of the repair of 1873-74 is a later source for the state of 1860
            d["confidence"] = "B"
            d["basis"] = f"{s(d.get('basis'))}; a plan of the Tongzhi repair of 1873-74, so B for 1860"
        dims.append(d)
    sheet("dimensions.csv", DIM_COLS, dims)
    views = []
    for d in by.get("view", []):
        if s(d.get("photo_id")) not in photo_ids:
            pid = slug_to_pid.get(s(d.get("photo_id")))
            if not pid:
                print("view of an unknown picture:", d.get("photo_id"), d["_topic"])
                continue
            d["photo_id"] = pid
        views.append(d)
    seen = set()
    views = [v for v in views if not ((v["photo_id"], v.get("id")) in seen or seen.add((v["photo_id"], v.get("id"))))]
    sheet("views.csv", VIEW_COLS, views)
    for d in by.get("best", []):
        ref = s(d.get("ref"))
        if ref and not re.match(r"^[PER]\d{4}$", ref):
            d["ref"] = slug_to_pid.get(ref, ref)
    sheet("best.csv", BEST_COLS, by.get("best", []), key=lambda r: (r["id"], int(r["rank"] or 99)))
    sheet("digs.csv", DIG_COLS, by.get("dig", []))
    sheet("interior.csv", INT_COLS, by.get("interior", []))
    # parts: one row per id. Two workers read the 九洲清晏 labels; their bases are joined. 同顺堂 is Tongzhi's name (1873) for the block where 基福堂 stood: the text row joins the plan row's box, not the other way round
    parts = {}
    for d in by.get("part", []):
        pid = s(d.get("id"))
        if pid == "YM03-N07" and s(d.get("action")).startswith("merge:"):
            d = dict(d, action="keep")
            parts["YM03-17"] = dict(id="YM03-17", name_zh="基福堂", name_pinyin="Jifu Tang", name_en="", what="the 1860 hall on the block that S01 labels 同顺堂, Tongzhi's name of 1873 for it", basis=s(d.get("basis")), source_id=s(d.get("source_id")), confidence=s(d.get("confidence")), action="merge:YM03-N07")
        if pid in parts:
            old_p = parts[pid]
            if old_p["action"] != s(d.get("action")):  # two workers disagree: the row stays as it is, and the doubt is said
                old_p["action"] = "keep"
                old_p["what"] = f"{old_p['what']}; the workers disagree on merging it ({s(d.get('action'))}), so it is kept"
            old_p["basis"] = f"{old_p['basis']} / {s(d.get('basis'))}"
            old_p["source_id"] = ";".join(dict.fromkeys(filter(None, old_p["source_id"].split(";") + s(d.get("source_id")).split(";"))))
            for k in ("name_pinyin", "name_en"):
                old_p[k] = old_p[k] or s(d.get(k))
        else:
            parts[pid] = {c: s(d.get(c)) for c in PART_COLS}
    for pr in parts.values():
        pr["name_zh"] = re.sub(r"\s*\(.*\)$", "", pr["name_zh"])  # the reading note goes to the basis, the name stays a name
    sheet("parts.csv", PART_COLS, sorted(parts.values(), key=lambda r: r["id"]))

    # about.json: fill only what is empty
    filled = 0
    drafts = {}
    for d in by.get("about", []):
        sid, field = s(d.get("id")), ABOUT_FIELDS.get(s(d.get("field")))
        if sid in about and field:
            drafts.setdefault((sid, field), []).append(s(d.get("text")))
    for (sid, field), texts in drafts.items():
        if not about[sid].get(field):
            about[sid][field] = "\n\n".join(dict.fromkeys(texts))
            filled += 1
    # the verified texts of the public scenes, and their Chinese drafts, replace the drafts; the checks are kept as a record
    verified = 0
    for d in by.get("text", []) + by.get("zh", []):
        sid, field = s(d.get("id")), s(d.get("field"))
        if sid in about and re.match(r"^(what|scene|later|interior|setting|survives|recons|best|gaps|summary)_(en|zh)$", field) and s(d.get("text")):
            about[sid][field] = s(d.get("text"))
            verified += 1
    print("verified fields", verified)
    for sid, fields in HAND.items():
        about.setdefault(sid, {}).update(fields)
    write_csv(SC / "checks.csv", ["id", "field", "sentence", "verdict", "source", "note", "fix"], [{k: s(d.get(k)) for k in ("id", "field", "sentence", "verdict", "source", "note", "fix")} for d in by.get("check", [])])
    (SC / "about.json").write_text(json.dumps(about, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    # questions and wishes
    q = head("research/questions.md")
    qn = max(int(x) for x in re.findall(r"\*\*Q(\d+)\.", q)) + 1
    items = []
    for d in by.get("question", []):
        text = re.sub(r"\s+", " ", s(d.get("text")))
        title = re.split(r"[:.;]\s", text, maxsplit=1)[0][:90]
        items.append(f"- **Q{qn}. {title}.** {text} ({d['_topic']} worker, Round 7)")
        qn += 1
    if items:
        q = q.replace("\n## Resolved", "\n### Found in Round 7: the scenes\n\n" + "\n".join(items) + "\n\n## Resolved", 1)
    (ROOT / "research/questions.md").write_text(q, encoding="utf-8")
    w = head("research/wishlist.md").rstrip("\n")
    wl = [f"| {s(d.get('what')).replace('|', '/')} | {s(d.get('replaces')).replace('|', '/')} | {s(d.get('where')).replace('|', '/')} | {s(d.get('how')).replace('|', '/')} |" for d in by.get("wish", [])]
    if wl:
        w += "\n" + "\n".join(wl)
    (ROOT / "research/wishlist.md").write_text(w + "\n", encoding="utf-8")
    print(f"sources +{len(new_src)}; pictures +{nxt - 1 - max(int(p['photo_id'][1:]) for p in csv_rows(head('research/photos/catalog.csv'))[1])}; evidence +{enxt - 1 - max(int(e['evidence_id'][1:]) for e in csv_rows(head('research/evidence/catalog.csv'))[1])}; recons +{rnxt - 1 - max(int(r['recon_id'][1:]) for r in csv_rows(head('research/reconstructions/catalog.csv'))[1])}; facts +{nf}; halls {len(halls)}; dims {len(dims)}; views {len(views)}; about fields filled {filled}; questions +{len(items)}; wishes +{len(wl)}")


if __name__ == "__main__":
    main()
