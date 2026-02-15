#!/usr/bin/env python3
"""
Parasite Resistance Scoring Algorithm for Manatee Creek Sheep.

Produces a composite score (0–100) for each sheep indicating how parasite-
resistant it is, where 100 = most resistant and 0 = least resistant.

Data sources used (in priority order):
  1. FAMACHA scores    — direct phenotypic evidence
  2. Treatment records — frequency of deworming / iron treatments
  3. Weak resistance flag — owner's experienced observation
  4. Health notes      — mentions of parasite issues
  5. Lineage scoring   — inherited from sire/dam scores
  6. Breed composition — some breeds are inherently more resistant
  7. Owner observations — Sir Loin's line and Kelsier noted as very resistant

Scoring approach:
  We compute sub-scores for each factor, weight them, then blend with
  lineage-inherited scores for sheep that lack direct observations.

  For sheep WITH direct data:
    40% FAMACHA sub-score
    25% Treatment sub-score
    20% Weak-resistance / health-note sub-score
    15% Breed sub-score

  For sheep WITHOUT direct data:
    50% Lineage-inherited score (avg of sire & dam scores)
    35% Breed sub-score
    15% Owner-observation bonus (known resistant lines)

References:
  - FAMACHA system: Kaplan et al. (2004), Vet Parasitol 123:47-56
  - Hair sheep parasite resistance: Burke & Miller (2020), Small Ruminant Res 181:13-17
  - Katahdin selection for resistance: Vanimisetti et al. (2004), J Anim Sci 82:595-604
"""

import json
import os
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, "..", "data", "flock_database.json")


# ── Breed-level parasite resistance ratings ───────────────────────
# Scale 0-100 based on published literature and breed characteristics.
# Hair sheep and tropically-adapted breeds score highest.
# Wool breeds and meat breeds with no tropical adaptation score lowest.
BREED_RESISTANCE = {
    "American Blackbelly":   90,   # Hair sheep, tropical origin, excellent resistance
    "Barbados Blackbelly":   92,   # Hair sheep, Caribbean origin, top-tier resistance
    "St Croix":              95,   # Hair sheep, Caribbean, among the most resistant breeds known
    "Katahdin":              80,   # Hair sheep, developed for parasite resistance
    "Gulf Coast Native":     85,   # Adapted to humid subtropical, strong natural resistance
    "Cracker":               82,   # Florida native breed, adapted to local parasites
    "St Augustine":          70,   # Regional hair/wool cross, moderate-good resistance
    "Wiltshire Horn":        65,   # Self-shedding, moderate resistance
    "Dorper":                50,   # Meat breed, moderate-low resistance
    "White Dorper":          50,   # Same as Dorper
    "Black Headed Dorper":   50,   # Same as Dorper
    "Awassi":                55,   # Fat-tail breed, some tropical adaptation
    "Tunis":                 55,   # North African origin, moderate resistance
    "Karakul":               50,   # Fat-tail breed, some adaptation
    "Jacob":                 45,   # Heritage breed, no particular resistance
    "East Friesian":         30,   # Dairy breed, poor parasite resistance
    "Hampshire":             35,   # Wool meat breed, below average resistance
    "Suffolk":               30,   # Wool meat breed, poor resistance
    "Cotswold":              25,   # Long-wool breed, poor resistance
    "Babydoll":              40,   # Miniature wool breed, moderate-low
    "Southdown":             40,   # Small meat breed, moderate-low
    "Texel":                 35,   # Continental meat breed, below average
}

# Default for unknown breeds
DEFAULT_BREED_RESISTANCE = 50


# ── Owner-observed resistant lines ────────────────────────────────
# These IDs are flagged by the owner as particularly parasite-resistant.
# Applied as a bonus when no direct FAMACHA/treatment data exists.
KNOWN_RESISTANT_IDS = {"kelsier"}
KNOWN_RESISTANT_SIRE_IDS = {"sir-loin"}  # offspring inherit a bonus


