---
name: breeding-advisor
description: "Evaluate sheep matings and pipeline placement against a performance-based checklist. Select by FAMACHA/FEC first, hair/wool second, breed third, meat fourth. Manages a 7-pen closed-loop breeding pipeline toward a hardy, hairy, meaty, parasite-resistant composite flock."
version: 2.0.0
---

# Breeding Advisor — Manatee Creek Flock

*Soli Deo Gloria — these animals depend on correct decisions.*

## Two Modes

### Mode 1: PAIRING CHECK
```
"Should I breed [ram] to [ewe]?"
"Evaluate [ram] × [ewe]"
```

### Mode 2: PIPELINE CHECK
```
"Where does this animal go in the pipeline?"
"Is [animal] ready to advance?"
"Which ram lamb cycles back?"
"Sort these ewes into the pipeline."
```

The advisor reads `data/flock_database.json` and `data/breed_reference.json`.

---

## CORE PHILOSOPHY

### Selection Hierarchy (non-negotiable)
1. **FAMACHA/FEC** — Can it survive parasites with minimal intervention?
2. **Hair/Wool** — Does it shed? (OBSERVED coat, not breed-predicted)
3. **Breed Composition** — Genetic context. Informs, does not decide.
4. **Meatiness** — Tiebreaker. All else equal, choose the meatiest.

### Hard Lessons (from this flock, on this property)
- Purchased **St Croix** (famous for parasite resistance) → DIED OF PARASITES here
- Purchased **Barbados Black Belly** → DIED OF PARASITES here
- **Windlestone Dorper** (exceptional SA bloodlines) are EXTREMELY VULNERABLE to parasites despite being hair sheep
- **Hair coat ≠ parasite resistance.** Independent genetic traits.
- **Breed reputation means NOTHING.** Only individual performance on THIS property matters.
- Cracker coat type is VARIABLE per individual — Merrie sheds, 00110 does not.
- Every animal currently alive has survived Florida parasite pressure. That survival IS the proven genetics.
- **GG and Rocky survive because owner skill improved**, not because they're resistant. They require aggressive treatment.

### Breeding Program Goal
**Closed-loop pipeline** producing animals that:
- Stay FAMACHA 1-2 without deworming
- Shed coat completely (no shearing)
- Have good muscling and growth rate
- Produce consistent, predictable offspring

---

## THE PIPELINE

### Structure
7 breeding pens in a geographic loop. Best ram lambs from Pen 2 (elite) cycle back to Pen 3 (intake).

```
Pen 3 (intake) → TF → Pen 4 → Pen 5 → Pen 6 → Pen 1 → Pen 2 (elite)
  ↑                                                            |
  └──────────── best ram lambs cycle back ─────────────────────┘
```

Goose Pen = grow-out (ram lambs) + Awassi dairy line (outside loop).

### Stage Details

| Stage | Pen | Size | Location | Ram | Advancement Criteria |
|-------|-----|------|----------|-----|---------------------|
| 1 (intake) | **Pen 3** | largest | SE, east | **00110** (287 lbs, wooly, meaty) | FAMACHA <3, FEC <500, shed >25% |
| 2 | **Tree Fort** | smallest | east, best shelter | **Gigi's 2025 Ram** (Kelsier×GG) | FAMACHA <3, FEC <400, shed >35% |
| 3 | **Pen 4** | large | east | **Rocky** (300 lbs, BHD/Awassi) | FAMACHA <3, FEC <350, shed >50% |
| 4 | **Pen 5** | med-large | east | **Buck** (271 lbs, Kat/Awassi) | FAMACHA <2, FEC <300, shed >65% |
| 5 | **Pen 6** | medium | NE, east | **Merrie** (200 lbs, observed shedder) | FAMACHA <2, FEC <250, shed >80% |
| 6 | **Pen 1** | med-small | SW, west (isolated) | **Charlie** (232 lbs, 100% hair) | FAMACHA <2, FEC <200, shed >90% |
| 7 (elite) | **Pen 2** | small | SW, west (most secure) | *Best ram lamb from Pen 1* | FAMACHA 1-2 only, FEC <150, shed >95% |
| Outside | **Goose Pen** | small-med | east | **MC08** (Awassi dairy) | Separate line |

### Pipeline Rules
- Animals ADVANCE by meeting criteria, not by age
- Animals that FAIL criteria are culled or sent back one stage for retesting
- Ram lambs pulled to Goose Pen grow-out at every stage
- Best ram lambs from Pen 2 cycle back to Pen 3 as replacement sires
- Some inbreeding is INTENTIONAL (line breeding toward homogeneity, F < 0.25)
- Awassi dairy line stays OUTSIDE the loop

