---
name: event-quest-design
description: Design offline event scavenger hunts, main/side quests.
category: productivity
---

# Offline Event & Scavenger Hunt Quest Design

Guidelines and workflows for designing interactive offline group events, location-based rally games, and 17 Agustus competitions (e.g., TMII, parks, outdoor venues).

## 1. Core Event Structure
When structuring multi-group offline events:
- **Main Quests (Wajib):** Pos-to-pos mandatory stations/games. Everyone must complete these for base points.
- **Side Quests (Opsional):** Location-based tasks or exploration riddles for bonus points (e.g., +1 to +5 pts).
- **Rule Constraints & Penalties:** Specific group constraints (e.g., dress code/baju adat, mandatory minimum participants) with defined penalties (e.g., -10 pts).
- **Randomized & Dual Opposite Route Management:** If stations are non-linear or have many groups (e.g., 15 groups), split groups into two opposite routes (e.g., Rute A: Pos 1 ➔ 2 ➔ 3 and Rute B: Pos 3 ➔ 2 ➔ 1) to prevent crowd bottlenecks at any single station.
- **Spatial Mapping & Collection Checkpoints (Pos Tempat Pengumpulan):** Group side quests geographically by proximity to assigned stations (Pos 1, Pos 2, Pos 3) or mark as "Bebas" / "Pos 1, Pos 2, atau Pos 3" (any pos). Add a dedicated `Pos Tempat Pengumpulan` column in the spreadsheet so participants turn in proof at the nearest station along their route without unnecessary venue backtracking. Audit quest title/description mismatches prior to assigning station checkpoints.
- **Hybrid Collection Channels (Physical Post vs WhatsApp Group):** In addition to physical station checkpoints, support digital submission channels (e.g., WhatsApp Group). Participants submit photo/video proof with the exact `No / ID Quest` in the caption. Update participant guide notes to cover both physical stamp verification and WhatsApp group submission.
- **Verification & Passport Stamp System:** Use a Group Passport (Paspor Kelompok) containing numbered stamp boxes (e.g., Boxes 1-25) carried by each group. Station organizers stamp the corresponding quest box upon proof verification, eliminating the need for separate physical organizer checklist forms.

## 2. Clue & Riddle Design Principles
Convert plain task descriptions into intriguing riddles/clues to make exploration interaktif while keeping the core objective clear upon reading:
- **Direct Task:** "Foto di depan patung harimau Sumatra"
  → **Clue:** *"Foto bersama bapaknya kucing"* or *"Temukan sang Raja Hutan Sumatra yang berdiri gagah menjaga wilayahnya!"*
- **Direct Task:** "Foto di depan boneka pengantin Anjungan Riau"
  → **Clue:** *"Cari sepasang pengantin yang tak pernah lelah tersenum di dalam rumah megah berwarna kuning emas Melayu!"*
- **Direct Task:** "Video tiru gerakan tari di monitor Sumbar"
  → **Clue:** *"Temukan layar ajaib penampil tari tradisional di tanah Minang dan ikuti gerakannya!"*
- **Direct Task:** "Foto 2 payung adat Mandailing"
  → **Clue:** *"Temukan sepasang payung kehormatan adat berwarna kuning di kediaman Raja Mandailing!"*
- **Direct Task:** "Foto pesawat RI-001 Seulawah di Aceh"
  → **Clue:** *"Temukan monumen perkasa burung besi Dakota RI-001 penembus angkasa di tanah Serambi Mekkah!"*

## 3. Difficulty & Scoring Matrix
- **Mudah (+1 - +2 pt):** Simple group poses, quick observations, minimal movement/coordination.
- **Sedang (+3 - +4 pt):** Interaction with public/staff, multi-location visits, video tasks (singing/dancing), finding specific indoor artifacts.
- **Sulit (+5 pt):** Physical coordination (human pyramid), precise positioning (miniature map matching), hidden/obscure artifacts (floor 2 items, small wood carvings).

4. Project Artifacts & Tracking
For any event planning project:
1. Maintain a dedicated project folder (e.g. `17an_tmii_project/`).
2. Keep a comprehensive `README.md` tracking event rules, group splits, station details, penalty policies, location groupings, and current task progress.
3. Separate **POV Peserta** (riddle description without explicit `[Clue]` tags/labels — pure riddle prose) from **POV Panitia** (exact location, target object, and reference photos).
   - **Peserta Sheet (Public Version):** Include ONLY public columns: `ID Quest`, `Nama Quest`, `Deskripsi & Clue Peserta`, `Format Bukti & Syarat`, and optional `Referensi Video` (for video/dance trends). Remove all answer spoilers: remove exact target objects, exact location/anjungan names, visual photo reference links, and collection post assignments so participants must solve the riddles on their own.
   - **Panitia Sheet (Internal Version):** Include organizer-facing details (`Target Objek / Tugas`, `Format Bukti`, `Referensi Video`). Cleanly strip any internal columns requested for removal (e.g., exact location names or photo reference codes) via API/script while keeping row alignment intact.
