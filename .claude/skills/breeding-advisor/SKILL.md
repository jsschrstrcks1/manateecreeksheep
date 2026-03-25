---
name: breeding-advisor
description: "Interprets breeding projector output, recommends sire×dam pairings, flags inbreeding risks, and explains tradeoffs in plain language. Wraps scripts/breeding_projector.py with flock-specific knowledge."
version: 1.0.0
---

# Breeding Advisor

> *"The LORD is my shepherd; I shall not want."* — Psalm 23:1 (ESV)

We tend these sheep as stewards, not owners. Every breeding decision affects real animals.

## Purpose

Translates the technical output of `breeding_projector.py` into actionable breeding recommendations. Claude interprets heterosis calculations, inbreeding coefficients, parasite resistance scores, and coat predictions — then recommends pairings a farmer can act on.

## When to Fire

- On `/breed` command
- When discussing sire/dam pairings or breeding plans
- When evaluating ram eligibility or ewe readiness
- When planning seasonal breeding groups

## How to Use

### Quick Recommendation
```bash
python3 scripts/breeding_projector.py --sire <sire_id> --dam <dam_id>
```

### Batch Analysis (All Possible Pairs in a Pen)
```bash
python3 scripts/breeding_projector.py --pen <pen_number>
```

### Full Flock Projection
```bash
python3 scripts/breeding_projector.py --all
```

## Interpreting Results

### Heterosis (Hybrid Vigor)
- **>15%**: Excellent — diverse cross, strong vigor expected
- **10-15%**: Good — meaningful heterosis
- **5-10%**: Moderate — some benefit
- **<5%**: Low — breeds are too similar for much hybrid vigor

### Inbreeding Coefficient (COI)
- **0-3%**: Safe — no concern
- **3-6%**: Monitor — acceptable but watch for trends
- **6-12%**: Caution — may see inbreeding depression
- **>12%**: Avoid — unacceptable inbreeding risk

### Parasite Resistance Score
- **8-10**: Excellent — Katahdin-like resistance (Kelsier is the gold standard)
- **6-8**: Good — should handle Florida conditions
- **4-6**: Fair — will need monitoring
- **<4**: Poor — likely to need frequent treatment

### Coat Type Prediction
- **Hair**: Preferred for Florida heat and low maintenance
- **Dual**: Acceptable — may shed seasonally
- **Wool**: Less desirable in Florida — heat stress risk

### Confidence (Stoplight)
- **GREEN**: High confidence in prediction
- **YELLOW**: Moderate — some assumptions made
- **RED**: Low — insufficient pedigree data

## Selection Priority (This Flock)

When recommending pairings, weight these factors in this order:

1. **Parasite resistance** — #1 priority. FAMACHA drives culling and breeding.
2. **Meat quality** — Maintain body condition and growth (Dorper influence)
3. **Milk production** — Preserve Awassi genetics for dairy potential
4. **Hair coat** — Moving toward hair sheep for Florida
5. **Hybrid vigor** — Strategic crosses across 22 breeds
6. **Inbreeding avoidance** — Track all pedigrees, prevent close matings

## Breeding Rules (Enforced)

- **R1**: Exclude placeholder/unknown "twin rams" from recommendations
- **R2**: Only recommend adult rams (≥9 months) with known DOB
- **R3**: Geriatric safety: if ewe age ≥6 years, exclude Ram 00110 (Orange Tag) — reduce dystocia risk
- **R4**: Only recommend rams marked "Eligible"

## Key Genetics Reference

| Animal | Breed | Strength | Notes |
|--------|-------|----------|-------|
| Kelsier | Katahdin | Gold standard parasite resistance | Benchmark sire |
| Awassi crosses | Awassi | Best milk production | Dual-purpose value |
| Dorper-Awassi | Cross | Meatiest offspring | Market potential |
| Katahdin foundation | Katahdin | All-around best | Core of the flock |

## Weak Resistance Watch List

These animals have shown poor parasite resistance. Their genetics should be used cautiously or culled:
GG, Azure, Rocky, Dorper 23 & 25, Circle Tail, W140, FM1, Baby, Bella, FM

Deceased weak animals (no longer breeding but relevant for pedigree): Shaggy, Butter Ball, Skitters, W136, Samson, Unnamed

## Current Pen Structure

| Pen | Ram | Key Ewes |
|-----|-----|----------|
| 1 | Kaladin | Eclipse, Merrie, Abg, Fm |
| 2 | Sir Loin | Azure, S2, Lara, Bambii, Pebbles |
| 3 | Sam | Baby, Zara, Half tail |
| 4 | Samson | Elsie, Nori, Trouble, Bsoe, Banana |
| 5 | Rocky/NoriSon | Amber 24, Broken tail, Little daisy |
| 6 | No ram | Shaggy, Serendipity, S1, Fm1, Fox tail, Circle tail |

## Recommendation Format

```
## Breeding Recommendation — [date]

### Top 3 Pairings
| Rank | Sire | Dam | Heterosis | COI | Parasite Score | Confidence |
|------|------|-----|-----------|-----|----------------|------------|

### Why These Pairings
1. [Plain language explanation]
2. [Plain language explanation]
3. [Plain language explanation]

### Risks to Monitor
- [Inbreeding concerns]
- [Weak resistance genetics carried]

### Pairings to Avoid
| Sire | Dam | Reason |
|------|-----|--------|
```

## Integration

- Uses **cognitive-memory** to track breeding decisions across sessions
- Respects **careful-not-clever** — never assume pedigree data
- References **flock-validation** for data integrity
- References **image-transcription** for source verification

---

*Soli Deo Gloria* — We steward these genetics for the glory of God and the health of the flock.
