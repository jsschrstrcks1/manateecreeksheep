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
        "notes": "Adjusted to 120-day equivalent.",
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
