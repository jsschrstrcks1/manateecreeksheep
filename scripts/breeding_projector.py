#!/usr/bin/env python3
"""
Breeding Results Projector for Manatee Creek Sheep.

Predicts offspring characteristics from any sire x dam combination,
including parasite resistance, breed composition, coat type, weight,
temperament, prolificacy, climate adaptation, and more.

Uses the flock's existing parasite resistance algorithm plus original
research data compiled from peer-reviewed papers, university extension
publications, and breed association data. See research/ directory.

Features:
  - Pen-based ram/ewe selector with movable assignments
  - Support for custom/new sheep with any breed composition
  - Stoplight confidence scoring (GREEN/YELLOW/RED)
  - Heterosis calculation using retained heterosis formula
  - Inbreeding coefficient estimation and depression modeling
  - Coat type prediction using major-gene + polygenic model

References:
  - Notter 1978, OSU Extension (heterosis tables)
  - Pollott 2011, Matika 2013 (coat genetics)
  - Doekes et al. 2021 (inbreeding depression meta-analysis)
  - Burke & Miller 2020 (hair sheep parasite resistance)
  - Tadesse et al. 2019 (heat tolerance breed comparison)
  - UF/IFAS VM264 (Florida breed recommendations)
"""

import json
import math
import os
import sys
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, "..", "data", "flock_database.json")

# Import the existing parasite resistance algorithm
sys.path.insert(0, SCRIPT_DIR)
from parasite_resistance import (
    BREED_RESISTANCE,
    DEFAULT_BREED_RESISTANCE,
    _breed_subscore,
    score_individual,
)


# ═══════════════════════════════════════════════════════════════════
# BREED DATA TABLES — from original research (see research/ dir)
# ═══════════════════════════════════════════════════════════════════

# Mature weight ranges (lbs): {breed: (ram_low, ram_high, ewe_low, ewe_high)}
# Sources: breed associations, OSU breeds database, UF/IFAS
BREED_WEIGHTS = {
    "Katahdin":             (180, 250, 120, 160),
    "Barbados Blackbelly":  (100, 150,  75, 100),
    "American Blackbelly":  (100, 150,  75, 100),
    "St Augustine":         (150, 200, 100, 140),
    "Dorper":               (200, 275, 150, 200),
    "Black Headed Dorper":  (200, 275, 150, 200),
    "White Dorper":         (200, 275, 150, 200),
    "Gulf Coast Native":    (125, 165, 100, 130),
    "Cracker":              (125, 165, 100, 130),
    "Hampshire":            (220, 275, 154, 220),
    "Suffolk":              (250, 350, 180, 250),
    "Cotswold":             (250, 300, 160, 200),
    "Tunis":                (175, 225, 125, 175),
    "Jacob":                (120, 180,  80, 120),
    "Babydoll":             ( 80, 120,  60, 100),
    "Karakul":              (175, 225, 100, 150),
    "Wiltshire Horn":       (220, 275, 130, 170),
    "East Friesian":        (200, 275, 150, 220),
    "Awassi":               (130, 175, 110, 160),
}

# Prolificacy: average lambs born per ewe lambing
# Sources: breed associations, extension pubs, NSIP data
BREED_PROLIFICACY = {
    "Katahdin":             1.8,   # Twins common, triplets occasional
    "Barbados Blackbelly":  1.9,   # Twins/triplets, very prolific
    "American Blackbelly":  1.8,   # Similar to BBB
    "St Augustine":         1.8,   # Consistent twinning
    "Dorper":               1.5,   # Singles/twins
    "Black Headed Dorper":  1.5,
    "White Dorper":         1.5,
    "Gulf Coast Native":    1.5,   # Singles/twins
    "Cracker":              1.5,   # Similar to GCN
    "Hampshire":            1.5,   # Singles/twins, triplets rare
    "Suffolk":              1.6,   # Twins common
    "Cotswold":             1.6,   # 150-175% lambing
    "Tunis":                1.7,   # Good twinning, triplets possible
    "Jacob":                1.7,   # Often twins, occasionally triplets
    "Babydoll":             1.5,   # Twins common
    "Karakul":              1.1,   # Singles predominant
    "Wiltshire Horn":       1.7,   # Good twinning
    "East Friesian":        2.25,  # Highest prolificacy
    "Awassi":               1.2,   # Low, 5% twins
}

# Mothering ability (0-10 scale, 10 = best)
# Sources: breed associations, extension literature
BREED_MOTHERING = {
    "Katahdin":             8,
    "Barbados Blackbelly":  7,
    "American Blackbelly":  7,
    "St Augustine":         8,
    "Dorper":               7,
    "Black Headed Dorper":  7,
    "White Dorper":         7,
    "Gulf Coast Native":    7,
    "Cracker":              7,
    "Hampshire":            7,
    "Suffolk":              7,
    "Cotswold":             9,    # Excellent mothers per Livestock Conservancy
    "Tunis":                9,    # Heavy milkers, attentive
    "Jacob":                9,    # Outstanding mothers
    "Babydoll":             9,    # Easy lambing, nurturing
    "Karakul":              9,    # Very protective, easy lambing
    "Wiltshire Horn":       8,    # Excellent maternal
    "East Friesian":        9,    # Outstanding milk production
    "Awassi":               9,    # Excellent milk, protective
}

# Temperament (0-10 scale, 10 = most docile, 0 = most flighty)
# Sources: breed associations, Grandin 2000, extension pubs
BREED_TEMPERAMENT = {
    "Katahdin":             7,
    "Barbados Blackbelly":  4,    # Can be flighty
    "American Blackbelly":  4,    # Can be flighty
    "St Augustine":         7,
    "Dorper":               7,
    "Black Headed Dorper":  7,
    "White Dorper":         7,
    "Gulf Coast Native":    5,    # Semi-wild heritage
    "Cracker":              5,    # Semi-wild heritage
    "Hampshire":            8,    # Docile
    "Suffolk":              8,    # Docile, calm
    "Cotswold":             8,    # Hardy and docile
    "Tunis":                9,    # Very docile, great for beginners
    "Jacob":                6,    # Docile but alert, can be skittish
    "Babydoll":             10,   # Exceptionally docile
    "Karakul":              6,    # Moderate, independent
    "Wiltshire Horn":       7,    # Gentle
    "East Friesian":        9,    # Very docile
    "Awassi":               9,    # Very docile, enjoy human contact
}

