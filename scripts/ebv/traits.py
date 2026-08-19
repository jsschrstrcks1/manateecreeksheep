"""Trait definitions: heritability, sign conventions, contemporary-group keys.

Heritabilities are mid-range estimates from published meta-analyses on
hair-sheep populations (Katahdin/St Croix/Dorper).

Sources:
  - Notter 2012. The Katahdin breed: a model for sustainable hair-sheep
    production. SID Sheep Production Handbook.
  - Vanimisetti et al 2004. Inheritance of fecal egg count and packed
    cell volume in lambs naturally infected with gastrointestinal
    parasites. J Anim Sci 82: 1602-1611.
  - Borg et al 2009. Genetic parameters for production traits in
    Katahdin hair sheep. J Anim Sci 87: 3851-3858.

Sign convention:
  - Higher EBV = MORE desirable for that trait.
  - For FAMACHA and FEC (where lower raw values are better — less
    parasite burden), we INVERT during extraction so higher EBV
    consistently means more resistant.
"""

TRAITS = {
    "PR": {  # Parasite Resistance (from FAMACHA observations, inverted)
        "name": "Parasite Resistance",
        "long_name": "Parasite resistance (composite from FAMACHA history)",
        "h2": 0.25,
        "units": "FAMACHA-score-inverted-deviation",
        "direction": "higher_better",
        "notes": "Computed from FAMACHA scores: lower FAMACHA = more resistant. We use deviation from contemporary mean, inverted so higher EBV = more resistant.",
    },
    "WWT": {  # Weaning weight
        "name": "Weaning Weight",
        "long_name": "60-day weaning weight",
        "h2": 0.30,
        "units": "lb",
        "direction": "higher_better",
        "notes": "Adjusted to 60-day equivalent. When only adult weight is recorded, we back-calculate via ADG.",
    },
    "PWT": {  # Post-weaning weight
        "name": "Post-Weaning Weight",
        "long_name": "120-day post-weaning weight",
        "h2": 0.35,
        "units": "lb",
        "direction": "higher_better",
        "notes": "Adjusted to 120-day equivalent. FLOCK-INTERNAL SOURCE: only true post-weaning weights — NOT adult weight (which would conflate age with growth). For most flock animals this is no-data unless NSIP-anchored. Adult weight goes to MWT instead.",
    },
    "MWT": {  # Mature (adult) weight — size/frame selection
        "name": "Mature Weight",
        "long_name": "Adult/mature body weight",
        "h2": 0.40,
        "units": "lb",
        "direction": "higher_better",
        "notes": "Adult body weight — the SIZE/maximum-frame axis. Separated from PWT 2026-06-12 so old heavy ewes no longer pollute the growth-rate ranking. This is where 'maximum size' selection (Awassi line, Rocky/Buck) lives. Fed by raw adult weight_lbs.",
    },
    "ADG": {  # Average daily gain
        "name": "Average Daily Gain",
        "long_name": "Average daily gain birth-to-weaning",
        "h2": 0.30,
        "units": "lb/day",
        "direction": "higher_better",
        "notes": "Birth-to-weaning average. Less affected by environment than absolute weights.",
    },
    "NLW": {  # Number lambs weaned (maternal)
        "name": "Lambs Weaned per Lambing",
        "long_name": "Number of lambs weaned per dam-lambing",
        "h2": 0.10,
        "units": "lambs",
        "direction": "higher_better",
        "notes": "Low heritability. Combines fertility, lambing ability, and milk yield. Maternal trait.",
    },
    "MILK": {  # Milk yield (inferred from offspring growth)
        "name": "Milk Yield (inferred)",
        "long_name": "Milk yield inferred from lamb ADG to weaning",
        "h2": 0.20,
        "units": "ADG-inferred",
        "direction": "higher_better",
        "notes": "Direct milk measurement absent — use offspring growth as proxy. A dam with chronic low milk shows depressed lamb ADG.",
    },
}


# ── Florida Cracker heritability calibration (MCS-27, operator-supplied priors) ──────────
# A separate, per-parasite-trait prior set for when the flock is evaluated as (or selected
# toward) a Florida Cracker-type heat- and parasite-adapted landrace, where parasite-trait
# heritability runs HIGHER than the generic hair-sheep meta-analysis values in TRAITS above.
# Values are the operator's calibration (MCS-27 spec); the parasite figures sit in the range
# published for locally-adapted landraces (e.g. FEC h2 ~0.2-0.4 in tropically-adapted breeds).
#
# NOT auto-applied: this flock is MIXED (Katahdin/Dorper/Awassi/…), not pure Florida Cracker,
# and h2 feeds estimate.py's EBV blend (new_ebv = h2*deviation + (1-h2)*mid_parent_ebv), so
# adopting these would SHIFT breeding rankings. This is an opt-in calibration, documented and
# reversible, for the operator to select — not a silent overwrite of the cited generic priors.
# Apply per-trait by copying a value into the matching TRAITS entry's "h2".
FLORIDA_CRACKER_H2 = {
    "FEC": 0.33,       # fecal egg count (parasite burden) — the primary resilience signal
    "FAMACHA": 0.31,   # FAMACHA anemia score — maps to the PR trait (FAMACHA-derived)
    "PCV": 0.22,       # packed cell volume — anemia, not yet a tracked trait here
    "BCS": 0.19,       # body condition score — not yet a tracked trait here
    "resilience": (0.10, 0.19),  # composite resilience heritability band
}

# Data-collection rule that PROTECTS these heritabilities (MCS-27): RETAIN PRE-TREATMENT
# records. A FAMACHA/FEC read AFTER a drench reflects the drug, not the animal's genetic
# resistance, so a post-drench value must never overwrite or stand in for the pre-drench one.
# The normalize_famacha merge is append/dedupe (never overwrites) and the FECRT tool reads
# the pre-drench count explicitly, so both already honor this; stated here as the standing rule.
RETAIN_PRE_TREATMENT_RECORDS = True


def contemporary_group_key(sheep_record: dict) -> str:
    """Group animals for trait deviation calculations.

    For our small flock we use a simple key: sex + birth-year + pen-band.
    Animals in the same contemporary group experienced similar
    management (same season, similar feed, same parasite pressure).
    """
    sex = sheep_record.get("sex", "unknown")
    dob = sheep_record.get("dob") or ""
    year = dob[:4] if dob else "unknown"
    pen = sheep_record.get("pen") or "none"
    return f"{sex}|{year}|{pen}"


if __name__ == "__main__":
    for code, t in TRAITS.items():
        print(f"  {code:<5} h2={t['h2']:.2f}  {t['name']}")
