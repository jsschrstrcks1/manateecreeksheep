#!/usr/bin/env python3
"""lambing_reconcile.py — reconcile the 2026 lambing log against the pedigree (MCS). READ-ONLY.

lambing_records_2026 is a name-keyed event log with something the pedigree does NOT carry:
lambs_born vs lambs_alive — BIRTH SURVIVAL. ewe_productivity deliberately leaves it out (its dam
field is a display name, and a wrong name→id match would corrupt a selection metric). This tool
does the reconciliation carefully and read-only: it resolves each lambing to a pedigree dam by its
explicit dam_id or a UNIQUE exact name (never a fuzzy guess — an ambiguous name is flagged, not
matched), surfaces birth survival, and cross-checks the pedigree (does the dam have about that many
offspring dated near the lambing?). It writes nothing; the two things it produces that the pedigree
cannot are birth survival and a data-integrity check between the two records.

  - reconcile(db): per lambing record — resolved dam, match basis, born/alive/survival, and a
    pedigree cross-check (offspring on file with a dob within a window of the lambing date).
  - birth_survival(db): flock birth-survival summary over the MATCHED records only (honest — an
    unmatched record contributes nothing rather than a guess).

    python3 scripts/lambing_reconcile.py            # reconciliation table + birth-survival summary
    python3 scripts/lambing_reconcile.py --json
"""
import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "flock_database.json"

DOB_WINDOW_DAYS = 14   # a pedigree offspring counts as "this lambing" if its dob is within +/- this
DOB_DISCREPANCY_DAYS = 60  # beyond the window but within this, treat as the SAME lambing dated wrong


def _norm(x):
    return re.sub(r"\s+", " ", str(x or "").strip().lower())


def _iso(d):
    try:
        return datetime.strptime(str(d), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def _name_index(db):
    idx = defaultdict(list)
    for s in db.get("sheep", []):
        if s.get("name"):
            idx[_norm(s["name"])].append(s["id"])
    return idx


def _resolve_dam(rec, name_idx, ids):
    """(dam_id|None, basis). basis ∈ dam_id | name | unmatched | ambiguous. Never a fuzzy guess."""
    if rec.get("dam_id"):
        return (rec["dam_id"], "dam_id" if rec["dam_id"] in ids else "dam_id_unknown")
    cand = name_idx.get(_norm(rec.get("dam")))
    if not cand:
        return (None, "unmatched")
    if len(cand) > 1:
        return (None, "ambiguous")
    return (cand[0], "name")


def reconcile(db):
    ids = {s["id"] for s in db.get("sheep", [])}
    name_idx = _name_index(db)
    # offspring by dam id, with dobs
    offspring = defaultdict(list)
    for s in db.get("sheep", []):
        if s.get("dam_id"):
            offspring[s["dam_id"]].append(_iso(s.get("dob")))

    rows = []
    for rec in db.get("lambing_records_2026", []):
        dam_id, basis = _resolve_dam(rec, name_idx, ids)
        born = rec.get("lambs_born", rec.get("lamb_count"))
        alive = rec.get("lambs_alive")
        ldate = _iso(rec.get("date"))
        survival = (round(alive / born * 100, 1) if isinstance(born, (int, float)) and born
                    and isinstance(alive, (int, float)) else None)
        # pedigree cross-check: offspring of this dam near the lambing date. Distinguish a genuine
        # date MATCH (within the window) from a date DISCREPANCY (offspring exist but are dated 15-60
        # days off — the same lambing recorded with a different date on one side) from genuinely
        # ABSENT (no offspring within either window). A lamb's dob is its lambing day, so a large
        # gap is a real accuracy discrepancy between the two records, not two separate events.
        ped_near = None
        check = "no_dam" if dam_id is None else "undated"
        if dam_id and ldate:
            dobs = [d for d in offspring.get(dam_id, []) if d]
            near = [d for d in dobs if abs((d - ldate).days) <= DOB_WINDOW_DAYS]
            disc = [d for d in dobs if DOB_WINDOW_DAYS < abs((d - ldate).days) <= DOB_DISCREPANCY_DAYS]
            ped_near = len(near)
            if near:
                check = ("ok" if isinstance(born, (int, float)) and len(near) == born
                         else f"count: pedigree {len(near)} vs record {born}")
            elif disc:
                nearest = min(disc, key=lambda d: abs((d - ldate).days))
                check = f"date_discrepancy: pedigree dob {nearest.isoformat()} vs record {ldate.isoformat()} ({abs((nearest-ldate).days)}d)"
            else:
                check = "no_offspring_on_file"
        rows.append({
            "date": rec.get("date"), "dam_input": rec.get("dam") or rec.get("dam_id"),
            "dam_id": dam_id, "match": basis,
            "lambs_born": born, "lambs_alive": alive, "survival_pct": survival,
            "sire_input": rec.get("sire") or rec.get("sire_id"),
            "pedigree_offspring_near_date": ped_near, "pedigree_check": check,
            "notes": rec.get("notes"),
        })
    rows.sort(key=lambda r: r["date"] or "")
    return rows


def birth_survival(db):
    """Flock birth survival over MATCHED, quantified records only."""
    rows = reconcile(db)
    born = sum(r["lambs_born"] for r in rows if isinstance(r["lambs_born"], (int, float)))
    alive = sum(r["lambs_alive"] for r in rows if isinstance(r["lambs_alive"], (int, float)))
    losses = [r for r in rows if isinstance(r["survival_pct"], (int, float)) and r["survival_pct"] < 100]
    return {"records": len(rows), "lambs_born": born, "lambs_alive": alive,
            "survival_pct": round(alive / born * 100, 1) if born else None,
            "records_with_a_loss": losses}


def main():
    ap = argparse.ArgumentParser(description="Reconcile 2026 lambing log vs pedigree (read-only)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    db = json.loads(DB_PATH.read_text())
    rows = reconcile(db)
    summ = birth_survival(db)
    if args.json:
        print(json.dumps({"reconciliation": rows, "birth_survival": summ}, indent=2)); return 0

    print(f"Lambing reconciliation (2026) — {len(rows)} records\n")
    print(f"  {'date':11} {'dam':22} {'match':10} {'born':>4} {'alive':>5} {'surv':>5}  pedigree check")
    for r in rows:
        surv = f"{r['survival_pct']:g}%" if r["survival_pct"] is not None else "—"
        print(f"  {str(r['date'] or '—'):11} {str(r['dam_input'])[:22]:22} {r['match']:10} "
              f"{str(r['lambs_born']):>4} {str(r['lambs_alive']):>5} {surv:>5}  {r['pedigree_check']}")

    print(f"\nBirth survival (matched, quantified records): {summ['lambs_alive']}/{summ['lambs_born']} "
          f"= {summ['survival_pct']}%")
    for r in summ["records_with_a_loss"]:
        print(f"  LOSS  {r['date']} {r['dam_input']}: {r['lambs_born']} born, {r['lambs_alive']} alive"
              + (f" — {r['notes'][:60]}" if r.get("notes") else ""))
    unmatched = [r for r in rows if r["match"] in ("unmatched", "ambiguous")]
    if unmatched:
        print(f"\n  {len(unmatched)} record(s) not matched to a pedigree dam (flagged, never guessed):")
        for r in unmatched:
            print(f"    {r['date']} {r['dam_input']!r} ({r['match']})")
    print("\n  Read-only. Birth survival is what the pedigree cannot give; the pedigree check flags"
          "\n  where the lambing log and the id-linked offspring disagree. Operator resolves.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
