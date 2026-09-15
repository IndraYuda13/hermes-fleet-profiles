# Anti-Slop Enforcement Checklist

Use this after `visual-authoring-core`. This is a **rationale and cluster audit**, not a CSS-token blacklist.

## 1. Default-debt evidence

- [ ] `DEFAULT_DEBT.md` exists for Depth 2/3 work and records shell, hero pattern, repeated containers, typography, color/effects, navigation, and motion as `KEEP_WITH_REASON`, `REPLACE`, or `NOT_APPLICABLE`.
- [ ] Every `KEEP_WITH_REASON` names a product, workflow, content, audience, accessibility, or brand reason. "Modern", "premium", "clean", "futuristic", and "industry standard" are insufficient by themselves.
- [ ] Framework/library defaults (shadcn/Tailwind/component-kit presets) are treated as primitives and visibly adapted where the design contract requires it.

## 2. Generic-cluster gate

Inspect the **dominant** shell, typography treatment, palette/material treatment, repeated container pattern, and motion pattern.

- [ ] Fewer than three dominant choices are unexplained category/model defaults, **or** each familiar choice has independent product/brief evidence.
- [ ] Near-black + neon glow + glass + mono, cream + editorial serif + red/terracotta, centered gradient hero + pill CTAs + three cards, arbitrary bento, and generic dashboard shells are challenged as clusters rather than cosmetically recolored.
- [ ] A single justified motif is never rejected merely because it is common.
- [ ] Changing hue, font, radius, border opacity, or glow intensity on the same structure does not count as redesign.

`>=3` unexplained dominant defaults => `GENERIC RISK: HIGH` => block visual PASS for Depth 2/3.

## 3. Effect budget

For every glow, gradient, blur, glass layer, grain, bloom, particle system, shader, or decorative 3D treatment:

- [ ] purpose is named;
- [ ] usage is bounded to named regions;
- [ ] hierarchy remains legible with the effect removed;
- [ ] motion/performance/reduced-motion fallback exists where relevant.

If multiple effects only communicate a vague adjective such as "AI", "premium", or "futuristic", consolidate or remove them.

## 4. Authorship checks

- [ ] Product mechanism/proof visibly shapes at least one major composition decision.
- [ ] Major regions are carried by real/synthetic-declared content or authored assets, not decorative chrome standing in for missing proof.
- [ ] Typography is specified by roles, hierarchy, measure, wrapping, and content behavior; no mandatory pairing formula.
- [ ] Color is specified by spatial/semantic roles, not a list of swatches sprayed uniformly through the page.
- [ ] Mobile changes framing/order/crop/interaction where needed; "stack everything" is not accepted without evidence that priority survives.
- [ ] Stable status never pulses; motion states `trigger -> change -> meaning -> end state`.

## 5. Fleet role directives

1. **AURORA** authors `PRODUCT_CONTEXT.md`, `CONTENT_MAP.md`, `REFERENCE_LEDGER.md`, `DEFAULT_DEBT.md`, candidate hypotheses, then the winning `DESIGN_DNA.md` / `DESIGN_CONTRACT.md`.
2. **FRAME** implements the accepted topology, type roles, palette/material topology, effect budget, assets, and responsive thesis without normalizing them back to framework defaults.
3. **LENS** reviews rendered pixels using logo-off/copy-swap, squint/grayscale, effect-off, generic-cluster, and responsive-identity probes.
4. **PRISM/SENTINEL** continue deterministic functional/security checks; they do not substitute for perceptual authorship review.
