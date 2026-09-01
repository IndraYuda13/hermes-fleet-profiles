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
1. Identify product/job, audience, information density, content type, device constraints, brand constraints and implementation stack.
2. Search styles/typography/colors/UX guidance that fit those constraints.
3. Choose one coherent visual concept and define why it fits. Do not mix unrelated aesthetics.
4. Define hierarchy, grid/container behavior, typography scale, spacing rhythm, color roles, component states, responsive transformations and interaction principles.
5. Test the concept against realistic content, empty/error/loading states and accessibility needs.

## Anti-template rules
Avoid habitual AI-SaaS defaults unless the product genuinely calls for them: purple/cyan glow, decorative glass blur everywhere, endless rounded pills, generic centered hero blocks, random gradient blobs, mixed icon families, fake charts/data, and animation without information value.

Distinctiveness should come from deliberate typography, composition, content treatment, interaction, density and consistent system choices—not gimmicks.

## Scale-aware design gate
- **Major new UI / redesign:** AURORA produces a full implementation-ready design spec.
- **Small patch in an established system:** use a concise delta spec; do not force a giant design document.
- FRAME follows the accepted design intent, but may flag technical/accessibility constraints and propose the smallest coherent adjustment.
- LENS judges the actual rendering; a design spec is not visual QA evidence.
