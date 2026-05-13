#!/usr/bin/env python3
"""
run_annual_eval.py — Build/merge per-year annual evaluation JSONs.

Closes L7 from MANATEE_CREEK_REDESIGN_PLAN.md.

Problem this solves
-------------------
`export_to_sheets.py` used to generate BLANK eval templates each run, so any
owner-filled scores typed into the sheet were lost on the next export.

Solution
--------
This script writes the per-year evaluation roster to:
    data/annual_evals/<year>_ram_eval.json
    data/annual_evals/<year>_ewe_eval.json

Each is the system of record for that year's eval. When re-run, the script
MERGES with the existing file: animals already present keep their scores;
new animals are appended with blank scores; animals that became deceased /
sold / culled / gifted between runs stay in the JSON (archive flag) so the
historical audit survives.

`export_to_sheets.py` (modified in the same commit) reads from these JSONs
instead of recomputing.

Usage
-----
    python3 scripts/run_annual_eval.py            # default year = current calendar year
    python3 scripts/run_annual_eval.py --year 2026
    python3 scripts/run_annual_eval.py --dry-run  # show what would change
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
DB_PATH = REPO_ROOT / "data" / "flock_database.json"
EVAL_DIR = REPO_ROOT / "data" / "annual_evals"

# Scoring schema — keep aligned with the headers in export_to_sheets.py
RAM_SCORE_KEYS = [
    "offspring_avg_famacha",      # 40%
    "offspring_shed_pct",          # 25%
    "offspring_avg_daily_gain",    # 15%
    "conception_rate",             # 10%
    "offspring_survival_90d",      # 10%
]
EWE_SCORE_KEYS = [
    "own_famacha_avg",     # 30%
    "deworming_events",    # 20%
    "shedding_score",      # 15%
    "lambing_success",     # 15%
    "offspring_famacha",   # 10%
    "bcs",                 # 10%
]


def empty_scores(keys):
    return {k: None for k in keys}


def stub_entry(sheep, score_keys):
    return {
        "id": sheep["id"],
        "name": sheep.get("name", ""),
        "pen": sheep.get("pen") or "",
        "stage": "",
        "scores": empty_scores(score_keys),
        "total_score": None,
        "action": "",
        "status": sheep.get("status", "unknown"),
        "archived": sheep.get("status") in ("deceased", "sold", "culled", "gifted"),
    }


def candidate_rams(db):
    return [
        s for s in db["sheep"]
        if s.get("status") == "alive"
        and s.get("sex") in ("ram", "ram_lamb")
        and s.get("pen") and s.get("pen") != "Goose Pen"
    ]


def candidate_ewes(db):
    return [
        s for s in db["sheep"]
        if s.get("status") == "alive"
        and s.get("sex") in ("ewe", "ewe_lamb")
    ]


def merge_eval(existing, current_candidates, score_keys):
    """Merge:
       - keep existing entries (preserves scores) for animals still on roster
       - update status field on each entry from the current DB
       - mark missing-from-current entries archived=True (they exited mid-year)
       - append new entries (blank) for fresh animals
    """
    by_id = {e["id"]: e for e in existing.get("animals", [])}
    current_ids = set()
    for s in current_candidates:
        current_ids.add(s["id"])
        if s["id"] in by_id:
            e = by_id[s["id"]]
            e["name"] = s.get("name", e.get("name", ""))
            e["pen"] = s.get("pen") or ""
            e["status"] = s.get("status", "alive")
            e["archived"] = False
        else:
            by_id[s["id"]] = stub_entry(s, score_keys)

    # Anyone in JSON but no longer on current roster -> mark archived but keep
    for eid, e in by_id.items():
        if eid not in current_ids:
            e["archived"] = True

    return sorted(by_id.values(), key=lambda x: (x.get("archived", False), x.get("pen", ""), x.get("name", "")))


def load_or_init(path, year, score_keys_label):
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {
        "year": year,
        "kind": score_keys_label,
        "created": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "last_updated": None,
        "animals": [],
    }


def run(year, dry_run=False):
    with open(DB_PATH) as f:
        db = json.load(f)
    EVAL_DIR.mkdir(parents=True, exist_ok=True)

    ram_path = EVAL_DIR / f"{year}_ram_eval.json"
    ewe_path = EVAL_DIR / f"{year}_ewe_eval.json"

    ram_doc = load_or_init(ram_path, year, "ram")
    ram_doc["animals"] = merge_eval(ram_doc, candidate_rams(db), RAM_SCORE_KEYS)
    ram_doc["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    ewe_doc = load_or_init(ewe_path, year, "ewe")
    ewe_doc["animals"] = merge_eval(ewe_doc, candidate_ewes(db), EWE_SCORE_KEYS)
    ewe_doc["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if dry_run:
        print(f"[dry-run] {year}_ram_eval.json: {len(ram_doc['animals'])} entries "
              f"({sum(1 for a in ram_doc['animals'] if not a['archived'])} active)")
        print(f"[dry-run] {year}_ewe_eval.json: {len(ewe_doc['animals'])} entries "
              f"({sum(1 for a in ewe_doc['animals'] if not a['archived'])} active)")
        return

    with open(ram_path, "w") as f:
        json.dump(ram_doc, f, indent=2, ensure_ascii=False)
    with open(ewe_path, "w") as f:
        json.dump(ewe_doc, f, indent=2, ensure_ascii=False)

    print(f"Wrote {ram_path.relative_to(REPO_ROOT)} ({len(ram_doc['animals'])} entries, "
          f"{sum(1 for a in ram_doc['animals'] if not a['archived'])} active)")
    print(f"Wrote {ewe_path.relative_to(REPO_ROOT)} ({len(ewe_doc['animals'])} entries, "
          f"{sum(1 for a in ewe_doc['animals'] if not a['archived'])} active)")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument("--year", type=int, default=datetime.now().year)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    run(args.year, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
