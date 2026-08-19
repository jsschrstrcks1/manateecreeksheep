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


_at_spec = importlib.util.spec_from_file_location("at", os.path.join(_here, "attention_triage.py"))
at = importlib.util.module_from_spec(_at_spec)
_at_spec.loader.exec_module(at)


def triage_tests():
    """Pins for the MCS-3 attention triage — trend, scoping, R/A/G, ordering."""
    from datetime import date as _date
    fails = []

    def check(name, cond):
        print(f"  {'ok  ' if cond else 'FAIL'} {name}")
        if not cond:
            fails.append(name)

    as_of = _date(2026, 4, 15)

    def animal(sid="t", scores=(), on_prop=True, pen="Pen 1", dob=None):
        return {"id": sid, "status": "alive", "on_property": on_prop, "pen": pen, "dob": dob,
                "health": {"famacha_scores": [
                    {"date": d, "score": v, "notes": ""} for d, v in scores]}}

    # trend: worsening detected between last two points; [CONFLICT] nulls excluded
    tr = at.famacha_trend(animal(scores=[("2026-03-01", 1), ("2026-04-01", 5)]), as_of)
    check("trend detects worsening 1→5", tr and tr["delta"] == 4)
    tr = at.famacha_trend(animal(scores=[("2026-03-01", 2)]), as_of)
    check("one point = no trend", tr is None)
    mixed = animal(scores=[("2026-03-01", 1), ("2026-04-01", 2)])
    mixed["health"]["famacha_scores"].append({"date": "2026-04-10", "score": None, "notes": "[CONFLICT]"})
    tr = at.famacha_trend(mixed, as_of)
    check("nulled [CONFLICT] row does not enter the trend", tr and tr["to"] == 2)

    # R/A/G assignment
    red = at.triage_one(animal(scores=[("2026-03-01", 1), ("2026-04-10", 5)]), as_of)
    check("anemic crash → RED", red["status"] == "RED")
    green = at.triage_one(animal(scores=[("2026-04-01", 1), ("2026-04-10", 1)]), as_of)
    check("fresh good scores → GREEN", green["status"] == "GREEN")
    stale = at.triage_one(animal(scores=[("2026-01-01", 1), ("2026-01-15", 1)]), as_of)
    check("stale checks → AMBER", stale["status"] == "AMBER")
    young = at.triage_one(animal(scores=(), pen="Pen 1", dob="2026-03-01"), as_of)
    check("young + no records → GREEN (first check due, not delinquent)", young["status"] == "GREEN")
    adult = at.triage_one(animal(scores=(), pen="Pen 1", dob="2024-01-01"), as_of)
    check("adult + no records → AMBER (first check owed)", adult["status"] == "AMBER")

    # scoping: registry imports (on_property False) excluded from the flock view
    db = {"sheep": [animal(sid="home", scores=[("2026-04-10", 1), ("2026-04-01", 1)]),
                    animal(sid="registry", on_prop=False)]}
    rows = at.triage_flock(db, as_of)
    check("on_property=False excluded from triage", [r["sheep_id"] for r in rows] == ["home"])

    # ordering: RED above AMBER above GREEN by score
    db = {"sheep": [animal(sid="calm", scores=[("2026-04-01", 1), ("2026-04-10", 1)]),
                    animal(sid="crash", scores=[("2026-03-01", 1), ("2026-04-10", 5)])]}
    rows = at.triage_flock(db, as_of)
    check("worst-first ordering", rows[0]["sheep_id"] == "crash")
    return fails


_fc_spec = importlib.util.spec_from_file_location("fc", os.path.join(_here, "fecrt_check.py"))
fc = importlib.util.module_from_spec(_fc_spec)
_fc_spec.loader.exec_module(fc)


