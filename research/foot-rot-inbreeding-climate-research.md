# SHEEP BREEDING PREDICTION TOOL -- RESEARCH DATA

## TOPIC 1: FOOT ROT RESISTANCE IN SHEEP BY BREED

### 1.1 Breed-Level Foot Rot Resistance Scores

Numerical resistance scores on a 1-10 scale (10 = most resistant, 1 = most susceptible) synthesized from comparative studies, GWAS data, and breed descriptions.

| Breed | Foot Rot Resistance Score | Climate Origin | Evidence Source |
|---|---|---|---|
| Gulf Coast Native | 9 | Humid subtropical (FL/Gulf) | UF/IFAS VM264; USDA foot rot challenge study |
| Florida Cracker | 9 | Humid subtropical (FL) | UF/IFAS VM264; Hidalgo et al. 2023 |
| St. Croix | 8 | Humid tropical (Caribbean) | USDA breed comparison (Parker et al. 2006) |
| Barbados Blackbelly | 8 | Humid tropical (Caribbean) | GWAS (Frontiers in Genetics 2023); UF/IFAS |
| American Blackbelly | 7 | Composite (US selected) | UF/IFAS VM264 |
| St. Augustine | 7 | Composite (FL selected) | UF/IFAS VM264 |
| Katahdin | 7 | Composite (Maine/W. African) | Lincoln Univ. DQA2 marker study; GWAS 2023 |
| Wiltshire Horn | 7 | Temperate (England, self-shedding) | Breed descriptions: "very resistant to foot rot" |
| Babydoll Southdown | 7 | Temperate (England, ancient) | Breed registry: "resistant to foot rot" |
| Karakul | 6 | Arid (Central Asia) | "Resistant to foot rot" BUT "susceptible on wet marshy ground" |
| Jacob | 6 | Primitive/hardy | "High resistance to parasites and hoof problems" |
| Tunis | 5 | Arid/Mediterranean (Tunisia) | No specific foot rot data; intermediate assumed from heritage |
| Suffolk | 5 | Temperate (England) | "Feet very resistant to foot rot" |
| Hampshire | 5 | Temperate (England) | British breed advantage (moderate); dark hooves |
| Dorper | 4 | Arid (South Africa) | Parker et al. 2006: Dorper crosses had highest foot rot scores |
| Awassi | 4 | Arid (Near East) | Fat-tailed, dry-adapted; no published foot rot resistance in humid |
| Cotswold | 3 | Temperate (England) | Long wool, no specific resistance data; heavy fleece = risk |
| East Friesian | 3 | Humid temperate (N. Germany) | No resistance data; dairy breed, high maintenance |

**Important caveat:** Karakul scores 6 in general, but in a Florida/wet environment, effective resistance drops to approximately 3-4 because the breed is specifically noted as susceptible "if restricted to wet marshy ground."

### 1.2 Heritability of Foot Rot Resistance (h-squared)

| Measure | h-squared Estimate | Source |
|---|---|---|
| General range (all breeds) | 0.10 - 0.30 | Nieuwhof et al. 2008; Raadsma & Conington 2011 |
| Single observation, pre-vaccination | 0.07 - 0.22 | NZ Merino CPT |
| Repeat measurements | ~0.30 | NZ Merino CPT |
| Average footrot score (NZ Merino) | 0.20 +/- 0.05 | NZ Merino Central Progeny Test |
| Scottish Blackface ewes (threshold model) | 0.19 (severe: 0.26) | Conington et al. |
| Mule ewes (threshold model) | 0.12 (severe: 0.19) | Conington et al. |
| **Best estimate for prediction tool** | **0.22** | Weighted mean across studies |

### 1.3 Genetic Basis of Foot Rot Resistance

**Key genes identified (GWAS, Frontiers in Genetics 2023, N=251 sheep):**
- **GBP6** (guanylate-binding protein 6) -- immune response / interferon-gamma pathway
- **TCHH** (trichohyalin) -- hoof growth and structural integrity
- **SLC38A1** (glutamine transporter) -- nutrient availability for immune function
- 3 genome-wide significant SNPs + 33 suggestive SNPs across 13 autosomes
- **MHC-DQA2** gene: allele *1101 = increased susceptibility; allele *1201 = decreased susceptibility

