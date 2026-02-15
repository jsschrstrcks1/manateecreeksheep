#!/usr/bin/env python3
"""
Build the initial flock database from all available sources.
Run once to create data/flock_database.json, then maintain by hand/AI.
"""

import json
from pathlib import Path
from datetime import date

REPO_ROOT = Path(__file__).parent.parent
DB_PATH = REPO_ROOT / "data" / "flock_database.json"

today = date.today().isoformat()

db = {
    "meta": {
        "version": "1.0.0",
        "farm_name": "Manatee Creek Sheep",
        "last_updated": today,
        "data_sources": [
            "spiral_notebook (IMG_8616-8643)",
            "flock_record_v2.xlsx",
            "data.csv",
            "google_sheet",
            "Sheep_Breeding_DB_CURRENT_COPY.xlsx"
        ],
        "primary_source": "spiral_notebook",
        "notes": "Spiral notebook images are the most current and authoritative. When sources conflict, notebook wins. Mom writes Azure as 'Amure'."
    },
    "sheep": [],
    "pens": {},
    "lambing_records_2026": [],
    "breed_reference": {
        "hair_breeds": ["Katahdin", "Dorper", "White Dorper", "St Croix", "Barbados Blackbelly", "American Blackbelly", "Wiltshire Horn"],
        "wool_breeds": ["Suffolk", "Hampshire", "Cotswold", "Tunis", "Gulf Coast Native"],
        "dual_purpose": ["St Augustine", "Cracker", "Awassi", "East Friesian"],
        "other": ["Jacob", "Babydoll", "Karakul"]
    },
    "breeding_goals": {
        "primary": "Parasite resistance via FAMACHA-driven selection",
        "secondary": ["Meat quality (Dorper influence)", "Milk production (Awassi influence)", "Hair coat selection"],
        "key_observations": {
            "most_parasite_resistant": "Kelsier (Katahdin)",
            "most_milky": "Awassi and Awassi crosses",
            "meatiest": "Dorper-Awassi cross",
            "total_breeds_in_flock": 22
        }
    }
}

def sheep(id, name, sex, status, **kwargs):
    """Helper to build a sheep record."""
    record = {
        "id": id,
        "name": name,
        "aliases": kwargs.get("aliases", []),
        "tag": kwargs.get("tag"),
        "mc_tag": kwargs.get("mc_tag"),
        "sex": sex,
        "breed_composition": kwargs.get("breed_composition", {}),
        "color_markings": kwargs.get("color_markings", ""),
        "weight_lbs": kwargs.get("weight_lbs"),
        "dob": kwargs.get("dob"),
        "dob_approximate": kwargs.get("dob_approximate", True),
        "sire_id": kwargs.get("sire_id"),
        "dam_id": kwargs.get("dam_id"),
        "status": status,
        "status_date": kwargs.get("status_date"),
        "status_notes": kwargs.get("status_notes", ""),
        "pen": kwargs.get("pen"),
        "measurements": kwargs.get("measurements", {}),
        "health": {
            "famacha_scores": kwargs.get("famacha_scores", []),
            "weak_resistance": kwargs.get("weak_resistance", False),
            "treatments": kwargs.get("treatments", []),
            "vaccinations": kwargs.get("vaccinations", []),
            "notes": kwargs.get("health_notes", [])
        },
        "breeding": {
            "is_breeding_animal": kwargs.get("is_breeding_animal", False),
            "breeding_group": kwargs.get("breeding_group", ""),
            "offspring_ids": kwargs.get("offspring_ids", []),
            "lambing_records": kwargs.get("lambing_records", [])
        },
        "source_refs": {
            "csv_row": kwargs.get("csv_row"),
            "notebook_image": kwargs.get("notebook_image", []),
        },
        "notes": kwargs.get("notes", ""),
        "confidence": kwargs.get("confidence", "medium"),
        "last_verified": today
    }
    return record

# ============================================================
# RAMS
# ============================================================

# Sir Loin - the main herd ram from CSV
db["sheep"].append(sheep("sir-loin", "Sir Loin", "ram", "alive",
    aliases=["Sirloin"],
    breed_composition={"primary": "St Augustine", "percentages": {"St Augustine": 100}, "coat_type": "mixed", "hair_percentage": 50},
    weight_lbs=300, dob="2012-01-01", dob_approximate=True,
    pen="Pen 2", is_breeding_animal=True,
    notes="Large ram, 300lbs. From CSV. One of the primary sires.",
    confidence="high", csv_row=1))

# Kelsier - Katahdin ram, MOST parasite resistant
db["sheep"].append(sheep("kelsier", "Kelsier", "ram", "alive",
    tag="22", aliases=["Tag 22"],
    breed_composition={"primary": "Katahdin", "percentages": {"Katahdin": 100}, "coat_type": "hair", "hair_percentage": 100},
    pen="Pen 4", is_breeding_animal=True,
    notes="Most parasite resistant sheep in the flock. Pure Katahdin. From Google Sheet Pen 4 data.",
    confidence="high"))

# GG (tag 23) - ram from Google Sheet
db["sheep"].append(sheep("gg", "GG", "ram", "alive",
    tag="23", aliases=["Gigi", "Gg"],
    breed_composition={"primary": "Katahdin/Hampshire", "percentages": {"Katahdin": 50, "Hampshire": 50}, "coat_type": "mixed", "hair_percentage": 50},
    pen="Pen 4", is_breeding_animal=True,
    weak_resistance=True,
    notes="Azure's full brother. On weak resistance list. From Google Sheet Pen 4 / notebook.",
    confidence="medium",
    offspring_ids=["gg-daughter-45", "lara-daughter-46", "gg-son-094"],
    notebook_image=["IMG_8628.PNG", "IMG_8634.PNG"]))

# Rocky - ram for Pen 5
db["sheep"].append(sheep("rocky", "Rocky", "ram", "alive",
    aliases=["Rock"],
    pen="Pen 5", is_breeding_animal=True,
    weak_resistance=True,
    notes="Ram for pen 5 group. On weak resistance list.",
    confidence="medium",
    notebook_image=["IMG_8628.PNG", "IMG_8629.PNG"]))

