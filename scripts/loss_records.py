#!/usr/bin/env python3
"""loss_records.py — documented loss records fit for indemnity claims (MCS-29). READ-ONLY.

The USDA Livestock Indemnity Program (LIP) can reimburse a portion of market value for livestock
lost to eligible causes — adverse weather/disaster (hurricane, flood, blizzard), predation, and
certain diseases — but ONLY with documentation: the date, the cause, the count, and supporting
evidence, filed with FSA within the program window. This flock has lost animals to Hurricane
Helene and to parasites; that history is worth capturing in a claim-ready shape while it can still
be documented, not reconstructed years later.

HONEST LIMIT — eligibility is an FSA determination, never this tool's. It classifies a loss by
CAUSE and reports whether the documentation LIP would ask for is present; it flags a loss as
"potentially eligible — confirm with FSA", and never asserts a claim will pay.

SHAPE — append-only loss_records[] (MCS-9 shape) for a documented loss:
    {date, cause_category, cause_detail, count, evidence, market_value, filed, notes}

  - classify_cause(text): free-text cause_of_death -> predation | weather | disease | other |
    unknown (the LIP-relevant buckets), shown with the source text.
  - indemnity_view(db): deceased animals categorized, with a documentation-completeness check
    (date? cause? evidence?) and a potentially-eligible flag. A loss with no cause is a NAMED gap.
  - validate_loss_record(): schema/date/count checks; record_loss(): append-only writer.

    python3 scripts/loss_records.py                 # loss ledger by cause + documentation gaps
    python3 scripts/loss_records.py --json
"""
import argparse
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "flock_database.json"

# free-text cause -> LIP-relevant category. Substrings, case-insensitive.
CAUSE_MAP = {
    "predation": ["coyote", "predator", "predation", "dog attack", "bear", "cougar", "vulture", "wildlife"],
    "weather": ["hurricane", "flood", "blizzard", "storm", "freeze", "heat", "lightning", "tornado", "helene", "idalia"],
    "disease": ["parasite", "worm", "haemonchus", "pneumonia", "disease", "infection", "coccidi", "illness"],
    "other": ["birth", "dystocia", "injury", "accident", "age", "old", "unknown cause", "found dead"],
}
POTENTIALLY_ELIGIBLE = {"predation", "weather", "disease"}   # LIP-relevant; FSA confirms actual eligibility
_KEYS = {"date", "cause_category", "cause_detail", "count", "evidence", "market_value", "filed", "notes"}


def _iso(d):
    try:
        return datetime.strptime(str(d), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def classify_cause(text):
    s = str(text or "").lower()
    if not s:
        return "unknown"
    for cat, phrases in CAUSE_MAP.items():
        if any(p in s for p in phrases):
            return cat
    return "other"


def record_loss(sheep, date, cause_category, cause_detail=None, count=1, evidence=None,
                market_value=None, filed=None, notes=None):
    """Append a documented loss record (pure addition, append-only)."""
    rec = {"date": date, "cause_category": cause_category, "cause_detail": cause_detail,
           "count": count, "evidence": evidence, "market_value": market_value,
           "filed": filed, "notes": notes}
    rec = {k: v for k, v in rec.items() if v is not None}
    sheep.setdefault("loss_records", []).append(rec)
    return rec


def validate_loss_record(sheep):
    issues = []
    for i, e in enumerate(sheep.get("loss_records") or []):
        where = f"{sheep.get('id')}#loss_records[{i}]"
        if not isinstance(e, dict):
            issues.append(f"{where}: not an object"); continue
        extra = set(e) - _KEYS
        if extra:
            issues.append(f"{where}: unknown key(s) {sorted(extra)}")
        if _iso(e.get("date")) is None:
            issues.append(f"{where}: missing/unparseable date {e.get('date')!r}")
        if e.get("cause_category") not in (set(CAUSE_MAP) | {"unknown"}):
            issues.append(f"{where}: cause_category {e.get('cause_category')!r} not a known category")
        c = e.get("count", 1)
        if not isinstance(c, int) or isinstance(c, bool) or c < 1:
            issues.append(f"{where}: count {c!r} must be a positive integer")
        if e.get("filed") is not None and not isinstance(e.get("filed"), bool):
            issues.append(f"{where}: filed {e.get('filed')!r} must be a boolean")
    return issues


def indemnity_view(db):
    """Deceased animals as loss entries: category, documentation completeness, eligibility hint."""
    rows = []
    for s in db.get("sheep", []):
        if s.get("status") != "deceased":
            continue
        cause = s.get("cause_of_death")
        cat = classify_cause(cause if isinstance(cause, str) else (cause or {}).get("detail") if isinstance(cause, dict) else cause)
        date = s.get("status_date")
        has_date = _iso(date) is not None
        has_cause = bool(cause)
        # evidence proxy: any source_refs / photos / a structured cause dict
        has_evidence = bool(s.get("source_refs") or s.get("photos") or isinstance(cause, dict))
        missing = []
        if not has_date:
            missing.append("no date of loss")
        if not has_cause:
            missing.append("no cause recorded")
        if not has_evidence:
            missing.append("no supporting evidence linked")
        rows.append({
            "id": s["id"], "name": s.get("name"), "date": date,
            "cause_category": cat, "cause_text": cause if isinstance(cause, str) else None,
            "potentially_eligible": cat in POTENTIALLY_ELIGIBLE,
            "documentation_gaps": missing,
            "claim_ready": cat in POTENTIALLY_ELIGIBLE and not missing,
        })
    rows.sort(key=lambda r: (not r["potentially_eligible"], r["date"] or ""))
    return rows


def main():
    ap = argparse.ArgumentParser(description="Documented loss records for indemnity (read-only)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    db = json.loads(DB_PATH.read_text())
    rows = indemnity_view(db)
    issues = []
    for s in db["sheep"]:
        issues += validate_loss_record(s)
    if args.json:
        print(json.dumps({"losses": rows, "validation_issues": issues}, indent=2)); return 0

    by_cat = Counter(r["cause_category"] for r in rows)
    eligible = [r for r in rows if r["potentially_eligible"]]
    ready = [r for r in rows if r["claim_ready"]]
    print(f"Loss ledger — {len(rows)} deceased on record; by cause: "
          f"{', '.join(f'{k}={v}' for k, v in by_cat.most_common())}\n")
    print(f"Potentially LIP-relevant (predation/weather/disease): {len(eligible)}; "
          f"documentation-complete: {len(ready)}\n")
    for r in eligible:
        gap = ("  <- " + "; ".join(r["documentation_gaps"])) if r["documentation_gaps"] else "  (claim-ready documentation)"
        print(f"  [{r['cause_category']:9}] {(r['name'] or r['id'])[:24]:24} {str(r['date'] or '—'):12}"
              f"{gap}")
    if issues:
        print(f"\nValidation issues ({len(issues)}):")
        for i in issues:
            print(f"  {i}")
    print("\n  Read-only. Eligibility is an FSA determination, never this tool's — 'potentially"
          "\n  eligible' flags the LIP-relevant causes; confirm and file with FSA within the program"
          "\n  window. A loss with no date/cause/evidence is a named gap. Append writer: record_loss().")
    return 0


if __name__ == "__main__":
    sys.exit(main())