### Ram Gradient (wooly→hair, early→late)
| Ram | Hair % | Observed Coat | Stage |
|-----|--------|--------------|-------|
| 00110 | 12.5% | extra wooly | 1 (intake) |
| Gigi's 2025 Ram | ~50% | wooly | 2 |
| Rocky | 50% | mixed | 3 (WEAK parasites — select hard against in offspring) |
| Buck | 50% | mixed | 4 |
| Merrie | 50% breed / 100% observed | full shedder | 5 |
| Charlie | 100% | full shedder | 6 (near-finished) |
| Best Pen 1 lamb | TBD | must be shedder | 7 (elite) |

---

## PAIRING CHECKLIST (revised for pipeline context)

### HARD BLOCKS (any one = REJECT)

**1. STATUS_CHECK** — Both animals must be alive.

**2. SUBFERTILITY_CHECK** — If ram exposed to ≥3 ewes for ≥6 months and ≤1 conceived → REJECT.
- Flock lesson: Eclipse bred 1/6 ewes in >1 year. Cull.

**3. FAMACHA_HARD_BLOCK** — If ewe's most recent FAMACHA ≥ 4, OR ≥2 scores of 4-5 in past 6 months → REJECT. Same for ram.
- Source: OSU Sheep Team FAMACHA guidance

**4. INBREEDING_MANAGED** — NOT a hard block. Calculate F coefficient.
- F < 0.125: OK (flag only)
- F 0.125-0.25: CONDITIONAL (monitor offspring)
- F > 0.25: REJECT (depression risk too high)
- Father-daughter in same pipeline stage: REJECT (too fast, skip a generation)
- Line breeding across pipeline stages: ACCEPTABLE (this is the design)

**5. EWE_AGE_CHECK** — REJECT if < 10 months. REJECT if > 9 years with lambing difficulty history.

**6. VACCINATION_CHECK** — REJECT if no CDT/Covexin within 12 months.

**7. DISEASE_CHECK** — REJECT if active contagious disease.

**8. RECOVERY_CHECK** — REJECT if ewe lambed < 5 months ago.

### RISK SCORES (accumulate, ≥14 = REJECT)

**9. DYSTOCIA_RISK** (0-6 pts) — Ram weight vs ewe weight, predicted birthweight.
- Ram > 2× ewe weight → +4 pts
- Ram > 1.5× ewe weight → +2 pts
- Predicted BW > 12 lbs → +4 pts

**10. FIRST_TIMER_RISK** (0-4 pts) — Never lambed → +3. Under 18 months at lambing → +1.

**11. PARASITE_HISTORY_RISK** (0-4 pts) — Average FAMACHA ≥ 3 → +2. Ever scored 5 → +2.

**12. DAM_LINE_PARASITE_RISK** (0-3 pts) — Dam had chronic FAMACHA ≥ 3 → +2. Dam AND grandam → +3.
- Flock lesson: Azure→Baby Azure, three generations of weakness.

**13. HIGH_OUTPUT_RISK** (0-3 pts) — Frequent twins/triplets + large ram → +2.

**14. RAM_TEMPERAMENT** (0-3 pts) — Aggressive toward ewes/lambs → +3.
- Rocky kept 114 from her newborn.

**15. BCS_RISK** (0-3 pts) — BCS < 2.5 → +3. BCS > 4.0 → +2.

**16. SEASONAL_RISK** (0-2 pts) — Lambing June-August (FL peak heat) → +2.

**17. RAM_LOAD** (0-2 pts) — > 6 ewes for yearling, > 15 for mature → +2.

**18. WOOL_RISK** (0-2 pts) — Offspring < 50% hair genetics AND both parents have wool coats → +2.
- NOTE: Use OBSERVED coat, not breed calculation. Merrie is 50% Cracker (breed=wool) but OBSERVED shedder.

### SOFT PREFERENCES (tiebreakers)

**19. PARASITE_RESISTANCE_BOOST** — Ram has proven FAMACHA 1-2 history → +1
**20. SHEDDING_BOOST** — Both parents are observed shedders → +1
**21. FLORIDA_ADAPTATION** — Both parents survived ≥2 FL summers → +1
**22. PROVEN_DAM** — Ewe has ≥2 successful lambings → +1
**23. PIPELINE_ALIGNMENT** — Pairing advances the pipeline goal (hair %, parasite resistance trending right direction) → +1
**24. MEATINESS** — Offspring expected to have good muscling (Suffolk, Dorper, or large-frame genetics) → +1

---

## SCORING

```
If ANY HARD BLOCK fires → REJECT
If TOTAL_RISK ≥ 14 → REJECT
If TOTAL_RISK 10-13 → CONDITIONAL (human override needed)
If TOTAL_RISK 6-9 → APPROVED WITH CAUTION
If TOTAL_RISK 0-5 → APPROVED

PREFERENCE_SCORE ranks multiple approved pairings.
```

## PIPELINE PLACEMENT

When asked "where does this animal go?":

