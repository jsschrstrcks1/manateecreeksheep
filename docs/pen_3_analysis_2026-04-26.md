# Pen 3 — Per-Animal Analysis

**Reviewer:** Claude (manual review, not script-generated)
**Date:** 2026-04-26
**Source records:** `data/flock_database.json` as of commit `57170cf`
**Method:** read each Pen 3 record in full, then write each finding by hand. Honest about what's in the record vs. what's inferred. Where I don't know, I say so.

Pen 3 contains 9 sheep records: 5 adults (2 rams + 3 ewes), 3 surviving lambs, and 1 lamb deceased 2026-04-22 (parasites).

---

## 1. `charlie-ram` — "Charlie" — MC20

**Quick read:** Dominant Pen 3 ram. Health record is clean and well-sourced (IMG_0651). Pedigree is null. Weight field disagrees with the only measured weight in the record. Owner-flagged action item: "Needs to move to a new pen but has not been moved yet" — still in Pen 3.

### What the record says

- Tag `MC20` (yellow); `mc_tag: MC20`. No secondary tags.
- Sex `ram`, status `alive`, pen `Pen 3`, confidence `high`.
- Breed: 50% Katahdin / 25% BHD / 12.5% ABB / 12.5% Wiltshire Horn → sums to 100%, hair 100%/wool 0%. Math is clean.
- color_markings: "White with black spots, black horns" — matches the photo and the visual_id block I added.
- visual_id block is present and was just added (commit 94035dd).

### Issues I'm seeing

1. **Weight contradiction.** Top-level `weight_lbs: 232.2` with `weight_estimated: true`. But the abscess-treatment notes record an actual measured weight of **108.2 lb** on 2026-02-28 (when he was lanced and weighed for the Nuflor dose). Two readings of the same field disagree by a factor of 2. The 108.2 is a real measurement; the 232.2 is some estimate. I don't know which the breeding scripts use. **Worth reconciling — pick the measured value as primary, keep the estimate (if wanted) in `measurements{}`.**

2. **DOB null.** No `dob` and no `dob_approximate` flag. Notes don't give a birth date either. Owner may know an age range from the purchase date.

3. **Pedigree null.** `sire_id: null`, `dam_id: null`. The free-text notes describe his lineage in detail ("BHD x Nori offspring bred to Katahdin... Charlie bought from friend Charlie who bred BHD to Nori, kept babies, bred to Katahdin"). The breed math (50K/25BHD/12.5ABB/12.5WH) is consistent with `(50% ABB / 50% WH dam) → ½-BHD daughter → that daughter × Katahdin`. So the "Nori" in his lineage *could* be the Pen 3 Nori — but it could also be a same-named ewe from the seller's farm. **Don't infer; ask.** Either way, the prose-only pedigree means breeding scripts that walk `sire_id`/`dam_id` skip him.

4. **Two parallel FAMACHA arrays inside `health{}`.** The record carries both `famacha_history` (8 entries, IMG_0651-sourced) and `famacha_scores` (7 entries, slightly different format and dates like `"2-13-26"` vs ISO `"2026-02-13"`). They overlap and don't conflict, but they're redundant. This same dual-array pattern appears in several other Pen 3 records — see pen-level findings.

5. **Action item buried in notes.** "Sexually aggressive, dominant ram in Pen 3. Likely siring lambs in this pen. **Needs to move to a new pen but has not been moved yet.**" This is a management decision the record is tracking but never elevates out of free-text. With Charlies Farm Ewe noted as "possibly a sibling" (same breed comp), and her existing lamb MC-2602 already attributed to Charlie as sire, the inbreeding risk is real and active. Worth elevating to a structured field or a pen-level action list.

6. **CL monitoring note.** "Monitor for CL" is in the notes. The 2-28 record clarifies the abscess was confirmed NOT CL ("catch-panel puncture"), which the visual_id-doc-pass note captured. Internal-consistent — just noting the watch flag is still there.

### What's solid

- Health record is well-sourced (IMG_0651 throughout), full FAMACHA + treatment + vaccination history Feb–Apr 2026.
- All FAMACHA scores 1–2; resolved abscess; no parasite flags.
- visual_id block accurate to the photo per owner confirmation.
- Tag, breed math, sex, status, confidence enums all valid.

---

## 2. `merrie` — "Merrieweather" — 00016

