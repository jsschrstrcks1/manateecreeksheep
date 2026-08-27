#!/usr/bin/env python3
"""input_inventory.py — flock input inventory: expiry + reorder alerts (MCS-25). READ-ONLY.

Wormer, vaccine, feed, minerals on hand — with expiry and reorder levels. Two failures this
prevents: an EXPIRED dewormer (a degraded anthelmintic under-doses, and under-dosing selects for
resistance — the same resistance the FECRT tool measures), and running OUT mid-need. Reads the
operator-owned data/input_inventory.json; authors no stock figures itself. Uses the MCS-12
quantity shape for amounts.

    python3 scripts/input_inventory.py                 # full status (expiry + reorder + uncounted)
    python3 scripts/input_inventory.py --expiring 60    # items expired or expiring within N days
    python3 scripts/input_inventory.py --reorder        # items at/below reorder level
    python3 scripts/input_inventory.py --json
"""
import argparse
import importlib.util
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

INV_PATH = Path(__file__).resolve().parent.parent / "data" / "input_inventory.json"

_q_spec = importlib.util.spec_from_file_location("quantity", str(Path(__file__).resolve().parent / "quantity.py"))
Q = importlib.util.module_from_spec(_q_spec)
_q_spec.loader.exec_module(Q)

EXPIRING_SOON_DAYS = 60


def _iso(d):
    try:
        return datetime.strptime(str(d), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def _qty(q):
    """Normalize an inventory quantity {value,unit} through the MCS-12 shape, or None."""
    if isinstance(q, dict) and "value" in q:
        return Q.make_quantity(q.get("value"), q.get("unit"))
    return None


def load_inventory():
    return json.loads(INV_PATH.read_text()).get("items", [])


def validate_inventory(items):
    issues = []
    valid_cat = {"anthelmintic", "vaccine", "antibiotic", "mineral", "feed", "supportive", "other"}
    for i, it in enumerate(items):
        where = f"items[{i}] ({it.get('name','?')})"
        if not it.get("name"):
            issues.append(f"{where}: no name")
        if it.get("category") not in valid_cat:
            issues.append(f"{where}: category {it.get('category')!r} not in {sorted(valid_cat)}")
        if it.get("expiry_date") is not None and _iso(it["expiry_date"]) is None:
            issues.append(f"{where}: expiry_date {it['expiry_date']!r} unparseable")
        for qf in ("quantity", "reorder_level"):
            v = it.get(qf)
            if v is not None and _qty(v) is None:
                issues.append(f"{where}: {qf} {v!r} is not a {{value,unit}} quantity")
        q, r = _qty(it.get("quantity")), _qty(it.get("reorder_level"))
        if q and r and q["measure"] != r["measure"]:
            issues.append(f"{where}: quantity ({q['unit']}) and reorder_level ({r['unit']}) are "
                          f"different measures — the reorder check cannot compare them")
    return issues


def status(items, as_of=None, soon_days=EXPIRING_SOON_DAYS):
    """Per item: expiry state and reorder state, honest about uncounted stock."""
    as_of = as_of or date.today()
    rows = []
    for it in items:
        exp = _iso(it.get("expiry_date"))
        if exp is None:
            estate = "no_expiry_on_file"
        elif exp < as_of:
            estate = "EXPIRED"
        elif exp <= as_of + timedelta(days=soon_days):
            estate = "expiring_soon"
        else:
            estate = "ok"
        qty = _qty(it.get("quantity"))
        rl = _qty(it.get("reorder_level"))
        if qty is None:
            rstate = "not_counted"
        elif rl is None:
            rstate = "ok"
        elif qty["measure"] != rl["measure"]:
            # a mL quantity against a kg reorder level can't be compared — reporting 'ok' here
            # would be a false-CALM (a genuinely low stock would never alert). Surface it instead.
            rstate = "reorder_unit_mismatch"
        elif qty["canonical_value"] <= rl["canonical_value"]:
            rstate = "REORDER"
        else:
            rstate = "ok"
        rows.append({"name": it.get("name"), "category": it.get("category"),
                     "expiry_date": it.get("expiry_date"), "expiry_state": estate,
                     "quantity": qty, "reorder_state": rstate})
    return rows


def main():
    ap = argparse.ArgumentParser(description="Flock input inventory: expiry + reorder (read-only)")
    ap.add_argument("--expiring", type=int, nargs="?", const=EXPIRING_SOON_DAYS, default=None,
                    help="items expired or expiring within N days (default 60)")
    ap.add_argument("--reorder", action="store_true", help="items at/below reorder level")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    items = load_inventory()
    rows = status(items, soon_days=args.expiring or EXPIRING_SOON_DAYS)
    issues = validate_inventory(items)

    if args.json:
        # quantities as their raw shape for json consumers
        print(json.dumps({"status": rows, "validation_issues": issues}, indent=2, default=str)); return 0

    if args.expiring is not None:
        flagged = [r for r in rows if r["expiry_state"] in ("EXPIRED", "expiring_soon")]
        print(f"Expiry — {len(flagged)} item(s) expired or expiring within {args.expiring} days\n")
        for r in flagged:
            print(f"  [{r['expiry_state']:14}] {r['name'][:34]:34} exp {r['expiry_date']}")
        if not flagged:
            print("  none (or no expiry dates entered yet).")
        return 0

    if args.reorder:
        flagged = [r for r in rows if r["reorder_state"] == "REORDER"]
        print(f"Reorder — {len(flagged)} item(s) at/below reorder level\n")
        for r in flagged:
            q = r["quantity"]
            print(f"  {r['name'][:34]:34} on hand {q['value']:g}{q['unit'] or ''}")
        if not flagged:
            print("  none at/below reorder level (or quantities not counted yet).")
        return 0

    expired = [r for r in rows if r["expiry_state"] == "EXPIRED"]
    soon = [r for r in rows if r["expiry_state"] == "expiring_soon"]
    reorder = [r for r in rows if r["reorder_state"] == "REORDER"]
    mismatch = [r for r in rows if r["reorder_state"] == "reorder_unit_mismatch"]
    uncounted = [r for r in rows if r["reorder_state"] == "not_counted"]
    print(f"Input inventory — {len(rows)} item(s): {len(expired)} expired, {len(soon)} expiring soon, "
          f"{len(reorder)} to reorder, {len(mismatch)} unit-mismatch, {len(uncounted)} not yet counted\n")
    for r in rows:
        q = r["quantity"]
        onhand = f"{q['value']:g}{q['unit'] or ''}" if q else "—"
        flags = []
        if r["expiry_state"] in ("EXPIRED", "expiring_soon"):
            flags.append(f"{r['expiry_state']} {r['expiry_date']}")
        if r["reorder_state"] == "REORDER":
            flags.append("REORDER")
        elif r["reorder_state"] == "reorder_unit_mismatch":
            flags.append("reorder unit mismatch — cannot compare")
        tail = ("  <- " + "; ".join(flags)) if flags else ""
        print(f"  {r['category']:12} {r['name'][:30]:30} on hand {onhand:10}{tail}")
    if issues:
        print(f"\nValidation issues ({len(issues)}):")
        for i in issues:
            print(f"  {i}")
    print("\n  Read-only; operator-owned counts (data/input_inventory.json). A null quantity reads as"
          "\n  'not counted', never zero. Expired dewormer under-doses and selects for resistance —"
          "\n  track expiry as carefully as the FECRT tracks efficacy.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
