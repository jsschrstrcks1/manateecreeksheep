#!/usr/bin/env python3
"""Typed per-animal health & adverse-event log (MCS-26, operator directive).

Soli Deo Gloria. The flock's health history deserves better than free-text notes.

Store: data/health_events.jsonl — APPEND-ONLY, one JSON object per line.
Never edit or delete a line; a wrong entry is corrected by appending a new event
of type "note" that names the event_id it corrects. History is history.

Event shape (validated here and by scripts/validate_flock.py):
  event_id       required  stable unique id (auto: <animal>-<date>-<type>[-N])
  animal_id      required  must exist in data/flock_database.json
  type           required  famacha | treatment | planned_treatment | vaccination |
                           death | birth | injury | illness | observation | weight | note
  date           required  ISO YYYY-MM-DD, or YYYY-MM-DD/YYYY-MM-DD range when only
                           a window is known (never invent a precise date — the
                           bulk-cleanup placeholder dates are the standing lesson)
  date_precision optional  exact | approximate | range   (default exact)
  score          optional  FAMACHA 1-5 (famacha events)
  drug           optional  product/class (treatment events), e.g. "ivermectin",
                           "levamisole (Prohibit)"
  dose           optional  free text
  withdrawal_until optional ISO date the animal is not safe to sell/slaughter
                           (MCS-7 seed; per-drug table comes later)
  details        required  what happened, in words
  source         required  where this knowledge comes from ("owner statement
                           2026-08-18", "IMG_0662", "vet visit")
  recorded_by    required  who wrote it (patron/agent/human)
  recorded_at    auto      ISO timestamp

Usage:
  python3 scripts/health_log.py add --animal <id> --type <t> --date <d> \
      --details "..." --source "..." --recorded-by <who> [--score N] [--drug ...] \
      [--dose ...] [--withdrawal-until d] [--date-precision p] [--event-id id]
  python3 scripts/health_log.py list [--animal <id>] [--type <t>] [--limit N]
  python3 scripts/health_log.py pending          # planned_treatment events
"""
import argparse
import datetime
import json
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
DB_PATH = Path(os.environ.get("FLOCK_DB_PATH") or REPO_ROOT / "data" / "flock_database.json")
# MCS-35: overridable so tests and probes NEVER touch the production ledger — a live
# withdrawal-computation probe reached the real log on 2026-08-18 and had to be scrubbed
# pre-commit (UL-106 class). Production default unchanged.
LOG_PATH = Path(os.environ.get("HEALTH_LOG_PATH") or REPO_ROOT / "data" / "health_events.jsonl")

VALID_TYPES = ["famacha", "treatment", "planned_treatment", "vaccination", "death",
               "birth", "injury", "illness", "observation", "weight", "note"]
VALID_PRECISION = ["exact", "approximate", "range"]
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}(/\d{4}-\d{2}-\d{2})?$")


# Free-text drug names in events -> drug_reference keys in the flock DB (MCS-7).
DRUG_ALIASES = {
    "ivermectin": "ivermectin", "ivomec": "ivermectin",
    "levamisole": "levamisole_prohibit", "prohibit": "levamisole_prohibit",
    "fenbendazole": "fenbendazole", "safeguard": "fenbendazole", "safe-guard": "fenbendazole",
    "panacur": "fenbendazole",
    "moxidectin": "moxidectin_cydectin", "cydectin": "moxidectin_cydectin",
    "albendazole": "albendazole_valbazen", "valbazen": "albendazole_valbazen",
}


def lookup_withdrawal(drug_text):
    """Return (days, basis, ref_note) from the DB drug_reference table, or (None, reason, None).

    Days precedence: house_default (defined as >= label, covers extra-label practice)
    > label > FARAD sheep WDI. Never invents a number for an unknown drug.
    """
    db = json.load(open(DB_PATH))
    ref = db.get("drug_reference") or {}
    key = None
    low = drug_text.lower()
    for alias, k in DRUG_ALIASES.items():
        if alias in low:
            key = k
            break
    if not key or key not in ref:
        return None, f"drug '{drug_text}' not in drug_reference table", None
    d = ref[key]
    for field, basis in (("house_default_meat_withdrawal_days", "house default (conservative, >= label)"),
                         ("label_meat_withdrawal_days", "sheep label"),
                         ("farad_sheep_meat_withdrawal_days", "FARAD sheep WDI")):
        if isinstance(d.get(field), int):
            return d[field], basis, d.get("label_note") or d.get("house_default_note") or d.get("farad_note")
    return None, f"drug_reference['{key}'] carries no numeric withdrawal", None


