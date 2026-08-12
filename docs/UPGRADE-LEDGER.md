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
| MCS-17 | **Master breeding pipeline — one row per mating, the whole cycle as derived dates, pending vs done** | EVSoft's "Master Breeding List" screen (operator-supplied screenshots, 2026-08-12) tracks each *mating* as one row carrying the full reproductive cycle: date bred → palpate → nest in → due → born → #born → wean → #weaned → **rebreed date**, with future/pending dates visually distinct from completed ones. The load-bearing idea: everything after "date bred" is **derived** — for sheep, gestation ~147d makes it deterministic. Record one fact (ewe X bred to ram Y on date D, which `breeding_plans` already wants) and the system computes: pregnancy-check window, due date, lambing watch, wean target (~60–90d), and rebreed eligibility — surfacing each as a pending item until confirmed done. This is MCS-9 derived-state + MCS-11 pending→done applied to reproduction, and it directly runs the 7-pen closed-loop pipeline's calendar instead of leaving it in heads/notebooks. Strong candidate — the flock is a *breeding* operation first. Concept from screenshots of proprietary software; no code exists to take. | `candidate` |
| MCS-18 | **Ewe lifetime productivity ledger — per-dam career table + born/weaned/raised chart** | EVSoft's per-doe "Litter Data Summary" (screenshot) lists every litter of a dam's career — date bred, sire, date born, #born, wean date, #weaned, #raised, #died, sex split — with a bar chart of born vs weaned vs sold per litter. The sheep translation is **the** meat-flock selection metric our flat `lambing_records_2026` list cannot answer: *lambs weaned per ewe, per year, over her lifetime* (and lamb-loss pattern). We already store the atoms (lambing records, offspring_ids, statuses); the gap is the per-dam pivot across years + the trend view. Feeds MCS-3's attention score (a ewe whose wean rate is collapsing deserves eyes) and the cull/keep decision with measured lifetime data. Pairs with MCS-17 (the pipeline writes the rows this view reads). **[Framing corrected 2026-08-12, operator: "Sheep don't have litters" — the unit is the *lambing* (1–3 lambs; prolificacy = single/twin/triplet, and `twin_of` already exists in the DB), not a transplanted litter concept. The lifetime-productivity idea survives; the vocabulary and the expected distributions (twinning rate, not litter size) are sheep's own.]** | `candidate` |
| MCS-19 | **Wool-vs-hair / shedding as a structured seasonal trait log — operator: "would be huge"** | Today coat type lives in prose on 3/276 sheep (`coat_observed`, e.g. "intermediate-to-wool-leaning… true type confirmed only after first peak-summer shed") and a manual "Shed Score 1–5" column on the ewe scorecard. The flock's stated goal is **hairy** — so this deserves the MCS-9 treatment: a structured per-animal **shed/coat observation log** (date + score 1–5 + observer note), appended each summer shed season, with the animal's current coat class *derived* from its latest scored observation instead of frozen prose. `coat_confidence` already admits the truth arrives seasonally — the log matches how the fact is actually learned. Feeds the hair% selection pipeline and MCS-22 mating prediction. Operator-named priority (2026-08-12). | `candidate` |
| MCS-20 | **Fat-tail phenotype + lineage tracking — operator: "would be huge"** | Exactly 1/276 sheep has a `fat_tail_observation` (FM, 50% Tunis — Tunis descends from fat-tailed Tunisian Barbary stock), yet fat-tail is a real heritable conformation trait relevant to the Awassi/Tunis genetics in the flock (and to carcass/market character). Row: a structured per-animal fat-tail phenotype score (even a simple none/intermediate/pronounced scale + date), plus lineage annotation of which lines carry it (Awassi, Tunis), so MCS-22 can predict it in planned matings instead of it living in one animal's prose note. Operator-named priority (2026-08-12). | `candidate` |
| MCS-21 | **Per-ewe milk records — operator: "would be huge" (CORRECTS my earlier dismissal)** | The EVSoft Sheep Register's "extensive record-keeping for milk production" was noted in the 2026-08-12 evaluation and **I marked it low-relevance ("meat/hair flock, not dairy") — the operator overruled that the same day**, and the data agrees with him: the flock carries **Awassi** (a premier fat-tailed *dairy* breed) and the breeding goals mention milk. Recording the correction rather than rewriting it — the dismissal was a wrong call, mine. Row: per-ewe milk records (date, yield, notes — MCS-12 quantity shape), which also feed **maternal milk ability** as a selection trait (lamb growth-to-weaning is substantially the dam's milk), tying into MCS-18's lifetime view even if no ewe is ever hand-milked for sale. | `candidate` |
| MCS-22 | **Mating outcome predictor — sire × dam → trait probabilities with a plain-language summary** | EVSoft's Genetics screen (screenshot) computes expected offspring for a proposed pairing — every outcome with its probability, sorted by frequency, capped by a human sentence ("expect the litter to be about 1/2 brokens, 1/4 solids, 1/4 charlies"). The sheep version predicts what this flock actually selects on: **coat (wool/hair/shed, MCS-19), fat-tail (MCS-20), scrapie genotype (MCS-15)**, color — from the sire/dam genotypes and phenotype records we hold. `breeding_projector.py` already does coat/composition projection, so this **extends existing machinery** rather than inventing it; the two lifts from EVSoft are (a) probabilities-by-frequency rather than a single predicted outcome, and (b) the plain-language line at the top. Serves the 7-pen pipeline's *pairing* decisions the way MCS-17 serves its *calendar*. | `candidate` |
| MCS-23 | **Ration evaluation against NRC requirements — feed *adequacy*, not just feed cost** | The Maryland Extension spreadsheet library (sheepandgoat.com, Susan Schoenian's program) centers on **ration evaluators**: given a class of animal (ewe late-gestation, lactating, growing lamb) and a proposed feed mix, check it against **NRC nutrient requirements** (2007 standards). Nothing in our ledger or DB touches nutritional adequacy — MCS-13 knows what feed *costs*, not whether the ewes are actually fed to requirement. It matters most exactly where the operator's priorities point: late-gestation/lactation nutrition drives lamb vigor and **milk** (MCS-21), and under-fed ewes read as parasite-suspect (FAMACHA/BCS decline) when the real cause is the ration — an MCS-8-style "disagreement is a signal" case. NRC requirements are public standards; the Extension spreadsheets are also directly usable as-is (their intended purpose). | `candidate` |
| MCS-24 | **"What weight to sell lambs" — marginal economics as a decision calculator** | A dedicated Extension spreadsheet answers one question: keep feeding this lamb or sell it now — marginal feed cost of the next pounds vs the price slide (heavier lambs often fetch *less per pound*). This is MCS-13's data sharpened into a **decision tool**: with a weight log (MCS-9-weight), feed costs (MCS-13), and a market price, the system can say "lamb X is past its optimum — sell" instead of leaving it to feel. Meat-flock relevant every single lamb crop. | `candidate` |
| MCS-25 | **Input inventory — what's in the barn cabinet, with expiry** | Livestocked tracks product inventories ("never in short supply"); we track *treatments given* but have no concept of the wormer/vaccine/feed **on hand** — quantity, expiry date, reorder point. Pairs tightly with MCS-7 (the withdrawal system already needs a drug table; inventory is the same table plus stock level) and MCS-11 (a "reorder Ivermectin" pending task when stock dips). Modest but real; dead simple once MCS-7's drug reference exists. | `candidate` |
| MCS-26 | **Comprehensive per-animal health & adverse-event log — "everything in between" (operator directive)** | Operator, 2026-08-12: *"track all medical things that we have to do to a given animal, from treating their feet for infection, to parasites, to fly strike, and predation, and everything in between."* Today `health{}` holds famacha_scores, treatments, vaccinations, notes — parasite-centric, and real events land in prose. Row: one **typed event log** per animal (the MCS-9 append-only shape) where every entry carries: **condition/event type** from a controlled vocabulary (hoof: foot rot/scald/abscess · parasites: internal/external · **fly strike** · **predation injury** · wound/laceration · mastitis · pneumonia/respiratory · pregnancy toxemia · pinkeye · soremouth/orf · bloat · heat stress · dystocia · other-with-note), **date · diagnosis (the *why* — the Record Book find) · treatment given (drug/dose/unit → feeds MCS-7 withdrawal) · body location · outcome/resolution date · observer**. Predation and injury are adverse *events*, not strictly medical — same log, typed differently, so flock-level questions ("how many fly-strike cases last summer? which pen? which coat types?") become queries. Feeds MCS-3 triage (open unresolved events = attention), MCS-11 (follow-up recheck as pending log), MCS-18 (lifetime health history per ewe), MCS-19 (fly strike correlates with coat/dags). Heat-stress typing would have captured baby-azure's death cause structurally instead of in prose. | `tracked` → `mcs-health-event-log` (P1) |
| MCS-27 | **Standard adjustment factors for lamb weights — birth type, rearing type, dam age (hair-specific tables)** | OSU Extension's Hair/Wool Sheep Record Keeping programs (AGEC fact sheets + Excel) center on **adjusted weaning weight**: raw weights corrected by standard factors for **age of dam, type of birth (single/twin/triplet), type of rearing, and sex** — with **hair sheep getting different factor tables than wool sheep**. Grounded gap in our EBV pipeline: `contemporary_group_key` = sex+birth-year+pen, and 60/120-day age adjustment exists, but **nothing corrects for birth/rearing type or dam age** — so a twin out of a yearling ewe is systematically under-scored on WWT/ADG against a single from a mature ewe, which distorts exactly the selection decisions the pipeline exists to make. Data partially present (`twin_of` on 5 records; lambing records carry lambs_born). Fix lives in `scripts/ebv/` (extend the adjustment before deviation-from-group), using published hair-sheep factors. | `candidate` |
| MCS-28 | **Intake quarantine records — biosecurity as a first-class record type** | farmers-library.com's 8-record framework includes one thing absent from our ledger and DB: **purchase & quarantine records** — seller/source, arrival date and observable arrival condition, transport, **quarantine location, planned review dates**, release. This is parasite-strategic for this flock, not bureaucracy: a purchased animal is the #1 way **anthelmintic-resistant worms** walk onto a farm (standard protocol: quarantine + aggressive multi-class deworming + FEC before pasture release), plus foot rot, soremouth, CL, OPP. The DB has `acquisition`/`arrival_date`/`breeder_provenance` on some records but no quarantine protocol or release gate. Shape: an intake record (MCS-26-typed events during quarantine + a pending release check, MCS-11) and a derived "in quarantine" state that MCS-9's movement log already expresses (quarantine pen = a location). Cheap once MCS-26 ships; high leverage per incident avoided. | `candidate` |
| MCS-29 | **Documented-loss records fit for indemnity claims — evidence at death time, money later** | `Matata-job/manyika-ranch` (a Tanzanian multi-camp cattle PWA) attaches **"Death & culling records + insurance claim fields"** — the death record is structured to carry the downstream financial claim from day one. The US translation is sharper: **USDA FSA's Livestock Indemnity Program (LIP)** pays for eligible losses to predation and adverse weather **including extreme heat** — both causes this flock has actually taken (predation is in the operator's MCS-26 directive; baby-azure died of heat 2026-06). LIP claims live or die on *documentation*: cause of death, date, evidence (photos, carcass, predation sign), and beginning/ending inventory. Row: when an MCS-26 event is typed `predation` or `heat stress` (or any death), the record prompts for the **evidence bundle at the time of loss** — photos, count, narrative, witness — so a claim window (LIP: notice within 30 days) is never missed for lack of paperwork. The DB's `photos` + `cause_of_death` + headcount are the atoms; the gap is the evidence prompt + claim-status field. Genuinely new angle: the only *revenue-recovery* row in the ledger. (hunch on program fit: operator should confirm LIP eligibility/AGI rules with FSA — the *record shape* is right regardless.) | `candidate` |
| MCS-30 | **FECRT / drench-check — measure whether each wormer still works on THIS farm** | `R-KenK/FECR` (R implementation of Cabaret & Berrag 2004 FECR methods) surfaced the standard the ledger was missing: the **Fecal Egg Count Reduction Test** — FEC at treatment, FEC again 10–14 days later, % reduction computed per **drug class**; reduction below ~95% means the farm's worm population is resistant to that drug. We already hold both halves (MCS-7 records the treatment+drug; MCS-8/`health` records FECs) — FECRT is *pairing them on purpose*: every deworming becomes a free resistance assay if a follow-up FEC lands in the window. The system's job: prompt the 10–14-day recheck (MCS-11 pending task), compute the reduction, and maintain a per-drug-class "still effective here?" table that the MCS-8 treat-decision reads. For a flock **breeding for parasite resistance in Florida**, knowing which chemistries still work is decision-critical — and it feeds MCS-28's quarantine release gate (arrival drench must be a class that works). Related: `juansvs/compFEC` (composite/pooled FEC sampling error) — pooled samples cut lab cost at known accuracy loss; noted for the protocol design. Concepts from published methods (public science); no code taken. | `candidate` |
| MCS-31 | **(hedged) Pedigree BLUP animal model — the someday-upgrade path for internal EBVs** | `radumust18/python-animal-td-model` (a BLUPF90 wrapper implementing the Animal Model for EBVs) names the professional-grade version of what `scripts/ebv/` approximates: the **animal model** solves all animals jointly using the full pedigree **relationship matrix**, so every relative's record informs every EBV — vs our deviation-from-contemporary-mean. Honest hedges: (a) NSIP already runs real BLUP for the 90 NSIP-anchored animals — the gap is only the un-anchored rest; (b) at ~276 head the accuracy gain over the current approach may not justify the machinery; (c) MCS-27's adjustment factors are the *prerequisite* either way (garbage-in otherwise). Recorded as the known upgrade path, deliberately not urged. Related grounding for **MCS-16**: `mastoffel/sheep_ID` (published Soay-sheep study, "genetic architecture and lifetime dynamics of **inbreeding depression** in a wild mammal") — inbreeding depression in sheep is real and lifetime-scale, which is the *why* behind MCS-16's F-coefficient serving the closed-loop policy. | `candidate` |
| MCS-32 | **Two-tier genetic trait card — Mendelian LETTERS + polygenic BARS, per-locus confidence (operator design question)** | Operator (2026-08-12): EVSoft tracks rabbit coat genetics as letters (aaB-C-DdE-) with offspring prediction — is anyone doing that for sheep, and can polygenic/multi-strategy traits go "on a chart anyway"? Research answer: **no open sheep software does this** (GitHub: games and a kitten-genetics app; the letters live in testing labs and registries, not flock tools) — but the design works if traits are split honestly into two tiers on one per-animal card. **Tier 1 — letters (true major loci, EVSoft-style genotype string + Punnett prediction in MCS-22):** scrapie PRNP 136/154/171 (commercial tests: Gene Check, Neogen, ~3–5 days — MCS-15); color loci (ASIP/Agouti, MC1R/Extension — sheep color genetics is characterized enough to letter, and genotypes can often be *inferred* from phenotype+pedigree without testing: a black lamb from two white parents proves both carry non-agouti); horns (RXFP2); **Booroola FecB** (+1 lamb/copy per copy — testable, and prolificacy-relevant to MCS-18); spider lamb (screening on some panels). Each locus carries a **source+confidence tag: tested / pedigree-inferred (probabilistic) / phenotype-constrained / unknown** — the DB's existing confidence discipline applied per-locus. **Tier 2 — bars (polygenic, no single "because"):** parasite resistance, shed/coat (MCS-19), fat-tail (MCS-20 — PDGFD/BMP2-region QTLs are published but there is no commercial test; phenotype score is the honest datum), foot health (a DQA2 marker test existed in NZ; mostly polygenic+environment → chart as event-history index from MCS-26), growth, maternal. Bar = EBV/index ± accuracy whisker + flock percentile — *you don't need the mechanism to select on the signal; that is what EBVs are for*. **The operator's multi-strategy insight becomes the chart's feature:** parasite resistance renders as SEPARATE bars per mechanism-proxy — FEC-based (resistance: kills worms) vs FAMACHA/anemia-based (resilience: tolerates them) — because an animal can be good at one and not the other, and that split is MCS-8's disagreement-signal expressed genetically. Unifies MCS-15/16/19/20/22/27/30 into one card; MCS-22's predictor reads Tier 1 as Punnett probabilities and Tier 2 as midparent EBVs. | `candidate` |
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
**[CORRECTED same day, 2026-08-12: operator — "Tracking milk … would be huge." The flock carries
Awassi (dairy) genetics and the breeding goals mention milk; the dismissal was my wrong call. See
MCS-21, which records the correction.]**
No code taken (proprietary).

