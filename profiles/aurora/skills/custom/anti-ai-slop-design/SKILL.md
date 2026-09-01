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

## Originality test

Ask:
- Could the same screenshot plausibly belong to 50 unrelated SaaS products?
- Is there a recognizable product personality?
- Does hierarchy reflect the user's real job?
- Is information density appropriate?
- Are visual motifs consistent enough to feel authored?

If the answer is weak, redesign before calling the interface polished.
