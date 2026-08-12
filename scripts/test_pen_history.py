#!/usr/bin/env python3
"""Regression pins for the MCS-9 pen-history lift (scripts/lib/pen_history.py + the
migration + the validate_flock drift check).

Run: python3 scripts/test_pen_history.py   (exit 0 = pass). No framework — the repo has none.

Covers: current_pen derivation (empty log, single/multi move, left-all-pens, un-migrated
fallback), migration idempotence, the scalar<->log mirror, and the validate_flock pen-drift
ERROR. Soli Deo Gloria.
"""
import copy
import importlib.util
import os
import sys

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)
from lib.pen_history import current_pen, derive_rosters, derive_id_to_pen  # noqa: E402


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, os.path.join(_here, filename))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mig = _load("mig", "migrate_pen_to_movements.py")
vf = _load("vf", "validate_flock.py")

failures = []


def check(name, cond):
    print(f"  {'ok  ' if cond else 'FAIL'} {name}")
    if not cond:
        failures.append(name)


# --- current_pen derivation -------------------------------------------------------------
check("empty log -> None", current_pen({"id": "a", "movements": []}) is None)
check("un-migrated (no movements key) falls back to scalar pen",
      current_pen({"id": "a", "pen": "Pen 3"}) == "Pen 3")
check("single move -> its 'to'",
      current_pen({"id": "a", "movements": [{"to": "Pen 1"}]}) == "Pen 1")
check("multiple moves -> LAST 'to' (array order is truth)",
      current_pen({"id": "a", "movements": [
          {"to": "Pen 1"}, {"to": "Pen 5"}, {"to": "Tree Fort"}]}) == "Tree Fort")
check("last move with empty 'to' -> None (left all pens)",
      current_pen({"id": "a", "movements": [{"to": "Pen 1"}, {"to": None}]}) is None)
check("log present WINS over stale scalar",
      current_pen({"id": "a", "pen": "Pen 9", "movements": [{"to": "Pen 2"}]}) == "Pen 2")

# --- derive rosters / id->pen -----------------------------------------------------------
_db = {"sheep": [
    {"id": "x", "movements": [{"to": "Pen 1"}]},
    {"id": "y", "movements": [{"to": "Pen 1"}, {"to": "Pen 2"}]},
    {"id": "z", "movements": []},
]}
check("derive_id_to_pen tracks the last move", derive_id_to_pen(_db) == {"x": "Pen 1", "y": "Pen 2", "z": None})
check("derive_rosters projects membership from the log",
      derive_rosters(_db) == {"Pen 1": ["x"], "Pen 2": ["y"]})

# --- migration seeding + idempotence ----------------------------------------------------
db1 = {"sheep": [
    {"id": "placed", "pen": "Pen 4"},
    {"id": "nopen", "pen": None},
]}
seeded, already, empty = mig.seed(db1)
check("migration seeds the placed sheep", seeded == 1 and empty == 1 and already == 0)
check("seeded log has one initial-placement move to the right pen",
      db1["sheep"][0]["movements"] == [{
          "date": None, "from": None, "to": "Pen 4",
          "reason": mig.SEED_REASON, "source": mig.SEED_SOURCE}])
check("no-pen sheep gets an empty log", db1["sheep"][1]["movements"] == [])
check("scalar pen mirrors the derived value after migration",
      db1["sheep"][0]["pen"] == "Pen 4" and db1["sheep"][1]["pen"] is None)

db2 = copy.deepcopy(db1)
seeded2, already2, empty2 = mig.seed(db2)
check("re-running migration is idempotent (nothing re-seeded)",
      seeded2 == 0 and already2 == 2 and db2 == db1)

# --- validate_flock pen-drift check -----------------------------------------------------
clean = {"sheep": [{"id": "ok", "pen": "Pen 1", "movements": [{"to": "Pen 1"}]}], "pens": {}}
check("consistent scalar+log -> no drift issue",
      not any("drift" in i for i in vf.validate_pen_movements(clean)))

drift = {"sheep": [{"id": "bad", "pen": "Pen 7", "movements": [{"to": "Pen 1"}]}], "pens": {}}
drift_issues = vf.validate_pen_movements(drift)
check("hand-edited scalar that disagrees with the log -> ERROR",
      any(i.startswith("ERROR") and "drift" in i for i in drift_issues))

premig = {"sheep": [{"id": "old", "pen": "Pen 2"}], "pens": {}}
check("record with no movements key -> soft WARNING, not ERROR",
      any(i.startswith("WARNING") and "movements" in i for i in vf.validate_pen_movements(premig)))

# Roster projection: a hand-maintained roster that lists someone the log places elsewhere
# (the baby-azure case — deceased, never removed from Pen 2 members) -> WARNING.
stale = {
    "sheep": [{"id": "dead", "status": "deceased", "pen": None, "movements": []}],
    "pens": {"pen_2": {"display_name": "Pen 2", "members": ["dead"]}},
}
check("stale roster member absent from the log -> roster WARNING",
      any(i.startswith("WARNING") and "roster lists 'dead'" in i for i in vf.validate_pen_movements(stale)))

aligned = {
    "sheep": [{"id": "here", "pen": "Pen 2", "movements": [{"to": "Pen 2"}]}],
    "pens": {"pen_2": {"display_name": "Pen 2", "members": ["here"]}},
}
check("roster and log agree -> no roster warning",
      not any("roster lists" in i for i in vf.validate_pen_movements(aligned)))

if failures:
    print(f"\n{len(failures)} FAILURE(S): {failures}")
    sys.exit(1)
print("\nAll pen-history pins passed.")
