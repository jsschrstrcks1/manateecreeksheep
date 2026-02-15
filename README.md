# Manatee Creek Sheep

Flock management, breeding program, and health tracking for a multi-breed sheep operation in Florida.

## Mission

Produce sheep that are **more parasite resistant**, while maintaining **meat quality** and **milk production**, through strategic crossbreeding of 22+ breeds with FAMACHA-driven selection.

**Soli Deo Gloria** — We tend these sheep as stewards, not owners.

## Breeding Goals

1. **Parasite Resistance** — Primary selection criterion. FAMACHA scoring drives every breeding and culling decision.
2. **Meat Quality** — Dorper and Dorper-Awassi crosses produce the meatiest animals.
3. **Milk Production** — Awassi genetics are the most milky breed in the flock.
4. **Hair Coat** — Moving toward hair sheep for Florida's climate (less maintenance, better heat tolerance).
5. **Hybrid Vigor** — 22 breed crosses provide diverse genetic resistance.

### Key Genetics Notes

- **Most parasite resistant:** Kelsier (Katahdin)
- **Most milky:** Awassi and Awassi crosses
- **Meatiest:** Dorper-Awassi cross
- Former owners reported minimal parasite issues — this has proved mostly true

## Repository Contents

```
manateecreeksheep/
├── data/
│   ├── flock_database.json          # Complete flock database (all sheep, pedigrees, health)
│   └── processed/                   # AI-readable versions of images (≤1800px)
├── scripts/
│   ├── process_images.py            # Resize oversized images for AI processing
│   └── validate_flock.py            # Validate database integrity
├── .claude/                         # Claude Code configuration
│   ├── settings.json                # Hooks and permissions
│   ├── skill-rules.json             # Skill auto-activation rules
│   └── skills/                      # Skill documentation
│       ├── careful-not-clever/      # Integrity guardrail
│       ├── image-transcription/     # Notebook transcription guide
│       └── flock-validation/        # Database validation guide
├── CLAUDE.md                        # AI assistant context and guidelines
├── careful.md                       # Integrity guardrail (readable reference)
├── data.csv                         # Historical flock records
├── flock_record_v2.xlsx             # Structured flock record spreadsheet
├── Sheep_Breeding_DB_CURRENT_COPY.xlsx  # Breeding database with mating plans
├── IMG_8560–8615.JPG                # Handwritten notebook pages with sheep photos
├── IMG_8616–8643.PNG                # Phone app notes (treatments, measurements, pens)
└── LICENSE                          # GNU AGPL v3
```

## Data Sources (Priority Order)

| Priority | Source | Description |
|----------|--------|-------------|
| 1 | Spiral notebook (PNG images) | Most current, most accurate |
| 2 | flock_record_v2.xlsx | Structured spreadsheet |
| 3 | data.csv | Historical records |
| 4 | Google Sheet | Breed composition calculations |
| 5 | Sheep_Breeding_DB.xlsx | Mating plans and rules |

## Quick Start

```bash
# Process oversized images for AI reading
python3 scripts/process_images.py

# Validate the flock database
python3 scripts/validate_flock.py
```

## Breeds in the Flock (22+)

**Hair:** Katahdin, Dorper, White Dorper, St Croix, Barbados Blackbelly, American Blackbelly, Wiltshire Horn
**Wool:** Suffolk, Hampshire, Cotswold, Tunis, Gulf Coast Native
**Dual-purpose:** St Augustine, Cracker, Awassi, East Friesian
**Other:** Jacob, Babydoll, Karakul

## Flock Size

As of February 2026, the flock includes ~50+ active animals across 6 pens plus a goose pen, with the 2026 lambing season in progress.

## License

GNU Affero General Public License v3.0