# Flocking instinct (0-10 scale, 10 = strongest flock behavior)
BREED_FLOCKING = {
    "Katahdin":             6,
    "Barbados Blackbelly":  5,
    "American Blackbelly":  5,
    "St Augustine":         7,
    "Dorper":               5,
    "Black Headed Dorper":  5,
    "White Dorper":         5,
    "Gulf Coast Native":    5,
    "Cracker":              5,
    "Hampshire":            6,    # Moderate
    "Suffolk":              3,    # Weak flocking, can be aggressive
    "Cotswold":             3,    # Loose/weak
    "Tunis":                7,    # Moderate-strong
    "Jacob":                4,    # Independent, scatter
    "Babydoll":             8,    # Strong social bonds
    "Karakul":              8,    # Strong, historically herded
    "Wiltshire Horn":       6,    # Moderate-strong
    "East Friesian":        5,    # Moderate, better in small groups
    "Awassi":               9,    # Very strong, close flocking
}

# Out-of-season breeding ability (0-10 scale, 10 = breeds year-round)
BREED_YEAR_ROUND = {
    "Katahdin":             8,    # Year-round, developed for it
    "Barbados Blackbelly":  9,    # Year-round, tropical origin
    "American Blackbelly":  9,
    "St Augustine":         8,
    "Dorper":               8,    # Year-round capability
    "Black Headed Dorper":  8,
    "White Dorper":         8,
    "Gulf Coast Native":    7,
    "Cracker":              7,
    "Hampshire":            2,    # Strongly seasonal
    "Suffolk":              2,    # Strongly seasonal
    "Cotswold":             3,    # Likely seasonal
    "Tunis":                9,    # Outstanding year-round
    "Jacob":                4,    # Limited data, likely seasonal
    "Babydoll":             2,    # Seasonal (Aug-Feb)
    "Karakul":              8,    # 3 crops in 2 years possible
    "Wiltshire Horn":       4,    # Limited data
    "East Friesian":        3,    # Seasonal
    "Awassi":               6,    # Partial, rams year-round
}

# Florida suitability (1-10 scale, combines heat + humidity tolerance)
# Source: climate adaptation research, UF/IFAS VM264, Tadesse et al. 2019
BREED_FL_SUITABILITY = {
    "Gulf Coast Native":    9.5,
    "Cracker":              9.5,
    "Barbados Blackbelly":  8.5,
    "American Blackbelly":  8.0,
    "St Augustine":         8.5,
    "Katahdin":             8.0,
    "Tunis":                6.5,
    "Dorper":               6.0,
    "Black Headed Dorper":  6.0,
    "White Dorper":         6.0,
    "Wiltshire Horn":       6.5,
    "Karakul":              5.5,  # Dry heat adapted, humidity concern
    "Awassi":               6.0,  # Dry heat adapted, humidity concern
    "Jacob":                5.0,
    "Babydoll":             4.5,
    "Hampshire":            3.5,
    "Suffolk":              3.5,
    "East Friesian":        3.0,
    "Cotswold":             2.5,
}

# Foot rot resistance (1-10 scale)
# Source: Parker et al. 2006, GWAS 2023, UF/IFAS
BREED_FOOT_ROT = {
    "Gulf Coast Native":    9,
    "Cracker":              9,
    "Barbados Blackbelly":  8,
    "American Blackbelly":  7,
    "St Augustine":         7,
    "Katahdin":             7,
    "Wiltshire Horn":       7,
    "Babydoll":             7,
    "Karakul":              6,    # Drops to 3-4 in wet FL environment
    "Jacob":                6,
    "Tunis":                5,
    "Suffolk":              5,
    "Hampshire":            5,
    "Dorper":               4,
    "Black Headed Dorper":  4,
    "White Dorper":         4,
    "Awassi":               4,
    "Cotswold":             3,
    "East Friesian":        3,
}

# Growth rate relative score (0-10 scale, 10 = fastest growth)
BREED_GROWTH_RATE = {
    "Suffolk":              10,   # Fastest among common breeds
    "Hampshire":            9,
    "Dorper":               8,
    "Black Headed Dorper":  8,
    "White Dorper":         8,
    "Katahdin":             7,
    "St Augustine":         6,
    "Wiltshire Horn":       6,
    "East Friesian":        7,
    "Tunis":                5,    # Moderate, but feed-efficient
    "Awassi":               5,
    "Cotswold":             4,    # Slow growers
    "Gulf Coast Native":    4,
    "Cracker":              4,
    "American Blackbelly":  4,
    "Barbados Blackbelly":  4,
    "Jacob":                3,    # Small frame, slow
    "Karakul":              4,
    "Babydoll":             3,    # Small, slow
}

# Shedding Potential Score (0-5 scale)
# Source: coat genetics research, KHSI, Pollott 2011
BREED_SHEDDING = {
    "Barbados Blackbelly":  5.0,
    "American Blackbelly":  5.0,
    "Katahdin":             4.5,
    "Wiltshire Horn":       4.0,
    "St Augustine":         4.0,
    "White Dorper":         3.0,
    "Dorper":               2.5,
    "Black Headed Dorper":  2.5,
    "Gulf Coast Native":    1.0,
    "Cracker":              1.0,
    "Tunis":                0.5,
    "Hampshire":            0.5,
    "Suffolk":              0.5,
    "Babydoll":             0.5,
    "Jacob":                0.5,
    "East Friesian":        0.5,
    "Karakul":              0.5,
    "Awassi":               0.5,
    "Cotswold":             0.0,
}

# Probability of carrying dominant shedding allele
# Source: Pollott 2011 two-part model
BREED_SHEDDING_GENE_PROB = {
    "Barbados Blackbelly":  1.0,
    "American Blackbelly":  1.0,
    "Katahdin":             0.95,
    "Wiltshire Horn":       0.85,
    "St Augustine":         0.85,
    "White Dorper":         0.70,
    "Dorper":               0.60,
    "Black Headed Dorper":  0.60,
    "Gulf Coast Native":    0.05,
    "Cracker":              0.05,
}
# All wool breeds default to 0.0

