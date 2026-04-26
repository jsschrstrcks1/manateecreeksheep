# Sheep Visual Identification Guide

**Purpose:** Let a future Claude (or human) look at a photograph and match each animal to its record in `data/flock_database.json`.

**How to use this:**
1. Note the pen context — photo location usually limits the candidate set to that pen's roster.
2. Eliminate by obvious phenotype: coat type (hair vs. wool), face color, body color, adult vs. lamb.
3. Narrow with distinguishing marks: tag numbers/colors, tail shape, scars, horn status, pedigree tells.
4. Cross-check with `pens.<pen_id>.ewes/ram/lambs` in the database.
5. Record confidence. If you cannot distinguish two animals by phenotype alone, say so — do not guess.

**Conventions:**
- **Coat type** is the single strongest filter. Hair breeds (Katahdin, Dorper, BBB, St Croix, St Augustine, Wiltshire Horn) shed naturally and look slick. Wool breeds (Hampshire, Suffolk, Cotswold, Tunis, Babydoll, Awassi) carry a thick fleece that needs shearing.
- **Face color** separates Hampshire/Suffolk descendants (black faces) from the rest.
- **Tag colors** in this flock: yellow MC-## tags are standard; green tags are separate; paper/metal no-color tags predate the MC series.
- When phenotype descriptions here conflict with a live photo, trust the photo and file an update — owner conversations have revised records before.

---

## Pen 3 — Charlie's breeding group (8 animals as of 2026-04-26)

Pen 3 is Charlie's hair-sheep breeding group. **No wool in this pen** (notebook 2026-02-20). Two rams co-resident — Charlie (MC-20, dominant, horned) and Merrie (00016, secondary, the largest animal in the pen per owner 2026-04-26). Three lactating adult ewes (Charlies Farm Ewe, Broken Tail, Nori) plus 3 surviving lambs after MC-2601's death.

**CORRECTED 2026-04-26 from prior CLAUDE.md state:** Pen 3 ram was listed as "Sam" — Sam died in Hurricane Helene (2024-09-26). His DB record carried a stale `status_date: 2026-04-02` bulk-cleanup placeholder, now corrected to the actual death date.

**CORRECTED 2026-04-26:** White twin lamb MC-2601 (`broken-tail-twin-ewe-2`) died 2026-04-22 from parasites. Was previously `status: alive` with stale `status_date: 2026-04-06` (bulk pattern). Roster reduced from 9 to 8.

### Adults (5)

#### `charlie-ram` — "Charlie"
- **Tag:** MC-20 (yellow)
- **Sex:** ram, adult
- **Breed:** 50% Katahdin / 25% BHD / 12.5% ABB / 12.5% Wiltshire Horn — **100% hair**
- **Phenotype:** White hair coat with **black spots**, **BLACK HORNS**. 108.2 lb (recorded 2026-02-28).
- **How to tell from `charlies-farm-ewe-p3`:** Same breed comp + similar piebald pattern, but Charlie has **black horns** and is male (no udder). She is polled and lactating.
- **How to tell from Merrie:** Charlie is white-with-black-spots and **HORNED**; Merrie is brown-and-tan and is the **larger** animal in the pen.
- **Health:** Jaw abscess lanced 2026-02-27, treated 4.5 mL Nuflor 2026-02-28.
- **Likely sired:** all 2026 Pen 3 lambs (Merrie possible alternate).

#### `merrie` — "Merrieweather" / "Merrie"
- **Tag:** 00016
- **Sex:** ram, adult (DOB 2023-01-14)
- **Sire/Dam:** S'More × Half Tail
- **Breed:** 50% Cracker / 28.1% St Augustine / 12.5% Katahdin / 6.3% BBB / 3.1% White Dorper — **~50% hair / 50% wool composite** (visually reads more hair due to Cracker dominance)
- **Phenotype:** **Brown and tan**. **OWNER-CONFIRMED 2026-04-26: BIGGEST animal in Pen 3** — has surpassed Broken Tail (DB 225 lb).
- **Flag:** DB weight calculator value of ~99.2 lb is from a 2023 birth-weight projection and is **STALE**. Needs a real weigh-in. Owner testimony supersedes the calc.
- **How to tell from Charlie:** Brown-and-tan vs. white-with-black-spots; larger frame; no prominent black horns.
- **How to tell from Broken Tail:** Different sex (ram vs ewe), different color (brown-tan vs white).

#### `broken-tail` — "Broken Tail" / "BT" / "Iron Lady"
- **Tag:** MC-15 (yellow); `secondary_tags: ["0029"]` is **suspect** — see anomaly note below
- **Sex:** ewe, adult (DOB 2018-01-18)
- **Sire/Dam:** Sir Loin × Half Tail
- **Breed:** 65.6% St Augustine / 28.1% Katahdin / 6.3% BBB — **100% hair**
- **Phenotype:** Solid **white** hair coat, large adult ewe. DB weight 225 lb. In evening light her body reads cream-toned (the same lighting effect noted on Lara in Pen 4).
- **Lambs this season:** twin ewes MC-2605 (brown, alive) and MC-2601 (white, **deceased 2026-04-22 parasites**).
- **How to tell from Merrie (also large):** Different sex; Broken Tail is solid white hair, Merrie is brown-and-tan.
- **How to tell from `charlies-farm-ewe-p3`:** Both lactating hair ewes, but BT is **solid white**, CFE is **multi-color piebald** with dark patches.
- **Notes:** Important pedigree dam — mother of Dodge, MC08, samson-daughter-p4, BT1, BT2.

#### `charlies-farm-ewe-p3` — "Charlies Farm Ewe" / "White Belly Ewe"
- **Tag:** MC-16 (yellow)
- **Sex:** ewe, adult
- **Breed:** 50% Katahdin / 25% BHD / 12.5% ABB / 12.5% WH — **100% hair** (same comp as Charlie)
- **Phenotype:** Multi-color piebald hair coat — white body with **dark patches on neck/shoulders**, white belly. Polled. Lactating (raising MC-2602).
- **Proximity tell:** lamb MC-2602 nearby — but the lamb is on the LEFT of the hay cage while the dam was photographed mid-right; they don't always cluster.
- **How to tell from Charlie:** **No horns** + visible **hanging udder**. Charlie is horned and male.
- **Pedigree note:** Nori-line descendant; "Charlies sheep" history — BHD × Nori line.

#### `nori` — "Nori"
- **Tag:** 0029
- **Sex:** ewe, adult (DOB 2023-02-01)
- **Breed:** 50% American Blackbelly / 50% Wiltshire Horn — **100% hair**
- **Phenotype:** **Badger pattern** — red/brown body with darker face and legs (classic ABB × WH cross). ~138 lb.
- **Physical distinguisher:** **Knot under chin** (per pen-3 notebook).
- **How to tell from Broken Tail:** Nori is badger-patterned (dark face, red body); BT is solid white. Different breed lines entirely.
- **How to tell from `charlies-farm-ewe-p3`:** Nori is badger-red overall; CFE is white-with-black-patches.
- **This-season lamb:** MC-2604 (ram, mottled brown/white).
- **Confusable with brown lambs at distance** but is much larger (adult).

### Lambs (3 surviving — fourth deceased 2026-04-22)