**Hoof color and hardness:**
- Popular belief: black hooves are harder and more resistant
- Hoof pigmentation heritability: h-squared = 0.51
- Genetically correlated with nose pigmentation (rG = 0.73)
- Mechanical testing (Scobie et al.): NO significant differences in stiffness or tensile strength between black, grey, and white hooves
- The association may be due to linked genes rather than pigmentation itself

**Nature of the trait:**
- Polygenic -- no major single gene responsible
- Subgroup-specific resistance (animal can resist one D. nodosus serogroup but not another)
- No strong genetic correlations with production traits (selecting for resistance does not harm production)

### 1.4 Environmental Factors for Florida

**Manatee County, FL climate:**
- Average annual rainfall: 55-56 inches
- Average relative humidity: 74% (range 72-76%)
- Summer highs: 88-91 degrees F
- Summer lows: 75-80 degrees F
- Rainy season: May through October
- Koppen classification: Cfa (humid subtropical)

**Environmental risk multipliers for foot rot:**
- Wet + warm conditions increase foot rot risk exponentially
- D. nodosus survives up to 7-14 days in moist soil
- Key risk factors: continuous moisture on hooves, muddy pens, soft soil, no rocky ground exposure
- Suggested environmental risk multiplier for FL: **1.5x to 2.0x** the baseline foot rot risk compared to temperate/dry climates

### 1.5 Breed Ranking Studies

**Parker et al. (2006) -- USDA foot rot challenge study** (Small Ruminant Research):
Breeds tested: Dorset, 1/2 Dorper, 3/4+ Dorper, Gulf Coast Native, Katahdin, St. Croix
- Least squares means for infected areas: Dorper crosses > all other breeds
- Percentage with foot rot odor: Dorper crosses > Dorset, Katahdin, St. Croix
- Gulf Coast Native and St. Croix showed best treatment response

---

## TOPIC 2: INBREEDING DEPRESSION IN SHEEP

### 2.1 Quantitative Effects Per 1% Increase in Inbreeding Coefficient (F)

| Trait | Change per 1% increase in F | Unit | Key Source |
|---|---|---|---|
| **Birth weight** | -6 to -25 g (median: -13.6 g) | grams | Ripollesa (Casellas 2008): -13.6 g; Sakiz: -24.5 g; Dormer: -6 g |
| **Weaning weight** | -12 to -93 g (median: -30 g) | grams | Baluchi: -21.7 g; Dormer: -93 g; Guilan males: -30 g |
| **Lamb survival** | -0.80% of total decline attributed to survival | relative | 80% of decline in litter weight weaned is due to survival effects |
| **Fertility/conception rate** | -0.46% per 1% F (absolute decline) | percentage points | Wiener et al. 1992: 0.71 to 0.44 over F=0 to F=0.59 |
| **Litter size** | -0.029 to -0.05 lambs | lambs/litter | Romanov: -0.05; Guilan: -0.029 at weaning |
| **Mature body weight** | -0.13 to -0.22% of trait mean | percent | Doekes meta-analysis 2021 |
| **Fleece weight** | -0.33% of trait SD per 1% F | percent SD | German breeds meta (2023); Rambouillet: -0.35 kg at 25% F |
| **Growth rate (ADG)** | -0.50% of trait SD per 1% F | percent SD | Doekes meta 2021; Baluchi: -1.81 g/day |
| **Parasite resistance (FEC)** | Significantly worse (no precise coefficient) | -- | Soay sheep: 10% increase in F = 60% reduction in survival odds, mediated by parasites |

### 2.2 Meta-Analysis Summary (Doekes et al. 2021, 154 studies)

Per 1% increase in pedigree-based F:
- Median decline: **0.13% of trait mean** (mean: 0.22%)
- Median decline: **0.59% of trait standard deviation** (mean: 0.71%)

**Sheep-specific estimates:**
- Overall sheep median: **-0.52% of trait SD** per 1% increase in F
- Weight/growth traits: **-0.73% of trait SD** per 1% F
- Reproduction traits: **-0.38% of trait SD** per 1% F

### 2.3 Ercanbrack & Knight (1991) -- Large-Scale U.S. Study

