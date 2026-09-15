# Macro-Compositional Diversity Gate & Anti-Template Normalization Standard

## 1. Diversity is structural

Token changes are not new directions. Recoloring a dark shell, swapping Inter for Space Grotesk, changing radius, adding noise, or replacing one glow with another does not create compositional diversity.

For Depth 2/3 exploration, compare candidates using this **12-axis macro fingerprint**:

| Axis | Inspect |
|---|---|
| 1. Reading / task path | linear, branching, staged, spatial, master-detail, progressive disclosure; where attention moves first/next |
| 2. Shell topology | page regions and their adjacency; persistent vs transient zones; full-bleed vs contained structure |
| 3. Focal distribution | single dominant focus, dual tension, distributed field, dense command surface; relative scale relationships |
| 4. Repetition model | list, matrix, sequence, editorial rhythm, grouped ledger, freeform field; what is actually equivalent |
| 5. Content-to-media relationship | proof beside copy, media as background, artifact as hero, annotation over artifact, data-led, type-led |
| 6. Density model | sparse narrative, mixed cadence, compact operational, progressive density; where density changes and why |
| 7. Navigation relationship | embedded in flow, persistent rail, top-level switcher, contextual local nav, command/search-led, spatial navigation |
| 8. Typographic geometry | role contrast, measure, alignment, wrapping, numeric treatment; not font-name difference alone |
| 9. Surface/material model | flat field, layered surfaces, physical/material metaphor, image-led, line-led, depth hierarchy; effects only when earned |
| 10. Color ownership | which regions own color/contrast and why; not hue names alone |
| 11. Motion grammar | state continuity, narrative transformation, object manipulation, restrained feedback, or intentionally static |
| 12. Responsive transformation | reorder, crop/reframe, interaction swap, disclosure, topology change, preserved identity invariant |

### Core collision rule

Two candidates are **not materially distinct** when axes 1–5 remain effectively the same and differences are mostly typography names, palette, radius, borders, or effects. Regenerate one candidate before tournament entry.

If the same **shell topology + focal distribution + repetition model + content/media relationship** recur from a recent fleet project without a product-specific reason, mark `MACRO_COLLISION` even if token-level differences are large.

## 2. Recent-fleet comparison

When build history for the previous 30 days is available, compare against every relevant recent UI surface in the same broad mode (`Persuade`, `Operate`, `Read`, `Experience`), not a cherry-picked project with an obviously different domain.

Record:

- project/build identifier;
- the 12-axis fingerprint at the level evidence supports;
- meaningful similarities;
- why a similarity is product-required or why it is collision debt.

If the history source is unavailable, write `RECENT_FLEET_COMPARISON: UNVERIFIED` and do not fabricate a diversity PASS. Candidate-to-candidate structural diversity is still required.

## 3. Candidate exploration integrity (AURORA)

1. **Structural divergence:** Candidate differences must be visible in low-information grayscale/squint views. Color/effect swaps do not count.
2. **Anti-strawman:** Every candidate must be viable for the product. Do not make one deliberately awkward so a familiar default wins.
3. **Product mechanism:** Every direction names the product behavior/content/proof that generates its structure.
4. **No novelty quota:** Diversity does not require a HUD, brutalism, terminal styling, 3D, bento, asymmetry, or any other fashionable alternative. A conventional structure may be correct if its relationships fit the task and its craft is product-specific.
5. **Default debt:** Every familiar category/framework choice is retained with an explicit reason or replaced.

## 4. Anti-normalization during implementation (FRAME)

FRAME must preserve the winning candidate's structural fingerprint. Coding convenience is not permission to normalize it into a stock sidebar, card grid, centered hero, or generic responsive stack.

Before LENS review, FRAME records implementation evidence for:

- major region topology;
- focal-size relationships;
- repeated-content model;
- signature product proof/asset;
- typography roles;
- color/material ownership;
- responsive transformations.

Minor CSS/token deviations are implementation details; a changed macro fingerprint is a design-contract violation and returns to AURORA/LENS.

## 5. LENS verification output

LENS reports separately:

- `TOKEN_DIVERSITY: PASS | COLLISION | UNVERIFIED`
- `MACRO_COMPOSITION_DIVERSITY: PASS | MACRO_COLLISION | UNVERIFIED`
- `RECENT_FLEET_COMPARISON: PASS | COLLISION | UNVERIFIED`

`MACRO_COLLISION` blocks visual PASS for Depth 2/3. `UNVERIFIED` must remain visible; it cannot be silently upgraded to PASS from model confidence alone.
