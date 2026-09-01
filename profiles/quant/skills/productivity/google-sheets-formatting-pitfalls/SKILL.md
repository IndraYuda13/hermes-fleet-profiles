---
name: google-sheets-formatting-pitfalls
description: "Use when creating formulas or images in Google Sheets."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
---

# Google Sheets Formatting & API Pitfalls

Practical workarounds when writing, formatting, or creating formulas in Google Sheets via API or script.

## Common Pitfalls & Solutions

### 1. Leading `+` or `=` causing `#ERROR!`
Google Sheets automatically evaluates values starting with `+` (e.g. `+1 pt`) or `=` as formulas when inserted via `USER_ENTERED`. If the text after `+` is invalid formula syntax, it returns `#ERROR!`.

**Fix:** Prepend a single quote (`'`) to force text mode:
```python
poin_val = "'+1 pt"  # Inserted into Sheets as literal '+1 pt' text
```

### 2. Formula Argument Delimiters in Non-US Locales
In Google Sheets spreadsheets configured with locales using comma decimal separators (e.g., `in_ID`, `id_ID`, `de_DE`), formula arguments MUST be separated by semicolons (`;`), not commas (`,`).

**Fix:** Detect locale or use semicolon for formula strings:
```python
# Indonesian / European locale syntax:
formula = '=HYPERLINK("https://example.com"; "Link Label")'
```

### 3. Range Parsing Errors when Sheet Name contains Parentheses or Spaces
When referencing sheet names with spaces or parentheses (e.g. `'Side Quests (25 SQ Best)'!A1:E10`) via Google Sheets API `values().get()` or `values().update()`, ranges must be correctly quoted. In Python scripts, double-escaping or unescaped quotes within raw string bounds can cause API `HttpError 400: Unable to parse range`.

**Fix:** Ensure exact single quotes wrap sheet names with special characters when constructing range parameters in API payloads.

### 4. Hotlinking Drive Images in `=IMAGE()` Formulas
Direct Google Drive `webViewLink` or `webContentLink` URLs fail or render blank in `=IMAGE()` formulas due to cross-origin / hotlinking restrictions.

**Fix:** Use the official Google Drive thumbnail endpoint:
```python
thumb_url = f"https://drive.google.com/thumbnail?id={file_id}&sz=w500"
image_formula = f'=IMAGE("{thumb_url}")'
```

### 5. Formatting Newly Appended Columns via API
When inserting or appending new columns to an existing formatted table (with custom header colors, zebra striping, font family, and borders), `values.update` only updates raw cell values, leaving cell styling unformatted or mismatched.

**Fix:** Use `spreadsheets().batchUpdate()` with `repeatCell` requests to explicitly apply header background (`backgroundColor`), font (`textFormat`), alignment, borders, and `updateDimensionProperties` to set pixel width for the new column.

### 6. Table Legibility & Link Formatting
Avoid populating table cells with long raw URLs (e.g., TikTok, CapCut, or Drive links). Always wrap URLs in `=HYPERLINK("url"; "🎬 Label / Emoji Text")` to keep the table clean and readable across devices.

### 7. Unmerging Ranges Before Inserting or Shifting Columns
When inserting new columns (`insertDimension`) into a table that contains merged header titles or footer notes (e.g. merged across `A1:E1`), Google Sheets API will not automatically expand the merged range, leading to broken alignment or API errors on subsequent update/format passes.

**Fix:** Query existing `merges` with `spreadsheets().get()`, issue `unmergeCells` requests to clear them, insert the new column, write updated cell values/headers, and then issue `mergeCells` requests spanning the expanded column count (`startIndex: 0, endIndex: total_columns`).
