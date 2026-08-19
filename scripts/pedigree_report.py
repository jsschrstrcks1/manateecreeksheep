#!/usr/bin/env python3
"""Pedigree view + inbreeding numbers (MCS-16).

Usage:
  python3 scripts/pedigree_report.py --animal <id> [--gens 4]     # tree + own F
  python3 scripts/pedigree_report.py --mate <ram_id> <ewe_id>     # prospective lamb F
  python3 scripts/pedigree_report.py --screen-pen "Pen 5"         # ram x every ewe in pen

F is Wright's coefficient from the recorded pedigree. HONEST LIMIT: unknown parents
contribute zero, so F is a LOWER BOUND — 0.0 means "no inbreeding visible in the
records", never "outbred". Soli Deo Gloria.
"""
import argparse
import json
import os
import sys
from pathlib import Path

_here = Path(__file__).parent
sys.path.insert(0, str(_here))
from lib.pedigree import ancestors_tree, build_parents, kinship_fn, prospective_f, render_tree, wright_f  # noqa: E402

REPO = _here.parent
DB_PATH = Path(os.environ.get("FLOCK_DB_PATH") or REPO / "data" / "flock_database.json")
LIMIT_NOTE = "(lower bound — unknown parents count zero; 0.0 = nothing visible, not outbred)"


def main():
    ap = argparse.ArgumentParser(description="Pedigree + Wright's F (MCS-16)")
    ap.add_argument("--animal")
    ap.add_argument("--gens", type=int, default=4)
    ap.add_argument("--mate", nargs=2, metavar=("RAM", "EWE"))
    ap.add_argument("--screen-pen", dest="screen_pen")
    args = ap.parse_args()
    db = json.load(open(DB_PATH))
    ids = {s["id"] for s in db.get("sheep", [])}
    parents = build_parents(db)

    if args.animal:
        if args.animal not in ids:
            sys.exit(f"'{args.animal}' not in flock DB")
        for line in render_tree(ancestors_tree(db, args.animal, args.gens)):
            print(line)
        print(f"\nF({args.animal}) = {wright_f(db, args.animal, parents):.4f} {LIMIT_NOTE}")
    elif args.mate:
        ram, ewe = args.mate
        for x in (ram, ewe):
            if x not in ids:
                sys.exit(f"'{x}' not in flock DB")
        f = prospective_f(db, ram, ewe, parents)
        print(f"prospective lamb F({ram} x {ewe}) = {f:.4f} {LIMIT_NOTE}")
    elif args.screen_pen:
        sheep = db.get("sheep", [])
        pen = [s for s in sheep if s.get("status") == "alive" and s.get("pen") == args.screen_pen]
        rams = [s for s in pen if s.get("sex") in ("ram", "ram_lamb")]
        ewes = [s for s in pen if s.get("sex") in ("ewe", "ewe_lamb")]
        if not rams:
            sys.exit(f"no living ram recorded in {args.screen_pen}")
        kin = kinship_fn(parents)
        for r in rams:
            print(f"ram {r['id']} x {args.screen_pen} ewes {LIMIT_NOTE}:")
            rows = sorted(((kin(r["id"], e["id"]), e["id"]) for e in ewes), reverse=True)
            for f, eid in rows:
                flag = "  << CLOSE" if f >= 0.125 else ""
                print(f"  F(lamb) = {f:.4f}  {eid}{flag}")
    else:
        sys.exit("one of --animal / --mate / --screen-pen required")


if __name__ == "__main__":
    main()
