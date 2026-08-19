#!/usr/bin/env python3
"""Regression pins for the 2026-08-18 flock-health work. Soli Deo Gloria.

Covers: famacha key normalization (mcs-famacha-schema-normalization) — the migration's
zero-loss fingerprint and the validator regression guard; the data-hygiene report
(mcs-health-record-validation); and the health-event log cross-check (mcs-health-event-log).

Run: python3 scripts/test_flock_health.py   (exit 0 = pass). No framework — the repo has none.
"""
import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path

_here = os.path.dirname(os.path.abspath(__file__))


def _load(name, fname):
    spec = importlib.util.spec_from_file_location(name, os.path.join(_here, fname))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


vf = _load("vf", "validate_flock.py")
mig = _load("mig", "migrate_famacha_keys.py")

FAILURES = []


def check(name, got, expect):
    ok = got == expect
    print(f"  {'ok  ' if ok else 'FAIL'} {name}: got={got!r} expected={expect!r}")
    if not ok:
        FAILURES.append(name)


# --- famacha key regression guard -------------------------------------------------
legacy = [{"id": "t1", "health": {"famacha_scores": [{"date": "1-1-26", "famacha": 3}]}},
          {"id": "t2", "health": {"famacha_history": [{"date": "2026-01-01", "score": "2", "note": "x"}]}},
          {"id": "t3", "health": {"famacha_scores": [{"date": "1-1-26", "score": 2}]}}]
errs = vf.validate_famacha_keys(legacy)
check("legacy 'famacha' key errors", any("t1" in e for e in errs), True)
check("legacy 'note' key errors", any("t2" in e for e in errs), True)
check("canonical 'score' key clean", any("t3" in e for e in errs), False)

# --- migration: renames, zero-loss fingerprint, idempotency ------------------------
db = {"sheep": [{"id": "a", "health": {"famacha_scores": [{"date": "d", "famacha": 4}],
                                       "famacha_history": [{"date": "d", "score": "3", "note": "n"}]}}]}
before = mig.famacha_fingerprint(db)
r1 = mig.migrate(db)
check("migration renames counted", r1, (1, 1))
check("fingerprint unchanged", mig.famacha_fingerprint(db) == before, True)
check("migrated entry uses score", "score" in db["sheep"][0]["health"]["famacha_scores"][0], True)
check("migrated entry dropped famacha", "famacha" in db["sheep"][0]["health"]["famacha_scores"][0], False)
r2 = mig.migrate(db)
check("idempotent second pass", r2, (0, 0))
check("post-migration validator clean", vf.validate_famacha_keys(db["sheep"]), [])

# --- data hygiene -------------------------------------------------------------------
sheep = [
    {"id": "alive-no-pen", "status": "alive"},
    {"id": "alive-penned", "status": "alive", "pen": "Pen 1"},
    {"id": "suspect-alive", "status": "alive", "pen": "Pen 2", "status_date": "2026-04-02"},
    {"id": "suspect-dead", "status": "deceased", "status_date": "2026-04-06"},
    {"id": "unclear", "status": "sold", "notes": "tag [UNCLEAR] read"},
    {"id": "notesonly", "status": "alive", "pen": "P", "health": {"famacha_scores": [{"date": "d", "notes": "booster"}]}},
]
w = vf.validate_data_hygiene(sheep)
check("no-pen aggregate warns", any("have no pen" in x for x in w), True)
check("no-pen count correct (1 of 4 alive)", any("1/4" in x for x in w), True)
check("suspect dates warn, alive named", any("suspect-alive" in x for x in w), True)
check("[UNCLEAR] counted", any("1 [UNCLEAR]" in x for x in w), True)
check("scoreless famacha entries counted", any("no score at all" in x for x in w), True)
check("clean flock produces no hygiene warnings",
      vf.validate_data_hygiene([{"id": "c", "status": "alive", "pen": "P"}]), [])

# --- health-event log cross-check ----------------------------------------------------
def events_check(lines, sheep_ids=("lamb-1",)):
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as f:
        f.write("\n".join(lines) + "\n")
        tmp = f.name
    saved = vf.HEALTH_EVENTS_PATH
    try:
        vf.HEALTH_EVENTS_PATH = Path(tmp)
        return vf.validate_health_events([{"id": i} for i in sheep_ids])
    finally:
        vf.HEALTH_EVENTS_PATH = saved
        os.unlink(tmp)


