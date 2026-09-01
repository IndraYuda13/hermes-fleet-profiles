# Owner Visual Acceptance State Machine & Mobile Rendering Invariants

## 1. Strict Owner Visual Acceptance State Machine

For all UI/UX missions, internal verification and external human acceptance are decoupled by strict state rules:

```text
Before Owner Evaluation:
  INTERNAL_RELEASE_GATE   = PASS | FAIL (internal agent consensus & test suites)
  OWNER_VISUAL_ACCEPTANCE = PENDING (owned exclusively by human owner)
  MISSION_RELEASE_STATE   = AWAITING_OWNER

Upon Owner Feedback:
  If Owner says PASS -> OWNER_VISUAL_ACCEPTANCE = PASS, MISSION_RELEASE_STATE = ACCEPTED
  If Owner says FAIL -> OWNER_VISUAL_ACCEPTANCE = FAIL, MISSION_RELEASE_STATE = VISUAL_REMEDIATION_REQUIRED
```

- **Invariant:** Internal agents (ORION, AURORA, FRAME, LENS, PRISM, SENTINEL) and automated test suites are strictly prohibited from declaring `OWNER_VISUAL_ACCEPTANCE = PASS`.
- **Supremacy:** An owner `FAIL` verdict decisively overrides all internal `PASS` declarations.

---

## 2. Mobile Form Control & SVG Rendering Invariants

### A. Reset Native Form Controls (`appearance: none`)
- Frameworks and desktop Chrome often mask unstyled `<select>`, `<input>`, and `<button>` elements.
- On mobile iOS WebKit and Android Chrome, unstyled `<select>` elements render ugly native OS drop-down styling and gradient borders.
- **Rule:** Always apply:
  ```css
  select, input, button {
    -webkit-appearance: none;
    -moz-appearance: none;
    appearance: none;
  }
  ```
  and provide custom SVG chevron/indicator icons.

### B. Explicit Inline SVG `fill="none"` Invariant
- Per SVG 1.1/2.0 specifications, any `<circle>`, `<path>`, or `<rect>` without an explicit `fill` attribute defaults to `#000000` (solid black).
- Relying purely on CSS classes (e.g. `.radial-bg { fill: none; }`) causes race conditions on mobile WebKit where the SVG paints as a solid black circular blob before external CSS finishes parsing.
- **Rule:** Always include inline `fill="none"` directly in SVG HTML:
  ```html
  <circle class="radial-bg" cx="50" cy="50" r="42" fill="none" stroke-width="8"></circle>
  ```

### C. Static Asset Versioning & Cache-Busting
- Production HTML files must link CSS/JS assets with version query strings (e.g. `apex.css?v=3.3.1`) to prevent Cloudflare edge or mobile device cache poisoning across deployments.

### D. Macro-Composition Negative Portfolio Comparison
- Never evaluate UI diversity against a single cherry-picked baseline.
- Audit proposed candidates across 12 macro-dimensions against all recent fleet UI projects (`incident-monitor`, `timesfm-trading`, `quant-entropy-telemetry`, `websocket-chat-demo`, etc.) before selecting a direction.
