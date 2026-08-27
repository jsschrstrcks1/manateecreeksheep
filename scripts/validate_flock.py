#!/usr/bin/env python3
"""
Validate the flock database for integrity.

Checks:
- Required fields present
- Breed percentages sum to ~100%
- Sire/dam references point to existing sheep
- Tag numbers unique among living animals
- No deceased sheep in active pens
- Health data consistency
"""

import json
import math
import sys
from pathlib import Path
from collections import Counter

REPO_ROOT = Path(__file__).parent.parent
DB_PATH = REPO_ROOT / "data" / "flock_database.json"

REQUIRED_FIELDS = ["id", "name", "sex", "status", "confidence"]
VALID_SEX = ["ram", "ewe", "ram_lamb", "ewe_lamb", "wether", "unknown"]
VALID_STATUS = ["alive", "deceased", "sold", "culled", "gifted", "unknown"]
VALID_CONFIDENCE = ["high", "medium", "low"]


def load_database():
    """Load the flock database."""
    if not DB_PATH.exists():
        print(f"ERROR: Database not found at {DB_PATH}")
        sys.exit(1)

    with open(DB_PATH) as f:
        return json.load(f)


def validate_required_fields(sheep_list):
    """Check all required fields are present."""
    errors = []
    for sheep in sheep_list:
        for field in REQUIRED_FIELDS:
            if field not in sheep or sheep[field] is None:
                errors.append(f"ERROR [{sheep.get('id', 'UNKNOWN')}]: Missing required field: {field}")

        if sheep.get("sex") and sheep["sex"] not in VALID_SEX:
            errors.append(f"ERROR [{sheep['id']}]: Invalid sex: {sheep['sex']}")

        if sheep.get("status") and sheep["status"] not in VALID_STATUS:
            errors.append(f"ERROR [{sheep['id']}]: Invalid status: {sheep['status']}")

        if sheep.get("confidence") and sheep["confidence"] not in VALID_CONFIDENCE:
            errors.append(f"ERROR [{sheep['id']}]: Invalid confidence: {sheep['confidence']}")

    return errors


def validate_structural_types(sheep_list):
    """Catch the STRUCTURAL type malformations that make the downstream tools crash with an opaque
    AttributeError/TypeError instead of a clear message — the gate, so one bad hand-edit or bad
    Sheets-sync is caught here (naming the record and field) rather than blanking a tool's whole
    output. Fields checked are the ones tools access as dicts/lists/hashable keys."""
    errors = []
    DICT_FIELDS = ("health", "breeding", "measurements", "breed_composition")
    LIST_FIELDS = ("pen_log", "shed_scores", "fat_tail_scores", "quarantine_intakes",
                   "loss_records", "notes_history")
    for i, sheep in enumerate(sheep_list):
        sid = sheep.get("id") if isinstance(sheep, dict) else None
        where = sid if sid else f"index {i}"
        if not isinstance(sheep, dict):
            errors.append(f"ERROR [{where}]: sheep record is not an object ({type(sheep).__name__})")
            continue
        if not sid or not isinstance(sid, str):
            errors.append(f"ERROR [{where}]: id is missing or not a string ({sheep.get('id')!r})")
        for f in ("sire_id", "dam_id"):
            v = sheep.get(f)
            if v is not None and not isinstance(v, str):
                errors.append(f"ERROR [{where}]: {f} must be a string id or null, got {type(v).__name__} {v!r}")
        for f in DICT_FIELDS:
            v = sheep.get(f)
            if v is not None and not isinstance(v, dict):
                errors.append(f"ERROR [{where}]: {f} must be an object or absent, got {type(v).__name__}")
        for f in LIST_FIELDS:
            v = sheep.get(f)
            if v is not None and not isinstance(v, list):
                errors.append(f"ERROR [{where}]: {f} must be a list or absent, got {type(v).__name__}")
        # nested health collections must be lists too (tools iterate them)
        health = sheep.get("health")
        if isinstance(health, dict):
            for f in ("famacha_scores", "fec_history", "treatments", "vaccinations", "health_events"):
                v = health.get(f)
                if v is not None and not isinstance(v, list):
                    errors.append(f"ERROR [{where}]: health.{f} must be a list or absent, got {type(v).__name__}")
    return errors


