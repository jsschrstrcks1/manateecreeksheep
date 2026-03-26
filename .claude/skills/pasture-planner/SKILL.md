---
name: pasture-planner
description: "Plans pasture rotation for Florida sheep operation. Considers parasite pressure, seasonal grass growth, pen capacity, and rest periods for larval die-off."
version: 1.0.0
---

# Pasture Planner

> *"He makes me lie down in green pastures."* — Psalm 23:2

## Purpose

Florida-specific pasture rotation planning that balances grazing needs with parasite management. The #1 health challenge in this flock is parasites — rotation is the first line of defense.

## When to Fire

- On `/pasture` command
- When discussing rotation, grazing, pen management
- When planning seasonal pen assignments
- When health-tracker flags rising parasite pressure

## Florida Pasture Knowledge

### Warm-Season Grasses (Primary: April–October)
- **Bahiagrass** — drought-tolerant, low maintenance, primary forage
- **Bermudagrass** — higher protein, more aggressive, needs management
- **Limpograss** — good for wet areas, moderate quality

### Cool-Season Options (November–March)
- **Annual ryegrass** — overseeded into Bahia for winter grazing
- **Oats/rye** — temporary winter forage plots

### Parasite Pressure by Season
| Season | Pressure | Why |
|--------|----------|-----|
| Jan-Mar | Low-Moderate | Cool, dry — larvae less active |
| Apr-May | Rising | Warming up, spring rains |
| Jun-Sep | **HIGH** | Hot, wet — peak larval survival |
| Oct-Dec | Declining | Cooling, drying |

## Rotation Rules

### Minimum Rest Period: 60 Days
Haemonchus contortus (barber pole worm) larvae need 60+ days without a host to die off in Florida conditions. **Never return animals to a pasture in less than 60 days.**

### Stocking Density
- Maximum: 6-8 ewes per acre of Bahiagrass
- With lambs: reduce to 4-5 ewes per acre
- Rams: 1 ram per 15-20 ewes

### Rainy Season Protocol (June-September)
- Rotate MORE frequently (every 3-4 weeks vs 4-6 weeks)
- Avoid low/wet areas where larvae concentrate
- Monitor FAMACHA weekly, not bi-weekly
- Consider sacrificial lot for feeding to spare pastures

## Current Pen Structure

| Pen | Ram | Ewes | Notes |
|-----|-----|------|-------|
| 1 | Kaladin | Eclipse, Merrie, Abg, Fm | |
| 2 | Sir Loin | Azure, S2, Lara, Bambii, Pebbles | |
| 3 | Sam | Baby, Zara, Half tail | |
| 4 | Samson | Elsie, Nori, Trouble, Bsoe, Banana | |
| 5 | Rocky/NoriSon | Amber 24, Broken tail, Little daisy | |
| 6 | No ram | Shaggy, Serendipity, S1, Fm1, Fox tail, Circle tail | |

## Rotation Plan Format

```
## Pasture Rotation Plan — [season]

### Schedule
| Week | Pen 1 | Pen 2 | Pen 3 | Pen 4 | Pen 5 | Pen 6 |
|------|-------|-------|-------|-------|-------|-------|
| 1 | Graze | Rest | Graze | Rest | Graze | Rest |
| ... |

### Rest Day Counter
| Pen | Days Resting | Status |
|-----|-------------|--------|
| 1 | 45 | Needs 15 more days |
| 2 | 72 | ✅ Safe to graze |

### Alerts
- [pen] approaching minimum rest period
- [pen] stocking density exceeded
```

## Integration

- **health-tracker** — FAMACHA trends inform rotation urgency
- **breeding-advisor** — pen assignments affect which rams breed which ewes
- **cognitive-memory** — rotation history persists across sessions

---

*Soli Deo Gloria* — Good pasture is good stewardship.
