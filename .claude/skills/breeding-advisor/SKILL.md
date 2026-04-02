---
name: breeding-advisor
description: "Evaluate proposed sheep matings against a 30-point checklist derived from multi-LLM orchestra review and peer-reviewed research. Every pairing must pass all HARD_BLOCKs, score RISK factors, and report SOFT_PREFERENCEs. Ewe survival is priority #1."
version: 1.0.0
---

# Breeding Advisor — Manatee Creek Flock

*Soli Deo Gloria — these animals depend on correct decisions.*

## Purpose

Evaluate ANY proposed ram × ewe pairing against this checklist. Run every check in order. If a HARD_BLOCK fires, REJECT the pairing immediately. Accumulate RISK_SCORE points. If total risk ≥ 14, REJECT. Report all SOFT_PREFERENCEs for human decision.

## How to Use

```
"Should I breed [ram] to [ewe]?"
"Evaluate [ram] × [ewe]"
"Who should go with [ram] in Pen [N]?"
```

The advisor reads `data/flock_database.json`, evaluates the checklist, and returns:
- APPROVED / REJECTED / CONDITIONAL
- Risk score breakdown
- Warnings
- Reasoning

## Data Required Per Animal

Before evaluating, confirm these fields exist in the database:
- `name`, `id`, `sex`, `tag`
- `breed_composition.percentages` (all breeds summing to ~100%)
- `dob` or `dob_approximate`
- `weight_lbs` (or estimate from breed standard)
- `pen` (current location)
- `status` (must be "alive")
- `sire_id`, `dam_id` (for inbreeding check)
- `health.famacha_history` (last 90 days minimum)
- `health.vaccinations` (CDT/Covexin within 12 months)

If data is missing, flag it. Do NOT guess. Mark the check as INCOMPLETE.

---

## THE CHECKLIST (30 factors, ordered by priority)

### HARD BLOCKS (any one = REJECT)

**1. EWE_STATUS_CHECK**
- Data: ewe `status`
- Rule: ewe must be `alive` and not `sold`, `deceased`, `gifted`, `culled`
- If FAIL → REJECT. Dead sheep don't breed.

**2. RAM_STATUS_CHECK**
- Data: ram `status`
- Rule: ram must be `alive`
- If FAIL → REJECT.

**3. RAM_FERTILITY_CHECK**
- Data: ram breeding history (ewes exposed vs ewes lambed)
- Rule: if ram exposed to ≥3 ewes for ≥6 months and ≤1 conceived → SUBFERTILE → REJECT
- Source: MSD Vet Manual, Dyneval review on subfertility
- Flock lesson: Eclipse (tag 113) bred 1/6 ewes in >1 year. Proven ewes, his fault.

**4. EWE_FAMACHA_HARD_BLOCK**
- Data: ewe `health.famacha_history`, last 90 days
- Rule: if ewe's most recent FAMACHA ≥ 4, OR if ewe has had ≥2 scores of 4-5 in past 6 months → REJECT
- Why: breeding a severely parasitized ewe risks her life during pregnancy
- Source: OSU Sheep Team FAMACHA guidance; ACSRPC selective treatment protocols
- Flock lesson: Gigi scored FAMACHA 5 twice in Feb 2026. Azure's baby scored 5 on 4-1-26.

**5. RAM_FAMACHA_HARD_BLOCK**
- Data: ram `health.famacha_history`, last 90 days
- Rule: if ram's most recent FAMACHA ≥ 4 → REJECT
- Why: parasitized rams have reduced semen quality and pass susceptibility

**6. INBREEDING_HARD_BLOCK**
- Data: `sire_id`, `dam_id` for both animals, traced 3 generations
- Rule: REJECT if ram is the ewe's sire, grandsire, full sibling, or half-sibling
- Rule: REJECT if calculated inbreeding coefficient F > 12.5% for proposed offspring
- Source: Barbados Blackbelly Sheep Assoc COI guidelines; St. Croix breeders practical guidelines
- Note: "Inbred is better than dead" — but F > 12.5% is too high.