def load_events():
    if not LOG_PATH.exists():
        return []
    events = []
    for n, line in enumerate(LOG_PATH.read_text().splitlines(), 1):
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError as ex:
            sys.exit(f"ABORT: data/health_events.jsonl line {n} unparseable ({ex}) — "
                     f"fix by APPENDING a correction, never by editing; ask the operator.")
    return events


def sheep_ids():
    db = json.load(open(DB_PATH))
    return {s["id"] for s in db.get("sheep", [])}


class RefusedError(ValueError):
    """A validation refusal — importers catch it; the CLI exits with its message."""


def append_event(*, animal, type, date, details, source, recorded_by,
                 date_precision="exact", score=None, drug=None, dose=None,
                 withdrawal_until=None, fec_epg=None, event_id=None, quantity=None, quiet=False):
    """Validate + append one event. Importable core (MCS-6 batch sessions use this);
    the CLI's `add` is a thin wrapper. Raises RefusedError, never sys.exit."""
    ids = sheep_ids()
    if animal not in ids:
        raise RefusedError(f"REFUSED: animal_id '{animal}' not in flock DB. The log never invents "
                           f"animals — check the id (case-sensitive) or add the animal to the DB first.")
    if type not in VALID_TYPES:
        raise RefusedError(f"REFUSED: type '{type}' not in {VALID_TYPES}")
    if not DATE_RE.match(date):
        raise RefusedError(f"REFUSED: date '{date}' must be YYYY-MM-DD or YYYY-MM-DD/YYYY-MM-DD "
                           f"(a range is the honest form when only a window is known)")
    if date_precision not in VALID_PRECISION:
        raise RefusedError(f"REFUSED: date_precision '{date_precision}' not in {VALID_PRECISION}")
    if "/" in date and date_precision != "range":
        raise RefusedError("REFUSED: a date window requires date_precision=range")
    if score is not None and score not in (1, 2, 3, 4, 5):
        raise RefusedError("REFUSED: FAMACHA score must be 1-5")

    events = load_events()
    existing = {e.get("event_id") for e in events}
    if not event_id:
        base = f"{animal}-{date.split('/')[0]}-{type}"
        event_id, n = base, 2
        while event_id in existing:
            event_id, n = f"{base}-{n}", n + 1
    elif event_id in existing:
        raise RefusedError(f"REFUSED: event_id '{event_id}' already exists — the log is "
                           f"append-only and ids never repeat.")

    e = {
        "event_id": event_id,
        "animal_id": animal,
        "type": type,
        "date": date,
        "date_precision": date_precision,
        "details": details,
        "source": source,
        "recorded_by": recorded_by,
        "recorded_at": datetime.datetime.now(datetime.timezone.utc)
                       .strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    for opt, v in (("score", score), ("drug", drug), ("dose", dose),
                   ("withdrawal_until", withdrawal_until), ("fec_epg", fec_epg)):
        if v is not None:
            e[opt] = v

    if quantity is not None:
        from lib.quantity import validate_quantity
        probs = validate_quantity(quantity)
        if probs:
            raise RefusedError(f"REFUSED: quantity invalid — {probs}")
        e["quantity"] = quantity

    # MCS-12: measurements land as the uniform quantity shape alongside the legacy
    # fields (which stay for existing consumers; event_quantities() normalizes both).
    try:
        from lib.quantity import make_quantity
        if type == "weight":
            m = re.search(r"(-?\d+(?:\.\d+)?)\s*(lbs|kg)?", details or "")
            if m:
                e["quantity"] = make_quantity("weight", float(m.group(1)), m.group(2) or "lbs")
        elif type == "famacha" and score is not None:
            e["quantity"] = make_quantity("famacha", score)
        elif fec_epg is not None:
            e["quantity"] = make_quantity("fec", fec_epg)
    except (ValueError, ImportError) as ex:
        raise RefusedError(f"REFUSED: quantity invalid — {ex}")

    # MCS-7: a real treatment with a known drug gets a computed slaughter-withdrawal
    # lock unless the caller supplied one. Unknown drug = loud CHECK LABEL, never a guess.
    if type == "treatment" and drug and "withdrawal_until" not in e:
        days, basis, note = lookup_withdrawal(drug)
        if days is not None:
            treat_end = date.split("/")[-1]
            end = datetime.date.fromisoformat(treat_end) + datetime.timedelta(days=days)
            e["withdrawal_until"] = end.isoformat()
            e["withdrawal_basis"] = f"{days}d meat — {basis}"
            if not quiet:
                print(f"withdrawal lock: not safe for slaughter until {e['withdrawal_until']} "
                      f"({days}d, {basis})" + (f" | {note}" if note else ""))
        elif not quiet:
            print(f"⚠ CHECK LABEL: {basis} — no withdrawal computed. Read the bottle in hand "
                  f"and re-add with --withdrawal-until, or extend data/flock_database.json "
                  f"drug_reference (label/FARAD-sourced only, never a guess).")
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(e, sort_keys=True) + "\n")
    if not quiet:
        print(f"appended {event_id}")
    return e