# Carcass quality (0-10 scale)
BREED_CARCASS = {
    "Suffolk":              10,
    "Hampshire":            9,
    "Dorper":               8,
    "Black Headed Dorper":  8,
    "White Dorper":         8,
    "Katahdin":             6,
    "Wiltshire Horn":       7,
    "Cotswold":             5,
    "Tunis":                6,
    "St Augustine":         6,
    "East Friesian":        5,
    "Awassi":               5,
    "Gulf Coast Native":    4,
    "Cracker":              4,
    "Barbados Blackbelly":  4,
    "American Blackbelly":  4,
    "Jacob":                4,
    "Karakul":              4,
    "Babydoll":             5,
}


# ═══════════════════════════════════════════════════════════════════
# HERITABILITY ESTIMATES — from heritability research
# ═══════════════════════════════════════════════════════════════════

HERITABILITY = {
    "birth_weight":         0.15,
    "weaning_weight":       0.25,
    "mature_weight":        0.40,
    "adg_preweaning":       0.25,
    "adg_postweaning":      0.25,
    "prolificacy":          0.10,
    "mothering":            0.10,
    "temperament":          0.20,
    "flocking":             0.10,
    "parasite_resistance":  0.22,  # FEC-based
    "foot_rot_resistance":  0.22,
    "coat_shedding":        0.50,
    "fl_suitability":       0.30,  # Composite of multiple heritable traits
    "year_round_breeding":  0.15,
    "carcass_quality":      0.30,
    "growth_rate":          0.25,
}

# ═══════════════════════════════════════════════════════════════════
# HETEROSIS TABLES — from heterosis research (Notter 1978, OSU Ext)
# ═══════════════════════════════════════════════════════════════════

# Individual (direct) heterosis as fraction (e.g., 0.05 = 5%)
INDIVIDUAL_HETEROSIS = {
    "birth_weight":         0.032,
    "weaning_weight":       0.050,
    "mature_weight":        0.040,
    "adg_preweaning":       0.053,
    "adg_postweaning":      0.066,
    "prolificacy":          0.028,
    "lamb_survival":        0.098,
    "growth_rate":          0.053,
    "carcass_quality":      0.000,  # No heterosis for carcass traits
}

# Inbreeding depression coefficients
# Fractional decline per 1% increase in F
INBREEDING_DEPRESSION = {
    "birth_weight":         0.00136,  # -13.6g per 1%F on ~10lb base
    "weaning_weight":       0.00100,  # -30g per 1%F on ~30kg base
    "mature_weight":        0.00130,  # -0.13% of mean per 1%F
    "prolificacy":          0.00230,  # -0.04 lambs on ~1.7 base per 1%F
    "lamb_survival":        0.00800,  # 80% of decline is survival
    "growth_rate":          0.00500,  # -0.50% of SD per 1%F
    "fertility":            0.00460,  # -0.46 pct pts per 1%F
}


# ═══════════════════════════════════════════════════════════════════
# CORE PREDICTION ENGINE
# ═══════════════════════════════════════════════════════════════════

def resolve_breed_composition(sheep, db_by_id, depth=0):
    """
    If a sheep has empty breed_composition, derive it from parents.
    Walks up the pedigree recursively (with depth limit to prevent loops).
    Returns the breed_composition dict (percentages, hair_percentage, coat_type).
    """
    comp = sheep.get("breed_composition", {})
    pcts = comp.get("percentages", {})
    if pcts:
        return comp  # Already has breed data

    if depth > 5:
        return comp  # Prevent infinite recursion

    sire_id = sheep.get("sire_id")
    dam_id = sheep.get("dam_id")
    sire = db_by_id.get(sire_id) if sire_id else None
    dam = db_by_id.get(dam_id) if dam_id else None

    if not sire and not dam:
        return comp  # No parents to derive from

    # Recursively resolve parent breeds
    sire_comp = resolve_breed_composition(sire, db_by_id, depth + 1) if sire else {}
    dam_comp = resolve_breed_composition(dam, db_by_id, depth + 1) if dam else {}

    sire_pcts = sire_comp.get("percentages", {})
    dam_pcts = dam_comp.get("percentages", {})

    if not sire_pcts and not dam_pcts:
        return comp

    # Average of available parents
    all_breeds = set(sire_pcts.keys()) | set(dam_pcts.keys())
    derived_pcts = {}
    if sire_pcts and dam_pcts:
        for breed in all_breeds:
            derived_pcts[breed] = (sire_pcts.get(breed, 0) + dam_pcts.get(breed, 0)) / 2
    elif sire_pcts:
        derived_pcts = dict(sire_pcts)  # Only sire known
    else:
        derived_pcts = dict(dam_pcts)  # Only dam known

    # Derive hair percentage
    sire_hair = sire_comp.get("hair_percentage")
    dam_hair = dam_comp.get("hair_percentage")
    if sire_hair is not None and dam_hair is not None:
        hair_pct = (sire_hair + dam_hair) / 2
    elif sire_hair is not None:
        hair_pct = sire_hair
    elif dam_hair is not None:
        hair_pct = dam_hair
    else:
        hair_pct = 50  # Unknown default

    if hair_pct >= 80:
        coat_type = "hair"
    elif hair_pct >= 30:
        coat_type = "mixed"
    else:
        coat_type = "wool"

    derived = {
        "percentages": derived_pcts,
        "hair_percentage": round(hair_pct, 1),
        "coat_type": coat_type,
    }

    # Cache on the sheep record so we don't recompute
    sheep["breed_composition"] = derived
    return derived


def _get_breed_value(table, breed_composition, default=5.0):
    """Weighted average of a breed trait table by breed percentages."""
    pcts = breed_composition.get("percentages", {})
    if not pcts:
        return default
    total_w = 0
    weighted = 0
    for breed, pct in pcts.items():
        val = table.get(breed, default)
        weighted += val * pct
        total_w += pct
    if total_w == 0:
        return default
    return weighted / total_w


def _get_weight_prediction(breed_composition, sex):
    """Predict mature weight range from breed composition."""
    pcts = breed_composition.get("percentages", {})
    if not pcts:
        return None, None
    low_total = 0
    high_total = 0
    total_w = 0
    for breed, pct in pcts.items():
        weights = BREED_WEIGHTS.get(breed)
        if weights:
            if sex == "ram":
                low_total += weights[0] * pct
                high_total += weights[1] * pct
            else:
                low_total += weights[2] * pct
                high_total += weights[3] * pct
            total_w += pct
    if total_w == 0:
        return None, None
    return round(low_total / total_w, 1), round(high_total / total_w, 1)