# ── FAMACHA score interpretation ──────────────────────────────────
# FAMACHA 1 = bright red (healthy), 5 = white (severely anemic/parasitized)
# We convert to a 0-100 resistance score.
FAMACHA_TO_SCORE = {
    1:   100,  # Optimal — no anemia
    1.5:  90,
    2:    80,  # Acceptable — minimal anemia
    2.5:  65,
    3:    50,  # Borderline — moderate anemia, may need treatment
    3.5:  35,
    4:    20,  # Dangerous — significant anemia
    4.5:  10,
    5:     0,  # Severely anemic — critical
}


def _parse_famacha(score_val):
    """Parse a FAMACHA score value to float, handling 'good' etc."""
    if isinstance(score_val, (int, float)):
        return float(score_val)
    if isinstance(score_val, str):
        s = score_val.strip().lower()
        if s in ("good", "excellent", "ok"):
            return 1.5  # Treat qualitative "good" as ~1.5
        try:
            return float(s)
        except ValueError:
            return None
    return None


def _famacha_subscore(famacha_records):
    """
    Calculate FAMACHA-based resistance sub-score (0-100).

    Uses the WEIGHTED AVERAGE of all scores, giving more weight to
    recent scores. Also considers improvement over time as a positive.
    """
    if not famacha_records:
        return None

    parsed = []
    for entry in famacha_records:
        val = _parse_famacha(entry.get("score"))
        if val is not None:
            parsed.append(val)

    if not parsed:
        return None

    # Weight more recent scores higher (last score gets 2x weight)
    if len(parsed) == 1:
        avg = parsed[0]
    else:
        weights = [1.0] * len(parsed)
        weights[-1] = 2.0  # Most recent gets double weight
        weighted_sum = sum(s * w for s, w in zip(parsed, weights))
        avg = weighted_sum / sum(weights)

    # Convert average FAMACHA to resistance score
    # Linear interpolation between known points
    if avg <= 1:
        score = 100
    elif avg >= 5:
        score = 0
    else:
        # Interpolate: FAMACHA 1→100, 2→80, 3→50, 4→20, 5→0
        breakpoints = [(1, 100), (2, 80), (3, 50), (4, 20), (5, 0)]
        for i in range(len(breakpoints) - 1):
            f1, s1 = breakpoints[i]
            f2, s2 = breakpoints[i + 1]
            if f1 <= avg <= f2:
                t = (avg - f1) / (f2 - f1)
                score = s1 + t * (s2 - s1)
                break
        else:
            score = 0

    # Bonus for improvement trend (got better over time)
    if len(parsed) >= 2:
        if parsed[-1] < parsed[0]:
            score = min(100, score + 5)  # Improving trend bonus
        elif parsed[-1] > parsed[0]:
            score = max(0, score - 5)    # Worsening trend penalty

    return round(score, 1)


def _treatment_subscore(treatments, famacha_records):
    """
    Calculate treatment-based resistance sub-score (0-100).

    Fewer parasite-related treatments = higher score.
    We filter to only parasite-related treatments (ivermectin, iron, dewormer).
    Non-parasite treatments (foot rot, thiamine) are excluded.
    """
    if not treatments and not famacha_records:
        return None  # No data at all

    # Count parasite-related treatments
    parasite_keywords = {"ivermectin", "iron", "dewormer", "deworm", "safeguard",
                         "cydectin", "prohibit", "valbazen", "nutridrench",
                         "vitamin b", "b-complex"}
    # Non-parasite keywords to exclude
    exclude_keywords = {"foot rot", "terramycin", "thiamine", "hoof", "lameness",
                        "cd&t", "vaccine", "vaccination"}

    parasite_tx_count = 0
    for tx in (treatments or []):
        treatment_str = tx.get("treatment", "").lower()
        # Skip non-parasite treatments
        if any(kw in treatment_str for kw in exclude_keywords):
            continue
        if any(kw in treatment_str for kw in parasite_keywords):
            parasite_tx_count += 1

    # Also count FAMACHA entries that resulted in treatment
    for entry in (famacha_records or []):
        notes = entry.get("notes", "").lower()
        if any(kw in notes for kw in parasite_keywords):
            # Don't double-count if already in treatments
            parasite_tx_count += 0.5

    # Scoring: 0 treatments = 100, each treatment knocks off points
    if parasite_tx_count == 0:
        return 100
    elif parasite_tx_count <= 0.5:
        return 90
    elif parasite_tx_count <= 1:
        return 70
    elif parasite_tx_count <= 2:
        return 50
    elif parasite_tx_count <= 3:
        return 30
    else:
        return 10


