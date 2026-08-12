# Upgrade Ledger — Manatee Creek Sheep

**Soli Deo Gloria.** Candidate upgrades for the flock system — design, feature, process,
anything worth remembering. Append the moment you notice it; the bar is "I noticed something,"
not "this is worth doing." A row is a *candidate*, not a commitment. Ground the claim or mark
it `(hunch)`. A refusal is an entry too (`decided-no` + reason) — re-deriving a decision costs
more than recording it.

Ids are repo-local (`MCS-NNN`), distinct from the household `UL-NNN` spine in `open-claw-stuff`.

| id | candidate | detail | status |
|----|-----------|--------|--------|
| MCS-1 | **Weather/climate-aware parasite-risk prompting** | Barber-pole worm (*Haemonchus*) pressure is heat- and rainfall-driven, so in Florida the FAMACHA-recheck interval is really a function of weather, not just a fixed calendar. Idea: layer a location/season signal over the existing FAMACHA/FEC records so the system nudges "recheck sooner — warm+wet stretch" instead of a flat schedule. Grounded in the actual epidemiology; the *idea* is sound, the calibration is the work. Noticed 2026-08-11 while evaluating three coincidentally-named "homesteady" GitHub repos for the operator — `brechy/homesteady-landing` (a marketing landing page for an unbuilt livestock+garden app; advertised "seasonal task lists by climate") and `thomaselucas/homesteady` (a garden-only student project doing weather-by-zip → USDA hardiness). Concept only; **no code taken** — neither repo has flock logic, both are unlicensed, one is a landing page and the other stale (Dec 2024). Build against our own records, not their code. | `candidate` |
| MCS-2 | **Push reminders to a channel the operator already watches** | The third lookalike, `entro-afk/homesteady` (2020, a Discord bot, no license, no livestock logic), does one thing worth naming: a due-date table DMs the user a reminder where they already are, instead of waiting for them to open an app. For the flock, a FAMACHA-recheck / treatment-withdrawal / breeding-due reminder pushed to text or a channel Ken already reads would get acted on more reliably than one that lives only in the records tool. Delivery-channel idea, not their code (Discord/Trello/Sheets stack, none of which we'd adopt). Pairs naturally with MCS-1: the weather signal decides *when* to nudge, this decides *where* the nudge lands. | `candidate` |
| MCS-3 | **Attention-priority triage list — who needs looking at first, by a composite score** | Instead of a flat flock roster, show a list sorted by a per-animal *attention score* with red/amber/green status, so the shepherd sees who to check first: composite of FAMACHA trend (worsening?), last FEC, days-since-last-check, plus late-pregnancy / recent-treatment flags. FAMACHA is already a 1–5 colour scale, so a "worst-first" triage view is a natural extension of data we already keep. The *shape* was prompted by `Brechy/AntLog` (a list of contenders each carrying a computed score, sorted descending, with status states) — but AntLog's score is literally `Math.random()`, so the substance here is entirely ours; only the UI pattern rhymed. No code taken. | `candidate` |
| MCS-4 | **`decided-no`: brechy's 60 repos hold no further flock concepts — do not re-mine** | Operator asked (2026-08-11) to explore all 60 of Brechy's GitHub repos for sheep-relevant concepts. Triaged the full account: **~30 are forks** of other people's OSS (redux, express, lodash, oh-my-zsh, freeCodeCamp, treeherder…) — not her work; **~20 are 2018 Galvanize bootcamp exercises** (toy problems, DOM drills, shopping carts, metronome, number-wizard, pixel-art, prison-escape); the rest are small original learning apps (SleepSmart sleep-toy dashboard + Flask API 2018; fraud-investigator probability-predictor exercise; expense-tracker; react-inbox; hangul-master flashcards; AntLog mocked ranker; help_generator hardcoded chore array). Only `homesteady-landing` is in our domain, and it already yielded MCS-1/MCS-2; AntLog prompted MCS-3. **Nothing else transfers.** Recorded so the account is not re-explored expecting flock gold. All repos unlicensed → no reuse grant regardless. | `decided-no` |

| MCS-5 | **EID + visual dual identity — two independent tags per animal** | `OogieM/LambTrackerMobile` (a real shepherd-built Android flock system, GPL-2, ~552 references to `eid`) documents every sheep by BOTH an electronic tag (EID/RFID) *and* a visual tag. The point: identity is robust to a lost or unreadable tag — scan the EID at the chute, but a torn-off button tag still identifies the animal by eye, and vice versa. For our records, storing both (and treating either as a valid lookup key) beats a single tag that, when it fails, orphans an animal's whole history. Concept from a GPL-2 project — free to *adopt as a design*; if we ever lift their code, GPL-2 obligations attach, so keep it concept-level. | `tracked` → `mcs-eid-visual-dual-identity` (P2) |
| MCS-6 | **"Working the flock" batch session — one pass, a per-animal action checklist** | LambTracker's `GroupSheepManagement` runs the whole flock through the chute in a single session, logging multiple interventions per animal at once via checkboxes: **wormer, vaccine, weight, blood draw, drug, trim toes, shear, weaned**. This matches how shepherding actually happens — you don't open each animal's page one at a time; you process the group and tick what you did to each as it comes through. A batch-entry mode (pick the animal, check off today's actions, next animal) would fit real barn/chute work far better than per-record forms. Design concept (GPL-2 source; ours to adapt at concept level). | `tracked` → `mcs-working-the-flock-batch-session` (P2) |
| MCS-7 | **Per-drug meat/milk withdrawal tracking with "not safe until" alerts** | LambTracker stores a `meat_withdrawal` period per drug/vaccine and alerts on slaughter withdrawal when one is administered. This is a food-safety essential we should have: when a ewe is treated, the system records the drug's withdrawal interval and flags the animal as **not safe to slaughter / milk-not-saleable until <date>** — so a treated animal can't be sold to slaughter or its milk marketed inside the withdrawal window by mistake. Directly relevant to a meat/parasite flock. Concept (GPL-2 source). | `tracked` → `mcs-drug-withdrawal-tracking` (P1) |
| MCS-8 | **FAMACHA + FEC combined deworming decision — and disagreement is a *signal*** | `DvdMeneses/FuzzyLogic-VERMIFUGA` (a FAMACHA-based goat-deworming decision project; no license, **concept only, no code**) combines the FAMACHA eye-color score with OPG/FEC (fecal egg count) rather than deworming on colour alone, and — the valuable part — treats the two *disagreeing* as diagnostically meaningful: **anemic (bad FAMACHA) but LOW egg count → the anemia may not be parasites** (look for another cause before dosing), while **good colour but HIGH egg count → the animal is coping but shedding heavily onto pasture** (a contamination / refugia consideration even though it "looks fine"). This sharpens MCS-1: the recheck/treat nudge should read FAMACHA and FEC *together*, and surface the mismatch cases rather than blindly deworming on one number. Grounded in the standard integrated-parasite-management practice. | `tracked` → `mcs-famacha-fec-combined-decision` (P1) |

