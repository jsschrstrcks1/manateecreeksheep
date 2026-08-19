#!/usr/bin/env python3
"""withdrawal_check.py — meat/milk drug-WITHDRAWAL clearance (MCS-7). READ-ONLY, food-safety.

The one question this answers: which treated animals are still within a drug withdrawal period,
and until when — so their meat or milk does not enter the food supply too early?

    clear_date = treatment_date + withdrawal_days   (per drug, meat and milk separately)

FOOD-SAFETY HONESTY — this tool authors NO withdrawal numbers. Every interval comes from
data/withdrawal_reference.json, which is VET/OPERATOR-OWNED. A drug whose interval is not
vet-confirmed there (status NEEDS_VET_CONFIRMATION, withdrawal_days=null) makes every animal
treated with it report **UNKNOWN — do not release until a vet/FARAD interval is confirmed**,
never "clear". Most drugs are used EXTRA-LABEL in sheep and their true interval (often longer
than any label figure) must come from the prescribing vet or FARAD (farad.org). The tool never
says an animal is safe to slaughter or milk; it computes the earliest clear date from a CONFIRMED
interval, or names exactly which drug still needs one.

A treatment string naming no recognized drug is surfaced under "unrecognized", not silently
cleared — an unlogged drug must never read as food-safe by omission.

    python3 scripts/withdrawal_check.py                 # animals in withdrawal now (+ unknowns)
    python3 scripts/withdrawal_check.py --as-of DATE     # status as of a date
    python3 scripts/withdrawal_check.py --gaps           # the confirmation worklist (drugs used, no confirmed interval)
    python3 scripts/withdrawal_check.py --json
"""
import argparse
import json
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "flock_database.json"
REF_PATH = Path(__file__).resolve().parent.parent / "data" / "withdrawal_reference.json"