def validate_breed_percentages(sheep_list):
    """Check breed percentages sum to ~100%.

    A record may carry an explicit ``unknown_percentage`` when part of the
    pedigree is genuinely unknowable (e.g. kelsier: KHSI Percent Registry 87%
    Katahdin, 13% pedigree-unknown per reg 198291X). The documented unknown
    completes the sum — honest incompleteness is not a defect. An UNdocumented
    shortfall still warns.
    """
    warnings = []
    for sheep in sheep_list:
        comp = sheep.get("breed_composition", {})
        pcts = comp.get("percentages", {})
        # `percentages` must be a mapping. A list/str/number here made `.values()` raise
        # AttributeError and CRASH the whole run (Lift hostile pass 2026-07-16, H-B) —
        # a validator that dies on bad data is the worst failure mode: the operator gets
        # NO report and believes the flock is clean. Warn per-record, never crash.
        if pcts and not isinstance(pcts, dict):
            warnings.append(
                f"WARNING [{sheep['id']}]: breed_composition.percentages is not an object "
                f"({type(pcts).__name__}) — cannot check the breed sum; fix the record."
            )
            continue
        if pcts:
            unknown = comp.get("unknown_percentage", 0)
            # bool is an int subclass; math.isfinite rejects NaN/inf. A NaN would otherwise
            # slip the check entirely: 87 + NaN = NaN, and abs(NaN-100) > 2 is False, silently
            # disabling the breed-sum guard for that record (found by the 2026-07-15 hostile pass).
            if isinstance(unknown, bool) or not isinstance(unknown, (int, float)) \
                    or not math.isfinite(unknown) or unknown < 0:
                unknown = 0
            # Validate every CONTRIBUTING VALUE before summing (Lift hostile pass 2026-07-16).
            # The NaN fixes (2026-07-15 unknown, 2026-07-16 value) each patched one non-finite
            # path, but `sum()` also CRASHES on a string/None/list value (json.load produces all
            # three from data) — TypeError before any isfinite check could run (H-A/H-E) — and a
            # NEGATIVE value could cancel another to a false ~100 (H-D). Fix the CLASS, not the
            # next field over: a value is valid only if it is a real, finite, non-negative number
            # and not a bool. Any invalid value warns loudly and the record's sum check is skipped
            # (a bad value already means the record needs a human).
            bad = [
                (name, val) for name, val in pcts.items()
                if isinstance(val, bool) or not isinstance(val, (int, float))
                or not math.isfinite(val) or val < 0
            ]
            if bad:
                shown = ", ".join(f"{n}={v!r}" for n, v in bad[:5])
                warnings.append(
                    f"WARNING [{sheep['id']}]: Breed percentages contain invalid value(s) "
                    f"({shown}) — each must be a finite, non-negative number; fix the record."
                )
                continue
            total = sum(pcts.values()) + unknown
            if abs(total - 100) > 2:
                warnings.append(
                    f"WARNING [{sheep['id']}]: Breed percentages sum to {total}% "
                    f"(expected ~100%{', incl. documented unknown' if unknown else ''})"
                )
    return warnings


def validate_references(sheep_list):
    """Check sire/dam references point to existing sheep."""
    errors = []
    sheep_ids = {s["id"] for s in sheep_list}
    sheep_sex = {s["id"]: s.get("sex") for s in sheep_list}

    for sheep in sheep_list:
        sire = sheep.get("sire_id")
        dam = sheep.get("dam_id")

        if sire and sire not in sheep_ids:
            errors.append(f"ERROR [{sheep['id']}]: Sire '{sire}' not found in database")
        elif sire and sheep_sex.get(sire) not in ("ram", "unknown", None):
            errors.append(f"WARNING [{sheep['id']}]: Sire '{sire}' has sex='{sheep_sex[sire]}' (expected ram)")

        if dam and dam not in sheep_ids:
            errors.append(f"ERROR [{sheep['id']}]: Dam '{dam}' not found in database")
        elif dam and sheep_sex.get(dam) not in ("ewe", "unknown", None):
            errors.append(f"WARNING [{sheep['id']}]: Dam '{dam}' has sex='{sheep_sex[dam]}' (expected ewe)")

    return errors


