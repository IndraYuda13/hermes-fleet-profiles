---
name: anti-ai-slop-design
description: Detect and replace generic AI-looking UI patterns with product-specific visual decisions.
version: 2.0.0
metadata:
  hermes:
    tags: [design-critique, originality, ui]
    category: custom
---

# Anti AI-Slop Design

## Principle

Do not ban popular patterns. Detect patterns that appear because they are statistically obvious rather than product-appropriate.

## Slop indicators

Evaluate for:
- centered badge + giant gradient hero + dual CTA by default,
- excessive `rounded-xl/2xl` containers,
- every section being a card grid,
- arbitrary purple/blue/cyan gradients,
- icon-in-colored-rounded-square repetition,
- generic shadcn/template hierarchy without product adaptation,
- decorative glassmorphism with no material purpose,
- same fade/slide motion on every block,
- excessive empty space masking weak hierarchy,
- overly symmetrical layout with no editorial emphasis,
- default placeholder illustrations unrelated to product,
- typography with no personality or numeric/data strategy,
- dashboards that look like templates rather than tools.

## Response

For every detected generic choice:
1. explain why it is generic in this product context,
2. identify the actual user/product need,
3. propose a more intentional alternative,
4. preserve clarity and usability,
5. avoid novelty for novelty's sake.

Do this at two levels:
- **single choice:** a common motif can remain when it has a real product/brief role;
- **default cluster:** inspect shell, typography treatment, palette/material, repeated containers, and motion together. If three or more dominant choices are model/category defaults with no independent rationale, redesign the composition/content system rather than recoloring the same template.

Apply an **effect-off test**: mentally remove glow, blur, gradients, particles and decorative 3D. If hierarchy or identity collapses, effects are doing work that composition/type/content should carry.

Apply a **default-debt test**: list the framework/category choices that would happen automatically and mark each `KEEP_WITH_REASON`, `REPLACE`, or `NOT_APPLICABLE` before calling the direction authored.

## Originality test

Ask:
- Could the same screenshot plausibly belong to 50 unrelated SaaS products?
- Is there a recognizable product personality?
- Does hierarchy reflect the user's real job?
- Is information density appropriate?
- Are visual motifs consistent enough to feel authored?
- Does the direction remain legible and recognizable in grayscale/squint view?
- Is the palette organized by spatial/semantic roles rather than accent spraying?
- Is mobile re-authored around priority, or merely a vertical stack of desktop regions?

If the answer is weak, redesign before calling the interface polished.
