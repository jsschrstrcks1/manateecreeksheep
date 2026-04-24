# Sheep Visual Identification — Process

How to identify sheep in photos against `data/flock_database.json` and write the results into `docs/sheep_visual_id.md` and the DB. Derived from the 2026-04-24 Pen 4 pass.

---

## Inputs you need before starting

1. **Photos of the pen.** A set of 2–5 images showing the animals from different angles is ideal.
2. **The pen identifier** (e.g., "Pen 4", "Goose Pen").
3. **The owner available to answer questions.** You will not finish this correctly without owner ground truth. Plan on it.

If any of these are missing, stop and ask.

---

## The process (in order)

### 1. Pull the pen roster from the DB

```python
# pens.pen_N gives you ram + ewes + lambs by id
db = json.load(open('data/flock_database.json'))
roster = db['pens'][pen_key]  # e.g. 'pen_4'
```

Every animal listed there is a candidate. Every animal NOT listed is a candidate too — **rosters are sometimes stale or missing animals** (Pen 4 had an unlisted Samson × Broken Tail ewe, and had a duplicate BHD record `g023-bhd-ewe` that was actually `lara` under a different tag).

So: build a candidate set starting with the roster, but stay alert for "mystery" sheep in the photo who don't fit any roster member.

### 2. Build a phenotype table

For each candidate, extract from the DB sheep record:
- `id`, `name`, `aliases`
- `tag`, `secondary_tags`, `mc_tag`
- `sex`, approximate age (from `dob`)
- `breed_composition.percentages`
- `breed_composition.hair_percentage` / `wool_percentage` (coat type is the most useful single filter)
- `color_markings`
- `visual_id` block if present (this is the best data — check it first)
- size/weight if recorded

Keep this table in front of you as you look at photos.

### 3. Apply the decision tree

Work these filters in this order — earlier ones are more reliable:

1. **Adult vs. lamb** — size + proportions.
2. **Coat type: hair vs. wool** — hair breeds (Katahdin, Dorper, St Croix, BBB, St Augustine, Wiltshire Horn) are slick, no fleece. Wool breeds (Hampshire, Suffolk, Cotswold, Tunis, Babydoll, Awassi) carry a thick fleece. This is the single strongest filter.
3. **Face color** — black face (Hampshire, Suffolk, BHD) vs. white face (most hair breeds, Cotswold, Tunis-fade-to-cream).
4. **Body color** — cream, dark, red, piebald, etc.
5. **Body size** — large vs. medium vs. small.
6. **Tag number/color** — the tie-breaker. Read them when you can.

### 4. Anchor high-confidence IDs first

Look for animals with unique phenotype combinations in the roster — those are "locked" IDs. For Pen 4 these were:
- FM = only large light-cream heavy-fleece animal
- Serendipity = only dark small patchy-coat adult
- Black lamb = only black lamb in the pen
- Small white hair-coat = only hair-coat small adult

Once those are locked, remaining candidates are smaller sets to disambiguate.

### 5. Flag confusion pairs before guessing

When two animals could plausibly be the same sheep in a photo, **name the pair and your uncertainty** before guessing. Examples from Pen 4:

- GG vs. Gigi's 2025 Ram — both black-faced wool.
- Lara (BHD hair) vs. Serendipity (dark mixed) — both can look dark-faced in evening light.
- MC08 vs. samson-daughter-p4 — siblings, both white-faced cream wool.

For each pair, ask: what's the cheapest tell? (size, condition, lamb proximity, tag visibility)

### 6. Ask the owner for ground truth on uncertain IDs

**Do not guess past medium confidence.** Write up your IDs in a table with confidence levels, then ask the owner:
- "Left-foreground dark animal — is it Serendipity?"
- "The black-faced ewe in the center — GG or samson-daughter-p4?"

Accept their correction without resistance. Owner testimony overrides DB assumptions.

### 7. Watch for DB errors the photo surfaces

