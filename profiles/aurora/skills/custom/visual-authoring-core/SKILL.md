---
name: visual-authoring-core
description: Canonical product design intelligence and anti-slop authority for AURORA. Governs product truth, content mapping, candidate hypotheses, rendered spike hand-off, and contract authoring.
metadata:
  hermes:
    editorial_name: "Visual Authoring Core"
    editorial_description: "Canonical product design intelligence and anti-slop authority for AURORA."
    requires_tools: ["web_search", "web_extract", "browser"]
---

# Visual Authoring Core (Hermes UI Design V4.1 Canonical Authority)

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
   - Owner feedback from the current product is evidence. Do not turn a previously liked palette, border treatment, type pairing, density, or composition into a standing fleet-wide motif.

4. **Universal Hard Gates vs Contextual Taste Dimensions:**
   - Deterministic hard gates (0 console errors, 0 overflow, readable contrast, touch ergonomics, grounded data) are non-negotiable.
   - Visual motifs (pure black, gradients, cards, borders, typography pairings, Lenis scrolling) are evaluated contextually based on product fit—never subjected to universal syntax bans.

5. **Pragmatic Asset Planning:**
   - Design around authentic project assets when supplied. If external assets are absent from the brief, use generated assets, procedural visuals, typography-led composition, or explicitly declared synthetic content. Never disguise undeclared placeholder stubs as final art.

6. **Aesthetic Priors Are Evidence, Never Defaults:**
   - Style catalogs, framework presets, prior fleet projects, benchmark sites, and model-familiar aesthetics are inputs to interrogate, not palettes or shells to adopt automatically.
   - A visual motif earns inclusion only when its role can be named: product mechanism, hierarchy, wayfinding, material metaphor, content proof, interaction feedback, or brand commitment.
   - A cluster of familiar motifs is a stronger warning than any single motif. Near-black + neon edge glow + glass cards + mono labels, cream + editorial serif + red accent, or centered gradient hero + pill CTAs are valid only when the product/brief independently earns the cluster.
   - If removing decorative effects (glow, blur, gradients, particles, texture) collapses the composition or identity, the direction is under-authored. Structure, type, content, and assets must carry the thesis first.

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
3. `REFERENCE_LEDGER.md`: Live benchmark inspection notes. Every reference gets a **single primary job** (`composition`, `typography`, `content/asset`, `interaction/motion`, `responsive`, or `material/color`), one transferable principle, one thing that must not be copied, and a product-fit note. A reference count without role separation is mood-board averaging and does not satisfy discovery.
4. `DEFAULT_DEBT.md`: Record category/framework defaults that are likely to appear automatically (shell, hero pattern, cards, typography, color/effects, navigation, motion). For each, mark `KEEP_WITH_REASON`, `REPLACE`, or `NOT_APPLICABLE`. This prevents defaults from becoming invisible decisions.

### Stage 2 — Macro-Candidate Hypotheses (`CANDIDATE_HYPOTHESES.md`)
Develop 3 distinct candidate hypotheses (3–5 for Depth 3). Each candidate specifies:
- **Visual Thesis:** One concise sentence summarizing the core experience logic.
- **Product Mechanism / Proof:** The real product behavior, content, artifact, data, or user action that gives the direction its visual form. A mood adjective alone is invalid.
- **Narrative / Experience Mechanism (Depth 3 Persuade or Experience):** State what changes as the user progresses, what product or message truth the change reveals, why interaction/motion is necessary, and what remains in reduced-motion mode. Decorative choreography without proof value is invalid.
- **Macro-Composition & Geometric Constraints:** Layout density tier, spatial zoning regions, grid track proportions (e.g. `grid-template-columns: 260px 1fr 300px`), and line measure budgets (e.g. `max-inline-size: 65ch`).
- **Archetype Qualities:** Expressed in ergonomic and spatial terms (e.g. "High-density telemetry matrix with segmented inspection zones" or "Asymmetrical editorial ledger with calm focal hierarchy"). Zero rigid component recipes.
- **Typography Strategy:** Role system (display/heading/body/label/data as applicable), hierarchy contrast, measure, wrapping behavior, fallback behavior, and font personality justified by product voice. Pairing is optional; no mandatory font triad or serif/sans formula.
- **Color & Material Topology:** Dominant field, contrast anchors, accent allocation, semantic colors, and any material/effect usage. Every glow, blur, gradient, glass layer, texture, or shader needs a named role and bounded region; decorative effects cannot substitute for hierarchy.
- **Signature Device:** 1–2 memorable, functional interaction/visual devices derived from product mechanisms.
- **Quiet Supporting Elements:** Secondary elements intentionally restrained to give the signature device breathing room.
- **Asset Strategy:** Sourced, procedural, generated, or typography-led asset plan.
- **Responsive Thesis:** What reorders, reframes, collapses, changes crop, or changes interaction on handheld sizes, and which identity cue must survive. "Stack vertically" is not a thesis.
- **Default-Debt Resolution:** Which entries from `DEFAULT_DEBT.md` this candidate keeps or replaces, with product-specific reasons.
- **Decoupled Specifications:** Technical specifications must omit persuasive pitch text to enable blind evaluation.

