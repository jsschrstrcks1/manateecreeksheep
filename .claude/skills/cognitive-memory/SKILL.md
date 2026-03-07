---
name: cognitive-memory
description: Cross-repository cognitive memory system. Persists knowledge across sessions using encode, consolidate, recall, extract, and forget operations. Memory is cognition, not storage.
trigger:
  - keyword: [memory, remember, recall, forget, "what do we know", "last session", "previous session", "what was", "do you remember"]
  - intent: ["recalling past context", "storing new knowledge", "resolving contradictions", "session continuity"]
  - event: session_start
priority: high
---

# Cognitive Memory System

> Memory as stewardship: what we remember shapes how we serve.

## Overview

This skill provides persistent cognitive memory across Claude Code sessions. It is NOT a database — it is a reasoning layer that encodes selectively, consolidates contradictions, recalls adaptively, and forgets intentionally.

**Memory store:** `/home/user/.memory/memory.json`
**Configuration:** `/home/user/.memory/memory-config.json`
**Operations script:** `/home/user/.memory/memory_ops.py`
**Archive:** `/home/user/.memory/archive/`

## Session Start Protocol

At the beginning of every session, recall relevant memories for this repository:

```bash
python3 /home/user/.memory/memory_ops.py recall "" --scope /manateecreeksheep --limit 10
python3 /home/user/.memory/memory_ops.py tree /manateecreeksheep
```

Present a brief summary to the user:
- Recent changes and current state
- Open questions or low-confidence memories
- Any contradictions flagged but not yet resolved

## Five Cognitive Operations

### 1. REMEMBER — When you learn something new

After transcribing notebook pages, updating records, or when the user states a new fact:

```bash
python3 /home/user/.memory/memory_ops.py remember "FACT" \
  --scope /manateecreeksheep/DOMAIN/SUBDOMAIN \
  --categories CAT1 CAT2 \
  --importance 0.0-1.0 \
  --confidence high|medium|low \
  --source-type notebook|spreadsheet|session|user \
  --source-ref "SOURCE"
```

**Importance guidelines for this repo:**
- 0.9: Breeding decisions, selection priorities, pedigree corrections
- 0.8: Pen assignments, ram assignments, health alerts
- 0.7: FAMACHA scores, treatment records, lamb observations
- 0.5: General notes, routine observations
- 0.3: Temporary states, transient observations

**Scope hierarchy for this repo:**
```
/manateecreeksheep
  /pens          — pen assignments, pen moves
    /pen-1 through /pen-6, /goose-pen
  /breeding      — breeding program, genetics
    /genetics    — breed composition, resistance traits
    /awassi      — Awassi-specific genetics
  /health        — FAMACHA scores, treatments, weak resistance
    /{sheep-id}  — per-animal health records
  /lambing       — lambing season records
    /2026        — 2026 season
  /identity      — aliases, tag numbers, name corrections
```

### 2. RECALL — When you need past context

Before making assertions about flock state, check memory:

```bash
python3 /home/user/.memory/memory_ops.py recall "QUERY" --scope /manateecreeksheep
```

**Always recall before:**
- Stating pen assignments ("Which pen is X in?")
- Reporting health history ("How is X doing?")
- Making breeding recommendations
- Answering "what do we know about..."

**Trust but verify:** If recall confidence is "low", say so. Don't present uncertain memories as facts.

### 3. EXTRACT — After notebook transcription or large outputs

When transcribing a notebook page or processing a large block of information, mentally decompose it into atomic facts. Each fact gets its own REMEMBER call.

**Example flow:**
1. Transcribe notebook image → get block of text
2. Identify individual facts (pen moves, health scores, treatments, lamb observations)
3. REMEMBER each fact separately with appropriate scope, importance, and confidence
4. Report any contradictions found during consolidation

### 4. TREE — To see what we know

```bash
python3 /home/user/.memory/memory_ops.py tree /manateecreeksheep
```

Use this to identify gaps in knowledge or to give the user an overview.

### 5. FORGET — To keep memory useful

```bash
# Dry run first
python3 /home/user/.memory/memory_ops.py forget --scope /manateecreeksheep/pens --older-than 60 --dry-run

# Then archive
python3 /home/user/.memory/memory_ops.py forget --scope /manateecreeksheep/pens --older-than 60
```

**Auto-forget candidates:**
- Pen assignments older than 60 days (pens change frequently)
- Superseded memories older than 30 days
- Low-importance memories never accessed

**Never forget:**
- Breeding decisions and pedigree facts (importance >= 0.9)
- The careful-not-clever principle
- Source hierarchy rules

## Integration with Existing Skills

This skill works alongside, not instead of, existing skills:

- **careful-not-clever**: Memory confidence levels inherit this philosophy. Low-confidence memories are flagged, never presented as certain.
- **flock-validation**: After REMEMBER operations that change flock data, validation still runs.
- **image-transcription**: After transcribing a notebook page, use EXTRACT to decompose into atomic memories.

## Consolidation Rules

When REMEMBER detects a similar existing memory:

1. **Same scope, higher-priority source** → Supersede the old memory
2. **Same scope, same-priority source, more recent** → Supersede
3. **Same scope, conflicting content, both low confidence** → Flag for human review, don't auto-resolve
4. **Different scope, similar content** → Both coexist (cross-domain knowledge is fine)

## What Memory Is NOT

- Memory does NOT replace the flock database (`data/flock_database.json`)
- Memory does NOT override primary sources (spiral notebook wins)
- Memory does NOT store raw data — it stores *conclusions about* data
- Memory does NOT act autonomously — you decide when to remember and recall

## Soli Deo Gloria

Careful, not clever. What we remember matters. What we forget matters too.
