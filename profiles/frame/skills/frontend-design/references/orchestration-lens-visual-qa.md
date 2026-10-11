# Fleet Orchestration & LENS Visual QA (distilled from fleet-visual-intelligence v3.1 + lens-visual-qa-engine v1.0)

## Role map (responsibilities are fixed; never blur them)
- ORION routes by Design Depth: D0 existing-system patch (FRAME, optional quick check) · D1 small feature on existing visual language (delta guidance → FRAME → LENS) · D2 new dashboard/product/redesign (multi-source research, >=3 directions, DNA+Contract) · D3 flagship art direction (deep research, 3–5 directions, remediation loop). Spawn a specialist only when it owns a unique uncertainty, deliverable, or verification.
- AURORA (design owner): product understanding before style; >=8 live references mapped with relevance / what-to-learn / what-NOT-to-copy; >=3 structurally distinct directions (not 3 palettes on one wireframe, no crippled strawman candidates); anti-generic gate (would it still look distinct with logo+copy removed?); then write DESIGN_DNA.md (archetype, grid, density, typography, color, signature elements, anti-patterns) and DESIGN_CONTRACT.md (layout, breakpoints, all states, tokens, motion).
- FRAME: implement the contract faithfully; UI libraries are primitives, not art direction; partition parallel child work by coherent ownership (shell / data / forms / responsive / motion) and merge holistically.
- LENS: independent verifier; may NEVER edit source, CSS, or git history.
- Implementers never self-certify; any code change invalidates prior PASS — retest the fresh SHA.

## Design-taste memory rule
Store only high-signal principles validated by operator feedback, with the context where each pattern fits. Never archive whole projects as reusable templates; every major project restarts from product understanding + live domain research.

---

# LENS 5-Gate Fail-Fast QA

## Philosophy
Never use a stochastic tool (VLM) for a deterministic job (geometry, contrast, runtime health). Fail-fast: gate N+1 never runs if gate N failed. Prove the harness itself before judging production.

## Gates
**Gate 0 — Runtime Health (<50ms):** zero console.error / uncaught exceptions; zero asset responses >= 400 (fonts, SVG, images, chunks); `document.fonts.ready` + network idle; DOM stable (MutationObserver quiet >= 200ms).
**Gate 1 — DOM & Semantic Integrity (<100ms):** banned-token scan on visible text (`/\b(undefined|NaN|\[object Object\]|null|Error:|NaNpx|\{\{.*\}\}\b/i`, excluding `code`/`pre`/`samp`/`[data-allow-raw-tokens]`); every `img` naturalWidth > 0; every `svg` has nonzero box and >=1 rendered shape; zero tofu (\uFFFD); page scrollWidth <= innerWidth; CDP AXTree: zero unlabelled interactive controls.
**Gate 2 — Metrology & Token Contract (<200ms):** WCAG contrast >= 4.5:1 normal / >= 3.0:1 large, computed from rendered colors (luminance L = 0.2126R + 0.7152G + 0.0722B); `data-ui-*` schema validation; silent clipping = scrollWidth > clientWidth with overflow:hidden and no ellipsis; touch targets >= 44x44 mobile / 36x36 desktop.
**Gate 3 — Interaction & Viewport Fuzzing (<2s):** viewport scrub 320→1920 in 25px steps asserting zero horizontal overflow; extreme content fuzz (200-char unbroken string, RTL Arabic, complex emoji, 0 / 999999999999 / negatives) without layout break; tab-walk asserts visible `:focus-visible` not occluded by sticky headers or overlays; CLS < 0.05.
**Gate 4 — VLM Macro Aesthetic (only after 0–3 pass):** 1:1 sector crops (never downscaled full-page); judge hierarchy, calm, theme cohesion; assign GENERIC RISK LOW/MEDIUM/HIGH — HIGH blocks PASS; verify the 2–5 DESIGN_DNA signature elements exist.

