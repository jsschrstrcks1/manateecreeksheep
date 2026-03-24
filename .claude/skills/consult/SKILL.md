---
name: consult
description: "Quick multi-LLM second opinion. Sends a single prompt to GPT, Gemini, or Grok with a role-based system prompt and returns structured feedback."
---

# Consult — Quick Second Opinion

*One model. One question. Structured feedback.*

## Usage

```
/consult <model> <role> "prompt text"
```

### Models
- **gpt** — OpenAI GPT (strong at structure, planning)
- **gemini** — Google Gemini (strong at expansion, cross-references)
- **grok** — xAI Grok (strong at challenge, adversarial thinking)

### Roles
- **challenge** — Push back on assumptions, surface weak reasoning
- **expand** — Add context, cross-references, historical background
- **structure** — Review logical flow and organization
- **critique** — Evaluate accuracy, completeness, clarity
- **plan** — Produce structured plans with steps and risks
- **safety** — Flag risks, errors, unsafe recommendations
- **freestyle** — General-purpose response

---

## Examples

```
/consult gpt plan "Review this breeding plan for the spring Katahdin pairings"
/consult gemini expand "What veterinary research supports FAMACHA scoring for hair sheep in Florida?"
/consult grok challenge "We're prioritizing parasite resistance over growth rate. What are we missing?"
```

---

## Backend Invocation

```bash
pip3 install -q -r /home/user/ken/orchestrator/requirements.txt
python3 /home/user/ken/orchestrator/consult.py <model> <role> "prompt text"
```

**Output:** JSON response to stdout with keys: `analysis`, `proposed_update`, `risks`, `confidence`
**Usage stats:** Printed to stderr (model, tokens, cost)

---

## Context Boundaries

### SEND
- Anonymized flock data, breeding objectives, trait scores, health summaries

### NEVER SEND
- Financial records, location details beyond "Florida"

---

## After Receiving Feedback

1. **Evaluate** — External feedback is advisory only. Claude validates all plans.
2. **Check claims** — If the response includes `claims`, verify against flock records.
3. **Apply careful-not-clever** — All modifications from consultation feedback must be verified.
