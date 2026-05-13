# 2026 Drought Cull List

**Date:** 2026-05-13
**Trigger:** Spring 2026 drought = lowest parasite pressure of the year. Animals scoring FAMACHA 4–5 under these conditions are failing during the easiest conditions possible — the strongest cull signal this flock will ever get.
**Framework:** `breeding_policy.selection_hierarchy` rank 1 — FAMACHA/FEC. *"FAMACHA 4–5 requiring treatment = cull candidate."*

---

## Methodology

1. Queried every alive animal in `data/flock_database.json` for any FAMACHA score ≥ 4 dated within the last 60 days (since 2026-03-14).
2. Cross-referenced against `health.weak_resistance: true` flag.
3. Added pedigree-impact assessment (alive offspring count + total pedigree references).
4. Categorized by recommended action.

---

## Summary

| Animal | Pen | Age | Weak-resist flag | Worst FAMACHA in 60d | Alive offspring | Recommended action |
|--------|-----|-----|------------------|---------------------|-----------------|--------------------|
| **GG** (gg) | Pen 4 | adult ewe | yes | 5 on 2026-04-10 (3rd emergency) | 2 | **Cull / auction** |
| **Rocky** (rocky) | Pen 2 | adult ram | yes | (no recent 4-5; flagged historically) | 2 | **Cull / replace** |
| **Serendipity White Ram Twin** | Pen 4 | lamb (~4 mo) | n/a | 5 on 2026-04-10 (recurring) | 0 | **Auction** |
| **Serendipity Black Ewe Twin** | Pen 4 | lamb (~4 mo) | n/a | 5 on 2026-04-10 (recurring) | 0 | **Auction** |
| **Baby Azure** | Pen 1 | lamb (~4 mo) | n/a | 5 on 2026-04-01 | 0 | **Auction-watch** |
| **Broken Tail Twin Ewe** | Pen 3 | lamb (~4.5 mo) | n/a | 5 on 2026-04-09 | 0 | **Auction-watch** |
| **Azure** (azure) | Pen 1 | adult ewe | yes | (no 4-5 in 60d; weak history) | 1 | **Watch + plan fall cull** |
| **FM** (fm) | Pen 4 | adult ewe | yes | (no 4-5 in 60d; weak history) | 3 | **Watch + plan fall cull** |
| **Lara** (lara) | Pen 4 | adult ewe | yes | (no 4-5 in 60d; weak history) | 0 | **Watch** |

---

## Cull / auction — immediate

### GG (id: `gg`) — adult ewe, Pen 4
- **FAMACHA timeline (60d):** 5 on 2026-04-10 — "Eyes almost white AGAIN (3rd emergency). Fenbendazole + Ivermectin + Iron 3 mL + VB 4 mL."
- **Weak-resistance flag:** yes
- **Hard-lessons context:** *"GG and Rocky are alive because owner skill improved, not because they are resistant. They require aggressive treatment to survive."*
- **Pedigree impact:** 2 alive descendants (gigi-2025-ram in Pen 4, gigi-2026-baby in Pen 3). 4 total records reference her. Removing her does not break pedigree refs.
- **Action:** **Cull / auction.** Drought-season FAMACHA 5 is the strongest cull signal. The line has now had three emergencies on a single animal. Her surviving descendants carry forward whatever salvageable genetics existed.

### Rocky (id: `rocky`) — adult ram, Pen 2
- **FAMACHA in 60d:** no recent 4–5 entries (but health.weak_resistance = true, and hard_lessons pair her with GG as "alive because owner skill, not resistance").
- **Pedigree impact:** 2 alive descendants in the pedigree. Pen 2 is now down to Rocky + 0053.
- **Action:** **Cull / replace.** Rocky's continued presence as a breeding ram conflicts with the selection hierarchy (rank 1: FAMACHA). The Pen 2 role can be reassigned. Plan a replacement before culling.