# Rock / Jerkface - Awassi cross ram (Pen 6)
db["sheep"].append(sheep("jerkface", "Rock (Jerkface)", "ram", "alive",
    aliases=["Rock", "Jerkface", "Awassi ram", "Awassi cross rock"],
    breed_composition={"primary": "Awassi cross", "percentages": {"Awassi": 50}, "coat_type": "mixed", "hair_percentage": 50},
    pen="Pen 6",
    is_breeding_animal=True,
    famacha_scores=[{"score": 5, "date": "2025-10-23"}],
    treatments=[{"date": "2024-10-24", "treatment": "iron and vitamin B"}],
    notes="Also called Jerkface. Awassi cross. Had sick episode 10-23-23. Treated with iron. In pen 6.",
    confidence="high",
    notebook_image=["IMG_8626.PNG", "IMG_8641.PNG"]))

# Samson - ram (deceased per weak resistance list)
db["sheep"].append(sheep("samson", "Samson", "ram", "deceased",
    pen="Pen 4",
    weak_resistance=True,
    is_breeding_animal=True,
    notes="Was ram for Pen 4 group (Elsie, Nori, Trouble, Bsoe, Bsoed, Banana). Deceased per weak resistance list. Pen 4 entry says 'Samson 4'.",
    confidence="medium",
    notebook_image=["IMG_8628.PNG", "IMG_8629.PNG"]))

# Sam - ram for Pen 3
db["sheep"].append(sheep("sam", "Sam", "ram", "alive",
    pen="Pen 3",
    is_breeding_animal=True,
    treatments=[{"date": "2025-tag-day", "treatment": "iron (FAMACHA 3)"}],
    notes="Ram for pen 3 group. Given iron treatment. Pen 3 includes: Baby, Baby momma, Zara, Half tail, New big girl 2.",
    confidence="medium",
    notebook_image=["IMG_8641.PNG"]))

# Kaladin - ram for Pen 1
db["sheep"].append(sheep("kaladin", "Kaladin", "ram", "alive",
    tag="014",
    pen="Pen 1",
    is_breeding_animal=True,
    measurements={"measurement_1": 19, "measurement_2": 20, "date": "2025"},
    notes="Ram for pen 1. With Eclipse, Merrie, Abg, Fm.",
    confidence="high",
    notebook_image=["IMG_8624.PNG", "IMG_8630.PNG"]))

# S'More - Cracker ram from CSV
db["sheep"].append(sheep("smore", "S'More", "ram", "unknown",
    breed_composition={"primary": "Cracker", "percentages": {"Cracker": 100}, "coat_type": "mixed", "hair_percentage": 50},
    weight_lbs=180,
    is_breeding_animal=True,
    notes="From CSV. Cracker ram, 180lbs. Status unknown - may be sold/deceased.",
    confidence="low", csv_row=2))

# Well Done - Katahdin ram from CSV
db["sheep"].append(sheep("well-done", "Well Done", "ram", "unknown",
    breed_composition={"primary": "Katahdin", "percentages": {"Katahdin": 100}, "coat_type": "hair", "hair_percentage": 100},
    weight_lbs=100,
    is_breeding_animal=True,
    notes="From CSV. Katahdin ram, 100lbs. Status unknown.",
    confidence="low", csv_row=3))

# Butter Ball - Dorper ram (deceased)
db["sheep"].append(sheep("butter-ball", "Butter Ball", "ram", "deceased",
    aliases=["Butterball"],
    breed_composition={"primary": "Dorper", "percentages": {"Dorper": 100}, "coat_type": "hair", "hair_percentage": 100},
    weak_resistance=True,
    notes="Dorper ram. Deceased per weak resistance list.",
    confidence="high",
    notebook_image=["IMG_8628.PNG"]))

# NoriSon - ram in pen 5, tag 54
db["sheep"].append(sheep("nori-son", "NoriSon", "ram", "alive",
    tag="054", aliases=["Nori's Son"],
    pen="Pen 5",
    dam_id="nori",
    is_breeding_animal=True,
    notes="Ram in pen 5 currently. Tag 54. Nori's son. Notebook lists associated tags: 47, Red ewe Lamb in 4, Little daisy (41 or 42), Tag 31, 2222, Elsie.",
    confidence="high",
    notebook_image=["IMG_8639.PNG"]))

# Charlie's ram / Mc11 - tag 12
db["sheep"].append(sheep("charlies-ram", "Charlie's Ram", "ram", "alive",
    tag="012", mc_tag="Mc11",
    aliases=["Mc 11 ram", "Charlie's ram 12"],
    measurements={"measurement_1": 26, "measurement_2": 22, "date": "2025"},
    notes="Photos from March 18, 2024. Also called Mc11 or tag 12. White lamb with yellow ear tag in photos.",
    confidence="high",
    notebook_image=["IMG_8624.PNG", "IMG_8631.PNG"]))

# Pippin - ram, tag 015
db["sheep"].append(sheep("pippin", "Pippin", "ram", "alive",
    tag="015",
    measurements={"measurement_1": 28, "measurement_2": 30.75, "date": "2025"},
    notes="Ram from measurement list.",
    confidence="medium",
    notebook_image=["IMG_8622.PNG"]))

# New black belly ram 018
db["sheep"].append(sheep("new-black-belly-ram", "New Black Belly Ram", "ram", "alive",
    tag="018",
    breed_composition={"primary": "American Blackbelly", "percentages": {"American Blackbelly": 100}, "coat_type": "hair", "hair_percentage": 100},
    measurements={"measurement_1": 18, "measurement_2": 19.5, "date": "2025"},
    notes="New ABB ram from measurement list.",
    confidence="medium",
    notebook_image=["IMG_8625.PNG"]))

# Charlie's lamb 0017
db["sheep"].append(sheep("charlies-lamb-0017", "Charlie's Lamb", "ram", "alive",
    tag="0017",
    sire_id="charlies-ram",
    measurements={"measurement_1": 29.5, "measurement_2": 29, "date": "2025"},
    notes="Charlie's ram's lamb. Tag 0017.",
    confidence="medium",
    notebook_image=["IMG_8625.PNG"]))

# Big free male 005
db["sheep"].append(sheep("big-free-male", "Big Free Male", "ram", "alive",
    tag="005",
    measurements={"measurement_1": 29, "measurement_2": 35, "date": "2025"},
    notes="Large free-roaming male from measurement list.",
    confidence="medium",
    notebook_image=["IMG_8623.PNG"]))

# ============================================================
# EWES - Current Flock
# ============================================================

