#!/usr/bin/env python3
"""scrapie_genotype.py — PRNP scrapie-genotype schema, classification, and mating predictor (MCS-15).

Classical scrapie susceptibility in sheep is governed by the PRNP gene, primarily codon 171:
the R allele confers resistance, the Q allele susceptibility. The three common genotypes:
    171 RR  -> resistant                 (the goal of the USDA National Scrapie Eradication Program)
    171 QR  -> reduced susceptibility
    171 QQ  -> susceptible
Codons 136 (A/V) and 154 (R/H) modify risk (the 136V/154R/171Q "VRQ" haplotype is the highest-risk
one); they are STORED here but the primary, settled advisory is on codon 171. Uncommon alleles
(H, K at 171) are not force-classified — the tool flags them for lab/vet classification rather than
guessing an effect.

This module authors NO genotype for any animal — genotype is lab data. It provides the schema, a
validator, the susceptibility classification, and a Mendelian mating PREDICTOR that is complete and
correct on any entered or hypothetical genotypes (each parent passes one 171 allele; offspring are
the Punnett combination). With no genotypes on file yet, the flock census honestly reads "unknown".

SHAPE — a scrapie_genotype object on the sheep:
    {codon_136, codon_154, codon_171, method, lab, date, source}

    python3 scripts/scrapie_genotype.py                    # flock genotype census (+ breeding note)
    python3 scripts/scrapie_genotype.py --cross RR QQ       # predict a mating's offspring at codon 171
    python3 scripts/scrapie_genotype.py --json
"""
import argparse
import json
import sys
from collections import Counter
from datetime import datetime
from itertools import product
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "flock_database.json"

ALLELES_171 = {"R", "Q", "H", "K"}     # R resistant, Q susceptible; H/K uncommon (flag, don't classify)
ALLELES_136 = {"A", "V"}
ALLELES_154 = {"R", "H"}
_GENO_KEYS = {"codon_136", "codon_154", "codon_171", "method", "lab", "date", "source"}


