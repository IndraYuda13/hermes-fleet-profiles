---
name: visual-authoring-core
description: Canonical product design intelligence and anti-slop authority for AURORA. Governs product truth, content mapping, candidate hypotheses, rendered spike hand-off, and contract authoring.
metadata:
  hermes:
    editorial_name: "Visual Authoring Core"
    editorial_description: "Canonical product design intelligence and anti-slop authority for AURORA."
    requires_tools: ["web_search", "web_extract", "browser"]
---

# Visual Authoring Core (Hermes UI Design V4 Canonical Authority)

`visual-authoring-core` is the single canonical design authority for AURORA. It governs the upstream product design intelligence protocol for UI Design Depth 2 and Depth 3 missions, ensuring design decisions originate from product truth and are tested in real pixels rather than self-certified in text.

---

## 1. Principles of Taste Without Aesthetic Dogma

1. **Product Truth Over Aesthetic Trends:**
   - Every visual decision must stem from what the product does, who uses it, and the operational environment—never from a catalog of current design tropes.
   - Spend boldness on one or two functional signature devices; keep secondary surfaces calm and disciplined.

2. **Pixel-First Verification (Creator != Certifier):**
   - Direction selection must occur on rendered pixels, not text descriptions.
   - AURORA authors candidate hypotheses and the final design contract. LENS independently evaluates rendered spikes in a blind tournament. AURORA never self-selects.

3. **Archetypes are Qualities, NOT Component Recipes:**
   - Archetypes define information density, spatial behavior, emotional character, interaction philosophy, and relationship to product truth.
   - Prescriptive component recipes are strictly prohibited. Visual components must arise from user journeys and product needs.
   - *Owner Preference Alignment:* Standing fleet preferences for modern precision, breathable negative space, specular 1px borders, and calm editorial craft are fully supported for applicable domains; what is prohibited is treating specific styling templates as mandatory dogma across unrelated projects.

4. **Universal Hard Gates vs Contextual Taste Dimensions:**
   - Deterministic hard gates (0 console errors, 0 overflow, readable contrast, touch ergonomics, grounded data) are non-negotiable.
   - Visual motifs (pure black, gradients, cards, borders, typography pairings, Lenis scrolling) are evaluated contextually based on product fit—never subjected to universal syntax bans.

5. **Pragmatic Asset Planning:**
   - Design around authentic project assets when supplied. If external assets are absent from the brief, use generated assets, procedural visuals, typography-led composition, or explicitly declared synthetic content. Never disguise undeclared placeholder stubs as final art.

---

## 2. Upstream Design Protocol (Stage 0 to Stage 6)

### Stage 0 — Classification & Surface Mode
ORION classifies the mission:
- **Design Depth:** 0 (Existing System), 1 (Delta Spec), 2 (Full Discovery: 3 candidates), 3 (Flagship / Premium: 3–5 candidates).
- **Surface Mode:**
  - *Persuade:* Marketing, launch page, conversion-driven. High visual storytelling, brand-forward typography.
  - *Operate:* Dashboards, consoles, telemetry. Dense, functional, low fatigue, high scanability.
  - *Read:* Documentation, editorial, knowledge base. Optimal line lengths, high typographic comfort.
  - *Experience:* WebGL, 3D, creative interactive canvas. Rich tactile feedback, spatial immersion.

### Stage 1 — Product Truth & Content Architecture
Before authoring visual hypotheses, produce:
1. `PRODUCT_CONTEXT.md`: Product type, target users, critical workflows, usage environment, density tier, trust targets, and domain constraints.
2. `CONTENT_MAP.md`: Explicit copy budgets per fold (headline word limits, subhead line budgets), authentic domain metrics, emotional beats, and section-by-section narrative hierarchy.
3. `REFERENCE_LEDGER.md`: Live benchmark inspection notes focused on spatial systems and layout principles (no style cloning).

