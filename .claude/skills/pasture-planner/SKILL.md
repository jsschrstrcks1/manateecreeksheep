---
name: pasture-planner
description: "Plans pasture rotation considering parasite pressure, seasonal grass growth, and pen capacity. Florida-specific with warm-season grass knowledge."
version: 1.0.0
---

# Pasture Planner

> *Tend the land so the land can tend the flock.*

## Purpose

Plans pasture rotation for a Florida sheep operation — balancing parasite control, forage quality, stocking density, and seasonal conditions.

## When to Fire

- On `/pasture` command
- When discussing rotation, grazing, pen management, or forage
- When planning seasonal moves
- After health-tracker flags parasite pressure

## Florida Grass Calendar

### Warm Season (March–October)
- **Bahiagrass**: Primary pasture grass. Drought-tolerant, handles sandy soil. Peak growth June-August.
- **Bermudagrass**: More nutritious than Bahia but needs fertilization. Good for hay.
- **Limpograss**: Wet areas. Maintains quality into fall better than others.

### Cool Season (November–February)
- **Annual ryegrass**: Over-seed into Bahia in October. Provides winter forage.
- **Oats/rye**: Emergency winter forage. Plant by mid-October in Florida.
- **Clover**: Nitrogen-fixing, good companion. Crimson clover for winter, white clover perennial.

## Rotation Rules

### Parasite Control
- **Minimum rest period: 60 days** between grazings on the same pasture
- Parasite larvae survive 3-6 weeks on pasture in Florida heat
- Larvae climb grass blades in morning dew — graze after 10 AM when possible
- Never graze below 3 inches — larvae concentrate in bottom 2 inches
- After deworming, move to clean pasture within 24 hours

### Stocking Density
- **Rule of thumb**: 5-7 sheep per acre on improved Bahia in Florida
- Adjust down during drought or when parasite pressure is high
- Ewes with lambs need 30% more space
- Rams in breeding pens: 1/4 acre minimum

### Current Pen Structure

| Pen | Ram | Ewes | Approx Size |
|-----|-----|------|-------------|
| 1 | Kaladin | Eclipse, Merrie, Abg, Fm | — |
| 2 | Sir Loin | Azure, S2, Lara, Bambii, Pebbles | — |
| 3 | Sam | Baby, Zara, Half tail | — |
| 4 | Samson | Elsie, Nori, Trouble, Bsoe, Banana | — |
| 5 | Rocky/NoriSon | Amber 24, Broken tail, Little daisy | — |
| 6 | No ram | Shaggy, Serendipity, S1, Fm1, Fox tail, Circle tail | — |

## Seasonal Rotation Plan

### Rainy Season (June–September)
- **HIGH parasite alert**: Warm + wet = larval explosion
- Increase rotation frequency (move every 2-3 weeks)
- Keep grass height above 4 inches
- Consider temporary sacrifice area during heavy rains
- Run FAMACHA checks every 2 weeks

### Dry Season (October–May)
- **Lower parasite pressure**: Can extend rotation to 4-6 weeks
- Over-seed ryegrass in October for winter forage
- Stockpile Bahia in September for fall grazing
- FAMACHA checks monthly

## Rotation Report Format

```
## Pasture Rotation Plan — [season/date]

| Pen | Current Pasture | Last Grazed | Rest Days | Next Move | Notes |
|-----|----------------|-------------|-----------|-----------|-------|

### Forage Status
| Pasture | Grass Height | Condition | Forage Type |
|---------|-------------|-----------|-------------|

### Parasite Risk: [LOW / MODERATE / HIGH]
Reason: [season, recent rain, recent FAMACHA data]
```

## Integration

- **health-tracker** — parasite data informs rotation urgency
- **breeding-advisor** — pregnant ewes need best pasture
- **cognitive-memory** — remember rotation history across sessions
- **flock-validation** — pen assignments must match rotation plan

---

*Soli Deo Gloria* — The land is the Lord's. We steward it faithfully.