def fecrt_tests():
    """Pins for the MCS-30 FECRT — drug-class parse, pairing, verdict bands, gap honesty."""
    from datetime import date as _date
    fails = []

    def check(name, cond):
        print(f"  {'ok  ' if cond else 'FAIL'} {name}")
        if not cond:
            fails.append(name)

    # drug-class parsing from free-text combos; supportive meds are not anthelmintics
    check("ivermectin -> macrocyclic-lactone", fc.anthelmintic_classes("Ivermectin") == ["macrocyclic-lactone"])
    check("combo names both classes", fc.anthelmintic_classes("Ivermectin + Fenbendazole + Iron") == ["benzimidazole", "macrocyclic-lactone"])
    check("supportive-only = no anthelmintic", fc.anthelmintic_classes("iron and vitamin B") == [])

    def animal(fecs):
        return {"id": "t", "health": {"fec_history": [{"date": d, "fec": v} for d, v in fecs]}}

    dd = _date(2026, 3, 1)
    # complete FECRT: 800 -> 20 at day 12 = 97.5% effective
    r = fc.fecrt_for_drench(animal([("2026-03-01", 800), ("2026-03-13", 20)]), dd, "macrocyclic-lactone")
    check("complete FECRT computes reduction", r["status"] == "complete" and r["reduction_pct"] == 97.5)
    check("effective band (>=95%)", r["verdict"] == "effective")
    # resistant: 800 -> 200 = 75%
    r = fc.fecrt_for_drench(animal([("2026-03-01", 800), ("2026-03-13", 200)]), dd, "benzimidazole")
    check("resistant band (<90%)", r["verdict"] == "resistant" and r["reduction_pct"] == 75.0)
    # suspected: 800 -> 72 = 91%
    r = fc.fecrt_for_drench(animal([("2026-03-01", 800), ("2026-03-13", 72)]), dd, "macrocyclic-lactone")
    check("suspected band (90-95%)", r["verdict"] == "suspected")
    # off-window post is flagged, not dropped
    r = fc.fecrt_for_drench(animal([("2026-03-01", 800), ("2026-03-19", 20)]), dd, "macrocyclic-lactone")
    check("off-window post flagged not dropped", r["status"] == "complete" and r["flags"])
    # gaps: no post, no pre, no fec
    check("no post FEC -> no_post", fc.fecrt_for_drench(animal([("2026-03-01", 800)]), dd, "x")["status"] == "no_post")
    check("no pre FEC -> no_pre", fc.fecrt_for_drench(animal([("2026-03-13", 20)]), dd, "x")["status"] == "no_pre")
    check("no fec at all -> no_fec", fc.fecrt_for_drench(animal([]), dd, "x")["status"] == "no_fec")
    check("pre FEC of 0 -> undefined (no_pre)", fc.fecrt_for_drench(animal([("2026-03-01", 0), ("2026-03-13", 0)]), dd, "x")["status"] == "no_pre")

    # efficacy table aggregates worst-case per class
    db = {"sheep": [
        {"id": "a", "health": {"treatments": [{"date": "2026-03-01", "treatment": "Ivermectin"}],
                               "fec_history": [{"date": "2026-03-01", "fec": 800}, {"date": "2026-03-13", "fec": 200}]}},
    ]}
    tbl = fc.efficacy_table(fc.all_drenches(db))
    check("table verdict = worst FECRT (resistant)", tbl["macrocyclic-lactone"]["status_here"] == "resistant")
    empty = fc.efficacy_table(fc.all_drenches({"sheep": [
        {"id": "b", "health": {"treatments": [{"date": "2026-03-01", "treatment": "Fenbendazole"}]}}]}))
    check("no paired FEC -> unknown, not a guess", empty["benzimidazole"]["status_here"] == "unknown_no_paired_fec")
    return fails


_ep_spec = importlib.util.spec_from_file_location("ep", os.path.join(_here, "ewe_productivity.py"))
ep = importlib.util.module_from_spec(_ep_spec)
_ep_spec.loader.exec_module(ep)


