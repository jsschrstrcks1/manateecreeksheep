#!/usr/bin/env python3
"""Pins for the flock agenda engine. Run: python3 scripts/test_flock_agenda.py (exit 0 = pass).
No framework — the repo has none. Spec: docs/superpowers/plans/2026-08-12-flock-agenda-engine.md
(pins below follow the plan verbatim, plus dated 2026-08-18 additions for the typed event log).
Soli Deo Gloria."""
import os
import sys
_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)
from datetime import date
from lib.flock_agenda import (parse_date, classify_treatment, withdrawal_items,
                              fecrt_items, famacha_items, anomaly_items, build_agenda)

failures = []


def check(name, cond):
    print(f"  {'ok  ' if cond else 'FAIL'} {name}")
    if not cond:
        failures.append(name)


# --- Task 1: parsing + classification (plan pins) ------------------------------------
check("ISO date", parse_date("2026-08-12") == date(2026, 8, 12))
check("US short date (famacha style)", parse_date("4-10-26") == date(2026, 4, 10))
check("garbage -> None, never a crash", parse_date("2023-2024") is None)
check("None -> None", parse_date(None) is None)
check("ISO range -> END of window (conservative)",
      parse_date("2026-08-11/2026-08-18") == date(2026, 8, 18))

w, b, u = classify_treatment("Ivermectin + Fenbendazole + Prohibit (levamisole)")
check("triple treatment finds 3 anthelmintics",
      sorted(w) == ["fenbendazole", "ivermectin", "levamisole_prohibit"])
w, b, u = classify_treatment("B-complex 2mL + pig iron 1mL")
check("supportive care is benign, no anthelmintic", w == [] and b and u == [])
w, b, u = classify_treatment("Mystery Drench 5mL")
check("unknown drug is FLAGGED, not ignored", u != [])
w, b, u = classify_treatment("VB 3mL + Iron 2mL")
check("flock 'VB' shorthand is benign (2026-08-18 addition)", w == [] and b and u == [])

# --- Task 2: withdrawal locks (plan pins) ---------------------------------------------
TODAY = date(2026, 8, 20)
DRUG_REF = {
    "ivermectin": {"house_default_meat_withdrawal_days": 14, "label_meat_withdrawal_days": 11},
    "fenbendazole": {"house_default_meat_withdrawal_days": 28},
    "levamisole_prohibit": {"label_meat_withdrawal_days": 3},
}
sheep = [{"id": "ewe1", "status": "alive", "health": {"treatments": [
    {"date": "2026-08-12", "treatment": "Ivermectin + Fenbendazole + Prohibit (levamisole)"},
    {"date": "2026-08-12", "treatment": "B-complex 2mL"},
    {"date": "2026-08-12", "treatment": "Mystery Drench"},
]}}]
items = withdrawal_items(sheep, DRUG_REF, TODAY)
locks = [i for i in items if i["type"] == "withdrawal_lock"]
check("three anthelmintics -> three locks", len(locks) == 3)
fen = next(i for i in locks if i["drug"] == "fenbendazole")
check("fenbendazole locks until 9/9 (28d)", fen["until"] == "2026-09-09")
iv = next(i for i in locks if i["drug"] == "ivermectin")
check("ivermectin uses HOUSE DEFAULT 14d over label 11d", iv["until"] == "2026-08-26")
lev = next(i for i in locks if i["drug"] == "levamisole_prohibit")
check("expired lock (3d) is not active at 8/20", lev["active"] is False)
check("unknown drug flagged", any(i["type"] == "unknown_withdrawal" for i in items))
check("benign supportive care produces nothing",
      not any("b-complex" in str(i).lower() for i in items))

# 2026-08-18 addition: typed events with explicit lock win over re-derivation
EVENTS = [{"type": "treatment", "animal_id": "ewe1", "date": "2026-08-12",
           "drug": "ivermectin", "withdrawal_until": "2026-08-26",
           "withdrawal_basis": "14d meat — house default"}]
ev_items = withdrawal_items(sheep, DRUG_REF, TODAY, EVENTS)
ev_iv = [i for i in ev_items if i.get("drug") == "ivermectin"]
check("event + free-text same (animal,date,drug) dedupes to ONE lock", len(ev_iv) == 1)
check("the surviving lock is the RECORDED one", "recorded at treatment" in ev_iv[0]["basis"])

# --- Task 3: FECRT + FAMACHA + anomalies (plan pins) ----------------------------------
f_items = fecrt_items(sheep, TODAY)
check("anthelmintic treatment -> one FECRT window per treatment day",
      len(f_items) == 1 and f_items[0]["due"] == "2026-08-22")   # 8/12 + 10d
check("FECRT window not overdue while inside 10-14d", f_items[0]["overdue"] is False)
f_late = fecrt_items(sheep, date(2026, 8, 28))
check("FECRT overdue after day 14", f_late[0]["overdue"] is True)

