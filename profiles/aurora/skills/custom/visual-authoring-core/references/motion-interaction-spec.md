# Motion & Interaction Spec — Authoring Rules

Rules for the class "author a motion/interaction spec that an implementer will code verbatim".
These are load-bearing correctness rules, not stylistic preferences: each one has bitten a real
implementation. Companion to the DESIGN_DNA ``motion principles`` slot in SKILL.md Stage 5.

---

## The one-line thesis to hold

Calm, purposeful motion with a few authored living moments. Motion clarifies state, causality,
and arrival. It never delays content, never loops, and never prices a legibility win for a flourish.

## Entrance must add motion, never hide content

- Page-load entrance animates **transform only** (translate/scale), never opacity. The hero must be
  fully legible at every frame, so first-paint can be proven with one computed-style assertion.
- Never author the pre-state in the shipped HTML. Add the entrance class from JS so a no-JS or
  CSS-failure page renders fully visible.
- Any scroll-reveal pre-state (e.g. `opacity: 0`) must live inside `@supports (translate: 0 0)`.
  No `@supports`, no hidden content — a browser missing the property must never get a blank page.

## The reveal deadline that strands elements forever

- The IntersectionObserver's effective root bottom is inset by its `rootMargin` (e.g. `-12%`).
  A reveal whose "already visible, mark done" boundary is *shallower* than that inset creates a
  **dead band**: an element parked there is partly visible on screen (so must not be dimmed) yet
  outside the root (so it can never intersect and can never reveal). It stays invisible forever.
  The boundary margin must be **larger** than the observer's root inset.
- Tag-time geometry and settled geometry disagree (measured ~29px on a real prototype). Add a
  protective margin, not an exact `innerHeight` comparison.
- Belt and braces: a bounded **one-shot** sweep promotes any still-pending element that is now
  inside the viewport. Per-element timer handles — a single shared handle is overwritten by the
  next item in the same batch, so only the last element ever gets its safety net.
- Inset (in-sheet) batches get **no early sweep**: at ~250ms a sheet has lifted its rows into view
  but their own stagger has not finished, and an early sweep would collapse it.

## Reduced motion removes movement, never geometry

- Never write a blanket `transform: none !important` over a component whose resting pose *is* a
  transform. If centring is `translate(-50%, -50%)` with `left: 50%`, cancelling the transform
  leaves `left: 50%` in force and throws the element far off-centre and partly off-screen.
- Reproduce the **resting pose** per breakpoint inside the reduced-motion block instead.
- Neutralising *timing* is not enough: override static pre-states (`opacity`, `translate`, `scale`)
  too, or reduced-motion users keep an invisible element that will never animate away.
- Any component whose enter/exit axis is a `translate` needs its settled pose pinned here as well,
  not just its `transform`: a pre-state offset held under reduced motion is the same class of bug.

### A mid-flight check under reduced motion is a self-contradicting gate

With timing neutralised to an instant there is no interior frame to sample, so an assert of the
form "the element was observed mid-flight" can only pass if the fallback is **broken**. Do not write
it, and do not silently omit the coverage either — **replace it** with the property that actually
holds, so the acceptance criteria still name a check:

| instead of | assert |
|---|---|
| element was mid-flight | it reached its settled pose instantly (state class applied, not hidden, correctly positioned, `opacity >= 0.999`) |
| element showed an interior opacity | **no** interior frame was ever recorded, and no intermediate pose was held |
| (nothing) | the transition duration was neutralised, and the lifecycle still terminated (node removed) |

State the replacement rule in the spec as a contract, not a note: every mid-flight N/A must be
replaced by its settled-state assertion, and a revision that drops the replacement is a coverage
regression, not housekeeping. The replacements must themselves be non-vacuous — see the
painted-frame rule below.

## Sampling mid-flight state without racing the clock

A flaky gate is worse than no gate: it burns cycles, and a green run cannot be trusted. Never assert
an in-transition state by sleeping a fixed wall-clock interval and reading the node once. The exit
may be shorter than the sleep, or a JS timer may remove the node mid-sleep, and the assert then fails
on sampling luck rather than on the artifact.

**Record the series, then pick the frame.** Run an in-page `requestAnimationFrame` recorder across
the element's whole lifecycle and assert against the recorded frames:

- enter = first frame carrying the entered-state class with `0 < opacity < 1`
- settled = last frame while the settled class holds and no exit class is present
- exit = first frame carrying the exit class with `0 < opacity < 1`

Sample the **interior** of a transition, never its boundary. The first frame of an enter or an exit
transition holds the value it is travelling *from* (often `opacity: 0` or `1`), which is not a
mid-flight state; an assert that reads it is mis-calibrated even when it happens to pass.

**Guard against degenerate captures.** Assert that the series actually observed what is being
claimed: at least 2 frames in the exit window, and removal observed in the log. Without a guard, a
recording that captured one frame — or none — passes silently.

**Filter to painted frames before judging position.** A `display: none` element (a `[hidden]` sheet,
a removed node) reports `transform: none`, which differs from the settled transform and gets
miscounted as mid-travel. Record a `painted` flag (has client rects AND not `[hidden]`) and judge
only painted frames; also report the painted-frame count so the population is auditable. The same
filter is what proves a reduced-motion "0 mid-flight frames" result is real rather than an empty
recording — a healthy run shows dozens of painted frames and zero of them interior.

**Slowing the timeline does not slow JS timers.** CDP `Animation.setPlaybackRate` scales CSS
animation/transition time only. A removal timer set in JS still fires in real time, so a mid-state
screenshot must be taken inside the real window: poll for the state change and then shoot, rather
than sleeping a guessed interval.

**Two green runs are two observations, not a proof of determinism.** Repeated passes cannot falsify a
low-rate race. Quote the per-context frame-count **distribution** (e.g. exit frames `12, 12, 12`
against a `>= 2` guard) as the margin, and if the host was loaded, say so plainly: passing under a
hostile load band is a stronger claim than passing on an idle box, but it is still not determinism.

## Two owners of one property fight silently

- If a component already owns `transform` (hover lift + press scale), do the reveal on
  `translate`/`scale` instead — otherwise one declaration quietly wins and the other is lost.
- A reveal's `transition` shorthand can outrank a component's own transition rule. Hand the element
  off to a terminal state (a `done` attribute/dataset) once the reveal lands, restoring the
  component's ownership. Without it, a hovered element inherits the reveal's duration **and its
  stagger delay** — a delayed hover is a defect.
- Guard the `transitionend` handler: ignore events where `event.target !== node` (descendants
  bubble) and where `propertyName` is not the property you animated. Either would drop the reveal
  state mid-flight.

## Numbers and state

- Never tween a number. Animate the **container** (a composited `scale` pop) while the digits change
  instantly, with `tabular-nums` — no reflow, no jitter, no neighbour shifting.
- Fire change-pops only on a real change, never on first paint.
- Countdowns, prices, and stable status do not animate at all.

## Budgets that keep it calm

- Cap animated elements per batch and cap the stagger delay hard; keep the worst-case reveal tail
  under ~300ms so a list never lands visibly late.
- Hover rules only under `@media (hover: hover) and (pointer: fine)` — a touch device must never get
  a sticky hover.
- Keep press feedback short (a dedicated short duration token) and separate from enter/exit.
- Never animate layout properties (width/height/top/left/margin). Never animate a focus ring.
- Prefer a transition + class add over a keyframe when a leaving element must not reflow siblings.
- Exit timing should be read from a token, not repeated as a magic number in JS.

## Forbidden list (make it explicit in the spec)

Infinite loops / ambient animation; parallax; scroll-jacking; smooth-scroll hijacking; animating
layout properties; animating focus rings; emoji; pulsing CTAs; fake telemetry; delaying critical
content; functional-element animation longer than ~600ms; re-animating already-revealed elements on
scroll-up.

## Acceptance checks the spec should name

- `document.getAnimations().filter(running).length === 0` at idle, and zero `infinite` occurrences.
- First paint: named above-the-fold elements present with `opacity: 1` at an early timestamp — the
  entrance travel may be mid-flight, legibility must not be.
- Mid-animation screenshots for each authored moment (cascade, pop, toast, sheet).
- Reduced-motion pass: sampled transitions neutralised, no dimmed element in view, dialogs still
  centred and fully in-viewport — and the settled pose identical to the no-preference pose, which is
  the check that proves the reduced-motion override did not destroy geometry.
- Mid-flight claims: never assert one from a timed single read. Record the frame series, assert on the
  interior frame, guard the series length, and quote the frame-count margin.