def ewe_productivity_tests():
    """Pins for the MCS-18 lifetime ledger — lambing grouping, survival classes, flags."""
    fails = []

    def check(name, cond):
        print(f"  {'ok  ' if cond else 'FAIL'} {name}")
        if not cond:
            fails.append(name)

    def db(*sheep):
        return {"sheep": list(sheep)}

    dam = {"id": "mama", "name": "Mama", "sex": "ewe", "status": "alive"}
    # twins share a dob = ONE lambing; a later dob = a second lambing
    kids = [
        {"id": "a", "dam_id": "mama", "dob": "2023-01-10", "status": "alive"},
        {"id": "b", "dam_id": "mama", "dob": "2023-01-10", "status": "sold"},     # twin
        {"id": "c", "dam_id": "mama", "dob": "2024-02-01", "status": "deceased"},
        {"id": "d", "dam_id": "mama", "dob": None, "status": "unknown"},          # undated
    ]
    row = ep.productivity(db(dam, *kids))[0]
    check("twins on one dob = one lambing", any(l["date"] == "2023-01-10" and l["lambs"] == 2 for l in row["lambing_detail"]))
    check("distinct dob = separate lambing", row["lambings"] == 3)  # 2023, 2024, undated
    check("lambs_born counts all offspring", row["lambs_born"] == 4)
    check("surviving = alive|sold|gifted", row["surviving_to_date"] == 2)
    check("died = deceased", row["died"] == 1)
    check("unknown surfaced, not folded", row["unknown_status"] == 1)
    check("lambs_per_lambing = born/lambings", row["lambs_per_lambing"] == round(4 / 3, 2))
    check("undated offspring flagged", any("undated" in f for f in row["flags"]))
    check("unknown status flagged", any("unknown" in f for f in row["flags"]))

    # a dam_id pointing at a RAM is flagged (mis-set parent link)
    ram = {"id": "pops", "name": "Pops", "sex": "ram", "status": "alive"}
    rrow = ep.productivity(db(ram, {"id": "x", "dam_id": "pops", "dob": "2026-01-01", "status": "alive"}))[0]
    check("dam_id resolving to a ram is flagged", any("RAM" in f for f in rrow["flags"]))

    # ordering: more surviving lambs ranks first
    d2 = db(
        {"id": "lo", "name": "Lo", "sex": "ewe", "status": "alive"},
        {"id": "hi", "name": "Hi", "sex": "ewe", "status": "alive"},
        {"id": "l1", "dam_id": "lo", "dob": "2026-01-01", "status": "alive"},
        {"id": "h1", "dam_id": "hi", "dob": "2026-01-01", "status": "alive"},
        {"id": "h2", "dam_id": "hi", "dob": "2025-01-01", "status": "alive"},
    )
    order = [r["ewe_id"] for r in ep.productivity(d2)]
    check("most-productive-first ordering", order[0] == "hi")
    return fails


_tr_spec = importlib.util.spec_from_file_location("traits", os.path.join(_here, "ebv", "traits.py"))
tr = importlib.util.module_from_spec(_tr_spec)
_tr_spec.loader.exec_module(tr)


def h2_prior_tests():
    """Pins for the MCS-27 h2 calibration priors (grounded half; factor tables deferred)."""
    fails = []

    def check(name, cond):
        print(f"  {'ok  ' if cond else 'FAIL'} {name}")
        if not cond:
            fails.append(name)

    p = tr.FLORIDA_CRACKER_H2
    check("FL Cracker FEC prior = 0.33", p["FEC"] == 0.33)
    check("FL Cracker FAMACHA prior = 0.31", p["FAMACHA"] == 0.31)
    check("FL Cracker PCV/BCS priors", p["PCV"] == 0.22 and p["BCS"] == 0.19)
    check("resilience band 0.10-0.19", p["resilience"] == (0.10, 0.19))
    check("retain-pre-treatment rule present", tr.RETAIN_PRE_TREATMENT_RECORDS is True)
    # the calibration is OPT-IN: it must NOT have silently overwritten the live generic priors
    check("live PR h2 unchanged (opt-in, not auto-applied)", tr.TRAITS["PR"]["h2"] == 0.25)
    check("existing traits intact", set(tr.TRAITS) >= {"PR", "WWT", "PWT", "MWT", "ADG", "NLW", "MILK"})
    return fails