### Serendipity White Ram Twin (id: `serendipity-twin-ram`) — lamb, Pen 4
- **FAMACHA timeline (60d):** 5 on 2026-04-10 — "EYES WHITE AGAIN. Iron 0.5 + VB12 1 mL + CDT booster."
- **Pedigree:** sire Kelsier (gold-standard parasite resistance), dam Serendipity. Failure here means *dam genetics dominated* despite the best available sire — the cross does not produce resistant lambs.
- **Action:** **Auction.** Will not survive the next pressure season; auctioning before failure is the kind step.

### Serendipity Black Ewe Twin (id: `serendipity-twin-ewe`) — lamb, Pen 4
- **FAMACHA timeline (60d):** 5 on 2026-04-10 — "Fenbendazole + Ivermectin + 3 mL Iron + 4 mL VitB + booster."
- **Pedigree:** same as twin above. Same Kelsier-sire-and-still-fails verdict.
- **Action:** **Auction.**

---

## Auction-watch — second-tier candidates

### Baby Azure (id: `baby-azure`) — lamb, Pen 1
- **FAMACHA timeline (60d):** 5 on 2026-04-01 — "FAMACHA 5, severe. Bright and alert despite score. Treated with Ivermectin + Fenbendazole + Iron + B12 + Nutridrench."
- **Pedigree:** dam is Azure (on weak-resistance list). Inheritance pattern suggests vulnerability is dam-dominant.
- **Action:** **Auction-watch.** Single emergency so far. Re-check at next inspection; if scores rebound and hold, keep on watch. If second 4–5 event, auction.

### Broken Tail Twin Ewe (id: `broken-tail-twin-ewe`) — lamb, Pen 3
- **FAMACHA timeline (60d):** 5 on 2026-04-09 — "EYES WHITE. 1 cc Iron, 1.5 cc VB shot, Ivermectin. Booster."
- **Pedigree:** dam Broken Tail (her own FAMACHA history is consistently good — described as "SOLID" matriarch). But her twin (white) also had eyes-white event 2026-04-09 ("both BT twins failing"). The line under stress shows weakness even with a strong dam.
- **Action:** **Auction-watch.** Re-check; if she recovers and holds, monitor. Twin sister was already flagged as parasite-vulnerable in DB.

---

## Watch + plan fall cull — weak-resistance adults with no current FAMACHA 4–5

These adult ewes carry the `weak_resistance: true` flag but did not score 4–5 in the last 60 days. They survived under drought (low pressure) by definition — but their history says they fail under heavier pressure. Plan to evaluate at fall vaccination day.

- **Azure** (Pen 1, 1 alive offspring): on weak list. Dam of Baby Azure (also flagged above).
- **FM** (Pen 4, 3 alive offspring including MC08 + samson-daughter-p4 + flan): on weak list. Pedigree-valuable as Cotswold/Tunis foundation; removal would lose breed diversity. Cull only if she fails under summer pressure.
- **Lara** (Pen 4, 0 alive offspring): on weak list. Pedigree-isolated. Lowest cost to remove.

---

## Pedigree-impact note

None of the recommendations break pedigree references — deceased/sold/culled animals are retained in the database for genealogy. The breeding-pipeline impact is:

- Pen 4 (weak-pen): losing GG + Serendipity twins reduces head count from 12 → 9, but the pen is already designated weak-resistance watch (per CLAUDE.md). Pen 4 has no replacement breeding stock pending.
- Pen 1: losing Baby Azure (if action upgrades to auction) does not reduce breeding stock — she is too young to have bred.
- Pen 2: losing Rocky requires a replacement ram. **Blocker.** Owner decision needed before action.
- Pen 3: losing Broken Tail Twin Ewe does not affect breeding (lamb, unbred).

---

## Output

This list is a recommendation. Owner makes the actual cull/auction decision. Once decisions are made, update each animal's record:
- For culled animals: `status` → `culled`, `status_date` set, `status_notes` records the cull rationale.
- For auctioned animals: `status` → `sold`, `status_date`, `sold_price`, `sold_to` (if known).
- Pen field nulled.

Validator (`python3 scripts/validate_flock.py`) should remain at 0 errors after the updates.

---

*Soli Deo Gloria.*