#### `charlies-farm-ewe-baby-p3` — "Charlies Farm Ewe Baby"
- **Tag:** MC-2602 (green)
- **Sex:** ewe lamb, DOB 2025-12-06 (~4.7 mo as of 2026-04-26 — **largest lamb in Pen 3**)
- **Dam:** Charlies Farm Ewe (sire most likely Charlie, possibly Merrie)
- **Phenotype:** **Big brown** ewe lamb. **White tip on tail**, **2 white socks** (rear legs), **white on crown**, **front legs ALL BROWN** (no socks). Polled.
- **How to tell from MC-2605 (BT brown twin):** MC-2602 is bigger (older + heavier), front legs are all brown. MC-2605 is smaller and the brown/white is more evenly mottled.
- **How to tell from MC-2604 (Nori's ram):** MC-2602 is ewe with brown front legs and rear white socks; MC-2604 is ram with white blaze, white-tipped ears, full white tail.

#### `broken-tail-twin-ewe` — "Broken Tail Twin Ewe (brown)"
- **Tag:** MC-2605 (green)
- **Sex:** ewe lamb, DOB 2025-12-31 (~3.8 mo)
- **Dam:** Broken Tail (sire most likely Charlie)
- **Phenotype:** Brown & white hair-coat ewe lamb. Polled.
- **Surviving twin** — sister MC-2601 deceased 2026-04-22.
- **How to tell from MC-2602:** smaller and more evenly brown-and-white mixed; not the largest brown lamb.

#### `nori-baby-p3` — "Nori's Baby Ram"
- **Tag:** MC-2604 (green)
- **Sex:** ram lamb, DOB 2026-01-10 (~3.5 mo)
- **Dam:** Nori (sire most likely Charlie)
- **Phenotype:** Brown-and-white **mottled** ram lamb. **White on top of ears**, **white blaze on face**, **full white tail**. Polled.
- **Proximity tell:** stays beside Nori on the right side of the pen.
- **How to tell from MC-2605:** different sex (ram vs ewe), different dam, white blaze + white-tipped ears + white tail.

### Deceased (1)

#### `broken-tail-twin-ewe-2` — "Broken Tail Twin Ewe (white)" — **deceased 2026-04-22, parasites**
- **Tag:** MC-2601
- **Sex:** ewe lamb, DOB 2025-12-31
- **Dam:** Broken Tail
- **Phenotype:** Solid **white** hair-coat ewe lamb.
- **Last known photo while alive:** the pre-2026-04-22 Pen 3 photo (provided 2026-04-26) — foreground center, small white lamb tucked behind her dam Broken Tail.
- **CORRECTED 2026-04-26:** prior status was `alive` with stale `status_date: 2026-04-06` (bulk-cleanup pattern). Real death date 2026-04-22, cause parasites.

---

## Pen 3 — Quick-Reference Decision Tree

```
Is it an adult? (>9 months — and Pen 3 is HAIR ONLY)
├── Ram
│   ├── White-with-black-spots, BLACK HORNS, 108 lb .................. charlie-ram (MC-20)
│   └── Brown-and-tan, biggest animal in pen, no prominent horns ..... merrie (00016)
└── Ewe (all lactating spring 2026)
    ├── Solid WHITE, large frame .................................... broken-tail (MC-15)
    ├── Multi-color piebald, white belly, dark neck patches .......... charlies-farm-ewe-p3 (MC-16)
    └── BADGER pattern (red body, dark face/legs), knot under chin ... nori (0029)

Is it a lamb? (<6 months — all polled, all hair)
├── Ewe
│   ├── BIGGEST brown lamb, white tail tip + 2 white socks + brown front legs . charlies-farm-ewe-baby-p3 (MC-2602)
│   └── Smaller brown-and-white mixed ......................................... broken-tail-twin-ewe (MC-2605)
└── Ram
    └── Mottled brown/white, white blaze + white-tipped ears + white tail ...... nori-baby-p3 (MC-2604)
```

**Single best tell per animal:**
- charlie-ram = black horns
- merrie = biggest in pen + brown-and-tan
- broken-tail = solid white adult
- charlies-farm-ewe-p3 = white-with-dark-patches lactating ewe
- nori = badger pattern + knot under chin
- MC-2602 = biggest lamb, brown front legs
- MC-2605 = smaller brown-white twin (the surviving one)
- MC-2604 = white blaze + white tail (the only ram lamb)

---

## Known visual confusion cases (Pen 3)

| Confusable pair | Tell them apart |
|---|---|
| `charlie-ram` vs. `charlies-farm-ewe-p3` | Same breed comp, similar piebald look. **Charlie has BLACK HORNS and is male; she is polled with a hanging udder.** |
| `merrie` vs. `broken-tail` (both large) | Different sex (ram vs ewe), different color (brown-tan vs solid white). Merrie is now the LARGEST animal in the pen per owner 2026-04-26. |
| `broken-tail` vs. `charlies-farm-ewe-p3` | Both lactating hair ewes. **BT is solid white**; CFE is **multi-color piebald** with dark neck patches. |
| `nori` vs. brown lambs at distance | Nori is much **larger** (adult ~138 lb) and has a darker badger face / dark legs. Lambs are smaller and lighter-faced. |
| `charlies-farm-ewe-baby-p3` (MC-2602) vs. `broken-tail-twin-ewe` (MC-2605) | MC-2602 is the **biggest** brown lamb (born 12-6-25, ~5 mo) with **front legs all brown** + 2 rear white socks. MC-2605 is smaller (born 12-31-25, ~4 mo) with more evenly mixed brown/white. |
| `nori-baby-p3` (MC-2604) vs. either brown ewe lamb | MC-2604 is the only **ram** lamb in the pen and has a distinctive **white blaze + white-tipped ears + full white tail**. The two ewe lambs are MC-2602 and MC-2605. |
| `broken-tail` vs. `broken-tail-twin-ewe-2` (when MC-2601 was alive) | Same color (white) but adult-vs-lamb size. Now moot — MC-2601 deceased 2026-04-22. |
| Photo-misread: animal in hay cage = Charlie, NOT Nori | Owner correction 2026-04-26 to Claude's first-pass guess: the dark-faced/spotted animal at the hay cage is **Charlie** (white body + black spots + black horns reads dark at distance). Nori is on the RIGHT side of the image, lying down with head up-right. |

---

## Provenance (Pen 3)

- **Built:** 2026-04-26 from a single Pen 3 photo provided by owner that day. Photo was taken **before 2026-04-22** (white twin MC-2601 is visible alive in it; she died 2026-04-22).
- **Owner-confirmed identifications (single photo, 2026-04-26 verbal):**
  - **Foreground left, large lying ewe (cream in evening light)** = `broken-tail`.
  - **Small white lamb tucked behind her** = `broken-tail-twin-ewe-2` (MC-2601). *Last known photo while alive — died 2026-04-22 parasites.*
  - **Mid-right standing piebald ewe with hanging udder** = `charlies-farm-ewe-p3` (MC-16).
  - **Brown lamb LEFT of the hay cage** = `charlies-farm-ewe-baby-p3` (MC-2602). *(Claude's first guess put her near her dam on the right — owner correction: she's on the LEFT.)*
  - **At the hay cage** = `charlie-ram` (MC-20). *(Claude's first guess was Nori; owner correction: that's Charlie. Nori is elsewhere.)*
  - **LEFT side of the hay cage, biggest animal in pen** = `merrie` (00016).
  - **Right side of image, lying head up-right** = `nori` (0029).
  - **Parallel to Nori, only head visible above her hindquarters** = `nori-baby-p3` (MC-2604).
  - **Just to the right of the hay cage** = `broken-tail-twin-ewe` (MC-2605).
- **DB corrections committed in this pass (2026-04-26):**
  - `broken-tail-twin-ewe-2`: `status: alive → deceased`, `status_date: 2026-04-06 → 2026-04-22`, added `cause_of_death: parasites`. Removed from `pens.pen_3.lambs`. **CORRECTED from prior bulk-cleanup status_date.**
  - `sam`: `status_date: 2026-04-02 → 2024-09-26`, added `cause_of_death: Hurricane Helene`. **CORRECTED from prior bulk-cleanup status_date** (owner 2026-04-26: Sam died in Helene, never in pen 3 since).
  - `pens.pen_3.notes`: appended MC-2601 death note; surviving-lamb count noted.
  - `CLAUDE.md` Pen Structure table: Pen 3 row updated — Sam removed, Charlie + Merrie + actual current roster shown.
  - `visual_id` blocks added to all 9 Pen 3 sheep records.
- **DB anomalies surfaced but NOT modified in this pass (deferred to index-card review):**
  - **Tag `0029` conflict:** `nori.tag = "0029"` AND `broken-tail.secondary_tags: ["0029"]`. Pen-3 notebook says Nori is 0029. Broken Tail's `0029` secondary entry looks stale. Owner 2026-04-26: "I don't know what the current tags are for either BT or Nori, but the index card photos should have that data." → flagged for resolution against `IMG_0660`-series notebook cards.
  - **`merrie` weight ~99 lb (2023 calc) is stale** — owner confirms he is now the largest animal in Pen 3. Needs a real weigh-in; weight number left untouched.
  - **DOB missing** on `charlie-ram` and `charlies-farm-ewe-p3`. Lower priority — leave for next notebook-card pass.
- **Photo gaps / not yet imaged from other angles:** The single photo is wide and partially occluded by the round hay cage. A close-up of Charlie's horns + a clean side profile of Merrie would lock the rams' phenotype permanently. Suggested for next session.
- **Lighting note (consistent with Pen 4 finding):** Evening/golden-hour light makes white animals (Broken Tail) read as cream-toned. Same effect that misled the Pen 4 picture-2 ID of Lara. Prefer midday light for color truth.

---



Pen 4 is the weak-resistance watch pen. All 2026 lambs sired by Kelsier (100% Katahdin). Ram of the adult breeding group is Gigi's 2025 son.

### Adults (8)

#### `gigi-2025-ram` — "Gigi's 2025 Ram"
- **Tag:** MC-09 (yellow)
- **Sex:** ram (yearling, ~15 mo as of Apr 2026)
- **Sire/Dam:** Kelsier × Gigi (GG)
- **Phenotype:** **"Looks like Gigi but smaller"** (owner, 2026-04-24). Hampshire/Suffolk phenotype — black face, white/cream wool body. Same visual type as his dam, just a scaled-down version. Despite 50% Katahdin (hair) from sire Kelsier, his dam's H/S wool dominates the coat.
- **How to tell from GG:** **size is the main tell — he is a smaller version of GG.** GG is the biggest black-faced animal in the pen; he's a smaller copy. Also: GG is losing condition (Apr 2026) while MC-09 is in good condition; tag MC-09 vs GG's MC-19.
- **How to tell from samson-daughter-p4:** He mirrors GG's look (H/S cross). Samson daughter is a different cross (100% Hampshire × hair-breed dam) — different frame/coat mix.
- **Health:** FAMACHA consistently 1–2. Watch whether he inherited Kelsier's parasite resistance or Gigi's weakness.

#### `gg` — "Gigi" / "GG"
- **Tag:** MC-19 (yellow)
- **Sex:** ewe, adult
- **Breed:** 50% Hampshire / 50% Suffolk — **100% wool**
- **Phenotype:** Classic Hampshire/Suffolk — **solid black face**, white wool body. Family favorite.
- **Body size:** **Largest of the black-faced Hampshire-type animals in Pen 4** — noticeably bigger frame than Gigi's 2025 Ram or samson-daughter-p4.
- **Condition tell (2026-04-24):** **Starting to lose condition** — nursing a huge lamb (Gigi's 2026 Baby, MC-2613, who is close to adult size at ~3.5 months) on top of three parasite emergencies. Expect hip/spine visibility, less "rounded" wool profile.
- **Proximity tell:** **Usually near her large multi-color lamb** (MC-2613). If you see a huge near-adult-size lamb in pen 4, the big worn-looking black-faced ewe beside her is GG.
- **Distinctive:** Three FAMACHA-5 emergencies (2-20, 2-27, 4-10 2026) — severe weak-resistance confirmed.
- **How to tell from her son (MC-09):** GG is **larger** + body condition visibly poorer; MC-19 tag vs MC-09; mature ewe frame vs yearling ram build.
- **Full brother:** Azure (same parents, Mom's "Amure").

#### `lara` — "Lara" / "BHD Ewe G023" / "Dorper 23"
- **Tag:** 023 (primary) — secondary green tag **G023**
- **Sex:** ewe, adult (DOB ~2018)
- **Breed:** 100% Black Headed Dorper — **100% hair**
- **Phenotype:** **Solid black head**, **white hair body** (slick, no fleece). **Golden-hour lighting makes her white body look tan/brown** — this caused a misID in pen-4 picture 2 (2026-04-24) where she appeared dark in evening sun.
- **Offspring on record:** Oliver & Spicy (twins by Sir Loin, DOB 12-30-23).
- **How to distinguish from GG:** both have black heads + white bodies, but **Lara = hair** (smooth, short) and **GG = wool** (thick fleece). Lara is typically leaner.
- **How to distinguish from Serendipity in low-light photos:** Both can look dark-faced in evening sun. **Lara has a hair coat** (slick); **Serendipity has a mixed hair+wool patchy coat** and is smaller.
- **Health:** On weak resistance list. FAMACHA borderline Feb 2026, recovered with VB. "Condition bad" 4-10-26 — Florida Dorper struggling.
- **Prior DB error (fixed 2026-04-24):** Lara was duplicated as `g023-bhd-ewe` (a newer record built from 2026 notebook cards after she got the G023 green tag). The original `lara` record was wrongly bulk-marked deceased 2026-04-02. Records merged; `g023-bhd-ewe` removed.

#### `fm` — "FM"
- **Tag:** 0011 (older tag style) / secondary GA1568-011
- **Sex:** ewe, adult (DOB 2021-02-14, ~5 yr)
- **Breed:** 50% Cotswold / 50% Tunis — **100% wool**
- **Phenotype (CORRECTED 2026-04-24):** **LIGHT CREAM / PALE WOOL body** — heavy uniform Cotswold/Tunis fleece, large-framed (~200 lb). The name "Tunis Red" refers to heritage, NOT her adult color. Tunis lambs are red but fade to cream. Any reddish tint, if any, is confined to face/legs — her body wool reads cream/pale.
- **How to tell from Serendipity (the actual dark-brown pen-4 ewe):** FM is **light cream**, Serendipity is **dark brown/near-black**. Opposite color spectrum. If you see a pale cream wool mountain, it's FM. If you see a dark patchy small ewe, it's Serendipity.
- **How to tell from FM2 (her daughter):** FM is **larger** and a slightly cleaner cream. FM2 is smaller with a **metallic gray sheen** in her cream.
- **Notes:** No babies this season. Confident good eyes.

#### `fm2-0051` — "FM2"
- **Tag:** 0051 (older tag style)
- **Sex:** ewe, adult
- **Sire/Dam:** Sir Loin × FM
- **Breed:** 25% Cotswold / 25% Tunis / 37.5% St Augustine / 12.5% Katahdin — **~50% wool / 50% hair** (but visually reads wool)
- **Phenotype:** *"Fat and gray. Metallic sheen cream coat, extra wooly"* — described explicitly in DB. Smaller version of FM but cream/gray not red.
- **How to tell from FM:** FM2 is smaller, coat is **cream/metallic-gray** not red, more wooly-looking.
- **This-season lamb:** FM2 Ram Lamb (MC2614).

#### `sm-white-ewe-p4` — "Small White Ewe (Pen 4)"
- **Tag:** MC189 (yellow)
- **Sex:** ewe, adult (but small — often mistaken for lamb)
- **Sire/Dam:** Dodge × Daisy (same parents as Little Daisy — they're sisters)
- **Breed:** 67.96% St Augustine / 27.33% Katahdin / 4.69% BBB — **100% hair**
- **Phenotype:** Small white **hair-coat** ewe. Slick, no fleece.
- **How to tell from wool lambs:** she's small like a lamb but her coat is smooth hair, and she has an MC-189 tag (lambs usually don't yet).
- **Sister:** Little Daisy (different pen).

#### `serendipity` — "Serendipity"
- **Tag:** MC157 (yellow), legacy tag 30
- **Sex:** ewe, adult (DOB 2022-03-25, ~4 yr)
- **Sire/Dam:** Sir Loin × Shaggy
- **Breed:** 37.5% St Augustine / 25% Babydoll / 25% Jacob / 12.5% Katahdin — **~50% hair / 50% wool**
- **Phenotype:** **Dark** mixed coat from Jacob (piebald/dark) + Babydoll (can be dark brown/black) heritage. Often appears near-black in certain lights. Owner ID'd her as "far left, dark" in 2026-04-24 pen-4 photos.
- **How to tell from other dark sheep:** Jacob heritage can produce patchy/piebald; thickly wooled dark coat; yellow MC-157 tag.
- **This-season lambs:** twins MC2606 (white ram) + MC2607 (black ewe).
- **Health:** Borderline FAMACHA 3s in Feb, recovered.

#### `samson-daughter-p4` — "Samson Daughter (Pen 4)" — **NEW record, added 2026-04-24**
- **Tag:** none recorded yet
- **Sex:** ewe, adult
- **Sire/Dam:** Samson × Broken Tail (owner-confirmed 2026-04-24; medium confidence — no notebook card yet)
- **Breed:** 50% Hampshire / 32.8% SA / 14.1% K / 3.1% BBB — **50% wool / 50% hair** (reads wool)
- **Phenotype (CORRECTED 2026-04-24 from photo):** **WHITE face** (not Hampshire black — face color did NOT inherit from Samson), **pointed nose**, **cream wool body**. Looks like her brother MC08 but with a more pointed nose and whiter face.
- **How to tell from her brother MC08:** Samson daughter has a **more pointed nose** and a **whiter face** than MC08. MC08 has a rounded muzzle and slightly cream-tinted face.
- **How to tell from GG / MC-09:** Different face color entirely — Samson daughter is **white-faced**, GG and MC-09 are **black-faced**. Face color alone separates them. The earlier guidance grouping her with the "black-faced pen-4 animals" was wrong.
- **Full sibling:** `mc08-ram` (Pen 6).
- **Flag:** Needs tag, notebook card, FAMACHA baseline at next handling. Smaller than adult ewes like GG — often appears "barely visible" in group photos.

### Lambs (4) — all sired by Kelsier (100% Katahdin, NSIP)

#### `gigi-2026-baby` — "Gigi's 2026 Baby"
- **Tag:** MC-2613
- **Sex:** ewe lamb, DOB 2026-01-10
- **Dam:** GG (Gigi)
- **Phenotype:** **Multi-color ewe** — record notes "multi color". Mixed from Hampshire/Suffolk dam + Katahdin sire.
- **Health:** FAMACHA trending medium 4-10-26 — may inherit dam's parasite susceptibility. Watch.

#### `serendipity-twin-ram` — "Serendipity White Ram Twin"
- **Tag:** MC2606
- **Sex:** ram lamb, DOB 2025-12-30
- **Dam:** Serendipity
- **Phenotype:** **White ram lamb**, twin to black ewe MC2607.
- **Health:** FAMACHA-5 emergency 4-10-26 (second time); weak resistance confirmed despite Kelsier sire.

#### `serendipity-twin-ewe` — "Serendipity Black Ewe Twin"
- **Tag:** MC2607
- **Sex:** ewe lamb, DOB 2025-12-30
- **Dam:** Serendipity
- **Phenotype:** **Black ewe lamb** (the dark small one in pen-4 photos). Twin to MC2606 white ram.
- **Health:** FAMACHA-5 at 6 weeks (2-12-26) and again 4-10-26 — severe weak resistance. Heavily treated.

#### `fm2-ram-lamb` — "FM2 Ram Lamb"
- **Tag:** MC2614
- **Sex:** ram lamb, DOB 2026-01-31
- **Dam:** FM2
- **Phenotype:** Young ram lamb from FM2. Expect cream/light coloring like dam.
- **Health:** FAMACHA consistently 1-2.

---

## Pen 4 — Quick-Reference Decision Tree

```
Is it an adult? (>9 months)
├── Hair coat (slick, no fleece)
│   ├── Black head, white body, medium frame ...... g023-bhd-ewe (G023)
│   └── Small white, MC189 tag .................... sm-white-ewe-p4
├── Wool coat (thick fleece)
│   ├── Black face, white wool body (Hampshire/Suffolk cross)
│   │   ├── Larger mature ewe, poor condition, MC-19 ..... gg (Gigi)
│   │   └── Yearling ram, "looks like Gigi smaller", MC-09 gigi-2025-ram
│   ├── White face, cream wool body (Samson × Broken Tail)
│   │   └── Pointed nose, no tag ........................ samson-daughter-p4 (NEW)
│   ├── Large, light CREAM uniform fleece, ~200 lb, tag 0011 . fm
│   ├── Smaller cream w/ metallic gray sheen, tag 0051 ....... fm2-0051
│   └── Small, DARK brown/near-black mixed coat, MC157 ....... serendipity
└── Lamb (<9 months)
    ├── Multi-color ewe, MC-2613 .................. gigi-2026-baby
    ├── White ram, MC2606 ......................... serendipity-twin-ram
    ├── Black ewe, MC2607 ......................... serendipity-twin-ewe
    └── Cream/light ram, MC2614 ................... fm2-ram-lamb
```

---

## Known visual confusion cases (Pen 4)

| Confusable pair | Tell them apart |
|---|---|
| GG vs. Gigi's 2025 Ram (MC-09) | Both Hampshire/Suffolk phenotype (black face, white wool). **GG is the largest black-faced animal in pen 4** and as of Apr 2026 is visibly losing condition from nursing MC-2613 + parasite load. MC-09 is "Gigi smaller" — yearling ram, leaner, better condition. Tags MC-19 vs MC-09. |
| samson-daughter-p4 vs. MC08 (her brother, Pen 6) | Both cream-wool, **white-faced** (not black). Samson daughter has a **more pointed nose** and **whiter face**. MC08 has a rounder muzzle, slightly cream-tinted face. MC08 has a yellow MC08 tag; sister has no tag yet. |
| samson-daughter-p4 vs. GG/MC-09 | **Face color separates them** — Samson daughter is WHITE-faced, GG and MC-09 are BLACK-faced. Earlier grouping as "three black-faced pen-4 animals" was wrong — owner correction 2026-04-24. |
| GG's lamb (MC-2613) vs. other pen-4 lambs | MC-2613 is **unusually large for 3.5 mo** — close to adult size. If a "lamb" looks near-grown, it's her. Other lambs (MC2606/2607/2614) are normal size. |
| GG vs. G023 (BHD) | Both black head + white body. GG = **wool**, G023 = **hair** — biggest tell. G023 leaner. |
| FM vs. FM2 | Mother/daughter. Both cream wool. **FM = larger (~200 lb), cleaner light cream.** **FM2 = smaller, metallic gray sheen in cream.** |
| **FM vs. Serendipity** | **Do NOT confuse — opposite colors.** FM = LARGE, LIGHT CREAM, heavy uniform fleece. Serendipity = SMALL, DARK brown/near-black, patchy mixed hair+wool coat. (Claude error 2026-04-24: wrongly IDed a dark sheep at trough as "FM/Tunis Red" — it was Serendipity.) |
| Small White Ewe vs. white lambs | All small and white, but SWE has **hair** coat + MC-189 tag. Lambs have softer lamb wool and MC-26## tags. |
| Serendipity vs. her black ewe twin (MC2607) | Adult vs. lamb size difference. Serendipity has MC-157 tag; twin has MC-2607. |

---

---

## Pen 2 — Rocky's Pen (2 animals as of 2026-04-24)

Pen 2 is currently a small two-animal pen: Rocky (the Awassi/BHD/EF ram) plus one unidentified white-faced wool ewe whose identity neither the DB nor the owner could confirm from photos alone. The ewe needs an ear-tag check at next handling before she can be named. Pen 2 is also the site's "secure pen" historically used for difficult rams (per `windlestone-kat-dorper.notes`), so stale Pen-2 assignments in the DB should be audited whenever a fresh pen pass is done.

### Adults (2 visible — 1 locked, 1 pending)

#### `rocky` — "Rocky" / "Jerkface" / "Butthead"
- **Tag:** 140
- **Sex:** ram, adult (weight on record ~300 lb)
- **Sire/Dam:** Teaser (Awassi Ram, 88%Aw/12%EF) × Dorper Ewe 198 (100% BHD)
- **Breed:** 50% Black Headed Dorper / 44% Awassi / 6% East Friesian — **50% hair / 50% wool (reads heavily wool right now)**
- **Phenotype (photo-confirmed 2026-04-24):** **Dark (near-black) head** with white hair-muzzle highlights from BHD heritage. **Curling ram horns** — the single strongest identifier. **Heavy red-brown wool body** from Awassi — shaggy, clumped, clearly needs shearing. **White lower legs.** Large heavy frame, ~300 lb.
- **Owner-confirmed identity 2026-04-24:** *"that ram is dorper awassi and ef"* — distinguishing him from **Buck** (K/Awassi/EF, in Tree Fort, not Pen 2). The key separator is BHD (Rocky) vs. Katahdin (Buck) in the hair-breed half.
- **How to tell from Buck (if ever co-housed):** Rocky = 50% BHD → dark head from Dorper. Buck = 50% Katahdin → would not have the same dominant black-head coloring. Both carry ~48% Awassi so both can be wooly, but the head colors separate them.
- **How to tell from `windlestone-kat-dorper`:** Windlestone-Kat-Dorper is **100% hair** (slick, no fleece). Rocky reads **heavily wool** (thick shaggy fleece Apr 2026). Coat type alone separates them — if the DB ever shows both in Pen 2, coat type is the tell. **Note:** the Windlestone-Kat-Dorper record shares aliases ("Butthead", "Charlie's Ram") with Rocky — possible duplicate risk; flagged for owner resolution.
- **Health:** On weak resistance list. FAMACHA 1 at 2-16-26. Yearly Covexin booster 3-13-26.

#### **Mystery Ewe — `[UNCLEAR]`** (flagged in `pens.pen_2.unidentified[]`, added 2026-04-24)
- **Tag:** **none visible in photos** — eyeball the ear tag at next handling
- **Sex:** ewe, adult
- **Phenotype (photo only, 2026-04-24):** **Clean white face, pink nose**, upright white ears, no dark pigment around eyes or muzzle. **Cream / off-white wool body** — shaggy/clumped fleece, needs shearing. Medium-small adult frame, clean white legs. **No visible horns.** Calm around Rocky.
- **Owner note 2026-04-24:** *"a pink nose generally indicates a gene for spots in their coloration"* — so she likely carries a spot-coloration allele even if she appears solid cream now.
- **Owner ruled OUT:** `nuba-0053` (she is in Pen 1 after lambing 3-24-26; owner confirmed the Pen 2 ewe is not her). "Nuba" was a Claude transcription error off the tag number, not a real name.
- **Confidence:** **low — pending tag check or clearer ID photo.** Do NOT assign her to an existing record without ground truth. If she is not in the current roster she may need a new record, same pattern as `samson-daughter-p4` in Pen 4.
- **Candidates to check when tag is readable:**
  - `tag-0044-wool-ewe` (Pen 1, tag 0044, 50% wool mixed, no color description on record) — phenotype plausible, pen assignment would need updating if it's her.
  - A roster-missing ewe not yet in the DB.

### Lambs (0)
None currently in Pen 2. Any lambs from 0053's 3-24-26 single-ewe birth stayed with her in Pen 1.

---

## Pen 2 — Quick-Reference Decision Tree

```
Is it an adult? (all Pen 2 animals are currently adults)
├── Ram?
│   ├── Dark head + curling HORNS + heavy red-brown WOOL + white legs + ~300 lb ..... rocky
│   └── (no other rams currently in photo — if you see a slick white hair ram,
│        that's either windlestone-kat-dorper (stale Pen 2 assignment) or Buck
│        (K/Aw/EF, tree fort) — confirm before IDing)
└── Ewe?
    └── White face, pink nose, cream wool body, no horns, medium frame ............. [UNCLEAR]
        (flagged in DB pens.pen_2.unidentified — needs tag check)
```

---

## Known visual confusion cases (Pen 2)

| Confusable pair | Tell them apart |
|---|---|
| Rocky vs. Buck (Tree Fort) | Both ~48% Awassi wool, can look similar wooly. Rocky is 50% **BHD** → dark head. Buck is 50% **Katahdin** → would not show the same dark BHD head coloring. Different pens (Rocky = Pen 2, Buck = Tree Fort). |
| Rocky vs. `windlestone-kat-dorper` | Rocky = heavy **wool** coat (shaggy, needs shearing). Windlestone-Kat-Dorper = 100% **hair** (slick). Coat type is the instant tell. **Flag:** Windlestone-Kat-Dorper's DB aliases ("Butthead", "Charlie's Ram") collide with Rocky's — possible duplicate record, pending owner resolution. |
| Mystery ewe vs. `nuba-0053` | Owner ruled out 2026-04-24 — 0053 is in Pen 1 after lambing. Not a visual tell, a ground-truth rule. |
| Mystery ewe vs. `tag-0044-wool-ewe` | Possible match if 0044 has a white face + pink nose (record is blank on color). Read 0044's tag at next pen pass — if she's there, roster moves her from Pen 1 to Pen 2. |

---

## Pen 2 — Provenance

- **Built:** 2026-04-24 from owner identification of three Pen 2 photos dated 2026-04-24 (close-up of Rocky through fence + two golden-hour shots of both sheep).
- **Owner-confirmed identifications:** Ram = Rocky/Jerkface/Butthead ("dorper awassi and ef"), confirmed by breed composition match vs. Buck ("kat awassi ef", in Tree Fort). Not-identifications: ewe is not 0053.
- **DB corrections made in this pass (all 2026-04-24):**
  - `pens.pen_2.ewes` emptied — 0053 belongs to Pen 1 per her individual record and owner confirmation; she was stale in the roster.
  - `pens.pen_2.unidentified[]` added to formally track the unknown ewe without guessing her identity.
  - `pens.pen_2.notes` rewritten to reflect current state (2 animals, not 3; Rocky + 1 unidentified).
  - `elsie.pen` corrected from `"Pen 2"` → `"Pen 5"` (owner: *"elsie is in 5 with angus"*). Also corrected stale notes referencing "Now lives in Pen 6 permanently."
  - `angus.pen` set from `null` → `"Pen 5"` per owner.
  - `pens.pen_5` roster updated: added `angus` to new `other_rams` field, added `elsie` to `ewes`; census bumped 6 → 8.
  - `nuba-0053.aliases` emptied (removed "Nubia" transcription error). Her notes now explicitly state "Nuba" was a Claude misread off the tag number, not a real name or notebook spelling.
  - `rocky` visual_id block added (face, horns, coat, body, pen_context, distinguishes_from Buck + Windlestone-Kat-Dorper). `color_markings` written from photos. `last_verified` bumped 2026-02-16 → 2026-04-24.
  - `windlestone-kat-dorper.status_notes` flagged — pen assignment Pen 2 is likely stale (ram not in photos), and aliases "Butthead" / "Charlie's Ram" collide with Rocky's aliases — possible duplicate-record risk. Deferred to owner.
- **Open questions carried forward:**
  1. Who is the white-faced wool ewe in Pen 2?
  2. Where is `windlestone-kat-dorper` actually pastured?
  3. Is `windlestone-kat-dorper` a distinct animal from Rocky or a duplicate record from confused notebook card-reading?

---

## Pen 4 — Provenance

- **Built:** 2026-04-24 from owner identification of IMG_2026-04-24 Pen 4 photo set (4 images) + MC08 reference photo.
- **Owner-confirmed identifications (Picture 1):** far-left dark = Serendipity; beside her = GG; half-behind GG = Gigi's 2026 baby; big sheep behind = FM; right of GG = FM2; right of FM2 = Gigi's 2025 ram; back-right = samson-daughter-p4 (full sister to MC08, Samson × Broken Tail).
- **Owner-confirmed identifications (Picture 3):** center black-faced adult = GG; samson-daughter-p4 barely visible back-right. Owner correction: samson-daughter-p4 has a **white face like her brother MC08**, NOT a black Hampshire face — supersedes earlier pedigree-based assumption. ⚠ Claude's picture-3 ID of "left at trough = FM" is suspect given FM/Serendipity confusion caught in picture 4 — may actually have been Serendipity. Needs re-verification.
- **Owner-confirmed identifications (Picture 4):** left foreground at trough = Serendipity; right foreground black-faced = GG. Claude had wrongly said left = FM. Fix: FM is LIGHT cream, not dark brown.
- **Reference photos:** MC08 (Pen 6) photo provided 2026-04-24 — shows cream wool, white face, rounded muzzle, yellow MC08 tag. Used as reference for identifying his full sister samson-daughter-p4.
- **Expansion plan:** replicate this structure for Pens 1, 2, 3, 5, 6, Goose, Chicken Coop, Tree Fort as owner verifies photos from each. Keep identity records in `data/flock_database.json` authoritative; this doc derives from them.

---

## Pen 6 — MC08 + Windlestone Awassi group (4 animals as of 2026-04-24)

Pen 6 is the MC08 ram group. Ram is `mc08-ram` (fawn wool cross, Samson × Broken Tail); ewes are the three Windlestone Ranch fat-tail Awassi ewes (2139, 0056, 0055). **Only 4 animals in the pen** as of 2026-04-24 — Elsie and her large triplet (MC-2618) are in Pen 5 with Angus; the small untagged triplet is staged for the 2026-04-26 auction (alive, no current pen).

**CORRECTED 2026-04-24 from prior roster assumption:** the DB listed Elsie + both triplets in Pen 6 and Elsie's own record said `pen: "Pen 2"`. Owner confirmed all three are not in Pen 6. Pen 6 = 4, not 7.

### Adults (4)

#### `mc08-ram` — "MC08"
- **Tag:** MC08 (yellow)
- **Sex:** ram, adult
- **Sire/Dam:** Samson (100% Hampshire) × Broken Tail (hair-breed dam)
- **Breed:** 50% Hampshire / 32.8% St Augustine / 14.1% Katahdin / 3.1% BBB — **50% wool / 50% hair** (reads WOOL — heavy fleece)
- **Phenotype:** **Cream/fawn heavy wool fleece**, **WHITE (cream-tinted) face** — NOT the Hampshire black face despite 50% Hampshire sire. Dam Broken Tail's hair-breed pigment dominated face. **Rounded muzzle**, cream/pink nose, light ears. **Polled** — the only hornless adult in Pen 6. Large frame (comparable to an Awassi ewe but leaner than 2139).
- **How to tell from the Windlestones:** MC08 is **polled** — Awassis all have horns. Also MC08's face reads cream/white; Awassi faces are brown.
- **How to tell from his full sister samson-daughter-p4 (Pen 4):** Same phenotype type (cream wool, white face) but MC08 has a **rounder nose** and **slightly less-white (more cream-tinted) face** than his sister. Sister is in Pen 4, not here.
- **How to tell from Elsie's large triplet (MC-2618):** MC-2618 is a 3.5-mo ewe lamb and is in **Pen 5**, not Pen 6. Any cream-wool yellow-tagged animal in a Pen-6 photo is MC08.
- **Notes:** Needs shearing (2026-02-20 observation).

#### `windlestone-2139` — "Windlestone Fat Tail 2139"
- **Tag:** 2139
- **Sex:** ewe, adult
- **Breed:** 95% Awassi — **100% wool** (fat-tail)
- **Phenotype:** **Heavy uniform cream/buff Awassi fleece**, **brown/reddish face**, **big curled horns — the largest in Pen 6**. **Biggest frame of the three Windlestones.** Legs standard/light.
- **How to tell from 0056:** 2139's horns are visibly larger and more prominent; 2139 is also a bigger-framed animal.
- **How to tell from 0055:** 2139 has big horns and light legs; 0055 has tiny horns and distinctive dark brown legs.
- **Notes:** No babies. "Big ewe w nice horns" (notebook). Covexin 8 3-13-26.

#### `windlestone-0056` — "Windlestone Fat Tail 0056"
- **Tag:** 0056 (orange/pink visible tag color in 2026-04-24 photo)
- **Sex:** ewe, adult
- **Breed:** 95% Awassi — **100% wool** (fat-tail)
- **Phenotype:** **Heavy cream/buff Awassi fleece**, **brown face**, **medium curled horns** — long, thick, clearly curled, but **smaller than 2139's and larger than 0055's tiny**. Medium frame. Legs standard/light.
- **Temperament tell:** "Nice to handle" per notebook — may approach closer to the handler than the other two.
- **How to tell from 2139:** 0056's horns are smaller than 2139's; smaller overall frame.
- **How to tell from 0055:** 0056 has clearly curled horns and light legs; 0055 has tiny/nubby horns and distinct dark brown legs.
- **Notes:** No babies. Covexin 8 3-13-26.

#### `windlestone-0055` — "Windlestone Fat Tail 0055"
- **Tag:** 0055
- **Sex:** ewe, adult
- **Breed:** 95% Awassi — **100% wool** (fat-tail)
- **Phenotype:** Cream/buff Awassi fleece, brown face, **tiny/nubby horns**, and — the single clearest visual tell — **DARK BROWN LEGS**. Medium frame.
- **How to tell from 2139 & 0056:** **Dark legs.** Neither 2139 nor 0056 has distinctly dark legs. If you see dark brown legs on an Awassi in Pen 6, it's 0055. Tiny horns confirm.
- **Notes:** No babies. Covexin 8 3-13-26.

### Lambs
None in Pen 6 as of 2026-04-24. (MC-2618, the one remaining Elsie triplet, is in Pen 5. The sm untagged triplet died 2026-04-06.)

---

## Pen 6 — Quick-Reference Decision Tree

```
Is it an adult? (>9 months)
├── Polled (no horns)
│   └── Cream/fawn heavy wool, white-cream face, yellow MC08 tag ..... mc08-ram
└── Horned (Awassi fat-tail, 95% wool)
    ├── BIG curled horns, biggest frame ............................... windlestone-2139
    ├── MEDIUM curled horns, "nice to handle", orange/pink tag ......... windlestone-0056
    └── TINY/nubby horns + DARK BROWN LEGS ............................ windlestone-0055
```

**Single best tell per animal:**
- MC08 = polled
- 2139 = biggest horns
- 0056 = moderate curled horns (between the other two)
- 0055 = dark brown legs

---

## Known visual confusion cases (Pen 6)

| Confusable pair | Tell them apart |
|---|---|
| 2139 vs. 0056 | Both Awassi ewes with curled horns. **2139's horns are visibly larger** and she is the bigger-framed animal. If horns are big and prominent, it's 2139; if moderate, it's 0056. |
| 0055 vs. 2139 or 0056 | **Dark brown legs = 0055.** Only 0055 has distinctly dark legs. Also: 0055's horns are tiny/nubby (both others have fully curled horns). |
| MC08 vs. any Awassi | **MC08 is polled** (no horns). All three Awassi ewes have horns. Face color also differs (MC08 cream/white; Awassis brown). |
| MC08 (Pen 6) vs. samson-daughter-p4 (Pen 4) | Full siblings, same cream-wool white-faced phenotype. MC08 has a **rounder nose**; sister has a **more pointed nose** and a **whiter face**. They are in different pens — pen context usually resolves this. |
| MC08 vs. elsie-triplet-lg-white-ewe (MC-2618) | MC-2618 is in **Pen 5**, not Pen 6 (owner correction 2026-04-24). Also: MC-2618 is a 3.5-mo ewe lamb (smaller, less-developed fleece) vs MC08 adult ram. If you see a cream-wool yellow-tag animal in a Pen-6 photo, it's MC08. |
| MC08 head-on vs. side profile (same animal) | Both 2026-04-24 photos of a cream-wool yellow-tag polled animal are MC08 from two angles — owner-confirmed 2026-04-24. Earlier speculation that the side-profile might be MC-2618 was wrong (she's not in Pen 6). |

---

## Provenance (Pen 6)

- **Built:** 2026-04-24 from IMG_2026-04-24 Pen 6 photo set (6 images: MC08 head-on, MC08 side profile, 2139 lying down w/ big horns, 0056 standing w/ curled horns + orange tag, 0055 dark legs profile, group shot ~4 animals at hay bale).
- **Owner-confirmed identifications (2026-04-24 verbal):**
  - **Head-on cream-wool yellow-tag polled animal = MC08.** Same animal as the side-profile shot.
  - **Side-profile cream-wool yellow-tag animal = MC08** (not MC-2618; MC-2618 is in Pen 5).
  - **Big ewe lying down w/ big curled horns = windlestone-2139.**
  - **Standing ewe w/ medium curled horns + orange/pink tag = windlestone-0056.**
  - **Ewe w/ distinct dark brown legs + tiny horns = windlestone-0055.**
- **Owner roster corrections (2026-04-24 verbal):**
  - Elsie is in **Pen 5** (DB had `pen: "Pen 2"`, Pen 6 roster had her listed — both wrong). With Angus and her one remaining triplet.
  - **MC-2618** (elsie-triplet-lg-white-ewe) is in **Pen 5**, not Pen 6 (and not Pen 5 lambs roster — added 2026-04-24).
  - **Small untagged triplet (elsie-triplet-sm-white-ewe) is ALIVE**, going to auction Sunday 2026-04-26 — currently has no permanent pen. *(CORRECTED from the earlier commit in this same branch which wrongly marked her deceased. Owner clarified 2026-04-24: one triplet gifted (black ram), one to auction (sm white ewe), one with Elsie in Pen 5 (lg white ewe MC-2618). The 2026-04-06 status_date was a stale/meaningless value, not a death date — cleared.)*
  - **Pen 6 roster size: 4** (1 ram + 3 ewes, no lambs), not 7.
- **Group-shot photo:** backlit at hay bale; individual IDs not resolvable at that distance, but headcount is consistent with the 4-animal roster (owner in pink dress visible for scale).
- **Uncertain / flagged for future verification:**
  - Pen 5 currently lists `ram: "eclipse"` (tag 113, marked subfertile + "going to auction 4-26"). Owner mentioned **Angus** in Pen 5 on 2026-04-24; ram/roster role not updated in this commit pending owner clarification. *(Resolved 2026-04-26 — see Pen 5 section below.)*
  - Windlestone Awassi breed percentages sum to 95% (pre-existing warning, not corrected).

---

## Pen 5 — NoriSon → Angus transition (photo session 2026-04-26)

Pen 5 was the NoriSon/Eclipse breeding group. As of **2026-04-26**, NoriSon was **sold at auction** and replaced by **Angus** (4-month-old Windlestone ram, arrived 2026-04-22). Two photos taken between 2026-04-22 and 2026-04-25 show a partial pen view: the new ram, two ewes, and a now-deceased lamb.

**Owner verbal ground truth, 2026-04-26:**
- Back-right corner of photo 1 = **Angus** (the new Pen 5 ram, 4 months old).
- Middle ewe (photo 2 center, photo 1 right-foreground) = **tag 00113**, full sister of `orange-tag-00110` (the Pen 1 ram). Cracker/GCN/Suffolk/Katahdin. **Moved to Pen 1 on 2026-04-25** — no longer in Pen 5 as of today.
- Right ewe in photo 2 = **OAV 2222** ("Kelsier's sister"), 100% Katahdin.
- Brown lamb in foreground (both photos) = 00113's singleton ram-or-ewe by NoriSon, **born 2026-04-22, died 2026-04-25** of failure to thrive. Owner: "00113 was a bad mom."

### Animals visible in the 2026-04-26 photo set (4)

#### `angus` — "Angus"
- **Tag:** none yet (new arrival)
- **Sex:** ram (ram lamb, ~4 months as of 2026-04-26 — DOB ~Dec 2025/Jan 2026)
- **Source:** Windlestone, picked up 2026-04-22
- **Breed:** **50% Katahdin / 25% Dorper / 25% Awassi** (owner-confirmed 2026-04-26 — 75% hair, 25% wool; coat reads hair). *(CORRECTED from prior "low confidence, Awassi appears twice" placeholder.)*
- **Phenotype:** **Black head + neck with a sharp boundary at the shoulders; WHITE body; short, slick shedding hair coat (no fleece).** Classic black-headed Dorper visual type by appearance. Young ram frame.
- **Photo position:** **Back-right corner of photo 1**, standing near the round container/bin in mid-distance.
- **How to lock him:** he is the **only** black-head/white-body hair-coat animal in Pen 5 — phenotype alone is sufficient. Confirmed by owner verbal 2026-04-26.
- **Role:** Replaced NoriSon as the Pen 5 breeding ram on or before 2026-04-26.
- **Flag:** Needs tag, breed comp clarification (one of the "Awassi" entries should likely be Katahdin), FAMACHA baseline at next handling.

#### `tag-00113-ewe-p1` — "00113" — **NEW record, added 2026-04-26**
- **Tag:** 00113 (per owner; not directly readable in photos)
- **Sex:** ewe, adult
- **Sire/Dam:** unknown — same parents as `orange-tag-00110` (Pen 1 ram, **full brother**) and `tag-114-fawn-wool` (full sister). Owner-confirmed full-sibling trio 2026-04-26.
- **Breed:** 50% Cracker / 25% Suffolk / 12.5% Gulf Coast Native / 12.5% Katahdin — **~87.5% wool**
- **Phenotype:** **Heavy cream/light wool fleece**, **BLACK FACE** (Suffolk dominance), **black legs**, **large frame**. Largest ewe visible in the 2026-04-26 photos.
- **Photo position:** **Center of photo 2 / right-foreground of photo 1**, standing on the sandy ground facing the camera (photo 2) or in profile (photo 1).
- **Current pen:** **Pen 1** (moved 2026-04-25). She was in Pen 5 unrostered before that.
- **2026 lambing:** Singleton lamb by NoriSon, born 2026-04-22, died 2026-04-25 (FTT). Owner: "00113 was a bad mom."
- **How to tell from `tag-114-fawn-wool` (her full sister):** Tag 114 is **fawn-colored wool**; 00113 is **cream wool with a black face**. Different color expression of the same Cracker/Suffolk cross.
- **How to tell from `orange-tag-00110` (her full brother):** Same breed comp & frame, but he is the ram in Pen 1 with an **orange tag**; she is a ewe.
- **How to tell from OAV 2222 in the same photo:** OAV is **slick hair coat, light face**; 00113 is **heavy wool, black face**. Opposite ends of the coat-type axis.
- **Health (owner verbal 2026-04-26):** **Very parasite resistant.** *Mothering* is the weak trait, not parasite handling. Owner: "00113 has been very parasite resistant. just a terrible mother." Treat as a parasite-resistance breeding candidate, but supervise lambing closely.
- **Flag:** Needs FAMACHA baseline (formal scoring), formal tag verification, age estimate at next handling.

#### `oav-2222` — "OAV 2222" / "Kelsier's Sister"
- **Tag:** 2222 (OAV/Oakvale Farm series)
- **Sex:** ewe, adult
- **Breed:** 100% Katahdin — **100% hair**
- **Phenotype:** **Slick hair coat**, **cream/light body**, **light/white face**, medium adult frame (~140 lb). Quiet, docile.
- **Photo position:** **Right of 00113 in photo 2** (looking at camera with one ear back); **far-right edge of photo 1** (partially cut off).
- **2026 lambing:** **None this year.** *(CORRECTED 2026-04-26: prior 2026-02-10 lambing record entry — twins by NoriSon — was wrong. Owner verbal: "OAV had no twins this year." Her last known lambing was 2024 — 2 lambs by Spotted Katahdin × Dorper, born 3-13-24. Both believed died eventually.)*
- **How to tell from 00113 (in same photo):** Hair coat vs wool, light face vs black face. Phenotype alone resolves the pair.
- **Health:** FAMACHA consistently 1–2. Thiamine deficiency 2024 (treated B-complex). On weak-resistance watch list as of older notes.

#### `tag-00113-singleton-2026` — "00113's Singleton (deceased)" — **NEW record, added 2026-04-26**
- **Tag:** none
- **Sex:** unknown
- **Sire/Dam:** NoriSon × tag-00113-ewe-p1
- **DOB / DOD:** **Born 2026-04-22, died 2026-04-25** (3-day life)
- **Cause:** Failure to thrive. Owner: "00113 was a bad mom."
- **Phenotype:** **Brown body** small lamb, visible at the bucket/feeder in the foreground of both 2026-04-26 photos before death.
- **Pen:** none (now deceased)

### Other Pen 5 roster animals NOT in these photos (still on roster, not visually verified this session)

- `tag-31-ewe-p5` — Sir Loin daughter, hair, "proven breeder, Eclipse failure"
- `tag-02-ewe-p5` — breed unclear, Pen 5
- `fawn-wool-ewe-p5` — fawn wool, long ears, tag 240006
- `little-daisy` — small white hair, Sir Loin × Daisy, sister of `sm-white-ewe-p4`. *(DB record currently lists `pen: "Pen 4"` — may be stale; pen5 roster includes her.)*
- `elsie` — Katahdin/SA/BBB hair, primary 2026 lambing dam
- `elsie-triplet-lg-white-ewe` (MC-2618) — Elsie's surviving triplet, sired by NoriSon

### Removed from Pen 5 in the 2026-04-26 sweep
- **NoriSon (= Eclipse, merged record)** — sold at auction 2026-04-26.
- **`elsie-triplet-sm-white-ewe`** — small white triplet, sold at auction 2026-04-26.
- **00113** — moved to Pen 1 on 2026-04-25.

---

## Pen 5 — Quick-Reference Decision Tree (visible animals 2026-04-26)

```
Is it an adult? (>9 months)
├── Hair coat (slick, no fleece)
│   ├── Light face + cream body, medium frame, tag 2222 ........ oav-2222 (Kelsier's sister)
│   └── Black head + neck w/ sharp white-body boundary
│       └── Young ram (~4 mo), no tag yet ...................... angus (NEW Pen 5 ram, Apr 2026)
└── Wool coat (heavy fleece)
    └── BLACK FACE + black legs, cream body, large frame, tag 00113 . tag-00113-ewe-p1
        (full sister of orange-tag-00110; moved to Pen 1 on 2026-04-25)
```

Lamb (visible): **brown body, small, 3 days old when photographed**, foreground both photos = `tag-00113-singleton-2026` (now deceased).

---

## Known visual confusion cases (Pen 5)

| Confusable pair | Tell them apart |
|---|---|
| 00113 vs. tag-114-fawn-wool (her full sister, Pen 1) | **Color**: 00113 is **cream-with-black-face wool**; 114 is **fawn wool**. Both have the same 50%Cr/25%Su/12.5%GCN/12.5%K breed comp. They are in different pens. |
| 00113 vs. orange-tag-00110 (her full brother, Pen 1) | **Sex.** Same breed comp & frame; orange-tag is the ram, has an **orange tag**; 00113 is the ewe. |
| 00113 vs. OAV 2222 (in same photo) | **Coat type.** 00113 is wool with black face; OAV is hair with light face. Opposite ends of the coat-type axis — phenotype alone resolves it. |
| Angus vs. OAV 2222 | Both have light bodies, but **Angus has a sharply black head/neck**; OAV is **uniformly light**. Angus is also a young ram (smaller frame, 4 mo); OAV is an adult ewe. |
| Angus vs. an adult Awassi (Pen 6) | Angus is **polled, slick hair**; Awassis are **horned, wool, fat-tailed**. Different pens, but if photo crops are ambiguous: hair-vs-wool resolves it. |
| Photographed lamb vs. any of Elsie's triplets | The brown foreground lamb (now deceased 4-25) is **00113's singleton**, NOT an Elsie triplet. Elsie's triplets are white (or black-ram, gifted). The big white lamb in Pen 5 is `elsie-triplet-lg-white-ewe` (MC-2618), not in these two photos. |

---

## Provenance (Pen 5)

- **Built:** 2026-04-26 from owner identification of the 2-photo Pen 5 set sent in this session (taken between 2026-04-22 and 2026-04-25).
- **Owner-confirmed identifications (verbal, 2026-04-26):**
  - **Back-right corner of photo 1 = Angus.** "4 months old."
  - **Middle ewe of photo 2 / right-foreground photo 1 = tag 00113.** "Full sister of the ram in pen 1. Cracker/GCN/Suffolk/Katahdin." Moved to Pen 1 on 2026-04-25.
  - **Right ewe of photo 2 = OAV 2222.** "Kelsier's sister, 2223 or 2222, something like that." (Tag confirmed 2222.)
  - **Brown foreground lamb = 00113's singleton by NoriSon.** Born 2026-04-22, died 2026-04-25 (FTT). "00113 was a bad mom."
- **Owner-confirmed DB corrections (verbal, 2026-04-26):**
  - **NoriSon = Eclipse.** Same animal — two records, now merged. Canonical id: `nori-son`. Aliases preserve "Eclipse," "Tag 113," "Tag 22." CORRECTED from prior assumption that they were separate rams.
  - **NoriSon/Eclipse sold at auction 2026-04-26**, along with `tag-0033-twin-ram-2` (the black ram lamb, dam tag-0033-hair-ewe) and `elsie-triplet-sm-white-ewe` (smaller of the two remaining Elsie triplet ewes). status="sold", status_date="2026-04-26".
  - **Kaladin is NOT deceased.** DB had him wrongly bulk-marked deceased 2026-04-02. CORRECTED to alive. (Owner: "i forgot that was his name.") He is NOT the Pen 1 ram — `orange-tag-00110` is. Kaladin's current pen unknown; not updated here.
  - **OAV 2222 had NO twins in 2026.** The 2026-02-10 lambing record was wrong and has been removed. Her prior twins (referenced in NoriSon's track record) were from earlier years.
  - **Daisy's Daughter 2 had NO lamb in 2026.** The 2026-02-07 lambing record was wrong and has been removed.
- **Owner assessment of NoriSon as a sire (verbal, 2026-04-26):** "Consistently hit or miss, in with 5 ewes for two years or so — only Elsie's triplets, 00113's singleton (died), OAV twins (prior years, died), Daisy's Daughter 2's lamb (believed died). Not a great contributor. One of the three of Elsie's lambs may have earned a place — I'm watching."
- **New animals added to DB this session:**
  - `tag-00113-ewe-p1` (Pen 1, alive, full sister of orange-tag-00110)
  - `tag-00113-singleton-2026` (deceased FTT, NoriSon × 00113)
- **New 2026 lambing record:** 2026-04-22, dam 00113, sire NoriSon, 1 born / 0 alive (Pen 5).
- **Photo-only IDs (4) confirmed.** Other Pen 5 roster animals (tag-31, tag-02, fawn-wool 240006, little-daisy, elsie, MC-2618) are not in these photos and not visually verified this session.
- **Pen-5 ram update applied:** `pens.pen_5.ram` changed from `eclipse` to `angus`.
- **Pen-1 roster update applied:** `tag-00113-ewe-p1` added to `pens.pen_1.ewes`.
- **Lighting note:** photos taken in low-angle morning/evening sun (long shadows visible). Body color may read warmer than midday truth — but the BLACK FACE on 00113 is clearly Suffolk-dominant, not a lighting artifact.

---

1. **Never invent phenotype.** If the DB doesn't describe a sheep's markings and you haven't seen her, say so. Mark `[UNCLEAR]`.
2. **Owner testimony beats DB** — the DB exists to encode owner knowledge, not override it.
3. **Update both places** — when a new identification is confirmed from photos, update `data/flock_database.json` AND this doc in the same commit.
4. **Tag numbers are the ground truth** — phenotype narrows candidates, tags confirm.