def _weakness_subscore(weak_resistance, health_notes):
    """
    Score based on weak resistance flag and health note mentions.
    Returns 0-100 where 100 = no weakness indicators.
    """
    score = 100

    if weak_resistance:
        score -= 60  # Major penalty for being on the weak list

    # Check health notes for parasite mentions
    parasite_note_keywords = {"parasite", "white eyes", "eyes were white", "anemic",
                              "worm", "barber pole", "low score", "low famacha"}
    for note in (health_notes or []):
        note_lower = note.lower()
        if any(kw in note_lower for kw in parasite_note_keywords):
            score -= 15

    return max(0, score)


def _breed_subscore(breed_composition):
    """
    Calculate breed-based resistance sub-score (0-100).
    Weighted average of breed resistance ratings by percentage.
    """
    percentages = breed_composition.get("percentages", {})
    if not percentages:
        return DEFAULT_BREED_RESISTANCE

    total_weight = 0
    weighted_score = 0
    for breed, pct in percentages.items():
        resistance = BREED_RESISTANCE.get(breed, DEFAULT_BREED_RESISTANCE)
        weighted_score += resistance * pct
        total_weight += pct

    if total_weight == 0:
        return DEFAULT_BREED_RESISTANCE

    return round(weighted_score / total_weight, 1)


def _owner_observation_bonus(sheep_id, sire_id, dam_id):
    """
    Bonus points for sheep the owner has specifically noted as resistant.
    Sir Loin's offspring and Kelsier.
    """
    bonus = 0

    if sheep_id in KNOWN_RESISTANT_IDS:
        bonus += 15

    if sire_id in KNOWN_RESISTANT_SIRE_IDS:
        bonus += 10

    if dam_id in KNOWN_RESISTANT_SIRE_IDS:
        bonus += 10

    return bonus


