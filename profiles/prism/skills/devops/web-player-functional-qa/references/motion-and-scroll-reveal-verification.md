# Motion & Scroll-Reveal Verification

Depth for SKILL.md §8-9: proving motion, reveal, reduced-motion, and idle-animation claims. Motion bugs are timing- and path-dependent, so a single pass proves almost nothing; the verdict comes from varying the reproduction path.

## Reveal state machine to assert
Most scroll-reveal implementations use three states on the same attribute/element set:
- `pending` -- below the fold at tag time, hidden (`opacity:0`, translated).
- `in` -- intersecting, transient; the reveal transition is running.
- `done` -- terminal; the transient reveal transition is removed so the component's own transition (e.g. hover) regains ownership.

Assert the **terminal** state, not the presence of animation: after the reveal settles, every revealable element must be `done` and `getComputedStyle(el).transitionProperty` must contain the component's own property (e.g. `transform`), proving the handoff landed. An element stuck in `pending` or `in` is a FAIL.

## The IntersectionObserver margin dead zone (highest-value defect class)

A reveal is often tagged by a geometric fold test but revealed by an observer with a shrunken root. Whenever the tag threshold and the observer's effective bottom differ, the band between them is a **permanent invisible hole**: elements tagged hidden that can never intersect, so they stay `opacity:0` forever.

```js
// tag rule:                 top >= vh * 0.92  -> pending (hidden)
// observer: rootMargin '0px 0px -12% 0px'    -> effective bottom = vh * 0.88
// dead band: [vh*0.88, vh*0.92)  -> tagged pending, can never intersect
```

Detection: after settling, list elements still `pending` and print `getBoundingClientRect()` for each. A `pending` element whose box overlaps the viewport is a hole; one fully above/below is merely off-screen and harmless until scrolled to. Compute the numbers -- `vh`, the tag threshold, and the observer's effective bottom -- rather than eyeballing a screenshot.

## Reproduction matrix (which paths trigger, which recover)

Scroll path determines whether the dead band is ever entered. Test all of these; a defect that appears under one and not another is path-dependent and must be reported as such.

| Path | Typical result |
|---|---|
| Instant jump deep into the page, then stay | enters the dead band; elements strand hidden |
| Instant jump, then incremental scroll back | may strand a subset |
| Single moderate flick / smooth scroll / `{behavior:'smooth'}` | observer fires on the way through; recovers |
| Keyboard `PageDown` xN / `Home` | usually recovers |
| Full incremental sweep over the whole page | terminal state for every element |

**Prefer the real in-product trigger over a synthetic `scrollTo`.** A same-page anchor, a deep link, or a category/pagination action that jumps scroll is a genuine user path and turns a "probe artefact" into a confirmed product defect. If the only trigger is one exact synthetic sequence, treat it as suspect until an in-product path reproduces it.

## Reduced-motion fallback assertions
- In `reduce`, hidden `pending` content must be forced visible: assert computed `opacity == '1'` and `translate` in `{none, 0px}` on a `pending` element, independent of whether JS ran. Content must never be dimmed.
- Transition/animation neutralisation: assert the computed value the engine reports, not the source literal -- a `0.001ms` rule computes to `"1e-06s"` and numerically starts with `0.000001s`.
- Global `!important` reduced-motion overrides can also cancel layout transforms the desktop design relies on (e.g. a centring `translate`). Visually check geometry, not just durations.

## Idle / infinite-animation check
- `document.getAnimations().filter(a => a.playState === 'running').length` must be `0` at rest and after settling. Non-zero at idle means an infinite/looping animation leaked past the intended bounded motion.

## Evidence binding
- Bind captured PNG/JSON to the artifact revision by hashing the source file (`sha256`) before and after the run; confirm it is unchanged.
- Attribute artifacts to your run by mtime window; a later run or a concurrent writer can overwrite the same filename and silently invalidate your evidence.