# Azure (Amure) - ewe
db["sheep"].append(sheep("azure", "Azure", "ewe", "alive",
    tag="024", aliases=["Amure", "Amber 24"],
    breed_composition={"primary": "Suffolk Cross", "percentages": {"Suffolk": 50, "Cracker": 50}, "coat_type": "wool", "hair_percentage": 6},
    pen="Pen 5",
    weak_resistance=True,
    famacha_scores=[{"score": 4, "date": "2025-tag-day", "notes": "treated with iron"}],
    notes="Mom calls her 'Amure'. GG's full sister. On weak resistance list. 94% wool per Google Sheet. Suffolk Cross. In Pen 5 under Rocky. Also listed in Pen 2 sirloin at different time.",
    confidence="high",
    notebook_image=["IMG_8628.PNG", "IMG_8629.PNG", "IMG_8630.PNG"]))

# Elsie - ewe, tag 26
db["sheep"].append(sheep("elsie", "Elsie", "ewe", "alive",
    tag="026",
    pen="Pen 4",
    famacha_scores=[{"score": 1, "date": "2025-tag-day", "notes": "no treat needed"}],
    breed_composition={"primary": "Katahdin cross", "percentages": {"Katahdin": 65.625, "Awassi": 22, "East Friesian": 3, "St Augustine": 6.25, "ABB": 3.125}, "coat_type": "mixed", "hair_percentage": 65},
    notes="Tag 26. FAMACHA 1 (excellent). In Samson/pen 4 group per notebook. Google Sheet shows her in Pen 2 offspring calculations.",
    confidence="high",
    notebook_image=["IMG_8639.PNG", "IMG_8641.PNG"]))

# Nori - ewe, retagged 29
db["sheep"].append(sheep("nori", "Nori", "ewe", "alive",
    tag="029", aliases=["Tag 29"],
    pen="Pen 4",
    is_breeding_animal=True,
    offspring_ids=["nori-son"],
    breed_composition={"primary": "Cracker/ABB/Wiltshire", "percentages": {"Cracker": 50, "American Blackbelly": 25, "Wiltshire Horn": 25}, "coat_type": "hair", "hair_percentage": 75},
    notes="Retagged to 29. Mother of NoriSon (tag 54). In pen 4 (Samson group). From Google Sheet Pen 6 breed data.",
    confidence="high",
    notebook_image=["IMG_8641.PNG", "IMG_8642.PNG"]))

# Merrie - ewe, tag 016
db["sheep"].append(sheep("merrie", "Merrie", "ewe", "alive",
    tag="016",
    pen="Pen 1",
    famacha_scores=[{"score": 3, "date": "2025-tag-day", "notes": "treated"}],
    measurements={"measurement_1": 30, "measurement_2": 31, "date": "2025"},
    notes="Tag 016. FAMACHA 3, treated. In Pen 1 under Kaladin.",
    confidence="high",
    notebook_image=["IMG_8622.PNG", "IMG_8630.PNG", "IMG_8641.PNG"]))

# Bella - ewe, tag 27
db["sheep"].append(sheep("bella", "Bella", "ewe", "alive",
    tag="027",
    pen="Pen 3",
    weak_resistance=True,
    famacha_scores=[{"score": "good", "date": "2025-tag-day", "notes": "eyes good"}],
    notes="Tagged 27. Eyes good at tag day. In Pen 3. On weak resistance list.",
    confidence="high",
    notebook_image=["IMG_8628.PNG", "IMG_8641.PNG"]))

# Cinderella - ewe, tag 28
db["sheep"].append(sheep("cinderella", "Cinderella", "ewe", "alive",
    tag="028",
    pen="Pen 3",
    famacha_scores=[{"score": "good", "date": "2025-tag-day", "notes": "eyes good"}],
    notes="Tagged 28. Eyes good at tag day. In Pen 3.",
    confidence="high",
    notebook_image=["IMG_8641.PNG"]))

# Serendipity - ewe, tag 30
db["sheep"].append(sheep("serendipity", "Serendipity", "ewe", "alive",
    tag="030",
    pen="Pen 6",
    breed_composition={"primary": "Katahdin/St Augustine/Babydoll/Jacob", "percentages": {"Katahdin": 12.5, "St Augustine": 37.5, "Babydoll": 25, "Jacob": 25}, "coat_type": "mixed", "hair_percentage": 75},
    offspring_ids=["serendipitys-baby-036"],
    health_notes=["Low FAMACHA score 7-24-25 along with GG and Lara"],
    notes="Tag 30. In pen 6 (no ram). 75% hair per Google Sheet. Mother of Mc12/036 baby ewe. Low score noted 7-24-25.",
    confidence="high",
    notebook_image=["IMG_8629.PNG", "IMG_8632.PNG", "IMG_8640.PNG", "IMG_8642.PNG"]))

# Serendipity's baby - 036, Mc12
db["sheep"].append(sheep("serendipitys-baby-036", "Serendipity's Baby", "ewe", "alive",
    tag="036", mc_tag="Mc12",
    dam_id="serendipity",
    notes="036, Mc12. Serendipity's baby ewe. Photo from March 18, 2024 shows white lamb with yellow MC12 ear tag.",
    confidence="high",
    notebook_image=["IMG_8632.PNG"]))

# Little Daisy - ewe, tag 35
db["sheep"].append(sheep("little-daisy", "Little Daisy", "ewe", "alive",
    tag="035", aliases=["Daisy"],
    pen="Pen 5",
    offspring_ids=["little-daisys-baby-mc01"],
    health_notes=["Needed parasite treatment April 13 2025 - eyes were white (tag 35)"],
    notes="Tag 35. In pen 5 (Rocky group). Mother of Mc01 (baby's baby). Needed parasite treatment April 13, 2025 with white eyes.",
    confidence="high",
    notebook_image=["IMG_8625.PNG", "IMG_8627.PNG", "IMG_8629.PNG", "IMG_8635.PNG"]))

# Little Daisy's baby - Mc01 (baby's baby)
db["sheep"].append(sheep("little-daisys-baby-mc01", "Little Daisy's Baby (Mc01)", "ewe", "alive",
    mc_tag="Mc01", aliases=["Baby's baby"],
    dam_id="little-daisy",
    notes="Mc01. Called 'baby's baby' in notebook. Little Daisy #35's offspring.",
    confidence="high",
    notebook_image=["IMG_8627.PNG"]))

# Baby - ewe
db["sheep"].append(sheep("baby", "Baby", "ewe", "alive",
    pen="Pen 3",
    weak_resistance=True,
    breed_composition={"primary": "Suffolk Cross", "percentages": {"Suffolk": 50, "Cracker": 25, "Katahdin": 12.5, "Gulf Coast Native": 6.25, "Katahdin": 6.25}, "coat_type": "wool", "hair_percentage": 25},
    notes="In pen 3 (Sam group). On weak resistance list. Google Sheet Pen 2 shows her as Suffolk Cross ewe offspring calculation parent.",
    confidence="medium",
    notebook_image=["IMG_8628.PNG", "IMG_8629.PNG"]))