**7. EWE_AGE_HARD_BLOCK**
- Data: ewe `dob`, current date
- Rule: REJECT if ewe < 10 months old (physically immature, pelvis not developed)
- Rule: REJECT if ewe > 9 years old AND has history of lambing difficulty
- Source: SDSU Extension ewe lamb breeding guidelines

**8. VACCINATION_HARD_BLOCK**
- Data: ewe and ram `health.vaccinations`
- Rule: REJECT if either animal lacks CDT/Covexin vaccination within past 12 months
- Why: unvaccinated animals risk Clostridial disease during pregnancy stress
- Flock note: All pens got Covexin 8 (goat vac for sheep) in March 2026.

**9. DISEASE_HARD_BLOCK**
- Data: ewe and ram health records
- Rule: REJECT if either animal has active contagious disease (foot rot, CL, pink eye, respiratory)
- Why: pregnancy stress + active disease = death risk

**10. EWE_RECOVERY_HARD_BLOCK**
- Data: ewe last lambing date, current date
- Rule: REJECT if ewe lambed < 5 months ago (insufficient recovery)
- Source: General veterinary guidance for subtropical conditions
- Flock note: Fawn Wool 114 lambed 3-29-26. Cannot breed again before Sept 2026.

### RISK SCORES (accumulate points, ≥14 total = REJECT)

**11. DYSTOCIA_BIRTHWEIGHT_RISK** (0-6 points)
- Data: ram's known lamb birthweights, ewe's known lamb birthweights, ewe weight
- Predicted BW = (0.65 × ewe avg lamb BW) + (0.35 × ram avg lamb BW) + litter adjustment
- Litter adjustment: singleton +2 lbs, twins -1 lb, triplets -3 lbs
- IF ewe is HIGH_OUTPUT line (Gigi, Azure): add +3 lbs (they throw big singles)
- Scoring:
  - Predicted BW 6-10 lbs → 0 points
  - Predicted BW 10-12 lbs → +2 points
  - Predicted BW 12-14 lbs → +4 points
  - Predicted BW > 14 lbs → +6 points
- Source: Dwyer & Bünger dystocia review; Hallowell et al. lambing difficulty factors
- Flock lesson: 00110 (50% Cracker/25% Suffolk) threw 12-15 lb lambs. Suffolk = big lambs.
- IMPORTANT: Use ACTUAL flock birthweights, not breed standards. Florida Dorper are small-framed.

**12. EWE_SIZE_VS_RAM_SIZE_RISK** (0-4 points)
- Data: ewe `weight_lbs`, ram `weight_lbs` (actual or estimated)
- Rule: if ram weight > 2× ewe weight → +4 points
- Rule: if ram weight > 1.5× ewe weight → +2 points
- Rule: if ram weight < 1.3× ewe weight → 0 points
- Why: oversized rams on small ewes = large lambs that don't fit
- Flock lesson: 00110 is 275-300 lbs. Florida Dorper ewes are ~100-130 lbs. That's 2×+ ratio.

**13. FIRST_TIMER_RISK** (0-4 points)
- Data: ewe reproductive history (prior lambings)
- Rule: if ewe has NEVER lambed before → +3 points
- Rule: if ewe is < 18 months old at expected lambing → +1 additional point
- Why: first lambing is highest risk for dystocia
- Source: McHugh et al. lambing risk factors

**14. EWE_PARASITE_HISTORY_RISK** (0-4 points)
- Data: ewe FAMACHA history, all available records
- Rule: if ewe has average FAMACHA ≥ 3.0 over past year → +2 points
- Rule: if ewe has ever scored FAMACHA 5 → +2 additional points
- Why: chronic parasite susceptibility worsens during pregnancy immunosuppression
- Source: UF/IFAS VM264; Vanimisetti et al. hair sheep parasite resistance
- Flock lesson: Gigi/Azure line dominates for susceptibility even with resistant sire.

