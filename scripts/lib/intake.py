"""Intake quarantine (MCS-28) + documented-loss records (MCS-29). Pure, no I/O.

Soli Deo Gloria.

MCS-28 — biosecurity first-class: a new arrival gets a quarantine row; release is
an agenda item, never a memory. Schema (ADDITIVE):
    db["intake_quarantine"] = [{
      "animal_id": .., "arrived": ISO, "source_farm": ..,
      "arrival_drench": str|null, "fec_on_arrival": int|null,
      "release_after_days": int (default 28),
      "released": ISO|null, "notes": ..}]

MCS-29 — losses documented well enough for an indemnity claim (USDA LIP shape:
what died, when, cause, evidence). DERIVED from death events + the flock DB —
no third ledger; this reports what the records already prove and names what an
adjuster would still ask for.
"""
from .flock_agenda import parse_date
from datetime import timedelta

DEFAULT_QUARANTINE_DAYS = 28


def validate_quarantine(db):
    issues = []
    ids = {s["id"] for s in db.get("sheep", [])}
    for i, q in enumerate(db.get("intake_quarantine") or []):
        tag = q.get("animal_id", f"row{i}")
        if q.get("animal_id") and q["animal_id"] not in ids:
            issues.append(f"ERROR [quarantine.{tag}]: animal_id not in flock DB")
        if not parse_date(q.get("arrived")):
            issues.append(f"ERROR [quarantine.{tag}]: arrived date unparseable")
        if q.get("released") and not parse_date(q.get("released")):
            issues.append(f"ERROR [quarantine.{tag}]: released date unparseable")
        if not q.get("source_farm"):
            issues.append(f"ERROR [quarantine.{tag}]: source_farm missing — biosecurity "
                          f"provenance is the point of the row")
    return issues


def quarantine_items(db, today):
    """Agenda items: releases due/overdue; arrival-workup gaps flagged while in."""
    items = []
    for q in db.get("intake_quarantine") or []:
        if q.get("released"):
            continue
        arrived = parse_date(q.get("arrived"))
        if not arrived:
            continue
        days = q.get("release_after_days") or DEFAULT_QUARANTINE_DAYS
        due = arrived + timedelta(days=days)
        gaps = []
        if not q.get("arrival_drench"):
            gaps.append("no arrival drench recorded")
        if q.get("fec_on_arrival") is None:
            gaps.append("no arrival FEC")
        items.append({"type": "quarantine_release", "animal_id": q.get("animal_id"),
                      "due": str(due), "overdue": today > due, "active": True,
                      "basis": f"arrived {arrived} from {q.get('source_farm','?')} — "
                               f"{days}d quarantine" + (f"; GAPS: {'; '.join(gaps)}" if gaps else "")})
    return items


# What a documented loss needs to survive an adjuster's questions (USDA LIP shape).
LOSS_EVIDENCE_FIELDS = ("cause", "date_known", "records_ref")


def loss_records(db, events):
    """One row per death: what the records prove, what is still missing for a claim."""
    out = []
    deaths = {e["animal_id"]: e for e in events or [] if e.get("type") == "death"}
    for s in db.get("sheep", []):
        if s.get("status") != "deceased":
            continue
        ev = deaths.get(s["id"])
        notes = (s.get("notes") or "")
        cause_known = ev is not None or "cause" in notes.lower() or "helene" in notes.lower() \
            or "haemonchosis" in notes.lower() or "parasit" in notes.lower() or "heat" in notes.lower()
        date_known = bool(s.get("status_date")) or (ev and ev.get("date"))
        missing = []
        if not cause_known:
            missing.append("cause")
        if not date_known:
            missing.append("date")
        if not ev:
            missing.append("typed death event (records_ref)")
        out.append({"animal_id": s["id"], "date": (ev or {}).get("date") or s.get("status_date"),
                    "cause_source": "event log" if ev else ("notes" if cause_known else None),
                    "claim_ready": not missing, "missing": missing})
    return out


# --- Input inventory (MCS-25) ------------------------------------------------------------
# db["input_inventory"] = [{"item": "Prohibit 52g", "category": "wormer|vaccine|feed|supply",
#   "on_hand": num, "unit": .., "expiry": ISO|null, "reorder_at": num|null, "source": ..}]
# Empty until the operator counts the shelf — quantities are barn facts, never invented.

VALID_INPUT_CATEGORIES = ("wormer", "vaccine", "feed", "supply")


def validate_inventory(db):
    issues = []
    for i, row in enumerate(db.get("input_inventory") or []):
        tag = row.get("item", f"row{i}")
        if not row.get("item"):
            issues.append(f"ERROR [inventory.row{i}]: no item name")
        if row.get("category") not in VALID_INPUT_CATEGORIES:
            issues.append(f"ERROR [inventory.{tag}]: category {row.get('category')!r} "
                          f"not in {VALID_INPUT_CATEGORIES}")
        if not isinstance(row.get("on_hand"), (int, float)) or row.get("on_hand") < 0:
            issues.append(f"ERROR [inventory.{tag}]: on_hand must be a non-negative number")
        if row.get("expiry") and not parse_date(row["expiry"]):
            issues.append(f"ERROR [inventory.{tag}]: expiry unparseable")
    return issues


def inventory_items(db, today, expiry_warn_days=60):
    """Agenda items: expired / expiring stock and reorder-point crossings."""
    items = []
    for row in db.get("input_inventory") or []:
        item = row.get("item", "?")
        exp = parse_date(row.get("expiry"))
        if exp:
            if exp < today:
                items.append({"type": "input_expired", "animal_id": None, "due": str(exp),
                              "overdue": True, "active": True,
                              "basis": f"{item}: EXPIRED {exp} — do not use; replace"})
            elif (exp - today).days <= expiry_warn_days:
                items.append({"type": "input_expiring", "animal_id": None, "due": str(exp),
                              "overdue": False, "active": True,
                              "basis": f"{item}: expires {exp} ({(exp - today).days}d)"})
        ra = row.get("reorder_at")
        if isinstance(ra, (int, float)) and isinstance(row.get("on_hand"), (int, float)) \
                and row["on_hand"] <= ra:
            items.append({"type": "input_reorder", "animal_id": None, "due": str(today),
                          "overdue": True, "active": True,
                          "basis": f"{item}: {row['on_hand']} {row.get('unit','')} on hand "
                                   f"<= reorder point {ra}"})
    return items
