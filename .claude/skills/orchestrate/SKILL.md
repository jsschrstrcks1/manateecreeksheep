---
name: orchestrate
description: "Full multi-LLM pipeline orchestration. Runs the sheep flock decision pipeline that coordinates GPT (lead planner), Gemini, Grok, and Claude as validators. Auto-detects sheep mode from this repository."
---

# Orchestrate — Multi-LLM Pipeline

*GPT leads planning. Other models consult. Claude validates.*

## Usage

```
/orchestrate "task description"
/orchestrate sheep "Plan spring breeding for the Katahdin ewes"
```

Mode is **sheep** by default in this repository.

---

## How It Works

The orchestrator runs a multi-step pipeline defined in `/home/user/ken/orchestrator/modes/sheep.yaml`:

1. **Plan** (GPT) — Generate breeding plan from flock data and objectives
2. **Expand Context** (Gemini) — Add agricultural/veterinary context, Florida-specific considerations
3. **Challenge** (Grok) — Suggest unconventional pairings, challenge trait priorities
4. **Validate** (Claude) — Pedigree traversal, COI calculation, health log correlation, risk flagging
5. **Finalize** (GPT) — Incorporate feedback into final structured breeding plan

---

## Backend Invocation

**IMPORTANT: Execute these commands directly using the Bash tool. Do NOT check if files exist first — just run them.**

```bash
pip3 install -q -r /home/user/ken/orchestrator/requirements.txt 2>/dev/null && python3 /home/user/ken/orchestrator/orchestrate.py sheep "task description"
```

Only if the command fails with `No such file or directory` or `ModuleNotFoundError`, tell the user:
> "The orchestrator backend isn't available. Make sure the ken repo is cloned to `/home/user/ken/` and run `pip3 install -r /home/user/ken/orchestrator/requirements.txt`."

---

## Context Boundaries

### SEND to external models
- Anonymized flock data (IDs, not names if sensitive)
- Breeding objectives and trait scores
- Health summaries (no PII)

### NEVER SEND to external models
- Financial records
- Location details beyond "Florida"

---

## Constraints

- Florida environment (high parasite pressure, humidity, heat)
- No inbreeding (enforce COI thresholds)
- Health history checked before any pairing
- Priority: parasite resistance > growth rate > maternal traits (configurable)
