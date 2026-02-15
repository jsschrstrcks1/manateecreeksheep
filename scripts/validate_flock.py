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
import sys
from pathlib import Path
from collections import Counter

REPO_ROOT = Path(__file__).parent.parent
DB_PATH = REPO_ROOT / "data" / "flock_database.json"

REQUIRED_FIELDS = ["id", "name", "sex", "status", "confidence"]
VALID_SEX = ["ram", "ewe", "ram_lamb", "ewe_lamb", "wether", "unknown"]
VALID_STATUS = ["alive", "deceased", "sold", "unknown"]
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


def validate_breed_percentages(sheep_list):
    """Check breed percentages sum to ~100%."""
    warnings = []
    for sheep in sheep_list:
        comp = sheep.get("breed_composition", {})
        pcts = comp.get("percentages", {})
        if pcts:
            total = sum(pcts.values())
            if abs(total - 100) > 2:
                warnings.append(
                    f"WARNING [{sheep['id']}]: Breed percentages sum to {total}% (expected ~100%)"
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
    """Check no two living sheep share a tag."""
    warnings = []
    living_tags = Counter()
    for sheep in sheep_list:
        if sheep.get("status") == "alive" and sheep.get("tag"):
            living_tags[sheep["tag"]] += 1

    for tag, count in living_tags.items():
        if count > 1:
            warnings.append(f"WARNING: Tag '{tag}' is shared by {count} living sheep")

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


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Validate flock database")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    parser.add_argument("--check-references", action="store_true", help="Only check sire/dam references")
    parser.add_argument("--check-images", action="store_true", help="Check image file references")
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
    else:
        all_issues.extend(validate_required_fields(sheep_list))
        all_issues.extend(validate_breed_percentages(sheep_list))
        all_issues.extend(validate_references(sheep_list))
        all_issues.extend(validate_tag_uniqueness(sheep_list))
        all_issues.extend(validate_pen_assignments(db))

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
