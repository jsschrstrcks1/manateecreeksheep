#!/usr/bin/env python3
"""Working-the-flock batch session — one pass through the chute, per-animal checklist (MCS-6).

Soli Deo Gloria.

Shepherding happens as a GROUP pass: you don't open each animal's page — you run the pen
through the chute and tick what you did to each as it comes. This tool matches that:
each animal is ONE LINE (interactive prompt or a prepared file), and every line becomes
properly-typed health events immediately (crash-safe: each animal's events are appended
the moment its line is accepted — a dropped phone at animal 30 loses nothing before it).

Line grammar (whitespace-separated after the animal id; order free):
    <animal_id> [f=N] [w=LBS] [wormer=DRUG] [vax=NAME] [fec=EPG] \
                [trim] [shear] [blood] [wean] [note="free text"] [skip]

  f=3            FAMACHA score            -> famacha event
  w=82           weight in lbs            -> weight event
  wormer=prohibit  deworming              -> treatment event (withdrawal lock auto-computed
                                             from drug_reference; unknown drug = loud flag)
  vax=cdt        vaccination              -> vaccination event
  fec=450        fecal egg count (epg)    -> observation event with fec_epg (MCS-8/30 fuel)
  trim|shear|blood|wean                   -> observation event(s), one per action
  note="..."     anything else            -> note event
  skip           animal seen, nothing done (recorded as observation so days-since resets? NO —
                 'skip' records NOTHING; it exists so a prepared file can list the whole pen)

Session order: --pen "Pen 2" walks that pen; --triage orders worst-first (MCS-3);
--from-file replays a prepared file (one line per animal). Every event carries the same
session source stamp so a whole chute day is queryable as one unit.

Concept lifted from LambTracker's GroupSheepManagement (GPL-2, design only, no code).
"""
import argparse
import datetime
import importlib.util
import json
import os
import shlex
import sys
from pathlib import Path

_here = Path(__file__).parent
sys.path.insert(0, str(_here))

_spec = importlib.util.spec_from_file_location("hl", _here / "health_log.py")
hl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hl)

FLAG_ACTIONS = {"trim": "hooves trimmed", "shear": "shorn", "blood": "blood drawn",
                "wean": "weaned"}


def parse_line(line):
    """One chute line -> (animal_id, plan) where plan is a list of event kwargs.
    Raises ValueError on grammar problems — the session shows the error and re-prompts;
    a file run aborts naming the line. Unknown tokens are ERRORS, not silently dropped."""
    toks = shlex.split(line)
    if not toks:
        return None, []
    animal, plan = toks[0], []
    for tok in toks[1:]:
        low = tok.lower()
        if low == "skip":
            return animal, []
        if low in FLAG_ACTIONS:
            plan.append(dict(type="observation", details=FLAG_ACTIONS[low]))
            continue
        if "=" not in tok:
            raise ValueError(f"unknown token '{tok}' (not an action flag, not key=value)")
        k, v = tok.split("=", 1)
        k = k.lower()
        if k == "f":
            plan.append(dict(type="famacha", score=int(v), details=f"FAMACHA {v} (chute session)"))
        elif k == "w":
            plan.append(dict(type="weight", details=f"weight {float(v)} lbs"))
        elif k == "wormer":
            plan.append(dict(type="treatment", drug=v, details=f"dewormed: {v} (chute session)"))
        elif k == "vax":
            plan.append(dict(type="vaccination", details=f"vaccinated: {v}"))
        elif k == "fec":
            plan.append(dict(type="observation", fec_epg=int(v), details=f"FEC {v} epg"))
        elif k == "note":
            plan.append(dict(type="note", details=v))
        else:
            raise ValueError(f"unknown key '{k}' in '{tok}'")
    return animal, plan


def apply_line(line, *, date, source, recorded_by, quiet=True):
    """Parse + append. Returns (animal, [event_ids]). Raises ValueError/RefusedError."""
    animal, plan = parse_line(line)
    if animal is None or not plan:
        return animal, []
    written = []
    for kw in plan:
        e = hl.append_event(animal=animal, date=date, source=source,
                            recorded_by=recorded_by, quiet=quiet, **kw)
        written.append(e["event_id"])
    return animal, written


def roster(args):
    db = json.load(open(hl.DB_PATH))
    sheep = [s for s in db.get("sheep", []) if s.get("status") == "alive"]
    if args.pen:
        return [s["id"] for s in sheep if s.get("pen") == args.pen]
    if args.triage:
        import subprocess
        out = subprocess.run([sys.executable, str(_here / "flock_triage.py"), "--all"],
                             capture_output=True, text=True).stdout
        order = [l.split()[2] for l in out.splitlines()
                 if l.strip() and l.split()[0].isdigit() and len(l.split()) > 2]
        known = {s["id"] for s in sheep}
        return [a for a in order if a in known]
    return sorted(s["id"] for s in sheep)


def main():
    ap = argparse.ArgumentParser(description="Batch chute session (MCS-6)")
    ap.add_argument("--pen", help="walk one pen")
    ap.add_argument("--triage", action="store_true", help="worst-first order (MCS-3)")
    ap.add_argument("--date", default=datetime.date.today().isoformat())
    ap.add_argument("--recorded-by", default=os.environ.get("USER", "chute"),
                    dest="recorded_by")
    ap.add_argument("--from-file", dest="from_file",
                    help="prepared session file, one line per animal")
    args = ap.parse_args()
    source = f"chute session {args.date}"

    if args.from_file:
        ok = bad = 0
        for n, line in enumerate(Path(args.from_file).read_text().splitlines(), 1):
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            try:
                animal, ids = apply_line(line, date=args.date, source=source,
                                         recorded_by=args.recorded_by)
                if ids:
                    print(f"  {animal}: {len(ids)} event(s)")
                    ok += 1
            except (ValueError, hl.RefusedError) as ex:
                print(f"LINE {n} REFUSED ({ex}) — nothing from this line written; "
                      f"earlier lines are already safe in the log.")
                bad += 1
        print(f"session done: {ok} animals recorded, {bad} refused")
        sys.exit(1 if bad else 0)

    ids = roster(args)
    print(f"Chute session {args.date} — {len(ids)} animals "
          f"({'pen ' + args.pen if args.pen else 'triage order' if args.triage else 'whole flock'}).")
    print("Per animal: f=N w=LBS wormer=DRUG vax=NAME fec=EPG trim shear blood wean "
          "note=\"...\" | blank = skip | q = end session\n")
    done = 0
    for aid in ids:
        while True:
            try:
                line = input(f"{aid}> ").strip()
            except EOFError:
                line = "q"
            if line == "q":
                print(f"session ended: {done} animals recorded")
                return
            if not line:
                break
            try:
                _, written = apply_line(f"{aid} {line}", date=args.date, source=source,
                                        recorded_by=args.recorded_by, quiet=False)
                if written:
                    done += 1
                break
            except (ValueError, hl.RefusedError) as ex:
                print(f"  {ex} — re-enter this animal")
    print(f"session done: {done} animals recorded")


if __name__ == "__main__":
    main()
