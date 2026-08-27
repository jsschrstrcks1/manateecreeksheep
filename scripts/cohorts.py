#!/usr/bin/env python3
"""cohorts.py — group/cohort as a first-class asset with log-derived, time-aware membership (MCS-10).

A cohort is a named group of animals — today that means a PEN. The pen movement log (MCS-9) already
records every move; this makes membership a first-class, TIME-AWARE query on top of it: not just
"who is in Pen 4 now" but "who was in Pen 4 on 2026-04-15" — the question you need to answer "which
animals shared parasite exposure that season" or "who was together when this outbreak started".
Membership is DERIVED from the log, never stored twice, so it can never drift out of sync.

  - pen_as_of(sheep, as_of): the pen in effect at a date — the last dated pen_log entry on/before
    as_of, falling back to an undated baseline entry, then the legacy scalar pen. None if unknown.
  - cohort_membership(db, as_of): {pen: [sheep_ids]} for the living, on-property flock at as_of.
  - cohort_summary(db, as_of): per cohort — head count and sex composition.
  - transitions(db, since, until): every pen move in a window (the log made legible as events).

Read-only; composes the MCS-9 log, stores nothing.

    python3 scripts/cohorts.py                       # cohort summary, now
    python3 scripts/cohorts.py --as-of 2026-04-15     # membership as of a date (time-aware)
    python3 scripts/cohorts.py --roster "Pen 4"       # who is in one cohort
    python3 scripts/cohorts.py --json
"""
import argparse
import json
import sys
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "flock_database.json"


def _iso(d):
    try:
        return datetime.strptime(str(d), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def pen_as_of(sheep, as_of=None):
    """The pen in effect at as_of (default today), derived time-aware from pen_log. An undated
    log entry is a baseline (in effect from the beginning); dated entries on/before as_of override
    it, latest winning. Falls back to the legacy scalar `pen`. None if nothing is known."""
    as_of = as_of or date.today()
    log = sheep.get("pen_log") or []
    baseline = None
    best = None  # (date, pen)
    for e in log:
        if not isinstance(e, dict) or not e.get("pen"):
            continue
        raw = e.get("date")
        d = _iso(raw)
        if d is None:
            # a genuinely UNDATED entry (date is null/absent) is the baseline; a present-but-
            # UNPARSEABLE date is a data error and is SKIPPED, not silently promoted to baseline
            # (which would make the animal appear in that pen for all past --as-of queries).
            if raw in (None, ""):
                baseline = e["pen"]
            # else: bad date -> ignore this entry
        elif d <= as_of and (best is None or d >= best[0]):
            best = (d, e["pen"])
    if best is not None:
        return best[1]
    if baseline is not None:
        return baseline
    return sheep.get("pen")               # legacy scalar fallback


def cohort_membership(db, as_of=None):
    """{pen: [sheep_id,...]} for living, on-property animals at as_of. Animals with no known pen
    are grouped under '(unpenned)' rather than dropped."""
    groups = defaultdict(list)
    for s in db.get("sheep", []):
        if s.get("status") != "alive" or s.get("on_property") is False:
            continue
        pen = pen_as_of(s, as_of) or "(unpenned)"
        groups[pen].append(s["id"])
    return dict(groups)


def cohort_summary(db, as_of=None):
    members = cohort_membership(db, as_of)
    by_id = {s["id"]: s for s in db.get("sheep", [])}
    rows = []
    for pen, ids in members.items():
        sexes = defaultdict(int)
        for i in ids:
            sexes[by_id.get(i, {}).get("sex", "unknown")] += 1
        rows.append({"cohort": pen, "count": len(ids), "sexes": dict(sexes), "members": sorted(ids)})
    rows.sort(key=lambda r: (-r["count"], r["cohort"]))
    return rows


def transitions(db, since=None, until=None):
    """Every dated pen move in [since, until], as legible events. The log, surfaced."""
    out = []
    for s in db.get("sheep", []):
        for e in (s.get("pen_log") or []):
            if not isinstance(e, dict):
                continue
            d = _iso(e.get("date"))
            if d is None:
                continue
            if since and d < since:
                continue
            if until and d > until:
                continue
            out.append({"date": d.isoformat(), "sheep_id": s["id"], "pen": e.get("pen"),
                        "note": e.get("note")})
    out.sort(key=lambda x: (x["date"], x["sheep_id"]))
    return out


def main():
    ap = argparse.ArgumentParser(description="Cohort/group membership, time-aware (read-only)")
    ap.add_argument("--as-of", default=None)
    ap.add_argument("--roster", default=None, help="list one cohort's members")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    as_of = _iso(args.as_of) if args.as_of else None
    if args.as_of and as_of is None:
        print(f"ERROR: --as-of {args.as_of!r} is not an ISO date", file=sys.stderr); return 2
    db = json.loads(DB_PATH.read_text())
    when = (as_of or date.today()).isoformat()

    if args.roster:
        members = cohort_membership(db, as_of).get(args.roster, [])
        if args.json:
            print(json.dumps({"cohort": args.roster, "as_of": when, "members": sorted(members)}, indent=2)); return 0
        print(f"Cohort {args.roster!r} as of {when} — {len(members)} member(s)\n")
        for m in sorted(members):
            print(f"  {m}")
        return 0

    rows = cohort_summary(db, as_of)
    if args.json:
        print(json.dumps({"as_of": when, "cohorts": rows}, indent=2)); return 0
    total = sum(r["count"] for r in rows)
    print(f"Cohorts (log-derived, time-aware) as of {when} — {len(rows)} cohort(s), {total} animals\n")
    for r in rows:
        sx = ", ".join(f"{k}:{v}" for k, v in sorted(r["sexes"].items()))
        print(f"  {r['cohort']:16} {r['count']:3}  ({sx})")
    print("\n  Membership is DERIVED from the MCS-9 pen log — never stored twice, never drifts."
          "\n  --as-of DATE gives membership at any past date; --roster NAME lists one cohort.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