def cmd_add(args):
    try:
        append_event(animal=args.animal, type=args.type, date=args.date,
                     details=args.details, source=args.source, recorded_by=args.recorded_by,
                     date_precision=args.date_precision, score=args.score, drug=args.drug,
                     dose=args.dose, withdrawal_until=args.withdrawal_until,
                     fec_epg=args.fec_epg, event_id=args.event_id)
    except RefusedError as ex:
        sys.exit(str(ex))


def cmd_list(args):
    events = load_events()
    if args.animal:
        events = [e for e in events if e.get("animal_id") == args.animal]
    if args.type:
        events = [e for e in events if e.get("type") == args.type]
    for e in events[-args.limit:]:
        extra = "".join(f" {k}={e[k]}" for k in ("score", "drug", "withdrawal_until") if k in e)
        print(f"{e.get('date'):>21}  {e.get('animal_id'):28} {e.get('type'):18}{extra}  {e.get('details','')[:80]}")
    print(f"({len(events)} matching events)")


def cmd_withdrawals(args):
    """Animals currently locked out of slaughter/sale (per-event locks + flock-level watch)."""
    today = datetime.date.today().isoformat()
    events = load_events()
    active = [e for e in events if e.get("withdrawal_until") and e["withdrawal_until"] >= today]
    if active:
        print("Per-animal locks (from health events):")
        for e in sorted(active, key=lambda x: x["withdrawal_until"]):
            print(f"  NOT SAFE until {e['withdrawal_until']}  {e['animal_id']:28} "
                  f"{e.get('drug','?')}  ({e.get('withdrawal_basis','')})")
    else:
        print("No active per-animal withdrawal locks in the event log.")
    db = json.load(open(DB_PATH))
    watch = db.get("withdrawal_watch") or []
    live = [w for w in watch if str(w.get("not_safe_for_slaughter_until", ""))[:10] >= today]
    if live:
        print("Flock-level withdrawal watch (data/flock_database.json):")
        for w in live:
            print(f"  NOT SAFE until {w['not_safe_for_slaughter_until']}  {w.get('animals','?')}  "
                  f"[{w.get('drug','?')}]")


def cmd_pending(args):
    events = load_events()
    planned = [e for e in events if e.get("type") == "planned_treatment"]
    done_keys = {(e.get("animal_id"), e.get("drug")) for e in events if e.get("type") == "treatment"}
    for e in planned:
        status = "DONE?" if (e.get("animal_id"), e.get("drug")) in done_keys else "PENDING"
        print(f"{status:8} {e.get('date')}  {e.get('animal_id')}  {e.get('drug','')}  {e.get('details','')[:70]}")
    print(f"({len(planned)} planned treatments)")


def main():
    ap = argparse.ArgumentParser(description="Typed per-animal health event log (MCS-26)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add", help="append one event")
    a.add_argument("--animal", required=True)
    a.add_argument("--type", required=True)
    a.add_argument("--date", required=True)
    a.add_argument("--date-precision", default="exact", dest="date_precision")
    a.add_argument("--details", required=True)
    a.add_argument("--source", required=True)
    a.add_argument("--recorded-by", required=True, dest="recorded_by")
    a.add_argument("--score", type=int)
    a.add_argument("--drug")
    a.add_argument("--dose")
    a.add_argument("--withdrawal-until", dest="withdrawal_until")
    a.add_argument("--fec-epg", dest="fec_epg", type=int,
                   help="fecal egg count, eggs per gram (MCS-8/MCS-30 substrate)")
    a.add_argument("--event-id", dest="event_id")
    a.set_defaults(fn=cmd_add)

    l = sub.add_parser("list", help="list events")
    l.add_argument("--animal")
    l.add_argument("--type")
    l.add_argument("--limit", type=int, default=50)
    l.set_defaults(fn=cmd_list)

    p = sub.add_parser("pending", help="planned treatments not yet recorded as done")
    p.set_defaults(fn=cmd_pending)

    w = sub.add_parser("withdrawals", help="animals currently in slaughter-withdrawal")
    w.set_defaults(fn=cmd_withdrawals)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
