# Anti-AI Slop Quality Governance & Web Design Standard (Fleet V4)

This reference defines the quality governance standards of the Hermes fleet. Canonical upstream design authority resides in `visual-authoring-core`.

---

## Part A: Universal Quality Invariants (Non-Negotiable Hard Gates)

These invariants apply to ALL surfaces and products regardless of visual style, archetype, or domain:

1. **Deterministic Runtime Health:**
   - Zero unhandled browser console errors (`console.error`).
   - Zero failed network requests (4xx/5xx) for stylesheets, scripts, fonts, or assets.
   - Web fonts fully loaded before visual capture (`document.fonts.ready`).

2. **Geometry & Metrology:**
   - Zero unintended horizontal overflow across canonical viewports (320px, 390px, 768px, 1440px, 1920px).
   - Critical titles, metrics, hero copy, and navigation items must never be clipped by `overflow: hidden` without intentional ellipsis or line-clamp.

3. **Motion Invariant (Stable Status Not Animated):**
   - Stable states (`Active`, `Online`, `Available`, `Connected`, `Operational`) must NEVER pulse, ping, blink, breathe, or animate continuously without specific product justification. Use a calm text label with an optional static indicator dot.
   - Active background processes may feature motion, provided it clearly communicates activity and possesses an explicit termination state.
   - Full support for `@media (prefers-reduced-motion: reduce)`.

4. **Authentic Data Grounding:**
   - Zero undeclared placeholder stubs (`Lorem Ipsum`, `John Doe`, `NaN`, `undefined`, unreplaced template brackets `{{...}}`).
   - Zero fabricated marketing claims: no fake testimonials, fake user counts ("10,000+ Happy Customers"), or fake media logos. Data must reflect authentic domain facts or be explicitly labeled as illustrative.

5. **Feature-Conditional Accessibility (WCAG 2.2 AA Baseline):**
   - Normative WCAG 2.2 AA contrast ratios and keyboard operability with visible focus rings.
   - *Feature-Conditional Check:* Keyboard focus traps are tested ONLY if modal dialogs or flyout drawers are present. Form validation boundaries are tested ONLY if input forms are present. Never fail a surface for absent components.
   - *Hermes UX Quality Target:* Touch targets >= 44x44px on mobile viewports are enforced as a Hermes UX quality target (not mislabeled as a normative WCAG AA requirement). APCA may be recorded as a supplementary perceptual signal.

6. **Contextual Motifs (No Universal Syntax Bans):**
   - Pure black (`#000000`), gradients, borders, cards, sans-serif typography (such as Inter), pill navigation, and inertial scrolling (Lenis) are NOT universally forbidden.
   - The defect is **unmotivated, generic defaults** deployed without relevance to product truth—not the CSS syntax itself. Pure black is appropriate for OLED telemetry or astronomical HUDs; gradients are appropriate for realistic material lighting; Inter is appropriate for dense enterprise tables.

7. **Pragmatic Asset Gate:**
   - Design around authentic project assets when provided. If external assets are absent from the brief, use generated assets, procedural visuals, typography-led composition, or explicitly declared synthetic content. Never disguise undeclared placeholder grey boxes as final art.

---

## Part B: Contextual Reference Patterns (Optional Archetypes)

The following patterns represent proven solutions for specific surface modes (e.g. immersive storytelling, brand-forward launch pages, or particle scrollytelling). They are **optional reference patterns, NOT universal commandments**:

1. **Architectural Dark Palette (Optional):**
   - Deep warm foundations (e.g. Slate Graphite `#18181b`, Weathered Basalt `#1a1918`) and cohesive 3–5 tone material families (mineral, botanical, or industrial). Non-blown highlights preserve base chroma.

2. **Typographic Contrast (Context-Dependent):**
   - Contrasting display titles with functional body text and precision monospace metadata is effective for narrative and editorial products.
   - For utility tools, developer documentation, or telemetry consoles, single-family typographic hierarchies (e.g. pure sans-serif or technical mono) with disciplined weight and scale contrast are equally first-class.

3. **Spatial Rhythm & Negative Space (Context-Dependent):**
   - Generous negative space and asymmetric spatial zoning avoid repetitive card-grid fatigue on editorial landing pages.
   - For high-density operational consoles, compact grid matrices and modular ribbons are preferred over expansive whitespace.

4. **Tactile Micro-Interactions (Context-Dependent):**
   - Macro framing remains anchored and stable; motion is reserved for functional feedback (hover affordances, state changes, spatial relations). Inertial scrolling (e.g. Lenis) may be applied when justified by scrollytelling mechanics.

---

## Part C: The V4 Orchestration Pipeline & Separation of Duties

1. **Brief & Grounding (AURORA):** Extract product truth, user jobs, and constraints. Construct `PRODUCT_CONTEXT.md` and `CONTENT_MAP.md` with explicit copy budgets before touching layout.
2. **Candidate Hypotheses (AURORA):** Develop 3 distinct macro-hypotheses (3–5 for Depth 3) specifying spatial logic, information density, and signature devices—omitting component recipes and persuasive pitch text.
3. **Visual Spikes (FRAME):** Implement lightweight, standalone rendered prototypes (Desktop Hero, 2nd Fold, Mobile Hero, 1 Signature Interaction) with realistic copy lengths and randomized/anonymized IDs.
4. **Blind Visual Tournament (LENS):** LENS evaluates rendered spikes against product context and user goals blind to candidate pitch/rationale. Pairwise comparison; bounded `NO_WINNER` circuit breaker (max 2 regeneration rounds before ORION arbitrates).
5. **Contract Authoring (AURORA) & Review (LENS):** AURORA authors `DESIGN_DNA.md` and `DESIGN_CONTRACT.md`. LENS reviews rendered evidence and issues `ACCEPT`, `REJECT`, or `REQUEST_REWORK` (Creator != Certifier).
6. **Asset Gate (AURORA):** Verify `ASSET_MANIFEST.json` ensuring no undeclared placeholders.
7. **Vertical Slice (FRAME) & Gate (LENS):** Build production-grade Hero + 1 narrative section + mobile responsive. LENS audits and must issue PASS before full implementation begins.
8. **Implementation Execution (FRAME):** Implement full reachable surface with stable test selectors (`data-testid`) and zero placeholder components.
9. **Dual-Plane QA (PRISM & LENS):** PRISM independently audits the deterministic execution plane (state machine, forms, accessibility semantics, regex sweep); LENS audits the perceptual rendered plane. Dual PASS required for release gate.
10. **Remediation & Rollback Governance:**
    - FRAME creates Git commit checkpoints.
    - LENS evaluates perceptual regression; PRISM evaluates functional regression.
    - ORION arbitrates `PROMOTE` / `KEEP_CURRENT_BEST` / `ROLLBACK`. LENS does not directly manipulate git history.
11. **Retest & Closure (ORION):** Retest only against the identical final `BUILD_SHA`. Record results in `CLOSURE_REPORT.md` and `RELEASE_DECISION_RECORD.md`.
