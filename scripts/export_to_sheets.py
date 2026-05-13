#!/usr/bin/env python3
"""
export_to_sheets.py — Generate TSV files from flock_database.json for Google Sheets import.

Produces tab-separated files that can be pasted directly into Google Sheets tabs.
Also generates an Apps Script (.gs) file that can auto-create/update sheets programmatically.

Usage:
    python3 scripts/export_to_sheets.py              # Generate all TSV + Apps Script
    python3 scripts/export_to_sheets.py --tsv-only    # Just TSV files
    python3 scripts/export_to_sheets.py --gs-only     # Just Apps Script

Output: data/sheets_export/
"""

import json
import os
import sys
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(SCRIPT_DIR)
DB_PATH = os.path.join(REPO_DIR, "data", "flock_database.json")
BREED_PATH = os.path.join(REPO_DIR, "data", "breed_reference.json")
OUT_DIR = os.path.join(REPO_DIR, "data", "sheets_export")

os.makedirs(OUT_DIR, exist_ok=True)


def gs_safe(text, max_len=None):
    """Sanitize a string for embedding in a JavaScript single-quoted string.
    Removes single quotes, backslashes, and non-ASCII characters to avoid any escaping issues."""
    s = str(text) if text is not None else ""
    s = s.replace("\\", "").replace("'", "").replace("\n", " ").replace("\r", "")
    # Replace common Unicode with ASCII equivalents
    s = s.replace("\u2014", " - ").replace("\u2013", "-")  # em-dash, en-dash
    s = s.replace("\u2192", "->").replace("\u2190", "<-")  # arrows
    s = s.replace("\u00D7", "x")  # multiplication sign
    s = s.replace("\u2260", "!=")  # not-equals
    s = s.replace("\u2265", ">=").replace("\u2264", "<=")  # >=, <=
    # Strip any remaining non-ASCII
    s = s.encode("ascii", "ignore").decode("ascii")
    if max_len:
        s = s[:max_len]
    return s


def load_data():
    with open(DB_PATH) as f:
        db = json.load(f)
    breeds = {}
    if os.path.exists(BREED_PATH):
        with open(BREED_PATH) as f:
            breeds = json.load(f)
    return db, breeds


def write_tsv(filename, headers, rows):
    path = os.path.join(OUT_DIR, filename)
    with open(path, "w") as f:
        f.write("\t".join(headers) + "\n")
        for row in rows:
            f.write("\t".join(str(v) for v in row) + "\n")
    print(f"  {filename}: {len(rows)} rows")


def export_pipeline_overview(db):
    policy = db.get("breeding_policy", {})
    pipeline = policy.get("pipeline", {})
    stages = pipeline.get("stages", {})

    headers = [
        "Stage", "Pen", "Size", "Location", "Ram ID", "Ram Name", "Ram Weight",
        "Ram Hair %", "Ram Coat Observed", "Ewe Count",
        "FAMACHA Criteria", "FEC Criteria", "Shed Criteria", "Shelter", "Notes"
    ]
    rows = []
    alive = {s["id"]: s for s in db["sheep"] if s.get("status") == "alive"}

    for pen_name, info in stages.items():
        ram_id = info.get("ram", "")
        ram = alive.get(ram_id, {})
        ram_name = ram.get("name", ram_id)
        ram_wt = ram.get("weight_lbs", "?")
        ram_bc = ram.get("breed_composition", {})
        ram_hair = ram_bc.get("hair_percentage", "?")
        ram_coat = ram_bc.get("coat_observed", ram_bc.get("coat_prediction", "?"))

        # Count ewes in this pen
        ewe_count = sum(
            1 for s in db["sheep"]
            if s.get("status") == "alive"
            and s.get("pen") == pen_name
            and s.get("sex") in ("ewe", "ewe_lamb")
        )

        adv = info.get("advancement_criteria", {})
        rows.append([
            info.get("stage", ""),
            pen_name,
            info.get("size", ""),
            info.get("location", ""),
            ram_id,
            ram_name,
            ram_wt,
            ram_hair,
            ram_coat,
            ewe_count,
            adv.get("famacha", ""),
            adv.get("fec_epg", ""),
            adv.get("shedding_pct", ""),
            info.get("shelter", ""),
            info.get("ram_notes", "")[:100],
        ])

    write_tsv("01_pipeline_overview.tsv", headers, rows)


