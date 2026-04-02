# Breeding Advisor — Required Data Points

Every field listed below must exist in `data/flock_database.json` for the breeding advisor to fully evaluate a pairing. If a field is missing, the advisor flags it as a DATA GAP and cannot complete that check.

## Per-Animal Required Fields (both ram and ewe)

### Identity (checks 1, 2)
| Field | Type | Example | Required By |
|---|---|---|---|
| `id` | string | `"rocky"` | All checks — unique identifier |
| `name` | string | `"Rocky"` | Display/reporting |
| `sex` | string | `"ram"` or `"ewe"` | Check 1, 2 — status validation |
| `tag` | string/null | `"140"` | Display/reporting |
| `status` | string | `"alive"` | Check 1, 2 — HARD_BLOCK if not alive |
| `pen` | string | `"Pen 2"` | Management/pen assignment |

### Breed & Genetics (checks 6, 15, 22, 23, 24, 25, 26)
| Field | Type | Example | Required By |
|---|---|---|---|
| `breed_composition.percentages` | object | `{"Katahdin": 50, "BHD": 25}` | Check 22 (hair vs wool), 23-26 (preferences) |
| `breed_composition.coat_type` | string | `"hair"` / `"wool"` / `"mixed"` | Check 22 |
| `breed_composition.hair_percentage` | number | `75` | Check 22 — offspring hair% calculation |
| `sire_id` | string/null | `"sir-loin"` | Check 6 — inbreeding, Check 15 — dam line |
| `dam_id` | string/null | `"half-tail"` | Check 6 — inbreeding, Check 15 — dam line |

### Age & DOB (checks 7, 13, 19)
| Field | Type | Example | Required By |
|---|---|---|---|
| `dob` | string (ISO date) | `"2023-01-14"` | Check 7 (age block), 13 (first-timer age), 19 (seasonal calc) |
| `dob_approximate` | boolean | `true` | Flag uncertainty in age-dependent checks |

### Weight & Condition (checks 11, 12, 18)
| Field | Type | Example | Required By |
|---|---|---|---|
| `weight_lbs` | number | `275` | Check 12 — size mismatch ratio |
| `body_condition_score` | number (1-5) | `3.5` | Check 18 — BCS risk |

### Health — FAMACHA (checks 4, 5, 14, 15)
| Field | Type | Example | Required By |
|---|---|---|---|
| `health.famacha_history` | array of objects | see below | Checks 4, 5, 14, 15 |
| `health.famacha_history[].date` | string (ISO) | `"2026-04-01"` | Recency check (must have within 90 days) |
| `health.famacha_history[].score` | number (1-5) | `2` | Threshold evaluation |
| `health.famacha_history[].notes` | string | `"eyes good"` | Context |

**Minimum required:** At least 1 FAMACHA score within past 90 days. Ideally 3+ scores over past 6 months for trend analysis.

### Health — Vaccinations (check 8)
| Field | Type | Example | Required By |
|---|---|---|---|
| `health.vaccinations` | array of objects | see below | Check 8 — HARD_BLOCK |
| `health.vaccinations[].date` | string (ISO) | `"2026-03-09"` | Must be within past 12 months |
| `health.vaccinations[].vaccine` | string | `"Covexin 8"` | Must include CDT or Covexin |

### Health — Treatments & Disease (check 9)
| Field | Type | Example | Required By |
|---|---|---|---|
| `health.treatments` | array of objects | see below | Check 9 — active disease |
| `health.treatments[].date` | string (ISO) | `"2026-02-20"` | Recency |
| `health.treatments[].treatment` | string | `"Ivermectin + Fenbendazole"` | Disease identification |
| `health.treatments[].notes` | string | `"FAMACHA 5 emergency"` | Context |

### Reproductive History — Ewe (checks 3, 10, 13, 16, 27)
| Field | Type | Example | Required By |
|---|---|---|---|
| `breeding.lambing_history` | array of objects | see below | Checks 10, 13, 16, 27 |
| `breeding.lambing_history[].date` | string (ISO) | `"2026-01-06"` | Check 10 — recovery interval |
| `breeding.lambing_history[].litter_size` | number | `3` | Check 16 — HIGH_OUTPUT detection |
| `breeding.lambing_history[].lamb_birth_weights` | array of numbers | `[8, 7, 6]` | Check 11 — birthweight prediction |
| `breeding.lambing_history[].complications` | string/null | `"dystocia"` | Check 7 — age+difficulty block |
| `breeding.lambing_history[].sire_id` | string | `"eclipse"` | Offspring tracking |
| `breeding.offspring_ids` | array of strings | `["elsie-triplet-1"]` | Pedigree tracing |
| `breeding.last_lambing_date` | string (ISO) | `"2026-01-06"` | Check 10 — quick lookup |
| `breeding.total_lambings` | number | `4` | Check 13 — first-timer detection |
| `breeding.category` | string | `"HIGH_OUTPUT"` | Check 16 — line risk |

