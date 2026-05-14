# Unfinished Tasks — Audit 2026-05-13

Audit of prior-thread work in `manateecreeksheep`. Skills applied:
`flock-validation` (domain), `verification-before-completion` (process),
`careful-not-clever` (integrity).

## Planned Pen Moves — 2026-05-14 (not yet executed)

Recorded after today's wean batch. **Not applied to flock_database.json yet** —
update records when each move is physically done.

| # | Move | From | To | Reason | Status |
|---|------|------|-----|--------|--------|
| 1 | Buck (Tree Fort ram) | Tree Fort (= Chicken Coop) | Pen 6 | Replace MC08 as Pen 6 ram (with the 3 Windlestone Awassi ewes) | ⏳ Planned |
| 2 | Rocky (tag 140, Pen 2 ram) | Pen 2 | Tree Fort | Take over Tree Fort with the 3 ewes (0035, Bambii, Ewe 24/0003) after Buck leaves | ⏳ Planned |
| 3 | MC08 (Pen 6 ram) | Pen 6 | Auction | Cull/sell — replaced by Buck on the Awassi ewes | ⏳ Planned |

### Pen-data drift surfaced and fixed 2026-05-14

Found while doing the wean update; resolved in this commit:

- **0053** (no proper name; prior "Nuba" was a Claude transcription error, owner-confirmed 2026-04-24): correctly placed in Pen 1 with her baby ewe. Live "Nuba" name uses scrubbed from CLAUDE.md, lambing records, and `nuba-baby-ewe` notes. **IDs `nuba-0053` and `nuba-baby-ewe` left as-is** — opaque identifiers with cross-references throughout (`dam_id`, `offspring_ids`, eval files); changing them risks cascading breaks. Explanatory notes about the original misread are preserved so the lesson isn't lost.
- **Little Daisy**: was Pen 4 in `sheep[].pen` and Pen 5 in `pens.pen_5.ewes` + CLAUDE.md table. Owner-confirmed 2026-05-14: Pen 2 (with Rocky). Reconciled across all three.
- **windlestone-kat-dorper (ram)**: `sheep[].pen` was Pen 2 but he wasn't in 2026-04-24 photos and owner-confirmed Pen 2 = Rocky + Little Daisy only. `pen` field cleared to null pending owner verification of his actual location.
- **Tag 114 fawn wool ewe**: was Tree Fort in `sheep[].pen` but Pen 1 in `pens.pen_1.ewes` + CLAUDE.md text (with her ram lamb). Reconciled to Pen 1.
- **Bambii tag correction + new Tree Fort ewe (2026-05-14)**: Owner enumerated every Tree Fort animal — Buck, White Ewe 0035, Bambii, and a previously-unrecorded ewe tagged 24/0003 (= "240003"). Three corrections applied:
  - **Bambii** had tag "24/0003" in DB (sourced from notebook card photo IMG_0627). Owner confirmed Bambii's actual tag is orange #35 and she came from Heather Oaks Farm; the 24/0003 reading was a transcription error. Tag, color (white with fawn markings), and origin fixed on the Bambii record.
  - **New record `tag-24-0003-tf`** added — the actual holder of yellow scrapie tag 24/0003. All white with some wool on her back, Sir Loin daughter, no proper name, in Tree Fort.
  - **Orange Tag 31 Ewe** (`tag-31-orange-tf`) removed from Tree Fort — owner confirmed she's no longer there but current pen is unknown. `pen` set to null; lamb (Orange 31 Ram Lamb) already weaned to Goose Pen.

### Open follow-up — Orange Tag 31 Ewe location (2026-05-14)

- Orange Tag 31 Ewe (`tag-31-orange-tf`) is **alive but unlocated**. Owner did not know which pen she is in as of 2026-05-14.
- **Action:** locate her on the farm and update `pen` (and `pens.<pen>.ewes`) when found.

After execution:
- Pen 2: Rocky out → only Little Daisy remains; Pen 2 becomes a holding pen
- Pen 6: MC08 out, Buck in — sire change for the Windlestone Awassi group
- Tree Fort: Buck out, Rocky in — sire change for the 3 nursing ewes (lambs already weaned today)