def _iso(d):
    try:
        return datetime.strptime(str(d), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def load_reference():
    ref = json.loads(REF_PATH.read_text())
    return {d["drug_key"].lower(): d for d in ref["drugs"]}


def match_drugs(treatment_str, ref):
    """The reference entries whose drug_key appears (word-boundary substring) in the treatment
    string. Longer keys first so 'b-complex' wins over a bare 'b' were one added."""
    s = str(treatment_str or "").lower()
    hits = []
    for key in sorted(ref, key=len, reverse=True):
        if re.search(r"(?<![a-z0-9])" + re.escape(key), s):
            hits.append(ref[key])
    return hits


def _clear(treat_date, days):
    """Last day still WITHIN withdrawal is treat_date+days; food is clear the day AFTER.
    days=0 (nutritional) → clear immediately (clear_date == treat_date)."""
    return treat_date + timedelta(days=int(days))


def withdrawal_for_treatment(sheep_id, t, ref, as_of):
    """Typed per-(treatment, drug) records. status ∈ in_withdrawal | clear | unknown_interval |
    no_withdrawal ; plus a single 'unrecognized' record when a treatment matched no drug."""
    td = _iso(t.get("date"))
    tstr = t.get("treatment")
    if td is None:
        return [{"sheep_id": sheep_id, "treatment": tstr, "date": None,
                 "status": "unknown_interval", "why": "treatment has no parseable date — cannot bracket a withdrawal"}]
    drugs = match_drugs(tstr, ref)
    if not drugs:
        return [{"sheep_id": sheep_id, "treatment": tstr, "date": td.isoformat(),
                 "status": "unrecognized", "why": "no recognized drug in this treatment string — review manually; do not assume food-safe"}]
    out = []
    for d in drugs:
        base = {"sheep_id": sheep_id, "treatment": tstr, "date": td.isoformat(),
                "drug": d["drug_key"], "generic": d.get("generic"), "class": d.get("class")}
        for kind in ("meat", "milk"):
            days = d.get(f"withdrawal_days_{kind}")
            if d["status"] == "NEEDS_VET_CONFIRMATION" or days is None:
                out.append({**base, "kind": kind, "status": "unknown_interval",
                            "why": f"{d['drug_key']} has no vet-confirmed {kind} withdrawal — obtain from vet/FARAD before release"})
                continue
            clear_on = _clear(td, days)
            if days == 0:
                out.append({**base, "kind": kind, "status": "no_withdrawal", "clear_date": clear_on.isoformat()})
            elif as_of <= clear_on:
                out.append({**base, "kind": kind, "status": "in_withdrawal", "clear_date": clear_on.isoformat(),
                            "days_remaining": (clear_on - as_of).days})
            else:
                out.append({**base, "kind": kind, "status": "clear", "clear_date": clear_on.isoformat()})
    return out


def scan(db, ref, as_of):
    recs = []
    for s in db.get("sheep", []):
        for t in (s.get("health", {}).get("treatments") or []):
            if isinstance(t, dict):
                recs.extend(withdrawal_for_treatment(s["id"], t, ref, as_of))
    return recs


def gaps(db, ref):
    """The confirmation worklist: every drug actually USED in the flock whose interval is not
    vet-confirmed, with how many treatment events invoke it."""
    used = {}
    for s in db.get("sheep", []):
        for t in (s.get("health", {}).get("treatments") or []):
            if not isinstance(t, dict):
                continue
            for d in match_drugs(t.get("treatment"), ref):
                if d["status"] == "NEEDS_VET_CONFIRMATION":
                    used[d["drug_key"]] = used.get(d["drug_key"], 0) + 1
    return sorted(({"drug": k, "generic": ref[k].get("generic"), "class": ref[k].get("class"),
                    "events": v, "source": ref[k].get("source")} for k, v in used.items()),
                  key=lambda r: -r["events"])


def main():
    ap = argparse.ArgumentParser(description="Meat/milk withdrawal clearance (read-only, food-safety)")
    ap.add_argument("--as-of", default=None)
    ap.add_argument("--gaps", action="store_true", help="the confirmation worklist (drugs used, no confirmed interval)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    as_of = _iso(args.as_of) if args.as_of else date.today()
    if args.as_of and as_of is None:
        print(f"ERROR: --as-of {args.as_of!r} is not an ISO date", file=sys.stderr)
        return 2
    db = json.loads(DB_PATH.read_text())
    ref = load_reference()

    if args.gaps:
        g = gaps(db, ref)
        if args.json:
            print(json.dumps(g, indent=2)); return 0
        print(f"Withdrawal confirmation worklist — {len(g)} drug(s) in use with NO vet-confirmed interval\n")
        for r in g:
            print(f"  {r['drug']:14} {r['class']:12} {r['events']:2} event(s)  ({r['generic']})")
        print("\n  Enter a vet/FARAD-confirmed meat (and milk) interval for each in"
              "\n  data/withdrawal_reference.json, set status 'vet_confirmed'. Until then any animal"
              "\n  treated with these reads UNKNOWN — never food-safe by omission.")
        return 0

    recs = scan(db, ref, as_of)
    if args.json:
        print(json.dumps({"as_of": as_of.isoformat(), "records": recs}, indent=2)); return 0

    inw = [r for r in recs if r["status"] == "in_withdrawal"]
    unk = [r for r in recs if r["status"] == "unknown_interval"]
    unrec = [r for r in recs if r["status"] == "unrecognized"]
    # collapse unknowns/in-withdrawal to per-animal worst case for the headline
    print(f"Withdrawal check — as of {as_of.isoformat()}: "
          f"{len({r['sheep_id'] for r in inw})} animal(s) in a CONFIRMED withdrawal, "
          f"{len({r['sheep_id'] for r in unk})} with an UNKNOWN interval\n")
    if inw:
        print("IN WITHDRAWAL (confirmed interval, not yet clear):")
        for r in sorted(inw, key=lambda r: r["clear_date"]):
            print(f"  {r['sheep_id']:24} {r['drug']:12} {r['kind']:4} clear {r['clear_date']} ({r['days_remaining']}d left)")
        print()
    if unk:
        print("UNKNOWN INTERVAL (treated with a drug lacking a vet-confirmed withdrawal — DO NOT release):")
        seen = set()
        for r in unk:
            k = (r["sheep_id"], r.get("drug"), r["date"])
            if k in seen:
                continue
            seen.add(k)
            print(f"  {r['sheep_id']:24} {r.get('drug','?'):12} treated {r['date']} — {r['why']}")
        print()
    if unrec:
        print("UNRECOGNIZED treatment strings (review — do not assume food-safe):")
        for r in unrec:
            print(f"  {r['sheep_id']:24} {r['date']}  {r['treatment']!r}")
        print()
    print("  Read-only, food-safety. Numbers are vet/operator-owned (data/withdrawal_reference.json);"
          "\n  this tool computes dates and names gaps, and never asserts an animal is safe to release.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
