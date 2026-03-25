---
name: health-tracker
description: "Tracks FAMACHA scores over time per animal, flags worsening trends, identifies weak resistance patterns before they become critical. Wraps scripts/parasite_resistance.py."
version: 1.0.0
---

# Health Tracker

> *"Know well the condition of your flocks, and give attention to your herds."* — Proverbs 27:23

## Purpose

Tracks animal health trends over time — especially FAMACHA scores and parasite resistance. Flags animals trending toward anemia before they're critical. Informs breeding decisions.

## When to Fire

- On `/health` command
- When discussing FAMACHA, deworming, or animal health
- After transcribing health records from spiral notebook images
- When evaluating which animals to cull

## FAMACHA Scale

| Score | Color | Meaning | Action |
|-------|-------|---------|--------|
| 1 | Red | Healthy | No treatment needed |
| 2 | Red-pink | Acceptable | Monitor |
| 3 | Pink | Borderline | Consider treatment |
| 4 | Pink-white | Anemic | Treat immediately |
| 5 | White | Severely anemic | Treat + evaluate for culling |

## Tracking Protocol

After each FAMACHA check, encode:

```bash
python3 /home/user/ken/orchestrator/memory_ops.py encode sheep fact \
  "FAMACHA check 2026-03-25: Kaladin=1, Eclipse=2, Azure=3 (trending up from 2), Baby=4 (treat now)" \
  --tags famacha,health,2026-03-25
```

## Trend Analysis

### Worsening Animals
Flag any animal whose FAMACHA score has increased by 2+ points over 3 checks, or any animal consistently at 3+.

### Known Weak Resistance List
These animals have demonstrated poor parasite resistance and should be monitored closely:
**Active:** GG, Azure, Rocky, Dorper 23 & 25, Circle Tail, W140, FM1, Baby, Bella, FM
**Deceased (pedigree relevant):** Shaggy, Butter Ball, Skitters, W136, Samson, Unnamed

### Seasonal Patterns
- **June-September**: Peak parasite pressure (rainy season, warm soil). Expect more 3+ scores.
- **December-February**: Lower pressure. Good baseline for identifying truly resistant animals.
- **Post-rain**: Check within 2 weeks of heavy rain. Parasite larvae hatch.

## Script Integration

```bash
# Run parasite resistance analysis
python3 scripts/parasite_resistance.py

# Run full flock validation (includes health checks)
python3 scripts/validate_flock.py
```

## Health Report Format

```
## Flock Health Report — [date]

### FAMACHA Summary
| Score | Count | Animals |
|-------|-------|---------|
| 1 | [N] | [names] |
| 2 | [N] | [names] |
| 3 | [N] | [names] — MONITOR |
| 4 | [N] | [names] — TREAT |
| 5 | [N] | [names] — CRITICAL |

### Trending Worse (vs. last check)
| Animal | Previous | Current | Trend |
|--------|----------|---------|-------|

### Treatment Log
| Animal | Treatment | Date | Response |
|--------|----------|------|----------|

### Breeding Implications
- [Animals with poor health trends should not be bred]
- [Strong health performers → priority breeding candidates]
```

## Integration

- **breeding-advisor** — health data informs breeding recommendations
- **flock-validation** — health records must be consistent
- **image-transcription** — health records from spiral notebooks feed this skill
- **cognitive-memory** — health trends persist across sessions

---

*"The LORD is my shepherd; I shall not want."* — Psalm 23:1

*Soli Deo Gloria* — We steward their health for God's glory.
