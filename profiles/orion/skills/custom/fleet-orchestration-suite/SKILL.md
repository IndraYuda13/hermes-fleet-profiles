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

## 5. UI Design V4 Lifecycle & Verification Hardening
For UI Design Depth 2 and Depth 3 missions, ORION enforces the full 14-stage V4 pipeline, Creator != Certifier boundary, bounded exploration budget, and dual independent release veto.
See complete procedural guide and invariant rules:
`skill_view("fleet-orchestration-suite", "references/ui-v4-orchestration-and-verification-governance.md")`

## 6. Asynchronous Dual-Verifier Arrival & Release State Machine
- **Asynchronous Verifier Arrival Handling:** When independent verifiers run in parallel (e.g. LENS visual QA and PRISM functional/a11y QA), one verifier will inevitably finish and report first via A2A or Kanban.
  1. *Early Arrival Acknowledgment:* Acknowledge receipt, inspect on-disk artifacts (`LENS_REVIEW_REPORT.json` or PRISM test logs), and approve promotion to `BEST_BUILD_SHA` for that verification dimension.
  2. *Strict In-Flight Guard:* Record `INTERNAL_VISUAL_GATE = PASS` (or functional pass), but keep `MISSION_RELEASE_STATE = IN_VERIFICATION` while sibling verifier tasks remain active (`status: running`). Never declare mission release or notify the human owner until ALL required verifier tasks reach terminal states.
  3. *Owner Acceptance Reservation:* `INTERNAL_RELEASE_GATE = PASS` marks internal verification closure only. `OWNER_VISUAL_ACCEPTANCE` and `OWNER_ACCEPTANCE` MUST remain `PENDING`. Internal agents (ORION, LENS, PRISM, FRAME) are strictly forbidden from setting owner acceptance to `PASS`; only the human owner can transition it.
  4. *Unified Meta-Release Synthesis:* Once all verifiers complete with PASS, ORION synthesizes the unified release decision record, bundles all visual and functional evidence, and presents the deliverable with `MISSION_RELEASE_STATE = AWAITING_OWNER`.

## 7. Declarative Fleet Upgrades, Gateway Lifecycle & Terminal Safety
- **HERMES_HOME Subprocess Scope Trap:** When running deployment or bootstrap scripts from inside an active profile session (such as `orion`), `$HERMES_HOME` is exported in the environment as `/root/.hermes/profiles/<profile_name>`. Scripts defaulting to `${HERMES_HOME:-$HOME/.hermes}` will mistakenly target the subprofile directory, polluting it with nested `profiles/` directories. Always explicitly prepend `HERMES_HOME="${HOME}/.hermes"` when invoking root fleet scripts or bootstrap tools from an active agent session.
- **Terminal Guard Lifecycle Choke Point & Sibling Gateway Restarts:** Running `systemctl --user restart hermes-gateway-<profile>.service` directly is blocked by Hermes's terminal lifecycle guard (`contains_gateway_lifecycle_command`), which matches `hermes-gateway` and `systemctl.*restart`. To restart sibling gateways safely without triggering the terminal guard, use the profile-flag CLI form: `hermes -p <sibling_profile> gateway restart`. The lifecycle guard explicitly permits restarting sibling profiles (`_named_profile_is_current` check allows sibling operations while blocking restarts of the executing profile). Never forcefully restart one's own current gateway profile mid-turn, as SIGTERM terminates the active child process before delivering the response.
- **Declarative Git Pulls vs Runtime Secret Preservation:** Git pulls from declarative configuration repositories (`hermes-fleet-profiles`) contain sanitized placeholders (`${MONETAG_API_TOKEN}`). Never use `--replace-config` blindly on live environments. Deploy declarative assets (`SOUL.md`, `profile.yaml`, custom/global skills) first, then surgically update targeted non-secret delta keys (e.g. `skills.disabled`) while preserving secrets byte-for-byte.
- **Fleet Model Re-Routing & Verification Invariant:** When changing default inference models across fleet profiles:
  1. *Verify Active Endpoints:* Query the local router/gateway first (`curl -s http://localhost:20128/v1/models | jq -r '.data[].id'`) to verify exact upstream model IDs (`gpt-sol`, `gpt-terra`, `ag-opus-pool`) before applying.
  2. *Surgical Per-Profile Update:* Use `hermes -p <profile> config set model.default <model_id>` to ensure atomic YAML updates without formatting corruption.
  3. *Audit State Before Restart:* Run `hermes profile list` to verify that each profile's model column matches the intended role-model topology.
  4. *Gateway Restart Guard:* Never attempt `hermes gateway restart --all` or restart the executing profile from within an active session—it is blocked fail-closed by Hermes terminal guards. Either delegate the restart to the human operator outside the gateway or restart sibling profiles individually via `hermes -p <sibling> gateway restart`.

