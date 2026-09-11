# Universal Anti-AI Slop Principles & World-Class Web Design Standard

This reference synthesizes the proven design decisions from the Awwwards-grade WebGL 3D Particle Scrollytelling project, high-end design research (e.g. OFF+BRAND study), and the 12-stage internal exploration workflow into domain-neutral, non-negotiable rules for building web interfaces that eliminate generic AI slop.

---

## 1. Color Palette: Elimination of "SaaS Cyan/Purple Fatigue"

### The Prohibited Cliché
Defaulting to pitch-black `#000000` combined with electric purple (`#8b5cf6`), neon cyan (`#06b6d4`), and multi-color gradient blur spheres. This creates instant visual fatigue and marks an interface as an uncurated AI template.

### The Standard
1. **Never Pure `#000000`**: Use warm, organic, architectural dark foundations (e.g. Deep Roasted Espresso `#131211`, Slate Graphite `#18181b`, Weathered Basalt `#1a1918`). Warmth adds mass, prestige, and tactile presence.
2. **Cohesive 3–5 Tone Botanical/Mineral Family**: Formulate colors as siblings that belong to the same physical material family (e.g., Warm Sand `#a88f6c`, Deep Moss `#3d633a`, Soft Sage `#6b9666`, Warm Amber `#db8f38`, Soft Champagne `#ebdcb8`). Zero orphan neon accents.
3. **Non-Blown Highlights**: Additive blending or glowing accents must preserve their base chroma. Never blow highlights out into pure flat white (`#ffffff`). Amber must remain deep incandescent amber; moss must remain organic verdant moss.

---

## 2. Typography as Primary Architecture

### The Prohibited Cliché
Using a single default sans-serif (Inter, Roboto, Arial) across all elements without optical scale contrast, or applying gradient text fills indiscriminately to headlines.

### The Standard
1. **The Typographic Triad (Contrast Across 3 Typographic Personalities)**:
   - **Editorial High-Contrast Serif** (`Playfair Display`, `Cormorant Garamond`): Conveys literature, philosophy, craft, and human intention for display titles and philosophical anchors.
   - **Modern Geometric/Functional Sans** (`Outfit`, `Inter`, `Public Sans`): Provides clean, high-legibility narrative flow with breathable line-height (1.6–1.75).
   - **Technical Monospace** (`JetBrains Mono`, `Fira Code`): Used for micro-telemetry, chapter indexes, coordinates, and precision tags. Adds engineering rigor.
2. **Extreme Scale & Optical Tracking**:
   - Giant display headings (`clamp(3.5rem, 6vw, 6.5rem)`) with tight negative tracking (`-0.025em` to `-0.03em`) and tight line-height (1.05–1.15).
   - Micro-metadata labels (`0.75rem` to `0.85rem`) with generous positive tracking (`+0.18em` to `+0.25em uppercase`).
3. **Copy is Sacred (Teks Mengusir Visual)**: Visuals must yield to readability. Use GPU-level repulsion halos (displacing particles/backgrounds away from text bounds) paired with HTML dual radial alpha scrims (without heavy compositor-crushing blurs on mobile) to guarantee WCAG AAA (7.5:1+) contrast under any motion state.

---

## 3. Demolition of the "Card Grid Addiction"

### The Prohibited Cliché
Splitting all page information into repetitive 3-box or 4-box card grids with identical borders, generic icons, and center-aligned bodies.

### The Standard
1. **Asymmetric Spatial Zoning**: Alternate viewport focus across sections (e.g., Section 0: Text Left / Visual Right; Section 1: Visual Far-Left / Text Right; Section 2: Full-screen Volumetric Center; Section 3: Asymmetrical Industrial Split).
2. **Card-Free Negative Space**: Information should float directly upon the atmospheric canvas with generous negative space (`clamp(7rem, 11vw, 13rem)` clearance). A border is only justified when grouping genuinely distinct interactive controls or technical data.
3. **Pacing and Scroll Distance**: Content chapters need generous vertical distance (e.g. 180vh to 220vh per chapter) so visual transformations feel cinematic, intentional, and calm rather than frantic.

---

## 4. Tactile Micro-Physics vs Cheap Macro Gimmicks

