"""Standard lamb weight adjustment (MCS-27). Pure functions, no I/O.

Soli Deo Gloria.

Adjusted 60-day weaning weight, the NSIP-lineage method (sources: Penn State
Extension "Ram Selection Principles"; NSIP age-adjustment literature, J. Anim. Sci.
— the formula interpolates actual growth to a common age, then multiplies by
factors for dam age and birth-rearing type so singles raised alone don't look
genetically superior to twins that shared a dam):

    est_60d = ((wean_wt - birth_wt) / age_at_weaning_days) * 60 + birth_wt
    adjusted = est_60d * dam_age_factor * birth_rear_factor [* sex_factor]

FACTOR TABLE DISCIPLINE: every factor row carries its source. The seed rows below
are the two examples the PSU Extension page states outright (dam 2yo = 1.08,
twin-raised-as-twin = 1.21, generic-breed factors); the REST of the generic table
must be filled FROM the NSIP/SID Sheep Production Handbook tables and cited on
entry — an unsourced multiplier silently reshapes every selection decision.
Missing factor => None returned and the caller says UNADJUSTED, never a guess.
"""

# (category, key) -> {"factor": float, "source": str}
# Seeded ONLY with values stated outright by the cited source; extend from the
# SID/NSIP tables with a source string per row.
FACTORS = {
    ("dam_age", "2"): {"factor": 1.08,
                       "source": "PSU Extension, Ram Selection Principles (generic breed)"},
    ("dam_age", "3-6"): {"factor": 1.00,
                         "source": "baseline mature dam (definitionally 1.00)"},
    ("birth_rear", "1-1"): {"factor": 1.00,
                            "source": "baseline single-raised-single (definitionally 1.00)"},
    ("birth_rear", "2-2"): {"factor": 1.21,
                            "source": "PSU Extension, Ram Selection Principles (generic breed)"},
}


def est_60d_weight(birth_wt, wean_wt, age_days):
    """Interpolated 60-day weight. None on impossible inputs — never a guess."""
    for v in (birth_wt, wean_wt, age_days):
        if not isinstance(v, (int, float)) or isinstance(v, bool):
            return None
    if age_days <= 0 or wean_wt < birth_wt or birth_wt <= 0:
        return None
    return (wean_wt - birth_wt) / age_days * 60 + birth_wt


def adjusted_60d(birth_wt, wean_wt, age_days, dam_age_key=None, birth_rear_key=None,
                 factors=FACTORS):
    """(adjusted_weight, applied, missing): applied lists (category, key, factor,
    source) actually used; missing lists factor keys requested but absent from the
    table — the caller reports those as UNADJUSTED dimensions, never silently 1.0
    ... except the explicit baseline rows, which ARE 1.0 by definition."""
    w = est_60d_weight(birth_wt, wean_wt, age_days)
    if w is None:
        return None, [], []
    applied, missing = [], []
    for cat, key in (("dam_age", dam_age_key), ("birth_rear", birth_rear_key)):
        if key is None:
            continue
        row = factors.get((cat, key))
        if row:
            w *= row["factor"]
            applied.append((cat, key, row["factor"], row["source"]))
        else:
            missing.append((cat, key))
    return round(w, 2), applied, missing
