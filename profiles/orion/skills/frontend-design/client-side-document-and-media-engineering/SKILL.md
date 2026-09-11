---
name: client-side-document-and-media-engineering
description: Use when building client-side document export or web media.
version: 1.0.0
metadata:
  hermes:
    tags: [frontend, export, pdf, docx, media, video, embeds, html2pdf]
    category: frontend-design
---

# Client-Side Document and Media Engineering

This skill provides proven procedures and strict technical invariants for client-side document generation (PDF via html2pdf.js, DOCX via docx.js) and resilient web media embedding (YouTube Shorts, video players, hero carousels).

## When to Use

- Building single-page web applications that export documents directly in the browser (resumes, CVs, invoices, reports) to PDF or Word (.docx).
- Embedding YouTube Shorts or third-party videos on commercial landing pages without risking broken players.
- Debugging or preventing "Error 153: Video player configuration error" on embedded video iframes.
- Fixing disappearing background images or pitch-black screens in legacy hero carousels (BizPage, Bootstrap, jQuery).

---

## 1. Client-Side Document Export (PDF & DOCX)

### The `docx.js` CDN Bundle Path Trap
- **Trap:** Referencing `https://cdn.jsdelivr.net/npm/docx@8.5.0/build/index.js` or generic root paths returns HTTP 404.
- **Mechanism:** In the npm `docx` package, the browser UMD bundle path differs across major versions:
  - For `docx@8.x`: The file is `build/index.umd.js` (`https://cdn.jsdelivr.net/npm/docx@8.5.0/build/index.umd.js`).
  - For `docx@9.x`: The file is `dist/index.umd.cjs` (`https://cdn.jsdelivr.net/npm/docx@9.7.1/dist/index.umd.cjs`).
  - Always verify `package.json` (`main` / `browser` / `exports` fields) via curl before embedding CDN scripts into client-side generators.
- **Rule:** Never use `build/index.js` for `docx`. Always specify `build/index.umd.js` (v8) or `dist/index.umd.cjs` (v9).

### Client-Side PDF Generation via html2pdf.js
- For clean A4 document output (such as ATS resumes or invoices):
```javascript
const opt = {
  margin: [10, 10, 10, 10], // mm [top, left, bottom, right]
  filename: filename,
  image: { type: 'jpeg', quality: 0.98 },
  html2canvas: { scale: 2.5, useCORS: true, letterRendering: true },
  jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' },
  pagebreak: { mode: ['avoid-all', 'css', 'legacy'] }
};
html2pdf().set(opt).from(element).save();
```
- **ATS Resume Layout Rule:** Always enforce single-column linear flow for ATS CVs. Avoid multi-column floating boxes, graphics, or nested tables that disrupt programmatic OCR/parser reading order.
- **The html2canvas Box-Shadow Capture Artifact in PDF Export:**
  - *Trap:* Rendering the document canvas with CSS `box-shadow` on screen (e.g. `box-shadow: 0 10px 25px rgba(0,0,0,0.1)`) without disabling it during PDF generation.
  - *Mechanism:* `html2canvas` captures the blurred drop-shadow into the canvas stream, embedding dirty, blurred grey borders along the outer margins of the downloaded PDF.
  - *Rule:* Temporarily strip `element.style.boxShadow = 'none'` before calling `html2pdf().set(opt).from(element).save()`, and restore the original shadow style inside the promise `.then()` and `.catch()` handlers.
- **Native Print Stylesheet (`@media print`) for Client-Side Document Generators:**
  - *Trap:* Omitting `@media print` when building client-side document generators.
  - *Mechanism:* When users press `Ctrl+P` / `Cmd+P` or select "Save as PDF" from the browser menu, the browser prints the full application shell (navbar, input forms, toolbars, buttons) instead of the clean document.
  - *Rule:* Always include a dedicated `@media print` block that hides all application chrome (`.app-navbar`, `.form-panel`, `.mobile-tab-banner`, `.preview-toolbar`) and forces the document canvas (`.a4-paper`) to `width: 100% !important; box-shadow: none !important; border: none !important; padding: 0 !important; margin: 0 !important;`.

### The `docx.js` OpenXML Paragraph Border Trap (`value` vs `style`)
- **Trap:** Specifying `border: { bottom: { value: 'single', size: 6, color: '...' } }` renders with NO horizontal divider lines in Microsoft Word, Google Docs, and WPS Office.
- **Mechanism:** In the OpenXML Word processing specification (`word/document.xml`), border elements require the `w:val` attribute (e.g. `<w:bottom w:val="single" .../>`). The `docx.js` library uses the property name `style: BorderStyle.SINGLE` (or `style: 'single'`). When `value: 'single'` is passed by mistake, `docx.js` completely omits `w:val` from the XML output (`<w:bottom w:color="..." w:sz="..."/>`). Microsoft Word and office suites treat a border without `w:val` as invalid or disabled and completely suppress the line.
- **Rule:** Always use `style: BorderStyle.SINGLE` when declaring paragraph borders in `docx.js`:
```javascript
border: {
  bottom: {
    style: BorderStyle.SINGLE,
    size: 12, // 1.5 pt
    color: '0F172A',
    space: 4
  }
}
```

### The Right-Aligned Date Tab-Stop Wrapping Trap in Word (`\t` vs 2-Column Borderless Table)
- **Trap:** Placing right-aligned dates in the same paragraph as the job title or company using a tab character `\t` (e.g. `new TextRun({ text: '\t' + dateStr })`).
- **Mechanism:** In real resumes, candidate job titles, company names, and locations are frequently long (e.g., *Warehouse & Inventory Control Staff • PT SiCepat Ekspres / Shopee Express Hub (Tangerang)*). Without an explicitly defined right tab stop anchored to the exact page margin, Word pushes the tab onto a second line, and narrow remaining space forces the date words to wrap across lines (e.g. `Jan 2021 –` on line 2 and `Sekarang` on line 3).
- **Rule:** Never rely on raw `\t` tab stops for right-aligned dates in DOCX item headers. Encapsulate each experience, project, or education header inside a borderless 2-column `Table` with `WidthType.PERCENTAGE`:
  - **Left Cell (75–78% width):** Title, Company/School, Location, and Grade/GPA.
  - **Right Cell (22–25% width, `alignment: AlignmentType.RIGHT`):** Date or Year range (`italics: true`).
  This guarantees dates remain strictly on a single line and stay anchored to the right margin across all Word desktop, mobile, Google Docs, and WPS viewers.