# Baby Momma - ewe
db["sheep"].append(sheep("baby-momma", "Baby Momma", "ewe", "alive",
    pen="Pen 3",
    notes="In pen 3 (Sam group).",
    confidence="medium",
    notebook_image=["IMG_8629.PNG"]))

# Zara - ewe
db["sheep"].append(sheep("zara", "Zara", "ewe", "alive",
    pen="Pen 3",
    breed_composition={"primary": "Dorper", "percentages": {"Dorper": 100}, "coat_type": "hair", "hair_percentage": 100},
    notes="In pen 3 (Sam group). Pure Dorper per Google Sheet Pen 4.",
    confidence="medium",
    notebook_image=["IMG_8629.PNG"]))

# Half Tail - ewe
db["sheep"].append(sheep("half-tail", "Half Tail", "ewe", "alive",
    pen="Pen 3",
    notes="In pen 3 (Sam group). From CSV as well - Ewe, 'Looks like Baby'.",
    confidence="medium",
    csv_row=15,
    notebook_image=["IMG_8629.PNG"]))

# Broken Tail - ewe
db["sheep"].append(sheep("broken-tail", "Broken Tail", "ewe", "alive",
    aliases=["Bt", "BT"],
    tag="034",
    pen="Pen 5",
    breed_composition={"primary": "Katahdin/St Augustine/Awassi/East Friesian", "percentages": {"Katahdin": 50, "St Augustine": 0, "Awassi": 22, "East Friesian": 3, "Dorper": 25}, "coat_type": "mixed", "hair_percentage": 75},
    notes="In pen 5 (Rocky group). Tag 34 from treatment list. 3/4 hair per Google Sheet Pen 3.",
    confidence="medium",
    csv_row=16,
    notebook_image=["IMG_8629.PNG", "IMG_8642.PNG"]))

# Trouble - ewe, tag 33
db["sheep"].append(sheep("trouble", "Trouble", "ewe", "alive",
    tag="033",
    pen="Pen 5",
    notes="Tag 33. In pen 5 treatment list.",
    confidence="medium",
    notebook_image=["IMG_8642.PNG"]))

# Bsoe - ewe, tag 32 (switch with 31)
db["sheep"].append(sheep("bsoe", "Bsoe", "ewe", "alive",
    tag="032",
    pen="Pen 5",
    notes="Tag 32 (switched with Bsoed's 31). In pen 5.",
    confidence="medium",
    notebook_image=["IMG_8642.PNG"]))

# Bsoed - ewe, tag 31
db["sheep"].append(sheep("bsoed", "Bsoed", "ewe", "alive",
    tag="031",
    pen="Pen 5",
    notes="Tag 31 (switched with Bsoe's 32). In pen 5.",
    confidence="medium",
    notebook_image=["IMG_8642.PNG"]))

# FM - ewe
db["sheep"].append(sheep("fm", "FM", "ewe", "alive",
    pen="Pen 1",
    weak_resistance=True,
    breed_composition={"primary": "Katahdin/Cotswold/Tunis", "percentages": {"Katahdin": 50, "Cotswold": 25, "Tunis": 25}, "coat_type": "mixed", "hair_percentage": 50},
    notes="In Pen 1 (Kaladin group). On weak resistance list. No treat at tag day. Google Sheet Pen 4 shows FM as 50% hair.",
    confidence="medium",
    csv_row=14,
    notebook_image=["IMG_8628.PNG", "IMG_8630.PNG", "IMG_8636.PNG", "IMG_8641.PNG"]))

# FM1 - ewe (different from FM)
db["sheep"].append(sheep("fm1", "FM1", "ewe", "alive",
    tag="009",
    pen="Pen 6",
    weak_resistance=True,
    measurements={"measurement_1": 23, "measurement_2": 29.5, "date": "2025"},
    notes="Different from FM. Tag 009. In pen 6 (no ram). On weak resistance list.",
    confidence="medium",
    notebook_image=["IMG_8624.PNG", "IMG_8628.PNG", "IMG_8629.PNG", "IMG_8642.PNG"]))

# Eclipse - ewe
db["sheep"].append(sheep("eclipse", "Eclipse", "ewe", "alive",
    pen="Pen 1",
    measurements={"measurement_1": 22.5, "measurement_2": 22, "date": "2025"},
    notes="In Pen 1 (Kaladin group).",
    confidence="medium",
    notebook_image=["IMG_8624.PNG", "IMG_8630.PNG"]))

# Abg - ewe, tag 22
db["sheep"].append(sheep("abg", "Abg", "ewe", "alive",
    tag="022",
    pen="Pen 1",
    notes="Tag 22 per treatment list (struck thru no treat). In Pen 1 (Kaladin group).",
    confidence="medium",
    notebook_image=["IMG_8630.PNG", "IMG_8641.PNG"]))

# Banana - ewe
db["sheep"].append(sheep("banana", "Banana", "ewe", "alive",
    pen="Pen 4",
    breed_composition={"primary": "Katahdin/St Augustine", "percentages": {"Katahdin": 62.5, "St Augustine": 37.5}, "coat_type": "hair", "hair_percentage": 62},
    sire_id="sir-loin",
    notes="In pen 4 (Samson group). From CSV: 62.5% Katahdin, 37.5% St Augustine. Sire: Sir Loin.",
    confidence="high",
    csv_row=5,
    notebook_image=["IMG_8629.PNG"]))

# Circle Tail - ewe
db["sheep"].append(sheep("circle-tail", "Circle Tail", "ewe", "alive",
    pen="Pen 6",
    weak_resistance=True,
    famacha_scores=[{"score": 5, "date": "2025-tag-day", "notes": "treated with iron also"}],
    notes="In pen 6 (no ram). On weak resistance list. FAMACHA 5, treated with iron.",
    confidence="medium",
    notebook_image=["IMG_8628.PNG", "IMG_8629.PNG", "IMG_8641.PNG"]))

# Fox Tail - ewe
db["sheep"].append(sheep("fox-tail", "Fox Tail", "ewe", "alive",
    pen="Pen 6",
    notes="In pen 6 (no ram).",
    confidence="medium",
    notebook_image=["IMG_8629.PNG"]))

# S1 - ewe
db["sheep"].append(sheep("s1", "S1", "ewe", "alive",
    pen="Pen 6",
    notes="In pen 6 (no ram).",
    confidence="low",
    notebook_image=["IMG_8629.PNG"]))