| MCS-9 | **Log-as-source-of-truth, current state DERIVED — the flock data-model spine** | `farmOS/farmOS` (GPL-2, 1.3k★, the mature reference-grade open-source farm-records platform, active since 2014) is built on one architectural decision worth stealing at the *design* level: the two primary record types are **Assets** (the animal, the pen, the group) and **Logs** (events with a timestamp), and **current state is never stored as a mutable field — it is derived from the logs.** An animal's current pen is computed from its movement logs; its group membership from group-assignment logs; inventory from input/harvest logs. The payoff is *free history that answers questions you didn't plan for*: "which pen was ewe #14 in during the July barber-pole spike?" or "which animals shared a paddock with the one that scoured?" fall straight out of the log, because nothing was ever overwritten. For a parasite-driven flock this is not a nicety — pasture-contamination and refugia reasoning (MCS-8) *need* a truthful movement history, and a system that stores only "current pen" throws exactly that away. This is the load-bearing choice: MCS-1/3/5/6/7/8 all get simpler and more honest once records are append-only events with derived state, and painful to retrofit later. Concept from a GPL-2 platform — adopt the *shape*, not the code (their stack is Drupal/PHP, which we would not take). | `implemented (pen dimension)` → `mcs-pen-movement-log-derived-state` (P1) |
| MCS-10 | **Group/cohort as a first-class asset with log-derived, time-aware membership** | farmOS models a **Group** as its own asset that "contains" members, and — because membership changes are recorded via logs (MCS-9) — you can ask *who was in this group at any past date*, not just now. For the flock this maps cleanly onto the cohorts a shepherd actually reasons about: a **breeding group** (which ram covered which ewes, and when), a **treatment cohort** (everyone dewormed on the same day, so their withdrawal windows and refugia effect are one query — pairs with MCS-6/MCS-7), a **drylot/refugia group** (animals pulled off contaminated pasture). Move an animal in or out with a log; the history is preserved. Distinct from MCS-6 (a single chute session) — this is about *durable, queryable cohorts over time*. Design concept (GPL-2 source, no code). | `candidate` |
| MCS-11 | **The reminder and the record are ONE object — a log's `pending`→`done` status** | In farmOS every log carries a **status: pending / done / abandoned** and a timestamp that can be in the future. That collapses a distinction we were about to build twice: a "recheck FAMACHA on the 20th" **reminder** (MCS-1/MCS-2) and the FAMACHA **observation record** are not two things — they are *one log*, created `pending` with a future date, then flipped to `done` when the check happens (carrying its FAMACHA/FEC quantities). The "what's overdue" triage (MCS-3) becomes simply *pending logs whose date has passed*; the weather signal (MCS-1) just moves a pending log's date earlier. One primitive — a dated, status-bearing log — underpins reminders, the worklist, and the historical record at once, instead of a separate reminders table that can drift out of sync with what was actually done. Data-model refinement of MCS-1/2/3 (GPL-2 source, concept only). | `candidate` |
| MCS-12 | **One `quantity` abstraction for every measurement — value + unit + measure + label** | farmOS attaches **Quantities** to logs as a uniform structure (a numeric value, a unit, a "measure" e.g. weight/count/ratio, and a label) rather than a bespoke database column per metric. Everything a shepherd measures fits the same shape: **body weight** (value+kg), **FAMACHA score** (1–5, a rating), **FEC/OPG egg count** (count per gram), **body condition score**, **temperature**. The benefit is that new measurements don't need schema changes, and trends/charts/alerts can be written *once* against "quantities of measure X" instead of per-field. Directly supports MCS-3's composite attention score (it reads several quantities) and MCS-8's FAMACHA+FEC pairing (two quantities on one observation log). Data-model concept from a GPL-2 platform; shape only, no code. | `candidate` |

