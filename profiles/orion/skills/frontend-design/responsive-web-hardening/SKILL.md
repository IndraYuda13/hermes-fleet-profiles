---
name: responsive-web-hardening
description: Use when hardening web UI for mobile screen responsiveness.
---

# Responsive Web Hardening & Mobile Viewport Standard

Engineering rules, layout invariants, form ergonomics, and headless testing standards for building hardened, mobile-first responsive web interfaces.

---

## 1. When to Use

Use this skill when:
1. Converting desktop-centric web layouts into fluid, thumb-friendly mobile interfaces.
2. Diagnosing horizontal overflow blowouts, text truncation, or displaced hamburger menus on mobile screens ($\le 480\text{px}$).
- **Hardening touch target accessibility, interactive slider controls, and multi-category filters for mobile viewports.**
- Verifying responsive UI rendering using headless browser automation (Chromium CLI, Playwright, Puppeteer).
4. Restructuring interactive forms, search bars, and sticky ad/nav containers for touch devices.

---

## 2. Core Procedural Workflow

### Step 1: Viewport & Root Overflow Guardrails
Every mobile-first layout must establish non-negotiable viewport constraints:
1. Ensure the standard viewport meta tag is present in `<head>`:
   ```html
   <meta name="viewport" content="width=device-width, initial-scale=1.0">
   ```
2. Lock the root and container elements against accidental horizontal scrolling:
   ```css
   html, body {
     max-width: 100%;
     overflow-x: hidden;
     box-sizing: border-box;
   }
   *, *::before, *::after {
     box-sizing: inherit;
   }
   ```
3. Wrap all tabular data in a scrollable containment container (`<div class="table-responsive">`) to prevent wide tables from stretching the viewport width.

---

### Step 2: Mobile Form Geometry (Stacked Card Standard)
- **The Horizontal Input-Group Blowout Anti-Pattern:**
  Nesting an input field and an action button with `white-space: nowrap` inside a single-row flex container on mobile screens (< 576px) causes horizontal overflow blowout when input min-width plus button padding exceeds the 360px–390px viewport width.
- **Stacked Card Standard:**
  On mobile viewports, stack search and action forms vertically inside a distinct card container (`flex-direction: column` with full-width `w-100` action buttons). Reserve single-row inline layouts strictly for desktop viewports (`@media (min-width: 768px)`):
  ```html
  <div class="search-card p-3 rounded-4 bg-white shadow-sm">
    <div class="d-flex flex-column flex-md-row gap-2">
      <input type="text" class="form-control form-control-lg" placeholder="Cari nama...">
      <button class="btn btn-primary btn-lg fw-bold w-100 w-md-auto text-nowrap">Cek Sekarang</button>
    </div>
  </div>
  ```
  This creates a large, thumb-friendly tap target ($\ge 48\text{px}$ height) spanning the viewport width for effortless single-hand mobile operation.

---

### Step 3: Card Header Geometry & Badge Clearance (Stacked Header Standard)
- **The Horizontal Flex Heading + Badge Squishing Anti-Pattern:**
  Placing a heading (`<h4>`) and an un-shrinkable badge (`<span class="badge">` with `white-space: nowrap`) inside a single-row flex container (`d-flex justify-content-between align-items-center`) without responsive stacking causes severe vertical squishing on mobile viewports ($\le 480\text{px}$).
  - *Mechanism:* The badge has a fixed width (180–220px for license or status codes). In a 320–360px viewport card with 32–48px internal padding, only 60–100px remains for the heading. If the heading text is long, the flex item is crushed into an ultra-narrow column.
  - *Aggravating Factor:* Combining this layout with `word-break: break-word` or `word-break: break-all` in CSS causes the crushed heading to break every word into 1- to 2-letter syllables stacked vertically into an unreadable column (e.g. `Kr-ed-iv-o`).
- **Stacked Card Header Standard:**
  Always stack card titles and metadata badges vertically on mobile viewports using responsive flex directions:
  ```html
  <div class="d-flex flex-column flex-sm-row justify-content-between align-items-start align-items-sm-center gap-2 mb-3">
    <h4 class="fw-bold text-dark mb-0 fs-5">1. Kredivo (PT Fintek Digital Indonesia)</h4>
    <span class="badge bg-success flex-shrink-0 align-self-start align-self-sm-auto">Berizin OJK: KEP-104/D.05/2019</span>
  </div>
  ```
  - *Typography Rule:* Use `word-break: normal; overflow-wrap: break-word;` on headings and card titles so words wrap naturally at space boundaries without breaking syllables unless an unbroken token exceeds the viewport width.

