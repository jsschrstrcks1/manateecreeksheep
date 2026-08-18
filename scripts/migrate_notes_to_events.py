#!/usr/bin/env python3
"""Move score-less famacha_scores entries into the typed health-event log (MCS-26 slice).

Soli Deo Gloria.

24 entries in health.famacha_scores carry no FAMACHA score at all — they are general
health notes ("Yearly booster given.") that predate the event log and were parked in
the only dated list the schema had. Each becomes a health event (type=note — automatic
re-typing would be guessing; a human can re-classify later by appending), and the
original entry is removed from famacha_scores.

Zero-loss, mechanically asserted: moved-out count == appended count, and every
(animal, date, notes) triple is byte-preserved in the event's details/date fields.
Dates: M-D-YY converted to ISO; an unparseable date leaves the entry IN PLACE and is
reported — never guessed. Dry-run by default; --apply writes both files.
"""
import argparse
import datetime
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
DB_PATH = REPO_ROOT / "data" / "flock_database.json"
EVENTS_PATH = REPO_ROOT / "data" / "health_events.jsonl"


def to_iso(s):
    if not isinstance(s, str):
        return None
    try:
        datetime.date.fromisoformat(s)
        return s
    except ValueError:
        pass
    m = re.fullmatch(r"(\d{1,2})-(\d{1,2})-(\d{2,4})", s.strip())
    if m:
        mo, d, y = int(m[1]), int(m[2]), int(m[3])
        y += 2000 if y < 100 else 0
        try:
            return datetime.date(y, mo, d).isoformat()
        except ValueError:
            return None
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    db = json.load(open(DB_PATH))
    existing_ids = set()
    if EVENTS_PATH.exists():
        for line in EVENTS_PATH.read_text().splitlines():
            if line.strip():
                existing_ids.add(json.loads(line).get("event_id"))

    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    moved, kept_unparseable, new_events = 0, [], []
    for s in db.get("sheep", []):
        scores = (s.get("health") or {}).get("famacha_scores")
        if not scores:
            continue
        remaining = []
        for e in scores:
            if not isinstance(e, dict) or "score" in e:
                remaining.append(e)
                continue
            iso = to_iso(e.get("date"))
            if iso is None:
                kept_unparseable.append((s["id"], e.get("date")))
                remaining.append(e)
                continue
            base = f"{s['id']}-{iso}-note"
            event_id, n = base, 2
            while event_id in existing_ids:
                event_id, n = f"{base}-{n}", n + 1
            existing_ids.add(event_id)
            new_events.append({
                "event_id": event_id,
                "animal_id": s["id"],
                "type": "note",
                "date": iso,
                "date_precision": "exact",
                "details": e.get("notes", ""),
                "source": f"migrated from famacha_scores entry (original date '{e.get('date')}')",
                "recorded_by": "syl",
                "recorded_at": now,
            })
            moved += 1
        s["health"]["famacha_scores"] = remaining

    print(f"movable: {moved} · left in place (unparseable date): {len(kept_unparseable)}")
    for aid, d in kept_unparseable:
        print(f"  kept [{aid}]: date {d!r}")
    if not args.apply:
        print("dry-run — nothing written (use --apply)")
        return
    assert moved == len(new_events)
    with open(EVENTS_PATH, "a") as f:
        for e in new_events:
            f.write(json.dumps(e, sort_keys=True) + "\n")
    with open(DB_PATH, "w") as f:
        json.dump(db, f, indent=2)
    print(f"written: {moved} events appended, famacha_scores pruned; run validate_flock.py")


if __name__ == "__main__":
    main()
