# Manatee Creek Data Redesign — Completion Plan

**Source thread:** session `01VbjUkAAxGLw6DP22izNYsZ` (Mar–Apr 2026, ~45 commits)
**Branch:** `claude/manatee-creek-redesign-plan-ZuzsE`
**Companion plan (orchestrator side):** `ken/MANATEE_CREEK_REDESIGN_PLAN.md`

---

## 1. What the thread built

A complete rebuild of the flock's breeding, health, and pen-management data
model around three principles:

1. **Selection hierarchy inverted** — FAMACHA/FEC > Hair (observed) > Breed >
   Meat. Performance beats pedigree.
2. **Closed 7-pen geographic pipeline** — Pen 3 (intake) → Tree Fort → Pen 4 →
   Pen 5 → Pen 6 → Pen 1 → Pen 2 (elite). Stages tighten; the best breed with
   the best.
3. **Every animal justifies its place every year** — ram + ewe annual
   evaluation rubrics are now the gate for advancement and culling.

### Artifacts landed

| File / location | What it is |
|---|---|
| `data/flock_database.json` | 179 sheep (50 alive, 77 deceased, 18 sold, 1 culled), 14 lambing records 2026, 47 animals with FAMACHA history, `breeding_policy`, `breeding_goals`, `tagging`, `headcount` sub-trees |
| `data/breed_reference.json` | 22 breeds classified hair/wool/intermediate with average weights |
| `data/sheets_export/` | 7 TSVs + `flock_sheets_update.gs` Apps Script |
| `scripts/export_to_sheets.py` | Regenerates the above from `flock_database.json` |
| `scripts/validate_flock.py` | Integrity checks (refs, breed %, tag uniqueness, status rules) |
| `.claude/skills/breeding-advisor/` | 30-point checklist, annual eval rubrics, `DATA_REQUIREMENTS.md` |
| `.claude/skills/google-sheets-sync/SKILL.md` | Sheet ↔ JSON bridge via MCP (documented, not wired) |
| `data/investigations/*.md` | Diet-to-taste, rosemary, hay/forage, rolled oats research |

### Key decisions encoded
- Kelsier (Katahdin) = gold standard sire — most parasite resistant
- St Croix & BBB lineages DIED on this property — reject in favor of Katahdin/Awassi
- Dorper is parasite-vulnerable despite hair coat — hair ≠ resistance
- Spring 2026 drought = lowest parasite pressure = strongest cull signal possible
- New tag convention: MC26xx green tags, rams in left ear, ewes in right

---

## 2. Loose ends — what isn't done

Ranked by risk to data integrity.

### L1. `pens.*` sub-tree is a zombie
```
pens.pen_1.members: 0
pens.pen_2.members: 0
...all nine pens: 0
```
Pen assignments live only on individual sheep's `pen` field. The `pens`
object is either (a) a legacy structure to delete, or (b) a derived roster
that needs a rebuild pass. Decide and fix.

### L2. Auction April 6 only partially recorded
3 of 5 planned auctions show `status=sold`: Eclipse, 0033 Twin Ram 1, 0033
Twin Ram 2. Verify BT Twin Ewe 2 White and Elsie Small White Triplet —
set `status`, `sold_date`, `sold_price`, `sold_to` if the auction happened.

### L3. Windlestone Kat/Dorper ram not confirmed in JSON
Commit `5067de2` announced his arrival to Pen 2 with FAMACHA 1 for 1 year,
100% hair, dangerous-handler note. Verify there's a sheep row with full
breed comp, DOB, attitude warning, and that he's actually placed in Pen 2.

### L4. Charlie "abscess" misdiagnosis not in health log
Commit `7306f6f` corrected it: catch-panel puncture, NOT CL. Charlie's
health record needs a dated entry reflecting this — otherwise future
readers will see "abscess" with no context and worry about CL.

### L5. `export_to_sheets.py` covers 7 tabs; full target is ~26
Missing tab generators:
- Master Flock List (identity + breed % + DOB + sire/dam + weight + tag)
- Breeding Season Tracker (per-lamb: sire, birth date, 30/60/90 day weights, ADG)
- Health & Treatment Log (date-indexed, FAMACHA at time of)
- Famacha & FEC Trend (longitudinal, per-animal)
- Weight History & ADG
- Active Ewes / Active Rams registries
- Costs & Financials
- Per-pen rosters (9 tabs — one per pen)

