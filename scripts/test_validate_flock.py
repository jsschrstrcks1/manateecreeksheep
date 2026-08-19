#!/usr/bin/env python3
"""Regression pins for validate_flock.py breed-percentage guards.

Run: python3 scripts/test_validate_flock.py   (exit 0 = pass). No framework — the repo has none.
Covers the NaN/inf holes closed by the 2026-07-15 hostile pass (unknown_percentage) and the
2026-07-16 cross-review (a non-finite value in `percentages` itself). Soli Deo Gloria.
"""
import importlib.util
import json
import os
import sys

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("vf", os.path.join(_here, "validate_flock.py"))
vf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vf)


def _run(pcts, unknown=0):
    sheep = [{"id": "t", "breed_composition": {"percentages": pcts, "unknown_percentage": unknown}}]
    return vf.validate_breed_percentages(sheep)


def _warned(result):
    return bool(result)


CASES = [
    # (name, pcts, unknown, expect_warning)
    ("legit 87+13 documented-unknown", {"dorper": 87, "awassi": 13}, 0, False),
    ("legit exactly 100", {"dorper": 100}, 0, False),
    ("legit 87 + unknown 13", {"dorper": 87}, 13, False),
    ("shortfall 87 no unknown", {"dorper": 87}, 0, True),
    # NaN/inf in unknown_percentage — coerced to 0 → shortfall warns (2026-07-15 hostile pass):
    ("unknown = NaN", {"dorper": 87}, float("nan"), True),
    ("unknown = inf", {"dorper": 87}, float("inf"), True),
    ("unknown = True (bool)", {"dorper": 87}, True, True),
    # NaN/inf in a percentages VALUE — the identical hole one field over (2026-07-16 cross-review):
    ("value = NaN", {"dorper": float("nan"), "awassi": 13}, 0, True),
    ("value = inf", {"dorper": float("inf")}, 0, True),
    # Lift hostile pass 2026-07-16 — the guard must WARN, never CRASH, on any bad value class:
    ("value = string (crashed sum())", {"dorper": "50", "awassi": 50}, 0, True),
    ("value = None (crashed sum())", {"dorper": None, "awassi": 100}, 0, True),
    ("value = bool True (counted as 1%)", {"dorper": True, "awassi": 99}, 0, True),
    ("value = negative cancels to false-100", {"dorper": 150, "awassi": -50}, 0, True),
    ("percentages is a LIST (crashed .values())", [50, 50], 0, True),
    ("percentages is a STRING (crashed .values())", "100", 0, True),
    # And a legit record with a bad SIBLING value still validates the good one's shape:
    ("mixed: one good one string", {"dorper": 50, "awassi": "x"}, 0, True),
]


_nf_spec = importlib.util.spec_from_file_location("nf", os.path.join(_here, "normalize_famacha.py"))
nf = importlib.util.module_from_spec(_nf_spec)
_nf_spec.loader.exec_module(nf)


