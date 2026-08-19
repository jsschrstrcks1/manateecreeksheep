#!/usr/bin/env python3
"""fecrt_check.py — FECRT (Fecal Egg Count Reduction Test) drench-check (MCS-30).

The one question this answers: DO THE DEWORMERS STILL WORK HERE? Haemonchus resistance is
regional and grows silently; the only honest measure is a paired FEC — a count at the drench,
and a count 10-14 days after — reduced into a percentage per drug class.

    reduction% = (pre_epg - post_epg) / pre_epg * 100

Efficacy classes (WAAVP-style, per drug CLASS not brand — resistance is shared within a class):
    >= 95%   effective        (susceptible)
    90-95%   suspected        (early resistance — watch, confirm)
    < 90%    resistant        (the drench is failing here)

READ-ONLY and WELFARE-BOUND: this computes and reports; it never withholds treatment. A
"resistant" verdict is an argument to CHANGE class / add refugia management / confirm with a
larger sample — never to stop treating an anemic animal. Thresholds and the drug->class map
are named constants, operator-tunable; regional lab guidance overrides.

HONEST DATA STATE: a FECRT needs a pre AND a post FEC bracketing one drench. Where the flock
record lacks that pairing (as it largely does today — FEC has been recorded rarely), the tool
says so per drench instead of inventing a reduction. Naming the gap IS the deliverable — it
tells you exactly which counts to start taking.

    python3 scripts/fecrt_check.py            # every drench, paired where possible
    python3 scripts/fecrt_check.py --table    # the does-it-work-here summary per drug class
    python3 scripts/fecrt_check.py --json
"""
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "flock_database.json"

# Drug -> anthelmintic CLASS. Supportive meds (iron, B12, Nuflor/antibiotic, nutridrench) are
# NOT anthelmintics and never start a FECRT. Matched case-insensitively as substrings; the
# table is the single source of which words in a free-text treatment string are dewormers.
DRUG_CLASS = {
    "ivermectin": "macrocyclic-lactone",
    "moxidectin": "macrocyclic-lactone",
    "doramectin": "macrocyclic-lactone",
    "eprinomectin": "macrocyclic-lactone",
    "fenbendazole": "benzimidazole",
    "albendazole": "benzimidazole",
    "oxfendazole": "benzimidazole",
    "safe-guard": "benzimidazole",
    "safeguard": "benzimidazole",
    "panacur": "benzimidazole",
    "valbazen": "benzimidazole",
    "levamisole": "imidazothiazole",
    "prohibit": "imidazothiazole",
    "levasole": "imidazothiazole",
}

EFFECTIVE = 95.0     # >= 95% reduction = effective / susceptible
SUSPECT = 90.0       # 90-95% = suspected resistance
POST_MIN_DAYS = 10   # a valid post-drench FEC is 10-14 days out (window bounds)
POST_MAX_DAYS = 14
POST_TOLERANCE = 7   # accept a slightly-off post window but FLAG it (7-21d) rather than drop it
PRE_MAX_DAYS = 3     # a pre-drench FEC counts if within 3 days before/on the drench


