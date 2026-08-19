#!/usr/bin/env python3
"""health_events.py — typed, append-only per-animal health & adverse-event log (MCS-26).

Foot rot, fly strike, abscess, coccidiosis, predation, dystocia — everything between routine
FAMACHA and a loss. Today these live as free text inside treatment strings and prose notes,
where no tool can count them, trend them, or feed them to the withdrawal (MCS-7) and triage
(MCS-3) engines. This adds the typed event they should have been all along.

SHAPE — append-only, same discipline as the pen movement log (MCS-9): a health_events[] list
on health, each entry:
    {date, condition, diagnosis, body_location, treatment, outcome, source, notes}
`condition` is drawn from a controlled vocabulary (CONDITION_VOCAB) so events are countable;
free text stays in `notes`. Append, never rewrite — an event is a fact about a day.

THREE read-only surfaces + one guarded writer:
  - animal_timeline(sheep): the unified, date-sorted event stream MERGING the typed log with the
    existing famacha / fec / treatment / vaccination collections — the single per-animal history
    that MCS-7 and MCS-3 can read from one place.
  - scan_candidates(db): free-text condition detection over HEALTH-CONTEXT fields only (treatment
    string + treatment notes), each shown WITH its source text as a low-confidence suggestion for
    the operator to confirm into a typed event. It never writes a guessed diagnosis — breed-prose
    notes are deliberately NOT scanned (they produced only false hits).
  - validate_events(sheep): schema + vocabulary + date checks on any typed events present.
  - record_event(...): the append-only writer (pure addition), for apply_card_update and future
    dated entry. Not a bulk free-text guesser.

    python3 scripts/health_events.py                 # candidate events + validation summary
    python3 scripts/health_events.py --timeline gg   # one animal's unified history
    python3 scripts/health_events.py --json
"""
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "flock_database.json"

# Controlled condition vocabulary — standard small-ruminant health conditions. Each maps a set of
# free-text trigger phrases to one canonical condition key so events are countable. Extend as the
# flock meets new conditions; keep keys stable (they are what gets counted and trended).
CONDITION_VOCAB = {
    "foot_rot": ["foot rot", "footrot", "hoof rot"],
    "abscess": ["abscess", "lanced", "lance ", "cl "],   # CL = caseous lymphadenitis (confirm)
    "fly_strike": ["fly strike", "flystrike", "maggot", "myiasis"],
    "coccidiosis": ["coccidi", "corid", "amprolium"],
    "pneumonia": ["pneumonia", "respiratory"],
    "mastitis": ["mastitis"],
    "dystocia": ["dystocia", "difficult birth", "malpresentation"],
    "pinkeye": ["pinkeye", "pink eye", "conjunctivitis"],
    "bottle_jaw": ["bottle jaw", "submandibular edema"],
    "lameness": ["lame", "limp", "founder", "scald"],
    "bloat": ["bloat"],
    "scours": ["scour", "diarrhea"],
    "predation": ["predation", "predator", "coyote", "dog attack"],
    "injury": ["wound", "injury", "laceration", "cut ", "bite"],
    "anemia": ["anemia", "anaemia", "pale", "famacha 5", "famacha 4"],
}

_EVENT_KEYS = {"date", "condition", "diagnosis", "body_location", "treatment", "outcome", "source", "notes"}
VALID_OUTCOMES = {"resolved", "ongoing", "recovered", "chronic", "culled", "died", "unknown", None}


