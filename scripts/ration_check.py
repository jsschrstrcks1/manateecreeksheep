#!/usr/bin/env python3
"""ration_check.py — ration adequacy vs NRC + dry-matter-intake estimate (MCS-23). READ-ONLY.

Two questions: how much dry matter should this animal eat per day (from its real body weight), and
does a given ration MEET the NRC nutrient requirement for its class? The first is computable now
from the flock's body weights; the second needs NRC requirement values, which are lab/reference
data the operator enters — this tool authors none, and reports 'unknown' (never 'adequate') for a
nutrient whose requirement is not on file.

  - dmi_estimate(weight_lb, animal_class): expected daily dry-matter intake = weight * a documented
    rule-of-thumb fraction (data/nutrition_requirements.json). Complete on real weights.
  - ration_adequacy(supplied, animal_class): per-nutrient supplied-vs-required verdict
    (adequate | deficient | excess | unknown_requirement), once NRC requirements are entered.
  - flock_dmi(db, animal_class): per-animal DMI estimate for the weighed, living flock.

    python3 scripts/ration_check.py                          # per-animal DMI estimate (maintenance)
    python3 scripts/ration_check.py --class early_lactation   # DMI for a production stage
    python3 scripts/ration_check.py --check TDN=60,CP=14 --class late_gestation   # adequacy of a ration
    python3 scripts/ration_check.py --json
"""
import argparse
import json
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "flock_database.json"
REQ_PATH = Path(__file__).resolve().parent.parent / "data" / "nutrition_requirements.json"

_NUTRIENTS = {"tdn": "tdn_pct", "cp": "cp_pct", "ca": "ca_pct", "p": "p_pct"}


def load_requirements():
    return json.loads(REQ_PATH.read_text()).get("classes", {})


def dmi_estimate(weight_lb, animal_class, reqs=None):
    """Expected daily dry-matter intake (lb) = weight * dmi_pct_bodyweight for the class. None if
    weight is not numeric or the class is unknown."""
    reqs = reqs if reqs is not None else load_requirements()
    if not isinstance(weight_lb, (int, float)) or isinstance(weight_lb, bool):
        return None
    cls = reqs.get(animal_class)
    if not cls or not isinstance(cls.get("dmi_pct_bodyweight"), (int, float)):
        return None
    return round(weight_lb * cls["dmi_pct_bodyweight"], 2)


def ration_adequacy(supplied, animal_class, reqs=None):
    """Per-nutrient verdict comparing a supplied ration (dict of nutrient->%DM, keys tdn/cp/ca/p)
    against the NRC requirement for the class. A nutrient with no requirement on file is
    'unknown_requirement' — never silently 'adequate'."""
    reqs = reqs if reqs is not None else load_requirements()
    cls = reqs.get(animal_class)
    if cls is None:
        return {"error": f"unknown animal class {animal_class!r}"}
    out = {}
    for short, key in _NUTRIENTS.items():
        req = cls.get(key)
        sup = supplied.get(short)
        if sup is None:
            out[short] = {"status": "not_supplied", "required": req}
        elif req is None:
            out[short] = {"status": "unknown_requirement", "supplied": sup,
                          "why": "NRC requirement not entered for this class — cannot judge adequacy"}
        elif sup < req:
            out[short] = {"status": "deficient", "supplied": sup, "required": req,
                          "shortfall": round(req - sup, 2)}
        elif sup > req * 1.5:
            out[short] = {"status": "excess", "supplied": sup, "required": req}
        else:
            out[short] = {"status": "adequate", "supplied": sup, "required": req}
    return out


def flock_dmi(db, animal_class, reqs=None):
    reqs = reqs if reqs is not None else load_requirements()
    rows = []
    for s in db.get("sheep", []):
        if s.get("status") != "alive" or s.get("on_property") is False:
            continue
        w = s.get("weight_lbs")
        dmi = dmi_estimate(w, animal_class, reqs)
        if dmi is not None:
            rows.append({"id": s["id"], "name": s.get("name"), "weight_lb": w, "dmi_lb": dmi})
    rows.sort(key=lambda r: -r["dmi_lb"])
    return rows


def _parse_supplied(spec):
    """'TDN=60,CP=14' -> {'tdn':60.0,'cp':14.0}."""
    out = {}
    for part in str(spec or "").split(","):
        if "=" in part:
            k, v = part.split("=", 1)
            try:
                out[k.strip().lower()] = float(v)
            except ValueError:
                pass
    return out


def main():
    ap = argparse.ArgumentParser(description="Ration adequacy + DMI estimate (read-only)")
    ap.add_argument("--class", dest="cls", default="maintenance",
                    help="animal class (maintenance/late_gestation/early_lactation/late_lactation/growing_lamb)")
    ap.add_argument("--check", default=None, help="ration nutrients, e.g. TDN=60,CP=14 — check adequacy")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    reqs = load_requirements()
    if args.cls not in reqs:
        print(f"ERROR: unknown class {args.cls!r}; known: {', '.join(reqs)}", file=sys.stderr); return 2

    if args.check is not None:
        supplied = _parse_supplied(args.check)
        verdict = ration_adequacy(supplied, args.cls, reqs)
        if args.json:
            print(json.dumps({"class": args.cls, "supplied": supplied, "adequacy": verdict}, indent=2)); return 0
        print(f"Ration adequacy — class {args.cls}\n")
        for n, v in verdict.items():
            print(f"  {n.upper():4} {v['status']:20} " + json.dumps({k: v[k] for k in v if k != 'status'}))
        print("\n  'unknown_requirement' means the NRC value is not in data/nutrition_requirements.json —"
              "\n  enter it from NRC (2007) to enable the judgment. Read-only; operator/vet decides.")
        return 0

    db = json.loads(DB_PATH.read_text())
    rows = flock_dmi(db, args.cls, reqs)
    if args.json:
        print(json.dumps({"class": args.cls, "dmi": rows}, indent=2)); return 0
    pct = reqs[args.cls]["dmi_pct_bodyweight"]
    print(f"Estimated daily dry-matter intake — class {args.cls} ({pct*100:g}% of body weight), "
          f"{len(rows)} weighed animals\n")
    for r in rows:
        print(f"  {(r['name'] or r['id'])[:28]:28} {r['weight_lb']:5g} lb  ->  {r['dmi_lb']:5g} lb DM/day")
    print("\n  DMI is a documented rule of thumb, not the NRC intake table. Nutrient adequacy needs"
          "\n  NRC requirements entered (currently null): ration_check.py --check TDN=..,CP=.. --class ..")
    return 0


if __name__ == "__main__":
    sys.exit(main())
