#!/usr/bin/env python3
"""Pins for MCS-13/24/25-adjacent economics, MCS-27 growth, MCS-28/29 intake+loss,
MCS-22 predictor. Run: python3 scripts/test_economics.py. Soli Deo Gloria."""
import os
import sys
from datetime import date

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)
from lib.economics import animal_ledger, hold_vs_sell, validate_economics
from lib.growth import adjusted_60d, est_60d_weight
from lib.intake import loss_records, quarantine_items, validate_quarantine

failures = []


def check(name, got, expect):
    ok = got == expect
    print(f"  {'ok  ' if ok else 'FAIL'} {name}: got={got!r} expected={expect!r}")
    if not ok:
        failures.append(name)


# --- MCS-13 ledger -------------------------------------------------------------------
check("no economics -> incomplete, never $0 profit",
      animal_ledger({"id": "a"}), (None, None, None, False))
led = animal_ledger({"economics": {"acquisition": {"cost": 150},
                                   "costs": [{"amount": 40, "source": "x"}],
                                   "proceeds": [{"amount": 300, "source": "auction"}]}})
check("ledger math", led, (190.0, 300.0, 110.0, True))
check("unsourced amount is ERROR", any("no source" in e for e in validate_economics(
    {"sheep": [{"id": "z", "economics": {"proceeds": [{"amount": 10}]}}]})), True)
check("non-numeric amount is ERROR", any("not a number" in e for e in validate_economics(
    {"sheep": [{"id": "z", "economics": {"costs": [{"amount": "cheap", "source": "s"}]}}]})), True)

# --- MCS-24 hold vs sell ---------------------------------------------------------------
r = hold_vs_sell(80, 3.0, 0.5, 0.6, 30)
check("hold math: later value - feed - now", r["marginal"],
      round((80 + 15) * 3.0 - 18.0 - 240.0, 2))
check("price-later assumption is stated", r["price_later_assumed_equal"], True)
try:
    hold_vs_sell(80, None, 0.5, 0.6, 30)
    check("missing input raises", False, True)
except ValueError:
    check("missing input raises", True, True)

# --- MCS-27 growth -----------------------------------------------------------------------
check("60d interpolation", est_60d_weight(10, 60, 75), (50 / 75) * 60 + 10)
check("impossible inputs -> None", est_60d_weight(10, 5, 75), None)
w, applied, missing = adjusted_60d(10, 60, 75, dam_age_key="2", birth_rear_key="2-2")
check("sourced factors applied (1.08 * 1.21)", w, round(50.0 * 1.08 * 1.21, 2))
check("every applied factor carries a source", all(a[3] for a in applied), True)
w2, applied2, missing2 = adjusted_60d(10, 60, 75, dam_age_key="1")
check("absent factor -> reported missing, never silent 1.0",
      (w2, missing2), (50.0, [("dam_age", "1")]))

# --- MCS-28 quarantine ---------------------------------------------------------------------
qdb = {"sheep": [{"id": "newbie"}],
       "intake_quarantine": [{"animal_id": "newbie", "arrived": "2026-08-01",
                              "source_farm": "Oakvale"}]}
qi = quarantine_items(qdb, date(2026, 8, 20))
check("release due 28d after arrival, not yet overdue",
      (qi[0]["due"], qi[0]["overdue"]), ("2026-08-29", False))
check("workup gaps named", "GAPS" in qi[0]["basis"], True)
check("released row emits nothing", quarantine_items(
    {"intake_quarantine": [{"animal_id": "x", "arrived": "2026-07-01",
                            "source_farm": "y", "released": "2026-07-29"}]},
    date(2026, 8, 20)), [])
check("missing source_farm is ERROR", any("source_farm" in e for e in validate_quarantine(
    {"sheep": [], "intake_quarantine": [{"arrived": "2026-08-01"}]})), True)

# --- MCS-29 loss records ----------------------------------------------------------------
ldb = {"sheep": [{"id": "d1", "status": "deceased", "status_date": "2026-08-15",
                  "notes": "died of haemonchosis"},
                 {"id": "d2", "status": "deceased", "notes": "gone"}]}
lev = [{"type": "death", "animal_id": "d1", "date": "2026-08-15"}]
rows = {r["animal_id"]: r for r in loss_records(ldb, lev)}
check("event-backed death is claim-ready", rows["d1"]["claim_ready"], True)
check("undocumented death names its gaps",
      set(rows["d2"]["missing"]) >= {"cause", "date"}, True)

# --- MCS-22 predictor (composition) ------------------------------------------------------
sys.path.insert(0, _here)
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location("mp", os.path.join(_here, "mating_predictor.py"))
mp = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(mp)
pdb = {"sheep": [
    {"id": "r", "sex": "ram", "genetics": {"prnp": {"codon_171": "QR"},
                                           "polygenic": {"parasite_resistance": {"score": 5, "basis": "b"}}}},
    {"id": "e", "sex": "ewe", "genetics": {"prnp": {"codon_171": "QQ"},
                                           "polygenic": {"parasite_resistance": {"score": 3, "basis": "b"}}}},
    {"id": "u", "sex": "ewe"}]}
pred = mp.predict(pdb, "r", "e")
check("PRNP cross carried through", pred["prnp_171"]["QR"]["p"], 0.5)
check("polygenic midparent labeled naive",
      pred["polygenic_midparent"]["parasite_resistance"]["expectation"], 4.0)
pred2 = mp.predict(pdb, "r", "u")
check("untyped dam -> UNPREDICTABLE, never fabricated",
      any("untyped" in u for u in pred2["unpredictable"]), True)

# --- MCS-25 inventory ---------------------------------------------------------------------
from lib.intake import inventory_items, validate_inventory
inv = {"input_inventory": [
    {"item": "Prohibit 52g", "category": "wormer", "on_hand": 1, "unit": "packet",
     "expiry": "2026-09-01", "reorder_at": 1, "source": "shelf count"},
    {"item": "old CDT", "category": "vaccine", "on_hand": 3, "expiry": "2026-01-01"}]}
ii = inventory_items(inv, date(2026, 8, 20))
check("expiring stock warns inside window",
      any(i["type"] == "input_expiring" for i in ii), True)
check("expired stock is overdue", any(i["type"] == "input_expired" for i in ii), True)
check("reorder point crossing fires", any(i["type"] == "input_reorder" for i in ii), True)
check("bad category is ERROR", any("category" in e for e in validate_inventory(
    {"input_inventory": [{"item": "x", "category": "snacks", "on_hand": 1}]})), True)

if failures:
    print(f"\n{len(failures)} FAILURE(S): {failures}")
    sys.exit(1)
print("\nAll economics/growth/intake/predictor pins passed.")