def fat_tail_tests():
    """Pins for the MCS-20 fat-tail phenotype + lineage tool: ancestry summation, expectation
    banding, append-only writer, range validation, legacy-observation read, expected-vs-observed."""
    fails = []

    def check(name, cond):
        print(f"  {'ok  ' if cond else 'FAIL'} {name}")
        if not cond:
            fails.append(name)

    _ft_spec = importlib.util.spec_from_file_location("ft", os.path.join(_here, "fat_tail.py"))
    ft = importlib.util.module_from_spec(_ft_spec)
    _ft_spec.loader.exec_module(ft)

    # ancestry summation across fat-tailed breeds; non-numeric skipped
    s = {"breed_composition": {"percentages": {"Awassi": 44, "Katahdin": 56}}}
    pct, breeds = ft.fat_tailed_ancestry(s)
    check("ancestry sums Awassi only (44)", pct == 44 and any("Awassi" in b for b in breeds))
    s2 = {"breed_composition": {"percentages": {"Tunis": 25, "Awassi": 25}}}
    check("ancestry sums multiple fat-tailed breeds (50)", ft.fat_tailed_ancestry(s2)[0] == 50)
    bad = {"breed_composition": {"percentages": {"Awassi": "lots"}}}
    check("ancestry skips non-numeric pct", ft.fat_tailed_ancestry(bad)[0] == 0)

    # expectation bands
    check("expectation high >=50", ft.expectation(50) == "high")
    check("expectation some >=12", ft.expectation(12) == "some" and ft.expectation(25) == "some")
    check("expectation trace >0", ft.expectation(5) == "trace")
    check("expectation none =0", ft.expectation(0) == "none")

    # writer append-only + drops None
    a = {"id": "t"}
    ft.record_fat_tail_score(a, "2026-06-11", 2, observer="ken")
    check("record_fat_tail_score appends", len(a["fat_tail_scores"]) == 1 and a["fat_tail_scores"][0]["score"] == 2)
    check("record drops None", "notes" not in a["fat_tail_scores"][0])

    # validate: range, bool, date, unknown key
    b = {"id": "b", "fat_tail_scores": [
        {"date": "2026-06-01", "score": 4},        # over range (max 3)
        {"date": "2026-06-01", "score": True},     # bool
        {"date": "bad", "score": 2},               # bad date
        {"date": "2026-06-01", "score": 2, "x": 1}]}  # unknown key
    iss = ft.validate_fat_tail(b)
    check("validator flags over-range (>3)", any("score 4" in i for i in iss))
    check("validator flags bool", any("score True" in i for i in iss))
    check("validator flags bad date", any("unparseable date" in i for i in iss))
    check("validator flags unknown key", any("unknown key" in i for i in iss))

    # legacy observation is read (not discarded), newest first
    leg = {"fat_tail_scores": [{"date": "2026-06-11", "score": 2, "observation": "wide"}],
           "fat_tail_observation": {"date": "2026-01-01", "observation": "legacy note"}}
    obs = ft._observations(leg)
    check("legacy + structured both read", len(obs) == 2)
    check("observations newest first", obs[0]["date"] == "2026-06-11")

    # lineage_view: expected-no-obs flag; observed-no-ancestry flag; thin-tailed excluded
    db = {"sheep": [
        {"id": "awassi_hi", "status": "alive", "breed_composition": {"percentages": {"Awassi": 95}}},
        {"id": "thin", "status": "alive", "breed_composition": {"percentages": {"Katahdin": 100}}},
        {"id": "surprise", "status": "alive", "breed_composition": {"percentages": {"Katahdin": 100}},
         "fat_tail_scores": [{"date": "2026-06-01", "score": 3}]},
    ]}
    view = {r["id"]: r for r in ft.lineage_view(db)}
    check("thin-tailed no-obs animal excluded", "thin" not in view)
    check("high-ancestry no-obs is flagged a gap", "no observation" in (view["awassi_hi"]["flag"] or ""))
    check("observed-without-ancestry flagged", "no fat-tailed ancestry" in (view["surprise"]["flag"] or ""))

    # live flock: the 95% Awassi Windlestone animals appear, expected high
    live = json.loads(open(os.path.join(_here, "..", "data", "flock_database.json")).read())
    lv = {r["id"]: r for r in ft.lineage_view(live)}
    check("live: a Windlestone fat-tail animal is expected high",
          any(r["expectation"] == "high" and r["ancestry_pct"] >= 88 for r in lv.values()))
    return fails


