#!/usr/bin/env python3
"""ewe_productivity.py — ewe lifetime productivity ledger (MCS-18). READ-ONLY.

Per-dam performance across her whole life, for breeding-selection decisions: how many
LAMBINGS she has had, how many lambs born, and how many survive to date. "Sheep have
LAMBINGS, not litters" (MCS-18) — the unit is the parturition event, and the useful ratio
is lambs-per-lambing (prolificacy) alongside survival.

SOURCE: the dam_id PEDIGREE is authoritative and cross-year — a ewe's offspring are every
sheep whose dam_id is her id (71 dams resolve this way). Offspring are grouped into lambings
by birth date (twins/triplets share a dob). lambing_records_2026 is a name-keyed event log
for one year and is NOT used as the spine (its dam field is a display name, not an id); it is
a candidate enrichment for born-vs-alive-at-birth, deliberately left out here rather than
matched by fuzzy name — a wrong dam match would corrupt a selection metric.

HONEST METRICS (stated, not overclaimed):
  - lambs_born        = offspring on record (a floor — an unrecorded lamb is invisible).
  - surviving_to_date = status alive | sold | gifted (left the farm alive or still here).
  - died              = status deceased (cause/age not always known — this is not a
                        weaning rate; true weaning needs weaning records this DB lacks).
  - unknown_status    = surfaced, never folded into survived or died.
  - lambings          = distinct birth dates among offspring; offspring with no dob are a
                        single flagged "undated" group (cannot be dated to a year).

    python3 scripts/ewe_productivity.py            # ledger, most-productive first
    python3 scripts/ewe_productivity.py --ewe gg   # one ewe, per-lambing detail
    python3 scripts/ewe_productivity.py --json
"""
import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "flock_database.json"

SURVIVING = {"alive", "sold", "gifted"}   # left the farm alive or still on it
DIED = {"deceased"}
CULLED = {"culled"}                        # a KNOWN management removal — not 'unknown'


def _year(dob):
    try:
        return datetime.strptime(str(dob), "%Y-%m-%d").year
    except (ValueError, TypeError):
        return None


def productivity(db):
    """One record per ewe that has offspring. Derived purely from dam_id links."""
    by_id = {s["id"]: s for s in db.get("sheep", [])}
    offspring = defaultdict(list)
    for s in db.get("sheep", []):
        dam = s.get("dam_id")
        if dam:
            offspring[dam].append(s)

    ledger = []
    for dam_id, kids in offspring.items():
        dam = by_id.get(dam_id)
        # group into lambings by exact dob; undated kids form one flagged group
        by_date = defaultdict(list)
        undated = []
        for k in kids:
            if k.get("dob"):
                by_date[k["dob"]].append(k)
            else:
                undated.append(k)
        lambings = []
        for dob in sorted(by_date):
            grp = by_date[dob]
            lambings.append({"date": dob, "year": _year(dob), "lambs": len(grp),
                             "lamb_ids": [k["id"] for k in grp]})
        if undated:
            lambings.append({"date": None, "year": None, "lambs": len(undated),
                             "lamb_ids": [k["id"] for k in undated], "undated": True})

        born = len(kids)
        surviving = sum(1 for k in kids if k.get("status") in SURVIVING)
        died = sum(1 for k in kids if k.get("status") in DIED)
        culled = sum(1 for k in kids if k.get("status") in CULLED)
        unknown = born - surviving - died - culled   # only genuinely-unknown outcomes
        n_lambings = len(lambings)
        flags = []
        if undated:
            flags.append(f"{len(undated)} offspring undated")
        if unknown:
            flags.append(f"{unknown} offspring status unknown")
        if dam is None:
            flags.append("dam_id does not resolve to a sheep record")
        elif dam.get("sex") == "ram":
            flags.append("dam_id resolves to a RAM — likely a mis-set parent link")

        ledger.append({
            "ewe_id": dam_id,
            "ewe_name": (dam or {}).get("name"),
            "status": (dam or {}).get("status"),
            "lambings": n_lambings,
            "lambs_born": born,
            "surviving_to_date": surviving,
            "died": died,
            "culled": culled,
            "unknown_status": unknown,
            "lambs_per_lambing": round(born / n_lambings, 2) if n_lambings else 0,
            "survival_pct": round(surviving / born * 100, 1) if born else None,
            "years": sorted({l["year"] for l in lambings if l["year"]}),
            "lambing_detail": lambings,
            "flags": flags,
        })
    # most productive first: surviving desc, then born, then prolificacy
    ledger.sort(key=lambda r: (-r["surviving_to_date"], -r["lambs_born"], -r["lambs_per_lambing"]))
    return ledger


def main():
    ap = argparse.ArgumentParser(description="Ewe lifetime productivity ledger (read-only)")
    ap.add_argument("--ewe", default=None, help="one ewe id, with per-lambing detail")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    db = json.loads(DB_PATH.read_text())
    ledger = productivity(db)

    if args.ewe:
        row = next((r for r in ledger if r["ewe_id"] == args.ewe), None)
        if row is None:
            print(f"ERROR: {args.ewe!r} has no offspring on record (or is not a dam)", file=sys.stderr)
            return 1
        ledger = [row]

    if args.json:
        print(json.dumps(ledger, indent=2))
        return 0

    if args.ewe:
        r = ledger[0]
        print(f"{r['ewe_name'] or r['ewe_id']} ({r['ewe_id']}) — {r['status']}")
        print(f"  {r['lambings']} lambings, {r['lambs_born']} lambs born, "
              f"{r['surviving_to_date']} surviving, {r['died']} died, {r['unknown_status']} unknown")
        print(f"  {r['lambs_per_lambing']} lambs/lambing"
              + (f", {r['survival_pct']:g}% surviving to date" if r["survival_pct"] is not None else ""))
        for l in r["lambing_detail"]:
            when = l["date"] or "undated"
            print(f"    {when}: {l['lambs']} lamb(s) — {', '.join(l['lamb_ids'])}")
        if r["flags"]:
            print("  flags: " + "; ".join(r["flags"]))
        return 0

    print(f"Ewe lifetime productivity — {len(ledger)} dams (dam_id pedigree)\n")
    print(f"  {'ewe':26} {'lmbg':>4} {'born':>4} {'surv':>4} {'died':>4} {'unk':>3} {'l/lm':>5}  years")
    for r in ledger:
        yrs = f"{min(r['years'])}-{max(r['years'])}" if r["years"] else "—"
        star = " *" if r["flags"] else ""
        print(f"  {(r['ewe_name'] or r['ewe_id'])[:26]:26} {r['lambings']:4} {r['lambs_born']:4} "
              f"{r['surviving_to_date']:4} {r['died']:4} {r['unknown_status']:3} {r['lambs_per_lambing']:5.2f}  {yrs}{star}")
    print("\n  surviving_to_date = alive|sold|gifted (NOT a formal weaning rate — this DB has no"
          "\n  weaning records). '*' = data-quality flag (undated offspring / unknown status).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
