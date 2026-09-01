# LENS 5-Gate Fail-Fast Specification & Failure Codes

Every defect detected by LENS must be tagged with a standardized failure code and gate identifier.

## Gate 0: Runtime Health & Network Telemetry
| Code | Name | Description | Severity |
|---|---|---|---|
| `G0_CONSOLE_ERROR` | Uncaught JS Exception | Browser console emitted a `TypeError`, `ReferenceError`, or unhandled promise rejection. | CRITICAL |
| `G0_ASSET_4XX_5XX` | Broken Static Asset | Network response for font, SVG, CSS, JS chunk, or image returned HTTP status >= 400. | CRITICAL |
| `G0_FONT_TIMEOUT` | WebFont Load Failure | `document.fonts.ready` did not resolve within the stabilization timeout. | HIGH |
| `G0_HYDRATION_RACE` | Unsettled DOM Lifecycle | DOM mutations continued past the 200ms debounce threshold (unstable hydration/infinite re-render). | HIGH |

---

## Gate 1: DOM & Semantic Integrity
| Code | Name | Description | Severity |
|---|---|---|---|
| `G1_FORBIDDEN_TOKEN` | Data Binding Leak | Raw primitive token (`undefined`, `null`, `NaN`, `[object Object]`) rendered in visible UI text. | CRITICAL |
| `G1_BROKEN_IMAGE` | Zero-Size Image | Tag `<img>` rendered with `naturalWidth === 0` or missing `src`. | HIGH |
| `G1_EMPTY_SVG` | Missing Icon Geometry | Tag `<svg>` has bounding box 0x0 or contains no rendered shape/path elements. | HIGH |
| `G1_TOFU_GLYPH` | Missing Font Glyph | Character rendered as replacement tofu box (`\uFFFD`). | HIGH |
| `G1_VIEWPORT_OVERFLOW` | Horizontal Page Bleed | `document.documentElement.scrollWidth > window.innerWidth` at default viewport. | CRITICAL |
| `G1_AXTREE_UNLABELLED` | Unaccessible Control | Interactive control (button/link/input) lacks accessible name in CDP AXTree. | MEDIUM |

---

## Gate 2: Deterministic Metrology & Token Contract
| Code | Name | Description | Severity |
|---|---|---|---|
| `G2_CONTRAST_FAIL` | WCAG Contrast Violation | Computed text-to-background contrast ratio is < 4.5:1 (normal text) or < 3.0:1 (large text/icons). | HIGH |
| `G2_SCHEMA_DRIFT` | Runtime Contract Mismatch | Element with `data-ui-*` violates its declared contract (e.g. touch target < 44px). | HIGH |
| `G2_SILENT_CLIPPING` | Text Clipped Without Ellipsis | `scrollWidth > clientWidth` with `overflow: hidden` but without `text-overflow: ellipsis`. | HIGH |
| `G2_TOUCH_TARGET_SMALL` | Undersized Touch Target | Interactive element has bounding box < 44x44px on mobile or < 36x36px on desktop. | MEDIUM |
| `G2_TOKEN_HARDCODED` | Arbitrary Hex / CSS Drift | Core surface or text color bypasses declared CSS variables in `DESIGN_CONTRACT.md`. | MEDIUM |

---

## Gate 3: Active Interaction & Viewport Fuzzing
| Code | Name | Description | Severity |
|---|---|---|---|
| `G3_RESPONSIVE_BREAK` | Intermediate Viewport Bleed | Horizontal scrollbar appeared during continuous 320px-1920px viewport scrubbing. | HIGH |
| `G3_STRESS_OVERFLOW` | Long Content Layout Break | Extreme 200-char string or numeric boundary payload broke container boundary without wrapping. | HIGH |
| `G3_FOCUS_INVISIBLE` | Missing Focus Ring | Keyboard Tab navigation focused an element without a visible `:focus-visible` indicator. | MEDIUM |
| `G3_FOCUS_OCCLUDED` | Focus Trapped Under Overlay | Focused active element is covered by a sticky header, floating pill, or modal backdrop. | HIGH |
| `G3_EXCESSIVE_CLS` | Layout Shift Violation | Cumulative Layout Shift (CLS) exceeded 0.05 during interaction walk. | MEDIUM |

---

## Gate 4: VLM Macro Aesthetic & Art Direction
| Code | Name | Description | Severity |
|---|---|---|---|
| `G4_GENERIC_AI_SLOP` | High Generic Risk | UI relies on generic AI tropes (arbitrary purple/cyan gradients, unstyled shadcn defaults, card spam). | HIGH (BLOCKS PASS) |
| `G4_SIGNATURE_MISSING` | Missing Signature Motif | One or more of the 2-5 unique design motifs from `DESIGN_DNA.md` are absent. | HIGH |
| `G4_HIERARCHY_NOISE` | Broken Visual Rhythm | Visual noise dominates; primary CTA or key telemetry metrics lack clear optical hierarchy. | MEDIUM |
| `G4_THEME_INCOHESION` | Surface Incohesion | Inconsistent elevation, corner radius philosophy, or font pairing across different sections. | MEDIUM |

---

## Remediation Dispatch Rules
1. **Gate 0, Gate 1, Gate 2, Gate 3 defects** $\to$ Dispatch directly to **FRAME** with exact CSS selector, computed values, and viewport dimensions.
2. **Gate 4 defects** $\to$ Dispatch to **FRAME** (implementation fix) or **AURORA** (if design contract clarification is needed).
3. **Any CRITICAL defect** immediately blocks the pipeline with verdict `FAIL`.