### The `docx.js` Variable Scope Trap in Conditional Blocks
- **Trap:** Defining shared table border or cell constants (`noBorder`, `headerDivider`, `cellBorders`) inside conditional branches (such as `if (state.showPhoto && state.profilePhoto)`).
- **Mechanism:** When the condition evaluates to false (e.g. candidate disables photo), subsequent sections (experience, education, or project 2-column tables) that reference `noBorder` throw an unhandled `ReferenceError: noBorder is not defined`, crashing the document export pipeline mid-generation.
- **Rule:** Always define shared borders, cell styles, and formatting constants (`const noBorder = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };`) at the top of the generator function scope before any conditional branching.

### The `docx.js` Dynamic Font Selection Omission Trap
- **Trap:** Allowing users to choose resume fonts (Calibri, Arial, Times New Roman, Garamond, Inter) in the web UI, but constructing `new Document({ sections: [...] })` without declaring document-level font styles.
- **Mechanism:** In OpenXML, if `styles.default.document.run.font` is not explicitly declared, Microsoft Word, Google Docs, and WPS Office ignore the UI's selected font and fall back to the user's localized default template font (typically Calibri or Times).
- **Rule:** Map the client-side font selector to canonical OpenXML font names and inject it into the root `Document` constructor styles:
```javascript
const fontMap = {
  'cv-font-calibri': 'Calibri',
  'cv-font-arial': 'Arial',
  'cv-font-times': 'Times New Roman',
  'cv-font-garamond': 'Garamond',
  'cv-font-inter': 'Arial'
};
const chosenFont = fontMap[state.font] || 'Calibri';

const doc = new Document({
  styles: {
    default: {
      document: {
        run: {
          font: chosenFont
        }
      }
    }
  },
  sections: [{
    properties: { page: { margin: { top: 1000, right: 1000, bottom: 1000, left: 1000 } } },
    children: children
  }]
});
```

### Monochromatic Professional ATS Palette (No Random Hyperlink Blue)
- **Rule:** Never style non-clickable metadata (such as GPA, exam scores, dates, or school names) with bright hyperlink blue (`#0284c7` or `#2563eb`). In ATS resume evaluation and printed copies, bright blue metadata confuses recruiters and looks like broken dead links. Restrict blue accents strictly to interactive URLs (`linkedin.com/...`, `github.com/...`) and keep all resume body metadata in formal dark slate / charcoal (`#334155` or `#0f172a`).

---

## 3. ATS Resume & CV Client-Side Architecture

### ATS 1-Column Strict Invariant
- **Rule:** Never use multi-column CSS grids, flex sidebars, floating boxes, or icon graphics for content in ATS resumes. Systems such as Workday, Taleo, Greenhouse, and Lever parse linear horizontal streams; multi-column layouts scramble text order.
- **Section Hierarchy:** Keep uppercase, standardized headings: `PROFESSIONAL SUMMARY`, `WORK EXPERIENCE`, `KEY PROJECTS & PORTFOLIO`, `EDUCATION`, `SKILLS & COMPETENCIES`, `CERTIFICATIONS & TRAINING`.
- **Bullet Points (STAR Formula):** Every work bullet point must pair an action verb (`Led`, `Optimized`, `Developed`, `Meningkatkan`, `Merancang`) with a quantifiable metric (`35%`, `$12,000`, `2.5M transactions`).

### Adaptive Multi-Tier Education Model (SD, SMP, SMA, SMK to Higher Ed)
- **Problem:** Many ATS resume builders hardcode collegiate terminology (`Universitas`, `Gelar`, `IPK/GPA`, `Topik Skripsi`), alienating high school, vocational, or primary school graduates and producing broken or awkward resume headers.
- **Adaptive Level Selector:** Provide an adaptive `edu.level` switch per education block:
  - `college`: *Nama Universitas/Politeknik*, *Gelar & Jurusan*, *IPK/GPA*, *Prestasi/Topik Skripsi*.
  - `smk`: *Nama Sekolah/SMK*, *Jurusan/Bidang Keahlian* (TKJ, RPL, Akuntansi, Otomotif), *Rata-rata Nilai Ijazah/Rapor*, *Pengalaman PKL / Prakerin / Prestasi*.
  - `sma`: *Nama Sekolah/SMA/MA*, *Peminatan/Jurusan* (MIPA/IPS/Bahasa), *Rata-rata Nilai Ujian/Ijazah*, *Kegiatan Organisasi/Prestasi* (OSIS, Paskibra).
  - `smp` / `sd`: *Nama Sekolah*, *Tahun Kelulusan*, *Nilai Rata-rata/Akhir*, *Kegiatan Ekstrakurikuler*.
- **Render Invariant (Preview, PDF & DOCX):**
  - For vocational/high school: render headings as `SMK - [Jurusan]` or `SMA - [Peminatan]`.
  - Format scores adaptively: use `(Nilai Rata-rata: X)` or `(Nilai Ijazah: X)` instead of `(IPK: X)`.
  - Treat PKL / Prakerin (Internships) and student technical projects with equal first-class status under experience/projects so vocational candidates achieve top ATS relevance for entry-level operator, admin, cashier, and technician positions.
  - Always provide a dedicated, realistic entry-level vocational preset profile (`Lulusan SMA / SMK`) in template libraries alongside collegiate roles.