def score_individual(sheep_record, db_by_id):
    """
    Calculate parasite resistance score for a single sheep.

    Returns dict:
      {
        "score": float 0-100,
        "grade": str (A/B/C/D/F),
        "confidence": str (high/medium/low),
        "has_direct_data": bool,
        "subscores": {
            "famacha": float or None,
            "treatment": float or None,
            "weakness": float or None,
            "breed": float,
            "lineage": float or None,
            "owner_obs": float,
        },
        "explanation": str,
      }
    """
    sid = sheep_record["id"]
    health = sheep_record.get("health", {})
    famacha = health.get("famacha_scores", [])
    treatments = health.get("treatments", [])
    weak_resistance = health.get("weak_resistance", False)
    health_notes = health.get("notes", [])
    breed_comp = sheep_record.get("breed_composition", {})
    sire_id = sheep_record.get("sire_id")
    dam_id = sheep_record.get("dam_id")

    # Calculate all sub-scores
    fam_score = _famacha_subscore(famacha)
    tx_score = _treatment_subscore(treatments, famacha)
    weak_score = _weakness_subscore(weak_resistance, health_notes)
    breed_score = _breed_subscore(breed_comp)
    owner_bonus = _owner_observation_bonus(sid, sire_id, dam_id)

    # Determine if we have direct phenotypic data
    has_direct = bool(famacha or treatments or weak_resistance or health_notes)

    explanations = []

    if has_direct:
        # ── DIRECT DATA PATH ──────────────────────────────────
        # Weight: 40% FAMACHA, 25% treatment, 20% weakness, 15% breed
        components = []
        weights = []

        if fam_score is not None:
            components.append(fam_score)
            weights.append(0.40)
            explanations.append(f"FAMACHA avg→{fam_score}")
        else:
            # Redistribute FAMACHA weight to treatment and weakness
            pass

        if tx_score is not None:
            components.append(tx_score)
            weights.append(0.25)
            if tx_score < 70:
                explanations.append(f"Treatment history→{tx_score}")

        components.append(weak_score)
        weights.append(0.20)
        if weak_resistance:
            explanations.append("On weak resistance list")

        components.append(breed_score)
        weights.append(0.15)

        # Normalize weights
        total_w = sum(weights)
        composite = sum(s * w / total_w for s, w in zip(components, weights))

        # Apply owner observation bonus (capped)
        composite = min(100, composite + owner_bonus)

        confidence = "high" if fam_score is not None else "medium"

    else:
        # ── LINEAGE-INHERITED PATH ────────────────────────────
        # No direct data — infer from parents and breed
        lineage_scores = []
        if sire_id and sire_id in db_by_id:
            sire_rec = db_by_id[sire_id]
            sire_health = sire_rec.get("health", {})
            sire_fam = _famacha_subscore(sire_health.get("famacha_scores", []))
            sire_weak = sire_health.get("weak_resistance", False)
            if sire_fam is not None:
                lineage_scores.append(sire_fam)
            elif sire_weak:
                lineage_scores.append(30)
            elif sire_id in KNOWN_RESISTANT_SIRE_IDS:
                lineage_scores.append(85)

        if dam_id and dam_id in db_by_id:
            dam_rec = db_by_id[dam_id]
            dam_health = dam_rec.get("health", {})
            dam_fam = _famacha_subscore(dam_health.get("famacha_scores", []))
            dam_weak = dam_health.get("weak_resistance", False)
            if dam_fam is not None:
                lineage_scores.append(dam_fam)
            elif dam_weak:
                lineage_scores.append(30)

        if lineage_scores:
            lineage_avg = sum(lineage_scores) / len(lineage_scores)
            # 50% lineage, 35% breed, 15% owner observation
            composite = lineage_avg * 0.50 + breed_score * 0.35 + owner_bonus * 0.15
            explanations.append(f"Lineage-inherited ({len(lineage_scores)} parent(s))")
            confidence = "medium"
        else:
            # Only breed and owner observation
            composite = breed_score + owner_bonus
            explanations.append("Breed-only estimate (no phenotypic or lineage data)")
            confidence = "low"

    composite = max(0, min(100, round(composite, 1)))

    # Letter grade
    if composite >= 85:
        grade = "A"
    elif composite >= 70:
        grade = "B"
    elif composite >= 55:
        grade = "C"
    elif composite >= 40:
        grade = "D"
    else:
        grade = "F"

    if owner_bonus > 0:
        if sid in KNOWN_RESISTANT_IDS:
            explanations.append("Owner-noted resistant (Kelsier)")
        if sire_id in KNOWN_RESISTANT_SIRE_IDS or dam_id in KNOWN_RESISTANT_SIRE_IDS:
            explanations.append("Sir Loin lineage (owner-noted resistant line)")

    return {
        "score": composite,
        "grade": grade,
        "confidence": confidence,
        "has_direct_data": has_direct,
        "subscores": {
            "famacha": fam_score,
            "treatment": tx_score,
            "weakness": weak_score,
            "breed": breed_score,
            "lineage": round(sum(lineage_scores) / len(lineage_scores), 1) if not has_direct and lineage_scores else None,
            "owner_obs": owner_bonus,
        },
        "explanation": "; ".join(explanations) if explanations else "Breed-based estimate",
    }


def score_all(db):
    """
    Score all sheep in the database.
    Returns dict: {sheep_id: score_dict}
    """
    db_by_id = {s["id"]: s for s in db["sheep"]}
    results = {}

    for sheep in db["sheep"]:
        results[sheep["id"]] = score_individual(sheep, db_by_id)

    return results


