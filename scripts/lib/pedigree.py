"""Pedigree views + Wright's inbreeding coefficient (MCS-16). Pure functions, no I/O.

Soli Deo Gloria.

We already store sire_id/dam_id; this renders them (N-generation tree) and QUANTIFIES
closeness: Wright's F via the standard kinship recursion —
    kinship(x, x) = 0.5 * (1 + F_x),  F_x = kinship(sire_x, dam_x)
    kinship(x, y) = 0.5 * (kinship(sire_x, y) + kinship(dam_x, y))   [x not ancestor-tied to y order]
    F(offspring of s,d) = kinship(s, d)

HONEST LIMIT, stated everywhere it prints: with incomplete pedigrees (unknown parents
contribute zero) F is a LOWER BOUND — a 0.0 against a two-generation pedigree means
"no inbreeding VISIBLE", never "outbred". Serves breeding_policy.inbreeding_policy
with a number instead of eyeballing the tree.
"""
from functools import lru_cache


def build_parents(db):
    return {s["id"]: (s.get("sire_id"), s.get("dam_id")) for s in db.get("sheep", [])}


def kinship_fn(parents):
    """Return a memoized kinship(a, b) over the given parent map.

    The recursion f(a,b) = 0.5*(f(s_a,b) + f(d_a,b)) is only valid through the
    individual that is NOT an ancestor of the other — recursing through an ancestor
    undercounts (parent x offspring would lose its direct 0.25). Standard resolution:
    always recurse through the individual of the LATER generation (the descendant),
    where generation = 1 + max(parents' generations), founders = 0."""
    @lru_cache(maxsize=None)
    def gen(x):
        if not x or x not in parents:
            return 0
        s, d = parents[x]
        return 1 + max(gen(s), gen(d)) if (s or d) else 0

    @lru_cache(maxsize=None)
    def kin(a, b):
        if not a or not b or a not in parents or b not in parents:
            return 0.0
        if a == b:
            s, d = parents[a]
            return 0.5 * (1.0 + (kin(s, d) if s and d else 0.0))
        # recurse through the younger individual (never an ancestor of the older)
        if gen(a) < gen(b):
            a, b = b, a
        s, d = parents[a]
        if not (s or d):
            return 0.0
        return 0.5 * (kin(s, b) + kin(d, b))
    return kin


def wright_f(db, animal_id, parents=None):
    """F for an existing animal (kinship of its parents). 0.0 when a parent is unknown
    — a LOWER BOUND, not an outbred verdict."""
    parents = parents or build_parents(db)
    s, d = parents.get(animal_id, (None, None))
    if not s or not d:
        return 0.0
    return kinship_fn(parents)(s, d)


def prospective_f(db, sire_id, dam_id, parents=None):
    """F of a HYPOTHETICAL lamb from this mating — the number the closed-loop
    inbreeding policy wants before the ram goes in."""
    parents = parents or build_parents(db)
    return kinship_fn(parents)(sire_id, dam_id)


def ancestors_tree(db, animal_id, generations=4):
    """Nested dict for rendering: {id, sire: {...}|None, dam: {...}|None}."""
    parents = build_parents(db)

    def node(aid, depth):
        if not aid or aid not in parents or depth < 0:
            return {"id": aid} if aid else None
        s, d = parents[aid]
        if depth == 0:
            return {"id": aid}
        return {"id": aid, "sire": node(s, depth - 1), "dam": node(d, depth - 1)}
    return node(animal_id, generations)


def render_tree(tree, indent=0):
    """Plain-text pedigree lines, sire branch above dam branch."""
    if not tree:
        return ["  " * indent + "(unknown)"]
    lines = ["  " * indent + (tree.get("id") or "(unknown)")]
    if "sire" in tree or "dam" in tree:
        lines += render_tree(tree.get("sire"), indent + 1)
        lines += render_tree(tree.get("dam"), indent + 1)
    return lines