**Candidate Validity Rule:** Candidates must remain materially different when viewed in grayscale and with logos/brand names hidden. Palette swaps, font swaps on the same wireframe, or the same card topology with different effects count as one candidate. At least two of these must differ materially: reading path/focal distribution, container topology, content-to-media relationship, repetition model, navigation relationship, section rhythm, density model, or interaction model.

### Stage 3 — Visual Spikes Hand-off (FRAME)
FRAME builds lightweight, standalone HTML/CSS/JS or Tailwind prototypes for each candidate:
- **Mandatory Spike Evidence:**
  1. Desktop composition evidence (around 1440px)
  2. Second-fold / narrative evidence
  3. Static mobile composition evidence (around 390px)
- *Note:* Mobile candidate evidence may be a static layout capture without complex interactive DOM engines (complex responsive DOM behaviors are validated on the Vertical Slice).
- Realistic copy lengths from `CONTENT_MAP.md`; zero undeclared placeholder stubs.
- Anonymized as Spike Alpha, Beta, Gamma with randomized ordering.

### Stage 4 — Blind Visual Tournament & Exploration Semantics (LENS)
LENS evaluates rendered spikes against product context and user goals without candidate author pitches:
- Pairwise differential comparison across candidates and baseline (if available).
- Scored under `CALIBRATION_V0` taste rubric schema with observable submetrics.
- Apply three perceptual probes before scoring:
  1. **Logo-off / copy-swap probe:** Would the shell plausibly fit many unrelated AI/SaaS products unchanged? If yes, identity cannot score >= 8.
  2. **Squint / grayscale probe:** Does hierarchy and compositional rhythm survive reduced detail and color? If no, composition cannot score >= 8.
  3. **Effect-off probe:** Mentally remove glow/blur/gradient/particle decoration. If the direction loses its thesis because effects were doing structural work, identity/composition cannot score >= 8.
- A candidate may be visually restrained and still win. Novelty, darkness, gradients, WebGL, or motion do not receive bonus points by themselves.
- **Exploration Counter Semantics:**
  * `round`: Satu siklus perancangan 3 hipotesis oleh AURORA dan pembuatan spike oleh FRAME.
  * `regeneration`: Perancangan set 3 hipotesis kandidat baru setelah vonis `NO_WINNER` (maksimal 2 regeneration rounds).
  * `candidate rework`: Penyempurnaan craft terarah untuk 1 kandidat setelah vonis `REWORK_CANDIDATE: <ID>` (maksimal 1 rework per kandidat per round).
  * `tournament attempt`: Setiap kali LENS mengevaluasi set kandidat atau kandidat yang dirework (total evaluasi turnamen dibatasi maksimal 4 kali percobaan kumulatif).
- **Deterministic State Machine Termination:**
  State machine turnamen dijamin selalu berhenti pada salah satu dari tiga state akhir:
  1. `WINNER: <Candidate_ID>` -> Lanjut ke Stage 5 (Contract Authoring).
  2. `ORION_ARBITRATION` -> Terjadi saat budget habis.
  3. `ESCALATION` -> Eskalasi ke human owner melalui `ESCALATION_RECORD.md`.
- **Arbitration Quality Floor (`PERCEPTUAL_FLOOR_UNCALIBRATED`):**
  Saat budget eksplorasi habis tanpa pemenang:
  - ORION dilarang memilih kandidat hanya karena lolos fungsi dan aksesibilitas.
  - Karena ambang batas numerik selera belum memiliki bukti empiris terkalibrasi di armada ini, status lantai selera diklasifikasikan secara eksplisit sebagai `PERCEPTUAL_FLOOR_UNCALIBRATED`.
  - Dalam status `PERCEPTUAL_FLOOR_UNCALIBRATED`, ORION hanya diizinkan:
    1. Menurunkan Design Depth (misal Depth 3 -> Depth 1 dengan delta design spec), ATAU
    2. Menerbitkan `ESCALATION_RECORD.md` kepada owner.
  - ORION dilarang mengklaim bahwa kandidat memenuhi standar kualitas visual minimum yang belum pernah dikalibrasi.