def compute_offspring_breed(sire_comp, dam_comp):
    """
    Compute offspring breed composition as average of parents.
    Each parent contributes 50% of their breed fractions.
    """
    sire_pcts = sire_comp.get("percentages", {})
    dam_pcts = dam_comp.get("percentages", {})
    all_breeds = set(sire_pcts.keys()) | set(dam_pcts.keys())

    offspring_pcts = {}
    for breed in all_breeds:
        s = sire_pcts.get(breed, 0)
        d = dam_pcts.get(breed, 0)
        offspring_pcts[breed] = (s + d) / 2

    # Calculate hair percentage
    sire_hair = sire_comp.get("hair_percentage")
    dam_hair = dam_comp.get("hair_percentage")
    if sire_hair is not None and dam_hair is not None:
        hair_pct = (sire_hair + dam_hair) / 2
    elif sire_hair is not None:
        hair_pct = sire_hair / 2  # Assume dam is unknown
    elif dam_hair is not None:
        hair_pct = dam_hair / 2
    else:
        # Estimate from breed shedding scores
        sire_shed = _get_breed_value(BREED_SHEDDING, sire_comp, 2.5)
        dam_shed = _get_breed_value(BREED_SHEDDING, dam_comp, 2.5)
        hair_pct = ((sire_shed + dam_shed) / 2) / 5.0 * 100

    # Determine coat type
    if hair_pct >= 80:
        coat_type = "hair"
    elif hair_pct >= 30:
        coat_type = "mixed"
    else:
        coat_type = "wool"

    return {
        "percentages": offspring_pcts,
        "hair_percentage": round(hair_pct, 1),
        "coat_type": coat_type,
    }


def compute_retained_heterosis(breed_composition):
    """
    Calculate retained heterosis fraction using the formula:
    Retained_H = 1 - SUM(Pi^2)
    where Pi = fractional contribution of each breed.

    Source: Iowa Beef Center, Penn State Extension
    """
    pcts = breed_composition.get("percentages", {})
    if not pcts:
        return 0
    fractions = [p / 100.0 for p in pcts.values() if p > 0]
    if len(fractions) <= 1:
        return 0  # Purebred — no heterosis
    sum_squared = sum(f ** 2 for f in fractions)
    return round(1.0 - sum_squared, 4)


def estimate_inbreeding(sire_record, dam_record, db_by_id):
    """
    Estimate inbreeding coefficient from pedigree overlap.
    Uses Wright's path coefficient method for known ancestors.
    Returns (F, explanation).
    """
    if not sire_record or not dam_record:
        return 0, "Unknown parentage"

    # Build ancestor sets (up to 3 generations)
    def get_ancestors(sheep_id, depth=3):
        """Get ancestors as {id: set_of_generation_depths}."""
        ancestors = {}
        if not sheep_id or sheep_id not in db_by_id:
            return ancestors
        queue = [(sheep_id, 0)]
        visited = set()
        while queue:
            sid, d = queue.pop(0)
            if d > depth or sid in visited:
                continue
            visited.add(sid)
            sheep = db_by_id.get(sid)
            if not sheep:
                continue
            sire_id = sheep.get("sire_id")
            dam_id = sheep.get("dam_id")
            if sire_id:
                ancestors.setdefault(sire_id, set()).add(d + 1)
                queue.append((sire_id, d + 1))
            if dam_id:
                ancestors.setdefault(dam_id, set()).add(d + 1)
                queue.append((dam_id, d + 1))
        return ancestors

    sire_ancestors = get_ancestors(sire_record["id"])
    dam_ancestors = get_ancestors(dam_record["id"])

    # Find common ancestors
    common = set(sire_ancestors.keys()) & set(dam_ancestors.keys())
    if not common:
        # Also check if sire IS an ancestor of dam or vice versa
        if sire_record["id"] in dam_ancestors:
            # Dam descends from sire
            min_gen = min(dam_ancestors[sire_record["id"]])
            f = 0.5 ** (min_gen + 1)
            return round(f, 4), f"Dam descends from sire ({min_gen} gen)"
        if dam_record["id"] in sire_ancestors:
            min_gen = min(sire_ancestors[dam_record["id"]])
            f = 0.5 ** (min_gen + 1)
            return round(f, 4), f"Sire descends from dam ({min_gen} gen)"
        return 0, "No common ancestors found (within 3 generations)"

    # Calculate F using Wright's formula
    f_total = 0
    explanations = []
    for ancestor_id in common:
        ancestor = db_by_id.get(ancestor_id)
        ancestor_name = ancestor["name"] if ancestor else ancestor_id
        for n1 in sire_ancestors[ancestor_id]:
            for n2 in dam_ancestors[ancestor_id]:
                path_f = 0.5 ** (n1 + n2 + 1)
                f_total += path_f
                explanations.append(
                    f"Common ancestor: {ancestor_name} "
                    f"(sire path={n1}, dam path={n2}, F+={path_f:.4f})"
                )

    return round(f_total, 4), "; ".join(explanations) if explanations else "Calculated from pedigree"