GOOD = json.dumps({"event_id": "e1", "animal_id": "lamb-1", "type": "death",
                   "date": "2026-08-11/2026-08-18", "source": "owner", "recorded_at": "t",
                   "details": "x"})
check("good event passes", events_check([GOOD]), [])
check("unparseable line errors", any("unparseable" in x for x in events_check(["{nope"])), True)
check("unknown animal errors",
      any("not in flock DB" in x for x in events_check([GOOD.replace("lamb-1", "ghost")])), True)
check("unknown type errors",
      any("unknown type" in x for x in events_check([GOOD.replace('"death"', '"exorcism"')])), True)
check("duplicate event_id errors",
      any("duplicate" in x for x in events_check([GOOD, GOOD])), True)
check("missing field errors",
      any("missing field 'source'" in x for x in events_check([GOOD.replace('"source": "owner", ', '')])), True)

# --- MCS-7 withdrawal lookup ---------------------------------------------------------
hl = _load("hl", "health_log.py")
d, basis, _ = hl.lookup_withdrawal("levamisole (Prohibit)")
check("Prohibit -> 3d sheep label", (d, "label" in basis), (3, True))
d, basis, _ = hl.lookup_withdrawal("ivermectin (horse paste)")
check("ivermectin -> 14d house default", (d, "house default" in basis), (14, True))
d, basis, _ = hl.lookup_withdrawal("fenbendazole")
check("fenbendazole -> 28d FARAD", d, 28)
d, basis, _ = hl.lookup_withdrawal("unicorn dust")
check("unknown drug -> no number invented", d, None)

# --- MCS-8 advisor matrix ------------------------------------------------------------
da = _load("da", "deworm_advisor.py")
import datetime as _dt
TODAY = _dt.date(2026, 8, 18)
fresh = TODAY - _dt.timedelta(days=3)
stale = TODAY - _dt.timedelta(days=120)

def adv(score, when, epg):
    return da.advise(score, when, epg, TODAY, 1000, 500, 14)

check("F5 fresh, no FEC -> RED treat + pre-dose sample",
      (adv(5, fresh, None)[1], "BEFORE" in adv(5, fresh, None)[2]), ("RED", True))
check("F5 stale -> RED but re-score first",
      "RE-SCORE" in adv(5, stale, None)[2], True)
check("F4 + low FEC -> RED mismatch investigate",
      "MISMATCH" in adv(4, fresh, 100)[2], True)
check("F1 + high FEC -> AMBER contamination mismatch",
      (adv(1, fresh, 1500)[1], "MISMATCH" in adv(1, fresh, 1500)[2]), ("AMBER", True))
check("F1 fresh, no FEC -> GREEN", adv(1, fresh, None)[1], "GREEN")
check("F2 stale -> AMBER re-score", adv(2, stale, None)[1], "AMBER")
check("range score '1-2' reads worst end", da.parse_score("1-2"), 2)
check("M-D-YY date parses", da.parse_date("3-13-26"), _dt.date(2026, 3, 13))
check("garbage date -> None not guessed", da.parse_date("next tuesday"), None)

# --- notes migration idempotency (module-level, synthetic) ----------------------------
mn = _load("mn", "migrate_notes_to_events.py")
check("M-D-YY -> ISO", mn.to_iso("2-12-26"), "2026-02-12")
check("bad date -> None", mn.to_iso("2025-2026"), None)

# --- MCS-3 triage scoring ------------------------------------------------------------
ft = _load("ft", "flock_triage.py")
T = _dt.date(2026, 8, 18)

def sc(**kw):
    base = dict(score=None, s_date=None, epg=None, trend_worse=False, days_since=None,
                cohort_loss_14d=False, pen_missing=False, today=T, fec_high=1000, stale_days=14)
    base.update(kw)
    return ft.score_animal(**base)[0]

