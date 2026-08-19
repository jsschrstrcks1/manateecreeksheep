#!/usr/bin/env python3
"""Pins for MCS-5 (dual identity), MCS-15 (PRNP), MCS-16 (pedigree + Wright's F).
Run: python3 scripts/test_identity_genetics.py. No framework. Soli Deo Gloria."""
import os
import sys

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)
from lib.genetics import offspring_possibilities, resistance_note, validate_genetics, validate_prnp
from lib.identity import all_tags, find_by_tag, validate_identity
from lib.pedigree import build_parents, prospective_f, wright_f

failures = []


def check(name, got, expect):
    ok = got == expect
    print(f"  {'ok  ' if ok else 'FAIL'} {name}: got={got!r} expected={expect!r}")
    if not ok:
        failures.append(name)


# --- MCS-5 dual identity -------------------------------------------------------------
db5 = {"sheep": [
    {"id": "a", "status": "alive", "tag": "22", "tag_color": "orange",
     "tags": [{"kind": "eid", "value": "840003123456789", "status": "active"},
              {"kind": "visual", "value": "22", "color": "orange", "status": "active"}]},
    {"id": "b", "status": "alive", "tag": "0053"},
    {"id": "c", "status": "alive",
     "tags": [{"kind": "visual", "value": "113", "status": "lost"}]},
]}
check("EID finds the animal", find_by_tag(db5, "840003123456789"), ["a"])
check("legacy scalar tag still finds", find_by_tag(db5, "0053"), ["b"])
check("LOST tag still resolves (old paperwork)", find_by_tag(db5, "113"), ["c"])
check("legacy scalar synthesized once, not duplicated",
      sum(1 for t in all_tags(db5["sheep"][0]) if str(t["value"]) == "22"), 1)
check("clean table validates", validate_identity(db5), [])
dup = {"sheep": [
    {"id": "x", "status": "alive", "tags": [{"kind": "eid", "value": "E1", "status": "active"}]},
    {"id": "y", "status": "alive", "tags": [{"kind": "eid", "value": "e1", "status": "active"}]}]}
check("shared ACTIVE EID between living sheep is ERROR",
      any("shared by living" in e for e in validate_identity(dup)), True)
check("bad kind caught", any("kind" in e for e in validate_identity(
    {"sheep": [{"id": "z", "tags": [{"kind": "rfid", "value": "1"}]}]})), True)

# --- MCS-15 PRNP ---------------------------------------------------------------------
check("valid record clean", validate_prnp({"codon_171": "QR", "confidence": "tested"}), [])
check("unalphabetized allele order caught",
      any("alphabetized" in p for p in validate_prnp({"codon_171": "RQ"})), True)
check("empty prnp caught", any("no codon" in p for p in validate_prnp({})), True)
check("RR x QQ -> all QR", offspring_possibilities({"codon_171": "RR"}, {"codon_171": "QQ"}),
      {"QR": 1.0})
check("QR x QR -> 1/4 RR, 1/2 QR, 1/4 QQ",
      offspring_possibilities({"codon_171": "QR"}, {"codon_171": "QR"}),
      {"RR": 0.25, "QR": 0.5, "QQ": 0.25})
check("unknown parent -> None, never fabricated",
      offspring_possibilities({"codon_171": "QR"}, {}), None)
check("resistance note", resistance_note("RR"), "resistant")
check("derived without source is ERROR", any("derivation" in e for e in validate_genetics(
    {"sheep": [{"id": "g", "genetics": {"prnp": {"codon_171": "QR", "confidence": "derived"}}}]})), True)

# --- MCS-16 Wright's F — textbook pedigrees -------------------------------------------
def ped(rows):
    return {"sheep": [{"id": i, "sire_id": s, "dam_id": d} for i, s, d in rows]}

# full siblings mated -> lamb F = 0.25
full_sib = ped([("S", None, None), ("D", None, None),
                ("bro", "S", "D"), ("sis", "S", "D")])
check("full-sib mating -> F 0.25", round(prospective_f(full_sib, "bro", "sis"), 4), 0.25)
# parent x offspring -> 0.25
po = ped([("S", None, None), ("D", None, None), ("kid", "S", "D")])
check("sire x own daughter -> F 0.25", round(prospective_f(po, "S", "kid"), 4), 0.25)
# half siblings -> 0.125
half = ped([("S", None, None), ("D1", None, None), ("D2", None, None),
            ("h1", "S", "D1"), ("h2", "S", "D2")])