def predict_coat(sire_comp, dam_comp, offspring_comp):
    """
    Predict coat type using the two-component model:
    1. Probability of shedding gene (major dominant gene)
    2. Shedding extent (polygenic, uses SPS weighted average)

    Source: Pollott 2011, Matika 2013
    """
    # Component A: Shedding gene probability
    sire_prob = _get_breed_value(BREED_SHEDDING_GENE_PROB, sire_comp, 0.0)
    dam_prob = _get_breed_value(BREED_SHEDDING_GENE_PROB, dam_comp, 0.0)

    # P(offspring has at least one copy) = 1 - P(neither parent passes it)
    # Simplified: average of parental probabilities as a reasonable estimate
    # for mixed-breed animals where genotype is unknown
    p_shedding = 1 - (1 - sire_prob * 0.5) * (1 - dam_prob * 0.5)

    # Component B: Shedding extent (polygenic, SPS 0-5)
    sire_sps = _get_breed_value(BREED_SHEDDING, sire_comp, 2.5)
    dam_sps = _get_breed_value(BREED_SHEDDING, dam_comp, 2.5)
    midparent_sps = (sire_sps + dam_sps) / 2

    # Apply heritability: offspring = pop_mean + h2 * (midparent - pop_mean)
    pop_mean = 2.5
    h2 = HERITABILITY["coat_shedding"]
    offspring_sps = pop_mean + h2 * (midparent_sps - pop_mean)

    # Predict shearing need
    if p_shedding > 0.5 and offspring_sps > 3.5:
        shearing = "Likely sheds completely — no shearing needed"
        coat_prediction = "hair"
    elif p_shedding > 0.5 and offspring_sps > 2.0:
        shearing = "Partial shedding — may need some shearing"
        coat_prediction = "mixed (shedding)"
    elif offspring_sps > 1.5:
        shearing = "Minimal shedding — will need shearing"
        coat_prediction = "mixed (wool-dominant)"
    else:
        shearing = "Full wool coat — requires regular shearing"
        coat_prediction = "wool"

    # Confidence
    if sire_sps >= 4.0 and dam_sps >= 4.0:
        confidence = "GREEN"
    elif abs(sire_sps - dam_sps) < 2.0:
        confidence = "YELLOW"
    else:
        confidence = "RED"  # Very different parents = unpredictable

    return {
        "prediction": coat_prediction,
        "shedding_probability": round(p_shedding, 2),
        "shedding_extent_score": round(offspring_sps, 2),
        "shearing_need": shearing,
        "confidence": confidence,
        "parent_sps": {"sire": round(sire_sps, 2), "dam": round(dam_sps, 2)},
    }


def predict_parasite_resistance(sire_record, dam_record, offspring_comp, db_by_id):
    """
    Predict offspring parasite resistance using the existing algorithm's
    breed scores, enhanced with parent phenotypic data where available.
    """
    # Breed-based baseline for offspring
    breed_score = _get_breed_value(BREED_RESISTANCE, offspring_comp, DEFAULT_BREED_RESISTANCE)

    # Get parent scores if they have phenotypic data
    sire_score_data = score_individual(sire_record, db_by_id) if sire_record else None
    dam_score_data = score_individual(dam_record, db_by_id) if dam_record else None

    # Blend parent phenotypic data with breed prediction
    parent_scores = []
    parent_details = []
    if sire_score_data:
        parent_scores.append(sire_score_data["score"])
        parent_details.append(
            f"Sire: {sire_score_data['score']:.0f} "
            f"({sire_score_data['grade']}, {sire_score_data['confidence']})"
        )
    if dam_score_data:
        parent_scores.append(dam_score_data["score"])
        parent_details.append(
            f"Dam: {dam_score_data['score']:.0f} "
            f"({dam_score_data['grade']}, {dam_score_data['confidence']})"
        )

    if parent_scores:
        parent_avg = sum(parent_scores) / len(parent_scores)
        # h2 for FEC = 0.22, so offspring = breed_mean + h2 * (parent_avg - breed_mean)
        h2 = HERITABILITY["parasite_resistance"]
        predicted = breed_score + h2 * (parent_avg - breed_score)
    else:
        predicted = breed_score

    # Apply heterosis bonus (parasite resistance is primarily breed effect,
    # but crossbreds show some advantage)
    retained_h = compute_retained_heterosis(offspring_comp)
    # Small heterosis effect for parasite resistance (~3-5% for crosses)
    heterosis_bonus = retained_h * 3.0
    predicted = min(100, predicted + heterosis_bonus)

    predicted = max(0, min(100, round(predicted, 1)))

    # Grade
    if predicted >= 85:
        grade = "A"
    elif predicted >= 70:
        grade = "B"
    elif predicted >= 55:
        grade = "C"
    elif predicted >= 40:
        grade = "D"
    else:
        grade = "F"

    # Confidence
    if parent_scores and all(
        s.get("confidence") == "high" for s in [sire_score_data, dam_score_data] if s
    ):
        confidence = "GREEN"
    elif parent_scores:
        confidence = "YELLOW"
    else:
        confidence = "RED"

    return {
        "score": predicted,
        "grade": grade,
        "breed_baseline": round(breed_score, 1),
        "heterosis_bonus": round(heterosis_bonus, 1),
        "retained_heterosis": retained_h,
        "parent_scores": parent_details,
        "confidence": confidence,
    }


