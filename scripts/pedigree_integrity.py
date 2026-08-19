#!/usr/bin/env python3
"""pedigree_integrity.py — pedigree soundness + prospective-mating inbreeding (COI). READ-ONLY.

Every breeding-selection tool in this repo (ewe_productivity, the EBV/h2 pipeline,
breeding_projector) trusts the sire_id/dam_id graph to be correct. Nothing checks it, and the
inbreeding recurrence in ebv/pedigree.py is only defined on an ACYCLIC pedigree. This tool is
the foundation guard: it (1) asserts the graph is sound with evidence, and (2) answers the one
question a mating decision actually asks — "what inbreeding coefficient would this lamb carry?"

TWO deliverables, both read-only and advisory:

  1. INTEGRITY — an iterative (never-recursing) audit of the graph, so it can report the very
     fault (a cycle) that would crash a recursive walk:
        - a parent id that resolves to no record
        - a dam that is a ram / a sire that is a ewe (a mis-set parent link)
        - an animal listed as its own parent
        - a CYCLE: an animal that is its own ancestor
     A clean report is itself worth having: it lets a breeding decision rest on a checked graph
     instead of an assumed one.

  2. INBREEDING (COI) — F for the living flock, and the PROSPECTIVE F of a mating BEFORE it
     happens (F_lamb = 0.5 * A(sire, dam)). There is no COI guard on planned matings today, and
     the flock already carries real inbreeding (F up to ~0.44). Inbreeding depression costs
     fertility, vigor, and IMMUNE COMPETENCE — the last matters doubly for a flock selected for
     parasite resilience, so a high-F animal that is also FAMACHA-anemic is a compounded signal.

COI bands are relationship EQUIVALENTS — arithmetic, not a cited study (F = 0.25 * A):
     < 0.0625   low        (below first-cousin)
  0.0625-0.125  watch      (~first-cousin mating)
   0.125-0.25   high       (~half-sib / grandparent-grandoffspring)
     >= 0.25    severe     (~full-sib / parent-offspring)
Thresholds are named constants, operator-tunable. This never blocks a mating or a treatment; a
high-COI verdict is an argument to pick a less-related sire, not husbandry law.

    python3 scripts/pedigree_integrity.py                 # integrity audit + living-flock F census
    python3 scripts/pedigree_integrity.py --pair RAM EWE  # prospective lamb COI for one mating
    python3 scripts/pedigree_integrity.py --planned       # COI of every planned_sire mating on file
    python3 scripts/pedigree_integrity.py --json
"""
import argparse
import importlib.util
import json
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "flock_database.json"

# Load the (now cycle-guarded) relationship math without assuming a package import path.
_spec = importlib.util.spec_from_file_location(
    "ebv_pedigree", str(Path(__file__).resolve().parent / "ebv" / "pedigree.py"))
P = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(P)

# COI bands — relationship equivalents (F = 0.25 * A). Tunable.
COI_WATCH = 0.0625    # ~first-cousin mating
COI_HIGH = 0.125      # ~half-sib / grandparent
COI_SEVERE = 0.25     # ~full-sib / parent-offspring


def coi_band(f):
    if f is None:
        return "unknown"
    if f >= COI_SEVERE:
        return "severe"
    if f >= COI_HIGH:
        return "high"
    if f >= COI_WATCH:
        return "watch"
    return "low"


def _ped_from_db(db):
    ped = {}
    for s in db.get("sheep", []):
        ped[s["id"]] = {"sire": s.get("sire_id"), "dam": s.get("dam_id"),
                        "dob": s.get("dob"), "sex": s.get("sex")}
    return ped


def find_cycles(ped):
    """Every animal whose ancestry contains a cycle, found by an ITERATIVE DFS (white/grey/black)
    so the detector itself can never recurse into the loop it is looking for. Returns a list of
    {animal, cycle:[ids...]} — one per distinct back-edge, deduped by frozenset of the loop."""
    WHITE, GREY, BLACK = 0, 1, 2
    color = {a: WHITE for a in ped}
    seen_loops = set()
    cycles = []
    for start in ped:
        if color[start] != WHITE:
            continue
        # explicit stack of (node, parent-iterator-index); track the grey path for reporting
        stack = [(start, 0)]
        path = [start]
        color[start] = GREY
        while stack:
            node, idx = stack[-1]
            parents = [p for p in (ped[node]["sire"], ped[node]["dam"]) if p and p in ped]
            if idx < len(parents):
                stack[-1] = (node, idx + 1)
                nxt = parents[idx]
                if color.get(nxt, BLACK) == GREY:
                    # back-edge -> cycle; slice the grey path from nxt to node
                    loop = path[path.index(nxt):] + [nxt]
                    fp = frozenset(loop)
                    if fp not in seen_loops:
                        seen_loops.add(fp)
                        cycles.append({"animal": nxt, "cycle": loop})
                elif color.get(nxt, BLACK) == WHITE:
                    color[nxt] = GREY
                    path.append(nxt)
                    stack.append((nxt, 0))
            else:
                color[node] = BLACK
                stack.pop()
                if path and path[-1] == node:
                    path.pop()
    return cycles


