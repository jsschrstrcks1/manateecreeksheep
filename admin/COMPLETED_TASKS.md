# Completed Tasks — manateecreeksheep (read-only archive)

> **Task custody (HLS):** Work queues live in `.household-library/catalog.jsonl` — not in this file.
> Find/checkout: `node admin/library.mjs preflight --query "<task>" --patron <id> --merge`
> **This document** is context/spec only unless stated otherwise.

**Generated:** 2026-08-19T04:14:22.061Z
**Authoritative completions:** `admin/VERIFIED_COMPLETED.md` (two-patron quorum) + catalog `state: complete`.
**Do not append ad hoc** — use `library verify` / `library complete`.

| task_id | title | artifact |
|---------|-------|----------|
| p0-1-duplicate-sheep-ids-regression | P0.1 Duplicate sheep IDs (REGRESSION) | verification probes, session 2026-07-14 |
| p0-2-today-s-dam-correction-is-half-applied-regression-from-this | P0.2 Today's dam correction is half-applied (REGRESSION — from this session) | manateecreeksheep branch claude/friendly-gates-x713uo |
| p0-3-broken-dam-reference | P0.3 Broken dam reference | verification probes, session 2026-07-14 |
| p0-4-invalid-status-enum | P0.4 Invalid status enum | verification probes, session 2026-07-14 |
| p0-5-gg-ewe-listed-as-sire-on-3-lambs-warning-but-pedigree-fatal | P0.5 GG (ewe) listed as sire on 3 lambs (WARNING but pedigree-fatal) | verification probes, session 2026-07-14 |
| p0-6-tag-collision-among-living-sheep | P0.6 Tag collision among living sheep | manateecreeksheep branch claude/friendly-gates-x713uo |
| pedigree-integrity-errors-block-level | Pedigree-integrity errors (block-level) | verification probes, session 2026-07-14 |
| mcs-validator-percentage-value-nan | Cross-review 2026-07-16: manateecreeksheep validator NaN hole one field over — sibling fixed unknown_percentage NaN but a NaN in a percentages VALUE still silently disabled the breed-sum guard (abs(NaN-100)>2 is False; json.load accepts NaN). FIXED: guard the total via math.isfinite. Regression pins added. | https://github.com/jsschrstrcks1/manateecreeksheep/issues/81 |
| memory-eclipse-idalia-scrub | Scrub Eclipse Idalia death refs — sold at auction 2026-04-26 not hurricane casualty | — |
| memory-norison-eclipse-canonical-flock-ssot | Flock SSOT: NoriSon = Eclipse (same animal), sold 2026-04-26 | — |
| p1-1-20-records-missing-required-confidence-field | P1.1 20 records missing required `confidence` field | verification probes 2026-07-14 |
| p1-2-windlestone-breed-percentages-sum-to-95 | P1.2 Windlestone breed percentages sum to 95% | verification probes 2026-07-14 |
| p1-3-image-reference-broken | P1.3 Image reference broken | verification probes 2026-07-14 |
| validator-errors-that-block-clean-integrity-pass | Validator ERRORs that block clean integrity pass | verification probes 2026-07-14 |
| mc-2026-07-11-mining-replay | CLOSED-REPLAY marker: manateecreeksheep session 2026-07-11 mining (8 candidates; 7 encoded + Helene merged into 79b75f4a). No new sheep-pen work — Pen3 already via PR-23. | https://github.com/jsschrstrcks1/manateecreeksheep/issues/75 |

*Legacy completions in handoffs and dated roadmaps are historical — migrate via catalog register if still open.*

```bash
node admin/library.mjs mirrors --repo manateecreeksheep
```
