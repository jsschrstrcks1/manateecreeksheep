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

# --- verdict -------------------------------------------------------------------------
if FAILURES:
    print(f"\n{len(FAILURES)} FAILURE(S): {FAILURES}")
    sys.exit(1)
print("\nAll flock-health pins passed.")
