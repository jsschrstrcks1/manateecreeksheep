"""Scrapie genotype tracking + pedigree-derived possibilities (MCS-15). Pure, no I/O.

Soli Deo Gloria.

Standard, public-domain sheep genetics (the USDA National Scrapie Eradication Program
is built on it): resistance is governed by PRNP codons 136 (A/V), 154 (R/H), 171
(R/Q — R confers resistance). Haplotypes run ARR (most resistant) .. VRQ (most
susceptible).

Schema (ADDITIVE):
    sheep["genetics"]["prnp"] = {
      "codon_136": "AA"|"AV"|"VV",  "codon_154": "RR"|"RH"|"HH",
      "codon_171": "RR"|"QR"|"QQ",
      "source": "lab name / test id / 'pedigree-derived'",  "tested": date,
      "confidence": "tested"|"derived"
    }
Only codon_171 is required to be useful; a record may carry just that.

DISCIPLINE: a derivation from pedigree yields a POSSIBILITY SET, never a single
asserted genotype — offspring_possibilities returns every Mendelian outcome with
probabilities; writing one of them into a record as fact requires a lab test.
"""
import itertools

VALID = {"codon_136": {"AA", "AV", "VV"},
         "codon_154": {"RR", "RH", "HH"},
         "codon_171": {"RR", "QR", "QQ"}}

RESISTANCE_171 = {"RR": "resistant", "QR": "carrier (partially resistant)",
                  "QQ": "susceptible"}


def validate_prnp(p):
    """List of problems for one prnp record (empty = valid)."""
    probs = []
    if not isinstance(p, dict):
        return [f"prnp is not an object: {p!r}"]
    for codon, vals in VALID.items():
        v = p.get(codon)
        if v is not None and v not in vals:
            probs.append(f"{codon} value {v!r} not in {sorted(vals)} "
                         f"(alleles alphabetized, e.g. 'QR' never 'RQ')")
    if not any(p.get(c) for c in VALID):
        probs.append("prnp record carries no codon at all")
    if p.get("confidence") not in (None, "tested", "derived"):
        probs.append(f"confidence {p.get('confidence')!r} not tested/derived")
    return probs


def offspring_possibilities(sire_genotype, dam_genotype, codon="codon_171"):
    """Mendelian outcome probabilities for one codon: {'QR': 0.5, ...}.
    Returns None if either parent's codon is unknown — no fabricated genetics."""
    sg, dg = (sire_genotype or {}).get(codon), (dam_genotype or {}).get(codon)
    if not sg or not dg or sg not in VALID[codon] or dg not in VALID[codon]:
        return None
    out = {}
    for a, b in itertools.product(sg, dg):
        g = "".join(sorted(a + b))
        out[g] = out.get(g, 0) + 0.25
    return out


def resistance_note(genotype_171):
    return RESISTANCE_171.get(genotype_171, "unknown")


def validate_genetics(db):
    issues = []
    for s in db.get("sheep", []):
        p = (s.get("genetics") or {}).get("prnp")
        if p is None:
            continue
        for prob in validate_prnp(p):
            issues.append(f"ERROR [{s['id']}]: prnp — {prob}")
        if p.get("confidence") == "derived" and not p.get("source"):
            issues.append(f"ERROR [{s['id']}]: derived prnp must name its derivation in source")
    return issues