def _iso(d):
    try:
        return datetime.strptime(str(d), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def _norm171(geno):
    """Normalize a codon-171 genotype string ('QR','RQ','R/Q','rq') to a sorted 2-allele tuple, or
    None if it is not two known alleles."""
    if not geno:
        return None
    s = str(geno).upper().replace("/", "").replace(" ", "").replace("-", "")
    if len(s) != 2 or any(a not in ALLELES_171 for a in s):
        return None
    return tuple(sorted(s))


def classify_171(geno):
    """Susceptibility class for a codon-171 genotype. Honest about uncommon alleles."""
    t = _norm171(geno)
    if t is None:
        return "unknown"
    a, b = t
    if {a, b} - {"R", "Q"}:
        return "uncommon_allele_consult_lab"   # H or K present — do not guess an effect
    if a == b == "R":
        return "resistant"
    if a == b == "Q":
        return "susceptible"
    return "reduced_susceptibility"            # QR


def validate_genotype(sheep):
    g = sheep.get("scrapie_genotype")
    if g is None:
        return []
    issues = []
    where = f"{sheep.get('id')}#scrapie_genotype"
    if not isinstance(g, dict):
        return [f"{where}: not an object"]
    extra = set(g) - _GENO_KEYS
    if extra:
        issues.append(f"{where}: unknown key(s) {sorted(extra)}")
    if g.get("codon_171") is not None and _norm171(g.get("codon_171")) is None:
        issues.append(f"{where}: codon_171 {g.get('codon_171')!r} is not two alleles from {sorted(ALLELES_171)}")
    for codon, valid in (("codon_136", ALLELES_136), ("codon_154", ALLELES_154)):
        v = g.get(codon)
        if v is not None:
            s = str(v).upper().replace("/", "").replace(" ", "")
            if len(s) != 2 or any(a not in valid for a in s):
                issues.append(f"{where}: {codon} {v!r} not two alleles from {sorted(valid)}")
    if g.get("date") is not None and _iso(g.get("date")) is None:
        issues.append(f"{where}: date {g.get('date')!r} unparseable")
    return issues


def cross_171(sire_geno, dam_geno):
    """Mendelian offspring genotype + susceptibility distribution at codon 171. Each parent passes
    one allele with prob 1/2; offspring are the Punnett combinations. Returns None if either parent
    genotype is not two known alleles."""
    sp, dp = _norm171(sire_geno), _norm171(dam_geno)
    if sp is None or dp is None:
        return None
    geno_counts = Counter()
    for a, b in product(sp, dp):
        geno_counts["".join(sorted((a, b)))] += 1
    n = sum(geno_counts.values())
    genotypes = {g: round(c / n, 3) for g, c in sorted(geno_counts.items())}
    classes = Counter()
    for g, c in geno_counts.items():
        classes[classify_171(g)] += c
    class_probs = {k: round(v / n, 3) for k, v in classes.items()}
    return {"sire_171": "".join(sp), "dam_171": "".join(dp),
            "offspring_genotypes": genotypes, "offspring_classes": class_probs}


def flock_census(db):
    rows = []
    for s in db.get("sheep", []):
        g = s.get("scrapie_genotype")
        g = g if isinstance(g, dict) else {}   # a malformed non-dict must not abort the whole census
        rows.append({"id": s["id"], "name": s.get("name"),
                     "codon_171": g.get("codon_171"), "class": classify_171(g.get("codon_171"))})
    return rows


def main():
    ap = argparse.ArgumentParser(description="PRNP scrapie genotype: schema, classification, mating predictor")
    ap.add_argument("--cross", nargs=2, metavar=("SIRE_171", "DAM_171"),
                    help="predict offspring at codon 171 for a mating (e.g. --cross RR QQ)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.cross:
        r = cross_171(args.cross[0], args.cross[1])
        if args.json:
            print(json.dumps(r, indent=2)); return 0
        if r is None:
            print("cannot predict: a codon-171 genotype must be two alleles from R/Q/H/K (e.g. RR, QR, QQ)")
            return 1
        print(f"Mating at codon 171: sire {r['sire_171']} x dam {r['dam_171']}\n")
        print("  offspring genotypes:")
        for g, p in r["offspring_genotypes"].items():
            print(f"    {g}  {p*100:g}%  ({classify_171(g)})")
        print("  offspring susceptibility:")
        for c, p in r["offspring_classes"].items():
            print(f"    {c:26} {p*100:g}%")
        print("\n  Codon 171: R resistant, Q susceptible. Selecting RR sires drives the flock toward"
              "\n  RR (the USDA NSEP goal). Advisory — the operator/vet decides; lab genotype required.")
        return 0

    db = json.loads(DB_PATH.read_text())
    rows = flock_census(db)
    issues = []
    for s in db["sheep"]:
        issues += validate_genotype(s)
    if args.json:
        print(json.dumps({"census": rows, "validation_issues": issues}, indent=2)); return 0
    counts = Counter(r["class"] for r in rows)
    typed = [r for r in rows if r["codon_171"]]
    print(f"Scrapie genotype census — {len(rows)} animals; {len(typed)} with a codon-171 genotype on file\n")
    for k, v in counts.most_common():
        print(f"  {k:28} {v}")
    if typed:
        print("\n  Genotyped animals:")
        for r in typed:
            print(f"    {(r['name'] or r['id'])[:28]:28} 171 {r['codon_171']}  ({r['class']})")
    else:
        print("\n  No codon-171 genotypes recorded yet. Genotype is lab data (blood/tissue); enter it in"
              "\n  scrapie_genotype.codon_171 per animal to enable RR-toward selection and mating prediction.")
    if issues:
        print(f"\nValidation issues ({len(issues)}):")
        for i in issues:
            print(f"  {i}")
    print("\n  Read-only; authors no genotype. Predictor: scripts/scrapie_genotype.py --cross RR QQ")
    return 0


if __name__ == "__main__":
    sys.exit(main())
