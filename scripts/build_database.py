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
            "Sheep_Breeding_DB_CURRENT_COPY.xlsx",
            "comprehensive_flock_spreadsheet (Feb 2026)"
        ],
        "primary_source": "spiral_notebook",
        "notes": "Spiral notebook images are the most current for pen assignments and status. Comprehensive flock spreadsheet is authoritative for breed compositions, parentage, DOBs, and weights. BBB lineage flows through Razzle(100BBB) x Frazzle(100K) -> Sugar(50BBB/50K) -> Hersheys(25BBB/37.5K/37.5SA) -> Half Tail(12.5BBB) -> downstream. BSOE dam is Two Pence (not Brown Knee). Anna's Big One = Banana in notebook."
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
    tag="2",
    aliases=["Sirloin", "SL"],
    breed_composition={"primary": "St Augustine/Katahdin", "percentages": {"St Augustine": 75, "Katahdin": 25}, "coat_type": "mixed", "hair_percentage": 25},
    color_markings="White",
    weight_lbs=309, dob="2012-01-01", dob_approximate=True,
    pen="Pen 2", is_breeding_animal=True,
    measurements={"girth": 43.25, "length": 49.5, "calculated_weight": 308.6, "date": "2023-2024"},
    notes="Flock spreadsheet: Tag 2, 75% St Augustine / 25% Katahdin. Sire: Chip, Dam: Shirley (off-farm). Primary herd sire. Weight calculator: 308.6lbs (girth 43.25, length 49.5). Pen 2 per notebook.",
    confidence="high", csv_row=1,
    offspring_ids=["annas-big-one", "half-tail", "broken-tail", "hersheys", "bsoe", "bsoed", "elsie", "little-song", "ab1"]))

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

# Rocky / Rock / Jerkface - 44%Awassi/50%BHD/6%EF ram — Pen 5 per notebook
# CLAUDE.md confirms: "Rock" = "Jerkface" = Awassi ram. These are the same animal.
# Notebook is authoritative: Rocky is the Pen 5 ram. Pen 6 has no ram.
db["sheep"].append(sheep("rocky", "Rocky", "ram", "alive",
    aliases=["Rock", "Jerkface", "Awassi ram", "Awassi cross rock"],
    breed_composition={"primary": "Black Headed Dorper/Awassi/East Friesian", "percentages": {"Awassi": 44, "Black Headed Dorper": 50, "East Friesian": 6}, "coat_type": "mixed", "hair_percentage": 50},
    weight_lbs=300,
    pen="Pen 2",
    is_breeding_animal=True,
    weak_resistance=True,
    famacha_scores=[{"score": 5, "date": "2025-10-23"}],
    treatments=[{"date": "2024-10-24", "treatment": "iron and vitamin B"}],
    notes="Also called Jerkface/Rock. 44%Awassi/50%BHD/6%EF per Rocky breeding page. Ram weight 300lbs, ewe weight prediction 200lbs. Had sick episode 10-23-23. Treated with iron. Pen 2 per owner. On weak resistance list. On 'Rams to Upgrade' list. Half wool.",
    confidence="high",
    notebook_image=["IMG_8626.PNG", "IMG_8628.PNG", "IMG_8629.PNG", "IMG_8641.PNG"]))

# Samson - ram (deceased per weak resistance list)
db["sheep"].append(sheep("samson", "Samson", "ram", "deceased",
    pen="Pen 4",
    weak_resistance=True,
    is_breeding_animal=True,
    notes="Was ram for Pen 4 group (Elsie, Nori, Trouble, Bsoe, Bsoed, Banana). Deceased per weak resistance list. Pen 4 entry says 'Samson 4'.",
    confidence="medium",
    notebook_image=["IMG_8628.PNG", "IMG_8629.PNG"]))

# Sam - ram for Pen 3 (100% Gulf Coast Native)
db["sheep"].append(sheep("sam", "Sam", "ram", "alive",
    pen="Pen 3",
    breed_composition={"primary": "Gulf Coast Native", "percentages": {"Gulf Coast Native": 100}, "coat_type": "wool", "hair_percentage": 0},
    is_breeding_animal=True,
    treatments=[{"date": "2025-tag-day", "treatment": "iron (FAMACHA 3)"}],
    notes="Ram for pen 3 group. 100% Gulf Coast Native per Merrie breeding page. Given iron treatment. Pen 3 includes: Baby, Baby momma, Zara, Half tail, New big girl 2.",
    confidence="high",
    notebook_image=["IMG_8641.PNG"]))

# Kaladin - ram for Pen 1 (S'More x Serendipity)
# NOTE: Living Kaladin (tag 014) is S'More x Serendipity. The deceased Kaladin (tag 24)
# was S'More x Anna = 50Cr/50K. Breeding page math for Merrie confirms this Kaladin
# has Babydoll and Jacob from Serendipity's side (via Shaggy).
db["sheep"].append(sheep("kaladin", "Kaladin", "ram", "alive",
    tag="014",
    aliases=["Kal"],
    pen="Pen 1",
    breed_composition={"primary": "Cracker/St Augustine/Babydoll/Jacob/Katahdin", "percentages": {"Cracker": 50, "St Augustine": 18.75, "Babydoll": 12.5, "Jacob": 12.5, "Katahdin": 6.25}, "coat_type": "mixed", "hair_percentage": 56},
    color_markings="White w black ears",
    sire_id="smore", dam_id="serendipity",
    is_breeding_animal=True,
    weight_lbs=52,
    measurements={"girth": 26, "length": 23, "calculated_weight": 51.8, "date": "2023-2024"},
    notes="Living Kaladin tag 014. S'More (100%Cr) x Serendipity (25%Babydoll/25%Jacob/12.5%K/37.5%SA). Breed: 50%Cr/18.75%SA/12.5%Babydoll/12.5%Jacob/6.25%K. Weight calculator: 51.8lbs. The deceased Kaladin (tag 24) was S'More x Anna = 50Cr/50K — different animal. With Eclipse, Merrie, Abg, Fm.",
    confidence="high",
    notebook_image=["IMG_8624.PNG", "IMG_8630.PNG"]))

# S'More - Cracker ram from CSV (parents: Gigantus x Minnie, off-farm)
db["sheep"].append(sheep("smore", "S'More", "ram", "deceased",
    tag="22",
    breed_composition={"primary": "Cracker", "percentages": {"Cracker": 100}, "coat_type": "mixed", "hair_percentage": 50},
    color_markings="Red",
    weight_lbs=200, dob="2021-01-14", dob_approximate=True,
    is_breeding_animal=True,
    offspring_ids=["kaladin", "merrie"],
    notes="Flock spreadsheet: Tag 22, 100% Cracker, 200lbs. Sire: Gigantus, Dam: Minnie (off-farm). Deceased per spreadsheet. Was major breeding ram - sired many 2023 lambs including Pippen, Merrie (by Half Tail), Danny's Girl, Circle Tail, BK1, BK2, HT1, anna1, BT1/BT2, Shaggy1, Shaggy2, BSOE1, BSOE2, Boots1, and Kaladin (by Serendipity). The deceased Kaladin (tag 24) was S'More x Anna.",
    confidence="high", csv_row=2))

