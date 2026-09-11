---
name: fleet-orchestration-suite
description: Use when orchestrating multi-agent fleet pipelines & QA.
---

# Fleet Multi-Agent Orchestration, Governance & Defect Management

Comprehensive standard operating procedure for orchestrating specialized autonomous AI agent fleets (ORION, AURORA, FRAME, LENS, FORGE, ATLAS, PRISM, SENTINEL) across A2A pipelines, Kanban DAG dispatches, Impeccable design overhauls, and runtime defect rembukan.

## 1. Fleet Role Separation & Ownership Matrix
| Fleet Role | Ownership Boundary | Primary Deliverables | Execution Invariant |
|---|---|---|---|
| **ORION** | Chief of Staff, decomposition, governance, verdict synthesis | Mission Contracts, Release Decision Records | `orion_production_edits == 0` |
| **AURORA** | Product design authority, UI tokens, OKLCH color palettes | `DESIGN.md`, `DESIGN_DNA.md`, `PRODUCT.md` | Design specs only; never implements code |
| **FRAME** | Frontend engineering, state machines, API integration | `styles.css`, `app.js`, HTML markup | Implements code; never self-certifies QA |
| **LENS** | Rendered visual/interaction QA & geometry verification | `VISUAL_QA_REPORT.md`, multi-viewport audits | Audits DOM; never edits production source |
| **FORGE** | Backend engineering, core business logic, worker daemons | APIs, SQLite queries, automation scripts | Backends & state machines |
| **ATLAS** | SRE, deployment, rollback anchors, process lifecycle | Systemd units, cgroup guards, rollback scripts | Infra stability & git anchors |
| **PRISM** | Functional QA, invariant assertions, test suites | Pytest suites, Playwright E2E tests | Strict test coverage; 0 false claims |

## 2. A2A Communication & Timeout Management
- **Dual-Timeout Architecture:** Outbound client timeout in `config.yaml` (`a2a_agents.<peer>.timeout`) must strictly synchronize with inbound gateway deadline in `.env` (`A2A_REPLY_TIMEOUT`). Target: LENS/PRISM/SENTINEL/ORION: 1800s; FORGE/FRAME/AURORA: 1200s; ATLAS/RADAR/QUANT: 900s.
- **Progressive Decomposition:** Break large tasks into sequential multi-turn steps using `context_id` continuation (<300 words instruction per turn).
- **Concise Retry & Mechanical Fallback:** If a specialist times out, dispatch a concise 3-bullet retry. Split mechanical work (screenshot capture via FORGE) from judgment (visual audit via LENS).

## 3. Defect Remediation Flow (Collaborative Rembukan)
- **Zero-Solo Invariant:** When runtime defects or upstream policy limits occur, ORION must never resolve them alone.
  1. *Discover & Isolate:* Trace logs and pin failure mechanisms.
  2. *Fleet Briefing:* Broadcast structured problem briefing via `a2a_orchestrate(capability="*")`.
  3. *Kanban DAG Dispatch:* Create discrete cards for logic (FORGE), UI (FRAME), infra (ATLAS), and QA (PRISM/LENS).
  4. *Independent Verification:* Implementer submits evidence; verifier confirms invariant pass before closure.
- **Native Kanban Toolset Invariant:** Always call native `kanban_*` tools directly against SQLite DB (`~/.hermes/kanban.db`) rather than running shell CLI subprocesses that suffer quote corruption.

## 4. Production UI Overhaul Governance & Rollback Anchors
- **Dynamic Git Anchors:** Before modifying production source, record exact branch (`git symbolic-ref --short HEAD`) and SHA (`git rev-parse HEAD`), create a dedicated feature branch, and author an automated 1-click rollback script (`rollback_to_vX_stable.sh`).
- **Feature-Level Rollback Verification:** Rollback verification must confirm feature signatures (canvas, WebGL, scripts) in a headless browser, not merely HTTP 200 or title tags.
- **Release Gating:** Two independent verification passes (PRISM functional + LENS visual) required before ORION presents deliverables for human review.
