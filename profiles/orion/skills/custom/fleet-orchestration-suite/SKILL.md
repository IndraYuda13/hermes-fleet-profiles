---
name: fleet-orchestration-suite
description: Use when orchestrating multi-agent fleet pipelines & QA.
---

# Fleet Multi-Agent Orchestration, Governance & Defect Management

Comprehensive standard operating procedure for orchestrating specialized autonomous AI agent fleets (ORION, AURORA, FRAME, LENS, FORGE, ATLAS, PRISM, SENTINEL) across A2A pipelines, Kanban DAG dispatches, Impeccable design overhauls, and runtime defect rembukan.

## 1. Fleet Role Separation & Impeccable Ownership Matrix
| Fleet Role | Ownership Boundary | Impeccable Tools & Primary Deliverables | Execution Invariant |
|---|---|---|---|
| **ORION** | Chief of Staff, decomposition, governance, verdict synthesis | `routing`, `shape`, `craft-floor` review; Mission Contracts, Release Records | `orion_production_edits == 0` |
| **AURORA** | Product design authority, UI tokens, OKLCH color palettes | `init`, `concept-seed`, `palette`, `typeset`; `DESIGN.md`, `PRODUCT.md` | Design specs only; never implements code |
| **FRAME** | Frontend engineering, state machines, API integration | `typeset`, `layout`, `adapt`, `polish`; `styles.css`, `app.js`, HTML | Implements code; never self-certifies QA |
| **LENS** | Rendered visual/interaction QA & geometry verification | `audit`, `critique`, `contrast-rhythm`; `VISUAL_QA_REPORT.md`, viewport audits | Audits DOM; never edits production source |
| **FORGE** | Backend engineering, core business logic, worker daemons | APIs, SQLite queries, automation scripts | Backends & state machines |
| **ATLAS** | SRE, deployment, rollback anchors, process lifecycle | Systemd units, cgroup guards, rollback scripts | Infra stability & git anchors |
| **PRISM** | Functional QA, invariant assertions, test suites | Pytest suites, Playwright E2E tests | Strict test coverage; 0 false claims |

### Impeccable UI Invariants across Fleet
1. **Tabular Numeric Rule:** Always enforce `font-variant-numeric: tabular-nums` on prices, timers, nominals, and counters to prevent layout jitter during real-time polling.
2. **Glassmorphic GPU Isolation:** Pair `backdrop-filter: blur(20px)` with `contain: layout paint` and `transform: translateZ(0)` on navigation bars to prevent mobile compositing lag.
3. **Mobile Touch Safety Floor:** Interactive elements, buttons, category tiles, and form inputs must enforce a minimum 44×44px touch target geometry on mobile viewports (<=768px).
4. **Zero Horizontal Overflow:** Enforce `max-width: 100vw; overflow-x: hidden;` on body/root and verify across canonical viewports (320px, 360px, 390px, 768px, 1024px, 1440px).

## 2. A2A Communication & Timeout Management
- **Dual-Timeout Architecture:** Outbound client timeout in `config.yaml` (`a2a_agents.<peer>.timeout`) must strictly synchronize with inbound gateway deadline in `.env` (`A2A_REPLY_TIMEOUT`). Target: LENS/PRISM/SENTINEL/ORION: 1800s; FORGE/FRAME/AURORA: 1200s; ATLAS/RADAR/QUANT: 900s.
- **Progressive Decomposition:** Break large tasks into sequential multi-turn steps using `context_id` continuation (<300 words instruction per turn).
- **Concise Retry & Mechanical Fallback:** If a specialist times out, dispatch a concise 3-bullet retry. Split mechanical work (screenshot capture via FORGE) from judgment (visual audit via LENS).
- **Two-Way A2A Reverse Smoke Test Invariant:** Never assume bidirectional connectivity from outbound pings alone; verify the reverse direction (e.g. LENS -> ORION) using direct A2A JSON-RPC `SendMessage` calls.
- **Supervised Gateway Self-Restart Invariant:** Running agents are blocked by terminal guards from restarting their own gateway service directly. Request graceful restart via control socket or have the operator trigger it.
- **Evidence Manifest Git Revision Strategy:** Manifests committed inside git can NEVER contain their own commit SHA (avalanche effect). FRAME commits code (implementation SHA); all manifests reference that SHA; evidence artifacts are committed in a separate evidence commit.
- **Serial Incremental SDLC Invariant:** When mandated to work step-by-step ("1 per 1 dikerjakan, di-test, di-verifikasi"), tag initial state (`vX-baseline`), decompose into separate Kanban cycles (FORGE/FRAME -> PRISM/ATLAS -> commit/tag), and never batch multiple improvements into a single monolithic commit.
- **Remote MCP & Ad Monetization Engine:** See `references/ad-network-and-mcp-monetag.md` for OAuth 2.1 PKCE flow, Monetag MCP setup, and Service Worker push ad integration runbooks.