### L6. `google-sheets-sync` not wired
Skill documents the setup (`claude mcp add google-sheets -- uvx
mcp-google-sheets@latest`, service-account creation, `GOOGLE_CLOUD_PROJECT=
constant-cubist-471700-e1`) but nobody's run it. Until it is, the sheet and
JSON drift anytime either changes.

### L7. Annual evaluations not instantiated
`breeding-advisor/SKILL.md` defines the rubric. `export_to_sheets.py`
computes the rows on the fly. There's no `data/ram_annual_eval.json` or
`data/ewe_annual_eval.json` — so last year's eval is irrecoverable once
the next export overwrites.

### L8. Investigations are orphans
`data/investigations/` has four research reports. None are referenced from:
- `flock_database.json`
- `breeding_policy`
- any export tab
- any breeding recommendation

The rosemary research in particular has a concrete actionable recommendation
(rosemary hedge + 14–21 day pre-slaughter pen) that's not in the plan.

### L9. Cognitive memory is empty
```
$ python3 /home/user/ken/orchestrator/memory_ops.py tree
{}
```
None of the thread's hard-won decisions are in `~/.memory/sheep/`. Next
session starts blind. Hard lessons (St Croix died here, drought = cull
signal), architectural decisions (7-pen loop, selection hierarchy),
definitions (Kelsier = gold standard) should be `--protected` memories.

### L10. `data/processed/` is empty
`scripts/process_images.py` exists. Images IMG_8560–IMG_8643 (4032×3024 or
1320×2868) exceed the 2000px API limit. No processed counterparts means
future sessions can't read the notebook images directly.

### L11. Drought-driven cull list hasn't landed
Commit `66cbde5` noted: "Animals scoring FAMACHA 4–5 now are failing
during easiest conditions. Strongest cull signal possible." No follow-up
commit names which animals that flags for culling. `breeding_policy` has
the general rule; there's no specific 2026 cull list as an output.

### L12. Notebook card transcription is still live
Most recent commit (2026-04-21) transcribes Pen 1 + Tree Fort cards. Mom
keeps taking pictures. This is continuous work, not a one-time job —
needs a repeatable workflow, not one more sprint.

---

## 3. Completion plan

Six phases, each independently shippable.

### Phase 1 — Integrity pass (this repo)
Fix L1, L2, L3, L4 in a single sweep.
- Decide on `pens` sub-tree: delete if legacy, or add a `scripts/rebuild_pens.py`
  that derives `pens.<name>.members` from sheep `pen` field.
- Verify BT Twin Ewe 2 White and Elsie Small White Triplet against the
  April 6 auction. Update `status`, `sold_date`, `sold_price`, `sold_to`.
- Confirm Windlestone ram is in JSON with full breed comp and Pen 2 placement.
- Add Charlie's catch-panel puncture entry with date to his health log.
- Run `python3 scripts/validate_flock.py --check-references --check-images`.
- Commit with diff summary per fix.

**Exit:** validator passes; four loose records reconciled.

### Phase 2 — Drought cull list (this repo)
Close L11.
- Query `flock_database.json` for every alive animal with any FAMACHA 4 or 5
  score in the last 60 days.
- Cross-reference against `breeding_policy.weak_resistance_list`.
- Produce `data/2026_drought_cull_list.md` with each animal's FAMACHA
  timeline, pen, pedigree impact of removal, and recommended action
  (auction / cull / watch-list).
- Append a `breeding_policy.hard_lessons` entry: "Spring 2026 drought
  revealed the true parasite-vulnerable cohort — failures under minimum
  pressure are the strongest cull signal we will ever get."

**Exit:** cull list committed; policy updated.

### Phase 3 — Export to 26 tabs (this repo)
Close L5.
- For each missing tab, add a `build_<tab>()` function to
  `export_to_sheets.py` that reads only `flock_database.json` +
  `breed_reference.json`.
- Per-pen rosters can be generated by one loop over `sheep[]` grouped by
  `pen`, producing 9 TSVs from one pass.
- Regenerate `flock_sheets_update.gs` to cover all 26 tabs.
- Add a `--dry-run` mode that prints expected tab count and row counts
  without writing.

**Exit:** `export_to_sheets.py` produces 26 TSVs + one Apps Script; row
counts match `flock_database.json` animal count.

### Phase 4 — Wire the MCP sync (this repo)
Close L6, replacing the paste-based workflow.
- Follow `.claude/skills/google-sheets-sync/SKILL.md` setup steps.
- Add `scripts/sync_sheet_to_json.py` that reads via MCP and diffs
  against `flock_database.json`. Drift is reported but not auto-applied
  (owner confirms each change).