**Quick read:** Solid health record with three IMG_0659-sourced FAMACHA checks all 1–2. Pedigree resolves cleanly (smore × half-tail, both in DB). Weight is contradictory across three places in the record. Offspring list is empty despite his being a breeding ram in a pen with four lambs.

### What the record says

- Tag `00016`; `mc_tag: null`. Aliases `["Merrie", "Merrieweather"]`.
- Sex `ram`, status `alive`, pen `Pen 3`, confidence `high`, `last_verified: 2026-02-16`.
- DOB `2023-01-14` with `dob_approximate: true`. (Yearling-into-2yo, ~3¼ yr now.)
- Sire `smore` (S'More, 100% Cracker, deceased ram — exists in DB), dam `half-tail` (deceased ewe — exists in DB). Both refs resolve.
- Breed: 50% Cracker / 28.125% St Aug / 12.5% Katahdin / 6.25% BBB / 3.125% White Dorper → sums to 100%. Hair 50% / wool 50%, but `coat_observed: "hair"` (which is the field worth trusting — he reads hair). Math clean.
- color_markings: "Brown and Tan".
- breeding.is_breeding_animal: true; `offspring_ids: []`.
- visual_id block present (just added), notes him as the largest animal in the pen per owner.

### Issues I'm seeing

1. **Weight is inconsistent across three places in the record.**
   - `weight_lbs: 200`, `weight_estimated: false`
   - `measurements.calculated_weight: 99.2` from `date: "2023-2024"`, with prior measurements of 30 and 31 inches in 2025
   - `notes` field still says "Weight calculator: 99.2lbs"
   - `visual_id.size`: I wrote "DB weight calc of ~99 lb is from 2023 birth-weight projection and is STALE" — but I missed that there's already a top-level `weight_lbs: 200` flagged as not-estimated, which would be more recent. So my visual_id text is **slightly wrong**: the 99.2 lb number is the calculator value, but the record's primary weight is 200 lb. Owner says he's the biggest animal in Pen 3 (i.e. ≥225 lb). So even 200 looks low.
   - **Recommendation:** weigh him; reconcile the three sources to a single primary `weight_lbs` with date.

2. **`offspring_ids` empty despite being a breeding ram.** Pen 3 has four lambs born this season (MC-2602, MC-2604, MC-2605, MC-2601). The notes on every lamb say "Sire probably Charlie (dominant) but could be Merrie." MC-2602's sire_id is committed to `charlie-ram`. The other three lamb records have `sire_id: null`. So Merrie's sire-status is literally "could be" for three lambs and "probably not" for one. Even given the uncertainty, his `offspring_ids: []` is at least worth a comment ("possible sire of MC-2604/2605/2601; not confirmed").

3. **`status_date: null` and `status_notes: ""`** — these are fine for a living, healthy animal, but the record carries them as empty strings rather than absent. Cosmetic.

4. **Two parallel FAMACHA arrays again.** `famacha_scores` (3 entries) and `famacha_history` (5 entries). Same dual-array oddity as Charlie.

5. **`health.notes`** has only one entry, and it's a tag confirmation, not health content. Health *content* is in the famacha arrays. Internal-consistent.

### What's solid

- Pedigree refs resolve. Sire is a recorded ram, dam is a recorded ewe, so the validator's sex check passes for both.
- FAMACHA all 1–2, no treatments, no parasite issues, CDT vaccinated 3-9-26 (twice — likely the same shot recorded by two pipelines, see pen-level finding).
- Breed math sums to 100%; coat_observed field set.
- Source refs include three notebook images (IMG_8622, IMG_8630, IMG_8641).

---

## 3. `charlies-farm-ewe-p3` — "Charlies Farm Ewe" / "White Belly Ewe" — MC16

**Quick read:** Healthy lactating ewe. Confidence is "medium" because the record itself flags pedigree uncertainty. The "possible sibling to Charlie" inbreeding note is real and now active — her current lamb MC-2602 has Charlie as sire. Pedigree is null and offspring list is empty despite that confirmed mother-of relationship.

### What the record says

- Tag `MC16` (yellow); `mc_tag: MC16`. Alias `["White Belly Ewe"]`.
- Sex `ewe`, status `alive`, pen `Pen 3`, confidence `medium`.
- Breed: 50% K / 25% BHD / 12.5% ABB / 12.5% WH → 100%, hair 100%. Identical breed comp to Charlie, which is the basis of the inbreeding flag.
- color_markings: "White Belly, multi color".
- weight_lbs: 155, weight_estimated: true.
- visual_id present.

### Issues I'm seeing

1. **`confidence: medium` is appropriate** because the notes themselves say "Nori line — one of Noris offspring, daughters, or granddaughters. Exact generation UNCLEAR." Good — that's honest.

2. **Pedigree null.** `sire_id` and `dam_id` are both null even though the notes say she's somewhere in the Nori line. If she's a Nori-line descendant, that means our Pen 3 Nori (or a same-named ewe from Charlie's farm) is in her ancestry. **Don't guess** which.

3. **DOB null** + no `dob_approximate` flag. The record has no age data at all.

4. **Inbreeding risk is documented but not structured.** Notes: "Same breed as Charlie — possible siblings. Inbreeding concern if bred to Charlie." MC-2602's record commits Charlie as sire. So:
   - If she and Charlie *are* siblings: MC-2602's coefficient of inbreeding is ~0.25 (full-sib mating).
   - If they share a grandparent (Nori): COI is ~0.0625 (first-cousin) or so.
   - If they're unrelated despite same breed comp: COI ~0.
   The record carries this as prose; the breeding scripts can't see it. **Not a fix-now item, but worth noting.**

5. **`offspring_ids` empty** despite MC-2602's record listing her as dam. Same gap as Merrie — should at minimum list `["charlies-farm-ewe-baby-p3"]`.

6. **Two parallel FAMACHA arrays again.** Same pattern.

### What's solid

- FAMACHA 1 across all checks Jan–Apr 2026. CDT vaccinated.
- visual_id matches photo (mid-right standing, lactating, hanging udder).
- Tag, breed math, sex, status enums valid.
- Source refs cited (IMG_0652).

---

## 4. `broken-tail` — "Broken Tail" / "Iron Lady" — MC-15

**Quick read:** Long pedigree story, well-documented offspring history, FAMACHA clean. Two structural issues: (a) `secondary_tags: ["0029"]` collides with Nori's primary tag — the in-record note "Prior tag 0029 moved to secondary_tags" suggests it's stale; (b) `breeding.is_breeding_animal: false` despite obviously being a breeding animal — she just had twins this season.

### What the record says

- Tag `MC-15`; `secondary_tags: ["0029"]`; `mc_tag: MC15`. Aliases `["Bt", "BT"]`.
- Sex `ewe`, status `alive`, pen `Pen 3`, confidence `high`, `last_verified: 2026-02-16`.
- DOB `2018-01-18`, `dob_approximate: true`. ~8 yrs old.
- Sire `sir-loin` (deceased ram, in DB), dam `half-tail` (deceased ewe, in DB). Both resolve.
- Breed: 65.625% St Aug / 28.125% K / 6.25% BBB → 100%. Hair 100%. Math clean.
- color_markings: "White".
- weight_lbs: 225 (no `weight_estimated` flag set — defaults to whatever).
- offspring_ids: 6 entries — `bt-lamb-2023`, `dodge`, `mc08-ram`, `samson-daughter-p4`, `broken-tail-twin-ewe`, `broken-tail-twin-ewe-2`. All six exist in DB. (One of these — MC-2601 — is now deceased.)
- visual_id present (just added).

### Issues I'm seeing

1. **Tag-0029 conflict.** Her `secondary_tags: ["0029"]` matches Nori's *primary* tag. Inside her own `health.notes`: *"Prior tag 0029 moved to secondary_tags."* That suggests **the 0029 was hers historically, then she got MC-15, and Nori inherited 0029** — or possibly the 0029 in her secondary list is a stale note that was never cleaned up. Owner deferred this fix to the index-card review (verbatim 2026-04-26: "I don't know what the current tags are for either BT or Nori, but the index card photos should have that data"). **Not fixing in this analysis — just confirming the conflict is real and not a copy-paste error.**

2. **`breeding.is_breeding_animal: false` is wrong.** She has six recorded offspring including two from this season. The flag should be `true`. Likely a stale init value.

3. **`breeding.lambing_records: []` is empty** even though the notes say "Lambed 2026-01-20 (twins)" and the offspring list contains the two twins. The lambing-record block was never populated.

4. **Weight measurement basis is unclear.** `weight_lbs: 225` but no `weight_estimated` flag (so we can't tell if measured or projected). If this is the breeding-page calculator, it's old.

5. **Notes contain a stale pen claim.** Inside the long `notes` blob: *"In pen 5 (Rocky group) per notebook."* and then later *"Pen 3 as of 2026."* Both are in the same notes string. Pen 3 is correct now per `pen` field; the Pen 5 fragment is preserved history. Cosmetic, but a future reader could be confused.

6. **Two parallel FAMACHA arrays again.** Same dual-array.

7. **Visual_id text I wrote** said "Often lies near her surviving brown twin MC-2605." That's an extrapolation from the photo, not from the owner's testimony. **Soft confidence — not a hard tell.** The photo shows her near the white twin (now deceased), not the brown twin.

### What's solid

- Pedigree refs resolve, parents are correct sex.
- Six offspring, all referenced sheep exist in DB.
- FAMACHA 1 throughout, no parasite flags personally (despite both her twins having or contracting issues).
- Source refs to IMG_0654.
- Owner colorful description preserved verbatim ("Gentle and sturdy matriarch... Crappy name for a phenomenal sheep.")

---

## 5. `nori` — "Nori" — 0029

**Quick read:** Healthy badger-pattern ewe. Has more aliases and prior tags than most records. Two structural issues: (a) `health.famacha_scores: []` is empty while `health.famacha_history` has 7 entries — the canonical-array confusion shows up most starkly here; (b) `offspring_ids` lists her two older sons but not her current 2026 lamb MC-2604.

### What the record says

- Tag `0029`; `mc_tag: null`. Aliases `["Tag 29", "No", "Tag 21"]`.
- Sex `ewe`, status `alive`, pen `Pen 3`, confidence `high`, `last_verified: 2026-02-16`.
- DOB `2023-02-01`, `dob_approximate: true`. ~3 yrs old.
- sire_id null, dam_id null. Notes carry prose pedigree: "Sire: 100%ABB, Dam: 100%WH."
- Breed: 50% ABB / 50% WH → 100%. Hair 100%. Math clean.
- color_markings: "Badger".
- weight_lbs: 139 (no `weight_estimated` flag).
- offspring_ids: `["nori-son", "eclipse"]`. Both exist (NoriSon deceased, Eclipse alive but pen=None).
- visual_id present.

### Issues I'm seeing

1. **`health.famacha_scores: []` empty, `health.famacha_history` has 7 entries.** This is the clearest example of the dual-array problem — one branch is empty, the other is populated. Any consumer reading `famacha_scores` will think Nori has zero recorded scores. Functional bug if any script uses that field.

2. **`offspring_ids` is missing MC-2604.** Her 2026 lamb (`nori-baby-p3`) is not in her offspring list, even though that lamb's `dam_id` correctly points back to `nori`. Bidirectional reference is broken on Nori's side.

3. **Pedigree null** despite the prose stating sire and dam breed compositions. No actual sheep IDs — possibly because her parents weren't on this farm. That's defensible; just noting.

4. **Aliases include "Tag 21"** — the notes confirm "tag 21 (tag lost)". So the record's tag history is `21 → 0029 (current)`. That's traceable. Good.

5. **The 0029 tag is unique among living sheep as a primary tag** (Broken Tail's `tag` is `MC-15`; she only has `0029` in `secondary_tags`). So the validator's "tag uniqueness among living" check passes for primaries.

6. **"Knot under chin"** noted 2026-02-26, monitored, never escalated. Visible on her 2026-04-09 check ("eyes good"). Worth a follow-up palpation, but not a current health issue per the record.

7. **Notes still say "In pen 4. ... Pen 3."** Same pen-history-in-prose pattern as Broken Tail. The `pen` field is `Pen 3`, which is current. Cosmetic.

### What's solid

- Tag, breed math, sex, status enums all valid.
- 6 recorded FAMACHA-history entries, all 1–2.
- Source refs to IMG_0641, IMG_0642, IMG_0657.

---

## 6. `charlies-farm-ewe-baby-p3` — "Charlies Farm Ewe Baby" — MC-2602

**Quick read:** Oldest lamb in Pen 3 (born 2025-12-06). Healthy. The record has the canonical structural issue of all four 2026 lamb records: empty `breed_composition.percentages`. Sire is committed to Charlie, which means inbreeding has occurred if dam and sire are siblings (record acknowledges that risk).

### What the record says

- Tag `MC-2602` (green); `mc_tag: MC2602`. Notes flag a prior `MC2609` that was scratched/disregarded.
- Sex `ewe`, status `alive`, pen `Pen 3`, confidence `medium`.
- DOB `2025-12-06`. (~4.7 mo as of 2026-04-26.)
- sire_id `charlie-ram` (resolves), dam_id `charlies-farm-ewe-p3` (resolves). Both correct sex.
- breed_composition: `percentages: {}`, `coat_type: "unknown"`. Empty.
- color_markings: "Big brown, white tip on tail, 2 white socks, white on crown, front legs all brown" — detailed, useful.
- visual_id present.

### Issues I'm seeing

1. **Empty breed_composition.** This is the most fixable thing in the record. If sire is Charlie (50K/25BHD/12.5ABB/12.5WH) and dam is CFE-p3 (same comp), then the lamb's breed is identical: 50K/25BHD/12.5ABB/12.5WH, hair 100%. The math is trivial and deterministic given the parent records. **The only reason not to commit it is the "Sire probably Charlie but could be Merrie" hedge in the lamb's notes** — but the structured `sire_id` field already commits to Charlie. If we trust `sire_id`, we should compute the breed comp.

2. **Confidence `medium` is right** because of the sire-uncertainty hedge in the notes.

3. **Inbreeding risk is real if dam/sire share parents.** Already discussed under #3. The record itself doesn't carry a coefficient-of-inbreeding field; that's a flock-wide gap, not Pen 3 specific.

4. **Notes embed pen rotation history** — "MC2602 green tag (was MC2609)" — useful tag traceability.

5. **Two parallel FAMACHA arrays.** Same pattern.

### What's solid

- Sire and dam refs resolve and have correct sex.
- 7 sourced FAMACHA entries, all 1–2 — including the 2026-04-09 "Booster, eyes good." She's not on the parasite watchlist.
- Color markings detailed enough to ID her in a photo.
- DOB present and exact (notebook-derived).

---

## 7. `broken-tail-twin-ewe` — "Broken Tail Twin Ewe (brown)" — MC-2605

**Quick read:** Severe parasite emergency 2026-04-09 (FAMACHA 5, treated). Twin sister died 2026-04-22 from the same disease class. This lamb is on the weak-resistance watchlist. Sire is null. Owner explicitly chose to keep her despite the FAMACHA 5.

### What the record says

- Tag `MC-2605` (green); `mc_tag: MC2605`. Notes mention `MC2625` as a lost-tag duplicate.
- Sex `ewe`, status `alive`, pen `Pen 3`, confidence `medium`.
- DOB `2025-12-31`. (~3.8 mo as of 2026-04-26.)
- sire_id `null`, dam_id `broken-tail` (resolves).
- breed_composition: `percentages: {}`, empty.
- color_markings: "Brown & white".
- **`weak_resistance: true`** at the top level (also lambda).
- `notes_history` carries the explicit owner decision: "KEPT: Owner clarified BT_WHITE twin (MC-2601) goes to auction, brown twin (MC-2605) stays despite 4-9 FAMACHA 5."
- visual_id present.

### Issues I'm seeing

1. **FAMACHA 5 on 2026-04-09** with eyes white — a parasite emergency. Treated same day with 1 cc Iron + VB + Ivermectin. Then her twin sister died from parasites 13 days later (2026-04-22). **MC-2605 should be on the high-priority recheck list right now.** No FAMACHA entry in the record after 2026-04-09 — last 17 days are unobserved.

2. **Sire null.** Notes say "Sire probably Charlie (dominant) but could be Merrie." Same hedge as her sister. If the assumed sire is Charlie, she'd be inbred with her dam Broken Tail through Half Tail (Broken Tail's dam) — *but only if Charlie has Half Tail in his ancestry, which is not stated.* I don't know Charlie's pedigree because his sire/dam are null. So inbreeding speculation here is just speculation.

3. **Empty breed_composition.** Same pattern as MC-2602. Without sire confirmation, breed math is undefined. Until owner commits a sire, `{}` is the honest state.

4. **`weak_resistance: true`** is set at the *top level* of the record, not inside `health{}`. The validator and the parasite-resistance scorer read `health.weak_resistance` (per the script's source). So this flag is in the wrong place. **The flag is there, but in a location that probably no consumer reads.**

5. **Two parallel FAMACHA arrays again.**

6. **Notes-history is the right way to carry the "kept despite FAMACHA 5" decision.** Good record-keeping; nothing to fix.

7. **`broken-tail.offspring_ids` does include MC-2605** — bidirectional ref works in this direction.

### What's solid

- Health record well-sourced (IMG_0655) — 5 famacha_history entries including the FAMACHA-5 emergency, treatment recorded with dose detail.
- DOB exact, dam ref resolves with correct sex.
- Owner-decision history captured in notes_history (the right schema for it).

### Health flag — needs current attention

> **MC-2605 had FAMACHA 5 on 4-9-26 and her twin died from parasites 13 days later. The DB has no observation on her since 4-9. She should be re-checked today (2026-04-26).**

I am not making any clinical recommendation — just reporting what the record says.

---

## 8. `broken-tail-twin-ewe-2` — "Broken Tail Twin Ewe 2 (White)" — MC-2601 — **DECEASED 2026-04-22**

**Quick read:** Just-deceased lamb. The record now correctly carries `status: deceased`, `status_date: 2026-04-22`, `cause_of_death: parasites` (commit 94035dd this morning). The record still has several stale auction-related fields from when she was being prepped to sell, which never happened — death intervened. Worth cleaning up.

### What the record says

- Tag `MC-2601`; `mc_tag` not set. Notes mention "(2x) MC-2610 + MC-2601" — double green tag from the notebook card, with the first number obscured.
- Sex `ewe`, **status `deceased` (CORRECT)**, **status_date `2026-04-22` (CORRECT)**, pen `null` (correct).
- DOB `2025-12-31`. (~3.8 mo at death.)
- sire_id null, dam_id `broken-tail`.
- breed_composition: `percentages: {}`, empty.
- color_markings: "White ewe".
- **`cause_of_death: "Parasites — owner-reported 2026-04-26."` (CORRECT)** — added in this branch's first commit.
- visual_id present, includes `deceased_note`.

### Issues I'm seeing — pre-existing fields that contradict the new deceased status

1. **`status_notes: "Auction Sunday April 6, 2026"`** — stale. April 6 auction never happened, owner already corrected that history once (see notes_history). Should be cleared or replaced with a death note.

2. **`scheduled_auction: "2026-04-26"`** — stale. The April-26 auction is today, and she's not going. Should be cleared.

3. **`notes_history` entry from 2026-04-22** says: *"STATUS CORRECTION: was marked sold prospectively for 4-6 auction that did NOT execute. Back to alive. Scheduled for 4-26-26 (coming Sunday) auction per owner."* That note is a dated record of an earlier correction; it's historically useful but its claim ("Back to alive. Scheduled for 4-26 auction") is now wrong because she died. **Don't delete the history — the right move is to add a *new* dated entry: "2026-04-22: Died of parasites. Auction did not occur."** This preserves the trail.

4. **`health.famacha_history` last entry says 2026-04-09 "Booster, eyes good (pre-auction)".** Then she died of parasites 13 days later. That's a fast crash from FAMACHA 1–2 to dead. Either (a) the 4-9 read was wrong, (b) something acute happened between 4-9 and 4-22, or (c) parasitism here was not eye-blanching anemia (could be something else, like coccidiosis). **I'm not making a clinical claim.** Just noting that the FAMACHA series and the cause-of-death don't tell a smooth story together — worth a more detailed cause note when the owner has time.

5. **Inside the `health.notes` block** there's a remnant string: *"Sold 4-15-26 auction."* — also stale. Both auction-related strings live inside the source-quoted note, so editing them risks rewriting source. Leave the source note; add a corrective entry.

6. **breed_composition empty** — same lamb pattern, no longer fixable post-death without a tissue sample. Acceptable to leave.

### What's solid

- Death status, date, cause, and pen=null are all set correctly.
- visual_id captures her as the last-known photo while alive.
- Dam ref resolves; Broken Tail's offspring_ids correctly includes her.
- Sex enum, status enum, confidence all valid.
- DOB exact.

### Suggested cleanup (separate, careful, in another commit)

- Clear `status_notes` (or replace with "Died 2026-04-22 of parasites.").
- Clear `scheduled_auction`.
- Add a 2026-04-26 entry to `notes_history`: "Died 2026-04-22 of parasites. Auction did not occur. Prior scheduled-auction fields cleared as stale."

---

## 9. `nori-baby-p3` — "Nori's Baby Ram (Pen 3)" — MC2604

**Quick read:** Borderline parasite-watch lamb. **FAMACHA 3 on 2026-04-09** — eyes "med." Same generation as MC-2601 (deceased) and MC-2605 (FAMACHA 5 watch). Same lambing season, same pen, same parasite environment. Dam-side reference is good, sire is null.

### What the record says

- Tag `MC2604` (green); `mc_tag: MC2604`. Notes: green tag was applied but "PULLED OUT" (later restored, per visual_id usage).
- Sex `ram`, status `alive`, pen `Pen 3`, confidence `medium`.
- DOB `2026-01-10`. (~3.5 mo.)
- sire_id null, dam_id `nori` (resolves).
- breed_composition: `percentages: {}`, empty.
- color_markings: "Brown & white mottled, full white tail, white on top of ears, white blaze".
- visual_id present.

### Issues I'm seeing

1. **FAMACHA 3 on 2026-04-09** ("Eyes med."). FAMACHA 3 is the borderline-monitor zone per the project's CLAUDE.md ("Score 3: Pink — borderline, monitor closely"). Last observation in the record. With his half-sister MC-2601 dead from parasites and his pen-mate MC-2605 hitting FAMACHA 5 on the same day, this lamb is in a high-risk cohort that hasn't been re-checked since 4-9.

2. **Sire null + missing offspring entry on Nori.** As noted under Nori, MC-2604 is missing from `nori.offspring_ids` even though his own `dam_id: nori` is correctly set.

3. **breed_composition empty.** Like the other lambs.

4. **Notes call him "0029/Noris Baby"** — that's a stale aliasing pattern from when Nori was being identified by tag 0029. Functional duplicate of the dam_id field; not harmful.

5. **`description` field at the top level** carries "Brown + white mottled. Full white tail. White on top of ears. White blaze." — duplicates `color_markings`. Both lamb records (MC-2602 and MC-2604) have this `description` duplication. Cosmetic.

6. **Two parallel FAMACHA arrays again.**

### What's solid

- Health record well-sourced (IMG_0658).
- DOB exact, dam ref resolves.
- Sex, status, confidence enums valid.
- The FAMACHA-3 read on 4-9 is recorded honestly and flagged in the inline notes ("track").

### Health flag — needs current attention

> **MC-2604 was FAMACHA 3 on 4-9 and is in the same cohort as a parasite-deceased lamb (MC-2601, 4-22) and a FAMACHA-5 lamb (MC-2605, 4-9). No re-check in the record since 4-9. Worth a fresh FAMACHA today.**

---

## Pen-level findings

These cut across animals and aren't worth duplicating per-record:

### A. Dual-array FAMACHA schema

Every Pen 3 health record carries **two parallel arrays**: `health.famacha_history` (more entries, ISO dates, IMG_0XXX-sourced) and `health.famacha_scores` (fewer entries, US-style dates like `"2-13-26"`, no source). They overlap but don't conflict. This appears to be two pipelines writing to the same record under different schema versions. **Not Pen 3-specific** — likely affects the whole DB. The validator doesn't catch it because both arrays are valid JSON. A future cleanup pass could pick a canonical array name and merge.

### B. Duplicate vaccination entries

Each adult's `health.vaccinations` for the 2026-03-09 CDT shot is recorded **twice** — once without source, once with source `IMG_0651`/`0652`/`0654`/`0657`/`0659`. The same shot, recorded by two pipelines. Not Pen 3-specific.

### C. Empty `breed_composition.percentages` on all four lamb records

`charlies-farm-ewe-baby-p3`, `broken-tail-twin-ewe`, `broken-tail-twin-ewe-2`, `nori-baby-p3` — all carry `percentages: {}` and `coat_type: "unknown"`. For MC-2602 the math is deterministic given the committed sire_id (`charlie-ram` × `charlies-farm-ewe-p3` → 50K/25BHD/12.5ABB/12.5WH). The other three have null sire_ids. Until owner commits a sire, the empty percentages are honest. **For MC-2602 specifically, the breed comp could be filled in.**

### D. Bidirectional pedigree references are inconsistently maintained

- `charlies-farm-ewe-p3.offspring_ids` doesn't list MC-2602, even though MC-2602's `dam_id` points to her.
- `nori.offspring_ids` doesn't list MC-2604, even though MC-2604's `dam_id` points to her.
- `broken-tail.offspring_ids` *does* list both MC-2605 and MC-2601 — this side works.

So child→parent refs are reliable; parent→child refs are spotty. Any consumer that walks parent→child (breeding tools listing "ewe X's lambs this season") will under-report.

### E. Tag-0029 conflict

Nori has primary tag `0029`. Broken Tail has `secondary_tags: ["0029"]` plus an in-record note saying "Prior tag 0029 moved to secondary_tags." The most likely truth is BT used to wear 0029, the tag came off, BT got MC-15, and Nori (separately) got 0029. But that's an inference — **owner deferred the fix to the index-card review.**

### F. Three lambs in the same cohort with parasite issues; one dead

Three of the four 2026 Pen 3 lambs from Broken Tail and Nori have parasite findings:
- MC-2601 (white twin) — DEAD 2026-04-22, parasites
- MC-2605 (brown twin) — FAMACHA 5 emergency 2026-04-09, treated, kept
- MC-2604 (Nori's baby) — FAMACHA 3 borderline 2026-04-09, "watch"
- MC-2602 (CFE's baby) — FAMACHA 1 throughout, no issues

The cohort divides cleanly along dam lines: Broken Tail's twins both crashed; Nori's lamb is borderline; only Charlies Farm Ewe's lamb is clean. **Three of four lambs in this pen are in a parasite-pressure window with no FAMACHA observation since 2026-04-09 (17 days ago).** This is a record-status observation — not a clinical recommendation.

### G. Charlie's pen-rotation action item

Buried in Charlie's notes: *"Needs to move to a new pen but has not been moved yet."* The notes also flag inbreeding risk with Charlies Farm Ewe (possible siblings, same breed comp). Not modeled as a structured action; lives only in prose.

### H. Validator status

After all my Pen 3 work this branch: **21 errors, 7 warnings — same as baseline before I started.** No Pen 3 record is on the validator's error list. The validator doesn't catch any of A–G above, which is why this manual analysis has value.

---

## Summary by animal

| Sheep | Health | DB integrity issues found |
|---|---|---|
| `charlie-ram` | Clean (FAMACHA 1–2, abscess resolved) | weight contradiction (108.2 vs 232.2), DOB null, pedigree null, dual FAMACHA arrays, "needs to move pens" action buried in notes |
| `merrie` | Clean (FAMACHA 1–2) | weight inconsistent across 3 places, offspring_ids empty, dual FAMACHA arrays |
| `charlies-farm-ewe-p3` | Clean (FAMACHA 1) | DOB null, pedigree null, offspring_ids empty (missing MC-2602), inbreeding flag in prose only |
| `broken-tail` | Clean (FAMACHA 1) | secondary_tag 0029 conflict with Nori's primary, breeding.is_breeding_animal=false (wrong), lambing_records empty, pen history embedded in notes |
| `nori` | Clean (FAMACHA 1–2; chin knot monitored) | famacha_scores=[] empty while famacha_history populated, offspring_ids missing MC-2604, pedigree null |
| `charlies-farm-ewe-baby-p3` | Clean (FAMACHA 1) | breed_composition empty (could be computed), inbreeding risk if dam/sire are siblings |
| `broken-tail-twin-ewe` | **WATCH — FAMACHA 5 on 4-9, no recheck since** | breed_composition empty, weak_resistance flag at wrong nesting level, sire null |
| `broken-tail-twin-ewe-2` | DECEASED 2026-04-22 (parasites) | stale auction fields (status_notes, scheduled_auction), stale text in source-quoted notes ("sold 4-15"), breed_composition empty |
| `nori-baby-p3` | **WATCH — FAMACHA 3 on 4-9, no recheck since** | breed_composition empty, sire null, missing from Nori's offspring_ids |

---

## What I did not do in this analysis

- **I did not modify the database.** This is a read-only analysis pass. Any cleanup belongs in a separate commit, with owner approval per item.
- **I did not run a parasite-resistance score.** The script exists and would give a number per animal, but I judged that a number adds less value here than reading each record.
- **I did not invent breed composition** for the three lambs whose sires are null.
- **I did not assume Charlie's lineage** runs through our Pen 3 Nori — the notes are ambiguous and I won't guess.
- **I did not "fix" Broken Tail's secondary-tag 0029 conflict** — owner deferred to the index-card review.

Soli Deo Gloria.
