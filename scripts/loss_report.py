#!/usr/bin/env python3
"""Documented-loss report (MCS-29): every deceased animal, what the records prove,
what an indemnity adjuster would still ask for. Derived — no third ledger.
Usage: python3 scripts/loss_report.py [--claim-ready-only]  Soli Deo Gloria."""
import argparse, json, os, sys
from pathlib import Path
_here = Path(__file__).parent
sys.path.insert(0, str(_here))
from lib.intake import loss_records

REPO = _here.parent
DB = Path(os.environ.get("FLOCK_DB_PATH") or REPO / "data" / "flock_database.json")
EV = Path(os.environ.get("HEALTH_LOG_PATH") or REPO / "data" / "health_events.jsonl")

ap = argparse.ArgumentParser()
ap.add_argument("--claim-ready-only", action="store_true")
args = ap.parse_args()
db = json.load(open(DB))
events = [json.loads(l) for l in EV.read_text().splitlines() if l.strip()] if EV.exists() else []
rows = loss_records(db, events)
ready = sum(1 for r in rows if r["claim_ready"])
for r in rows:
    if args.claim_ready_only and not r["claim_ready"]:
        continue
    flag = "READY " if r["claim_ready"] else "GAPS  "
    print(f"{flag} {r['animal_id']:30} {str(r['date'] or '?'):22} "
          f"{r['cause_source'] or 'cause UNKNOWN'}"
          + (f"  missing: {', '.join(r['missing'])}" if r["missing"] else ""))
print(f"\n({ready}/{len(rows)} deceased records claim-ready; the rest name their gaps — "
      f"suspect bulk-cleanup dates are already in the owner questionnaire)")