## 3. Defect Remediation Flow (Collaborative Rembukan)
- **Zero-Solo Invariant:** When runtime defects or upstream policy limits occur, ORION must never resolve them alone.
  1. *Discover & Isolate:* Trace logs and pin failure mechanisms.
  2. *Fleet Briefing:* Broadcast structured problem briefing via `a2a_orchestrate(capability="*")`.
  3. *Kanban DAG Dispatch:* Create discrete cards for logic (FORGE), UI (FRAME), infra (ATLAS), and QA (PRISM/LENS).
  4. *Independent Verification:* Implementer submits evidence; verifier confirms invariant pass before closure.
- **Kanban Task Creation & CLI Fallback:** For reading, commenting, and updating tasks, use native `kanban_show`, `kanban_comment`, and `kanban_list`. For task creation: if the native `kanban_create` tool encounters parameter signature mismatches (e.g. `missing required positional argument: 'title'`), use the deterministic Hermes CLI directly:
  `/usr/local/lib/hermes-agent/venv/bin/hermes kanban create --tenant "<TENANT>" --assignee "<ASSIGNEE>" --priority <PRIORITY> [--parent "<PARENT_ID>"] --workspace "dir:<PATH>" --body "<BODY>" --json "<TITLE>"`
  Always include `--json` for structured JSON output and verifiable task ID parsing.
- **Strict Anti-Polling Invariant & Native Event-Driven Session Wake:**
  - *Zero Busy-Wait Rule:* ORION must NEVER run sleep-and-check polling loops in terminal (`sleep 30` -> `kanban_show` -> `sleep 30`, or bash `while` loops) while awaiting background worker completion. Polling is forbidden: it wastes tool calls, burns foreground timeouts (600s), blocks user interaction, and violates the reactive gateway architecture.
  - *Hermes Core Native Wake:* Hermes Agent core natively handles session wake (`gateway/wake.py` and `delivery_mode="notify+wake"`). When `kanban_create` is called from a gateway session, it auto-subscribes the orchestrator with `notify+wake`.
  - *Mandatory Turn Release:* After dispatching Kanban tasks (and linking dependencies), ORION MUST report the dispatch status clearly and conclude the turn immediately. Do not hang the session waiting. The live gateway will natively wake ORION's session the exact second the worker reaches a terminal event (`completed`, `review_requested`, or `blocked`), injecting the event payload into the conversation turn.

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

## 8. Bi-Directional Fleet Profile Synchronization & Remote Backup (hermes-fleet-profiles)
When persisting live fleet policy, SOUL.md updates, custom skills, or model changes back to the version-controlled fleet repository (`/root/projects/hermes-fleet-profiles` -> `IndraYuda13/hermes-fleet-profiles.git`):
1. **Model & Role Topology Alignment:**
   - The validation engine (`scripts/validate_fleet.py`) enforces that `profiles/<name>/config.yaml` model defaults match `governance/roles.yaml`.
   - If profile models change (e.g. migrating Sol/Terra/Opus allocations), update `governance/roles.yaml` to match before running validation.
2. **Declarative Synchronization Execution:**
   - Always run with root Hermes home: `HERMES_HOME=/root/.hermes bash scripts/sync.sh` (dry run inspection) followed by `HERMES_HOME=/root/.hermes bash scripts/sync.sh --apply`.
   - `sync.sh --apply` automatically stages declarative changes into `profiles/` and `global/skills/`, creating an immutable timestamped snapshot in `/root/projects/hermes-fleet-backups/YYYYMMDDTHHMMSSZ`.
