---
name: creative-engineering-orchestration
description: Route UI builds through expert design, implementation, visual QA, remediation, and final verification.
version: 2.0.0
metadata:
  hermes:
    tags: [orchestration, frontend, design, kanban]
    category: custom
---

# Creative Engineering Orchestration

## When to use

Websites, dashboards, web apps, frontend-heavy features, redesigns, design systems, UI/UX repair, or any task where rendered experience matters.

## Default specialist roles

AURORA — product design direction.
FORGE — architecture/backend/general engineering.
FRAME — frontend experience implementation.
PRISM — functional/quantitative QA.
LENS — rendered visual/responsive QA.
ATLAS — runtime/deployment reliability when relevant.
SENTINEL — independent final correctness/security gate.
ORION — orchestration and final synthesis.

Do not force every specialist into trivial work.

## Preferred DAG

AURORA + FORGE → FRAME → PRISM + LENS + ATLAS(if relevant) → remediation → PRISM/LENS regression → SENTINEL → ORION.

Review findings normally return to the appropriate implementer:
- visual/frontend → FRAME,
- product/design → AURORA + FRAME,
- engineering/backend → FORGE,
- deployment/runtime → ATLAS.

Reviewers should not silently become the final implementer.

## Persistent source

For real software builds prefer a durable project directory or Git/worktree workspace. Do not rely on scratch as the only durable source location.

## Visual gate

Successful build is insufficient. Important UI requires LENS rendered evidence across representative phone, tablet, desktop, wide/ultrawide layouts plus relevant states/interactions.

## Revision integrity

If source changes after successful test/review, invalidate affected previous PASS. Final verification must correspond to final source revision.

## Proactive improvement & Anti-AI-Slop Aesthetics

Treat user requirements as the minimum contract. Allow meaningful improvements inside intent/scope. Do not suppress expert initiative; do not permit unrelated scope creep.

When designing or rebuilding user interfaces:
- **Reject Generic "AI Slop":** Avoid default SaaS tropes (uniform soft pill shapes, muddy purple-to-indigo gradients, low-contrast typography, and timid layouts).
- **Commit to Distinct Aesthetic Directions:** Explicitly identify and execute clear visual styles (e.g. Minimalist Neo-Brutalism with hard offset shadows/solid bold borders, Linear/Raycast dark micro-terminals, Swiss monospaced high-density ledgers, or clean industrial utility).
- **Tactile Feedback & Numeric Weight:** Ensure interactive states provide physical-feeling click displacement and financial/metric data uses robust tabular monospace formatting.

## Final report

Separate what was implemented, functionally tested, visually verified, security verified, operationally verified, and what remains limited. Never collapse unverified claims into "production ready."
