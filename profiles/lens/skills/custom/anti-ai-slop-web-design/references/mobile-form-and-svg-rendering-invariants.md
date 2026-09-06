# Mobile Form Control, Responsive Layout & SVG Rendering Reference (Fleet V3.3)

## 1. Resetting Native OS Form Controls (iOS Safari & Android Chrome)

Desktop Chrome often renders unstyled `<select>` elements with transparent backgrounds, masking missing CSS. However, real mobile devices (WebKit and Android) inject native OS chrome, rounded gray borders, and native arrow graphics.

### Mandatory CSS Baseline for All Form Controls:
```css
/* 1. Global appearance reset */
select,
input[type="text"],
input[type="search"],
button {
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
  border-radius: 0;
  margin: 0;
}

/* 2. Custom Select Wrapper Pattern */
.custom-select-wrapper {
  position: relative;
  display: inline-flex;
  align-items: center;
}

.custom-select {
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
  background: var(--apex-bg-surface-2);
  color: var(--apex-text-primary);
  border: 1px solid var(--apex-border-subtle);
  border-radius: var(--apex-radius-xs);
  padding: 4px 24px 4px 8px; /* Extra right padding for custom chevron */
  font-family: var(--font-mono);
  font-size: 11px;
  cursor: pointer;
  outline: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23F59E0B' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 6px center;
  background-size: 10px;
}

.custom-select:focus {
  border-color: var(--apex-amber-base);
  box-shadow: 0 0 0 1px var(--apex-amber-base);
}
```

---

## 2. SVG Default Fill Defense (`fill="none"`)

### The Default SVG Black Fill Trap:
According to the W3C SVG specification, the initial value of the `fill` property on SVG shape elements (`<circle>`, `<path>`, `<rect>`, `<polygon>`) is `black` (`#000000`).
If SVG markup relies solely on an external stylesheet (e.g. `.radial-bg { fill: none; }`), mobile WebKit or initial paint cycles can render the shape with a **solid black fill**, creating giant dark blobs over the UI.

### Mandatory SVG Markup Rule:
Always declare `fill="none"` directly as an inline attribute on the SVG element:

```html
<!-- CORRECT: Inline fill defense -->
<svg class="health-radial-svg" viewBox="0 0 100 100" aria-hidden="true">
  <circle class="radial-bg" cx="50" cy="50" r="42" fill="none" stroke-width="8"></circle>
  <circle class="radial-progress" cx="50" cy="50" r="42" fill="none" stroke-width="8" stroke-dasharray="263.89"></circle>
</svg>
```

---

## 3. Deliberate Mobile Segmented Deck Architecture (360px–430px)

### Anti-Pattern: The Infinite Vertical Card Dump
When desktop layouts with multiple toolbars, search boxes, and tables are naively converted to mobile with simple `flex-direction: column`, the mobile UI becomes a long, unconstrained vertical scroll list of 20+ elements where navigation and context are lost.

### Best Practice: Intentional Multi-Bay Dock Architecture
1. **Single-Active-Bay Viewport:** On mobile screens (`<768px`), display only the active bay (`bay-pulse`, `bay-matrix`, or `bay-triage`) occupying `height: calc(100vh - header - dock)`.
2. **Fixed Bottom Mobile Dock:** Provide quick-switching tabs with haptic feedback styling, active indicators, and real-time alert badges.
3. **Sub-Header Responsive Reflow:** Multi-control headers (e.g. Title + Sort Dropdown + Counter) must reflow into a structured 2-row layout on mobile rather than overflowing or colliding.
4. **Bottom Safe Area Padding:** Scrolling containers must always have `padding-bottom: calc(env(safe-area-inset-bottom) + 72px)` so the bottom card clears the fixed navigation dock.
