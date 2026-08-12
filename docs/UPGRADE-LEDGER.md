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

**Provenance note (2026-08-11):** these two rows are the *only* survivors of evaluating
`brechy/homesteady-landing`, `thomaselucas/homesteady`, and `entro-afk/homesteady` at the
operator's request. Verdict on all three: coincidental name collision, none related to each
other, none a tool or component for this project. What survived is two feature *concepts*, not
software to integrate. Concepts only; nothing installed; all three are unlicensed (all-rights-
reserved by default), so there is no reuse grant even where a fragment looked handy.

**Soli Deo Gloria.**
