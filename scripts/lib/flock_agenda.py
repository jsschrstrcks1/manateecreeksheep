"""Flock agenda engine — derive due items from flock_database.json. Pure functions, no I/O.

The MCS-11 'reminder and record are one object' shape: agenda items are DERIVED from the
records (MCS-9 rule), never stored as a second mutable list that can drift. Spec:
docs/superpowers/plans/2026-08-12-flock-agenda-engine.md; ledger rows MCS-7/11/30.

ADAPTATIONS from the 2026-08-12 plan, dated 2026-08-18 (post-plan reality):
 - famacha key: the schema normalization made `score` canonical (89 legacy `famacha` keys
   migrated; validator now ERRORS on the legacy key). The engine reads canonical-first with
   a legacy fallback kept as defense-in-depth — the plan's original concern, inverted.
 - second treatment source: data/health_events.jsonl (MCS-26, built 2026-08-18) carries
   typed treatment events with explicit withdrawal_until computed at record time. The engine
   reads BOTH the DB's free-text health.treatments and the typed events; an explicit
   withdrawal_until on an event wins over re-derivation, and (animal, date, drug) dedupes
   the two sources.
 - benign vocabulary: the DB's actual treatment strings use 'VB' for vitamin B — matched on
   word boundary so supportive care is not flagged unknown.

Soli Deo Gloria.
"""
import re
from datetime import date, datetime, timedelta

# --- policy constants (operator-tunable; sources noted) ------------------------------------
FAMACHA_RECHECK_DAYS = {5: 7, 4: 7, 3: 14}      # >=4: high risk weekly; 3: fortnight
FECRT_WINDOW = (10, 14)                          # days post-treatment (Cabaret & Berrag 2004)
LOOKBACK_DAYS = 60                               # covers the longest withdrawal (28d) + slack

# Substrings that identify each drug_reference entry in free-text treatment strings.
DRUG_KEYWORDS = {
    "ivermectin": ("ivermectin", "ivomec"),
    "fenbendazole": ("fenbendazole", "safe-guard", "safeguard", "panacur"),
    "levamisole_prohibit": ("levamisole", "prohibit"),
    "moxidectin_cydectin": ("moxidectin", "cydectin"),
    "albendazole_valbazen": ("albendazole", "valbazen"),
}
# Supportive care with no meaningful withdrawal — recognised so it is not flagged unknown.
BENIGN_KEYWORDS = ("b-complex", "b complex", "b12", "vitamin b", "iron", "nutridrench",
                   "nutri-drench", "probios", "electrolyte", "cdt", "booster")
BENIGN_WORD_RE = re.compile(r"\bvb\b", re.I)     # 'VB 3mL' = vitamin B in this flock's shorthand