### Zero-Friction National Education Catalog (PDDikti & Kemendikbud Dual-Path Picker)
- **Problem:** Users dread typing long official institution/program titles (e.g., *Universitas Indonesia*, *S1 Teknik Informatika*, *Teknik Komputer dan Jaringan (TKJ)*), leading to typos, abandoned forms, or inconsistent ATS headings.
- **Dual-Path Architecture:**
  1. **Native Datalists:** Bind inputs to `<datalist id="...">` (`listUniversities`, `listSmkMajors`, `listCollegeMajors`, `listSmkSchools`, etc.) for zero-latency browser autocomplete on click/typing without any network roundtrip.
  2. **Categorized Modal Picker:** Provide an interactive modal (`openDiktiModal`) with instant search and tabs (*PTN/PTS*, *Jurusan S1/D3*, *Jurusan SMK*, *Sekolah*) so users can complete both institution and major with a single click.
  3. **Offline Invariant:** Embed catalog datasets directly in client-side code/DOM to avoid CORS blocks, rate-limits, and downtime from government frontend endpoints.
- **The 300,000+ Schools DOM Memory Exhaustion Trap:**
  - *Trap:* Attempting to dump all ~220,000–300,000+ national schools (SD, SMP, SMA, SMK) directly into raw HTML `<datalist>` or `<option>` tags.
  - *Mechanism:* Allocating hundreds of thousands of DOM option nodes inflates the HTML payload by 20–30MB, consuming hundreds of MBs of browser heap, causing Google Chrome, Edge, and mobile browsers to freeze or throw "Page Unresponsive" / out-of-memory crashes.
  - *Fix (Hierarchical Administrative Synthesis Pattern):* Combine a curated, pre-indexed offline datalist of top PTN/PTS and model schools with a **Hierarchical Dapodik Explorer (38 Provinces -> 514 Regencies/Cities -> School Level -> State/Private Status -> Index/Foundation Name)**. This dynamically synthesizes the canonical Kemendikbud name (e.g. `SMK Negeri 1 Kota Bandung`, `SMA Negeri 8 Jakarta Selatan`) on the fly with zero DOM bloat and 100% geographic coverage.
- **Bootstrap Modal Background Transparency & Text Collision Bug:**
  - *Trap:* Opening Bootstrap modals over rich form editors causes underlying form text to bleed through the modal.
  - *Mechanism:* In certain Bootstrap CSS builds or custom stylesheets, `.modal-content` lacks an explicit solid background declaration, leaving it translucent and colliding with underlying inputs and buttons.
  - *Rule:* Always explicitly declare `#modalId .modal-content { background-color: #ffffff !important; border: 1px solid #cbd5e1 !important; box-shadow: 0 15px 35px rgba(0,0,0,0.25) !important; }` and ensure child cards inside the modal have explicit opaque backgrounds.
- **Simplicity Over Modal Pickers:** If the user or product specification prioritizes speed and low cognitive friction ("biar user yang ketik aja"), do not impose heavy modal dialogs or multi-step geographic selectors onto simple text fields; rely on clean standard inputs with smart contextual placeholders (e.g. `SMK Negeri 1 Jakarta`, `Universitas Indonesia`) and lightweight native `<datalist>` autocomplete.

### Multi-Industry & Non-Tech Role Presets (Beyond IT/Tech Bias)
- **Problem:** Many resume builders default solely to tech (software engineering, UI/UX) and digital marketing presets, leaving high-volume applicant demographics (F&B, retail sales, office administration, warehouse logistics) with zero guidance on how to write metric-driven STAR bullet points for non-desk or operational roles.
- **Rule:** Provide categorized, multi-sector preset profiles that illustrate quantified accomplishments in each field:
  - *Restoran, Kafe & Ritel:*
    - **F&B / Barista / Resto Crew:** Highlight espresso calibration, drink speed of service (<3.5 min), volume (350+ orders/day), waste reduction (-15%), food hygiene (HACCP), and customer satisfaction (CSAT 97%). Include tools like Moka/Majoo POS, grinder, and certifications (BNSP Barista, HACCP).
    - **Sales, Kasir & Ritel Toko:** Highlight sales quota attainment (115%), daily cashier volume (150+ transactions), zero cash discrepancy, upselling/cross-selling, visual merchandising (+18% impulse buy), and BNSP Ritel certification.
  - *Kantor & Operasional:*
    - **Administrasi & Keuangan:** Highlight accounts payable/receivable (AR/AP), petty cash reconciliation (100% balanced), tax invoice issuance (e-Faktur PPN, PPh 21/23), advanced Excel (Pivot, VLOOKUP/XLOOKUP), Accurate Accounting, and Brevet Pajak A/B.
    - **Gudang, Logistik & Ekspedisi:** Highlight warehouse picking/packing volume (400-500 packages/shift), low dispatch error rate (<0.05%), stock opname inventory accuracy (0% shrinkage), FIFO/LIFO, WMS, and SIO Forklift / K3 certification.
  - *Teknologi & Bisnis Digital:* Software Engineer / IT, Marketing & Growth Specialist.
  - *Lulusan Baru & Kejuruan:* Fresh Graduate Sarjana, Lulusan SMA/SMK Kejuruan (admin, operator, junior technician).

### Live Split-Screen & Client-Side Engines
- **Debounced Sync:** Use a 150–200ms debounce on form input events before re-rendering the live A4 preview to prevent DOM thrashing and preserve 60 FPS typing.
- **Defensive Target Element Null-Guards in Preview Loops:**
  - *Trap:* Adding a new dynamic UI feature (such as class toggles `.classList.add('has-photo')` or styling changes on header containers) without defensive null checks.
  - *Mechanism:* If a target preview element ID is missing, misspelled, or conditionally omitted, invoking properties or methods on `null` throws an unhandled `TypeError`. This silently crashes the entire synchronization loop at that line, preventing subsequent fields (name, role, contacts, summary) from ever reaching the live preview and stranding the document on stale default placeholders (`NAMA LENGKAP ANDA`).
  - *Rule:* Always guard all preview DOM mutations with defensive checks (`if (cvHeaderBox && prevPhotoFrame) { ... }`) or optional chaining, ensuring that any missing presentation node fails open without halting the core text update pipeline.
