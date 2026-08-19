#!/usr/bin/env python3
"""deworm_decision.py — FAMACHA + FEC combined deworming advisory (MCS-8).

DOCTRINE (from the MCS-8 spec, grounded in standard integrated parasite management):
read FAMACHA and FEC TOGETHER, and treat DISAGREEMENT as a diagnostic signal:
  - anemic (FAMACHA 4-5) + LOW egg count  -> anemia may NOT be parasites — INVESTIGATE
    before dosing (liver fluke, nutrition, chronic disease all present as pale membranes);
  - good colour (1-2) + HIGH egg count    -> the animal copes but is SHEDDING heavily onto
    pasture — a refugia/contamination consideration, not an automatic dose;
  - do not deworm on FAMACHA alone        -> a missing FEC is surfaced as the gap it is.

READ-ONLY BY DESIGN: this tool writes nothing and doses nothing. It is an advisory that
sorts the flock worst-first and names its evidence (score, date, age). Welfare calls stay
with the operator — an anemic animal is flagged URGENT regardless of what the egg count
says, because "investigate before dosing" never means "withhold care".

THRESHOLDS are named constants, stated not hidden. FAMACHA: 1-2 good, 3 borderline,
4-5 anemic (the standard card). FEC (eggs per gram, Haemonchus-oriented small-ruminant
guidance): < 500 low, 500-999 moderate, >= 1000 high. Regional labs vary — these are
operator-tunable defaults, not universal truth. Staleness: a FAMACHA older than
STALE_DAYS is flagged; in-season guidance is a check every 2-4 weeks, so a months-old
score is a reason to RECHECK, not a basis to dose.

    python3 scripts/deworm_decision.py                 # whole flock (alive), worst-first
    python3 scripts/deworm_decision.py --sheep kelsier # one animal, full detail
    python3 scripts/deworm_decision.py --as-of 2026-04-15   # evaluate as of a date
    python3 scripts/deworm_decision.py --json          # machine-readable (agenda engine feed)
"""
import argparse
import importlib.util
import json
import sys
from datetime import date, datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "flock_database.json"

# Named thresholds — operator-tunable, defaults from standard integrated parasite management.
FAMACHA_ANEMIC = 4.0        # >= 4 is anemic (treat/urgent territory on the card)
FAMACHA_BORDERLINE = 3.0    # == 3 borderline -> recheck sooner
FEC_LOW = 500               # epg  < 500  = low
FEC_HIGH = 1000             # epg >= 1000 = high
STALE_DAYS = 45             # a FAMACHA older than this is a recheck prompt, not evidence

# The scorer's range-aware parser ('1-2' -> 1.5) is the one FAMACHA parser in the repo —
# reuse it rather than fork a second interpretation of the same value format.
_pr_spec = importlib.util.spec_from_file_location(
    "parasite_resistance", str(Path(__file__).resolve().parent / "parasite_resistance.py"))
_pr = importlib.util.module_from_spec(_pr_spec)
_pr_spec.loader.exec_module(_pr)
parse_famacha = _pr._parse_famacha


