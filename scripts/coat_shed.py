#!/usr/bin/env python3
"""coat_shed.py — coat type + seasonal SHEDDING score as a structured trait (MCS-19).

Hair sheep earn their keep by shedding their winter coat cleanly on their own; a poor shedder
needs shearing (labor, cost) and carries a heritable FAULT worth selecting against. Right now
"coat" lives as a sentence in three records, and one of them literally says the coat type "can
only be confirmed after the first peak-summer shed (July-August 2026)" — the observation this
log exists to hold. This adds the structured, seasonal trait so shedding can be scored, trended,
and fed into breeding selection.

SHEDDING SCORE — a 0-5 convention (this tool's stated scale, tunable; aligns with the common
hair-sheep shedding score where higher = cleaner shed):
    0 = no shed — full winter coat retained
    1 = minimal — small patches only
    2 = partial — belly/neck shed, body coat retained
    3 = moderate — over half shed
    4 = mostly shed — small retained patches (britch/topline)
    5 = complete, clean shed
Assessed in the PEAK window (default June 1 - Aug 31): a hair animal that has NOT cleanly shed by
then is the one to flag. A single low score in April means little; a low score in July is a fault.

SHAPE — append-only shed_scores[] (same discipline as the MCS-9 pen log), each:
    {date, score, region_notes, coat_type, observer, notes}

  - coat_classify(text): read-only interpretation of the free-text coat_observed field into
    hair | wool | intermediate | unknown, shown WITH the source text — makes the 3 existing coat
    observations countable without discarding the prose.
  - record_shed_score(): append-only writer (pure addition).
  - validate_shed(): score-range/date/schema checks.
  - selection_view(): per hair/intermediate animal, the latest PEAK-season shed score and a
    poor-shedder flag; animals with no peak score are surfaced as a collection gap, never scored 0.

    python3 scripts/coat_shed.py                 # coat-type census + shedding selection view
    python3 scripts/coat_shed.py --year 2026     # peak-window shed scores for a given year
    python3 scripts/coat_shed.py --json
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "flock_database.json"

SHED_MIN, SHED_MAX = 0, 5
POOR_SHEDDER_MAX = 2          # <=2 in the peak window is a poor shed (tunable)
PEAK_START = (6, 1)          # Jun 1
PEAK_END = (8, 31)          # Aug 31
_SHED_KEYS = {"date", "score", "region_notes", "coat_type", "observer", "notes"}


def _iso(d):
    try:
        return datetime.strptime(str(d), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def _in_peak(d):
    return d is not None and (PEAK_START <= (d.month, d.day) <= PEAK_END)


def coat_classify(text):
    """Read-only interpretation of a free-text coat description into a canonical type.
    Returns (type, matched_reason). Order matters: 'intermediate' and 'wool-leaning' win over a
    bare 'wool'/'hair' substring so 'intermediate-to-wool-leaning' is not mislabeled pure wool."""
    s = str(text or "").lower()
    if not s:
        return ("unknown", "no coat observation")
    if "intermediate" in s or ("wool" in s and "hair" in s) or "leaning" in s:
        return ("intermediate", "mixed/intermediate wording")
    if "wool" in s:
        return ("wool", "'wool'")
    if "hair" in s:
        return ("hair", "'hair'")
    return ("unknown", "unrecognized coat wording")


def record_shed_score(sheep, date, score, region_notes=None, coat_type=None, observer=None, notes=None):
    """Append a seasonal shedding score (pure addition, append-only)."""
    ev = {"date": date, "score": score, "region_notes": region_notes,
          "coat_type": coat_type, "observer": observer, "notes": notes}
    ev = {k: v for k, v in ev.items() if v is not None}
    sheep.setdefault("shed_scores", []).append(ev)
    return ev


def validate_shed(sheep):
    issues = []
    for i, e in enumerate(sheep.get("shed_scores") or []):
        where = f"{sheep.get('id')}#shed_scores[{i}]"
        if not isinstance(e, dict):
            issues.append(f"{where}: not an object"); continue
        extra = set(e) - _SHED_KEYS
        if extra:
            issues.append(f"{where}: unknown key(s) {sorted(extra)}")
        if _iso(e.get("date")) is None:
            issues.append(f"{where}: missing/unparseable date {e.get('date')!r}")
        sc = e.get("score")
        if not isinstance(sc, (int, float)) or isinstance(sc, bool) or not (SHED_MIN <= sc <= SHED_MAX):
            issues.append(f"{where}: score {sc!r} out of range {SHED_MIN}-{SHED_MAX}")
    return issues


def _latest_peak_score(sheep, year=None):
    """The most recent peak-window (summer) shed score, optionally within one year. None if the
    animal has no peak-season score — a GAP, never silently treated as 0."""
    best = None
    for e in (sheep.get("shed_scores") or []):
        if not isinstance(e, dict):
            continue
        d = _iso(e.get("date"))
        sc = e.get("score")
        if not _in_peak(d) or not isinstance(sc, (int, float)) or isinstance(sc, bool):
            continue
        if year is not None and d.year != year:
            continue
        if best is None or d > best[0]:
            best = (d, sc)
    return best


def selection_view(db, year=None):
    """Per hair/intermediate on-property animal: coat type, latest peak shed score, poor-shedder
    flag, or a 'no peak score' gap. Wool animals are excluded (shedding does not apply)."""
    rows = []
    for s in db.get("sheep", []):
        if s.get("status") != "alive" or s.get("on_property") is False:
            continue
        ctype, _ = coat_classify(s.get("coat_observed"))
        # include hair/intermediate/unknown (a hair breed with no coat note still owes a shed obs);
        # exclude only confirmed wool.
        if ctype == "wool":
            continue
        peak = _latest_peak_score(s, year)
        if peak is None:
            rows.append({"id": s["id"], "name": s.get("name"), "coat_type": ctype,
                         "peak_score": None, "flag": "no peak-season shed score on record"})
        else:
            d, sc = peak
            rows.append({"id": s["id"], "name": s.get("name"), "coat_type": ctype,
                         "peak_score": sc, "peak_date": d.isoformat(),
                         "flag": "POOR SHEDDER" if sc <= POOR_SHEDDER_MAX else None})
    rows.sort(key=lambda r: (r["peak_score"] is not None, r["peak_score"] if r["peak_score"] is not None else 99))
    return rows


def main():
    ap = argparse.ArgumentParser(description="Coat type + seasonal shedding trait (read-only surfaces)")
    ap.add_argument("--year", type=int, default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    db = json.loads(DB_PATH.read_text())

    from collections import Counter
    coat_counts = Counter()
    observed = []
    for s in db["sheep"]:
        if s.get("coat_observed"):
            ctype, _ = coat_classify(s["coat_observed"])
            coat_counts[ctype] += 1
            observed.append({"id": s["id"], "coat_type": ctype, "text": s["coat_observed"]})
    view = selection_view(db, args.year)
    issues = []
    for s in db["sheep"]:
        issues += validate_shed(s)

    if args.json:
        print(json.dumps({"coat_observations": observed, "selection_view": view,
                          "validation_issues": issues}, indent=2)); return 0

    print(f"Coat type — {len(observed)} free-text observation(s) classified "
          f"({', '.join(f'{k}={v}' for k, v in coat_counts.most_common()) or 'none'})")
    for o in observed:
        print(f"  {o['coat_type']:12} {o['id']:26} {o['text'][:60]!r}")

    scored = [r for r in view if r["peak_score"] is not None]
    poor = [r for r in view if r.get("flag") == "POOR SHEDDER"]
    gaps = [r for r in view if r["peak_score"] is None]
    print(f"\nShedding selection view — {len(view)} hair/intermediate animals, "
          f"{len(scored)} peak-scored, {len(poor)} poor shedder(s), {len(gaps)} awaiting a peak-season score")
    for r in scored:
        fl = f"  <- {r['flag']}" if r.get("flag") else ""
        print(f"  score {r['peak_score']}  {(r['name'] or r['id'])[:28]:28} ({r['coat_type']}){fl}")
    if gaps:
        print(f"\n  {len(gaps)} animal(s) have no peak-season (Jun-Aug) shed score yet — the July-August"
              "\n  window is when a hair animal's shed is judged. Record with record_shed_score().")
    if issues:
        print(f"\nValidation issues ({len(issues)}):")
        for i in issues:
            print(f"  {i}")
    print("\n  Read-only. Score 0-5 (higher = cleaner shed); a low score in the PEAK window is the"
          "\n  fault to select against. Append-only writer is record_shed_score(). Operator decides.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