- **Optional Formal Profile Photo Pattern (Dual-Mode ATS vs Local HRD):**
  - *Context:* Global tech/multinational ATS systems (Workday, Taleo, Lever) discourage photos to prevent bias and OCR degradation. Conversely, domestic Indonesian job markets (BUMN, government agencies, banking, retail, front-office, customer service) frequently expect a 3x4 formal pasfoto with neat attire and clean backdrop.
  - *Dual-Mode Architecture:* Make photo upload **100% optional** with an explicit master switch: `[✓] Tampilkan Foto di CV`. When toggled OFF: header renders 100% linear text with zero empty image containers or broken tags (pure ATS compliance). When toggled ON: header switches dynamically via CSS (`.cv-header.has-photo`) to a 2-column flexbox containing contact metadata on the left and a 3x4 formal photo frame on the right. Content below the header divider remains strictly single-column.
  - *Photo Frame Sizing & Aspect Ratio Standards:*
    - Avoid undersized ~70px thumbnail frames that leave awkward dead space below the photo and look drowned out against bold candidate names.
    - *Headroom & Portrait Image Cropping Pitfall:* Setting `object-fit: cover` with default `object-position: center` (or 50% 50%) inside square or short frames shears off the crown of the head/hair on portrait photos. Formal passport/ID photos place the head in the upper 30–40% of the canvas; vertical midpoint cropping clips off the hair. Always declare `object-position: center 8%;` (or `top center`) on formal headshots and preview thumbnails to preserve safe headroom.
    - *Standard Formal Portrait 3:4:* Size at `105px x 135px` (or `108px x 140px` on Executive) with `1.5px–2px solid #0f172a` border, `border-radius: 6px`, subtle shadow, and `object-fit: cover; object-position: center 8%;`. In Word (`docx.js`), use `{ width: 95, height: 122 }`.
    - *Square 400x400 / 1:1 Aspect Ratio:* When modern corporate, digital, or symmetrical profile framing is desired (`400x400 px`), size at `100x100px` (or `105x105px` on Executive) with `aspect-ratio: 1 / 1; border-radius: 6px; object-fit: cover; object-position: center 8%;`. In the form upload widget, render thumbnail preview at 60x60px (1:1). In Word (`docx.js`), set `transformation: { width: 95, height: 95 }`.
  - *Zero-Server Client-Side Persistence:* Store uploaded images via `FileReader.readAsDataURL()` as a Base64 data URI string. Persist the Base64 payload directly in `localStorage` alongside form state and bundle it inside JSON backup archives (`Cadangan_Profil.json`) so users never lose uploaded photos across sessions or machines.
  - *DOCX ImageRun Export Integration:* For Word (`docx.js`), convert the Base64 image payload into a binary `Uint8Array` via `atob()`. Encapsulate the header inside a borderless 2-column `Table` with `WidthType.PERCENTAGE` (78% text, 22% photo) containing an `ImageRun({ data: bytes, transformation: { width: 88, height: 118 } })`. Wrap in a try/catch block with automatic fallback to standard text paragraphs if image parsing or binary conversion encounters corrupted data.
- **Real-Time ATS Readiness Scoring:** Calculate an instant 0–100 quality score client-side checking:
  1. Contact completeness (email, phone, location, LinkedIn).
  2. Summary word count (optimal: 30–100 words).
  3. Action verb detection via word boundary regex.
  4. Metric quantification detection via regex `\b(\d+%|\$\d+|Rp|\d+\+|\d+x)\b`.
  5. Technical vs Soft skills balance.
  6. Value-add sections completeness (Languages & Certifications).
- **The ATS Action Verb & Metric Regex Leading/Trailing Whitespace Trap:**
  - *Trap:* Writing action verb or metric detection regexes with literal boundary spaces (e.g. `/ (memimpin|mengembangkan|...) /i` or `/ (\d+%) /i`).
  - *Mechanism:* Standard resume formatting dictates that bullet points start immediately with an action verb at index 0 (e.g. `"Memimpin audit stok..."`) and end with metrics right before punctuation (e.g. `"...sebesar 35%."`). Mandatory spaces in regex patterns fail on string start/end boundaries, generating false negatives and docking candidate ATS scores by 15–20 points despite perfectly written STAR bullets.
  - *Rule:* Always use standard word boundary anchors `\b` (`/\b(memimpin|mengembangkan|led|built|...)\b/i`) and handle currency/metric variants (`/\b(\d+[%x+]|\$\d+|Rp\s*\d+|\d+\s*(juta|ribu|user|klien|paket|sku))\b/i`) without mandatory surrounding whitespace.
- **Dynamic Font Class Replacement Trap in Single-Page Apps:**
  - *Trap:* Replacing font classes on a preview element via naive regex (e.g. `className.replace(/cv-font-[a-z]+/g, '')`) while passing bare font names (`calibri`, `arial`) to `classList.add()`, or failing to match the exact CSS class prefix.
  - *Mechanism:* The regex fails to match bare class names, causing subsequent font changes to accumulate multiple font classes on the same element (`.calibri.arial.garamond.times`). CSS cascade rules dictate that whichever class appears last in the stylesheet permanently overrides earlier ones, making the font selector appear broken.
  - *Rule:* Maintain an explicit array of supported font classes (`const ALL_FONTS = ['cv-font-calibri', 'cv-font-arial', ...]`). Before applying a newly selected font, iterate through `ALL_FONTS` with `paper.classList.remove(f)`, ensuring only the exact selected font class remains active.