**15. DAM_LINE_PARASITE_RISK** (0-3 points)
- Data: ewe's dam and grandam FAMACHA history (if available)
- Rule: if ewe's dam had chronic FAMACHA ≥ 3 → +2 points (susceptibility is heritable, h² 0.2-0.4)
- Rule: if ewe's dam AND grandam both had chronic issues → +3 points
- Source: Ngere et al. 2018 Katahdin FEC heritability; Safari et al. 2005 genetic parameters
- Flock lesson: Azure is Gigi's sister. Baby Azure (Azure's daughter) scored FAMACHA 5. Three generations of weakness.

**16. HIGH_OUTPUT_LINE_RISK** (0-3 points)
- Data: ewe's lambing history (twins/triplets frequency), maternal line
- Rule: if ewe frequently has twins or triplets → +2 points with TERMINAL or large ram
- Rule: if ewe is from known HIGH_OUTPUT line (Gigi, Azure, Elsie) → +1 additional
- Why: HIGH_OUTPUT + big ram = large or multiple large lambs = dystocia
- Source: GPT breeding spec review; Hatcher et al. ewe mortality factors

**17. RAM_TEMPERAMENT_RISK** (0-3 points)
- Data: handler observations, notes
- Rule: if ram is documented aggressive toward ewes or lambs → +3 points
- Rule: if ram is aggressive toward other rams but not ewes → +1 point
- Flock lesson: Rocky (Jerkface) kept Fawn Wool 114 away from her newborn. Charlie is sexually aggressive/dominant but not documented hurting ewes.

**18. EWE_BCS_RISK** (0-3 points)
- Data: ewe body condition score (1-5 scale)
- Rule: BCS < 2.5 → +3 points (underweight, pregnancy toxemia risk)
- Rule: BCS > 4.0 → +2 points (overweight, dystocia risk)
- Rule: BCS 2.5-4.0 → 0 points
- Source: Zoetis flock health; OSU breeding season considerations
- Flock note: Serendipity was "skinny" while nursing twins 2-27-26.

**19. SEASONAL_TIMING_RISK** (0-2 points)
- Data: expected breeding date → calculate lambing date (breeding + 147 days)
- Rule: if lambing falls June-August (Florida peak heat) → +2 points
- Why: heat stress reduces lamb survival and ewe recovery
- Source: Frontiers in Animal Science, hair sheep subtropical adaptation

**20. RAM_BREEDING_LOAD_RISK** (0-2 points)
- Data: number of ewes already assigned to this ram this season
- Rule: > 6 ewes for yearling ram → +2 points
- Rule: > 15 ewes for mature ram → +2 points
- Source: Sheep 101 ram:ewe ratios; AW Extension WA conception strategies

**21. INBREEDING_WARNING_RISK** (0-2 points)
- Data: calculated F coefficient for proposed offspring
- Rule: F 3.125%-6.25% → +1 point (flag, monitor)
- Rule: F 6.25%-12.5% → +2 points (concerning but not blocked)
- Source: PMC inbreeding study in small flocks

**22. WOOL_VS_HAIR_RISK** (0-2 points)
- Data: ram and ewe coat genetics (hair% from breed composition)
- Rule: if pairing produces offspring < 50% hair genetics → +2 points
- Why: wool lambs in Florida = higher parasite load, heat stress, shearing costs
- Flock goal: moving toward hair sheep. Wool is a step backward.

### SOFT PREFERENCES (tiebreakers, 0-1 points each)

**23. PARASITE_RESISTANCE_BOOST**
- If ram has ≥50% Cracker, Katahdin, St. Croix, GCN, or ABB genetics → +1 preference point
- Source: UF/IFAS VM264 breed recommendations for Florida

**24. MEAT_PRODUCTION_BOOST**
- If pairing expected to produce offspring with ≥25% BHD, Dorper, or Suffolk → +1 preference
- Why: market lambs need meat genetics

**25. CLIMATE_ADAPTATION_BOOST**
- If both parents are hair sheep or Florida-adapted breeds → +1 preference
- Source: UF/IFAS; Frontiers review on hair sheep in Americas