3. **Fleet Policy Validation Gate:**
   - Execute `python3 scripts/validate_fleet.py --repo-root /root/projects/hermes-fleet-profiles`.
   - All role toolsets, model parity checks, and SOUL invariants must return `Fleet policy: PASS`.
4. Git Commit & Remote Push:
   - Check `git status`, add all synced declarative updates, author a descriptive commit, and push upstream to `origin main`.
   - Ensure user project working branches (e.g. `digiflazz-topup-bot`) are also pushed to their respective remotes.

## 9. Full-Stack Fleet Bootstrapping Pipeline (PRD to Production Release)
When bootstrapping a greenfield full-stack product from a formal PRD:
1. **Workspace & Baseline Ratification:**
   - Initialize `/root/projects/<app_name>` git repository.
   - Commit the ratified PRD to `docs/PRD.md` as the inviolable baseline before authoring code.
2. **Canonical 6-Layer Dependency DAG:**
   - **Layer 1 (Parallel Architecture & Tokens, Priority 100):**
     - `AURORA`: Visual Design System, Design Tokens, Editorial Style, Anti-AI Slop UI contract (`docs/DESIGN_SYSTEM.md`).
     - `FORGE`: PostgreSQL schema (Drizzle ORM), atomic inventory reservation, immutable wallet ledger, payment gateway client & background worker sweeps.
   - **Layer 2 (Frontend Implementation, Priority 90):**
     - `FRAME`: Storefront, bottom-sheet cart, dynamic input view, QRIS payment screen with 1-tap save, customer dashboard, admin portal. Parents: `AURORA` + `FORGE`.
   - **Layer 3 (Runtime & Infrastructure, Priority 80):**
     - `ATLAS`: DB provisioning, background worker daemon (systemd), ingress reverse proxy (Nginx / Cloudflare Tunnel) with SSL/TLS, health check. Parent: `FRAME`.
   - **Layer 4 (Independent Dual-QA Gate, Priority 70):**
     - `PRISM`: Concurrency race testing (anti-overselling), webhook idempotency, late-payment ledger reconciliation, wallet boundary checks. Parent: `ATLAS`.
     - `LENS`: Rendered visual QA across 360px/390px/412px viewports, anti-slop compliance, 0px horizontal overflow, touch target geometry (>=44px). Parent: `ATLAS`.
   - **Layer 5 (Security Audit, Priority 65):**
     - `SENTINEL`: RBAC boundary verification (Owner vs Admin/Support financial mutations), IDOR on invoice attachments, secret sanitization. Parents: `PRISM` + `LENS`.
   - **Layer 6 (Production Release & Synthesis, Priority 50):**
     - `ORION`: Verification synthesis, Definition of Done compliance audit, operational handoff. Parent: `SENTINEL`.
3. **Concurrency Sequence Invariant (Postgres Advisory Locks):**
   - In high-concurrency checkout races, autoincrement sequence counters or non-locked queries for human-readable order/invoice numbers (e.g. `ORD-YYYYMMDD-XXXX`) collide or abort under row contention.
   - Serialize sequence generation inside transactions using PostgreSQL transaction-scoped advisory locks (`SELECT pg_advisory_xact_lock(hashtext('order_seq_lock'))`) so concurrent checkouts serialize cleanly without deadlocks or sequence gaps.
4. **Defect Disposition Ledger & Conditional Staged Release:**
   - When independent verifiers (SENTINEL, LENS) surface material P0/P1 defects (e.g. missing session auth on admin APIs, attachment BOLA/IDOR, WCAG contrast violations) alongside verified core business logic:
     - Do not declare unconditional production release.
     - Do not halt the entire project if public read-only discovery is functional and secure.
     - Author an explicit **Defect Disposition Ledger** mapping each defect to its owning specialist (`FORGE` for security/API, `FRAME` for UI/WCAG), severity (`P0/P1/P2`), exact reproduction tests, and target files.
     - Issue a **Conditional Staged Release (Restricted Beta)**: public catalog/browsing approved on live ingress, while checkout, payment processing, and admin mutations remain gated until the remediation sprint completes.

