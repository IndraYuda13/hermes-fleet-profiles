# Hermes UI V4 Multi-Agent Orchestration & Verification Governance

This reference defines the authoritative orchestration and verification standard for executing UI Design Depth 2 and Depth 3 missions across the autonomous fleet (ORION, AURORA, FRAME, LENS, PRISM).

---

## 1. The 14-Stage Lifecycle & Role DAG

```text
[Stage 0: ORION Entry]
       │
[Stage 1: AURORA Discovery] ─────────> PRODUCT_CONTEXT.md, CONTENT_MAP.md, REFERENCE_LEDGER.md
       │
[Stage 2: AURORA Hypotheses] ────────> CANDIDATE_HYPOTHESES.md (Geometric/Spatial constraints)
       │
[Stage 3: FRAME Visual Spikes] ──────> spikes/ (Desktop 1440, Fold 2, Static Mobile 390), SPIKE_MANIFEST.json
       │
[Stage 4: LENS Blind Tournament] ────> VISUAL_TOURNAMENT.json (WINNER, REWORK_CANDIDATE, NO_WINNER)
       │ (Bounded: max 2 regen rounds, max 1 rework/round, max 4 total attempts -> ORION arbitration)
[Stage 5: AURORA Contract Authoring] ─> DESIGN_DNA.md, DESIGN_CONTRACT.md, INTERACTION_CONTRACT.json
       │ (LENS reviews: ACCEPT / REJECT / REQUEST_REWORK; Creator != Certifier)
[Stage 6: AURORA Asset Gate] ────────> ASSET_MANIFEST.json (Supplied, generated, procedural, typography)
       │
[Stage 7: FRAME Vertical Slice] ─────> Hero + 1 narrative section + mobile responsive
       │
[Stage 8: LENS Slice Gate] ──────────> VERTICAL_SLICE_REPORT.md (PASS -> advance to full build)
       │
[Stage 9: FRAME Implementation] ─────> frontend-source, BUILD_MANIFEST.json (Git checkpoint)
       │
[Stage 10 & 11: Parallel Dual QA] ───┬─> PRISM (Deterministic Plane: state, forms, a11y, mock regex)
                                     └─> LENS (Perceptual Plane: CALIBRATION_V0 taste rubric + submetrics)
       │ (Isolated browser contexts; Dual PASS required; Independent Veto)
[Stage 12: Remediation Loop] ────────> DEFECT_LEDGER.json (DESIGN_DEFECT -> aurora, CODE_DEFECT -> frame)
       │ (Bounded: max 2 cycles; ORION arbitrates PROMOTE / KEEP_CURRENT_BEST / ROLLBACK)
[Stage 13: Retest] ──────────────────> RETEST_REPORT.md (Tested on new exact BUILD_SHA)
       │
[Stage 14: ORION Closure] ───────────> CLOSURE_REPORT.md, RELEASE_DECISION_RECORD.md
```

---

## 2. Invariant Rules for Autonomous Orchestration

1. **Creator != Certifier (Non-Negotiable):**
   - AURORA authors candidate hypotheses and the final design contract, but LENS evaluates rendered visual spikes and certifies vertical slice gates. AURORA never self-selects.
   - FRAME implements code, but LENS and PRISM certify. FRAME never self-certifies.
   - LENS is an auditor and has `production_write: false`. LENS never edits application source or executes git commands.

2. **Candidate Hypotheses vs. Component Recipes:**
   - Archetypes define information density, spatial behavior, emotional tone, and interaction philosophy.
   - Prescriptive component recipes (e.g. "Apple-grade = translucent top bar + pill nav + specular border") are prohibited as universal dogma.
   - *Owner Preference Alignment:* Standing fleet preferences for modern precision, breathable negative space, specular 1px borders, and calm editorial craft are fully supported for applicable domains; what is prohibited is treating specific styling templates as mandatory dogma across unrelated projects.
   - Hypotheses must specify **Spatial Geometry & Layout Tracks** (grid column ratios, container boundaries, line measure budgets, density tiers) so FRAME does not have to invent layout from scratch.

