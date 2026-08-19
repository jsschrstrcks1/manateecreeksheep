#!/usr/bin/env python3
"""attention_triage.py — worst-first attention-priority triage with R/A/G status (MCS-3).

One list answering the farm question "who needs eyes first?": a composite of
  - the MCS-8 combined deworm advisory (scripts/deworm_decision.py — urgency + mismatch),
  - FAMACHA TREND (worsening between the last two dated scores adds attention;
    improvement never hides risk),
  - DAYS SINCE ANY CHECK (last dated FAMACHA / FEC / treatment / vaccination),
  - data-hygiene flags (alive-with-no-pen; [CONFLICT] scores awaiting notebook re-check).

COMPOSES, never duplicates: FAMACHA parsing, thresholds, and the decision matrix live in
deworm_decision/parasite_resistance — this module only ranks and colors. READ-ONLY.

R/A/G semantics (stated, tunable):
  RED   — known risk now: deworm urgency 3 (anemic / anemia-mismatch), or a worsening
          trend that has reached borderline-or-worse.
  AMBER — needs attention soon: urgency 1-2, checks stale beyond RECHECK_DAYS, a
          worsening trend still in the good band, unresolved [CONFLICT] rows, or an
          adult with no dated records at all (a first check is owed).
  GREEN — recent data, unremarkable signals. A YOUNG animal (< FIRST_CHECK_AGE_DAYS)
          with no records is GREEN with "first check due" noted — lambs are not
          delinquent for being new. (Tunable default, not husbandry law.)

    python3 scripts/attention_triage.py                # alive flock, worst-first
    python3 scripts/attention_triage.py --as-of DATE   # evaluate as of a date
    python3 scripts/attention_triage.py --json         # agenda-engine feed shape
"""
import argparse
import importlib.util
import json
import sys
from datetime import date, datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "flock_database.json"

RECHECK_DAYS = 45           # matches deworm_decision.STALE_DAYS — one staleness story
FIRST_CHECK_AGE_DAYS = 90   # a younger animal with no records is not delinquent (tunable)

_dd_spec = importlib.util.spec_from_file_location(
    "deworm_decision", str(Path(__file__).resolve().parent / "deworm_decision.py"))
dd = importlib.util.module_from_spec(_dd_spec)
_dd_spec.loader.exec_module(dd)