## Failure codes & dispatch
G0_CONSOLE_ERROR, G0_ASSET_4XX_5XX, G0_FONT_TIMEOUT, G0_HYDRATION_RACE · G1_FORBIDDEN_TOKEN, G1_BROKEN_IMAGE, G1_EMPTY_SVG, G1_TOFU_GLYPH, G1_VIEWPORT_OVERFLOW, G1_AXTREE_UNLABELLED · G2_CONTRAST_FAIL, G2_SCHEMA_DRIFT, G2_SILENT_CLIPPING, G2_TOUCH_TARGET_SMALL, G2_TOKEN_HARDCODED · G3_RESPONSIVE_BREAK, G3_STRESS_OVERFLOW, G3_FOCUS_INVISIBLE, G3_FOCUS_OCCLUDED, G3_EXCESSIVE_CLS · G4_GENERIC_AI_SLOP (blocks PASS), G4_SIGNATURE_MISSING, G4_HIERARCHY_NOISE, G4_THEME_INCOHESION.
Dispatch G0–G3 defects to FRAME with exact selector, computed values, viewport; G4 to FRAME, or AURORA when the contract itself needs clarification. Any CRITICAL defect → verdict FAIL immediately.

## Runtime schema contract (`data-ui-*`)
Declarative attributes in the DOM remove verifier guesswork and evaluate deterministically in <10ms with zero tokens:
- `data-ui-surface` (base|elevated|overlay|glass-specular|sunken) → computed background/backdrop-filter must match the declared token.
- `data-ui-role` (shell|hero|metric-card|data-grid|toolbar|modal) → structural identity.
- `data-ui-overflow` (contain|scroll-x|scroll-y|visible) → contain asserts scrollWidth/Height <= clientWidth/Height.
- `data-ui-min-touch="N"` → rect >= NxN on touch viewports.
- `data-ui-align` → optical alignment delta <= 1.5px.
- `data-ui-typography` (display|heading-1|heading-2|body|caption|mono) → computed font matches the token scale.
- `data-ui-truncate` (ellipsis|clamp-2|clamp-3|wrap) → ellipsis asserts text-overflow + nowrap.
- `data-ui-contrast=">=4.5"` → measured ratio meets the floor.
- `data-allow-raw-tokens` exempts code/doc subtrees from Gate 1; `data-ui-intentional-overlap` exempts badges/stacks from collision detection.

## Synthetic mutation calibration (who watches the watcher)
Before auditing a production build, inject 5 mutants into a sandbox copy and require 100% detection: M1 "user: undefined" heading → G1_FORBIDDEN_TOKEN · M2 img src→404 → G1_BROKEN_IMAGE · M3 text color = background → G2_CONTRAST_FAIL · M4 container height:12px overflow:hidden on a 3-line paragraph → G2_SILENT_CLIPPING · M5 emptied `<svg></svg>` icon → G1_EMPTY_SVG. Mutation Score < 100% ⇒ verdict HARNESS_UNCALIBRATED_FAIL; the harness may not certify production until it catches every mutant.

## Coverage & evidence
Surface audit closure must be mathematical: Discovered = Tested + Justified N/A + Blocked; any unclassified surface is a FAIL. A runnable Playwright/CDP harness (Gate 0–3 + mutation calibration) lives at fleet-upgrade/lens-visual-qa-engine/scripts/lens_audit_harness.js.

## Macro-compositional diversity gate
Token diffing is not diversity: swapping palette or font on the same wireframe is not variation, and comparing across unlike domains cherry-picks. Before any DIVERSITY: PASS, compare against every fleet project of the last 30 days across 5 dimensions — layout archetype/shell, metric/telemetry presentation, navigation model, data presentation, surface hierarchy. LENS issues two separate scores: TOKEN_DIVERSITY and MACRO_COMPOSITION_DIVERSITY; MACRO_COLLISION forces overall FAIL. FRAME must never normalize an innovative contract layout back into sidebar + 4-KPI-card flexbox for convenience, and must verify all signature elements exist in the rendered DOM.