def _iso(d):
    try:
        return datetime.strptime(str(d), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def anthelmintic_classes(treatment_str):
    """The set of anthelmintic CLASSES named in a free-text treatment string (a combo drench
    like 'Ivermectin + Fenbendazole' names two — both get a FECRT attempt)."""
    s = str(treatment_str or "").lower()
    return sorted({cls for drug, cls in DRUG_CLASS.items() if re.search(r"\b" + re.escape(drug), s)})


def _fecs(sheep):
    out = []
    for e in (sheep.get("health", {}).get("fec_history") or []):
        d = _iso(e.get("date")) if isinstance(e, dict) else None
        if d is not None and isinstance(e.get("fec"), (int, float)):
            out.append((d, float(e["fec"])))
    return sorted(out)


def fecrt_for_drench(sheep, drench_date, drug_class):
    """Pair a pre and post FEC around one drench. Returns a typed record — never a guessed
    reduction. status ∈ complete | no_pre | no_post | no_fec."""
    fecs = _fecs(sheep)
    base = {"sheep_id": sheep.get("id"), "date": drench_date.isoformat(), "drug_class": drug_class}
    if not fecs:
        return {**base, "status": "no_fec", "why": "no FEC on record for this animal — a FECRT needs a count at the drench and one 10-14d later"}
    pre = [(d, v) for d, v in fecs if -PRE_MAX_DAYS <= (d - drench_date).days <= 0]
    post = [(d, v, (d - drench_date).days) for d, v in fecs if POST_MIN_DAYS - POST_TOLERANCE <= (d - drench_date).days <= POST_MAX_DAYS + POST_TOLERANCE]
    if not pre:
        return {**base, "status": "no_pre", "why": f"no FEC within {PRE_MAX_DAYS}d before the drench — cannot measure the starting load"}
    if not post:
        return {**base, "status": "no_post", "why": f"no FEC {POST_MIN_DAYS}-{POST_MAX_DAYS}d after the drench — the reduction cannot be computed"}
    pre_epg = pre[-1][1]
    post_d, post_epg, post_off = min(post, key=lambda p: abs(p[2] - 12))
    flags = []
    if not (POST_MIN_DAYS <= post_off <= POST_MAX_DAYS):
        flags.append(f"post FEC {post_off}d out (ideal {POST_MIN_DAYS}-{POST_MAX_DAYS})")
    if pre_epg <= 0:
        return {**base, "status": "no_pre", "why": "pre-drench FEC is 0 — no egg load to reduce; FECRT is undefined"}
    reduction = round((pre_epg - post_epg) / pre_epg * 100, 1)
    verdict = "effective" if reduction >= EFFECTIVE else "suspected" if reduction >= SUSPECT else "resistant"
    return {**base, "status": "complete", "pre_epg": pre_epg, "post_epg": post_epg,
            "post_offset_days": post_off, "reduction_pct": reduction, "verdict": verdict, "flags": flags}


def all_drenches(db):
    """Every anthelmintic drench across the flock, each expanded per drug class it contained."""
    out = []
    for s in db.get("sheep", []):
        for t in (s.get("health", {}).get("treatments") or []):
            if not isinstance(t, dict):
                continue
            d = _iso(t.get("date"))
            classes = anthelmintic_classes(t.get("treatment"))
            for cls in classes:
                if d is None:
                    out.append({"sheep_id": s.get("id"), "date": None, "drug_class": cls,
                                "status": "no_fec", "why": "drench has no date — cannot bracket a FECRT"})
                else:
                    out.append(fecrt_for_drench(s, d, cls))
    return out


def efficacy_table(drenches):
    """The does-it-work-here summary per drug class: completed FECRTs aggregated, plus a count
    of drenches that could not be measured (the gap that needs FEC data)."""
    table = {}
    for r in drenches:
        cls = r["drug_class"]
        t = table.setdefault(cls, {"drug_class": cls, "complete": 0, "reductions": [],
                                   "verdicts": {"effective": 0, "suspected": 0, "resistant": 0}, "unmeasured": 0})
        if r["status"] == "complete":
            t["complete"] += 1
            t["reductions"].append(r["reduction_pct"])
            t["verdicts"][r["verdict"]] += 1
        else:
            t["unmeasured"] += 1
    for t in table.values():
        if t["reductions"]:
            t["mean_reduction_pct"] = round(sum(t["reductions"]) / len(t["reductions"]), 1)
            worst = min(t["reductions"])
            t["status_here"] = "effective" if worst >= EFFECTIVE else "suspected" if worst >= SUSPECT else "resistant"
        else:
            t["mean_reduction_pct"] = None
            t["status_here"] = "unknown_no_paired_fec"
        del t["reductions"]
    return table


def main():
    ap = argparse.ArgumentParser(description="FECRT drench-check (read-only, welfare-bound)")
    ap.add_argument("--table", action="store_true", help="does-it-work-here summary per drug class")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    db = json.loads(DB_PATH.read_text())
    drenches = all_drenches(db)
    table = efficacy_table(drenches)

    if args.json:
        print(json.dumps({"drenches": drenches, "efficacy_table": list(table.values())}, indent=2))
        return 0

    if args.table:
        print("Does-it-work-here — anthelmintic efficacy per drug class (FECRT-derived)\n")
        if not table:
            print("  No anthelmintic drenches on record.")
        for t in sorted(table.values(), key=lambda x: x["drug_class"]):
            mr = f"{t['mean_reduction_pct']:g}% mean reduction" if t["mean_reduction_pct"] is not None else "no paired FEC yet"
            print(f"  {t['drug_class']:20} {t['status_here']:22} ({t['complete']} measured, {t['unmeasured']} unmeasured; {mr})")
        print("\n  'unknown_no_paired_fec' is the honest state for a class never FECRT-tested here —"
              "\n  start taking a FEC at the drench and one 10-14d later to fill it. Read-only; welfare first.")
        return 0

    complete = [r for r in drenches if r["status"] == "complete"]
    gaps = [r for r in drenches if r["status"] != "complete"]
    print(f"FECRT drench-check — {len(drenches)} anthelmintic drench-events, "
          f"{len(complete)} measurable, {len(gaps)} unmeasurable (missing paired FEC)\n")
    for r in complete:
        fl = ("  [" + "; ".join(r["flags"]) + "]") if r["flags"] else ""
        print(f"  {r['sheep_id']:26} {r['date']} {r['drug_class']:20} "
              f"{r['pre_epg']:g}→{r['post_epg']:g} epg = {r['reduction_pct']:g}% {r['verdict'].upper()}{fl}")
    if gaps:
        from collections import Counter
        c = Counter(r["status"] for r in gaps)
        print(f"\n  Unmeasurable ({len(gaps)}): " + ", ".join(f"{k}={v}" for k, v in c.items()))
        print("  These name exactly which counts are missing — the FECRT can only run on paired FECs.")
    print("\n  Read-only, welfare-bound: a 'resistant' verdict argues to change drug class / add"
          "\n  refugia management, never to withhold treatment from an animal that needs it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