def _parse_iso(d):
    try:
        return datetime.strptime(str(d), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def famacha_trend(sheep, as_of=None):
    """Direction between the last two dated, parseable FAMACHA scores at/before as_of.
    Returns {'delta': float, 'from': s, 'to': s} (positive delta = WORSENING — higher
    FAMACHA is paler) or None with fewer than two points. A trend needs two real
    observations; [CONFLICT]-nulled rows do not count."""
    pts = []
    for e in (sheep.get("health", {}).get("famacha_scores") or []):
        if not isinstance(e, dict):
            continue
        val = dd.parse_famacha(e.get("score"))
        d = _parse_iso(e.get("date"))
        if val is None or d is None or (as_of and d > as_of):
            continue
        pts.append((d, val))
    if len(pts) < 2:
        return None
    pts.sort()
    (_, prev), (_, last) = pts[-2], pts[-1]
    return {"delta": last - prev, "from": prev, "to": last}


def days_since_check(sheep, as_of=None):
    """Days since the most recent dated event of any kind (FAMACHA, FEC, treatment,
    vaccination). None = no dated record exists at all."""
    ref = as_of or date.today()
    h = sheep.get("health", {}) or {}
    latest = None
    for coll in ("famacha_scores", "fec_history", "treatments", "vaccinations"):
        for e in (h.get(coll) or []):
            if not isinstance(e, dict):
                continue
            d = _parse_iso(e.get("date"))
            if d is None or d > ref:
                continue
            if latest is None or d > latest:
                latest = d
    return (ref - latest).days if latest else None


def _age_days(sheep, as_of=None):
    dob = _parse_iso(sheep.get("dob"))
    if dob is None:
        return None
    return ((as_of or date.today()) - dob).days


def triage_one(sheep, as_of=None):
    """One animal's triage record: {sheep_id, status R|A|G, score, reasons[], decision,
    trend, days_since_check}. Higher score = more attention. Weights are stated inline —
    a composite that hides its arithmetic is a vibe, not a triage."""
    rec = dd.decide(sheep, as_of)
    trend = famacha_trend(sheep, as_of)
    since = days_since_check(sheep, as_of)
    reasons = []
    score = 0.0

    score += rec["urgency"] * 10                      # deworm urgency dominates (0..30)
    if rec["urgency"] >= 3:
        reasons.append(f"deworm: {rec['decision']}")
    elif rec["urgency"] >= 1:
        reasons.append(f"deworm: {rec['decision']}")
    if "mismatch_signal" in rec["flags"]:
        score += 5
        reasons.append("FAMACHA/FEC mismatch — diagnostic signal")

    worsening = trend is not None and trend["delta"] > 0
    if worsening:
        score += 4 + 2 * trend["delta"]
        reasons.append(f"FAMACHA worsening {trend['from']:g}→{trend['to']:g}")

    if since is None:
        age = _age_days(sheep, as_of)
        if age is not None and age < FIRST_CHECK_AGE_DAYS:
            reasons.append(f"young ({age}d) — first check due")
        else:
            score += 6
            reasons.append("no dated records — first check owed")
    elif since > RECHECK_DAYS:
        score += min(6.0, since / 30.0)               # staleness grows, capped
        reasons.append(f"last check {since}d ago")

    if sheep.get("status") == "alive" and not sheep.get("pen"):
        score += 2
        reasons.append("alive with no pen recorded")
    conflicts = sum(1 for e in (sheep.get("health", {}).get("famacha_scores") or [])
                    if isinstance(e, dict) and e.get("score") is None and "CONFLICT" in str(e.get("notes", "")))
    if conflicts:
        score += 2
        reasons.append(f"{conflicts} [CONFLICT] score(s) await notebook re-check")

    if rec["urgency"] >= 3 or (worsening and trend["to"] >= dd.FAMACHA_BORDERLINE):
        status = "RED"
    elif (rec["urgency"] >= 1 or worsening or conflicts
          or (since is not None and since > RECHECK_DAYS)
          or (since is None and "first check owed" in " ".join(reasons))):
        status = "AMBER"
    else:
        status = "GREEN"

    return {"sheep_id": sheep.get("id"), "status": status, "score": round(score, 1),
            "reasons": reasons, "decision": rec["decision"],
            "trend": trend, "days_since_check": since}


def triage_flock(db, as_of=None):
    # on-property only: registry/pedigree imports (on_property: False) are not owed checks
    rows = [triage_one(s, as_of) for s in db.get("sheep", [])
            if s.get("status") == "alive" and s.get("on_property") is not False]
    rows.sort(key=lambda r: (-r["score"], r["sheep_id"] or ""))
    return rows


def main():
    ap = argparse.ArgumentParser(description="Attention-priority triage (read-only)")
    ap.add_argument("--as-of", default=None)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--limit", type=int, default=None, help="show only the top N")
    args = ap.parse_args()
    as_of = _parse_iso(args.as_of) if args.as_of else None
    if args.as_of and as_of is None:
        print(f"ERROR: --as-of {args.as_of!r} is not an ISO date", file=sys.stderr)
        return 2
    db = json.loads(DB_PATH.read_text())
    rows = triage_flock(db, as_of)
    if args.json:
        print(json.dumps({"as_of": (as_of or date.today()).isoformat(), "triage": rows}, indent=2))
        return 0
    counts = {"RED": 0, "AMBER": 0, "GREEN": 0}
    for r in rows:
        counts[r["status"]] += 1
    print(f"Attention triage — {len(rows)} alive, as of {(as_of or date.today()).isoformat()}  "
          f"(RED {counts['RED']} / AMBER {counts['AMBER']} / GREEN {counts['GREEN']})\n")
    shown = rows[:args.limit] if args.limit else rows
    for r in shown:
        if r["status"] == "GREEN" and not args.limit:
            continue  # default view: the attention list, not the whole roster
        print(f"  [{r['status']:5}] {r['score']:5.1f}  {r['sheep_id']:28} {'; '.join(r['reasons']) or 'unremarkable'}")
    greens = counts["GREEN"]
    if greens and not args.limit:
        print(f"\n  (+{greens} GREEN not shown — --limit 0 for all)")
    print("\n  Read-only advisory; weights stated in triage_one(). Operator decides.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
