#!/usr/bin/env python3
"""Deworming decision advisor — FAMACHA + FEC read TOGETHER (MCS-8).

Soli Deo Gloria.

Grounded in standard integrated parasite management (the FuzzyLogic-VERMIFUGA
concept, adopted concept-only): the two numbers are one diagnostic, and their
DISAGREEMENT is itself a signal —

  anemic (FAMACHA 4-5) + LOW egg count   -> anemia may NOT be parasites: investigate
                                            (liver fluke, coccidia, nutrition) while treating
  good colour        + HIGH egg count    -> animal copes but is seeding the pasture:
                                            contamination/refugia consideration, tighter recheck
  anemic             + HIGH egg count    -> treat — and after the 2026-08-18 losses, NOT with
                                            ivermectin alone (presumptive resistance on property)
  anemic             + NO egg count      -> treat clinically per FAMACHA; pull a fecal sample
                                            BEFORE dosing so the treatment doubles as a
                                            FECRT baseline (MCS-30)

Data sources: data/health_events.jsonl (famacha events with `score`, any event with
`fec_epg`) and the DB's health.famacha_scores (ISO or M-D-YY dates; unparseable
dates are counted and skipped, never guessed).

Thresholds are DEFAULTS from common Haemonchus practice, tunable by flag — not lab
truth: FEC high >= 1000 epg, low < 500 epg; scores stale after 21 days (14 in
warm-wet season, --season warm-wet). The advisor never doses anything; it ranks
and explains. Owner and vet decide.
"""
import argparse
import datetime
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
DB_PATH = REPO_ROOT / "data" / "flock_database.json"
EVENTS_PATH = REPO_ROOT / "data" / "health_events.jsonl"


def parse_date(s):
    """ISO, ISO range (use end), or M-D-YY. None when unparseable — counted, not guessed."""
    if not s or not isinstance(s, str):
        return None
    s = s.split("/")[-1].strip()
    try:
        return datetime.date.fromisoformat(s)
    except ValueError:
        pass
    m = re.fullmatch(r"(\d{1,2})-(\d{1,2})-(\d{2,4})", s)
    if m:
        mo, d, y = int(m[1]), int(m[2]), int(m[3])
        y += 2000 if y < 100 else 0
        try:
            return datetime.date(y, mo, d)
        except ValueError:
            return None
    return None


def parse_score(v):
    """int 1-5, or the WORST end of a '1-2' style range (conservative), else None."""
    if isinstance(v, int):
        return v if 1 <= v <= 5 else None
    if isinstance(v, str):
        nums = [int(n) for n in re.findall(r"[1-5]", v)]
        return max(nums) if nums else None
    return None


def latest_signals(sheep, events, unparseable):
    """Per animal: (famacha_score, famacha_date, fec_epg, fec_date)."""
    fam, fec = {}, {}

    def consider_fam(aid, date, score):
        if score is None:
            return
        if date is None:
            unparseable[0] += 1
            return
        if aid not in fam or date > fam[aid][1]:
            fam[aid] = (score, date)

    for s in sheep:
        h = s.get("health") or {}
        for e in (h.get("famacha_scores") or []):
            if isinstance(e, dict):
                consider_fam(s["id"], parse_date(e.get("date")), parse_score(e.get("score")))
        for e in (h.get("famacha_history") or []):
            if isinstance(e, dict):
                consider_fam(s["id"], parse_date(e.get("date")), parse_score(e.get("score")))
    for e in events:
        if e.get("type") == "famacha":
            consider_fam(e["animal_id"], parse_date(e.get("date")), parse_score(e.get("score")))
        if e.get("fec_epg") is not None:
            d = parse_date(e.get("date"))
            if d and (e["animal_id"] not in fec or d > fec[e["animal_id"]][1]):
                fec[e["animal_id"]] = (e["fec_epg"], d)
    return fam, fec


