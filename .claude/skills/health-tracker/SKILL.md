---
name: health-tracker
description: "Tracks FAMACHA scores and health trends per animal over time. Flags animals trending toward anemia before they're critical. Links health data to breeding decisions."
version: 1.0.0
---

# Health Tracker

> *"The LORD is my shepherd."* — Psalm 23:1

## Purpose

Monitors individual animal health over time, focusing on FAMACHA trends and parasite resistance. Catches problems before they become emergencies.

## When to Fire

- On `/health` command
- When discussing FAMACHA scores, deworming, or animal health
- After transcribing health records from spiral notebook images
- When breeding-advisor needs health context

## FAMACHA Scale

| Score | Color | Meaning | Action |
|-------|-------|---------|--------|
| 1 | Red | Healthy | None needed |
| 2 | Red-Pink | Acceptable | Monitor |
| 3 | Pink | Borderline | Consider treatment |
| 4 | Pink-White | Anemic | Treat immediately |
| 5 | White | Severely anemic | Emergency treatment, evaluate culling |

## Trend Detection

Flag animals whose FAMACHA scores are **worsening across consecutive checks**:
- 1→2→3 across 3 checks = **trending down, monitor closely**
- Consistent 3+ = **chronic weakness, breeding decision needed**
- Any score of 4-5 = **immediate flag**

## Known Weak Resistance Animals

These animals have documented poor parasite resistance:
**Active:** GG, Azure, Rocky, Dorper 23, Dorper 25, Circle Tail, W140, FM1, Baby, Bella, FM
**Deceased (pedigree relevant):** Shaggy, Butter Ball, Skitters, W136, Samson, Unnamed

## Data Sources

- `data/flock_database.json` — structured health records
- `scripts/parasite_resistance.py` — calculates resistance scores
- Spiral notebook images (IMG_8560–8643) — primary source for FAMACHA checks

## Health Report Format

```
## Flock Health Report — [date]

### Animals of Concern
| Animal | Tag | Pen | Last FAMACHA | Trend | Action |
|--------|-----|-----|-------------|-------|--------|

### Flock Summary
- Average FAMACHA: [score]
- Animals at 1-2: [count] ([%])
- Animals at 3: [count] ([%])
- Animals at 4-5: [count] ([%])

### Breeding Impact
- [animal] trending weak → exclude from breeding / reduce offspring priority
```

## Integration

- **breeding-advisor** — health trends inform which animals to breed/cull
- **flock-validation** — validates health record completeness
- **image-transcription** — new health data comes from notebook transcription
- **cognitive-memory** — trend observations persist across sessions

---

*Soli Deo Gloria* — Good stewardship means catching problems early.