- **Split-Screen Web App Mobile Responsive Architecture (Two-Tier Navbar & Segmented Switcher):**
  - *Trap:* Keeping desktop-style single-row navbars and relying solely on vertical stacking (`flex-direction: column`) on mobile viewports (<992px) for split-screen apps (Form on left, Live A4 Document on right).
  - *Mechanism:* Single-row navbars overflow horizontally off-screen on 375–390px mobile viewports, pushing critical primary CTAs (`Unduh PDF`, `Unduh Word`) completely out of reach. Furthermore, stacking the document below a long form forces users to scroll 3,000+ pixels just to preview their edits, causing high drop-off and frustration.
  - *Rule:* For split-screen document web apps on mobile:
    1. Adopt a **Two-Tier Mobile Navbar**: Row 1 contains branding and status/score badge; Row 2 contains compact action buttons (`Contoh Profil`, `Data Profil`, `PDF`, `Word`) using short labels (`PDF` / `Word` instead of `Unduh PDF / Unduh Word (.docx)`).
    2. Implement a **Segmented Mobile View Switcher** (`[ 📝 Isi Formulir ]` | `[ 👁️ Pratinjau CV ]`) pinned at the top of the workspace. Toggling between tabs shows/hides `.form-panel` and `.preview-panel` instantly (`body.show-preview`), delivering a native mobile app UX without endless scrolling.
- **The Nested HTML Double-Escaping Trap (`&amp;` in Rendered DOM):**
  - *Trap:* Pre-escaping substrings (e.g. `detail += (detail ? ' — ' + escapeHtml(notes) : escapeHtml(notes));`) that are subsequently interpolated into a template string passing the entire composite through `escapeHtml(detail)`.
  - *Mechanism:* The first `escapeHtml` replaces literal `&` with `&amp;`. When `detail` passes through the outer `escapeHtml`, the `&` in `&amp;` is escaped again into `&amp;amp;`. The browser DOM decodes only the outer entity level, causing literal `&amp;` to appear in the rendered UI (e.g. `Istilah Logistik &amp; WMS` instead of `Istilah Logistik & WMS`).
  - *Rule:* Escape text exactly once at the final boundary before HTML insertion. Keep intermediate variables as plain unescaped strings, and apply `escapeHtml()` only to the final atomic expression or wrapper template. During automated QA, always assert `element.textContent.includes('&amp;') === false`.
- **The Form Reset (`clearAllData`) Incomplete State Mutation Pitfall:**
  - *Trap:* Adding new form sections (e.g. demographics accordion, custom toggle switches, auxiliary contact handles) without updating the form clearing/reset routine.
  - *Mechanism:* When a user clicks "Reset Form" to start fresh, core fields (name, email, experience) clear, but unmapped auxiliary inputs remain populated, leaving stale candidate data in the newly generated document.
  - *Rule:* Whenever a new input or toggle switch is added to a form, immediately update `collectCurrentState()`, `loadState()`, and `clearAllData()` in lockstep to guarantee complete state mutation on reset.
- **URL & Link Attribute Escaping in Dynamic Document Templates:**
  - *Trap:* Interpolating user-provided URLs or handles into `<a href="${url}">` without attribute escaping (e.g. `href="${p.link}"`).
  - *Mechanism:* If a user inputs quotes or special characters, the attribute breaks out of the HTML tag, corrupting surrounding DOM elements or triggering XSS.
  - *Rule:* Always sanitize link URLs and attributes via `escapeHtml(url)` inside `href="..."`, and ensure protocol prefixes are strictly normalized (`https://`).

- **A4 Page Overflow Monitor:** Compare `element.scrollHeight` against standard A4 display height (~1050px–1100px) to warn users in real time when their content exceeds 1.0 page.
- **Client-Side Profile Backup/Restore (JSON):** Provide zero-server JSON export (`Blob` + `createObjectURL`) and import (`FileReader.readAsText`) so users can maintain multiple target CV versions safely on their local machine.
- **Orphaned Punctuation & Line-Break Traps in Metadata Lists (Contact Rows & Tag Strips):**
  - *Trap:* Joining inline items with free-floating bullet elements (`<span class="sep-dot">•</span>`) or applying `display: flex; flex-direction: column` to a container with separator elements causes separator symbols to wrap onto a line by themselves (`orphaned bullets`) or create empty separator rows.
  - *Mechanism:* Standard CSS word-wrapping breaks on whitespace preceding or following `<span class="sep-dot">•</span>`. In constrained containers (like A4 headers or cards), long email/LinkedIn URLs force the trailing separator or next item to break independently.
  - *Fix:*
    1. Enclose each item in an atomic component with `white-space: nowrap; display: inline-flex; align-items: center;`.
    2. Dynamically construct the array of non-empty items in JS and join them via `.join('<span class="sep-dot">•</span>')` or CSS pseudo-elements (`:not(:last-child)::after { content: ' • '; }`).
    3. Never apply `flex-direction: column` to a list that contains horizontal separator nodes without explicitly setting `.sep-dot { display: none !important; }`.
- **Executive Layout Invariant (Clean Authority, Responsive Header & Divider Consistency):**
  - In executive or high-level professional resumes, enforce:
    1. Equalized Section Dividers: All section headings (`SUMMARY`, `EXPERIENCE`, `PROJECTS`, `EDUCATION`, `SKILLS`) must feature identical, high-contrast horizontal dividers (`1.8px–2.5px solid #0f172a`), avoiding partial/faint styling that disappears on print or scan.
    2. Dynamic Header Alignment: When a formal photo is uploaded, header switches to a 2-column flexbox (`.cv-header.has-photo` with text block left, 3x4 photo frame right with solid 2px border). When no photo is present, header smoothly centers with balanced contact distribution (`justify-content: center`).
    3. UI Form Input & Toolbar Padding: Keep select dropdowns (e.g. font pickers, role switchers) sufficiently wide (`min-width: 175px`) so localized labels (e.g. `Arial (Paling Aman)`) never get clipped by browser native select chrome.

