"""Group/cohort as derived, time-aware membership (MCS-10). Pure functions, no I/O.

Soli Deo Gloria.

farmOS concept (design only): a group's membership is a PROJECTION of logs, so "who
was in Pen 5 on July 3rd" is answerable — not just "who is there now". No second
hand-maintained roster is ever stored (MCS-9 discipline; the pens{} roster is the
legacy copy already being retired).

Cohorts a shepherd actually reasons about, each derived from records we already keep:
  pen_members_at    — movement log (MCS-9) replayed to a date
  treatment_cohort  — health events: same drug, same day (FECRT groups, MCS-30)
  breeding_group    — matings: one ram's exposure window (MCS-17)
"""
from .flock_agenda import parse_date


def pen_at(sheep, on_date):
    """The pen one animal was in on a date, from its movement log. None = not in any
    pen / unknown. Undated seed moves count as 'since forever' (they are the migrated
    snapshot); array order is truth for same-date sequences."""
    current = None
    for m in sheep.get("movements") or []:
        d = parse_date(m.get("date"))
        if d is None or d <= on_date:
            current = m.get("to") or None
    return current


def pen_members_at(db, pen, on_date):
    """Living-or-then-alive animals whose movement log places them in `pen` on the date.
    Status filtering is deliberately NOT applied — an animal that later died was still
    in the pen that day, and that is exactly what exposure questions need."""
    return sorted(s["id"] for s in db.get("sheep", []) if pen_at(s, on_date) == pen)


def treatment_cohort(events, on_date, drug_substring=None):
    """Everyone treated on one day (optionally one drug) — the FECRT day-10-14 recheck
    group, and the 'same bottle, same day' exposure cohort."""
    day = str(on_date)
    out = set()
    for e in events or []:
        if e.get("type") != "treatment":
            continue
        if not (e.get("date") == day or str(e.get("date", "")).split("/")[-1] == day):
            continue
        if drug_substring and drug_substring.lower() not in str(e.get("drug", "")).lower():
            continue
        out.add(e["animal_id"])
    return sorted(out)


def breeding_group(db, ram_id):
    """Every open/confirmed mating for one ram: his current cover group (MCS-17)."""
    rows = [m for m in db.get("matings") or []
            if m.get("ram_id") == ram_id and m.get("status") not in ("failed", "closed")]
    return sorted({m.get("ewe_id") for m in rows if m.get("ewe_id")})
