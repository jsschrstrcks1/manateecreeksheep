/**
 * Manatee Creek Flock — Google Sheets Updater
 * Generated: 2026-04-02 17:59
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

function updatePipelineOverview(ss) {
  var sheet = getOrCreateSheet(ss, 'Pipeline Overview');
  var data = [
    ['Stage','Pen','Size','Location','Ram','Ram Weight','Hair %','Coat','Ewes','FAMACHA Req','FEC Req','Shed Req','Shelter','Notes'],
    ['1','Pen 3','largest (~4x Tree Fort)','SE corner, east side','00110','?','?','?',11,'<3','<500','>25%','standard','287 lbs, 12.5% hair, extra wooly but big and meaty. Starts converting wool ewes.'],
    ['2','Tree Fort','smallest','east side, between Goose Pen and Pen 4','Gigis 2025 Ram','?','?','?',3,'<3','<400','>35%','best on property','Kelsier x GG, ~50% hair, wooly. 50% Katahdin from NSIP sire. Tests Kelsier genet'],
    ['3','Pen 4','large','east side','Rocky','300','50','mixed',9,'<3','<350','>50%','standard','300 lbs, 50% hair (BHD/Awassi). WEAK parasites but adds meat/Dorper genetics. Se'],
    ['4','Pen 5','medium-large','east side','Buck','270.8','50','mixed',5,'<2','<300','>65%','standard','271 lbs, 50% hair (Kat/Awassi). Katahdin adds parasite resistance back after Roc'],
    ['5','Pen 6','medium','NE corner, east side','Serendipity White Ram Twin','?','?','?',2,'<2','<250','>80%','standard','Serendipity White Ram Twin (Kelsier×Serendipity, ~56% Kat). PROVISIONAL — pendin'],
    ['6','Pen 1','medium-small','SW corner, west side (isolated)','Merrie','200','50.0','hair',3,'<2','<200','>90%','solid','Merrie (200 lbs, observed shedder). 2nd best shedding ram. Stage 6 refinement.'],
    ['7','Pen 2','small','SW corner, west side (isolated, most secure)','Charlie','232.2','100.0','hair',2,'1-2 only','<150','>95%','solid, most secure','Charlie (232 lbs, 100% hair). Best ram in flock. Earned elite status. Broken Tai'],
    ['outside','Goose Pen','small-medium','east side, between Pen 3 and Tree Fort','MC08','190','?','?',3,'','','','standard','190 lbs, unknown breed, very wooly. Awassi dairy line only. Outside main pipelin'],
  ];
  sheet.getRange(1, 1, data.length, data[0].length).setValues(data);
  formatHeader(sheet, data[0].length);
  autoResize(sheet, data[0].length);
}

function updateActiveFlock(ss) {
  var sheet = getOrCreateSheet(ss, 'Active Flock');
  var data = [
    ['Pen','Stage','Name','ID','Tag','Sex','Weight','Breed','Hair %','Wool %','Coat Obs','Coat Pred','Sire','Dam','Weak Parasites','Notes'],
    ['Pen 3','1','Orange Tag Ram','orange-tag-00110','00110','ram','287.5','Cracker/Suffolk/GCN/Katahdin','12.5','87.5','wool','wool','None','None','','Tag 00110, orange tag. Ram. Poop trimmed at butt 2-19-2026. '],
    ['Pen 3','1','Azure','azure','20','ewe','212.5','Hampshire/Suffolk','0','100','','wool','None','None','YES','Mom calls her \'Amure\'. GG\'s full sister. On weak resistan'],
    ['Pen 3','1','Baby Azure','baby-azure','None','ewe','','[UNCLEAR - Azure offspring]','','','','','None','azure','','No tag (now tagged, number TBD). Born 1-10-26. Azures baby, '],
    ['Pen 3','1','Bambii','bambii','None','ewe','None','','','','','','None','None','','In Pen 2 (Sir Loin group) per spiral notebook (authoritative'],
    ['Pen 3','1','Charlies Ewe','charlies-ewe','None','ewe','','[UNCLEAR]','','','','','None','None','','No tag (now tagged, number TBD). Single baby (ram, born 12-2'],
    ['Pen 3','1','Ewe Tag 02','tag-02-ewe-p5','02','ewe','','[UNCLEAR]','','','','','','','','Tag 02. Ewe. Pen 5. No babies. Proven breeder — Eclipse fail'],
    ['Pen 3','1','FM','fm','0011','ewe','212.5','Cotswold/Tunis','0','100','','wool','fm-sire','fm-dam','YES','Tag GA1568-011, 50% Cotswold / 50% Tunis, Tunis Red, 200lbs.'],
    ['Pen 3','1','FM2','fm2-0051','0051','ewe','185','Cotswold/Tunis/St Augustine/Katahdin','50.0','50','','mixed','sir-loin','fm','','Tag 0051. FM2. Fat and gray. 1 baby ram born 1-31-26. Sire: '],
    ['Pen 3','1','Fawn Wool Ewe (Pen 5)','fawn-wool-ewe-p5','None','ewe','','Wool','','','','','','','','No tag (now tagged TBD). Wool ewe, fawn color, long ears. Pe'],
    ['Pen 3','1','GG','gg','23','ewe','212.5','Hampshire/Suffolk','0','100','','wool','None','None','YES','Azure\'s full brother. On weak resistance list. From Google '],
    ['Pen 3','1','Nuba','nuba-0053','0053','ewe','175','Hampshire/St Augustine/Katahdin','50.0','50','','mixed','samson','None','','Tag 0053. White Hair ewe. Name: Nuba (notebook spelling). No'],
    ['Pen 3','1','Wool Ewe 0044','tag-0044-wool-ewe','0044','ewe','170','Katahdin/Awassi/East Friesian','50','50','','mixed','None','None','','Tag 0044. Wool ewe. No babies. Source: notebook card, pen 1.'],
    ['Tree Fort','2','Gigis 2025 Ram','gigi-2025-ram','09','ram','','[Kelsier x Gigi offspring]','','','','','kelsier','gg','','Tag 09 [UNCLEAR]. Gigis 2025 baby. Yearling ram, old enough '],
    ['Tree Fort','2','Fawn Wool Ewe 114','tag-114-fawn-wool','114','ewe','145','Cracker/Suffolk/GCN/Katahdin','12.5','87.5','','wool','None','None','','Tag 114, orange tag. Fawn wool ewe. Was in Pen 2 but moved t'],
    ['Tree Fort','2','Orange Tag 31 Ewe (Tree Fort)','tag-31-orange-tf','31','ewe','','','','','','','','','','Tag 31, orange tag. DIFFERENT animal from Tag 31 in Pen 5. C'],
    ['Tree Fort','2','Serendipity','serendipity','030','ewe','138','St Augustine/Babydoll/Jacob/Katahdin','50.0','50','','mixed','sir-loin','shaggy','','Breeding page: 25%Babydoll/25%Jacob/12.5%K/37.5%SA. Tag 30. '],
    ['Pen 4','3','Rocky','rocky','140','ram','300','Black Headed Dorper/Awassi/East Friesian','50','50','','mixed','teaser','dorper-ewe-198','YES','Also called Jerkface/Rock/Louise\'s Ram. Tag 140. 44%Awassi/'],
    ['Pen 4','3','0035 Baby Ewe','tag-0035-baby-ewe','None','ewe','','','','','','','','tag-0035-white-ewe','','Born 1-2-26. 0035s baby ewe. 7 weeks old 2-20-26. Source: no'],
    ['Pen 4','3','BHD Ewe G023','g023-bhd-ewe','G023','ewe','128.0','Black Headed Dorper','100','0','','hair','None','None','','Tag G023. BHD ewe. No babies. FAMACHA borderline (3) on 2-20'],
    ['Pen 4','3','Bambiis Baby','bambii-baby','None','ewe','','','','','','','','bambii','','Born 12-28-25. Bambiis baby. 7.5 weeks old 2-20-26. Sex UNCL'],
    ['Pen 4','3','Broken Tail Twin Ewe','broken-tail-twin-ewe','None','ewe','','[UNCLEAR - Broken Tail offspring]','','','','','None','broken-tail','','No tag (now tagged TBD). Born 12-31-25. Broken Tails twin ew'],
    ['Pen 4','3','Broken Tail Twin Ewe 2 (White)','broken-tail-twin-ewe-2','None','ewe','','[UNCLEAR - Broken Tail offspring]','','','','','None','broken-tail','','No tag (now tagged TBD). Born 12-31-25. Broken Tails second '],
    ['Pen 4','3','Gigis 2026 Baby','gigi-2026-baby','None','ewe','','[Kelsier x Gigi offspring]','','','','','kelsier','gg','','Born 1-10-26. Gigis baby. Multi color ewe. Sire: Kelsier. 5.'],
    ['Pen 4','3','Little Daisy','little-daisy','035','ewe','145','St Augustine/Katahdin/BBB','100.0','0','','hair','dodge','daisy','','Breeding page: Dodge (Sir Loin x Broken Tail) x Daisy (Sir L'],
    ['Pen 4','3','Small White Ewe (Pen 4)','sm-white-ewe-p4','None','ewe','145','St Augustine/Katahdin/BBB','100.0','0','','hair','dodge','daisy','','No tag (now tagged TBD). Small white ewe. No babies. Eyes go'],
    ['Pen 4','3','White Ewe 0035','tag-0035-white-ewe','0035','ewe','130','Black Headed Dorper/Katahdin','100','0','','hair','','','','Tag 0035. White ewe with dot on ear. Single baby (ewe, born '],
    ['Pen 5','4','Buck','buck','None','ram','270.8','Katahdin/Awassi/East Friesian','50','50','','mixed','None','None','','Current Buck in chicken coop. Brother of original Buck who d'],
    ['Pen 5','4','Charlies Farm Ewe Baby','charlies-farm-ewe-baby-p3','None','ewe','','[UNCLEAR - Charlies Farm Ewe offspring]','','','','','charlie-ram','charlies-farm-ewe-p3','','No tag (now tagged TBD). Born 12-6-25. Baby ewe from Charlie'],
    ['Pen 5','4','Elsie Large White Ewe Triplet','elsie-triplet-lg-white-ewe','None','ewe','','','','','','','eclipse','elsie','','Born 1-6-26. Elsies triplet. Large white female. Sire: Eclip'],
    ['Pen 5','4','Elsie Small White Ewe Triplet','elsie-triplet-sm-white-ewe','None','ewe','','','','','','','eclipse','elsie','','Born 1-6-26. Elsies triplet. Small white female. Sire: Eclip'],
    ['Pen 5','4','Noris Baby (Pen 3)','nori-baby-p3','None','ewe','','[UNCLEAR - Nori offspring]','','','','','None','nori','','No tag (now tagged TBD). Born 1-10-26. 0029/Noris Baby. 5.3 '],
    ['Pen 5','4','Serendipity Black Ewe Twin','serendipity-twin-ewe','None','ewe','','[Kelsier x Serendipity offspring]','','','','','kelsier','serendipity','','Born 12-30-25. Serendipitys black ewe twin. Sire: Kelsier. F'],
    ['Pen 6','5','Serendipity White Ram Twin','serendipity-twin-ram','None','ram','','[Kelsier x Serendipity offspring]','','','','','kelsier','serendipity','','Born 12-30-25. Serendipitys white ram twin. Sire: Kelsier. F'],
    ['Pen 6','5','Charlies Farm Ewe (Pen 3)','charlies-farm-ewe-p3','None','ewe','155','Katahdin/BHD/ABB/Wiltshire Horn','100.0','0','','hair','None','None','','No tag (now tagged TBD). Ewe from Charlies Farm. Multi color'],
    ['Pen 6','5','OAV 2222','oav-2222','2222','ewe','140','Katahdin','100','0','','hair','None','None','','Kelsier\'s sister. 100% Katahdin confirmed by Rocky and OAV '],
    ['Pen 1','6','Merrie','merrie','00016','ram','200','Cracker/St Augustine/Katahdin/BBB/White Dorper','50.0','50','hair','hair','smore','half-tail','','Flock spreadsheet: Tag 016, ram. S\'More (100%Cr) x Half Tai'],
    ['Pen 1','6','Ewe Tag 31','tag-31-ewe-p5','31','ewe','170','St Augustine/Katahdin','100','0','','hair','sir-loin','','','Tag 31. Ewe. Pen 5. No babies. Proven breeder in prior years'],
    ['Pen 1','6','Hair Ewe 0033','tag-0033-hair-ewe','0033','ewe','170','St Augustine/Katahdin','100.0','0','','hair','sir-loin','None','','Tag 0033. Hair ewe. Had twins (2 rams, born ~1-1-26). Source'],
    ['Pen 1','6','Nori','nori','0029','ewe','139','ABB/Wiltshire Horn','100','0','','hair','None','None','','Nori breeding page: 50%ABB/50%WH, tag 21 (tag lost). Ewe wei'],
    ['Pen 2','7','Charlie','charlie-ram','None','ram','232.2','Katahdin/BHD/ABB/Wiltshire Horn','100.0','0','','hair','None','None','','No tag (now tagged, number TBD). Charlies Ram. Horned. Had j'],
    ['Pen 2','7','Broken Tail','broken-tail','034','ewe','225','St Augustine/Katahdin/BBB','100.0','0','','hair','sir-loin','half-tail','','Flock spreadsheet: 6.25% BBB / 28.125% Katahdin / 65.625% St'],
    ['Pen 2','7','Elsie','elsie','025','ewe','175','Katahdin/St Augustine/BBB','100.0','0','','hair','well-done','half-tail','','Breeding page: Tag 25, 6.25%ABB(BBB)/65.625%K/28.125%SA. DOB'],
    ['Goose Pen','outside','0033 Twin Ram 1 (White/Brown)','tag-0033-twin-ram-1','None','ram','','[UNCLEAR - 0033 offspring]','','','','','None','tag-0033-hair-ewe','','No tag (now tagged, number TBD). Born ~1-1-26. Twin from 003'],
    ['Goose Pen','outside','0033 Twin Ram 2 (Black)','tag-0033-twin-ram-2','None','ram','','[UNCLEAR - 0033 offspring]','','','','','None','tag-0033-hair-ewe','','No tag (now tagged, number TBD). Born ~1-1-26. Twin from 003'],
    ['Goose Pen','outside','114 Black Ram Lamb','tag-114-black-ram-lamb','None','ram','','[UNCLEAR - 114 offspring]','','','','','rocky','tag-114-fawn-wool','','Born 3-29-2026. Little black ram lamb with white spot on hea'],
    ['Goose Pen','outside','Charlies Ewe Ram Lamb','charlies-ram-lamb','None','ram','','[UNCLEAR]','','','','','None','charlies-ewe','','No tag (now tagged, number TBD). Born 12-26-25. 9.5 weeks ol'],
    ['Goose Pen','outside','Eclipse','eclipse','113','ram','251.2','St Augustine/ABB/Wiltshire Horn/Katahdin','100.0','0','','hair','sir-loin','nori','','25%ABB/12.5%K/37.5%SA/25%WH. Sir Loin (25K/75SA) x Nori (50A'],
    ['Goose Pen','outside','FM2 Ram Lamb','fm2-ram-lamb','None','ram','','[Kelsier x FM2 offspring]','','','','','kelsier','fm2-0051','','Born 1-31-26. FM2s baby ram. Sire: Kelsier. 2.6 weeks old as'],
    ['Goose Pen','outside','MC08','mc08-ram','MC08','ram','190','[UNCLEAR - possibly Samson or Buck son]','','','','','','','','Tag MC08, yellow. Ram. Fawn wool sheep. Possibly Samsons son'],
    ['Goose Pen','outside','Orange 31 Ram Lamb','tag-31-orange-tf-ram-lamb','None','ram','','','','','','','','tag-31-orange-tf','','Born 1-2-26. Orange tag 31 ewes baby ram. 7 weeks old 2-20-2'],
    ['Goose Pen','outside','Windlestone Fat Tail 0055','windlestone-0055','0055','ewe','200.0','Awassi (almost pure)','0','95','','wool','','','','Tag 0055. Windlestone Ranch fat tail (Awassi) ewe. Tiny/sm h'],
    ['Goose Pen','outside','Windlestone Fat Tail 0056','windlestone-0056','0056','ewe','200.0','Awassi (almost pure)','0','95','','wool','','','','Tag 0056. Windlestone Ranch fat tail (Awassi) ewe. Med thick'],
    ['Goose Pen','outside','Windlestone Fat Tail 2139','windlestone-2139','2139','ewe','200.0','Awassi (almost pure)','0','95','','wool','','','','Tag 2139. Windlestone Ranch fat tail (Awassi) ewe. Big ewe w'],
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
    ['Selection Hierarchy','#4 Meatiness','Tiebreaker. Given two animals equal in parasites, coat, and breed — choose the meatiest.'],
    ['','',''],
    ['Hard Lesson','','St Croix purchased and brought to property DIED OF PARASITES. Breed reputation ≠ individual resistance.'],
    ['Hard Lesson','','Barbados Black Belly purchased and brought to property DIED OF PARASITES. Same lesson.'],
    ['Hard Lesson','','Windlestone Dorper (exceptional South African bloodlines) are EXTREMELY VULNERABLE to parasites despite being hair sheep'],
    ['Hard Lesson','','GG and Rocky are alive because owner skill improved, not because they are resistant. They require aggressive treatment t'],
    ['Hard Lesson','','Cracker coat type is VARIABLE per individual — Merrie sheds, 00110 does not. Cannot classify per breed.'],
    ['Hard Lesson','','Every animal currently alive has survived Florida parasite pressure. That survival IS the genetics that work.'],
    ['Hard Lesson','','Buying outside genetics is HIGH RISK. Even \'resistant\' breeds die here. Safest investment is what\'s already proven on'],
    ['','',''],
    ['Pipeline','Target Animal','Hardy (survives Florida with minimal care), Hairy (sheds coat), Meaty (good muscling/growth), Parasite resistant (FAMACH'],
    ['Pipeline','Inbreeding Policy','Managed tool, not hard block. F < 0.25 acceptable. Intentional line breeding toward homogeneity.'],
    ['Pipeline','Key Insight',''],
    ['','',''],
    ['Stress Test Fix','2026-04-02','Baby Azure moved from Stage 3 to Stage 1 (FAMACHA 5 in dry season = worst performer)'],
    ['Stress Test Fix','2026-04-02','Charlie + Broken Tail + Elsie moved to Pen 2 (elite) — they earned it, no need to wait'],
    ['Stress Test Fix','2026-04-02','Merrie promoted to Pen 1 (Stage 6) — 2nd best shedder after Charlie'],
    ['Stress Test Fix','2026-04-02','Serendipity White Ram Twin placed at Pen 6 (Stage 5) — PROVISIONAL pending summer FAMACHA'],
    ['Known Vulnerability','','Charlie is single point of failure (only 100% hair ram). Backup: test Kelsier sons summer 2026.'],
    ['Known Vulnerability','','Rocky at Stage 3 contaminates with weak parasite genetics. Mitigate by hard culling his FAMACHA-3+ offspring.'],
    ['Known Vulnerability','','00110 daughters ~87% wool. Pipeline needs 5-6 stages to breed out. First finished animals ~10 years.'],
    ['Known Vulnerability','','Inbreeding spiral risk as Charlie sons cycle back. Monitor F coefficient. Introduce outside genetics if F > 0.20.'],
    ['Known Vulnerability','','Hurricane risk — east side pens more exposed than west side.'],
    ['Known Vulnerability','','16 ewe lambs scored FAMACHA 1-2 in dry summer — provisional only. Retest in wet season.'],
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
    ['American Black Belly','hair',115,137,'Hair sheep. Small frame. Excellent parasite resistance.'],
    ['Awassi','wool',200,308,'Wool. Fat-tailed dairy breed. Middle East origin. Heat tolerant.'],
    ['Babydoll','wool',80,125,'Wool. Miniature Southdown. Very small.'],
    ['Barbados Black Belly','hair',95,125,'Hair sheep. Foundation of many hair breeds.'],
    ['Black Headed Dorper','hair',160,300,'Hair sheep. FL Dorper are small-framed (~80% of standard). Meat breed.'],
    ['Cotswold','wool',200,300,'Wool. Long-wool breed. Large frame.'],
    ['Cracker','wool',110,225,'Florida native heritage. Coat type VARIABLE — some individuals shed (Merrie), others retain wool (00'],
    ['East Friesian','wool',210,275,'Wool. Dairy breed. High milk production.'],
    ['Gulf Coast Native','wool',125,165,'SE US native. WOOL coat despite being parasite resistant. Often confused with hair sheep due to hard'],
    ['Hampshire','wool',200,300,'Wool. Meat breed. Large frame.'],
    ['Jacob','wool',100,150,'Wool. Heritage breed. Small frame.'],
    ['Karakul','intermediate',130,175,'Fat-tailed. Some shedding. Arid-adapted.'],
    ['Katahdin','hair',160,235,'Gold standard hair sheep. Parasite resistant. Developed by Michael Piel from St Croix/Suffolk/Wiltsh'],
    ['Southdown','wool',180,250,'Wool. Babydoll type. Compact meat breed.'],
    ['St Augustine','hair',185,300,'HAIR sheep — Florida native. Heat/parasite adapted.'],
    ['St Croix','hair',120,165,'Hair sheep. Caribbean origin. Foundation of Katahdin.'],
    ['Suffolk','wool',200,300,'Wool. Terminal meat sire. Big lambs, dystocia risk.'],
    ['Tunis','wool',160,275,'Wool. Fat-tailed. Good mothering. Heat tolerant for a wool breed.'],
    ['White Dorper','hair',185,235,'Hair sheep. Meat breed.'],
    ['Wiltshire Horn','hair',150,300,'Hair/shedding sheep. Used in Katahdin development.'],
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
    ['Rocky','rocky','Pen 4','3','','','','','','',''],
    ['Buck','buck','Pen 5','4','','','','','','',''],
    ['Merrie','merrie','Pen 1','6','','','','','','',''],
    ['Orange Tag Ram','orange-tag-00110','Pen 3','1','','','','','','',''],
    ['Charlie','charlie-ram','Pen 2','7','','','','','','',''],
    ['Gigis 2025 Ram','gigi-2025-ram','Tree Fort','2','','','','','','',''],
    ['Serendipity White Ram Twin','serendipity-twin-ram','Pen 6','5','','','','','','',''],
  ];
  sheet.getRange(1, 1, data.length, data[0].length).setValues(data);
  formatHeader(sheet, data[0].length);
  autoResize(sheet, data[0].length);
}

function updateEweEval(ss) {
  var sheet = getOrCreateSheet(ss, 'Ewe Annual Eval');
  var data = [
    ['Ewe','ID','Pen','Stage','Own FAMACHA (30%)','Deworm Events (20%)','Shed Score 1-5 (15%)','Lambing (15%)','Offspring FAMACHA (10%)','BCS (10%)','TOTAL','ACTION'],
    ['Azure','azure','Pen 3','1','','','','','','','',''],
    ['Baby Azure','baby-azure','Pen 3','1','','','','','','','',''],
    ['Bambii','bambii','Pen 3','1','','','','','','','',''],
    ['Charlies Ewe','charlies-ewe','Pen 3','1','','','','','','','',''],
    ['Ewe Tag 02','tag-02-ewe-p5','Pen 3','1','','','','','','','',''],
    ['FM','fm','Pen 3','1','','','','','','','',''],
    ['FM2','fm2-0051','Pen 3','1','','','','','','','',''],
    ['Fawn Wool Ewe (Pen 5)','fawn-wool-ewe-p5','Pen 3','1','','','','','','','',''],
    ['GG','gg','Pen 3','1','','','','','','','',''],
    ['Nuba','nuba-0053','Pen 3','1','','','','','','','',''],
    ['Wool Ewe 0044','tag-0044-wool-ewe','Pen 3','1','','','','','','','',''],
    ['Fawn Wool Ewe 114','tag-114-fawn-wool','Tree Fort','2','','','','','','','',''],
    ['Orange Tag 31 Ewe (Tree Fort)','tag-31-orange-tf','Tree Fort','2','','','','','','','',''],
    ['Serendipity','serendipity','Tree Fort','2','','','','','','','',''],
    ['0035 Baby Ewe','tag-0035-baby-ewe','Pen 4','3','','','','','','','',''],
    ['BHD Ewe G023','g023-bhd-ewe','Pen 4','3','','','','','','','',''],
    ['Bambiis Baby','bambii-baby','Pen 4','3','','','','','','','',''],
    ['Broken Tail Twin Ewe','broken-tail-twin-ewe','Pen 4','3','','','','','','','',''],
    ['Broken Tail Twin Ewe 2 (White)','broken-tail-twin-ewe-2','Pen 4','3','','','','','','','',''],
    ['Gigis 2026 Baby','gigi-2026-baby','Pen 4','3','','','','','','','',''],
    ['Little Daisy','little-daisy','Pen 4','3','','','','','','','',''],
    ['Small White Ewe (Pen 4)','sm-white-ewe-p4','Pen 4','3','','','','','','','',''],
    ['White Ewe 0035','tag-0035-white-ewe','Pen 4','3','','','','','','','',''],
    ['Charlies Farm Ewe Baby','charlies-farm-ewe-baby-p3','Pen 5','4','','','','','','','',''],
    ['Elsie Large White Ewe Triplet','elsie-triplet-lg-white-ewe','Pen 5','4','','','','','','','',''],
    ['Elsie Small White Ewe Triplet','elsie-triplet-sm-white-ewe','Pen 5','4','','','','','','','',''],
    ['Noris Baby (Pen 3)','nori-baby-p3','Pen 5','4','','','','','','','',''],
    ['Serendipity Black Ewe Twin','serendipity-twin-ewe','Pen 5','4','','','','','','','',''],
    ['Charlies Farm Ewe (Pen 3)','charlies-farm-ewe-p3','Pen 6','5','','','','','','','',''],
    ['OAV 2222','oav-2222','Pen 6','5','','','','','','','',''],
    ['Ewe Tag 31','tag-31-ewe-p5','Pen 1','6','','','','','','','',''],
    ['Hair Ewe 0033','tag-0033-hair-ewe','Pen 1','6','','','','','','','',''],
    ['Nori','nori','Pen 1','6','','','','','','','',''],
    ['Broken Tail','broken-tail','Pen 2','7','','','','','','','',''],
    ['Elsie','elsie','Pen 2','7','','','','','','','',''],
    ['Windlestone Fat Tail 0055','windlestone-0055','Goose Pen','outside','','','','','','','',''],
    ['Windlestone Fat Tail 0056','windlestone-0056','Goose Pen','outside','','','','','','','',''],
    ['Windlestone Fat Tail 2139','windlestone-2139','Goose Pen','outside','','','','','','','',''],
  ];
  sheet.getRange(1, 1, data.length, data[0].length).setValues(data);
  formatHeader(sheet, data[0].length);
  autoResize(sheet, data[0].length);
}

function updateDeceasedSold(ss) {
  var sheet = getOrCreateSheet(ss, 'Deceased & Sold');
  var data = [
    ['Name','ID','Tag','Sex','Status','Date','Breed','Sire','Dam','Notes'],
    ['Sir Loin','sir-loin','2','ram','deceased','2026-04-02','St Augustine/Katahdin','None','None','Flock spreadsheet: Tag 2, 75% St Augustine / 25% Katahdin. S'],
    ['Kelsier','kelsier','2223','ram','deceased','None','Katahdin','None','None','Most parasite resistant sheep in the flock. Deceased. Pure K'],
    ['Samson','samson','None','ram','deceased','None','Hampshire','None','None','Was ram for Pen 4 group (Elsie, Nori, Trouble, Bsoe, Bsoed, '],
    ['Sam','sam','None','ram','deceased','2026-04-02','Gulf Coast Native','None','None','Ram for pen 3 group. 100% Gulf Coast Native per Merrie breed'],
    ['Kaladin','kaladin','014','ram','deceased','2026-04-02','Cracker/St Augustine/Babydoll/Jacob/Katahdin','smore','serendipity','Living Kaladin tag 014. DOB 5/11/2023 per extension service.'],
    ['S\'More','smore','22','ram','deceased','None','Cracker','None','None','Flock spreadsheet: Tag 22, 100% Cracker, 200lbs. Sire: Gigan'],
    ['Well Done','well-done','8','ram','deceased','None','Katahdin','None','None','Flock spreadsheet: Tag 8, 100% Katahdin, 175lbs. Sire: Big D'],
    ['Butter Ball','butter-ball','None','ram','deceased','None','Dorper','None','None','Dorper ram. Deceased per weak resistance list.'],
    ['NoriSon','nori-son','054','ram','deceased','2026-04-02','','sir-loin','nori','Ram in pen 5 currently. Tag 54. Also was tag 22. Sir Loin so'],
    ['Charlie\'s Ram','charlies-ram','012','ram','deceased','2026-04-02','','None','None','Photos from March 18, 2024. Also called Mc11 or tag 12. Whit'],
    ['Pippin','pippin','015','ram','sold','None','Cracker/St Augustine/Katahdin','smore','bsoed','Pippin/BSOE1. Tag 015. S\'More (100%Cr) x BSOED (40.5K/59.5S'],
    ['New Black Belly Ram','new-black-belly-ram','018','ram','deceased','2026-04-02','American Blackbelly','None','None','New ABB ram from measurement list. Marked deceased April 202'],
    ['Charlie\'s Lamb','charlies-lamb-0017','0017','ram','deceased','2026-04-02','','charlies-ram','None','Charlie\'s ram\'s lamb. Tag 0017. Marked deceased April 2026'],
    ['Buck (Original)','buck-original','None','ram','deceased','None','Katahdin/Awassi/East Friesian','None','None','Original Buck ram in chicken coop. Came from Windlestone. 48'],
    ['Big Free Male','big-free-male','005','ram','deceased','2026-04-02','','None','None','Large free-roaming male from measurement list. Marked deceas'],
    ['Bella','bella','027','ewe','deceased','2026-04-02','','None','None','Tag 027 (from Heather Oaks Farm). 027 and 27 are different s'],
    ['Cinderella','cinderella','028','ewe','deceased','2026-04-02','','None','None','Tagged 28. Eyes good at tag day. In Pen 3. Marked deceased A'],
    ['Serendipity\'s Ram (2024)','serendipity-ram-2024','None','ram','deceased','2026-04-02','Hampshire/St Augustine/Babydoll/Jacob/Katahdin','samson','serendipity','Serendipity\'s 2024 ram lamb by Samson (100% Hampshire). Bre'],
    ['Serendipity\'s Baby','serendipitys-baby-036','036','ewe','deceased','2026-04-02','','kelsier','serendipity','036, Mc12. Serendipity\'s baby ewe. Sire: Kelsier (pen 4 ram'],
    ['Little Daisy\'s Baby (Mc01)','little-daisys-baby-mc01','None','ewe','deceased','2026-04-02','','None','little-daisy','Mc01. Called \'baby\'s baby\' in notebook. Little Daisy #35\'],
    ['Baby','baby','None','ewe','deceased','2026-04-02','Suffolk Cross','None','None','In pen 3 (Sam group). On weak resistance list. Google Sheet '],
    ['Baby Momma','baby-momma','None','ewe','deceased','2026-04-02','','None','None','In pen 3 (Sam group). Marked deceased April 2026 — not on no'],
    ['Zara','zara','025','ewe','deceased','None','Dorper','None','None','Tag 25. Zara = Dorper 25 (same animal). 100% Dorper. Decease'],
    ['Half Tail','half-tail','None','ewe','deceased','2026-04-02','St Augustine/Katahdin/BBB','sir-loin','hersheys','Flock spreadsheet: 12.5% BBB / 31.25% Katahdin / 56.25% St A'],
    ['Trouble','trouble','033','ewe','deceased','2026-04-02','Katahdin/St Augustine/Dorper','sir-loin','haylee-lawson','Flock spreadsheet: Tag 9/retagged 33, 25%Dorper/37.5%K/37.5%'],
    ['Bsoe','bsoe','032','ewe','deceased','2026-04-02','Katahdin/St Augustine','sir-loin','two-pence','Flock spreadsheet: 56%K/44%SA, 185lbs. DOB ~1/1/2019. Sir Lo'],
    ['Bsoed','bsoed','031','ewe','deceased','2026-04-02','St Augustine/Katahdin','sir-loin','bsoe','Flock spreadsheet: ~40.5%K/~59.5%SA, 175lbs. DOB 1/18/2020. '],
    ['FM1','fm1','009','ewe','deceased','2026-04-02','St Augustine/Cotswold/Tunis/Katahdin','sir-loin','fm','FM1 = Sir Loin × FM per FM breeding page. Tag 009. DOB 4/1/2'],
    ['Gertrude Moon','gertrude-moon','022','ewe','deceased','None','American Black Belly','gertrude-moon-sire','gertrude-moon-dam','Gertrude Moon aka Bitch Face (BF). Tag 22. 100%ABB. DOB ~202'],
    ['GM Twin 1 (2024)','gm-twin1-2024','None','unknown','deceased','None','ABB/St Augustine/Katahdin','sir-loin','gertrude-moon','Born 1-2-24. Sir Loin x Gertrude Moon. Not kept per owner.'],
    ['GM Twin 2 (2024)','gm-twin2-2024','None','unknown','deceased','None','ABB/St Augustine/Katahdin','sir-loin','gertrude-moon','Born 1-2-24. Sir Loin x Gertrude Moon. Not kept per owner.'],
    ['Circle Tail','circle-tail','None','ewe','deceased','2026-04-02','Cracker/St Augustine/Katahdin','smore','brown-knee','Flock spreadsheet: 50% Cracker / 21.875% Katahdin / 28.125% '],
    ['Fox Tail','fox-tail','017','ewe','deceased','None','Cracker/St Augustine/Katahdin/Dorper','smore','trouble','Tag 17. S\'More (100%Cr) x Trouble (37.5K/37.5SA/25Dorper). '],
    ['S1','s1','None','ewe','deceased','2026-04-02','','None','None','In pen 6 (no ram). Marked deceased April 2026 — not on noteb'],
    ['S2','s2','None','ewe','deceased','2026-04-02','','None','None','In pen 2 (sirloin group). Marked deceased April 2026 — not o'],
    ['Lara','lara','023','ewe','deceased','2026-04-02','Black Headed Dorper','lara-sire','lara-dam','Tag 23. 100% Black Headed Dorper per breeding page (previous'],
    ['Pebbles','pebbles','None','ewe','deceased','2026-04-02','','None','None','In pen 2 (sirloin group). FAMACHA 3, treated. Entry struck t'],
    ['Anna','anna','1','ewe','deceased','None','Katahdin','None','None','Flock spreadsheet: Tag 1, 100% Katahdin, 175lbs. DOB 1/12/20'],
    ['Boots','boots','7','ewe','culled','None','Dorper/Katahdin','None','None','Flock spreadsheet: Tag 7, 50% Dorper / 50% Katahdin, 130lbs.'],
    ['Patches','patches','27','ewe','deceased','2026-04-02','','None','None','Weight calculator: 65.6lbs (girth 27, length 27). Tag 27 — c'],
    ['Little Song','little-song','008','ewe','deceased','2026-04-02','St Augustine/Katahdin','sir-loin','annas-big-one','Flock spreadsheet: Tag 8/retagged 008, 43.75% Katahdin / 56.'],
    ['Black Rock','black-rock','010','ewe','deceased','2026-04-02','','None','None','Tag 010. From measurement list. No measurements recorded yet'],
    ['Question Tail','question-tail','001','ewe','deceased','2026-04-02','','None','None','Tag 001. From measurement list. Marked deceased April 2026 —'],
    ['Female 004','female-004','004','ewe','deceased','2026-04-02','','None','None','Tag 004. From measurement list. Marked deceased April 2026 —'],
    ['Half Tail\'s Baby','half-tails-baby','007','ewe','deceased','2026-04-02','','None','half-tail','Tag 007. Half Tail\'s baby. From measurement list. Marked de'],
    ['Sb1 (Crown)','sb1-crown','002','ewe','deceased','2026-04-02','','None','None','Tag 002. Called \'Sb1 (crown)\' in measurements. Weight calc'],
    ['Sb2 (All Black)','sb2-all-black','003','ewe','deceased','2026-04-02','','None','None','Tag 003. Called \'Sb2 (all black)\' in measurements. Weight '],
    ['New Big Girl 2','new-big-girl-2','None','ewe','deceased','2026-04-02','','None','None','In pen 3 (Sam group). Marked deceased April 2026 — not on no'],
    ['Daisy\'s Daughter 2','daisys-daughter-2','None','ewe','deceased','2026-04-02','St Augustine/Katahdin/BBB/Wiltshire','None','daisy','From Google Sheet Pen 5 and 6. In NoriSon\'s group. Differen'],
    ['Tag 31','tag-31-ewe','031-pen2','ewe','deceased','2026-04-02','Katahdin/St Augustine/Dorper/BBB','None','None','From Google Sheet Pen 2. 69.25% wool. Different from Bsoed t'],
    ['Tag 33','tag-33','033-pen1','ewe','deceased','2026-04-02','Katahdin/St Augustine/BBB/Cracker/White Dorper/Suffolk/GCN','None','None','From Google Sheet Pen 1. 3/4 hair. Has twins. Marked decease'],
    ['Bambi','bambi','037','ewe','deceased','2026-04-02','Katahdin/Dorper','None','None','Weight calculator: tag 35, 81.3lbs (girth 29, length 29). Go'],
    ['Irish','irish','None','ewe','deceased','2026-04-02','','None','little-daisy','Little Daisy\'s daughter. Needed parasite treatment April 13'],
    ['Unnamed (Pen 2)','unnamed-pen2','None','ewe','deceased','2026-04-02','','None','None','Unnamed ewe in pen 2 (sirloin group). Not the same as the de'],
    ['Fl51870-0502','fl51870-0502','Fl51870-0502','ewe','deceased','2026-04-02','Hampshire/Suffolk','None','None','Florida scrapie tag Fl51870-0502. 50%Hampshire/50%Suffolk. E'],
    ['FM\'s Lamb (2023)','fm-lamb-2023','None','ewe','deceased','2026-04-02','St Augustine/Cotswold/Tunis/Katahdin','sir-loin','fm','FM × Sir Loin lamb = FM1 (tag 009). Born 4/1/2023. Birth wei'],
    ['Ext Lamb 8 (ABG)','ext-lamb-8','None','ram','deceased','None','','None','None','Extension service lamb ID 8. Ram, born 1/24/2023 (type 3). E'],
    ['Shaggy','shaggy','None','ewe','deceased','None','Babydoll/Jacob','None','None','Flock spreadsheet: 50% Babydoll / 50% Jacob, Black, 140lbs. '],
    ['Skitters','skitters','None','ewe','deceased','None','Karakul','None','None','Deceased. 100% Karakul per Rocky breeding page. Also called '],
    ['W136','w136','None','ewe','deceased','None','','None','None','Deceased. On weak resistance list.'],
    ['Unnamed (Deceased)','unnamed-deceased','None','unknown','deceased','None','','None','None','Deceased. On weak resistance list as \'Unnamed (deceased)\'.'],
    ['Hersheys','hersheys','3','ewe','deceased','None','BBB/Katahdin/St Augustine','sir-loin','sugar','Flock spreadsheet: Tag 3, 25% BBB / 37.5% Katahdin / 37.5% S'],
    ['GG\'s Daughter','gg-daughter-45','045','ewe','deceased','None','','gg','None','GG\'s daughter (GG is sire). Tag 45. Deceased.'],
    ['Lara\'s Daughter','lara-daughter-46','046','ewe','sold','None','','gg','lara','GG (sire) x Lara (dam) daughter. Tag 46. Sold because prone '],
    ['GG\'s Son','gg-son-094','094','ram','deceased','None','','gg','None','GG\'s son. Tag 094. Deceased.'],
    ['430-2079','tag-430-2079','430-2079','ewe','deceased','2023-08-21','Suffolk/Hampshire','None','None','Tag 430-2079 (pen 5). 25%Hampshire/75%Suffolk. Ewe weight 33'],
    ['Kelsier\'s Sister','kelsiers-sister','2241','ewe','deceased','None','Katahdin','None','None','Kelsier\'s sister. Tag 2241. 100% Katahdin. Weight 150lbs. B'],
    ['Dorper Ram (Deceased)','dorper-ram-deceased','None','ram','deceased','None','Dorper','None','None','Dorper ram from sick sheep note. Given iron and B on 10-24. '],
    ['Tag 240002','tag-240002','240002','unknown','sold','2026-02-15','','None','None','Sold 2026-02-15.'],
    ['Tag 0049','tag-0049','0049','unknown','sold','2026-02-15','','None','None','Sold 2026-02-15.'],
    ['Tag 240001','tag-240001','240001','unknown','sold','2026-02-15','','None','None','Sold 2026-02-15.'],
    ['Mc06','mc06','None','unknown','sold','2026-02-15','','None','None','Sold 2026-02-15. MC tag Mc06.'],
    ['Tag 0050','tag-0050','0050','unknown','sold','2026-02-15','','None','None','Sold 2026-02-15. Possibly one of the goose pen auction lambs'],
    ['Razzle','razzle','5','ram','deceased','None','Barbados Blackbelly','None','None','Flock spreadsheet: Tag 5, 100% BBB ram, Badger color, 125lbs'],
    ['Frazzle','frazzle','6','ewe','deceased','None','Katahdin','None','None','Flock spreadsheet: Tag 6, 100% Katahdin ewe, Black, 175lbs. '],
    ['Almond Joy','almond-joy','None','ram','deceased','None','','None','None','From Sheep Breeding DB. Ram culled (C) for being cryptorchid'],
    ['Sugar','sugar','4','ewe','deceased','None','BBB/Katahdin','razzle','frazzle','Flock spreadsheet: Tag 4, 50% BBB / 50% Katahdin, Tan, 224lb'],
    ['Penny','penny','None','ewe','deceased','None','','None','None','From Sheep Breeding DB. Ewe culled (C) for poor shedding.'],
    ['Two Pence','two-pence','None','ewe','deceased','None','Katahdin/St Augustine','None','None','From Sheep Breeding DB. Ewe culled as daughter of cryptorchi'],
    ['Haylee Lawson','haylee-lawson','14','ewe','deceased','None','Dorper/Katahdin','None','None','Flock spreadsheet: Tag 14, 50% Dorper / 50% Katahdin, White,'],
    ['Pretzel','pretzel','13','ewe','deceased','None','Dorper/Katahdin','None','None','Flock spreadsheet: Tag 13, 75% Dorper / 25% Katahdin, Black/'],
    ['W140','w140','None','ewe','deceased','2026-04-02','','None','None','On weak resistance list. Status alive but weak. Marked decea'],
    ['Anna\'s Big One','annas-big-one','None','ewe','deceased','2026-04-02','Katahdin/St Augustine','sir-loin','anna','Flock spreadsheet: 62.5% Katahdin / 37.5% St Augustine, 200l'],
    ['Dorpy','dorpy','None','ewe','deceased','2026-04-02','Katahdin/Dorper/Babydoll','None','None','From Google Sheet Pen 4. Tag 34 offspring row. Marked deceas'],
    ['Tag 34 (Pen 4)','tag-34-pen4','None','ewe','deceased','2026-04-02','Katahdin/St Augustine','None','None','From Google Sheet Pen 4. 100% hair. Marked deceased April 20'],
    ['Dodge','dodge','None','ram','sold','','Sir Loin x Broken Tail offspring','sir-loin','broken-tail','Sold off farm. Buyers named him Dodge. Sire of Little Daisy.'],
    ['Daisy','daisy','None','ewe','sold','','Sir Loin x Anna offspring','sir-loin','anna','Sold off farm. Buyers named her Daisy. Dam of Little Daisy.'],
    ['Elsie Black Ram Triplet','elsie-triplet-black-ram','None','ram','gifted','2026-03-15','','eclipse','elsie','Born 1-6-26. Elsies triplet. Black ram. Sire: Eclipse. Gifte'],
    ['Goose Pen 09','goose-09','09','ram','sold','2026-02-15','','','','Sold at auction 2-15-26. ~00.'],
    ['Goose Pen 50','goose-50','50','ewe','sold','2026-02-15','','','','Wooly Tan. Sold at auction 2-15-26. ~00.'],
    ['Goose Pen 06','goose-06','06','ram','sold','2026-02-15','','','','White Hair/Tan. Sold at auction 2-15-26. ~00.'],
    ['Goose Pen L19','goose-l19','L19','ewe','sold','2026-02-15','','','','Black, sheared. Sold at auction 2-15-26. ~00.'],
  ];
  sheet.getRange(1, 1, data.length, data[0].length).setValues(data);
  formatHeader(sheet, data[0].length);
  autoResize(sheet, data[0].length);
}
