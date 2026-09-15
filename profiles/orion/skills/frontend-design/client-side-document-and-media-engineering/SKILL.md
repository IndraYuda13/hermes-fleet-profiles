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
- For clean A4 document output (such as ATS resumes, invoices, or EPDA disbursement sheets) across ALL devices (desktop, tablet, and mobile smartphones), implement the **Isolated Viewport Iframe Engine Pattern**:
```javascript
async function exportPerfectA4PDF(sourceElementId, filename) {
  const source = document.getElementById(sourceElementId);
  if (!source) return;

  const sourceHtml = source.outerHTML;

  // 1. ISOLATED VIEWPORT IFRAME ENGINE:
  // Creates an independent 800px viewport. Isolates rendering from mobile phone viewports (390px),
  // split-screen flex containers, browser zoom levels, and scroll offsets.
  const iframe = document.createElement('iframe');
  iframe.id = 'pdfIsolationExportFrame';
  iframe.style.position = 'fixed';
  iframe.style.left = '-9999px';
  iframe.style.top = '0';
  iframe.style.width = '800px';
  iframe.style.height = '1140px';
  iframe.style.zIndex = '-9999';
  iframe.style.border = 'none';
  iframe.style.background = '#ffffff';
  document.body.appendChild(iframe);

  const idoc = iframe.contentWindow.document;
  idoc.open();
  idoc.write(`
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: #ffffff; color: #000000; width: 794px; margin: 0 auto; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
        .a4-paper {
          width: 794px !important;
          max-width: 794px !important;
          height: 1120px !important;
          max-height: 1120px !important;
          padding: 35px 42px 25px 42px !important;
          box-sizing: border-box !important;
          font-family: 'Consolas', 'Courier New', monospace;
          font-size: 8.2pt;
          line-height: 1.22;
          display: flex;
          flex-direction: column;
          justify-content: space-between;
          background: #ffffff;
        }
        table { width: 100%; border-collapse: collapse; table-layout: fixed; box-sizing: border-box; font-family: 'Consolas', monospace; font-size: 8pt; }
        td, th { padding: 2.5px 5px; border: 1px solid #000000; vertical-align: middle; }
        .doc-head-table td, .doc-bottom-grid td { border: none; }
        .t-left { text-align: left !important; }
        .t-center { text-align: center !important; }
        .t-right { text-align: right !important; }
      </style>
    </head>
    <body>
      ${sourceHtml}
    </body>
    </html>
  `);
  idoc.close();

  // Allow layout and web fonts to settle
  await new Promise(r => setTimeout(r, 200));

  const targetEl = idoc.querySelector('.a4-paper') || idoc.body.firstElementChild;

  const opt = {
    margin: [0, 0, 0, 0], // 0 margin in jsPDF because padding is internal
    filename: filename,
    image: { type: 'jpeg', quality: 0.98 },
    html2canvas: { 
      scale: 2, 
      useCORS: true, 
      logging: false,
      scrollX: 0,
      scrollY: 0,
      width: 794,
      height: 1120,
      windowWidth: 800
    },
    jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' },
    pagebreak: { mode: 'avoid-all' } // Strict single-page enforcement
  };

  try {
    const generator = iframe.contentWindow.html2pdf || window.html2pdf;
    await generator().set(opt).from(targetEl).save();
    if (document.getElementById('pdfIsolationExportFrame')) {
      document.body.removeChild(iframe);
    }
  } catch (err) {
    if (document.getElementById('pdfIsolationExportFrame')) {
      document.body.removeChild(iframe);
    }
    console.error("PDF export error, fallback to print:", err);
    window.print();
  }
}
```
- **The `position: fixed` + `z-index: -1` html2canvas Blank Canvas Trap (`canvasHeight = 0` / 3KB Empty PDF):**
  - *Trap:* Attempting to hide an export clone with `position: fixed; z-index: -1;` before passing it to `html2pdf().from(clone)`.
  - *Mechanism:* In `html2canvas`, any element with `position: fixed` causes the layout engine to compute a canvas height of `0` (`canvasHeight: 0`). Furthermore, `z-index: -1` paints the element behind the root stacking context and dark background of `document.body`. Together, `html2canvas` outputs an empty canvas, and `jsPDF` produces a 3KB blank white PDF file.
  - *Rule:* Never use `position: fixed` or negative `z-index` on export clones. If using client-side canvas capture, mount offscreen inside an isolated `<iframe>`.
- **The Hidden-Tab / Ancestor `display: none` Trap in Client-Side PDF Generation (3KB Blank/Empty PDF):**
  - *Trap:* Triggering `html2pdf()` or `html2canvas` while the source element (e.g. `#epdaPaper`) resides inside a parent container that is hidden via `display: none` (such as a mobile tabbed interface where the Form tab is active and the Document Preview tab is hidden).
  - *Mechanism:* Elements inside `display: none` ancestors are completely omitted from the browser's layout render tree. Calling `.cloneNode(true)` on such an element clones an uncomputed node with `offsetWidth = 0` and `offsetHeight = 0`. When `html2canvas` attempts to measure or rasterize it, canvas height evaluates to `0`, producing an empty canvas stream, and `jsPDF` saves a completely blank 3KB white PDF file.
  - *Fix (Isolated Active Paint Engine Pattern):* When cloning an element for export, NEVER rely on the parent container's visibility state. Append the clone directly to `document.body`, explicitly force `display: flex !important; flex-direction: column !important; justify-content: space-between !important; width: 794px !important; max-width: 794px !important; height: 1120px !important; max-height: 1120px !important; position: fixed !important; left: 0 !important; top: 0 !important; z-index: 99999 !important; background: #ffffff !important; box-sizing: border-box !important; padding: 35px 42px 25px 42px !important;`, wait 100–150ms for the browser to compute the layout and render styles, run `html2pdf().set(opt).from(clone).save()`, and remove the clone inside `.then()` and `.catch()` handlers.
- **The CSS Animation Frozen-State Trap in `@media print` (The 1KB / Blank Headless Print PDF Bug):**
  - *Trap:* Adding CSS entry animations (e.g. `animation: fadeIn 0.2s ease-in-out;` where `@keyframes fadeIn { from { opacity: 0; transform: translateY(3px); } to { opacity: 1; transform: translateY(0); } }`) to tab sections or document preview panels causes automated or headless printing (Chrome `--print-to-pdf`, Puppeteer, Playwright, or CDP `Page.printToPDF`) to produce a 1KB completely blank white PDF with zero text.
  - *Mechanism:* In headless or programmatic PDF printing, the browser rasterizes print media before animations are scheduled to run, or permanently freezes all CSS transitions and `@keyframes` animations at their initial keyframe (`from { opacity: 0; }`). Because `opacity: 0` is stamped onto the printable container during render tree generation, the print engine treats the element as completely invisible and outputs an empty white page with an empty content stream.
  - *Rule:* In `@media print`, ALWAYS explicitly disable all animations and transitions globally, and force target containers to full opacity:
    ```css
    @media print {
      * {
        -webkit-print-color-adjust: exact !important;
        print-color-adjust: exact !important;
        animation: none !important;
        transition: none !important;
      }
      #printableContainer,
      .tab-section {
        display: block !important;
        opacity: 1 !important;
        transform: none !important;
        animation: none !important;
      }
    }
    ```
- **The Responsive Media Query Pollution of `@media print` Trap (Blank Page on Mobile Print):**
  - *Trap:* Declaring mobile responsive breakpoints as bare `@media (max-width: 1100px)` instead of scoped `@media screen and (max-width: 1100px)`.
  - *Mechanism:* Bare `@media (max-width: ...)` applies to all media types including `print`. When users print from a smartphone (360px–390px viewport) or a headless browser, the browser evaluates the breakpoint against the screen width before printing. If the responsive rule contains an ID selector `#previewCol { display: none !important; }`, it overrides `@media print` class rules like `.preview-container { display: block !important; }` due to higher CSS specificity (`0,1,0,0` vs `0,0,1,0`). The document container remains `display: none` during printing, causing the browser to print an empty white page.
  - *Rule:* ALWAYS declare responsive breakpoints as `@media screen and (max-width: ...)`. In `@media print`, explicitly target the printable container by its exact ID and class with `display: block !important; width: 100% !important; padding: 0 !important; margin: 0 auto !important;`, and hide application chrome (`#controlsCol, .controls-container, .mobile-tab-bar, .no-print, header.app-topbar`).
- **The In-Situ Single-Page JavaScript Syntax Collision Trap ("Semuanya Tidak Bisa di Klik"):**
  - *Trap:* When replacing or updating functions in client-side HTML `<script>` blocks via regex or find-and-replace, dangling commas, mismatched braces, or unremoved trailing fragments (e.g. `},\n jsPDF: ...`) leave invalid syntax.
  - *Mechanism:* Browsers parse `<script>` tags as a single compilation unit. An unhandled `SyntaxError` at any line halts execution of the entire script. Consequently, top-level functions (`calculate`, `loadHub`, `downloadPDF`, `printDoc`) are never defined on `window`, causing all button clicks, form inputs, and dropdowns across the application to silently fail (`malah semuanya tidak bisa di klik`).
  - *Rule:* Always validate `<script>` syntax programmatically (e.g. extracting `<script>` content and asserting `node -c` exits 0) immediately after modifying in-situ client code before deploying to production or declaring completion.
- **The Superior Native Vector Print Architecture (`window.print()` with Dynamic Document Title):**
  - *Trap:* Trying to force `html2canvas` rasterization for client-side PDF downloads when the user expects vector-grade print quality ("sempurna seperti print A4").
  - *Mechanism:* `html2canvas` converts DOM elements into raster bitmap images before placing them in `jsPDF`. This introduces blurriness, missing CSS features, mobile viewport clipping, and large file sizes (~500KB–1MB). In contrast, `window.print()` delegates directly to the browser's native C++ print engine (Blink/WebKit/Gecko), rendering 100% crisp vector text, razor-sharp table borders at 1200 DPI, and exact `@media print` CSS with zero canvas bugs and compact file size (~100KB).
  - *Pattern (Dynamic Document Title Pre-Fill for Native PDF Export):*
    To give users a 1-click "Download PDF" experience using the native vector print engine:
    ```javascript
    function downloadPDF() {
      const vessel = document.getElementById('inpVessel').value.trim().replace(/[^a-zA-Z0-9]/g, '_');
      const port = document.getElementById('inpPort').value.trim().replace(/[^a-zA-Z0-9]/g, '_');
      const filename = `EPDA_${vessel}_${port}_BGM`;

      // Dynamically update document.title: Modern browsers (Chrome, Safari, Edge) automatically
      // use document.title as the default suggested file name in the "Save as PDF" dialog!
      const prevTitle = document.title;
      document.title = filename;

      showToast("📄 Membuka dialog cetak PDF... Pilih 'Save as PDF' untuk hasil 100% jernih dan sempurna!");

      setTimeout(() => {
        window.print();
        setTimeout(() => { document.title = prevTitle; }, 2000);
      }, 300);
    }
    ```
    This completely eliminates client-side canvas bugs while ensuring the user's downloaded PDF is 100% identical in perfection to Print A4.
- **The Mobile Viewport Half-Page Distortion & Left Shearing Trap (`html2pdf.js` on Smartphones):**
  - *Trap:* Triggering `html2pdf.js` / `html2canvas` directly on an in-DOM or cloned element in a mobile browser (iOS Safari or Android Chrome) produces a PDF where the document is compressed into the left 40%–50% of the page, the right half of the A4 page is completely blank white, and the left table margin is sheared off.
  - *Mechanism:* `html2canvas` inherently adopts the host document's `window.innerWidth` (e.g. 375px–390px on smartphones) and current scroll coordinates. Even if the cloned element has `width: 794px`, the mobile browser's layout engine constrains canvas rasterization to the narrow mobile viewport width (~390px). When `jsPDF` places this 390px-wide canvas image onto a 595pt (210mm) A4 canvas, it covers only half the page width. Furthermore, mobile pinch-zoom or touch scroll offsets push the left side of the canvas into negative coordinates, slicing off the leftmost columns and headers.
  - *Rule:* Never render `html2canvas` in the host document when mobile compatibility is required. Always mount an offscreen `<iframe>` with `width: 800px; height: 1140px; position: fixed; left: -9999px;`, inject the document and print CSS, and run `html2pdf` from inside the iframe. The iframe establishes its own independent desktop-grade viewport with zero scroll offset and zero mobile media-query interference, ensuring identical 100% full-width, single-page A4 PDF output on all devices.
- **The Split-Screen / Responsive Container html2canvas Offset Trap (Left Shearing & Clipped Columns):**
  - *Trap:* Passing an element directly to `html2pdf().from(element)` while it sits inside a split-screen CSS grid/flexbox layout or a horizontally scrolled container, especially when passing `windowWidth: 800` or `scrollX: 0`.
  - *Mechanism:* `html2canvas` evaluates bounding client rect coordinates relative to the window or scroll parent. If the document sits in the right pane (e.g. `X = 560px`), forcing `windowWidth: 800` or `scrollX: 0` causes `html2canvas` to capture from the window's left edge (X=0) instead of the element's local coordinate origin. This shifts the target element 300px+ to the left into negative space, shearing off the left header, logo, and left-side table columns.
  - *Rule:* Never capture an in-situ document element residing inside a split-screen or scrolled container. Always deep-clone the element (`cloneNode(true)`), mount it fixed at `(0, 0)` with exact A4 pixel dimensions (`width: 794px; height: 1120px; box-sizing: border-box;`), render with `html2pdf`, and unmount on completion.
- **The Spurious Blank 2nd Page Trap in html2pdf.js:**
  - *Trap:* The exported single-page PDF unexpectedly generates a second page that is 100% blank white.
  - *Mechanism:* In standard A4 portrait at 96 DPI, printable page height is 297mm (1122.5px). If the rendered canvas height exceeds 1122px by even 1 single subpixel (e.g. 1123px) due to font line-height, borders, or table gaps, `jsPDF` automatically generates a second page to accommodate the overflowing 1px slice.
  - *Rule:*
    1. Lock the export clone height strictly to `height: 1120px; max-height: 1120px; overflow: hidden;` (2–3px below 1122.5px).
    2. Set `pagebreak: { mode: 'avoid-all' }` in `html2pdf` options.
- **The Dual-Margin Trap in html2pdf.js (Right-Margin Truncation):**
  - *Trap:* Specifying non-zero margins (e.g. `margin: [8, 10, 8, 10]`) in `html2pdf` options when the target element (`.a4-paper`) is already styled to physical A4 width (`width: 210mm; box-sizing: border-box;`) with its own internal padding.
  - *Mechanism:* `html2pdf.js` delegates to `jsPDF.addImage()`, which places the rendered canvas starting at `x = margin_left` (10mm). A 210mm wide canvas placed at `x = 10mm` terminates at `x = 220mm`. Because physical A4 paper is strictly 210mm wide, the rightmost 10mm (table borders, remarks column, currency labels, stamps) is pushed off-page and clipped off completely.
  - *Rule:* When the target element defines internal margins/padding, `opt.margin` MUST be `0`. Lock `.a4-paper` with `width: 210mm; max-width: 210mm; min-height: 297mm; box-sizing: border-box !important; padding: 10mm 12mm 8mm 12mm;`.
- **Table Layout Hardening for Zero-Overflow PDF:**
  - *Rule:* Always set `.bgm-cost-table, .vessel-grid-table, table { table-layout: fixed; width: 100%; box-sizing: border-box !important; word-break: break-word; }`. Without `table-layout: fixed`, long text in remarks or particulars forces table cells beyond 100% width, causing right borders to disappear in PDF export.
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

## 6. Enterprise & Maritime Commercial Document Generators (EPDA, Proforma & Quotation Invoices)

### Authentic Maritime & Corporate Invoice Typography Invariant
- **Trap:** Styling enterprise disbursement or invoice previews with generic rounded web fonts (e.g. Inter, Poppins, Roboto) or soft pastel borders.
- **Mechanism:** In global maritime trade, chartering, and international disbursement auditing, shipping documents (EPDA, FDA, Charter Parties, Fixture Notes) are audited line-by-line by international disbursement accountants. Documents styled with casual web aesthetics appear amateurish, unverified, and lack legal authority.
- **Rule:** While the application control shell can use modern sans-serif (e.g. Plus Jakarta Sans), the live A4 document sheet MUST use high-contrast monospace / typewriter typography (`'Consolas', 'Courier New', 'IBM Plex Mono', monospace`) with `font-variant-numeric: tabular-nums`. Monospace enforces strict tabular character alignment, eliminates ambiguous digit spacing, and provides the authentic legal look of enterprise maritime documentation.

### Grid Borders, Column Structure & Decimal Alignment
- **Rule:** Never use borderless floating rows or soft box-shadows on the document table itself.
- Construct the main disbursement table with crisp `1px–1.5px solid #000000` gridlines (`border-collapse: collapse`), dark navy header bands (`#002060` with bold white uppercase text), and a standardized 4-column structure:
  `[PARTICULARS] | [TARIFF / CALCULATION BASIS] | [AMOUNT] | [REMARKS]`
- Set the `TARIFF / BASIS` column to show explicit multiplication formulas (e.g. `22,698 x 0.1 x 3 Day(s)` or `0.00179 x 30,000`), allowing charterers to verify math instantly.
- Right-align all currency amounts (`text-align: right !important`) so decimal points align vertically down the entire column.

### Domain Grounding & Operational Hub Presets
- **Trap:** Building commercial calculators with random mock ports or generic placeholder locations.
- **Mechanism:** Sales and operations teams lose time re-entering local tariffs, while executive stakeholders immediately notice the disconnection from real company operations.
- **Rule:** Always ground preset configurations directly in the company's verified corporate profile and strategic operational hubs. For shipping agencies like BGM, provide 1-click presets aligned with their official operational hubs (e.g. Morowali/Bahodopi, Balikpapan/Lubuk Tutung, Taboneo/Muara Berau, Cigading/Ciwandan, Dumai, Batam STS, Gresik, Jakarta HQ, Manokwari), pre-populating typical vessel specifications (GRT, DWT, LOA), cargo volumes, and localized port tariffs.
- **Dual Selector Architecture (Native Dropdown + Visual Preset Grid):** Always pair visual preset card buttons with a prominent, stylized native `<select>` dropdown (`#selBgmPortHub`) at the top of the form with two-way state synchronization. Non-technical users instinctively look for a formal dropdown menu to switch operational hubs.

### Commercial Form Control & Mobile 1-Column Invariant
- **The Multi-Column Form Grid Squeeze Trap (<640px Viewports):**
  - *Trap:* Retaining 2-column or 3-column CSS grids (`.grid-2`, `.grid-3`) inside form cards on mobile screens (360px–414px).
  - *Mechanism:* On a 390px phone, 3 columns leave only ~90px width per cell. Long parameter labels (e.g. `Port Supervision`, `Harbour Dues`, `Light Dues`) and unit texts collide horizontally, forcing the rightmost column outside the viewport or truncating inputs.
  - *Rule:* Always enforce single-column flow (`grid-template-columns: 1fr !important; gap: 10px !important;`) on mobile viewports (<640px).
- **The Desktop Canvas Viewport Blowout Trap on Mobile (Split-Screen Document Apps):**
  - *Trap:* In a split-screen document app (Left: Form controls, Right: Live A4 preview canvas ~794px wide), on mobile viewports (<1100px or <640px), failing to hide the A4 canvas container (`display: none !important`) by default causes the 794px-wide A4 canvas to expand the host document body width to 794px.
  - *Mechanism:* In mobile browsers (360px–390px viewports), an unhidden 794px child element forces `document.body.scrollWidth` to ~800px. As a result, all 100%-width topbars, action buttons, tab bars, and metric cards stretch across 800px. On a 390px physical phone screen, the user only sees the left 390px, causing the right half of the navbar, the "Print A4" button, the right tab, and form inputs to appear sheared or cut off at the right edge.
  - *Rule:* In split-screen document applications with desktop print canvases, ALWAYS isolate and hide the print canvas on mobile viewports by default in CSS:
    ```css
    @media (max-width: 1100px) {
      html, body { overflow-x: hidden !important; max-width: 100vw !important; }
      main.workspace-grid { grid-template-columns: 1fr !important; overflow-x: hidden !important; padding: 12px !important; }
      #previewCol { display: none !important; max-width: 100vw !important; overflow-x: auto !important; }
    }
    ```
    Only unhide the preview container when the user explicitly clicks the "Pratinjau A4" tab via `switchTab('preview')` using `style.setProperty('display', 'flex', 'important')`.
- **Mobile Financial Metrics Bar 2x2 Grid Invariant:**
  - *Trap:* Displaying a 4-item KPI financial metrics bar as a single horizontal flex row on mobile screens.
  - *Mechanism:* Even with `flex-wrap: wrap`, long currency values (e.g. `Rp 713,258,700` and `$43,227.80`) push the 3rd and 4th metric boxes off the right screen margin on 360px–390px viewports.
  - *Rule:* On mobile screens (<640px), always restructure metric bars into an explicit 2x2 grid (`display: grid; grid-template-columns: 1fr 1fr !important; gap: 8px !important; width: 100% !important;`) with subtle horizontal dividers, ensuring all 4 financial metrics remain 100% visible, centered, and crisp without clipping.
- **Inline Input Unit Badges:**
  - *Rule:* Embed numeric units (`$/MT`, `$/GRT`, `USD`, `DAYS`, `MTs`, `MOVES`) as right-aligned badge pills inside an `.input-unit-wrapper` (with `padding-right: 60px;` on the `<input>` and `pointer-events: none;` on the badge). Never let unit strings float inline next to field labels where they crowd horizontal space.
- **Collapsible Form Card Zero-Clipping Discipline:**
  - *Trap:* Setting `overflow: hidden` on collapsible accordion cards containing form inputs.
  - *Mechanism:* If JavaScript accordion toggles set fixed heights or if browser reflow glitches occur, `overflow: hidden` clips bottom inputs to 0px height, making fields appear missing.
  - *Rule:* Ensure expanded form cards maintain `overflow: visible; height: auto !important; min-height: auto !important;` with adequate bottom padding (`padding-bottom: 20px`).

### Pass-Through vs Margin Financial Decomposition
- **Rule:** Clearly decompose commercial disbursement calculations into:
  1. *Pass-Through Costs (Port & Government Dues):* Quay Dues, Pilotage (per movement: Terminal Anchor, Anchor-Berth, Berth-Anchor, Anchor-Dept), Towage, Harbour Dues, Light Dues, Quarantine boat hire, PKKA, Shifting. Separate items subject to VAT (e.g. Indonesian PPN 11% on Quay Dues, Pilotage, and Towage) from non-VAT government PNBP fees.
  2. *Agency Remuneration (Gross Margin):* Port clearance lumpsum and agency fees.
  3. *Vessel / Owner Account Expenses:* Crew health / RT Swab, fresh water, and provisions.
- In the application shell, display live KPI cards tracking Grand Total (USD), Equivalent Local Currency (IDR via standard bank exchange rate), Pass-Through Dues, and Agency Margin in real time so the commercial desk knows profit margins before dispatching quotes.

### One-Click Multi-Channel Quotation Fast-Path
- **Rule:** In addition to direct A4 PDF download and print features, always provide a one-click "Salin Penawaran (Copy Quotation Summary)" button.
- The button formats the calculated particulars, cost breakdown, Grand Total, and corporate contact details into clean, professional plain text copied to the clipboard, allowing the commercial team to respond to charterer email or WhatsApp inquiries in under 10 seconds.

### The Dedicated Form Reset & State Nullification Pattern (`resetForm` with Confirmation Gate)
- **Problem:** In enterprise operational generators with rich default presets, users frequently need to clear pre-filled dummy/sample data to input a brand-new vessel and custom local tariffs from scratch without manually backspacing 20+ fields.
- **Dual Placement Architecture:** Provide a dedicated Reset / Clear button in two strategic touchpoints:
  1. Primary topbar actions row (`[ 🔄 Reset Form ]` styled in subtle warning red `rgba(239, 68, 68, 0.12)`).
  2. Preset selector header (compact inline button `[ 🔄 Kosongkan / Reset Form ]` adjacent to the hub dropdown).
- **Confirmation Guard Invariant:** Always protect destructive reset actions with an explicit confirmation dialog: `if (!confirm("Apakah Anda yakin ingin mengosongkan seluruh formulir untuk input kapal baru?")) return;` to prevent accidental data loss during active calculations.
- **Complete State Purge & Neutralization:**
  - Clear text inputs (`inpMessrs`, `inpVessel`, `inpFlag`, `inpEta`, `inpPort`, `inpLoading` to `""`).
  - Zero numeric inputs (`inpGrt`, `inpDwt`, `inpLoa`, and all itemized port charges to `0.00` or `""`).
  - Strip `.active` highlight styling from all preset buttons (`document.querySelectorAll('.btn-hub').forEach(b => b.classList.remove('active'))`).
  - Reset `<select>` dropdowns to a neutral disabled placeholder (`<option value="" disabled>— Formulir Manual / Pilih Hub —</option>`).
  - Re-invoke `calculate()` immediately so live A4 paper preview and KPI metric cards zero out ($0.00) in real time.
- **The Falsy Fallback Expression Trap in Live Document Renderers (`|| 'DEFAULT_STRING'`):**
  - *Trap:* Using logical OR fallbacks for user inputs (e.g. `const vessel = document.getElementById('inpVessel').value || 'MV PROPEL TBN';` or `const port = input.value || 'BAHADOPI';`) in the calculation/preview loop.
  - *Mechanism:* When a user clicks "Reset / Kosongkan Form", the input field value becomes `""` (empty string). In JavaScript, `""` evaluates to falsy, which immediately triggers the `|| 'DEFAULT_STRING'` fallback, re-populating the live document with the sample vessel, client, and port names and misleading the user into thinking the reset failed.
  - *Rule:* Never use fallback strings for document fields. Always read values cleanly with `(input.value || '').trim()`, and render clean neutral hyphens or empty strings on the document (`document.getElementById('docVessel').textContent = vessel || '-';`).
- **The Zero-State Zombie Formula & Static Remarks Trap (Eliminating `0 x 0 x 1 Day(s)` Artifacts):**
  - *Trap:* Interpolating formula strings (e.g. `${fmtInt(grt)} x ${quayRate} x ${days} Day(s)`) or leaving static remarks table cells (e.g. `139.60 USD`, `LUMPSUM`, `BOAT HIRE WITH LAUNCH OF PORT`) without zero-guards.
  - *Mechanism:* When values are reset or empty, the preview table continues displaying nonsensical zero formulas (`0 x 0 x 1 Day(s)`, `0 x 0 + 0.00`, `0.00 $ x 0 Est. Crew`) and orphaned remarks, creating visual clutter that confuses users about whether old tariffs remain active.
  - *Rule:* In live document projections, guard all formula strings, amounts, and remarks behind positive value checks:
    - If variables are zero, set basis to clean hyphen `'-'` (`dQuayBasis.textContent = (grt > 0 && quayRate > 0 && days > 0) ? ... : '-'`).
    - Bind remarks cells to explicit IDs (`dPilotTariff`, `dClearanceRemarks`, `dBoatHireRemarks`) and clear them to empty string `''` when the associated itemized cost is zero.

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

---

## 7. Retail & Service Business POS, Cashflow & Monthly Profit/Loss Financial Systems

### Architecture for Daily/Monthly Cashflow & POS Engines (Barbershop, Salons, Workshops, Cafes)
When building single-page financial calculators and cash register systems for service businesses:
1. **Daily POS Register & Monthly Omset Synchronization:**
   - Implement tap-to-add service cards reflecting the business's official pricelist with visual gold/neon accents.
   - Record transactions with timestamp, customer name/table, itemized services, payment method (`Cash`, `QRIS`, `Transfer`), and line-item totals.
   - Real-time KPI deck must track both daily metrics (Today's Income / Uang Masuk Hari Ini) and monthly cumulative metrics (Monthly Gross Revenue / Omset Bulan Ini) dynamically filtered by active month (`YYYY-MM`).
2. **Operational Expense Ledger (Uang Keluar Harian & Bulanan):**
   - Provide a structured daily expense tracker partitioned into realistic service categories: *Stok Bahan Baku & Produk* (Blade/silet, pomade, shampoo, shaving cream), *Operasional & Kebersihan* (Laundry handuk, neck paper, sanitasi), *Utilitas* (Listrik PLN, PDAM, WiFi), *Gaji & Komisi Barber/Capster*, *Konsumsi*, and *Perawatan Alat* (Service clipper, asah gunting).
   - Display real-time Today's Expense vs Monthly Total Expenses.
3. **Dynamic Catalog / Pricelist Manager with Persistent Storage:**
   - Store service catalogs in browser `localStorage` (`KEY_SERVICES`) so price changes persist permanently without requiring a backend database.
   - Provide in-place editing for service name, unit price, and package description, plus ability to add custom services or delete discontinued items.
   - *Factory Reset Invariant:* Always provide a "Reset ke Harga Asli" button that restores the catalog back to the baseline benchmark data if user edits cause discrepancies.
4. **Monthly P&L Ledger & Cashflow Reconciliation:**
   - Compute Net Profit: $\text{Net Profit} = \text{Total Income} - \text{Total Expenses}$.
   - Compute Profit Margin: $\text{Margin } \% = \left(\frac{\text{Net Profit}}{\text{Total Income}}\right) \times 100\%$.
   - Display two reconciliation tables:
     * *Service Distribution:* Aggregates volume sold per service (e.g. 71 heads shaved/styled) and revenue generated per service line.
     * *Daily Cashflow Ledger:* Row-by-row daily balance ($+\text{In}, -\text{Out}, =\text{Net}$) across days 1–31 of the active month.
5. **Executive Monthly Statement A4 PDF Export:**
   - Render a formal single-page A4 document matching corporate accounting standards:
     * Business Identity & Contacts header with period badge.
     * Metadata strip (Bulan buku, total hari aktif operasional, tanggal cetak).
     * Section I: Executive P&L Summary (Omset, Biaya, Laba Bersih, Margin).
     * Section II: Itemized Service Revenue Breakdown.
     * Section III: Categorized Operational Expense Allocation.
     * Dual authorization block: Signature box for *Kasir / Frontdesk* and *Owner / Management*.
   - Combine with a 1-click WhatsApp copy button (`copyMonthlySummary`) that formats the monthly financial summary into clean, professional text ready for instant messaging.
6. **The Complete Financial Data Purge & Seeding Guard Pattern (`resetAllFinancialData`):**
   - *Problem:* Users wanting to put the financial calculator into real production need to wipe out all pre-populated dummy/simulation transactions (both orders and expenses) so cashflow starts completely clean from Rp 0.
   - *Trap:* Clearing data via `localStorage.removeItem(KEY_ORDERS)` without an explicit seed state flag. On the next browser reload, standard bootstrap logic (`if (!savedOrders) seedData()`) detects null storage and automatically re-populates the sample orders, frustrating the user.
   - *Rule:* Implement a persistent seed flag (`localStorage.setItem('barber_seeded_flag', 'cleared')`) and store an explicit empty array (`JSON.stringify([])`). Guard `initData()` so it never overwrites a user-initiated clean slate:
     ```javascript
     function resetAllFinancialData() {
       if (!confirm("Hapus semua riwayat transaksi uang masuk & keluar? Data kas akan dimulai dari Rp 0.")) return;
       orders = [];
       expenses = [];
       currentCart = {};
       localStorage.setItem(KEY_ORDERS, JSON.stringify([]));
       localStorage.setItem(KEY_EXPENSES, JSON.stringify([]));
       localStorage.setItem('barber_seeded_flag', 'cleared');
       renderPosPricelist();
       renderCartUI();
       recalculateAll();
     }
     ```
     Always pair this with a "Muat Data Contoh (Demo)" button (`reloadDemoData`) on the monthly ledger toolbar so the owner can restore simulation data if they wish to test projections.

---

## 8. Maritime Cargo Loading Progress & Statement of Facts (SOF) Generator Architecture

When building daily cargo monitoring, vessel turnaround, and Statement of Facts (SOF) web systems for shipping agencies, stevedoring companies, and charterers:

### Operational Telemetry & Mathematical Foundations
- **Primary Input Matrix:**
  - *Target Stowage Plan (MT):* Contractual or planned cargo quantity (e.g. `51,740 MT` Coal in bulk).
  - *Cargo Loaded Previous (MT):* Cumulative cargo loaded up to the start of the current operational period/shift.
  - *Cargo Loaded Current Shift (MT):* Quantity loaded during the active shift/day (e.g. `7,500 MT`).
  - *Operating Hours (Hours):* Active net loading hours during the shift (e.g. `4.8 hrs`).
- **Standardized Mathematical Formulas:**
  - $\text{Total Loaded to Date} = \text{Previous Loaded} + \text{Current Shift Loaded}$
  - $\text{Balance Cargo to Load} = \text{Target Stowage Plan} - \text{Total Loaded to Date}$
  - $\text{Loading Progress } \% = \left(\frac{\text{Total Loaded to Date}}{\text{Target Stowage Plan}}\right) \times 100\%$
  - $\text{Average Loading Rate} = \frac{\text{Current Shift Loaded}}{\text{Operating Hours}} \quad (\text{MT / Hour})$
  - $\text{Estimated Time of Completion (ETC)}:$ Projected completion timestamp calculated as:
    $$\text{Remaining Hours} = \frac{\text{Balance Cargo}}{\text{Average Loading Rate}}$$
- **Mandatory Maritime Contingency Clause (`IAGWP & WP`):**
  - In international shipping law, maritime agencies and charterers NEVER provide unconditional completion dates. Unconditional guarantees expose the agency to demurrage/despatch disputes or laytime breach claims.
  - Always append the mandatory international maritime disclaimer to all estimated completion timestamps:
    👉 **`IAGWP & WP`** (*If All Goes Well and Weather Permitting*).

### Port Weather & Sea Telemetry Integration
- In dry bulk shipping (coal, clinker, grain, bauxite), rain or high swells trigger immediate cargo hatch closure and suspension of loading operations.
- Integrate a live port weather widget tracking:
  - *Sky Condition:* (Fine, Sunny, Cloudy, Overcast, Rain, Thunderstorm).
  - *Air Temperature:* Current, Minimum, and Maximum (°C).
  - *Wind Speed & Direction:* (e.g. `13 km/h / 7 Knots — Gentle Breeze`).
  - *Humidity & Precipitation Probability:* High humidity and rain probabilities (>40%) alert operations of potential hatch-closing risks.
  - *Sea & Swell Condition:* (e.g. `Calm, Swell 0.2 – 0.5 Mtr`).
  - *Operational Impact Outlook:* Explicit narrative statement confirming whether cargo operations are proceeding without interruption or documenting weather downtime.

### Statement of Facts (SOF) Chronological Event Ledger
- Provide an interactive, expandable chronology of port milestones:
  - Standard Milestones: `Vsl Arrived at Roads/Anchorage`, `1st Notice of Readiness (NOR) Tendered`, `Dropped Anchor`, `2nd NOR Re-Tendered`, `Port Authorities Onboard (Inward Clearance)`, `Free Pratique Granted by Health Quarantine (KKP)`, `Authorities Disembarked`, `Pilot Onboard & Shifted to Jetty`, `All Fast Alongside Berth`, `Commence Cargo Loading Operations`, `Draft Survey Completed`, `Hatch Closed Due to Rain (Stoppage)`, `Resumed Loading`, `Completed Cargo Operations`, `Unberthed / Cast Off`.
  - Allow adding custom milestone rows (Date, Time `HH:MM hrs`, Description) with instant reordering and row deletion.

### Dual-Mode Photo Documentation Engine (Camera & File Upload)
When documenting ship operations, draft surveys, hatch loading, and conveyor belt status:
1. **Triple-Path Capture Architecture:**
   - *Native Mobile Camera Trigger:* `<input type="file" id="cameraCaptureInput" accept="image/*" capture="environment">` directly launches the rear camera app on Android and iOS devices.
   - *In-Browser Live WebCam Snapshot Modal:* For users working on laptops or tablets with browser webcam permissions, provide an in-page modal using `navigator.mediaDevices.getUserMedia({ video: { facingMode: { ideal: 'environment' } } })` rendering to a `<video autoplay playsinline>` feed, with a snapshot trigger drawing to an offscreen `<canvas>` and converting to Base64 JPEG data URL via `canvas.toDataURL('image/jpeg', 0.88)`.
   - *Gallery / Multi-File Upload:* `<input type="file" id="fileUploadInput" accept="image/*" multiple>` allowing batch selection of inspection photos from local storage.
2. **Photo Management & Captioning:**
   - Store photos as `{ id, dataUrl, caption, filename }` in client state.
   - Render interactive thumbnail cards in the control panel with an editable caption input (`"Kapal sandar di Dermaga"`, `"Pemuatan Palka No. 3"`) and a delete button.
3. **Print & PDF Layout Hardening for Photo Annex:**
   - In the live A4 document sheet, render attached photos in a dedicated Section D (`OPERATIONAL PHOTO DOCUMENTATION`) arranged in a crisp 2-column or 3-column grid with dark subtitle bars.
   - **Page-Break Invariant:** Prevent ugly mid-photo clipping by declaring:
     ```css
     @media print {
       .photo-card-doc,
       .photo-doc-section,
       .report-table,
       .sof-doc-table,
       .weather-box-container {
         page-break-inside: avoid !important;
         break-inside: avoid !important;
       }
     }
     ```
   - If photos exceed Page 1 space, `page-break-inside: avoid` gracefully pushes the photo grid onto Page 2 as an official Photo Annex without splitting image boxes across page edges.

### Interactive HTML5 Time Pickers (`<input type="time">`) & Operational Timestamp Engineering
- **The Plain Text Time Input Trap in Maritime Chronologies:**
  - *Trap:* Using generic `<input type="text">` for operational time fields (e.g. `value="11:10 hrs LT"` or `value="05:36"`).
  - *Mechanism:* Text fields force users to manually type numbers, colons, spaces, and suffixes on keyboards, leading to inconsistent casing (`11.10`, `11:10 AM`, `1110hrs`), typos, and frustration. Users expect the browser's native 3-column time picker flyout (Hours, Minutes, AM/PM) with scrollable columns and blue selection highlights.
  - *Rule:* Always use native `<input type="time">` for all operational timestamps.
- **The Tiny Clock Icon Hit-Target Trap & `onclick="this.showPicker()"` Ergonomics:**
  - *Trap:* Expecting users to click the tiny 16px native clock indicator on the far edge of the time input.
  - *Mechanism:* In Chromium desktop (Chrome, Edge, Opera), clicking the text area of `<input type="time">` merely focuses the hour segment for keyboard typing. The native 3-column dropdown picker opens ONLY when the user clicks directly on the small clock icon. On high-resolution desktop screens or touchpads, this small target causes repeated misclicks.
  - *Rule:* Always attach `onclick="this.showPicker()"` to `<input type="time">` elements:
    ```html
    <input type="time" class="time-picker-box" id="inpTime" value="11:10" onclick="this.showPicker()" onchange="recalc()" title="Pilih Jam">
    ```
    This programmatically opens the 3-column flyout dropdown whenever the user clicks *anywhere* inside the input box.
- **Dark-Theme WebKit Calendar/Clock Indicator Inversion:**
  - *Trap:* Rendering native time or date pickers on dark background panels (`background: #0f172a` or dark navy) without styling the WebKit indicator.
  - *Mechanism:* The default browser indicator icon is dark grey/black. Against dark backgrounds, it becomes nearly invisible.
  - *Rule:* In dark mode stylesheets, explicitly invert the indicator icon to crisp white and add smooth hover scale:
    ```css
    input[type="time"]::-webkit-calendar-picker-indicator,
    input[type="date"]::-webkit-calendar-picker-indicator {
      filter: invert(1);
      cursor: pointer;
      opacity: 0.85;
      padding: 2px;
      border-radius: 4px;
      transition: transform 0.2s, opacity 0.2s;
    }
    input[type="time"]::-webkit-calendar-picker-indicator:hover,
    input[type="date"]::-webkit-calendar-picker-indicator:hover {
      opacity: 1;
      transform: scale(1.2);
    }
    ```
- **The Native Date Picker (`<input type="date">`) vs Ambiguous `<select>` or Free-Text Trap:**
  - *Trap:* When users ask to "pilih/select tanggal jangan manual", implementing an HTML `<select>` tag with a hardcoded list of dates or leaving a manual text field (`<input type="text">`).
  - *Mechanism:* In colloquial user phrasing, "select tanggal" frequently means selecting the date from an interactive graphical calendar picker (the native HTML5 `<input type="date">` popup with monthly calendar grid, year/month navigation, "Today", "Clear", and blue highlighted day) as seen in Chromium/Chrome. A static `<select>` dropdown restricts date range flexibility, requires maintaining arbitrary date arrays, and frustrates users, while free-text inputs invite formatting errors.
  - *Rule:* Always use native HTML5 `<input type="date">` with `onclick="this.showPicker()"` for date selection. Pair it with an automatic date synthesizer that converts the standard ISO value (`YYYY-MM-DD`) into the formal corporate/maritime format (e.g. `14TH SEPT 2026`) in live document previews and exported plain-text summaries.
- **Dual-Engine Real-Time Geolocation & Location Auto-Switching Architecture (GPS + Zero-Permission IP Fallback):**
  - *Trap:* Forcing operators to manually re-type local port names and coordinates whenever they move between operational hubs, or relying solely on `navigator.geolocation` which fails silently when users deny permission or use desktop PCs without GPS chips.
  - *Mechanism:* Field agents, surveyors, and commercial desk staff work across varied environments (onboard vessels, at the jetty, in transit, or at headquarters in Jakarta). If geolocation relies only on browser GPS, permission denial breaks the automated flow. If it relies only on manual presets, users cannot instantly adapt the report to their current physical station ("contoh saya di jakarta dan langsung lokasi berganti di jakarta").
  - *Architecture (Dual-Engine Location & Port Auto-Switching):*
    1. *High-Accuracy GPS (First Pass):* Attempt `navigator.geolocation.getCurrentPosition` with a 6-second timeout for mobile devices and GPS-equipped laptops.
    2. *Zero-Permission IP-Based Fallback (Second Pass):* If GPS is denied, unavailable, or times out, immediately and seamlessly fall back to client-side or backend IP Geolocation (e.g. `https://ipwho.is/` or local `weather_api.php`). IP lookup requires zero browser permissions and instantly resolves the user's city (e.g. Jakarta, Balikpapan, Surabaya) and regional coordinates.
    3. *Reverse Geocoding & Port Matching:* Pass coordinates through reverse geocoding (`api.bigdatacloud.net` or local lookup) to identify the municipality. Automatically map municipal names to canonical commercial port terminals (e.g. `Jakarta` -> `Tanjung Priok Port (Jakarta)`, `Banten / Cilegon` -> `Cigading Port`, `Kutai / Bengalon` -> `Lubuk Tutung Port (Kobexindo Jetty)`).
    4. *Cascading Real-Time Synchronization:*
       - Update the port input in the form.
       - Update the header KPI summary bar (`Pelabuhan Aktif: [City]`).
       - Immediately fetch live meteorological and marine wave telemetry for those exact coordinates.
       - Re-render the live A4 document header (`Port of Call`) and Section B weather card in real time.
       - Provide both an explicit `[ 📍 Deteksi Lokasi Saya (GPS / IP) ]` button and categorized 1-click location preset cards so users can toggle between their physical location and target vessel terminals instantly.
- **Single-Column Time Picker Simplicity vs Double-Column Clutter Trap in Tabular SOF:**
  - *Trap:* Placing two separate time pickers (Start Time and End Time) side-by-side inside every row of an operational milestone table.
  - *Mechanism:* Most operational events (arrival, NOR, dropped anchor, inspection, commence) occur at a single discrete point in time. Displaying two time inputs per row clutters the table, reduces horizontal space for descriptions, and causes cognitive confusion for users.
  - *Rule:* Keep the primary time column to exactly **one** `<input type="time">` per row with `onclick="this.showPicker()"`. For events that span durations, let the single time picker capture the event milestone and document the end time in the description (e.g. `Waiting port authority onboard (until 09:50 hrs)`).
- **Live Meteorological & Marine Satellite Telemetry Architecture (Google Weather & Satellite Dual-Engine):**
  - *Trap:* Leaving weather telemetry purely manual or relying on proprietary weather APIs that require paid keys or fail under browser CORS restrictions.
  - *Mechanism:* Commercial vessel loading reports require real-time, defensible meteorological data on the exact day and shift the report is generated (especially wind speed in Knots, precipitation probability for hatch closure, and swell height). Manual entry wastes time and invites guesswork.
  - *Architecture (Dual-Engine Live Weather Telemetry):*
    1. *Local Backend Proxy (`weather_api.php`):* Maintains a lookup table of regional maritime port coordinates (e.g. Lubuk Tutung `0.7667° N, 117.7333° E`, Taboneo `-3.7333° S, 114.4833° E`, Bahodopi `-2.8167° S, 122.1500° E`, Cigading `-6.0167° S, 105.9500° E`).
    2. *Zero-Auth CORS-Enabled Direct Fallback:* If hosted statically or run offline from `file:///`, fall back directly to Open-Meteo Weather & Marine APIs (NOAA/ECMWF feeds) without requiring API keys.
    3. *Automated Unit Conversions:* Convert km/h to Knots (`kmh * 0.54`) and map to standard Beaufort scale terms (Gentle Breeze, Fresh Breeze, Light Air). Parse swell and wind wave heights into a clean marine string (`Calm / Smooth, Swell 0.1 – 0.3 Mtr`).
    4. *Operational Impact Synthesis:* Automatically evaluate rain probability (>60%) and WMO weather codes to generate an actionable operational advisory (e.g. recommending continuous loading vs standby hatch closure).
    5. *User Feedback & Telemetry Status:* Provide an explicit `[ 🔄 Sync Cuaca Live ]` button with a spinning indicator, live connection badge (`● Live Connected: [Port]`), and real-time update timestamp.
- **Automatic Operational Hours & Loading Rate Telemetry Calculation:**
  - Pair Commence Date/Time (`inpCommenceDate`, `inpCommenceTime`) with Cut-Off Date/Time (`inpCutoffDate`, `inpCutoffTime`).
  - Compute active shift operating hours automatically:
    $$\text{Operating Hours} = \frac{\text{Timestamp}_{\text{Cutoff}} - \text{Timestamp}_{\text{Commence}}}{3600 \times 1000}$$
  - Feed this value directly into the real-time average loading rate ($\text{MT} / \text{Hour}$), eliminating manual arithmetic and human calculation errors during shift handovers.

### Dual Deliverable Standard: Vector PDF & One-Click Chat Copy
- Provide two instant dispatch channels:
  1. **`[ 📄 Unduh PDF Resmi ]`:** Pre-fills `document.title = LOADING_REPORT_${vessel}_${port}_BGM` and invokes native vector printing (`window.print()`) rendering a 100% crisp, A4 corporate document complete with diamond agency logos, tabular particulars, weather widget, SOF timeline, and photo annex.
  2. **`[ 📋 Salin Format Email / WA ]`:** Copies clean, standardized plain-text markdown matching international shipping agency protocols directly to clipboard, allowing operators to send comprehensive updates to charterers (e.g. Mr. Hadi) in under 5 seconds.