def parse_date(s):
    """DB dates come in ISO (2026-08-12), ISO ranges (use the END — conservative for
    withdrawal math), and US-short (4-10-26). Anything else -> None, never a crash."""
    if not s or not isinstance(s, str):
        return None
    s = s.strip().split("/")[-1].strip()
    for fmt in ("%Y-%m-%d", "%m-%d-%y", "%m/%d/%y", "%m-%d-%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def classify_treatment(text):
    """Return (withdrawal_drug_keys, benign_hits, unknown_tokens) for one treatment string."""
    low = (text or "").lower()
    drugs = [k for k, kws in DRUG_KEYWORDS.items() if any(kw in low for kw in kws)]
    benign = [kw for kw in BENIGN_KEYWORDS if kw in low]
    if BENIGN_WORD_RE.search(low):
        benign.append("vb")
    unknown = [] if (drugs or benign or not low.strip()) else [text.strip()]
    return drugs, benign, unknown


def _wd_days(ref_entry):
    """House default wins (conservative, practice-aware); else FARAD; else label."""
    return ref_entry.get("house_default_meat_withdrawal_days") \
        or ref_entry.get("farad_sheep_meat_withdrawal_days") \
        or ref_entry.get("label_meat_withdrawal_days")


def _event_treatments(events, cutoff):
    """Typed treatment events (MCS-26) as (animal_id, date, drug_keys, explicit_until, raw)."""
    out = []
    for e in events or []:
        if e.get("type") != "treatment":
            continue
        d = parse_date(e.get("date"))
        if not d or d < cutoff:
            continue
        drugs, _, unknown = classify_treatment(e.get("drug") or "")
        out.append((e.get("animal_id"), d, drugs, e.get("withdrawal_until"), e, unknown))
    return out


def withdrawal_items(sheep_list, drug_ref, today, events=None):
    items = []
    cutoff = today - timedelta(days=LOOKBACK_DAYS)
    seen = set()   # (animal, date, drug) — events win over free-text re-derivation
    # A slaughter-withdrawal lock is only meaningful on an animal that could be sold:
    # deceased/sold animals drop out (measured live 2026-08-18: the first run locked
    # three dead lambs, which is noise wearing a safety label).
    alive = {s["id"] for s in sheep_list if s.get("status") == "alive"}

    for aid, d, drugs, explicit_until, e, unknown in _event_treatments(events, cutoff):
        if aid not in alive:
            continue
        for u in unknown:
            if not explicit_until:
                items.append({"type": "unknown_withdrawal", "animal_id": aid,
                              "due": str(d), "overdue": True, "active": True,
                              "basis": f"treatment '{u}' on {d}: no withdrawal on file — "
                                       f"consult label/FARAD; NOT silently ignored"})
        for key in (drugs or ([None] if explicit_until else [])):
            seen.add((aid, d, key))
            if explicit_until:
                until = parse_date(explicit_until)
                items.append({"type": "withdrawal_lock", "animal_id": aid, "drug": key or "recorded",
                              "until": str(until), "active": until >= today, "overdue": False,
                              "due": str(until),
                              "basis": f"{e.get('drug')} {d} — lock recorded at treatment "
                                       f"({e.get('withdrawal_basis', 'event log')})"})
            elif key:
                ref = drug_ref.get(key) or {}
                days = _wd_days(ref)
                if not days:
                    items.append({"type": "unknown_withdrawal", "animal_id": aid,
                                  "due": str(d), "overdue": True, "active": True,
                                  "basis": f"{key} on {d}: drug known but no withdrawal days on file"})
                    continue
                until = d + timedelta(days=int(days))
                items.append({"type": "withdrawal_lock", "animal_id": aid, "drug": key,
                              "until": str(until), "active": until >= today, "overdue": False,
                              "due": str(until), "basis": f"{key} {d} + {days}d withdrawal"})

    for s in sheep_list:
        if s["id"] not in alive:
            continue
        for t in (s.get("health") or {}).get("treatments") or []:
            d = parse_date(t.get("date"))
            if not d or d < cutoff:
                continue
            drugs, _benign, unknown = classify_treatment(t.get("treatment"))
            for u in unknown:
                items.append({"type": "unknown_withdrawal", "animal_id": s["id"],
                              "due": str(d), "overdue": True, "active": True,
                              "basis": f"treatment '{u}' on {d}: no withdrawal on file — "
                                       f"consult label/FARAD; NOT silently ignored"})
            for key in drugs:
                if (s["id"], d, key) in seen:
                    continue
                ref = drug_ref.get(key) or {}
                days = _wd_days(ref)
                if not days:
                    items.append({"type": "unknown_withdrawal", "animal_id": s["id"],
                                  "due": str(d), "overdue": True, "active": True,
                                  "basis": f"{key} on {d}: drug known but no withdrawal days on file"})
                    continue
                until = d + timedelta(days=int(days))
                items.append({"type": "withdrawal_lock", "animal_id": s["id"], "drug": key,
                              "until": str(until), "active": until >= today, "overdue": False,
                              "due": str(until),
                              "basis": f"{key} {d} + {days}d withdrawal"})
    return items


def fecrt_items(sheep_list, today, events=None):
    """One FEC-recheck window per anthelmintic treatment day (MCS-30 drench-check)."""
    items, cutoff = [], today - timedelta(days=LOOKBACK_DAYS)
    alive = {s["id"] for s in sheep_list if s.get("status") == "alive"}
    per_animal_days = {}

    for aid, d, drugs, _until, e, _u in _event_treatments(events, cutoff):
        if drugs and aid in alive:
            per_animal_days.setdefault(aid, {}).setdefault(d, set()).update(drugs)
    for s in sheep_list:
        if s.get("status") != "alive":
            continue
        for t in (s.get("health") or {}).get("treatments") or []:
            d = parse_date(t.get("date"))
            drugs, _, _ = classify_treatment(t.get("treatment"))
            if d and d >= cutoff and drugs:
                per_animal_days.setdefault(s["id"], {}).setdefault(d, set()).update(drugs)

    for aid, days in per_animal_days.items():
        for d, drugs in days.items():
            lo, hi = d + timedelta(days=FECRT_WINDOW[0]), d + timedelta(days=FECRT_WINDOW[1])
            if today <= hi:
                items.append({"type": "fecrt_due", "animal_id": aid, "due": str(lo),
                              "window_end": str(hi), "overdue": False, "active": True,
                              "basis": f"FEC recheck 10-14d after {'+'.join(sorted(drugs))} on {d} "
                                       f"tests drug efficacy (FECRT, MCS-30)"})
            elif (today - hi).days <= 21:   # missed recently: still worth saying, then let go
                items.append({"type": "fecrt_due", "animal_id": aid, "due": str(lo),
                              "window_end": str(hi), "overdue": True, "active": True,
                              "basis": f"FECRT window after {d} treatment CLOSED unmet"})
    return items


def famacha_items(sheep_list, today, events=None):
    items = []
    ev_scores = {}
    for e in events or []:
        if e.get("type") == "famacha" and e.get("score") is not None:
            d = parse_date(e.get("date"))
            if d:
                cur = ev_scores.get(e["animal_id"])
                if not cur or d > cur[0]:
                    ev_scores[e["animal_id"]] = (d, e["score"])
    for s in sheep_list:
        if s.get("status") != "alive":
            continue
        scores = (s.get("health") or {}).get("famacha_scores") or []
        dated = [(parse_date(f.get("date")), f) for f in scores]
        dated = [(d, f) for d, f in dated if d]
        best = max(dated, key=lambda x: x[0]) if dated else None
        ev = ev_scores.get(s["id"])
        if ev and (not best or ev[0] >= best[0]):
            d, raw = ev
        elif best:
            d, f = best
            # canonical `score` first (2026-08-18 normalization); legacy `famacha` kept as
            # defense-in-depth — the validator now ERRORS on it, so this fallback should
            # never fire on committed data, but the engine stays correct if it does.
            raw = f.get("score", f.get("famacha"))
        else:
            continue
        try:
            score = int(raw)
        except (TypeError, ValueError):
            continue
        days = FAMACHA_RECHECK_DAYS.get(score)
        if not days:
            continue
        due = d + timedelta(days=days)
        items.append({"type": "famacha_recheck", "animal_id": s["id"], "due": str(due),
                      "overdue": due < today, "active": True,
                      "basis": f"last FAMACHA {score} on {d} -> recheck within {days}d"})
    return items


def anomaly_items(anomalies, today):
    return [{"type": "pending_identification", "animal_id": None, "due": a.get("date"),
             "overdue": True, "active": True, "basis": a.get("issue", "")[:200]}
            for a in anomalies or [] if a.get("status") == "pending_identification"]


def watch_items(watch, today):
    """Flock-level withdrawal_watch rows (hand-kept, MCS-38) surfaced until per-animal
    backfill retires them — a group lock the per-animal records cannot yet derive
    (e.g. the 2026-08-12 whole-flock round, animal identities pending owner)."""
    items = []
    for w in watch or []:
        until = parse_date(str(w.get("not_safe_for_slaughter_until", ""))[:10])
        if not until:
            continue
        items.append({"type": "withdrawal_lock", "animal_id": None,
                      "group": w.get("animals"), "drug": w.get("drug"),
                      "until": str(until), "active": until >= today, "overdue": False,
                      "due": str(until),
                      "basis": f"FLOCK-LEVEL watch: {w.get('animals','?')} — {w.get('drug','?')} "
                               f"(hand-kept; retire into per-animal events, MCS-38)"})
    return items


def build_agenda(db, today, events=None):
    sheep_list = db.get("sheep", [])
    from .breeding import breeding_items
    items = (withdrawal_items(sheep_list, db.get("drug_reference") or {}, today, events)
             + fecrt_items(sheep_list, today, events)
             + famacha_items(sheep_list, today, events)
             + anomaly_items(db.get("anomalies"), today)
             + watch_items(db.get("withdrawal_watch"), today)
             + breeding_items(db, today, events))
    from .intake import inventory_items, quarantine_items
    items += [i for i in quarantine_items(db, today) if i.get("active")]
    items += [i for i in inventory_items(db, today) if i.get("active")]
    items = [i for i in items if i.get("active")]
    items.sort(key=lambda i: (not i["overdue"], i.get("due") or "9999", str(i.get("animal_id"))))
    return {"generated_for": str(today),
            "summary": {
                "overdue": sum(1 for i in items if i["overdue"]),
                "withdrawal_locks_active": sum(1 for i in items if i["type"] == "withdrawal_lock"),
                "unknown_withdrawals": sum(1 for i in items if i["type"] == "unknown_withdrawal"),
            },
            "items": items}
