/**
 * Manatee Creek Flock  -  Google Sheets Updater
 * Generated: 2026-05-13 15:07
 *
 * HOW TO USE:
 * 1. Open your Google Sheet
 * 2. Extensions -> Apps Script
 * 3. Paste this entire file (replace any existing code)
 * 4. Click Run -> updateAllSheets
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

function updatePipelineOverview(ss) {
  var sheet = getOrCreateSheet(ss, 'Pipeline Overview');
  var data = [
    ['Stage','Pen','Size','Location','Ram','Ram Weight','Hair %','Coat','Ewes','FAMACHA Req','FEC Req','Shed Req','Shelter','Notes'],
    ['1','Pen 3','largest (~4x Tree Fort)','SE corner, east side','00110','?','?','?','7','<3','<500','>25%','standard','287 lbs, 12.5% hair, extra wooly but big and meaty. Starts converting wool ewes.'],
    ['2','Tree Fort','smallest','east side, between Goose Pen and Pen 4','Gigis 2025 Ram','?','?','?','5','<3','<400','>35%','best on property','Kelsier x GG, ~50% hair, wooly. 50% Katahdin from NSIP sire. Tests Kelsier genet'],
    ['3','Pen 4','large','east side','Buck','270.8','50','mixed','9','<3','<350','>50%','standard','Buck (271 lbs, 50% Kat/48% Awassi/2% EF). Promoted from Pen 5. Better parasites '],
    ['4','Pen 5','medium-large','east side','Serendipity White Ram Twin','?','?','?','8','<2','<300','>65%','standard','Serendipity White Ram Twin (Kelsier x Serendipity). Stage 4. PROVISIONAL.'],
    ['5','Pen 6','medium','NE corner, east side','Merrieweather','200','50.0','hair','3','<2','<250','>80%','standard','Merrie (200 lbs, observed shedder). Florida heritage. Stage 5 refinement.'],
    ['6','Pen 1','medium-small','SW corner, west side (isolated)','Charlie','232.2','100.0','hair','8','<2','<200','>90%','solid','Charlie (232 lbs, 100% hair Kat/BHD/ABB/WH). Moved from Pen 2 to Pen 1 when Wind'],
    ['7','Pen 2','small','SW corner, west side (isolated, most secure)','Windlestone Kat/Dorper Ram','','100.0','hair','0','1-2 only','<150','>95%','solid, most secure','Windlestone Kat/Dorper (50% top Kat x 50% elite Dorper). 100% hair, FAMACHA 1 fo'],
    ['outside','Goose Pen','small-medium','east side, between Pen 3 and Tree Fort','MC08','190','0','wool','0','','','','standard','190 lbs, unknown breed, very wooly. Awassi dairy line only. Outside main pipelin'],
  ];
  sheet.getRange(1, 1, data.length, data[0].length).setValues(data);
  formatHeader(sheet, data[0].length);
  autoResize(sheet, data[0].length);
}

function updateActiveFlock(ss) {
  var sheet = getOrCreateSheet(ss, 'Active Flock');
  var data = [
    ['Pen','Stage','Name','ID','Tag','Sex','Weight','Breed','Hair %','Wool %','Coat Obs','Coat Pred','Sire','Dam','Weak Parasites','Notes'],
    ['Pen 3','1','Charlie','charlie-ram','MC20','ram','232.2','Katahdin/BHD/ABB/Wiltshire Horn','100.0','0','','hair','','','','No tag (now tagged, number TBD). Charlies Ram. Horned. CATCH'],
    ['Pen 3','1','Noris Baby Ram (Pen 3)','nori-baby-p3','MC2604','ram','','[UNCLEAR - Nori offspring]','','','','','','nori','','No tag (now tagged TBD). Born 1-10-26. 0029/Noris Baby. 5.3 '],
    ['Pen 3','1','Broken Tail','broken-tail','MC-15','ewe','225','St Augustine/Katahdin/BBB','100.0','0','','hair','sir-loin','half-tail','','Flock spreadsheet: 6.25% BBB / 28.125% Katahdin / 65.625% St'],
    ['Pen 3','1','Broken Tail Twin Ewe','broken-tail-twin-ewe','MC-2605','ewe','','[UNCLEAR - Broken Tail offspring]','','','','','','broken-tail','','No tag (now tagged TBD). Born 12-31-25. Broken Tails twin ew'],
    ['Pen 3','1','Charlies Farm Ewe (Pen 3)','charlies-farm-ewe-p3','MC16','ewe','155','Katahdin/BHD/ABB/Wiltshire Horn','100.0','0','','hair','','','','No tag (now tagged TBD). Ewe from Charlies Farm. Multi color'],
    ['Pen 3','1','Charlies Farm Ewe Baby','charlies-farm-ewe-baby-p3','MC-2602','ewe','','[UNCLEAR - Charlies Farm Ewe offspring]','','','','','charlie-ram','charlies-farm-ewe-p3','','No tag (now tagged TBD). Born 12-6-25. Baby ewe from Charlie'],
    ['Pen 3','1','Cocoas Daughter (by Loki)','cocoas-daughter-by-loki','','ewe','','','','','','','loki','cocoa','',''],
    ['Pen 3','1','Gigis 2026 Baby','gigi-2026-baby','MC-2613','ewe','','[Kelsier x Gigi offspring]','','','','','kelsier','gg','','Born 1-10-26. Gigis baby. Multi color ewe. Sire: Kelsier. 5.'],
    ['Pen 3','1','Nori','nori','0029','ewe','139','ABB/Wiltshire Horn','100','0','','hair','','','','Nori breeding page: 50%ABB/50%WH, tag 21 (tag lost). Ewe wei'],
    ['Tree Fort','2','0035 Baby Ram','tag-0035-baby-ewe','MC-2617','ram_lamb','','','','','','','','tag-0035-white-ewe','','Born 1-2-26. 0035s baby ewe. 7 weeks old 2-20-26. Source: no'],
    ['Tree Fort','2','Orange 31 Ram Lamb','tag-31-orange-tf-ram-lamb','MC2616','ram','','','','','','','','tag-31-orange-tf','','Born 1-2-26. Orange tag 31 ewes baby ram. 7 weeks old 2-20-2'],
    ['Tree Fort','2','Bambii','bambii','24/0003','ewe','','','','','','','','','','In Pen 2 (Sir Loin group) per spiral notebook (authoritative'],
    ['Tree Fort','2','Bambiis Baby','bambii-baby','MC-2615','ewe','','','','','','','','bambii','','Born 12-28-25. Bambiis baby. 7.5 weeks old 2-20-26. Sex UNCL'],
    ['Tree Fort','2','Fawn Wool Ewe 114','tag-114-fawn-wool','114','ewe','145','Cracker/Suffolk/GCN/Katahdin','12.5','87.5','','wool','','','','Tag 114, orange tag. Fawn wool ewe. Was in Pen 2 but moved t'],
    ['Tree Fort','2','Orange Tag 31 Ewe (Tree Fort)','tag-31-orange-tf','31','ewe','','','','','','','','','','Tag 31 (ORANGE tag  -  different from Pen 5s yellow Tag 31).'],
    ['Tree Fort','2','White Ewe 0035','tag-0035-white-ewe','0035','ewe','130','Black Headed Dorper/Katahdin','100','0','','hair','','','','Tag 0035. White ewe with dot on ear. Single baby (ewe, born '],
    ['Pen 4','3','FM2 Ram Lamb','fm2-ram-lamb','MC2614','ram','','[Kelsier x FM2 offspring]','','','','','kelsier','fm2-0051','','Born 1-31-26. FM2s baby ram. Sire: Kelsier. 2.6 weeks old as'],
    ['Pen 4','3','Gigis 2025 Ram','gigi-2025-ram','MC-09','ram','','[Kelsier x Gigi offspring]','','','','','kelsier','gg','','Tag 09 [UNCLEAR]. Gigis 2025 baby. Yearling ram, old enough '],
    ['Pen 4','3','Merrieweather','merrie','00016','ram','200','Cracker/St Augustine/Katahdin/BBB/White Dorper','50.0','50','hair','hair','smore','half-tail','','Flock spreadsheet: Tag 016, ram. SMore (100%Cr) x Half Tail '],
    ['Pen 4','3','Serendipity White Ram Twin','serendipity-twin-ram','MC2606','ram','','[Kelsier x Serendipity offspring]','','','','','kelsier','serendipity','','Born 12-30-25. Serendipitys white ram twin. Sire: Kelsier. F'],
    ['Pen 4','3','FM','fm','0011','ewe','212.5','Cotswold/Tunis','0','100','','wool','fm-sire','fm-dam','YES','Tag GA1568-011, 50% Cotswold / 50% Tunis, Tunis Red, 200lbs.'],
    ['Pen 4','3','FM2','fm2-0051','0051','ewe','185','Cotswold/Tunis/St Augustine/Katahdin','50.0','50','','mixed','sir-loin','fm','','Tag 0051. FM2. Fat and gray. 1 baby ram born 1-31-26. Sire: '],
    ['Pen 4','3','GG','gg','MC-19','ewe','212.5','Hampshire/Suffolk','0','100','','wool','','','YES','Azures full brother. On weak resistance list. From Google Sh'],
    ['Pen 4','3','Lara','lara','023','ewe','160','Black Headed Dorper','100','0','','hair','lara-sire','lara-dam','YES','MERGED 2026-04-24: This record (Lara, tag 023) was duplicate'],
    ['Pen 4','3','Little Daisy','little-daisy','035','ewe','145','St Augustine/Katahdin/BBB','100.0','0','','hair','dodge','daisy','','Breeding page: Dodge (Sir Loin x Broken Tail) x Daisy (Sir L'],
    ['Pen 4','3','Samson Daughter (Pen 4)','samson-daughter-p4','','ewe','','Hampshire/Cotswold/Tunis','0','100','','wool','samson','fm','','Identified by owner 2026-04-24 from Pen 4 photos (back-right'],
    ['Pen 4','3','Serendipity','serendipity','MC157','ewe','138','St Augustine/Babydoll/Jacob/Katahdin','50.0','50','','mixed','sir-loin','shaggy','','Breeding page: 25%Babydoll/25%Jacob/12.5%K/37.5%SA. Tag 30. '],
    ['Pen 4','3','Serendipity Black Ewe Twin','serendipity-twin-ewe','MC2607','ewe','','[Kelsier x Serendipity offspring]','','','','','kelsier','serendipity','','Born 12-30-25. Serendipitys black ewe twin. Sire: Kelsier. F'],
    ['Pen 4','3','Small White Ewe (Pen 4)','sm-white-ewe-p4','MC189','ewe','145','St Augustine/Katahdin/BBB','100.0','0','','hair','dodge','daisy','','No tag (now tagged TBD). Small white ewe. No babies. Eyes go'],
    ['Pen 5','4','Angus','angus','','ram','','Katahdin/Dorper/Awassi','75','25','','hair','','','',''],
    ['Pen 5','4','Elsie','elsie','025','ewe','175','Katahdin/St Augustine/BBB','100.0','0','','hair','well-done','half-tail','','Breeding page: Tag 25, 6.25%ABB(BBB)/65.625%K/28.125%SA. DOB'],
    ['Pen 5','4','Elsie Large White Ewe Triplet','elsie-triplet-lg-white-ewe','MC-2618','ewe','','','','','','','nori-son','elsie','','Born 1-6-26. Elsies triplet. Large white female. Sire: Eclip'],
    ['Pen 5','4','Ewe Tag 02','tag-02-ewe-p5','02','ewe','','[UNCLEAR]','','','','','','','','Tag 02. Ewe. Pen 5. No babies. Proven breeder  -  Eclipse fa'],
    ['Pen 5','4','Ewe Tag 31','tag-31-ewe-p5','31','ewe','170','St Augustine/Katahdin','100','0','','hair','sir-loin','','','Tag 31. Ewe. Pen 5. No babies. Proven breeder in prior years'],
    ['Pen 5','4','Fawn Wool Ewe (Pen 5)','fawn-wool-ewe-p5','240006','ewe','','Wool','','','','','','','','No tag (now tagged TBD). Wool ewe, fawn color, long ears. Pe'],
    ['Pen 5','4','OAV 2222','oav-2222','2222','ewe','140','Katahdin','100','0','','hair','','','','Kelsiers sister. 100% Katahdin confirmed by Rocky and OAV 22'],
    ['Pen 5','4','OAV 2222 Lamb 1 (White-Rust)','oav-2222-lamb-1','','ewe_lamb','','','','','','','nori-son','oav-2222','',''],
    ['Pen 5','4','OAV 2222 Lamb 2 (White-Rust + Black Dot)','oav-2222-lamb-2','','ewe_lamb','','','','','','','nori-son','oav-2222','',''],
    ['Pen 6','5','MC08','mc08-ram','MC08','ram','190','Hampshire/Cotswold/Tunis','0','100','','wool','samson','fm','','Tag MC08, yellow. Ram in Pen 6 with Windlestone Awassi ewes.'],
    ['Pen 6','5','Windlestone Fat Tail 0055','windlestone-0055','0055','ewe','200.0','Awassi/East Friesian','0','100','','wool','','','','Tag 0055. Windlestone Ranch fat tail (Awassi) ewe. Tiny/sm h'],
    ['Pen 6','5','Windlestone Fat Tail 0056','windlestone-0056','0056','ewe','200.0','Awassi/East Friesian','0','100','','wool','','','','Tag 0056. Windlestone Ranch fat tail (Awassi) ewe. Med thick'],
    ['Pen 6','5','Windlestone Fat Tail 2139','windlestone-2139','2139','ewe','200.0','Awassi/East Friesian','0','100','','wool','','','','Tag 2139. Windlestone Ranch fat tail (Awassi) ewe. Big ewe w'],
    ['Pen 1','6','Charlies Ewe Ram Lamb','charlies-ram-lamb','MC-2619','ram','','Katahdin/Awassi/BHD/ABB/Wiltshire Horn','75.0','25.0','','hair','buck','charlies-ewe','','Buck(Kat/Awassi/EF) x Charlies Ewe(Kat/BHD/ABB/WH). 75% hair'],
    ['Pen 1','6','Orange Tag Ram','orange-tag-00110','00110','ram','287.5','Cracker/Suffolk/GCN/Katahdin','12.5','87.5','wool','wool','','','','Tag 00110, orange tag. Ram. Poop trimmed at butt 2-19-2026. '],
    ['Pen 1','6','00113','tag-00113-ewe-p1','00113','ewe','','Cracker/Suffolk/GCN/Katahdin','12.5','87.5','','wool','','','','NEW RECORD 2026-04-26 (added from Pen 5 photo session). Full'],
    ['Pen 1','6','0053','nuba-0053','0053','ewe','175','Hampshire/St Augustine/Katahdin','50.0','50','','mixed','samson','','','Tag 0053. White hair ewe  -  no proper name; prior Nuba / Nu'],
    ['Pen 1','6','0053s Baby Ewe','nuba-baby-ewe','','ewe','','','','','','','rocky','nuba-0053','','Born 3-24-26 to Nuba (0053) in Pen 1. Sire: Rocky. Black w/ '],
    ['Pen 1','6','Azure','azure','20','ewe','212.5','Hampshire/Suffolk','0','100','','wool','','','YES','Mom calls her Amure. GGs full sister. On weak resistance lis'],
    ['Pen 1','6','Baby Azure','baby-azure','MC-2610','ewe','','[UNCLEAR - Azure offspring]','','','','','','azure','','No tag (now tagged, number TBD). Born 1-10-26. Azures baby, '],
    ['Pen 1','6','Charlies Ewe','charlies-ewe','MC2620','ewe','','Katahdin/BHD/ABB/Wiltshire Horn','100.0','0','','hair','','','','Nori line: Nori(ABB/WH) x Dorper -> x Katahdin -> Charlies E'],
    ['Pen 1','6','Hair Ewe 0033','tag-0033-hair-ewe','0033','ewe','170','St Augustine/Katahdin','100.0','0','','hair','sir-loin','','','Tag 0033. Hair ewe. Had twins (2 rams, born ~1-1-26). Source'],
    ['Pen 1','6','Wool Ewe 0044','tag-0044-wool-ewe','0044','ewe','170','Katahdin/Awassi/East Friesian','50','50','','mixed','','','','Tag 0044. Wool ewe. No babies. Source: notebook card, pen 1.'],
    ['Pen 2','7','Rocky','rocky','140','ram','300','Black Headed Dorper/Awassi/East Friesian','50','50','','mixed','teaser','dorper-ewe-198','YES','Also called Jerkface/Rock/Louises Ram. Tag 140. 44%Awassi/50'],
    ['Pen 2','7','Windlestone Kat/Dorper Ram','windlestone-kat-dorper','','ram','','Katahdin/Dorper','100.0','0','hair','hair','','','','Windlestone Kat/Dorper: 50% top-tier Katahdin x 50% elite Do'],
    ['Chicken Coop','?','Buck','buck','MC-2433','ram','270.8','Katahdin/Awassi/East Friesian','50','50','','mixed','','','','Current Buck in chicken coop. Brother of original Buck who d'],
    ['','?','Dodge','dodge','','ram','277.3','St Augustine/Katahdin/BBB','100.0','0','','hair','sir-loin','broken-tail','','Sir Loin (25K/75SA) x Broken Tail (28.125K/65.625SA/6.25BBB)'],
    ['','?','Kaladin','kaladin','014','ram','52','Cracker/St Augustine/Babydoll/Jacob/Katahdin','25.0','75.0','','wool','smore','serendipity','','Living Kaladin tag 014. DOB 5/11/2023 per extension service.'],
    ['','?','Loki','loki','','ram','','','','','','','dodge','daisy-of-sugar','',''],
    ['','?','Cocoa','cocoa','','ewe','','','','','','','smore','half-tail','',''],
    ['','?','Daisy (of Sugar)','daisy-of-sugar','','ewe','','','','','','','sir-loin','sugar','',''],
    ['Goose Pen','outside','114 Black Ram Lamb','tag-114-black-ram-lamb','','ram','','[UNCLEAR - 114 offspring]','','','','','rocky','tag-114-fawn-wool','','Born 3-29-2026. Little black ram lamb with white spot on hea'],
  ];
  sheet.getRange(1, 1, data.length, data[0].length).setValues(data);
  formatHeader(sheet, data[0].length);
  autoResize(sheet, data[0].length);
  // Color-code by stage
  for (var i = 2; i <= data.length; i++) {
    var stage = sheet.getRange(i, 2).getValue();
    var color = '#ffffff';
    if (stage == 1) color = '#ffcccc';
    else if (stage == 2) color = '#ffd9b3';
    else if (stage == 3) color = '#ffffcc';
    else if (stage == 4) color = '#ccffcc';
    else if (stage == 5) color = '#ccffff';
    else if (stage == 6) color = '#cce5ff';
    else if (stage == 7) color = '#e5ccff';
    sheet.getRange(i, 1, 1, data[0].length).setBackground(color);
  }
}

function updateBreedingPolicy(ss) {
  var sheet = getOrCreateSheet(ss, 'Breeding Policy');
  var data = [
    ['Category','Item','Details'],
    ['Selection Hierarchy','#1 FAMACHA/FEC','Can it survive parasites with minimal intervention? FAMACHA 1-2 without deworming = gold. FAMACHA 4-5 requiring treatmen'],
    ['Selection Hierarchy','#2 Hair/Wool','Does it shed its coat? Observed coat, not calculated from breed. Score at weaning: 1=full wool, 5=full shed.'],
    ['Selection Hierarchy','#3 Breed Composition','Genetic background for context. Informs but does not decide. A mutt with FAMACHA 1 beats a purebred Katahdin with FAMACH'],
    ['Selection Hierarchy','#4 Meatiness','Tiebreaker. Given two animals equal in parasites, coat, and breed  -  choose the meatiest.'],
    ['','',''],
    ['Hard Lesson','','St Croix purchased and brought to property DIED OF PARASITES. Breed reputation != individual resistance.'],
    ['Hard Lesson','','Barbados Black Belly purchased and brought to property DIED OF PARASITES. Same lesson.'],
    ['Hard Lesson','','Windlestone Dorper (exceptional South African bloodlines) are EXTREMELY VULNERABLE to parasites despite being hair sheep'],
    ['Hard Lesson','','GG and Rocky are alive because owner skill improved, not because they are resistant. They require aggressive treatment t'],
    ['Hard Lesson','','Cracker coat type is VARIABLE per individual  -  Merrie sheds, 00110 does not. Cannot classify per breed.'],
    ['Hard Lesson','','Every animal currently alive has survived Florida parasite pressure. That survival IS the genetics that work.'],
    ['Hard Lesson','','Buying outside genetics is HIGH RISK. Even resistant breeds die here. Safest investment is whats already proven on this '],
    ['Hard Lesson','','Spring 2026 is an extreme drought. Animals scoring FAMACHA 4-5 during DRY season (lowest parasite pressure) will be cata'],
    ['Hard Lesson','','{date: 2026-05-13, lesson: Spring 2026 drought cull list (Phase 2 close-out), detail: "Drought-season FAMACHA audit iden'],
    ['Hard Lesson','','{date: 2026-04-22, lesson: Transplant-environment caveat, detail: "Untreated-at-source-farm survival is a positive but a'],
    ['Hard Lesson','','{date: 2026-04-22, lesson: Pen 4 reframe  -  weak pen breeds too, detail: "Earlier v5 spec called Pen 4 off the breeding'],
    ['','',''],
    ['Pipeline','Target Animal','Hardy (survives Florida with minimal care), Hairy (sheds coat), Meaty (good muscling/growth), Parasite resistant (FAMACH'],
    ['Pipeline','Inbreeding Policy','Managed tool, not hard block. F < 0.25 acceptable. Intentional line breeding toward homogeneity.'],
    ['Pipeline','Key Insight',''],
    ['','',''],
    ['Stress Test Fix','2026-04-02','Baby Azure moved from Stage 3 to Stage 1 (FAMACHA 5 in dry season = worst performer)'],
    ['Stress Test Fix','2026-04-02','Charlie + Broken Tail + Elsie moved to Pen 2 (elite)  -  they earned it, no need to wait'],
    ['Stress Test Fix','2026-04-02','Merrie promoted to Pen 1 (Stage 6)  -  2nd best shedder after Charlie'],
    ['Stress Test Fix','2026-04-02','Serendipity White Ram Twin placed at Pen 6 (Stage 5)  -  PROVISIONAL pending summer FAMACHA'],
    ['Known Vulnerability','','Charlie is single point of failure (only 100% hair ram). Backup: test Kelsier sons summer 2026.'],
    ['Known Vulnerability','','Rocky at Stage 3 contaminates with weak parasite genetics. Mitigate by hard culling his FAMACHA-3+ offspring.'],
    ['Known Vulnerability','','00110 daughters ~87% wool. Pipeline needs 5-6 stages to breed out. First finished animals ~10 years.'],
    ['Known Vulnerability','','Inbreeding spiral risk as Charlie sons cycle back. Monitor F coefficient. Introduce outside genetics if F > 0.20.'],
    ['Known Vulnerability','','Hurricane risk  -  east side pens more exposed than west side.'],
    ['Known Vulnerability','','16 ewe lambs scored FAMACHA 1-2 in dry summer  -  provisional only. Retest in wet season.'],
    ['Known Vulnerability','','Baby Azure FAMACHA 5 in dry summer when all other lambs scored 1-2. Cull candidate.'],
  ];
  sheet.getRange(1, 1, data.length, data[0].length).setValues(data);
  formatHeader(sheet, data[0].length);
  autoResize(sheet, data[0].length);
}

function updateBreedReference(ss) {
  var sheet = getOrCreateSheet(ss, 'Breed Reference');
  var data = [
    ['Breed','Type','Avg Ewe Wt','Avg Ram Wt','Notes'],
    ['American Black Belly','hair','115','137','Hair sheep. Small frame. Excellent parasite resistance.'],
    ['Awassi','wool','200','308','Wool. Fat-tailed dairy breed. Middle East origin. Heat tolerant.'],
    ['Babydoll','wool','80','125','Wool. Miniature Southdown. Very small.'],
    ['Barbados Black Belly','hair','95','125','Hair sheep. Foundation of many hair breeds.'],
    ['Black Headed Dorper','hair','160','300','Hair sheep. FL Dorper are small-framed (~80% of standard). Meat breed.'],
    ['Cotswold','wool','200','300','Wool. Long-wool breed. Large frame.'],
    ['Cracker','wool','110','225','Florida native heritage. Coat type VARIABLE  -  some individuals shed (Merrie), others retain wool ('],
    ['East Friesian','wool','210','275','Wool. Dairy breed. High milk production.'],
    ['Gulf Coast Native','wool','125','165','SE US native. WOOL coat despite being parasite resistant. Often confused with hair sheep due to hard'],
    ['Hampshire','wool','200','300','Wool. Meat breed. Large frame.'],
    ['Jacob','wool','100','150','Wool. Heritage breed. Small frame.'],
    ['Karakul','intermediate','130','175','Fat-tailed. Some shedding. Arid-adapted.'],
    ['Katahdin','hair','160','235','Gold standard hair sheep. Parasite resistant. Developed by Michael Piel from St Croix/Suffolk/Wiltsh'],
    ['Southdown','wool','180','250','Wool. Babydoll type. Compact meat breed.'],
    ['St Augustine','hair','185','300','HAIR sheep  -  Florida native. Heat/parasite adapted.'],
    ['St Croix','hair','120','165','Hair sheep. Caribbean origin. Foundation of Katahdin.'],
    ['Suffolk','wool','200','300','Wool. Terminal meat sire. Big lambs, dystocia risk.'],
    ['Tunis','wool','160','275','Wool. Fat-tailed. Good mothering. Heat tolerant for a wool breed.'],
    ['White Dorper','hair','185','235','Hair sheep. Meat breed.'],
    ['Wiltshire Horn','hair','150','300','Hair/shedding sheep. Used in Katahdin development.'],
  ];
  sheet.getRange(1, 1, data.length, data[0].length).setValues(data);
  formatHeader(sheet, data[0].length);
  // Color hair=green, wool=red, intermediate=yellow
  for (var i = 2; i <= data.length; i++) {
    var type = sheet.getRange(i, 2).getValue();
    var color = type == 'hair' ? '#ccffcc' : (type == 'wool' ? '#ffcccc' : '#ffffcc');
    sheet.getRange(i, 2).setBackground(color);
  }
  autoResize(sheet, data[0].length);
}

function updateRamEval(ss) {
  var sheet = getOrCreateSheet(ss, 'Ram Annual Eval');
  var data = [
    ['Ram','ID','Pen','Stage','Offspring FAMACHA (40%)','Offspring Shed % (25%)','Offspring ADG (15%)','Conception Rate (10%)','Offspring Survival (10%)','TOTAL','ACTION'],
    ['Rocky','rocky','Pen 2','7','','','','','','',''],
    ['Buck','buck','Chicken Coop','?','','','','','','',''],
    ['Merrieweather','merrie','Pen 4','3','','','','','','',''],
    ['Charlies Ewe Ram Lamb','charlies-ram-lamb','Pen 1','6','','','','','','',''],
    ['Orange Tag Ram','orange-tag-00110','Pen 1','6','','','','','','',''],
    ['Charlie','charlie-ram','Pen 3','1','','','','','','',''],
    ['Noris Baby Ram (Pen 3)','nori-baby-p3','Pen 3','1','','','','','','',''],
    ['Gigis 2025 Ram','gigi-2025-ram','Pen 4','3','','','','','','',''],
    ['Serendipity White Ram Twin','serendipity-twin-ram','Pen 4','3','','','','','','',''],
    ['FM2 Ram Lamb','fm2-ram-lamb','Pen 4','3','','','','','','',''],
    ['MC08','mc08-ram','Pen 6','5','','','','','','',''],
    ['0035 Baby Ram','tag-0035-baby-ewe','Tree Fort','2','','','','','','',''],
    ['Orange 31 Ram Lamb','tag-31-orange-tf-ram-lamb','Tree Fort','2','','','','','','',''],
    ['Windlestone Kat/Dorper Ram','windlestone-kat-dorper','Pen 2','7','','','','','','',''],
    ['Angus','angus','Pen 5','4','','','','','','',''],
  ];
  sheet.getRange(1, 1, data.length, data[0].length).setValues(data);
  formatHeader(sheet, data[0].length);
  autoResize(sheet, data[0].length);
}

function updateEweEval(ss) {
  var sheet = getOrCreateSheet(ss, 'Ewe Annual Eval');
  var data = [
    ['Ewe','ID','Pen','Stage','Own FAMACHA (30%)','Deworm Events (20%)','Shed Score 1-5 (15%)','Lambing (15%)','Offspring FAMACHA (10%)','BCS (10%)','TOTAL','ACTION'],
    ['Broken Tail','broken-tail','Pen 3','1','','','','','','','',''],
    ['Broken Tail Twin Ewe','broken-tail-twin-ewe','Pen 3','1','','','','','','','',''],
    ['Charlies Farm Ewe (Pen 3)','charlies-farm-ewe-p3','Pen 3','1','','','','','','','',''],
    ['Charlies Farm Ewe Baby','charlies-farm-ewe-baby-p3','Pen 3','1','','','','','','','',''],
    ['Cocoas Daughter (by Loki)','cocoas-daughter-by-loki','Pen 3','1','','','','','','','',''],
    ['Gigis 2026 Baby','gigi-2026-baby','Pen 3','1','','','','','','','',''],
    ['Nori','nori','Pen 3','1','','','','','','','',''],
    ['Bambii','bambii','Tree Fort','2','','','','','','','',''],
    ['Bambiis Baby','bambii-baby','Tree Fort','2','','','','','','','',''],
    ['Fawn Wool Ewe 114','tag-114-fawn-wool','Tree Fort','2','','','','','','','',''],
    ['Orange Tag 31 Ewe (Tree Fort)','tag-31-orange-tf','Tree Fort','2','','','','','','','',''],
    ['White Ewe 0035','tag-0035-white-ewe','Tree Fort','2','','','','','','','',''],
    ['FM','fm','Pen 4','3','','','','','','','',''],
    ['FM2','fm2-0051','Pen 4','3','','','','','','','',''],
    ['GG','gg','Pen 4','3','','','','','','','',''],
    ['Lara','lara','Pen 4','3','','','','','','','',''],
    ['Little Daisy','little-daisy','Pen 4','3','','','','','','','',''],
    ['Samson Daughter (Pen 4)','samson-daughter-p4','Pen 4','3','','','','','','','',''],
    ['Serendipity','serendipity','Pen 4','3','','','','','','','',''],
    ['Serendipity Black Ewe Twin','serendipity-twin-ewe','Pen 4','3','','','','','','','',''],
    ['Small White Ewe (Pen 4)','sm-white-ewe-p4','Pen 4','3','','','','','','','',''],
    ['Elsie','elsie','Pen 5','4','','','','','','','',''],
    ['Elsie Large White Ewe Triplet','elsie-triplet-lg-white-ewe','Pen 5','4','','','','','','','',''],
    ['Ewe Tag 02','tag-02-ewe-p5','Pen 5','4','','','','','','','',''],
    ['Ewe Tag 31','tag-31-ewe-p5','Pen 5','4','','','','','','','',''],
    ['Fawn Wool Ewe (Pen 5)','fawn-wool-ewe-p5','Pen 5','4','','','','','','','',''],
    ['OAV 2222','oav-2222','Pen 5','4','','','','','','','',''],
    ['OAV 2222 Lamb 1 (White-Rust)','oav-2222-lamb-1','Pen 5','4','','','','','','','',''],
    ['OAV 2222 Lamb 2 (White-Rust + Black Dot)','oav-2222-lamb-2','Pen 5','4','','','','','','','',''],
    ['Windlestone Fat Tail 0055','windlestone-0055','Pen 6','5','','','','','','','',''],
    ['Windlestone Fat Tail 0056','windlestone-0056','Pen 6','5','','','','','','','',''],
    ['Windlestone Fat Tail 2139','windlestone-2139','Pen 6','5','','','','','','','',''],
    ['00113','tag-00113-ewe-p1','Pen 1','6','','','','','','','',''],
    ['0053','nuba-0053','Pen 1','6','','','','','','','',''],
    ['0053s Baby Ewe','nuba-baby-ewe','Pen 1','6','','','','','','','',''],
    ['Azure','azure','Pen 1','6','','','','','','','',''],
    ['Baby Azure','baby-azure','Pen 1','6','','','','','','','',''],
    ['Charlies Ewe','charlies-ewe','Pen 1','6','','','','','','','',''],
    ['Hair Ewe 0033','tag-0033-hair-ewe','Pen 1','6','','','','','','','',''],
    ['Wool Ewe 0044','tag-0044-wool-ewe','Pen 1','6','','','','','','','',''],
    ['Cocoa','cocoa','','?','','','','','','','',''],
    ['Daisy (of Sugar)','daisy-of-sugar','','?','','','','','','','',''],
  ];
  sheet.getRange(1, 1, data.length, data[0].length).setValues(data);
  formatHeader(sheet, data[0].length);
  autoResize(sheet, data[0].length);
}

function updateDeceasedSold(ss) {
  var sheet = getOrCreateSheet(ss, 'Deceased & Sold');
  var data = [
    ['Name','ID','Tag','Sex','Status','Date','Breed','Sire','Dam','Notes'],
    ['Sir Loin','sir-loin','2','ram','deceased','2026-04-02','St Augustine/Katahdin','','','Flock spreadsheet: Tag 2, 75% St Augustine / 25% Katahdin. S'],
    ['Kelsier','kelsier','2223','ram','deceased','','Katahdin','','','Most parasite resistant sheep in the flock. Deceased. Pure K'],
    ['Samson','samson','','ram','deceased','','Hampshire','','','Was ram for Pen 4 group (Elsie, Nori, Trouble, Bsoe, Bsoed, '],
    ['Sam','sam','','ram','deceased','2024-09-26','Gulf Coast Native','','','Ram for pen 3 group. 100% Gulf Coast Native per Merrie breed'],
    ['SMore','smore','22','ram','deceased','','Cracker','','','Flock spreadsheet: Tag 22, 100% Cracker, 200lbs. Sire: Gigan'],
    ['Well Done','well-done','8','ram','deceased','','Katahdin','','','Flock spreadsheet: Tag 8, 100% Katahdin, 175lbs. Sire: Big D'],
    ['Butter Ball','butter-ball','','ram','deceased','','Dorper','','','Dorper ram. Deceased per weak resistance list.'],
    ['NoriSon','nori-son','054','ram','sold','2026-04-26','St Augustine/ABB/Wiltshire Horn/Katahdin','sir-loin','nori','MERGED RECORD 2026-04-26: Eclipse (tag 113) and NoriSon (tag'],
    ['Charlies Ram','charlies-ram','012','ram','deceased','2026-04-02','','','','Photos from March 18, 2024. Also called Mc11 or tag 12. Whit'],
    ['Pippin','pippin','015','ram','sold','','Cracker/St Augustine/Katahdin','smore','bsoed','Pippin/BSOE1. Tag 015. SMore (100%Cr) x BSOED (40.5K/59.5SA)'],
    ['New Black Belly Ram','new-black-belly-ram','018','ram','deceased','2026-04-02','American Blackbelly','','','New ABB ram from measurement list. Marked deceased April 202'],
    ['Charlies Lamb','charlies-lamb-0017','0017','ram','deceased','2026-04-02','','charlies-ram','','Charlies rams lamb. Tag 0017. Marked deceased April 2026  - '],
    ['Buck (Original)','buck-original','','ram','deceased','','Katahdin/Awassi/East Friesian','','','Original Buck ram in chicken coop. Came from Windlestone. 48'],
    ['Big Free Male','big-free-male','005','ram','deceased','2026-04-02','','','','Large free-roaming male from measurement list. Marked deceas'],
    ['Bella','bella','027','ewe','deceased','2026-04-02','','','','Tag 027 (from Heather Oaks Farm). 027 and 27 are different s'],
    ['Cinderella','cinderella','028','ewe','deceased','2026-04-02','','','','Tagged 28. Eyes good at tag day. In Pen 3. Marked deceased A'],
    ['Serendipitys Ram (2024)','serendipity-ram-2024','','ram','deceased','2026-04-02','Hampshire/St Augustine/Babydoll/Jacob/Katahdin','samson','serendipity','Serendipitys 2024 ram lamb by Samson (100% Hampshire). Breed'],
    ['Serendipitys Baby','serendipitys-baby-036','036','ewe','deceased','2026-04-02','','kelsier','serendipity','036, Mc12. Serendipitys baby ewe. Sire: Kelsier (pen 4 ram).'],
    ['Little Daisys Baby (Mc01)','little-daisys-baby-mc01','','ewe','deceased','2026-04-02','','','little-daisy','Mc01. Called babys baby in notebook. Little Daisy #35s offsp'],
    ['Baby','baby','','ewe','deceased','2026-04-02','Suffolk Cross','','','In pen 3 (Sam group). On weak resistance list. Google Sheet '],
    ['Baby Momma','baby-momma','','ewe','deceased','2026-04-02','','','','In pen 3 (Sam group). Marked deceased April 2026  -  not on '],
    ['Zara','zara','025','ewe','deceased','','Dorper','','','Tag 25. Zara = Dorper 25 (same animal). 100% Dorper. Decease'],
    ['Half Tail','half-tail','','ewe','deceased','2024-09-26','St Augustine/Katahdin/BBB','sir-loin','hersheys','Flock spreadsheet: 12.5% BBB / 31.25% Katahdin / 56.25% St A'],
    ['Trouble','trouble','033','ewe','deceased','2026-04-02','Katahdin/St Augustine/Dorper','sir-loin','haylee-lawson','Flock spreadsheet: Tag 9/retagged 33, 25%Dorper/37.5%K/37.5%'],
    ['Bsoe','bsoe','032','ewe','deceased','2026-04-02','Katahdin/St Augustine','sir-loin','two-pence','Flock spreadsheet: 56%K/44%SA, 185lbs. DOB ~1/1/2019. Sir Lo'],
    ['Bsoed','bsoed','031','ewe','deceased','2026-04-02','St Augustine/Katahdin','sir-loin','bsoe','Flock spreadsheet: ~40.5%K/~59.5%SA, 175lbs. DOB 1/18/2020. '],
    ['FM1','fm1','009','ewe','deceased','2026-04-02','St Augustine/Cotswold/Tunis/Katahdin','sir-loin','fm','FM1 = Sir Loin x FM per FM breeding page. Tag 009. DOB 4/1/2'],
    ['Gertrude Moon','gertrude-moon','022','ewe','deceased','','American Black Belly','gertrude-moon-sire','gertrude-moon-dam','Gertrude Moon aka Bitch Face (BF). Tag 22. 100%ABB. DOB ~202'],
    ['GM Twin 1 (2024)','gm-twin1-2024','','unknown','deceased','','ABB/St Augustine/Katahdin','sir-loin','gertrude-moon','Born 1-2-24. Sir Loin x Gertrude Moon. Not kept per owner.'],
    ['GM Twin 2 (2024)','gm-twin2-2024','','unknown','deceased','','ABB/St Augustine/Katahdin','sir-loin','gertrude-moon','Born 1-2-24. Sir Loin x Gertrude Moon. Not kept per owner.'],
    ['Circle Tail','circle-tail','','ewe','deceased','2026-04-02','Cracker/St Augustine/Katahdin','smore','brown-knee','Flock spreadsheet: 50% Cracker / 21.875% Katahdin / 28.125% '],
    ['Fox Tail','fox-tail','017','ewe','deceased','','Cracker/St Augustine/Katahdin/Dorper','smore','trouble','Tag 17. SMore (100%Cr) x Trouble (37.5K/37.5SA/25Dorper). 50'],
    ['S1','s1','','ewe','deceased','2026-04-02','','','','In pen 6 (no ram). Marked deceased April 2026  -  not on not'],
    ['S2','s2','','ewe','deceased','2026-04-02','','','','In pen 2 (sirloin group). Marked deceased April 2026  -  not'],
    ['Pebbles','pebbles','','ewe','deceased','2026-04-02','','','','In pen 2 (sirloin group). FAMACHA 3, treated. Entry struck t'],
    ['Anna','anna','1','ewe','deceased','','Katahdin','','','Flock spreadsheet: Tag 1, 100% Katahdin, 175lbs. DOB 1/12/20'],
    ['Boots','boots','7','ewe','culled','','Dorper/Katahdin','','','Flock spreadsheet: Tag 7, 50% Dorper / 50% Katahdin, 130lbs.'],
    ['Patches','patches','27','ewe','deceased','2026-04-02','','','','Weight calculator: 65.6lbs (girth 27, length 27). Tag 27  - '],
    ['Little Song','little-song','008','ewe','deceased','2026-04-02','St Augustine/Katahdin','sir-loin','annas-big-one','Flock spreadsheet: Tag 8/retagged 008, 43.75% Katahdin / 56.'],
    ['Black Rock','black-rock','010','ewe','deceased','2026-04-02','','','','Tag 010. From measurement list. No measurements recorded yet'],
    ['Question Tail','question-tail','001','ewe','deceased','2026-04-02','','','','Tag 001. From measurement list. Marked deceased April 2026  '],
    ['Female 004','female-004','004','ewe','deceased','2026-04-02','','','','Tag 004. From measurement list. Marked deceased April 2026  '],
    ['Half Tails Baby','half-tails-baby','007','ewe','deceased','2026-04-02','','','half-tail','Tag 007. Half Tails baby. From measurement list. Marked dece'],
    ['Sb1 (Crown)','sb1-crown','002','ewe','deceased','2026-04-02','','','','Tag 002. Called Sb1 (crown) in measurements. Weight calculat'],
    ['Sb2 (All Black)','sb2-all-black','003','ewe','deceased','2026-04-02','','','','Tag 003. Called Sb2 (all black) in measurements. Weight calc'],
    ['New Big Girl 2','new-big-girl-2','','ewe','deceased','2026-04-02','','','','In pen 3 (Sam group). Marked deceased April 2026  -  not on '],
    ['Daisys Daughter 2','daisys-daughter-2','','ewe','deceased','2026-04-02','St Augustine/Katahdin/BBB/Wiltshire','','daisy','From Google Sheet Pen 5 and 6. In NoriSons group. Different '],
    ['Tag 31','tag-31-ewe','031-pen2','ewe','deceased','2026-04-02','Katahdin/St Augustine/Dorper/BBB','','','From Google Sheet Pen 2. 69.25% wool. Different from Bsoed t'],
    ['Tag 33','tag-33','033-pen1','ewe','deceased','2026-04-02','Katahdin/St Augustine/BBB/Cracker/White Dorper/Suffolk/GCN','','','From Google Sheet Pen 1. 3/4 hair. Has twins. Marked decease'],
    ['Bambi','bambi','037','ewe','deceased','2026-04-02','Katahdin/Dorper','','','Weight calculator: tag 35, 81.3lbs (girth 29, length 29). Go'],
    ['Irish','irish','','ewe','deceased','2026-04-02','','','little-daisy','Little Daisys daughter. Needed parasite treatment April 13, '],
    ['Unnamed (Pen 2)','unnamed-pen2','','ewe','deceased','2026-04-02','','','','Unnamed ewe in pen 2 (sirloin group). Not the same as the de'],
    ['Fl51870-0502','fl51870-0502','Fl51870-0502','ewe','deceased','2026-04-02','Hampshire/Suffolk','','','Florida scrapie tag Fl51870-0502. 50%Hampshire/50%Suffolk. E'],
    ['FMs Lamb (2023)','fm-lamb-2023','','ewe','deceased','2026-04-02','St Augustine/Cotswold/Tunis/Katahdin','sir-loin','fm','FM x Sir Loin lamb = FM1 (tag 009). Born 4/1/2023. Birth wei'],
    ['Ext Lamb 8 (ABG)','ext-lamb-8','','ram','deceased','','','','','Extension service lamb ID 8. Ram, born 1/24/2023 (type 3). E'],
    ['Shaggy','shaggy','','ewe','deceased','','Babydoll/Jacob','','','Flock spreadsheet: 50% Babydoll / 50% Jacob, Black, 140lbs. '],
    ['Skitters','skitters','','ewe','deceased','','Karakul','','','Deceased. 100% Karakul per Rocky breeding page. Also called '],
    ['W136','w136','','ewe','deceased','','','','','Deceased. On weak resistance list.'],
    ['Unnamed (Deceased)','unnamed-deceased','','unknown','deceased','','','','','Deceased. On weak resistance list as Unnamed (deceased).'],
    ['Hersheys','hersheys','3','ewe','deceased','','BBB/Katahdin/St Augustine','sir-loin','sugar','Flock spreadsheet: Tag 3, 25% BBB / 37.5% Katahdin / 37.5% S'],
    ['GGs Daughter','gg-daughter-45','045','ewe','deceased','','','kelsier','gg','GGs daughter. Tag 45. Sire: Kelsier, Dam: GG (owner-confirme'],
    ['Laras Daughter','lara-daughter-46','046','ewe','sold','','','kelsier','lara','Kelsier (sire) x Lara (dam) daughter. Tag 46. Sold because p'],
    ['GGs Son','gg-son-094','094','ram','deceased','','','kelsier','gg','GGs son. Tag 094. Sire: Kelsier, Dam: GG (owner-confirmed 20'],
    ['430-2079','tag-430-2079','430-2079','ewe','deceased','2023-08-21','Suffolk/Hampshire','','','Tag 430-2079 (pen 5). 25%Hampshire/75%Suffolk. Ewe weight 33'],
    ['Kelsiers Sister','kelsiers-sister','2241','ewe','deceased','','Katahdin','','','Kelsiers sister. Tag 2241. 100% Katahdin. Weight 150lbs. Bre'],
    ['Dorper Ram (Deceased)','dorper-ram-deceased','','ram','deceased','','Dorper','','','Dorper ram from sick sheep note. Given iron and B on 10-24. '],
    ['Tag 240002','tag-240002','240002','unknown','sold','2026-02-15','','','','Sold 2026-02-15.'],
    ['Tag 0049','tag-0049','0049','unknown','sold','2026-02-15','','','','Sold 2026-02-15.'],
    ['Tag 240001','tag-240001','240001','unknown','sold','2026-02-15','','','','Sold 2026-02-15.'],
    ['Mc06','mc06','','unknown','sold','2026-02-15','','','','Sold 2026-02-15. MC tag Mc06.'],
    ['Tag 0050','tag-0050','0050','unknown','sold','2026-02-15','','','','Sold 2026-02-15. Possibly one of the goose pen auction lambs'],
    ['Razzle','razzle','5','ram','deceased','','Barbados Blackbelly','','','Flock spreadsheet: Tag 5, 100% BBB ram, Badger color, 125lbs'],
    ['Frazzle','frazzle','6','ewe','deceased','','Katahdin','','','Flock spreadsheet: Tag 6, 100% Katahdin ewe, Black, 175lbs. '],
    ['Almond Joy','almond-joy','','ram','deceased','','','','','From Sheep Breeding DB. Ram culled (C) for being cryptorchid'],
    ['Sugar','sugar','4','ewe','deceased','','BBB/Katahdin','razzle','frazzle','Flock spreadsheet: Tag 4, 50% BBB / 50% Katahdin, Tan, 224lb'],
    ['Penny','penny','','ewe','deceased','','','','','From Sheep Breeding DB. Ewe culled (C) for poor shedding.'],
    ['Two Pence','two-pence','','ewe','deceased','','Katahdin/St Augustine','','','From Sheep Breeding DB. Ewe culled as daughter of cryptorchi'],
    ['Haylee Lawson','haylee-lawson','14','ewe','deceased','','Dorper/Katahdin','','','Flock spreadsheet: Tag 14, 50% Dorper / 50% Katahdin, White,'],
    ['Pretzel','pretzel','13','ewe','deceased','','Dorper/Katahdin','','','Flock spreadsheet: Tag 13, 75% Dorper / 25% Katahdin, Black/'],
    ['W140','w140','','ewe','deceased','2026-04-02','','','','On weak resistance list. Status alive but weak. Marked decea'],
    ['Annas Big One','annas-big-one','','ewe','deceased','2026-04-02','Katahdin/St Augustine','sir-loin','anna','Flock spreadsheet: 62.5% Katahdin / 37.5% St Augustine, 200l'],
    ['Dorpy','dorpy','','ewe','deceased','2026-04-02','Katahdin/Dorper/Babydoll','','','From Google Sheet Pen 4. Tag 34 offspring row. Marked deceas'],
    ['Tag 34 (Pen 4)','tag-34-pen4','','ewe','deceased','2026-04-02','Katahdin/St Augustine','','','From Google Sheet Pen 4. 100% hair. Marked deceased April 20'],
    ['0033 Twin Ram 1 (White/Brown)','tag-0033-twin-ram-1','MC2608','ram','sold','2026-04-06','[UNCLEAR - 0033 offspring]','','tag-0033-hair-ewe','No tag (now tagged, number TBD). Born ~1-1-26. Twin from 003'],
    ['0033 Twin Ram 2 (Black)','tag-0033-twin-ram-2','MC2609','ram','sold','2026-04-26','[UNCLEAR - 0033 offspring]','','tag-0033-hair-ewe','No tag (now tagged, number TBD). Born ~1-1-26. Twin from 003'],
    ['Broken Tail Twin Ewe 2 (White)','broken-tail-twin-ewe-2','MC-2601','ewe','deceased','2026-04-22','[UNCLEAR - Broken Tail offspring]','','broken-tail','No tag (now tagged TBD). Born 12-31-25. Broken Tails second '],
    ['Daisy (Anna line)','daisy-anna-line','','ewe','sold','','Sir Loin x Anna offspring','sir-loin','anna','Sold off farm. Buyers named her Daisy. CORRECTION 2026-05-13'],
    ['Elsie Small White Ewe Triplet','elsie-triplet-sm-white-ewe','','ewe','sold','2026-04-26','','nori-son','elsie','Born 1-6-26. Elsies triplet. Small white female. Sire: NoriS'],
    ['Elsie Black Ram Triplet','elsie-triplet-black-ram','','ram','gifted','2026-03-15','','nori-son','elsie','Born 1-6-26. Elsies triplet. Black ram. Sire: Eclipse. Gifte'],
    ['Goose Pen 09','goose-09','09','ram','sold','2026-02-15','','','','Sold at auction 2-15-26. ~00.'],
    ['Goose Pen 50','goose-50','50','ewe','sold','2026-02-15','','','','Wooly Tan. Sold at auction 2-15-26. ~00.'],
    ['Goose Pen 06','goose-06','06','ram','sold','2026-02-15','','','','White Hair/Tan. Sold at auction 2-15-26. ~00.'],
    ['Goose Pen L19','goose-l19','L19','ewe','sold','2026-02-15','','','','Black, sheared. Sold at auction 2-15-26. ~00.'],
    ['00113s Singleton (deceased)','tag-00113-singleton-2026','','unknown','deceased','2026-04-25','[Cracker/Suffolk/GCN/Katahdin x Sir Loin/Nori]','nori-son','tag-00113-ewe-p1','Singleton lamb of 00113 by NoriSon. Born 2026-04-22, died 20'],
  ];
  sheet.getRange(1, 1, data.length, data[0].length).setValues(data);
  formatHeader(sheet, data[0].length);
  autoResize(sheet, data[0].length);
}
