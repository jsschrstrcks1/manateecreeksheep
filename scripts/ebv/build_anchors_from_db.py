#!/usr/bin/env python3
"""Generate data/ebv/nsip_anchors.json from sheep records' nsip_ebvs fields.

Converts NSIP-native EBV values into the simpler per-trait dict format
that compute_ebvs.py uses as anchor input.

Mapping (NSIP scale → our pipeline trait):
    NSIP WFEC (negative = better, eggs/g)     → PR (we negate so + = better)
    NSIP PFEC (negative = better, eggs/g)     → PR (averaged with WFEC if both)
    NSIP PWWT (lb)                            → PWT
    NSIP WWT  (lb)                            → WWT
    NSIP NLB  (proxy)                         → NLW

Scale note: the resulting EBVs are on NSIP-native scale (egg counts for
PR), NOT the flock-internal FAMACHA-inverted scale. Treat the
anchored-animal rankings as a separate confidence band.

Usage:
    python3 scripts/ebv/build_anchors_from_db.py
"""
from __future__ import annotations
import json
from pathlib import Path


def get_nsip_val(nsip: dict, group: str, trait: str):
    """Pull a single trait value from a sheep's nsip_ebvs dict."""
    g = nsip.get(group, {}) or {}
    t = g.get(trait, {}) or {}
    return t.get("val") if isinstance(t, dict) else None


def main():
    with open("data/flock_database.json") as f:
        db = json.load(f)

    anchors = {
        "_documentation": {
            "generated_from": "sheep[].nsip_ebvs by scripts/ebv/build_anchors_from_db.py",
            "scale_note": ("EBVs are NSIP-native scale (egg counts for FEC). "
                           "Pipeline uses sign convention: positive PR = more resistant, "
                           "so we negate WFEC and PFEC when populating PR."),
            "mapping": {
                "PR": "Average of -WFEC and -PFEC",
                "PWT": "NSIP PWWT (post-weaning weight EBV, lb)",
                "WWT": "NSIP WWT (weaning weight EBV, lb)",
                "NLW": "NSIP NLB (number lambs born, proxy)",
            },
        }
    }

    n_animals = 0
    for s in db["sheep"]:
        nsip = s.get("nsip_ebvs")
        if not nsip or not isinstance(nsip, dict):
            continue
        wfec = get_nsip_val(nsip, "parasite_resistance", "WFEC")
        pfec = get_nsip_val(nsip, "parasite_resistance", "PFEC")
        pwwt = get_nsip_val(nsip, "weight_traits", "PWWT")
        wwt = get_nsip_val(nsip, "weight_traits", "WWT")
        nlb = get_nsip_val(nsip, "reproduction", "NLB")
        entry = {}
        # PR from NSIP WFEC: negated (NSIP WFEC negative = more resistant
        # → flip so positive PR = more resistant).
        # PFEC convention is ambiguous in source data — recorded but not
        # used as a PR anchor here.
        if wfec is not None:
            entry["PR"] = round(-wfec, 4)
            entry["PR_source"] = f"NSIP WFEC={wfec} (negated; positive PR = more resistant)"
            if pfec is not None:
                entry["PR_pfec_recorded"] = pfec  # for reference, not used
        if pwwt is not None:
            entry["PWT"] = pwwt
            entry["PWT_source"] = "NSIP PWWT"
        if wwt is not None:
            entry["WWT"] = wwt
            entry["WWT_source"] = "NSIP WWT"
        if nlb is not None:
            entry["NLW"] = nlb
            entry["NLW_source"] = "NSIP NLB (proxy for NLW)"
        # US Hair index for context
        us = (nsip.get("us_hair_composite_index") or {}).get("val") if isinstance(nsip.get("us_hair_composite_index"), dict) else None
        if us is not None:
            entry["_us_hair_index"] = us
        entry["_progeny"] = nsip.get("progeny_evaluated")
        entry["_flocks"] = nsip.get("flocks_represented")
        entry["_snapshot_date"] = nsip.get("snapshot_date")
        entry["_label"] = s.get("name")
        if entry.get("PR") is not None or entry.get("PWT") is not None or entry.get("WWT") is not None or entry.get("NLW") is not None:
            anchors[s["id"]] = entry
            n_animals += 1

    out = Path("data/ebv/nsip_anchors.json")
    with open(out, "w") as f:
        json.dump(anchors, f, indent=2, ensure_ascii=False)
    print(f"Wrote {out} with anchors for {n_animals} animals")


if __name__ == "__main__":
    main()