def integrity_report(db):
    ped = _ped_from_db(db)
    ids = set(ped)
    missing_parent, dam_is_ram, sire_is_ewe, self_parent = [], [], [], []
    for a, r in ped.items():
        sire, dam = r["sire"], r["dam"]
        if sire and sire not in ids:
            missing_parent.append({"animal": a, "role": "sire", "missing_id": sire})
        if dam and dam not in ids:
            missing_parent.append({"animal": a, "role": "dam", "missing_id": dam})
        if dam in ids and ped[dam]["sex"] == "ram":
            dam_is_ram.append({"animal": a, "dam": dam})
        if sire in ids and ped[sire]["sex"] == "ewe":
            sire_is_ewe.append({"animal": a, "sire": sire})
        if sire == a or dam == a:
            self_parent.append(a)
    cycles = find_cycles(ped)
    total = (len(missing_parent) + len(dam_is_ram) + len(sire_is_ewe)
             + len(self_parent) + len(cycles))
    return {
        "records": len(ped),
        "faults_total": total,
        "clean": total == 0,
        "missing_parent": missing_parent,
        "dam_is_ram": dam_is_ram,
        "sire_is_ewe": sire_is_ewe,
        "self_parent": self_parent,
        "cycles": cycles,
    }


def _alive_on_property(db):
    return [s for s in db.get("sheep", [])
            if s.get("status") == "alive" and s.get("on_property") is not False]


def flock_inbreeding(db, ped):
    """F for every living, on-property animal that has BOTH parents on file (F is undefined
    without both). Sorted most-inbred first. Cycle-tainted animals are surfaced, not crashed."""
    rows = []
    for s in _alive_on_property(db):
        a = s["id"]
        r = ped.get(a, {})
        if not (r.get("sire") and r.get("dam")):
            continue  # F undefined without both parents — omit rather than report a false 0
        try:
            f = round(P.inbreeding(a, ped), 4)
            rows.append({"id": a, "name": s.get("name"), "F": f, "band": coi_band(f)})
        except P.PedigreeCycleError:
            rows.append({"id": a, "name": s.get("name"), "F": None, "band": "unknown",
                         "flag": "ancestry contains a cycle — see integrity report"})
    rows.sort(key=lambda x: (x["F"] is None, -(x["F"] or 0)))
    return rows


def _ancestors(animal, ped, limit=12):
    """Iterative ancestor closure (never recurses), depth-bounded for safety on any graph."""
    out, seen, frontier, depth = set(), {animal}, [animal], 0
    while frontier and depth < limit:
        nxt = []
        for x in frontier:
            r = ped.get(x, {})
            for p in (r.get("sire"), r.get("dam")):
                if p and p in ped and p not in seen:
                    seen.add(p)
                    out.add(p)
                    nxt.append(p)
        frontier, depth = nxt, depth + 1
    return out


def mate_coi(sire, dam, ped, by_name=None):
    """Prospective inbreeding of the lamb of (sire x dam): F_lamb = 0.5 * A(sire, dam).
    Read-only. Returns a typed record incl. shared ancestors (the reason for the relatedness)
    and any sex mismatch. Never raises: a cyclic ancestry is reported, not thrown."""
    base = {"sire": sire, "dam": dam}
    warnings = []
    if sire not in ped:
        return {**base, "status": "unknown_sire", "why": f"{sire!r} not in pedigree"}
    if dam not in ped:
        return {**base, "status": "unknown_dam", "why": f"{dam!r} not in pedigree"}
    if sire == dam:
        return {**base, "status": "invalid", "why": "an animal cannot be mated to itself"}
    if ped[sire]["sex"] == "ewe":
        warnings.append(f"{sire!r} is recorded as a ewe, not a ram")
    if ped[dam]["sex"] == "ram":
        warnings.append(f"{dam!r} is recorded as a ram, not a ewe")
    try:
        a = P.relationship(sire, dam, ped)
    except P.PedigreeCycleError as e:
        return {**base, "status": "cycle", "why": str(e)}
    f_lamb = round(0.5 * a, 4)
    shared = sorted(_ancestors(sire, ped) & _ancestors(dam, ped))
    return {**base, "status": "ok", "A_sire_dam": round(a, 4), "lamb_F": f_lamb,
            "band": coi_band(f_lamb), "shared_ancestors": shared, "warnings": warnings}


