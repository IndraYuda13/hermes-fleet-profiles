---
name: editorial-pdf
description: "Use when creating editorial A4 PDFs via headless Chrome."
version: 1.3.0
author: Nous Research
license: MIT
metadata:
  hermes:
    tags: [pdf, editorial, html-to-pdf, headless-chrome, documents, legal-memo, prd, technical-spec, transcript, minutes]
    category: productivity
    related_skills: [pdf, docx]
---

# Editorial PDF Generation

Workflow for generating publication-quality, editorial A4 PDFs using HTML/CSS rendered via Headless Chrome (`google-chrome --headless`).

## When to Use

- Generating legal memos, executive briefs, formal reports, analysis documents, or invoices as PDF.
- Generating Product Requirement Documents (PRDs), technical architecture blueprints, and enterprise system specifications.
- Generating formal meeting minutes (*notulensi*), academic bimbingan records, and multi-page verbatim transcripts.
- When pixel-perfect typography, crisp container styling, and precise multi-page flow are required.
- Do NOT use reportlab for editorial documents when Headless Chrome is available.

## Standard Procedure

1. **Author HTML Document (`@page` CSS):**
   - Use standard A4 page size: `@page { size: A4 portrait; margin: 12mm 14mm 12mm 14mm; }` (or 11mm 13mm to 14mm 16mm).
   - Set clean system typography: `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif`.
   - Use `-webkit-print-color-adjust: exact; print-color-adjust: exact;` to preserve backgrounds and borders.
   - For fixed multi-page reports (e.g. 2-4 pages), structure each page as an explicit flex container:
     ```css
     .page {
       page-break-after: always;
       break-after: page;
       height: 274mm;
       max-height: 274mm;
       display: flex;
       flex-direction: column;
       justify-content: space-between;
       overflow: hidden;
     }
     .page:last-child { page-break-after: avoid; break-after: avoid; }
     ```
   - For hybrid documents (executive summary pages followed by flowing multi-page transcripts or logs):
     - Use `@page` margin boxes for running header/footer and dynamic page counters:
       ```css
       @page {
         @bottom-right {
           content: "Halaman " counter(page);
           font-size: 7.5pt;
           color: #94a3b8;
         }
         @bottom-left {
           content: "Dokumen Notulensi & Transkrip...";
           font-size: 7.5pt;
           color: #94a3b8;
         }
       }
       ```
     - Enclose distinct summary sections in `.page { page-break-after: always; break-after: page; }` blocks, and let the transcript flow naturally afterward.

2. **Structural Component Design (No Monospace Box/ASCII Wrapping):**
   - For architectural flowcharts, platform layers, and system matrices, **never** use fixed-width plaintext ASCII borders (`+----+`, `|  |`). In portrait A4 with standard margins, monospace box borders wrap across lines or clip, breaking visual hierarchy.
   - Instead, author structural diagrams using native HTML/CSS flex/grid components (e.g. `.arch-box`, `.arch-row`, `.arch-layer` with clean cards, colored pill badges, subtle dark or light backgrounds, and crisp borders). This guarantees responsive fluid scaling, crisp vector rendering, zero awkward line wrapping, and high readability in visual audits.

3. **PRD & Technical Specification Blueprint Pattern:**
   - **Executive Metadata Strip:** 4-column matrix (Product Name, Initiator/Team, Version/Status, Priority P0-P3) paired with a 4-card metric strip (key numeric KPI targets like latency, dispute reduction %, download seconds, billing cycle).
   - **Competitive Differentiation Matrix:** 3-column table comparing conventional/public solutions vs. proprietary enterprise portal across core capabilities, closed with a bold strategic positioning callout.
   - **User Personas & Data Flow Architecture:** 3 distinct persona cards defining Role, Core Needs, and Usage Behavior. Pair with a 4-quadrant dark architecture container (`.arch-box`) detailing client edge, core services, and cloud layers.
   - **Functional Requirement Numbering:** Standardize requirement codes (e.g. `FR-1.1`, `FR-1.2`) in clear 3-column tables: Requirement Code, Feature Name, and Technical Specification & Business Logic.
   - **Non-Functional Requirements (NFR) & Security:** 3-column NFR table paired with Row-Level Security (RLS) and immutable audit trail cards.
   - **Multi-Sprint Roadmap & Risk Mitigation:** Phased sprint roadmap table paired with operational risk mitigation grid and a dark engineering sign-off container (no signature lines or stamps).

