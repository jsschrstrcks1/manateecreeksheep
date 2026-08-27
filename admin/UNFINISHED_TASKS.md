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

<!-- library register 2026-08-11T01:39:44.289Z -->
| ul220-manateecreeksheep-merge-never-committed | 1 | UL-336: UL-220's manateecreeksheep careful-not-clever superset merge was NEVER PERFORMED. UL-220 records that copy as 503 lines = canonical v1.4.1 in full + flock domain section, version 1.4.1-flock.1, verified zero-loss both ways. Measured 2026-08-11: disk 54L, HEAD 54L, origin/main 54L, last touched 2026-07-26 by a merge commit. The 503-line merge exists nowhere in git — third confirmed instance of UL-326 (a write into an ephemeral working tree recorded as achieved without ever being committed). The 54L copy IS a legitimate domain variant: 35 unique lines of flock doctrine (spiral-notebook-is-authority, sire/dam confirmation against sources, tag aliases) that canonical does not contain, so it must NOT be overwritten. It also carries ZERO hard-safety content: no catastrophic-irreversible-command refusals, no four layers, no economy ladder, no confidence scale. Correct fix is the superset merge UL-220 describes: canonical v1.4.2 in full PLUS the 35 flock lines preserved verbatim, version 1.4.2-flock.1, zero-loss verified BOTH directions (every canonical line present, every one of the 35 flock lines present). Requires someone who knows the flock domain to place the domain section sensibly. Urgency is bounded and measured, not assumed: the mechanical dangerous-command belt is wired at USER level in /root/.claude/settings.json, so this gap is doctrinal rather than the only line of defence (UL-203 correction applies). |

<!-- library register 2026-08-27T05:05:50.774Z -->
| audit0827-mcs-web-write-path | 1 | P1 AUDIT-0827: web/app.py has no route that writes flock_database.json (2 non-GET routes, both pure computation) — every correction in the P0/P1 pedigree backlog means hand-editing a ~27,000-line JSON, which is the structural reason the backlog persists. Build a minimal owner-only edit path (per-field correction endpoint + audit log), then burn down the mirror's P0 items. First step either way: run scripts/validate_flock.py to settle the admin-mirror vs root-tasks contradiction (validator claimed 0 errors 2026-05-13; mirror of 2026-07-11 lists them open). |

<!-- library register 2026-08-27T05:05:51.170Z -->
| audit0827-mcs-sheets-gs-coverage | 2 | P2 AUDIT-0827: data/sheets_export/flock_sheets_update.gs writes 7 of the 25 exported tabs; the plan (MANATEE_CREEK_REDESIGN_PLAN.md:164-176) required 26 TSVs + full .gs coverage — 18 tabs (Master Flock List 186 rows, Health Log, Famacha Trend 402 rows, Weight/ADG, per-pen rosters...) are manual copy-paste only, and the export itself stops at 25 vs the plan's 26. Extend the generators in scripts/export_to_sheets.py (:606-788 pattern) and reconcile the tab count. |

<!-- library register 2026-08-27T05:05:51.559Z -->
| audit0827-mcs-migration-never-run | 2 | P2 AUDIT-0827: the 113->26-tab migration script (572 lines, checkpoint/resume) lives in ken/skills/google-sheets-migration/ — a different repo than the data it migrates — and by every local artifact was never executed (no checkpoint file, HANDOFF.md still prospective: step 1 is 'paste into Apps Script editor'); live sheet state unverifiable from a container. Operator+agent on the Mac: run it (or record the decision to abandon), and move/mirror the skill into this repo so README.md:230 stops documenting a skill the repo does not have. |

<!-- library register 2026-08-27T05:05:51.951Z -->
| audit0827-mcs-famacha-field-split | 2 | P2 AUDIT-0827: flock_database.json carries BOTH famacha_history (151 occurrences) and famacha_scores (246); web/app.py:390 reads famacha_scores while the breeding-advisor's DATA_REQUIREMENTS require health.famacha_history for checks 4/5/14/15 — a half-completed rename splits consumers across two fields (advisor impact inferred, not traced live). Unify the field, migrate the records, update both consumers. |

<!-- library register 2026-08-27T05:05:52.356Z -->
| audit0827-mcs-ebv-pipeline-orphan | 3 | P3 AUDIT-0827: the EBV pipeline is the household's largest orphan — ~455 data files (ebvs_scraped ~230, khsi_cache ~225, rankings, dumps), 10 scripts (~1,840 lines), docs/ebv_pipeline.md — with zero references in the web app; likewise 16 generated breeding-plan markdowns (incl. 4 unmarked versions of the ebv-weighted allocation with no current-marker), full FAMACHA/weight/treatment history, annual evals (all-null stubs awaiting owner scores, no input surface), the drought cull list, 7 research docs, and ~100 unorganized IMG_*.JPG (~290 MB) at repo root. Decide the viewing surface (extend the Flask app) or mark each output CLI-only; mark the current breeding-plan version; move the images out of the root. |

<!-- library register 2026-08-27T05:05:52.774Z -->
| audit0827-mcs-config-hardcodes | 3 | P3 AUDIT-0827: the Google Sheet ID is hardcoded in a generated string literal (export_to_sheets.py:567), the generated .gs, and the sibling-repo migration skill — retargeting means editing a Python-embedded JS literal; DB_PATH is independently re-derived in 10 files (2 relative, breaking off-root); breed genetics weights are Python literals while data/breed_reference.json goes unread; GOOGLE_CLOUD_PROJECT/credentials exist only as prose (no .env.example though .gitignore whitelists one); PORT is the repo's only env-driven setting. Centralize into one config module + .env.example. |
