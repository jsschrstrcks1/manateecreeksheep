<!-- Soli Deo Gloria. The flock is entrusted, not owned; the records serve real animals. -->

# Sheep Tasks — Consolidated Plan (2026-08-18)

**Operator ask:** *"find the sheep tasks in the HLS and Upgrade ledger and make a plan."*
**Sources consulted (measured this session, not assumed):**

- HLS catalog (`open-claw-stuff/.household-library/catalog.jsonl`): 120 sheep-related rows —
  23 complete, 97 open (76 registered · 18 available · 3 returned).
- `open-claw-stuff/docs/HOUSEHOLD-TASK-INDEX.md` (full MCS-N specs for the mcs-* tasks).
- `admin/UNFINISHED_TASKS.md` (this repo's mirror, generated 2026-07-11 — stale; see F6).
- `open-claw-stuff/docs/UPGRADE-LEDGER.md` sheep rows (UL-276/279/280/281/285/307,
  UL-449/455/701 — the UL-220 merge saga).
- `open-claw-stuff/docs/PERMANENT-LAYER-AUDIT-2026-08-12.md` (parity matrix + sheep expansions).
- Cognitive memory recall through the evidence envelope (directives honored, evidence weighed).
- Fresh measurements of `data/flock_database.json` and this repo's hook surface (below).

**Standing directives that bind every task in this plan** (operator-endorsed memories):

1. `status_date` values **2026-04-02 and 2026-04-06 are bulk-cleanup placeholders, not real
   death dates** — always ask the operator for the real date and cause (19fdb7dd).
2. **Never finalize a sheep ID below medium confidence without owner confirmation.** Owner
   testimony overrides DB text and pedigree inference (51435d7a).
3. `data/flock_database.json` is **SSOT for identity/status/pen**; memories are hints; never
   write memory conclusions into the DB without a `validate_flock.py` pass (d16d28e4).
4. **Pen 4 breeds.** It is the weak/pet/chronic pen but every ewe is a lamb-producing asset;
   do not model it as a no-breeding isolation pen (d33f0296).
5. Helene (2024-09-26) is the default hypothesis for stale-deceased corrections; Idalia only on
   contrary evidence. NoriSon = Eclipse, sold alive 2026-04-26 — never a hurricane casualty
   (79b75f4a, 881009c2). "Nuba" is a transcription error for tag 0053 — never reintroduce (74dede4e).

---

## Findings (fresh, 2026-08-18)

| # | Finding | Evidence |
|---|---------|----------|
| F1 | **94 of 145 alive animals have no `pen` recorded** (only 51 assigned: Pen 2×12, Pen 1×9, Pen 5×8, Pen 4×7, …). The old `p3-1-six-alive-sheep-have-no-pen` task title is off by 15× against today's DB. | measured `data/flock_database.json` this session |
| F2 | **43 records still carry the suspect bulk-cleanup status_dates** (2026-04-02/-06); 1 of them on an *alive* record. Each needs an operator-supplied real date/cause per directive 1. | measured |
| F3 | **16 `[UNCLEAR]` markers** in the DB (task `p4-2` says twelve — it has grown). | measured |
| F4 | `validate_flock.py` passes **0 errors / 0 warnings** while F1–F3 stand — confirming `mcs-health-record-validation`: the validator battery predates the newer content and has no teeth for these classes. | ran validator this session |
| F5 | **The sheep UPGRADE-LEDGER does not exist in this clone** (`docs/UPGRADE-LEDGER.md` absent from working tree and all local git history), despite the 2026-08-12 audit citing it and `mcs-ledger-check-parity` describing "34 MCS ids" in it. The MCS-N specs survive in the HLS task index. UL-326-class: recorded, never landed. Same for the agenda-engine plan (`docs/superpowers/plans/2026-08-12-flock-agenda-engine.md` — absent in every clone here). | searched all 16 clones |
| F6 | `admin/UNFINISHED_TASKS.md` mirror is stale (2026-07-11); regenerate with `node admin/library.mjs mirrors --repo manateecreeksheep`. | file header |
| F7 | **UL-220/UL-350 careful-not-clever flock superset IS now landed** — PR #85 (`e019d95`) merged the 1.4.1-flock.1 519-line copy; skill-sync doctor grades it TRACKED. `ul220-manateecreeksheep-merge-never-committed` needs verification + completion in HLS, not rework. | git log + doctor this session |
| F8 | **This repo's main still lacks**: `dangerous-command-guard.mjs`, `arm-hooks-path.sh`, reasoning-log hooks, `REASONING-LOG.md`; `core.hooksPath` unset. The 2026-08-13 "16/16" rollout lives on branch `claude/memory-system-evaluation-s0yup4`, unmerged here. `mcs-repo-safety-parity` is genuinely open. (Sophos posture injection itself IS live: sophos-inject.sh present + wired, updated to current SSOT this session.) | ls + git config this session |

---

## The plan

Ordered by the household standard: **next most important architecturally** — what the rest
rests on — not best bang for the buck. Every phase honors the five directives above. Data
tasks that need Ken's testimony are batched, not dribbled.

### Phase 0 — Owner-sync bundle (blocks everything data-shaped; needs Ken, ~one sitting)

One consolidated questionnaire, one session, instead of 40 micro-interruptions.
Tasks: `mcs-owner-sync-unknowns` (P3) + `p4-1` + `p4-2` + `mc-buck-original-death-date-2026-05-14`
+ `mc-kaladin-current-pen-2026-04-26` + `open-follow-up-orange-tag-31-ewe-location` + F2's 43 dates.

- Build the questionnaire FROM the DB (script, not hand-list): the 43 suspect-date records
  (Helene-first per directive 5), 16 `[UNCLEAR]` markers, unknown-status animals, low-confidence
  IDs. Group by pen/pedigree so Ken can answer from memory efficiently.
- Apply answers only through `validate_flock.py`-gated commits; every correction cites
  "owner 2026-08-…" in the record, per DB convention.
- Also confirm the 3 never-executed pen moves (`mcs-pen-moves-pending`, P1: Buck→Pen 6,
  Rocky tag140→Tree Fort, MC08→auction) — executed in the field or not?

### Phase 1 — Data integrity foundation (architectural root; everything downstream reads this)

1. **`mcs-famacha-schema-normalization` (P1)** — migrate the 91-`famacha`/16-`score` key split,
   add a validator rule so it cannot recur. Live catch already showed 16 animals silently
   dropping from agenda logic.
2. **`mcs-health-record-validation` (P2, do it here anyway)** — give the validator teeth for
   the classes F4 proved invisible: suspect status_dates, pen-missing-on-alive, `[UNCLEAR]`
   count regression, famacha key uniformity. The validator is the gate every later phase
   depends on; a green light that can't see red is worse than none.
3. **`mcs-pen-movement-log-derived-state` (MCS-9, P1)** — pen as append-only movement log,
   current pen derived. This is the *structural* fix for F1's 94 missing pens: one
   chute-day census seeds the log (fold in `pen-assignment-hygiene`, `p3-1`, `p3-2`).
4. **`mcs-quantity-abstraction` (MCS-12, P2)** — one value+unit+measure+label shape. Cheap,
   and MCS-18/21/23/24/27 all build on it; do it before they exist, not after.
5. Regenerate the mirror (F6) and recreate `docs/UPGRADE-LEDGER.md` in this repo from the
   HLS task index (F5), then wire `mcs-ledger-check-parity` (P2) so the 9th ledger is guarded.

### Phase 2 — Health & parasite core (the operating business of this flock)

Order within phase: 26 → 7 → 8 → 30 → 1.

1. **`mcs-health-event-log` (MCS-26, P1 — operator directive)** — typed per-animal health and
   adverse-event log. The substrate for everything below.
2. **`mcs-drug-withdrawal-tracking` (MCS-7, P1)** — food-safety essential: per-drug withdrawal
   intervals, "not safe until <date>" locks on sell/cull views.
3. **`mcs-famacha-fec-combined-decision` (MCS-8, P1)** — never deworm on FAMACHA alone;
   disagreement is a diagnostic signal (refugia discipline).
4. **`mcs-fecrt-drench-check` (MCS-30, P1)** — FEC at treatment + 10–14d per drug class;
   detects anthelmintic resistance before it costs animals.
5. **`mcs-weather-parasite-prompting` (MCS-1, P1)** — warm+wet stretch tightens the recheck
   cadence.
   Field tasks ride along at next handling: `mc-00113-shearing-and-famacha` (P4),
   `mc-angus-tag-and-famacha-baseline` (P5) — fold into the first
   `mcs-working-the-flock-batch-session` (P2).

### Phase 3 — Agenda & delivery (turns records into a morning to-do)

1. **Recover or rewrite the agenda-engine plan first** (F5) — do not build from a cited
   document nobody can read.
2. **`mcs-flock-agenda-engine` (P1)** — derive withdrawal locks, FECRT windows, FAMACHA
   rechecks, pending IDs from the DB. Dual-read famacha keys until Phase 1.1 lands.
3. **`mcs-attention-triage-list` (MCS-3, P1)** — worst-first composite R/A/G.
4. **`mcs-periparturient-window` (MCS-33, P1)** — lambing calendar auto-schedules the
   vulnerable-window checks (depends on MCS-17 exposure windows; can start on recorded due dates).
5. **`mcs-pending-done-log` (MCS-11, P2)** and **`mcs-push-reminders` (MCS-2, P2)** — reminder
   and record as one object; deliver to a channel Ken already watches.
6. **`mcs-flock-pwa` (P1, operator directive)** — chute-side offline entry; last in the phase
   because it displays what 1–5 produce. `mcs-sheets-sync-l6` (P2) + `ken-mcs-migration-k-phases`
   (P1, ken repo) stay coordinated here — decide sheets-as-mirror vs PWA-as-entry before
   running migration.gs.

### Phase 4 — Breeding & genetics (three "operator: huge" items live here)

1. **`mcs-breeding-pipeline` (MCS-17, P1)** — one row per mating, derived dates, exposure
   windows. Unlocks MCS-33 fully; explicitly a parasite-control instrument.
2. **`mcs-ewe-lifetime-productivity` (MCS-18, P1)** and **`mcs-weight-adjustment-factors`
   (MCS-27, P1)** — the selection ledger.
3. **`mcs-genetic-trait-card` (MCS-32, P1)** + **`mcs-scrapie-genotype` (MCS-15, P1)** —
   two-tier trait card discipline; commercial PRNP testing feeds it.
4. **`mcs-coat-shed-trait-log` (MCS-19)**, **`mcs-fat-tail-tracking` (MCS-20)**,
   **`mcs-milk-records` (MCS-21)** — the three operator-huge phenotype logs; each is a thin
   seasonal capture once MCS-12's quantity shape exists.
5. Then predictors: `mcs-mating-outcome-predictor` (MCS-22, P2),
   `mcs-pedigree-inbreeding-views` (MCS-16, P2). `mcs-blup-animal-model` (MCS-31) and
   `mcs-cv-image-scoring` (MCS-14) stay parked as HEDGED someday-items — recorded, not scheduled.
   Field follow-ups: `mc-bambii-2027-breeding-partner`, `mc-00113-foster-dam-plan-for-rebreed`,
   `mc-baby-azure-heat-signal-review` fold into MCS-17 rows when it exists.

### Phase 5 — Economics, biosecurity, ops

`mcs-animal-economics` (MCS-13, P2) → `mcs-sell-weight-calculator` (MCS-24, P2) →
`mcs-input-inventory` (MCS-25, P2) → `mcs-quarantine-intake` (MCS-28, P2) →
`mcs-indemnity-loss-records` (MCS-29, P2) → `mcs-ration-nrc-evaluation` (MCS-23, P2) →
`mcs-eid-visual-dual-identity` (P2) → `mcs-group-cohorts` (MCS-10, P2).
MCS-28's quarantine concept already cross-pollinated household-wide as `hh-repo-intake-gate`.

### Parallel track — repo harness parity (independent of data phases; F8)

- **`mcs-repo-safety-parity` (P1)** — dangerous-command guard + arm-hooks-path into this repo's
  main (the 08-13 rollout branch never merged here). Layer-3 pass, live 8-case battery, per the
  Archive-proven pattern.
- **`mcs-privacy-attestation-parity` (P1)** — this repo holds family/farm data and pushes ungated.
- Reasoning-log machinery (this repo is on the `hh-reasoning-log-parity` target list).
- **Verify + complete `ul220-manateecreeksheep-merge-never-committed`** (F7: work is merged as
  PR #85; needs a second-patron assurance-case stamp, not code).
- Housekeeping: `mc-2026-07-12-mining-handoff-extract` (P2), `mcs-centralia-image-attachments`
  (P4, needs owner uploads — add to Phase 0 questionnaire).

---

## Sequencing rationale (why this order)

**Phase 1 before everything computational:** every engine (agenda, triage, breeding, economics)
reads the DB; F4 proved the current gate cannot see the known defect classes. Building engines
on ungated data manufactures confident wrong answers — the exact pre-reasoning failure Sophos
exists to prevent.

**Phase 0 first and batched** because 43 + 16 + 94 unknowns are answerable only by Ken
(directives 1–2 forbid guessing), and one structured sitting costs him less than months of
one-off questions.

**Health before breeding:** parasite management is the flock's stated operating priority
(MCS-17's own spec calls the breeding pipeline "a parasite-control instrument"), and MCS-7
withdrawal tracking is a food-safety obligation, not a feature.

**PWA last in its phase:** it is the window, not the machine — it should ship displaying real
agenda output, not placeholder data.

**Soli Deo Gloria.** Getting the records right *is* the care of the flock.