---

### Step 4: Responsive Header & Hamburger Toggle Clearance
- **Navbar Badge Clearance Invariant:**
  In headers containing brand text and supplementary status/compliance badges, collapse or hide secondary badges on small screens (`d-none d-sm-inline-block`).
  - *Mechanism:* Keeping secondary badges visible in the top flex row crowds out the hamburger menu toggle (`☰`), pushing it off-screen or causing it to wrap into an awkward second line.
- **Touch Target & Position Invariant:**
  Anchor the hamburger toggle to the far right with `justify-content: space-between`, ensuring its bounding box maintains $\ge 44 \times 44\text{px}$ touch bounds and at least 12px margin from the viewport edge.

---

### Step 5: Fluid Typography Over Static Desktop Scales
- Avoid fixed font sizes on primary headlines (e.g. static `2.35rem` / ~38px on `h1`).
- Implement CSS fluid typography using `clamp()` to scale typography smoothly across screen widths:
  ```css
  h1.hero-title {
    font-size: clamp(1.4rem, 4.5vw, 2.35rem);
    line-height: 1.25;
    overflow-wrap: break-word;
    word-break: normal;
  }
  ```
  This guarantees that long titles wrap naturally onto 2–3 lines without clipping glyphs or overflowing containers.

---

### Step 6: Touch Target Hardening (WCAG 2.1 & Google Usability Standards)
Default framework button classes (e.g. Bootstrap `.btn-sm`, `.btn-close`) frequently render at 28px–31px height, failing WCAG 2.1 touch target criteria (minimum 38px–44px) and causing mis-taps on mobile touchscreens.
- **Global Touch Target Floor**:
  ```css
  .btn-sm {
    padding: 7px 14px !important;
    font-size: 0.84rem !important;
    min-height: 38px !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
  }
  .btn-close {
    min-height: 32px !important;
    min-width: 32px !important;
    padding: 8px !important;
  }
  ```
- **Form Controls & Sliders**:
  Ensure every range slider (`<input type="range">`), number input, and select element has an explicit `<label for="...">` and an `aria-label` attribute describing its function and units.

---

### Step 7: Mobile Pill Rails for Multi-Category Catalogs
Wrapping 5+ category filter pills with `flex-wrap: wrap` on small screens pushes primary content down by 100px–150px.
- **Horizontal Scrollable Pill Rail Standard**:
  Wrap filter pills in a touch-scrolling track that does not wrap vertically:
  ```css
  .filter-pills-scroll {
    display: flex;
    flex-wrap: nowrap;
    overflow-x: auto;
    gap: 8px;
    padding-bottom: 4px;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none; /* Hide default scrollbar on Firefox */
  }
  .filter-pills-scroll::-webkit-scrollbar {
    display: none; /* Hide scrollbar on Chrome/Safari */
  }
  .filter-pills-scroll .btn-filter-category {
    flex-shrink: 0;
    min-height: 40px;
    padding: 8px 16px;
    white-space: nowrap;
  }
  ```
  This keeps the interface compact, visually modern, and ergonomically swipeable by thumbs.

---

### Step 8: Long-Scroll Directory Ergonomics (Floating Back-to-Top Standard)
In long directories (such as regulatory catalogs or deep guides spanning 50+ cards), mobile users experience scrolling fatigue when returning to the search input or navbar.
- **Floating Action Button (FAB) Implementation**:
  ```html
  <button id="btn-back-to-top" class="btn-back-to-top" aria-label="Kembali ke atas">↑</button>
  ```
  ```css
  .btn-back-to-top {
    position: fixed;
    bottom: 24px;
    right: 24px;
    width: 44px;
    height: 44px;
    border-radius: 50%;
    background-color: var(--primary-color, #1e40af);
    color: #fff;
    border: none;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
    opacity: 0;
    visibility: hidden;
    transition: opacity 0.3s ease, visibility 0.3s ease, transform 0.2s ease;
    z-index: 1040;
  }
  .btn-back-to-top.show {
    opacity: 1;
    visibility: visible;
  }
  ```
  ```javascript
  const backToTopBtn = document.getElementById('btn-back-to-top');
  if (backToTopBtn) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 350) backToTopBtn.classList.add('show');
      else backToTopBtn.classList.remove('show');
    }, { passive: true });
    backToTopBtn.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }
  ```

---

