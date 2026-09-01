---
name: fleet-impeccable-orchestration
description: Orchestrate Impeccable UI design & QA across fleet roles.
version: 1.0.0
author: Fleet Architecture & Orion Lead
license: MIT
metadata:
  hermes:
    tags: [ui, ux, impeccable, design-systems, frontend, visual-qa, orchestration, aurora, frame, lens, orion]
    category: fleet-upgrade
---

# Fleet Impeccable Orchestration Standard (V1.0)

Protocol for integrating the `impeccable` design and frontend engineering capability across the Hermes Fleet (ORION, AURORA, FRAME, LENS) while strictly preserving role separation, evidence discipline, and zero-production-edit boundaries.

## When to Use
Use whenever executing frontend redesigns, UI/UX overhauls, design system creation, or web application building where Impeccable design tools and playbooks are available to the fleet.

---

## 2. Fleet Role Ownership & Impeccable Allocation

| Fleet Role | Ownership Boundary | Impeccable Workflows & Tools | Key Artifacts / Deliverables |
|---|---|---|---|
| **ORION** | Orchestration, decomposition, dependency DAG, evidence governance, final synthesis (`orion_production_edits == 0`). | `routing`, `shape`, `craft-floor` reference review. | Mission Contracts, Release Decision Records, Synthesis Reports. |
| **AURORA** | Product design authority, information architecture, visual direction, design system tokens. | `init`, `concept-seed`, `palette` (OKLCH Helmholtz-Kohlrausch rules), `typeset`, `craft-floor`. | `PRODUCT.md`, `DESIGN.md`, `DESIGN_DNA.md`, `DESIGN_CONTRACT.md`, `UI_STYLE_FINGERPRINT.md`. |
| **FRAME** | Production frontend engineering, browser-side code, state machines, API integration. | `typeset` (tabular numbers), `layout`, `adapt` (dual-mode responsive), `polish`, `optimize`. | `styles.css`, `app.js`, `index.html`, responsive layouts. |
| **LENS** | Independent rendered visual/interaction QA & art direction verification (LENS does not edit code). | `audit`, `critique`, `contrast-rhythm`, `responsive-integrity`. | `VISUAL_QA_REPORT.md`, multi-viewport screenshots, overflow audits. |

---

## 3. Core Execution Principles & Invariants

1. **Role Boundary Invariant:**
   - ORION governs and never touches production source.
   - AURORA specifies design and never implements code.
   - FRAME implements code and never self-certifies visual QA.
   - LENS audits rendered artifacts and never modifies production source.
2. **Tabular Numeric Rule:**
   - Always enforce `font-variant-numeric: tabular-nums` (e.g. JetBrains Mono / monospace pairing) on prices, timers, nominals, and numeric counters to prevent layout jitter during real-time polling.
3. **Glassmorphic GPU Layer Isolation:**
   - Pair `backdrop-filter: blur(20px)` with `contain: layout paint` and `transform: translateZ(0)` on fixed/sticky navigation bars to eliminate mobile compositing lag.
4. **Mobile Touch Safety Floor:**
   - Interactive elements, buttons, category tiles, and form inputs must enforce a minimum 44×44px touch target geometry on mobile viewports (<=768px).
5. **Zero Horizontal Overflow:**
   - Enforce `max-width: 100vw; overflow-x: hidden;` on body/root and test across 7 canonical viewports (`320px`, `360px`, `390px`, `768px`, `1024px`, `1440px`, `1920px`).

---

## 4. Supporting Knowledge Banks
- `references/live-nickname-inquiry-pattern.md` — Real-time debounced game ID & nickname lookup architecture, sequence token race condition prevention, and non-blocking fallback strategies.
- `references/rich-brand-asset-catalog-pipeline.md` — Complete discovery, dynamic path traversal-safe serving, 3:4 portrait poster card design, and fallback rendering pipeline for high-density brand visual catalogs.
- `references/in-game-items-and-currency-cards.md` — In-game item currencies, tiered diamond assets, glowing pass badges (WDP/Welkin/Starlight), and dynamic client-side resolution patterns.