4. **Multi-Page Flow & Dialogue / Verbatim Transcript Pattern:**
   - **Dialogue & Log Cards:** Ensure individual dialogue cards or log items do not get split awkwardly across page breaks by enforcing:
     ```css
     .dialogue-card, .log-item {
       page-break-inside: avoid;
       break-inside: avoid;
     }
     ```
   - **Section Headers & Dividers:** Keep section headings attached to their succeeding content:
     ```css
     .section-divider, .section-title {
       page-break-after: avoid;
       break-after: avoid;
     }
     ```
   - **Summary Page Balancing:** When grouping executive summary sections (e.g. Metadata, Matrix, Tech Stack, Milestones, Action Items) into dedicated pages before a transcript:
     - Check for trailing micro-orphans: ensure a list or card group does not spill 1-2 orphan lines onto a new page just before a section page-break.
     - Eliminate bottom void: if an executive summary page has 20-30% empty space at the bottom, adjust card internal padding (e.g., from `8px` to `12px`), row gaps, and typography line-height so the content breathes comfortably and visual weight is balanced across the page.

5. **Render with Headless Chrome:**
   - Execute:
     ```bash
     google-chrome --headless --disable-gpu --no-sandbox --no-pdf-header-footer --print-to-pdf=<output.pdf> <input.html>
     ```
   - **Crucial Flag:** Always include `--no-pdf-header-footer`. Without this, Chromium stamps the file path, date/time, and unformatted page numbers at the top and bottom.

6. **Verify Page Count & Flow (PyMuPDF / pdfinfo / pdftoppm):**
   - Check page count and metadata via `pdfinfo <output.pdf>`.
   - If an unexpected trailing page occurs with only 1-2 lines or a single section, adjust font sizes (e.g. 10pt -> 9.5pt) or container paddings to achieve a balanced, deliberate page count.

7. **Visual & Proofreading Inspection via `vision_analyze`:**
   - Render page previews to PNG via `pdftoppm`:
     ```bash
     pdftoppm -png -r 150 -f 1 -l 4 output.pdf /tmp/preview/page
     ```
   - Inspect key pages with `vision_analyze` to verify:
     - Text legibility, contrast, and zero clipping/overflow along container borders.
     - Vertical balance: check that early executive pages do not leave awkward empty voids or truncated sections.
     - Zero typos, proper capitalization of corporate and technical terms, and correct formal syntax (e.g. EYD/PUEBI).
     - Mathematical reconciliation: verify that all arithmetic in tables, percentage shares, formulas, and line items calculate exactly to the displayed sums.

## Core Rules & Constraints

- **No Signatures / No Stamps:** Never include signature blocks, sign lines, or stamp graphics in generated PDFs unless explicitly commanded by the user. Use a dark executive sign-off text card for engineering/governance authorization.
- **Tone & Text:** Plain-text arrows (`->`), no LaTeX in chat/text, avoid robotic em dashes in Indonesian copy. Keep badge/header wording aligned with user direction.
- **Zero-Typo & Data Precision:** Reconcile data against primary sources (e.g. API output, database rows) before rendering. Never fabricate placeholder numbers, and ensure real email usernames or technical aliases are preserved accurately without false autocorrection.
- **Native Delivery:** Return the generated PDF via `MEDIA:/absolute/path/to/file.pdf` for direct download on WhatsApp/Telegram.