### Step 9: Responsive Ad Slots & Fixed Banner Clearance
1. **Ad Slot Dimension Adaptation:**
   Never lock top or in-content ad containers to fixed desktop leaderboard dimensions (`728x90`). Use responsive wrappers that adapt to standard mobile IAB units (`320x50` or `300x250`):
   ```css
   .ad-slot-leaderboard {
     min-height: 50px;
     max-width: 100%;
   }
   @media (min-width: 768px) {
     .ad-slot-leaderboard { min-height: 90px; }
   }
   ```
2. **Fixed Sticky Footer Clearance Invariant:**
   When mounting fixed sticky mobile banners or bottom ads (`position: fixed; bottom: 0;`), declare explicit bottom padding on `body` or the main scroll container (`padding-bottom: calc(var(--sticky-banner-height) + 24px)`).
   - *Mechanism:* Without bottom clearance, fixed overlays occlude bottom legal disclaimers, action links, and quick tips even when the page is scrolled to the absolute bottom.

---

### Step 10: Headless Verification & Testing Standards

#### The Linux Desktop Chromium Minimum Window Width Pitfall (`kMinWindowWidth = 500px`)
When executing CLI commands like:
```bash
google-chrome --headless=new --window-size=390,844 --screenshot=out.png "https://example.com"
```
on Linux desktop Chromium builds, Blink's window manager enforces a minimum window width (`kMinWindowWidth = 500px`) unless mobile device emulation is driven via CDP (`Emulation.setDeviceMetricsOverride`).
- **The Artifact:** Chromium renders the layout at a viewport width of 500px (`window.innerWidth === 500`), but crops the saved PNG artifact to 390px, causing the right ~110px of content to appear falsely clipped/truncated.
- **Verification Rule:**
  1. For CLI-based headless screenshots on Linux without CDP emulation, set `--window-size` to $\ge 500\text{px}$ width (e.g. `--window-size=500,900`) to inspect the natural mobile layout without false screenshot clipping.
  2. For true $\le 412\text{px}$ mobile viewport audits, drive Chromium through CDP/Playwright with explicit `isMobile: true` and mobile user-agent emulation:
     ```python
     cdp("Emulation.setDeviceMetricsOverride", width=390, height=844, deviceScaleFactor=3, mobile=True)
     ```

---

## 3. Pitfalls & Anti-Patterns

- **Sub-36px touch targets (`btn-sm` trap)**: Leaving default framework `.btn-sm` styling (30-32px height) on mobile cards and filters violates WCAG 2.1 and creates mis-tap frustration. Enforce $\ge 38\text{px}$ to $44\text{px}$ minimum bounding height.
- **Vertical pill stacking blowout**: Wrapping 5+ filter tags with `flex-wrap: wrap` consumes excessive vertical screen space on mobile. Use horizontal swipeable pill rails (`overflow-x: auto; flex-wrap: nowrap;`).
- **Unlabeled range and numeric inputs**: Omitting `aria-label` or `<label for="...">` on mobile interactive sliders and input groups lowers accessibility scores and degrades assistive technology usability.
- **Single-row flex inputs on mobile**: Keeping an input and button side-by-side on $\le 480\text{px}$ viewports causes button text to push outside the screen boundary. Stack vertically on mobile.
- **Horizontal flex heading + badge squishing**: Pairing an unshrinkable badge (`white-space: nowrap`) and a long heading in a horizontal flex without `flex-column flex-sm-row` forces the heading into an ultra-narrow column. Stack vertically on small screens.
- **Aggressive word-break on headings**: Applying `word-break: break-word` or `break-all` on headings causes narrow columns to fracture words into vertical single-syllable stacks. Always use `word-break: normal; overflow-wrap: break-word;`.
- **Unbounded badges in mobile navbars**: Displaying multiple inline badges alongside the brand logo forces the hamburger toggle button off-screen. Hide secondary badges on mobile (`d-none d-sm-inline-block`).
- **Static desktop heading fonts**: Setting `h1` above `2rem` without `clamp()` causes awkward line breaks and overflow on 360px–390px devices.
- **Sticky banner occlusion**: Failing to add bottom padding equal to sticky footer height leaves critical compliance notices and CTA buttons unclickable beneath the overlay.
- **False-positive clipping diagnosis from CLI screenshots**: Diagnosing text wrapping as broken when running headless Chrome on Linux at `--window-size=390,844` without accounting for the 500px desktop minimum window constraint. Always test at $\ge 500\text{px}$ or use CDP mobile emulation.
