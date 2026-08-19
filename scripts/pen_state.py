#!/usr/bin/env python3
"""pen_state.py — pen as an append-only movement log; current pen DERIVED (MCS-9).

WHY (farm reality): animals move between pens over time, and WHEN they moved matters —
breeding-exposure windows (which ram was in the pen when), and pen-level parasite management.
The legacy model stored only a mutable scalar `sheep['pen']`: the current pen, with no history.
A move overwrote the past.

WHAT: this introduces `sheep['pen_log']`, an append-only list of moves
    [{date, pen, note?, source?}, ...]
and keeps `sheep['pen']` as a DERIVED CACHE equal to the last logged pen — so the ~8 existing
consumers that read `sheep['pen']` (ebv/*, run_annual_eval, breeding_projector, export_to_sheets,
apply_card_update) are UNCHANGED. Every future move should go through `record_move` so it is
dated and preserved; the validator (validate_flock.py) checks the cache still equals the log.

HONEST SCOPE: there is no historical move data in the database today, so the seed writes ONE
dateless entry per penned animal (its current pen). The value is forward-looking — moves from
here on are captured. This does not fabricate a history that was never recorded.

    python scripts/pen_state.py --seed            # dry-run: show what would be seeded
    python scripts/pen_state.py --seed --apply     # write pen_log seeds
"""
import json
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "flock_database.json"


def current_pen(sheep):
    """The animal's current pen, DERIVED from the append-only log (last entry with a pen).
    Falls back to the legacy scalar for a record not yet seeded."""
    for entry in reversed(sheep.get("pen_log") or []):
        if isinstance(entry, dict) and entry.get("pen"):
            return entry["pen"]
    return sheep.get("pen")


def record_move(sheep, pen, date=None, note=None, source=None):
    """Append a dated move and refresh the derived `pen` cache. Returns True if a move was
    recorded, False for a no-op (already in `pen`). A move to the SAME pen is not logged —
    the log is moves, not check-ins. Callers that set a pen (e.g. apply_card_update) should
    route through here so the move is dated and preserved instead of overwriting the past."""
    log = sheep.setdefault("pen_log", [])
    if current_pen(sheep) == pen and log:
        sheep["pen"] = pen
        return False
    entry = {"date": date, "pen": pen}
    if note:
        entry["note"] = note
    if source:
        entry["source"] = source
    log.append(entry)
    sheep["pen"] = pen  # derived cache stays in lock-step with the log
    return True


def seed_from_scalar(sheep):
    """Initialize pen_log from the legacy scalar `pen` (one entry) when absent. Dated from
    status_date where available, else null (unknown — not invented). Returns True if seeded."""
    if "pen_log" in sheep:
        return False
    pen = sheep.get("pen")
    if not pen:
        return False
    sheep["pen_log"] = [{
        "date": sheep.get("status_date"),
        "pen": pen,
        "note": "seeded from legacy scalar pen (pre-log history not recorded)",
    }]
    return True


def _seed_all(apply):
    db = json.loads(DB_PATH.read_text())
    seeded = 0
    already = 0
    no_pen = 0
    for s in db["sheep"]:
        if "pen_log" in s:
            already += 1
            continue
        if not s.get("pen"):
            no_pen += 1
            continue
        # dry-run: seed a copy to count; apply: seed in place
        if seed_from_scalar(s):
            seeded += 1
    # LOSSLESS invariant: every penned animal's current pen is unchanged by seeding.
    mismatch = [s["id"] for s in db["sheep"] if s.get("pen") and current_pen(s) != s.get("pen")]
    print("pen_log seed —", "APPLY" if apply else "DRY-RUN")
    print(f"  penned animals seeded:      {seeded}")
    print(f"  already had a pen_log:      {already}")
    print(f"  no pen (nothing to seed):   {no_pen}")
    print(f"  derived-vs-scalar mismatch: {len(mismatch)} {mismatch[:5]}")
    if mismatch:
        print("\n  REFUSING — seeding must not change any current pen.")
        return 2
    if apply:
        DB_PATH.write_text(json.dumps(db, indent=2, ensure_ascii=True) + "\n")
        print(f"\n  WROTE {DB_PATH} — pen_log seeded; sheep['pen'] unchanged (now a derived cache).")
    else:
        print("\n  Dry-run only — nothing written. Re-run with --seed --apply to write.")
    return 0


def main(argv):
    if "--seed" in argv:
        return _seed_all("--apply" in argv)
    print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