def export_active_flock(db):
    headers = [
        "Pen", "Stage", "Name", "ID", "Tag", "Sex", "Weight (lbs)",
        "Breed Primary", "Hair %", "Wool %", "Coat Observed", "Coat Predicted",
        "Sire ID", "Dam ID",
        "Weak Parasites", "Last FAMACHA", "Status", "Notes"
    ]
    rows = []

    policy = db.get("breeding_policy", {})
    pipeline = policy.get("pipeline", {})
    stages = pipeline.get("stages", {})
    pen_to_stage = {pen: info.get("stage", "?") for pen, info in stages.items()}

    for s in sorted(db["sheep"], key=lambda x: (
        str(pen_to_stage.get(x.get("pen", ""), 99)),
        str(x.get("pen", "zzz")),
        0 if x.get("sex") in ("ram", "ram_lamb") else 1,
        str(x.get("name", ""))
    )):
        if s.get("status") != "alive":
            continue

        bc = s.get("breed_composition", {})
        health = s.get("health", {})
        fam_scores = health.get("famacha_scores", health.get("famacha_history", []))
        last_fam = ""
        if isinstance(fam_scores, list) and fam_scores:
            last = fam_scores[-1]
            if isinstance(last, dict):
                last_fam = f'{last.get("score", "?")} ({last.get("date", "?")})'
            else:
                last_fam = str(last)

        rows.append([
            s.get("pen", "?"),
            pen_to_stage.get(s.get("pen", ""), "?"),
            s.get("name", ""),
            s.get("id", ""),
            s.get("tag", ""),
            s.get("sex", ""),
            s.get("weight_lbs", ""),
            bc.get("primary", ""),
            bc.get("hair_percentage", ""),
            bc.get("wool_percentage", ""),
            bc.get("coat_observed", ""),
            bc.get("coat_prediction", ""),
            s.get("sire_id", ""),
            s.get("dam_id", ""),
            "YES" if health.get("weak_resistance") else "",
            last_fam,
            s.get("status", ""),
            (s.get("notes", "") or "")[:120],
        ])

    write_tsv("02_active_flock.tsv", headers, rows)


def export_breeding_policy(db):
    policy = db.get("breeding_policy", {})
    headers = ["Category", "Item", "Details"]
    rows = []

    # Selection hierarchy
    for h in policy.get("selection_hierarchy", []):
        rows.append(["Selection Hierarchy", f'#{h["rank"]} {h["trait"]}', h["description"]])

    rows.append(["", "", ""])

    # Hard lessons
    for lesson in policy.get("hard_lessons", []):
        rows.append(["Hard Lesson", "", lesson])

    rows.append(["", "", ""])

    # Pipeline info
    pipe = policy.get("pipeline", {})
    rows.append(["Pipeline", "Target Animal", pipe.get("target_animal", "")])
    rows.append(["Pipeline", "Inbreeding Policy", pipe.get("inbreeding_policy", "")])
    rows.append(["Pipeline", "Awassi Separate", str(pipe.get("awassi_separate", ""))])
    rows.append(["Pipeline", "Key Insight", pipe.get("key_insight", "")])

    rows.append(["", "", ""])

    # Stress test
    st = policy.get("stress_test", {})
    if st:
        for fix in st.get("critical_fixes_applied", []):
            rows.append(["Stress Test Fix", st.get("date", ""), fix])
        for vuln in st.get("known_vulnerabilities", []):
            rows.append(["Known Vulnerability", "", vuln])

    write_tsv("03_breeding_policy.tsv", headers, rows)


def export_breed_reference(breeds):
    headers = ["Breed", "Type (hair/wool)", "Avg Ewe Wt (lbs)", "Avg Ram Wt (lbs)", "Notes"]
    rows = []
    for breed, info in sorted(breeds.items()):
        rows.append([
            breed,
            info.get("type", ""),
            info.get("avg_ewe_wt", ""),
            info.get("avg_ram_wt", ""),
            info.get("notes", "")[:150],
        ])
    write_tsv("04_breed_reference.tsv", headers, rows)


def export_annual_eval_template(db, year=None):
    """Export annual eval TSVs from the persisted per-year JSONs.

    System of record: data/annual_evals/<year>_(ram|ewe)_eval.json.
    Run scripts/run_annual_eval.py to (re)generate or merge the JSONs against
    the current flock_database.json before re-exporting. Owner-typed scores
    are preserved across re-runs.

    Closes L7 from MANATEE_CREEK_REDESIGN_PLAN.md.
    """
    from datetime import datetime
    from pathlib import Path

    if year is None:
        year = datetime.now().year

    repo_root = Path(__file__).parent.parent
    ram_json = repo_root / "data" / "annual_evals" / f"{year}_ram_eval.json"
    ewe_json = repo_root / "data" / "annual_evals" / f"{year}_ewe_eval.json"

    if not ram_json.exists() or not ewe_json.exists():
        print(f"  [warn] {year} eval JSONs missing — run: python3 scripts/run_annual_eval.py --year {year}")
        return

    # Ram TSV — columns mirror RAM_SCORE_KEYS in run_annual_eval.py
    with open(ram_json) as f:
        ram_doc = json.load(f)
    headers = [
        "Ram Name", "Ram ID", "Pen", "Stage", "Status",
        "Offspring Avg FAMACHA (40%)", "Offspring Shed % (25%)",
        "Offspring Avg Daily Gain (15%)", "Conception Rate (10%)",
        "Offspring Survival 90d (10%)",
        "TOTAL SCORE", "ACTION (Keep/Demote/Replace/Cull)"
    ]
    rows = []
    for a in ram_doc.get("animals", []):
        if a.get("archived"):
            continue
        sc = a.get("scores", {})
        rows.append([
            a.get("name", ""), a["id"], a.get("pen", ""), a.get("stage", ""), a.get("status", ""),
            sc.get("offspring_avg_famacha") or "",
            sc.get("offspring_shed_pct") or "",
            sc.get("offspring_avg_daily_gain") or "",
            sc.get("conception_rate") or "",
            sc.get("offspring_survival_90d") or "",
            a.get("total_score") or "",
            a.get("action", ""),
        ])
    write_tsv("05_ram_annual_eval.tsv", headers, rows)

    # Ewe TSV — columns mirror EWE_SCORE_KEYS in run_annual_eval.py
    with open(ewe_json) as f:
        ewe_doc = json.load(f)
    headers = [
        "Ewe Name", "Ewe ID", "Pen", "Stage", "Status",
        "Own FAMACHA Avg (30%)", "Deworming Events (20%)",
        "Shedding Score 1-5 (15%)", "Lambing Success (15%)",
        "Offspring FAMACHA Avg (10%)", "BCS (10%)",
        "TOTAL SCORE", "ACTION (Advance/Hold/Drop/Cull)"
    ]
    rows = []
    for a in ewe_doc.get("animals", []):
        if a.get("archived"):
            continue
        sc = a.get("scores", {})
        rows.append([
            a.get("name", ""), a["id"], a.get("pen", ""), a.get("stage", ""), a.get("status", ""),
            sc.get("own_famacha_avg") or "",
            sc.get("deworming_events") or "",
            sc.get("shedding_score") or "",
            sc.get("lambing_success") or "",
            sc.get("offspring_famacha") or "",
            sc.get("bcs") or "",
            a.get("total_score") or "",
            a.get("action", ""),
        ])
    write_tsv("06_ewe_annual_eval.tsv", headers, rows)


