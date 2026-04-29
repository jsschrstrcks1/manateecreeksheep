# Manatee Creek Sheep

Flock management, breeding program, and health tracking for a multi-breed
sheep operation in Florida.

> **Soli Deo Gloria.** We tend these sheep as stewards, not owners.

---

## Table of Contents

- [Mission](#mission)
- [Breeding Goals](#breeding-goals)
- [Key Genetics Notes](#key-genetics-notes)
- [Repository Contents](#repository-contents)
- [Data Sources (Priority Order)](#data-sources-priority-order)
- [Quick Start](#quick-start)
- [The 7-Pen Pipeline](#the-7-pen-pipeline)
- [FAMACHA & Health Tracking](#famacha--health-tracking)
- [Breeds in the Flock](#breeds-in-the-flock-22)
- [Working with Records](#working-with-records)
- [Skills & AI Assistance](#skills--ai-assistance)
- [Multi-LLM Integration](#multi-llm-integration)
- [Privacy & Safety](#privacy--safety)
- [License](#license)

---

## Mission

Produce sheep that are **more parasite resistant**, while maintaining
**meat quality** and **milk production**, through strategic crossbreeding
of 22+ breeds with FAMACHA-driven selection.

Every breeding and culling decision is rooted in real, verified data.
Records are kept carefully — never cleverly. The flock book takes priority
over any spreadsheet, app, or AI summary.

---

## Breeding Goals

Selection priority is **performance-based**, in this order:

1. **Parasite resistance** — Primary criterion. FAMACHA scoring drives
   every breeding and culling decision.
2. **Hair coat** — Moving toward hair sheep for Florida's climate (less
   maintenance, better heat tolerance).
3. **Breed character** — Composite goal: hardy, hairy, meaty,
   parasite-resistant.
4. **Meat quality** — Dorper and Dorper-Awassi crosses produce the
   meatiest animals.
5. **Milk production** — Awassi genetics carry the most milk in the flock.
6. **Hybrid vigor** — 22 breed crosses give diverse genetic resistance.

## Key Genetics Notes

- **Most parasite resistant:** Kelsier (Katahdin)
- **Most milky:** Awassi and Awassi crosses
- **Meatiest:** Dorper-Awassi cross
- Former owners reported minimal parasite issues — this has proved mostly
  true in field observation since takeover.

---

## Repository Contents

```
manateecreeksheep/
├── data/
│   ├── flock_database.json            # Complete flock database (sheep, pedigrees, health)
│   └── processed/                     # AI-readable image versions (≤1800 px)
├── scripts/
│   ├── process_images.py              # Resize oversized images for AI processing
│   └── validate_flock.py              # Validate database integrity
├── .claude/                           # Claude Code configuration
│   ├── settings.json                  # Hooks and permissions
│   ├── skill-rules.json               # Skill auto-activation rules
│   └── skills/
│       ├── careful-not-clever/        # Integrity guardrail
│       ├── image-transcription/       # Notebook transcription guide
│       ├── flock-validation/          # Database validation guide
│       ├── breeding-advisor/          # Mating evaluation
│       ├── pasture-planner/           # Rotation planning
│       ├── health-tracker/            # FAMACHA trend tracking
│       ├── google-sheets-sync/        # Spreadsheet ↔ JSON bridge
│       └── google-sheets-migration/   # Tab migration helper
├── CLAUDE.md                          # AI assistant context
├── careful.md                         # Integrity guardrail (readable reference)
├── data.csv                           # Historical flock records
├── flock_record_v2.xlsx               # Structured flock record spreadsheet
├── Sheep_Breeding_DB_CURRENT_COPY.xlsx # Breeding database with mating plans
├── IMG_8560–8615.JPG                  # Notebook page photos (handwritten)
├── IMG_8616–8643.PNG                  # Phone-app notes (treatments, pens, weights)
└── LICENSE                            # GNU AGPL v3
```

---

## Data Sources (Priority Order)

The spiral notebook is canonical. When sources disagree, the notebook
wins.

| Priority | Source | Description |
|---|---|---|
| 1 | Spiral notebook (PNG images) | Most current, most accurate |
| 2 | `flock_record_v2.xlsx` | Structured spreadsheet |
| 3 | `data.csv` | Historical records |
| 4 | Google Sheet (linked via `google-sheets-sync`) | Breed composition calculations |
| 5 | `Sheep_Breeding_DB.xlsx` | Mating plans and rules |

`flock_database.json` is the **derived** source of truth used by tooling
— it must always trace back to one of the sources above.

---

## Quick Start

```bash
# Process oversized images for AI reading
python3 scripts/process_images.py

# Validate the flock database
python3 scripts/validate_flock.py
```

Validation runs a strict pass over `data/flock_database.json` and reports:

- Pedigree consistency (parents must exist; no cycles)
- Breed composition math (percentages must sum within tolerance)
- Pen assignments (every active sheep belongs to exactly one pen)
- Tag uniqueness
- Health record completeness (FAMACHA must have date + score)

---

## The 7-Pen Pipeline

Breeding is organized as a **closed-loop 7-pen pipeline** moving sheep
toward the composite goal. The `breeding-advisor` skill evaluates every
proposed mating against the pipeline rules.

Pens cycle from quarantine/observation through selection, breeding,
gestation, lambing, and grow-out. Movement between pens is recorded in
the notebook first, then propagated to `flock_database.json`.

The `pasture-planner` skill schedules rotation considering:

- Parasite pressure (worm larvae viability by season)
- Florida grass-growth curve
- Pen carrying capacity
- Required rest periods for larval die-off

---

## FAMACHA & Health Tracking

FAMACHA scoring (1–5, eyelid color → anemia level) is the primary health
signal. The `health-tracker` skill maintains per-animal trend lines and
flags any sheep heading toward anemia *before* it becomes critical.

Treatment records (dewormer, dose, date, weight, withdrawal period) are
captured in the phone-app notebook (`IMG_8616+.PNG`) and transcribed to
JSON via the `image-transcription` skill.

Animals with chronically poor FAMACHA are removed from the breeding
pipeline regardless of other traits. **Parasite resistance comes first.**

---

## Breeds in the Flock (22+)

**Hair:** Katahdin, Dorper, White Dorper, St Croix, Barbados Blackbelly,
American Blackbelly, Wiltshire Horn

**Wool:** Suffolk, Hampshire, Cotswold, Tunis, Gulf Coast Native

**Dual-purpose:** St Augustine, Cracker, Awassi, East Friesian

**Other:** Jacob, Babydoll, Karakul

As of February 2026, the flock includes ~50+ active animals across 6 pens
plus a goose pen, with the 2026 lambing season in progress.

---

## Working with Records

### Adding a notebook page

1. Photograph the page; drop the file into the repo root.
2. Run `python3 scripts/process_images.py` to produce an AI-readable copy
   in `data/processed/`.
3. Use the `image-transcription` skill (or transcribe by hand) to extract
   structured data into `data/flock_database.json`.
4. Run `python3 scripts/validate_flock.py` and fix any errors before
   committing.

### Editing an animal record

Edit `data/flock_database.json` directly. The `careful-not-clever` skill
enforces that every change traces back to a notebook entry, treatment
record, or measurement. Speculative or inferred edits must be flagged
explicitly in the record.

### Syncing with Google Sheets

Use the `google-sheets-sync` skill to push or pull breed-composition
calculations between the spreadsheet and `flock_database.json`. The skill
validates math both ways and refuses to overwrite divergent records
without explicit confirmation.

---

## Skills & AI Assistance

The `.claude/skills/` directory bundles the helpers used during sessions
on this repo:

| Skill | Purpose |
|---|---|
| `careful-not-clever` | Integrity guardrail. Active on every file modification. |
| `image-transcription` | Transcribe notebook pages and phone-app screenshots. |
| `flock-validation` | Validate database integrity (`validate_flock.py` runner). |
| `breeding-advisor` | Evaluate proposed matings against the pipeline. |
| `pasture-planner` | Plan pasture rotation by season and parasite load. |
| `health-tracker` | FAMACHA trends, anemia early warning. |
| `google-sheets-sync` | Bidirectional sync between spreadsheet and JSON. |
| `google-sheets-migration` | Migrate the legacy 113-tab spreadsheet to the new 26-tab structure. |

---

## Multi-LLM Integration

This repo defaults to **`sheep` mode** in the multi-LLM orchestrator
hosted in [ken](https://github.com/jsschrstrcks1/ken).

In `sheep` mode the lead planner is **GPT** (multi-step constraint
reasoning), with **Gemini**, **Grok**, and **Claude** acting as
validators against breeding rules and integrity guardrails.

| Skill | Usage |
|---|---|
| `/consult` | `/consult gpt structure "evaluate this mating"` |
| `/orchestrate sheep "<task>"` | Full pipeline: GPT plans, validators check, Claude integrates |
| Cognitive memory | Scope `/manateecreeksheep` |

#### Setup (per session)

```bash
pip3 install -q -r /home/user/ken/orchestrator/requirements.txt
```

---

## Privacy & Safety

- The flock database contains tag numbers, dates, and pedigrees but no
  customer or personal information.
- Image files include the operator's notebook handwriting; treat as
  semi-private.
- Never push speculative breeding results as fact. Use the `confidence`
  field in records when uncertainty exists.
- Never run scripts that mutate `flock_database.json` without first
  running `validate_flock.py` against the prior version.

---

## License

GNU Affero General Public License v3.0 — see `LICENSE`.

---

*Everything we do here is for the glory of God.*