def coat_shed_tests():
    """Pins for the MCS-19 coat/shed trait log: coat classification, append-only shed writer,
    score-range validation, peak-window selection, and the never-false-zero gap rule."""
    fails = []

    def check(name, cond):
        print(f"  {'ok  ' if cond else 'FAIL'} {name}")
        if not cond:
            fails.append(name)

    _cs_spec = importlib.util.spec_from_file_location("cs", os.path.join(_here, "coat_shed.py"))
    cs = importlib.util.module_from_spec(_cs_spec)
    _cs_spec.loader.exec_module(cs)

    # coat_classify — intermediate wording wins over a bare wool/hair substring
    check("classify intermediate-to-wool-leaning", cs.coat_classify("intermediate-to-wool-leaning")[0] == "intermediate")
    check("classify hair", cs.coat_classify("hair (per owner)")[0] == "hair")
    check("classify wool", cs.coat_classify("heavy wool fleece")[0] == "wool")
    check("classify hair+wool -> intermediate", cs.coat_classify("smooth hair with wool patches")[0] == "intermediate")
    check("classify empty -> unknown", cs.coat_classify("")[0] == "unknown")

    # record_shed_score append-only, drops None
    s = {"id": "t"}
    cs.record_shed_score(s, "2026-07-15", 4, observer="ken")
    cs.record_shed_score(s, "2026-08-01", 5)
    check("record_shed_score appends", len(s["shed_scores"]) == 2 and s["shed_scores"][0]["score"] == 4)
    check("record_shed_score drops None", "notes" not in s["shed_scores"][0])

    # validate_shed — range, type, bool, date, unknown key
    bad = {"id": "b", "shed_scores": [
        {"date": "2026-07-01", "score": 6},          # over range
        {"date": "2026-07-01", "score": -1},         # under range
        {"date": "2026-07-01", "score": "3"},        # non-numeric
        {"date": "2026-07-01", "score": True},       # bool
        {"date": "bad", "score": 3},                 # bad date
        {"date": "2026-07-01", "score": 3, "x": 1},  # unknown key
    ]}
    iss = cs.validate_shed(bad)
    check("validator flags over-range score", any("score 6" in i for i in iss))
    check("validator flags bool score", any("score True" in i for i in iss))
    check("validator flags bad date", any("unparseable date" in i for i in iss))
    check("validator flags unknown key", any("unknown key" in i for i in iss))
    check("clean shed score validates", cs.validate_shed(s) == [])

    # _latest_peak_score: summer counts, April doesn't; None when no peak score
    peaky = {"shed_scores": [{"date": "2026-04-10", "score": 1}, {"date": "2026-07-20", "score": 4},
                             {"date": "2026-08-15", "score": 5}]}
    lp = cs._latest_peak_score(peaky)
    check("latest peak score is the Aug one", lp is not None and lp[1] == 5)
    check("no peak score -> None (not 0)", cs._latest_peak_score({"shed_scores": [{"date": "2026-04-10", "score": 1}]}) is None)

    # selection_view: poor-shedder flag, wool excluded, gap never scored 0
    db = {"sheep": [
        {"id": "poor", "status": "alive", "coat_observed": "hair",
         "shed_scores": [{"date": "2026-07-10", "score": 1}]},
        {"id": "good", "status": "alive", "coat_observed": "hair",
         "shed_scores": [{"date": "2026-07-10", "score": 5}]},
        {"id": "woolly", "status": "alive", "coat_observed": "heavy wool"},
        {"id": "nodata", "status": "alive", "coat_observed": "hair"},
    ]}
    view = cs.selection_view(db)
    ids = {r["id"]: r for r in view}
    check("wool animal excluded from shedding view", "woolly" not in ids)
    check("poor shedder flagged", ids["poor"]["flag"] == "POOR SHEDDER")
    check("good shedder not flagged", ids["good"].get("flag") is None)
    check("no-data animal is a gap, not score 0", ids["nodata"]["peak_score"] is None)
    return fails