def famacha_tests():
    """Pins for the FAMACHA schema rule + the normalize_famacha migration invariants."""
    fails = []

    def check(name, cond):
        print(f"  {'ok  ' if cond else 'FAIL'} {name}")
        if not cond:
            fails.append(name)

    # -- validator rule --
    legacy_hist = [{"id": "t", "health": {"famacha_scores": [], "famacha_history": [{"date": "2026-02-12", "score": 2}]}}]
    check("famacha_history present → warns", bool(vf.validate_famacha_schema(legacy_hist)))
    legacy_key = [{"id": "t", "health": {"famacha_scores": [{"date": "2026-02-12", "famacha": 2}]}}]
    check("legacy 'famacha' key → warns", bool(vf.validate_famacha_schema(legacy_key)))
    canonical = [{"id": "t", "health": {"famacha_scores": [{"date": "2026-02-12", "score": 2, "notes": []}]}}]
    check("canonical schema → clean", not vf.validate_famacha_schema(canonical))

    # -- migration invariants --
    # same date, range in scores + point in history → point wins, range preserved in raw (lossless)
    h1 = {"famacha_history": [{"date": "2026-02-12", "score": 1, "notes": []}],
          "famacha_scores": [{"date": "2-12-26", "famacha": "1-2", "notes": []}]}
    out1, rep1 = nf.canonicalize(h1)
    e1 = out1[0]
    check("compatible range∋point → one entry", len(out1) == 1)
    check("compatible → clean point as score", e1["score"] == 1)
    check("compatible → range preserved in raw", "1-2" in (e1.get("raw") or []))
    check("compatible → no conflict flagged", not rep1["conflicts"])

    # genuine disagreement (5 vs 1) → score null, both in raw, flagged
    h2 = {"famacha_history": [{"date": "2026-04-10", "score": 5, "notes": []}],
          "famacha_scores": [{"date": "4-10-26", "famacha": 1, "notes": []}]}
    out2, rep2 = nf.canonicalize(h2)
    e2 = out2[0]
    check("genuine conflict → score null", e2["score"] is None)
    check("genuine conflict → both values in raw", set(map(str, e2.get("raw") or [])) == {"5", "1"})
    check("genuine conflict → reported", len(rep2["conflicts"]) == 1)
    check("genuine conflict → CONFLICT note", "CONFLICT" in e2["notes"])
    check("notes is a STRING (consumer contract)", isinstance(e2["notes"], str))

    # date normalization: M-D-YY → ISO; unparseable kept verbatim
    check("M-D-YY normalized to ISO", nf.normalize_date("2-12-26") == ("2026-02-12", True))
    check("ISO stays ISO", nf.normalize_date("2026-02-12") == ("2026-02-12", True))
    check("unparseable range kept verbatim", nf.normalize_date("2025-2026") == ("2025-2026", False))

    # consumer range parsing (enables the normalized range-valued scores to be scored)
    _pr_spec = importlib.util.spec_from_file_location("pr", os.path.join(_here, "parasite_resistance.py"))
    pr = importlib.util.module_from_spec(_pr_spec)
    _pr_spec.loader.exec_module(pr)
    check("scorer parses range '1-2' → midpoint 1.5", pr._parse_famacha("1-2") == 1.5)
    check("scorer parses range '2-3' → midpoint 2.5", pr._parse_famacha("2-3") == 2.5)
    check("scorer still parses plain int", pr._parse_famacha(3) == 3.0)

    # idempotency: canonicalize(canonicalize(x)) == canonicalize(x)
    once, _ = nf.canonicalize(h1)
    twice, _ = nf.canonicalize({"famacha_scores": once})
    check("idempotent (raw carried forward)", json.dumps(once, sort_keys=True) == json.dumps(twice, sort_keys=True))

    return fails


_ps_spec = importlib.util.spec_from_file_location("pen_state", os.path.join(_here, "pen_state.py"))
ps = importlib.util.module_from_spec(_ps_spec)
_ps_spec.loader.exec_module(ps)


def pen_tests():
    """Pins for the pen movement-log model (MCS-9) + the derived-cache validator rule."""
    fails = []

    def check(name, cond):
        print(f"  {'ok  ' if cond else 'FAIL'} {name}")
        if not cond:
            fails.append(name)

    # current_pen derives from the log's last entry; falls back to scalar pre-seed
    check("current_pen falls back to scalar pre-seed", ps.current_pen({"pen": "Pen 4"}) == "Pen 4")
    s = {"pen": "Pen 4"}
    ps.seed_from_scalar(s)
    check("seed creates a one-entry log", len(s["pen_log"]) == 1 and s["pen_log"][0]["pen"] == "Pen 4")
    check("seed leaves current pen unchanged", ps.current_pen(s) == "Pen 4")
    check("seed is idempotent (no re-seed)", ps.seed_from_scalar(s) is False)

    # record_move appends + updates the derived cache; a same-pen move is a no-op
    moved = ps.record_move(s, "Pen 6", date="2026-05-01", note="weaning")
    check("record_move logs a real move", moved is True and len(s["pen_log"]) == 2)
    check("record_move updates derived cache", s["pen"] == "Pen 6" and ps.current_pen(s) == "Pen 6")
    check("move preserves the prior pen in the log", s["pen_log"][0]["pen"] == "Pen 4")
    noop = ps.record_move(s, "Pen 6")
    check("same-pen move is a no-op (log is moves, not check-ins)", noop is False and len(s["pen_log"]) == 2)

    # validator: cache/log disagreement is an ERROR; out-of-order dates a WARNING
    bad_cache = [{"id": "t", "pen": "Pen 1", "pen_log": [{"date": "2026-01-01", "pen": "Pen 2"}]}]
    errs = vf.validate_pen_log(bad_cache)
    check("cache≠log → ERROR", any(e.startswith("ERROR") and "disagrees" in e for e in errs))
    good = [{"id": "t", "pen": "Pen 2", "pen_log": [{"date": "2026-01-01", "pen": "Pen 1"}, {"date": "2026-02-01", "pen": "Pen 2"}]}]
    check("in-order, consistent → clean", not vf.validate_pen_log(good))
    ooo = [{"id": "t", "pen": "Pen 2", "pen_log": [{"date": "2026-02-01", "pen": "Pen 1"}, {"date": "2026-01-01", "pen": "Pen 2"}]}]
    check("out-of-order dates → WARNING", any(e.startswith("WARNING") for e in vf.validate_pen_log(ooo)))
    return fails


