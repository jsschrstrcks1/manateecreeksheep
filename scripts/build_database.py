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
    offspring_ids=["annas-big-one", "half-tail", "broken-tail", "hersheys", "bsoe", "bsoed", "elsie", "little-song", "ab1", "dodge", "daisy", "oliver", "spicy", "fm-lamb-2023", "gm-twin1-2024", "gm-twin2-2024"]))

# Kelsier = OAV 2223 = UF Ram Test — Katahdin ram, MOST parasite resistant
# Breeding page (OAV 2223): 100%K, tag 2223, DOB 12-21-22. Born as twin. Birth weight 10lbs, ADG 0.36.
# NSIP ID: 640301-2022-222223. Received from OAV Sam Mushko on 10-5-23.
# UF RAM TEST DATA. Parasite Resistance Y, Breed All Year Y.
# FEC avg 138.9 (tested 2-18-23 through 8-24-23). CDT 10-23-23.
# UF Ram Test 2023 Official Results (from 230907-UF-Ram-Test_Index-FINAL PDF):
#   Tx=0, ADG=0.07, ADG Ratio=25.73, WDA=0.51, WDA Ratio=109.37,
#   ADGxWDA Ratio=67.55, Avg FEC=157, FEC Ratio=446.65, Overall Index=257.10
#   Ranked 5th of 40 rams. Never dewormed. 5th lowest FEC of all test rams.
# Consigner: Oakvale Farm - Samantha Musho, DVM - DeLeon Springs, FL
# Note: Other OAV 22xx rams in the sale catalog listed as 87.5% Katahdin,
#   but breeding page says 100%K. OAV 2223 was not in the sale catalog
#   (possibly retained or sold privately). Breed % left as 100% per breeding page.
# Sister OAV 2222 (alive, in flock). Sister tag 2241 (deceased).
db["sheep"].append(sheep("kelsier", "Kelsier", "ram", "alive",
    tag="2223", aliases=["Tag 22", "UF Ram Test", "OAV 2223", "NSIP 640301-2022-222223"],
    breed_composition={"primary": "Katahdin", "percentages": {"Katahdin": 100}, "coat_type": "hair", "hair_percentage": 100},
    weight_lbs=250,
    dob="2022-12-21",
    pen="Pen 4", is_breeding_animal=True,
    vaccinations=[{"date": "2023-10-23", "vaccine": "CDT"}],
    notes="Most parasite resistant sheep in the flock. Pure Katahdin. OAV 2223 = Kelsier = UF Ram Test. NSIP ID: 640301-2022-222223. Born as twin. Birth weight 10lbs, ADG 0.36. Received from OAV Sam Mushko, DVM (Oakvale Farm, DeLeon Springs FL) on 10-5-23. Ram weight 250lbs, ewe weight prediction 150lbs. UF Ram Test 2023: Ranked 5th of 40 rams, never dewormed (Tx=0), ADG=0.07 (test period), WDA=0.51, Avg FEC=157 (FEC Ratio=446.65), Overall Index=257.10. Individual FEC readings: 2-18-23: 100, 4-6-23: 300, 5-25-23: 350, 6-15-23: 0, 6-29-23: 0, 7-13-23: 50, 7-27-23: 200, 8-10-23: 50, 8-24-23: 200 (avg 138.9). CDT vaccinated 10-23-23. Attributes: Parasite Resistant, Heat/Cold/Wet Tolerant, Breed All Year. Sister OAV 2222 (alive). Sister tag 2241 (deceased).",
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

# Rocky / Rock / Jerkface / Louise's Ram - 44%Awassi/50%BHD/6%EF ram, tag 140
# CLAUDE.md confirms: "Rock" = "Jerkface" = Awassi ram. These are the same animal.
# Breeding page: Pen 5, tag 140. Sire: Awassi Ram "Teaser" (88Aw/12EF). Dam: Dorper Ewe 198 (100%BHD).
# Born as multiple. Medical: FAMACHA 3 (BPW, Ivermectin); FAMACHA 4.5 on 9-20-23 (BPW, Ivermectin+iron+nutridrench).
db["sheep"].append(sheep("rocky", "Rocky", "ram", "alive",
    tag="140",
    aliases=["Rock", "Jerkface", "Awassi ram", "Awassi cross rock", "Louise's Ram"],
    breed_composition={"primary": "Black Headed Dorper/Awassi/East Friesian", "percentages": {"Awassi": 44, "Black Headed Dorper": 50, "East Friesian": 6}, "coat_type": "mixed", "hair_percentage": 50},
    weight_lbs=300,
    pen="Pen 2",
    sire_id="teaser", dam_id="dorper-ewe-198",
    is_breeding_animal=True,
    weak_resistance=True,
    born_as_multiple=True,
    famacha_scores=[{"score": 3, "date": "unknown", "notes": "BPW condition, Ivermectin"}, {"score": 4.5, "date": "2023-09-20", "notes": "BPW condition, Ivermectin and iron x nutridrench"}, {"score": 5, "date": "2023-10-23", "notes": "sick episode"}],
    treatments=[{"date": "2023-09-20", "treatment": "Ivermectin and iron x nutridrench"}, {"date": "2024-10-24", "treatment": "iron and vitamin B"}],
    notes="Also called Jerkface/Rock/Louise's Ram. Tag 140. 44%Awassi/50%BHD/6%EF per breeding page. Sire: Awassi Ram 'Teaser' (88Aw/12EF). Dam: Dorper Ewe 198 (100%BHD). Born as multiple. Ram weight 300lbs, ewe weight 200lbs. Medical: FAMACHA 3 (BPW, Ivermectin); FAMACHA 4.5 9-20-23 (BPW, Ivermectin+iron+nutridrench). Sick episode 10-23-23. Breeding page says Pen 5, now in Pen 2 per owner. On weak resistance list. On 'Rams to Upgrade' list. Half wool.",
    confidence="high",
    notebook_image=["IMG_8626.PNG", "IMG_8628.PNG", "IMG_8629.PNG", "IMG_8641.PNG"]))

# Teaser - Awassi ram, Rocky's sire (88%Awassi/12%East Friesian)
db["sheep"].append(sheep("teaser", "Teaser", "ram", "unknown",
    aliases=["Awassi Ram Teaser"],
    breed_composition={"primary": "Awassi/East Friesian", "percentages": {"Awassi": 88, "East Friesian": 12}, "coat_type": "wool", "hair_percentage": 0},
    offspring_ids=["rocky"],
    notes="Rocky's sire per Rocky breeding page. 88%Awassi/12%East Friesian. Called 'Awassi Ram Teaser'. Off-farm.",
    confidence="high"))

# Dorper Ewe 198 - Rocky's dam (100% Black Headed Dorper)
db["sheep"].append(sheep("dorper-ewe-198", "Dorper Ewe 198", "ewe", "unknown",
    breed_composition={"primary": "Black Headed Dorper", "percentages": {"Black Headed Dorper": 100}, "coat_type": "hair", "hair_percentage": 100},
    offspring_ids=["rocky"],
    notes="Rocky's dam per Rocky breeding page. 100% black face dorper. Off-farm.",
    confidence="high"))

# Samson - ram (deceased per weak resistance list) — 100% Hampshire per Buck breeding page
db["sheep"].append(sheep("samson", "Samson", "ram", "deceased",
    pen="Pen 4",
    breed_composition={"primary": "Hampshire", "percentages": {"Hampshire": 100}, "coat_type": "wool", "hair_percentage": 0},
    weight_lbs=400,
    weak_resistance=True,
    is_breeding_animal=True,
    offspring_ids=["serendipity-ram-2024", "ht-samson-2024"],
    notes="Was ram for Pen 4 group (Elsie, Nori, Trouble, Bsoe, Bsoed, Banana). Deceased per weak resistance list. Pen 4 entry says 'Samson 4'. 100% Hampshire per Buck, tag-2241, and 430-2079 breeding pages (3/4 pages). Ram weight 400lbs, ewe weight prediction 340lbs. Sired Serendipity's 2024 ram lamb and Half Tail's 2024 lamb (born 2/12/24, 10lbs). Note: OAV 2222 and Serendipity breeding pages list Samson as 100% Southdown — possible data entry error (other pages say Hampshire). Serendipity page also shows Samson with Sam's weights (165/125) instead of his actual weights (400/340).",
    confidence="high",
    notebook_image=["IMG_8628.PNG", "IMG_8629.PNG"]))

# Sam - ram for Pen 3 (100% Gulf Coast Native)
db["sheep"].append(sheep("sam", "Sam", "ram", "alive",
    pen="Pen 3",
    breed_composition={"primary": "Gulf Coast Native", "percentages": {"Gulf Coast Native": 100}, "coat_type": "wool", "hair_percentage": 0},
    weight_lbs=165,
    is_breeding_animal=True,
    treatments=[{"date": "2025-tag-day", "treatment": "iron (FAMACHA 3)"}],
    notes="Ram for pen 3 group. 100% Gulf Coast Native per Merrie breeding page. Ram weight 165lbs, ewe weight prediction 125lbs (from multiple breeding pages). Given iron treatment. Pen 3 includes: Baby, Baby momma, Zara, Half tail, New big girl 2.",
    confidence="high",
    notebook_image=["IMG_8641.PNG"]))

# Kaladin - ram for Pen 1 (S'More x Serendipity)
# NOTE: Living Kaladin (tag 014) is S'More x Serendipity. The deceased Kaladin (tag 24)
# was S'More x Anna = 50Cr/50K. Breeding page math for Merrie confirms this Kaladin
# has Babydoll and Jacob from Serendipity's side (via Shaggy).
# Extension Service 2023: Lamb ID 14, SR × SM, born 5/11/2023, sex 2 (ewe), single, birth wt 6lbs.
#   Weaned 7/18/2023 at 52lbs (68 days). ADG 0.68. Adj WW 100 (ratio 137 — highest!).
#   NOTE: Extension service lists sex as "2" (ewe), but all other records say ram.
#   This is likely a data entry error — kept as ram per all other sources.
db["sheep"].append(sheep("kaladin", "Kaladin", "ram", "alive",
    tag="014",
    aliases=["Kal"],
    pen="Pen 1",
    breed_composition={"primary": "Cracker/St Augustine/Babydoll/Jacob/Katahdin", "percentages": {"Cracker": 50, "St Augustine": 18.75, "Babydoll": 12.5, "Jacob": 12.5, "Katahdin": 6.25}, "coat_type": "mixed", "hair_percentage": 56},
    color_markings="White w black ears",
    dob="2023-05-11",
    sire_id="smore", dam_id="serendipity",
    is_breeding_animal=True,
    birth_weight=6,
    weight_lbs=52,
    measurements={"girth": 26, "length": 23, "calculated_weight": 51.8, "date": "2023-2024"},
    extension_service={"lamb_id": 14, "birth_date": "2023-05-11", "birth_weight": 6, "birth_rearing_type": 1, "sex_code": 2, "weaning_date": "2023-07-18", "weaning_weight": 52, "weaning_age_days": 68, "age_group": 60, "wda": 2.00, "adg": 0.68, "age_corrected_ww": 96, "adjusted_ww": 100, "adj_ww_ratio": 137},
    notes="Living Kaladin tag 014. DOB 5/11/2023 per extension service. S'More (100%Cr) x Serendipity (25%Babydoll/25%Jacob/12.5%K/37.5%SA). Breed: 50%Cr/18.75%SA/12.5%Babydoll/12.5%Jacob/6.25%K. Birth weight 6lbs (single). Weaned 7/18/2023 at 52lbs (68 days). ADG 0.68. Adjusted WW 100 (ratio 137 — HIGHEST in 2023 class). Extension service lists sex as ewe (code 2) — likely data entry error, all other sources say ram. The deceased Kaladin (tag 24) was S'More x Anna = 50Cr/50K — different animal. With Merrie, Gertrude Moon (Abg), Fm in Pen 1.",
    confidence="high",
    notebook_image=["IMG_8624.PNG", "IMG_8630.PNG"]))

# S'More - Cracker ram from CSV (parents: Gigantus x Minnie, off-farm)
db["sheep"].append(sheep("smore", "S'More", "ram", "deceased",
    tag="22",
    breed_composition={"primary": "Cracker", "percentages": {"Cracker": 100}, "coat_type": "mixed", "hair_percentage": 50},
    color_markings="Red",
    weight_lbs=200, dob="2021-01-14", dob_approximate=True,
    is_breeding_animal=True,
    offspring_ids=["kaladin", "merrie", "pippin", "fox-tail", "trouble-lamb-2023", "bsoed-lamb-2023", "bt-lamb-2023", "ht-ext-lamb-2023", "shaggy-1", "shaggy-2", "bk1", "bk2", "circle-tail", "merrie-bs2"],
    notes="Flock spreadsheet: Tag 22, 100% Cracker, 200lbs. Sire: Gigantus, Dam: Minnie (off-farm). Deceased per spreadsheet. Was major breeding ram - sired many 2022-2023 lambs including Pippen and merrie-BS2 (by BSOED), Merrie (by Half Tail), Fox Tail (by Trouble, tag 17 — deceased Helene), Foxtail 1/BK1 and Foxtail 2/BK2 (by Brown Knee), Circle Tail (by Brown Knee), BT1/BT2 (by Broken Tail), HT ext lamb (by Half Tail), Shaggy1/Shaggy2 (by Shaggy), Bsoed's lamb, Trouble's lamb, and Kaladin (by Serendipity). The deceased Kaladin (tag 24) was S'More x Anna.",
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

# Pippin / BSOE1 - ram, tag 015 (S'More x BSOE)
# Extension Service 2023: Lamb ID 4, BSOE × SM, born 1/29/2023, ram, single (type 1), birth wt 9lbs.
#   Weaned 5/23/2023 at 59lbs (114 days). ADG 0.44. Adj WW 62 (ratio 77).
# CORRECTED: Per BSOED breeding page, Pippen is S'More × BSOED (not BSOE), born 12/12/2022. Sold.
# Breed: S'More(100%Cr) x BSOED(40.5%K/59.5%SA) = 50%Cr/20.25%K/29.75%SA
db["sheep"].append(sheep("pippin", "Pippin", "ram", "sold",
    tag="015",
    aliases=["BSOE1", "Pippen"],
    dob="2022-12-12",
    sire_id="smore", dam_id="bsoed",
    breed_composition={"primary": "Cracker/St Augustine/Katahdin", "percentages": {"Cracker": 50, "St Augustine": 29.75, "Katahdin": 20.25}, "coat_type": "mixed", "hair_percentage": 70},
    birth_weight=9,
    weight_lbs=80,
    measurements={"girth": 28, "length": 30.75, "calculated_weight": 80.4, "date": "2023-2024"},
    extension_service={"lamb_id": 4, "birth_date": "2023-01-29", "birth_weight": 9, "birth_rearing_type": 1, "sex_code": 1, "weaning_date": "2023-05-23", "weaning_weight": 59, "weaning_age_days": 114, "age_group": 120, "wda": 0.52, "adg": 0.44, "age_corrected_ww": 62, "adjusted_ww": 62, "adj_ww_ratio": 77},
    notes="Pippin/BSOE1. Tag 015. S'More (100%Cr) x BSOED (40.5K/59.5SA). DOB 12/12/2022 per BSOED breeding page. Sold. White body, tan ear, Wool (probably). Birth weight 9lbs (single). Weaned 5/23/2023 at 59lbs (114 days). ADG 0.44. Adj WW 62 (ratio 77). Weight calculator: 80.4lbs. 50%Cr/29.75%SA/20.25%K. CORRECTED: Dam changed from BSOE to BSOED per breeding page.",
    confidence="high",
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

# Buck (Original) - ram, was in chicken coop — from Windlestone
# Breed confirmed by Buck breeding page: 48%Awassi/2%EF/50%Katahdin.
# DECEASED — "deceased helene" noted on breeding page attributes.
# Replaced by his brother, also named Buck (see buck-current).
db["sheep"].append(sheep("buck-original", "Buck (Original)", "ram", "deceased",
    aliases=["Buck"],
    breed_composition={"primary": "Katahdin/Awassi/East Friesian", "percentages": {"Katahdin": 50, "Awassi": 48, "East Friesian": 2}, "coat_type": "mixed", "hair_percentage": 50},
    pen="Chicken Coop",
    weight_lbs=212,
    is_breeding_animal=True,
    status_notes="Deceased - Hurricane Helene",
    notes="Original Buck ram in chicken coop. Came from Windlestone. 48%Awassi/2%EF/50%Katahdin confirmed by Buck breeding page. Ram weight 212lbs, ewe weight prediction 155.2lbs. Deceased per breeding page ('deceased helene'). Replaced by his brother (also named Buck). Not related to Nori — listed as prospective breeding option only. Prospective breedings calculated with: Sir Loin, Rocky, Sam, Samson (100%Hampshire), Louise Dorper (100%BHD), Ruth's St Augustine (100%Hampshire?), Kelsier (listed as 'UF Ram Test', 100%Katahdin).",
    confidence="high"))

# Buck (Current) - brother of original Buck, now in chicken coop
# Same breed as his brother (Katahdin/Awassi/EF from Windlestone).
db["sheep"].append(sheep("buck", "Buck", "ram", "alive",
    breed_composition={"primary": "Katahdin/Awassi/East Friesian", "percentages": {"Katahdin": 50, "Awassi": 48, "East Friesian": 2}, "coat_type": "mixed", "hair_percentage": 50},
    pen="Chicken Coop",
    is_breeding_animal=True,
    notes="Current Buck in chicken coop. Brother of original Buck who died in Hurricane Helene. Same breed: 48%Awassi/2%EF/50%Katahdin. From Windlestone (same source as brother).",
    confidence="high"))

# Dodge - ram (Sir Loin x Broken Tail) — Little Daisy's sire
# Inbred: Sir Loin is both sire and grandsire (Broken Tail's sire).
# Breed: avg(25K/75SA, 28.125K/65.625SA/6.25BBB) = 26.5625K/70.3125SA/3.125BBB
db["sheep"].append(sheep("dodge", "Dodge", "ram", "unknown",
    sire_id="sir-loin", dam_id="broken-tail",
    breed_composition={"primary": "St Augustine/Katahdin/BBB", "percentages": {"St Augustine": 70.3125, "Katahdin": 26.5625, "Barbados Blackbelly": 3.125}, "coat_type": "mixed", "hair_percentage": 27},
    offspring_ids=["little-daisy"],
    notes="Little Daisy's sire. Sir Loin (25K/75SA) x Broken Tail (28.125K/65.625SA/6.25BBB). Inbred: Sir Loin is Broken Tail's sire. Status unknown — from Little Daisy breeding page pedigree.",
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
    offspring_ids=["nori-son", "eclipse"],
    breed_composition={"primary": "ABB/Wiltshire Horn", "percentages": {"American Blackbelly": 50, "Wiltshire Horn": 50}, "coat_type": "hair", "hair_percentage": 100},
    color_markings="Badger",
    weight_lbs=139, dob="2023-02-01",
    notes="Nori breeding page: 50%ABB/50%WH, tag 21 (tag lost). Ewe weight 138.83lbs, ram weight 217.5lbs. Sire: 100%ABB, Dam: 100%WH. DOB ~2/1/2023. Mother of NoriSon (tag 54) and Eclipse (2022, deceased Hurricane Idalia). In pen 4.",
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
# Breeding page: 25%Babydoll/25%Jacob/12.5%K/37.5%SA. Tag 30. Ewe weight 137.5lbs.
# 2022 offspring: Kaladin (by S'More). 2024 offspring: Ram (by Samson).
# FAMACHA 1 (9-20-23). Not flighty, Good Mother, Attentive, Protective, Docile, Heat Tolerant.
# Breeding page says Pen 2, but user said Pen 4 with twins — user/notebook is authoritative.
db["sheep"].append(sheep("serendipity", "Serendipity", "ewe", "alive",
    tag="030",
    aliases=["SE", "Seren"],
    pen="Pen 4",
    breed_composition={"primary": "St Augustine/Babydoll/Jacob/Katahdin", "percentages": {"St Augustine": 37.5, "Babydoll": 25, "Jacob": 25, "Katahdin": 12.5}, "coat_type": "mixed", "hair_percentage": 75},
    color_markings="Black",
    weight_lbs=138, dob="2022-03-25",
    date_acquired="2022-03-25",
    sire_id="sir-loin", dam_id="shaggy",
    famacha_scores=[{"score": 1, "date": "2023-09-20", "notes": "no treatment needed"}],
    offspring_ids=["serendipitys-baby-036", "kaladin", "serendipity-ram-2024"],
    health_notes=["Low FAMACHA score 7-24-25 along with GG and Lara"],
    is_breeding_animal=True,
    notes="Breeding page: 25%Babydoll/25%Jacob/12.5%K/37.5%SA. Tag 30. DOB 3/25/2022. Acquired 3/25/2022. Ewe weight 137.5lbs, ram weight prediction 222.75lbs. Sir Loin (25K/75SA) x Shaggy (50Babydoll/50Jacob). Black w white on head and spots by mouth. Not flighty, Good Mother, Attentive, Protective, Docile, Heat Tolerant. FAMACHA 1 (9-20-23). 2023: S'More lamb born 1/29/2023 — sterile, deceased (parasites). Also 2023: Kaladin (by S'More, born 5/11/2023). 2024: ram (by Samson). Also mother of Mc12/036 baby ewe. Bred to Kaladin 9-6-23, Samson Jan-Feb. Pen 4 with twins (2026). Lambed 2026-02-03 (twins).",
    confidence="high",
    notebook_image=["IMG_8629.PNG", "IMG_8632.PNG", "IMG_8640.PNG", "IMG_8642.PNG"]))

# Serendipity's 2024 ram lamb (by Samson)
# Breed: avg(25Babydoll/25Jacob/12.5K/37.5SA, 100Hampshire) = 12.5Babydoll/12.5Jacob/6.25K/50Hampshire/18.75SA
db["sheep"].append(sheep("serendipity-ram-2024", "Serendipity's Ram (2024)", "ram", "alive",
    sire_id="samson", dam_id="serendipity",
    breed_composition={"primary": "Hampshire/St Augustine/Babydoll/Jacob/Katahdin", "percentages": {"Hampshire": 50, "St Augustine": 18.75, "Babydoll": 12.5, "Jacob": 12.5, "Katahdin": 6.25}, "coat_type": "mixed", "hair_percentage": 19},
    notes="Serendipity's 2024 ram lamb by Samson (100% Hampshire). Breed: 50%Hampshire/18.75%SA/12.5%Babydoll/12.5%Jacob/6.25%K. From Serendipity breeding page 2024 section.",
    confidence="high"))

# Serendipity's baby - 036, Mc12
db["sheep"].append(sheep("serendipitys-baby-036", "Serendipity's Baby", "ewe", "alive",
    tag="036", mc_tag="Mc12",
    dam_id="serendipity",
    notes="036, Mc12. Serendipity's baby ewe. Photo from March 18, 2024 shows white lamb with yellow MC12 ear tag.",
    confidence="high",
    notebook_image=["IMG_8632.PNG"]))

# Little Daisy - ewe, tag 35 — Dodge (Sir Loin x Broken Tail) x Daisy (Sir Loin x Half Tail)
# Breeding page: 4.6875%BBB / 27.325%K / 67.9625%SA. DOB 3-23-23. Pen 3 on breeding page.
# Previously had incorrect breed (12.5%BHD/50%Cr/18.75%K/18.75%SA) from misidentified data.
# Corrected from Little Daisy breeding page which shows full pedigree.
db["sheep"].append(sheep("little-daisy", "Little Daisy", "ewe", "alive",
    tag="035",
    pen="Pen 5",
    dob="2023-03-23",
    sire_id="dodge", dam_id="daisy",
    breed_composition={"primary": "St Augustine/Katahdin/BBB", "percentages": {"St Augustine": 67.9625, "Katahdin": 27.325, "Barbados Blackbelly": 4.6875}, "coat_type": "mixed", "hair_percentage": 30},
    weight_lbs=145,
    offspring_ids=["little-daisys-baby-mc01"],
    is_breeding_animal=True,
    health_notes=["Needed parasite treatment April 13 2025 - eyes were white (tag 35)"],
    notes="Breeding page: Dodge (Sir Loin x Broken Tail) x Daisy (Sir Loin x Half Tail). 4.6875%BBB/27.325%K/67.9625%SA. DOB 3/23/2023. Ewe weight prediction 144.69lbs, ram weight prediction 270.91lbs. Breeding page says Pen 3 (notebook says Pen 5 — notebook authoritative). Bred to Rocky (8-13-23). Attributes: Not Flighty, Good Mother, Attentive, Protective, Heat Tolerant, Breed All Year. Mother of Mc01 (baby's baby). Needed parasite treatment April 13, 2025 with white eyes. Inbred: Sir Loin is grandsire on both sides.",
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
    offspring_ids=["broken-tail", "half-tails-baby", "elsie", "ht-ext-lamb-2023", "merrie", "daisy", "ht-samson-2024"],
    notes="Flock spreadsheet: 12.5% BBB / 31.25% Katahdin / 56.25% St Augustine, 180lbs. DOB ~1/1/2017. Sir Loin (25K/75SA) x Hersheys (25BBB/37.5K/37.5SA). Born as twin. 25% inbreeding (Sir Loin is both sire and maternal grandsire). Grandparents: Auction Sheep 1 & 2 (via Chip), Razzle & Frazzle (via Sugar). Mother of Broken Tail, Elsie (by Well Done, DOB 2/8/2022, ADG 0.56), HT ext lamb (by S'More), Merrie (by S'More), Daisy, and 2024 lamb (by Samson, born 2/12/2024, 10lb birth wt). Ewe weight prediction 140lbs (breeding page). In pen 3 (Sam group) per notebook.",
    confidence="high",
    csv_row=16,
    notebook_image=["IMG_8629.PNG"]))

# Half Tail's 2024 lamb (Samson x Half Tail, born 2/12/2024)
# Per Half Tail breeding page. Bred 8-31-23, born 2-12-24. Birth wt 10lbs.
# Breed: Samson(100%Hampshire) x HT(12.5BBB/31.25K/56.25SA) = 50%H/6.25%BBB/15.625%K/28.125%SA
db["sheep"].append(sheep("ht-samson-2024", "Half Tail's Lamb (2024)", "unknown", "unknown",
    sire_id="samson", dam_id="half-tail",
    dob="2024-02-12",
    breed_composition={"primary": "Hampshire/St Augustine/Katahdin/BBB", "percentages": {"Hampshire": 50, "St Augustine": 28.125, "Katahdin": 15.625, "Barbados Blackbelly": 6.25}, "coat_type": "mixed", "hair_percentage": 50},
    birth_weight=10,
    notes="Samson (100%H) x Half Tail (12.5BBB/31.25K/56.25SA). Born 2/12/2024. Bred 8/31/2023. Birth weight 10lbs. 50%Hampshire/28.125%SA/15.625%K/6.25%BBB. Sex unknown. Per Half Tail breeding page.",
    confidence="high"))

# Broken Tail - ewe
db["sheep"].append(sheep("broken-tail", "Broken Tail", "ewe", "alive",
    aliases=["Bt", "BT"],
    tag="034",
    pen="Pen 5",
    breed_composition={"primary": "St Augustine/Katahdin/BBB", "percentages": {"St Augustine": 65.625, "Katahdin": 28.125, "Barbados Blackbelly": 6.25}, "coat_type": "mixed", "hair_percentage": 34},
    color_markings="White",
    weight_lbs=225, dob="2018-01-18", dob_approximate=True,
    sire_id="sir-loin", dam_id="half-tail",
    offspring_ids=["bt-lamb-2023", "dodge"],
    notes="Flock spreadsheet: 6.25% BBB / 28.125% Katahdin / 65.625% St Augustine, 225lbs. DOB 1/18/2018. Sir Loin (25K/75SA) x Half Tail (12.5BBB/31.25K/56.25SA). Mother of BT1 and BT2 lambs (by S'More) and Dodge (by Sir Loin — inbred). Lambed 2026-01-20 (twins). In pen 5 (Rocky group) per notebook. Owner note: 'Gentle and sturdy matriarch. She's survived coyotes, dogs, floods, always twins unassisted, and raises them well. They are always good sized. Crappy name for a phenomenal sheep.'",
    confidence="high",
    csv_row=17,
    notebook_image=["IMG_8629.PNG", "IMG_8642.PNG"]))

# Trouble - ewe, tag 33 (Sir Loin x Haylee Lawson)
# Extension Service 2023: Lamb ID 17, T × SM, born 2/22/2023, ram, single (type 1), birth wt 8lbs.
#   Weaned 5/23/2023 at 84lbs (90 days). ADG 0.84. Adj WW 84 (ratio 104).
db["sheep"].append(sheep("trouble", "Trouble", "ewe", "alive",
    tag="033",
    aliases=["Tr", "T"],
    pen="Pen 5",
    breed_composition={"primary": "Katahdin/St Augustine/Dorper", "percentages": {"Katahdin": 37.5, "St Augustine": 37.5, "Dorper": 25}, "coat_type": "hair", "hair_percentage": 62},
    color_markings="White",
    weight_lbs=180, dob="2021-01-01", dob_approximate=True,
    sire_id="sir-loin", dam_id="haylee-lawson",
    is_breeding_animal=True,
    offspring_ids=["trouble-lamb-2023", "fox-tail"],
    notes="Flock spreadsheet: Tag 9/retagged 33, 25%Dorper/37.5%K/37.5%SA, 180lbs. DOB ~1/1/2021. Sir Loin (25K/75SA) x Haylee Lawson (50D/50K). 2023 offspring: ram lamb (ID 17) by S'More born 2/22/2023 (8lb birth wt, single, weaned 84lbs at 90 days — 2nd best male lamb). Also mother of Fox Tail (tag 17, by S'More, died in Helene). In pen 5 per notebook.",
    confidence="high",
    notebook_image=["IMG_8642.PNG"]))

# Bsoe (Black Spot on Ear) - ewe, tag 32 (Sir Loin x Two Pence)
# Breeding page: 56K/44SA, Pen 4 (now Pen 5 per notebook). Ram weight 241.6, ewe weight 144.4.
# 2023 bred to Merrie (ram). Prospective breeding offspring have label glitch: shows "Southdown" for Katahdin and "St Croix" for St Augustine — numbers correct, names wrong.
db["sheep"].append(sheep("bsoe", "Bsoe", "ewe", "alive",
    tag="032",
    aliases=["Black Spot on Ear", "BSOE"],
    pen="Pen 5",
    breed_composition={"primary": "Katahdin/St Augustine", "percentages": {"Katahdin": 56, "St Augustine": 44}, "coat_type": "hair", "hair_percentage": 56},
    color_markings="White",
    weight_lbs=185, dob="2019-01-01", dob_approximate=True,
    sire_id="sir-loin", dam_id="two-pence",
    is_breeding_animal=True,
    offspring_ids=["bsoed"],
    notes="Flock spreadsheet: 56%K/44%SA, 185lbs. DOB ~1/1/2019. Sir Loin (25K/75SA) x Two Pence. Mother of BSOED (by Sir Loin). Tag 32 (switched with Bsoed). Breeding page: Pen 4 (now Pen 5 per notebook). Ram weight projection 241.6lbs, ewe weight projection 144.4lbs. 2023 bred to Merrie (tag 016, ram). 2025: 2 ewe lambs born 1-25-25 by Awassi×Kat ram. CORRECTED: Pippen and Merrie-BS2 are BSOED's offspring, not BSOE's, per BSOED breeding page.",
    confidence="high",
    notebook_image=["IMG_8642.PNG"]))

# Bsoed (Black Spot Daughter) - ewe, tag 31 (Sir Loin x BSOE)
# Extension Service 2023: Lamb ID 1, BSOE D × SM, born 2/22/2023, ram, type 4, birth wt 8lbs.
#   Weaned 5/23/2023 at 64lbs (90 days). ADG 0.62. Adj WW 77 (ratio 96).
db["sheep"].append(sheep("bsoed", "Bsoed", "ewe", "alive",
    tag="031",
    aliases=["Black Spot Daughter", "BSOED", "BSOE D", "Black Spot on Ear Daughter"],
    pen="Pen 5",
    breed_composition={"primary": "St Augustine/Katahdin", "percentages": {"Katahdin": 40.5, "St Augustine": 59.5}, "coat_type": "mixed", "hair_percentage": 40},
    color_markings="White",
    weight_lbs=175, dob="2020-01-18", dob_approximate=True,
    sire_id="sir-loin", dam_id="bsoe",
    born_as_multiple=True,
    is_breeding_animal=True,
    offspring_ids=["bsoed-lamb-2023", "pippin", "merrie-bs2"],
    notes="Flock spreadsheet: ~40.5%K/~59.5%SA, 175lbs. DOB 1/18/2020. Sir Loin (25K/75SA) x BSOE (56K/44SA). Tag 31 (switched with Bsoe). Born as triplet per breeding page. Mother of Pippen (sold) and Merrie-BS2 (by S'More, born 12/12/2022) per breeding page. 2023 offspring: ram lamb (ID 1) by S'More born 2/22/2023. 2025: 2 lambs (ewe + ram) born 1-25-25 by Buck. In pen 5 per notebook.",
    confidence="high",
    notebook_image=["IMG_8642.PNG"]))

# FM's sire - Tunis ram (off-farm)
db["sheep"].append(sheep("fm-sire", "FM's Sire (Tunis Red)", "ram", "unknown",
    breed_composition={"primary": "Tunis", "percentages": {"Tunis": 100}, "coat_type": "wool", "hair_percentage": 0},
    offspring_ids=["fm"],
    notes="FM's sire per breeding page. Tunis Red ram. Off-farm.",
    confidence="medium"))

# FM's dam - Cotswold ewe (off-farm)
db["sheep"].append(sheep("fm-dam", "FM's Dam (Cotswold)", "ewe", "unknown",
    breed_composition={"primary": "Cotswold", "percentages": {"Cotswold": 100}, "coat_type": "wool", "hair_percentage": 0},
    offspring_ids=["fm"],
    notes="FM's dam per breeding page. Cotswold ewe. Off-farm.",
    confidence="medium"))

# FM - ewe (purchased, GA tag 1568-011)
# Extension Service 2023: Lamb ID 9, FM × SL, born 4/1/2023, ram, single (type 1), birth wt 12lbs.
#   Weaned 5/23/2023 at 67lbs (52 days). ADG 1.06. Adj WW 80 (ratio 110).
db["sheep"].append(sheep("fm", "FM", "ewe", "alive",
    pen="Pen 1",
    weak_resistance=True,
    breed_composition={"primary": "Cotswold/Tunis", "percentages": {"Cotswold": 50, "Tunis": 50}, "coat_type": "wool", "hair_percentage": 0},
    color_markings="Tunis Red",
    weight_lbs=200, dob="2021-02-14",
    date_acquired="2021-02-27",
    sire_id="fm-sire", dam_id="fm-dam",
    is_breeding_animal=True,
    offspring_ids=["fm-lamb-2023", "flan"],
    notes="Tag GA1568-011, 50% Cotswold / 50% Tunis, Tunis Red, 200lbs. DOB 2/14/2021 per breeding page. Acquired 2/27/2021. Sire: Tunis (red), Dam: Cotswold. 2023: FM1 ram lamb (ID 9) by Sir Loin born 4/1/2023 (12lb birth wt, single, weaned 67lbs at 52 days). Eclipse also listed on breeding page as potential 2023 offspring (dec?/April — may not have survived). 2026: Flan (by Sir Loin, born 2/1/2026). In Pen 1 (Kaladin group). On weak resistance list.",
    confidence="high",
    csv_row=15,
    notebook_image=["IMG_8628.PNG", "IMG_8630.PNG", "IMG_8636.PNG", "IMG_8641.PNG"]))

# FM1 - ewe (Sir Loin x FM, born 4/1/2023)
# FM breeding page confirms FM1 = Sir Loin × FM. Same as extension service lamb ID 9.
# Breed: SL(25K/75SA) × FM(50Cotswold/50Tunis) = 25%Cotswold/12.5%K/37.5%SA/25%Tunis
db["sheep"].append(sheep("fm1", "FM1", "ewe", "alive",
    tag="009",
    pen="Pen 6",
    sire_id="sir-loin", dam_id="fm",
    dob="2023-04-01",
    breed_composition={"primary": "St Augustine/Cotswold/Tunis/Katahdin", "percentages": {"St Augustine": 37.5, "Cotswold": 25, "Tunis": 25, "Katahdin": 12.5}, "coat_type": "mixed", "hair_percentage": 12},
    weak_resistance=True,
    weight_lbs=67,
    measurements={"girth": 29.5, "length": 23, "calculated_weight": 66.7, "date": "2023-2024"},
    notes="FM1 = Sir Loin × FM per FM breeding page. Tag 009. DOB 4/1/2023. 25%Cotswold/12.5%K/37.5%SA/25%Tunis. Same as extension service lamb ID 9 (sex may have been misrecorded as ram in extension service). In pen 6 (no ram). On weak resistance list. On 'Ewes to Upgrade' list. Half wool. Weight calculator: 66.7lbs.",
    confidence="high",
    notebook_image=["IMG_8624.PNG", "IMG_8628.PNG", "IMG_8629.PNG", "IMG_8642.PNG"]))

# Eclipse - RAM (Sir Loin x Nori) - DECEASED after Hurricane Idalia
# CORRECTED: Eclipse was a ram, not a ewe. Sire is Sir Loin per FM breeding page and Azure breeding page.
db["sheep"].append(sheep("eclipse", "Eclipse", "ram", "deceased",
    sire_id="sir-loin", dam_id="nori",
    breed_composition={"primary": "St Augustine/ABB/Wiltshire Horn/Katahdin", "percentages": {"American Blackbelly": 25, "Katahdin": 12.5, "St Augustine": 37.5, "Wiltshire Horn": 25}, "coat_type": "hair", "hair_percentage": 62},
    weight_lbs=42,
    measurements={"girth": 22, "length": 26, "calculated_weight": 41.9, "date": "2023-2024"},
    status_notes="Died after Hurricane Idalia (Aug 2023)",
    notes="25%ABB/12.5%K/37.5%SA/25%WH. Sir Loin (25K/75SA) x Nori (50ABB/50WH). RAM (corrected from ewe). Nori's 2022 offspring. Weight calculator: 41.9lbs. Died after Hurricane Idalia (Aug/Sep 2023). Was in Pen 1 before death. Also listed on FM breeding page as potential offspring.",
    confidence="high",
    notebook_image=["IMG_8624.PNG", "IMG_8630.PNG"]))

# CORRECTION: ABG = Anna's Big Girl = Anna's Big One = Banana (tag 44, alive, in Pen 4).
# ABG is NOT Gertrude Moon. They are separate sheep.
# Gertrude Moon = BF = Bitch Face = "Unnamed" = tag 22, 100%ABB, DECEASED.

# Gertrude Moon / Bitch Face - tag 22, 100% American Black Belly, DECEASED
# Breeding page: 100%ABB. DOB 2020. Sire: ABB Ram, Dam: ABB Ewe. Acquired 5-4-23.
# Awful mother — no offspring kept. Owner's mother calls her "Bitch Face" / "BF".
db["sheep"].append(sheep("gertrude-moon", "Gertrude Moon", "ewe", "deceased",
    tag="022",
    aliases=["Bitch Face", "BF", "Unnamed", "ABB ewe"],
    breed_composition={"primary": "American Black Belly", "percentages": {"American Blackbelly": 100}, "coat_type": "hair", "hair_percentage": 100},
    weight_lbs=144, dob="2020-01-01", dob_approximate=True,
    sire_id="gertrude-moon-sire", dam_id="gertrude-moon-dam",
    born_as_multiple=True,
    date_acquired="2023-05-04",
    famacha_scores=[{"score": 4, "date": "2023-09-06", "notes": "Ivermectin"}, {"score": 2, "date": "2023-09-18", "notes": "no treatment"}],
    treatments=[{"date": "2023-09-06", "treatment": "Ivermectin"}],
    measurements={"girth": 36.75, "length": 32, "calculated_weight": 144.1, "date": "2023-2024"},
    offspring_ids=["gm-twin1-2024", "gm-twin2-2024"],
    status_notes="Deceased. Awful mother — no offspring kept.",
    notes="Gertrude Moon aka Bitch Face (BF). Tag 22. 100%ABB. DOB ~2020. Acquired 5-4-23. DECEASED — awful mother, no offspring kept. Twins born 1-2-24 by Sir Loin (not kept). FAMACHA 4→2 (Sept 2023). Weight calculator: 144.1lbs. NOT the same as ABG (Anna's Big One/Banana).",
    confidence="high",
    notebook_image=["IMG_8630.PNG", "IMG_8641.PNG"]))

# Gertrude Moon's sire - ABB Ram (off-farm)
db["sheep"].append(sheep("gertrude-moon-sire", "Gertrude Moon's Sire", "ram", "unknown",
    breed_composition={"primary": "American Black Belly", "percentages": {"American Blackbelly": 100}, "coat_type": "hair", "hair_percentage": 100},
    offspring_ids=["gertrude-moon"],
    notes="Gertrude Moon's sire per breeding page. 'ABB Ram.' Off-farm.",
    confidence="medium"))

# Gertrude Moon's dam - ABB Ewe (off-farm)
db["sheep"].append(sheep("gertrude-moon-dam", "Gertrude Moon's Dam", "ewe", "unknown",
    breed_composition={"primary": "American Black Belly", "percentages": {"American Blackbelly": 100}, "coat_type": "hair", "hair_percentage": 100},
    offspring_ids=["gertrude-moon"],
    notes="Gertrude Moon's dam per breeding page. 'ABB Ewe.' Off-farm.",
    confidence="medium"))

# Gertrude Moon's 2024 twin 1 — NOT KEPT
db["sheep"].append(sheep("gm-twin1-2024", "GM Twin 1 (2024)", "unknown", "deceased",
    sire_id="sir-loin", dam_id="gertrude-moon",
    dob="2024-01-02",
    breed_composition={"primary": "ABB/St Augustine/Katahdin", "percentages": {"American Blackbelly": 50, "St Augustine": 37.5, "Katahdin": 12.5}, "coat_type": "hair", "hair_percentage": 62},
    status_notes="Not kept — Gertrude Moon was an awful mother.",
    notes="Born 1-2-24. Sir Loin x Gertrude Moon. Not kept per owner.",
    confidence="high"))

# Gertrude Moon's 2024 twin 2 — NOT KEPT
db["sheep"].append(sheep("gm-twin2-2024", "GM Twin 2 (2024)", "unknown", "deceased",
    sire_id="sir-loin", dam_id="gertrude-moon",
    dob="2024-01-02",
    breed_composition={"primary": "ABB/St Augustine/Katahdin", "percentages": {"American Blackbelly": 50, "St Augustine": 37.5, "Katahdin": 12.5}, "coat_type": "hair", "hair_percentage": 62},
    status_notes="Not kept — Gertrude Moon was an awful mother.",
    notes="Born 1-2-24. Sir Loin x Gertrude Moon. Not kept per owner.",
    confidence="high"))

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

# Fox Tail - ewe, tag 17 (S'More x Trouble) - DECEASED (Hurricane Helene)
db["sheep"].append(sheep("fox-tail", "Fox Tail", "ewe", "deceased",
    tag="017",
    sire_id="smore", dam_id="trouble",
    breed_composition={"primary": "Cracker/St Augustine/Katahdin/Dorper", "percentages": {"Cracker": 50, "St Augustine": 18.75, "Katahdin": 18.75, "Black Headed Dorper": 12.5}, "coat_type": "mixed", "hair_percentage": 62},
    weight_lbs=118,
    measurements={"girth": 35, "length": 29, "calculated_weight": 118.4, "date": "2023-2024"},
    notes="Tag 17. S'More (100%Cr) x Trouble (37.5K/37.5SA/25Dorper). 50%Cr/18.75%SA/18.75%K/12.5%Dorper. Died in Hurricane Helene. Weight calculator: 118.4lbs. Was on 'Ewes to Upgrade' list. Was in pen 6 (no ram).",
    confidence="high",
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
# Breeding page: 100% Black Headed Dorper. DOB 2018. Received from Charles Elingham.
# Sire: dorper ram, Dam: dorper ewe. Multiple: Y. Ewe weight 159.82lbs, Ram weight 300lbs.
# 2023: Bred to Sir Loin 7-4-23, due Nov 23. Born 12-30-23: Oliver (3.75lbs) and Spicy (5.8lbs).
# Medical: FAMACHA 3 on 9-6-23 (Ivermectin, post-Idalia stress); FAMACHA 2 on 9-18-23 (no treatment).
db["sheep"].append(sheep("lara", "Lara", "ewe", "alive",
    tag="023",
    aliases=["Dorper 23"],
    pen="Pen 2",
    breed_composition={"primary": "Black Headed Dorper", "percentages": {"Black Headed Dorper": 100}, "coat_type": "hair", "hair_percentage": 100},
    weight_lbs=160, dob="2018-01-01", dob_approximate=True,
    sire_id="lara-sire", dam_id="lara-dam",
    weak_resistance=True,
    born_as_multiple=True,
    measurements={"girth": 36.75, "length": 35.5, "calculated_weight": 159.8, "date": "2023-2024"},
    famacha_scores=[{"score": 3, "date": "2023-09-06", "notes": "Ivermectin after Idalia, probably stress induced"}, {"score": 2, "date": "2023-09-18", "notes": "no treatment"}],
    treatments=[{"date": "2023-09-06", "treatment": "Ivermectin (post-Hurricane Idalia stress)"}, {"date": "2024-10-24", "treatment": "iron and vitamin B"}],
    health_notes=["Sick sheep note: one of Dorper 23/25 is Lara", "Low score 7-24-25"],
    received_from="Charles Elingham",
    offspring_ids=["oliver", "spicy"],
    is_breeding_animal=True,
    notes="Tag 23. 100% Black Headed Dorper per breeding page (previously listed as generic Dorper). DOB 2018. Sire: dorper ram, Dam: dorper ewe (both off-farm). Received from Charles Elingham. Multiple: Y. Ewe weight 159.82lbs, ram weight projection 300lbs. 2023: bred to Sir Loin 7-4-23, due Nov 23. Born 12-30-23: Oliver (3.75lbs) and Spicy (5.8lbs) — twins by Sir Loin. FAMACHA 3 on 9-6-23 (Ivermectin, post-Idalia stress), FAMACHA 2 on 9-18-23 (no treatment). Weight calculator: 159.8lbs. On 'Ewes to Upgrade' and weak resistance list.",
    confidence="high",
    notebook_image=["IMG_8626.PNG", "IMG_8628.PNG", "IMG_8630.PNG", "IMG_8636.PNG", "IMG_8640.PNG", "IMG_8641.PNG"]))

# Lara's sire - dorper ram (off-farm, received from Charles Elingham)
db["sheep"].append(sheep("lara-sire", "Lara's Sire", "ram", "unknown",
    breed_composition={"primary": "Dorper", "percentages": {"Dorper": 100}, "coat_type": "hair", "hair_percentage": 100},
    offspring_ids=["lara"],
    notes="Lara's sire per Lara breeding page. 'Dorper ram.' Off-farm, from Charles Elingham.",
    confidence="medium"))

# Lara's dam - dorper ewe (off-farm, received from Charles Elingham)
db["sheep"].append(sheep("lara-dam", "Lara's Dam", "ewe", "unknown",
    breed_composition={"primary": "Dorper", "percentages": {"Dorper": 100}, "coat_type": "hair", "hair_percentage": 100},
    offspring_ids=["lara"],
    notes="Lara's dam per Lara breeding page. 'Dorper ewe.' Off-farm, from Charles Elingham.",
    confidence="medium"))

# Oliver - ram/ewe lamb, born 12-30-23 (Sir Loin x Lara)
# Breed: avg(25K/75SA, 100BHD) = 50%BHD/12.5%K/37.5%SA
db["sheep"].append(sheep("oliver", "Oliver", "unknown", "unknown",
    sire_id="sir-loin", dam_id="lara",
    dob="2023-12-30",
    breed_composition={"primary": "Black Headed Dorper/St Augustine/Katahdin", "percentages": {"Black Headed Dorper": 50, "St Augustine": 37.5, "Katahdin": 12.5}, "coat_type": "hair", "hair_percentage": 62},
    birth_weight=3.75,
    notes="Born 12-30-23. Sir Loin (25K/75SA) x Lara (100%BHD). Twin with Spicy. Birth weight 3.75lbs. 50%BHD/37.5%SA/12.5%K. From Lara breeding page 2023 section.",
    confidence="high"))

# Spicy - ram/ewe lamb, born 12-30-23 (Sir Loin x Lara)
# Breed: avg(25K/75SA, 100BHD) = 50%BHD/12.5%K/37.5%SA
db["sheep"].append(sheep("spicy", "Spicy", "unknown", "unknown",
    sire_id="sir-loin", dam_id="lara",
    dob="2023-12-30",
    breed_composition={"primary": "Black Headed Dorper/St Augustine/Katahdin", "percentages": {"Black Headed Dorper": 50, "St Augustine": 37.5, "Katahdin": 12.5}, "coat_type": "hair", "hair_percentage": 62},
    birth_weight=5.8,
    notes="Born 12-30-23. Sir Loin (25K/75SA) x Lara (100%BHD). Twin with Oliver. Birth weight 5.8lbs. 50%BHD/37.5%SA/12.5%K. From Lara breeding page 2023 section.",
    confidence="high"))

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

# Daisy - ewe (Sir Loin x Half Tail) — Little Daisy's dam
# Breed: avg(25K/75SA, 31.25K/56.25SA/12.5BBB) = 28.125K/65.625SA/6.25BBB
# Mother of Little Daisy (by Dodge), and likely mother of Daisy's Daughter 1 and 2.
db["sheep"].append(sheep("daisy", "Daisy", "ewe", "unknown",
    sire_id="sir-loin", dam_id="half-tail",
    breed_composition={"primary": "St Augustine/Katahdin/BBB", "percentages": {"St Augustine": 65.625, "Katahdin": 28.125, "Barbados Blackbelly": 6.25}, "coat_type": "mixed", "hair_percentage": 34},
    offspring_ids=["little-daisy", "daisys-daughter-1", "daisys-daughter-2"],
    notes="Little Daisy's dam. Sir Loin (25K/75SA) x Half Tail (12.5BBB/31.25K/56.25SA). Mother of Little Daisy (by Dodge), and likely Daisy's Daughter 1 and 2. Status unknown — from Little Daisy breeding page pedigree.",
    confidence="high"))

# Daisy's Daughter (1 and 2 - from Google Sheet)
db["sheep"].append(sheep("daisys-daughter-1", "Daisy's Daughter 1", "ewe", "unknown",
    dam_id="daisy",
    breed_composition={"primary": "St Augustine/Katahdin/BBB", "percentages": {"St Augustine": 67.9625, "Katahdin": 27.325, "Barbados Blackbelly": 4.7}, "coat_type": "mixed", "hair_percentage": 30},
    notes="From Google Sheet Pen 6 breed calculations. Different from Daisy's Daughter 2. Mother is Daisy (Sir Loin x Half Tail).",
    confidence="low"))

db["sheep"].append(sheep("daisys-daughter-2", "Daisy's Daughter 2", "ewe", "alive",
    dam_id="daisy",
    breed_composition={"primary": "St Augustine/Katahdin/BBB/Wiltshire", "percentages": {"St Augustine": 67.9625, "Katahdin": 27.325, "Barbados Blackbelly": 4.7, "Wiltshire Horn": 0}, "coat_type": "mixed", "hair_percentage": 30},
    pen="Pen 5",
    notes="From Google Sheet Pen 5 and 6. In NoriSon's group. Different from Daisy's Daughter 1. Mother is Daisy (Sir Loin x Half Tail).",
    confidence="low",
    notebook_image=[]))

# Gertude - from Google Sheet Pen 5
# REMOVED: "gertrude" entry from Google Sheet had wrong breed data (25ABB/37.5SA/12.5K/25WH = Eclipse's breed, not Gertrude Moon's).
# Gertrude Moon = ABG (tag 22, 100% ABB) — see "abg" entry above. The Google Sheet "Gertrude" in Pen 5 was a misattribution.

# OAV 2222 - 100% Katahdin, Kelsier's sister — from OAV Sam Mushko
# Breeding page: Pen 6 (but notebook has her in Pen 5 — notebook is authoritative for current pen).
# 2024 offspring: 2 lambs by "Spotted Katahdin x Dorper from OAV", born 3-13-24, 7lbs each.
# Medical: Thiamine deficiency 3-13-24, dosed with B-complex. FAMACHA "Good".
# Docile Yes, Flighty No.
db["sheep"].append(sheep("oav-2222", "OAV 2222", "ewe", "alive",
    tag="2222", aliases=["2222"],
    pen="Pen 5",
    breed_composition={"primary": "Katahdin", "percentages": {"Katahdin": 100}, "coat_type": "hair", "hair_percentage": 100},
    weight_lbs=140,
    is_breeding_animal=True,
    famacha_scores=[{"score": "Good", "date": "2024-03-13"}],
    treatments=[{"date": "2024-03-13", "treatment": "B-complex (thiamine deficiency)"}],
    offspring_ids=["oav-2222-lamb-1", "oav-2222-lamb-2"],
    notes="Kelsier's sister. 100% Katahdin confirmed by Rocky and OAV 2222 breeding pages. Tag OAV 2222. Ewe weight 140lbs, ram weight prediction 250lbs. Docile, not flighty. Breeding page says Pen 6 (notebook says Pen 5 — notebook is authoritative). 2024 offspring: 2 lambs by 'Spotted Katahdin x Dorper from OAV' (end of Oct mating, born 3-13-24, 7lbs each). Thiamine deficiency 3-13-24, treated with B-complex. Lambed 2026-02-10 (twins). Part of OAV/UF Ram Test Katahdin family with Kelsier (OAV 2223) and tag 2241 (deceased). Received from OAV Sam Mushko.",
    confidence="high",
    notebook_image=["IMG_8639.PNG"]))

# NOTE: OAV 2223 = Kelsier (same animal). See Kelsier entry above.

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

# Fl51870-0502 - ewe, 50% Hampshire / 50% Suffolk, Florida scrapie tag
# Breeding page: 285.61lbs. Bred to Sam (8-21-23) and Sir Loin (8-30-23, due Feb).
# FAMACHA 4 (9-6-23, Ivermectin) then 2 (9-18-23, no treatment). Docile, not flighty.
# Name in breeding page includes "(Pen 1-2)" and "(Pen 3)" notations.
db["sheep"].append(sheep("fl51870-0502", "Fl51870-0502", "ewe", "alive",
    tag="Fl51870-0502",
    breed_composition={"primary": "Hampshire/Suffolk", "percentages": {"Hampshire": 50, "Suffolk": 50}, "coat_type": "wool", "hair_percentage": 0},
    weight_lbs=286,
    famacha_scores=[{"score": 4, "date": "2023-09-06", "notes": "Ivermectin"}, {"score": 2, "date": "2023-09-18", "notes": "no treatment"}],
    is_breeding_animal=True,
    notes="Florida scrapie tag Fl51870-0502. 50%Hampshire/50%Suffolk. Ewe weight 285.61lbs, ram weight prediction 385lbs. Bred to Sam (8-21-23) and Sir Loin (8-30-23, due February). Docile, not flighty. FAMACHA 4→2 Sept 2023. Breeding page name shows '(Pen 1-2)' and '(Pen 3)' notations. [UNCLEAR] which flock name this corresponds to, if any.",
    confidence="medium"))

# ============================================================
# 2023 EXTENSION SERVICE LAMB RECORDS — Manatee Creek, Ken Baker
# Farm: Manatee Creek. Owner: Ken Baker. Lamb Year: 2023. Weaning date: 5/23/2023 (most).
# 15 lambs tracked. Age group averages: 60-day N=3 avg=73, 90-day N=2 avg=81, 120-day N=10 avg=87.
# Overall averages: WDA 0.79, ADG 0.63, Age Corr WW 74, Adj WW 84, ratio 106.
# ============================================================

# FM's 2023 lamb (ID 9) — Sir Loin × FM, born 4/1/2023 = FM1 (tag 009)
# This is the same sheep as FM1 (tag 009, currently in Pen 6).
# Extension service recorded as ram (sex_code 1), but FM1 is in ewe pen — likely ewe.
# Breed: avg(25K/75SA, 50Cotswold/50Tunis) = 25%Cotswold/12.5%K/37.5%SA/25%Tunis
# NOTE: Kept as separate entry for extension service data; FM1 entry has pen/measurement data.
db["sheep"].append(sheep("fm-lamb-2023", "FM's Lamb (2023)", "ewe", "alive",
    aliases=["FM1"],
    sire_id="sir-loin", dam_id="fm",
    dob="2023-04-01",
    breed_composition={"primary": "St Augustine/Cotswold/Tunis/Katahdin", "percentages": {"St Augustine": 37.5, "Cotswold": 25, "Tunis": 25, "Katahdin": 12.5}, "coat_type": "mixed", "hair_percentage": 12},
    birth_weight=12,
    extension_service={"lamb_id": 9, "birth_date": "2023-04-01", "birth_weight": 12, "birth_rearing_type": 1, "sex_code": 1, "weaning_date": "2023-05-23", "weaning_weight": 67, "weaning_age_days": 52, "age_group": 60, "wda": 1.29, "adg": 1.06, "age_corrected_ww": 75, "adjusted_ww": 80, "adj_ww_ratio": 110},
    notes="FM × Sir Loin lamb = FM1 (tag 009). Born 4/1/2023. Birth weight 12lbs (single — heaviest birth weight in class!). Weaned 5/23/2023 at 67lbs (52 days). ADG 1.06. Adj WW 80 (ratio 110). 25%Cotswold/12.5%K/37.5%SA/25%Tunis. Now in Pen 6 as FM1.",
    confidence="high"))

# Trouble's 2023 ram lamb (ID 17) — S'More × Trouble, born 2/22/2023
# Breed: avg(100Cr, 37.5K/37.5SA/25D) = 50%Cr/18.75%K/18.75%SA/12.5%Dorper
db["sheep"].append(sheep("trouble-lamb-2023", "Trouble's Lamb (2023)", "ram", "unknown",
    sire_id="smore", dam_id="trouble",
    dob="2023-02-22",
    breed_composition={"primary": "Cracker/Katahdin/St Augustine/Dorper", "percentages": {"Cracker": 50, "Katahdin": 18.75, "St Augustine": 18.75, "Dorper": 12.5}, "coat_type": "mixed", "hair_percentage": 50},
    birth_weight=8,
    extension_service={"lamb_id": 17, "birth_date": "2023-02-22", "birth_weight": 8, "birth_rearing_type": 1, "sex_code": 1, "weaning_date": "2023-05-23", "weaning_weight": 84, "weaning_age_days": 90, "age_group": 90, "wda": 0.93, "adg": 0.84, "age_corrected_ww": 84, "adjusted_ww": 84, "adj_ww_ratio": 104},
    notes="Trouble × S'More ram lamb. Born 2/22/2023. Birth weight 8lbs (single). Weaned 5/23/2023 at 84lbs (90 days). ADG 0.84 — excellent growth. Adj WW 84 (ratio 104). 50%Cr/18.75%K/18.75%SA/12.5%D.",
    confidence="high"))

# Bsoed's 2023 ram lamb (ID 1) — S'More × Bsoed, born 2/22/2023
# Breed: avg(100Cr, 40.5K/59.5SA) = 50%Cr/20.25%K/29.75%SA
db["sheep"].append(sheep("bsoed-lamb-2023", "Bsoed's Lamb (2023)", "ram", "unknown",
    sire_id="smore", dam_id="bsoed",
    dob="2023-02-22",
    breed_composition={"primary": "Cracker/St Augustine/Katahdin", "percentages": {"Cracker": 50, "St Augustine": 29.75, "Katahdin": 20.25}, "coat_type": "mixed", "hair_percentage": 50},
    birth_weight=8,
    extension_service={"lamb_id": 1, "birth_date": "2023-02-22", "birth_weight": 8, "birth_rearing_type": 4, "sex_code": 1, "weaning_date": "2023-05-23", "weaning_weight": 64, "weaning_age_days": 90, "age_group": 90, "wda": 0.71, "adg": 0.62, "age_corrected_ww": 64, "adjusted_ww": 77, "adj_ww_ratio": 96},
    notes="Bsoed × S'More ram lamb. Born 2/22/2023. Birth weight 8lbs (type 4). Weaned 5/23/2023 at 64lbs (90 days). ADG 0.62. Adj WW 77 (ratio 96). 50%Cr/29.75%SA/20.25%K.",
    confidence="high"))

# BT's 2023 ram lamb (ID 5) — S'More × Broken Tail, born 12/12/2022
# Breed: avg(100Cr, 6.25BBB/28.125K/65.625SA) = 50%Cr/3.125%BBB/14.0625%K/32.8125%SA
db["sheep"].append(sheep("bt-lamb-2023", "BT's Lamb (2023)", "ram", "unknown",
    sire_id="smore", dam_id="broken-tail",
    dob="2022-12-12",
    breed_composition={"primary": "Cracker/St Augustine/Katahdin/BBB", "percentages": {"Cracker": 50, "St Augustine": 32.8125, "Katahdin": 14.0625, "Barbados Blackbelly": 3.125}, "coat_type": "mixed", "hair_percentage": 50},
    birth_weight=9,
    extension_service={"lamb_id": 5, "birth_date": "2022-12-12", "birth_weight": 9, "birth_rearing_type": 4, "sex_code": 1, "weaning_date": "2023-05-23", "weaning_weight": 118, "weaning_age_days": 162, "age_group": 120, "wda": 0.73, "adg": 0.67, "age_corrected_ww": 90, "adjusted_ww": 108, "adj_ww_ratio": 134},
    notes="Broken Tail × S'More ram lamb (BT1 or BT2). Born 12/12/2022 (counted in 2023 class). Birth weight 9lbs (type 4). Weaned 5/23/2023 at 118lbs (162 days) — heaviest weaning weight in class! ADG 0.67. Adj WW 108 (ratio 134). 50%Cr/32.8%SA/14%K/3.1%BBB.",
    confidence="high"))

# HT's 2023 ram lamb (ID 7) — S'More × Half Tail, born 2/4/2023
# Could be HT1 or possibly Merrie (DOB discrepancy: spreadsheet says Merrie born 1/14/2023).
# Extension service says single birth (type 1), so HT only had one lamb weighed.
# Breed: avg(100Cr, 12.5BBB/31.25K/56.25SA) = 50%Cr/6.25%BBB/15.625%K/28.125%SA
db["sheep"].append(sheep("ht-ext-lamb-2023", "HT's Extension Lamb (2023)", "ram", "unknown",
    sire_id="smore", dam_id="half-tail",
    dob="2023-02-04",
    breed_composition={"primary": "Cracker/St Augustine/Katahdin/BBB", "percentages": {"Cracker": 50, "St Augustine": 28.125, "Katahdin": 15.625, "Barbados Blackbelly": 6.25}, "coat_type": "mixed", "hair_percentage": 50},
    birth_weight=7,
    extension_service={"lamb_id": 7, "birth_date": "2023-02-04", "birth_weight": 7, "birth_rearing_type": 1, "sex_code": 1, "weaning_date": "2023-05-23", "weaning_weight": 69, "weaning_age_days": 108, "age_group": 120, "wda": 0.64, "adg": 0.57, "age_corrected_ww": 76, "adjusted_ww": 76, "adj_ww_ratio": 94},
    notes="Half Tail × S'More ram lamb. Born 2/4/2023 (single birth). May be HT1 or Merrie (Merrie DOB from spreadsheet is 1/14/2023 vs 2/4/2023 here — 3 week discrepancy). Weaned 5/23/2023 at 69lbs (108 days). ADG 0.57. Adj WW 76 (ratio 94). 50%Cr/28.125%SA/15.625%K/6.25%BBB.",
    confidence="medium"))

# Shaggy's 2023 ram lamb 1 (ID 2) — S'More × Shaggy, born 1/29/2023
# Breed: avg(100Cr, 50Babydoll/50Jacob) = 50%Cr/25%Babydoll/25%Jacob
db["sheep"].append(sheep("shaggy-1", "Shaggy1", "ram", "unknown",
    sire_id="smore", dam_id="shaggy",
    dob="2023-01-29",
    breed_composition={"primary": "Cracker/Babydoll/Jacob", "percentages": {"Cracker": 50, "Babydoll": 25, "Jacob": 25}, "coat_type": "mixed", "hair_percentage": 50},
    birth_weight=6,
    extension_service={"lamb_id": 2, "birth_date": "2023-01-29", "birth_weight": 6, "birth_rearing_type": 4, "sex_code": 1, "weaning_date": "2023-05-23", "weaning_weight": 68, "weaning_age_days": 114, "age_group": 120, "wda": 0.60, "adg": 0.54, "age_corrected_ww": 71, "adjusted_ww": 86, "adj_ww_ratio": 106},
    notes="Shaggy × S'More ram lamb (Shaggy1). Born 1/29/2023 (type 4). Birth weight 6lbs. Weaned 5/23/2023 at 68lbs (114 days). ADG 0.54. Adj WW 86 (ratio 106). 50%Cr/25%Babydoll/25%Jacob.",
    confidence="high"))

# Shaggy's 2023 ram lamb 2 (ID 3) — S'More × Shaggy, born 1/29/2023
db["sheep"].append(sheep("shaggy-2", "Shaggy2", "ram", "unknown",
    sire_id="smore", dam_id="shaggy",
    dob="2023-01-29",
    breed_composition={"primary": "Cracker/Babydoll/Jacob", "percentages": {"Cracker": 50, "Babydoll": 25, "Jacob": 25}, "coat_type": "mixed", "hair_percentage": 50},
    birth_weight=6,
    extension_service={"lamb_id": 3, "birth_date": "2023-01-29", "birth_weight": 6, "birth_rearing_type": 4, "sex_code": 1, "weaning_date": "2023-05-23", "weaning_weight": 59, "weaning_age_days": 114, "age_group": 120, "wda": 0.52, "adg": 0.46, "age_corrected_ww": 62, "adjusted_ww": 74, "adj_ww_ratio": 92},
    notes="Shaggy × S'More ram lamb (Shaggy2). Born 1/29/2023 (type 4). Birth weight 6lbs. Weaned 5/23/2023 at 59lbs (114 days). ADG 0.46. Adj WW 74 (ratio 92). 50%Cr/25%Babydoll/25%Jacob.",
    confidence="high"))

# BK's 2023 ewe lamb 1 (ID 16) — S'More × Brown Knee, born 1/24/2023
# AKA Foxtail 1. Breed: avg(100Cr, 43.75K/56.25SA) = 50%Cr/21.875%K/28.125%SA
db["sheep"].append(sheep("bk1", "Foxtail 1", "ewe", "unknown",
    sire_id="smore", dam_id="brown-knee",
    dob="2023-01-24",
    breed_composition={"primary": "Cracker/St Augustine/Katahdin", "percentages": {"Cracker": 50, "St Augustine": 28.125, "Katahdin": 21.875}, "coat_type": "mixed", "hair_percentage": 50},
    birth_weight=8,
    extension_service={"lamb_id": 16, "birth_date": "2023-01-24", "birth_weight": 8, "birth_rearing_type": 4, "sex_code": 2, "weaning_date": "2023-05-23", "weaning_weight": 99, "weaning_age_days": 119, "age_group": 120, "wda": 0.83, "adg": 0.76, "age_corrected_ww": 100, "adjusted_ww": 109, "adj_ww_ratio": 135},
    notes="Foxtail 1 (formerly BK1). Brown Knee × S'More ewe lamb. Born 1/24/2023 (type 4). Birth weight 8lbs. Weaned 5/23/2023 at 99lbs (119 days) — BEST ewe lamb! ADG 0.76. Adj WW 109 (ratio 135). 50%Cr/28.125%SA/21.875%K.",
    confidence="high"))

# BK's 2023 ewe lamb 2 (ID 15) — S'More × Brown Knee, born 1/24/2023
# AKA Foxtail 2.
db["sheep"].append(sheep("bk2", "Foxtail 2", "ewe", "unknown",
    sire_id="smore", dam_id="brown-knee",
    dob="2023-01-24",
    breed_composition={"primary": "Cracker/St Augustine/Katahdin", "percentages": {"Cracker": 50, "St Augustine": 28.125, "Katahdin": 21.875}, "coat_type": "mixed", "hair_percentage": 50},
    birth_weight=8,
    extension_service={"lamb_id": 15, "birth_date": "2023-01-24", "birth_weight": 8, "birth_rearing_type": 4, "sex_code": 2, "weaning_date": "2023-05-23", "weaning_weight": 80, "weaning_age_days": 119, "age_group": 120, "wda": 0.67, "adg": 0.61, "age_corrected_ww": 81, "adjusted_ww": 88, "adj_ww_ratio": 109},
    notes="Foxtail 2 (formerly BK2). Brown Knee × S'More ewe lamb. Born 1/24/2023 (type 4). Birth weight 8lbs. Weaned 5/23/2023 at 80lbs (119 days). ADG 0.61. Adj WW 88 (ratio 109). 50%Cr/28.125%SA/21.875%K.",
    confidence="high"))

# Unknown 7yo ewe's ram lamb (ID 35) — likely Anna (age ~7 in 2023), born 2/1/2023
# No sire listed in extension service. Type 4, birth weight 7lbs.
db["sheep"].append(sheep("ext-lamb-35", "Ext Lamb 35", "ram", "unknown",
    dob="2023-02-01",
    birth_weight=7,
    extension_service={"lamb_id": 35, "birth_date": "2023-02-01", "birth_weight": 7, "birth_rearing_type": 4, "sex_code": 1, "ewe_age": 7, "weaning_date": "2023-05-23", "weaning_weight": 81, "weaning_age_days": 111, "age_group": 120, "wda": 0.73, "adg": 0.67, "age_corrected_ww": 87, "adjusted_ww": 109, "adj_ww_ratio": 135},
    notes="Extension service lamb ID 35. Ram, born 2/1/2023 (type 4). Ewe age 7 — likely Anna (DOB ~2016). No sire listed. Birth weight 7lbs. Weaned 5/23/2023 at 81lbs (111 days). ADG 0.67. Adj WW 109 (ratio 135 — tied for best). May be anna1 (S'More offspring).",
    confidence="medium"))

# Unknown 3yo ewe's ram lamb (ID 27) — born 2/1/2023
db["sheep"].append(sheep("ext-lamb-27", "Ext Lamb 27", "ram", "unknown",
    dob="2023-02-01",
    birth_weight=7,
    extension_service={"lamb_id": 27, "birth_date": "2023-02-01", "birth_weight": 7, "birth_rearing_type": 4, "sex_code": 1, "ewe_age": 3, "weaning_date": "2023-05-23", "weaning_weight": 66, "weaning_age_days": 111, "age_group": 120, "wda": 0.59, "adg": 0.53, "age_corrected_ww": 71, "adjusted_ww": 85, "adj_ww_ratio": 106},
    notes="Extension service lamb ID 27. Ram, born 2/1/2023 (type 4). Ewe age 3 — unknown dam. No sire listed. Birth weight 7lbs. Weaned 5/23/2023 at 66lbs (111 days). ADG 0.53. Adj WW 85 (ratio 106).",
    confidence="low"))

# Unknown 3yo ewe's ewe lamb (ID 10) — born 3/23/2023
db["sheep"].append(sheep("ext-lamb-10", "Ext Lamb 10", "ewe", "unknown",
    dob="2023-03-23",
    birth_weight=5,
    extension_service={"lamb_id": 10, "birth_date": "2023-03-23", "birth_weight": 5, "birth_rearing_type": 4, "sex_code": 2, "ewe_age": 3, "weaning_date": "2023-05-23", "weaning_weight": 36, "weaning_age_days": 61, "age_group": 60, "wda": 0.59, "adg": 0.51, "age_corrected_ww": 35, "adjusted_ww": 39, "adj_ww_ratio": 53},
    notes="Extension service lamb ID 10. Ewe, born 3/23/2023 (type 4). Ewe age 3 — unknown dam. No sire listed. Birth weight 5lbs. Weaned 5/23/2023 at 36lbs (61 days). ADG 0.51. Adj WW 39 (ratio 53 — lowest). Smallest/youngest lamb in class.",
    confidence="low"))

# Extension Service: ABG (ID 8) — may be Gertrude Moon × Sir Loin, born 1/24/2023
# Ewe listed as age 1 but Gertrude Moon was ~3 in 2023. Acquired 5-4-23 per breeding page.
# Type 3 (triplet?) — anomalous. Possible earlier acquisition date or different ewe.
db["sheep"].append(sheep("ext-lamb-8", "Ext Lamb 8 (ABG)", "ram", "deceased",
    dob="2023-01-24",
    birth_weight=8,
    extension_service={"lamb_id": 8, "birth_date": "2023-01-24", "birth_weight": 8, "birth_rearing_type": 3, "sex_code": 1, "ewe_id": "ABG", "ewe_age": 1, "sire_id": "SL", "weaning_date": "2023-05-23", "weaning_weight": 60, "weaning_age_days": 119, "age_group": 120, "wda": 0.50, "adg": 0.44, "age_corrected_ww": 60, "adjusted_ww": 77, "adj_ww_ratio": 95},
    status_notes="Not kept — Gertrude Moon was an awful mother, no offspring kept per owner.",
    notes="Extension service lamb ID 8. Ram, born 1/24/2023 (type 3). Ewe: ABG age 1, Sire: SL (Sir Loin). Not kept. Birth weight 8lbs. Weaned 5/23/2023 at 60lbs (119 days). ADG 0.44. Adj WW 77 (ratio 95).",
    confidence="low"))

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

# 430-2079 - ewe, 25%Hampshire/75%Suffolk, DECEASED
# Breeding page: Pen 5, DOB 2017, acquired 8-21-23, weight 335.15lbs.
# Bred to Rocky (8-21-23) and Samson (8-30-23). Docile, not flighty. Breed All Year Y.
# Medical: foot rot from previous owner (kept near swamp), treated with Terramycin.
db["sheep"].append(sheep("tag-430-2079", "430-2079", "ewe", "deceased",
    tag="430-2079",
    breed_composition={"primary": "Suffolk/Hampshire", "percentages": {"Suffolk": 75, "Hampshire": 25}, "coat_type": "wool", "hair_percentage": 0},
    weight_lbs=335,
    dob="2017-01-01", dob_approximate=True,
    pen="Pen 5",
    is_breeding_animal=True,
    status_date="2023-08-21",
    treatments=[{"date": "2023", "treatment": "Terramycin (foot rot)"}],
    notes="Tag 430-2079 (pen 5). 25%Hampshire/75%Suffolk. Ewe weight 335.15lbs, ram weight prediction 400lbs. DOB 2017. Acquired 8-21-23 from guy who kept her near a swamp — had foot rot, treated with Terramycin. Bred to Rocky (8-21-23) and Samson (8-30-23). Docile, not flighty. Breed All Year Y, Wet Tolerant No. Multiple: Y (has had multiples). Deceased per owner.",
    confidence="high"))

# Kelsier's Sister - tag 2241, 100% Katahdin, deceased
# Breeding page: 100%K, weight 150lbs, FAMACHA 3 (10-5-23).
# Bred to Sir Loin 10-5-23 (due Feb 27th). Then deceased.
# Attributes noted: Good Mother?, Attentive, Protective, Milky, Docile, Strong Flocking,
# Parasite Resistance, Heat/Cold/Wet Tolerant.
db["sheep"].append(sheep("kelsiers-sister", "Kelsier's Sister", "ewe", "deceased",
    tag="2241",
    breed_composition={"primary": "Katahdin", "percentages": {"Katahdin": 100}, "coat_type": "hair", "hair_percentage": 100},
    weight_lbs=150,
    famacha_scores=[{"score": 3, "date": "2023-10-05"}],
    is_breeding_animal=True,
    notes="Kelsier's sister. Tag 2241. 100% Katahdin. Weight 150lbs. Breeding page attributes: Flighty?, Good Mother?, Attentive, Protective, Milky, Docile, Strong Flocking, Parasite Resistant, Heat/Cold/Wet Tolerant. Bred to Sir Loin 10-5-23 (due Feb 27th). FAMACHA 3 on 10-5-23. Deceased.",
    confidence="high"))

db["sheep"].append(sheep("dorper-ram-deceased", "Dorper Ram (Deceased)", "ram", "deceased",
    breed_composition={"primary": "Dorper", "percentages": {"Dorper": 100}, "coat_type": "hair", "hair_percentage": 100},
    treatments=[{"date": "2024-10-24", "treatment": "iron and vitamin B"}],
    notes="Dorper ram from sick sheep note. Given iron and B on 10-24. Deceased.",
    confidence="medium",
    notebook_image=["IMG_8626.PNG"]))

# ============================================================
# SOLD 2026-02-15
# ============================================================

db["sheep"].append(sheep("tag-240002", "Tag 240002", "unknown", "sold",
    tag="240002",
    status_date="2026-02-15",
    notes="Sold 2026-02-15.",
    confidence="high"))

db["sheep"].append(sheep("tag-0049", "Tag 0049", "unknown", "sold",
    tag="0049",
    status_date="2026-02-15",
    notes="Sold 2026-02-15.",
    confidence="high"))

db["sheep"].append(sheep("tag-240001", "Tag 240001", "unknown", "sold",
    tag="240001",
    status_date="2026-02-15",
    notes="Sold 2026-02-15.",
    confidence="high"))

db["sheep"].append(sheep("mc06", "Mc06", "unknown", "sold",
    mc_tag="Mc06",
    status_date="2026-02-15",
    notes="Sold 2026-02-15. MC tag Mc06.",
    confidence="high"))

db["sheep"].append(sheep("tag-0050", "Tag 0050", "unknown", "sold",
    tag="0050",
    status_date="2026-02-15",
    notes="Sold 2026-02-15. Possibly one of the goose pen auction lambs (tag 50).",
    confidence="high"))

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
        "ewes": ["fm"],
        "notes": "Kaladin's group. Merrie (tag 016) is also a ram in this pen. ABG (Anna's Big One) in Pen 4, not Pen 1. Gertrude Moon/BF deceased — removed. Eclipse (ram) deceased (Hurricane Idalia). May 14 2025: vaccinated pen 1 lambs."
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
        "ewes": ["elsie", "s1", "fm1", "circle-tail"],
        "notes": "No ram. Elsie here with triplets. Fox Tail (tag 17) was here but deceased (Hurricane Helene). Shaggy was here but deceased (killed after Helene). Serendipity moved to Pen 4 with twins."
    },
    "goose_pen": {
        "ram": None,
        "ewes": [],
        "notes": "Auction lambs: tags 09, 50, 06, L19, and others."
    },
    "chicken_coop": {
        "ram": "buck",
        "ewes": [],
        "notes": "Buck (Katahdin/Awassi/EF ram) housed in chicken coop. Current Buck is brother of original Buck who died in Hurricane Helene. Both from Windlestone."
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
