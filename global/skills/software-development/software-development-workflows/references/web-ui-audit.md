# Evidence-Driven Web UI Audit

Use this reference for redesign reviews, mockup audits, responsive QA, and pre-production UI validation.

## 1. Establish the real target

Before judging pixels, map the live page to its source and runtime:

- Find the project directory from session history and filesystem evidence.
- Resolve proxy or tunnel ingress to the local port.
- Identify the listener process, parent process, bind address, service-manager unit, restart policy, and health behavior.
- Resolve proxy/tunnel configuration to the actual listener; a similarly named service may serve a different directory or port.
- Compare hashes of live static assets with local files when possible.
- Record whether the target is a disposable mock, production frontend, or stale duplicate.

This prevents reviewing the wrong tree and exposes deployment risks such as an unsupervised preview server parented by a shell/gateway, a public bind that relies only on firewall policy, or missing version control. HTTP 200 is not deployment readiness.

## 2. Audit four layers separately

### Visual system

Check hierarchy, typography, spacing rhythm, color tokens, icon language, surface and elevation system, brand distinctiveness, and whether visual effects support the product.

Do not equate modern with neon, glass, gradients, or 3D. A style only succeeds when it strengthens brand recognition and the primary user task.

### Conversion and information architecture

List every apparent entry point and primary CTA. If search, shortcut cards, and a wizard all compete, the page lacks a clear conversion path. Verify that decorative hero content does not push the transaction task below the fold, especially on mobile.

### Functional flow

Exercise every major route end to end:

- Search and empty search
- Popular shortcuts
- Every wizard branch
- Backtracking and changing parent selections
- Empty, invalid, long, and special-character form inputs
- Payment-method fees, totals, and payment-specific completion instructions
- Required fields cannot be bypassed; displayed category, product, target, fee, total, method, and final instructions remain mutually consistent
- Confirmation, payment, order tracking, login, and modal dismissal

After changing a parent selection, assert that dependent state is reset. A valid dependency is `category -> brand -> type -> product -> destination -> payment`. Changing `brand` must clear `type`, `product`, price, and incompatible downstream state.

### Semantics and accessibility

Automated accessibility scores are not sufficient. Manually verify:

- Clickable cards use semantic controls or equivalent role, keyboard activation, and focusability.
- Tab order reaches all actions.
- Focus indicators are visible.
- Dialogs have dialog semantics, initial focus, focus containment, Escape dismissal, and focus restoration.
- Tap targets are at least 44 by 44 CSS pixels.
- Inputs have visible labels, appropriate types, validation, and nearby recovery text.
- Reduced-motion mode actually stops decorative animation.

## 3. Probe implementation seams

Static source inspection should include:

- Inline handlers whose referenced functions are missing.
- CSS classes used by dynamic views but never styled.
- `innerHTML` fed by user, URL, API, or persisted state.
- Default browser controls leaking into themed screens.
- Timers, animation loops, and global event listeners without cleanup.
- WebGL initialization without capability fallback.
- Hard-coded category or product assumptions in shortcut handlers.

For DOM insertion tests, trace the complete source-to-sink path and use harmless marker markup in a controlled audit. First verify whether the input becomes an element; when authorized, use a non-destructive execution marker such as setting a temporary `data-*` attribute to distinguish HTML injection from executable DOM XSS. Record the exact source location and sink. Treat successful insertion as an injection sink even if the current source is self-XSS only; do not extrapolate to server compromise without evidence.

## 4. Responsive verification discipline

Use fresh navigation at each viewport. Resizing a live WebGL page can reveal useful race conditions, but it must not replace a fresh mobile load.

Test at minimum:

- Desktop 1440 by 900
- Mobile 375 by 812
- Tablet around 768px

Record document width versus viewport width and enumerate overflowing elements. Inspect touch-target dimensions programmatically. For WebGL canvases, compare CSS bounds and backing-store dimensions after resize.

## 5. Performance and graceful degradation

Run a lab audit, then interpret it instead of copying scores. Capture FCP, LCP, Speed Index, TBT, CLS, console errors, unused JavaScript, render-blocking resources, and forced reflow.

For 3D or continuous motion:

- Lazy-load the renderer after critical UI.
- Prefer a smaller renderer or custom shader when a full engine is mostly unused.
- Provide a static image or CSS fallback.
- Catch WebGL context creation failure.
- Pause when off-screen or when the document is hidden.
- Respect `prefers-reduced-motion`.
- Downgrade or remove decorative 3D on small screens when it delays the task.

## 6. Reporting

Prioritize findings by user and business impact:

- **P0:** broken core action, invalid transaction state, injection or security sink, data loss.
- **P1:** severe conversion, accessibility, responsive, or deployment weakness.
- **P2:** polish, SEO, minor performance, and content defects.

Each finding should contain evidence, impact, and concrete remediation. Separate observed fact from design judgment. Recommend a redesign direction only after identifying the highest-leverage structural problem.