def health_event_tests():
    """Pins for the MCS-26 typed health-event log: append-only writer, schema/vocabulary
    validation, free-text candidate detection (health-context only), and the unified timeline."""
    fails = []

    def check(name, cond):
        print(f"  {'ok  ' if cond else 'FAIL'} {name}")
        if not cond:
            fails.append(name)

    _he_spec = importlib.util.spec_from_file_location("he", os.path.join(_here, "health_events.py"))
    he = importlib.util.module_from_spec(_he_spec)
    _he_spec.loader.exec_module(he)

    # record_event: append-only, pure addition
    s = {"id": "t", "health": {}}
    he.record_event(s, "2026-01-01", "foot_rot", body_location="left rear", outcome="resolved")
    he.record_event(s, "2026-02-01", "abscess", treatment="lanced")
    ev = s["health"]["health_events"]
    check("record_event appends (append-only)", len(ev) == 2 and ev[0]["condition"] == "foot_rot")
    check("record_event drops None fields", "diagnosis" not in ev[0])

    # validate_events: catches bad date, unknown condition, unknown outcome, unknown key
    bad = {"id": "b", "health": {"health_events": [
        {"date": "not-a-date", "condition": "foot_rot"},
        {"date": "2026-01-01", "condition": "wobblies"},          # not in vocab
        {"date": "2026-01-01", "condition": "abscess", "outcome": "vanished"},  # bad outcome
        {"date": "2026-01-01", "condition": "abscess", "bogus": 1},  # unknown key
    ]}}
    iss = he.validate_events(bad)
    check("validator flags unparseable date", any("unparseable date" in i for i in iss))
    check("validator flags out-of-vocab condition", any("not in vocabulary" in i for i in iss))
    check("validator flags bad outcome", any("not a known outcome" in i for i in iss))
    check("validator flags unknown key", any("unknown key" in i for i in iss))
    check("clean typed event validates", he.validate_events(s) == [])

    # _classify maps phrases; scan only health-context (a mastitis in a BREED note is not a candidate)
    check("classify foot rot -> foot_rot", he._classify("Terramycin (foot rot)") == ["foot_rot"])
    check("classify abscess", "abscess" in he._classify("Flushed abscess."))
    db = {"sheep": [
        {"id": "a", "notes": "breed page mentions mastitis lineage", "health": {"treatments": []}},
        {"id": "b", "health": {"treatments": [{"date": "2023", "treatment": "Terramycin (foot rot)"}]}},
    ]}
    cands = he.scan_candidates(db)
    check("scan finds foot_rot in treatment", any(c["sheep_id"] == "b" and c["condition"] == "foot_rot" for c in cands))
    check("scan does NOT read breed-prose notes (no mastitis candidate)",
          not any(c["condition"] == "mastitis" for c in cands))

    # scan skips an already-typed event (dedup by date+condition)
    db2 = {"sheep": [{"id": "b", "health": {
        "treatments": [{"date": "2023-01-01", "treatment": "foot rot"}],
        "health_events": [{"date": "2023-01-01", "condition": "foot_rot"}]}}]}
    check("scan skips already-typed event", he.scan_candidates(db2) == [])

    # timeline merges + sorts across collections
    tl_sheep = {"id": "t", "health": {
        "famacha_scores": [{"date": "2026-03-01", "score": 3}],
        "fec_history": [{"date": "2026-01-15", "fec": 400}],
        "treatments": [{"date": "2026-02-01", "treatment": "Ivermectin"}],
        "vaccinations": [{"date": "2026-04-01", "vaccine": "CDT"}],
        "health_events": [{"date": "2026-01-01", "condition": "foot_rot"}]}}
    tl = he.animal_timeline(tl_sheep)
    check("timeline merges all 5 kinds", len(tl) == 5)
    check("timeline sorted by date", [e["date"] for e in tl] == sorted(e["date"] for e in tl))
    check("timeline first is the event, last the vaccination", tl[0]["kind"] == "event" and tl[-1]["kind"] == "vaccination")

    # the real flock's foot_rot candidate is caught (tag-430-2079)
    live = json.loads(open(os.path.join(_here, "..", "data", "flock_database.json")).read())
    lc = he.scan_candidates(live)
    check("live: foot_rot candidate on tag-430-2079",
          any(c["condition"] == "foot_rot" and c["sheep_id"] == "tag-430-2079" for c in lc))
    return fails