| MCS-15 | **Scrapie genotype (PRNP codons 136/154/171) tracking + breeding selection** | EVSoft's "Sheep Register" tracks **scrapie codons** — and this is a real, standard, *heritable* sheep trait our model doesn't keep. Scrapie resistance is governed by the PRNP (prion protein) gene, chiefly codon **171** (the **R** allele confers resistance, **Q** susceptibility) plus 136 (A/V) and 154 (R/H); breeders record genotypes in haplotype notation (**ARR** = most resistant … **VRQ** = most susceptible) — the USDA National Scrapie Eradication Program is built on exactly these. For a **breeding** flock selecting for hardiness this is a peer to FAMACHA/FEC: a per-animal genotype field (e.g. `171: QR`, or `ARR/ARQ`) that (a) flags susceptible animals, (b) feeds breeding decisions toward resistant offspring, and (c) can be *derived down a pedigree* we already store (sire/dam alleles → possible offspring genotypes). Directly serves the closed-loop pipeline. New dimension. Concept only — EVSoft is proprietary (no source); the genetics are public-domain standard practice. | `candidate` |
| MCS-16 | **Rendered pedigree views + certificates, and (our extension) an inbreeding coefficient** | EVSoft's rabbit register surfaces the lineage we already store (sire/dam) as *presentation*: N-generation pedigree charts (6 on screen; 3/4-gen printable certificates), full-sibling / half-sibling grouping, and ancestor/descendant browsing. We keep `sire_id`/`dam_id`/`offspring_ids` but don't render a pedigree or issue a certificate. **Our extension beyond EVSoft:** compute an **inbreeding coefficient** (Wright's F) from that pedigree — EVSoft *shows* pedigrees but I did not see it *quantify* inbreeding; the F-coefficient is the natural add, and it directly serves the flock's stated closed-loop inbreeding policy (`breeding_policy.inbreeding_policy`) instead of leaving "too close?" to eyeballing the tree. Moderate value; the data exists, the gap is the view + the coefficient. Concept (pedigree-rendering prompted by proprietary EVSoft; F-coefficient is standard population genetics). | `candidate` |
| MCS-14 | **(hedged/low-confidence) Image → 1–5 score via computer vision — BCS, and by analogy FAMACHA** | `MVet-Platform/M-Vet_Livestock_Datasets` (Jupyter, no license, a 2024 hackathon resource hub, **concept only**) frames "predict a **body condition score** (1–5) from a photo of the animal" as a CV regression task. The transferable *method* — phone photo at the chute → a 1–5 score — rhymes with two numbers we already keep: BCS (MCS-12) and, more interestingly, **FAMACHA** (also a 1–5 scale, but of eye-membrane colour), which is a natural image-classification target and which we already log in `health.famacha_scores`. The flock already handles images (notebook-card transcription, `process_images.py`), so the pipeline is not foreign. **Heavy honest hedges, which is why this is low-confidence, not a plan:** (1) sheep BCS is traditionally *hands-on* palpation because fleece/hair hides body condition — photo-BCS is weaker for sheep than for the short-haired cattle/pigs M-Vet targets (our hair focus helps a little, not enough to trust blindly); (2) photo-FAMACHA is **safety-critical** — a wrong read drives a wrong deworming decision — and needs a labelled dataset we do **not** have, plus validation against the physical card; (3) dedicated FAMACHA apps already exist (`mauriciobenjamin700/FAMACHA_APP_*`, noted below). So: a real method, recorded, but not worth building until there's labelled data and a safety story. No code/data taken (unlicensed). | `candidate` |
| MCS-13 | **Per-animal economic lifecycle — cost basis in, proceeds out, profit per genetics** | `DigiBanks99/livestock-tracker` (C#/.NET + Angular, **no license → all-rights-reserved, concept only, no code**) records on each animal a full money+lifecycle spine we don't yet keep: `PurchaseDate`+`PurchasePrice`, `SellDate`+`SellPrice`, `ArrivalWeight`, `BirthDate`, `DateOfDeath`. For a *meat* operation this closes a real loop: cost basis (purchase price + accumulated feed/medical inputs) vs. sale proceeds = **profit per animal**, and paired with a weight log (MCS-9 extended to weight), **cost-of-gain** and days-to-market. The selection payoff is the point — the flock goal is "hardy, hairy, **meaty**, parasite-resistant," and this lets "which genetics actually pay" become a measured selection signal instead of a hunch, tying breeding decisions to the operation's economics. New dimension (not a reframe of an existing row). Candidate — Ken's call whether the flock is bought-in enough for purchase-side tracking to earn its keep, or whether it's mostly sell-side + input costs. | `candidate` |

**DigiBanks99/livestock-tracker evaluation (2026-08-12):** C#/.NET + Angular/NgRx, ~13★, long-
lived (2018→2026), **no license file → all-rights-reserved by default; concepts only, no code
taken** (its stack is not ours regardless). Its architecture *independently confirms* the MCS-9
lift: every dimension is a per-animal **transaction log** — `WeightTransactions[]`,
`MedicalTransactions[]`, `FeedingTransactions[]` hang off the `Animal`, exactly the append-only
event shape farmOS uses and we just adopted for pen. Two reinforcements, one new find, one minor
idea:
- **Reinforces MCS-9 → weight:** weight is a `WeightTransaction` log here, not a scalar — direct
  support for extending our movement-log treatment to the weight/measurements dimension next
  (our `measurements{}` is still a single overwrite; see MCS-9's "still a scalar" row).
- **Reinforces MCS-12:** both `MedicalTransaction.Dose` and `FeedingTransaction.Quantity` carry a
  shared `UnitId` → `Unit` reference — the uniform value+unit shape MCS-12 proposes. Also notes
  that a medical record should capture **dose + unit** (pairs with MCS-7 withdrawal tracking).
- **NEW (MCS-13):** the purchase/sell price + date lifecycle above — genuinely absent from our model.
- **Minor idea (not ledgered separately):** the app's validations **freeze a sold/deceased
  animal's record** (reject edits after a terminal state). A modest "terminal-state guard" for our
  DB — e.g. reject a movement or measurement dated after `DateOfDeath` — would have flagged
  exactly the baby-azure staleness from a different angle. Folds into the MCS-9 validation family;
  noted here rather than promoted. **No upstream code taken.**

**EVSoft / Evans Software evaluation (2026-08-12):** `https://evsoft.us` — "Quality Software for
Animal Breeders Since 1988," a proprietary Windows breeding-registry product (Rabbit/Cavy/
Chinchilla registers + "Other Species": birds, goats, pigeons, chickens, **sheep**). **Proprietary,
no source → concepts only** (which is all we'd take anyway). This was the richest of the sweep after
farmOS. New finds: **MCS-15** (scrapie genotype — the sheep register's headline feature and a real
gap in our model) and **MCS-16** (rendered pedigrees/certificates + an inbreeding coefficient).
Reinforcements, not new rows: multi-key animal lookup by name/ear#/cage#/reg# **confirms MCS-5**
(any tag a valid key); growth charts + **Feed Conversion Ratio** confirm extending MCS-9 to a
weight/growth *log* and sharpen **MCS-13** (feed-efficiency / cost-of-gain as a selection+economic
metric); per-operation income/expense-by-category confirms **MCS-13**; auto age-class from birth
date and over/under weight-standard flags are the **MCS-9 derived-state / MCS-3 triage** patterns in
another tool. Milk-production records noted but low-relevance (this is a meat/hair flock, not dairy).
No code taken (proprietary).

**`decided-no` (2026-08-12): `rancher/rancher` — a Kubernetes/container platform, not ranching.**
Name-and-metaphor collision (ranch → rancher). The repo (Go, Apache-2.0, ~25.8k★, "Complete
container management platform"; its `cattle` topic is the DevOps "pets vs cattle" meme and an old
orchestrator codename, not animals). Zero husbandry content. The only conceivable household touch
is the *infrastructure* layer — Rancher's desired-state reconciliation / multi-cluster fleet
management rhymes with Atlas/HELM — but that is **not the sheep project**, and the household already
runs its own governed runtime, so it is not even a gap there. Off-domain for the flock; not
re-examined. (For the flock's data model, the relevant pattern is MCS-9's event-log→derived-state,
which is a records shape, not a control-loop reconciler.)

**`decided-no` (2026-08-12): `Lcry/a-sheep-assistant` — a bot for the mobile GAME "羊了个羊 /
Sheep a Sheep", not livestock.** Operator flagged it with a China-origin caution. The repo
(Python, GPL-3.0, ~795★) is an auto-solver — its own description says "羊了个羊助手 … 一键闯关"
(one-click level-clearing) for the viral tile-matching game 《羊了个羊》. The word "sheep" is the
game's *name*; there is no animal husbandry here at all. Out under the "**not games**" rule and
simply off-domain — another coincidental sheep name-collision, like the homesteady lookalikes.
**Handling of the China caution:** evaluated from repository metadata only — **no clone, no
execution, no code imported** (mantra + heightened supply-chain wariness); the description's WeChat
self-promotion was ignored as untrusted marketing, not acted on. Nothing installed; no risk
realized. Not re-examined.

**Two-repo evaluation (2026-08-12) — one game (rejected), one hackathon dataset:**
- `DragN0007/Overhauled-Livestock-1.20.1` — **`decided-no`: a Minecraft mod** (Java, Minecraft
  version "1.20.1", author DragN0007 makes "Overhauled Horses/Wolves" Forge mods; description "An
  overhaul for livestock/ farm animals" is in-game animals). Falls under the operator's standing
  "**Not games**" rule (2026-08-11). No husbandry concept; not re-examined.
- `MVet-Platform/M-Vet_Livestock_Datasets` — a 2024 CV **hackathon** resource hub (animal-type
  detection + BCS-from-photo, subjects cattle/goats/pigs, no license, no sheep, no parasite data).
  Not a management tool; the dataset itself transfers nothing. Only the *method* survived as the
  hedged, low-confidence **MCS-14** (image → 1–5 score), explicitly not worth building yet. No
  data taken (unlicensed).

**farmOS evaluation (2026-08-12):** `farmOS/farmOS` (GPL-2.0, PHP/Drupal, ~1,335★, active
since 2014; topics incl. `livestock`). Reviewed at the operator's request. This is the
strongest external source seen so far — not a toy or a lookalike but the **mature reference
platform** for farm record-keeping, and its data model is the real prize. MCS-9..MCS-12 are the
survivors: one architectural spine (append-only logs, derived state) and three refinements it
enables (time-aware groups, reminder=record, uniform quantities). Also noted inline: farmOS
models **ID Tags as a multi-valued list** on the animal (generalises MCS-5's two-tag idea to N
tags, each a valid key) and **Flags** (`Priority`, `Needs review`) as freeform record tags
(generalises MCS-3's R/A/G triage). **Honest strategic note for the operator — build vs. adopt:**
farmOS already *does* much of what this project is scoped to do (animal assets, medical/treatment
logs, movements, groups, quantities, a JSON:API, self-hostable). Before building all of it from
scratch it is worth a deliberate decision on whether to **adopt or extend farmOS** (GPL-2, so
derivative works inherit GPL-2 obligations) versus build our own lighter tool that borrows only
these design shapes. That is the operator's call, not mine — recorded here so the question is on
the page rather than lost. **No upstream code taken; concepts and data-model shapes only.**

**MCS-9 implementation note (2026-08-12) — the pen dimension shipped, concept lifted not code:**
Implemented the farmOS "log is the source of truth, current state is derived" shape for the
*pen* dimension (weight/measurements and breeding-group dimensions remain `candidate`). What
landed on branch `claude/memory-system-evaluation-s0yup4`:
- **`scripts/lib/pen_history.py`** — pure derived-state library: `current_pen(sheep)` reads the
  last entry of an append-only `sheep["movements"]` log (array order is truth; `date` may be
  null and is annotation, never used to reorder — we do not invent move dates); `derive_rosters`
  / `derive_id_to_pen` project the `pens{}` roster back out of the logs.
- **`scripts/migrate_pen_to_movements.py`** — idempotent, dry-run-by-default migration. Seeded
  51/276 placed sheep with a single "initial placement" movement (date null — entry date
  genuinely unknown); the other 225 got an empty log. Measured first: the scalar `pen` and the
  `pens{}` rosters were 100% consistent (0 disagreements), so seeding needed no guesswork. The
  scalar `pen` field is **kept as a derived mirror** (every Sheets export + web consumer reads
  it) and recomputed from the log, so nothing downstream broke — verified `export_to_sheets.py
  --dry-run` still plans all 24 tabs.
- **`scripts/validate_flock.py`** — new `validate_pen_movements(db)`: scalar-vs-log **drift is an
  ERROR** (the mirror can't be hand-edited out from under the log), plus roster-vs-log projection
  **WARNINGs** and movement-shape checks. Wired into the default run.
- **`scripts/test_pen_history.py`** — 20 no-framework pins (derivation, migration idempotence,
  drift ERROR, roster WARNING). Green; existing `test_validate_flock.py` still green.
- **First real catch:** the roster check immediately surfaced `baby-azure` — **deceased** (heat,
  2026-06-24), yet still listed in Pen 2's `members` roster while her own record correctly had no
  pen. The lift didn't create the discrepancy; it *exposed* a stale hand-roster entry, and the
  derived state (in no pen) is the more correct one. Left as a surfaced WARNING, **not** silently
  edited (her prose-only history Pen 1→Goose Pen→Pen 2→died was not fabricated into structured
  moves, and the hand roster is the operator's to correct deliberately). This is the payoff of
  MCS-9 in one example: drift that was invisible is now a CI warning. **No farmOS code taken.**

**Provenance note (2026-08-11):** MCS-1..MCS-4 are the *only* survivors of evaluating
`brechy/homesteady-landing`, `thomaselucas/homesteady`, and `entro-afk/homesteady` at the
operator's request. Verdict on all three: coincidental name collision, none related to each
other, none a tool or component for this project. What survived is two feature *concepts*, not
software to integrate. Concepts only; nothing installed; all three are unlicensed (all-rights-
reserved by default), so there is no reuse grant even where a fragment looked handy.

**GitHub livestock/FAMACHA scan (2026-08-11):** MCS-5..MCS-8 came from a targeted search for
real critter-management tools (not games/exercises). Sources: `OogieM/LambTrackerMobile`
(GPL-2, a genuine long-lived shepherd-built system — the richest source; note it moved active
development to GitLab, worth a deeper look later); `DvdMeneses/FuzzyLogic-VERMIFUGA` (FAMACHA+FEC
deworming logic; unlicensed → concept only); `iamsakan/flockbook` (fresh 2026 weight/medical/
reminder app — confirmed the feature triad we already plan, no *new* concept, unlicensed). Also
seen and noted but not mined deeply: `mauriciobenjamin700/FAMACHA_APP_MOBILE`/`_DESKTOP`
(dedicated FAMACHA apps, Python/Kivy), `AmanyaPhillip/Farm-Management` (offline-first Flutter,
reinforces MCS-1's offline angle), `elaclef/REPROsheep2.0_ABM` (academic dairy-sheep reproduction
model — research, not a tool). **No upstream code taken from any of them.**

**Soli Deo Gloria.**
