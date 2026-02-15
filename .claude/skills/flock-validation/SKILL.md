---
name: flock-validation
description: Validate flock database integrity including pedigree consistency, breed composition math, pen assignments, tag uniqueness, and health record completeness.
---

# Flock Database Validation

## Validation Checks

### 1. Required Fields
Every sheep record must have:
- `id` (unique, kebab-case)
- `name` (display name)
- `sex` (ram, ewe, ram_lamb, ewe_lamb, wether, unknown)
- `status` (alive, deceased, sold, unknown)
- `confidence` (high, medium, low)

### 2. Breed Composition
- All breed percentages must sum to 100% (±1% for rounding)
- Each breed must be a recognized breed name
- `coat_type` should match: mostly hair breeds → "hair", mostly wool breeds → "wool", otherwise "mixed"
- `hair_percentage` should be calculable from breed percentages

### 3. Pedigree Integrity
- Every `sire_id` must reference an existing sheep with `sex` = "ram"
- Every `dam_id` must reference an existing sheep with `sex` = "ewe"
- No circular references (A is parent of B is parent of A)
- Sire/dam should be older than offspring (if DOBs are known)

### 4. Tag Uniqueness
- No two **living** sheep should have the same `tag` number
- Deceased sheep may share tags with living sheep (tags get reused)
- Tags noted as "retagged" should be verified

### 5. Pen Assignments
- Every sheep with `status` = "alive" should have a pen assignment
- No deceased sheep should be listed in active pens
- Pen ram assignments should match the pens object

### 6. Health Records
- Sheep on the "weak resistance" list should have `health.weak_resistance` = true
- Treatment dates should be chronological
- FAMACHA scores should be 1–5

## Running Validation

```bash
python3 scripts/validate_flock.py
python3 scripts/validate_flock.py --strict    # Treat warnings as errors
python3 scripts/validate_flock.py --check-references  # Verify sire/dam links
python3 scripts/validate_flock.py --check-images      # Verify image references exist
```

## Severity Levels

- **ERROR**: Must fix before committing (missing required fields, broken references)
- **WARNING**: Should investigate (suspicious breed percentages, missing pen assignments)
- **INFO**: Optional improvements (missing optional fields, incomplete health records)