# S2 - ewe
db["sheep"].append(sheep("s2", "S2", "ewe", "alive",
    pen="Pen 2",
    notes="In pen 2 (sirloin group).",
    confidence="low",
    notebook_image=["IMG_8630.PNG"]))

# Lara - ewe
db["sheep"].append(sheep("lara", "Lara", "ewe", "alive",
    pen="Pen 2",
    health_notes=["One of Dorper 23 & 25 from sick sheep note", "Low score 7-24-25"],
    notes="In pen 2 (sirloin group). From sick sheep note: 'one of these is Lara'. Low FAMACHA score 7-24-25.",
    confidence="medium",
    notebook_image=["IMG_8626.PNG", "IMG_8630.PNG", "IMG_8636.PNG", "IMG_8640.PNG"]))

# Pebbles - ewe
db["sheep"].append(sheep("pebbles", "Pebbles", "ewe", "alive",
    pen="Pen 2",
    famacha_scores=[{"score": 3, "date": "2025-tag-day", "notes": "treated (struck thru)"}],
    notes="In pen 2 (sirloin group). FAMACHA 3, treated. Entry struck through in treatment list.",
    confidence="medium",
    notebook_image=["IMG_8630.PNG", "IMG_8641.PNG"]))

# Anna - ewe from CSV
db["sheep"].append(sheep("anna", "Anna", "ewe", "unknown",
    breed_composition={"primary": "Katahdin", "percentages": {"Katahdin": 100}, "coat_type": "hair", "hair_percentage": 100},
    weight_lbs=250, dob="2012-01-01", dob_approximate=True,
    dam_id="anna",
    notes="From CSV. Katahdin ewe, 250lbs. Status unknown - not found in recent notebook data.",
    confidence="low", csv_row=4))

# Boots - ewe, tag 006
db["sheep"].append(sheep("boots", "Boots", "ewe", "alive",
    tag="006",
    breed_composition={"primary": "Cracker/Barbados Blackbelly/St Augustine", "percentages": {"Cracker": 50, "Barbados Blackbelly": 25, "St Augustine": 25}, "coat_type": "hair", "hair_percentage": 75},
    notes="Tag 006. From CSV and measurement list. Cracker/BBB/St Augustine mix.",
    confidence="medium",
    csv_row=11,
    notebook_image=["IMG_8623.PNG"]))

# Patches - ewe
db["sheep"].append(sheep("patches", "Patches", "ewe", "alive",
    measurements={"outer": 27, "inner": 29, "measurement_1": 43.5, "measurement_2": 27, "date": "2025"},
    notes="From measurement list. Two sets of measurements recorded.",
    confidence="medium",
    notebook_image=["IMG_8624.PNG"]))

# Little Song - ewe, tag 008
db["sheep"].append(sheep("little-song", "Little Song", "ewe", "alive",
    tag="008",
    measurements={"measurement_1": 23, "measurement_2": 28, "date": "2025"},
    notes="Tag 008. From measurement list.",
    confidence="medium",
    notebook_image=["IMG_8624.PNG"]))

# Black Rock - tag 010
db["sheep"].append(sheep("black-rock", "Black Rock", "ewe", "alive",
    tag="010",
    notes="Tag 010. From measurement list. No measurements recorded yet.",
    confidence="low",
    notebook_image=["IMG_8624.PNG"]))

# Question Tail - tag 001
db["sheep"].append(sheep("question-tail", "Question Tail", "ewe", "alive",
    tag="001",
    measurements={"measurement_1": 25, "measurement_2": 32, "date": "2025"},
    notes="Tag 001. From measurement list.",
    confidence="medium",
    notebook_image=["IMG_8622.PNG"]))

# Female 004
db["sheep"].append(sheep("female-004", "Female 004", "ewe", "alive",
    tag="004",
    measurements={"measurement_1": 27.5, "measurement_2": 25.5, "date": "2025"},
    notes="Tag 004. From measurement list.",
    confidence="medium",
    notebook_image=["IMG_8622.PNG"]))

# Half Tail's Baby - tag 007
db["sheep"].append(sheep("half-tails-baby", "Half Tail's Baby", "ewe", "alive",
    tag="007",
    dam_id="half-tail",
    measurements={"measurement_1": 27.5, "measurement_2": 27.5, "date": "2025"},
    notes="Tag 007. Half Tail's baby. From measurement list.",
    confidence="medium",
    notebook_image=["IMG_8622.PNG"]))

# Sb1 (crown) - tag 002
db["sheep"].append(sheep("sb1-crown", "Sb1 (Crown)", "ewe", "alive",
    tag="002",
    measurements={"measurement_1": 25.25, "measurement_2": 32, "date": "2025"},
    notes="Tag 002. Called 'Sb1 (crown)' in measurements.",
    confidence="medium",
    notebook_image=["IMG_8623.PNG"]))

# Sb2 (all black) - tag 003
db["sheep"].append(sheep("sb2-all-black", "Sb2 (All Black)", "ewe", "alive",
    tag="003",
    color_markings="all black",
    measurements={"measurement_1": 25, "measurement_2": 31.5, "date": "2025"},
    notes="Tag 003. Called 'Sb2 (all black)' in measurements.",
    confidence="medium",
    notebook_image=["IMG_8623.PNG"]))

# New Big Girl 2 - ewe
db["sheep"].append(sheep("new-big-girl-2", "New Big Girl 2", "ewe", "alive",
    pen="Pen 3",
    notes="In pen 3 (Sam group).",
    confidence="low",
    notebook_image=["IMG_8629.PNG"]))

# Daisy's Daughter (1 and 2 - from Google Sheet)
db["sheep"].append(sheep("daisys-daughter-1", "Daisy's Daughter 1", "ewe", "alive",
    breed_composition={"primary": "St Augustine/Katahdin/BBB", "percentages": {"St Augustine": 67.9625, "Katahdin": 27.325, "Barbados Blackbelly": 4.7}, "coat_type": "mixed", "hair_percentage": 30},
    notes="From Google Sheet Pen 6 breed calculations. Different from Daisy's Daughter 2.",
    confidence="low"))

db["sheep"].append(sheep("daisys-daughter-2", "Daisy's Daughter 2", "ewe", "alive",
    breed_composition={"primary": "St Augustine/Katahdin/BBB/Wiltshire", "percentages": {"St Augustine": 67.9625, "Katahdin": 27.325, "Barbados Blackbelly": 4.7, "Wiltshire Horn": 0}, "coat_type": "mixed", "hair_percentage": 30},
    pen="Pen 5",
    notes="From Google Sheet Pen 5 and 6. In NoriSon's group. Different from Daisy's Daughter 1.",
    confidence="low",
    notebook_image=[]))

