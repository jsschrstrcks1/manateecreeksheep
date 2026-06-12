#!/usr/bin/env python3
"""CLI: compute EBVs for every animal across all defined traits.

Usage:
    python3 scripts/ebv/compute_ebvs.py
    python3 scripts/ebv/compute_ebvs.py --nsip data/ebv/nsip_anchors.json
    python3 scripts/ebv/compute_ebvs.py --animal centralia-lamb-2026

Outputs:
    data/ebv/ebvs_2026-06-09.json   (per-animal, per-trait EBVs)
    data/ebv/rankings.md            (top-20 per trait, human-readable)

NSIP anchor file format (optional input):
    {
      "sheep_id_in_db": {"PR": 0.45, "WWT": 4.2, ...},
      ...
    }
"""
import argparse
import json
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from pedigree import load_pedigree, inbreeding
from traits import TRAITS
from extract import (
    load_db,
    extract_parasite_resistance,
    extract_adult_weight,
    extract_birth_weight,
    extract_adg,
    extract_lambs_weaned,
)
from estimate import compute_trait_ebvs, rank_for_trait


TRAIT_EXTRACTORS = {
    "PR": extract_parasite_resistance,
    "WWT": extract_birth_weight,   # nearest proxy for "growth potential at weaning"
    "PWT": extract_adult_weight,
    "ADG": extract_adg,
    "NLW": extract_lambs_weaned,
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nsip", help="Path to NSIP anchor JSON")
    ap.add_argument("--animal", help="Animal ID to focus the report on")
    ap.add_argument("--db", default="data/flock_database.json")
    ap.add_argument("--outdir", default="data/ebv")
    args = ap.parse_args()

    db = load_db(args.db)
    sheep_by_id = {s["id"]: s for s in db["sheep"]}
    ped = load_pedigree(args.db)
    nsip_anchors = {}
    if args.nsip and Path(args.nsip).exists():
        with open(args.nsip) as f:
            raw = json.load(f)
        nsip_anchors = {k: v for k, v in raw.items() if not k.startswith("_") and isinstance(v, dict)}

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()

    # Compute per-trait EBVs
    per_trait_results = {}
    for code in TRAIT_EXTRACTORS:
        phen = TRAIT_EXTRACTORS[code](db)
        anchors = {k: v.get(code) for k, v in nsip_anchors.items() if v.get(code) is not None}
        result = compute_trait_ebvs(code, phen, ped, sheep_by_id, nsip_ebvs=anchors)
        per_trait_results[code] = result

    # --- SCALE TAGGING + STANDARDIZATION -------------------------------
    # EBVs arrive on incompatible rulers:
    #   - NSIP-anchored PR is WFEC egg-count scale (±10-34)
    #   - flock blup-light PR is FAMACHA-inverted scale (±0.3-13)
    #   - NSIP weight is true lb-EBV (±4); flock weight is raw-bodyweight
    #     deviation (±60)
    # Mixing them on one ranking is invalid. We standardize each EBV to a
    # z-score WITHIN its own (trait, scale-pool), so "+2" means "2 SD above
    # the mean of your measurement type". default-zero (no data) animals are
    # given z=None and excluded from ranked tables (no-data != average).
    from statistics import mean as _mean, pstdev as _pstdev

    def scale_of(code, method):
        if method == "default-zero":
            return None  # no data
        if method == "nsip-anchored":
            return f"{code}:nsip"
        # blup-light / mid-parent off flock phenotypes (or mixed). Group them
        # as the flock-internal pool for this trait.
        return f"{code}:flock"

    # Collect values per (trait, scale-pool), excluding no-data
    pools = {}  # pool_key -> list of values
    for code in TRAIT_EXTRACTORS:
        for sid in ped:
            method = per_trait_results[code]["methods"][sid]
            pool = scale_of(code, method)
            if pool is None:
                continue
            v = per_trait_results[code]["ebvs"][sid]
            pools.setdefault(pool, []).append(v)
    pool_stats = {}
    for pool, vals in pools.items():
        m = _mean(vals) if vals else 0.0
        sd = _pstdev(vals) if len(vals) > 1 else 0.0
        pool_stats[pool] = (m, sd)

    def zscore(code, sid):
        method = per_trait_results[code]["methods"][sid]
        pool = scale_of(code, method)
        if pool is None:
            return None
        m, sd = pool_stats[pool]
        v = per_trait_results[code]["ebvs"][sid]
        if sd == 0:
            return 0.0
        return round((v - m) / sd, 3)

    # Combine into per-animal EBV table
    all_ids = sorted(ped.keys())
    per_animal = {}
    for sid in all_ids:
        rec = sheep_by_id.get(sid, {})
        per_animal[sid] = {
            "name": rec.get("name"),
            "sex": rec.get("sex"),
            "pen": rec.get("pen"),
            "status": rec.get("status"),
            "inbreeding_F": round(inbreeding(sid, ped), 4),
            "ebvs": {
                code: {
                    "value": per_trait_results[code]["ebvs"][sid],
                    "method": per_trait_results[code]["methods"][sid],
                    "accuracy": per_trait_results[code]["accuracy"][sid],
                    "scale": scale_of(code, per_trait_results[code]["methods"][sid]),
                    "z": zscore(code, sid),
                    "has_data": per_trait_results[code]["methods"][sid] != "default-zero",
                }
                for code in TRAIT_EXTRACTORS
            },
        }

    out_path = outdir / f"ebvs_{today}.json"
    with open(out_path, "w") as f:
        json.dump(
            {
                "computed_on": today,
                "n_animals": len(per_animal),
                "traits": {c: {k: v for k, v in TRAITS[c].items() if k != "notes"} for c in TRAIT_EXTRACTORS},
                "nsip_anchors_used": list(nsip_anchors.keys()) if nsip_anchors else [],
                "ebvs": per_animal,
            },
            f,
            indent=2,
        )
    print(f"Wrote {out_path}")

    # Rankings doc
    rank_lines = [f"# EBV Rankings — {today}\n\n"]
    rank_lines.append(f"Computed on {len(ped)} animals.\n\n")
    if nsip_anchors:
        rank_lines.append(f"NSIP anchors loaded for: {', '.join(nsip_anchors.keys())}\n\n")
    rank_lines.append("Method legend: nsip-anchored (acc 0.95) > blup-light (acc 0.85) > mid-parent (acc 0.55-0.75) > default-zero (no data).\n\n")
    rank_lines.append("**Ranked by z-score** (SD above the mean of the animal's own measurement pool), "
                      "so NSIP-scale and flock-scale EBVs are comparable. The `scale` column shows which "
                      "ruler each came from. No-data animals (default-zero) are EXCLUDED — absence of data "
                      "is not average performance.\n\n")
    for code in TRAIT_EXTRACTORS:
        r = per_trait_results[code]
        rank_lines.append(f"## {code} — {r['trait_name']} (h²={r['h2']:.2f})\n\n")
        rank_lines.append(f"Phenotypes recorded: {r['n_with_phenotype']} animals. Flock mean: {r['flock_mean_phenotype']:.3f} {r['units']}\n\n")
        rank_lines.append("| Rank | Animal | EBV | z | scale | Method | Acc | Sex | Pen |\n")
        rank_lines.append("|------|--------|-----|---|-------|--------|-----|-----|-----|\n")
        # Alive animals WITH data, ranked by z-score
        rows = []
        for sid in r["ebvs"]:
            if sheep_by_id.get(sid, {}).get("status") != "alive":
                continue
            if r["methods"][sid] == "default-zero":
                continue  # no data — exclude
            z = per_animal[sid]["ebvs"][code]["z"]
            rows.append((sid, r["ebvs"][sid], z))
        rows.sort(key=lambda t: -(t[2] if t[2] is not None else -999))
        for i, (sid, val, z) in enumerate(rows[:20], 1):
            rec = sheep_by_id.get(sid, {})
            sc = per_animal[sid]["ebvs"][code]["scale"] or "—"
            zs = f"{z:+.2f}" if z is not None else "—"
            rank_lines.append(
                f"| {i} | `{sid}` | {val:+.3f} | {zs} | {sc} | {r['methods'][sid]} | {r['accuracy'][sid]:.2f} | {rec.get('sex')} | {rec.get('pen')} |\n"
            )
        rank_lines.append("\n")

    ranks_path = outdir / f"rankings_{today}.md"
    with open(ranks_path, "w") as f:
        f.writelines(rank_lines)
    print(f"Wrote {ranks_path}")

    # Focused single-animal report
    if args.animal:
        sid = args.animal
        if sid not in per_animal:
            print(f"ERROR: {sid} not in pedigree", file=sys.stderr)
            sys.exit(1)
        focus = per_animal[sid]
        print(f"\n=== EBV report for {sid} ===")
        print(f"  Name: {focus['name']}, sex: {focus['sex']}, pen: {focus['pen']}, status: {focus['status']}")
        print(f"  Inbreeding F: {focus['inbreeding_F']:.4f}")
        for code, ebv_entry in focus["ebvs"].items():
            t = TRAITS[code]
            print(
                f"  {code:<5} ({t['name']:<25}) EBV={ebv_entry['value']:+.3f} {t['units']:<35} "
                f"method={ebv_entry['method']:<15} acc={ebv_entry['accuracy']:.2f}"
            )


if __name__ == "__main__":
    main()