check("fresh F5 scores 50+", sc(score=5, s_date=T - _dt.timedelta(days=2), days_since=2) >= 50, True)
check("stale F5 scores 35-base", sc(score=5, s_date=T - _dt.timedelta(days=120)) >= 35, True)
check("no famacha at all scores 25", sc(), 25)
check("cohort death adds 15", sc(cohort_loss_14d=True) - sc(), 15)
check("pen unknown adds 5", sc(pen_missing=True) - sc(), 5)
check("days-since capped at 10", sc(days_since=700) - sc(), 10)
check("same-day dup collapses to worst (no fake trend)",
      ft.famacha_series({"health": {"famacha_scores": [{"date": "2026-04-11", "score": 1}],
                                    "famacha_history": [{"date": "2026-04-11", "score": "1-2"}]}},
                        [], "x"),
      [(_dt.date(2026, 4, 11), 2)])

# --- pen canon (operator directive 2026-08-18: 8 pens, aliases resolve) ---------------
ph = _load("ph", os.path.join("lib", "pen_history.py"))
check("8 canonical pens exactly", len(ph.CANONICAL_PENS), 8)
check("Chicken Coop -> Tree Fort", ph.canonical_pen("Chicken Coop"), "Tree Fort")
check("Lamb Pen -> Goose Pen", ph.canonical_pen("Lamb Pen"), "Goose Pen")
check("canonical name passes through", ph.canonical_pen("Pen 4"), "Pen 4")
check("unknown name returned unchanged (validator flags, never invents)",
      ph.canonical_pen("Barn Annex"), "Barn Annex")
canon_db = {"sheep": [{"id": "a", "status": "alive", "pen": "Chicken Coop"}], "pens": {}}
check("alias in scalar pen is an ERROR",
      any("alias" in e for e in vf.validate_pen_canon(canon_db)), True)
check("canonical scalar pen is clean",
      vf.validate_pen_canon({"sheep": [{"id": "a", "pen": "Tree Fort"}], "pens": {}}), [])
mig_pa = _load("mpa", "migrate_pen_aliases.py")
tdb = {"sheep": [{"id": "a", "pen": "Chicken Coop",
                  "movements": [{"date": None, "from": None, "to": "Chicken Coop"}]}],
       "pens": {"tree_fort": {"display_name": "Tree Fort", "ewes": ["x"], "notes": "tf"},
                "chicken_coop": {"display_name": "Chicken Coop", "ewes": ["a"], "notes": "cc"}}}
ch = mig_pa.migrate(tdb)
check("alias migration renames scalar + movement + merges pens",
      (ch["scalar"], ch["moves"], ch["pens_merged"]), (1, 1, ["chicken_coop -> tree_fort"]))
check("merged roster is the union", sorted(tdb["pens"]["tree_fort"]["ewes"]), ["a", "x"])
check("both notes survive verbatim",
      "tf" in tdb["pens"]["tree_fort"]["notes"] and "cc" in tdb["pens"]["tree_fort"]["notes"], True)
check("alias recorded on canonical entry", tdb["pens"]["tree_fort"]["aliases"], ["Chicken Coop"])
check("alias migration idempotent", mig_pa.migrate(tdb)["scalar"], 0)

# --- MCS-6 batch session grammar + MCS-35 isolation ------------------------------------
wf = _load("wf", "work_flock.py")
a, plan = wf.parse_line('ewe1 f=3 w=82 wormer=prohibit vax=cdt fec=450 trim note="limp better"')
check("line parses all keys + flag", (a, len(plan)), ("ewe1", 7))
check("famacha kwarg typed", any(p["type"] == "famacha" and p["score"] == 3 for p in plan), True)
check("fec rides observation", any(p.get("fec_epg") == 450 for p in plan), True)
check("skip yields empty plan", wf.parse_line("ewe1 skip"), ("ewe1", []))
check("blank line yields nothing", wf.parse_line("   "), (None, []))
try:
    wf.parse_line("ewe1 sheared")   # not a known flag ('shear' is)
    check("unknown token raises", False, True)
except ValueError:
    check("unknown token raises", True, True)