4. Primary Output Focus — Excel (`.xlsx`):
   - Focus primary output on Excel (`.xlsx`) generated programmatically (e.g., via `openpyxl`). Do not rely on CSV when physical image embedding or rich layout is requested.
   - Columns: `ID Quest, Nama Quest, Level / Kesulitan, Poin, Deskripsi & Syarat Kelulusan (Clue Peserta), Lokasi / Anjungan (POV Panitia), Target Objek / Tugas, Format Bukti, Kode Referensi Foto`.
   - Embed physical reference photos directly into the sheet (`ws.add_image`) inside a dedicated "Tabel Referensi Foto Bukti Panitia" section at the bottom.
   - Use clean typography (e.g., Calibri), dark blue headers (`#1F4E78`), white text, subtle borders, zebra striping (`#F9FAFB`), explicit column widths, and merged cells for photo rows.
   - Cross-check incoming image batches thoroughly: verify exact image filenames and contents against existing reference codes before asking the user for re-uploads to ensure no submitted photo is missed or misidentified.
   - **Generation Script Integrity & Audit:** When adding/modifying quests or re-indexing quest IDs (e.g., deleting an item), inspect the script generator (e.g., `make_excel.py`) to verify that the `quests_data` array and loop logic contain all intended items without accidental truncation or hardcoded cutoffs. Verify row count and max SQ ID programmatically after running `openpyxl` generation scripts.
5. **Quest Pruning & Multi-Sheet Comparison Workflows:**
   - When evaluating proposed reductions/elimination of quests (e.g. 47 SQ down to 25 SQ), group reasons into clear criteria categories: (A) Double-snap/redundant at same spot, (B) Indoor bottleneck / narrow stairs / safety risk, (C) High-variability or non-distinctive targets.
   - Create a dedicated comparison sheet tab (e.g., `Side Quests (25 SQ Best)`) alongside the full sheet rather than overwriting or creating separate files. Keep sheet names within Excel's 31-character limit (`ws.title[:31]`).
   - Audit photo references when pruning: identify and prune orphan photo reference codes where all child quests were removed, then re-index active photo codes (`REF-FOTO-01` to `REF-FOTO-12`) for clarity.

5. Photo-Based Quest Extraction & Photo Reference Cataloging
When extracting quests from venue photos:
- Identify prominent cultural landmarks, statues, signage, or unique architectural elements (e.g. 3D text signs, totem carvings, fauna statues).
- Assign unique photo reference codes (`REF-FOTO-01`, `REF-FOTO-02`, etc.).
- Link each photo code to its respective Side Quest IDs in the rightmost table column so organizers can instantly verify proof photos during the event.
- **Bulk Quest Expansion from Photo Archives / Zip Uploads:** When the user supplies a batch of new location reference photos (e.g. via `.zip` archive or multi-photo uploads) for event quest expansion:
  1. Extract the archive into the project assets directory (`assets/new_sq/`).
  2. Parse the filenames/metadata for clues, location names, and specific pose/task instructions provided by the user.
  3. Formulate intriguing participant clues, precise organizer target objects, appropriate proof formats (photo vs video), and pos assignments.
  4. Append the newly generated SQ items (e.g., `SQ26` to `SQ35`) to both public (**Peserta**) and internal (**Panitia**) sheets/tables programmatically, preserving header formatting, text wrapping, and alignment across both sheets.

## 6. Google Sheets API v4 Formatting Pitfalls (Python Automation)
When writing custom Python scripts using `googleapiclient.discovery.build('sheets', 'v4')` for styling/formatting via `batchUpdate`:
- **Text Wrapping**: Use `wrapStrategy: 'WRAP'` inside `userEnteredFormat`, NOT `wrapText`. Field mask MUST be `'userEnteredFormat(...,wrapStrategy)'`.
- **Column Widths (`updateDimensionProperties`)**: Pass `properties: {'pixelSize': N}` and set `fields: 'pixelSize'` (do NOT use `'properties.pixelSize'`).
- **Row Freezing (`updateSheetProperties`)**: Use `gridProperties: {'frozenRowCount': N}` with `fields: 'gridProperties.frozenRowCount'`.
- **Leading `+` or `=` in Values:** When writing text like `+1 pt` or `+5 pt` to Google Sheets via API (`USER_ENTERED`), Google Sheets automatically parses leading `+` or `=` as a formula, causing `#ERROR!`. Prepend a single quote (e.g. `'+1 pt`) when setting strings with leading math symbols so Sheets treats them as plain text.
- **Formula Delimiters by Locale:** In non-US locales (such as Indonesian `in_ID`), Google Sheets requires semicolons `;` instead of commas `,` to separate formula arguments (e.g. `=HYPERLINK("url"; "label")`).
- **Google Drive Images in `=IMAGE()` Formulas:** Direct Drive viewer URLs (`/view`) or export URLs fail in `=IMAGE()`. Use thumbnail URLs (`https://drive.google.com/thumbnail?id=FILE_ID&sz=w500`) or direct CDN links (`https://lh3.googleusercontent.com/d/FILE_ID`).