**26. GENETIC_DIVERSITY_BOOST**
- If pairing introduces breed genetics not currently dominant in flock → +1 preference
- Why: hybrid vigor, long-term flock health

**27. PROVEN_DAM_BOOST**
- If ewe has ≥2 successful lambings with no complications → +1 preference
- Why: known good mothers are lower risk

**28. NSIP_DATA_BOOST**
- If ram or ewe has NSIP enrollment with favorable EPDs → +1 preference
- Source: NSIP registry; Burke et al. 2023 low-FEC EBV sire studies
- Flock note: Kelsier (deceased) was NSIP enrolled. FEC avg 138.8, ADG 0.36. Gold standard.

### INFORMATIONAL (track, don't score)

**29. ECONOMIC_VALUE**
- Data: estimated market value of offspring, feed cost, vet cost
- Track: is this pairing cost-effective?
- Source: Silva et al. lamb production cost analysis

**30. OFFSPRING_RETENTION_PLAN**
- Data: breeder intent (keep daughters? sell all? wether rams?)
- Track: if EXPERIMENTAL ram, do NOT retain daughters until proven
- Flock note: MC08 is experimental. Don't retain his daughters yet.

---

## SCORING SUMMARY

```
TOTAL_RISK = sum of all RISK_SCORE points (checks 11-22)

If ANY HARD_BLOCK fires (checks 1-10) → REJECT
If TOTAL_RISK ≥ 14 → REJECT (CRITICAL risk)
If TOTAL_RISK 10-13 → CONDITIONAL (HIGH risk, needs human override)
If TOTAL_RISK 6-9 → APPROVED WITH CAUTION (MODERATE risk)
If TOTAL_RISK 0-5 → APPROVED (LOW risk)

PREFERENCE_SCORE = sum of SOFT_PREFERENCE points (checks 23-28)
Use to rank multiple approved pairings for the same ewe.
```

## OUTPUT FORMAT

For each proposed pairing, output:

```
RAM: [name] (tag [tag])
EWE: [name] (tag [tag])
DECISION: APPROVED / CONDITIONAL / REJECTED
RISK SCORE: [N] / 30 possible
RISK LEVEL: LOW / MODERATE / HIGH / CRITICAL

HARD BLOCKS: [list any that fired, or "None"]
RISK BREAKDOWN:
  - Dystocia BW: +[N] (predicted [X] lbs)
  - Size mismatch: +[N] (ram [X] lbs, ewe [Y] lbs)
  - First timer: +[N]
  - Parasite history: +[N]
  - Dam line parasite: +[N]
  - High output line: +[N]
  - Ram temperament: +[N]
  - BCS: +[N]
  - Seasonal: +[N]
  - Ram load: +[N]
  - Inbreeding: +[N] (F=[X]%)
  - Wool/Hair: +[N]
PREFERENCES: [list any that apply]
WARNINGS: [anything the human should know]
DATA GAPS: [any missing data that prevented full evaluation]
```

## SOURCES

- UF/IFAS Extension VM264: Selection of Sheep Meat Breeds in Florida
- Dwyer & Bünger: A review of dystocia in sheep
- Ngere et al. 2018: Genome-wide association study of GIN resistance in Katahdin
- Safari et al. 2005: Review of genetic parameters for sheep production traits
- Burke et al. 2023: Low-FEC EBV sire effects on lamb parasite resistance
- Forbes et al. 2024: Adding GI parasite resistance to hair sheep breeding objective
- McHugh et al.: Risk factors associated with lambing traits
- Hatcher et al.: Ewe mortality during pre-lambing and lambing
- OSU Sheep Team: Breeding Season Preparation (FAMACHA guidance)
- SDSU Extension: Breeding Ewe Lambs
- Zoetis: Flock Health Solutions (BCS guidelines)
- MSD Vet Manual: Reproductive physiology of sheep
- Manatee Creek flock data April 2026 (notebook cards, database)
