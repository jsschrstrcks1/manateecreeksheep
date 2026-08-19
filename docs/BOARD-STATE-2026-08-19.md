<!-- Soli Deo Gloria. Closing board-state report — end of the 2026-08-18/19 build loop. -->

# Board state — 2026-08-19 (end of build loop)

The buildable board is **dry**: every MCS ledger row and HLS sheep task that could be
built from data we actually hold has been built, tested, and returned for quorum.
What remains needs either **Ken's answers**, **the field**, or **the Atlas runtime** —
none of it is codeable honestly from this chair.

Branch: `claude/sophos-install-sheep-tasks-5y1wv2` (both repos). ~28 HLS tasks built
across 13 rounds under patron `syl`. Validator: 0 errors, 3 known warnings. All 7 test
suites green.

## Built (this loop, high level)

| Family | What ships |
|---|---|
| Health spine | Typed append-only event log (MCS-26) + `health_log.py` CLI, withdrawal auto-locks (MCS-7), famacha key migration, notes→events migration |
| Chute | `work_flock.py` batch grammar (f/w/wormer/vax/fec/shed/tail/milk/trim/shear/blood/wean/note), crash-safe per-line appends, `app/chute.html` phone front end (MCS-6/33) |
| Agenda | `flock_agenda.py` engine: withdrawal, FECRT rechecks, FAMACHA cadence, anomaly watch, breeding calendar, quarantine releases, inventory alerts → `data/agenda.json` |
| Parasites | Deworm advisor (MCS-8), triage ordering (MCS-3), FECRT pairing (MCS-30 core), weather module gated on coordinates (MCS-1, refuses without them) |
| Breeding | Matings schema + derived statuses (MCS-17), predictor (MCS-22), pedigree/Wright's F (MCS-16), PRNP + trait cards (MCS-15/32), ewe productivity (MCS-18) |
| Pens | 8-pen canon (1–6 + Tree Fort + Goose Pen) with aliases, movements log, point-in-time cohorts (MCS-9/10/40) |
| Economics | Per-animal ledger (MCS-13), hold-vs-sell (MCS-24), adjusted 60d weights with sourced factors (MCS-27), input inventory (MCS-25) — all refuse invented numbers |
| Intake/loss | Quarantine records with 28d release gate (MCS-28), LIP-shape loss records — 3/80 deceased currently claim-ready (MCS-29) |
| Capture | Quantity shape (MCS-12) incl. coat-shed/fat-tail/milk measures (MCS-19/20/21) wired into chute + log |
| Guards | Pre-commit ledger check + flock validation on staged data; pre-push privacy attestation + force protection |

## Owner-gated (waiting on Ken — the questionnaire is the front door)

1. **`admin/OWNER-SYNC-QUESTIONNAIRE.md`** — 43 placeholder dates, 94-animal pen census,
   5 UNCLEAR markers, ram-in dates (seeds the whole breeding calendar), farm coordinates
   (unlocks weather tightening), **economics figures** (unlocks profit/hold-vs-sell), and
   the **shelf inventory count** (unlocks expiry/reorder alerts).
2. **Prohibit outcome** — the levamisole dose for Lara's ram lamb (planned 2026-08-19),
   plus FEC samples before dose and at day 10–14: the first real FECRT data point on
   presumptive ivermectin resistance.
3. **Repo privacy flip** — manateecreeksheep is still PUBLIC; the pre-push gate blocks
   future sessions until it is flipped (`flip-manateecreeksheep-to-private`, P6).
4. **"Lara is on"** clarification (mend vs. treatment) — one questionnaire line.
5. **PR #83 / stranded branch** `claude/memory-system-evaluation-s0yup4` — operator merge
   review (MCS-39); 4 salvages already lifted.

## Atlas-side (needs the runtime, not this session)

- ~~Serving `data/agenda.json` to phones~~ **DONE 2026-08-19** — `GET /api/flock/agenda`
  wired into atlas-serve (owner-gated, OK/STALE/UNAVAILABLE, never empty-OK); goes live
  at the next atlas-serve restart on the cluster.
- Push-reminder delivery (MCS-2 push half → `mcs-push-reminders-delivery`) — blocked on
  Ken's channel choice (questionnaire ask added), then a small Atlas delivery hook.
- `mcs-sheets-sync-l6` (sheet round-trip) and the PWA server half (MCS-34).

## Parked deliberately

- MCS-14 (CV condition scoring) and MCS-31 (BLUP animal model) — HEDGED, cost over benefit
  at 276 head; MCS-23 (NRC ration evaluation) — needs sourced NRC tables + actual feed data.

**Soli Deo Gloria.**