_dd_spec = importlib.util.spec_from_file_location("dd", os.path.join(_here, "deworm_decision.py"))
dd = importlib.util.module_from_spec(_dd_spec)
_dd_spec.loader.exec_module(dd)


def deworm_tests():
    """Pins for the MCS-8 FAMACHA+FEC combined decision matrix — every cell, incl. the two
    mismatch cases the spec treats as diagnostic signals (absent from current data, so they
    are pinned with fixtures)."""
    from datetime import date as _date
    fails = []

    def check(name, cond):
        print(f"  {'ok  ' if cond else 'FAIL'} {name}")
        if not cond:
            fails.append(name)

    as_of = _date(2026, 4, 15)

    def animal(fam=None, fec=None):
        h = {}
        if fam is not None:
            h["famacha_scores"] = [{"date": "2026-04-10", "score": fam, "notes": ""}]
        if fec is not None:
            h["fec_history"] = [{"date": "2026-04-10", "fec": fec}]
        return {"id": "t", "status": "alive", "health": h}

    # the two MISMATCH diagnostic cells (the spec's reason for existing)
    r = dd.decide(animal(fam=4, fec=100), as_of)
    check("anemic + LOW fec → investigate (not dose)", r["decision"] == "investigate_anemia_nonparasitic")
    check("anemic + LOW fec → mismatch flagged + urgent", "mismatch_signal" in r["flags"] and r["urgency"] == 3)
    r = dd.decide(animal(fam=1, fec=1500), as_of)
    check("good colour + HIGH fec → refugia watch (not dose)", r["decision"] == "refugia_contamination_watch")
    check("good + HIGH fec → mismatch flagged", "mismatch_signal" in r["flags"])

    # the agreeing / plain cells
    check("anemic + HIGH fec → treat_and_verify", dd.decide(animal(fam=5, fec=2000), as_of)["decision"] == "treat_and_verify")
    check("good + LOW fec → monitor_routine", dd.decide(animal(fam=1, fec=100), as_of)["decision"] == "monitor_routine")
    check("borderline 3 → recheck", dd.decide(animal(fam=3), as_of)["decision"] == "recheck_borderline")

    # missing-data honesty (three states, never a silent default)
    r = dd.decide(animal(fam=5), as_of)
    check("anemic + NO fec → urgent + fec named as the gap", r["decision"] == "urgent_check_fec_needed" and r["urgency"] == 3)
    check("good + NO fec → fec_needed (never dose on FAMACHA alone)", dd.decide(animal(fam=1), as_of)["decision"] == "fec_needed")
    check("nothing on record → no_data", dd.decide(animal(), as_of)["decision"] == "no_data")

    # evidence hygiene
    r = dd.decide(animal(fam="1-2", fec=100), as_of)
    check("range score '1-2' parsed via the shared parser", r["famacha"] and r["famacha"]["score"] == 1.5)
    stale = {"id": "t", "status": "alive", "health": {"famacha_scores": [{"date": "2026-01-01", "score": 2, "notes": ""}]}}
    check("stale famacha flagged", any(f.startswith("famacha_stale") for f in dd.decide(stale, as_of)["flags"]))
    conflicted = {"id": "t", "status": "alive", "health": {"famacha_scores": [{"date": "2026-04-10", "score": None, "notes": "[CONFLICT]"}]}}
    check("a nulled [CONFLICT] score is NOT evidence", dd.decide(conflicted, as_of)["decision"] == "no_data")
    future = {"id": "t", "status": "alive", "health": {"famacha_scores": [{"date": "2026-05-01", "score": 5, "notes": ""}]}}
    check("as-of ignores future-dated entries", dd.decide(future, as_of)["decision"] == "no_data")

    # ordering: worst first
    flock = {"sheep": [animal(fam=1, fec=100) | {"id": "calm"}, animal(fam=5, fec=2000) | {"id": "sick"}]}
    order = [r["sheep_id"] for r in dd.decide_flock(flock, as_of)]
    check("flock sorts worst-first", order[0] == "sick")
    return fails


def main():
    failures = []
    for name, pcts, unknown, expect in CASES:
        got = _warned(_run(pcts, unknown))
        status = "ok  " if got == expect else "FAIL"
        if got != expect:
            failures.append(name)
        print(f"  {status} {name}: warned={got} expected={expect}")
    print("\nFAMACHA schema + migration pins:")
    failures += famacha_tests()
    print("\nPen movement-log pins:")
    failures += pen_tests()
    print("\nMCS-8 deworm-decision pins:")
    failures += deworm_tests()
    if failures:
        print(f"\n{len(failures)} FAILURE(S): {failures}")
        sys.exit(1)
    print(f"\nAll {len(CASES)} breed-percentage + FAMACHA + pen + deworm guard pins passed.")


if __name__ == "__main__":
    main()
