# Mobile Zero-Overflow Form & Print-to-PDF Pagination Discipline

This reference documents proven patterns and strict technical invariants discovered when building mobile-first HTML applications (360px–412px viewports) and generating structured executive multi-page PDF documents.

---

## Part 1: Mobile Zero-Overflow Form Discipline (360px–390px Viewports)

### 1. The `100vw` & Fixed Horizontal Offset Trap
- **Trap:** Setting `width: 100vw` or combining `left: 8px; right: 8px; width: 100vw` on floating bottom bars.
- **Mechanism:** In CSS, `100vw` includes the viewport vertical scrollbar width. On mobile or narrow windows, `100vw` + padding/margins forces the container outside the viewport, causing severe horizontal overflow and clipping off the rightmost 20% of child elements.
- **Rule:** Use `left: 8px; right: 8px; width: auto;` or `left: 0; right: 0; width: 100%;` with strict `box-sizing: border-box`.

### 2. Segmented Tab Switcher (50-50 Equal Width)
- Never rely on content-sized tabs on mobile.
- Use `display: flex; width: 100%;` with children having `flex: 1 1 0; min-width: 0; width: 50%;` and `text-overflow: ellipsis; white-space: nowrap; overflow: hidden;`.
- Alternatively, `display: grid; grid-template-columns: 1fr 1fr; width: 100%;`.

### 3. Preset Button Grids (4-Pill Horizontal Rows)
- **Trap:** Using `grid-template-columns: repeat(4, 1fr)` with large gaps or long labels, which causes the 4th button (e.g. `100K`) to be pushed off-screen.
- **Fix:** Use `display: flex; gap: 3px; width: 100%;` with `.pill-btn { flex: 1 1 0; min-width: 0; font-size: 9px; padding: 5px 0; text-align: center; }`.

### 4. Form Controls & `<select>` Intrinsic Sizing
- Long `<option>` labels can expand a `<select>` box beyond the screen width if `max-width: 100%` and `overflow: hidden; text-overflow: ellipsis;` are not explicitly defined.
- Always apply:
```css
input, select, textarea {
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}
```

---

## Part 2: High-Density Executive Print-to-PDF Pagination (HTML → Headless Chrome)

### 1. Sizing and Page Break Control
- Defaulting to unconstrained page breaks causes orphaned formula boxes or KPI blocks on empty pages.
- **Page Margin Rule:** Use `@page { size: A4 portrait; margin: 14mm 14mm 14mm 14mm; }`.
- **Target Page Budget:** Design each logical section to fit strictly within a predefined integer page count (e.g., 3 pages total):
  - **Page 1:** Header Banner, Executive Summary, Problem Statement Table, Amortization Formula, and 4 KPI Cards.
  - **Page 2:** Logic Flowchart (Mermaid), Real Simulation Table, and Monthly/Annual Projections.
  - **Page 3:** Value Proposition Grid (2x2), 4-Step SOP, Management Recommendations, and Sign-off Footer.

### 2. Chromium Headless PDF Generation Command
```bash
google-chrome --headless=new --no-sandbox --disable-gpu \
  --print-to-pdf=/path/to/output.pdf \
  --print-to-pdf-no-header \
  file:///path/to/document.html
```

### 3. Visual Multi-Page PDF Verification with pdftoppm
Always extract rendered pages to PNG and verify with `vision_analyze` to ensure zero empty/orphaned pages:
```bash
pdftoppm -png -r 150 /path/to/output.pdf /path/to/page
```
Verify every single page image (`page-1.png`, `page-2.png`, etc.) for visual balance, typography hierarchy, and non-clipping before finalizing.