def withdrawal_tests():
    """Pins for MCS-7 meat/milk withdrawal engine. The engine must (a) compute clear dates
    correctly from a CONFIRMED interval, (b) NEVER report clear for an unconfirmed drug, and
    (c) surface an unrecognized treatment rather than silently clear it."""
    fails = []

    def check(name, cond):
        print(f"  {'ok  ' if cond else 'FAIL'} {name}")
        if not cond:
            fails.append(name)

    import datetime as _dt
    _wc_spec = importlib.util.spec_from_file_location("wc", os.path.join(_here, "withdrawal_check.py"))
    wc = importlib.util.module_from_spec(_wc_spec)
    _wc_spec.loader.exec_module(wc)

    # synthetic reference: one confirmed 28-day meat drug, one unconfirmed, one nutritional
    ref = {
        "confirmedrug": {"drug_key": "confirmedrug", "generic": "cx", "class": "antibiotic",
                         "withdrawal_days_meat": 28, "withdrawal_days_milk": 96, "status": "vet_confirmed"},
        "mystery": {"drug_key": "mystery", "generic": "mx", "class": "anthelmintic",
                    "withdrawal_days_meat": None, "withdrawal_days_milk": None, "status": "NEEDS_VET_CONFIRMATION"},
        "iron": {"drug_key": "iron", "generic": "iron", "class": "nutritional",
                 "withdrawal_days_meat": 0, "withdrawal_days_milk": 0, "status": "no_withdrawal"},
    }
    td = _dt.date(2026, 1, 1)
    t = {"date": "2026-01-01", "treatment": "ConfirmeDrug 5mL"}

    # (a) date math: last in-withdrawal day is treat+28 (2026-01-29); clear the day after
    r_meat = [x for x in wc.withdrawal_for_treatment("t", t, ref, _dt.date(2026, 1, 29)) if x["kind"] == "meat"][0]
    check("day 28 still in_withdrawal", r_meat["status"] == "in_withdrawal" and r_meat["clear_date"] == "2026-01-29")
    r_after = [x for x in wc.withdrawal_for_treatment("t", t, ref, _dt.date(2026, 1, 30)) if x["kind"] == "meat"][0]
    check("day 29 (after clear) is clear", r_after["status"] == "clear")
    r_milk = [x for x in wc.withdrawal_for_treatment("t", t, ref, _dt.date(2026, 3, 1)) if x["kind"] == "milk"][0]
    check("milk interval independent of meat (96d)", r_milk["status"] == "in_withdrawal" and r_milk["clear_date"] == "2026-04-07")

    # (b) unconfirmed drug NEVER reads clear — meat and milk both unknown_interval
    mt = {"date": "2020-01-01", "treatment": "Mystery drench"}
    rs = wc.withdrawal_for_treatment("t", mt, ref, _dt.date(2026, 1, 1))
    check("unconfirmed drug -> unknown_interval (never clear)",
          all(x["status"] == "unknown_interval" for x in rs) and len(rs) == 2)

    # (c) nutritional -> no_withdrawal ; unrecognized string surfaced, not cleared
    nt = {"date": "2026-01-01", "treatment": "Iron 3mL"}
    check("nutritional -> no_withdrawal",
          all(x["status"] == "no_withdrawal" for x in wc.withdrawal_for_treatment("t", nt, ref, _dt.date(2026, 6, 1))))
    ut = {"date": "2026-01-01", "treatment": "Hoof trim"}
    rs_u = wc.withdrawal_for_treatment("t", ut, ref, _dt.date(2026, 1, 1))
    check("unrecognized treatment surfaced", len(rs_u) == 1 and rs_u[0]["status"] == "unrecognized")

    # (d) word-boundary matching: 'vb12' matches vb but 'ivermectin' isn't a false 'iron' hit
    live = wc.load_reference()
    keys = {d["drug_key"] for d in wc.match_drugs("Ivermectin + Fenbendazole + VB 3mL + Iron 2mL", live)}
    check("combo string matches ivermectin+fenbendazole+vb+iron",
          {"ivermectin", "fenbendazole", "vb", "iron"} <= keys)

    # (e) shipped reference authors NO withdrawal numbers for real drugs (all NEEDS_VET_CONFIRMATION)
    real_drugs = [d for d in live.values() if d["class"] in ("anthelmintic", "antibiotic", "coccidiostat", "vaccine")]
    check("no fabricated intervals for real drugs in shipped reference",
          all(d["status"] == "NEEDS_VET_CONFIRMATION" and d["withdrawal_days_meat"] is None for d in real_drugs))

    # (f) gaps worklist finds the 6 real drugs actually used in the flock
    db = json.loads(open(os.path.join(_here, "..", "data", "flock_database.json")).read())
    g = wc.gaps(db, live)
    check("gaps worklist lists ivermectin & fenbendazole & nuflor",
          {"ivermectin", "fenbendazole", "nuflor"} <= {r["drug"] for r in g})
    return fails


