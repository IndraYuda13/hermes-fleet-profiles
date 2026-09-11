---
name: production-ui-overhaul-governance
description: Use when planning and executing production UI/UX overhauls.
version: 1.0.0
metadata:
  hermes:
    tags: [ui, overhaul, kanban, orchestration, rollback, qa]
    category: custom
---

# Production UI Overhaul Governance

## Overview
Standard operating procedure for executing major UI/UX overhauls and visual redesigns on live, running web applications. Ensures zero downtime, cryptographic rollback readiness, mathematical visual precision, and rigorous multi-agent verification.

## 1. Pre-Overhaul Stable Baseline & Rollback Anchor (ATLAS)
Before modifying any production source files, styles, or templates:
1. **Dynamic Git Anchors (Anti-Stale-Baseline Invariant):** Never assume the active branch from memory, notes, or documentation. Always query runtime git state: record exact active branch (`git symbolic-ref --short HEAD`) and exact commit SHA (`git rev-parse HEAD`). Tag the stable state (`vX.Y.Z-pre-overhaul-stable`) from that exact commit and branch to a dedicated feature branch (`feature/<name>`).
2. **Feature Signature Fingerprinting:** Inspect and record critical interactive/visual capabilities currently live in production (e.g. WebGL/Three.js 3D canvas `#vault3dCanvas`, procedural shaders, audio toggles, specific script bundles). Rollback scripts and verifiers must target these exact signatures.
3. **Physical Standalone Backup:** Clone the active web/frontend directory to an isolated backup directory (e.g., `web-skeleton-backup-vX-pre-overhaul-stable/`) and verify file count and SHA-256 cryptographic parity.
4. **1-Click Rollback Script:** Generate an automated script (`rollback_to_vX_stable.sh`) with `--dry-run` capability that restores files from the standalone backup, checks out the exact recorded branch and commit SHA, and confirms service health.
5. **Feature-Level Rollback Verification:** Rollback verification must NOT stop at HTTP 200 or page `<title>` match (both can pass on a stale or downgraded baseline). The verification must use headless browser evaluation to confirm that recorded feature signatures (e.g. 3D canvas dimensions > 0, interactive scripts, WebGL context) are actively rendering before declaring rollback complete.

## 2. HD Asset Discovery & Mathematical Ratio Curation (RADAR)
Never rely on low-res placeholders or deformed graphics during an overhaul:
1. **Source Authentic High-Res Media:** Search and download transparent PNG/WebP character artwork, official game/brand vector logos, and promotional assets.
2. **Aspect-Ratio Parity ("Anti-Menceng" Invariant):** All cards (e.g. 3:4 portrait cards) must strictly conform to target ratios (`aspect-ratio: 3 / 4;` or exact width/height like 600x800 px).
3. **Automated Verification:** Execute a Python script using Pillow (`PIL.Image`) to verify `(w, h)`, aspect ratio (`w / h`), alpha channel extrema, and format before delivering assets to the frontend implementer.

## 3. Design DNA & Geometry Contract (AURORA)
Establish a binding design contract (`DESIGN_CONTRACT.md`) defining:
- Shell architecture (e.g. fixed left navigation rail on desktop vs. docked bottom navigation on mobile).
- Strict design tokens: base dark canvas, surface panels, 1px specular hairlines, and primary/secondary accent colors.
- Pure inline SVG contract: avoid external mutating CDN icon scripts (e.g. `lucide.createIcons()`) that trigger layout shifts (CLS) or fail during dynamic DOM re-renders.

## 4. Native Frontend Implementation & Zero-Regression Logic (FRAME)
Implement layout natively using standard CSS Grid and Flexbox:
- **Mobile Ergonomics:** Replace desktop rails with floating or docked bottom navigation bars (min height 44px+ touch targets) and include keyboard safety guardrails (`body:has(input:focus)` or `focusin` listeners).
- **Zero-Regression Wiring:** Preserve existing state engines, catalog endpoints, debounced inquiry validators, QRIS countdown timers, SSE polling, invoice tracking, and auth sessions.
- **Continuous Width Scrubbing:** Ensure `document.documentElement.scrollWidth <= window.innerWidth` across continuous width sweeps from 320px to 1920px (zero horizontal overflow).

## 5. Dual Independent Quality Gates
A production overhaul cannot be released based on developer self-certification:
- **PRISM (Functional QA):** Executes automated test suites (e.g. pytest, Playwright end-to-end tests) verifying catalog pagination, nickname inquiry validation, checkout drawer flow, order tracking, and account wallet authentication. Requires 0 console errors and 0 unhandled exceptions.
- **LENS (Visual & Geometry QA):** Audits rendered DOM across 8+ standard viewports, tests interactive states (hover, drawer slide-over, dialogs), and asserts WCAG 2.1 AA text contrast compliance.
- **ORION (Meta-Gate):** Evaluates verifiable on-disk evidence (`RELEASE_DECISION_RECORD`) before transitioning state to `AWAITING_OWNER_REVIEW`.
