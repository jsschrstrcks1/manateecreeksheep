#!/usr/bin/env python3
"""Attention-priority triage — who needs looking at FIRST (MCS-3).

Soli Deo Gloria.

Worst-first composite attention score per living animal, so the shepherd walks out
the door with a ranked list instead of a flat roster. Composes the MCS-8 advisor's
signals (latest FAMACHA + FEC, staleness) with trend, cohort-loss proximity, pen
friction, and withdrawal flags. The score RANKS; the advisor line under each animal
says WHY and what to do. Nothing here doses anything — owner and vet decide.

Components (defaults; every weight visible in --explain output):
  FAMACHA 4-5 (current)          +50    FAMACHA 4-5 but stale        +35
  FAMACHA 3                      +20    no parseable FAMACHA at all  +25
  score stale (season window)    +15    worsening trend (last two)   +15
  FEC >= high threshold          +20    FEC missing while FAMACHA>=3 +10
  days since last check          +1/wk, capped +10
  death in same pen within 14d   +15    pen unknown (can't find her) +5

Bands: RED >= 50 · AMBER >= 25 · GREEN below. Withdrawal locks shown as flags.
"""
import argparse
import datetime
import json
from pathlib import Path

import importlib.util as _ilu
_here = Path(__file__).parent
_spec = _ilu.spec_from_file_location("da", _here / "deworm_advisor.py")
da = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(da)

REPO_ROOT = _here.parent
DB_PATH = REPO_ROOT / "data" / "flock_database.json"
EVENTS_PATH = REPO_ROOT / "data" / "health_events.jsonl"


def famacha_series(sheep_rec, events, aid):
    """All parseable (date, score) points for one animal, ascending by date."""
    pts = []
    h = sheep_rec.get("health") or {}
    for src in (h.get("famacha_scores") or []), (h.get("famacha_history") or []):
        for e in src:
            if isinstance(e, dict):
                d, sc = da.parse_date(e.get("date")), da.parse_score(e.get("score"))
                if d and sc:
                    pts.append((d, sc))
    for e in events:
        if e.get("animal_id") == aid and e.get("type") == "famacha":
            d, sc = da.parse_date(e.get("date")), da.parse_score(e.get("score"))
            if d and sc:
                pts.append((d, sc))
    # One point per DATE (worst end kept): the same check often appears in both
    # famacha_scores and famacha_history, sometimes as '1' beside '1-2' — without
    # collapsing, that same-day pair reads as a fake worsening trend.
    by_date = {}
    for d, sc in pts:
        by_date[d] = max(by_date.get(d, 0), sc)
    return sorted(by_date.items())


def score_animal(*, score, s_date, epg, trend_worse, days_since, cohort_loss_14d,
                 pen_missing, today, fec_high, stale_days):
    parts = []
    stale = s_date is not None and (today - s_date).days > stale_days
    if score is None:
        parts.append(("no parseable FAMACHA", 25))
    elif score >= 4:
        parts.append((f"FAMACHA {score} (stale)" if stale else f"FAMACHA {score}", 35 if stale else 50))
    elif score == 3:
        parts.append(("FAMACHA 3", 20))
    if score is not None and stale and score < 4:
        parts.append((f"score {(today - s_date).days}d old", 15))
    if trend_worse:
        parts.append(("worsening trend", 15))
    if epg is not None and epg >= fec_high:
        parts.append((f"FEC {epg} epg", 20))
    if epg is None and score is not None and score >= 3:
        parts.append(("no FEC beside FAMACHA>=3", 10))
    if days_since is not None:
        parts.append((f"{days_since}d since last check", min(days_since // 7, 10)))
    if cohort_loss_14d:
        parts.append(("death in same pen <=14d", 15))
    if pen_missing:
        parts.append(("pen unknown", 5))
    return sum(w for _, w in parts), parts


def main():
    ap = argparse.ArgumentParser(description="Worst-first flock triage (MCS-3)")
    ap.add_argument("--top", type=int, default=15)
    ap.add_argument("--all", action="store_true", help="show every animal, not just top N")
    ap.add_argument("--explain", action="store_true", help="show score components")
    ap.add_argument("--fec-high", type=int, default=1000)
    ap.add_argument("--fec-low", type=int, default=500)
    ap.add_argument("--season", choices=["normal", "warm-wet"], default="warm-wet")
    args = ap.parse_args()
    stale_days = 14 if args.season == "warm-wet" else 21
    today = datetime.date.today()

    db = json.load(open(DB_PATH))
    sheep = db.get("sheep", [])
    events = []
    if EVENTS_PATH.exists():
        events = [json.loads(l) for l in EVENTS_PATH.read_text().splitlines() if l.strip()]
    unparseable = [0]
    fam, fec = da.latest_signals(sheep, events, unparseable)

    # pens that lost an animal to a dated death event in the last 14 days
    recent_loss_pens = set()
    pen_of = {s["id"]: s.get("pen") for s in sheep}
    for e in events:
        if e.get("type") == "death":
            d = da.parse_date(e.get("date"))
            if d and (today - d).days <= 14:
                # pen at death is nulled on the record; use dam/cohort pen via the event animal's last pen note is gone —
                # fall back to the dam's pen when the dead animal's pen is null (lamb losses cluster with dams).
                dead = next((s for s in sheep if s["id"] == e["animal_id"]), None)
                p = (dead or {}).get("pen") or pen_of.get((dead or {}).get("dam_id"))
                if p:
                    recent_loss_pens.add(p)

    active_locks = {e["animal_id"] for e in events
                    if e.get("withdrawal_until") and e["withdrawal_until"] >= today.isoformat()}

    rows = []
    for s in sheep:
        if s.get("status") != "alive":
            continue
        aid = s["id"]
        score, s_date = fam.get(aid, (None, None))
        epg, _ = fec.get(aid, (None, None))
        series = famacha_series(s, events, aid)
        trend_worse = len(series) >= 2 and series[-1][1] > series[-2][1]
        days_since = (today - s_date).days if s_date else None
        total, parts = score_animal(
            score=score, s_date=s_date, epg=epg, trend_worse=trend_worse,
            days_since=days_since, cohort_loss_14d=(s.get("pen") in recent_loss_pens),
            pen_missing=not s.get("pen"), today=today,
            fec_high=args.fec_high, stale_days=stale_days)
        _, _, advice = da.advise(score, s_date, epg, today, args.fec_high, args.fec_low, stale_days)
        rows.append((total, aid, s.get("pen"), parts, advice, aid in active_locks))

    rows.sort(key=lambda r: (-r[0], r[1]))
    shown = rows if args.all else rows[: args.top]
    for total, aid, pen, parts, advice, locked in shown:
        band = "RED" if total >= 50 else ("AMBER" if total >= 25 else "GREEN")
        lock = " [WITHDRAWAL]" if locked else ""
        print(f"{total:4}  {band:5} {aid:30} pen={pen or '?':12}{lock}  {advice}")
        if args.explain:
            print("        " + " · ".join(f"{n} +{w}" for n, w in parts))
    print(f"\n({len(rows)} living animals ranked; showing {len(shown)}; "
          f"season={args.season}, FEC high>={args.fec_high})")
    if unparseable[0]:
        print(f"note: {unparseable[0]} entries with unparseable dates skipped, not guessed")


if __name__ == "__main__":
    main()