### The Prohibited Cliché
Exaggerated 3D whole-card tilt on hover, bouncy rubber-band easing, aggressive mouse-follow wobbling, and floating decorative spheres that serve no semantic purpose.

### The Standard
1. **Macro Stability, Micro Tactility**: Macro compositions stay anchored, authoritative, and stable. Motion is reserved for subtle micro-interactions (e.g. localized surface displacement / goosebumps along surface normals $R < 0.65$ when cursor passes, without disturbing macro framing).
2. **Kinetic Inertia Scrolling**: Smooth virtual scrolling (e.g., Lenis) synchronized directly into the animation RAF loop with zero frame-rate stutter (`lagSmoothing(0)`). Scroll feels weighted, damped, and continuous.

---

## 5. Shape Fidelity & Authentic Silhouettes (Anti-Blob Gate)

### The Prohibited Cliché
Generating generic noisy spheres, indistinct blobs, or vague organic masses and labeling them as "AI Core", "Neural Intelligence", or "Cloud Data".

### The Standard
1. **Black-and-White Silhouette Test**: Any 3D model, vector graphic, or brand mark must be instantly recognizable from its silhouette alone, even with shading removed.
2. **Anatomical & Mechanical Realism**:
   - An anatomical brain must feature a deep bilateral longitudinal fissure ($|x| \ge 0.12$), recognizable temporal/occipital lobes, cerebellar folia ridges, and a tapered brainstem with pons bulge.
   - An industrial lightbulb must have a teardrop envelope, narrowing neck waist, genuine helical screw threading (E27 ridges), bottom contact terminal, and dual-arch tungsten filament.
   - A globe must render accurate continental landmasses (Americas, Africa, Eurasia) with geographic density rather than random noise on a sphere.

---

## 6. Space-Conscious Mobile Re-Composition

### The Prohibited Cliché
Treating mobile responsive design as merely CSS `width: 100%` on desktop elements, which causes text cards to completely blanket background 3D or visual art.

### The Standard
1. **Two-Tier Vertical Stage**: On mobile (<768px), split the viewport into distinct visual zones:
   - Upper 45–50%: Elevated 3D/Visual hero window (camera pulled back $+1.8$ to $+2.8$ units, object translated upward $+0.8$ to $+1.35$).
   - Lower 50%: Typography card docked at the bottom (`margin-top: auto; justify-content: flex-end`) with light translucent scrim.
2. **Navigation Metamorphosis**: Desktop vertical rails that consume 80–120px margin must disappear on mobile and transform into a floating minimal pill capsule anchored at the bottom thumb zone (`bottom: 1.25rem`). Zero horizontal overflow across 320px–2560px.

---

## 7. Quality Governance: Creator != Certifier (Adversarial QA)

### The Prohibited Cliché
An agent or developer writing code and immediately self-certifying: *"The UI looks great and passes all requirements."*

### The Standard
1. **Separation of Duties**:
   - **AURORA**: Dictates Design DNA, 12-dimension style fingerprint, color tokens, and typography hierarchy.
   - **FRAME**: Faithfully executes code and mathematical asset distribution.
   - **LENS & PRISM**: Independently audit headless rendered viewports (Playwright CDP + VLM).
2. **Zero-Bypass Failure Remediation**: If LENS identifies that an asset looks like a blob or typography overlaps an element, work CANNOT proceed to completion. An explicit remediation task must be routed back to FRAME to reformulate the mathematics or CSS before independent retest.

---

## 8. The 8 Mandatory Hard Checks (Lens Review Contract)

Before any UI build can receive a `pass` verdict, all 8 hard checks must pass (return `true`). A failure on any check triggers an immediate `verdict = "revise"`:

1. **`no_emoji_ui_icons`**: Unicode emoji are strictly forbidden as UI navigation, action, button, card header, or decorative icons. A single, coherent SVG family (e.g. Lucide/custom) or text labels must be used.
2. **`stable_status_not_animated`**: Stable states (`Active`, `Online`, `Available`, `Connected`, `Operational`) must NEVER pulse, ping, blink, breathe, or animate continuously. Use a calm text label with an optional static dot. Motion is reserved only for active, ongoing background tasks with clear end conditions.
3. **`primary_flow_works`**: Primary CTAs must not be dead links (`href="#"`, `href=""`, `javascript:void(0)` without handlers). All primary flows must be clickable and navigable.
4. **`important_content_not_clipped`**: Critical titles, metrics, hero copy, and navigation items must never be clipped by `overflow: hidden` without intentional ellipsis or line-clamp.
5. **`keyboard_and_touch_usable`**: Mobile touch targets must meet ergonomic standards ($\ge 44 \times 44\text{px}$). No essential navigation or data may be locked behind desktop-only hover states.
6. **`reduced_motion_reviewed`**: All motion must respect `@media (prefers-reduced-motion: reduce)` and gracefully stop or dampen for users sensitive to vestibular motion.
7. **`fonts_and_assets_loaded`**: Zero broken images (`naturalWidth > 0`), zero 4xx/5xx network asset failures, and clean web font readiness before capture.
8. **`claims_and_data_are_grounded`**: Strictly zero generic marketing hallucinations: no fake testimonials ("John Doe, CEO at Acme"), fake metrics ("10,000+ Happy Customers"), or fake media badges ("As featured on Forbes/TechCrunch") unless grounded in authentic domain facts or explicitly marked as illustrative.

---

## 9. The 6-Dimension Calibrated Scoring Rubric

Lens audits builds across 6 weighted dimensions (Total 100 points):

| Dimension | Weight | Target Assessment |
|---|---|---|
| **Identity & Brief Match** | 25% | Specificity to product/domain; custom character; zero template genericness. |
| **Composition & Hierarchy** | 25% | Clear primary/secondary focal path; rhythm; breathing room; anti-card-grid. |
| **Typography** | 15% | Typographic triad; measure; optical tracking; contrast ratio $\ge 7:1$. |
| **Assets & Visual Direction** | 15% | Proof-driven visuals; authentic photography/renders; intentional cropping. |
| **Interaction & Motion** | 10% | Tactile micro-interactions; calm anchored macro; reduced-motion compliance. |
| **Responsive** | 10% | Intentional mobile two-tier stage; touch targets $\ge 44\text{px}$; zero overflow. |

**Scoring Anchors**:
- `0–3`: Gagal total atau hierarki membingungkan.
- `4–5`: Berfungsi tetapi template default AI slop (centered hero + dual pill + 3-box bento).
- `6–7`: Ada arah desain jelas namun ada kelemahan struktural material.
- `8–9`: Koheren, spesifik, bernilai editorial tinggi dengan sedikit kelemahan minor.
- `10`: Museum-grade / Awwwards level dengan bukti visual sangat kuat.

**Pass Threshold**:
- Weighted Total $\ge 85/100$
- Minimum $\ge 8/10$ across EVERY individual dimension
- All 8 Hard Checks = `true`
- Zero blocking defects

---

## 10. The 12-Stage Anti-Slop Orchestration Pipeline

1. **Brief & Grounding**: Extract authentic product constraints and core conversion actions. Do not hallucinate business data.
2. **Visual Reference Discovery**: Inspect live references in headless browser; extract concrete spatial, typographic, and motion lessons.
3. **3 Structural Candidates**: Explore 3 radically distinct layout/hierarchy candidates (not just color palette swaps).
4. **Concept Selection (Lens + Orion)**: Lens critiques candidates; Orion locks one global direction and designates one token owner.
5. **Design Contract**: Generate compact `DESIGN_CONTRACT.md` specifying typography triad, semantic colors, grid, and assets.
6. **Real Asset Production & Cropping**: Secure and crop authentic imagery before implementation. No placeholder grey boxes.
7. **Vertical Slice (Hero + 1 Section)**: Build complete hero and first follow-up section on desktop and mobile. Audit with Lens before fanning out.
8. **Implementation Execution**: FRAME implements remaining surfaces with stable selectors and zero placeholder components.
9. **Binding Lens Review**: Lens executes `LensEngineV2` across all 7 gates and issues `LENS_REVIEW_REPORT.json`.
10. **Priority Remediation Loop**: Maximum 5 priority design defects + all hard check failures per cycle. Budget: 2–4 cycles.
11. **Retest & SHA Validation**: Lens retests the new build SHA. If no progress after 2 cycles, re-evaluate direction.
12. **Verified Handoff**: Release verified build, inspection artifacts, and residual risk notes.
