"""Pen history — the flock's location as an append-only event log, current pen DERIVED.

Concept lifted (design only, no code) from farmOS/farmOS (GPL-2): the two primary
record types are Assets and Logs, and an asset's *current* location is never stored
as a mutable field — it is derived from its movement logs. Nothing is overwritten, so
the history that parasite/refugia reasoning needs ("which pen was ewe #14 in during
the July barber-pole spike?", "which animals shared a paddock with the one that
scoured?") is always answerable. See docs/UPGRADE-LEDGER.md MCS-9.

The event log lives at `sheep["movements"]`: an ordered list, oldest first, each entry
{ "date": <ISO string|null>, "from": <pen display name|null>, "to": <pen display name|null>,
  "reason": <str>, "source": <str> }. A `to` of null/"" means "removed from all pens"
(sold, off-property, died). `date` may be null when the real move date is unknown — so
ARRAY ORDER is the source of truth for "current", and date is annotation, validated for
monotonicity but never used to reorder. This is honest: we append in the order moves
happen; we do not invent dates to sort by.

The scalar `sheep["pen"]` field is KEPT as a derived mirror (every Sheets export and web
consumer reads it), but it is now downstream of the log, not an independent author. The
migration and validate_flock keep the two in lockstep; drift is an ERROR, by design.

Pure functions, no I/O. Soli Deo Gloria.
"""


def movements_of(sheep):
    """The movement log for one sheep, as a list (empty if unset/None)."""
    return sheep.get("movements") or []


def current_pen(sheep):
    """Derive the animal's current pen from its movement log.

    Rules, in order:
      - If a movement log exists, the LAST entry's `to` is the current pen
        (empty/None `to` => not in any pen; returns None).
      - If there is no movement log at all (un-migrated record), fall back to the
        legacy scalar `pen` field so this is safe to call mid-migration.
    """
    moves = movements_of(sheep)
    if moves:
        to = moves[-1].get("to")
        return to if to else None
    return sheep.get("pen") or None


def derive_id_to_pen(db):
    """Map every sheep id -> its derived current pen (or None)."""
    return {s["id"]: current_pen(s) for s in db.get("sheep", [])}


def derive_rosters(db):
    """Derive {pen display name -> [member sheep ids]} from the movement logs.

    This is the pens{} roster ('ewes'/'rams'/'members') recomputed from the log — the
    whole point of MCS-9 is that the roster is a projection of the events, not a second
    hand-maintained source that can silently disagree.
    """
    rosters = {}
    for s in db.get("sheep", []):
        p = current_pen(s)
        if p:
            rosters.setdefault(p, []).append(s["id"])
    return rosters


# --- Pen canon (operator directive 2026-08-18) ---------------------------------------------
# "Pens 1-6, plus Tree Fort, and Goose Pen make 8 not 9. Tree Fort is sometimes called
#  chicken coop, and goose pen is sometimes called lamb pen."
# Canonical display names below; aliases map the spoken/legacy names onto them. The DB's
# 2026-05-14 note ("Tree Fort = Chicken Coop, same physical pen") agrees. Before the
# 2026-08-18 alias migration the pens{} dict carried NINE keys (tree_fort AND chicken_coop)
# and 2+ scalar pen values said "Chicken Coop" — the same split-identity defect class as
# the famacha key split, wearing a pen name.
CANONICAL_PENS = ("Pen 1", "Pen 2", "Pen 3", "Pen 4", "Pen 5", "Pen 6",
                  "Tree Fort", "Goose Pen")
PEN_ALIASES = {
    "Chicken Coop": "Tree Fort",
    "Lamb Pen": "Goose Pen",
    "Goose": "Goose Pen",
}


def canonical_pen(name):
    """Canonical display name for a pen, resolving known aliases. None stays None;
    an UNKNOWN name comes back unchanged (the validator flags it — never silently
    invent a pen)."""
    if not name:
        return None
    return PEN_ALIASES.get(name, name)