When executed, update:
- `data/flock_database.json` sheep records: pen + last_verified
- `data/flock_database.json` `pens` section: ram fields
- `CLAUDE.md` Pen Structure table — remove the **Planned:** notes, update rams

## Sweep Progress — 2026-05-13 session 2

Validator state after sweep: **0 errors, 0 warnings** (was 21 errors, 7 warnings).
All P0/P1 validator issues from this audit closed.

| Item | Commit | Status |
|------|--------|--------|
| P0.2 — MC08/samson-daughter-p4 dam correction (bidirectional offspring_ids) | `14a6334` | ✅ Done |
| P3.2 — null pen on sold 0033 twin rams | `dc9aab3` | ✅ Done |
| P1.1 — add confidence to 16 of 20 missing records | `bc174ac` | ✅ Done |
| P0.3 — null charlies-ewe.dam_id (broken nori-line-f2 ref) | `efc3600` | ✅ Done |
| P0.4 — add 'gifted' to validator VALID_STATUS + fix elsie record | `754a11c` | ✅ Done |
| P1.3 — fix IMG_0661 broken ref (missing .JPG ext) | `25c1f37` | ✅ Done |
| P0.5 — fix GG-as-sire on 3 lambs (Kelsier is the sire) | `20e7b20` | ✅ Done |
| P0.1 dodge — merge duplicate (same animal, sold to Danny) | `60b9a00` | ✅ Done |
| P0.1 daisy — split duplicates (two different ewes; Little Daisy is from half-tail line) | `29976fc` | ✅ Done |
| P1.2 — Windlestone ewes: missing 5% is East Friesian | `2353de0` | ✅ Done |
| L4 — Charlie: catch-panel puncture (NOT CL), resolved ~2 weeks | `07de324` | ✅ Done |
| P0.6 — tag-31 collision: add tag_color field, validator now keys on (tag,color) | `e8cff46` | ✅ Done |

**Open work — bigger plan-doc phases** (per MANATEE_CREEK_REDESIGN_PLAN.md):

| L# | Item | Status | Commit / file |
|----|------|--------|---------------|
| L5 | export to 26 tabs + --dry-run | ✅ Done | `8820e12` — 25 TSV tabs + Apps Script |
| L6 | google-sheets-sync MCP wired | ⏸ Blocked | needs GCP project credentials |
| L7 | annual eval persistence (data/annual_evals/) | ✅ Done | `384fa47` |
| L8 | investigations -> breeding_policy.referenced_research | ✅ Done | `d3f72fc` |
| L9 | cognitive memory protected entries | ✅ Done | 7 entries in ~/.memory/sheep/ |
| L10 | data/processed/ + parity validator | ✅ Done | `b6c9472` (processed/ gitignored) |
| L11 | 2026 drought cull list | ✅ Done | `d319b84` — data/2026_drought_cull_list.md |
| L12 | docs/NOTEBOOK_CARD_WORKFLOW.md SOP | ✅ Done | `d354c6f` |
| L2 follow-up | BT Twin Ewe 2 + Elsie sm-white triplet | ✅ Done | BT-2 deceased 2026-04-22; Elsie sold 2026-04-26 |

**Still open — require owner input or external setup:**

- **L6** — MCP wiring needs GOOGLE_CLOUD_PROJECT credentials + service account; owner action required to complete the round-trip sheet ↔ JSON sync.
- **P4.1** — `sm-white-ewe-p4` (alive Pen 4, confidence low) — needs owner ID.
- **P4.3** — 7 lambing records with unknown sire (Broken Tail 1-20, Tag 33 1-27, Zara 1-28, Azure 1-29, Gigi 2-5, Tag 31 2-13, OAV 2222 4-30); CLAUDE.md says Pen 4 lambs are all Kelsier, others need confirmation.
- **Owner action from L11** — apply cull/auction decisions from `data/2026_drought_cull_list.md` once you've reviewed; update status / status_date / status_notes per animal.
- **Owner action from L7** — fill in annual eval scores in the Google Sheet (or directly in `data/annual_evals/2026_*_eval.json`); they persist across re-runs.

