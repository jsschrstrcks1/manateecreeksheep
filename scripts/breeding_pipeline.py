#!/usr/bin/env python3
"""Breeding pipeline CLI (MCS-17): record matings, see the derived cycle.

Usage:
  python3 scripts/breeding_pipeline.py add --ewe <id> --ram <id> \
      --exposure-start YYYY-MM-DD [--exposure-end YYYY-MM-DD] [--notes "..."] \
      --source "owner statement ..." --recorded-by <who>
  python3 scripts/breeding_pipeline.py list [--status exposed|confirmed|lambed|failed|closed]
  python3 scripts/breeding_pipeline.py set-status --mating-id <id> --status <s> [--notes "..."]

One row per mating; everything downstream (preg check, due window, lambing watch,
wean, rebreed) is DERIVED — see scripts/lib/breeding.py. Rows are never deleted;
a wrong row gets status=closed + a note. Soli Deo Gloria.
"""
import argparse
import datetime
import json
import os
import sys
from pathlib import Path

_here = Path(__file__).parent
sys.path.insert(0, str(_here))
from lib.breeding import VALID_STATUS, derived_status, mating_windows, validate_matings  # noqa: E402

REPO = _here.parent
DB_PATH = Path(os.environ.get("FLOCK_DB_PATH") or REPO / "data" / "flock_database.json")
EVENTS_PATH = Path(os.environ.get("HEALTH_LOG_PATH") or REPO / "data" / "health_events.jsonl")


def load():
    db = json.load(open(DB_PATH))
    events = []
    if EVENTS_PATH.exists():
        events = [json.loads(l) for l in EVENTS_PATH.read_text().splitlines() if l.strip()]
    return db, events


def save(db):
    issues = validate_matings(db)
    if issues:
        for i in issues:
            print(i)
        sys.exit("REFUSED: matings table would be invalid — nothing written.")
    with open(DB_PATH, "w") as f:
        json.dump(db, f, indent=2)


def cmd_add(args):
    db, _ = load()
    matings = db.setdefault("matings", [])
    base = f"{args.ewe}-x-{args.ram}-{args.exposure_start}"
    mid, n = base, 2
    while any(m.get("mating_id") == mid for m in matings):
        mid, n = f"{base}-{n}", n + 1
    row = {
        "mating_id": mid, "ewe_id": args.ewe, "ram_id": args.ram,
        "exposure_start": args.exposure_start,
        "exposure_end": args.exposure_end or args.exposure_start,
        "status": "exposed",
        "source": args.source, "recorded_by": args.recorded_by,
        "recorded_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    if args.notes:
        row["notes"] = args.notes
    matings.append(row)
    save(db)
    w = mating_windows(row)
    print(f"added {mid}")
    print(f"  preg check: {w['preg_check'][0]}..{w['preg_check'][1]}")
    print(f"  due window: {w['due'][0]}..{w['due'][1]}")


def cmd_list(args):
    db, events = load()
    rows = db.get("matings") or []
    for m in rows:
        st = derived_status(m, events)
        if args.status and st != args.status:
            continue
        w = mating_windows(m)
        due = f"due {w['due'][0]}..{w['due'][1]}" if w else "DATES UNPARSEABLE"
        print(f"{m['mating_id']:44} {st:10} {due}")
    print(f"({len(rows)} matings)")


def cmd_set_status(args):
    db, _ = load()
    for m in db.get("matings") or []:
        if m.get("mating_id") == args.mating_id:
            if args.status not in VALID_STATUS:
                sys.exit(f"REFUSED: status must be one of {VALID_STATUS}")
            m["status"] = args.status
            if args.notes:
                m["notes"] = (m.get("notes", "") + " | " if m.get("notes") else "") + args.notes
            save(db)
            print(f"{args.mating_id} -> {args.status}")
            return
    sys.exit(f"REFUSED: mating_id '{args.mating_id}' not found")


def main():
    ap = argparse.ArgumentParser(description="Breeding pipeline (MCS-17)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add")
    a.add_argument("--ewe", required=True)
    a.add_argument("--ram", required=True)
    a.add_argument("--exposure-start", required=True, dest="exposure_start")
    a.add_argument("--exposure-end", dest="exposure_end")
    a.add_argument("--notes")
    a.add_argument("--source", required=True)
    a.add_argument("--recorded-by", required=True, dest="recorded_by")
    a.set_defaults(fn=cmd_add)
    l = sub.add_parser("list")
    l.add_argument("--status")
    l.set_defaults(fn=cmd_list)
    s = sub.add_parser("set-status")
    s.add_argument("--mating-id", required=True, dest="mating_id")
    s.add_argument("--status", required=True)
    s.add_argument("--notes")
    s.set_defaults(fn=cmd_set_status)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
