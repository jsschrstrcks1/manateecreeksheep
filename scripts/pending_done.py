#!/usr/bin/env python3
"""pending_done.py — the pending/done log: reminder and record as ONE object (MCS-11). READ-ONLY view.

A to-do list and a history that live apart always drift. Here they are the same thing: an item is
raised 'pending' with a due date, and when the work is done the SAME item becomes the record —
status 'done', a done_date, and a result. Nothing is retyped; nothing is lost. This is the substrate
the flock-agenda engine will schedule against, and it is fed by the triage: the animals the MCS-3
triage marks worst-first are exactly the pending items that should exist.

  - open_items(as_of): pending items, overdue first.
  - record_pending()/mark_done()/cancel(): the lifecycle writers (pure transitions; done/cancelled
    items are kept, never deleted).
  - validate_items(): schema/date/status checks.
  - suggest_from_triage(db): READ-ONLY — proposes pending items from the current triage RED/AMBER
    animals, deduped against items already open for that animal. Never writes; the operator confirms.

    python3 scripts/pending_done.py                      # open items (overdue first) + done summary
    python3 scripts/pending_done.py --suggest             # pending items the triage implies
    python3 scripts/pending_done.py --as-of DATE --json
"""
import argparse
import importlib.util
import json
import sys
from datetime import date, datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "flock_database.json"
LOG_PATH = Path(__file__).resolve().parent.parent / "data" / "pending_done.json"

VALID_STATUS = {"pending", "done", "cancelled"}
_KEYS = {"id", "action", "target", "created", "due", "status", "done_date", "result", "source", "notes"}


def _iso(d):
    try:
        return datetime.strptime(str(d), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def load_items():
    return json.loads(LOG_PATH.read_text()).get("items", [])


def record_pending(items, item_id, action, target, created, due=None, source=None, notes=None):
    """Append a pending item (pure addition)."""
    it = {"id": item_id, "action": action, "target": target, "created": created,
          "due": due, "status": "pending", "source": source, "notes": notes}
    it = {k: v for k, v in it.items() if v is not None}
    items.append(it)
    return it


def mark_done(items, item_id, done_date, result=None):
    """Transition an item pending -> done IN PLACE (the reminder becomes the record). Returns the
    item, or None if the id is not found."""
    for it in items:
        if it.get("id") == item_id:
            it["status"] = "done"
            it["done_date"] = done_date
            if result is not None:
                it["result"] = result
            return it
    return None


def cancel(items, item_id, reason=None):
    for it in items:
        if it.get("id") == item_id:
            it["status"] = "cancelled"
            if reason is not None:
                it["notes"] = reason
            return it
    return None


def validate_items(items):
    issues = []
    seen = set()
    for i, it in enumerate(items):
        where = f"items[{i}] ({it.get('id','?')})"
        if not isinstance(it, dict):
            issues.append(f"{where}: not an object"); continue
        extra = set(it) - _KEYS
        if extra:
            issues.append(f"{where}: unknown key(s) {sorted(extra)}")
        iid = it.get("id")
        if not iid:
            issues.append(f"{where}: no id")
        elif iid in seen:
            issues.append(f"{where}: duplicate id {iid!r}")
        else:
            seen.add(iid)
        if it.get("status") not in VALID_STATUS:
            issues.append(f"{where}: status {it.get('status')!r} not in {sorted(VALID_STATUS)}")
        if _iso(it.get("created")) is None:
            issues.append(f"{where}: created {it.get('created')!r} unparseable")
        for df in ("due", "done_date"):
            if it.get(df) is not None and _iso(it.get(df)) is None:
                issues.append(f"{where}: {df} {it.get(df)!r} unparseable")
        if it.get("status") == "done" and not it.get("done_date"):
            issues.append(f"{where}: done item has no done_date")
    return issues


def open_items(items, as_of=None):
    """Pending items, overdue first (soonest due first; undated last)."""
    as_of = as_of or date.today()
    opens = [it for it in items if it.get("status") == "pending"]
    def key(it):
        d = _iso(it.get("due"))
        return (d is None, d or date.max)
    for it in opens:
        d = _iso(it.get("due"))
        it["_overdue"] = bool(d and d < as_of)
    opens.sort(key=key)
    return opens


def suggest_from_triage(db, items):
    """Read-only: pending items the current triage implies, deduped against open items already
    targeting that animal. Composes MCS-3; never writes."""
    spec = importlib.util.spec_from_file_location(
        "attention_triage", str(Path(__file__).resolve().parent / "attention_triage.py"))
    at = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(at)
    open_targets = {it.get("target") for it in items if it.get("status") == "pending"}
    rows = at.triage_flock(db)
    out = []
    for r in rows:
        if r["status"] in ("RED", "AMBER") and r["sheep_id"] not in open_targets:
            out.append({"action": f"{r['decision']} ({'; '.join(r['reasons'][:2])})",
                        "target": r["sheep_id"], "priority": r["status"], "source": "triage"})
    return out


def main():
    ap = argparse.ArgumentParser(description="Pending/done log — reminder and record as one (read-only)")
    ap.add_argument("--as-of", default=None)
    ap.add_argument("--suggest", action="store_true", help="pending items the triage implies (read-only)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    as_of = _iso(args.as_of) if args.as_of else date.today()
    if args.as_of and as_of is None:
        print(f"ERROR: --as-of {args.as_of!r} is not an ISO date", file=sys.stderr); return 2
    items = load_items()

    if args.suggest:
        db = json.loads(DB_PATH.read_text())
        sug = suggest_from_triage(db, items)
        if args.json:
            print(json.dumps(sug, indent=2)); return 0
        print(f"Triage-implied pending items — {len(sug)} (not yet on the log)\n")
        for s in sug:
            print(f"  [{s['priority']:5}] {s['target']:24} {s['action']}")
        print("\n  Read-only suggestions. Add the ones you want with record_pending(); the operator"
              "\n  confirms — the triage proposes, it does not auto-schedule.")
        return 0

    issues = validate_items(items)
    opens = open_items(items, as_of)
    done = [it for it in items if it.get("status") == "done"]
    if args.json:
        print(json.dumps({"as_of": as_of.isoformat(), "open": opens, "done_count": len(done),
                          "validation_issues": issues}, indent=2)); return 0
    overdue = [it for it in opens if it.get("_overdue")]
    print(f"Pending/done log — {len(opens)} open ({len(overdue)} overdue), {len(done)} done, "
          f"as of {as_of.isoformat()}\n")
    for it in opens:
        due = it.get("due") or "—"
        od = " OVERDUE" if it.get("_overdue") else ""
        print(f"  [{('DUE ' + due):16}]{od:8} {str(it.get('target','')):24} {it.get('action','')}")
    if not opens:
        print("  no open items.")
    if issues:
        print(f"\nValidation issues ({len(issues)}):")
        for i in issues:
            print(f"  {i}")
    print("\n  Reminder and record are one object: mark_done() turns a pending item into its own"
          "\n  record (done_date + result). --suggest proposes items from the triage. Operator decides.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
