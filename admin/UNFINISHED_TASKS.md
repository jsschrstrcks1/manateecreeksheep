# Unfinished Tasks — manateecreeksheep

> **Task custody (HLS):** Work queues live in `.household-library/catalog.jsonl` — not in this file.
> Find/checkout: `node admin/library.mjs preflight --query "<task>" --patron <id> --merge`
> **This document** is context/spec only unless stated otherwise.

**Generated:** 2026-07-11T22:27:48.253Z
**SSOT:** `.household-library/catalog.jsonl`

Open tasks for this repo (`state` ≠ `complete`). Regenerate:

```bash
node admin/library.mjs mirrors --repo manateecreeksheep
```

| priority | state | holder | task_id | title |
|----------|-------|--------|---------|-------|
| 0 | available | — | p0-1-duplicate-sheep-ids-regression | P0.1 Duplicate sheep IDs (REGRESSION) |
| 0 | available | — | p0-2-today-s-dam-correction-is-half-applied-regression-from-this | P0.2 Today's dam correction is half-applied (REGRESSION — from this session) |
| 0 | available | — | p0-3-broken-dam-reference | P0.3 Broken dam reference |
| 0 | available | — | p0-4-invalid-status-enum | P0.4 Invalid status enum |
| 0 | available | — | p0-5-gg-ewe-listed-as-sire-on-3-lambs-warning-but-pedigree-fatal | P0.5 GG (ewe) listed as sire on 3 lambs (WARNING but pedigree-fatal) |
| 0 | available | — | p0-6-tag-collision-among-living-sheep | P0.6 Tag collision among living sheep |
| 0 | available | — | pedigree-integrity-errors-block-level | Pedigree-integrity errors (block-level) |
| 1 | registered | — | memory-eclipse-idalia-scrub | Scrub Eclipse Idalia death refs — sold at auction 2026-04-26 not hurricane casualty |
| 1 | registered | — | memory-norison-eclipse-canonical-flock-ssot | Flock SSOT: NoriSon = Eclipse (same animal), sold 2026-04-26 |
| 1 | available | — | p1-1-20-records-missing-required-confidence-field | P1.1 20 records missing required `confidence` field |
| 1 | available | — | p1-2-windlestone-breed-percentages-sum-to-95 | P1.2 Windlestone breed percentages sum to 95% |
| 1 | available | — | p1-3-image-reference-broken | P1.3 Image reference broken |
| 1 | available | — | validator-errors-that-block-clean-integrity-pass | Validator ERRORs that block clean integrity pass |
| 2 | available | — | master-plan-loose-ends-status-vs-manatee-creek-redesign-plan-md | Master plan loose ends (status vs MANATEE_CREEK_REDESIGN_PLAN.md) |
| 3 | available | — | p3-1-six-alive-sheep-have-no-pen | P3.1 Six alive sheep have no pen |
| 3 | available | — | p3-2-two-sold-sheep-still-tagged-with-a-pen | P3.2 Two sold sheep still tagged with a pen |
| 3 | available | — | pen-assignment-hygiene | Pen-assignment hygiene |
| 4 | available | — | data-source-freshness | Data-source freshness |
| 4 | registered | — | mc-00113-shearing-and-famacha | Shear 00113 + take formal FAMACHA baseline; log parasite-resistance data |
| 4 | registered | — | mc-baby-azure-heat-signal-review | Fold Baby Azure heat-death into Azure × Kelsier breeding notes; heat tolerance is a lambing selection criterion |
| 4 | registered | — | mc-buck-breed-comp-verify-2026-05-14 | Verify Buck breeding-page composition source against flock_database.json and REPO-AGENT-APPENDIX (disputed comp — session 2026-05-14) |
| 4 | registered | — | mc-buck-original-death-date-2026-05-14 | Resolve Buck original ram identity merge and death-date uncertainty (session 2026-05-14) |
| 4 | registered | — | mc-kaladin-current-pen-2026-04-26 | Locate Kaladin's current pen (alive; pen null after bulk-cleanup correction) |
| 4 | available | — | p4-1-low-confidence-records-that-never-received-owner-verificati | P4.1 Low-confidence records that never received owner verification |
| 4 | available | — | p4-2-twelve-unclear-markers-still-in-db | P4.2 Twelve `[UNCLEAR]` markers still in DB |
| 4 | available | — | p4-3-lambing-record-sire-holes | P4.3 Lambing-record sire holes |
| 5 | registered | — | mc-00113-foster-dam-plan-for-rebreed | If 00113 is re-bred, arrange a foster dam in advance; parasite-resistance donor but proven bad mother |
| 5 | registered | — | mc-angus-tag-and-famacha-baseline | Tag Angus + take FAMACHA baseline at next handling |
| 5 | registered | — | mc-bambii-2027-breeding-partner | Bambii (Tree Fort, orange #35) 2027 breeding partner planning |
| 5 | available | — | open-follow-up-orange-tag-31-ewe-location-2026-05-14 | Open follow-up — Orange Tag 31 Ewe location (2026-05-14) |
| 5 | available | — | p5-1-no-handoff-md | P5.1 No HANDOFF.md |
| 5 | available | — | p5-2-no-unfinished-tasks-md-baseline-before-this-audit | P5.2 No `unfinished_tasks.md` baseline before this audit |
| 5 | available | — | p5-3-no-notebook-card-workflow-md-l12 | P5.3 No NOTEBOOK_CARD_WORKFLOW.md (L12) |
| 5 | available | — | pen-data-drift-surfaced-and-fixed-2026-05-14 | Pen-data drift surfaced and fixed 2026-05-14 |
| 5 | available | — | planned-pen-moves-2026-05-14-not-yet-executed | Planned Pen Moves — 2026-05-14 (not yet executed) |
| 5 | available | — | process-docs-gaps | Process / docs gaps |
| 5 | available | — | recommended-next-sweep-one-commit-each | Recommended next sweep (one commit each) |
| 5 | available | — | sweep-progress-2026-05-13-session-2 | Sweep Progress — 2026-05-13 session 2 |

<!-- library register 2026-07-16T00:09:47.255Z -->
| mcs-validator-percentage-value-nan | 1 | Cross-review 2026-07-16: manateecreeksheep validator NaN hole one field over — sibling fixed unknown_percentage NaN but a NaN in a percentages VALUE still silently disabled the breed-sum guard (abs(NaN-100)>2 is False; json.load accepts NaN). FIXED: guard the total via math.isfinite. Regression pins added. |

<!-- library register 2026-08-12T02:10:35.610Z -->
| mcs-drug-withdrawal-tracking | 1 | MCS-7 (from LambTracker, GPL-2, concept only): per-drug meat/milk WITHDRAWAL tracking with 'not safe until <date>' alerts. When an animal is treated, record the drug's withdrawal interval and flag the animal as not-safe-to-slaughter / milk-not-saleable until the window clears, so a treated animal can't be sold to slaughter or its milk marketed by mistake. Food-safety essential for a meat/parasite flock. Store withdrawal period per drug in the drug table; compute per-animal clear-date on treatment; surface it on the animal record and in any 'ready to sell/cull' view. |

<!-- library register 2026-08-12T02:10:36.435Z -->
| mcs-famacha-fec-combined-decision | 1 | MCS-8 (from FuzzyLogic-VERMIFUGA, concept only): deworming decision reads FAMACHA + FEC TOGETHER, and treats disagreement as a diagnostic signal. Rules: anemic (bad FAMACHA) + LOW egg count -> anemia may NOT be parasites, investigate before dosing; good colour + HIGH egg count -> animal copes but is shedding heavily onto pasture (refugia/contamination consideration). Do not deworm on FAMACHA alone. Sharpens the recheck/treat nudge (see MCS-1): surface the mismatch cases rather than blindly dosing on one number. Grounded in standard integrated parasite management. |

<!-- library register 2026-08-12T02:12:24.521Z -->
| mcs-eid-visual-dual-identity | 2 | EID + visual dual identity — store both electronic (RFID) and visual tags per animal; either is a valid lookup key so a lost/unreadable tag never orphans an animal's history (concept from OogieM/LambTrackerMobile, GPL-2 — design only) |

<!-- library register 2026-08-12T02:12:32.803Z -->
| mcs-working-the-flock-batch-session | 2 | Working-the-flock batch session — run the whole flock through the chute in one pass, ticking per-animal actions (wormer/vaccine/weight/blood/drug/trim-toes/shear/weaned) instead of per-record forms (concept from LambTracker GroupSheepManagement, GPL-2 — design only) |

<!-- library register 2026-08-12T02:54:21.538Z -->
| mcs-pen-movement-log-derived-state | 1 | MCS-9: pen as append-only movement log, current pen DERIVED (farmOS concept, no code) — movements[] source of truth, scalar pen mirrored, drift+roster validation, migration seeded 51/276; surfaced baby-azure stale-roster drift |
