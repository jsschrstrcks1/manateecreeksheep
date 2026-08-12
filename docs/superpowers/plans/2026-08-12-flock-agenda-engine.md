# Flock Agenda Engine + Household Integration Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Derive the flock's due-items agenda (withdrawal expiries, FECRT windows, FAMACHA rechecks, pending identifications) from `flock_database.json` as a pure, tested engine — the single feed that Atlas serves, Crane displays, and notifications deliver.

**Architecture:** Phase 1 (THIS plan, fully specified): a pure-function agenda engine in manateecreeksheep with a CLI that writes `data/agenda.json`. Phases 2–4 (roadmap below, each needing its own plan against open-claw-stuff): Atlas serves the agenda read-only with a no-false-green staleness guard; Crane/A.B.O.R.T. renders it as a read-only truth panel; MCS-1's weather signal reuses Crane's existing Open-Meteo feed; notifications go to the channel the operator picks. Data flows one way: flock DB (SSOT) → agenda.json → Atlas → Crane/notify. Nothing upstream ever writes back.

**Tech Stack:** Python 3 stdlib only (matches every existing `scripts/` tool); no-framework test runner (repo convention, see `scripts/test_pen_history.py`).

**Placement rationale (the operator's question — HELM, Atlas, or Crane?):** All three, each in its lane, per the household's own architecture law:
- **manateecreeksheep** keeps the data and the *derivation* (this plan) — the truth is computed where the records live, testably, with no household coupling.
- **Atlas** (control plane) gets the *service*: serve `agenda.json` + optionally schedule the daily refresh/notify. Atlas is where services run; a reminder is an action, and actions belong to the control plane.
- **Crane/A.B.O.R.T.** (read-only truth layer — "the truth layer never auto-actions") gets the *display*: a flock panel showing overdue/due items and withdrawal locks. Crane already carries Weather Ops (Open-Meteo + RainViewer), which is exactly MCS-1's weather signal — reuse, don't rebuild.
- **HELM** gets nothing in v1. HELM is the governed cognition pipeline; a date comparison is not cognition. (Optional later: a HELM-composed weekly flock brief that *reads* the agenda.)

---

## Phase 1 — the agenda engine (fully specified below)

### Agenda item types (v1)

| type | source | rule |
|---|---|---|
| `withdrawal_lock` | `health.treatments` × `drug_reference` | each anthelmintic treatment locks slaughter until date+WD days (house-default days when the flock's practice is extra-label) |
| `unknown_withdrawal` | treatments naming a drug not in `drug_reference` and not on the benign list | flag loudly — "unknown withdrawal, consult label/FARAD"; never silently no-op |
| `fecrt_due` | any anthelmintic treatment | follow-up FEC due day 10–14 post-treatment (MCS-30) |
| `famacha_recheck` | `health.famacha_scores` | last score ≥4 → recheck in 7d; =3 → 14d; ≤2 → none (policy constants, operator-tunable) |
| `pending_identification` | `anomalies[]` with that status | standing action item until resolved |

Every item: `{type, animal_id (or null), due, until (locks), overdue (bool at --today), basis}`. Output sorted: overdue first, then by due date.

### Task 1: date parsing + drug classification

**Files:**
- Create: `scripts/lib/flock_agenda.py`
- Test: `scripts/test_flock_agenda.py`

- [ ] **Step 1: Write the failing tests**

```python
#!/usr/bin/env python3
"""Pins for the flock agenda engine. Run: python3 scripts/test_flock_agenda.py (exit 0 = pass).
No framework — the repo has none. Soli Deo Gloria."""
import os, sys
_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)
from datetime import date
from lib.flock_agenda import parse_date, classify_treatment

failures = []
def check(name, cond):
    print(f"  {'ok  ' if cond else 'FAIL'} {name}")
    if not cond: failures.append(name)

# parse_date must handle BOTH formats present in the DB (measured 2026-08-12):
check("ISO date", parse_date("2026-08-12") == date(2026, 8, 12))
check("US short date (famacha style)", parse_date("4-10-26") == date(2026, 4, 10))
check("garbage -> None, never a crash", parse_date("2023-2024") is None)
check("None -> None", parse_date(None) is None)

# classify_treatment: known anthelmintics, known benign, unknown
w, b, u = classify_treatment("Ivermectin + Fenbendazole + Prohibit (levamisole)")
check("triple treatment finds 3 anthelmintics",
      sorted(w) == ["fenbendazole", "ivermectin", "levamisole_prohibit"])
w, b, u = classify_treatment("B-complex 2mL + pig iron 1mL")
check("supportive care is benign, no anthelmintic", w == [] and b and u == [])
w, b, u = classify_treatment("Mystery Drench 5mL")
check("unknown drug is FLAGGED, not ignored", u != [])

if failures:
    print(f"\n{len(failures)} FAILURE(S): {failures}"); sys.exit(1)
print("\nAll agenda pins passed.")
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 scripts/test_flock_agenda.py`
Expected: `ModuleNotFoundError` / `ImportError` (lib.flock_agenda does not exist).

- [ ] **Step 3: Minimal implementation**

```python
"""Flock agenda engine — derive due items from flock_database.json. Pure functions, no I/O.

The MCS-11 'reminder and record are one object' shape: agenda items are DERIVED from the
records (MCS-9 rule), never stored as a second mutable list that can drift. See
docs/UPGRADE-LEDGER.md MCS-7/11/30 and docs/superpowers/plans/2026-08-12-flock-agenda-engine.md.
Soli Deo Gloria.
"""
from datetime import date, timedelta

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
                   "nutri-drench", "probios", "electrolyte")

def parse_date(s):
    """DB dates come in ISO (2026-08-12) and US-short (4-10-26). Anything else -> None."""
    if not s or not isinstance(s, str):
        return None
    s = s.strip()
    for fmt in ("%Y-%m-%d", "%m-%d-%y", "%m/%d/%y", "%m-%d-%Y", "%m/%d/%Y"):
        try:
            from datetime import datetime
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None

def classify_treatment(text):
    """Return (withdrawal_drug_keys, benign_hits, unknown_tokens) for one treatment string."""
    low = (text or "").lower()
    drugs = [k for k, kws in DRUG_KEYWORDS.items() if any(kw in low for kw in kws)]
    benign = [kw for kw in BENIGN_KEYWORDS if kw in low]
    # Unknown = the string names SOMETHING but nothing we recognise at all.
    unknown = [] if (drugs or benign or not low.strip()) else [text.strip()]
    return drugs, benign, unknown
```

- [ ] **Step 4: Run tests — expect all pass**
- [ ] **Step 5: Commit** — `git add scripts/lib/flock_agenda.py scripts/test_flock_agenda.py && git commit -m "feat(agenda): date parsing + treatment classification"`

### Task 2: withdrawal locks + unknown-drug flags

**Files:** Modify `scripts/lib/flock_agenda.py`; extend `scripts/test_flock_agenda.py`.

- [ ] **Step 1: Failing tests (append before the failures check)**

```python
from lib.flock_agenda import withdrawal_items
TODAY = date(2026, 8, 20)
DRUG_REF = {
    "ivermectin": {"house_default_meat_withdrawal_days": 14, "label_meat_withdrawal_days": 11},
    "fenbendazole": {"house_default_meat_withdrawal_days": 28},
    "levamisole_prohibit": {"label_meat_withdrawal_days": 3},
}
sheep = [{"id": "ewe1", "status": "alive", "health": {"treatments": [
    {"date": "2026-08-12", "treatment": "Ivermectin + Fenbendazole + Prohibit (levamisole)"},
    {"date": "2026-08-12", "treatment": "B-complex 2mL"},
    {"date": "2026-08-12", "treatment": "Mystery Drench"},
]}}]
items = withdrawal_items(sheep, DRUG_REF, TODAY)
locks = [i for i in items if i["type"] == "withdrawal_lock"]
check("three anthelmintics -> three locks", len(locks) == 3)
fen = next(i for i in locks if i["drug"] == "fenbendazole")
check("fenbendazole locks until 9/9 (28d)", fen["until"] == "2026-09-09")
iv = next(i for i in locks if i["drug"] == "ivermectin")
check("ivermectin uses HOUSE DEFAULT 14d over label 11d", iv["until"] == "2026-08-26")
lev = next(i for i in locks if i["drug"] == "levamisole_prohibit")
check("expired lock (3d) is not active at 8/20", lev["active"] is False)
check("unknown drug flagged", any(i["type"] == "unknown_withdrawal" for i in items))
check("benign supportive care produces nothing",
      not any("b-complex" in str(i).lower() for i in items))
```

- [ ] **Step 2: Run — expect ImportError on `withdrawal_items`**
- [ ] **Step 3: Implement**

```python
def _wd_days(ref_entry):
    """House default wins (it is the conservative, practice-aware number); else label."""
    return ref_entry.get("house_default_meat_withdrawal_days") \
        or ref_entry.get("farad_sheep_meat_withdrawal_days") \
        or ref_entry.get("label_meat_withdrawal_days")

def withdrawal_items(sheep_list, drug_ref, today):
    items = []
    cutoff = today - timedelta(days=LOOKBACK_DAYS)
    for s in sheep_list:
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
```

- [ ] **Step 4: Run tests — pass** · **Step 5: Commit** `feat(agenda): withdrawal locks + unknown-drug flags`

### Task 3: FECRT windows + FAMACHA rechecks + anomaly items

**Files:** Modify `scripts/lib/flock_agenda.py`; extend tests.

- [ ] **Step 1: Failing tests**

```python
from lib.flock_agenda import fecrt_items, famacha_items, anomaly_items
f_items = fecrt_items(sheep, TODAY)
check("anthelmintic treatment -> one FECRT window per treatment day",
      len(f_items) == 1 and f_items[0]["due"] == "2026-08-22")   # 8/12 + 10d
check("FECRT window not overdue while inside 10-14d", f_items[0]["overdue"] is False)
f_late = fecrt_items(sheep, date(2026, 8, 28))
check("FECRT overdue after day 14", f_late[0]["overdue"] is True)

sheep_fam = [{"id": "ewe2", "status": "alive", "health": {"famacha_scores": [
    {"date": "2026-08-12", "famacha": 5, "notes": ""}]}}]
fam = famacha_items(sheep_fam, TODAY)
check("FAMACHA 5 -> recheck 7d -> due 8/19, overdue at 8/20",
      fam and fam[0]["due"] == "2026-08-19" and fam[0]["overdue"] is True)
check("deceased sheep produce nothing",
      famacha_items([{"id": "x", "status": "deceased", "health": {"famacha_scores":
        [{"date": "2026-08-12", "famacha": 5}]}}], TODAY) == [])
check("non-numeric famacha ('Good') skipped without crash",
      famacha_items([{"id": "y", "status": "alive", "health": {"famacha_scores":
        [{"date": "2026-08-12", "famacha": "Good"}]}}], TODAY) == [])

anoms = anomaly_items([{"date": "2026-08-12", "issue": "Tinker unidentified",
                        "status": "pending_identification"},
                       {"date": "2026-05-21", "issue": "old", "status": "resolved"}], TODAY)
check("pending anomaly surfaces, resolved does not",
      len(anoms) == 1 and anoms[0]["overdue"] is True)
```

- [ ] **Step 2: Run — ImportError expected** · **Step 3: Implement**

```python
def fecrt_items(sheep_list, today):
    """One FEC-recheck window per anthelmintic treatment day (MCS-30 drench-check)."""
    items, cutoff = [], today - timedelta(days=LOOKBACK_DAYS)
    for s in sheep_list:
        if s.get("status") != "alive":
            continue
        seen_days = set()
        for t in (s.get("health") or {}).get("treatments") or []:
            d = parse_date(t.get("date"))
            drugs, _, _ = classify_treatment(t.get("treatment"))
            if not d or d < cutoff or not drugs or d in seen_days:
                continue
            seen_days.add(d)
            lo, hi = d + timedelta(days=FECRT_WINDOW[0]), d + timedelta(days=FECRT_WINDOW[1])
            if today <= hi:
                items.append({"type": "fecrt_due", "animal_id": s["id"], "due": str(lo),
                              "window_end": str(hi), "overdue": False, "active": True,
                              "basis": f"FEC recheck 10-14d after {'+'.join(drugs)} on {d} "
                                       f"tests drug efficacy (FECRT, MCS-30)"})
            elif (today - hi).days <= 21:   # missed recently: still worth saying, then let go
                items.append({"type": "fecrt_due", "animal_id": s["id"], "due": str(lo),
                              "window_end": str(hi), "overdue": True, "active": True,
                              "basis": f"FECRT window after {d} treatment CLOSED unmet"})
    return items

def famacha_items(sheep_list, today):
    items = []
    for s in sheep_list:
        if s.get("status") != "alive":
            continue
        scores = (s.get("health") or {}).get("famacha_scores") or []
        dated = [(parse_date(f.get("date")), f) for f in scores]
        dated = [(d, f) for d, f in dated if d]
        if not dated:
            continue
        d, f = max(dated, key=lambda x: x[0])
        try:
            score = int(f.get("famacha"))
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
```

- [ ] **Step 4: Run tests — pass** · **Step 5: Commit** `feat(agenda): FECRT windows, FAMACHA rechecks, anomaly items`

### Task 4: assembly + CLI

**Files:** Modify `scripts/lib/flock_agenda.py`; Create `scripts/flock_agenda.py`; extend tests.

- [ ] **Step 1: Failing test**

```python
from lib.flock_agenda import build_agenda
db = {"sheep": sheep + sheep_fam, "drug_reference": DRUG_REF,
      "anomalies": [{"date": "2026-08-12", "issue": "Tinker", "status": "pending_identification"}]}
ag = build_agenda(db, TODAY)
check("agenda has meta + items", "generated_for" in ag and isinstance(ag["items"], list))
check("overdue items sort first", all(
    not (b["overdue"] and not a["overdue"]) for a, b in zip(ag["items"], ag["items"][1:])))
check("active withdrawal locks counted in summary", ag["summary"]["withdrawal_locks_active"] >= 1)
```

- [ ] **Step 2: Run — ImportError** · **Step 3: Implement**

```python
def build_agenda(db, today):
    sheep_list = db.get("sheep", [])
    items = (withdrawal_items(sheep_list, db.get("drug_reference") or {}, today)
             + fecrt_items(sheep_list, today)
             + famacha_items(sheep_list, today)
             + anomaly_items(db.get("anomalies"), today))
    items = [i for i in items if i.get("active")]
    items.sort(key=lambda i: (not i["overdue"], i.get("due") or "9999"))
    return {"generated_for": str(today),
            "summary": {
                "overdue": sum(1 for i in items if i["overdue"]),
                "withdrawal_locks_active": sum(1 for i in items if i["type"] == "withdrawal_lock"),
                "unknown_withdrawals": sum(1 for i in items if i["type"] == "unknown_withdrawal"),
            },
            "items": items}
```

CLI `scripts/flock_agenda.py` (complete file):

```python
#!/usr/bin/env python3
"""Emit the flock agenda. Default prints a table; --json writes data/agenda.json.
--today YYYY-MM-DD pins the clock (tests/replays). Soli Deo Gloria."""
import argparse, json, os, sys
from datetime import date
_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)
from lib.flock_agenda import build_agenda, parse_date

REPO = os.path.dirname(_here)
DB = os.path.join(REPO, "data", "flock_database.json")
OUT = os.path.join(REPO, "data", "agenda.json")

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--today", help="YYYY-MM-DD (default: real today)")
    ap.add_argument("--json", action="store_true", help="also write data/agenda.json")
    args = ap.parse_args()
    today = parse_date(args.today) if args.today else date.today()
    if args.today and not today:
        print(f"unparseable --today: {args.today}"); sys.exit(2)
    with open(DB) as f:
        db = json.load(f)
    ag = build_agenda(db, today)
    print(f"Flock agenda for {ag['generated_for']} — "
          f"{ag['summary']['overdue']} overdue, "
          f"{ag['summary']['withdrawal_locks_active']} withdrawal locks, "
          f"{ag['summary']['unknown_withdrawals']} unknown-withdrawal flags\n")
    for i in ag["items"]:
        mark = "!!" if i["overdue"] else "  "
        print(f" {mark} {i['due']}  {i['type']:<24} {str(i.get('animal_id') or '-'):<22} {i['basis'][:90]}")
    if args.json:
        with open(OUT, "w") as f:
            json.dump(ag, f, indent=2)
        print(f"\nwrote {OUT}")

if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run `python3 scripts/test_flock_agenda.py` (all pass) AND the live smoke:**

Run: `python3 scripts/flock_agenda.py --today 2026-08-20`
Expected: table listing GG's fenbendazole lock (until 2026-09-09), the ivermectin locks (until 2026-08-26), FECRT windows due 2026-08-22, GG + Azure FAMACHA rechecks, Tinker pending-identification. Cross-check by hand against `withdrawal_watch` in the DB.

- [ ] **Step 5: Run the full suite** — `python3 scripts/test_flock_agenda.py && python3 scripts/test_pen_history.py && python3 scripts/test_validate_flock.py && python3 scripts/validate_flock.py`
- [ ] **Step 6: Commit** `feat(agenda): assembly + CLI — the household integration feed`

### Task 5: ledger + HLS closeout

- [ ] Mark the plan/agenda work in `docs/UPGRADE-LEDGER.md` (MCS-7/11/30 rows gain "engine shipped" note), commit `[no-reasoning]`, push, and return the HLS task for quorum.

---

## Phases 2–4 — household integration roadmap (each gets its own plan, written against open-claw-stuff at execution time)

**Phase 2 — Atlas serves it (control plane).** A read-only endpoint (shape: `GET /flock/agenda` returning `data/agenda.json` + freshness metadata) backed by the manateecreeksheep checkout on the Atlas host, refreshed by `git pull && flock_agenda.py --json` on a timer. MUST follow the household **no-false-green** law: if the checkout is stale (>24h) or the pull fails, the endpoint says STALE/UNAVAILABLE — never yesterday's agenda presented as today's. An Atlas frontend card mirrors the summary counts. *Decision point for the operator: which notification channel is "the one you already watch" (MCS-2) — Atlas push, text, or something else. The daily digest goes there; individual OVERDUE items escalate.*

**Phase 3 — Crane displays it (truth layer).** A read-only flock panel in A.B.O.R.T.: summary counts, overdue list, active withdrawal locks. Crane law holds: display only, no actions. Tie into Crane's existing attention states: an open FAMACHA-5 or an overdue `unknown_withdrawal` participates in the attention/danger visual language the HUD already has.

**Phase 4 — weather closes MCS-1 (reuse Crane's feed).** Crane Weather Ops already pulls Open-Meteo for this property. A small enrichment in the Phase-2 refresh job: when the trailing 14 days are Haemonchus-favorable (warm + wet — thresholds start at the literature's ~10°C+ with moisture, tuned for Florida where the answer is usually "yes" in summer), tighten `FAMACHA_RECHECK_DAYS` one notch (14→10, 7→5) and say so in each item's `basis`. Advisory only; the agenda never treats anyone.

**Phase 5 — the flock PWA (operator directive 2026-08-12).** Installable PWA served BY Atlas at
`/flock` on the tailnet (same origin as the Phase-2 agenda API). First-run token entry, stored
on-device encrypted at rest (passkey/WebAuthn-PRF-wrapped where supported; non-extractable
CryptoKey fallback) — never baked into the bundle, never synced. Prefer a flock-SCOPED token over
the owner token on phones (Atlas already tiers owner vs family; `/helm` stays owner-device-only).
Offline-first with a sync queue for chute-side entry (FAMACHA, weights, MCS-6 batch sessions);
reads the agenda; strict CSP, no third-party scripts. Needs its own plan against Atlas's actual
serving patterns; Phase 2 is its prerequisite.

**Phase 5 auth model (operator decision 2026-08-12): one app, progressive by token — NO second
auth system.** The token entered at setup determines the app: a **flock-scoped token** renders the
pure sheep app (barn view home screen; the household-infra surfaces do not exist for that token —
containment by scope, not by navigation; this is the family/mother case solved with zero new auth
infrastructure); the **owner token** grows the same install into agenda + Atlas cards + HELM
links, with a hard visual boundary when crossing out of sheep-world (distinct header treatment +
persistent "back to flock" crumb — the operator's prominent-links idea, applied to the owner mode
where two worlds genuinely coexist). BINDING RULE: capability is enforced SERVER-SIDE by the
token's scope at every endpoint; the PWA discovers capabilities via a whoami-style call and merely
reflects them — hiding a panel is UX, Atlas refusing is the security. Server-side work item for
Phase 2: add a `flock` scope to Atlas's existing owner/partner/family token tiers (the mechanism
that already refuses non-owner on `/helm` — same mechanism, one more tier).

**Explicitly out of scope until their prerequisites exist:** periparturient scheduling (MCS-33 — needs MCS-17's breeding pipeline), HELM involvement (optional weekly brief, later).

## Self-review notes
- Spec coverage: withdrawal (MCS-7) ✓ Task 2 · FECRT (MCS-30) ✓ Task 3 · FAMACHA recheck (MCS-1/11 core) ✓ Task 3 · pending IDs ✓ Task 3 · assembly/CLI ✓ Task 4 · Atlas/Crane/weather/notify ✓ Phases 2–4 as named follow-on plans (deliberate: their code patterns must be read in open-claw-stuff first, and Atlas changes are Layer-3 harness changes in the operator's runtime).
- Types consistent: every item carries `type/animal_id/due/overdue/active/basis`; `until` only on locks; checked across Tasks 2–4.
- No placeholders: every step carries runnable code or an exact command.
