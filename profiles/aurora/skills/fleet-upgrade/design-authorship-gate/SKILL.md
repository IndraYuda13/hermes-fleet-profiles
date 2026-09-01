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
2. Identify 3–5 product-specific visual/content cues. Avoid decorating with generic SaaS motifs that have no semantic relation to the product.
3. For open-ended work, produce 2–3 **materially different** directions. Different means composition/type/surface/interaction logic, not just palette swaps.
4. If using references, extract principles (rhythm, contrast, density, navigation, type behavior). Do not clone another brand's signature layout by default.
5. Define typography, spacing rhythm, color roles, surfaces, icon language, motion intent, and responsive behavior.
6. Define empty/loading/error/dense/long-content states that materially affect the surface.
7. Render and inspect the actual output at representative viewports.
8. Run the specificity test: **if the product name/logo were replaced, would this still look equally plausible for 20 unrelated AI/SaaS apps?** If yes, reject and redesign.
9. Check common unjustified AI-slop signals: centered mega-hero, decorative pill/badge soup, purple-blue glow, glassmorphism, repeated rounded cards, arbitrary bento grid, identical fade-ups, generic stock icon rows, default typography with no rationale.
10. Score 0–5: product specificity, hierarchy, typography, spatial rhythm, visual coherence, interaction intent, responsive completeness, accessibility. Any score <4 in specificity/hierarchy/coherence blocks handoff.

## Pitfalls
- Treating minimalism as permission for under-designed empty space.
- Adding novelty that harms usability.
- Banning a motif categorically; the issue is unjustified default use.
- Reviewing source instead of rendered output.

## Verification
Handoff includes visual thesis, chosen direction + rejected alternatives, scorecard, actual renders/evidence, and unresolved design risks.
