#!/usr/bin/env python3
"""Emit the flock agenda. Default prints a table; --json writes data/agenda.json.
--today YYYY-MM-DD pins the clock (tests/replays). Reads flock_database.json (SSOT)
plus the typed health-event log (data/health_events.jsonl, MCS-26). Soli Deo Gloria."""
import argparse
import json
import os
import sys
from datetime import date

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)
from lib.flock_agenda import build_agenda, parse_date

REPO = os.path.dirname(_here)
DB = os.path.join(REPO, "data", "flock_database.json")
EVENTS = os.path.join(REPO, "data", "health_events.jsonl")
OUT = os.path.join(REPO, "data", "agenda.json")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--today", help="YYYY-MM-DD (default: real today)")
    ap.add_argument("--json", action="store_true", help="also write data/agenda.json")
    args = ap.parse_args()
    today = parse_date(args.today) if args.today else date.today()
    if args.today and not today:
        print(f"unparseable --today: {args.today}")
        sys.exit(2)
    with open(DB) as f:
        db = json.load(f)
    events = []
    if os.path.exists(EVENTS):
        with open(EVENTS) as f:
            events = [json.loads(l) for l in f if l.strip()]
    ag = build_agenda(db, today, events)
    print(f"Flock agenda for {ag['generated_for']} — "
          f"{ag['summary']['overdue']} overdue, "
          f"{ag['summary']['withdrawal_locks_active']} withdrawal locks, "
          f"{ag['summary']['unknown_withdrawals']} unknown-withdrawal flags\n")
    for i in ag["items"]:
        mark = "!!" if i["overdue"] else "  "
        print(f" {mark} {i['due']}  {i['type']:<24} {str(i.get('animal_id') or '-'):<22} {i['basis'][:90]}")
    if args.json:
        with open(OUT, "w") as f:
            json.dump(ag, f, indent=2)
        print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
