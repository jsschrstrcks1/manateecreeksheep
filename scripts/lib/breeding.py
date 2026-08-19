"""Master breeding pipeline — one row per mating, the cycle as DERIVED dates (MCS-17).

Soli Deo Gloria.

The load-bearing idea (EVSoft screenshots, concept only — no code exists to take):
record ONE fact — ewe X exposed to ram Y over window [start, end] — and everything
after it is arithmetic: pregnancy-check window, due window, lambing watch, wean
target, rebreed eligibility. Pen breeding means EXPOSURE WINDOWS, not single service
dates (a ram co-resident 40 days gives a 40-day-wide due window — the honest shape;
narrowing it requires an observed service or a preg check, never a guess).

Rows live at db["matings"] (append-only list; corrections are status changes +
notes, same discipline as everywhere else). Pending vs done is DERIVED against the
health-event log: a birth event for the ewe inside/after the due window flips the
mating to lambed — MCS-9 derived-state + MCS-11 pending->done applied to
reproduction. This pipeline is explicitly a parasite-control instrument: it is what
lets MCS-33 schedule the periparturient-window FAMACHA tightening.

Policy constants are operator-tunable and sourced:
  gestation 147d +/- 5 (sheep standard); preg-check 35-45d post-exposure-start
  (udder/ultrasound practice); wean 60-90d; rebreed ~30d post-wean.
Pure functions, no I/O.
"""
from datetime import timedelta

from .flock_agenda import parse_date

GESTATION_DAYS = 147
GESTATION_SLACK = 5
PREG_CHECK_WINDOW = (35, 45)      # days after exposure START
WEAN_WINDOW = (60, 90)            # days after birth
REBREED_AFTER_WEAN = 30

VALID_STATUS = ("exposed", "confirmed", "lambed", "failed", "closed")


def mating_windows(m):
    """All derived windows for one mating row, or None if dates unparseable.
    Returns dict of (start, end) date pairs; single-date service = zero-width window."""
    start = parse_date(m.get("exposure_start"))
    if not start:
        return None
    end = parse_date(m.get("exposure_end")) or start
    if end < start:
        return None
    bred = parse_date(m.get("confirmed_bred_date"))
    due_lo = (bred or start) + timedelta(days=GESTATION_DAYS - GESTATION_SLACK)
    due_hi = (bred or end) + timedelta(days=GESTATION_DAYS + GESTATION_SLACK)
    return {
        "exposure": (start, end),
        "preg_check": (start + timedelta(days=PREG_CHECK_WINDOW[0]),
                       end + timedelta(days=PREG_CHECK_WINDOW[1])),
        "due": (due_lo, due_hi),
    }


def birth_for(m, events):
    """The birth event that satisfies this mating, if any: a `birth` event on the ewe
    dated on/after (due_lo - 21d) — early lambs happen; a birth long before the window
    belongs to a previous cycle and is not claimed."""
    w = mating_windows(m)
    if not w:
        return None
    floor = w["due"][0] - timedelta(days=21)
    for e in events or []:
        if e.get("type") == "birth" and e.get("animal_id") == m.get("ewe_id"):
            d = parse_date(e.get("date"))
            if d and d >= floor:
                return e
    return None


def derived_status(m, events):
    """Recorded status, upgraded by evidence: a satisfying birth event => lambed."""
    if m.get("status") in ("failed", "closed"):
        return m["status"]
    if birth_for(m, events):
        return "lambed"
    return m.get("status", "exposed")


def breeding_items(db, today, events=None):
    """Agenda items for every open mating: preg-check windows, lambing watch, wean
    targets. Same item shape as the rest of the agenda engine."""
    items = []
    for m in db.get("matings") or []:
        status = derived_status(m, events)
        if status in ("failed", "closed"):
            continue
        w = mating_windows(m)
        if not w:
            items.append({"type": "mating_unparseable", "animal_id": m.get("ewe_id"),
                          "due": None, "overdue": True, "active": True,
                          "basis": f"mating {m.get('mating_id')}: dates unparseable — fix the row"})
            continue
        ewe, ram = m.get("ewe_id"), m.get("ram_id")
        if status == "lambed":
            b = birth_for(m, events)
            bd = parse_date(b.get("date"))
            lo, hi = bd + timedelta(days=WEAN_WINDOW[0]), bd + timedelta(days=WEAN_WINDOW[1])
            if today <= hi + timedelta(days=30):
                items.append({"type": "wean_due", "animal_id": ewe,
                              "due": str(lo), "window_end": str(hi),
                              "overdue": today > hi, "active": True,
                              "basis": f"lambed {bd} (x {ram}) -> wean {WEAN_WINDOW[0]}-"
                                       f"{WEAN_WINDOW[1]}d; rebreed eligible ~{hi + timedelta(days=REBREED_AFTER_WEAN)}"})
            continue
        pc_lo, pc_hi = w["preg_check"]
        if status == "exposed" and today >= pc_lo - timedelta(days=7):
            items.append({"type": "preg_check_due", "animal_id": ewe,
                          "due": str(pc_lo), "window_end": str(pc_hi),
                          "overdue": today > pc_hi, "active": True,
                          "basis": f"exposed to {ram} {w['exposure'][0]}..{w['exposure'][1]} -> "
                                   f"preg check {pc_lo}..{pc_hi}"})
        due_lo, due_hi = w["due"]
        if today >= due_lo - timedelta(days=14):
            items.append({"type": "lambing_watch", "animal_id": ewe,
                          "due": str(due_lo), "window_end": str(due_hi),
                          "overdue": today > due_hi, "active": True,
                          "basis": f"due window {due_lo}..{due_hi} (x {ram}; gestation "
                                   f"{GESTATION_DAYS}±{GESTATION_SLACK}d) — MCS-33 periparturient "
                                   f"FAMACHA tightening applies"})
    return items


def validate_matings(db):
    """Row integrity: refs exist and are the right sex, dates parse, status sane,
    ids unique. ERRORS — a wrong mating row schedules the wrong ewe's lambing watch."""
    issues = []
    sheep = {s["id"]: s for s in db.get("sheep", [])}
    seen = set()
    for m in db.get("matings") or []:
        mid = m.get("mating_id", "?")
        if mid in seen:
            issues.append(f"ERROR [matings.{mid}]: duplicate mating_id")
        seen.add(mid)
        for role, want in (("ewe_id", ("ewe", "ewe_lamb")), ("ram_id", ("ram", "ram_lamb"))):
            aid = m.get(role)
            if not aid or aid not in sheep:
                issues.append(f"ERROR [matings.{mid}]: {role} '{aid}' not in flock DB")
            elif sheep[aid].get("sex") not in want + ("unknown",):
                issues.append(f"ERROR [matings.{mid}]: {role} '{aid}' has sex="
                              f"{sheep[aid].get('sex')!r} (expected {want[0]})")
        if m.get("status") and m["status"] not in VALID_STATUS:
            issues.append(f"ERROR [matings.{mid}]: status '{m['status']}' not in {VALID_STATUS}")
        if mating_windows(m) is None:
            issues.append(f"ERROR [matings.{mid}]: exposure dates unparseable or reversed")
    return issues