def predict_all_traits(sire_record, dam_record, db_by_id):
    """
    Generate complete breeding projection for a sire x dam cross.

    Resolves breed composition from parents if missing, then returns
    a dict with predictions for all traits, breed composition,
    heterosis, inbreeding, and confidence levels.
    """
    # Resolve breed composition from pedigree if missing
    sire_comp = resolve_breed_composition(sire_record, db_by_id)
    dam_comp = resolve_breed_composition(dam_record, db_by_id)

    # 1. Offspring breed composition
    offspring_comp = compute_offspring_breed(sire_comp, dam_comp)
    retained_h = compute_retained_heterosis(offspring_comp)
    num_breeds = len([p for p in offspring_comp["percentages"].values() if p > 0.5])

    # 2. Inbreeding
    f_coeff, f_explanation = estimate_inbreeding(sire_record, dam_record, db_by_id)
    if f_coeff >= 0.125:
        f_risk = "DANGER"
        f_confidence = "RED"
    elif f_coeff >= 0.07:
        f_risk = "WARNING"
        f_confidence = "RED"
    elif f_coeff >= 0.03:
        f_risk = "MONITOR"
        f_confidence = "YELLOW"
    else:
        f_risk = "LOW"
        f_confidence = "GREEN"

    # 3. Weight predictions (for both sexes)
    ram_low, ram_high = _get_weight_prediction(offspring_comp, "ram")
    ewe_low, ewe_high = _get_weight_prediction(offspring_comp, "ewe")

    # Apply heterosis to weight (~4% for mature weight)
    h_weight = 1 + (INDIVIDUAL_HETEROSIS.get("mature_weight", 0.04) * retained_h)
    # Apply inbreeding depression
    id_weight = 1 - (INBREEDING_DEPRESSION.get("mature_weight", 0.0013) * f_coeff * 100)

    weight_factor = h_weight * id_weight
    if ram_low:
        ram_low = round(ram_low * weight_factor)
        ram_high = round(ram_high * weight_factor)
    if ewe_low:
        ewe_low = round(ewe_low * weight_factor)
        ewe_high = round(ewe_high * weight_factor)

    # Weight confidence
    sire_has_weight = bool(sire_record.get("weight_lbs"))
    dam_has_weight = bool(dam_record.get("weight_lbs"))
    sire_has_breed = bool(sire_comp.get("percentages"))
    dam_has_breed = bool(dam_comp.get("percentages"))

    if sire_has_breed and dam_has_breed:
        weight_confidence = "YELLOW"  # Breed-based prediction
    elif sire_has_breed or dam_has_breed:
        weight_confidence = "RED"
    else:
        weight_confidence = "RED"

    # 4. Trait predictions (breed-weighted averages with heterosis)
    def predict_trait(table, trait_name, default=5.0):
        sire_val = _get_breed_value(table, sire_comp, default)
        dam_val = _get_breed_value(table, dam_comp, default)
        midparent = (sire_val + dam_val) / 2

        h2 = HERITABILITY.get(trait_name, 0.20)
        # Predicted = population_mean + h2 * (midparent - population_mean)
        # But since our breed tables ARE the population means by breed,
        # and midparent IS our best estimate, we use midparent directly
        # and apply heterosis on top
        h_bonus = INDIVIDUAL_HETEROSIS.get(trait_name, 0.0) * retained_h
        id_penalty = INBREEDING_DEPRESSION.get(trait_name, 0.0) * f_coeff * 100

        predicted = midparent * (1 + h_bonus) * (1 - id_penalty)

        # Confidence based on breed data availability
        if sire_has_breed and dam_has_breed:
            confidence = "YELLOW"  # Breed averages, not individual data
        else:
            confidence = "RED"

        return {
            "value": round(predicted, 2),
            "sire_breed_avg": round(sire_val, 2),
            "dam_breed_avg": round(dam_val, 2),
            "heterosis_pct": round(h_bonus * 100, 1),
            "inbreeding_penalty_pct": round(id_penalty * 100, 1),
            "confidence": confidence,
        }

    # 5. Parasite resistance (uses existing algorithm)
    parasite = predict_parasite_resistance(
        sire_record, dam_record, offspring_comp, db_by_id
    )

    # 6. Coat prediction
    coat = predict_coat(sire_comp, dam_comp, offspring_comp)

    # 7. Compile all predictions
    prolificacy = predict_trait(BREED_PROLIFICACY, "prolificacy", 1.5)
    temperament = predict_trait(BREED_TEMPERAMENT, "temperament", 6.0)
    mothering = predict_trait(BREED_MOTHERING, "mothering", 7.0)
    flocking = predict_trait(BREED_FLOCKING, "flocking", 5.0)
    year_round = predict_trait(BREED_YEAR_ROUND, "year_round_breeding", 5.0)
    fl_suit = predict_trait(BREED_FL_SUITABILITY, "fl_suitability", 5.0)
    foot_rot = predict_trait(BREED_FOOT_ROT, "foot_rot_resistance", 5.0)
    growth = predict_trait(BREED_GROWTH_RATE, "growth_rate", 5.0)
    carcass = predict_trait(BREED_CARCASS, "carcass_quality", 5.0)

    return {
        "sire": {
            "name": sire_record["name"],
            "id": sire_record["id"],
            "breed": _format_breed(sire_comp),
        },
        "dam": {
            "name": dam_record["name"],
            "id": dam_record["id"],
            "breed": _format_breed(dam_comp),
        },
        "offspring_breed": {
            "percentages": {
                k: round(v, 2)
                for k, v in sorted(
                    offspring_comp["percentages"].items(), key=lambda x: -x[1]
                )
                if v > 0.5
            },
            "coat_type": offspring_comp["coat_type"],
            "hair_percentage": offspring_comp["hair_percentage"],
            "num_breeds": num_breeds,
        },
        "heterosis": {
            "retained_fraction": retained_h,
            "retained_pct": round(retained_h * 100, 1),
            "num_breeds": num_breeds,
            "confidence": "GREEN" if num_breeds >= 2 else "YELLOW",
        },
        "inbreeding": {
            "coefficient": f_coeff,
            "pct": round(f_coeff * 100, 2),
            "risk_level": f_risk,
            "explanation": f_explanation,
            "confidence": f_confidence,
        },
        "weight": {
            "ram_range": (ram_low, ram_high) if ram_low else None,
            "ewe_range": (ewe_low, ewe_high) if ewe_low else None,
            "heterosis_factor": round(h_weight, 3),
            "inbreeding_factor": round(id_weight, 3),
            "confidence": weight_confidence,
        },
        "parasite_resistance": parasite,
        "coat": coat,
        "prolificacy": prolificacy,
        "temperament": temperament,
        "mothering": mothering,
        "flocking": flocking,
        "year_round_breeding": year_round,
        "fl_suitability": fl_suit,
        "foot_rot_resistance": foot_rot,
        "growth_rate": growth,
        "carcass_quality": carcass,
    }


def _format_breed(comp):
    """Format breed composition for display."""
    pcts = comp.get("percentages", {})
    if not pcts:
        return "Unknown"
    parts = []
    for breed, pct in sorted(pcts.items(), key=lambda x: -x[1]):
        if pct > 0.5:
            parts.append(f"{pct:.1f}% {breed}")
    return ", ".join(parts) if parts else "Unknown"


# ═══════════════════════════════════════════════════════════════════
# CONFIDENCE LABELS
# ═══════════════════════════════════════════════════════════════════

def _conf_label(conf):
    """Convert confidence code to display label."""
    labels = {
        "GREEN": "[GREEN]  High confidence",
        "YELLOW": "[YELLOW] Moderate confidence",
        "RED": "[RED]    Low confidence",
    }
    return labels.get(conf, conf)


# ═══════════════════════════════════════════════════════════════════
# REPORT FORMATTER
# ═══════════════════════════════════════════════════════════════════

