---
name: google-sheets-sync
description: "Bridges the Google Sheets spreadsheet (primary flock data source) with local flock_database.json. Eliminates manual export. Validates changes against careful-not-clever principles."
version: 1.0.0
---

# Google Sheets Sync

> *"The LORD is my shepherd; I shall not want."* — Psalm 23:1

## Purpose

The flock's primary data lives in a Google Sheets spreadsheet. This skill bridges the gap between the live spreadsheet and the local `data/flock_database.json`, eliminating manual export and ensuring data stays current.

## Setup (One-Time)

### 1. Install Google Sheets MCP Server

```bash
claude mcp add google-sheets -- uvx mcp-google-sheets@latest
```

### 2. Configure Google Cloud Service Account

The project already has: `GOOGLE_CLOUD_PROJECT=constant-cubist-471700-e1`

Steps:
1. Go to Google Cloud Console → APIs & Services → Enable Google Sheets API
2. Create a service account (or use existing one)
3. Download the service account JSON key
4. Set environment variable: `GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json`
5. Share the flock spreadsheet with the service account's email address

### 3. Verify Connection

```bash
claude mcp list  # Should show google-sheets as Connected
```

In a Claude Code session, type `/mcp` to see active servers.

## Sync Workflow

### `/sync` — Full Sync

1. **Read** — Pull current data from Google Sheets
2. **Compare** — Diff against `data/flock_database.json`
3. **Report** — Show changes found:
   - New animals added
   - Updated records (pen changes, health updates, breeding records)
   - Deleted/sold/deceased animals
4. **Validate** — Check each change against careful-not-clever:
   - Does this contradict spiral notebook images? → BLOCK
   - Is this a calculated field (breed %, resistance score)? → SKIP (recalculate locally)
   - Is this marked [UNCLEAR] locally? → FLAG for manual review
5. **Apply** — Write verified changes to `flock_database.json`
6. **Verify** — Run `python3 scripts/validate_flock.py`

### What to Sync

| Data | Direction | Notes |
|------|-----------|-------|
| Animal records (tag, name, breed, DOB, status) | Sheets → Local | Primary source |
| Pen assignments | Sheets → Local | Changes frequently |
| Breeding records | Sheets → Local | Seasonal updates |
| Health records (FAMACHA, treatments) | Sheets → Local | Most frequent changes |
| Pedigree (sire/dam) | Sheets → Local | Rarely changes |

### What NOT to Auto-Sync

| Data | Why |
|------|-----|
| Anything contradicting spiral notebook images | Notebook is highest authority (Priority 1) |
| Breed composition percentages | Calculated from parents — recalculate locally |
| Parasite resistance scores | Calculated by `scripts/parasite_resistance.py` |
| [UNCLEAR] items | Need manual resolution, not overwrite |
| Deceased animal details | Preserve local historical data |

## Conflict Resolution

When Sheets and local data disagree:

1. **Sheets wins** for: pen assignments, current health status, recent treatments
2. **Local wins** for: historical data, pedigree verified against notebook, breed math
3. **Flag for human** for: conflicting pedigree data, suspicious tag numbers, any animal not in the notebook

## Sync Report Format

```
## Flock Sync Report — [date]

### Changes Found
| Animal | Field | Sheets Value | Local Value | Action |
|--------|-------|-------------|-------------|--------|
| Eclipse | pen | 1 | 3 | APPLY (Sheets wins) |
| NoriSon | sire | unknown | Nori | KEEP LOCAL (notebook verified) |

### Summary
- Applied: [N] changes
- Kept local: [N] items
- Flagged for review: [N] items
- Validation: [pass/fail]
```

## Integration

- **careful-not-clever** — every sync change validated before applying
- **flock-validation** — runs after sync to verify database integrity
- **health-tracker** — new FAMACHA data feeds health trends
- **breeding-advisor** — updated pen assignments affect breeding recommendations
- **cognitive-memory** — encode sync decisions as protected memories
- **image-transcription** — notebook images override Sheets when conflicting

---

*Soli Deo Gloria* — Accurate records are faithful stewardship.
