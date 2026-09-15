---
name: frontend-design
description: Role-safe product design and frontend intelligence using the active profile's local UI/UX Pro Max engine; enforces deliberate visual systems without generic AI-template fallback.
license: MIT
---

# Frontend Design Intelligence — AURORA / FRAME

Use this skill only for product/UI work. Respect role boundaries: **AURORA defines design intent/system; FRAME implements it.** LENS independently verifies the rendered result.

## Profile-local design search
Never hard-code another profile's directory. Named Hermes profiles use their own active `HERMES_HOME`, so call the UI/UX search engine from the active profile:

```bash
python3 "${HERMES_HOME}/skills/creative/ui-ux-pro-max/scripts/search.py" "<query>" --domain <style|color|chart|landing|product|ux|typography|icons|gsap|react|web>
```

If the script is missing, report that exact missing dependency rather than silently falling back to an unrelated design style.

## Product-first workflow
1. Identify product/job, audience, information density, content/proof, device constraints, brand constraints and implementation stack.
2. State a product mechanism and one-sentence visual thesis **before** querying a style/color/font catalog. Name the category defaults most likely to appear automatically.
3. Use UI/UX search to answer specific uncertainties (e.g. data density, readable type behavior, accessible palette roles, interaction patterns). Treat search results as ingredients/evidence, never a complete art direction or an instruction to adopt a named style.
4. For open-ended Depth 2/3 work, explore materially different composition hypotheses before selecting a direction. Palette/font/effect swaps on the same topology count as one hypothesis.
5. Define hierarchy, grid/container topology, typography roles, spacing rhythm, color/material ownership, effect budget, component states, responsive transformations and interaction principles.
6. Test the concept against realistic content, empty/error/loading states, accessibility needs, logo-off/squint/effect-off probes, and mobile recomposition.

Catalog output must never outrank `visual-authoring-core`, a project brief, accepted design contract, or rendered evidence. Do not persist a generated "design system" for Depth 2/3 until AURORA/LENS has accepted the rendered direction.

## Anti-template rules
Avoid habitual AI-SaaS defaults unless the product genuinely calls for them: purple/cyan glow, decorative glass blur everywhere, endless rounded pills, generic centered hero blocks, random gradient blobs, mixed icon families, fake charts/data, and animation without information value.

Judge **clusters**, not isolated syntax. A justified gradient or dark surface is fine; three or more dominant category/model defaults without independent product reasons is `GENERIC RISK: HIGH` for Depth 2/3.

Distinctiveness should come from deliberate typography roles, composition, content/proof treatment, color/material topology, interaction, density, authored assets and responsive behavior—not gimmicks.

## Scale-aware design gate
- **Major new UI / redesign:** AURORA produces a full implementation-ready design spec.
- **Small patch in an established system:** use a concise delta spec; do not force a giant design document.
- FRAME follows the accepted design intent, but may flag technical/accessibility constraints and propose the smallest coherent adjustment.
- LENS judges the actual rendering; a design spec is not visual QA evidence.