def _iso(d):
    try:
        return datetime.strptime(str(d), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def record_event(sheep, date, condition, diagnosis=None, body_location=None,
                 treatment=None, outcome=None, source=None, notes=None):
    """Append a typed health event (pure addition, append-only). Returns the event dict.
    `condition` should be a CONDITION_VOCAB key; a free condition is allowed but flagged by the
    validator so it can be folded into the vocabulary rather than silently proliferating."""
    ev = {"date": date, "condition": condition, "diagnosis": diagnosis,
          "body_location": body_location, "treatment": treatment, "outcome": outcome,
          "source": source, "notes": notes}
    ev = {k: v for k, v in ev.items() if v is not None}
    sheep.setdefault("health", {}).setdefault("health_events", []).append(ev)
    return ev


def validate_events(sheep):
    """Schema/vocabulary/date issues in this animal's typed health_events. Read-only."""
    issues = []
    for i, e in enumerate(sheep.get("health", {}).get("health_events") or []):
        where = f"{sheep.get('id')}#health_events[{i}]"
        if not isinstance(e, dict):
            issues.append(f"{where}: not an object")
            continue
        extra = set(e) - _EVENT_KEYS
        if extra:
            issues.append(f"{where}: unknown key(s) {sorted(extra)}")
        if "date" not in e or _iso(e.get("date")) is None:
            issues.append(f"{where}: missing/unparseable date {e.get('date')!r}")
        if not e.get("condition"):
            issues.append(f"{where}: no condition")
        elif e["condition"] not in CONDITION_VOCAB:
            issues.append(f"{where}: condition {e['condition']!r} not in vocabulary (add it or reclassify)")
        if e.get("outcome") not in VALID_OUTCOMES:
            issues.append(f"{where}: outcome {e.get('outcome')!r} not a known outcome")
    return issues


def _classify(text):
    """Canonical condition keys whose trigger phrases appear in a text blob."""
    s = str(text or "").lower()
    return sorted({cond for cond, phrases in CONDITION_VOCAB.items()
                   if any(p in s for p in phrases)})


def scan_candidates(db):
    """Read-only: candidate adverse events detected in HEALTH-CONTEXT free text (treatment string
    + treatment notes only — breed-composition prose is not scanned, it yields only false hits).
    Each carries the SOURCE text; these are suggestions for the operator to confirm, never writes."""
    out = []
    for s in db.get("sheep", []):
        # already-typed events are not candidates
        typed_dates = {(_iso(e.get("date")), e.get("condition"))
                       for e in (s.get("health", {}).get("health_events") or []) if isinstance(e, dict)}
        for t in (s.get("health", {}).get("treatments") or []):
            if not isinstance(t, dict):
                continue
            blob = f"{t.get('treatment','')} {t.get('notes','')}"
            for cond in _classify(blob):
                if (_iso(t.get("date")), cond) in typed_dates:
                    continue
                out.append({"sheep_id": s["id"], "date": t.get("date"), "condition": cond,
                            "source_text": blob.strip(), "confidence": "candidate",
                            "why": "detected in a treatment record — confirm and log as a typed event"})
    out.sort(key=lambda r: (r["condition"], r["sheep_id"]))
    return out


def animal_timeline(sheep):
    """Unified, date-sorted health history: typed events + famacha + fec + treatments +
    vaccinations, each as {date, kind, detail}. The one-place history MCS-7/MCS-3 can read."""
    h = sheep.get("health", {}) or {}
    tl = []
    for e in (h.get("health_events") or []):
        if isinstance(e, dict):
            tl.append({"date": e.get("date"), "kind": "event",
                       "detail": f"{e.get('condition','?')}"
                                 + (f" @{e['body_location']}" if e.get("body_location") else "")
                                 + (f" -> {e['outcome']}" if e.get("outcome") else "")})
    for e in (h.get("famacha_scores") or []):
        if isinstance(e, dict):
            tl.append({"date": e.get("date"), "kind": "famacha", "detail": f"score {e.get('score')}"})
    for e in (h.get("fec_history") or []):
        if isinstance(e, dict):
            tl.append({"date": e.get("date"), "kind": "fec", "detail": f"{e.get('fec')} epg"})
    for e in (h.get("treatments") or []):
        if isinstance(e, dict):
            tl.append({"date": e.get("date"), "kind": "treatment", "detail": e.get("treatment")})
    for e in (h.get("vaccinations") or []):
        if isinstance(e, dict):
            tl.append({"date": e.get("date"), "kind": "vaccination", "detail": e.get("vaccine")})
    tl.sort(key=lambda x: (_iso(x["date"]) or datetime.min.date(), x["kind"]))
    return tl


def main():
    ap = argparse.ArgumentParser(description="Typed health & adverse-event log (read-only surfaces)")
    ap.add_argument("--timeline", metavar="SHEEP_ID", default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    db = json.loads(DB_PATH.read_text())

    if args.timeline:
        s = next((x for x in db["sheep"] if x["id"] == args.timeline), None)
        if s is None:
            print(f"ERROR: {args.timeline!r} not found", file=sys.stderr); return 1
        tl = animal_timeline(s)
        if args.json:
            print(json.dumps(tl, indent=2)); return 0
        print(f"Health timeline — {s.get('name') or s['id']} ({s['id']}), {len(tl)} events\n")
        for e in tl:
            print(f"  {str(e['date'] or '—'):12} {e['kind']:12} {e['detail']}")
        return 0

    cands = scan_candidates(db)
    issues = []
    for s in db["sheep"]:
        issues += validate_events(s)
    if args.json:
        print(json.dumps({"candidates": cands, "validation_issues": issues}, indent=2)); return 0

    from collections import Counter
    typed = sum(len(s.get("health", {}).get("health_events") or []) for s in db["sheep"])
    print(f"Health-event log — {typed} typed event(s) on file; {len(cands)} candidate(s) detected "
          f"in treatment free text\n")
    if cands:
        by = Counter(c["condition"] for c in cands)
        print("Candidate adverse events (confirm and log as typed events):")
        for c in cands:
            print(f"  {c['condition']:12} {c['sheep_id']:22} {str(c['date'] or '—'):12} {c['source_text'][:48]!r}")
        print("  by condition: " + ", ".join(f"{k}={v}" for k, v in by.most_common()))
    if issues:
        print(f"\nValidation issues ({len(issues)}):")
        for i in issues:
            print(f"  {i}")
    else:
        print("\nValidation: no typed-event schema issues.")
    print("\n  Read-only. Candidates carry their source text and are operator-confirmed, never"
          "\n  auto-written. record_event() is the append-only (MCS-9 shape) writer.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
