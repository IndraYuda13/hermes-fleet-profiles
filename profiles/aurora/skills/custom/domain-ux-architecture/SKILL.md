---
name: domain-ux-architecture
description: "Use for domain-specific product UX architecture."
version: 1.0.0
metadata:
  hermes:
    tags: [ux, architecture, accessibility, learning, documents, ats, fintech, checkout, product-design]
    category: custom
---

# Domain UX Architecture

Class-level guidance for designing product interfaces whose domain constraints materially shape the interaction model: inclusive learning tools, document and ATS builders, digital commerce, and fintech checkout. Start here when a product's users, data integrity, accessibility needs, export format, or payment lifecycle matter more than a generic component recipe.

## Always-On Architecture Rules

- **Derive structure from the user's irreversible risk:** Preserve attention and transcript data in learning tools, parser fidelity in documents, and price/payment truth in commerce; domain risk should decide layout and state handling.
- **Model asynchronous and failure states explicitly:** Every inquiry, scoring, export, payment, delivery, and live-stream operation needs loading, stale, timeout, retry, and terminal states so the interface never implies success from a request merely starting.
- **Keep source-of-truth boundaries visible:** Recompute prices and inventory on the server, normalize imported document data before rendering, and distinguish interim from finalized live text so client convenience cannot corrupt authoritative state.
- **Make every important signal perceivable through more than one channel:** Pair color with text, icon, position, motion, or sound-equivalent feedback, while honoring reduced-motion, hearing, and keyboard needs.
- **Reserve layout space before dynamic content arrives:** Use stable media ratios, measured page boundaries, reserved live regions, and predictable bottom clearance to prevent reflow, clipping, and occlusion.
- **Treat mobile as a re-authored task flow:** Transform controls according to task priority—such as a payment dock, focused detail route, or horizontal category track—instead of blindly stacking desktop regions.
- **Use progressive disclosure to protect focus:** Keep the primary task visible, move secondary audits or setup details into deliberate drawers/accordions, and provide direct return paths to the field or state that needs action.
- **Verify the real interaction contract:** Do not display shortcut hints, live status, export claims, or payment completion affordances unless the corresponding event handlers, persistence, and terminal-state checks exist.

## Domain Sections

### Inclusive Learning and Shared Displays

- Replace auditory-only cues with visual or tactile equivalents, and never add ambient audio to assistive learning flows unless explicitly required.
- Preserve finalized transcript nodes while updating only the interim tail; this prevents visual jitter during speech recognition and protects dual-gaze tracking.
- Pause auto-scroll when the learner inspects history or a word definition, and offer an obvious return-to-live control.
- Design classroom views for distance and projector washout: retain split layouts at common XGA widths, use fluid large type, high contrast, and explicit wrapping for long tokens.
- Persist uncommitted transcript data continuously and expose microphone activity visually before transcription arrives.
- Give shared-display controls keyboard and presenter support, with touch targets of at least 44px and a distraction-free presentation mode.

See `references/inclusive-learning-and-display.md` for the detailed interaction and accessibility checklist.

### Document, Resume, and ATS Builders

- Keep parser-facing documents linear and semantic; vary templates through typography, spacing, hierarchy, and restrained accents rather than multi-column reading order.
- Monitor rendered page height continuously, protect repeatable blocks from splitting, and surface a clear overflow warning before export.
- Debounce live scoring and deep-link each finding to the exact field that can fix it; feedback must be actionable without displacing the editing context.
- Normalize imported or stored profiles through a versioned adapter before rendering, and keep preview and DOCX/PDF export configuration synchronized.
- Treat URLs, labels, bullets, metrics, and section order as content quality constraints, not merely visual decoration.

See `references/document-export-and-ats.md` for parser, scoring, persistence, and export rules.

### Fintech Checkout and Digital Commerce

- Prefer a short, unidirectional purchase path with scoped drafts, non-blocking identity inquiry, deterministic server-side pricing, and explicit inventory/security boundaries.
- Represent payment as a state machine from pending through confirmation, fulfillment, and receipt; use idempotency, signed webhooks, atomic claims, and visibility resync to prevent duplicate or stale outcomes.
- Preserve guest conversion by deferring account creation until after purchase, while providing secure order lookup and short-lived account-binding links.
- Keep payment and price surfaces numerically stable: use tabular numerals, reserved media geometry, minimum touch targets, safe-area padding, and keyboard-aware floating actions.
- Use branded imagery only when it verifies the selected product; provide resilient fallbacks and zero-CLS containers instead of decorative asset dependence.
- Make tactile feedback optical or haptic by default in consumer checkout, and keep expensive effects bounded by visibility, viewport, and device-pixel-ratio budgets.

See `references/fintech-commerce-patterns.md` for checkout state, catalog, media, responsive, and performance patterns.

## Domain QA Gate

Before handoff, verify:

1. The primary domain failure mode is named and covered by an explicit UI state.
2. Dynamic content cannot cause loss of data, silent clipping, layout shift, or duplicate fulfillment.
3. Keyboard, touch, assistive technology, reduced-motion, and distance-viewing behavior are specified where relevant.
4. Server-authoritative values and client drafts are clearly separated.
5. Exported or delivered artifacts are tested in their real downstream consumer, not only in the preview.
6. Fixture data exercises success, empty, loading, stale, failure, and terminal states with realistic domain values.