def _parse_iso(d):
    try:
        return datetime.strptime(str(d), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def latest_famacha(sheep, as_of=None):
    """Most recent dated, parseable FAMACHA at or before as_of.
    Returns {score, date, age_days} or None. Entries with score None (e.g. the
    normalization's [CONFLICT] rows) are skipped — an unverified value is not evidence."""
    best = None
    for e in (sheep.get("health", {}).get("famacha_scores") or []):
        if not isinstance(e, dict):
            continue
        val = parse_famacha(e.get("score"))
        d = _parse_iso(e.get("date"))
        if val is None or d is None:
            continue
        if as_of and d > as_of:
            continue
        if best is None or d > best[1]:
            best = (val, d)
    if best is None:
        return None
    ref = as_of or date.today()
    return {"score": best[0], "date": best[1].isoformat(), "age_days": (ref - best[1]).days}


def latest_fec(sheep, as_of=None):
    """Most recent dated FEC (epg) at or before as_of. Returns {epg, date, age_days} or None."""
    best = None
    for e in (sheep.get("health", {}).get("fec_history") or []):
        if not isinstance(e, dict):
            continue
        epg = e.get("fec")
        d = _parse_iso(e.get("date"))
        if not isinstance(epg, (int, float)) or d is None:
            continue
        if as_of and d > as_of:
            continue
        if best is None or d > best[1]:
            best = (float(epg), d)
    if best is None:
        return None
    ref = as_of or date.today()
    return {"epg": best[0], "date": best[1].isoformat(), "age_days": (ref - best[1]).days}


def decide(sheep, as_of=None):
    """The MCS-8 combined decision for one animal. Returns a typed record:
      {sheep_id, decision, urgency, why, famacha, fec, flags}
    decision ∈ treat_and_verify | investigate_anemia_nonparasitic |
               refugia_contamination_watch | monitor_routine | recheck_borderline |
               urgent_check_fec_needed | fec_needed | no_data
    urgency 0 (none) .. 3 (urgent). Missing/stale data is SURFACED (three states, never
    a silent default) — the honest answer for most of this flock today is 'recheck'."""
    fam = latest_famacha(sheep, as_of)
    fec = latest_fec(sheep, as_of)
    flags = []
    if fam and fam["age_days"] > STALE_DAYS:
        flags.append(f"famacha_stale_{fam['age_days']}d")
    if fec and fec["age_days"] > STALE_DAYS:
        flags.append(f"fec_stale_{fec['age_days']}d")

    def rec(decision, urgency, why):
        return {"sheep_id": sheep.get("id"), "decision": decision, "urgency": urgency,
                "why": why, "famacha": fam, "fec": fec, "flags": flags}

    if fam is None and fec is None:
        return rec("no_data", 0, "no dated FAMACHA or FEC on record — nothing to decide from")

    anemic = fam is not None and fam["score"] >= FAMACHA_ANEMIC
    borderline = fam is not None and FAMACHA_BORDERLINE <= fam["score"] < FAMACHA_ANEMIC
    fec_high = fec is not None and fec["epg"] >= FEC_HIGH
    fec_low = fec is not None and fec["epg"] < FEC_LOW

    if anemic and fec is not None and fec_low:
        flags.append("mismatch_signal")   # the spec's diagnostic case #1
        return rec("investigate_anemia_nonparasitic", 3,
                   f"FAMACHA {fam['score']:g} (anemic) but FEC {fec['epg']:g} epg (low) — "
                   "anemia may NOT be parasites; investigate (fluke, nutrition, chronic "
                   "disease) before dosing. Urgent because the animal IS anemic.")
    if anemic and fec is not None:
        return rec("treat_and_verify", 3,
                   f"FAMACHA {fam['score']:g} (anemic) + FEC {fec['epg']:g} epg — signals "
                   "agree on parasitism; treat, and record the drench for a FECRT follow-up "
                   "(MCS-30).")
    if anemic:
        return rec("urgent_check_fec_needed", 3,
                   f"FAMACHA {fam['score']:g} (anemic) with NO egg count — the integrated "
                   "rule wants an FEC before dosing, and the anemia itself needs eyes on the "
                   "animal NOW. Welfare first: 'investigate' never means 'withhold care'.")
    if not anemic and fam is not None and fec is not None and fec_high:
        flags.append("mismatch_signal")   # the spec's diagnostic case #2
        return rec("refugia_contamination_watch", 2,
                   f"FAMACHA {fam['score']:g} (coping) but FEC {fec['epg']:g} epg (high) — "
                   "the animal tolerates the load yet is seeding the pasture. A "
                   "refugia/contamination management call, not an automatic dose.")
    if borderline:
        return rec("recheck_borderline", 1,
                   f"FAMACHA {fam['score']:g} is borderline — recheck on a short interval"
                   + ("" if fec else "; an FEC would sharpen the call") + ".")
    if fam is not None and fec is None:
        return rec("fec_needed", 0,
                   f"FAMACHA {fam['score']:g} (good) but no egg count on record — do not "
                   "manage on FAMACHA alone; an FEC completes the picture.")
    return rec("monitor_routine", 0,
               "signals present and unremarkable — routine monitoring.")


def decide_flock(db, as_of=None, alive_only=True):
    out = []
    for s in db.get("sheep", []):
        if alive_only and s.get("status") != "alive":
            continue
        out.append(decide(s, as_of))
    # worst-first: urgency desc, then mismatches, then staleness-flagged
    out.sort(key=lambda r: (-r["urgency"], "mismatch_signal" not in r["flags"], r["sheep_id"] or ""))
    return out


def main():
    ap = argparse.ArgumentParser(description="FAMACHA+FEC combined deworming advisory (read-only)")
    ap.add_argument("--sheep", default=None, help="one sheep id")
    ap.add_argument("--as-of", default=None, help="evaluate as of ISO date (default today)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--all", action="store_true", help="include non-alive animals")
    args = ap.parse_args()

    as_of = _parse_iso(args.as_of) if args.as_of else None
    if args.as_of and as_of is None:
        print(f"ERROR: --as-of {args.as_of!r} is not an ISO date", file=sys.stderr)
        return 2
    db = json.loads(DB_PATH.read_text())

    if args.sheep:
        target = next((s for s in db["sheep"] if s.get("id") == args.sheep), None)
        if target is None:
            print(f"ERROR: sheep {args.sheep!r} not found", file=sys.stderr)
            return 1
        results = [decide(target, as_of)]
    else:
        results = decide_flock(db, as_of, alive_only=not args.all)

    if args.json:
        print(json.dumps({"as_of": (as_of or date.today()).isoformat(),
                          "thresholds": {"famacha_anemic": FAMACHA_ANEMIC, "fec_low": FEC_LOW,
                                         "fec_high": FEC_HIGH, "stale_days": STALE_DAYS},
                          "decisions": results}, indent=2))
        return 0

    URG = {3: "URGENT", 2: "watch ", 1: "recheck", 0: "  ok  "}
    counts = {}
    for r in results:
        counts[r["decision"]] = counts.get(r["decision"], 0) + 1
    print(f"Deworm advisory (read-only) — {len(results)} animals, as of {(as_of or date.today()).isoformat()}")
    print("  " + ", ".join(f"{k}: {v}" for k, v in sorted(counts.items(), key=lambda kv: -kv[1])))
    print()
    for r in results:
        fam = r["famacha"]
        fec = r["fec"]
        famtxt = f"FAM {fam['score']:g} ({fam['date']}, {fam['age_days']}d)" if fam else "FAM —"
        fectxt = f"FEC {fec['epg']:g} ({fec['date']})" if fec else "FEC —"
        mm = "  ⚠ MISMATCH" if "mismatch_signal" in r["flags"] else ""
        print(f"  [{URG[r['urgency']]}] {r['sheep_id']:28} {famtxt:34} {fectxt:22} {r['decision']}{mm}")
        if r["urgency"] >= 2 or mm:
            print(f"           {r['why']}")
    print("\n  Advisory only — welfare and dosing decisions are the operator's. "
          "Thresholds are stated defaults; regional lab guidance overrides.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