Data: 13,807 ewe records + 16,470 lamb records from Rambouillet, Targhee, Columbia sheep. Average inbreeding ~20-25%.

**Breakdown of causes of decline in litter weight weaned:**
- 80% due to lamb survival reduction
- 11% due to fertility decline
- 6% due to prolificacy decline
- 3% due to weaning weight decline

### 2.4 Conception Rate and Prolificacy Data (Wiener et al. 1992)

| F level | Conception rate (1st service) | Conception rate (3 services) | Prolificacy |
|---|---|---|---|
| 0.00 | 0.71 | 0.91 | 1.73 |
| 0.25 | ~0.56 | ~0.83 | 1.37 |
| 0.38 | ~0.48 | ~0.78 | ~1.30 |
| 0.59 | 0.44 | 0.74 | 1.24 |
| Line crosses (outbred) | 0.78 | 0.97 | -- |

### 2.5 Inbreeding Thresholds

| F Level | Description | Risk Level |
|---|---|---|
| 0% | No inbreeding | Baseline |
| < 3% | Distant shared ancestors | Low risk, generally safe |
| 3-6% | Common in well-managed flocks | Acceptable, monitor |
| **7%** | **Industry management threshold** | **Problems begin to emerge** |
| 10% | Documented detrimental effects | Significant risk |
| 12.5% | Half-sibling or grandparent mating | High risk -- visible depression |
| 25% | Full sibling or parent-offspring mating | Dangerous -- severe depression |
| > 25% | Multiple generations of close mating | Critical -- survival at risk |

**Average F in well-managed purebred sheep flocks:** 2-6%

### 2.6 Wright's Inbreeding Coefficient Formula

```
F_x = SUM over all common ancestors A of:
    (1/2)^(n1 + n2 + 1) * (1 + F_A)

Where:
  F_x  = inbreeding coefficient of individual X
  n1   = number of generations from parent 1 to common ancestor A
  n2   = number of generations from parent 2 to common ancestor A
  F_A  = inbreeding coefficient of common ancestor A (0 if not inbred)
```

**Quick reference F values (no prior inbreeding):**

| Mating | F |
|---|---|
| Parent x offspring | 0.250 |
| Full siblings | 0.250 |
| Half siblings | 0.125 |
| Grandparent x grandchild | 0.125 |
| First cousins | 0.0625 |
| Half first cousins | 0.03125 |

### 2.7 Formulas for Prediction Tool

```python
# Inbreeding depression for a continuous trait
Predicted_value = Base_value * (1 - bm * F * 100)
# Where bm = fractional decline per 1% F, F = inbreeding coefficient (0-1)

# Survival (multiplicative, Soay sheep data)
Odds_survival = Odds_base * exp(-6.0 * delta_F)
```

---

## TOPIC 3: CLIMATE ADAPTATION -- WET HEAT vs DRY HEAT

### 3.1 Breed Climate Adaptation Classification

| Breed | Adaptation Type | Heat Score (1-10) | Humidity Score (1-10) | Overall FL Score |
|---|---|---|---|---|
| Gulf Coast Native | WET heat (native FL/Gulf) | 9 | 10 | 9.5 |
| Florida Cracker | WET heat (native FL) | 9 | 10 | 9.5 |
| St. Croix | WET heat (Caribbean tropical) | 9 | 9 | 9.0 |
| Barbados Blackbelly | WET heat (Caribbean tropical) | 8 | 9 | 8.5 |
| American Blackbelly | WET heat (US composite) | 8 | 8 | 8.0 |
| St. Augustine | WET heat (FL composite) | 8 | 9 | 8.5 |
| Katahdin | WET heat (composite, W. African) | 8 | 8 | 8.0 |
| Tunis | DRY heat (Mediterranean/N. Africa) | 8 | 5 | 6.5 |
| Dorper | DRY heat (South Africa arid) | 7 | 5 | 6.0 |
| Wiltshire Horn | Temperate + self-shedding | 7 | 6 | 6.5 |
| Karakul | DRY heat (Central Asian desert) | 8 | 3 | 5.5 |
| Awassi | DRY heat (Syro-Arabian desert) | 9 | 3 | 6.0 |
| Jacob | Temperate (hardy primitive) | 5 | 5 | 5.0 |
| Babydoll Southdown | Temperate (England) | 4 | 5 | 4.5 |
| Hampshire | Temperate (England) | 3 | 4 | 3.5 |
| Suffolk | Temperate (England) | 3 | 4 | 3.5 |
| Cotswold | Temperate (England, long wool) | 2 | 3 | 2.5 |
| East Friesian | Temperate humid (N. Europe dairy) | 2 | 4 | 3.0 |

