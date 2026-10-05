---
name: editorial-pdf
description: "Use when creating editorial A4 PDFs via headless Chrome."
version: 1.2.0
author: Nous Research
license: MIT
metadata:
  hermes:
    tags: [pdf, editorial, html-to-pdf, headless-chrome, documents, legal-memo, prd, technical-spec]
    category: productivity
    related_skills: [pdf, docx]
---

# Editorial PDF Generation

Workflow for generating publication-quality, editorial A4 PDFs using HTML/CSS rendered via Headless Chrome (`google-chrome --headless`).

## When to Use

- Generating legal memos, executive briefs, formal reports, analysis documents, or invoices as PDF.
- Generating Product Requirement Documents (PRDs), technical architecture blueprints, and enterprise system specifications.
- When pixel-perfect typography, crisp container styling, and precise multi-page flow are required.
- Do NOT use reportlab for editorial documents when Headless Chrome is available.

## Standard Procedure

1. **Author HTML Document (`@page` CSS):**
   - Use standard A4 page size: `@page { size: A4 portrait; margin: 11mm 13mm 11mm 13mm; }` (or up to 14mm 16mm).
   - Set clean system typography: `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif`.
   - Use `-webkit-print-color-adjust: exact; print-color-adjust: exact;` to preserve backgrounds and borders.
   - For exact multi-page layouts without orphan/trailing pages, structure each page as an explicit flex container:
     ```css
     .page {
       page-break-after: always;
       height: 274mm;
       max-height: 274mm;
       display: flex;
       flex-direction: column;
       justify-content: space-between;
       overflow: hidden;
     }
     .page:last-child { page-break-after: avoid; }
     ```
   - Place a pinned `.page-header` at the top, a flexible `.content` in the middle (`flex: 1; display: flex; flex-direction: column; gap: 8px;`), and a pinned `.page-footer` at the bottom with explicit pagination (`Halaman X dari Y`).

2. **Structural Component Design (No Monospace Box/ASCII Wrapping):**
   - For architectural flowcharts, platform layers, and system matrices, **never** use fixed-width plaintext ASCII borders (`+----+`, `|  |`). In portrait A4 with standard margins, monospace box borders wrap across lines or clip, breaking visual hierarchy.
   - Instead, author structural diagrams using native HTML/CSS flex/grid components (e.g. `.arch-box`, `.arch-row`, `.arch-layer` with clean cards, colored pill badges, subtle dark or light backgrounds, and crisp borders). This guarantees responsive fluid scaling, crisp vector rendering, zero awkward line wrapping, and high readability in visual audits.

3. **PRD & Technical Specification Blueprint Pattern:**
   - **Executive Metadata Strip:** 4-column matrix (Product Name, Initiator/Team, Version/Status, Priority P0-P3) paired with a 4-card metric strip (key numeric KPI targets like latency, dispute reduction %, download seconds, billing cycle).
   - **Competitive Differentiation Matrix:** 3-column table comparing conventional/public solutions (e.g. public AIS tracking) vs. proprietary enterprise portal across core capabilities, closed with a bold strategic positioning callout.
   - **User Personas & Data Flow Architecture:** 3 distinct persona cards (Foreign Client/Principal, Field Officer, HQ Operations) defining Role, Core Needs, and Usage Behavior. Pair with a 4-quadrant dark architecture container (`.arch-box`) detailing Field Edge PWA, Jakarta Central Core, Client Extranet Portal, and Cloud Services.
   - **Functional Requirement Numbering:** Standardize requirement codes (e.g. `FR-1.1`, `FR-1.2`, `FR-2.1`) in clear 3-column tables: Requirement Code, Feature Name, and Technical Specification & Business Logic.
   - **Non-Functional Requirements (NFR) & Security:** 3-column NFR table (Availability, Performance Latency, Storage, Device Compatibility) paired with Row-Level Security (RLS) and immutable audit trail cards.
   - **Multi-Sprint Roadmap & Risk Mitigation:** 3-row phased sprint roadmap table (Month 1, Month 2, Month 3 across 6 sprints) paired with a 3-card operational risk mitigation grid and a dark engineering sign-off container (no signature lines or stamps).

4. **Render with Headless Chrome:**
   - Execute:
     ```bash
     google-chrome --headless --disable-gpu --no-sandbox --no-pdf-header-footer --print-to-pdf=<output.pdf> <input.html>
     ```
   - **Crucial Flag:** Always include `--no-pdf-header-footer`. Without this, Chromium stamps the file path, date/time, and unformatted page numbers at the top and bottom.

5. **Verify Page Count & Flow (PyMuPDF / pdfinfo):**
   - Check page count programmatically:
     ```python
     import pymupdf
     doc = pymupdf.open('output.pdf')
     print('Pages:', len(doc))
     ```
   - If an unexpected trailing page occurs with only 1-2 lines or a single section, adjust font sizes (e.g. 10pt -> 9.5pt) or container paddings to achieve a balanced, deliberate page count.

6. **Visual & Proofreading Inspection via `vision_analyze`:**
   - Export pages to PNG:
     ```python
     for i, page in enumerate(doc):
         page.get_pixmap(dpi=150).save(f'/tmp/page_{i+1}.png')
     ```
   - Inspect every page with `vision_analyze` to verify:
     - Text legibility, contrast, and zero clipping/overflow along container borders.
     - Architecture and diagram integrity: ensure no text wrapping in code blocks or diagram cards.
     - Zero typos, proper capitalization of corporate and technical terms, and correct formal syntax (e.g. EYD/PUEBI).
     - Mathematical reconciliation: verify that all arithmetic in tables, percentage shares, formulas, and line items calculate exactly to the displayed sums.

## Core Rules & Constraints

- **No Signatures / No Stamps:** Never include signature blocks, sign lines, or stamp graphics in generated PDFs unless explicitly commanded by the user. Use a dark executive sign-off text card for engineering/governance authorization.
- **Tone & Text:** Plain-text arrows (`->`), no LaTeX in chat/text, avoid robotic em dashes in Indonesian copy. Keep badge/header wording aligned with user direction (e.g. "Telah Yuridis" instead of non-standard elongation).
- **Zero-Typo & Data Precision:** Reconcile data against primary sources (e.g. API output, database rows) before rendering. Never fabricate placeholder numbers, and ensure real email usernames or technical aliases are preserved accurately without false autocorrection.
- **Native Delivery:** Return the generated PDF via `MEDIA:/absolute/path/to/file.pdf` for direct download on Telegram.