def format_report(prediction):
    """Format a prediction dict as a human-readable report."""
    p = prediction
    lines = []
    w = 80

    lines.append("=" * w)
    lines.append("BREEDING RESULTS PROJECTION")
    lines.append(f"  Sire: {p['sire']['name']}  ({p['sire']['breed']})")
    lines.append(f"  Dam:  {p['dam']['name']}  ({p['dam']['breed']})")
    lines.append("=" * w)

    # Breed composition
    lines.append("\n--- OFFSPRING BREED COMPOSITION ---")
    for breed, pct in p["offspring_breed"]["percentages"].items():
        bar = "#" * int(pct / 2)
        lines.append(f"  {breed:<25} {pct:6.2f}%  {bar}")
    lines.append(f"  Coat type: {p['offspring_breed']['coat_type']} "
                 f"(hair {p['offspring_breed']['hair_percentage']:.0f}%)")
    lines.append(f"  Number of breeds: {p['offspring_breed']['num_breeds']}")

    # Heterosis
    h = p["heterosis"]
    lines.append(f"\n--- HETEROSIS ---  {_conf_label(h['confidence'])}")
    lines.append(f"  Retained heterosis: {h['retained_pct']:.1f}% "
                 f"({h['num_breeds']} breeds)")
    if h["retained_pct"] == 0:
        lines.append("  (Purebred cross — no heterosis)")
    elif h["retained_pct"] >= 60:
        lines.append("  (Good heterosis retention — multi-breed advantage)")
    elif h["retained_pct"] >= 40:
        lines.append("  (Moderate heterosis — some hybrid vigor)")

    # Inbreeding
    ib = p["inbreeding"]
    lines.append(f"\n--- INBREEDING ---  {_conf_label(ib['confidence'])}")
    lines.append(f"  Coefficient (F): {ib['pct']:.2f}%  "
                 f"Risk: {ib['risk_level']}")
    if ib["coefficient"] > 0:
        lines.append(f"  {ib['explanation']}")

    # Weight
    wt = p["weight"]
    lines.append(f"\n--- PREDICTED WEIGHT ---  {_conf_label(wt['confidence'])}")
    if wt["ram_range"]:
        lines.append(f"  Ram:  {wt['ram_range'][0]}-{wt['ram_range'][1]} lbs")
    if wt["ewe_range"]:
        lines.append(f"  Ewe:  {wt['ewe_range'][0]}-{wt['ewe_range'][1]} lbs")
    if wt["heterosis_factor"] != 1.0:
        lines.append(f"  Heterosis adjustment: {(wt['heterosis_factor']-1)*100:+.1f}%")
    if wt["inbreeding_factor"] != 1.0:
        lines.append(f"  Inbreeding penalty:   {(wt['inbreeding_factor']-1)*100:+.1f}%")

    # Parasite resistance
    pr = p["parasite_resistance"]
    lines.append(f"\n--- PARASITE RESISTANCE ---  {_conf_label(pr['confidence'])}")
    lines.append(f"  Predicted score: {pr['score']:.1f}/100  (Grade: {pr['grade']})")
    lines.append(f"  Breed baseline: {pr['breed_baseline']:.1f}")
    if pr["heterosis_bonus"] > 0:
        lines.append(f"  Heterosis bonus: +{pr['heterosis_bonus']:.1f}")
    for detail in pr["parent_scores"]:
        lines.append(f"  {detail}")

    # Coat
    ct = p["coat"]
    lines.append(f"\n--- COAT TYPE ---  {_conf_label(ct['confidence'])}")
    lines.append(f"  Prediction: {ct['prediction']}")
    lines.append(f"  Shedding probability: {ct['shedding_probability']*100:.0f}%")
    lines.append(f"  Shedding extent score: {ct['shedding_extent_score']:.1f}/5.0")
    lines.append(f"  {ct['shearing_need']}")
    lines.append(f"  Parent SPS: sire={ct['parent_sps']['sire']}, "
                 f"dam={ct['parent_sps']['dam']}")

    # All other traits
    trait_rows = [
        ("Prolificacy (lambs/ewe)",   p["prolificacy"],          "lambs"),
        ("Temperament (docility)",    p["temperament"],          "/10"),
        ("Mothering Ability",         p["mothering"],            "/10"),
        ("Flocking Instinct",         p["flocking"],             "/10"),
        ("Year-Round Breeding",       p["year_round_breeding"],  "/10"),
        ("Florida Suitability",       p["fl_suitability"],       "/10"),
        ("Foot Rot Resistance",       p["foot_rot_resistance"],  "/10"),
        ("Growth Rate",               p["growth_rate"],          "/10"),
        ("Carcass Quality",           p["carcass_quality"],      "/10"),
    ]

    lines.append(f"\n--- TRAIT PREDICTIONS ---")
    lines.append(f"  {'Trait':<28} {'Predicted':>9} {'Sire':>8} {'Dam':>8} "
                 f"{'H%':>5} {'ID%':>5}  Confidence")
    lines.append("  " + "-" * 76)
    for label, data, unit in trait_rows:
        val_str = f"{data['value']:.2f}{unit}"
        h_str = f"+{data['heterosis_pct']:.1f}" if data["heterosis_pct"] > 0 else "0.0"
        id_str = f"-{data['inbreeding_penalty_pct']:.1f}" if data["inbreeding_penalty_pct"] > 0 else "0.0"
        lines.append(
            f"  {label:<28} {val_str:>9} {data['sire_breed_avg']:>8.2f} "
            f"{data['dam_breed_avg']:>8.2f} {h_str:>5} {id_str:>5}  "
            f"{data['confidence']}"
        )

    lines.append("\n" + "=" * w)
    lines.append("Confidence: GREEN = high (phenotypic data), "
                 "YELLOW = moderate (breed averages), RED = low (incomplete data)")
    lines.append("H% = heterosis bonus, ID% = inbreeding depression penalty")
    lines.append("=" * w)

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════
# PEN-BASED SELECTOR — default assignments from database
# ═══════════════════════════════════════════════════════════════════

def get_pen_assignments(db):
    """
    Get current pen assignments: which rams are with which ewes.
    Returns {pen: {"rams": [...], "ewes": [...]}}
    """
    pens = defaultdict(lambda: {"rams": [], "ewes": []})
    by_id = {s["id"]: s for s in db["sheep"]}

    for sheep in db["sheep"]:
        if sheep.get("status") != "alive":
            continue
        pen = sheep.get("pen")
        if not pen:
            continue
        sex = sheep.get("sex", "unknown")
        if sex == "ram":
            pens[pen]["rams"].append(sheep)
        elif sex == "ewe":
            pens[pen]["ewes"].append(sheep)

    return dict(pens)


