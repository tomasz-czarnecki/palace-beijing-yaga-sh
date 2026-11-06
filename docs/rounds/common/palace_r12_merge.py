"""Round 12: how research/greens/species.csv was first made from the six workers' rows in scratch. A record, not a pipeline step: species.csv is hand-edited from Round 12 on.

Adds `id` (GS-0001, ...), `form` (how the view draws the plant, from the plant's name: pine, cypress, willow, broad, blossom, bamboo, shrub, topiary, hedge, lotus, floating, reed,
rock, and none for what is not drawn: fields, lawns, climbers, potted plants), `height_m` (blank: the species default of scripts/greens1860.py) and `worker`.
Rows are kept in the workers' order; nothing in them is changed except trimmed blanks.
  python3 docs/rounds/common/palace_r12_merge.py /opt/data/cache/scratch
"""

import csv
import sys
from pathlib import Path

WORKERS = ["texts_ym_a", "texts_ym_b", "cc_qc_xy", "album_a", "album_b", "survivors_accounts"]
COLS = ["id", "scene_id", "plant_zh", "latin", "name_en", "role", "form", "place", "place_text", "season", "height_m", "source_kind", "sources", "locator", "quote",
        "confidence", "status", "use", "reject_reason", "note", "worker"]

# The first rule that matches the plant's name wins; the role can override (a potted plant, a field, a lawn is not drawn).
FORMS = [
    (("修剪", "树篱", "绿篱"), "topiary"),
    (("石", "假山", "峰"), "rock"),
    (("白皮松", "松"), "pine"),
    (("柏", "桧", "檜"), "cypress"),
    (("柳",), "willow"),
    (("竹",), "bamboo"),
    (("荷", "莲", "蓮", "菡萏", "藕", "芙蕖"), "lotus"),
    (("芦", "蘆", "葦", "苇", "蒲", "蓼", "荻", "菰", "莎", "芦苇"), "reed"),
    (("荇", "菱", "萍", "藻", "蘋"), "floating"),
    (("桃", "杏", "梅", "李", "梨", "海棠", "玉兰", "玉蘭", "花树", "樱", "辛夷"), "blossom"),
    (("牡丹", "芍药", "芍藥", "菊", "花", "丁香", "蔷薇", "月季", "萱"), "shrub"),
    (("藤", "萝", "蘿", "葡萄", "瓜"), "none"),
    (("稻", "麦", "麥", "禾", "黍", "蔬", "菜", "桑麻", "粟"), "none"),
    (("草", "苔", "芝"), "none"),
    (("槐", "榆", "桐", "梧", "枫", "楓", "红叶", "落叶", "阔叶", "树", "樹", "木", "银杏", "柿", "枣", "棗", "楸", "桑", "椿", "栗", "林"), "broad"),
]


def form_of(row):
    if row["role"] in ("potted", "field", "lawn", "climber"):
        return "none"
    if row["role"] == "hedge":
        return "hedge"
    name = row["plant_zh"]
    for keys, form in FORMS:
        if any(k in name for k in keys):
            return form
    return {"lotus": "lotus", "reed": "reed", "bamboo": "bamboo", "aquatic": "floating", "flower_bed": "shrub"}.get(row["role"], "broad")


def main():
    scratch = Path(sys.argv[1] if len(sys.argv) > 1 else "/opt/data/cache/scratch")
    rows = []
    for w in WORKERS:
        for r in csv.DictReader(open(scratch / f"palace_r12_greens_rows_{w}.csv", encoding="utf-8")):
            r = {k: (v or "").strip() for k, v in r.items() if k}
            r["worker"] = w
            r["form"] = form_of(r)
            r["height_m"] = ""
            rows.append(r)
    for i, r in enumerate(rows, 1):
        r["id"] = f"GS-{i:04d}"
    out = Path(__file__).resolve().parents[3] / "research/greens/species.csv"
    with open(out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, COLS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in COLS})
    print(f"{len(rows)} rows to {out}")


if __name__ == "__main__":
    main()
