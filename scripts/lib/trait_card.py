"""Two-tier genetic trait card (MCS-32). Pure functions, no I/O.

Soli Deo Gloria.

Operator design (2026-08-12), split honestly into two tiers on one per-animal card:
  Tier 1 — LETTERS: true major loci only, Mendelian genotype strings with per-locus
           source + confidence. PRNP (MCS-15) is the first resident; the spot-color
           locus joins it (household fact, owner 2026-04-24: a PINK NOSE indicates
           CARRIER status for a spot-coloration gene even on a solid-colored animal).
  Tier 2 — BARS: polygenic traits (parasite resistance, heat tolerance, maternal) as
           1-5 scores with a stated basis — never dressed up as single-locus letters,
           because they aren't.

Schema (ADDITIVE):
  sheep["genetics"]["loci"] = {
    "<locus>": {"genotype": "Ss", "source": "...", "confidence":
                "tested"|"inferred-phenotype"|"derived-pedigree"}}
  sheep["genetics"]["polygenic"] = {
    "<trait>": {"score": 1-5, "basis": "...", "source": "..."}}

A cross prediction is a POSSIBILITY SET (Punnett), same discipline as MCS-15.
"""
import itertools

VALID_LOCUS_CONF = ("tested", "inferred-phenotype", "derived-pedigree")


def mendelian_cross(g1, g2):
    """Punnett outcome probabilities for two diploid genotype strings ('Ss' x 'ss').
    None if either is not a 2-allele string — never fabricated."""
    if not (isinstance(g1, str) and isinstance(g2, str) and len(g1) == 2 and len(g2) == 2):
        return None
    out = {}
    for a, b in itertools.product(g1, g2):
        # canonical order: uppercase (dominant) first, then alphabetical
        pair = "".join(sorted(a + b, key=lambda c: (c.lower(), c.islower())))
        out[pair] = out.get(pair, 0) + 0.25
    return out


def trait_card(sheep):
    """Assemble one animal's card from what the record actually holds — absent tiers
    are absent, never padded."""
    g = sheep.get("genetics") or {}
    card = {"id": sheep.get("id"), "tier1": {}, "tier2": {}, "phenotype_flags": []}
    if g.get("prnp"):
        p = g["prnp"]
        card["tier1"]["PRNP-171"] = {
            "genotype": p.get("codon_171"),
            "source": p.get("source"),
            "confidence": p.get("confidence"),
        }
    for locus, rec in (g.get("loci") or {}).items():
        card["tier1"][locus] = rec
    for trait, rec in (g.get("polygenic") or {}).items():
        card["tier2"][trait] = rec
    notes = (sheep.get("notes") or "").lower()
    if "pink nose" in notes:
        card["phenotype_flags"].append(
            "pink nose -> spot-coloration CARRIER (owner-stated genetics fact 2026-04-24)")
    return card


def validate_trait_cards(db):
    issues = []
    for s in db.get("sheep", []):
        g = s.get("genetics") or {}
        for locus, rec in (g.get("loci") or {}).items():
            if not isinstance(rec, dict):
                issues.append(f"ERROR [{s['id']}]: loci.{locus} is not an object")
                continue
            gt = rec.get("genotype")
            if not (isinstance(gt, str) and len(gt) == 2):
                issues.append(f"ERROR [{s['id']}]: loci.{locus}.genotype {gt!r} is not a "
                              f"2-allele string — polygenic traits belong in tier 2, not letters")
            if rec.get("confidence") not in VALID_LOCUS_CONF:
                issues.append(f"ERROR [{s['id']}]: loci.{locus}.confidence "
                              f"{rec.get('confidence')!r} not in {VALID_LOCUS_CONF}")
            if not rec.get("source"):
                issues.append(f"ERROR [{s['id']}]: loci.{locus} has no source — an unsourced "
                              f"letter becomes a fact in six months")
        for trait, rec in (g.get("polygenic") or {}).items():
            if not isinstance(rec, dict) or rec.get("score") not in (1, 2, 3, 4, 5):
                issues.append(f"ERROR [{s['id']}]: polygenic.{trait} needs score 1-5")
            elif not rec.get("basis"):
                issues.append(f"ERROR [{s['id']}]: polygenic.{trait} has no basis")
    return issues