Findings are grouped by severity. Each item lists the evidence command so a
future session can reproduce. Items mark **STATE** = confirmed gap, **REGRESSION**
= prior fix needs follow-up, or **STALE-CLAIM** = recorded as done but evidence
disagrees.

---

## P0 — Pedigree-integrity errors (block-level)

These are validator ERRORs and pedigree consistency bugs. The
`careful-not-clever` hook should fire on any edit until these are clean.

### P0.1 Duplicate sheep IDs (REGRESSION)
- `id: dodge` appears twice, both `status=alive` — sire/dam refs to "dodge" are
  ambiguous.
- `id: daisy` appears twice — one `status=unknown`, one `status=sold`.
- **Repro:** `python3 -c "import json; d=json.load(open('data/flock_database.json')); ids={}; [ids.setdefault(s['id'],[]).append(s.get('status')) for s in d['sheep']]; [print('DUP:',i,v) for i,v in ids.items() if len(v)>1]"`
- **Fix:** merge or rename. Owner verification required to pick the canonical row.

### P0.2 Today's dam correction is half-applied (REGRESSION — from this session)
After today's commits 3e932a0 + 9d820a0 moved MC08 + samson-daughter-p4 dam to FM:
- `broken-tail.breeding.offspring_ids` still lists `mc08-ram` and `samson-daughter-p4`.
- `broken-tail.notes` still reads "Mother of … MC08 and samson-daughter-p4 (twins by Samson — owner-confirmed 2026-04-24)".
- `fm.breeding.offspring_ids` is missing `mc08-ram` and `samson-daughter-p4`.
- **Fix:** remove the two IDs from `broken-tail.offspring_ids`, update its notes,
  add the two IDs to `fm.offspring_ids`. Then `python3 scripts/validate_flock.py
  --check-references` should still pass.

### P0.3 Broken dam reference
- `charlies-ewe` references `dam_id: nori-line-f2` which does not exist in the database.
- **Repro:** `python3 scripts/validate_flock.py --check-references` → 1 ERROR.
- **Fix:** either create the `nori-line-f2` placeholder record (low-confidence,
  status=unknown, off-property) or null out the dam_id pending owner clarification.

### P0.4 Invalid status enum
- `elsie-triplet-black-ram` has `status: gifted` — not in the allowed
  enum (`alive | deceased | sold | unknown`).