- **Standardized Resume Form Controls & Ergonomics (The Flawless ATS Form Pattern):**
  - **Checkbox "Masih Bekerja di Sini" (Current Job):**
    - Never force users to type "Sekarang" / "Present" manually into an end-date text field.
    - Provide a dedicated checkbox `[ ] Masih Bekerja`. When checked: hide/disable end-date inputs, display a clean status badge `✓ Saat Ini (Masih Bekerja)`, and automatically format output to `"Saat Ini"` / `"Present"`.
  - **Segmented Month & Year Selectors vs Free-Text Dates:**
    - Free-text inputs like "Jan 2021" invite inconsistent casing, abbreviations, and separators ("Jan 21", "Januari 2021", "01/2021").
    - Split date inputs into two dedicated `<select>` dropdowns: Month (`Jan` to `Des`) and Year (`1980` to `2030`). This enforces 100% uniform chronological strings across PDF and DOCX exports.
  - **Dedicated "Kemampuan Bahasa (Languages)" Section:**
    - Languages must not be buried inside unstructured free-text skill chips. Provide a dedicated Languages section with:
      - Language Name (with datalist suggestions)
      - Standardized CEFR / Professional Proficiency dropdown: *Penutur Asli (Native / Bilingual)*, *Fasih / Mahir Profesional (Fluent)*, *Tingkat Menengah (Intermediate)*, *Tingkat Dasar (Basic / Elementary)*.
      - Optional test scores / credentials field (e.g. TOEFL, IELTS, JLPT, HSK).
      - Render as a distinct linear subsection in both PDF and DOCX.
  - **Optional Demographics & Physical Attributes Accordion (Domestic / Industrial Gate):**
    - International ATS models reject demographic attributes (age, gender, height/weight, marital status). However, domestic Indonesian manufacturing, plant operators, hospitality, aviation, and local state-owned enterprises (BUMN) frequently mandate them.
    - Isolate demographic fields into an expandable, optional accordion with an explicit explanatory note: *"Isi hanya jika disyaratkan khusus oleh lowongan (manufaktur, perhotelan, BUMN lokal)."*
    - Guard rendering with an explicit toggle: `[ ] Tampilkan Informasi Demografi di Lembar CV`. When disabled, the CV remains 100% compliant with global ATS anti-bias guidelines.
  - **Item Reordering (Move Up / Down Controls):**
    - Every dynamic repeatable item (Experiences, Projects, Education, Languages, Certifications) must feature explicit `▲` (Move Up / Newer) and `▼` (Move Down / Older) buttons.
    - This allows candidates to correct ordering errors and maintain strict reverse-chronological order in seconds without deleting or retyping entire sections.
  - **Dynamic Card Action Bar vs Absolute Positioning Trap (Anti-Collision Header Pattern):**
    - *Trap:* Styling card action controls (delete icon, reorder up/down arrows) with `position: absolute; top: 10px; right: 10px;` inside dynamic item cards.
    - *Mechanism:* In multi-column forms or cards with top-row inputs (e.g. *Perusahaan / Instansi \** in Experience, *Jenjang Pendidikan* dropdown in Education, or *Tahun* in Certifications), absolute action buttons float directly over input borders, dropdown chevrons, and labels. On constrained split-screen or mobile viewports, the trash icon collides directly into the input box or dropdown, causing severe visual overlap, clipped borders, and misclick risks.
    - *Rule:* Never use absolute positioning for card-level actions. Apply a universal dedicated flex header bar (`.item-card-header`) across ALL dynamic item sections (Experience, Projects, Education, Languages, Certifications) with a subtle bottom divider (`border-bottom: 1px solid #f1f5f9`) that cleanly isolates the entry badge (`#1`), item title, and button group (`▲`, `▼`, and a styled inline `🗑 Hapus` button) from the form inputs below. Ensure `.btn-delete-item` uses `display: inline-flex;` with explicit padding and text label. Never update one section while leaving sibling dynamic cards on floating absolute buttons.
  - **Conditional Date Input Clean Replacement Pattern:**
    - *Trap:* Retaining empty or disabled end-date dropdowns alongside an active "Saat Ini" status badge when "Masih Bekerja" is checked.
    - *Mechanism:* Displaying both dropdowns and an active badge in the same column clutters vertical rhythm and confuses users into thinking an end date selection is still required.
    - *Rule:* When "Masih Bekerja" is active, completely hide the end-date month/year dropdowns (`display: none`) and display only the clean status pill (`✓ Saat Ini (Masih Bekerja)`). When unchecked, hide the badge and restore the month and year dropdowns.

  - **White-Label & Custom Brand Decoupling Pattern:**
    - When rebranding or white-labeling generator apps (e.g. replacing generic terminology like "ATS Resume Pro" with a custom brand such as "Papiaw Resume Pro"):
      1. Decouple technical parser compatibility from consumer brand identity: Keep background ATS parser compliance intact in the layout and parsing notes, but rebrand user-facing product titles, navbar brand badges, readiness score indicators (`Skor Papiaw`), audit drawers, and export filenames (`CV_[Name]_Papiaw.pdf`, `CV_[Name]_Papiaw.docx`, `Cadangan_CV_Papiaw_[Name].json`).
      2. Storage Migration Fallback: When updating `localStorage` keys or JSON payload schemas, always implement backward-compatible read fallbacks (`localStorage.getItem('brand_cv_data_v2') || localStorage.getItem('ats_cv_data_v2')`) so user draft data is never lost across brand transitions.

---

## 4. Client-Side Protected Vault & Multi-View Hub Architecture

### Zero-Backend Protected Storage Gateway (The Cyber-Lock & Zero-Knowledge Vault Pattern)
- **Use Case:** Personal developer hubs, portfolio ecosystems, and client-side web platforms (e.g. `papiaw.my.id`) requiring tiered access:
  1. *Public Gateway:* Direct client-side web apps (e.g. CV / Resume Generator).
  2. *Protected Storage (Umum):* Public asset / template vault guarded by an access PIN against automated scraping.
  3. *Restricted Arsenal (Private Tools):* Developer tooling, internal scripts, and CLI utilities guarded by a private Master Key.
