# Notebook Card Workflow — Standing Operating Procedure

**Scope:** Every time Mom adds new spiral-notebook card photos to the repo,
follow this loop. Closes L12 from `MANATEE_CREEK_REDESIGN_PLAN.md`.

**Trigger:** New `IMG_*.JPG` / `IMG_*.PNG` files appear at the repo root.

**Companions:** `.claude/skills/image-transcription/SKILL.md` (rules),
`docs/NEW_CARDS_2026_APRIL.md` (worked example), `careful.md` (integrity).

---

## The loop

```
photo → process (resize) → transcribe → propose JSON diff
       → owner review → validator → commit
```

Six steps. Each independently re-runnable if interrupted.

### 1. Drop the photos

Mom or owner copies new images to the repo root with their original
iPhone filenames (`IMG_0676.JPG`, `IMG_8644.PNG`, etc.). Do not rename.
Originals never get deleted (non-negotiable rule #1).

### 2. Process to ≤1800px

```bash
python3 scripts/process_images.py --status       # see what's pending
python3 scripts/process_images.py                # process all oversized
# or, per file:
python3 scripts/process_images.py --file IMG_0676.JPG
```

Output lands in `data/processed/IMG_*.jpeg`. The Claude API rejects
images >2000px; reading the original directly is forbidden by the
PreToolUse(Read) hook in `.claude/settings.json`. **Always read the
processed version.**

If `data/processed/` is missing, the script creates it.

### 3. Transcribe per the image-transcription skill

Open each new image with `Read`. For every sheep data point, capture:

- `source: IMG_####` (track provenance)
- type: `treatment | measurement | pen_assignment | health_note | lambing | identification`
- date (if visible in phone-app timestamp or written)
- exact transcription
- normalized version for the database

**Hard rules:**
- Mark uncertain handwriting as `[UNCLEAR]`. Do not guess.
- Preserve original spellings in raw notes (Mom writes "Amure" — keep
  that, normalize to "Azure" only in the canonical fields).
- Struck-through entries mean deceased / sold / treatment-not-given /
  corrected-elsewhere. Record the strikethrough and interpret carefully.

### 4. Propose JSON diff — DO NOT apply yet

Build the proposed update to `data/flock_database.json` as a *visible
edit* in your conversation (Edit tool, dry-run pass). Per card, the
candidate fields are typically:

- `pen` if pen-assignment changed
- `health.famacha_history[]` and/or `health.treatments[]` if a treatment
  is shown
- `health.vaccinations[]` for CDT/Covexin booster days
- `notes_history[]` for one-line dated annotations
- `status_date` + `status` if the card records a death or sale
- `tag` / `mc_tag` / `secondary_tags` if a new tag is shown
- `last_verified` set to the card date
- `source_refs.notebook_image[]` extended with the new IMG ref

Per the `careful-not-clever` PostToolUse hook, the harness will block
the edit if pedigree fields (sire/dam/breed comp) changed without source
verification. Be ready to explain why.

### 5. Owner review

For anything beyond a routine FAMACHA + treatment log entry — surface
it. Examples that require explicit owner confirmation before commit:

- Sire / dam changes (pedigree-canonical fields)
- Status changes (alive → deceased / sold / culled / gifted)
- Pen reassignments to a new pen (vs continuing the current pen)
- Tag-number conflicts (use the `tag_color` field if both kept their
  numbers — see P0.6 close-out)
- Breed-composition revisions

If the card is ambiguous, ask the question in chat with the image
attached. Do not infer.

### 6. Validator + atomic commit

```bash
python3 scripts/validate_flock.py
# Expect: 0 errors, 0 warnings (the current clean baseline)
```

If clean, commit. **One commit per logical unit of work** (rule #7),
not one commit per card. A typical commit groups one pen's check-day
worth of cards.

```
git add data/flock_database.json data/processed/IMG_####.jpeg <other relevant>
git commit -m "Card transcription: <pen>/<date> — <one-line summary>"
git push -u origin <branch>
```

If the validator reports new errors or warnings, *fix them in the same
session* — never push a regression. The 0/0 baseline is the line.

---

## Edge cases

### Cards covering multiple animals
A single group log (e.g., `IMG_0611` = Pen 5 group log) updates many
records. Apply each update; commit them together with a clear message:
`Pen 5 group log 2026-03-13 (IMG_0611): Corid 3-8 to 3-13, CDT 3-10, …`

### Cards correcting earlier records
A new card may override a prior database entry (e.g., "DOB 1-2-26"
correcting an earlier "12-26-25"). When this happens:
1. Update the canonical field.
2. Add a `notes_history` entry dated today, citing the IMG_#### that
   forced the correction.
3. Keep the old value visible in `notes` if it ever appeared in
   downstream artifacts (`data/sheets_export/*.tsv` etc.).

### Re-uploads / filename guesses
The April 2026 batch had four images sent inline after the IMG range
had been gap-filled. Those were assigned best-guess IMG numbers in
pen-adjacency order (see `docs/NEW_CARDS_2026_APRIL.md` for the
caveat). If a new batch arrives without filenames, follow the same
pattern: pick the next free IMG number in the source range, note the
caveat in the per-card log.

### Cards in the wrong order
Mom's phone app does not preserve linear order. Sort by date *visible
on the card* not file modification time. When the card has no date,
infer from context (other cards on the same checkup day, pen-group
logs) and note `dob_approximate: true` or `last_verified` set to a
range.

---

## Status of `data/processed/`

Per L10 (still open), the processed directory is recreated on each run
of `scripts/process_images.py`. The session that closes L10 will keep
all current images processed and add a validator check for parity
between source-image count and processed-image count.

Until L10 lands: re-run the processor before any transcription session
so the latest cards are available at ≤1800px.

---

## When in doubt

The owner is the source of truth, the notebook is the highest-fidelity
written source, and the database is the canonical store. If they
disagree, prefer the most recent owner statement, but write a
`notes_history` entry explaining the prior position and why it
changed.

*Soli Deo Gloria.*