### 3.2 Physiological Mechanisms of Heat Tolerance

| Mechanism | DRY Heat | WET Heat | Key Breeds |
|---|---|---|---|
| Respiratory evaporation (panting) | High | Moderate (reduced by humidity) | All breeds |
| Cutaneous sweating | Very high | LOW (humidity blocks evaporation) | Hair sheep > wool |
| Coat insulation reduction | High | CRITICAL | Hair sheep, Wiltshire Horn |
| Peripheral vasodilation | Moderate | Moderate | All breeds |
| Fat tail energy storage | High (drought) | LOW (insulates, traps heat) | Awassi, Karakul |
| Body size (small = better) | Moderate | High (SA:volume ratio) | Small hair sheep |

**Specific data from Tadesse et al. (2019) -- Dorper vs. Katahdin vs. St. Croix under high heat load:**

| Measure | Dorper | Katahdin | St. Croix |
|---|---|---|---|
| Rectal temp at HLI 95 (1 PM) | 39.18 C | 39.12 C | 38.83 C |
| Resp. rate at HLI 95 (1 PM) | 149.2 bpm | 143.6 bpm | 137.3 bpm |

**Heat resilience ranking: St. Croix > Katahdin > Dorper**

### 3.3 Why Wet Heat Is Harder Than Dry Heat

1. **Evaporative cooling drops** as humidity rises -- at 74-80% RH moisture gradient is minimal
2. **Fat-tailed breeds disadvantaged** -- insulation traps body heat with no drought benefit
3. **Wool retention more damaging** -- traps moisture creating perpetually humid microclimate
4. **Parasite burden compounds heat stress** -- H. contortus thrives in warm, moist conditions

### 3.4 Crossbreeding Dry-Heat x Wet-Heat Breeds

**Predicted crossbreed outcomes:**

| Cross | Heat | Humidity | Parasite Resistance | Overall FL |
|---|---|---|---|---|
| Katahdin x Gulf Coast Native | High | High | High | Excellent (8-9) |
| St. Croix x Katahdin | High | High | High | Excellent (8-9) |
| Katahdin x Dorper | Moderate-High | Moderate | Moderate | Moderate (6-7) |
| Katahdin x Awassi | Moderate-High | Moderate | Moderate | Moderate (5-6) |
| Katahdin x Karakul | Moderate | Moderate | Moderate | Moderate (5-6) |
| Dorper x Awassi | High | Low-Moderate | Low-Moderate | Poor-Moderate (4-5) |

**Formula for crossbreed climate adaptation:**
```python
F1_adaptation = (sire_score + dam_score) / 2 * heterosis_multiplier
# heterosis_multiplier = 1.05-1.10 for same climate type crosses
# heterosis_multiplier = 0.95-1.00 for different climate type crosses
```

### 3.5 UF/IFAS Recommendations for Florida

Six breeds recommended for Florida meat production (VM264, Bennett & Diehl, July 2024):
1. **American Blackbelly / Barbados Blackbelly**
2. **Dorper**
3. **Florida Cracker/Florida Native**
4. **Katahdin**
5. **St. Augustine**
6. **St. Croix**

UF/IFAS Sheep Unit maintains only **Katahdin** and **Florida Native** (plus crossbreds).

**Critical criterion:** "Natural parasite resistance is the most important selection aspect" for Florida.

### 3.6 Florida Cracker Sheep Genetic Parameters (Hidalgo et al. 2023)

| Trait | h-squared | SE |
|---|---|---|
| Fecal Egg Count (FEC) | 0.33 | 0.09 |
| FAMACHA score (FAM) | 0.31 | 0.10 |
| Packed Cell Volume (PCV) | 0.22 | 0.09 |
| Body Condition Score (BCS) | 0.19 | 0.07 |

---

## SUMMARY: KEY NUMBERS FOR THE PREDICTION TOOL

