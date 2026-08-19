#!/usr/bin/env python3
"""One-time, idempotent migration: seed each sheep's movement log from the scalar `pen`.

MCS-9 lift (see docs/UPGRADE-LEDGER.md and scripts/lib/pen_history.py). Before this, an
animal's pen lived in TWO independently-authored places — `sheep["pen"]` (scalar) and the
`pens{}` rosters — which could drift. Measured 2026-08-12: they were 100% consistent (51
placed sheep, 0 disagreements, no phantom ids), so we can seed the append-only log from the
scalar field without reconciliation guesswork.

What it does, per sheep:
  - If it already has a `movements` list -> leave it ALONE (idempotent; re-running is safe).
  - Else if it has a scalar `pen` -> seed ONE movement: from null -> that pen, an
    "initial placement" whose date is null (we do not know WHEN it entered; inventing a
    date would be exactly the clever-not-careful shortcut this household forbids).
  - Else -> give it an empty `movements: []` so every record has the field uniformly.
  - Finally, re-derive the scalar `pen` from the log so the mirror is guaranteed consistent.

Dry-run by default; pass --apply to write. Soli Deo Gloria.
"""
import argparse
import json
import os
import sys

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)
from lib.pen_history import current_pen  # noqa: E402

DB_PATH = os.path.join(_here, "..", "data", "flock_database.json")

SEED_SOURCE = (
    "migrated 2026-08-12: seeded from scalar pen field "
    "(measured consistent with pens{} rosters — 51 placed, 0 disagreements)"
)
SEED_REASON = "initial placement (migrated snapshot; real entry date unknown)"


def seed(db):
    """Mutate db in place. Return counts (seeded, already_had_log, empty)."""
    seeded = already = empty = 0
    for s in db.get("sheep", []):
        if isinstance(s.get("movements"), list):
            already += 1
        else:
            p = s.get("pen")
            if p:
                s["movements"] = [{
                    "date": None,
                    "from": None,
                    "to": p,
                    "reason": SEED_REASON,
                    "source": SEED_SOURCE,
                }]
                seeded += 1
            else:
                s["movements"] = []
                empty += 1
        # Mirror the scalar from the log so the two can never disagree post-migration.
        s["pen"] = current_pen(s)
    return seeded, already, empty


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Write changes (default: dry-run)")
    args = parser.parse_args()

    with open(DB_PATH) as f:
        db = json.load(f)

    seeded, already, empty = seed(db)
    print(f"Sheep: {len(db.get('sheep', []))}")
    print(f"  seeded new movement log:      {seeded}")
    print(f"  already had a log (skipped):  {already}")
    print(f"  no pen -> empty log:          {empty}")

    if not args.apply:
        print("\n[dry-run] No file written. Re-run with --apply to persist.")
        return

    # indent=2, ensure_ascii default True — matches build_database.py and the file's
    # dominant convention (non-ASCII stored as \uXXXX escapes). A migration must change only
    # what it intends (the movement logs); this keeps the diff to the added logs plus one
    # stray literal em-dash normalised into the file's own escape convention.
    with open(DB_PATH, "w") as f:
        json.dump(db, f, indent=2)
    print(f"\nWrote {DB_PATH}")


if __name__ == "__main__":
    main()
