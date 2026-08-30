# Upgrade Ledger — manateecreeksheep

Append-only. One row per candidate; never delete. Ground each claim or mark it `(hunch)`.
A refusal is an entry too (`decided-no` + reason). Soli Deo Gloria.

> **Note (2026-08-30):** a parallel ledger with more rows exists on the sibling branch
> `claude/sophos-install-sheep-tasks` (483 lines). When the branches reconcile, these ledgers
> UNION (append-only). This file records the operator's decisions on THIS lane plus the
> parallel-implementation finding below.

---

## Operator decisions & preferences (session memory — Ken)

Recorded so the next session does not re-litigate settled choices. These are the operator's
actual selections this session, not inferences.

| # | Decision | What Ken chose | Evidence / context |
|---|----------|----------------|--------------------|
| D1 | Scope of "build it" | **The MCS feature program** (Layer 1), NOT repo-safety parity | "No — the feature build" |
| D2 | Entry point | **Data-model foundation** first | AskUserQuestion answer |
| D3 | Cadence | **Continuous autonomous building**, loop until done; "keep going. keep building." | repeated across turns |
| D4 | Posture | **Careful, not clever**; accuracy is worship (heirloom flock records); honest about gaps; no fabricated numbers | household law + repeated |
| D5 | Tool shape preference | **Read-only / pure-addition** advisories; operator decides; never a silent write of a guessed value | every tool built this way, unchallenged |
| D6 | Florida Cracker h2 priors | **Keep opt-in, NOT auto-applied** (mixed flock) until a flock-internal heritability check exists | "2 need more info" → I explained; left opt-in |
| D7 | Data-starved features | **Defer** scaffolds for absent data (milk, sell-weight, economics) unless explicitly asked; prefer well-fed tools | stated preference; accepted |
| D8 | Evaluation rigor | Wanted **adversarial review + edge testing**; fix must/should-fixes | "evaluate…how it must be improved", "edge test it" |
| D9 | Single entry point | Valued a **hub** over 13 loose scripts (built `flock.py`) | review verdict accepted, dashboard kept |

---

## Candidates

| UL | Area | Candidate | Status | Notes |
|----|------|-----------|--------|-------|
| UL-MCS-001 | process | **Parallel-implementation collision** — a sibling branch (`claude/sophos-install-sheep-tasks`) built ~11,950 lines of overlapping flock tooling (quantity, pedigree, cohorts/pen_history, ewe_productivity, deworm/triage, health events, intake, loss, mating) in parallel with this branch. Neither is merged to `main`. | **needs-operator** | This is the "resolve to the superset / never duplicate" case (careful-not-clever §Multi-agent). Recommendation below. Both branches have real, non-identical value. |
| UL-MCS-002 | correctness | Sibling `lib/pedigree.py` uses **topological generation ordering** and is COI-correct; it never had the DOB-string bug this lane had to fix. On the pedigree axis, their code is already right. | tracked | Argues their core math is sound; my correctness edge is elsewhere (food-safety, edge-hardening, tests). |
| UL-MCS-003 | superset | Tools **unique to this lane**, not present by filename on the sibling: dedicated food-safety `withdrawal_check` (+ residual-token guard), `vaccination_check`, `lambing_reconcile`, `flock.py` hub, the structural-types validator gate, and 375 test pins. | tracked | These are the pieces the superset should keep from this lane. |
| UL-MCS-004 | superset | Features **broader on the sibling**, absent here: flock-agenda engine (+ plan doc), chute/census web apps, weather-parasite signal, per-animal economics, mating predictor, trait card, owner-sync questionnaire, and a `flock_database.json` migration. | tracked | These are what the superset should keep from the sibling. |
| UL-MCS-005 | process | The `open_prs` / superset-guard advisory that should have surfaced the sibling's open work never showed it to either lane. Duplicate effort resulted. | tracked (hunch) | Same failure class as the household's UL-348 (three lanes, one fix). Worth confirming the guard is armed on this repo. |

## Recommendation (UL-MCS-001)

The sibling branch is the **broader and, on pedigree, at-least-as-correct** base. The careful
resolution is: **adopt the sibling branch as the base**, then **port this lane's verified-unique
pieces onto it** — the food-safety `withdrawal_check`, `vaccination_check`, `lambing_reconcile`,
the structural-types validator gate, and the test rigor. This is a superset, not a winner-take-all.

This is **the operator's canonical-architecture decision** and it involves a data migration
(`flock_database.json`), so it is not executed unilaterally — merging two ~11k-line bodies of work
the wrong way destroys a sibling's effort and is irreversible. Awaiting the operator's direction on
which branch is canonical and whether to port this lane's unique tools onto it.