- **The Client-Side Hardcoded Plaintext / F12 Console Bypass Vulnerability ("Soft-Lock"):**
  - *Trap:* Storing passwords (`const VAULT_KEYS = { umum: '...', private: '...' }`) or catalog datasets directly in JavaScript source code and relying on CSS `display: none` modals for security.
  - *Mechanism:* Any visitor can view passwords via `View Page Source` (`Ctrl+U`) or bypass the password modal instantly in the browser Developer Tools (F12) console by typing `showView('private')` or setting unlocked flags.
  - *Rule:* Never store plaintext passwords or sensitive catalog payloads in client-side code when true security against inspection is required. Use soft-locks only for non-sensitive anti-crawler deterrents.
- **Zero-Knowledge Military-Grade Cryptographic Vault Architecture (AES-256-GCM + PBKDF2 Web Crypto API):**
  - To achieve unhackable client-side protection on static hosting (Cloudflare Pages, Vercel, VPS Nginx) with zero backend servers:
    1. *Zero Plaintext in Source:* Completely remove passwords from source code. Store protected catalogs exclusively as encrypted ciphertext blobs: `{ salt: '...', iv: '...', ciphertext: '...' }`.
    2. *Cryptographic Key Derivation:* Derive a 256-bit AES-GCM key from the user-entered password and salt using `crypto.subtle.importKey` + `crypto.subtle.deriveKey` with PBKDF2 (100,000 iterations, SHA-256).
    3. *Authenticated Decryption (AES-GCM):* Decrypt the ciphertext with `crypto.subtle.decrypt({ name: 'AES-GCM', iv }, key, ciphertext)`. If the password is correct, plaintext JSON restores and renders. If the password is wrong (even by 1 character), AES-GCM tag verification mathematically fails (`OperationError` / Auth Tag Mismatch), keeping data completely scrambled.
    4. *Defensive Route Guarding (Anti-F12 Console Bypass):* In the view router `showView(target)`, strictly verify that `decryptedVaults[target]` exists in memory. If `null`, refuse view activation, clear the DOM grid, and route to the unlock modal. F12 console executions cannot render anything because the plaintext does not exist in memory.
    5. *Volatile Memory Isolation (Never Store Plaintext in Storage):* Keep decrypted payloads exclusively in volatile JavaScript runtime variables (`let decryptedVaults = { umum: null, private: null }`). Never write decrypted data to `localStorage` or `sessionStorage` where browser storage inspectors or XSS could retrieve it.
    6. *Instant Memory Purge on Lock:* When the user clicks "Lock Vault" or "Kunci Kembali", set `decryptedVaults[target] = null`, wipe the DOM container (`grid.innerHTML = ''`), and remove all session flags.
    7. *In-Browser Re-Key / Password Change Engine:* Provide an in-browser re-encryption utility using `crypto.subtle.encrypt` so the site owner can enter a new custom password, re-encrypt the in-memory data with a fresh random salt and IV, and copy the new ciphertext JSON directly into their repository.
- **The Modal Close Variable Overwrite / Premature State Reset Trap:**
  - *Trap:* Invoking a modal teardown function `closeModal()` before routing `showView(activeTargetVault)`.
  - *Mechanism:* `closeModal()` sets `activeTargetVault = null`. When `showView(activeTargetVault)` is invoked immediately after, it receives `null`, causing the view switcher to fail silently with no active view visible (`isUmumActive: false`).
  - *Rule:* Always capture the target route into a local constant (`const target = activeTargetVault;`) before invoking modal teardown, then route using `showView(target)`.
- **The Production UI Password Hint-Box / Default Credential Leak Trap:**
  - *Trap:* Retaining development hint boxes, default password badges, or helper text (e.g. `Kunci Dekripsi Bawaan: ...` or `Password Default: <code>...</code>`) on cards or unlock modals.
  - *Mechanism:* Even with unbreakable AES-256 zero-knowledge encryption, displaying or hinting the decryption key directly in the UI completely defeats access gating, allowing any visitor to copy the key and unlock restricted vaults immediately.
  - *Rule:* Never leave password hint boxes, default credential tags, or placeholder key strings in user-facing UI or client JavaScript. In production, modal footers must display only generic security status disclaimers (e.g. `Terproteksi Zero-Knowledge AES-256-GCM. Akses hanya untuk pemilik kunci`). Ensure all default key strings are 100% stripped from cards, forms, and scripts prior to delivery.

---

## 5. Client-Side Code Obfuscation, Anti-Inspect & DevTools Hardening

### The Dual-Build Maintainability Invariant
- **Trap:** Running in-place destructive obfuscation, minification, or string mangling directly onto the primary working source file.
- **Mechanism:** Once JavaScript is obfuscated with control-flow flattening, hexadecimal identifier renaming (`_0x1a2b`), and string array encoding, reverse-engineering or maintaining your own code becomes nearly impossible. Any future bug fix or feature addition requires recreating the code from scratch.
- **Rule:** Always maintain two strictly separated build targets:
  1. `src/` or `index.dev.html`: The pristine, well-structured, human-readable development source for ongoing feature work and debugging.
  2. `dist/` or `index.html`: The fully minified, obfuscated, and hardened production artifact generated via build scripts. Never make manual edits to the obfuscated production artifact.
- **Build Automation Template:** See `templates/build_armor.py` for a self-contained, turnkey Python build pipeline that parses `<script>`, injects anti-inspect listeners, exports public functions to `window`, runs `javascript-obfuscator`, and collapses HTML/CSS/JS into a single dense 1-line production artifact.

### Comprehensive 4-Tier Anti-Inspect & Source Protection Standard
When users request that client-side code be unreadable or scrambled when inspected across desktop and mobile browsers:
1. **HTML & CSS Minification (Single-Line Collapse):**
   - Strip all indentation, line breaks, and comments, collapsing the entire document into a single continuous stream. This immediately disorients casual visitors using `View Page Source` (`Ctrl+U`).
