# Universal Anti-Default Visual Authoring Reference

This reference exists to prevent a common failure mode: replacing one AI template with another. It is subordinate to `visual-authoring-core` and must never be interpreted as a recipe library.

The previous generation of anti-slop guidance over-corrected by prescribing combinations such as sans + italic editorial serif, black + glass surfaces, white pill CTAs, marquee masks, and frosted sticky headers. Those can be excellent in the right project, but making them universal merely creates a more fashionable form of generic output.

## 1. What "authored" means

An authored interface has a causal chain that can be inspected:

`product truth -> content/proof -> hierarchy -> composition -> type/color/material -> interaction -> responsive behavior`

If the explanation starts with a style label ("futuristic", "premium", "Awwwards", "glassmorphism", "neo-brutalist", "editorial") and works backward toward the product, the direction is at high risk of being generic.

For Depth 2/3 work, every major visual decision must answer at least one of these questions:

- What real product mechanism, artifact, workflow, audience behavior, or brand commitment does this express?
- What hierarchy or reading-order problem does this solve?
- What information or state does this make easier to understand?
- What proof does this provide that copy alone cannot?
- What interaction causality or spatial relationship does this clarify?

"It looks modern/premium/technical" is not sufficient evidence.

## 2. OFF+BRAND calibration: learn the relationship, not the costume

Fleet research in `hermes-design-research.md` and inspected OFF+BRAND case studies show a useful quality bar without yielding a reusable aesthetic template:

- The strongest hero is usually tied to the subject's mechanism or story. Vizcom demonstrates sketch -> transform -> iterate; motion proves what the product does instead of decorating a generic headline.
- Typography, scale, position, negative space, imagery, and motion operate as one composition. No single effect carries the identity alone.
- Technology is selected as a storytelling/tooling consequence: 3D, WebGL, Rive, GSAP, or simpler treatments are used when the idea needs them. They are not quality badges.
- The visual language changes by client. Restrained enterprise work, expressive athlete/fan work, product-led 3D, and scalable component systems can all meet the same craft bar.
- Mobile keeps the thesis and priority, then changes framing, crop, order, and interaction as needed. Ambition is translated rather than merely shrunk.
- Reusable systems can coexist with original art direction: repeated components preserve consistency while the product-specific content, hierarchy, and signature experience carry identity.

Therefore **do not copy OFF+BRAND's sphere, WebGL, oversized type, color, motion, or typography as a fleet house style**. Copy the discipline: one strong idea, product proof, decisive composition, integrated craft, and breakpoint-specific authorship.

## 3. Composition before chrome

Before adding effects, verify the page in a low-information view (squint, grayscale, or blurred screenshot):

- one primary focal region is obvious;
- secondary regions form an intentional reading/task path;
- repetition reflects equivalent content rather than a component-library habit;
- negative space separates meaning instead of padding an under-designed page;
- section rhythm changes when narrative priority changes;
- the composition remains recognizable when brand name/logo is hidden.

Cards, bento grids, sidebars, split heroes, sticky rails, full-bleed media, and editorial fields are all valid structures. None is a default answer. Choose topology from content relationships and workflow.

## 4. Typography is a role system

Define the jobs first: display, heading, body, label, data/numeric, code, annotation, or any smaller subset the product actually needs.

For each role specify:

- hierarchy contrast (size, weight, width, case, spacing, style);
- reading measure and line-height behavior;
- wrap/truncation/localization behavior;
- numeric/data features when relevant;
- fallback and loading behavior;
- why the chosen face belongs to this subject or operating context.

One family can be excellent. Two or more families can be excellent. A sans + italic serif pairing is **not** inherently more authored than a disciplined single-family system. Do not add a serif, mono, all-caps label, or extreme display face merely to signal taste.

## 5. Color and material use topology, not swatch decoration

Write the palette as roles and spatial ownership:

- dominant field/canvas;
- primary and secondary ink;
- contrast anchor(s);
- action/focus/selection;
- semantic state colors;
- optional atmospheric/material regions.

