#!/usr/bin/env python3
"""Pins for the breeding pipeline (MCS-17). Run: python3 scripts/test_breeding.py.
No framework — the repo has none. Soli Deo Gloria."""
import os
import sys
from datetime import date

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)
from lib.breeding import (birth_for, breeding_items, derived_status,
                          mating_windows, validate_matings)

failures = []


def check(name, got, expect):
    ok = got == expect
    print(f"  {'ok  ' if ok else 'FAIL'} {name}: got={got!r} expected={expect!r}")
    if not ok:
        failures.append(name)


M = {"mating_id": "e1-x-r1-2026-06-01", "ewe_id": "e1", "ram_id": "r1",
     "exposure_start": "2026-06-01", "exposure_end": "2026-07-10", "status": "exposed"}

w = mating_windows(M)
check("due window from exposure WINDOW (start+142 .. end+152)",
      (str(w["due"][0]), str(w["due"][1])), ("2026-10-21", "2026-12-09"))
check("preg check 35d after start .. 45d after end",
      (str(w["preg_check"][0]), str(w["preg_check"][1])), ("2026-07-06", "2026-08-24"))
single = mating_windows({"exposure_start": "2026-06-01"})
check("single service date -> 10-day due window (147±5)",
      (str(single["due"][0]), str(single["due"][1])), ("2026-10-21", "2026-10-31"))
check("reversed dates -> None, never a guess",
      mating_windows({"exposure_start": "2026-07-01", "exposure_end": "2026-06-01"}), None)

BIRTH = [{"type": "birth", "animal_id": "e1", "date": "2026-10-25"}]
check("satisfying birth flips status to lambed", derived_status(M, BIRTH), "lambed")
check("no birth -> stays exposed", derived_status(M, []), "exposed")
OLD_BIRTH = [{"type": "birth", "animal_id": "e1", "date": "2026-01-05"}]
check("a birth from a previous cycle is NOT claimed", derived_status(M, OLD_BIRTH), "exposed")
check("failed status is terminal", derived_status({**M, "status": "failed"}, BIRTH), "failed")

db = {"sheep": [{"id": "e1", "sex": "ewe", "status": "alive"},
                {"id": "r1", "sex": "ram", "status": "alive"}],
      "matings": [M]}
items = breeding_items(db, date(2026, 7, 20))
check("open mating inside preg-check window -> preg_check_due",
      [i["type"] for i in items], ["preg_check_due"])
items2 = breeding_items(db, date(2026, 10, 15))
check("14d before due window -> lambing_watch appears",
      any(i["type"] == "lambing_watch" for i in items2), True)
items3 = breeding_items(db, date(2026, 11, 1), BIRTH)
check("after birth -> wean_due, no lambing_watch",
      ([i["type"] for i in items3]), (["wean_due"]))
check("wean window 60-90d from birth",
      (items3[0]["due"], items3[0]["window_end"]), ("2026-12-24", "2027-01-23"))

check("valid table validates clean", validate_matings(db), [])
bad = {"sheep": db["sheep"],
       "matings": [{"mating_id": "x", "ewe_id": "r1", "ram_id": "ghost",
                    "exposure_start": "nope", "status": "maybe"},
                   {"mating_id": "x", "ewe_id": "e1", "ram_id": "r1",
                    "exposure_start": "2026-06-01"}]}
errs = validate_matings(bad)
check("wrong-sex ewe caught", any("expected ewe" in e for e in errs), True)
check("missing ram caught", any("ghost" in e for e in errs), True)
check("bad status caught", any("maybe" in e for e in errs), True)
check("unparseable dates caught", any("unparseable" in e for e in errs), True)
check("duplicate mating_id caught", any("duplicate" in e for e in errs), True)

if failures:
    print(f"\n{len(failures)} FAILURE(S): {failures}")
    sys.exit(1)
print("\nAll breeding pins passed.")