def pedigree_tests():
    """Pins for the pedigree-integrity + mate-COI tool and the cycle-guard hardening of
    ebv/pedigree.py. Two halves: (a) the safety hardening changed NO value on the acyclic
    real flock; (b) the new advisory's math and honesty guarantees hold."""
    fails = []

    def check(name, cond):
        print(f"  {'ok  ' if cond else 'FAIL'} {name}")
        if not cond:
            fails.append(name)

    _pe_spec = importlib.util.spec_from_file_location(
        "ebv_pedigree", os.path.join(_here, "ebv", "pedigree.py"))
    P = importlib.util.module_from_spec(_pe_spec)
    _pe_spec.loader.exec_module(P)
    _pi_spec = importlib.util.spec_from_file_location(
        "pedigree_integrity", os.path.join(_here, "pedigree_integrity.py"))
    pi = importlib.util.module_from_spec(_pi_spec)
    _pi_spec.loader.exec_module(pi)

    ped = P.load_pedigree(os.path.join(_here, "..", "data", "flock_database.json"))

    # (a) OUTPUT-PRESERVATION: the cycle guard must not perturb acyclic real-flock values.
    if "broken-tail" in ped:
        check("F(broken-tail) preserved = 0.375", round(P.inbreeding("broken-tail", ped), 4) == 0.375)
    if "half-tail" in ped:
        check("F(half-tail) preserved = 0.25", round(P.inbreeding("half-tail", ped), 4) == 0.25)
    if "broken-tail" in ped and "half-tail" in ped:
        check("A(broken-tail,half-tail) preserved = 1.0",
              round(P.relationship("broken-tail", "half-tail", ped), 4) == 1.0)

    # (a) CYCLE GUARD: a cyclic pedigree raises the TYPED error, never a RecursionError.
    c3 = {"x": {"sire": "y", "dam": "z", "dob": "", "sex": "ram"},
          "y": {"sire": "z", "dam": "x", "dob": "", "sex": "ewe"},
          "z": {"sire": "x", "dam": "y", "dob": "", "sex": "ram"}}
    try:
        P.relationship("x", "y", c3)
        check("3-cycle raises PedigreeCycleError", False)
    except P.PedigreeCycleError:
        check("3-cycle raises PedigreeCycleError", True)
    except RecursionError:
        check("3-cycle raises PedigreeCycleError (got RecursionError)", False)

    # (b) coi_band boundaries (relationship equivalents, F=0.25*A)
    check("band low  <0.0625", pi.coi_band(0.06) == "low")
    check("band watch 0.0625", pi.coi_band(0.0625) == "watch")
    check("band high  0.125", pi.coi_band(0.125) == "high")
    check("band severe 0.25", pi.coi_band(0.25) == "severe")
    check("band unknown None", pi.coi_band(None) == "unknown")

    # (b) find_cycles catches a synthetic cycle; the real flock is clean
    check("find_cycles detects a synthetic 3-cycle", len(pi.find_cycles(c3)) >= 1)
    rep = pi.integrity_report({"sheep": [{"id": k, "sire_id": v["sire"], "dam_id": v["dam"],
                                          "dob": v["dob"], "sex": v["sex"]} for k, v in ped.items()]})
    check("real flock pedigree is CLEAN", rep["clean"] is True)

    # (b) mate_coi honesty: self invalid, unrelated F=0, sex-swap warns, unknown id typed
    check("mate self -> invalid", pi.mate_coi("half-tail", "half-tail", ped)["status"] == "invalid")
    check("mate unknown -> typed", pi.mate_coi("half-tail", "nope-xyz", ped)["status"] == "unknown_dam")
    if "merrie" in ped and "lara" in ped:
        r = pi.mate_coi("merrie", "lara", ped)
        check("unrelated mate F=0 low", r["lamb_F"] == 0 and r["band"] == "low")
    if "merrie" in ped and "serendipity" in ped:
        r = pi.mate_coi("merrie", "serendipity", ped)
        check("live watch mate merrie x serendipity F=0.0938",
              r["lamb_F"] == 0.0938 and r["band"] == "watch" and "sir-loin" in r["shared_ancestors"])
        r2 = pi.mate_coi("serendipity", "merrie", ped)  # sexes swapped
        check("sex-swapped mate warns twice", len(r2["warnings"]) == 2)

    # (b) F census omits (never false-zeroes) animals lacking both parents
    fc = pi.flock_inbreeding({"sheep": [{"id": "orphan", "status": "alive", "sire_id": None, "dam_id": None}]},
                             {"orphan": {"sire": None, "dam": None, "dob": None, "sex": "ewe"}})
    check("F census omits a both-parents-missing animal", fc == [])
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
    print("\nMCS-3 attention-triage pins:")
    failures += triage_tests()
    print("\nMCS-30 FECRT pins:")
    failures += fecrt_tests()
    print("\nMCS-18 ewe-productivity pins:")
    failures += ewe_productivity_tests()
    print("\nMCS-27 h2-prior pins:")
    failures += h2_prior_tests()
    print("\nMCS-20 fat-tail-lineage pins:")
    failures += fat_tail_tests()
    print("\nMCS-19 coat/shed-trait pins:")
    failures += coat_shed_tests()
    print("\nMCS-26 health-event-log pins:")
    failures += health_event_tests()
    print("\nMCS-7 withdrawal-clearance pins:")
    failures += withdrawal_tests()
    print("\nPedigree-integrity + mate-COI + cycle-guard pins:")
    failures += pedigree_tests()
    if failures:
        print(f"\n{len(failures)} FAILURE(S): {failures}")
        sys.exit(1)
    print(f"\nAll {len(CASES)} breed-percentage + FAMACHA + pen + deworm + triage + FECRT + productivity guard pins passed.")


if __name__ == "__main__":
    main()