Then state where each role appears and approximately how much visual area it owns. This prevents "accent color everywhere" and random gradient spraying.

### Effect budget

Glow, blur, gradient, glass, grain, bloom, particles, 3D lighting, chrome reflections, and shaders are **effects**, not identity by themselves.

For each effect used, record:

1. its semantic or material purpose;
2. the bounded region(s) where it may appear;
3. what the hierarchy looks like with the effect removed;
4. its reduced-motion/performance fallback when applicable.

If several effects all express the same vague idea ("futuristic", "AI", "premium"), keep the strongest one or remove the cluster.

## 6. Assets carry proof

The largest visual regions deserve the strongest content. Prefer, as available:

- real product UI/data/artifacts;
- authentic photography or project media;
- generated/procedural assets designed for the composition;
- diagrams that explain a mechanism;
- typography-led composition when type itself is the correct evidence.

Do not fill a missing proof region with glass cards, gradient blobs, generic device mockups, icon tiles, or fake telemetry. Chrome cannot compensate for absent content.

## 7. Motion must have causality

Every motion pattern states `trigger -> change -> meaning -> end state`.

Good uses include demonstrating transformation, preserving spatial continuity, revealing cause/effect, indicating active work, or focusing attention during a narrative transition. Stable status does not pulse. Identical fade-up entrances on every section are not choreography.

For brand/experience surfaces, one authored sequence can be expressive. For operate/read surfaces, interaction feedback and state continuity usually matter more than ambient motion.

## 8. Responsive means re-authoring

For each major region, decide whether narrow layouts should:

- preserve;
- reorder;
- reframe/crop;
- collapse/disclose;
- change interaction model;
- simplify decorative complexity;
- move an action into a reachable position.

Record the identity invariant that must survive. A desktop split composition may become an overlap, crop, sequence, carousel, or linear story on mobile. "Stack all columns" is only acceptable when the resulting priority and narrative remain intentional.

## 9. Default-cluster challenge

These are warning clusters, not banned syntax:

| Familiar cluster | Challenge before accepting |
|---|---|
| Near-black canvas + cyan/purple neon + glass cards + mono labels | What product mechanism independently earns each piece? Would a non-AI/non-crypto product use the same shell unchanged? |
| Warm cream + editorial serif + terracotta/red accent + hairlines | Is this derived from the subject, or a current design-model default? Does type/content still feel specific with the palette removed? |
| Centered badge + huge gradient headline + two pill CTAs + 3-card feature row | Does the visitor's real decision path actually have this hierarchy? What proof belongs in the first viewport instead? |
| Arbitrary bento grid of equal rounded tiles | Are the items semantically equivalent and spatially comparable, or was the grid selected because it is easy to generate? |
| Sidebar + KPI cards + chart cards + generic table | Does the user's operating workflow need these regions in this order, or is this a dashboard starter template? |
| Full-page WebGL/particles | Does the spatial behavior explain or embody the subject, and is there an equally clear reduced/fallback path? |

If **three or more** dominant choices come from a familiar cluster and have no independent product/brief rationale, classify the direction as generic and redesign at the composition/content level. Changing hue, radius, font, or glow intensity does not clear the finding.

## 10. Final authoring checks

Before hand-off, answer with rendered evidence:

1. **Mechanism:** What product truth visibly shaped the page?
2. **Composition:** What makes the reading/task path specific to this content?
3. **Typography:** What are the role contrasts, and why these faces/metrics?
4. **Color/material:** Which regions own the palette and effects, and why?
5. **Assets:** What visual proof occupies the major regions?
6. **Motion:** What changes, why, and when does it stop?
7. **Responsive:** What was re-authored on mobile, and what identity cue survived?
8. **Default debt:** Which category/framework defaults were deliberately kept, and why?

If those answers are generic adjectives or CSS descriptions instead of product relationships, the work is not ready for visual PASS.
