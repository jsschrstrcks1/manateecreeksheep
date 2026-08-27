#!/usr/bin/env python3
"""vaccination_check.py — CDT / clostridial vaccination compliance (MCS). READ-ONLY.

CDT (Clostridium perfringens C&D + tetanus) is the core sheep vaccine: it prevents enterotoxemia
("overeating disease") and tetanus, both of which kill quickly and are almost entirely preventable.
The protocol is well established: lambs get an initial two-dose series, and every animal needs an
ANNUAL booster; a bred ewe is boosted ~3-6 weeks pre-lambing so colostral immunity passes to the
lamb. This tool reads the 117 dated vaccination records and flags who is due — never a fabricated
schedule, just dates measured against tunable, standard intervals.

  - last_cdt(sheep, as_of): the most recent CDT/clostridial vaccination on/before a date.
  - compliance(db, as_of): per alive, on-property animal — current | booster_overdue | never, with
    days since the last dose. Animals with no CDT on record are the sharpest flag (no protection).

    python3 scripts/vaccination_check.py            # compliance worklist (overdue + never)
    python3 scripts/vaccination_check.py --as-of DATE --json
"""
import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "flock_database.json"

# strings that denote a CDT / clostridial vaccine (matched case-insensitively as substrings)
CDT_ALIASES = ("cdt", "cd&t", "cd t", "cd&amp;t", "covexin", "clostrid", "vision", "bar vac", "barvac")
ANNUAL_DAYS = 365        # a booster is due one year after the last dose (tunable)
GRACE_DAYS = 30          # a small grace before calling it overdue


def _iso(d):
    try:
        return datetime.strptime(str(d), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def _is_cdt(vaccine):
    s = str(vaccine or "").lower()
    return any(a in s for a in CDT_ALIASES)


def last_cdt(sheep, as_of=None):
    """The most recent CDT/clostridial vaccination date on/before as_of, or None."""
    as_of = as_of or date.today()
    best = None
    for v in (sheep.get("health", {}).get("vaccinations") or []):
        if not isinstance(v, dict) or not _is_cdt(v.get("vaccine")):
            continue
        d = _iso(v.get("date"))
        if d is None or d > as_of:
            continue
        if best is None or d > best:
            best = d
    return best


def _cdt_doses(sheep, as_of=None):
    """Count of distinct-dated CDT doses on/before as_of — to spot a lamb still owed its 2nd dose."""
    as_of = as_of or date.today()
    dates = set()
    for v in (sheep.get("health", {}).get("vaccinations") or []):
        if isinstance(v, dict) and _is_cdt(v.get("vaccine")):
            d = _iso(v.get("date"))
            if d and d <= as_of:
                dates.add(d)
    return len(dates)


def compliance(db, as_of=None):
    as_of = as_of or date.today()
    rows = []
    for s in db.get("sheep", []):
        if s.get("status") != "alive" or s.get("on_property") is False:
            continue
        last = last_cdt(s, as_of)
        if last is None:
            status, since = "never", None
        else:
            since = (as_of - last).days
            status = "booster_overdue" if since > ANNUAL_DAYS + GRACE_DAYS else "current"
        rows.append({"id": s["id"], "name": s.get("name"), "status": status,
                     "last_cdt": last.isoformat() if last else None, "days_since": since,
                     "doses_on_file": _cdt_doses(s, as_of)})
    order = {"never": 0, "booster_overdue": 1, "current": 2}
    rows.sort(key=lambda r: (order[r["status"]], -(r["days_since"] or 10**6)))
    return rows


def main():
    ap = argparse.ArgumentParser(description="CDT/clostridial vaccination compliance (read-only)")
    ap.add_argument("--as-of", default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    as_of = _iso(args.as_of) if args.as_of else date.today()
    if args.as_of and as_of is None:
        print(f"ERROR: --as-of {args.as_of!r} is not an ISO date", file=sys.stderr); return 2
    db = json.loads(DB_PATH.read_text())
    rows = compliance(db, as_of)
    if args.json:
        print(json.dumps({"as_of": as_of.isoformat(), "compliance": rows}, indent=2)); return 0

    never = [r for r in rows if r["status"] == "never"]
    overdue = [r for r in rows if r["status"] == "booster_overdue"]
    current = [r for r in rows if r["status"] == "current"]
    print(f"CDT / clostridial compliance — as of {as_of.isoformat()}: "
          f"{len(never)} never vaccinated, {len(overdue)} booster overdue, {len(current)} current\n")
    if never:
        print("NEVER on record (no clostridial protection — the sharpest flag):")
        for r in never:
            print(f"  {(r['name'] or r['id'])[:30]:30}")
    if overdue:
        print("\nBOOSTER OVERDUE (annual):")
        for r in overdue:
            yrs = r["days_since"] / 365.0
            print(f"  {(r['name'] or r['id'])[:30]:30} last {r['last_cdt']} ({yrs:.1f}y ago)")
    print("\n  Read-only advisory. Annual booster + lamb initial 2-dose series; boost bred ewes"
          "\n  ~3-6 weeks pre-lambing. Intervals are tunable standards. Operator/vet decides.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
