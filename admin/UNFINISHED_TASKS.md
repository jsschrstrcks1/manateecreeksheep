# Unfinished Tasks — manateecreeksheep

> **Task custody (HLS):** Work queues live in `.household-library/catalog.jsonl` — not in this file.
> Find/checkout: `node admin/library.mjs preflight --query "<task>" --patron <id> --merge`
> **This document** is context/spec only unless stated otherwise.

**Generated:** 2026-08-19T04:04:38.824Z
**SSOT:** `.household-library/catalog.jsonl`

Open tasks for this repo (`state` ≠ `complete`). Regenerate:

```bash
node admin/library.mjs mirrors --repo manateecreeksheep
```

| priority | state | holder | task_id | title |
|----------|-------|--------|---------|-------|
| 1 | returned | — | mcs-attention-triage-list | MCS-3: attention-priority triage list — worst-first composite score (FAMACHA trend, FEC, days-since-check, flags) with R/A/G status |
| 1 | registered | — | mcs-breeding-pipeline | MCS-17: master breeding pipeline — one row per mating, derived dates (check/due/wean/rebreed), exposure WINDOWS for pen breeding; unlocks MCS-33 scheduling; PRIORITY: parasite-control instrument |
| 1 | registered | — | mcs-coat-shed-trait-log | MCS-19 (operator: huge): wool-vs-hair/shedding as structured seasonal trait log — shed score 1-5 + date each summer, coat class derived |
| 1 | returned | — | mcs-drug-withdrawal-tracking | MCS-7 (from LambTracker, GPL-2, concept only): per-drug meat/milk WITHDRAWAL tracking with 'not safe until <date>' alerts. When an animal is treated, record the drug's withdrawal interval and flag the animal as not-safe-to-slaughter / milk-not-saleable until the window clears, so a treated animal can't be sold to slaughter or its milk marketed by mistake. Food-safety essential for a meat/parasite flock. Store withdrawal period per drug in the drug table; compute per-animal clear-date on treatment; surface it on the animal record and in any 'ready to sell/cull' view. |
| 1 | registered | — | mcs-ewe-lifetime-productivity | MCS-18: ewe lifetime productivity ledger — per-dam lambings across years (lambs weaned per ewe lifetime; sheep have lambings not litters) |
| 1 | returned | — | mcs-famacha-fec-combined-decision | MCS-8 (from FuzzyLogic-VERMIFUGA, concept only): deworming decision reads FAMACHA + FEC TOGETHER, and treats disagreement as a diagnostic signal. Rules: anemic (bad FAMACHA) + LOW egg count -> anemia may NOT be parasites, investigate before dosing; good colour + HIGH egg count -> animal copes but is shedding heavily onto pasture (refugia/contamination consideration). Do not deworm on FAMACHA alone. Sharpens the recheck/treat nudge (see MCS-1): surface the mismatch cases rather than blindly dosing on one number. Grounded in standard integrated parasite management. |
| 1 | returned | — | mcs-famacha-schema-normalization | AUDIT FINDING: famacha_scores entries split 91 'famacha' vs 16 'score' keys (Lara's history among the 16) — normalize via migration + validator rule; agenda-engine plan already fixed to dual-read so nothing silently drops |
| 1 | registered | — | mcs-fat-tail-tracking | MCS-20 (operator: huge): fat-tail phenotype scoring + lineage tracking (Awassi/Tunis lines) feeding mating prediction |
| 1 | registered | — | mcs-fecrt-drench-check | MCS-30: FECRT drench-check — FEC at treatment + 10-14d later per drug class; maintains the does-it-still-work-here table (ivermectin=medium already recorded); welfare guardrails bound |
| 1 | returned | — | mcs-flock-agenda-engine | Flock agenda engine (plan: docs/superpowers/plans/2026-08-12-flock-agenda-engine.md) — derive withdrawal locks, FECRT windows, FAMACHA rechecks, pending IDs from flock DB; the feed Atlas serves and Crane displays (Phases 2-4 follow-on) |
| 1 | returned | — | mcs-flock-pwa | Flock PWA (operator directive): installable, offline-first, served by Atlas /flock on tailnet; token entered once per device, encrypted at rest (passkey-PRF), never in bundle; prefer flock-scoped token; chute-side entry + agenda (plan Phase 5) |
| 1 | registered | — | mcs-genetic-trait-card | MCS-32: two-tier genetic trait card — Mendelian letters w/ per-locus source+confidence (scrapie, color, horns, Booroola, TMEM154, FGFR3) + polygenic EBV bars (resistance/resilience/avoidance/maternal; burden-conditioned; evidence-grade labels; tolerance-slope mature form) |
| 1 | returned | — | mcs-health-event-log | MCS-26 (operator directive): typed per-animal health & adverse-event log — foot rot, parasites, fly strike, predation, everything in between; condition vocabulary + diagnosis + treatment + body location + outcome, append-only (MCS-9 shape), feeds MCS-7 withdrawal and MCS-3 triage |
| 1 | registered | — | mcs-milk-records | MCS-21 (operator: huge): per-ewe milk records (MCS-12 quantity shape) + maternal milk ability as selection trait |
| 1 | returned | — | mcs-pen-movement-log-derived-state | MCS-9: pen as append-only movement log, current pen DERIVED (farmOS concept, no code) — movements[] source of truth, scalar pen mirrored, drift+roster validation, migration seeded 51/276; surfaced baby-azure stale-roster drift |
| 1 | registered | — | mcs-pen-moves-pending | 3 planned pen moves NEVER applied (Buck->Pen6, Rocky tag140->TreeFort, MC08->auction) + Orange Tag 31 ewe unlocated since 5/14 + Windlestone ram isolation rec (chat-got-pen-plan: 'reported dangerous'). VERIFY against current movements log first; apply as MCS-9 movement events |
| 1 | registered | — | mcs-periparturient-window | MCS-33: periparturient window management — lambing calendar auto-schedules FAMACHA/FEC checks + late-gestation nutrition flag; maternal resistance as selection signal |
| 1 | returned | — | mcs-privacy-attestation-parity | AUDIT EXPANSION: privacy attestation (tools/attest-repo-private + pre-push gate, completed for OCS) absent from manateecreeksheep — pushes ungated while the repo now carries family/operational data (photos, family names, health, finances-adjacent) |
| 1 | returned | — | mcs-repo-safety-parity | AUDIT EXPANSION: dangerous-command guard + arm-hooks-path into manateecreeksheep — the P0 guard (hostile-hardened via 10+ completed OCS passes) is ABSENT from the sheep repo's hooks and core.hooksPath is UNSET (measured: .githooks chain dead in git, the UL-226/229 disease). Harness change: Layer 3 discipline applies |
| 1 | registered | — | mcs-scrapie-genotype | MCS-15: scrapie genotype (PRNP 136/154/171) tracking + breeding selection; commercial tests exist (Gene Check/Neogen); pedigree-derivable |
| 1 | registered | — | mcs-weather-parasite-prompting | MCS-1: weather/climate-aware parasite-risk prompting — warm+wet stretch tightens FAMACHA recheck intervals (Phase 4 of integration plan reuses Crane Open-Meteo feed) |
| 1 | registered | — | mcs-weight-adjustment-factors | MCS-27: standard adjustment factors for lamb weights (birth type, rearing, dam age; hair-specific tables) + h2 calibration pass (Florida Cracker priors: FEC .33 FAMACHA .31 PCV .22 BCS .19; resilience .10-.19; retain pre-treatment records rule) |
| 1 | registered | — | ul220-manateecreeksheep-merge-never-committed | UL-350: UL-220's manateecreeksheep careful-not-clever superset merge was NEVER PERFORMED. UL-220 records that copy as 503 lines = canonical v1.4.1 in full + flock domain section, version 1.4.1-flock.1, verified zero-loss both ways. Measured 2026-08-11: disk 54L, HEAD 54L, origin/main 54L, last touched 2026-07-26 by a merge commit. The 503-line merge exists nowhere in git — third confirmed instance of UL-353 (a write into an ephemeral working tree recorded as achieved without ever being committed). The 54L copy IS a legitimate domain variant: 35 unique lines of flock doctrine (spiral-notebook-is-authority, sire/dam confirmation against sources, tag aliases) that canonical does not contain, so it must NOT be overwritten. It also carries ZERO hard-safety content: no catastrophic-irreversible-command refusals, no four layers, no economy ladder, no confidence scale. Correct fix is the superset merge UL-220 describes: canonical v1.4.2 in full PLUS the 35 flock lines preserved verbatim, version 1.4.2-flock.1, zero-loss verified BOTH directions (every canonical line present, every one of the 35 flock lines present). Requires someone who knows the flock domain to place the domain section sensibly. Urgency is bounded and measured, not assumed: the mechanical dangerous-command belt is wired at USER level in /root/.claude/settings.json, so this gap is doctrinal rather than the only line of defence (UL-203 correction applies). |
| 2 | available | — | master-plan-loose-ends-status-vs-manatee-creek-redesign-plan-md | Master plan loose ends (status vs MANATEE_CREEK_REDESIGN_PLAN.md) |
| 2 | registered | — | mc-2026-07-12-mining-handoff-extract | Extract manateecreeksheep container commit 1c7dfad (or 1ed8d05) SESSION-2026-07-12-HANDOFF.md + SCRIPTS/2026-07-12-mine-memories.py + 18 ephemeral /root/.memory JSON from redesign-plan-ZuzsE container — NOT on GitHub (push never succeeded). Replay to ocs-work/.memory after content arrives. |
| 2 | registered | — | mcs-animal-economics | MCS-13: per-animal economic lifecycle — cost basis in, proceeds out, profit per genetics; cost-of-gain with weight log |
| 2 | registered | — | mcs-eid-visual-dual-identity | EID + visual dual identity — store both electronic (RFID) and visual tags per animal; either is a valid lookup key so a lost/unreadable tag never orphans an animal's history (concept from OogieM/LambTrackerMobile, GPL-2 — design only) |
| 2 | registered | — | mcs-group-cohorts | MCS-10: group/cohort as first-class asset with log-derived time-aware membership (breeding groups, treatment cohorts, refugia groups) |
| 2 | returned | — | mcs-health-record-validation | AUDIT EXPANSION: validate_flock's completed P0.x/P1.x battery predates the health-record era — extend to treatments shape/dates, famacha entry shape, drug_reference/withdrawal_watch consistency, anomalies schema |
| 2 | registered | — | mcs-indemnity-loss-records | MCS-29: documented-loss records fit for indemnity claims (USDA LIP: predation + extreme heat; 30-day notice) — evidence bundle prompted at time of loss |
| 2 | registered | — | mcs-input-inventory | MCS-25: input inventory — wormer/vaccine/feed on hand with expiry + reorder point; balance derived from transactions |
| 2 | returned | — | mcs-ledger-check-parity | AUDIT EXPANSION: the sheep UPGRADE-LEDGER now carries 34 MCS ids + tracked pointers but OCS's concept-ledger-check guards only its own 8 ledgers — extend or twin the checker (dup ids, dangling tracked pointers) for manateecreeksheep |
| 2 | registered | — | mcs-mating-outcome-predictor | MCS-22: mating outcome predictor — sire x dam -> trait probabilities with plain-language topline; Tier-1 Punnett + Tier-2 midparent EBVs with spread (never certainty); extends breeding_projector |
| 2 | registered | — | mcs-pedigree-inbreeding-views | MCS-16: rendered pedigree views + certificates + Wright's inbreeding coefficient for the closed-loop policy (F field already seeded on 2 records) |
| 2 | registered | — | mcs-pending-done-log | MCS-11: reminder and record are ONE object — pending->done dated log entries underpin reminders, worklist, and history |
| 2 | registered | — | mcs-push-reminders | MCS-2: push reminders to a channel the operator already watches — delivery layer for the agenda (channel choice = operator decision point, plan Phase 2) |
| 2 | returned | — | mcs-quantity-abstraction | MCS-12: one quantity shape for every measurement (value+unit+measure+label) — weight, FAMACHA, FEC, BCS, temp without schema changes |
| 2 | registered | — | mcs-quarantine-intake | MCS-28: intake quarantine records — biosecurity first-class; arrival drench + FEC-clean release gate (resistant-worm defense) |
| 2 | registered | — | mcs-ration-nrc-evaluation | MCS-23: ration evaluation against NRC requirements — feed ADEQUACY; late-gestation protein funds immunity; underfed reads as parasite-suspect |
| 2 | registered | — | mcs-sell-weight-calculator | MCS-24: what-weight-to-sell-lambs marginal economics calculator (feed cost of next lbs vs price slide) |
| 2 | registered | — | mcs-sheets-sync-l6 | L6 (redesign plan, only blocked phase): google-sheets MCP round-trip sync needs GCP project credentials — OPERATOR provides creds; sheet and JSON drift until done |
| 2 | returned | — | mcs-working-the-flock-batch-session | Working-the-flock batch session — run the whole flock through the chute in one pass, ticking per-animal actions (wormer/vaccine/weight/blood/drug/trim-toes/shear/weaned) instead of per-record forms (concept from LambTracker GroupSheepManagement, GPL-2 — design only) |
| 3 | registered | — | mcs-blup-animal-model | MCS-31 (HEDGED): pedigree BLUP animal model as someday-upgrade for internal EBVs — NSIP covers anchored 90; deliberately not urged; registered for tracking only |
| 3 | registered | — | mcs-cv-image-scoring | MCS-14 (HEDGED low-confidence): image->1-5 score via CV for BCS/FAMACHA — NOT to build until labelled data + safety story exist; registered for tracking only |
| 3 | registered | — | mcs-owner-sync-unknowns | Owner-sync bundle: 12 [UNCLEAR] markers, unknown-status animals (daisys-daughter-1, tag-35-ewe, ext-lambs...), 7 unknown-sire lambing records, L7 annual eval scores, L11 drought cull list review |
| 3 | available | — | p3-1-six-alive-sheep-have-no-pen | P3.1 Six alive sheep have no pen |
| 3 | available | — | p3-2-two-sold-sheep-still-tagged-with-a-pen | P3.2 Two sold sheep still tagged with a pen |
| 3 | available | — | pen-assignment-hygiene | Pen-assignment hygiene |
| 4 | available | — | data-source-freshness | Data-source freshness |
| 4 | registered | — | mc-00113-shearing-and-famacha | Shear 00113 + take formal FAMACHA baseline; log parasite-resistance data |
| 4 | registered | — | mc-baby-azure-heat-signal-review | Fold Baby Azure heat-death into Azure × Kelsier breeding notes; heat tolerance is a lambing selection criterion |
| 4 | registered | — | mc-buck-breed-comp-verify-2026-05-14 | Verify Buck breeding-page composition source against flock_database.json and REPO-AGENT-APPENDIX (disputed comp — session 2026-05-14) |
| 4 | registered | — | mc-buck-original-death-date-2026-05-14 | Resolve Buck original ram identity merge and death-date uncertainty (session 2026-05-14) |
| 4 | registered | — | mc-kaladin-current-pen-2026-04-26 | Locate Kaladin's current pen (alive; pen null after bulk-cleanup correction) |
| 4 | registered | — | mcs-centralia-image-attachments | Centralia records: 8 image references pending owner attachments (ram_1/2/4/5, registration scans, NSIP detail screen, IMG_2355 crate arrival) — files described in records but never committed; owner must supply, then re-run validate --check-images |
| 4 | available | — | p4-1-low-confidence-records-that-never-received-owner-verificati | P4.1 Low-confidence records that never received owner verification |
| 4 | available | — | p4-2-twelve-unclear-markers-still-in-db | P4.2 Twelve `[UNCLEAR]` markers still in DB |
| 4 | available | — | p4-3-lambing-record-sire-holes | P4.3 Lambing-record sire holes |
| 5 | registered | — | mc-00113-foster-dam-plan-for-rebreed | If 00113 is re-bred, arrange a foster dam in advance; parasite-resistance donor but proven bad mother |
| 5 | registered | — | mc-angus-tag-and-famacha-baseline | Tag Angus + take FAMACHA baseline at next handling |
| 5 | registered | — | mc-bambii-2027-breeding-partner | Pick 2027 breeding partner for Bambii + Bambii's Baby (Charlie vs Angus, not Rocky) |
| 5 | available | — | open-follow-up-orange-tag-31-ewe-location-2026-05-14 | Open follow-up — Orange Tag 31 Ewe location (2026-05-14) |
| 5 | available | — | p5-1-no-handoff-md | P5.1 No HANDOFF.md |
| 5 | available | — | p5-2-no-unfinished-tasks-md-baseline-before-this-audit | P5.2 No `unfinished_tasks.md` baseline before this audit |
| 5 | available | — | p5-3-no-notebook-card-workflow-md-l12 | P5.3 No NOTEBOOK_CARD_WORKFLOW.md (L12) |
| 5 | available | — | pen-data-drift-surfaced-and-fixed-2026-05-14 | Pen-data drift surfaced and fixed 2026-05-14 |
| 5 | available | — | planned-pen-moves-2026-05-14-not-yet-executed | Planned Pen Moves — 2026-05-14 (not yet executed) |
| 5 | available | — | process-docs-gaps | Process / docs gaps |
| 5 | available | — | recommended-next-sweep-one-commit-each | Recommended next sweep (one commit each) |
| 5 | available | — | sweep-progress-2026-05-13-session-2 | Sweep Progress — 2026-05-13 session 2 |