- Document the workflow: edit in sheet → `sync_sheet_to_json.py` →
  validator → commit.

**Exit:** MCP connection verified; round-trip sheet↔JSON with no drift
on a known-good animal.

### Phase 5 — Annual eval persistence (this repo)
Close L7.
- Extract eval logic from `export_to_sheets.py` into
  `scripts/run_annual_eval.py`.
- Output to `data/annual_evals/YYYY_ram_eval.json` and
  `data/annual_evals/YYYY_ewe_eval.json` — immutable per-year audit.
- `export_to_sheets.py` reads from these JSONs instead of recomputing,
  so last year's eval survives this year's export.

**Exit:** `data/annual_evals/2026_ram_eval.json` +
`2026_ewe_eval.json` committed; export produces same rows from the
persisted files.

### Phase 6 — Investigation tie-in + image pipeline + memory (this repo)
Close L8, L9, L10, L12.
- **L8:** add `breeding_policy.referenced_research[]` pointing to
  `data/investigations/*.md` with a one-line `decision_affected` note each.
  Add a "Pre-slaughter rosemary protocol" to `breeding_goals.market_uplift`
  or similar.
- **L10:** run `scripts/process_images.py` over the full image set. Verify
  processed count equals source count. Add a validator check.
- **L12:** document the notebook card workflow in
  `docs/NOTEBOOK_CARD_WORKFLOW.md` — photo → image-transcription skill →
  proposed JSON diff → owner review → commit. One document, short,
  repeatable.
- **L9 (cognitive memory):** encode the thread's durable decisions as
  `--protected` memories. Minimum set:
  - `selection_hierarchy`: FAMACHA > Hair > Breed > Meat
  - `kelsier_gold_standard`: Katahdin, most parasite resistant
  - `hard_lesson_stcroix_bbb`: lineages died of parasites on property
  - `hard_lesson_dorper`: hair coat ≠ parasite resistance
  - `pipeline_v3`: 7-pen geographic closed loop, stage criteria tighten
  - `tag_convention_2026`: MC26xx green, rams left, ewes right
  - `drought_2026_rule`: failures under minimum pressure = strongest cull signal

**Exit:** memory `tree` shows protected entries for each bullet; all four
L-items closed.

---

## 4. Execution order

```
Phase 1 (integrity) ──┐
                      ├─► Phase 3 (26 tabs) ──► Phase 4 (MCP sync) ──┐
Phase 2 (cull list) ──┘                                              │
                                                                     ├─► Phase 6 (tie-in + memory)
                      Phase 5 (annual eval persistence) ─────────────┘
```

Phases 1 and 2 are independent and small; do them first to stabilize the
JSON before any schema expansion. Phase 3 expands the export; Phase 4
replaces the paste workflow — do in that order so the 26-tab output is
proven before MCP takes over. Phase 5 is independent of 3/4 but needed
before Phase 6 so memory can reference audited evals. Phase 6 closes
everything and encodes the lessons.

---

## 5. Out of scope

- Migrating the 113-tab historical sheet into the new 26-tab structure.
  That's `ken/.claude/skills/google-sheets-migration/` and is tracked in
  the companion `ken/MANATEE_CREEK_REDESIGN_PLAN.md`. The migration
  rescues **historical** records; this plan is about **current** records.
- Building new investigation research. The 4 existing reports are enough
  — this plan tie them in, not add more.
- Changing the orchestrator, adapters, or multi-LLM infrastructure.

---

## 6. What "done" looks like

1. `pens.*` either populated or deleted — no zombie structure.
2. April 6 auction fully reconciled (5/5 animals), Windlestone ram
   placed, Charlie health log corrected.
3. 2026 drought cull list committed with per-animal reasoning.
4. `export_to_sheets.py` produces 26 TSV tabs; Apps Script updates all 26.
5. Google Sheets MCP sync works round-trip with no drift.
6. `data/annual_evals/2026_*_eval.json` exist and are the eval's system of
   record.
7. `data/processed/` has a processed image for every IMG_85xx source.
8. `breeding_policy.referenced_research[]` links to every
   `data/investigations/*.md`.
9. Cognitive memory `tree --domain sheep` returns seven protected
   foundational memories.
10. `docs/NOTEBOOK_CARD_WORKFLOW.md` exists as the standing operating
    procedure for Mom's continuing photos.

---

*Soli Deo Gloria.*
