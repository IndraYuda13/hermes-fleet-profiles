# Design Contract as Runtime Schema (`data-ui-*`)

This protocol standardizes the collaboration contract between **AURORA** (Design Specification), **FRAME** (Frontend Implementation), and **LENS** (Automated Verification).

---

## 1. Why Runtime Schemas?
Traditional visual QA fails because the verifier has to "guess" whether an overlapping badge, an asymmetrical grid, or an unusual margin is intentional art direction or a rendering defect.

By embedding declarative `data-ui-*` attributes in the DOM:
- **AURORA** defines the contract in `DESIGN_CONTRACT.md`.
- **FRAME** embeds lightweight `data-ui-*` attributes into component JSX/HTML.
- **LENS** validates computed styles deterministically in < 10ms with zero AI token cost.

---

## 2. Core `data-ui-*` Attribute Specification

### A. Surface & Hierarchy
| Attribute | Allowed Values | Verification Invariant |
|---|---|---|
| `data-ui-surface` | `base`, `elevated`, `overlay`, `glass-specular`, `sunken` | Computed `background-color` and `backdrop-filter` must match the declared design token CSS variable. |
| `data-ui-role` | `shell`, `hero`, `metric-card`, `data-grid`, `toolbar`, `modal` | Validates structural container identity in layout hierarchy. |

### B. Geometry & Overflow Containment
| Attribute | Allowed Values | Verification Invariant |
|---|---|---|
| `data-ui-overflow` | `contain`, `scroll-x`, `scroll-y`, `visible` | If `contain`: assert `el.scrollWidth <= el.clientWidth && el.scrollHeight <= el.clientHeight`. If `visible`: assert intentional out-of-flow context (`position: absolute/fixed`). |
| `data-ui-min-touch` | Number (e.g. `44`, `48`) | Assert `rect.width >= N && rect.height >= N` on touch-enabled viewports. |
| `data-ui-align` | `center`, `start`, `end`, `stretch` | For flex/grid containers, validates optical alignment delta <= 1.5px. |

### C. Typography & Content Protection
| Attribute | Allowed Values | Verification Invariant |
|---|---|---|
| `data-ui-typography` | `display`, `heading-1`, `heading-2`, `body`, `caption`, `mono` | Computed `font-family`, `font-size`, and `line-height` match typography token scale. |
| `data-ui-truncate` | `ellipsis`, `clamp-2`, `clamp-3`, `wrap` | If `ellipsis`: assert `text-overflow === 'ellipsis' && white-space === 'nowrap'`. |
| `data-ui-contrast` | `>=4.5`, `>=3.0`, `>=7.0` | Computed relative luminance contrast ratio must meet or exceed the specified ratio. |

### D. Bypass & Intentional Exceptions
| Attribute | Purpose | Verification Behavior |
|---|---|---|
| `data-allow-raw-tokens` | Marks code blocks, JSON viewers, tech documentation | Disables Gate 1 banned token scanner (`undefined`/`null`) for this element's subtree. |
| `data-ui-intentional-overlap` | Marks floating notification badges, avatar stacks | Disables Gate 2 sibling collision detection for this element. |

---

## 3. Implementation Example (FRAME)

```html
<!-- Primary Action Button with Explicit Runtime Contract -->
<button
  class="btn-primary"
  data-ui-role="action-btn"
  data-ui-min-touch="44"
  data-ui-contrast=">=4.5"
  data-ui-surface="elevated"
>
  <svg class="icon" data-ui-icon="cart" viewBox="0 0 24 24">
    <path d="M..."/>
  </svg>
  <span>Confirm Payment</span>
</button>

<!-- Code Block with Explicit Token Whitelist -->
<pre data-allow-raw-tokens="true">
  <code>const value = null; // Valid technical text</code>
</pre>
```

---

## 4. Deterministic LENS Evaluator (Browser Context)

```javascript
// LENS executes this in page context via CDP / Playwright:
function validateRuntimeSchemas() {
  const defects = [];

  // 1. Validate Touch Targets
  document.querySelectorAll('[data-ui-min-touch]').forEach(el => {
    const min = parseFloat(el.getAttribute('data-ui-min-touch'));
    const rect = el.getBoundingClientRect();
    if (rect.width < min || rect.height < min) {
      defects.push({
        code: 'G2_SCHEMA_DRIFT',
        selector: getSelector(el),
        message: `Touch target ${rect.width.toFixed(1)}x${rect.height.toFixed(1)}px is smaller than required ${min}x${min}px`
      });
    }
  });

  // 2. Validate Overflow Containment
  document.querySelectorAll('[data-ui-overflow="contain"]').forEach(el => {
    if (el.scrollWidth > el.clientWidth || el.scrollHeight > el.clientHeight) {
      defects.push({
        code: 'G2_SILENT_CLIPPING',
        selector: getSelector(el),
        message: `Element overflows containment bounds: scrollWidth=${el.scrollWidth}, clientWidth=${el.clientWidth}`
      });
    }
  });

  return defects;
}
```
