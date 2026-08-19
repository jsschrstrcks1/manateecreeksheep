#!/usr/bin/env python3
"""Mating outcome predictor (MCS-22): sire x dam -> trait possibilities, plain terms.

Composes what already exists — nothing new is invented here:
  PRNP Mendelian possibilities (MCS-15), per-locus Punnett sets (MCS-32),
  polygenic midparent expectation (labeled as the naive average it is),
  prospective inbreeding F (MCS-16, lower bound).

Usage: python3 scripts/mating_predictor.py --sire <id> --dam <id>
Soli Deo Gloria.
"""
import argparse
import json
import os
import sys
from pathlib import Path

_here = Path(__file__).parent
sys.path.insert(0, str(_here))
from lib.genetics import offspring_possibilities, resistance_note  # noqa: E402
from lib.pedigree import build_parents, prospective_f  # noqa: E402
from lib.trait_card import mendelian_cross  # noqa: E402

REPO = _here.parent
DB_PATH = Path(os.environ.get("FLOCK_DB_PATH") or REPO / "data" / "flock_database.json")


def predict(db, sire_id, dam_id):
    by_id = {s["id"]: s for s in db.get("sheep", [])}
    sire, dam = by_id.get(sire_id), by_id.get(dam_id)
    if not sire or not dam:
        raise SystemExit(f"unknown animal: {sire_id if not sire else dam_id}")
    sg, dg = sire.get("genetics") or {}, dam.get("genetics") or {}
    out = {"sire": sire_id, "dam": dam_id,
           "inbreeding_f": prospective_f(db, sire_id, dam_id, build_parents(db)),
           "prnp_171": None, "loci": {}, "polygenic_midparent": {}, "unpredictable": []}

    poss = offspring_possibilities(sg.get("prnp"), dg.get("prnp"))
    if poss:
        out["prnp_171"] = {g: {"p": p, "note": resistance_note(g)} for g, p in poss.items()}
    else:
        out["unpredictable"].append("PRNP-171 (one or both parents untyped — test, don't guess)")

    s_loci, d_loci = sg.get("loci") or {}, dg.get("loci") or {}
    for locus in sorted(set(s_loci) & set(d_loci)):
        cross = mendelian_cross(s_loci[locus].get("genotype"), d_loci[locus].get("genotype"))
        if cross:
            out["loci"][locus] = cross
    for locus in sorted(set(s_loci) ^ set(d_loci)):
        out["unpredictable"].append(f"locus {locus} (typed on one parent only)")

    s_poly, d_poly = sg.get("polygenic") or {}, dg.get("polygenic") or {}
    for trait in sorted(set(s_poly) & set(d_poly)):
        a, b = s_poly[trait].get("score"), d_poly[trait].get("score")
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            out["polygenic_midparent"][trait] = {
                "expectation": round((a + b) / 2, 1),
                "note": "naive midparent average — an expectation, not a promise; "
                        "polygenic traits scatter"}
    return out


def main():
    ap = argparse.ArgumentParser(description="Mating predictor (MCS-22)")
    ap.add_argument("--sire", required=True)
    ap.add_argument("--dam", required=True)
    args = ap.parse_args()
    db = json.load(open(DB_PATH))
    r = predict(db, args.sire, args.dam)
    print(f"{r['sire']} x {r['dam']}")
    print(f"  prospective lamb F = {r['inbreeding_f']:.4f} (lower bound — unknown parents count zero)")
    if r["prnp_171"]:
        for g, info in sorted(r["prnp_171"].items()):
            print(f"  PRNP-171 {g}: {info['p']:.0%} — {info['note']}")
    for locus, cross in r["loci"].items():
        print(f"  {locus}: " + "  ".join(f"{g} {p:.0%}" for g, p in sorted(cross.items())))
    for trait, e in r["polygenic_midparent"].items():
        print(f"  {trait}: midparent {e['expectation']}/5 ({e['note']})")
    for u in r["unpredictable"]:
        print(f"  UNPREDICTABLE: {u}")


if __name__ == "__main__":
    main()