def _fmt_pct_dict(percentages):
    if not percentages:
        return ""
    return ", ".join(f"{k} {v}%" for k, v in percentages.items())


def _famacha_entries(sheep):
    """Yield (date_str, score, notes) tuples flattened across both field shapes."""
    h = sheep.get("health") or {}
    for entry in h.get("famacha_history", []) or []:
        yield entry.get("date", ""), entry.get("score", ""), entry.get("notes", "")
    for entry in h.get("famacha_scores", []) or []:
        yield entry.get("date", ""), entry.get("famacha", ""), entry.get("notes", "")


def _treatment_entries(sheep):
    h = sheep.get("health") or {}
    for t in h.get("treatments", []) or []:
        yield t.get("date", ""), t.get("treatment", ""), t.get("notes", "")


def export_master_flock_list(db):
    """Every animal (alive + deceased + sold + gifted + culled). Identity-first view."""
    headers = [
        "Name", "ID", "Tag", "Tag Color", "Sex", "Status", "Status Date", "Pen",
        "DOB", "DOB Approx", "Sire ID", "Dam ID",
        "Breed Primary", "Breed %", "Coat Type",
        "Weight (lb)", "Weight Estimated", "Confidence",
    ]
    rows = []
    for s in db["sheep"]:
        bc = s.get("breed_composition") or {}
        rows.append([
            s.get("name", ""), s["id"], s.get("tag") or "", s.get("tag_color") or "",
            s.get("sex", ""), s.get("status", ""), s.get("status_date") or "",
            s.get("pen") or "",
            s.get("dob") or "", "Y" if s.get("dob_approximate") else "",
            s.get("sire_id") or "", s.get("dam_id") or "",
            bc.get("primary", ""), _fmt_pct_dict(bc.get("percentages")),
            bc.get("coat_type", ""),
            s.get("weight_lbs") or "", "Y" if s.get("weight_estimated") else "",
            s.get("confidence", ""),
        ])
    rows.sort(key=lambda r: (r[5] != "alive", r[7], r[0]))  # alive first, then pen, then name
    write_tsv("08_master_flock_list.tsv", headers, rows)


def export_active_rams(db):
    """Registry of all alive rams and ram_lambs."""
    headers = [
        "Name", "ID", "Tag", "Pen", "DOB", "Breed Primary",
        "Weight (lb)", "Offspring Count", "Sire ID", "Dam ID",
    ]
    rows = []
    for s in db["sheep"]:
        if s.get("status") != "alive": continue
        if s.get("sex") not in ("ram", "ram_lamb"): continue
        offspring = (s.get("breeding") or {}).get("offspring_ids") or []
        bc = s.get("breed_composition") or {}
        rows.append([
            s.get("name", ""), s["id"], s.get("tag") or "",
            s.get("pen") or "", s.get("dob") or "",
            bc.get("primary", ""),
            s.get("weight_lbs") or "",
            len(offspring),
            s.get("sire_id") or "", s.get("dam_id") or "",
        ])
    rows.sort(key=lambda r: (r[3], r[0]))
    write_tsv("09_active_rams.tsv", headers, rows)


