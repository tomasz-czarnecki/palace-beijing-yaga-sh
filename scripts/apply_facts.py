"""Applies research/evidence/facts.csv to research/buildings.csv. Idempotent: a second run changes nothing. Runs after build_r1.py, which writes the rows from its inputs.

  uv run python scripts/apply_facts.py

Only `apply`, `name`, `note` and `size_lead` rows touch the csv; a `size_lead` is a dimension stated in a reconstruction or a modern study, kept in its own column `size_lead` with its citation, and never a size of the row, a source of the row or a reason to raise a grade; a `lead` was seen in a search summary and waits until someone reads it; `gate` rows belong to layers/walls_1860 and wait for that layer's next build. An empty field takes the value. A field already filled keeps what it has: `built`, `changed` and `destroyed` take the new value after it, any other goes to the note, so the conflict stays visible. Each applied row adds its source to `sources`. Confidence rises from C to B with any applied fact; from B to A only on a dated Qing text (S05, S200, S201, S207, S208, S210) that names the thing itself.
"""

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QING = {"S05", "S200", "S201", "S207", "S208", "S210"}
APPEND = {"built", "changed", "destroyed"}


def reading(value):
    """A label the plan leaves part unread, settled by a text: `思顺堂 Si Shun Tang (...)`."""
    m = re.match(r"([\u4e00-\u9fff]+)\s*([A-Za-z' ]*)", value)
    return m[1], m[2].strip()


def add_note(row, text):
    head, sep, plan = row["notes"].partition(" | plan:")
    if row["notes"].startswith("plan:"):
        head, sep, plan = "", " | plan:", row["notes"][5:]
    if text in head:
        return False
    head = f"{head.rstrip()} {text}".strip()
    row["notes"] = head + sep + plan
    return True


def main():
    with open(ROOT / "research/buildings.csv", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fields, rows = reader.fieldnames, list(reader)
    by_id = {r["id"]: r for r in rows}
    stated_now = set()  # rows whose plan size a stated one replaced in this run: the other side may follow
    done = {"filled": 0, "appended": 0, "noted": 0, "named": 0, "raised": 0, "already": 0, "lead": 0, "size_lead": 0}
    for fact in csv.DictReader(open(ROOT / "research/evidence/facts.csv", encoding="utf-8", newline="")):
        if fact["decision"] in ("lead", "gate"):
            done["lead"] += 1
            continue
        row = by_id[fact["id"]]
        field, value = fact["field"], fact["value"]
        tag = f"{value} ({fact['source_id']}{', ' + fact['locator'] if fact['locator'] else ''})."
        if fact["decision"] == "size_lead":
            if tag not in row["size_lead"]:
                row["size_lead"] = f"{row['size_lead']} {tag}".strip()
                done["size_lead"] += 1
            continue
        if fact["decision"] == "correct":  # a figure of ours shown wrong: replaced, with the old one kept in the note
            if row[field] != value:
                old = row[field]
                row[field] = value
                if field in ("frontage_m", "depth_m"):
                    row["size_source"] = f"stated: {fact['source_id']}, {fact['locator']}"
                    add_note(row, f"Round 6 replaced {field.removesuffix('_m')} {old or 'none'} m.")
                elif field in ("lat", "lon"):
                    row["pos_source"] = f"{fact['source_id']}, moved in Round 6: {fact['locator']}"
                elif field == "orientation_deg":  # Round 7: a text or the album says which way the front faces; the plan's local turn is kept
                    row["orientation_assumed"] = "False"
                    add_note(row, f"Round 7 turned the front from {old}° ({fact['source_id']} {fact['locator']}).")
                done["corrected"] = done.get("corrected", 0) + 1
            continue
        if fact["decision"] == "name":
            zh, py = reading(value)
            if row["name_zh"] != zh:
                row["name_zh"], row["name_pinyin"] = zh, py or row["name_pinyin"]
                done["named"] += 1
        elif fact["decision"] == "note":
            done["noted" if add_note(row, tag) else "already"] += 1
        elif not row[field]:
            row[field] = value
            done["filled"] += 1
            if field in ("frontage_m", "depth_m"):
                row["size_source"] = f"stated: {fact['source_id']}, {fact['locator']}"
        elif value in row[field] or "first dated item" in value:  # a first dated use says less than a date already there
            done["already"] += 1
        elif field == "destroyed" and row[field] == "1860":
            row[field] = value
            done["filled"] += 1
        elif field in APPEND:
            row[field] = f"{row[field]}; {value}"
            done["appended"] += 1
        elif field in ("frontage_m", "depth_m") and ("plan px" in row["size_source"] or fact["id"] in stated_now):  # a stated size wins over the plan's estimate, both sides of it
            row[field] = value
            row["size_source"] = f"stated: {fact['source_id']}, {fact['locator']}"
            stated_now.add(fact["id"])
            done["filled"] += 1
        else:
            done["noted" if add_note(row, f"{field}: {tag}") else "already"] += 1
        have = row["sources"].split(";") if row["sources"] else []
        for s in re.findall(r"S\d+", fact["source_id"]):
            if s not in have:
                have.append(s)
        row["sources"] = ";".join(have)
        cited = set(re.findall(r"S\d+", fact["source_id"]))
        if row["confidence"] == "C" and fact["suggest_confidence"] in ("A", "B"):
            row["confidence"] = "B"
            done["raised"] += 1
        if row["confidence"] == "B" and fact["suggest_confidence"] == "A" and cited & QING and fact["field"] in ("built", "changed", "bays"):
            row["confidence"] = "A"
            done["raised"] += 1
    with open(ROOT / "research/buildings.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fields)
        w.writeheader()
        w.writerows(rows)
    print(done)


if __name__ == "__main__":
    main()