- **Fix:** extend the enum to include `gifted` (it's a real disposition the flock
  uses — git log shows L1 plan added enum tightening but didn't anticipate gifting),
  OR remap to `sold` with `sold_price=0` and a note. Owner preference required.

### P0.5 GG (ewe) listed as sire on 3 lambs (WARNING but pedigree-fatal)
- `gg-daughter-45`, `lara-daughter-46`, `gg-son-094` all have `sire_id: gg`.
- `gg.sex = ewe` — she is the dam, not the sire.
- **Repro:** `python3 scripts/validate_flock.py` → 3 WARNINGs.
- **Fix:** for each lamb, identify the real ram (CLAUDE.md says "All 2026 lambs
  in Pen 4 sired by Kelsier" — likely Kelsier for the GG offspring; Lara's
  daughter sire needs owner confirmation). Swap so `sire_id` points to a ram
  and `dam_id` to gg (or the right ewe).

### P0.6 Tag collision among living sheep
- Tag `31` shared by `tag-31-ewe-p5` (Pen 5) and `tag-31-orange-tf` (Tree Fort).
- Notebook policy: tag uniqueness among living animals.
- **Fix:** owner confirms which animal got retagged; rename one. The Tree Fort
  one is "Orange Tag 31" per CLAUDE.md, so the Pen 5 one likely kept the original
  number — likely the Tree Fort animal needs an alternate tag annotation.

---

## P1 — Validator ERRORs that block clean integrity pass

### P1.1 20 records missing required `confidence` field
- Validator strict mode errors 20 records: `tag-31-ewe-p5`, `tag-02-ewe-p5`,
  `fawn-wool-ewe-p5`, `dodge`, `daisy`, three `elsie-triplet-*`, three
  `windlestone-*`, two `tag-0035-*`, two `tag-31-orange-tf-*`, four `goose-*`.
- **Repro:** `python3 scripts/validate_flock.py | grep "Missing required field"`
- **Fix:** add `"confidence": "medium"` (or `"high"` / `"low"` as appropriate)
  to each. The Windlestone Awassi trio is owner-verified — should be high.

### P1.2 Windlestone breed percentages sum to 95%
- `windlestone-2139`, `windlestone-0056`, `windlestone-0055` each declare
  95% Awassi, no other breed.
- **Fix:** add the missing 5% (likely "Unknown" or owner-stated other breed)
  OR change to 100% if they're full Awassi. The CLAUDE.md pen table says
  "All 3 ewes are 95% Awassi fat-tail" so 95% may be intentional — but the
  validator expects 100% sum. Decide: add 5% Unknown breed entry, or update
  validator tolerance.

### P1.3 Image reference broken
- `lara` record references `IMG_0661` which does not exist on disk.
- **Repro:** `python3 scripts/validate_flock.py --check-images`
- **Fix:** locate the actual notebook image for Lara, update the reference, or
  remove the ref if the photo is lost.

---

## P2 — Master plan loose ends (status vs MANATEE_CREEK_REDESIGN_PLAN.md)

The plan documents L1–L12 loose ends. Reverified 2026-05-13:

| L# | Item | Plan-doc status | Current state | Verdict |
|----|------|-----------------|---------------|---------|
| L1 | `pens.*` zombie sub-tree | "members: 0" | All 9 pens populated (pen_1=12, pen_3=7, pen_4=12, pen_5=8, pen_6=4, tree_fort=6, chicken_coop=1, goose_pen=0) | **DONE** |
| L2 | April 6 auction partial | 3/5 sold | 4/5 reconciled; **BT Twin Ewe 2 White not located in DB** | **PARTIAL** |
| L3 | Windlestone Kat/Dorper ram | "verify in JSON" | Angus in Pen 5, breed 50%K/25%D/25%Aw, alive | **DONE** (placed Pen 5 not Pen 2 — owner moved him) |
| L4 | Charlie catch-panel puncture vs CL | "needs dated entry" | Charlie's notes still mention "abscess" with no "catch-panel" or "puncture" correction | **NOT DONE** |
| L5 | Export to 26 tabs | "7 tabs covered" | not re-checked this session — owner to confirm | **UNKNOWN** |
| L6 | google-sheets-sync MCP wiring | "documented, not wired" | skill exists; no scripts/sync_sheet_to_json.py | **NOT DONE** |
| L7 | Annual eval persistence | "no JSONs" | `data/annual_evals/` does not exist | **NOT DONE** |
| L8 | Investigation tie-in | "orphans" | `breeding_policy.referenced_research` is MISSING; 11 investigation files in `data/investigations/` | **NOT DONE** |
| L9 | Cognitive memory empty | "tree {}" | not re-checked this session (needs ken/) | **UNKNOWN** |
| L10 | `data/processed/` empty | "no processed images" | directory does not exist at all | **NOT DONE** |
| L11 | Drought cull list | "not landed" | no `data/*cull*` file | **NOT DONE** |
| L12 | Notebook card workflow doc | "transcription continues" | `docs/NOTEBOOK_CARD_WORKFLOW.md` does not exist | **NOT DONE** |

---

## P3 — Pen-assignment hygiene

### P3.1 Six alive sheep have no pen
- `kaladin`, `dodge` (×2 — see P0.1), `cocoa`, `daisy-of-sugar`, `loki`.
- CLAUDE.md notes Cocoa/Loki/Daisy-of-Sugar are off-property (Danny's animals,
  pedigree-only). Kaladin's pen is open. dodge duplicate compounds this.
- **Fix:** add an explicit pen value for on-property sheep (or a marker
  like `"pen": null` + `"on_property": false` for Danny's animals — that
  pattern is in use for Niece).

### P3.2 Two sold sheep still tagged with a pen
- `tag-0033-twin-ram-1` (sold 2026-04-06) and `tag-0033-twin-ram-2` (sold
  2026-04-26) both still have `pen: Pen 1`.
- **Fix:** null the `pen` on sold animals; alternatively, the plan's exit
  criterion is "no deceased/sold sheep in active pens".

---

## P4 — Data-source freshness

### P4.1 Low-confidence records that never received owner verification
24 records carry `confidence: low`. Many are historical (deceased, "likely
hurricane casualty"); some are unresolved current animals:
- `sm-white-ewe-p4` — **alive, Pen 4, confidence low** — needs owner ID
  (visible in 2026-04-24 photo set).
- `daisys-daughter-1`, `tag-35-ewe`, `ext-lamb-27`, `ext-lamb-10`,
  `banana-split`, `banana-split-baby`, `fleecity`, `stew`, `fm2` —
  `status: unknown`. Decide alive/deceased/sold for each at next owner sync.
- **Repro:** `python3 -c "import json; d=json.load(open('data/flock_database.json'));
  [print(s['id'], s.get('status')) for s in d['sheep'] if s.get('confidence')=='low']"`

### P4.2 Twelve `[UNCLEAR]` markers still in DB
Includes 1 breed `primary` field (`"primary": "[UNCLEAR]"`), a tag number for
Gigi's 2025 ram ("Tag 09 [UNCLEAR]"), 5+ lambing-record sires marked
`"[UNCLEAR]"`. Each is an open question waiting on a notebook re-read or
owner sync.
- **Repro:** `grep -n "\[UNCLEAR\]" data/flock_database.json`

### P4.3 Lambing-record sire holes
Seven 2026 lambing records have an unknown or blank sire:
- 2026-01-20 dam=Broken Tail (Pen 2)
- 2026-01-27 dam=Tag 33 (Pen 1)
- 2026-01-28 dam=Zara (Pen 3)
- 2026-01-29 dam=Azure (Pen 2)
- 2026-02-05 dam=Gigi (no pen)
- 2026-02-13 dam=Tag 31 (no pen)
- 2026-04-30 dam=null pen=null (the OAV 2222 record from commit 8e5ae59 may have a malformed entry — verify)
- **Fix:** owner sync. Most are likely Kelsier (Pen 4 cohort) or Sir Loin/Charlie (Pen 3).

---

## P5 — Process / docs gaps

### P5.1 No HANDOFF.md
- Repo has no `HANDOFF.md` files anywhere. CLAUDE.md mandates them per the
  Handoff Protocol (ken/CLAUDE.md §Handoff Protocol).
- **Fix:** when next significant work starts, write `HANDOFF.md` at repo root
  with what-was-done / what's-next.

### P5.2 No `unfinished_tasks.md` baseline before this audit
- This document is the first one. Going forward, update it after each
  multi-session campaign so the gap list stays current.

### P5.3 No NOTEBOOK_CARD_WORKFLOW.md (L12)
- Mom keeps photographing notebook cards. There's no SOP for converting a
  fresh photo → JSON diff → review → commit. Each session reinvents it.

---

## Recommended next sweep (one commit each)

Ordered by smallest-risk-to-largest:

1. **Fix P0.2** — finish today's MC08/samson-daughter-p4 dam correction by
   editing `broken-tail.offspring_ids`, `broken-tail.notes`, and
   `fm.offspring_ids` for bidirectional consistency.
2. **Fix P0.1** — resolve `dodge` and `daisy` duplicates (owner pick).
3. **Fix P1.1** — add `confidence` field to the 20 missing records (most
   are pen-roster animals already known to high confidence).
4. **Fix P0.6** — resolve tag-31 collision.
5. **Fix P0.4** — decide on `gifted` enum policy.
6. **Fix P3.2** — null pens on sold sheep.
7. **Fix L4** — add the catch-panel puncture note to Charlie.
8. **Fix P0.3, P0.5** — broken `nori-line-f2` ref + GG-as-sire mis-attributions.
9. **Then** start on plan Phase 2 (drought cull list) since the JSON is now clean.

Validator must return `0 errors, 0 warnings` after sweep 1–6 before moving
on to plan phases.

---

*Soli Deo Gloria.*