def export_active_ewes(db):
    """Registry of all alive ewes and ewe_lambs."""
    headers = [
        "Name", "ID", "Tag", "Pen", "DOB", "Breed Primary",
        "Weight (lb)", "Lambing Records", "Sire ID", "Dam ID",
    ]
    rows = []
    for s in db["sheep"]:
        if s.get("status") != "alive": continue
        if s.get("sex") not in ("ewe", "ewe_lamb"): continue
        lr = (s.get("breeding") or {}).get("lambing_records") or []
        bc = s.get("breed_composition") or {}
        rows.append([
            s.get("name", ""), s["id"], s.get("tag") or "",
            s.get("pen") or "", s.get("dob") or "",
            bc.get("primary", ""),
            s.get("weight_lbs") or "",
            len(lr),
            s.get("sire_id") or "", s.get("dam_id") or "",
        ])
    rows.sort(key=lambda r: (r[3], r[0]))
    write_tsv("10_active_ewes.tsv", headers, rows)


def export_health_treatment_log(db):
    """Date-indexed treatment log flattened across all sheep."""
    headers = ["Date", "Animal ID", "Animal Name", "Pen", "Treatment", "Notes"]
    rows = []
    for s in db["sheep"]:
        for date, treatment, notes in _treatment_entries(s):
            if not date and not treatment: continue
            rows.append([
                date, s["id"], s.get("name", ""), s.get("pen") or "",
                treatment, notes,
            ])
    rows.sort(key=lambda r: (r[0], r[2]), reverse=True)  # most recent first
    write_tsv("11_health_treatment_log.tsv", headers, rows)


def export_famacha_trend(db):
    """Longitudinal FAMACHA per animal. One row per score event."""
    headers = ["Date", "Animal ID", "Animal Name", "Pen", "Score", "Notes"]
    rows = []
    for s in db["sheep"]:
        for date, score, notes in _famacha_entries(s):
            if not date and score in (None, ""): continue
            rows.append([
                date, s["id"], s.get("name", ""), s.get("pen") or "",
                score, notes,
            ])
    rows.sort(key=lambda r: (r[0], r[2]), reverse=True)
    write_tsv("12_famacha_trend.tsv", headers, rows)


def export_weight_history(db):
    """Current weight + ADG slot per animal. ADG columns left blank for now —
    populated once historical weight series are entered."""
    headers = [
        "Animal ID", "Name", "Pen", "Status", "Current Weight (lb)", "Estimated",
        "30d Weight", "60d Weight", "90d Weight", "ADG (lb/day)",
    ]
    rows = []
    for s in db["sheep"]:
        if s.get("weight_lbs") is None: continue
        rows.append([
            s["id"], s.get("name", ""), s.get("pen") or "", s.get("status", ""),
            s.get("weight_lbs") or "", "Y" if s.get("weight_estimated") else "",
            "", "", "", "",
        ])
    rows.sort(key=lambda r: (r[3] != "alive", r[2], r[1]))
    write_tsv("13_weight_history_adg.tsv", headers, rows)


def export_breeding_season_tracker(db):
    """Per-lamb tracker pulled from lambing_records_2026 + sheep[] cross-ref."""
    headers = [
        "Birth Date", "Dam", "Sire", "Pen", "Lambs Born", "Lambs Alive", "Notes",
    ]
    rows = []
    for r in db.get("lambing_records_2026", []) or []:
        rows.append([
            r.get("date", ""), r.get("dam", "") or "", r.get("sire", "") or "",
            r.get("pen", "") or "", r.get("lambs_born", ""), r.get("lambs_alive", ""),
            r.get("notes", "") or "",
        ])
    rows.sort(key=lambda x: x[0], reverse=True)
    write_tsv("14_breeding_season_tracker.tsv", headers, rows)


def export_costs_financials_template(db):
    """Owner-filled costs/financials tab. Schema only — values entered in sheet."""
    headers = [
        "Date", "Category", "Animal/Pen", "Item", "Vendor",
        "Quantity", "Unit Cost", "Total Cost", "Notes",
    ]
    write_tsv("15_costs_financials.tsv", headers, [])


def export_per_pen_rosters(db):
    """One TSV per pen — same column shape as Active Flock but pen-filtered."""
    headers = [
        "Name", "ID", "Tag", "Sex", "DOB", "Breed Primary",
        "Weight (lb)", "Sire ID", "Dam ID", "Status",
    ]
    pen_to_rows = {}
    for s in db["sheep"]:
        if s.get("status") != "alive": continue
        pen = s.get("pen") or "no_pen"
        bc = s.get("breed_composition") or {}
        pen_to_rows.setdefault(pen, []).append([
            s.get("name", ""), s["id"], s.get("tag") or "",
            s.get("sex", ""), s.get("dob") or "",
            bc.get("primary", ""),
            s.get("weight_lbs") or "",
            s.get("sire_id") or "", s.get("dam_id") or "",
            s.get("status", ""),
        ])
    # Write one tab per pen, deterministic order
    base = 16
    pen_order = [
        "Pen 1", "Pen 2", "Pen 3", "Pen 4", "Pen 5", "Pen 6",
        "Tree Fort", "Chicken Coop", "Goose Pen", "no_pen",
    ]
    # numbering: 16=Pen 1 ... 21=Pen 6, 22=Tree Fort, 23=Chicken Coop, 24=Goose Pen, 25=no_pen
    written = 0
    for i, pen in enumerate(pen_order):
        if pen not in pen_to_rows: continue
        rows = sorted(pen_to_rows[pen], key=lambda r: (r[3], r[0]))
        slug = pen.lower().replace(" ", "_")
        write_tsv(f"{base + i:02d}_pen_{slug}.tsv", headers, rows)
        written += 1
    return written