def advise(score, s_date, epg, today, fec_high, fec_low, stale_days):
    """Return (rank, status, advice). rank: lower = worse."""
    stale = s_date is not None and (today - s_date).days > stale_days
    if score is None:
        return 3, "AMBER", "no parseable FAMACHA on record — score at next handling"
    if score >= 4:
        if stale:
            return 0, "RED", (f"FAMACHA {score} on record but it is {(today - s_date).days}d old — "
                              f"RE-SCORE FIRST THING; if still 4-5, treat (not ivermectin alone) "
                              f"with a pre-dose fecal sample")
        if epg is None:
            return 0, "RED", (f"FAMACHA {score}: treat clinically — pull a fecal sample BEFORE "
                              f"dosing (free FECRT baseline); not ivermectin alone (resistance signal)")
        if epg >= fec_high:
            return 0, "RED", (f"FAMACHA {score} + FEC {epg} epg: treat — different class than "
                              f"ivermectin; recheck FEC day 10-14 (FECRT)")
        if epg < fec_low:
            return 0, "RED", (f"FAMACHA {score} but FEC only {epg} epg: MISMATCH — anemia may not "
                              f"be barber pole (fluke? coccidia? nutrition?); investigate while treating")
        return 0, "RED", f"FAMACHA {score} + FEC {epg} epg: treat and investigate"
    if score == 3:
        note = f" (score {(today - s_date).days}d old — recheck overdue)" if stale else ""
        if epg is not None and epg >= fec_high:
            return 1, "AMBER", f"FAMACHA 3 + FEC {epg} epg: borderline both ways — treat-or-recheck within days{note}"
        return 2, "AMBER", f"FAMACHA 3: recheck within a week{note}"
    # score 1-2
    if epg is not None and epg >= fec_high:
        return 1, "AMBER", (f"good colour but FEC {epg} epg: MISMATCH — coping but seeding pasture; "
                            f"refugia/contamination consideration, tighten recheck cadence")
    if stale:
        return 2, "AMBER", f"FAMACHA {score} but {(today - s_date).days}d old — re-score (warm-wet season)"
    return 4, "GREEN", f"FAMACHA {score}, no adverse signals"


def main():
    ap = argparse.ArgumentParser(description="FAMACHA+FEC deworming advisor (MCS-8)")
    ap.add_argument("--animal", help="one animal id (default: all alive)")
    ap.add_argument("--fec-high", type=int, default=1000)
    ap.add_argument("--fec-low", type=int, default=500)
    ap.add_argument("--season", choices=["normal", "warm-wet"], default="warm-wet",
                    help="warm-wet halves the staleness window (default in FL summer)")
    args = ap.parse_args()
    stale_days = 14 if args.season == "warm-wet" else 21

    db = json.load(open(DB_PATH))
    sheep = db.get("sheep", [])
    events = []
    if EVENTS_PATH.exists():
        events = [json.loads(l) for l in EVENTS_PATH.read_text().splitlines() if l.strip()]
    unparseable = [0]
    fam, fec = latest_signals(sheep, events, unparseable)

    targets = [s for s in sheep if s.get("status") == "alive"]
    if args.animal:
        targets = [s for s in sheep if s["id"] == args.animal]
        if not targets:
            raise SystemExit(f"animal '{args.animal}' not in flock DB")

    today = datetime.date.today()
    rows = []
    for s in targets:
        score, s_date = fam.get(s["id"], (None, None))
        epg, _ = fec.get(s["id"], (None, None))
        rank, status, advice = advise(score, s_date, epg, today, args.fec_high, args.fec_low, stale_days)
        rows.append((rank, status, s["id"], score, s_date, epg, advice))

    rows.sort(key=lambda r: (r[0], r[2]))
    counts = {"RED": 0, "AMBER": 0, "GREEN": 0}
    for rank, status, aid, score, s_date, epg, advice in rows:
        counts[status] += 1
        if status != "GREEN" or args.animal:
            sc = f"F{score}@{s_date}" if score else "F—"
            fe = f" FEC {epg}" if epg is not None else ""
            print(f"{status:5} {aid:30} {sc}{fe}  {advice}")
    print(f"\n{counts['RED']} RED · {counts['AMBER']} AMBER · {counts['GREEN']} GREEN "
          f"(of {len(rows)}; thresholds high>={args.fec_high} low<{args.fec_low} epg, "
          f"stale>{stale_days}d, season={args.season})")
    if unparseable[0]:
        print(f"note: {unparseable[0]} dated entries had unparseable dates and were skipped, "
              f"not guessed — they predate ISO discipline")


if __name__ == "__main__":
    main()