check("half-sib mating -> F 0.125", round(prospective_f(half, "h1", "h2"), 4), 0.125)
# unrelated -> 0; unknown parents -> lower bound 0
check("unrelated -> F 0", prospective_f(half, "D1", "D2"), 0.0)
check("existing animal from unknown parents -> F 0 (lower bound)",
      wright_f(ped([("solo", None, None)]), "solo"), 0.0)
# offspring OF the full-sib mating has F=0.25 recorded via wright_f
fs2 = ped([("S", None, None), ("D", None, None), ("bro", "S", "D"), ("sis", "S", "D"),
           ("inbred", "bro", "sis")])
check("wright_f of full-sib offspring = 0.25", round(wright_f(fs2, "inbred"), 4), 0.25)

# --- MCS-10 cohorts --------------------------------------------------------------------
from datetime import date as _date
from lib.cohorts import breeding_group, pen_at, pen_members_at, treatment_cohort
mv = {"id": "m", "movements": [
    {"date": None, "from": None, "to": "Pen 1"},
    {"date": "2026-06-01", "from": "Pen 1", "to": "Pen 5"},
    {"date": "2026-08-01", "from": "Pen 5", "to": None}]}
check("pen replay: before dated moves -> seed pen", pen_at(mv, _date(2026, 1, 1)), "Pen 1")
check("pen replay: mid-window", pen_at(mv, _date(2026, 7, 1)), "Pen 5")
check("pen replay: after removal -> None", pen_at(mv, _date(2026, 8, 10)), None)
cdb = {"sheep": [mv, {"id": "n", "movements": [{"date": "2026-05-01", "from": None, "to": "Pen 5"}]}]}
check("pen members at date", pen_members_at(cdb, "Pen 5", _date(2026, 7, 1)), ["m", "n"])
tev = [{"type": "treatment", "animal_id": "a", "date": "2026-08-12", "drug": "ivermectin"},
       {"type": "treatment", "animal_id": "b", "date": "2026-08-11/2026-08-12", "drug": "ivermectin"},
       {"type": "treatment", "animal_id": "c", "date": "2026-08-12", "drug": "prohibit"},
       {"type": "famacha", "animal_id": "d", "date": "2026-08-12"}]
check("treatment cohort same day", treatment_cohort(tev, "2026-08-12"), ["a", "b", "c"])
check("treatment cohort filtered by drug", treatment_cohort(tev, "2026-08-12", "ivermectin"), ["a", "b"])
bdb = {"matings": [{"ram_id": "r", "ewe_id": "e1", "status": "exposed"},
                   {"ram_id": "r", "ewe_id": "e2", "status": "failed"}]}
check("breeding group excludes failed", breeding_group(bdb, "r"), ["e1"])

# --- MCS-32 trait card -------------------------------------------------------------------
from lib.trait_card import mendelian_cross, trait_card, validate_trait_cards
check("Ss x ss -> half carriers", mendelian_cross("Ss", "ss"), {"Ss": 0.5, "ss": 0.5})
check("bad genotype -> None never fabricated", mendelian_cross("S", "ss"), None)
card = trait_card({"id": "t", "notes": "Docile. Pink nose noted 4-24.",
                   "genetics": {"prnp": {"codon_171": "QR", "confidence": "tested"},
                                "loci": {"spot": {"genotype": "Ss", "source": "phenotype",
                                                  "confidence": "inferred-phenotype"}},
                                "polygenic": {"parasite_resistance": {"score": 4, "basis": "FEC history"}}}})
check("card tier1 carries PRNP + locus", sorted(card["tier1"]), ["PRNP-171", "spot"])
check("card tier2 carries polygenic", list(card["tier2"]), ["parasite_resistance"])
check("pink-nose phenotype flag fires", len(card["phenotype_flags"]), 1)
bad32 = {"sheep": [{"id": "z", "genetics": {"loci": {"resist": {"genotype": "high", "confidence": "tested", "source": "x"}},
                                            "polygenic": {"meh": {"score": 9}}}}]}
errs32 = validate_trait_cards(bad32)
check("polygenic-dressed-as-letters caught", any("tier 2" in e for e in errs32), True)
check("bad polygenic score caught", any("score 1-5" in e for e in errs32), True)

if failures:
    print(f"\n{len(failures)} FAILURE(S): {failures}")
    sys.exit(1)
print("\nAll identity/genetics/pedigree pins passed.")