def validate_tag_uniqueness(sheep_list):
    """Check no two living sheep share a (tag, tag_color) pair.

    Some animals arrive from other farms wearing tags that happen to match
    a number already used on the property. When the tag colors differ, the
    animals are still distinguishable in the field, so the pair (tag,
    tag_color) is the real uniqueness key. tag_color defaults to 'yellow'
    (the on-property default) when not set.
    """
    warnings = []
    living_pairs = Counter()
    for sheep in sheep_list:
        if sheep.get("status") == "alive" and sheep.get("tag"):
            color = sheep.get("tag_color", "yellow")
            living_pairs[(sheep["tag"], color)] += 1

    for (tag, color), count in living_pairs.items():
        if count > 1:
            warnings.append(
                f"WARNING: Tag '{tag}' ({color}) is shared by {count} living sheep"
            )

    return warnings


def validate_pen_assignments(db):
    """Check pen assignments are consistent."""
    warnings = []
    sheep_map = {s["id"]: s for s in db.get("sheep", [])}

    for pen_name, pen_data in db.get("pens", {}).items():
        ewes = pen_data.get("ewes", [])
        for eid in ewes:
            if eid in sheep_map:
                if sheep_map[eid].get("status") == "deceased":
                    warnings.append(f"WARNING [{pen_name}]: Deceased sheep '{eid}' listed in active pen")
            else:
                warnings.append(f"WARNING [{pen_name}]: Unknown sheep '{eid}' listed in pen")

    return warnings


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"}


def validate_processed_parity():
    """Every source image at the repo root should have a ≤1800px processed
    counterpart at data/processed/<stem>.jpeg.

    Closes L10 from MANATEE_CREEK_REDESIGN_PLAN.md. Run scripts/process_images.py
    to fill any gaps reported here.
    """
    warnings = []
    processed_dir = REPO_ROOT / "data" / "processed"
    if not processed_dir.exists():
        warnings.append(
            "WARNING: data/processed/ does not exist — run scripts/process_images.py"
        )
        return warnings

    source_imgs = []
    for p in REPO_ROOT.iterdir():
        if p.is_file() and p.suffix in IMAGE_EXTENSIONS:
            source_imgs.append(p)

    missing = []
    for src in source_imgs:
        target = processed_dir / (src.stem + ".jpeg")
        if not target.exists():
            missing.append(src.name)

    if missing:
        warnings.append(
            f"WARNING: {len(missing)} source images lack a processed counterpart "
            f"(run scripts/process_images.py). First few: {missing[:5]}"
        )
    return warnings


def validate_famacha_schema(sheep_list):
    """Canonical FAMACHA schema (established by scripts/normalize_famacha.py): every
    observation lives in health.famacha_scores[], its value under 'score' (never the legacy
    'famacha' key), and there is NO parallel health.famacha_history. This is not cosmetic:
    parasite_resistance.py reads only famacha_scores[].score, so any drift back to the old
    split silently hides observations from the parasite-resistance scorer that drives
    breeding selection. Drift is a WARNING (data present but mis-shelved), not a hard error."""
    warnings = []
    for sheep in sheep_list:
        health = sheep.get("health") or {}
        sid = sheep.get("id", "UNKNOWN")
        if "famacha_history" in health:
            warnings.append(
                f"WARNING [{sid}]: legacy 'famacha_history' present — run "
                f"scripts/normalize_famacha.py --apply to merge it into famacha_scores "
                f"(the scorer never reads famacha_history)"
            )
        for entry in (health.get("famacha_scores") or []):
            if isinstance(entry, dict) and "famacha" in entry:
                warnings.append(
                    f"WARNING [{sid}]: famacha_scores entry ({entry.get('date')}) uses the "
                    f"legacy 'famacha' key instead of 'score' — invisible to the scorer"
                )
    return warnings


