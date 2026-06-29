# Skills — manateecreeksheep

> The working flock. ~52 sheep, 9 pens, breeding pipeline, FAMACHA tracking. 26 skills configured — the densest skill stack of any livestock or domain repo because the operation is alive.

This document is the human-facing index of all Claude Code skills configured in this repository. The agent-facing pointer lives in [`CLAUDE.md`](CLAUDE.md). Skills follow the agent-skills-spec format and live under `.claude/skills/`.

**Total skills configured: 26.** 16 are the standard household kit + 10 are sheep-domain or orchestrator-specific.

---

## Quick reference

| Skill | Activation | Default | Domain |
|---|---|---|---|
| [`careful-not-clever`](#careful-not-clever) | automatic on every file modification | on | Integrity guardrail |
| [`breeding-advisor`](#breeding-advisor) | explicit | on | Breeding decisions |
| [`flock-validation`](#flock-validation) | automatic before commit | on | Database integrity |
| [`health-tracker`](#health-tracker) | automatic on health record edits | on | FAMACHA trends |
| [`pasture-planner`](#pasture-planner) | explicit | on | Rotation planning |
| [`image-transcription`](#image-transcription) | automatic on notebook image | on | Notebook OCR |
| [`google-sheets-sync`](#google-sheets-sync) | explicit | on | Spreadsheet ↔ JSON |
| [`consult`](#multi-llm-orchestrator) | explicit | on | Multi-LLM second opinion |
| [`orchestrate`](#multi-llm-orchestrator) | explicit | on | Multi-LLM pipeline (sheep mode) |
| [`orchestra`](#multi-llm-orchestrator) | explicit | on | Multi-LLM round-robin |
| `icp-2` | automatic on content writing | on | Human-First SEO/AEO 2026 |
| Standard household kit (16 skills) | mixed | on | See [section below](#standard-household-kit) |

---

## How invocation works

Claude Code skills can fire three ways:

**1. Automatic activation** via YAML `keywords:` and surrounding context. `careful-not-clever` fires on **every file modification** — it's the integrity guardrail for the whole repo.

**2. Explicit invocation:**

```
"Use the breeding-advisor to evaluate Charlie × Azure for spring 2026."
/skill breeding-advisor
```

**3. Implicit invocation by task shape** — notebook image reads trigger `image-transcription`; flock-database edits trigger `flock-validation`; completion claims trigger `verification-before-completion`.

---

## Sheep-domain skills

### `careful-not-clever`

**Path:** `.claude/skills/careful-not-clever/SKILL.md`

Integrity guardrail for sheep flock management. Enforces careful, verified work over clever shortcuts. Activates on every file modification to ensure sheep records, pedigrees, and health data are verified before committing. **Everything we do is for the glory of God, and with integrity.**

**Activation:** automatic on every file modification.

**The rule:**

- Spiral notebook images are MOST AUTHORITATIVE — when sources conflict, the notebook wins
- Read source first; understand what's there; check consistency; state assumptions
- One logical change at a time
- Verify every relationship (sire/dam claims must be confirmed in source data)
- Mark uncertainty `[UNCLEAR]`; set `confidence: "low"` for unverified data
- Verify, then report

**Key aliases the skill normalizes:**

- "Amure" (Mom's spelling) = **Azure**
- "Rock" = "Jerkface" = Awassi ram
- Mc11 = Charlie's ram = tag 12
- Mc12 = 036 = Serendipity's baby ewe
- NoriSon = ram in pen 5, tag 54

### `breeding-advisor`

**Path:** `.claude/skills/breeding-advisor/SKILL.md`
**Version:** 2.0.0

Evaluates sheep matings and pipeline placement against a performance-based checklist. Selection hierarchy (non-negotiable):

1. **FAMACHA/FEC** — parasite resistance first
2. **Hair/Wool** — OBSERVED coat, not breed-predicted
3. **Breed Composition** — informs, doesn't decide
4. **Meatiness** — tiebreaker

**Two modes:**

```
Mode 1: PAIRING CHECK
  "Should I breed [ram] to [ewe]?"
  "Evaluate [ram] × [ewe]"

Mode 2: PIPELINE CHECK
  "Where does this animal go in the pipeline?"
  "Is [animal] ready to advance?"
  "Which ram lamb cycles back?"
```

**Hard blocks (any one = REJECT):**

- Either animal not alive
- Subfertility (ram exposed to ≥3 ewes for ≥6 months, ≤1 conceived)
- FAMACHA ≥4 most recent OR ≥2 scores of 4-5 in past 6 months
- Inbreeding F > 0.25
- Ewe age < 10 months OR > 9 years with dystocia history
- No CDT/Covexin within 12 months
- Active contagious disease
- Ewe lambed < 5 months ago

**Risk scores accumulate, ≥14 = REJECT.** Full rubric in `SKILL.md`.

**The 7-pen pipeline:**

```
Pen 3 (intake) → TF → Pen 4 → Pen 5 → Pen 6 → Pen 1 → Pen 2 (elite)
  ↑                                                            |
  └──────────── best ram lambs cycle back ───────────────┘
```

Plus Goose Pen (grow-out + Awassi dairy line, outside loop).

### `flock-validation`

Validates `data/flock_database.json` against integrity rules.

**Manual invocation:**

```
python3 scripts/validate_flock.py
python3 scripts/validate_flock.py --check-references   # orphan sire/dam IDs
python3 scripts/validate_flock.py --check-images       # image refs
```

**Validates:** pedigree consistency (no cycles, parents exist), breed composition math, pen assignments (every active sheep in exactly one pen), tag uniqueness, health record completeness.

### `health-tracker`

Tracks FAMACHA scores and health trends per animal over time. Flags animals trending toward anemia *before* they're critical. Links health data to breeding decisions.

**FAMACHA scale (1–5):**

| Score | Color | Action |
|---|---|---|
| 1 | Red | none |
| 2 | Red-pink | none |
| 3 | Pink | borderline, monitor |
| 4 | Pink-white | treat |
| 5 | White | treat immediately, consider culling |

### `pasture-planner`

Plans pasture rotation for the Florida sheep operation. Considers parasite pressure (worm larvae viability by season), seasonal grass growth, pen capacity, required rest periods for larval die-off.

### `image-transcription`

Transcribes sheep records from spiral notebook photos and handwritten notes. Extracts treatment data, measurements, pen assignments, sheep identification from notebook page images.

**Activation:** automatic when reading `IMG_8560–8615.JPG` (handwritten notebook pages) or `IMG_8616–8643.PNG` (phone-app notes).

**Image sizes:**

| Range | Type | Content |
|---|---|---|
| IMG_8560–8615 | JPG | Handwritten notebook pages |
| IMG_8616–8643 | PNG | Phone app notes (treatments, measurements, pen assignments) |

**Always use `data/processed/` for AI reads** — originals are 4032×3024 or 1320×2868, exceeding the 2000 px API limit.

### `google-sheets-sync`

Bridges the Google Sheets spreadsheet (primary flock data source) with local `flock_database.json`. Eliminates manual export. Validates changes against careful-not-clever principles.

**Activation:** explicit. Use when pulling fresh data from the sheet or pushing validated changes back.

---

## Multi-LLM orchestrator

This repo defaults to **`sheep` mode** in the orchestrator hosted in [ken](https://github.com/jsschrstrcks1/ken). **Lead model: GPT** (planning), with Claude as validator/safety. Almost unique among sister repos — most have Claude in the lead.

| Skill | Slash command | Usage |
|---|---|---|
| `consult` | `/consult` | `/consult gpt plan "breeding plan for spring lambing"` |
| `orchestrate` | `/orchestrate sheep "<task>"` | Pipeline: Plan (GPT) → Context (Gemini) → Challenge (Grok) → Validate (Claude) → Finalize (GPT) |
| `orchestra` | `/orchestra "<task>"` | Multi-LLM round-robin debate |

**Context boundaries:**

- **SEND**: anonymized flock data, breeding objectives, trait scores, health summaries
- **NEVER SEND**: financial records, location details beyond "Florida"

First-time setup per session:

```bash
bash /home/user/ken/orchestrator/bootstrap-env.sh 2>/dev/null
pip3 install -q -r /home/user/ken/orchestrator/requirements.txt
```

---

## Standard household kit

Common to every sister repo. Canonical versions live in `ken/.claude/skills/`.

| Skill | Activation | One-line |
|---|---|---|
| `brainstorming` | automatic on creative work | Pre-implementation creative exploration. |
| `cognitive-memory` | automatic on session start | Cross-session knowledge persistence. Memory scope: `/sheep`. |
| `executing-plans` | explicit | Use when executing a written plan. |
| `finishing-a-development-branch` | explicit | Decide merge / PR / cleanup. |
| `prompt-optimizer` | automatic on prompt-improvement requests | Optimizes raw prompts. Advisory only. |
| `receiving-code-review` | explicit | Use when receiving review feedback. |
| `requesting-code-review` | explicit | Use when completing tasks before merging. |
| `safety-guard` | automatic on destructive ops | Prevents destructive operations. **Critical here — the data drives breeding decisions.** |
| `security-review` | automatic on auth/secrets/payment | Security checklist + patterns. |
| `security-scan` | explicit | Scans `.claude/` config. |
| `session-checkpoint` | automatic + explicit | Atomic commits, checkpoint summaries, rate-limit recovery. |
| `subagent-driven-development` | explicit | Implementation plans with independent tasks. |
| `systematic-debugging` | automatic on bug/test-failure | Use before proposing fixes. |
| `using-git-worktrees` | explicit | Isolate feature work. |
| `verification-before-completion` | automatic on completion claims | Refuses "complete/fixed/passing" without observed output. |
| `writing-plans` | explicit | Use when you have a spec for a multi-step task. |

Plus `icp-2` (Human-First SEO/AEO 2026) for any content surface.

---

## Image safeguard (mandatory)

All original images are 4032×3024 px or 1320×2868 px — both exceed Claude's 2000 px API limit.

**Always use processed versions from `data/processed/`:**

```bash
# Check image status
python3 scripts/process_images.py --status

# Process all oversized images
python3 scripts/process_images.py

# Process a single image
python3 scripts/process_images.py --file IMG_8560.JPG
```

**NEVER delete any image.** Every image is a primary source document.

---

## Data source priority

When sources disagree, the higher tier wins:

| Priority | Source | Description |
|----------|--------|-------------|
| **1 (HIGHEST)** | Spiral notebook images (PNG/JPG) | Mom's phone app notes — most current, most accurate |
| **2** | `flock_record_v2.xlsx` | Structured spreadsheet |
| **3** | `data.csv` | Historical records |
| **4** | Google Sheet | Breed composition calculations |
| **5** | `Sheep_Breeding_DB_CURRENT_COPY.xlsx` | Mating plans, ram eligibility |

`flock_database.json` is the **derived** source of truth used by tooling. It must always trace back to one of the sources above.

---

## See also

- [`CLAUDE.md`](CLAUDE.md) — agent context (includes pen rosters and aliases)
- [`README.md`](README.md) — repository overview
- [`careful.md`](careful.md) — integrity guardrail (human-readable mirror of the skill)
- `ken` — hosts the orchestrator
