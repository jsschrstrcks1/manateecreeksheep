# Prompt — Identify sheep in the next pen

Paste this into a new Claude Code thread (or edit the pen name inline) when you want another thread to work through the next pen's photos.

---

## The prompt

> I'm going to give you photos from **Pen N** (replace with the actual pen — e.g., Pen 1, Pen 3, Goose Pen) and I want you to identify every sheep visible, then update the repository's visual identification documentation and flock database.
>
> Before you do anything else, read these two files in this repo:
>
> 1. `docs/sheep_visual_id.md` — the living visual-ID guide. The Pen 4 section is complete and is your template.
> 2. `docs/sheep_visual_id_process.md` — the step-by-step process and the patterns that have bitten previous attempts.
>
> Then follow the process in `sheep_visual_id_process.md` exactly. Specifically:
>
> 1. Pull the roster for Pen N from `data/flock_database.json` under `pens.pen_N` (or the equivalent pen key — check the `pens` dict for the right name).
> 2. For each animal in the roster, build a phenotype table pulling from the `sheep` array: tag, breed composition, hair_percentage vs wool_percentage, color_markings, and any existing `visual_id` block.
> 3. Run the decision tree: adult/lamb → hair/wool → face color → body color → size → tag.
> 4. Identify every sheep you can see in the photos. Lock high-confidence IDs first; flag confusion pairs with your uncertainty before guessing.
> 5. Ask me for ground truth on anything below medium confidence. Don't guess.
> 6. Watch for the DB-error patterns documented in the process doc: missing records, duplicate records, wrong status (especially `2026-04-02` bulk-cleanup dates), misleading `color_markings` (heritage names that don't match adult color), and animals whose face color doesn't match what you'd expect from a single parent's breed.
> 7. Write the result as ONE commit on a branch named `claude/evaluate-pen-N-sheep-<suffix>`. That commit should:
>    - Update `data/flock_database.json` with per-animal `visual_id` blocks, corrected `color_markings`, fixed pen roster, merged duplicates, added missing animals.
>    - Add a new section to `docs/sheep_visual_id.md` for Pen N following the Pen 4 structure (per-animal subsections, decision tree, confusion-pair table, provenance block).
>    - Have a commit message that names each change and marks any correction as "CORRECTED from prior assumption".
> 8. Validate the DB before committing: `python3 scripts/validate_flock.py` — ensure you don't introduce NEW errors (pre-existing errors are OK to leave).
> 9. Report back to me with: locked IDs, pending IDs needing my confirmation, and any DB anomalies you found.
>
> Do not guess phenotype. Do not invent animals. When in doubt, ask me.
>
> Photos follow:
>
> [attach the photos]

---

## Notes for the person running this prompt

- **Pick the right pen key.** Pens in `data/flock_database.json` use keys like `pen_1`, `pen_2`, `goose_pen`, `chicken_coop`, `tree_fort`. Check the top-level `pens` dict.
- **Have the photos ready.** The Pen 4 pass used 4 group photos plus one head-shot of a sibling in another pen (MC08) to resolve a phenotype question. Plan to provide at least 2–3 angles of the pen, and be willing to send supporting photos from other pens when cross-sibling verification helps.
- **Plan for a conversation.** The thread will come back with questions. Budget time to answer them — the process is designed to ask rather than guess.
- **Owner knowledge wins.** If an automated "hook" in the thread complains about unverified claims, your testimony overrides it. The thread has been instructed to proceed with your corrections and note the hook's concern in the commit message.
- **One pen per thread.** Don't try to do multiple pens at once. Complexity compounds and errors cascade.

---

## After the thread finishes

Review the commit on the branch. Spot-check:

- Did every animal in the photos get an ID?
- Did the phenotype descriptions match what you see in the photos?
- Did they surface any DB anomalies (missing/duplicate/wrong-status records) and fix them cleanly?
- Is there a confusion-pair table for any ambiguous phenotypes?

If it looks good, merge the branch. If there are issues, iterate in the same thread — don't spawn a new one.