### Foot Rot Resistance
- Default heritability: **h-squared = 0.22**
- Environmental multiplier for FL: **1.5-2.0x baseline risk**
- Score each breed 1-10 per table in Section 1.1
- Adjust dry-heat breeds downward by 2-3 points for Florida wetness

### Inbreeding Depression
- **Birth weight:** -13.6 g per 1% F
- **Weaning weight:** -30 g per 1% F
- **Fertility:** -0.46 percentage points per 1% F
- **Litter size:** -0.04 lambs per 1% F
- **Growth rate:** -0.50% of SD per 1% F
- **Survival:** multiply odds by exp(-6.0 * delta_F)
- **Overall production:** -0.13% of trait mean per 1% F
- **Warning threshold:** F >= 0.07 (7%)
- **Danger threshold:** F >= 0.125 (12.5%)

### Climate Adaptation
- Score breeds using Heat + Humidity matrix in Section 3.1
- Crossbreed: average parental scores, multiply by 1.05-1.10 (same type) or 0.95-1.00 (different types)
- Best for Manatee County FL: Gulf Coast Native, Florida Cracker, St. Croix, BBB, Katahdin, St. Augustine
- Worst for Manatee County FL: Cotswold, East Friesian, Hampshire, Suffolk

---

## SOURCES

**Foot Rot Resistance:**
- [GWAS footrot hair and wool sheep -- Frontiers in Genetics 2023](https://www.frontiersin.org/journals/genetics/articles/10.3389/fgene.2023.1297444/full)
- [Footrot resistant Katahdin -- Lincoln University / NIFA](https://portal.nifa.usda.gov/web/crisprojectpages/0225329)
- [Effect of breed on foot rot treatment -- Parker et al. 2006](https://www.sciencedirect.com/science/article/abs/pii/S0921448806001581)
- [Comparative susceptibility five breeds -- Emery et al. 1984](https://pubmed.ncbi.nlm.nih.gov/6743147/)
- [VM264 UF/IFAS 2024](https://edis.ifas.ufl.edu/publication/VM264)
- [GWAS footrot Texel -- Genetics Selection Evolution 2015](https://gsejournal.biomedcentral.com/articles/10.1186/s12711-015-0119-3)
- [MHC-DQA2 footrot susceptibility](https://www.sciencedirect.com/science/article/pii/S0034528821003143)
- [Hoof material properties -- Scobie et al.](https://www.researchgate.net/publication/325357894)

**Inbreeding Depression:**
- [Meta-analysis 30 years -- Doekes et al. 2021](https://pmc.ncbi.nlm.nih.gov/articles/PMC8234567/)
- [Inbreeding depression livestock -- Leroy 2014](https://onlinelibrary.wiley.com/doi/10.1111/age.12178)
- [Founder inbreeding depression birth weight -- Casellas 2008](https://academic.oup.com/jas/article-abstract/87/1/72/4731061)
- [Inbreeding reproduction wool -- Ercanbrack & Knight 1991](https://pubmed.ncbi.nlm.nih.gov/1808170/)
- [Rapid inbreeding effects -- Wiener et al. 1992](https://www.cambridge.org/core/journals/animal-science/article/abs/)
- [Inbreeding depression German sheep 2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10668769/)
- [Soay sheep inbreeding dynamics 2021](https://www.nature.com/articles/s41467-021-23222-9)

**Climate Adaptation:**
- [Heat load Dorper Katahdin St. Croix -- Tadesse et al. 2019](https://www.tandfonline.com/doi/full/10.1080/09712119.2019.1674658)
- [Hair sheep Americas -- Frontiers 2023](https://www.frontiersin.org/journals/animal-science/articles/10.3389/fanim.2023.1195680/full)
- [Florida Cracker genetic parameters -- Hidalgo et al. 2023](https://www.frontiersin.org/journals/animal-science/articles/10.3389/fanim.2023.1249470/full)
- [Breeds for challenging environments -- PMC 2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10575318/)
- [Climate-mediated selective pressures sheep -- PMC 2014](https://pmc.ncbi.nlm.nih.gov/articles/PMC4245822/)
- [FAO breeding plans tropics](https://www.fao.org/4/x6536e/X6536E06.htm)