def planned_matings(db, ped):
    """COI for every mating implied by a ewe's planned_sire field."""
    out = []
    for s in db.get("sheep", []):
        sire = s.get("planned_sire")
        if sire:
            r = mate_coi(sire, s["id"], ped)
            r["planned_breeding_season"] = s.get("planned_breeding_season")
            out.append(r)
    out.sort(key=lambda x: -(x.get("lamb_F") or -1))
    return out


def main():
    ap = argparse.ArgumentParser(description="Pedigree integrity + prospective-mating COI (read-only)")
    ap.add_argument("--pair", nargs=2, metavar=("SIRE", "DAM"), help="prospective lamb COI for one mating")
    ap.add_argument("--planned", action="store_true", help="COI of every planned_sire mating on file")
    ap.add_argument("--limit", type=int, default=15, help="rows in the F census (default 15; 0 = all)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    db = json.loads(DB_PATH.read_text())
    ped = _ped_from_db(db)

    if args.pair:
        r = mate_coi(args.pair[0], args.pair[1], ped)
        if args.json:
            print(json.dumps(r, indent=2)); return 0
        if r["status"] != "ok":
            print(f"cannot compute: {r['status']} — {r.get('why','')}"); return 1
        print(f"Prospective mating {r['sire']} x {r['dam']}")
        print(f"  A(sire,dam) = {r['A_sire_dam']:g}   ->   lamb F = {r['lamb_F']:g}  [{r['band'].upper()}]")
        if r["shared_ancestors"]:
            print(f"  shared ancestors ({len(r['shared_ancestors'])}): {', '.join(r['shared_ancestors'])}")
        else:
            print("  no shared ancestors on record — unrelated as far as the pedigree knows")
        for w in r["warnings"]:
            print(f"  ! {w}")
        print("\n  Read-only advisory. A high band argues for a less-related sire, never against breeding.")
        return 0

    if args.planned:
        rows = planned_matings(db, ped)
        if args.json:
            print(json.dumps(rows, indent=2)); return 0
        if not rows:
            print("No planned_sire matings on file.")
            return 0
        print(f"Planned matings — prospective lamb COI ({len(rows)})\n")
        for r in rows:
            if r["status"] != "ok":
                print(f"  {r['sire']} x {r['dam']}: {r['status']} ({r.get('why','')})")
                continue
            print(f"  [{r['band']:6}] lamb F={r['lamb_F']:g}  {r['sire']} x {r['dam']}"
                  + (f"  ({r['planned_breeding_season']})" if r.get("planned_breeding_season") else ""))
        print("\n  Read-only advisory. Operator decides.")
        return 0

    # default: integrity audit + living-flock inbreeding census
    rep = integrity_report(db)
    fcensus = flock_inbreeding(db, ped)
    if args.json:
        print(json.dumps({"integrity": rep, "flock_inbreeding": fcensus}, indent=2)); return 0

    print(f"Pedigree integrity — {rep['records']} records, "
          + ("CLEAN (no graph faults)" if rep["clean"] else f"{rep['faults_total']} FAULT(S)") + "\n")
    if not rep["clean"]:
        for a in rep["cycles"]:
            print(f"  CYCLE: {a['animal']} is its own ancestor via {' -> '.join(a['cycle'])}")
        for m in rep["missing_parent"]:
            print(f"  MISSING {m['role']}: {m['animal']} -> {m['missing_id']!r} (no such record)")
        for m in rep["dam_is_ram"]:
            print(f"  DAM IS RAM: {m['animal']} dam={m['dam']}")
        for m in rep["sire_is_ewe"]:
            print(f"  SIRE IS EWE: {m['animal']} sire={m['sire']}")
        for a in rep["self_parent"]:
            print(f"  SELF-PARENT: {a} lists itself as a parent")
        print()

    shown = fcensus if args.limit == 0 else fcensus[:args.limit]
    print(f"Living-flock inbreeding — {len(fcensus)} animals with both parents on file "
          f"(showing {len(shown)}, most-inbred first)\n")
    for r in shown:
        f = "  n/a" if r["F"] is None else f"{r['F']:.4f}"
        star = "  <- " + r["flag"] if r.get("flag") else ""
        print(f"  [{r['band']:6}] F={f}  {(r['name'] or r['id'])[:30]:30} {r['id']}{star}")
    print("\n  F undefined without BOTH parents on file (those animals are omitted, not shown as 0)."
          "\n  Bands are relationship equivalents (F=0.25*A). Read-only; welfare first; operator decides.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
