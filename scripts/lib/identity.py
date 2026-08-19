"""EID + visual dual identity (MCS-5). Pure functions, no I/O.

Soli Deo Gloria.

Concept from LambTrackerMobile (GPL-2, design only): every animal may carry BOTH an
electronic tag (EID/RFID) and a visual tag, and EITHER is a valid lookup key — a
torn-off button tag or a dead RFID never orphans a history.

Schema (ADDITIVE — the legacy scalar `tag`/`tag_color` stays, as the mirror of the
primary active visual tag; nothing is migrated wholesale):
    sheep["tags"] = [
      {"kind": "visual"|"eid", "value": "...", "color": opt, "location": opt,
       "status": "active"|"lost"|"retired", "applied": opt-date, "notes": opt}
    ]
A lost tag is never deleted — status flips to "lost" so the old number still finds
the animal in old paperwork.
"""

VALID_KINDS = ("visual", "eid")
VALID_TAG_STATUS = ("active", "lost", "retired")


def all_tags(sheep):
    """Every identity token for one animal: structured tags[] plus the legacy scalar."""
    out = []
    for t in sheep.get("tags") or []:
        if isinstance(t, dict) and t.get("value"):
            out.append(t)
    if sheep.get("tag"):
        legacy = str(sheep["tag"])
        if not any(str(t.get("value")) == legacy for t in out):
            out.append({"kind": "visual", "value": legacy,
                        "color": sheep.get("tag_color", "yellow"),
                        "status": "active", "legacy_scalar": True})
    return out


def find_by_tag(db, value):
    """All sheep matching a tag value (visual or EID, any status — old numbers must
    still resolve in old paperwork). Exact string match, case-insensitive."""
    v = str(value).strip().lower()
    hits = []
    for s in db.get("sheep", []):
        if any(str(t.get("value", "")).strip().lower() == v for t in all_tags(s)):
            hits.append(s["id"])
    return hits


def validate_identity(db):
    """tags[] shape; ACTIVE-EID uniqueness among living animals (two live sheep sharing
    an active EID is a scanner giving the wrong history at the chute — ERROR)."""
    issues = []
    live_eids = {}
    for s in db.get("sheep", []):
        for i, t in enumerate(s.get("tags") or []):
            if not isinstance(t, dict):
                issues.append(f"ERROR [{s['id']}]: tags[{i}] is not an object")
                continue
            if t.get("kind") not in VALID_KINDS:
                issues.append(f"ERROR [{s['id']}]: tags[{i}].kind {t.get('kind')!r} not in {VALID_KINDS}")
            if not t.get("value"):
                issues.append(f"ERROR [{s['id']}]: tags[{i}] has no value")
            if t.get("status", "active") not in VALID_TAG_STATUS:
                issues.append(f"ERROR [{s['id']}]: tags[{i}].status {t.get('status')!r} "
                              f"not in {VALID_TAG_STATUS}")
            if (t.get("kind") == "eid" and t.get("status", "active") == "active"
                    and s.get("status") == "alive" and t.get("value")):
                key = str(t["value"]).lower()
                if key in live_eids and live_eids[key] != s["id"]:
                    issues.append(f"ERROR: active EID '{t['value']}' shared by living sheep "
                                  f"'{live_eids[key]}' and '{s['id']}'")
                live_eids[key] = s["id"]
    return issues