### Stage 2 — Macro-Candidate Hypotheses (`CANDIDATE_HYPOTHESES.md`)
Develop 3 distinct candidate hypotheses (3–5 for Depth 3). Each candidate specifies:
- **Visual Thesis:** One concise sentence summarizing the core experience logic.
- **Macro-Composition & Geometric Constraints:** Layout density tier, spatial zoning regions, grid track proportions (e.g. `grid-template-columns: 260px 1fr 300px`), and line measure budgets (e.g. `max-inline-size: 65ch`).
- **Archetype Qualities:** Expressed in ergonomic and spatial terms (e.g. "High-density telemetry matrix with segmented inspection zones" or "Asymmetrical editorial ledger with calm focal hierarchy"). Zero rigid component recipes.
- **Typography Strategy:** Type scale, measure, and font personality justified by product voice (no mandatory font triad).
- **Signature Device:** 1–2 memorable, functional interaction/visual devices derived from product mechanisms.
- **Quiet Supporting Elements:** Secondary elements intentionally restrained to give the signature device breathing room.
- **Asset Strategy:** Sourced, procedural, generated, or typography-led asset plan.
- **Decoupled Specifications:** Technical specifications must omit persuasive pitch text to enable blind evaluation.

### Stage 3 — Visual Spikes Hand-off (FRAME)
FRAME builds lightweight, standalone HTML/CSS/JS or Tailwind prototypes for each candidate:
- Focus on Desktop Hero (1440px) + 2nd Fold + static interaction state previews (`:hover`/`:focus`/toggled class).
- Realistic copy lengths from `CONTENT_MAP.md`; zero undeclared placeholder stubs.
- Anonymized as Spike Alpha, Beta, Gamma with randomized ordering.
- Full mobile DOM restructuring and advanced interactive state engines are deferred to Stage 7 (Vertical Slice) on the single winning candidate.

### Stage 4 — Blind Visual Tournament (LENS)
LENS evaluates rendered spikes against product context and user goals without candidate author pitches:
- Pairwise differential comparison across candidates and baseline (if available).
- Scored under `CALIBRATION_V0` taste rubric schema.
- **Tournament Verdicts:**
  - `WINNER: <ID>`: Clear winner that satisfies taste threshold and macro-diversity.
  - `REWORK_CANDIDATE: <ID>`: A candidate has winning spatial architecture but remediable craft defects; advance with targeted craft punch-list.
  - `NO_WINNER`: All candidates medioker or generic AI slop.
- **Bounded Exploration Loop:** Max 2 regeneration rounds on `NO_WINNER` before ORION arbitrates (select best available, downgrade Design Depth, or escalate).

### Stage 5 — Co-Signed Design Contract
AURORA authors the final specification based on the tournament winner:
- `DESIGN_DNA.md`: Spatial grid, density rules, type hierarchy, surface layers, motion principles, signature element specs.
- `DESIGN_CONTRACT.md`: Implementation-ready route composition, state models (default, hover, focus, active, loading, error, empty), and stable test selectors (`data-testid`).
- LENS reviews rendered evidence and issues `ACCEPT`, `REJECT`, or `REQUEST_REWORK`.

### Stage 6 — Asset Gate (`ASSET_MANIFEST.json`)
Before full implementation begins:
- All visual assets declared with source (supplied, procedural, generated, typography-led, or approved synthetic).
- Zero undeclared fake placeholders or broken assets.
- Desktop and mobile crop/display plans verified.

---

## 3. Calibrated Taste Rubric (Schema CALIBRATION_V0)

Unified 6-dimension schema matching `lens-review-contract.md` and `LENS_REVIEW_REPORT.json`:

| Dimension Key | Weight | Core Evaluative Focus |
|---|---:|---|
| `identity` | 25% | **Product Specificity & Visual Thesis:** Do spatial and visual choices reflect authentic product truth, mechanisms, and audience, rather than generic SaaS tropes? |
| `composition` | 25% | **Hierarchy, Density & Macro-Diversity:** Is the primary focal point obvious within 3 seconds? Does density support task clarity? Avoids repeating recent fleet shells (anti-collision). |
| `typography` | 15% | **Scale, Measure & Typographic Voice:** Are scale ratios, line measures, and hierarchy controlled without default unstyled fonts? |
| `assets` | 15% | **Content & Asset Authenticity:** Are visuals and copy mutually reinforcing, with authentic data and realistic measure? |
| `interaction` | 10% | **Micro-Tactility & Motion Meaning:** Does motion clarify state changes or spatial relationships rather than acting as decorative slop? |
| `responsive` | 10% | **Mobile Recomposition & Ergonomics:** Is mobile layout thoughtfully restructured for handheld tasks and touch targets, not merely stacked? |

*Note: Rubric weights are calibrated under schema version CALIBRATION_V0 and may be tuned via empirical Taste Pack benchmarks.*