def print_report(db, scores):
    """Print a human-readable parasite resistance report."""
    by_id = {s["id"]: s for s in db["sheep"]}

    # Only show alive sheep in the main ranking
    alive_scores = {sid: sc for sid, sc in scores.items()
                    if by_id[sid].get("status") == "alive"}

    print("=" * 90)
    print("MANATEE CREEK SHEEP — PARASITE RESISTANCE REPORT")
    print("=" * 90)
    print()

    # Summary stats
    all_scores = [sc["score"] for sc in alive_scores.values()]
    high_conf = [sc for sc in alive_scores.values() if sc["confidence"] == "high"]
    med_conf = [sc for sc in alive_scores.values() if sc["confidence"] == "medium"]
    low_conf = [sc for sc in alive_scores.values() if sc["confidence"] == "low"]

    print(f"Alive sheep scored: {len(alive_scores)}")
    print(f"  High confidence (direct FAMACHA):  {len(high_conf)}")
    print(f"  Medium confidence (treatments/lineage): {len(med_conf)}")
    print(f"  Low confidence (breed estimate only): {len(low_conf)}")
    print(f"  Average score: {round(sum(all_scores)/len(all_scores), 1)}")
    print()

    # Grade distribution
    grade_counts = defaultdict(int)
    for sc in alive_scores.values():
        grade_counts[sc["grade"]] += 1
    print("Grade distribution:")
    for g in ["A", "B", "C", "D", "F"]:
        count = grade_counts.get(g, 0)
        bar = "#" * count
        print(f"  {g}: {count:3d}  {bar}")
    print()

    # Top 15 most resistant
    ranked = sorted(alive_scores.items(), key=lambda x: -x[1]["score"])
    print("-" * 90)
    print(f"{'RANK':<5} {'NAME':<25} {'SCORE':>6} {'GR':>3} {'CONF':<7} {'EXPLANATION'}")
    print("-" * 90)

    print("\n  TOP 15 — MOST RESISTANT:")
    for i, (sid, sc) in enumerate(ranked[:15]):
        sheep = by_id[sid]
        name = sheep["name"]
        tag = sheep.get("tag", "")
        tag_str = f" (tag {tag})" if tag else ""
        print(f"  {i+1:<4} {name + tag_str:<25} {sc['score']:>6.1f} {sc['grade']:>3} {sc['confidence']:<7} {sc['explanation'][:45]}")

    # Bottom 15 — least resistant
    print(f"\n  BOTTOM 15 — LEAST RESISTANT:")
    for i, (sid, sc) in enumerate(reversed(ranked[-15:])):
        sheep = by_id[sid]
        name = sheep["name"]
        tag = sheep.get("tag", "")
        tag_str = f" (tag {tag})" if tag else ""
        rank = len(ranked) - i
        print(f"  {rank:<4} {name + tag_str:<25} {sc['score']:>6.1f} {sc['grade']:>3} {sc['confidence']:<7} {sc['explanation'][:45]}")

    # Weak resistance list analysis
    print(f"\n{'=' * 90}")
    print("WEAK RESISTANCE LIST — DETAILED BREAKDOWN")
    print(f"{'=' * 90}")
    weak_sheep = [(sid, sc) for sid, sc in alive_scores.items()
                  if by_id[sid].get("health", {}).get("weak_resistance")]
    weak_sheep.sort(key=lambda x: x[1]["score"])
    for sid, sc in weak_sheep:
        sheep = by_id[sid]
        subs = sc["subscores"]
        print(f"\n  {sheep['name']} (score: {sc['score']}, grade: {sc['grade']})")
        print(f"    FAMACHA: {subs['famacha'] if subs['famacha'] is not None else 'no data'}")
        print(f"    Treatment: {subs['treatment'] if subs['treatment'] is not None else 'no data'}")
        print(f"    Weakness penalty: {subs['weakness']}")
        print(f"    Breed baseline: {subs['breed']}")

    # Owner-noted resistant lines
    print(f"\n{'=' * 90}")
    print("OWNER-NOTED RESISTANT LINES")
    print(f"{'=' * 90}")

    # Sir Loin's offspring
    sl = by_id.get("sir-loin")
    if sl:
        offspring_ids = sl.get("breeding", {}).get("offspring_ids", [])
        print(f"\n  Sir Loin's offspring ({len(offspring_ids)} total):")
        for oid in offspring_ids:
            if oid in alive_scores:
                sc = alive_scores[oid]
                o = by_id[oid]
                print(f"    {o['name']:<25} score: {sc['score']:>5.1f}  grade: {sc['grade']}  {sc['confidence']}")

    # Kelsier
    if "kelsier" in alive_scores:
        sc = alive_scores["kelsier"]
        print(f"\n  Kelsier:  score: {sc['score']}, grade: {sc['grade']}")

    print()


def main():
    with open(DB_PATH) as f:
        db = json.load(f)

    scores = score_all(db)
    print_report(db, scores)

    return scores


if __name__ == "__main__":
    main()