def validate_pen_log(sheep_list):
    """Pen is an append-only movement log (MCS-9, scripts/pen_state.py) with sheep['pen'] as a
    DERIVED cache of the last logged pen. Two invariants keep the cache honest:
      1. sheep['pen'] equals the current pen derived from pen_log (else a move bypassed the log).
      2. pen_log dates are non-decreasing where present (an append-only log is chronological).
    ERROR on a cache/log disagreement (a real inconsistency); WARNING on out-of-order dates."""
    try:
        from pen_state import current_pen
    except ImportError:
        import importlib.util as _il
        _sp = _il.spec_from_file_location("pen_state", str(Path(__file__).resolve().parent / "pen_state.py"))
        _ps = _il.module_from_spec(_sp)
        _sp.loader.exec_module(_ps)
        current_pen = _ps.current_pen
    issues = []
    for sheep in sheep_list:
        sid = sheep.get("id", "UNKNOWN")
        log = sheep.get("pen_log")
        if log is None:
            continue
        if sheep.get("pen") != current_pen(sheep):
            issues.append(
                f"ERROR [{sid}]: sheep['pen']={sheep.get('pen')!r} disagrees with the pen_log's "
                f"current pen {current_pen(sheep)!r} — a move bypassed record_move()"
            )
        dated = [e.get("date") for e in log if isinstance(e, dict) and e.get("date")]
        if dated != sorted(dated):
            issues.append(f"WARNING [{sid}]: pen_log dates are out of order (append-only logs are chronological)")
    return issues


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Validate flock database")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    parser.add_argument("--check-references", action="store_true", help="Only check sire/dam references")
    parser.add_argument("--check-images", action="store_true", help="Check image file references")
    parser.add_argument("--check-processed-parity", action="store_true", help="Check every source image has a processed counterpart at ≤1800px")
    args = parser.parse_args()

    db = load_database()
    sheep_list = db.get("sheep", [])

    print(f"Flock database: {len(sheep_list)} sheep records")
    print(f"Active: {sum(1 for s in sheep_list if s.get('status') == 'alive')}")
    print(f"Deceased: {sum(1 for s in sheep_list if s.get('status') == 'deceased')}")
    print(f"Sold: {sum(1 for s in sheep_list if s.get('status') == 'sold')}")
    print()

    all_issues = []

    if args.check_references:
        all_issues.extend(validate_references(sheep_list))
    elif args.check_images:
        # Check image references exist
        for sheep in sheep_list:
            for ref in sheep.get("source_refs", {}).get("notebook_image", []):
                img_path = REPO_ROOT / ref
                processed_path = REPO_ROOT / "data" / "processed" / (Path(ref).stem + ".jpeg")
                if not img_path.exists() and not processed_path.exists():
                    all_issues.append(f"WARNING [{sheep['id']}]: Image reference not found: {ref}")
    elif args.check_processed_parity:
        all_issues.extend(validate_processed_parity())
    else:
        all_issues.extend(validate_structural_types(sheep_list))
        all_issues.extend(validate_required_fields(sheep_list))
        all_issues.extend(validate_breed_percentages(sheep_list))
        all_issues.extend(validate_references(sheep_list))
        all_issues.extend(validate_tag_uniqueness(sheep_list))
        all_issues.extend(validate_pen_assignments(db))
        all_issues.extend(validate_famacha_schema(sheep_list))
        all_issues.extend(validate_pen_log(sheep_list))

    errors = [i for i in all_issues if i.startswith("ERROR")]
    warnings = [i for i in all_issues if i.startswith("WARNING")]

    if errors:
        print("ERRORS:")
        for e in errors:
            print(f"  {e}")
        print()

    if warnings:
        print("WARNINGS:")
        for w in warnings:
            print(f"  {w}")
        print()

    if not errors and not warnings:
        print("All checks passed.")

    total_issues = len(errors) + (len(warnings) if args.strict else 0)
    print(f"\nResult: {len(errors)} errors, {len(warnings)} warnings")

    sys.exit(1 if total_issues > 0 else 0)


if __name__ == "__main__":
    main()