# Gertude - from Google Sheet Pen 5
db["sheep"].append(sheep("gertrude", "Gertrude", "ewe", "alive",
    pen="Pen 5",
    breed_composition={"primary": "ABB/St Augustine/Katahdin/Wiltshire", "percentages": {"American Blackbelly": 25, "St Augustine": 37.5, "Katahdin": 12.5, "Wiltshire Horn": 25}, "coat_type": "hair", "hair_percentage": 62},
    notes="From Google Sheet Pen 5 breed data. NoriSon's group.",
    confidence="low"))

# OAV 2222 - from Google Sheet Pen 5
db["sheep"].append(sheep("oav-2222", "OAV 2222", "ewe", "alive",
    tag="2222", aliases=["2222"],
    pen="Pen 5",
    breed_composition={"primary": "Katahdin/St Augustine/ABB/Wiltshire/BBB", "percentages": {"Katahdin": 100}, "coat_type": "hair", "hair_percentage": 100},
    notes="From Google Sheet Pen 5. Tag 2222. Also mentioned in NoriSon's notebook page.",
    confidence="low",
    notebook_image=["IMG_8639.PNG"]))

# Heather Oaks - from Google Sheet Pen 5
db["sheep"].append(sheep("heather-oaks", "Heather Oaks", "ewe", "alive",
    pen="Pen 5",
    breed_composition={"primary": "Katahdin/Dorper/ABB/St Augustine/Wiltshire", "percentages": {"Katahdin": 37.5, "Dorper": 25, "American Blackbelly": 12.5, "St Augustine": 6.25, "Wiltshire Horn": 12.5}, "coat_type": "mixed", "hair_percentage": 75},
    notes="From Google Sheet Pen 5 breed data.",
    confidence="low"))

# Tag 31 - from Google Sheet Pen 2
db["sheep"].append(sheep("tag-31-ewe", "Tag 31", "ewe", "alive",
    tag="031-pen2",
    breed_composition={"primary": "Katahdin/St Augustine/Dorper/BBB", "percentages": {"Katahdin": 28.125, "St Augustine": 56.5, "Dorper": 25, "Barbados Blackbelly": 6.125}, "coat_type": "mixed", "hair_percentage": 31},
    notes="From Google Sheet Pen 2. 69.25% wool. Different from Bsoed tag 31 in pen 5.",
    confidence="low"))

# Tag 33 - from Google Sheet Pen 1
db["sheep"].append(sheep("tag-33", "Tag 33", "ewe", "alive",
    tag="033-pen1",
    breed_composition={"primary": "Katahdin/St Augustine/BBB/Cracker/White Dorper/Suffolk/GCN", "coat_type": "mixed", "hair_percentage": 25},
    notes="From Google Sheet Pen 1. 3/4 hair. Has twins.",
    confidence="low"))

# Tag 35 - from Google Sheet Pen 3
db["sheep"].append(sheep("tag-35-ewe", "Tag 35", "ewe", "alive",
    tag="035-pen3",
    breed_composition={"primary": "Katahdin/St Augustine/Awassi/East Friesian", "percentages": {"Katahdin": 29.75, "St Augustine": 70.25, "Awassi": 22, "East Friesian": 3}, "coat_type": "mixed", "hair_percentage": 75},
    notes="From Google Sheet Pen 3. Broken Tail x Buck. 3/4 hair.",
    confidence="low"))

# Bambi - tag 37
db["sheep"].append(sheep("bambi", "Bambi", "ewe", "alive",
    tag="037",
    pen="Pen 3",
    breed_composition={"primary": "Katahdin/Dorper/Awassi/East Friesian", "percentages": {"Katahdin": 50, "Dorper": 50, "Awassi": 22, "East Friesian": 3}, "coat_type": "mixed", "hair_percentage": 75},
    notes="Tag 37. Google Sheet Pen 3 shows 3/4 hair. Broken Tail x Buck. Also appears in pen 2 sirloin notebook list.",
    confidence="medium",
    notebook_image=["IMG_8624.PNG", "IMG_8630.PNG"]))

# Irish - Little Daisy's daughter
db["sheep"].append(sheep("irish", "Irish", "ewe", "alive",
    dam_id="little-daisy",
    health_notes=["Needed parasite treatment April 13 2025 - eyes better but still worthy of treating, maybe a 2"],
    notes="Little Daisy's daughter. Needed parasite treatment April 13, 2025. Eyes better than Daisy but still scored ~2.",
    confidence="medium",
    notebook_image=["IMG_8635.PNG"]))

# Unnamed - in pen 2
db["sheep"].append(sheep("unnamed-pen2", "Unnamed (Pen 2)", "ewe", "alive",
    pen="Pen 2",
    notes="Unnamed ewe in pen 2 (sirloin group). Not the same as the deceased 'Unnamed' on the weak resistance list.",
    confidence="low",
    notebook_image=["IMG_8630.PNG"]))

# ============================================================
# DECEASED / SOLD
# ============================================================

db["sheep"].append(sheep("shaggy", "Shaggy", "ewe", "deceased",
    pen="Pen 6",
    weak_resistance=True,
    famacha_scores=[{"score": 4, "date": "2025-tag-day", "notes": "no treat (struck thru)"}],
    breed_composition={"primary": "Katahdin", "percentages": {"Katahdin": 100}, "coat_type": "hair", "hair_percentage": 100},
    notes="Deceased per weak resistance list. Was in pen 6. From CSV: purebred Katahdin.",
    confidence="high",
    csv_row=12,
    notebook_image=["IMG_8628.PNG", "IMG_8629.PNG", "IMG_8641.PNG"]))

db["sheep"].append(sheep("bambii", "Bambii", "ewe", "deceased",
    pen="Pen 2",
    notes="Struck through in treatment list, indicating deceased or removed. Was in pen 2 sirloin group.",
    confidence="medium",
    notebook_image=["IMG_8630.PNG", "IMG_8641.PNG"]))

db["sheep"].append(sheep("skitters", "Skitters", "ewe", "deceased",
    breed_composition={"primary": "Karakul cross", "percentages": {"Karakul": 50}, "coat_type": "mixed"},
    weak_resistance=True,
    notes="Deceased. Karakul cross. On weak resistance list.",
    confidence="high",
    notebook_image=["IMG_8628.PNG"]))