2. **AST-Level JavaScript Obfuscation:**
   - Apply AST transformations via tools like `javascript-obfuscator`:
     - *Identifier Mangling:* Transform all function and variable names into hexadecimal identifiers (`_0x4b1a`, `_0x2ef8`).
     - *String Array Encoding & Shuffling:* Shift all literal strings, classes, and URLs into an encoded Base64/RC4 array accessed via lookup wrappers.
     - *Control Flow Flattening:* Transform linear logic into state-machine switch-case dispatcher loops to break automatic code decompilers and beautifiers.
3. **The Inline HTML Event Handler Mangling Trap:**
   - *Trap:* Running `javascript-obfuscator` without explicitly exporting public event handler functions to `window` or passing them to `--reserved-names`.
   - *Mechanism:* In standard obfuscation, top-level function declarations (`function showView() { ... }`) are renamed to mangled identifiers (e.g. `_0x4b1a`) or wrapped inside an IIFE. When a user clicks `<button onclick="showView('home')">`, the browser looks for `window.showView`, finds `undefined`, and throws an unhandled `ReferenceError: showView is not defined`, breaking all button interactions on the site.
   - *Rule:* Always explicitly bind all public UI handler functions onto `window` at the end of the script before obfuscation (e.g. `window.showView = showView; window.requestAccess = requestAccess; ...`) AND pass the identifier list to `--reserved-names` in `javascript-obfuscator`. This guarantees seamless inline HTML event execution while internal algorithms, encryption logic, and ciphertexts remain 100% scrambled.
4. **Self-Defending & Anti-Prettify Defect Trap:**
   - Enable `selfDefending: true` when appropriate.
   - *Mechanism:* The script computes a cryptographic hash or regex length check on its own function bodies. If a user or browser DevTools attempts to format or "pretty-print" the script (`{ }` in Chrome DevTools), the whitespace tampering triggers a continuous debugger loop or recursive call that halts or freezes the inspecting tab.
5. **Cross-Browser DevTools & Shortcut Blockers:**
   - Prevent standard user shortcuts and mouse inspection:
   ```javascript
   // Disable Right Click (Context Menu)
   document.addEventListener('contextmenu', e => e.preventDefault());

   // Block Developer Keyboard Shortcuts across Windows, Linux & macOS
   document.addEventListener('keydown', e => {
     if (
       e.key === 'F12' ||
       ((e.ctrlKey || e.metaKey) && e.shiftKey && ['I','J','C','i','j','c'].includes(e.key)) ||
       ((e.ctrlKey || e.metaKey) && (e.key === 'u' || e.key === 'U')) ||
       ((e.ctrlKey || e.metaKey) && (e.key === 's' || e.key === 'S'))
     ) {
       e.preventDefault();
       return false;
     }
   });
   ```
   - Pair with an asynchronous `debugger;` probe running inside a `setInterval` worker or periodic `console.clear()` to pause execution or wipe logs if DevTools is opened via browser settings menus.
   - *UX Disclosure Invariant:* Always inform the owner that client-side obfuscation and anti-inspect techniques significantly deter casual inspection, scrapers, and script-kiddies, but cannot substitute for true cryptographic encryption (AES-256 Zero-Knowledge) or server-side authentication for genuine secrets.

### Mobile CLI Code Snippet Overflow Invariant
- *Trap:* Displaying terminal command boxes (`<code>python3 ...</code>` or `curl ...`) inside card grids without constrained horizontal scrolling.
- *Mechanism:* Developer commands frequently exceed standard mobile viewport widths (360px–390px). Without defensive styling, pre/code tags push card borders outward and trigger horizontal viewport scrolling (`hasHorizontalScroll: true`), breaking the responsive mobile experience.
- *Rule:* Always style terminal command boxes with `overflow-x: auto; white-space: nowrap; max-width: 100%;` and subtle custom scrollbars, ensuring that commands stay neatly scrollable within their card and `document.documentElement.scrollWidth === window.innerWidth`.

---

## 2. Resilient Media & Video Embeds

### YouTube Shorts 'Error 153' (Video Player Configuration Error)
- **Trap:** Embedding YouTube Shorts via raw `<iframe>` with query parameters (`autoplay=1`, `loop=1`, etc.) frequently displays a black screen with `"Video player configuration error Error 153"` and `"Watch video on YouTube"`.
- **Mechanism:** In YouTube's embed policy, Shorts that feature copyrighted commercial audio/music or channel-level embedding restrictions refuse to render in third-party iframes, especially across custom domains or referrers.
- **Fix (Smart Facade Player Pattern):**
  - Render an interactive video card containing the official high-res poster (`https://i.ytimg.com/vi/<VIDEO_ID>/hqdefault.jpg`), an overlay with a glowing YouTube SVG Play badge, and a direct target link or dynamic on-click modal player.
  - This avoids iframe crashes, cuts initial page payload by ~1.5 MB per video, and guarantees zero broken players.
  - Alternatively, if local video hosting is permitted, use native HTML5 `<video autoplay muted loop playsinline>` which completely bypasses YouTube API restrictions.

### jQuery Hero Carousel Background-Image Blankout
- **Trap:** Legacy themes (e.g., BizPage) often use JavaScript in `main.js` that extracts `<img src="...">` from `.carousel-background`, removes the element from DOM (`.remove()`), and injects `background-image: url(...)` into `.carousel-item`.
- **Mechanism:** If script execution is deferred, or if double CSS overlays (`#intro .carousel-item::before` at 70% black + inline linear-gradient) are stacked, the hero section appears as a solid pitch-black box before or even after load.
- **Rule:** Set `style="background-image: url('...')"`, `background-size: cover;`, and `background-position: center;` directly in the HTML tag on `.carousel-item`, and tune overlay gradients to 0.40–0.65 opacity so real workshop action and sparks remain vivid.
