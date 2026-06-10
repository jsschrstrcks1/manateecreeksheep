# EBV Pipeline — How It Works

A flock-internal Estimated Breeding Value pipeline that can be anchored
to NSIP data when available.

> **Honest scope:** This is NOT a substitute for full NSIP. NSIP uses
> national contemporary-group data and full BLUP variance components
> across thousands of flocks. We use within-flock phenotypic deviations
> + pedigree relationships + (optional) NSIP-anchored ancestor EBVs
> propagated down through Wright's path coefficients. Accuracy is
> roughly 70-80% of a real multi-flock NSIP run when anchors are
> available; lower when running purely on internal data.

---

## Quick start

```bash
# Run on all animals
python3 scripts/ebv/compute_ebvs.py

# With NSIP anchor data
python3 scripts/ebv/compute_ebvs.py --nsip data/ebv/nsip_anchors.json

# Focused report on one animal
python3 scripts/ebv/compute_ebvs.py --animal centralia-lamb-2026
```

Outputs land in `data/ebv/`:
- `ebvs_<date>.json` — per-animal per-trait values + method + accuracy
- `rankings_<date>.md` — top-20 alive animals per trait

---

## Pipeline architecture

```
scripts/ebv/
├── pedigree.py      Wright's tabular method (A-matrix, F, path coef)
├── traits.py        Trait definitions + heritabilities (literature)
├── extract.py       Pull phenotypes from data/flock_database.json
├── estimate.py      EBV math (BLUP-light, mid-parent, NSIP-anchored)
└── compute_ebvs.py  CLI + output formatting
```

---

## Traits tracked

| Code | Trait | h² | Units | Direction |
|------|-------|----|----|-----------|
| PR | Parasite Resistance | 0.25 | FAMACHA-inverted | higher = more resistant |
| WWT | Weaning Weight | 0.30 | lb | higher = better |
| PWT | Post-Weaning Weight | 0.35 | lb | higher = better |
| ADG | Average Daily Gain | 0.30 | lb/day | higher = better |
| NLW | Lambs Weaned per Lambing | 0.10 | lambs | higher = better |
| MILK | Milk Yield (inferred) | 0.20 | ADG-inferred | higher = better |

Heritability estimates are mid-range values from published hair-sheep
meta-analyses (Notter 2012, Vanimisetti 2004, Borg 2009). Citations in
`scripts/ebv/traits.py`.

---

## EBV calculation methods (in priority order)

For each animal we choose the highest-accuracy method that applies:

1. **NSIP-anchored** (accuracy ~0.95)
   `EBV = NSIP value from the anchor file`

2. **BLUP-light** (accuracy ~0.85)
   Animal has own phenotype.
   `EBV = h² × (own - contemporary_group_mean) + (1 - h²) × mid_parent_EBV`

3. **Mid-parent** (accuracy 0.35-0.75)
   No own phenotype but parents have EBVs.
   `EBV = 0.5 × (sire_EBV + dam_EBV)`

4. **Default zero** (accuracy 0)
   No data for self or parents. Falls back to flock mean (no signal).

The pipeline iterates until convergence so that mid-parent EBVs
propagate down to grand-offspring etc.

---

## Pedigree math

Henderson's tabular method computes the **numerator relationship
matrix** A, where:

- `A(i, i) = 1 + F_i` (self-relationship with inbreeding correction)
- `A(i, j) = 0.5 × (A(sire_i, j) + A(dam_i, j))` when i is younger
- `F_i = 0.5 × A(sire_i, dam_i)` (inbreeding coefficient)

Path coefficient for propagating ancestor EBVs:
`path_coef(ancestor, descendant) = 0.5 × A(ancestor, descendant)`

---

## NSIP anchor file format

```json
{
  "_comment": "Optional comments (keys starting with _ are skipped)",
  "sheep_id_in_db": {
    "PR": 0.45,
    "WWT": 3.2,
    "PWT": 4.1,
    "ADG": 0.05,
    "NLW": 0.15
  }
}
```

EBVs are deviations from the NSIP reference population mean.
**Positive = better than NSIP-population average.**

Example file: `data/ebv/nsip_anchors_example.json` (PLACEHOLDER values
only — replace with actual NSIP retrievals).

---

## Where NSIP data comes from

When the operator gets access to NSIP records for specific ancestors:

1. Go to nsip.org or the KHSI database
2. Look up the named ancestor (e.g., CENTRALIA SHU 3320)
3. Note their EBVs for the traits you care about (FEC, WWT, PWT, NLW, MWT)
4. Add entries to the anchor JSON
5. Rerun the pipeline

The pipeline will use those values directly for the ancestors and
propagate them down to the lamb via Wright's path coefficients.

---

## Limitations to know

- **Contemporary group is approximate.** We use sex + birth-year + pen
  as the group key. Real NSIP uses farm + season + management cohort.
- **No variance component estimation.** We use literature heritabilities,
  not flock-specific estimates (would need ≥3 years of structured
  recording).
- **No selection-index multi-trait weighting.** Each trait is computed
  independently. A future enhancement could combine traits into a
  weighted index (e.g., 0.5 PR + 0.3 ADG + 0.2 NLW).
- **Missing-data tolerant but lossy.** Sheep without phenotype AND
  without parents in the pedigree get EBV = 0, which conflates "no
  data" with "average."
- **Lambs born this year have F=0 unless full pedigree is recorded.**
  Our DB has many missing grand-ancestors, so true inbreeding may be
  underestimated.

---

## Validation checks built in

- Trait extractor reports counts so you can see how much real data each
  trait has (`python3 scripts/ebv/extract.py`).
- Pedigree module reports A and F for a few known animals on every run
  (`python3 scripts/ebv/pedigree.py`).
- Each EBV record carries `method` and `accuracy` fields so you can
  see at a glance whether to trust it.