db["sheep"].append(sheep("w136", "W136", "ewe", "deceased",
    weak_resistance=True,
    notes="Deceased. On weak resistance list.",
    confidence="high",
    notebook_image=["IMG_8628.PNG"]))

db["sheep"].append(sheep("unnamed-deceased", "Unnamed (Deceased)", "unknown", "deceased",
    weak_resistance=True,
    notes="Deceased. On weak resistance list as 'Unnamed (deceased)'.",
    confidence="low",
    notebook_image=["IMG_8628.PNG"]))

db["sheep"].append(sheep("hersheys", "Hersheys", "ewe", "deceased",
    breed_composition={"primary": "Katahdin/St Augustine", "percentages": {"Katahdin": 62.5, "St Augustine": 37.5}, "coat_type": "hair", "hair_percentage": 62},
    notes="From CSV. Deceased. Katahdin/St Augustine mix.",
    confidence="high", csv_row=13))

db["sheep"].append(sheep("gg-daughter-45", "GG's Daughter", "ewe", "deceased",
    tag="045",
    dam_id="gg",
    notes="GG's daughter. Tag 45. Deceased.",
    confidence="high",
    notebook_image=["IMG_8634.PNG"]))

db["sheep"].append(sheep("lara-daughter-46", "Lara's Daughter", "ewe", "sold",
    tag="046",
    dam_id="gg",
    status_notes="Sold - prone to Coccidia",
    notes="GG/Lara's daughter. Tag 46. Sold because prone to Coccidia.",
    confidence="high",
    notebook_image=["IMG_8634.PNG"]))

db["sheep"].append(sheep("gg-son-094", "GG's Son", "ram", "deceased",
    tag="094",
    sire_id="gg",
    notes="GG's son. Tag 094. Deceased.",
    confidence="high",
    notebook_image=["IMG_8634.PNG"]))

db["sheep"].append(sheep("dorper-ram-deceased", "Dorper Ram (Deceased)", "ram", "deceased",
    breed_composition={"primary": "Dorper", "percentages": {"Dorper": 100}, "coat_type": "hair", "hair_percentage": 100},
    treatments=[{"date": "2024-10-24", "treatment": "iron and vitamin B"}],
    notes="Dorper ram from sick sheep note. Given iron and B on 10-24. Deceased.",
    confidence="medium",
    notebook_image=["IMG_8626.PNG"]))

db["sheep"].append(sheep("w140", "W140", "ewe", "alive",
    weak_resistance=True,
    notes="On weak resistance list. Status alive but weak.",
    confidence="low",
    notebook_image=["IMG_8628.PNG"]))

# ============================================================
# ADDITIONAL FROM CSV
# ============================================================

db["sheep"].append(sheep("brown-knee", "Brown Knee", "ewe", "unknown",
    breed_composition={"primary": "Katahdin/St Augustine", "percentages": {"Katahdin": 62.5, "St Augustine": 37.5}, "coat_type": "hair", "hair_percentage": 62},
    sire_id="sir-loin",
    notes="From CSV. Katahdin/St Augustine mix. Sire: Sir Loin. Status unknown - not in recent notebook.",
    confidence="low", csv_row=6))

db["sheep"].append(sheep("black-spot-on-ear", "Black Spot on Ear", "ewe", "unknown",
    breed_composition={"primary": "Katahdin/St Augustine", "percentages": {"Katahdin": 62.5, "St Augustine": 37.5}, "coat_type": "hair", "hair_percentage": 62},
    sire_id="sir-loin",
    notes="From CSV. Status unknown.",
    confidence="low", csv_row=7))

db["sheep"].append(sheep("banana-split", "Banana Split", "ewe", "unknown",
    breed_composition={"primary": "Katahdin/St Augustine", "percentages": {"Katahdin": 62.5, "St Augustine": 37.5}, "coat_type": "hair", "hair_percentage": 62},
    sire_id="sir-loin",
    notes="From CSV. Status unknown.",
    confidence="low", csv_row=8))

db["sheep"].append(sheep("fleecity", "Fleecity", "ewe", "unknown",
    breed_composition={"primary": "Katahdin/Cracker", "percentages": {"Katahdin": 50, "Cracker": 50}, "coat_type": "mixed", "hair_percentage": 50},
    notes="From CSV. Status unknown.",
    confidence="low", csv_row=10))

# Dorper 23 and 25 from weak resistance list
db["sheep"].append(sheep("dorper-23", "Dorper 23", "ewe", "alive",
    tag="023",
    breed_composition={"primary": "Dorper", "percentages": {"Dorper": 100}, "coat_type": "hair", "hair_percentage": 100},
    weak_resistance=True,
    treatments=[{"date": "2024-10-24", "treatment": "iron and vitamin B"}],
    notes="From weak resistance list and sick sheep note. Dorper ewe. Tag 23. Struck thru in treatment list.",
    confidence="medium",
    notebook_image=["IMG_8626.PNG", "IMG_8628.PNG", "IMG_8641.PNG"]))

db["sheep"].append(sheep("dorper-25", "Dorper 25", "ewe", "alive",
    tag="025",
    breed_composition={"primary": "Dorper", "percentages": {"Dorper": 100}, "coat_type": "hair", "hair_percentage": 100},
    weak_resistance=True,
    treatments=[{"date": "2024-10-24", "treatment": "iron and vitamin B"}],
    notes="From weak resistance list and sick sheep note. Dorper ewe. Tag 25 (no tag per treatment list). Struck thru.",
    confidence="medium",
    notebook_image=["IMG_8626.PNG", "IMG_8628.PNG", "IMG_8641.PNG"]))

# FM2 from Google Sheet
db["sheep"].append(sheep("fm2", "FM2", "ewe", "alive",
    breed_composition={"primary": "Katahdin/St Augustine/Cotswold/Tunis", "percentages": {"Katahdin": 12.5, "St Augustine": 37.5, "Cotswold": 25, "Tunis": 25}, "coat_type": "mixed", "hair_percentage": 25},
    notes="From Google Sheet Pen 4. FM2 Baby is 75% hair.",
    confidence="low"))

# Dorpy from Google Sheet
db["sheep"].append(sheep("dorpy", "Dorpy", "ewe", "alive",
    breed_composition={"primary": "Katahdin/Dorper/Babydoll", "percentages": {"Katahdin": 50, "Dorper": 25, "Babydoll": 25}, "coat_type": "mixed", "hair_percentage": 75},
    notes="From Google Sheet Pen 4. Tag 34 offspring row.",
    confidence="low"))