sheep_fam = [{"id": "ewe2", "status": "alive", "health": {"famacha_scores": [
    {"date": "2026-08-12", "score": 5, "notes": ""}]}}]
fam = famacha_items(sheep_fam, TODAY)
check("FAMACHA 5 -> recheck 7d -> due 8/19, overdue at 8/20",
      fam and fam[0]["due"] == "2026-08-19" and fam[0]["overdue"] is True)
check("deceased sheep produce nothing",
      famacha_items([{"id": "x", "status": "deceased", "health": {"famacha_scores":
        [{"date": "2026-08-12", "score": 5}]}}], TODAY) == [])
check("non-numeric famacha ('Good') skipped without crash",
      famacha_items([{"id": "y", "status": "alive", "health": {"famacha_scores":
        [{"date": "2026-08-12", "score": "Good"}]}}], TODAY) == [])
check("legacy 'famacha' key entries still READ (defense-in-depth post-migration)",
      famacha_items([{"id": "z", "status": "alive", "health": {"famacha_scores":
        [{"date": "2026-08-12", "famacha": 4}]}}], TODAY) != [])
check("newer famacha EVENT overrides older DB score",
      famacha_items(sheep_fam, TODAY,
                    [{"type": "famacha", "animal_id": "ewe2", "date": "2026-08-15",
                      "score": 2}]) == [])

anoms = anomaly_items([{"date": "2026-08-12", "issue": "Tinker unidentified",
                        "status": "pending_identification"},
                       {"date": "2026-05-21", "issue": "old", "status": "resolved"}], TODAY)
check("pending anomaly surfaces, resolved does not",
      len(anoms) == 1 and anoms[0]["overdue"] is True)

# --- Task 4: assembly (plan pins) -----------------------------------------------------
db = {"sheep": sheep + sheep_fam, "drug_reference": DRUG_REF,
      "anomalies": [{"date": "2026-08-12", "issue": "Tinker", "status": "pending_identification"}]}
ag = build_agenda(db, TODAY)
check("agenda has meta + items", "generated_for" in ag and isinstance(ag["items"], list))
check("overdue items sort first", all(
    not (b["overdue"] and not a["overdue"]) for a, b in zip(ag["items"], ag["items"][1:])))
check("active withdrawal locks counted in summary", ag["summary"]["withdrawal_locks_active"] >= 1)

# --- 2026-08-18 live-run fixes pinned --------------------------------------------------
from lib.flock_agenda import watch_items
dead = [{"id": "gone", "status": "deceased", "health": {"treatments": [
    {"date": "2026-08-12", "treatment": "Ivermectin"}]}}]
check("deceased animals get NO withdrawal locks (noise wearing a safety label)",
      withdrawal_items(dead, DRUG_REF, TODAY) == [])
wi = watch_items([{"animals": "GG only", "drug": "fenbendazole",
                   "not_safe_for_slaughter_until": "2026-09-09 (FARAD sheep 28d)"}], TODAY)
check("flock-level watch row surfaces as group lock",
      len(wi) == 1 and wi[0]["until"] == "2026-09-09" and wi[0]["animal_id"] is None)
check("expired watch row goes inactive",
      watch_items([{"animals": "x", "drug": "d",
                    "not_safe_for_slaughter_until": "2026-08-15"}], TODAY)[0]["active"] is False)



# --- MCS-1 warm-wet cadence -------------------------------------------------------------
_ww_sheep = [{"id": "s3", "status": "alive",
              "health": {"famacha_scores": [{"date": "2026-08-01", "score": 3}]}},
             {"id": "s2", "status": "alive",
              "health": {"famacha_scores": [{"date": "2026-08-01", "score": 2}]}}]
_base = famacha_items(_ww_sheep, date(2026, 8, 19))
check("base cadence: score 3 -> 14d", [i["due"] for i in _base if i["animal_id"] == "s3"] == ["2026-08-15"])
check("base cadence: score 2 gets NO item", not any(i["animal_id"] == "s2" for i in _base))
_ww = famacha_items(_ww_sheep, date(2026, 8, 19), season="warm-wet")
check("warm-wet: score 3 tightens to 7d", [i["due"] for i in _ww if i["animal_id"] == "s3"] == ["2026-08-08"])
check("warm-wet: score 2 earns a 14d recheck", [i["due"] for i in _ww if i["animal_id"] == "s2"] == ["2026-08-15"])
check("warm-wet basis names the cadence", all("warm-wet cadence" in i["basis"] for i in _ww) and len(_ww) == 2)

if failures:
    print(f"\n{len(failures)} FAILURE(S): {failures}")
    sys.exit(1)
print("\nAll agenda pins passed.")