def export_deceased_sold(db):
    headers = [
        "Name", "ID", "Tag", "Sex", "Status", "Status Date",
        "Breed Primary", "Sire ID", "Dam ID", "Notes"
    ]
    rows = []
    for s in db["sheep"]:
        if s.get("status") in ("deceased", "sold", "culled", "gifted"):
            rows.append([
                s.get("name", ""),
                s.get("id", ""),
                s.get("tag", ""),
                s.get("sex", ""),
                s.get("status", ""),
                s.get("status_date", ""),
                s.get("breed_composition", {}).get("primary", ""),
                s.get("sire_id", ""),
                s.get("dam_id", ""),
                (s.get("notes", "") or "")[:120],
            ])
    write_tsv("07_deceased_sold.tsv", headers, rows)


def generate_apps_script(db, breeds):
    """Generate a Google Apps Script that creates/updates all sheets from embedded data."""

    alive = [s for s in db["sheep"] if s.get("status") == "alive"]
    policy = db.get("breeding_policy", {})
    pipeline = policy.get("pipeline", {})
    stages = pipeline.get("stages", {})
    pen_to_stage = {pen: info.get("stage", "?") for pen, info in stages.items()}

    gs = """/**
 * Manatee Creek Flock — Google Sheets Updater
 * Generated: """ + datetime.now().strftime("%Y-%m-%d %H:%M") + """
 *
 * HOW TO USE:
 * 1. Open your Google Sheet
 * 2. Extensions → Apps Script
 * 3. Paste this entire file (replace any existing code)
 * 4. Click Run → updateAllSheets
 * 5. Authorize when prompted
 *
 * This will create/update these tabs:
 *   - Pipeline Overview
 *   - Active Flock
 *   - Breeding Policy
 *   - Breed Reference
 *   - Ram Annual Eval
 *   - Ewe Annual Eval
 *   - Deceased/Sold
 */

function updateAllSheets() {
  var ss = SpreadsheetApp.openById('1EQ5bOZL5Xmzu_7VvaMHTHWIwHPJqDKTJY_MMPduKrJU');

  updatePipelineOverview(ss);
  updateActiveFlock(ss);
  updateBreedingPolicy(ss);
  updateBreedReference(ss);
  updateRamEval(ss);
  updateEweEval(ss);
  updateDeceasedSold(ss);

  SpreadsheetApp.getUi().alert('All sheets updated! Soli Deo Gloria.');
}

function getOrCreateSheet(ss, name) {
  var sheet = ss.getSheetByName(name);
  if (!sheet) {
    sheet = ss.insertSheet(name);
  }
  sheet.clear();
  return sheet;
}

function formatHeader(sheet, numCols) {
  var range = sheet.getRange(1, 1, 1, numCols);
  range.setFontWeight('bold');
  range.setBackground('#4a86c8');
  range.setFontColor('#ffffff');
  sheet.setFrozenRows(1);
}

function autoResize(sheet, numCols) {
  for (var i = 1; i <= numCols; i++) {
    sheet.autoResizeColumn(i);
  }
}

"""

    # --- Pipeline Overview ---
    gs += "function updatePipelineOverview(ss) {\n"
    gs += "  var sheet = getOrCreateSheet(ss, 'Pipeline Overview');\n"
    gs += "  var data = [\n"
    gs += "    ['Stage','Pen','Size','Location','Ram','Ram Weight','Hair %','Coat','Ewes','FAMACHA Req','FEC Req','Shed Req','Shelter','Notes'],\n"

    for pen_name, info in stages.items():
        ram_id = info.get("ram", "")
        ram = next((s for s in alive if s["id"] == ram_id), {})
        ram_name = ram.get("name", ram_id)
        ram_wt = ram.get("weight_lbs", "?")
        bc = ram.get("breed_composition", {})
        hair = bc.get("hair_percentage", "?")
        coat = bc.get("coat_observed", bc.get("coat_prediction", "?"))
        ewe_count = sum(1 for s in alive if s.get("pen") == pen_name and s.get("sex") in ("ewe", "ewe_lamb"))
        adv = info.get("advancement_criteria", {})
        notes = info.get("ram_notes", "")[:80]

        row_vals = [
            gs_safe(info.get('stage', '')),
            gs_safe(pen_name),
            gs_safe(info.get('size', '')),
            gs_safe(info.get('location', '')),
            gs_safe(ram_name),
            gs_safe(ram_wt),
            gs_safe(hair),
            gs_safe(coat),
            str(ewe_count),
            gs_safe(adv.get('famacha', '')),
            gs_safe(adv.get('fec_epg', '')),
            gs_safe(adv.get('shedding_pct', '')),
            gs_safe(info.get('shelter', '')),
            gs_safe(notes, 80),
        ]
        gs += "    ['" + "','".join(row_vals) + "'],\n"

    gs += "  ];\n"
    gs += "  sheet.getRange(1, 1, data.length, data[0].length).setValues(data);\n"
    gs += "  formatHeader(sheet, data[0].length);\n"
    gs += "  autoResize(sheet, data[0].length);\n"
    gs += "}\n\n"

    # --- Active Flock ---
    gs += "function updateActiveFlock(ss) {\n"
    gs += "  var sheet = getOrCreateSheet(ss, 'Active Flock');\n"
    gs += "  var data = [\n"
    gs += "    ['Pen','Stage','Name','ID','Tag','Sex','Weight','Breed','Hair %','Wool %','Coat Obs','Coat Pred','Sire','Dam','Weak Parasites','Notes'],\n"

    for s in sorted(alive, key=lambda x: (
        str(pen_to_stage.get(x.get("pen", ""), 99)),
        str(x.get("pen", "zzz")),
        0 if x.get("sex") in ("ram", "ram_lamb") else 1,
        str(x.get("name", ""))
    )):
        bc = s.get("breed_composition", {})
        name = s.get("name", "")
        notes = (s.get("notes", "") or "")[:80].replace("\n", " ")
        pen = s.get("pen", "?")
        stage = pen_to_stage.get(pen, "?")
        weak = "YES" if s.get("health", {}).get("weak_resistance") else ""

        row_vals = [
            gs_safe(pen), gs_safe(stage), gs_safe(name), gs_safe(s.get('id','')),
            gs_safe(s.get('tag','')), gs_safe(s.get('sex','')), gs_safe(s.get('weight_lbs','')),
            gs_safe(bc.get('primary','')), gs_safe(bc.get('hair_percentage','')),
            gs_safe(bc.get('wool_percentage','')), gs_safe(bc.get('coat_observed','')),
            gs_safe(bc.get('coat_prediction','')), gs_safe(s.get('sire_id','')),
            gs_safe(s.get('dam_id','')), gs_safe(weak), gs_safe(notes, 60),
        ]
        gs += "    ['" + "','".join(row_vals) + "'],\n"

    gs += "  ];\n"
    gs += "  sheet.getRange(1, 1, data.length, data[0].length).setValues(data);\n"
    gs += "  formatHeader(sheet, data[0].length);\n"
    gs += "  autoResize(sheet, data[0].length);\n"
    gs += "  // Color-code by stage\n"
    gs += "  for (var i = 2; i <= data.length; i++) {\n"
    gs += "    var stage = sheet.getRange(i, 2).getValue();\n"
    gs += "    var color = '#ffffff';\n"
    gs += "    if (stage == 1) color = '#ffcccc';\n"
    gs += "    else if (stage == 2) color = '#ffd9b3';\n"
    gs += "    else if (stage == 3) color = '#ffffcc';\n"
    gs += "    else if (stage == 4) color = '#ccffcc';\n"
    gs += "    else if (stage == 5) color = '#ccffff';\n"
    gs += "    else if (stage == 6) color = '#cce5ff';\n"
    gs += "    else if (stage == 7) color = '#e5ccff';\n"
    gs += "    sheet.getRange(i, 1, 1, data[0].length).setBackground(color);\n"
    gs += "  }\n"
    gs += "}\n\n"

    # --- Breeding Policy ---
    gs += "function updateBreedingPolicy(ss) {\n"
    gs += "  var sheet = getOrCreateSheet(ss, 'Breeding Policy');\n"
    gs += "  var data = [\n"
    gs += "    ['Category','Item','Details'],\n"

    for h in policy.get("selection_hierarchy", []):
        gs += "    ['" + "','".join([gs_safe('Selection Hierarchy'), gs_safe(f'#{h["rank"]} {h["trait"]}'), gs_safe(h["description"], 120)]) + "'],\n"

    gs += "    ['','',''],\n"

    for lesson in policy.get("hard_lessons", []):
        gs += "    ['" + "','".join([gs_safe('Hard Lesson'), '', gs_safe(lesson, 120)]) + "'],\n"

    gs += "    ['','',''],\n"

    pipe = policy.get("pipeline", {})
    gs += "    ['" + "','".join([gs_safe('Pipeline'), gs_safe('Target Animal'), gs_safe(pipe.get('target_animal',''), 120)]) + "'],\n"
    gs += "    ['" + "','".join([gs_safe('Pipeline'), gs_safe('Inbreeding Policy'), gs_safe(pipe.get('inbreeding_policy',''), 120)]) + "'],\n"
    gs += "    ['" + "','".join([gs_safe('Pipeline'), gs_safe('Key Insight'), gs_safe(pipe.get('key_insight',''), 120)]) + "'],\n"

    gs += "    ['','',''],\n"

    st = policy.get("stress_test", {})
    for fix in st.get("critical_fixes_applied", []):
        gs += "    ['" + "','".join([gs_safe('Stress Test Fix'), gs_safe(st.get('date','')), gs_safe(fix, 120)]) + "'],\n"
    for vuln in st.get("known_vulnerabilities", []):
        gs += "    ['" + "','".join([gs_safe('Known Vulnerability'), '', gs_safe(vuln, 120)]) + "'],\n"

    gs += "  ];\n"
    gs += "  sheet.getRange(1, 1, data.length, data[0].length).setValues(data);\n"
    gs += "  formatHeader(sheet, data[0].length);\n"
    gs += "  autoResize(sheet, data[0].length);\n"
    gs += "}\n\n"

    # --- Breed Reference ---
    gs += "function updateBreedReference(ss) {\n"
    gs += "  var sheet = getOrCreateSheet(ss, 'Breed Reference');\n"
    gs += "  var data = [\n"
    gs += "    ['Breed','Type','Avg Ewe Wt','Avg Ram Wt','Notes'],\n"

    for breed_name, info in sorted(breeds.items()):
        gs += "    ['" + "','".join([gs_safe(breed_name), gs_safe(info.get('type','')), gs_safe(info.get('avg_ewe_wt','')), gs_safe(info.get('avg_ram_wt','')), gs_safe(info.get('notes',''), 100)]) + "'],\n"

    gs += "  ];\n"
    gs += "  sheet.getRange(1, 1, data.length, data[0].length).setValues(data);\n"
    gs += "  formatHeader(sheet, data[0].length);\n"
    gs += "  // Color hair=green, wool=red, intermediate=yellow\n"
    gs += "  for (var i = 2; i <= data.length; i++) {\n"
    gs += "    var type = sheet.getRange(i, 2).getValue();\n"
    gs += "    var color = type == 'hair' ? '#ccffcc' : (type == 'wool' ? '#ffcccc' : '#ffffcc');\n"
    gs += "    sheet.getRange(i, 2).setBackground(color);\n"
    gs += "  }\n"
    gs += "  autoResize(sheet, data[0].length);\n"
    gs += "}\n\n"

    # --- Ram Annual Eval ---
    gs += "function updateRamEval(ss) {\n"
    gs += "  var sheet = getOrCreateSheet(ss, 'Ram Annual Eval');\n"
    gs += "  var data = [\n"
    gs += "    ['Ram','ID','Pen','Stage','Offspring FAMACHA (40%)','Offspring Shed % (25%)','Offspring ADG (15%)','Conception Rate (10%)','Offspring Survival (10%)','TOTAL','ACTION'],\n"

    for s in alive:
        if s.get("sex") in ("ram", "ram_lamb") and s.get("pen") and s["pen"] != "Goose Pen":
            name = gs_safe(s["name"])
            stage = gs_safe(pen_to_stage.get(s.get("pen", ""), "?"))
            gs += "    ['" + "','".join([name, gs_safe(s['id']), gs_safe(s.get('pen','')), stage, '','','','','','','']) + "'],\n"

    gs += "  ];\n"
    gs += "  sheet.getRange(1, 1, data.length, data[0].length).setValues(data);\n"
    gs += "  formatHeader(sheet, data[0].length);\n"
    gs += "  autoResize(sheet, data[0].length);\n"
    gs += "}\n\n"

    # --- Ewe Annual Eval ---
    gs += "function updateEweEval(ss) {\n"
    gs += "  var sheet = getOrCreateSheet(ss, 'Ewe Annual Eval');\n"
    gs += "  var data = [\n"
    gs += "    ['Ewe','ID','Pen','Stage','Own FAMACHA (30%)','Deworm Events (20%)','Shed Score 1-5 (15%)','Lambing (15%)','Offspring FAMACHA (10%)','BCS (10%)','TOTAL','ACTION'],\n"

    for s in sorted(alive, key=lambda x: (str(pen_to_stage.get(x.get("pen",""), 99)), str(x.get("name","")))):
        if s.get("sex") in ("ewe", "ewe_lamb"):
            name = gs_safe(s["name"])
            stage = gs_safe(pen_to_stage.get(s.get("pen", ""), "?"))
            gs += "    ['" + "','".join([name, gs_safe(s['id']), gs_safe(s.get('pen','')), stage, '','','','','','','','']) + "'],\n"

    gs += "  ];\n"
    gs += "  sheet.getRange(1, 1, data.length, data[0].length).setValues(data);\n"
    gs += "  formatHeader(sheet, data[0].length);\n"
    gs += "  autoResize(sheet, data[0].length);\n"
    gs += "}\n\n"

    # --- Deceased/Sold ---
    gs += "function updateDeceasedSold(ss) {\n"
    gs += "  var sheet = getOrCreateSheet(ss, 'Deceased & Sold');\n"
    gs += "  var data = [\n"
    gs += "    ['Name','ID','Tag','Sex','Status','Date','Breed','Sire','Dam','Notes'],\n"

    for s in db["sheep"]:
        if s.get("status") in ("deceased", "sold", "culled", "gifted"):
            row_vals = [
                gs_safe(s.get('name','')), gs_safe(s.get('id','')), gs_safe(s.get('tag','')),
                gs_safe(s.get('sex','')), gs_safe(s.get('status','')), gs_safe(s.get('status_date','')),
                gs_safe(s.get('breed_composition',{}).get('primary','')),
                gs_safe(s.get('sire_id','')), gs_safe(s.get('dam_id','')),
                gs_safe(s.get('notes',''), 60),
            ]
            gs += "    ['" + "','".join(row_vals) + "'],\n"

    gs += "  ];\n"
    gs += "  sheet.getRange(1, 1, data.length, data[0].length).setValues(data);\n"
    gs += "  formatHeader(sheet, data[0].length);\n"
    gs += "  autoResize(sheet, data[0].length);\n"
    gs += "}\n"

    # Post-process: strip non-ASCII from entire output
    gs = gs.replace("\u2014", " - ").replace("\u2013", "-")
    gs = gs.replace("\u2192", "->").replace("\u2190", "<-")
    gs = gs.replace("\u00D7", "x").replace("\u2260", "!=")
    gs = gs.replace("\u2265", ">=").replace("\u2264", "<=")
    gs = gs.encode("ascii", "ignore").decode("ascii")

    # Post-process: remove any unescaped single quotes inside JS string literals
    # Split into lines and fix any line where a data value contains a single quote
    import re
    fixed_lines = []
    for line in gs.split("\n"):
        # Only process data array lines (start with whitespace + [')
        if line.strip().startswith("['" ) and line.strip().endswith("'],"):
            # Replace single quotes INSIDE data values (not the delimiters)
            # Strategy: extract values between ','  delimiters and clean them
            parts = line.split("','")
            cleaned = []
            for i, part in enumerate(parts):
                if i == 0:
                    # First part: starts with ['
                    prefix = part[:part.index("'") + 1]
                    val = part[part.index("'") + 1:]
                    cleaned.append(prefix + val.replace("'", ""))
                elif i == len(parts) - 1:
                    # Last part: ends with '],
                    if part.endswith("'],"):
                        val = part[:-3]
                        cleaned.append(val.replace("'", "") + "'],")
                    elif part.endswith("'],\n"):
                        val = part[:-5]
                        cleaned.append(val.replace("'", "") + "'],")
                    else:
                        cleaned.append(part.replace("'", ""))
                else:
                    cleaned.append(part.replace("'", ""))
            line = "','".join(cleaned)
        fixed_lines.append(line)
    gs = "\n".join(fixed_lines)

    gs_path = os.path.join(OUT_DIR, "flock_sheets_update.gs")
    with open(gs_path, "w") as f:
        f.write(gs)
    print(f"  flock_sheets_update.gs: Apps Script generated")


