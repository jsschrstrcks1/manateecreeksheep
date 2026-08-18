#!/usr/bin/env python3
"""Normalize FAMACHA entry keys in data/flock_database.json (mcs-famacha-schema-normalization).

Soli Deo Gloria.

The problem (measured 2026-08-18, superset of the audit's 91/16 snapshot):
  health.famacha_scores entries split across key spellings — 89 use `famacha`,
  16 use `score`, 24 have neither (they are general health notes that predate a
  health-event log; left alone here, surfaced by validate_flock's hygiene report).
  health.famacha_history has 9 entries using `note` beside 273 using `notes`.
  Dual-key data means any consumer that reads one spelling silently drops the
  other — the agenda-engine plan had to be patched to dual-read for exactly this.

Canonical spellings, chosen to match the majority convention ACROSS structures:
  score value key: `score`   (famacha_history's convention, 282 entries)
  note text key:   `notes`

What this script does — and all it does:
  famacha_scores:  rename key `famacha` -> `score` (value untouched)
  famacha_history: rename key `note`    -> `notes` (value untouched)
  An entry carrying BOTH spellings is never merged silently: it aborts with the
  record id so a human can decide which value is true.

Dry-run by default; --apply writes. Idempotent: a second run finds 0 renames.
Zero-loss is asserted mechanically: entry counts and the multiset of
(date, value) pairs must be identical before and after, or the script aborts
without writing.
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
DB_PATH = REPO_ROOT / "data" / "flock_database.json"


def famacha_fingerprint(db):
    """Multiset of every FAMACHA-bearing datum, key-spelling-blind."""
    fp = Counter()
    for s in db.get("sheep", []):
        h = s.get("health") or {}
        for e in h.get("famacha_scores") or []:
            val = e.get("score", e.get("famacha"))
            fp[("scores", s.get("id"), e.get("date"), repr(val), repr(e.get("notes")))] += 1
        for e in h.get("famacha_history") or []:
            if isinstance(e, dict):
                fp[("history", s.get("id"), e.get("date"), repr(e.get("score")),
                    repr(e.get("notes", e.get("note"))), repr(e.get("source")))] += 1
    return fp


def migrate(db):
    renamed_scores = renamed_notes = 0
    for s in db.get("sheep", []):
        h = s.get("health") or {}
        for e in h.get("famacha_scores") or []:
            if "famacha" in e:
                if "score" in e:
                    sys.exit(f"ABORT [{s.get('id')}]: famacha_scores entry carries BOTH "
                             f"'famacha' and 'score' ({e!r}) — human decision needed, nothing written.")
                e["score"] = e.pop("famacha")
                renamed_scores += 1
        for e in h.get("famacha_history") or []:
            if isinstance(e, dict) and "note" in e:
                if "notes" in e:
                    sys.exit(f"ABORT [{s.get('id')}]: famacha_history entry carries BOTH "
                             f"'note' and 'notes' ({e!r}) — human decision needed, nothing written.")
                e["notes"] = e.pop("note")
                renamed_notes += 1
    return renamed_scores, renamed_notes


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--apply", action="store_true", help="write the migration (default: dry-run)")
    args = ap.parse_args()

    db = json.load(open(DB_PATH))
    before = famacha_fingerprint(db)
    renamed_scores, renamed_notes = migrate(db)
    after = famacha_fingerprint(db)

    if before != after:
        gained = after - before
        lost = before - after
        sys.exit(f"ABORT: fingerprint changed — lost={list(lost)[:3]} gained={list(gained)[:3]}. "
                 f"Nothing written.")

    print(f"famacha_scores:  {renamed_scores} 'famacha' -> 'score' renames")
    print(f"famacha_history: {renamed_notes} 'note' -> 'notes' renames")
    print(f"fingerprint: {sum(before.values())} FAMACHA-bearing entries, identical before/after")

    if not args.apply:
        print("dry-run — nothing written (use --apply)")
        return
    if renamed_scores == 0 and renamed_notes == 0:
        print("already normalized — nothing to write")
        return
    with open(DB_PATH, "w") as f:
        json.dump(db, f, indent=2)
    print(f"written: {DB_PATH}")


if __name__ == "__main__":
    main()
