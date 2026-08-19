#!/usr/bin/env python3
"""Ewe lifetime productivity ledger (MCS-18) — per-dam lambings across years, derived.

Soli Deo Gloria.

Sheep have lambings, not litters: the selection question is lambs (born, alive,
eventually weaned) per ewe per year, across her lifetime. This derives it — never
stores it — from what the records already hold:

  1. sheep[].dam_id links (117 today): every animal crediting its dam, with birth
     year from its DOB when present;
  2. lambing_records_2026 rows (dam recorded by NAME — resolved against names,
     aliases, then ids; an unresolvable name is REPORTED, never guessed to an id).

The two sources overlap for 2026 (a lambing row and the lamb records it produced);
lambs are counted from dam_id links where they exist and the lambing row supplies
born/alive counts and dates — the report shows both and never silently sums
overlapping sources into a double count.

Usage: python3 scripts/ewe_productivity.py [--ewe <id>] [--min-lambings N]
"""
import argparse
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).parent.parent
DB_PATH = Path(os.environ.get("FLOCK_DB_PATH") or REPO / "data" / "flock_database.json")


def name_index(sheep):
    idx = {}
    for s in sheep:
        idx[s["id"].lower()] = s["id"]
        if s.get("name"):
            idx.setdefault(s["name"].lower(), s["id"])
        for a in s.get("aliases") or []:
            if isinstance(a, str):
                idx.setdefault(a.lower(), s["id"])
    return idx


def resolve_dam(name, idx):
    """Resolve a lambing-record dam name to a sheep id, or None (reported, not guessed)."""
    if not name:
        return None
    low = name.strip().lower()
    return idx.get(low) or idx.get(low.replace(" ", "-"))


def productivity(db):
    """Return (per_ewe dict, unresolved list). per_ewe[id] = {
        offspring: [ids], offspring_years: {year: n}, lambing_rows: [...],
        rows_born, rows_alive }"""
    sheep = db.get("sheep", [])
    by_id = {s["id"]: s for s in sheep}
    idx = name_index(sheep)
    per = defaultdict(lambda: {"offspring": [], "offspring_years": defaultdict(int),
                               "lambing_rows": [], "rows_born": 0, "rows_alive": 0})
    for s in sheep:
        dam = s.get("dam_id")
        if dam and dam in by_id:
            per[dam]["offspring"].append(s["id"])
            dob = s.get("dob") or ""
            year = dob[:4] if len(dob) >= 4 and dob[:4].isdigit() else "unknown"
            per[dam]["offspring_years"][year] += 1
    unresolved = []
    for row in db.get("lambing_records_2026") or []:
        dam_id = resolve_dam(row.get("dam"), idx)
        if not dam_id:
            unresolved.append(row.get("dam"))
            continue
        per[dam_id]["lambing_rows"].append(row)
        per[dam_id]["rows_born"] += row.get("lambs_born") or 0
        per[dam_id]["rows_alive"] += row.get("lambs_alive") or 0
    return dict(per), unresolved


def main():
    ap = argparse.ArgumentParser(description="Ewe lifetime productivity (MCS-18)")
    ap.add_argument("--ewe")
    ap.add_argument("--min-lambings", type=int, default=0, dest="min_l")
    args = ap.parse_args()
    db = json.load(open(DB_PATH))
    by_id = {s["id"]: s for s in db.get("sheep", [])}
    per, unresolved = productivity(db)

    rows = []
    for eid, p in per.items():
        s = by_id.get(eid, {})
        if s.get("sex") not in ("ewe", "ewe_lamb", None):
            continue
        years = {y for y in p["offspring_years"] if y != "unknown"}
        rows.append((eid, s.get("status", "?"), len(p["offspring"]), len(years),
                     len(p["lambing_rows"]), p["rows_born"], p["rows_alive"]))
    rows.sort(key=lambda r: -r[2])
    if args.ewe:
        rows = [r for r in rows if r[0] == args.ewe]
    print(f"{'ewe':30} {'status':9} {'lambs(dam_id)':>13} {'years':>5} "
          f"{'2026 rows':>9} {'born':>4} {'alive':>5}")
    shown = 0
    for eid, st, n_off, n_years, n_rows, born, alive in rows:
        if n_off + n_rows < max(args.min_l, 1):
            continue
        print(f"{eid:30} {st:9} {n_off:>13} {n_years:>5} {n_rows:>9} {born:>4} {alive:>5}")
        shown += 1
    print(f"\n({shown} dams with recorded production; dam_id-linked lambs and 2026 lambing "
          f"rows shown side by side — overlapping sources are never silently summed)")
    if unresolved:
        print(f"UNRESOLVED lambing-record dam names ({len(unresolved)}) — fix by adding the "
              f"name as an alias, never by guessing: {sorted(set(unresolved))}")


if __name__ == "__main__":
    main()