### Reproductive History — Ram (checks 3, 17, 20)
| Field | Type | Example | Required By |
|---|---|---|---|
| `breeding.ewes_exposed` | number | `6` | Check 3 — fertility test |
| `breeding.ewes_conceived` | number | `1` | Check 3 — fertility test |
| `breeding.exposure_months` | number | `14` | Check 3 — fertility test |
| `breeding.current_season_count` | number | `4` | Check 20 — breeding load |
| `breeding.role` | string | `"SAFETY"` / `"BALANCED"` / `"TERMINAL"` / `"EXPERIMENTAL"` | Assignment logic |
| `temperament` | string | `"aggressive_to_rams"` / `"aggressive_to_ewes"` / `"docile"` | Check 17 |

### Maternal Line (checks 15, 16)
| Field | Type | Example | Required By |
|---|---|---|---|
| `maternal_line_id` | string | `"gigi_azure_line"` | Check 15, 16 — dam line risk |
| `maternal_line_type` | string | `"HIGH_OUTPUT"` / `"BALANCED"` / `"HARDY"` | Check 16 |

### NSIP Data (check 28)
| Field | Type | Example | Required By |
|---|---|---|---|
| `nsip.enrolled` | boolean | `true` | Check 28 — preference |
| `nsip.lpn_id` | string | `"6403012022222223"` | Registry lookup |
| `nsip.wfec_ebv` | number | `-34.5` | Parasite resistance EPD |
| `nsip.pfec_ebv` | number | `-46.44` | Parasite resistance EPD |
| `nsip.hair_index` | number | `100.52` | Composite index |

### Economic (check 29)
| Field | Type | Example | Required By |
|---|---|---|---|
| `cost.purchase_price` | number | `200` | Check 29 — ROI |
| `cost.annual_maintenance` | number | `150` | Check 29 — ROI |
| `cost.offspring_market_value` | number | `300` | Check 29 — ROI |

### Management Notes (check 30)
| Field | Type | Example | Required By |
|---|---|---|---|
| `notes` | string | free text | Context for all checks |
| `confidence` | string | `"high"` / `"medium"` / `"low"` | Data quality flag |
| `source_refs` | object | `{"notebook_card": "Card 1 pen 1"}` | Verification trail |

---

## Derived Data (calculated, not stored)

These are computed during evaluation, not stored per-animal:

| Derived Field | Calculation | Used By |
|---|---|---|
| `age_months` | `(today - dob) / 30.44` | Checks 7, 13 |
| `days_since_last_lambing` | `today - last_lambing_date` | Check 10 |
| `avg_famacha_6mo` | average of scores in past 180 days | Check 14 |
| `inbreeding_coefficient_F` | Wright's F from pedigree | Checks 6, 21 |
| `predicted_birth_weight` | formula in check 11 | Check 11 |
| `ram_to_ewe_weight_ratio` | `ram_weight / ewe_weight` | Check 12 |
| `offspring_hair_percentage` | `(ram_hair% + ewe_hair%) / 2` | Check 22 |
| `offspring_breed_percentages` | `(ram_breed% + ewe_breed%) / 2` per breed | Checks 23-26 |

---

## Current Data Gaps in Flock Database (April 2026)

Animals from notebook cards are missing many of these fields. Priority gaps:

### CRITICAL (blocks evaluation)
- `weight_lbs` — missing for most animals. Need weights.
- `body_condition_score` — not recorded for any animal. Need BCS.
- `breed_composition.percentages` — missing for: Charlies Ewe, Hair Ewe 0033, Wool Ewe 0044, most Pen 1 animals, Charlies Farm Ewe, Small White Ewe, many others marked `[UNCLEAR]`
- `breeding.lambing_history` — structured lambing records missing for most ewes. Have notes but not structured data.
- `sire_id` / `dam_id` — unknown for many Charlie's farm animals, Tree Fort animals

### HIGH (limits accuracy)
- `breeding.ewes_exposed` / `ewes_conceived` — not tracked per ram. Only known anecdotally (Eclipse 1/6).
- `breeding.lamb_birth_weights` — not recorded on most cards. Only know 00110 threw "12-15 lbs."
- `temperament` — noted for Rocky ("Jerkface") and Charlie ("sexually aggressive") but not standardized.

### MEDIUM (nice to have)
- `nsip` data — only Kelsier (deceased) had NSIP enrollment
- `cost` data — partial in old spreadsheet Costs tab
- `maternal_line_id` — needs to be assigned based on pedigree analysis

### Actions to Fill Gaps
1. **Weigh all adults** at next handling — heart girth + body length → estimated weight
2. **BCS all adults** at next handling — 1-5 scale, trained eye
3. **Record birth weights** for all future lambs (bathroom scale works)
4. **Assign breed %** to unknowns based on parentage or visual assessment
5. **Structure lambing history** from notebook cards into database format
