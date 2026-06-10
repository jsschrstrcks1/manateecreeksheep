"""Pedigree relationships, inbreeding, and path coefficients.

Implements Henderson's tabular method for the numerator relationship
matrix (A-matrix). For our small flock (~200 records) this runs in <1s.

References:
  Henderson 1976. A simple method for computing the inverse of a
  numerator relationship matrix used in prediction of breeding values.
  Biometrics 32: 69-83.

The numerator relationship coefficient A_ij between two animals i and j
is twice the probability that two alleles, one drawn at random from
each, are identical by descent. For:
  - Self: A_ii = 1 + F_i (where F_i = inbreeding coefficient)
  - Parent-offspring: A_ij = 0.5 (unrelated parents)
  - Full sibs (unrelated parents): A_ij = 0.5
  - Half sibs: A_ij = 0.25
"""
from __future__ import annotations
import json
from functools import lru_cache
from pathlib import Path


def load_pedigree(db_path: str = "data/flock_database.json") -> dict:
    """Return {sheep_id: {"sire": id|None, "dam": id|None, "dob": str|None}}."""
    with open(db_path) as f:
        db = json.load(f)
    ped = {}
    for s in db["sheep"]:
        ped[s["id"]] = {
            "sire": s.get("sire_id"),
            "dam": s.get("dam_id"),
            "dob": s.get("dob"),
            "sex": s.get("sex"),
        }
    return ped


def relationship(a: str, b: str, ped: dict, memo: dict | None = None) -> float:
    """Numerator relationship coefficient A(a, b).

    Recursive Wright path-counting via the tabular recurrence:
        A(i, j) = 0.5 * (A(sire_i, j) + A(dam_i, j))   for i != j
        A(i, i) = 1 + F_i = 1 + 0.5 * A(sire_i, dam_i)
    """
    if memo is None:
        memo = {}
    if a is None or b is None:
        return 0.0
    key = (a, b) if a < b else (b, a)
    if key in memo:
        return memo[key]
    if a == b:
        # Self-relationship = 1 + inbreeding
        if a not in ped:
            r = 1.0
        else:
            sire = ped[a].get("sire")
            dam = ped[a].get("dam")
            if sire and dam and sire in ped and dam in ped:
                f = 0.5 * relationship(sire, dam, ped, memo)
            else:
                f = 0.0
            r = 1.0 + f
        memo[key] = r
        return r
    # Cross-relationship: recurse via the older animal's parents.
    # Order by DOB if available so the younger animal expands.
    def dob_of(x):
        d = ped.get(x, {}).get("dob") or ""
        return d
    if dob_of(a) > dob_of(b):
        younger, older = a, b
    else:
        younger, older = b, a
    if younger not in ped:
        memo[key] = 0.0
        return 0.0
    sire = ped[younger].get("sire")
    dam = ped[younger].get("dam")
    rs = relationship(sire, older, ped, memo) if sire else 0.0
    rd = relationship(dam, older, ped, memo) if dam else 0.0
    r = 0.5 * (rs + rd)
    memo[key] = r
    return r


def inbreeding(animal: str, ped: dict, memo: dict | None = None) -> float:
    """F_i = inbreeding coefficient = 0.5 * A(sire_i, dam_i)."""
    if memo is None:
        memo = {}
    if animal not in ped:
        return 0.0
    sire = ped[animal].get("sire")
    dam = ped[animal].get("dam")
    if not sire or not dam:
        return 0.0
    return 0.5 * relationship(sire, dam, ped, memo)


def path_coefficient(ancestor: str, descendant: str, ped: dict) -> float:
    """Contribution of one ancestor's breeding value to a descendant's BV.

    For a direct ancestor n generations back via one path:
        coefficient = (1/2)^n
    Multiple paths add. We compute as A(ancestor, descendant)/2 for the
    "additive contribution of one ancestor to one descendant" — same
    quantity used to propagate ancestor EBVs down.
    """
    return 0.5 * relationship(ancestor, descendant, ped)


if __name__ == "__main__":
    # Smoke test on real flock
    ped = load_pedigree()
    # Centralia lamb x its parents — relationship should be 0.5
    if "centralia-lamb-2026" in ped:
        a = relationship("centralia-lamb-2026", "centralia-ram-214168", ped)
        b = relationship("centralia-lamb-2026", "centralia-dam-181084x", ped)
        f = inbreeding("centralia-lamb-2026", ped)
        print(f"Centralia lamb -- sire: A={a:.4f}, dam: A={b:.4f}, F={f:.4f}")
    # Half-Tail's offspring
    if "broken-tail" in ped and "elsie" in ped:
        a = relationship("broken-tail", "elsie", ped)
        print(f"Broken Tail -- Elsie (half-sibs via Half Tail): A={a:.4f}")