# Tag 34 from Google Sheet Pen 4
db["sheep"].append(sheep("tag-34-pen4", "Tag 34 (Pen 4)", "ewe", "alive",
    breed_composition={"primary": "Katahdin/St Augustine", "percentages": {"Katahdin": 43.75, "St Augustine": 56.25}, "coat_type": "mixed", "hair_percentage": 100},
    notes="From Google Sheet Pen 4. 100% hair.",
    confidence="low"))

# ============================================================
# PEN ASSIGNMENTS (from spiral notebook - most current)
# ============================================================

db["pens"] = {
    "pen_1": {
        "ram": "kaladin",
        "ewes": ["eclipse", "merrie", "abg", "fm"],
        "notes": "Kaladin's group. May 14 2025: vaccinated pen 1 lambs."
    },
    "pen_2": {
        "ram": "sir-loin",
        "ewes": ["azure", "s2", "lara", "bambii", "unnamed-pen2", "pebbles"],
        "notes": "Sirloin's group. Azure also listed in pen 5 at different time. Bambii may be deceased."
    },
    "pen_3": {
        "ram": "sam",
        "ewes": ["baby", "baby-momma", "zara", "half-tail", "new-big-girl-2"],
        "notes": "Sam's group. Bella (tag 27) and Cinderella (tag 28) also in pen 3 per treatment notes."
    },
    "pen_4": {
        "ram": "samson",
        "ewes": ["elsie", "nori", "trouble", "bsoe", "bsoed", "banana"],
        "notes": "Samson's group (Samson may be deceased - replaced?). Pen 4 also home to Kelsier and GG per Google Sheet."
    },
    "pen_5": {
        "ram": "rocky",
        "ewes": ["azure", "broken-tail", "little-daisy"],
        "notes": "Rocky's group. NoriSon (tag 54) also in pen 5. Notebook shows this is current arrangement."
    },
    "pen_6": {
        "ram": None,
        "ewes": ["shaggy", "serendipity", "s1", "fm1", "fox-tail", "circle-tail"],
        "notes": "No ram. Shaggy deceased. Jerkface (Awassi ram) was here for treatment."
    },
    "goose_pen": {
        "ram": None,
        "ewes": [],
        "notes": "Auction lambs: tags 09, 50, 06, L19, and others."
    }
}

# ============================================================
# 2026 LAMBING RECORDS (from flock_record_v2.xlsx)
# ============================================================

db["lambing_records_2026"] = [
    {"date": "2026-01-20", "dam": "Broken Tail", "sire": "[UNCLEAR]", "lambs_born": 2, "lambs_alive": 2, "notes": "Twins", "pen": "Pen 2"},
    {"date": "2026-01-23", "dam": "Elsie", "sire": "[UNCLEAR]", "lambs_born": 2, "lambs_alive": 2, "notes": "Twins (EH = ewe healthy)", "pen": "Pen 4"},
    {"date": "2026-01-25", "dam": "Nori", "sire": "[UNCLEAR]", "lambs_born": 1, "lambs_alive": 1, "notes": "EH", "pen": "Pen 4"},
    {"date": "2026-01-27", "dam": "Tag 33", "sire": "[UNCLEAR]", "lambs_born": 2, "lambs_alive": 2, "notes": "Twins (Ew = ewe)", "pen": "Pen 1"},
    {"date": "2026-01-28", "dam": "Zara", "sire": "[UNCLEAR]", "lambs_born": 1, "lambs_alive": 1, "notes": "EH", "pen": "Pen 3"},
    {"date": "2026-01-29", "dam": "Azure", "sire": "[UNCLEAR]", "lambs_born": 1, "lambs_alive": 1, "notes": "Renamed Amure in notes", "pen": "Pen 2"},
    {"date": "2026-01-30", "dam": "Dorpy", "sire": "[UNCLEAR]", "lambs_born": 1, "lambs_alive": 1, "notes": "Dorper/Katahdin cross", "pen": "Pen 4"},
    {"date": "2026-02-01", "dam": "FM", "sire": "[UNCLEAR]", "lambs_born": 1, "lambs_alive": 1, "notes": "", "pen": "Pen 4"},
    {"date": "2026-02-02", "dam": "Tag 34", "sire": "[UNCLEAR]", "lambs_born": 1, "lambs_alive": 1, "notes": "Fm2", "pen": "Pen 4"},
    {"date": "2026-02-03", "dam": "Serendipity", "sire": "[UNCLEAR]", "lambs_born": 1, "lambs_alive": 1, "notes": "", "pen": "Pen 5"},
    {"date": "2026-02-05", "dam": "Gigi", "sire": "[UNCLEAR]", "lambs_born": 1, "lambs_alive": 1, "notes": "GG's lamb (Ew)", "pen": ""},
    {"date": "2026-02-07", "dam": "Daisy's Daughter 2", "sire": "[UNCLEAR]", "lambs_born": 1, "lambs_alive": 1, "notes": "", "pen": "Pen 5"},
    {"date": "2026-02-10", "dam": "OAV 2222", "sire": "[UNCLEAR]", "lambs_born": 2, "lambs_alive": 2, "notes": "Twins", "pen": "Pen 5"},
    {"date": "2026-02-13", "dam": "Tag 31", "sire": "[UNCLEAR]", "lambs_born": 1, "lambs_alive": 1, "notes": "FM", "pen": ""}
]

# ============================================================
# FINALIZE COUNTS
# ============================================================

total = len(db["sheep"])
alive = sum(1 for s in db["sheep"] if s["status"] == "alive")
deceased = sum(1 for s in db["sheep"] if s["status"] == "deceased")
sold = sum(1 for s in db["sheep"] if s["status"] == "sold")
unknown = sum(1 for s in db["sheep"] if s["status"] == "unknown")

db["meta"]["total_sheep"] = total
db["meta"]["active_sheep"] = alive
db["meta"]["deceased_count"] = deceased
db["meta"]["sold_count"] = sold
db["meta"]["unknown_count"] = unknown

# Write database
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(DB_PATH, "w") as f:
    json.dump(db, f, indent=2)

print(f"Flock database created at {DB_PATH}")
print(f"  Total records: {total}")
print(f"  Alive: {alive}")
print(f"  Deceased: {deceased}")
print(f"  Sold: {sold}")
print(f"  Unknown: {unknown}")
print(f"  Pens: {len(db['pens'])}")
print(f"  Lambing records 2026: {len(db['lambing_records_2026'])}")
