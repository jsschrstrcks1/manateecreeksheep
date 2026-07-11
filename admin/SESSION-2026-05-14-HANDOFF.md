# Session 2026-05-14 handoff — memory + HLS propagation

Written by a container-scoped Claude Code session that could reach:
- `/home/user/manateecreeksheep` (this repo)
- `/home/user/open-claw-stuff` (household host, holds HLS catalog + `.memory/`)
- `/home/user/ken` (holds `orchestrator/memory_ops.py`)

**Could NOT reach:** `/Users/kenbaker/ocs-work` (the Mac SSOT). Anything the Mac SSOT holds beyond the in-container mirror was left alone.

## What this session did

### Sheep-database work (manateecreeksheep repo)
Committed to `claude/lamb-weaning-pens-uC2Fh` and fast-forwarded to `main` (per operator instruction) — HEAD `13a863e`. Most recent substantive commit is `0e96ae8` **"Merge windlestone-kat-dorper into buck-original (same animal)"**. Records reconciled per owner statement 2026-05-14.

### Memory writes (open-claw-stuff/.memory/sheep/)
Four new memories encoded via `python3 /home/user/ken/orchestrator/memory_ops.py encode sheep …`. All `protected=true`, tagged `manateecreeksheep`. Files (new, untracked at time of writing):
- `.memory/sheep/000b2d2d.json`
- `.memory/sheep/26ba314e.json`
- `.memory/sheep/ef71d86c.json`
- `.memory/sheep/fc76151f.json`

Content:
1. `buck-original == "Windlestone Kat/Dorper Ram"` (aliases include Butthead, Charlie's Ram) — duplicate record merged and deleted.
2. buck-original death date is unknown; the "Hurricane Helene" attribution is unreliable because Feb–Mar 2026 FAMACHA + CDT records post-date Helene.
3. Both buck-original and current buck breed compositions derive from a "Buck breeding page" that has not been re-verified — comps flagged uncertain until owner re-checks the source docs.
4. Current buck (Tree Fort, alive 2026) sired the 2026 wean batch (tag-0035-baby-ewe, tag-31-orange-tf-ram-lamb, bambii-baby, and — already in DB — charlies-ram-lamb).

Sheep-domain memory count: 72 → 76 on disk.

### HLS catalog writes (open-claw-stuff/.household-library/)
Registered 3 follow-ups via `node admin/library.mjs register`:
- `mc-buck-breed-comp-verify-2026-05-14` (P4) — verify buck-original + current buck breed comp from Buck breeding page docs
- `mc-buck-original-death-date-2026-05-14` (P4) — confirm buck-original actual date of death
- `mc-bambii-2027-breeding-partner` (P5) — pick Bambii + Bambii's Baby 2027 breeding partner (Charlie vs Angus, not Rocky)

Reflected in:
- `.household-library/catalog.jsonl` (+3 rows)
- `.household-library/events.jsonl` (+3 `user_requested` events)
- `docs/HOUSEHOLD-TASK-INDEX.md` (+3 index rows)
- `manateecreeksheep/admin/UNFINISHED_TASKS.md` (new file, this repo, +3 rows)

## Known snags for the SSOT-visible agent

### 1. library.mjs REPO_MAP missing `manateecreeksheep`
`open-claw-stuff/admin/library.mjs` line 19-27 hard-codes `REPO_MAP` for InTheWake / ken / Romans / Grandmasrecipes but not `manateecreeksheep`. `repoPath("manateecreeksheep")` falls through to the literal string `"manateecreeksheep"`, which gets resolved relative to CWD. That created a stray `open-claw-stuff/manateecreeksheep/admin/UNFINISHED_TASKS.md`. I moved the file to the real `manateecreeksheep/admin/UNFINISHED_TASKS.md` and `rm -rf`'d the stray subdir before committing.

**Fix on Mac:** add `manateecreeksheep: process.env.MANATEE_ROOT || "/Users/kenbaker/…/manateecreeksheep"` to REPO_MAP, or set `MANATEECREEKSHEEP_ROOT` env, so future runs write to the real repo directly.

### 2. Pre-existing catalog duplicates
`.household-library/catalog.jsonl` in HEAD (`13a863e`) already contains multiple task_ids twice — verified with `grep -c "merge-p0-pr-after-review"` = 2 both in HEAD and in the pushed state. This is not from my session. Running `node admin/library.mjs mirrors` regenerates `admin/UNFINISHED_TASKS.md` / `admin/COMPLETED_TASKS.md` from the catalog and faithfully carries the duplicates through. My commit includes that regeneration; the underlying dup wasn't fixed.

**Fix on Mac:** `node admin/dedup-catalog.mjs --apply` then re-run `node admin/library.mjs mirrors --repo open-claw-stuff`.

### 3. Household SSOT sync
The container's `/home/user/open-claw-stuff/.household-library/` is a mirror of the Mac SSOT at `/Users/kenbaker/ocs-work/.household-library/`. My 3 new catalog rows + memory writes need to be sync'd back to the Mac copy — normally done by pulling `open-claw-stuff main` on the Mac.

## Commands to replay from Mac if needed

```bash
# From /Users/kenbaker/ocs-work:
git -C ~/…/open-claw-stuff pull origin main         # picks up 3 catalog rows + 4 memories
git -C ~/…/manateecreeksheep pull origin main       # picks up UNFINISHED_TASKS.md

# Dedup catalog (optional cleanup):
node ~/…/open-claw-stuff/admin/dedup-catalog.mjs --apply
node ~/…/open-claw-stuff/admin/library.mjs mirrors --repo open-claw-stuff
```

Soli Deo Gloria.
