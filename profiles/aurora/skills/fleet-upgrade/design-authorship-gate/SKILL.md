---
name: design-authorship-gate
description: Reject generic UI before design handoff.
version: 1.0.0
author: Fleet Upgrade Research
license: MIT
metadata:
  hermes:
    tags: [design, ui, ux, art-direction, anti-slop]
    category: fleet-upgrade
---
# Design Authorship Gate

## When to Use
Use for any open-ended UI redesign, new product surface, landing page, dashboard, or visual-system change before handing work to FRAME.

## Procedure
1. State product, audience, primary job, constraints, and a one-sentence **visual thesis**.
2. State the **product mechanism/proof** that gives the visual thesis form. Identify 3–5 product-specific visual/content cues. Avoid decorating with generic SaaS motifs that have no semantic relation to the product.
3. Create a small **default-debt register** for shell, hero, repeated containers, typography, color/effects, navigation and motion: `KEEP_WITH_REASON | REPLACE | N/A`.
4. For open-ended work, produce 2–3 **materially different** directions. Different means at least two structural axes (reading/focal path, topology, media/content relationship, repetition, density, navigation, interaction), not palette/font/effect swaps.
5. If using references, give each one a primary job (composition/type/asset/motion/responsive/material), extract one principle and one anti-copy note. Do not average references into a moodboard style.
6. Define typography roles, spacing rhythm, color/material ownership, effect budget, surfaces, icon language, motion intent, and responsive identity invariant.
7. Define empty/loading/error/dense/long-content states that materially affect the surface.
8. Render and inspect the actual output at representative viewports.
9. Run the specificity test: **if the product name/logo were replaced, would this still look equally plausible for 20 unrelated AI/SaaS apps?** If yes, reject and redesign.
10. Run squint/grayscale and effect-off probes. Hierarchy must survive reduced detail/color; identity must not depend on glow/blur/gradient/particles doing structural work.
11. Check common unjustified AI-slop clusters: centered mega-hero + pill/badge soup + feature cards; near-black + purple/cyan glow + glass + mono; cream + editorial serif + red accent; arbitrary bento; generic dashboard shells. A single justified motif is not a failure. `>=3` unexplained dominant defaults blocks handoff.
12. Score 0–5: product specificity, hierarchy, typography, spatial rhythm, color/material coherence, visual coherence, interaction intent, responsive completeness, accessibility. Any score <4 in specificity/hierarchy/coherence blocks handoff.

## Pitfalls
- Treating minimalism as permission for under-designed empty space.
- Adding novelty that harms usability.
- Banning a motif categorically; the issue is unjustified default use.
- Reviewing source instead of rendered output.

## Verification
Handoff includes visual thesis, chosen direction + rejected alternatives, scorecard, actual renders/evidence, and unresolved design risks.