def project_pen(pen_name, pens, db_by_id):
    """
    Project all possible crosses for a given pen.
    Returns list of predictions for each ram x ewe combination.
    """
    pen_data = pens.get(pen_name, {})
    rams = pen_data.get("rams", [])
    ewes = pen_data.get("ewes", [])

    projections = []
    for ram in rams:
        for ewe in ewes:
            pred = predict_all_traits(ram, ewe, db_by_id)
            projections.append(pred)

    return projections


def make_custom_sheep(name, sex, breed_percentages, weight=None):
    """
    Create a minimal sheep record for projection purposes.
    Allows entering new/hypothetical sheep with any breed composition.

    breed_percentages: dict like {"Katahdin": 50, "Dorper": 50}
    """
    # Calculate hair percentage from breed composition
    comp = {"percentages": breed_percentages}
    sps = _get_breed_value(BREED_SHEDDING, comp, 2.5)
    hair_pct = (sps / 5.0) * 100

    if hair_pct >= 80:
        coat_type = "hair"
    elif hair_pct >= 30:
        coat_type = "mixed"
    else:
        coat_type = "wool"

    record = {
        "id": f"custom-{name.lower().replace(' ', '-')}",
        "name": name,
        "sex": sex,
        "status": "alive",
        "breed_composition": {
            "percentages": breed_percentages,
            "hair_percentage": round(hair_pct, 1),
            "coat_type": coat_type,
        },
        "health": {},
        "breeding": {"offspring_ids": []},
    }
    if weight:
        record["weight_lbs"] = weight
    return record


# ═══════════════════════════════════════════════════════════════════
# MAIN — CLI interface
# ═══════════════════════════════════════════════════════════════════

def main():
    with open(DB_PATH) as f:
        db = json.load(f)

    db_by_id = {s["id"]: s for s in db["sheep"]}

    if len(sys.argv) < 2:
        print_usage(db, db_by_id)
        return

    command = sys.argv[1]

    if command == "cross":
        if len(sys.argv) < 4:
            print("Usage: breeding_projector.py cross <sire_id> <dam_id>")
            return
        sire_id = sys.argv[2]
        dam_id = sys.argv[3]
        if sire_id not in db_by_id:
            print(f"Error: Sire '{sire_id}' not found in database")
            return
        if dam_id not in db_by_id:
            print(f"Error: Dam '{dam_id}' not found in database")
            return
        pred = predict_all_traits(db_by_id[sire_id], db_by_id[dam_id], db_by_id)
        print(format_report(pred))

    elif command == "pen":
        pen_name = sys.argv[2] if len(sys.argv) > 2 else None
        pens = get_pen_assignments(db)
        if not pen_name:
            print("Available pens:")
            for pen, data in sorted(pens.items()):
                rams = ", ".join(r["name"] for r in data["rams"])
                ewes = ", ".join(e["name"] for e in data["ewes"])
                print(f"  {pen}: rams=[{rams}]  ewes=[{ewes}]")
            return
        projections = project_pen(pen_name, pens, db_by_id)
        if not projections:
            print(f"No crosses possible for {pen_name}")
            return
        for pred in projections:
            print(format_report(pred))
            print("\n")

    elif command == "custom":
        # Example: breeding_projector.py custom "My Ram" ram "Katahdin:50,Dorper:50" dam_id
        if len(sys.argv) < 6:
            print("Usage: breeding_projector.py custom <name> <sex> "
                  "<breed:pct,breed:pct> <mate_id>")
            return
        name = sys.argv[2]
        sex = sys.argv[3]
        breed_str = sys.argv[4]
        mate_id = sys.argv[5]

        # Parse breed string — supports "Katahdin:50,Dorper:50" or "50% Katahdin, 50% Dorper"
        breed_pcts = {}
        for part in breed_str.split(","):
            part = part.strip()
            if ":" in part:
                breed, pct = part.rsplit(":", 1)
                breed_pcts[breed.strip()] = float(pct)
            elif "%" in part:
                # "50% Katahdin" format
                pct_str, breed = part.split("%", 1)
                breed_pcts[breed.strip()] = float(pct_str.strip())
            else:
                print(f"Error: Cannot parse breed entry '{part}'")
                print("Use 'Breed:pct' or 'pct% Breed' format")
                return

        custom = make_custom_sheep(name, sex, breed_pcts)
        mate = db_by_id.get(mate_id)
        if not mate:
            print(f"Error: Mate '{mate_id}' not found")
            return

        if sex == "ram":
            pred = predict_all_traits(custom, mate, db_by_id)
        else:
            pred = predict_all_traits(mate, custom, db_by_id)
        print(format_report(pred))

    elif command == "all":
        # Project all current pen assignments
        pens = get_pen_assignments(db)
        for pen_name in sorted(pens.keys()):
            projections = project_pen(pen_name, pens, db_by_id)
            if projections:
                print(f"\n{'#' * 80}")
                print(f"# PEN: {pen_name}")
                print(f"{'#' * 80}")
                for pred in projections:
                    print(format_report(pred))
                    print()

    else:
        print(f"Unknown command: {command}")
        print_usage(db, db_by_id)


def print_usage(db, db_by_id):
    print("Manatee Creek Sheep — Breeding Results Projector")
    print()
    print("Usage:")
    print("  breeding_projector.py cross <sire_id> <dam_id>")
    print("  breeding_projector.py pen [pen_name]")
    print("  breeding_projector.py custom <name> <sex> <breed:pct,...> <mate_id>")
    print("  breeding_projector.py all")
    print()
    print("Examples:")
    print('  python3 scripts/breeding_projector.py cross kelsier serendipity')
    print('  python3 scripts/breeding_projector.py pen "Pen 4"')
    print('  python3 scripts/breeding_projector.py custom "Test Ram" ram '
          '"Katahdin:50,Dorper:50" serendipity')
    print()

    # Show available breeding animals
    pens = get_pen_assignments(db)
    print("Current pen assignments:")
    for pen, data in sorted(pens.items()):
        rams = [f"{r['name']} ({r['id']})" for r in data["rams"]]
        ewes = [f"{e['name']} ({e['id']})" for e in data["ewes"]]
        print(f"  {pen}:")
        if rams:
            print(f"    Rams: {', '.join(rams)}")
        if ewes:
            print(f"    Ewes: {', '.join(ewes)}")


if __name__ == "__main__":
    main()