**EVSoft screenshots addendum (2026-08-12, operator-supplied):** Ken shared five Rabbit Register
screens — his verdict "It's ugly. but it does a lot that we could learn from," and the screens
bear it out: ~35 years of breeder workflow encoded behind a dated skin; the *presentation* is not
the concept. New rows: **MCS-17** (Master Breeding List — per-mating pipeline with derived
palpate/due/wean/rebreed dates, pending rendered distinctly from done) and **MCS-18** (per-dam
lifetime litter summary + born/weaned/raised chart — the ewe-lifetime-productivity selection
metric). Reinforcements seen on screen, not re-rowed: inline per-row status glyphs (medical/photo/
winnings icons) on the herd roster → MCS-3's triage view; kinship color-coding (full sibs black,
half-by-sire blue, half-by-dam red) **plus a sibling-group total-sales stat** (economic value of a
LINE) → MCS-16 + MCS-13; per-animal sale entries with category pivot and a mileage (tax) tab →
MCS-13; multi-key sorted roster (ear#/name/cage/reg#) → MCS-5. Concepts read off screenshots of
proprietary software; nothing to copy but the ideas.

**EVSoft screenshots, second batch (2026-08-12, operator-supplied; operator framing: "looks aren't
everything… for rabbits this stuff works great. For sheep, I have no idea. We're doing our own
thing"):** Four more screens. (1) **TaskMaster chore calendar** — a month grid with a **live weather
overlay** (wunderground temps per day) beside per-animal treatment due-items ("Coccidia Trmnt",
"Ivomec Trmnt", "3 tasks due by Today"): that is MCS-1 (weather-aware parasite prompting) + MCS-2
(reminders where you look) + MCS-11 (task=record) **already composed in shipping 2014 rabbit
software** — independent validation that the combination is a real breeder workflow, not our
invention. (2) **Genetics Data screen** — sire×dam → offspring outcomes with probabilities sorted
by frequency and a plain-language topline → **MCS-22**. (3) **Pedigree tree** — sex-color-coded
nodes with per-ancestor stats and expandable winnings → MCS-16 (noting `inbreeding_coefficient`
already exists on 2/276 records — the extension is partially seeded). (4) **Animal detail screen**
— the genotype string lives ON the animal record (aaB-C-DdE-) → the exact shape MCS-15 wants for
scrapie codons; buyer/sale panel and weight-chart tab → MCS-13/MCS-9. Operator directives captured
from this batch: **milk, fat-tail genetics, wool-vs-hair are named-priority tracking dimensions**
(→ MCS-19/20/21) and **sheep don't have litters** (→ MCS-18 corrected to lambings/prolificacy).

**Proactive GitHub survey (2026-08-12, operator: "do some research on github looking for what we
are building"):** Six targeted queries across the ledger's axes (flock management · FAMACHA/FEC/
anthelmintic · lambing/breeding · EBV · grazing/pasture · scrapie/genotype). Findings: 
(a) the flock-management axis is **exhausted** — "sheep flock management record" returns exactly
one repo (flockbook, already ledgered), grazing-rotation returns one 2026 MVP stub; the general-
tool space really is as covered as the saturation note claimed. (b) The **academic/science corner
is where the commercial sweep had holes**: → **MCS-30** (FECRT drench-check, from R-KenK/FECR +
compFEC) and → **MCS-31** (BLUP animal model upgrade path, from radumust18/python-animal-td-model;
plus mastoffel/sheep_ID grounding MCS-16's inbreeding case with published Soay-sheep evidence).
(c) Everything else was name-collision noise (Lamb waves, LAMB optimizer, sheepdog storage, Cult
of the Lamb — and our old friend 羊了个羊 back in the results). Deep genomics (CNV callers, GTEx
pipelines, imputation) noted and deliberately left alone — research infrastructure, not flock
tooling, wrong scale for 276 head.

**`decided-no` (2026-08-12): dementatech "Smart Ranch" suite — title-only scaffolding, nothing to
mine.** Operator's URL (`dementatech/smart-ranch-web`) does not exist; the real family is four
repos — `smart-ranch` (web), `-mobile`, `-backend`, `-ai` — **all created the same day
(2026-01-12), all 0★, dead since mid-January**, plus a sibling `OWENALBERT606/smart-ranch-web`
(2026-01-13, same project family). Both READMEs read in full: one-line title stubs ("A Smart Ai
Powered Livestock Management System", "AI micro service powering the Smart Ranch Project") — no
features, no data model, no statement of what the AI does. There is literally nothing to evaluate
beyond the name. Not re-examined unless the project grows real documentation.
**[Verified 2026-08-12, after the operator challenged the depth of the first pass — fairly: the
first verdict rested on metadata + READMEs without opening the trees. Full shallow clones of
`smart-ranch`, `smart-ranch-ai`, and `smart-ranch-backend` (read-only, nothing executed): each is
ONE "Initial commit" containing exactly ONE file, README.md. The decided-no stands, now measured
rather than assumed.]**

**Three-repo evaluation (2026-08-12): manyika-ranch / Ranch-App-Capstone / castle-ranch-herddb.**
(1) `Matata-job/manyika-ranch` (TypeScript PWA, 2 weeks old, deployed, no license — concepts only):
a thoughtfully-scoped Tanzanian multi-camp **cattle** system. New → **MCS-29** (loss records
carrying insurance/indemnity evidence). Confirmations: camp movements **with audit trail** → MCS-9;
eartag+photo+pedigree registry → MCS-5/16; vaccination schedules → MCS-11/26; offline PWA with
sync queue → the offline angle noted since the first sweep; role-based access (Owner/Manager/Vet/
Clerk…) → n/a at our scale but the *Vet role* idea rhymes with MCS-26's professional-contact field.
(2) `ttyczka/Ranch-App-Capstone` (C#, MIT, 0★, dead Dec 2021): **metadata-only** — README and tree
unreachable without unauthenticated-API workarounds; a 6-week student capstone doesn't warrant
them. Not assessed beyond that; recorded so the gap is visible, `decided-no` on effort grounds.
(3) `dlhiwig/castle-ranch-herddb` (JS, no license, 0★ — repo's entire life was **4 minutes** on
2026-04-13): README describes an AI-assisted staff portal (Anthropic API, "controlled writes for
supported actions", rule-based fallback). No new wheat — **this household already runs the
stronger version of that exact idea** (agents doing governed writes to the flock DB under Sophos,
vs. their "controlled writes"); its `destiny` field (intended disposition per animal) is already
covered by our `conditional_cull`/`do_not_sell`/`pet`/`scheduled_auction` fields. `decided-no`.

**`decided-no` (2026-08-12): `ardywibowo/RanchHand` — a one-day 2017 student demo, no transferable
wheat.** "TI Livestock Monitoring": MATLAB experiments in sensor placement and **noisy
trilateration** (radio-positioning of cattle) + a web app with test data. Created and last pushed
the same day (2017-08-30), 2★, no license, no health/behavior signals, cattle-only. The one
concept it gestures at — **automated position sensing** — deliberately does *not* earn a row for
this operation: a 9-pen flock's location truth is pen membership, and a pen move is a husbandry
*event* recorded at the gate (MCS-9), not a telemetry problem; hardware data-acquisition at the
chute (EID readers, scales) is already noted under MCS-5/Livestocked. If the operation ever runs
open range or virtual fencing, revisit — that would be commercial GPS-collar tech, not this repo.
No code taken (unlicensed, and nothing to take).

**Ranch Manager / Carnelena / farmers-library evaluation (2026-08-12):** 
(1) **ranchmanageropen.com** (Ranch Manager sheep edition — commercial, concepts only). Operator
called it comprehensive; it is — but almost everything maps to existing rows: scrapie ID on the
animal → MCS-15's neighborhood (note the distinction: this is the **scrapie flock/premise tag ID**,
a regulatory identifier, vs MCS-15's *genotype* — both belong on the record); treatments/vet
visits → MCS-26; movement tracking → MCS-9; shearing + dairy production → MCS-19/MCS-21; P&L →
MCS-13; calendar+reminders → MCS-11/MCS-2; photos on pedigree → MCS-16 (DB already has `photos`).
**One real sharpening kept → MCS-17:** it computes due dates from "**pasture or recorded
breeding**" — i.e., when the service date is unknown (pasture/pen exposure), the due date is a
**window derived from ram-in/ram-out dates**, not a point. Our pen-breeding reality is exactly
that; MCS-17's pipeline must accept an exposure *interval* and emit a lambing *watch window*.
(2) **carnelena.com** sheep template — **403/blocked**, not evaluated; recorded so nobody assumes
it was. (3) **farmers-library.com** — an 8-record-type framework; mostly confirms (master list w/
exit reason → status/cause_of_death; exception-based daily observations w/ observer + recheck →
MCS-26/MCS-3; pasture+feed records → MCS-9/MCS-23; expenses/sales → MCS-13). **New → MCS-28**
(quarantine/intake biosecurity). **One epistemic refinement adopted into MCS-26:** record
**observable signs at observation time, diagnosis only when confirmed** — "no unconfirmed
diagnoses, no invented dosages." MCS-26's diagnosis field therefore splits: `signs` (what was
seen) vs `diagnosis` (confirmed, with how) — matching the DB's existing confidence-field
discipline. Their line "each entry depends on knowing exactly which animal" is MCS-5's case made
independently.

**OSU Extension sheep pages evaluation (2026-08-12):** Operator pointed at
`extension.okstate.edu/topics/…/sheep` (two pages). **Honest access limit:** OSU's site sits
behind a Cloudflare challenge that blocked both the fetcher and curl; I did not fight the bot
guard. Evaluated via search-indexed content instead — enough for the substance, but the fact
sheets were not read in full. The **two software items** are OSU's *Hair Sheep* and *Wool Sheep
Record Keeping Software* (free Excel workbooks + AGEC fact-sheet guides; lamb/ram/ewe tabs,
ewe age auto-derived, protected formula cells). Their core value → **MCS-27** (standard
adjustment factors — dam age, birth type, rearing type, sex; hair-specific tables), a grounded
gap in our `scripts/ebv/` pipeline. Also on the pages: *Sheep Health and Management* (select/cull
on production records — confirms MCS-18), *A Planning Calendar for Sheep Herd Health and
Management* (health tasks keyed to production stages — the MCS-17 pipeline + MCS-11 pending-task
shape as an annual calendar; contents unfetched, noted not mined), a printable *Ewe Production
Record* and *AGEC-335 Lamb Record*. The operator's same-message medical directive became
**MCS-26** (typed health & adverse-event log), registered directly to HLS.

**Record-book / FarmKeep / FlockFiler evaluation (2026-08-12):** Three operator-pointed sources;
verdict: **mostly confirmation, thin new wheat — a saturation signal.** 
(1) **mamaonthehomestead.com "Sheep Record Book"** (free printable PDF; extracted all 9 forms).
Paper forms show what a working shepherd actually writes: identification w/ photo+sire+dam,
medical (DATE·ID·**DIAGNOSIS**·MEDICATION·DOSAGE·NOTES), breeding (expected due vs actual lambing
→ MCS-17's derivation in paper form), lambing (per-lamb IDs, sex, **birth weight**), wool
production, additions+losses (headcount — DB already keeps this), sales (price + **customer
contact**). One small named idea adopted into MCS-7/MCS-8's orbit rather than a new row: **record
the DIAGNOSIS, not just the treatment** — our `health.treatments` captures what was given; a
diagnosis field captures *why*, which is exactly where MCS-8's "anemic but low FEC → not
parasites" conclusion needs to live. Customer-contact-on-sale reinforces MCS-13.
(2) **farmkeep.com free templates** (9): livestock/breeding/health/production/expense/feeding all
confirm existing rows; the **inventory template's shape** — beginning balance · purchased · used/
sold · ending balance — sharpens MCS-25 into the derived-state pattern (stock level is *derived*
from transactions, MCS-9's rule applied to the cabinet). Incubation template off-species.
(3) **flockfiler.com** (dedicated sheep software, Lite $50 / Pro $296, Win+Mac): its public pages
document only — automatic **pedigree calculation** (MCS-16 confirmed by a sheep-specific tool),
search across everything, **full import/export of ALL data** (data-sovereignty; confirms our
local-JSON-first posture, same point EVSoft makes), Pro = analysis/optimization tier. The pages do
NOT document FAMACHA/NSIP/scrapie specifics; deeper claims would be guesses and are not made.
**Meta-observation for the operator:** three sources, zero new numbered rows — the last several
sources now confirm the ledger rather than extend it. The domain's tool-space is approaching
covered; remaining value is in *building* the tracked rows, not surveying more tools. Two operator-pointed sources. 
**`livestocked.com`** — commercial multi-species livestock SaaS (cattle→chickens; Windows/Android/
iOS/Mac, offline-capable). Mostly *confirms* existing rows: pasture movements → MCS-9; tasks/to-dos
→ MCS-11; integrated ag accounting → MCS-13; scale/drafter/tag-reader hardware (Yardflow) → MCS-5's
EID angle; stocking-rate + head-count forecasting → territory of the repo's existing
`pasture-planner` skill (noted as a forecasting extension there, not a new row). One genuinely new
concept → **MCS-25** (input inventory). Proprietary SaaS; concepts only.
**`sheepandgoat.com/spreadsheets`** — University of Maryland Extension (Susan Schoenian), ~23 free
spreadsheets. The richest *practical* source of the sweep: unlike code repos these are **directly
usable as tools** (that is their intended use; some are password-protected to preserve formulas —
contact listed). New concepts → **MCS-23** (NRC ration evaluation — feed adequacy) and **MCS-24**
(optimal sell-weight marginal economics). Reinforcements: enterprise budgets + Schedule F → whole-
operation extension of MCS-13; marketing-alternatives comparison → MCS-13. Also noted:
**BioWorma cost spreadsheet** — a pointer to *biological* larval control (Duddingtonia flagrans
fungus fed daily; traps strongyle larvae in manure), a parasite-management intervention absent from
our MCS-1/MCS-8 thinking and directly relevant to Florida Haemonchus pressure; the husbandry
decision is the operator's, the costing tool exists. NRC math is public standards; no lift issues.

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
