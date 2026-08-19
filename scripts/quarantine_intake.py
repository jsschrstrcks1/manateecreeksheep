#!/usr/bin/env python3
"""quarantine_intake.py — intake quarantine & biosecurity records (MCS-28). READ-ONLY surfaces.

Biosecurity is cheapest at the gate. A new arrival can carry anthelmintic-resistant worms that,
once loose in the flock, never leave — so best practice is a QUARANTINE DRENCH (a novel drug class
to kill what the animal brought), ISOLATION for an observation period, and a FEC at intake before
the animal joins the resident flock. Today that discipline lives nowhere structured. This adds the
intake record and flags where the biosecurity steps are undocumented.

SHAPE — append-only quarantine_intakes[] (MCS-9 shape), one per arrival:
    {arrival_date, source, quarantine_pen, drench_drug, drench_date, fec_at_intake,
     observation_days, release_date, cleared, notes}

Biosecurity checklist (what a complete intake documents; tunable):
    - a quarantine drench recorded (drug + date)
    - a FEC at intake (so a resistant-worm arrival is caught, not spread)
    - an isolation/observation period before release
A recorded arrival missing these is surfaced as a GAP, not assumed compliant.

    python3 scripts/quarantine_intake.py                 # intake status + biosecurity gaps
    python3 scripts/quarantine_intake.py --json
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "flock_database.json"

_KEYS = {"arrival_date", "source", "quarantine_pen", "drench_drug", "drench_date",
         "fec_at_intake", "observation_days", "release_date", "cleared", "notes"}


def _iso(d):
    try:
        return datetime.strptime(str(d), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def record_intake(sheep, arrival_date, source=None, quarantine_pen=None, drench_drug=None,
                  drench_date=None, fec_at_intake=None, observation_days=None,
                  release_date=None, cleared=None, notes=None):
    """Append a quarantine intake record (pure addition, append-only)."""
    rec = {"arrival_date": arrival_date, "source": source, "quarantine_pen": quarantine_pen,
           "drench_drug": drench_drug, "drench_date": drench_date, "fec_at_intake": fec_at_intake,
           "observation_days": observation_days, "release_date": release_date,
           "cleared": cleared, "notes": notes}
    rec = {k: v for k, v in rec.items() if v is not None}
    sheep.setdefault("quarantine_intakes", []).append(rec)
    return rec


def validate_intake(sheep):
    issues = []
    for i, e in enumerate(sheep.get("quarantine_intakes") or []):
        where = f"{sheep.get('id')}#quarantine_intakes[{i}]"
        if not isinstance(e, dict):
            issues.append(f"{where}: not an object"); continue
        extra = set(e) - _KEYS
        if extra:
            issues.append(f"{where}: unknown key(s) {sorted(extra)}")
        if _iso(e.get("arrival_date")) is None:
            issues.append(f"{where}: missing/unparseable arrival_date {e.get('arrival_date')!r}")
        for df in ("drench_date", "release_date"):
            if e.get(df) is not None and _iso(e.get(df)) is None:
                issues.append(f"{where}: {df} {e.get(df)!r} unparseable")
        if e.get("cleared") is not None and not isinstance(e.get("cleared"), bool):
            issues.append(f"{where}: cleared {e.get('cleared')!r} is not a boolean")
        fec = e.get("fec_at_intake")
        if fec is not None and (not isinstance(fec, (int, float)) or isinstance(fec, bool) or fec < 0):
            issues.append(f"{where}: fec_at_intake {fec!r} not a non-negative number")
        rd, ad = _iso(e.get("release_date")), _iso(e.get("arrival_date"))
        if rd and ad and rd < ad:
            issues.append(f"{where}: release_date {rd} precedes arrival_date {ad}")
    return issues


def _checklist_gaps(rec):
    gaps = []
    if not rec.get("drench_drug"):
        gaps.append("no quarantine drench recorded")
    if rec.get("fec_at_intake") is None:
        gaps.append("no intake FEC")
    if not rec.get("release_date") and rec.get("observation_days") is None:
        gaps.append("no observation period / release")
    return gaps


def biosecurity_view(db):
    """Per animal with a quarantine record OR arrival/acquisition provenance: intake status and the
    biosecurity steps still undocumented. A recorded arrival with no quarantine record is itself a
    gap (arrived, biosecurity unlogged) — never assumed compliant."""
    rows = []
    for s in db.get("sheep", []):
        intakes = s.get("quarantine_intakes") or []
        has_provenance = bool(s.get("arrival_date") or s.get("physical_arrival_date")
                              or s.get("acquisition") or s.get("breeder_provenance"))
        if not intakes and not has_provenance:
            continue
        if intakes:
            latest = intakes[-1]
            in_q = not latest.get("cleared") and not latest.get("release_date")
            rows.append({"id": s["id"], "name": s.get("name"),
                         "status": "in_quarantine" if in_q else "cleared",
                         "arrival_date": latest.get("arrival_date"),
                         "source": latest.get("source"),
                         "gaps": _checklist_gaps(latest)})
        else:
            rows.append({"id": s["id"], "name": s.get("name"), "status": "arrival_unlogged",
                         "arrival_date": s.get("arrival_date") or s.get("physical_arrival_date"),
                         "source": s.get("source"),
                         "gaps": ["arrival on record but no quarantine intake documented"]})
    rows.sort(key=lambda r: (r["status"] != "in_quarantine", r["id"]))
    return rows


def main():
    ap = argparse.ArgumentParser(description="Intake quarantine & biosecurity records (read-only)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    db = json.loads(DB_PATH.read_text())
    rows = biosecurity_view(db)
    issues = []
    for s in db["sheep"]:
        issues += validate_intake(s)
    if args.json:
        print(json.dumps({"intake": rows, "validation_issues": issues}, indent=2)); return 0

    in_q = [r for r in rows if r["status"] == "in_quarantine"]
    unlogged = [r for r in rows if r["status"] == "arrival_unlogged"]
    print(f"Quarantine & biosecurity — {len(rows)} animals with an intake record or arrival "
          f"provenance; {len(in_q)} in quarantine, {len(unlogged)} arrival(s) with no intake logged\n")
    for r in rows:
        g = ("  <- " + "; ".join(r["gaps"])) if r["gaps"] else ""
        print(f"  [{r['status']:16}] {(r['name'] or r['id'])[:26]:26} arrived {str(r['arrival_date'] or '—'):12}{g}")
    if issues:
        print(f"\nValidation issues ({len(issues)}):")
        for i in issues:
            print(f"  {i}")
    print("\n  Read-only. A complete intake documents a quarantine drench (novel class), an intake FEC,"
          "\n  and an isolation period. Append-only writer is record_intake(). Operator decides.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
