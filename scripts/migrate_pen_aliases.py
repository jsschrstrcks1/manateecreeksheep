#!/usr/bin/env python3
"""One-time, idempotent migration: resolve pen ALIASES to the 8-pen canon.

Operator directive 2026-08-18: "pens 1-6, plus tree fort, and goose pen make 8 not 9.
Tree fort is sometimes called chicken coop, and goose pen is sometimes called lamb pen."

Measured before this migration: pens{} carried NINE keys (tree_fort AND chicken_coop as
separate entries with separate rosters and notes), and 2+ sheep records carried the scalar
pen "Chicken Coop". Same split-identity defect class as the famacha key split.

What it does:
  - Scalar `pen` on every sheep: alias -> canonical (value rename only).
  - Movement log entries (`from`/`to`): alias -> canonical.
  - pens{} dict: each alias entry is UNION-MERGED into its canonical entry —
    rosters unioned (order preserved, no duplicates), notes CONCATENATED verbatim with a
    dated merge marker (nothing is summarized or dropped), scalar fields kept from the
    canonical entry with the alias's value preserved in the merge note when they differ.
    The alias's spoken name is recorded in the canonical entry's `aliases` list.
  - Fields unique to the alias entry are copied across (never overwriting canonical).

Zero-loss asserted mechanically: every roster id present before is present after, and both
notes strings survive byte-for-byte inside the merged notes. Dry-run by default; --apply
writes. Idempotent: a second run finds nothing to do. Soli Deo Gloria.
"""
import argparse
import json
import os
import sys

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)
from lib.pen_history import PEN_ALIASES, canonical_pen  # noqa: E402

DB_PATH = os.path.join(_here, "..", "data", "flock_database.json")

# pens{} dict keys for the known alias entries -> their canonical entry's key
ALIAS_KEYS = {"chicken_coop": "tree_fort", "lamb_pen": "goose_pen"}
ROLES = ("rams", "ewes", "lambs", "members")


def migrate(db):
    changed = {"scalar": 0, "moves": 0, "pens_merged": []}

    for s in db.get("sheep", []):
        p = s.get("pen")
        if p and canonical_pen(p) != p:
            s["pen"] = canonical_pen(p)
            changed["scalar"] += 1
        for m in s.get("movements") or []:
            for fld in ("from", "to"):
                v = m.get(fld)
                if v and canonical_pen(v) != v:
                    m[fld] = canonical_pen(v)
                    changed["moves"] += 1

    pens = db.get("pens") or {}
    for akey, ckey in ALIAS_KEYS.items():
        if akey not in pens:
            continue
        alias = pens.pop(akey)
        canon = pens.setdefault(ckey, {"display_name": canonical_pen(alias.get("display_name"))})
        # zero-loss bookkeeping
        before_ids = set()
        for role in ROLES:
            before_ids.update(alias.get(role) or [])
            before_ids.update(canon.get(role) or [])
        a_notes, c_notes = alias.get("notes") or "", canon.get("notes") or ""

        for role in ROLES:
            merged = list(canon.get(role) or [])
            for mid in alias.get(role) or []:
                if mid not in merged:
                    merged.append(mid)
            canon[role] = merged
        marker = (f" | MERGED 2026-08-18 (operator: '{alias.get('display_name', akey)}' is an "
                  f"alias of '{canon.get('display_name', ckey)}' — same physical pen; 8-pen canon): ")
        canon["notes"] = c_notes + marker + a_notes
        al = canon.setdefault("aliases", [])
        if alias.get("display_name") and alias["display_name"] not in al:
            al.append(alias["display_name"])
        for k, v in alias.items():
            if k in ("display_name", "notes", "aliases", *ROLES):
                continue
            if k not in canon or canon[k] in (None, "", []):
                canon[k] = v
            elif canon[k] != v and v not in (None, "", []):
                canon["notes"] += f" [merge note: alias entry had {k}={v!r}; canonical keeps {canon[k]!r}]"

        after_ids = set()
        for role in ROLES:
            after_ids.update(canon.get(role) or [])
        assert before_ids <= after_ids, f"roster loss merging {akey} -> {ckey}"
        assert a_notes in canon["notes"] and c_notes in canon["notes"], "notes loss"
        changed["pens_merged"].append(f"{akey} -> {ckey}")

    return changed


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    db = json.load(open(DB_PATH))
    changed = migrate(db)
    print(f"scalar pen renames: {changed['scalar']} · movement renames: {changed['moves']} · "
          f"pens merged: {changed['pens_merged'] or 'none'}")
    if not args.apply:
        print("dry-run — nothing written (use --apply)")
        return
    if not (changed["scalar"] or changed["moves"] or changed["pens_merged"]):
        print("already canonical — nothing to write")
        return
    with open(DB_PATH, "w") as f:
        json.dump(db, f, indent=2)
    print(f"written: {DB_PATH}")


if __name__ == "__main__":
    main()
