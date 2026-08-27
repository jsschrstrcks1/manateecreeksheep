#!/usr/bin/env python3
"""flock.py — the one entry point: "what needs eyes today?" (Flock Manager dashboard). READ-ONLY.

The flock tools were 13 separate scripts, each re-read one at a time and mentally joined. This is
the hub that COMPOSES the live-signal ones into a single worst-first briefing — no new logic, it
calls the same functions the individual tools do, so the numbers here always match them:

  - HEALTH ATTENTION  — attention_triage (RED/AMBER worst-first)
  - WITHDRAWAL HOLDS  — withdrawal_check (animals whose meat/milk is held: in-withdrawal or unknown)
  - INBREEDING ALERTS — pedigree_integrity (living animals at F >= high, and any graph faults)
  - OPEN TASKS        — pending_done (overdue/open items) + triage-implied suggestions
  - COHORTS           — cohorts (pen headcounts, time-aware)

Everything read-only and advisory; the operator decides. Run this first each day; drill into the
named tool for detail.

    python3 scripts/flock.py                 # today's briefing
    python3 scripts/flock.py --as-of DATE     # as of a date
    python3 scripts/flock.py --json
"""
import argparse
import importlib.util
import json
import sys
from datetime import date, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
DB_PATH = HERE.parent / "data" / "flock_database.json"


def _load(name):
    spec = importlib.util.spec_from_file_location(name, str(HERE / f"{name}.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _iso(d):
    try:
        return datetime.strptime(str(d), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def briefing(db, as_of=None):
    """Compose the live-signal tools into one structured briefing dict."""
    at = _load("attention_triage")
    wc = _load("withdrawal_check")
    pi = _load("pedigree_integrity")
    pdmod = _load("pending_done")
    co = _load("cohorts")
    vc = _load("vaccination_check")

    # HEALTH: worst-first triage (RED/AMBER)
    triage = at.triage_flock(db, as_of)
    red = [r for r in triage if r["status"] == "RED"]
    amber = [r for r in triage if r["status"] == "AMBER"]

    # WITHDRAWAL: animals currently held (in a confirmed withdrawal or an unknown interval)
    wref = wc.load_reference()
    wrecs = wc.scan(db, wref, as_of or date.today())
    held = {}
    for r in wrecs:
        if r["status"] in ("in_withdrawal", "unknown_interval"):
            held.setdefault(r["sheep_id"], set()).add(r["status"])
    withdrawal_holds = [{"sheep_id": k, "states": sorted(v)} for k, v in held.items()]

    # INBREEDING: graph faults + living animals at F >= high band
    integrity = pi.integrity_report(db)
    ped = pi._ped_from_db(db)
    fcensus = pi.flock_inbreeding(db, ped)
    high_f = [r for r in fcensus if r.get("F") is not None and r["F"] >= pi.COI_HIGH]

    # TASKS: open/overdue pending items + triage-implied suggestions
    items = pdmod.load_items()
    opens = pdmod.open_items(items, as_of or date.today())
    overdue = [it for it in opens if it.get("_overdue")]
    suggestions = pdmod.suggest_from_triage(db, items)

    # VACCINATION: clostridial (CDT) never / booster-overdue
    vax = vc.compliance(db, as_of)
    vax_never = [r for r in vax if r["status"] == "never"]
    vax_overdue = [r for r in vax if r["status"] == "booster_overdue"]

    # COHORTS
    cohorts = co.cohort_summary(db, as_of)

    return {
        "as_of": (as_of or date.today()).isoformat(),
        "health": {"red": red, "amber": amber},
        "withdrawal_holds": withdrawal_holds,
        "inbreeding": {"graph_clean": integrity["clean"], "faults": integrity["faults_total"],
                       "high_F": high_f},
        "vaccination": {"never": vax_never, "booster_overdue": vax_overdue},
        "tasks": {"open": len(opens), "overdue": len(overdue), "suggestions": len(suggestions)},
        "cohorts": cohorts,
    }


def main():
    ap = argparse.ArgumentParser(description="Flock Manager — one briefing (read-only)")
    ap.add_argument("--as-of", default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    as_of = _iso(args.as_of) if args.as_of else None
    if args.as_of and as_of is None:
        print(f"ERROR: --as-of {args.as_of!r} is not an ISO date", file=sys.stderr); return 2
    db = json.loads(DB_PATH.read_text())
    b = briefing(db, as_of)
    if args.json:
        print(json.dumps(b, indent=2, default=str)); return 0

    print(f"═══ Manatee Creek Flock — briefing for {b['as_of']} ═══\n")

    red, amber = b["health"]["red"], b["health"]["amber"]
    print(f"HEALTH ATTENTION (attention_triage.py):  {len(red)} RED, {len(amber)} AMBER")
    for r in red:
        print(f"    RED   {r['sheep_id']:26} {'; '.join(r['reasons'][:2])}")
    for r in amber[:6]:
        print(f"    amber {r['sheep_id']:26} {'; '.join(r['reasons'][:1])}")
    if len(amber) > 6:
        print(f"    (+{len(amber)-6} more amber — see attention_triage.py)")

    wh = b["withdrawal_holds"]
    print(f"\nWITHDRAWAL HOLDS (withdrawal_check.py):  {len(wh)} animal(s) meat/milk held")
    for r in wh[:8]:
        print(f"    {r['sheep_id']:26} {', '.join(r['states'])}")
    if len(wh) > 8:
        print(f"    (+{len(wh)-8} more — see withdrawal_check.py --gaps)")

    inb = b["inbreeding"]
    print(f"\nINBREEDING (pedigree_integrity.py):  graph "
          + ("CLEAN" if inb["graph_clean"] else f"{inb['faults']} FAULT(S)")
          + f", {len(inb['high_F'])} living animal(s) at F>=0.125 (high/severe)")
    for r in inb["high_F"][:8]:
        print(f"    F={r['F']:.3f} [{r['band']}]  {(r['name'] or r['id'])[:30]}")

    vax = b["vaccination"]
    print(f"\nVACCINATION (vaccination_check.py):  {len(vax['never'])} never CDT-vaccinated, "
          f"{len(vax['booster_overdue'])} booster overdue")
    for r in vax["never"][:6]:
        print(f"    never  {(r['name'] or r['id'])[:30]}")
    if len(vax["never"]) > 6:
        print(f"    (+{len(vax['never'])-6} more — see vaccination_check.py)")

    t = b["tasks"]
    print(f"\nTASKS (pending_done.py):  {t['open']} open ({t['overdue']} overdue); "
          f"{t['suggestions']} triage-implied not yet logged")

    print(f"\nCOHORTS (cohorts.py):  {len(b['cohorts'])} pens — "
          + ", ".join(f"{c['cohort']} {c['count']}" for c in b["cohorts"][:6])
          + (" …" if len(b["cohorts"]) > 6 else ""))

    print("\n  Read-only briefing composed from the individual tools (numbers match them exactly)."
          "\n  Drill into the named script for detail. Operator decides.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