1. Check FAMACHA/FEC history → determines earliest possible stage
2. Check observed coat → hair animals can enter later stages
3. Check breed composition → context for which ram pairs well
4. Check weight → size-match to ram at target stage
5. Check parentage → avoid father-daughter in same pen

**Advancement:** Animal meets ALL criteria for current stage → moves to next stage.
**Failure:** Animal fails criteria → cull, or drop back one stage for retesting (one retry only).
**Ram recycling:** Best ram lamb from Pen 2 (elite) → tested through summer → if passes FAMACHA, enters Pen 3 as sire.

---

## ANNUAL EVALUATION — EVERY ANIMAL JUSTIFIES ITS PLACE

No animal is permanent. Every ram and ewe must earn their spot each year based on measured performance. Evaluate at the end of each lambing season.

### Ram Annual Review

Score each ram on his OFFSPRING performance (not his own traits):

| Metric | Weight | Method | Cull Threshold |
|--------|--------|--------|----------------|
| Offspring avg FAMACHA | 40% | Average all lambs' FAMACHA scores at 6 months | Avg > 3.0 |
| Offspring shedding % | 25% | % of lambs scoring ≥3 on 1-5 shed scale at weaning | < 40% shedding |
| Offspring weight gain | 15% | Avg daily gain birth→weaning | Bottom 25% vs other rams |
| Conception rate | 10% | Ewes exposed vs ewes lambed | < 60% |
| Offspring survival | 10% | Lambs alive at 90 days / lambs born | < 70% |

**Actions:**
- **KEEP:** Meets or exceeds all thresholds. Stays at current stage or advances.
- **DEMOTE:** Fails 1 metric. Drops back one pipeline stage.
- **REPLACE:** Fails 2+ metrics. Replace with best available ram lamb.
- **CULL:** Fails FAMACHA threshold OR conception < 40%. Remove from flock.

A ram's sons that outperform him on these metrics SHOULD replace him. This is the pipeline working.

### Ewe Annual Review

Score each ewe on her OWN performance plus OFFSPRING:

| Metric | Weight | Method | Cull Threshold |
|--------|--------|--------|----------------|
| Own FAMACHA (annual avg) | 30% | Average of all scores taken during year | Avg > 2.5 |
| Deworming events | 20% | Number of times dewormed in past 12 months | > 2 treatments |
| Observed shedding | 15% | Coat score 1-5 at peak shedding season | Score < 2 at Stage 4+ |
| Lambing success | 15% | Lambed without assistance, lamb(s) alive at 30 days | Failed lambing |
| Offspring FAMACHA | 10% | Her lambs' avg FAMACHA at 6 months | Avg > 3.0 |
| Weight/condition | 10% | BCS at breeding time (target 2.5-4.0) | BCS < 2 or > 4.5 |

**Actions:**
- **ADVANCE:** Meets all thresholds for current stage + next stage criteria. Move forward.
- **HOLD:** Meets current stage thresholds but not next stage. Stay, retest next year.
- **DROP BACK:** Fails 1 metric at current stage. Move back one stage. One retry.
- **CULL:** Fails 2+ metrics, OR fails after dropping back, OR avg FAMACHA > 3.5 at any stage.

### Shedding Score (1-5 scale, scored at peak shedding season)

| Score | Description |
|-------|-------------|
| 1 | Full wool retention — no shedding |
| 2 | Partial shed — patches of wool remain (>50%) |
| 3 | Mostly shed — some wool on topline/belly (<50% remaining) |
| 4 | Nearly clean — small tufts only |
| 5 | Full shed — clean hair coat, no wool |

### Annual Calendar

| Month | Action |
|-------|--------|
| January | Pre-breeding FAMACHA check. BCS scoring. Vaccination boosters. |
| February-March | Lambing season. Record births, birthweights, dam behavior. |
| April | Post-lambing FAMACHA. Start lamb FAMACHA at 8 weeks. |
| June | Peak shedding — score all animals on 1-5 scale. |
| August | Weaning. Weigh lambs. Score lambs on FAMACHA/shedding/weight. |
| September | **ANNUAL REVIEW.** Score all rams and ewes. Advance/hold/drop/cull. |
| October | Move animals to new pipeline positions. Place replacement rams. |
| November-December | Breeding season. Ram exposure begins. |

---

## SOURCES

- UF/IFAS Extension VM264: Selection of Sheep Meat Breeds in Florida
- Dwyer & Bünger: Dystocia review
- Ngere et al. 2018: Katahdin FEC heritability (h² 0.2-0.4)
- Burke et al. 2023: Low-FEC EBV sire effects
- Forbes et al. 2024: GI parasite resistance in hair sheep breeding objectives
- OSU Sheep Team: FAMACHA guidance
- Manatee Creek flock data April 2026
- Multi-LLM investigate pipeline (Grok, GPT, Perplexity, You.com — April 2026)
- Owner hard lessons: St Croix, BBB, Windlestone Dorper parasite failures on-site
