---
name: image-transcription
description: Transcribe sheep records from spiral notebook photos and handwritten notes. Handle extraction of treatment data, measurements, pen assignments, and sheep identification from notebook page images.
---

# Image Transcription for Sheep Records

## Core Principles

1. **Accuracy Over Speed** — One correct record is worth more than ten guessed ones
2. **Source Fidelity** — Record exactly what the image shows, then normalize
3. **Honesty About Uncertainty** — Use `[UNCLEAR]` for anything you can't confidently read

## Pre-Transcription Checklist

- [ ] Image is from `data/processed/` directory (≤1800px)
- [ ] Identify the type: spiral notebook note, handwritten card, sheep photo, ear tag close-up
- [ ] Note the date if visible (phone notes show timestamps)

## Image Types

### Phone App Notes (PNG files, IMG_8616–8643)
- Treatment records with FAMACHA scores
- Measurement records (height, girth)
- Pen assignment lists
- Sick sheep records with dates
- Health notes and vaccination records

### Handwritten Notebook Pages (JPG files, IMG_8560–8615)
- Detailed sheep check records
- Close-up photos of individual sheep with ear tags
- Breed identification notes
- Lambing records

## Transcription Format

For each sheep data point found, record:
- **Source image**: IMG_####
- **Data type**: treatment | measurement | pen_assignment | health_note | lambing | identification
- **Date**: if visible in the image
- **Content**: exact transcription of the text/data
- **Normalized**: cleaned version for the database

## Struck-Through Text

Text with strikethrough in the notebook generally means:
- The animal is **deceased** or **sold**
- The treatment was **not given** (e.g., "no treat" struck through)
- The entry was **corrected** elsewhere

Always note strikethrough and interpret carefully.

## MUST DO

- Use `data/processed/*.jpeg` versions only
- Note which image each data point comes from
- Preserve original spellings in notes field
- Mark uncertain readings as `[UNCLEAR]`

## MUST NOT

- Read original images (>2000px)
- Guess unclear handwriting
- Invent data not visible in the image
- Discard information because it seems contradictory (record it and flag it)