3. **Visual Spike Scope & Mobile Evidence:**
   - Candidate visual spikes in Stage 3 require:
     1. Desktop composition evidence (around 1440px)
     2. Second-fold / narrative evidence
     3. Static mobile composition evidence (around 390px)
   - Mobile candidate evidence may be a static layout capture without complex interactive DOM engines. Full interactive state machines and responsive recomposition are validated at Stage 7 (Vertical Slice Gate) on the winning candidate.

4. **Bounded Exploration Budget:**
   - Stage 4 Blind Tournament supports `WINNER: <ID>`, `REWORK_CANDIDATE: <ID>`, and `NO_WINNER`.
   - `REWORK_CANDIDATE` is capped at max 1 rework attempt per candidate with targeted craft punch-list.
   - `NO_WINNER` regeneration is capped at max 2 rounds.
   - Total tournament evaluation attempts are capped at 4 attempts maximum.
   - If budget is exhausted without a winner, ORION explicitly arbitrates:
     a. Select best available candidate with documented trade-offs (only if it meets minimum functional and accessibility floors),
     b. Downgrade Design Depth (e.g. Depth 3 -> Depth 1 with explicit delta spec), OR
     c. Record an explicit escalation (`ESCALATION_RECORD.md`).
     Silent selection of sub-floor candidates is strictly prohibited.

5. **Dual Independent Release Veto & Asynchronous Verifier Arrival:**
   - `RELEASE_GATE = PRISM_PASS && LENS_PASS` bound to identical `BUILD_SHA`.
   - A single verifier PASS cannot authorize release. If either verifier reports FAIL, closure is blocked.
   - PRISM and LENS execute in isolated browser contexts to prevent mutable state contamination.
   - When verifiers complete asynchronously, early arrival of one verifier PASS authorizes local baseline promotion (`BEST_BUILD_SHA`), but final release synthesis and owner handoff remain gated until the sibling verifier reaches terminal PASS.
   - Release State Machine: Internal pass transitions `INTERNAL_RELEASE_GATE = PASS`, while `OWNER_VISUAL_ACCEPTANCE = PENDING` and `MISSION_RELEASE_STATE = AWAITING_OWNER`. Only the human owner can transition `OWNER_ACCEPTANCE` to `PASS`.

6. **Regression Logic & BEST_BUILD_SHA Ownership:**
   - FRAME creates Git commit checkpoints.
   - LENS evaluates perceptual regression against `BEST_BUILD_SHA`.
   - **Perceptual regression is valid with or without geometry drift** (typography degradation, font fallback, image/crop degradation, visual hierarchy loss, contrast degradation, color relationship degradation, asset quality regression, motion degradation, product-specificity loss).
   - Deterministic signals (bounding-box drift, overflow, clipping, runtime console errors) are hard regression triggers.
   - `NEGLIGIBLE_DELTA` requires zero deterministic regression AND zero material perceptual degradation on pairwise comparison.
   - Model-noise assumptions (±3–5 points) are classified as `CALIBRATION_HYPOTHESIS / UNMEASURED`; no arbitrary 4.0 deadband permitted.
   - **ORION determines:** `PROMOTE` (new revision resolves defects without regression), `KEEP_CURRENT_BEST` (new revision exhibits regressions), or `ROLLBACK`. FRAME executes git operations.

7. **Defect Partitioning in Remediation:**
   - `DEFECT_LEDGER.json` strictly partitions defects:
     * `DESIGN_DEFECT` (Aesthetic, typography ratios, color tension, archetype mismatch) -> Routed to **AURORA** to patch `DESIGN_CONTRACT.md`.
     * `CODE_DEFECT` (Console error, layout overflow, broken interaction, WCAG contrast, DOM accessibility) -> Routed to **FRAME** to fix in `remediated-source`.
   - Remediation cycles are capped at max 2 cycles.

8. **Feature-Conditional Hard Checks & User Journey Scope:**
   - Focus trap is tested only if modal/dialog surfaces are present.
   - Form validation is tested only if input forms are present.
   - Ketiadaan komponen yang disyaratkan oleh journey pada brief diklasifikasikan sebagai pelanggaran kontrak.

9. **Contextual Motifs vs. Syntax Bans:**
   - Pure black (`#000000`), gradients, borders, cards, sans-serif typography (such as Inter), pill navigation, and Lenis are NOT universally forbidden.
   - The defect is unmotivated usage irrelevant to product truth—not the CSS syntax itself.