import subprocess
import tempfile
with tempfile.TemporaryDirectory() as td:
    sess = os.path.join(td, "s.txt")
    log = os.path.join(td, "log.jsonl")
    open(sess, "w").write("lara f=1\n")
    env = dict(os.environ, HEALTH_LOG_PATH=log)
    r = subprocess.run([sys.executable, os.path.join(_here, "work_flock.py"),
                        "--from-file", sess, "--date", "2026-08-19", "--recorded-by", "test"],
                       capture_output=True, text=True, env=env)
    check("isolated session exits 0", r.returncode, 0)
    check("event landed in the ISOLATED log (MCS-35)",
          os.path.exists(log) and "lara-2026-08-19-famacha" in open(log).read(), True)

# --- chute app build (MCS-34 slice 1) ---------------------------------------------------
bca = _load("bca", "build_chute_app.py")
roster = bca.build_roster()
check("roster covers every living animal", len(roster) > 100, True)
check("roster rows carry the app's fields",
      all(set(r) >= {"id", "name", "tag", "pen", "score", "score_date", "rank"} for r in roster), True)
check("roster is triage-sorted (worst first)",
      all(a["rank"] >= b["rank"] for a, b in zip(roster, roster[1:])), True)
check("no deceased animal baked in",
      "lara-2026-lamb" not in {r["id"] for r in roster}, True)

# --- MCS-12 quantity shape --------------------------------------------------------------
q = _load("q", os.path.join("lib", "quantity.py"))
check("weight quantity builds", q.make_quantity("weight", 82.5),
      {"measure": "weight", "value": 82.5, "unit": "lbs"})
check("famacha 0 refused", bool_raises := (lambda: q.make_quantity("famacha", 0)) and True, True)
try:
    q.make_quantity("famacha", 0); check("famacha 0 raises", False, True)
except ValueError:
    check("famacha 0 raises", True, True)
try:
    q.make_quantity("vibes", 10); check("unknown measure raises", False, True)
except ValueError:
    check("unknown measure raises", True, True)
check("negative fec invalid via validate", q.validate_quantity({"measure": "fec", "value": -5, "unit": "epg"}) != [], True)
check("legacy famacha event normalizes to quantity",
      q.event_quantities({"type": "famacha", "score": 4}),
      [{"measure": "famacha", "value": 4, "unit": "score"}])
check("fec_epg field normalizes",
      q.event_quantities({"type": "observation", "fec_epg": 900}),
      [{"measure": "fec", "value": 900, "unit": "epg"}])
sers = q.quantity_series(
    [{"animal_id": "a", "date": "2026-08-01", "type": "weight",
      "quantity": {"measure": "weight", "value": 70, "unit": "lbs"}},
     {"animal_id": "a", "date": "2026-08-18", "type": "famacha", "score": 2},
     {"animal_id": "b", "date": "2026-08-18", "type": "famacha", "score": 5}],
    "a", "famacha")
check("series filters by animal+measure", sers, [("2026-08-18", 2)])

# --- MCS-18 ewe productivity ------------------------------------------------------------
ep = _load("ep", "ewe_productivity.py")
tdb18 = {"sheep": [{"id": "mama", "name": "Mama", "sex": "ewe", "status": "alive",
                    "aliases": ["Old Girl"]},
                   {"id": "kid1", "dam_id": "mama", "dob": "2025-03-01"},
                   {"id": "kid2", "dam_id": "mama", "dob": "2026-02-01"},
                   {"id": "orphan", "dam_id": "ghost-dam"}],
         "lambing_records_2026": [
             {"dam": "Old Girl", "lambs_born": 2, "lambs_alive": 1},
             {"dam": "Nobody Known", "lambs_born": 1, "lambs_alive": 1}]}
per, unres = ep.productivity(tdb18)
check("dam_id lambs credited", len(per["mama"]["offspring"]), 2)
check("years distinguished", sorted(per["mama"]["offspring_years"]), ["2025", "2026"])
check("lambing row resolves via ALIAS", per["mama"]["rows_born"], 2)
check("unknown dam name reported, never guessed", unres, ["Nobody Known"])
check("dam_id to nonexistent dam not credited", "ghost-dam" in per, False)

# --- verdict -------------------------------------------------------------------------
if FAILURES:
    print(f"\n{len(FAILURES)} FAILURE(S): {FAILURES}")
    sys.exit(1)
print("\nAll flock-health pins passed.")