### Stage 5 — Co-Signed Design Contract
AURORA authors the final specification based on the tournament winner:
- `DESIGN_DNA.md`: Spatial grid, density rules, composition rhythm, type roles/hierarchy, color & material topology, effect budget, surface layers, motion principles, signature element specs, anti-default decisions, and responsive identity invariants.
- `DESIGN_CONTRACT.md`: Implementation-ready route composition, state models (default, hover, focus, active, loading, error, empty), and stable test selectors (`data-testid`).
- LENS reviews rendered evidence and issues `ACCEPT`, `REJECT`, or `REQUEST_REWORK` (Creator != Certifier; LENS does not co-author).

### Stage 6 — Asset Gate (`ASSET_MANIFEST.json`)
Before full implementation begins:
- All visual assets declared with source (supplied, procedural, generated, typography-led, or approved synthetic).
- Zero undeclared fake placeholders or broken assets.
- Desktop and mobile crop/display plans verified.

---

## 3. Calibrated Taste Rubric & Submetrics Observability (Schema CALIBRATION_V0)

Unified 6-dimension schema matching `lens-review-contract.md` and `LENS_REVIEW_REPORT.json`:

| Dimension Key | Weight | Submetrics Tracked | Core Evaluative Focus |
|---|---:|---|---|
| `identity` | 25% | `product_specificity`, `visual_thesis_coherence` | Do form, content treatment, color/material choices, and signature devices arise from authentic product mechanisms/audience? Penalize category-default clusters and effect-led identity. |
| `composition` | 25% | `hierarchy`, `macro_diversity_originality` | Is the focal path obvious within 3 seconds and resilient in grayscale/squint view? Do topology, rhythm, and density express the content rather than a framework shell? |
| `typography` | 15% | `typography_measure` | Do role contrast, measure, wrapping, numeric/data treatment, and font character form a coherent system rather than a fashionable pairing recipe? |
| `assets` | 15% | `asset_integration` | Do visuals/content provide product proof at the scale the composition needs, with intentional crops and no chrome substituting for missing authored assets? |
| `interaction` | 10% | `interaction_meaning` | Does motion clarify state, causality, or product mechanism? Is visual energy concentrated into authored moments rather than ambient looping effects? |
| `responsive` | 10% | `responsive_recomposition` | Does mobile preserve the direction's hierarchy and identity through deliberate re-authorship, not merely stack or shrink desktop regions? |

### Submetric Observability Contract (Benchmark Depth 2/3)
- Nilai `null` diizinkan untuk kompatibilitas hanya jika status field adalah `not_applicable`.
- Untuk misi Depth 2 dan Depth 3, seluruh submetrik tidak boleh secara diam-diam dibiarkan `null`.
- Setiap submetrik yang berlaku wajib memiliki:
  * `score`: nilai numerik (0–10) sesuai rubrik CALIBRATION_V0,
  * `status`: `"applicable"` atau `"not_applicable"`,
  * `evidence`: ringkasan bukti konkret yang dapat diinspeksi.

### Generic-Default Cluster Gate (Depth 2/3)
Before a visual PASS, LENS must list the dominant shell, typography treatment, palette/material treatment, repeated container pattern, and motion pattern. If **three or more** are recognizable category/model defaults and lack independent product/brief rationale, classify `GENERIC RISK: HIGH` and block the candidate regardless of weighted total. This is a cluster/rationale gate, not a syntax ban: one justified motif never fails by itself.

---

## 4. Checkpoint & Regression Evaluation Principles

1. **Deterministic vs. Perceptual Signals:**
   - Deterministic signals (bounding-box drift, overflow, clipping, runtime errors) are hard regression triggers.
   - Perceptual regression is valid **with or without geometry drift** (typography degradation, font fallback, image/crop degradation, visual hierarchy loss, contrast degradation, color relationship degradation, asset quality regression, motion degradation, product-specificity loss).
2. **Model Noise Discipline:**
   - Any assumption of vision model noise (±3–5 points) is classified as `CALIBRATION_HYPOTHESIS / UNMEASURED`.
   - `NEGLIGIBLE_DELTA` cannot be granted solely because a score delta is < 4 and bounding boxes are stable; pairwise perceptual comparison against `BEST_BUILD_SHA` governs.
