"""Write research/photos/catalog.csv from the pictures worker's research/plan/photos_raw.csv: `name:` entries of `shows` become building ids where a name matches one row."""

import csv
from pathlib import Path

RAW = Path("research/plan/photos_raw.csv")
OUT = Path("research/photos/catalog.csv")


def main() -> None:
    with open("research/buildings.csv", encoding="utf-8", newline="") as f:
        b = list(csv.DictReader(f))
    tops = {}
    for r in b:
        for k in (r["name_zh"], r["name_on_plan"]):
            if k and not r["parent_id"]:
                tops.setdefault(k, r["id"])
    with open(RAW, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
        fields = rows[0].keys()
    mapped, kept = 0, 0
    for r in rows:
        shows, also = [], [r["also_shows"]] if r["also_shows"] else []
        for s in [x for x in r["shows"].split(";") if x]:
            if s.startswith("name:"):
                _, name, conf = s.split(":")
                if name in tops:
                    shows.append(f"{tops[name]}:{conf}")
                    mapped += 1
                else:  # the whole garden, or the whole Xiyang Lou: no single id
                    also.append(name)
                    kept += 1
            else:
                shows.append(s)
        r["shows"] = ";".join(shows)
        r["also_shows"] = "; ".join(also)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fields)
        w.writeheader()
        w.writerows(rows)
    known = {r["id"] for r in b}
    bad = [s for r in rows for s in r["shows"].split(";") if s and s.split(":")[0] not in known]
    free = sum(1 for r in rows if r["rights_class"] == "free")
    print(f"catalog: {len(rows)} rows, {free} free, {len(rows) - free} research-only; name: mapped {mapped}, kept as text {kept}; unknown ids {bad}")
    # the copyright check: no research-only file outside research/raw
    for r in rows:
        assert not (r["rights_class"] != "free" and r["file"] and not r["file"].startswith("research/raw/")), r["photo_id"]
        assert not (r["rights_class"] == "free" and r["file"] and not r["file"].startswith("research/photos/images/")), r["photo_id"]


if __name__ == "__main__":
    main()