Photo IDs frequently expose DB problems:
- **Missing records** (Samson × Broken Tail daughter wasn't in any roster)
- **Duplicate records** (Lara = G023, two records for the same sheep)
- **Wrong status** (Lara and Half Tail both wrongly bulk-marked deceased on 2026-04-02)
- **Wrong pedigree** (MC08's sire was "[UNCLEAR]" — owner resolved to Samson × Broken Tail)
- **Misleading color_markings** (FM labeled "Tunis Red" but is actually light cream — the label was a heritage name, not an adult color)

Treat each photo session as an opportunity to fix these. Every correction is a commit with a clear message.

### 8. Write updates in three places, in one commit

1. **`data/flock_database.json`** — update `color_markings`, add a `visual_id` block, fix `status`/`pen`, add new records, merge duplicates.
2. **`docs/sheep_visual_id.md`** — update the animal's entry, the decision tree, the confusion-pair table, and the provenance section.
3. **Commit message** — name what changed and why. Be explicit about "CORRECTED from prior assumption" so future Claudes don't re-introduce the same error.

---

## Patterns that will bite you (seen in Pen 4)

### Heritage-name color words in `color_markings` may not match adult appearance
- FM had `"color_markings": "Tunis Red"`. She is not red. She is cream. "Tunis Red" described her breed origin, not her body.
- Fix: always cross-check a color note with an actual photo before trusting it.

### Single-parent breed assumptions for face color are unreliable
- Samson was 100% Hampshire (classic black face). His two offspring MC08 and samson-daughter-p4 have **white faces**. The hair-breed dam (Broken Tail) dominated face pigment.
- Fix: never assume "Hampshire sire → black-faced offspring" without seeing the animal.

### Evening/golden-hour light distorts body color
- Lara (BHD: white body standard) appeared tan-brown in pen-4 picture 2 taken in low-angle evening sun.
- Fix: note the lighting when writing phenotype descriptions. Prefer midday photos for color truth.

### Tag conventions evolve
- The "G" prefix in G023 is a green-tag series overlay on the older "023" number. Same animal, two records.
- Fix: before assuming two records are different animals, compare numeric tag + breed + age.

### Bulk-cleanup dates are not real death dates
- Half Tail, Lara, and others carry `status_date: 2026-04-02`. That's a bulk date when missing animals were swept to `deceased`. Half Tail actually died during Hurricane Helene (2024-09-26); Lara is alive.
- Fix: when you see 2026-04-02, it's suspicious. Ask the owner.

### Rosters can be missing a real animal
- Pen 4 was missing a Samson × Broken Tail ewe who is clearly in the photos. Roster was 10; reality was 11.
- Fix: count animals in the photo. If they don't match the roster, the roster is wrong.

---

## Integrity guardrails (CAREFUL-NOT-CLEVER)

From `CLAUDE.md` / `careful.md`:
- **Never invent phenotype.** If the DB doesn't describe a sheep and you haven't seen them, mark `[UNCLEAR]`, confidence `low`, and say so.
- **Owner testimony beats DB text.** The DB exists to encode owner knowledge, not override it.
- **Everything for the glory of God.** Accuracy matters because real animals depend on correct records.

If a hook or automated check contradicts clear owner testimony, note the hook's concern but proceed — the owner is the primary source. File the concern in the commit message.

---

## Output format (what the other thread should produce)

For a new pen, the other thread should hand back:

1. **A commit to `claude/evaluate-pen-N-sheep-<suffix>` branch** containing:
   - An updated `data/flock_database.json` with per-animal `visual_id` blocks, corrected `color_markings`, fixed pen roster, merged duplicates, added missing animals.
   - A new section in `docs/sheep_visual_id.md` for that pen, mirroring the Pen 4 structure:
     - Per-animal subsections with tag, sex, breed, phenotype, distinguishers
     - Quick-reference decision tree
     - Known visual confusion cases table
     - Provenance block (who confirmed what, when, from which picture)
   - Clear commit message explaining corrections.

2. **A brief conversation summary** for the owner stating:
   - Which animals are locked and confidence
   - Which IDs still need owner confirmation
   - Any DB anomalies surfaced (missing animals, duplicates, wrong status)
