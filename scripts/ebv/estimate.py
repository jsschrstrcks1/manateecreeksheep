"""Estimate breeding values.

Methods (in order of preference per animal):

  1. NSIP-anchored (if external NSIP EBV is loaded for this animal)
     EBV = NSIP_EBV directly. Highest accuracy.

  2. BLUP-light (own phenotype + ancestor info)
     For animals with their own measurement:
         EBV_i = h² × (P_i − μ_group) + (1 − h²) × MidParent_EBV
     If no group statistics available:
         EBV_i = h² × (P_i − flock_mean)

  3. Mid-parent (no own data)
     EBV_i = 0.5 × (EBV_sire + EBV_dam)

  4. Ancestor propagation (no parents in flock; some named ancestors)
     EBV_i = Σ over ancestors a:  path_coef(a, i) × EBV_a

  5. Default zero (no data at all)

Accuracy (rough): 0.5 for ancestor-only; 0.7 for mid-parent; 0.8+ when
own phenotype is present alongside ancestor data.
"""
from __future__ import annotations
from statistics import mean, pstdev
from typing import Iterable

from pedigree import relationship, path_coefficient
from traits import TRAITS, contemporary_group_key


def group_means(phenotypes: dict, ped: dict, sheep_by_id: dict) -> dict:
    """Mean phenotype per contemporary group + overall flock mean.

    Returns {"groups": {group_key: mean}, "flock": flock_mean}.
    """
    groups = {}
    all_vals = []
    for sid, val in phenotypes.items():
        if sid not in sheep_by_id:
            continue
        key = contemporary_group_key(sheep_by_id[sid])
        groups.setdefault(key, []).append(val)
        all_vals.append(val)
    group_avg = {k: mean(v) for k, v in groups.items()}
    flock_avg = mean(all_vals) if all_vals else 0.0
    return {"groups": group_avg, "flock": flock_avg, "n": len(all_vals)}


def compute_trait_ebvs(
    trait_code: str,
    phenotypes: dict,
    ped: dict,
    sheep_by_id: dict,
    nsip_ebvs: dict | None = None,
    max_iterations: int = 6,
) -> dict:
    """Compute EBVs for all animals in the pedigree for one trait.

    Iterates so that mid-parent EBVs propagate to grand-offspring etc.
    """
    nsip_ebvs = nsip_ebvs or {}
    trait = TRAITS[trait_code]
    h2 = trait["h2"]
    means = group_means(phenotypes, ped, sheep_by_id)

    # Initialize EBV table
    ebv = {sid: 0.0 for sid in ped}
    method = {sid: "default-zero" for sid in ped}
    accuracy = {sid: 0.0 for sid in ped}

    # Apply NSIP anchors first
    for sid, val in nsip_ebvs.items():
        if sid in ebv:
            ebv[sid] = float(val)
            method[sid] = "nsip-anchored"
            accuracy[sid] = 0.95

    # Iterate: each pass updates EBVs based on own data + current parent EBVs.
    for it in range(max_iterations):
        changed = 0
        for sid, rec in ped.items():
            if method[sid] == "nsip-anchored":
                continue
            sheep = sheep_by_id.get(sid, {})
            own_phen = phenotypes.get(sid)
            sire, dam = rec.get("sire"), rec.get("dam")
            sire_ebv = ebv.get(sire, 0.0) if sire in ebv else 0.0
            dam_ebv = ebv.get(dam, 0.0) if dam in ebv else 0.0
            mid_parent_ebv = 0.5 * (sire_ebv + dam_ebv)

            if own_phen is not None:
                # BLUP-light: own deviation + mid-parent.
                # Use flock mean if contemporary group has fewer than 2 animals
                # (a single-member group gives a meaningless 0 deviation).
                group_key = contemporary_group_key(sheep)
                group_mean_v = means["groups"].get(group_key, means["flock"])
                group_size = sum(
                    1 for s in sheep_by_id.values()
                    if contemporary_group_key(s) == group_key and s["id"] in phenotypes
                )
                if group_size < 2:
                    group_mean_v = means["flock"]
                deviation = own_phen - group_mean_v
                new_ebv = h2 * deviation + (1.0 - h2) * mid_parent_ebv
                new_method = "blup-light"
                new_acc = min(0.90, 0.55 + 0.20 * (1 if mid_parent_ebv != 0 else 0) + 0.15)
            elif sire in ped and dam in ped:
                # Mid-parent
                new_ebv = mid_parent_ebv
                new_method = "mid-parent"
                new_acc = min(0.75, 0.35 + 0.20 * (1 if sire_ebv != 0 else 0) + 0.20 * (1 if dam_ebv != 0 else 0))
            else:
                new_ebv = 0.0
                new_method = "default-zero"
                new_acc = 0.0

            # Update if EBV value changed OR method category changed.
            if abs(new_ebv - ebv[sid]) > 1e-6 or method[sid] != new_method:
                ebv[sid] = new_ebv
                method[sid] = new_method
                accuracy[sid] = new_acc
                changed += 1
        if changed == 0:
            break

    return {
        "trait": trait_code,
        "trait_name": trait["name"],
        "h2": h2,
        "units": trait["units"],
        "direction": trait["direction"],
        "flock_mean_phenotype": means["flock"],
        "n_with_phenotype": means["n"],
        "ebvs": {sid: round(ebv[sid], 4) for sid in ped},
        "methods": method,
        "accuracy": {sid: round(accuracy[sid], 2) for sid in ped},
    }


def rank_for_trait(result: dict, top_n: int = 20, sheep_by_id: dict | None = None) -> list:
    """Return top-N animals for a single trait."""
    ebvs = result["ebvs"]
    rows = sorted(ebvs.items(), key=lambda kv: -kv[1])
    out = []
    for sid, val in rows[:top_n]:
        row = {
            "id": sid,
            "ebv": val,
            "method": result["methods"][sid],
            "accuracy": result["accuracy"][sid],
        }
        if sheep_by_id and sid in sheep_by_id:
            row["pen"] = sheep_by_id[sid].get("pen")
            row["status"] = sheep_by_id[sid].get("status")
            row["sex"] = sheep_by_id[sid].get("sex")
        out.append(row)
    return out
