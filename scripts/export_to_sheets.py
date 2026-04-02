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


def export_annual_eval_template(db):
    """Generate blank scoring templates for annual review."""

    # Ram evaluation template
    headers = [
        "Ram Name", "Ram ID", "Pen", "Stage",
        "Offspring Avg FAMACHA (40%)", "Offspring Shed % (25%)",
        "Offspring Avg Daily Gain (15%)", "Conception Rate (10%)",
        "Offspring Survival 90d (10%)",
        "TOTAL SCORE", "ACTION (Keep/Demote/Replace/Cull)"
    ]
    rows = []
    for s in db["sheep"]:
        if s.get("status") == "alive" and s.get("sex") in ("ram", "ram_lamb"):
            if s.get("pen") and s["pen"] != "Goose Pen":
                rows.append([
                    s["name"], s["id"], s.get("pen", ""), "",
                    "", "", "", "", "", "", ""
                ])
    write_tsv("05_ram_annual_eval.tsv", headers, rows)

    # Ewe evaluation template
    headers = [
        "Ewe Name", "Ewe ID", "Pen", "Stage",
        "Own FAMACHA Avg (30%)", "Deworming Events (20%)",
        "Shedding Score 1-5 (15%)", "Lambing Success (15%)",
        "Offspring FAMACHA Avg (10%)", "BCS (10%)",
        "TOTAL SCORE", "ACTION (Advance/Hold/Drop/Cull)"
    ]
    rows = []
    for s in db["sheep"]:
        if s.get("status") == "alive" and s.get("sex") in ("ewe", "ewe_lamb"):
            rows.append([
                s["name"], s["id"], s.get("pen", ""), "",
                "", "", "", "", "", "", "", ""
            ])
    write_tsv("06_ewe_annual_eval.tsv", headers, rows)


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
  var ss = SpreadsheetApp.getActiveSpreadsheet();

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
        ram_name = ram.get("name", ram_id).replace("'", "\\'")
        ram_wt = ram.get("weight_lbs", "?")
        bc = ram.get("breed_composition", {})
        hair = bc.get("hair_percentage", "?")
        coat = bc.get("coat_observed", bc.get("coat_prediction", "?"))
        ewe_count = sum(1 for s in alive if s.get("pen") == pen_name and s.get("sex") in ("ewe", "ewe_lamb"))
        adv = info.get("advancement_criteria", {})
        notes = info.get("ram_notes", "")[:80].replace("'", "\\'")

        gs += f"    ['{info.get('stage','')}','{pen_name}','{info.get('size','')}','{info.get('location','')}','{ram_name}','{ram_wt}','{hair}','{coat}',{ewe_count},'{adv.get('famacha','')}','{adv.get('fec_epg','')}','{adv.get('shedding_pct','')}','{info.get('shelter','')}','{notes}'],\n"

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
        name = s.get("name", "").replace("'", "\\'")
        notes = (s.get("notes", "") or "")[:80].replace("'", "\\'").replace("\n", " ")
        pen = s.get("pen", "?")
        stage = pen_to_stage.get(pen, "?")
        weak = "YES" if s.get("health", {}).get("weak_resistance") else ""

        gs += f"    ['{pen}','{stage}','{name}','{s.get('id','')}','{s.get('tag','')}','{s.get('sex','')}','{s.get('weight_lbs','')}','{bc.get('primary','').replace(chr(39),'')}','{bc.get('hair_percentage','')}','{bc.get('wool_percentage','')}','{bc.get('coat_observed','')}','{bc.get('coat_prediction','')}','{s.get('sire_id','')}','{s.get('dam_id','')}','{weak}','{notes[:60]}'],\n"

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
        desc = h["description"].replace("'", "\\'")[:120]
        gs += f"    ['Selection Hierarchy','#{h['rank']} {h['trait']}','{desc}'],\n"

    gs += "    ['','',''],\n"

    for lesson in policy.get("hard_lessons", []):
        l = lesson.replace("'", "\\'")[:120]
        gs += f"    ['Hard Lesson','','{l}'],\n"

    gs += "    ['','',''],\n"

    pipe = policy.get("pipeline", {})
    target = pipe.get("target_animal", "").replace("'", "\\'")[:120]
    gs += f"    ['Pipeline','Target Animal','{target}'],\n"
    inb = pipe.get("inbreeding_policy", "").replace("'", "\\'")[:120]
    gs += f"    ['Pipeline','Inbreeding Policy','{inb}'],\n"
    ki = pipe.get("key_insight", "").replace("'", "\\'")[:120]
    gs += f"    ['Pipeline','Key Insight','{ki}'],\n"

    gs += "    ['','',''],\n"

    st = policy.get("stress_test", {})
    for fix in st.get("critical_fixes_applied", []):
        f_str = fix.replace("'", "\\'")[:120]
        gs += f"    ['Stress Test Fix','{st.get('date','')}','{f_str}'],\n"
    for vuln in st.get("known_vulnerabilities", []):
        v_str = vuln.replace("'", "\\'")[:120]
        gs += f"    ['Known Vulnerability','','{v_str}'],\n"

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
        notes = info.get("notes", "").replace("'", "\\'")[:100]
        gs += f"    ['{breed_name}','{info.get('type','')}',{info.get('avg_ewe_wt','')},{info.get('avg_ram_wt','')},'{notes}'],\n"

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
            name = s["name"].replace("'", "\\'")
            stage = pen_to_stage.get(s.get("pen", ""), "?")
            gs += f"    ['{name}','{s['id']}','{s.get('pen','')}','{stage}','','','','','','',''],\n"

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
            name = s["name"].replace("'", "\\'")
            stage = pen_to_stage.get(s.get("pen", ""), "?")
            gs += f"    ['{name}','{s['id']}','{s.get('pen','')}','{stage}','','','','','','','',''],\n"

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
            name = s.get("name", "").replace("'", "\\'")
            notes = (s.get("notes", "") or "")[:80].replace("'", "\\'").replace("\n", " ")
            gs += f"    ['{name}','{s.get('id','')}','{s.get('tag','')}','{s.get('sex','')}','{s.get('status','')}','{s.get('status_date','')}','{s.get('breed_composition',{}).get('primary','').replace(chr(39),'')}','{s.get('sire_id','')}','{s.get('dam_id','')}','{notes[:60]}'],\n"

    gs += "  ];\n"
    gs += "  sheet.getRange(1, 1, data.length, data[0].length).setValues(data);\n"
    gs += "  formatHeader(sheet, data[0].length);\n"
    gs += "  autoResize(sheet, data[0].length);\n"
    gs += "}\n"

    gs_path = os.path.join(OUT_DIR, "flock_sheets_update.gs")
    with open(gs_path, "w") as f:
        f.write(gs)
    print(f"  flock_sheets_update.gs: Apps Script generated")


def main():
    tsv_only = "--tsv-only" in sys.argv
    gs_only = "--gs-only" in sys.argv

    db, breeds = load_data()
    print(f"Exporting flock data ({len([s for s in db['sheep'] if s.get('status')=='alive'])} alive, {len(db['sheep'])} total)")
    print(f"Output: {OUT_DIR}/\n")

    if not gs_only:
        export_pipeline_overview(db)
        export_active_flock(db)
        export_breeding_policy(db)
        if breeds:
            export_breed_reference(breeds)
        export_annual_eval_template(db)
        export_deceased_sold(db)

    if not tsv_only:
        generate_apps_script(db, breeds)

    print(f"\nDone. To update Google Sheets:")
    print(f"  Option A: Open each .tsv file → copy/paste into a Google Sheet tab")
    print(f"  Option B: Open Google Sheet → Extensions → Apps Script → paste flock_sheets_update.gs → Run updateAllSheets")


if __name__ == "__main__":
    main()
