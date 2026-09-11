---
name: document-builder-ux-architecture
description: Use when designing resume, CV, or document builders.
version: 1.0.0
metadata:
  hermes:
    tags: [document-builder, cv-builder, resume-ats, product-design, live-preview, html2pdf, docx-export]
    category: custom
---

# Document & ATS Resume Builder UX Architecture

Standardized architectural patterns and UX principles for building high-converting, parser-compliant document, resume, and CV generators with live split-screen preview and multi-format export.

---

## 1. Downstream Parser & Export Invariants (The Non-Negotiables)

When designing tools whose outputs are processed by automated parsers (ATS like Workday, Taleo, Greenhouse, Lever) or printed via client-side engines (`html2pdf.js` / `html2canvas` / `docx.js`):

### The 1-Column Linear Vertical Rule
- **Never design asymmetric multi-column or sidebar layouts** (e.g. 30% left rail, 70% right body) for ATS documents.
- **Mechanism:** ATS text extraction parsers read documents horizontally across the full page width. Multi-column text gets interleaved line-by-line, corrupting contact details and mixing sidebar skills into job bullet points.
- **PDF Engine Mechanism:** Client-side HTML-to-PDF renderers (`html2canvas`) cannot reliably calculate page breaks across tall, unbalanced flexbox columns, producing split text lines and cut-off headers.
- **Rule:** All resume templates must maintain a **strictly linear 1-column layout**. Template variation must come from typographic scale, header alignment, section dividers, margins, and restrained accent colors.

### A4 Page Boundary & Overflow Monitor
- Recruiters review resumes in 6–7 seconds. A document that accidentally spills over to 1.1 pages (with 2 trailing lines on page 2) signals poor executive communication.
- **Live Height Meter:** Calculate live DOM height of `#resumePaper` relative to standard A4 scale (~1,050px–1,120px at 96 DPI).
- **Visual Feedback:** Display an active status badge in the preview toolbar: `1.0 Halaman (Optimal)` vs `1.3 Halaman (Peringatan: Potensi terpotong 2 halaman)` with a dashed page-break indicator on the canvas.
- **CSS Isolation:** Apply `break-inside: avoid; page-break-inside: avoid;` to every repeatable item container (`.cv-item`).

### Semantic Content Hygiene
- Avoid icon-only links or icon glyph fonts inside anchor tags. ATS parsers either drop icons or transcribe them into junk characters. Use clear text labels: `linkedin.com/in/username` or `GitHub: github.com/user/project`.
- Strip bloated query strings (e.g. `?ref=...`, `?utm_...`) from contact and project URLs.

---

## 2. Real-Time Scoring & Heuristic Feedback Architecture

### Performance Cadence
- **Debounce 150ms–200ms:** Never run dictionary lookup, action-verb parsing, and regex pattern matching synchronously on `oninput`. Debounce calculations to preserve sub-16ms frame times and prevent typing lag.
- **RAF for Animation:** Use `requestAnimationFrame` strictly for visual progress ring and numeric counter transitions.

### Progressive Disclosure UX Pattern
- **Floating Header Pill:** Place a compact, sticky score badge in the top navigation bar: `[ 85/100 • Sangat Siap ATS ]` with a dynamic SVG circular progress ring (Red < 60, Yellow 60–79, Green >= 80).
- **Offcanvas Audit Drawer:** Clicking the badge slides out a dedicated drawer from the right. This prevents form inputs from being pushed down the page.
- **Actionable Deep-Links:** Each audit item provides a `Perbaiki` button that auto-scrolls to and focuses the exact target input field.

### 100-Point ATS Heuristic Model
1. **Profile & Contact Integrity (20 pts):** Full name, target role, valid email/phone format, location, professional summary (30–120 words).
2. **Experience & Action Verbs (25 pts):** >= 1 validated role; bullet points initiated with strong active verbs (bilingual dictionary check: ID *Memimpin, Merancang, Mengoptimalkan*; EN *Architected, Engineered, Led, Accelerated*).
3. **Quantified Outcomes (20 pts):** Regex detection of metrics and numbers (`/\b(\d+[\d,.]*%?|\$\d+|Rp\s*\d+|\d+\+?|\d+\s*(x|persen|karyawan|users?|klien|proyek))\b/i`) in >= 60% of bullet points.
4. **Skill Taxonomy (15 pts):** Hard Skills (>= 5), Tools/Platforms (>= 3), Soft Skills (>= 3).
5. **Education & Depth (10 pts):** Institution & degree; at least 1 Project or Certification.
6. **Formatting Hygiene (10 pts):** Zero empty bullets; clean URLs.

---

## 3. Template Archetypes & Styling Parity

Maintain strict 1-column layout across all templates while supporting distinct industry personas:

| Template | Primary Audience | Header Structure | Typographic Hierarchy | Section Divider |
|---|---|---|---|---|
| **Harvard Classic** | Corporate, Finance, BUMN, Legal, Academia | Center-aligned, bullet dot (`•`) separator | Times New Roman or Garamond (Serif) | 1px solid black border-bottom |
| **Modern Tech** | Software, DevOps, Startup, Product Design | Left-aligned, subtle color bar, contrast role tag | Inter or Calibri (Geometric Sans) | 2px solid accent color (Navy/Slate Blue) |
| **Executive** | C-Level, VP, Senior Consultant, Director | Split horizontal (Name/Title left, Contact grid right) | Merriweather or Georgia (Warm Semi-serif) | Tracked uppercase header with double line |

### DOCX Synchronization
Always pair CSS classes on the preview canvas with an exported `DOCX_TEMPLATES` configuration dictionary (`docx.js` alignments, border colors, font families) so Word downloads match the on-screen preview.

---

## 4. Data Persistence & Backward Compatibility

### Versioned Envelope Pattern
Always wrap exported JSON profiles in a versioned envelope:
```json
{
  "app": "ats_cv_generator",
  "version": 2,
  "exportedAt": "2026-09-09T08:00:00.000Z",
  "template": "harvard",
  "font": "cv-font-calibri",
  "data": {
    "fullName": "...",
    "targetRole": "...",
    "experiences": [],
    "educations": [],
    "projects": [],
    "certifications": []
  }
}
```

### Zero-Crash Normalization Adapter
Before loading imported JSON or `localStorage` data into application state, run it through an adapter:
```javascript
function normalizeState(raw) {
  const source = raw.data ? raw.data : raw;
  return {
    fullName: source.fullName || '',
    targetRole: source.targetRole || '',
    experiences: Array.isArray(source.experiences) ? source.experiences : [],
    educations: Array.isArray(source.educations) ? source.educations : [],
    projects: Array.isArray(source.projects) ? source.projects : [],
    certifications: Array.isArray(source.certifications) ? source.certifications : []
  };
}
```

---

## 5. Flagship Differentiators (Jobscan / Resume.io Level)
- **Job Description Keyword Matcher:** Drawer where users paste a job posting; client-side tokenization extracts matched vs missing keywords with a 1-click `+ Add to Skills` button.
- **STAR Formula Suggestion Assistant:** Contextual prompt chips (*Situation, Task, Action, Result*) next to achievement inputs.
- **Reorderable & Toggleable Sections:** Up/Down move buttons and visibility toggles per section so fresh graduates (Education/Projects first) and experienced professionals (Experience first) configure optimal hierarchy.