def main():
    tsv_only = "--tsv-only" in sys.argv
    gs_only = "--gs-only" in sys.argv
    dry_run = "--dry-run" in sys.argv

    db, breeds = load_data()
    print(f"Exporting flock data ({len([s for s in db['sheep'] if s.get('status')=='alive'])} alive, {len(db['sheep'])} total)")
    print(f"Output: {OUT_DIR}/\n")

    if dry_run:
        # Compute expected tab count and per-tab row counts without writing.
        alive = [s for s in db["sheep"] if s.get("status") == "alive"]
        pens_used = sorted({s.get("pen") or "no_pen" for s in alive})
        pen_count = len([p for p in pens_used if p in {"Pen 1","Pen 2","Pen 3","Pen 4","Pen 5","Pen 6","Tree Fort","Chicken Coop","Goose Pen","no_pen"}])
        fixed_tabs = 15  # 01-15 baseline (excluding per-pen)
        # 01 pipeline_overview, 02 active_flock, 03 breeding_policy, 04 breed_reference,
        # 05 ram_eval, 06 ewe_eval, 07 deceased_sold, 08 master_flock_list,
        # 09 active_rams, 10 active_ewes, 11 health_treatment_log, 12 famacha_trend,
        # 13 weight_history_adg, 14 breeding_season_tracker, 15 costs_financials
        total = fixed_tabs + pen_count
        print(f"[dry-run] Planned tabs: {total} ({fixed_tabs} fixed + {pen_count} per-pen)")
        print(f"[dry-run] Animals: {len(alive)} alive, {sum(1 for s in db['sheep'] if s.get('status')=='deceased')} deceased, {sum(1 for s in db['sheep'] if s.get('status')=='sold')} sold")
        print(f"[dry-run] Per-pen tabs: {pens_used}")
        print(f"[dry-run] Lambing records 2026: {len(db.get('lambing_records_2026',[]))}")
        return

    if not gs_only:
        export_pipeline_overview(db)
        export_active_flock(db)
        export_breeding_policy(db)
        if breeds:
            export_breed_reference(breeds)
        export_annual_eval_template(db)
        export_deceased_sold(db)
        # L5 expansion: 08-15 fixed tabs + 16-24 per-pen rosters
        export_master_flock_list(db)
        export_active_rams(db)
        export_active_ewes(db)
        export_health_treatment_log(db)
        export_famacha_trend(db)
        export_weight_history(db)
        export_breeding_season_tracker(db)
        export_costs_financials_template(db)
        export_per_pen_rosters(db)

    if not tsv_only:
        generate_apps_script(db, breeds)

    print(f"\nDone. To update Google Sheets:")
    print(f"  Option A: Open each .tsv file → copy/paste into a Google Sheet tab")
    print(f"  Option B: Open Google Sheet → Extensions → Apps Script → paste flock_sheets_update.gs → Run updateAllSheets")


if __name__ == "__main__":
    main()
