# Session handoff — manateecreeksheep buck/Bambii (2026-05-14)

**Container session:** encoded 4 `sheep` memories + registered 3 HLS tasks; pushed `manateecreeksheep` shelf at `13a863e`.  
**Mac replay (grok1, 2026-07-11):** HLS tasks + REPO_MAP fix + catalog dedup applied on true SSOT.  
**Soli Deo Gloria.**

## Mac verification

| Artifact | On GitHub SSOT? |
|----------|-----------------|
| `manateecreeksheep` `13a863e` (library shelf) | Yes |
| Container `SESSION-2026-05-14-HANDOFF` (full) | **No** — this file is Mac-written summary |
| 4 `.memory/sheep/` encodes on `open-claw-stuff` remote | **Not verified** — Mac SSOT still at `acd2758`; replay memories when export lands |
| 3 HLS tasks | **Yes** — Mac-registered `mc-buck-*`, `mc-bambii-*` (#64–#66) |

## HLS tasks (catalog SSOT)

| task_id | P | Issue |
|---------|---|-------|
| `mc-buck-breed-comp-verify-2026-05-14` | 4 | [#64](https://github.com/jsschrstrcks1/manateecreeksheep/issues/64) |
| `mc-buck-original-death-date-2026-05-14` | 4 | [#65](https://github.com/jsschrstrcks1/manateecreeksheep/issues/65) |
| `mc-bambii-2027-breeding-partner` | 5 | [#66](https://github.com/jsschrstrcks1/manateecreeksheep/issues/66) |

## Snags fixed on Mac

1. **`library.mjs` REPO_MAP** — added `manateecreeksheep` → cluster path (was writing stray subdir).
2. **Catalog duplicates** — `dedup-catalog.mjs --apply` on household catalog (pre-existing, e.g. `merge-p0-pr-after-review`).

## Memories to replay (when container export available)

Topics from container (4 protected `sheep` memories):

- Buck original identity merge
- Death-date uncertainty
- Disputed breeding-page comp source
- Current buck's 2026 Tree Fort sirings

Copy from `admin/memory-exports/` or re-encode — **do not invent** from this stub.

## Reading order

- `admin/REPO-AGENT-APPENDIX.md` (Tree Fort membership 2026-05-14)
- `unfinished_tasks.md` (planned pen moves)
- `docs/NEW_CARDS_2026_APRIL.md` (Bambii / Tree Fort cards)