# Well Done - Katahdin ram from CSV (parents: Big Daddy x Gulf, off-farm)
db["sheep"].append(sheep("well-done", "Well Done", "ram", "deceased",
    tag="8",
    breed_composition={"primary": "Katahdin", "percentages": {"Katahdin": 100}, "coat_type": "hair", "hair_percentage": 100},
    color_markings="Black",
    weight_lbs=175, dob="2021-02-14", dob_approximate=True,
    is_breeding_animal=True,
    offspring_ids=["stew", "elsie"],
    status_notes="Culled - did not pass on his parasite resistance well",
    notes="Flock spreadsheet: Tag 8, 100% Katahdin, 175lbs. Sire: Big Daddy, Dam: Gulf (off-farm). Father of Stew (by Fleecity) and Elsie (by Half Tail). Culled per Breeding DB.",
    confidence="high", csv_row=3))

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
    weight_lbs=36,
    measurements={"girth": 22, "length": 22.5, "calculated_weight": 36.3, "date": "2023-2024"},
    notes="Photos from March 18, 2024. Also called Mc11 or tag 12. White lamb with yellow ear tag in photos. Weight calculator: 36.3lbs.",
    confidence="high",
    notebook_image=["IMG_8624.PNG", "IMG_8631.PNG"]))

# Pippin - ram, tag 015
db["sheep"].append(sheep("pippin", "Pippin", "ram", "alive",
    tag="015",
    weight_lbs=80,
    measurements={"girth": 28, "length": 30.75, "calculated_weight": 80.4, "date": "2023-2024"},
    notes="Ram from measurement list. Weight calculator: 80.4lbs (girth 28, length 30.75).",
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

# Buck - ram in chicken coop (Katahdin/Awassi/East Friesian)
# From Nori breeding page prospective offspring: Buck contributes ~48%Awassi/50%K/2%EF
db["sheep"].append(sheep("buck", "Buck", "ram", "alive",
    breed_composition={"primary": "Katahdin/Awassi/East Friesian", "percentages": {"Katahdin": 50, "Awassi": 48, "East Friesian": 2}, "coat_type": "mixed", "hair_percentage": 50},
    pen="Chicken Coop",
    is_breeding_animal=True,
    notes="Ram in chicken coop per owner. Katahdin/Awassi/EF. Breed derived from Nori breeding page prospective offspring (25ABB/24Awassi/1EF/25K/25WH offspring with Nori means Buck ~50K/48Awassi/2EF). Bred to Nori in 2024 — Nori's lamb born 1-6-25, birth weight 12lbs.",
    confidence="high"))

# Nori's 2024 lamb (by Buck, born 1-6-25)
db["sheep"].append(sheep("nori-2024-lamb", "Nori's 2024 Lamb", "unknown", "alive",
    dob="2025-01-06",
    sire_id="buck", dam_id="nori",
    notes="Born 1-6-25, birth weight 12lbs. Sired by Buck. From Nori breeding page.",
    confidence="high"))

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

# Azure (Amure) - ewe — NOT "Amber" in weight calc (that was Skitters/Karakul)
db["sheep"].append(sheep("azure", "Azure", "ewe", "alive",
    tag="024", aliases=["Amure", "Amber 24"],
    breed_composition={"primary": "Suffolk Cross", "percentages": {"Suffolk": 50, "Cracker": 50}, "coat_type": "wool", "hair_percentage": 6},
    pen="Pen 5",
    weak_resistance=True,
    famacha_scores=[{"score": 4, "date": "2025-tag-day", "notes": "treated with iron"}],
    notes="Mom calls her 'Amure'. GG's full sister. On weak resistance list. 94% wool per Google Sheet. Suffolk Cross. In Pen 5 / also in Pen 2 at different time. NOTE: 'Amber' in weight calculator is Skitters (Karakul), not Azure.",
    confidence="high",
    notebook_image=["IMG_8628.PNG", "IMG_8629.PNG", "IMG_8630.PNG"]))

# Elsie - ewe, tag 25 (Well Done x Half Tail)
db["sheep"].append(sheep("elsie", "Elsie", "ewe", "alive",
    tag="025",
    pen="Pen 6",
    famacha_scores=[{"score": 1, "date": "2023-09-06"}, {"score": 1, "date": "2023-09-18"}],
    breed_composition={"primary": "Katahdin/St Augustine/BBB", "percentages": {"Katahdin": 65.625, "St Augustine": 28.125, "Barbados Blackbelly": 6.25}, "coat_type": "hair", "hair_percentage": 72},
    color_markings="Black w White",
    weight_lbs=140, dob="2022-02-08",
    sire_id="well-done", dam_id="half-tail",
    offspring_ids=["rorshach", "rorshach-sister"],
    notes="Breeding page: Tag 25, 6.25%ABB(BBB)/65.625%K/28.125%SA. DOB 2/8/2022. Well Done (100K) x Half Tail (12.5BBB/31.25K/56.25SA). Ewe weight 140lbs. Black w White. Birth weight 12lbs, ADG 0.558. Offspring 2023: Rorshach and sister (by Sir Loin, mated Aug 17). FAMACHA 1 (9-6-23 and 9-18-23). Now in Pen 6 with triplets. Lambed 2026-01-23 (triplets).",
    confidence="high",
    notebook_image=["IMG_8639.PNG", "IMG_8641.PNG"]))

# Nori - ewe, tag 21 (tag lost) — 50%ABB/50%WH per breeding page
db["sheep"].append(sheep("nori", "Nori", "ewe", "alive",
    tag="021", aliases=["Tag 29", "No", "Tag 21"],
    pen="Pen 4",
    is_breeding_animal=True,
    offspring_ids=["nori-son", "eclipse", "nori-2024-lamb"],
    breed_composition={"primary": "ABB/Wiltshire Horn", "percentages": {"American Blackbelly": 50, "Wiltshire Horn": 50}, "coat_type": "hair", "hair_percentage": 100},
    color_markings="Badger",
    weight_lbs=139, dob="2023-02-01",
    notes="Nori breeding page: 50%ABB/50%WH, tag 21 (tag lost). Ewe weight 138.83lbs, ram weight 217.5lbs. Sire: 100%ABB, Dam: 100%WH. DOB ~2/1/2023. Mother of NoriSon (tag 54), Eclipse (2022, deceased Hurricane Idalia), and 2024 lamb (by Buck, born 1-6-25, birth weight 12lbs). In pen 4.",
    confidence="high",
    notebook_image=["IMG_8641.PNG", "IMG_8642.PNG"]))

# Merrie - ram, tag 016 (S'More x Half Tail)
db["sheep"].append(sheep("merrie", "Merrie", "ram", "alive",
    tag="016",
    pen="Pen 1",
    breed_composition={"primary": "Cracker/St Augustine/Katahdin/BBB/White Dorper", "percentages": {"Cracker": 50, "St Augustine": 28.125, "Katahdin": 12.5, "Barbados Blackbelly": 6.25, "White Dorper": 3.125}, "coat_type": "mixed", "hair_percentage": 72},
    color_markings="Brown and Tan",
    dob="2023-01-14",
    sire_id="smore", dam_id="half-tail",
    weight_lbs=99,
    famacha_scores=[{"score": 3, "date": "2025-tag-day", "notes": "treated"}],
    measurements={"girth": 31.5, "length": 30, "calculated_weight": 99.2, "date": "2023-2024", "prev_measurement_1": 30, "prev_measurement_2": 31, "prev_date": "2025"},
    is_breeding_animal=True,
    notes="Flock spreadsheet: Tag 016, ram. S'More (100%Cr) x Half Tail (12.5%BBB/31.25%K/56.25%SA). DOB 1/14/2023. Brown and Tan. 50%Cr/28.125%SA/12.5%K/6.25%BBB/3.125%WD. Weight calculator: 99.2lbs. In Pen 1.",
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

# Serendipity - ewe, tag 30 (Sir Loin x Shaggy)
db["sheep"].append(sheep("serendipity", "Serendipity", "ewe", "alive",
    tag="030",
    aliases=["SE", "Seren"],
    pen="Pen 4",
    breed_composition={"primary": "St Augustine/Babydoll/Jacob/Katahdin", "percentages": {"St Augustine": 37.5, "Babydoll": 25, "Jacob": 25, "Katahdin": 12.5}, "coat_type": "mixed", "hair_percentage": 75},
    color_markings="Black",
    weight_lbs=140, dob="2022-01-12",
    sire_id="sir-loin", dam_id="shaggy",
    offspring_ids=["serendipitys-baby-036", "kaladin"],
    health_notes=["Low FAMACHA score 7-24-25 along with GG and Lara"],
    notes="Flock spreadsheet: 25% Babydoll / 25% Jacob / 12.5% Katahdin / 37.5% St Augustine, Black, 140lbs. DOB 1/12/2022. Sir Loin (25K/75SA) x Shaggy (50Babydoll/50Jacob). Mother of Mc12/036 baby ewe and Kaladin (by S'More). Now in Pen 4 with twins per owner.",
    confidence="high",
    notebook_image=["IMG_8629.PNG", "IMG_8632.PNG", "IMG_8640.PNG", "IMG_8642.PNG"]))

# Serendipity's baby - 036, Mc12
db["sheep"].append(sheep("serendipitys-baby-036", "Serendipity's Baby", "ewe", "alive",
    tag="036", mc_tag="Mc12",
    dam_id="serendipity",
    notes="036, Mc12. Serendipity's baby ewe. Photo from March 18, 2024 shows white lamb with yellow MC12 ear tag.",
    confidence="high",
    notebook_image=["IMG_8632.PNG"]))

# Little Daisy - ewe, tag 35 (12.5%BHD/50%Cr/18.75%K/18.75%SA)
db["sheep"].append(sheep("little-daisy", "Little Daisy", "ewe", "alive",
    tag="035", aliases=["Daisy"],
    pen="Pen 5",
    breed_composition={"primary": "Cracker/Katahdin/St Augustine/Black Headed Dorper", "percentages": {"Black Headed Dorper": 12.5, "Cracker": 50, "Katahdin": 18.75, "St Augustine": 18.75}, "coat_type": "hair", "hair_percentage": 81},
    offspring_ids=["little-daisys-baby-mc01"],
    health_notes=["Needed parasite treatment April 13 2025 - eyes were white (tag 35)"],
    notes="Tag 35. 12.5%BHD/50%Cr/18.75%K/18.75%SA per Rocky breeding page. In pen 5 (Rocky group). Mother of Mc01 (baby's baby). Needed parasite treatment April 13, 2025 with white eyes. Hair sheep.",
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
    breed_composition={"primary": "Suffolk Cross", "percentages": {"Suffolk": 50, "Cracker": 25, "Katahdin": 18.75, "Gulf Coast Native": 6.25}, "coat_type": "wool", "hair_percentage": 25},
    notes="In pen 3 (Sam group). On weak resistance list. Google Sheet Pen 2 shows her as Suffolk Cross ewe offspring calculation parent.",
    confidence="medium",
    notebook_image=["IMG_8628.PNG", "IMG_8629.PNG"]))

# Baby Momma - ewe
db["sheep"].append(sheep("baby-momma", "Baby Momma", "ewe", "alive",
    pen="Pen 3",
    notes="In pen 3 (Sam group).",
    confidence="medium",
    notebook_image=["IMG_8629.PNG"]))

# Zara - ewe, tag 25 = Dorper 25 — DECEASED
db["sheep"].append(sheep("zara", "Zara", "ewe", "deceased",
    tag="025",
    aliases=["Dorper 25"],
    pen="Pen 3",
    breed_composition={"primary": "Dorper", "percentages": {"Dorper": 100}, "coat_type": "hair", "hair_percentage": 100},
    weak_resistance=True,
    treatments=[{"date": "2024-10-24", "treatment": "iron and vitamin B"}],
    notes="Tag 25. Zara = Dorper 25 (same animal). 100% Dorper. Deceased per owner. Was in pen 3 (Sam group). On weak resistance list. Lambed 2026-01-28.",
    confidence="high",
    notebook_image=["IMG_8626.PNG", "IMG_8628.PNG", "IMG_8629.PNG", "IMG_8641.PNG"]))

# Half Tail - ewe
db["sheep"].append(sheep("half-tail", "Half Tail", "ewe", "alive",
    pen="Pen 3",
    breed_composition={"primary": "St Augustine/Katahdin/BBB", "percentages": {"St Augustine": 56.25, "Katahdin": 31.25, "Barbados Blackbelly": 12.5}, "coat_type": "mixed", "hair_percentage": 44},
    color_markings="White",
    weight_lbs=180, dob="2017-01-01", dob_approximate=True,
    sire_id="sir-loin", dam_id="hersheys",
    offspring_ids=["broken-tail", "half-tails-baby", "elsie", "ht1", "merrie"],
    notes="Flock spreadsheet: 12.5% BBB / 31.25% Katahdin / 56.25% St Augustine, 180lbs. DOB ~1/1/2017. Sir Loin (25K/75SA) x Hersheys (25BBB/37.5K/37.5SA). Mother of Broken Tail, Elsie (by Well Done), HT1 (by S'More), Merrie (by S'More). In pen 3 (Sam group) per notebook.",
    confidence="high",
    csv_row=16,
    notebook_image=["IMG_8629.PNG"]))

# Broken Tail - ewe
db["sheep"].append(sheep("broken-tail", "Broken Tail", "ewe", "alive",
    aliases=["Bt", "BT"],
    tag="034",
    pen="Pen 5",
    breed_composition={"primary": "St Augustine/Katahdin/BBB", "percentages": {"St Augustine": 65.625, "Katahdin": 28.125, "Barbados Blackbelly": 6.25}, "coat_type": "mixed", "hair_percentage": 34},
    color_markings="White",
    weight_lbs=225, dob="2018-01-18", dob_approximate=True,
    sire_id="sir-loin", dam_id="half-tail",
    offspring_ids=["bt1-lamb", "bt2-lamb"],
    notes="Flock spreadsheet: 6.25% BBB / 28.125% Katahdin / 65.625% St Augustine, 225lbs. DOB 1/18/2018. Sir Loin (25K/75SA) x Half Tail (12.5BBB/31.25K/56.25SA). Mother of BT1 and BT2 lambs (by S'More). Lambed 2026-01-20 (twins). In pen 5 (Rocky group) per notebook.",
    confidence="high",
    csv_row=17,
    notebook_image=["IMG_8629.PNG", "IMG_8642.PNG"]))

# Trouble - ewe, tag 33 (Sir Loin x Haylee Lawson)
db["sheep"].append(sheep("trouble", "Trouble", "ewe", "alive",
    tag="033",
    aliases=["Tr"],
    pen="Pen 5",
    breed_composition={"primary": "Katahdin/St Augustine/Dorper", "percentages": {"Katahdin": 37.5, "St Augustine": 37.5, "Dorper": 25}, "coat_type": "hair", "hair_percentage": 62},
    color_markings="White",
    weight_lbs=180, dob="2021-01-01", dob_approximate=True,
    sire_id="sir-loin", dam_id="haylee-lawson",
    notes="Flock spreadsheet: Tag 9/retagged 33, 25% Dorper / 37.5% Katahdin / 37.5% St Augustine, 180lbs. DOB ~1/1/2021. Sir Loin (25K/75SA) x Haylee Lawson (50D/50K). In pen 5 per notebook.",
    confidence="high",
    notebook_image=["IMG_8642.PNG"]))

# Bsoe (Black Spot on Ear) - ewe, tag 32 (Sir Loin x Two Pence)
db["sheep"].append(sheep("bsoe", "Bsoe", "ewe", "alive",
    tag="032",
    aliases=["Black Spot on Ear", "BSOE"],
    pen="Pen 5",
    breed_composition={"primary": "Katahdin/St Augustine", "percentages": {"Katahdin": 56, "St Augustine": 44}, "coat_type": "hair", "hair_percentage": 56},
    color_markings="White",
    weight_lbs=185, dob="2019-01-01", dob_approximate=True,
    sire_id="sir-loin", dam_id="two-pence",
    offspring_ids=["bsoe1", "bsoe2", "pippen", "merrie-bs2"],
    notes="Flock spreadsheet: 56% Katahdin / 44% St Augustine, 185lbs. DOB ~1/1/2019. Sir Loin (25K/75SA) x Two Pence. Mother of BSOE1/Pippen and BSOE2/Merrie (by S'More). Tag 32 (switched with Bsoed). In pen 5 per notebook.",
    confidence="high",
    notebook_image=["IMG_8642.PNG"]))

# Bsoed (Black Spot Daughter) - ewe, tag 31 (Sir Loin x BSOE)
db["sheep"].append(sheep("bsoed", "Bsoed", "ewe", "alive",
    tag="031",
    aliases=["Black Spot Daughter", "BSOED"],
    pen="Pen 5",
    breed_composition={"primary": "St Augustine/Katahdin", "percentages": {"Katahdin": 40.5, "St Augustine": 59.5}, "coat_type": "mixed", "hair_percentage": 40},
    color_markings="White",
    weight_lbs=175, dob="2020-01-18", dob_approximate=True,
    sire_id="sir-loin", dam_id="bsoe",
    notes="Flock spreadsheet: ~40.5% Katahdin / ~59.5% St Augustine, 175lbs. DOB 1/18/2020. Sir Loin (25K/75SA) x BSOE (56K/44SA). Tag 31 (switched with Bsoe). In pen 5 per notebook.",
    confidence="high",
    notebook_image=["IMG_8642.PNG"]))

# FM - ewe (purchased, GA tag 1568-011)
db["sheep"].append(sheep("fm", "FM", "ewe", "alive",
    pen="Pen 1",
    weak_resistance=True,
    breed_composition={"primary": "Cotswold/Tunis", "percentages": {"Cotswold": 50, "Tunis": 50}, "coat_type": "wool", "hair_percentage": 0},
    color_markings="Red",
    weight_lbs=200, dob="2021-01-10", dob_approximate=True,
    offspring_ids=["flan"],
    notes="Flock spreadsheet: Tag GA1568-011, 50% Cotswold / 50% Tunis, Red, 200lbs. DOB 1/10/2021. Purchased (Sire: Annie 1, Dam: Annie 2). Mother of Flan (by Sir Loin). In Pen 1 (Kaladin group). On weak resistance list. Lambed 2026-02-01.",
    confidence="high",
    csv_row=15,
    notebook_image=["IMG_8628.PNG", "IMG_8630.PNG", "IMG_8636.PNG", "IMG_8641.PNG"]))

# FM1 - ewe (different from FM)
db["sheep"].append(sheep("fm1", "FM1", "ewe", "alive",
    tag="009",
    pen="Pen 6",
    weak_resistance=True,
    weight_lbs=67,
    measurements={"girth": 29.5, "length": 23, "calculated_weight": 66.7, "date": "2023-2024"},
    notes="Different from FM. Tag 009. In pen 6 (no ram). On weak resistance list. On 'Ewes to Upgrade' list. Half wool. Weight calculator: 66.7lbs.",
    confidence="medium",
    notebook_image=["IMG_8624.PNG", "IMG_8628.PNG", "IMG_8629.PNG", "IMG_8642.PNG"]))

# Eclipse - ewe (Nori's 2022 offspring) - DECEASED after Hurricane Idalia
db["sheep"].append(sheep("eclipse", "Eclipse", "ewe", "deceased",
    dam_id="nori",
    breed_composition={"primary": "St Augustine/ABB/Wiltshire Horn/Katahdin", "percentages": {"American Blackbelly": 25, "Katahdin": 12.5, "St Augustine": 37.5, "Wiltshire Horn": 25}, "coat_type": "hair", "hair_percentage": 62},
    weight_lbs=42,
    measurements={"girth": 22, "length": 26, "calculated_weight": 41.9, "date": "2023-2024"},
    status_notes="Died after Hurricane Idalia (Aug 2023)",
    notes="25%ABB/12.5%K/37.5%SA/25%WH per Merrie breeding page. Nori's 2022 offspring (only one Eclipse per owner). Weight calculator: 41.9lbs. Died after Hurricane Idalia (Aug/Sep 2023). Was in Pen 1 (Kaladin group) before death.",
    confidence="high",
    notebook_image=["IMG_8624.PNG", "IMG_8630.PNG"]))

# Abg - ewe, tag 22 (ABB ewe per weight calculator)
db["sheep"].append(sheep("abg", "Abg", "ewe", "alive",
    tag="022",
    aliases=["ABB ewe"],
    pen="Pen 1",
    weight_lbs=144,
    measurements={"girth": 36.75, "length": 32, "calculated_weight": 144.1, "date": "2023-2024"},
    notes="Tag 22. Called 'Abb ewe' in weight calculator. Weight calculator: 144.1lbs. In Pen 1 (Kaladin group).",
    confidence="high",
    notebook_image=["IMG_8630.PNG", "IMG_8641.PNG"]))

# NOTE: "Banana" in the notebook is the same animal as "Anna's Big One" (spreadsheet abbreviation "B").
# Removed duplicate - see annas-big-one entry in ADDITIONAL FROM CSV section.

# Circle Tail - ewe (S'More x Brown Knee)
db["sheep"].append(sheep("circle-tail", "Circle Tail", "ewe", "alive",
    aliases=["CT1"],
    pen="Pen 6",
    weak_resistance=True,
    breed_composition={"primary": "Cracker/St Augustine/Katahdin", "percentages": {"Cracker": 50, "St Augustine": 28.125, "Katahdin": 21.875}, "coat_type": "mixed", "hair_percentage": 50},
    dob="2023-01-22",
    sire_id="smore", dam_id="brown-knee",
    weight_lbs=64,
    famacha_scores=[{"score": 5, "date": "2025-tag-day", "notes": "treated with iron also"}],
    measurements={"girth": 27.5, "length": 25.5, "calculated_weight": 64.3, "date": "2023-2024"},
    notes="Flock spreadsheet: 50% Cracker / 21.875% Katahdin / 28.125% St Augustine. DOB 1/22/2023. S'More (100Cr) x Brown Knee (43.75K/56.25SA). In pen 6 (no ram). On weak resistance list. FAMACHA 5. Weight calculator: 64.3lbs.",
    confidence="high",
    notebook_image=["IMG_8628.PNG", "IMG_8629.PNG", "IMG_8641.PNG"]))

# Fox Tail - ewe
db["sheep"].append(sheep("fox-tail", "Fox Tail", "ewe", "alive",
    pen="Pen 6",
    weight_lbs=118,
    measurements={"girth": 35, "length": 29, "calculated_weight": 118.4, "date": "2023-2024"},
    notes="In pen 6 (no ram). Weight calculator: 118.4lbs. On 'Ewes to Upgrade' list.",
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

# Lara - ewe, tag 23 = Dorper 23 from weak resistance list
db["sheep"].append(sheep("lara", "Lara", "ewe", "alive",
    tag="023",
    aliases=["Dorper 23"],
    pen="Pen 2",
    breed_composition={"primary": "Dorper", "percentages": {"Dorper": 100}, "coat_type": "hair", "hair_percentage": 100},
    weight_lbs=160,
    weak_resistance=True,
    measurements={"girth": 36.75, "length": 35.5, "calculated_weight": 159.8, "date": "2023-2024"},
    treatments=[{"date": "2024-10-24", "treatment": "iron and vitamin B"}],
    health_notes=["Sick sheep note: one of Dorper 23/25 is Lara", "Low score 7-24-25"],
    notes="Tag 23. Lara = Dorper 23 (same animal). 100% Dorper. In pen 2 (sirloin group). Weight calculator: 159.8lbs. On 'Ewes to Upgrade' list and weak resistance list.",
    confidence="high",
    notebook_image=["IMG_8626.PNG", "IMG_8628.PNG", "IMG_8630.PNG", "IMG_8636.PNG", "IMG_8640.PNG", "IMG_8641.PNG"]))

# Pebbles - ewe
db["sheep"].append(sheep("pebbles", "Pebbles", "ewe", "alive",
    pen="Pen 2",
    famacha_scores=[{"score": 3, "date": "2025-tag-day", "notes": "treated (struck thru)"}],
    notes="In pen 2 (sirloin group). FAMACHA 3, treated. Entry struck through in treatment list.",
    confidence="medium",
    notebook_image=["IMG_8630.PNG", "IMG_8641.PNG"]))

# Anna - ewe from CSV (parents: Show King x Show Queen, off-farm)
db["sheep"].append(sheep("anna", "Anna", "ewe", "deceased",
    tag="1",
    breed_composition={"primary": "Katahdin", "percentages": {"Katahdin": 100}, "coat_type": "hair", "hair_percentage": 100},
    color_markings="White",
    weight_lbs=175, dob="2012-01-12", dob_approximate=True,
    offspring_ids=["annas-big-one"],
    notes="Flock spreadsheet: Tag 1, 100% Katahdin, 175lbs. DOB 1/12/2012. Sire: Show King, Dam: Show Queen (off-farm). Mother of Anna's Big One (by Sir Loin). The deceased Kaladin (tag 24) was also S'More x Anna, but that is a different animal from the living Kaladin (tag 014, S'More x Serendipity). Deceased per flock spreadsheet.",
    confidence="high", csv_row=4))

# Boots - ewe (purchased from Maria, culled per spreadsheet)
db["sheep"].append(sheep("boots", "Boots", "ewe", "culled",
    tag="7",
    breed_composition={"primary": "Dorper/Katahdin", "percentages": {"Dorper": 50, "Katahdin": 50}, "coat_type": "hair", "hair_percentage": 100},
    color_markings="White/Tan",
    weight_lbs=130, dob="2020-02-14", dob_approximate=True,
    offspring_ids=["dannys-girl", "boots-1"],
    status_notes="Culled per flock spreadsheet",
    notes="Flock spreadsheet: Tag 7, 50% Dorper / 50% Katahdin, 130lbs. DOB 2/14/2020. Purchased from Maria (Sire: Maria 1, Dam: Maria 2). Mother of Danny's Girl and Boots 1 (both by S'More). Culled.",
    confidence="high",
    csv_row=11,
    notebook_image=["IMG_8623.PNG"]))

# Patches - ewe
db["sheep"].append(sheep("patches", "Patches", "ewe", "alive",
    weight_lbs=66,
    measurements={"girth": 27, "length": 27, "calculated_weight": 65.6, "date": "2023-2024"},
    notes="Weight calculator: 65.6lbs (girth 27, length 27). Weight calc shows tag 27 but Bella is also tag 27 — [UNCLEAR] if same animal or tag conflict.",
    confidence="medium",
    notebook_image=["IMG_8624.PNG"]))

# Little Song - ewe, tag 008 (Sir Loin x Anna's Big One)
db["sheep"].append(sheep("little-song", "Little Song", "ewe", "alive",
    tag="008",
    aliases=["LS"],
    breed_composition={"primary": "St Augustine/Katahdin", "percentages": {"Katahdin": 43.75, "St Augustine": 56.25}, "coat_type": "mixed", "hair_percentage": 44},
    color_markings="White",
    dob="2023-01-24",
    sire_id="sir-loin", dam_id="annas-big-one",
    weight_lbs=60,
    measurements={"girth": 28, "length": 23, "calculated_weight": 60.1, "date": "2023-2024"},
    notes="Flock spreadsheet: Tag 8/retagged 008, 43.75% Katahdin / 56.25% St Augustine, White. DOB 1/24/2023. Sir Loin (25K/75SA) x Anna's Big One (62.5K/37.5SA). Weight calculator: 60.1lbs.",
    confidence="high",
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
    weight_lbs=68,
    measurements={"girth": 25.25, "length": 32, "calculated_weight": 68.0, "date": "2023-2024"},
    notes="Tag 002. Called 'Sb1 (crown)' in measurements. Weight calculator: 68.0lbs.",
    confidence="medium",
    notebook_image=["IMG_8623.PNG"]))

# Sb2 (all black) - tag 003
db["sheep"].append(sheep("sb2-all-black", "Sb2 (All Black)", "ewe", "alive",
    tag="003",
    color_markings="all black",
    weight_lbs=66,
    measurements={"girth": 25, "length": 31.5, "calculated_weight": 65.6, "date": "2023-2024"},
    notes="Tag 003. Called 'Sb2 (all black)' in measurements. Weight calculator: 65.6lbs.",
    confidence="medium",
    notebook_image=["IMG_8623.PNG"]))

# New Big Girl 2 - ewe
db["sheep"].append(sheep("new-big-girl-2", "New Big Girl 2", "ewe", "alive",
    pen="Pen 3",
    notes="In pen 3 (Sam group).",
    confidence="low",
    notebook_image=["IMG_8629.PNG"]))

# Daisy's Daughter (1 and 2 - from Google Sheet)
db["sheep"].append(sheep("daisys-daughter-1", "Daisy's Daughter 1", "ewe", "unknown",
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
db["sheep"].append(sheep("gertrude", "Gertrude", "ewe", "unknown",
    pen="Pen 5",
    breed_composition={"primary": "ABB/St Augustine/Katahdin/Wiltshire", "percentages": {"American Blackbelly": 25, "St Augustine": 37.5, "Katahdin": 12.5, "Wiltshire Horn": 25}, "coat_type": "hair", "hair_percentage": 62},
    notes="From Google Sheet Pen 5 breed data. NoriSon's group.",
    confidence="low"))

# OAV 2222 - confirmed 100% Katahdin per Rocky breeding page
db["sheep"].append(sheep("oav-2222", "OAV 2222", "ewe", "alive",
    tag="2222", aliases=["2222"],
    pen="Pen 5",
    breed_composition={"primary": "Katahdin", "percentages": {"Katahdin": 100}, "coat_type": "hair", "hair_percentage": 100},
    notes="100% Katahdin confirmed by Rocky breeding page. Tag 2222. In pen 5 (NoriSon group). Lambed 2026-02-10 (twins).",
    confidence="high",
    notebook_image=["IMG_8639.PNG"]))

# Heather Oaks - from Google Sheet Pen 5
db["sheep"].append(sheep("heather-oaks", "Heather Oaks", "ewe", "unknown",
    pen="Pen 5",
    breed_composition={"primary": "Katahdin/Dorper/ABB/St Augustine/Wiltshire", "percentages": {"Katahdin": 37.5, "Dorper": 25, "American Blackbelly": 12.5, "St Augustine": 12.5, "Wiltshire Horn": 12.5}, "coat_type": "mixed", "hair_percentage": 75},
    notes="From Google Sheet Pen 5 breed data.",
    confidence="low"))

# Tag 31 - from Google Sheet Pen 2
db["sheep"].append(sheep("tag-31-ewe", "Tag 31", "ewe", "alive",
    tag="031-pen2",
    breed_composition={"primary": "Katahdin/St Augustine/Dorper/BBB", "percentages": {"Katahdin": 28.125, "St Augustine": 49.625, "Dorper": 16, "Barbados Blackbelly": 6.25}, "coat_type": "mixed", "hair_percentage": 31},
    notes="From Google Sheet Pen 2. 69.25% wool. Different from Bsoed tag 31 in pen 5. Lambed 2026-02-13.",
    confidence="low"))

# Tag 33 - from Google Sheet Pen 1
db["sheep"].append(sheep("tag-33", "Tag 33", "ewe", "alive",
    tag="033-pen1",
    breed_composition={"primary": "Katahdin/St Augustine/BBB/Cracker/White Dorper/Suffolk/GCN", "coat_type": "mixed", "hair_percentage": 25},
    notes="From Google Sheet Pen 1. 3/4 hair. Has twins.",
    confidence="low"))

# Tag 35 - from Google Sheet Pen 3
db["sheep"].append(sheep("tag-35-ewe", "Tag 35", "ewe", "unknown",
    tag="035-pen3",
    breed_composition={"primary": "Katahdin/St Augustine", "percentages": {"Katahdin": 29.75, "St Augustine": 70.25}, "coat_type": "mixed", "hair_percentage": 30},
    notes="From Google Sheet Pen 3. Broken Tail x Buck. Had Awassi(22%)/EF(3%) overlay in Google Sheet but removing as those were Sir Loin era calculations. Status unknown - Google Sheet only, may be same as Little Daisy (tag 35).",
    confidence="low"))

# Bambi - tag 37 (weight calculator listed as 35 but that's Little Daisy's tag)
db["sheep"].append(sheep("bambi", "Bambi", "ewe", "alive",
    tag="037",
    pen="Pen 3",
    weight_lbs=81,
    breed_composition={"primary": "Katahdin/Dorper", "percentages": {"Katahdin": 50, "Dorper": 50}, "coat_type": "hair", "hair_percentage": 100},
    measurements={"girth": 29, "length": 29, "calculated_weight": 81.3, "date": "2023-2024"},
    notes="Weight calculator: tag 35, 81.3lbs (girth 29, length 29). Google Sheet Pen 3 shows 3/4 hair. Broken Tail x Buck. Also appears in pen 2 sirloin notebook list.",
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
    breed_composition={"primary": "Babydoll/Jacob", "percentages": {"Babydoll": 50, "Jacob": 50}, "coat_type": "wool", "hair_percentage": 0},
    color_markings="Black",
    weight_lbs=140, dob="2019-01-01", dob_approximate=True,
    offspring_ids=["serendipity", "shaggy-1", "shaggy-2"],
    status_notes="Killed by humans after Hurricane Helene",
    notes="Flock spreadsheet: 50% Babydoll / 50% Jacob, Black, 140lbs. DOB ~1/1/2019. Purchased (Sire: Jacob 1, Dam: Baby Doll 1). Mother of Serendipity (by Sir Loin), Shaggy 1 and Shaggy 2 (by S'More). Deceased — killed by humans after Hurricane Helene. Was in Pen 6. On weak resistance list. Was on 'Ewes to Keep anyway' list. Wool sheep.",
    confidence="high",
    csv_row=14,
    notebook_image=["IMG_8628.PNG", "IMG_8629.PNG", "IMG_8641.PNG"]))

db["sheep"].append(sheep("bambii", "Bambii", "ewe", "alive",
    pen="Pen 2",
    notes="In Pen 2 (Sir Loin group) per spiral notebook (authoritative). Was struck through in treatment list but notebook roster is definitive for alive/active status.",
    confidence="high",
    notebook_image=["IMG_8630.PNG", "IMG_8641.PNG"]))

db["sheep"].append(sheep("skitters", "Skitters", "ewe", "deceased",
    aliases=["Amber"],
    breed_composition={"primary": "Karakul", "percentages": {"Karakul": 100}, "coat_type": "wool", "hair_percentage": 0},
    weight_lbs=176,
    measurements={"girth": 38, "length": 36.5, "calculated_weight": 175.7, "date": "2023-2024"},
    weak_resistance=True,
    notes="Deceased. 100% Karakul per Rocky breeding page. Also called 'Amber' per owner. Weight calculator: 175.7lbs (from 2023-2024 when alive). On weak resistance list. Was on 'Ewes to Keep anyway' list. Wool sheep.",
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
    tag="3",
    breed_composition={"primary": "BBB/Katahdin/St Augustine", "percentages": {"Barbados Blackbelly": 25, "Katahdin": 37.5, "St Augustine": 37.5}, "coat_type": "mixed", "hair_percentage": 62},
    color_markings="Black",
    weight_lbs=150, dob="2015-02-01", dob_approximate=True,
    sire_id="sir-loin", dam_id="sugar",
    offspring_ids=["half-tail"],
    notes="Flock spreadsheet: Tag 3, 25% BBB / 37.5% Katahdin / 37.5% St Augustine, 150lbs. DOB 2/1/2015. Sir Loin (25K/75SA) x Sugar (50BBB/50K). Mother of Half Tail. Deceased.",
    confidence="high", csv_row=18))

db["sheep"].append(sheep("gg-daughter-45", "GG's Daughter", "ewe", "deceased",
    tag="045",
    sire_id="gg",
    notes="GG's daughter (GG is sire). Tag 45. Deceased.",
    confidence="high",
    notebook_image=["IMG_8634.PNG"]))

db["sheep"].append(sheep("lara-daughter-46", "Lara's Daughter", "ewe", "sold",
    tag="046",
    sire_id="gg", dam_id="lara",
    status_notes="Sold - prone to Coccidia",
    notes="GG (sire) x Lara (dam) daughter. Tag 46. Sold because prone to Coccidia.",
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

# ============================================================
# INACTIVE / CULLED (from Sheep_Breeding_DB)
# ============================================================

db["sheep"].append(sheep("razzle", "Razzle", "ram", "deceased",
    tag="5",
    breed_composition={"primary": "Barbados Blackbelly", "percentages": {"Barbados Blackbelly": 100}, "coat_type": "hair", "hair_percentage": 100},
    color_markings="Badger",
    weight_lbs=125, dob="2014-03-01", dob_approximate=True,
    offspring_ids=["sugar"],
    status_notes="Culled - temperament",
    notes="Flock spreadsheet: Tag 5, 100% BBB ram, Badger color, 125lbs. DOB 3/1/2014. Purchased from auction (Sire: Auction 1, Dam: Auction 2). Father of Sugar (by Frazzle). Culled for temperament.",
    confidence="high"))

db["sheep"].append(sheep("frazzle", "Frazzle", "ewe", "deceased",
    tag="6",
    breed_composition={"primary": "Katahdin", "percentages": {"Katahdin": 100}, "coat_type": "hair", "hair_percentage": 100},
    color_markings="Black",
    weight_lbs=175, dob="2013-02-27", dob_approximate=True,
    offspring_ids=["sugar"],
    status_notes="Died - age",
    notes="Flock spreadsheet: Tag 6, 100% Katahdin ewe, Black, 175lbs. DOB 2/27/2013. Purchased from auction (Sire: Auction 2, Dam: Auction 3). Mother of Sugar (by Razzle). Died of old age.",
    confidence="high"))

db["sheep"].append(sheep("almond-joy", "Almond Joy", "ram", "deceased",
    status_notes="Culled - cryptorchid",
    notes="From Sheep Breeding DB. Ram culled (C) for being cryptorchid.",
    confidence="medium"))

db["sheep"].append(sheep("sugar", "Sugar", "ewe", "deceased",
    tag="4",
    breed_composition={"primary": "BBB/Katahdin", "percentages": {"Barbados Blackbelly": 50, "Katahdin": 50}, "coat_type": "hair", "hair_percentage": 100},
    color_markings="Tan",
    weight_lbs=224, dob="2014-02-14", dob_approximate=True,
    sire_id="razzle", dam_id="frazzle",
    offspring_ids=["hersheys"],
    status_notes="Culled - mastitis",
    notes="Flock spreadsheet: Tag 4, 50% BBB / 50% Katahdin, Tan, 224lbs. DOB 2/14/2014. Razzle (100BBB) x Frazzle (100K). Mother of Hersheys (by Sir Loin). Culled for mastitis.",
    confidence="high"))

db["sheep"].append(sheep("penny", "Penny", "ewe", "deceased",
    status_notes="Culled - poor shedder",
    notes="From Sheep Breeding DB. Ewe culled (C) for poor shedding.",
    confidence="medium"))

db["sheep"].append(sheep("two-pence", "Two Pence", "ewe", "deceased",
    breed_composition={"primary": "Katahdin/St Augustine", "percentages": {"Katahdin": 87, "St Augustine": 13}, "coat_type": "hair", "hair_percentage": 87},
    offspring_ids=["bsoe"],
    status_notes="Culled - daughter of cryptorchid",
    notes="From Sheep Breeding DB. Ewe culled as daughter of cryptorchid (Almond Joy). Mother of BSOE (by Sir Loin). Breed estimated from BSOE's composition: if BSOE=56K/44SA and Sir Loin=25K/75SA, Two Pence ~87K/13SA.",
    confidence="medium"))

db["sheep"].append(sheep("haylee-lawson", "Haylee Lawson", "ewe", "deceased",
    tag="14",
    breed_composition={"primary": "Dorper/Katahdin", "percentages": {"Dorper": 50, "Katahdin": 50}, "coat_type": "hair", "hair_percentage": 100},
    color_markings="White",
    weight_lbs=175, dob="2019-01-01", dob_approximate=True,
    offspring_ids=["trouble"],
    notes="Flock spreadsheet: Tag 14, 50% Dorper / 50% Katahdin, White, 175lbs. DOB ~1/1/2019. Purchased (Sire: HL1, Dam: HL2). Mother of Trouble (by Sir Loin). Deceased.",
    confidence="high"))

db["sheep"].append(sheep("pretzel", "Pretzel", "ewe", "deceased",
    tag="13",
    breed_composition={"primary": "Dorper/Katahdin", "percentages": {"Dorper": 75, "Katahdin": 25}, "coat_type": "hair", "hair_percentage": 100},
    color_markings="Black/White",
    weight_lbs=130, dob="2022-01-20",
    status_notes="Deceased per flock spreadsheet",
    notes="Flock spreadsheet: Tag 13, 75% Dorper / 25% Katahdin, Black/White, 130lbs. DOB 1/20/2022. Purchased from Maria (Sire: Maria 3, Dam: Maria 4). Deceased.",
    confidence="high"))

db["sheep"].append(sheep("w140", "W140", "ewe", "alive",
    weak_resistance=True,
    notes="On weak resistance list. Status alive but weak.",
    confidence="low",
    notebook_image=["IMG_8628.PNG"]))

# ============================================================
# ADDITIONAL FROM CSV
# ============================================================

db["sheep"].append(sheep("brown-knee", "Brown Knee", "ewe", "unknown",
    aliases=["BK"],
    breed_composition={"primary": "St Augustine/Katahdin", "percentages": {"Katahdin": 43.75, "St Augustine": 56.25}, "coat_type": "mixed", "hair_percentage": 44},
    weight_lbs=150, dob="2016-02-14", dob_approximate=True,
    sire_id="sir-loin", dam_id="annas-big-one",
    offspring_ids=["circle-tail", "bk1", "bk2"],
    notes="Flock spreadsheet: 43.75% Katahdin / 56.25% St Augustine, 150lbs. DOB 2/14/2016. Sir Loin (25K/75SA) x Anna's Big One (62.5K/37.5SA). Mother of Circle Tail, BK1, and BK2 (by S'More). Note: BSOE's dam is Two Pence, not Brown Knee (corrected from earlier CSV).",
    confidence="medium", csv_row=6))

# NOTE: "Black Spot on Ear" from the old CSV referred to a DIFFERENT lineage calculation (via Brown Knee).
# The flock spreadsheet confirms BSOE's dam is Two Pence, not Brown Knee.
# This old CSV entry is removed - see "bsoe" entry above which has the correct parentage.

db["sheep"].append(sheep("banana-split", "Banana Split", "ewe", "unknown",
    breed_composition={"primary": "St Augustine/Katahdin", "percentages": {"St Augustine": 70.3125, "Katahdin": 29.6875}, "coat_type": "mixed", "hair_percentage": 30},
    weight_lbs=235, dob="2015-11-14", dob_approximate=True,
    sire_id="sir-loin", dam_id="bsoe",
    offspring_ids=["banana-split-baby"],
    notes="From CSV & Breeding DB. 70.3% St Augustine, 29.7% Katahdin (calculated: Sir Loin x BSOE). Mother of Banana Split Baby. Status unknown - not in recent notebook. Note: old CSV had dam as 'Black Spot on Ear' which is the same as BSOE.",
    confidence="low", csv_row=8))

db["sheep"].append(sheep("fleecity", "Fleecity", "ewe", "unknown",
    breed_composition={"primary": "Katahdin/Dorper", "percentages": {"Katahdin": 50, "Dorper": 50}, "coat_type": "hair", "hair_percentage": 100},
    weight_lbs=100, dob="2021-01-14", dob_approximate=True,
    offspring_ids=["stew"],
    notes="From CSV. 50% Katahdin, 50% Dorper. Same parents as Boots (Boots Dad x Boots Mom) - they are siblings. Mother of Stew (by Well Done). Status unknown - not in recent notebook.",
    confidence="low", csv_row=13))

# Banana Split Baby - ram from CSV (Sir Loin x Banana Split)
db["sheep"].append(sheep("banana-split-baby", "Banana Split Baby", "ram", "unknown",
    tag="8",
    breed_composition={"primary": "St Augustine/Katahdin", "percentages": {"St Augustine": 72.656, "Katahdin": 27.344}, "coat_type": "mixed", "hair_percentage": 27},
    weight_lbs=12.3, dob="2022-02-23",
    sire_id="sir-loin", dam_id="banana-split",
    notes="From CSV & Breeding DB. ~72.7% St Augustine, ~27.3% Katahdin (calculated: Sir Loin x Banana Split). Status unknown - not in recent notebook.",
    confidence="low", csv_row=9))

# Anna's Big One - ewe from CSV (Sir Loin x Anna) = "Banana" in notebook
db["sheep"].append(sheep("annas-big-one", "Anna's Big One", "ewe", "alive",
    aliases=["Banana", "B"],
    breed_composition={"primary": "Katahdin/St Augustine", "percentages": {"Katahdin": 62.5, "St Augustine": 37.5}, "coat_type": "hair", "hair_percentage": 62},
    color_markings="White",
    weight_lbs=200, dob="2014-12-01", dob_approximate=True,
    pen="Pen 4",
    sire_id="sir-loin", dam_id="anna",
    offspring_ids=["brown-knee", "little-song", "ab1"],
    notes="Flock spreadsheet: 62.5% Katahdin / 37.5% St Augustine, 200lbs. DOB 12/1/2014. Sir Loin x Anna. Called 'Banana' in notebook. In Pen 4 (Samson group) per notebook. Mother of Brown Knee (by Sir Loin), Little Song (by Sir Loin), and AB1 (by Sir Loin).",
    confidence="high", csv_row=10))

# Stew - ram from CSV (Well Done x Fleecity - CSV has sire/dam swapped)
db["sheep"].append(sheep("stew", "Stew", "ram", "unknown",
    tag="11",
    breed_composition={"primary": "Katahdin/Dorper", "percentages": {"Katahdin": 75, "Dorper": 25}, "coat_type": "hair", "hair_percentage": 75},
    color_markings="Black w White Markings",
    weight_lbs=11.3, dob="2022-02-08",
    sire_id="well-done", dam_id="fleecity",
    notes="From CSV. 75% Katahdin, 25% Dorper. Well Done (sire) x Fleecity (dam) - CSV had sire/dam columns swapped. Status unknown - not in recent notebook.",
    confidence="low", csv_row=12))

# NOTE: Dorper 23 = Lara (tag 23) — merged into "lara" entry above.

# NOTE: Dorper 25 = Zara (tag 25) — merged into "zara" entry above.

# FM2 from Google Sheet
db["sheep"].append(sheep("fm2", "FM2", "ewe", "unknown",
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
        "other_rams": ["merrie"],
        "ewes": ["abg", "fm"],
        "notes": "Kaladin's group. Merrie (tag 016) is also a ram in this pen. Eclipse was here but is deceased (Hurricane Idalia). May 14 2025: vaccinated pen 1 lambs."
    },
    "pen_2": {
        "ram": "sir-loin",
        "other_rams": ["rocky"],
        "ewes": ["azure", "s2", "lara", "bambii", "unnamed-pen2", "pebbles"],
        "notes": "Sirloin's group per spiral notebook. Rocky/Jerkface also in Pen 2 per owner."
    },
    "pen_3": {
        "ram": "sam",
        "ewes": ["baby", "baby-momma", "half-tail", "new-big-girl-2"],
        "notes": "Sam's group. Zara was here but is deceased. Bella (tag 27) and Cinderella (tag 28) also in pen 3 per treatment notes."
    },
    "pen_4": {
        "ram": "samson",
        "ewes": ["nori", "trouble", "bsoe", "bsoed", "annas-big-one", "serendipity"],
        "notes": "Samson's group (Samson deceased — pen may have new ram). 'Banana' in notebook = Anna's Big One. Pen 4 also home to Kelsier and GG per Google Sheet. Elsie moved to Pen 6 with triplets. Serendipity now here with twins per owner."
    },
    "pen_5": {
        "ram": "nori-son",
        "ewes": ["broken-tail", "little-daisy"],
        "notes": "NoriSon (tag 54) is the pen 5 ram. Rocky moved to Pen 2. Notebook lists Amber 24, Broken tail, Little daisy. Amber 24 = Azure (also listed in pen 2)."
    },
    "pen_6": {
        "ram": None,
        "ewes": ["elsie", "s1", "fm1", "fox-tail", "circle-tail"],
        "notes": "No ram. Elsie here with triplets. Shaggy was here but is deceased (killed after Hurricane Helene). Serendipity moved to Pen 4 with twins."
    },
    "goose_pen": {
        "ram": None,
        "ewes": [],
        "notes": "Auction lambs: tags 09, 50, 06, L19, and others."
    },
    "chicken_coop": {
        "ram": "buck",
        "ewes": [],
        "notes": "Buck (Katahdin/Awassi/EF ram) housed in chicken coop."
    }
}

# ============================================================
# 2026 LAMBING RECORDS (from flock_record_v2.xlsx)
# ============================================================

db["lambing_records_2026"] = [
    {"date": "2026-01-20", "dam": "Broken Tail", "sire": "[UNCLEAR]", "lambs_born": 2, "lambs_alive": 2, "notes": "Twins", "pen": "Pen 2"},
    {"date": "2026-01-23", "dam": "Elsie", "sire": "[UNCLEAR]", "lambs_born": 3, "lambs_alive": 3, "notes": "Triplets per owner. Elsie now in Pen 6 with lambs.", "pen": "Pen 6"},
    {"date": "2026-01-25", "dam": "Nori", "sire": "[UNCLEAR]", "lambs_born": 1, "lambs_alive": 1, "notes": "EH", "pen": "Pen 4"},
    {"date": "2026-01-27", "dam": "Tag 33", "sire": "[UNCLEAR]", "lambs_born": 2, "lambs_alive": 2, "notes": "Twins (Ew = ewe)", "pen": "Pen 1"},
    {"date": "2026-01-28", "dam": "Zara", "sire": "[UNCLEAR]", "lambs_born": 1, "lambs_alive": 1, "notes": "EH", "pen": "Pen 3"},
    {"date": "2026-01-29", "dam": "Azure", "sire": "[UNCLEAR]", "lambs_born": 1, "lambs_alive": 1, "notes": "Renamed Amure in notes", "pen": "Pen 2"},
    {"date": "2026-01-30", "dam": "Dorpy", "sire": "[UNCLEAR]", "lambs_born": 1, "lambs_alive": 1, "notes": "Dorper/Katahdin cross", "pen": "Pen 4"},
    {"date": "2026-02-01", "dam": "FM", "sire": "[UNCLEAR]", "lambs_born": 1, "lambs_alive": 1, "notes": "", "pen": "Pen 4"},
    {"date": "2026-02-02", "dam": "Tag 34", "sire": "[UNCLEAR]", "lambs_born": 1, "lambs_alive": 1, "notes": "Fm2", "pen": "Pen 4"},
    {"date": "2026-02-03", "dam": "Serendipity", "sire": "[UNCLEAR]", "lambs_born": 2, "lambs_alive": 2, "notes": "Twins per owner. Serendipity now in Pen 4 with twins.", "pen": "Pen 4"},
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
culled = sum(1 for s in db["sheep"] if s["status"] == "culled")
sold = sum(1 for s in db["sheep"] if s["status"] == "sold")
unknown = sum(1 for s in db["sheep"] if s["status"] == "unknown")

db["meta"]["total_sheep"] = total
db["meta"]["active_sheep"] = alive
db["meta"]["deceased_count"] = deceased
db["meta"]["culled_count"] = culled
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
print(f"  Culled: {culled}")
print(f"  Sold: {sold}")
print(f"  Unknown: {unknown}")
print(f"  Pens: {len(db['pens'])}")
print(f"  Lambing records 2026: {len(db['lambing_records_2026'])}")
