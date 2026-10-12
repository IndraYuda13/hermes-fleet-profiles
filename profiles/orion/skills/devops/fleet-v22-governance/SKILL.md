---
name: fleet-v22-governance
description: Fleet v3.2 Quality Governance Standard for multi-agent software engineering, visual QA, functional verification, independent review loops, revision integrity, disk guards, delegation controls, and release gates.
version: 3.2.1
author: Hermes Fleet Architecture
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [governance, quality, git-revision, defect-ledger, disk-guard, mcp-roles, delegation-control, fleet-v32]
    category: devops
    requires_toolsets: [kanban, terminal, file]
environments:
  - kanban
  - agent
---

# Fleet v3.2 Quality Governance Standard

*Architecture Version: Fleet v3.2 (Hermes Agent v0.20.2)*
*Policy Baseline: V2.2.1 Unified & Hardened*

Systemic operating rules for multi-agent software engineering, visual QA, functional verification, delegation controls, and fleet architecture integrity.

## Core Governance Invariants & Rules

### Rule 1: Revision Integrity Gate
- For software projects managed in Git, establish a final Git commit SHA after implementation/remediation.
- PRISM, LENS, SENTINEL, and ORION final synthesis MUST record the exact same Git commit SHA in their reports and metadata.
- Any source code change made after a PASS immediately invalidates every affected prior PASS and requires re-running verification against the new commit SHA.
- ORION must refuse `FINAL VERIFIED` or release sign-off when final-source revision and verification revisions differ (`stale_revision_pass_accepted = NO`).

### Rule 2: Defect Disposition Ledger & Interactive Mutation Verification
- Every P0/P1/P2 visual or functional finding must be recorded with explicit status: `RESOLVED` or `ACCEPTED`.
- If `ACCEPTED`, a clear rationale, impact assessment, and tradeoff analysis must be documented.
- Findings may NOT silently disappear or be labeled merely "ignored".
- P0/P1 defects may NEVER be accepted for final release unless the user explicitly authorizes an override.
- **Interactive Mutation Rule (LENS/PRISM):** Visual QA is forbidden from relying purely on static page load snapshots. QA workers MUST execute interactive mutations across every clickable control (theme toggles, currency switches, privacy masks, tabs, modals, transaction CRUD triggers) and assert computed CSS/DOM mutations (e.g. background-color RGB mutation, DOM node insertion/removal, class additions) before declaring PASS.
- **Framework Version Rule (FRAME/FORGE):** When upgrading or using modern frontend framework major versions (such as Tailwind CSS v4+), do not assume legacy selector behaviors (e.g., class-based `.dark` selectors). Explicit variants (e.g., `@custom-variant dark (&:where(.dark, .dark *));`) and computed CSS styles must be verified in the browser.
- **Anti-AI-Slop Visual Baseline (AURORA/FRAME):** Proactively eliminate generic SaaS patterns (uniform rounded pill bubbles, purple/violet neon gradients, weak low-contrast typography). Enforce strong aesthetic character (such as Minimalist Neo-Brutalism with high-contrast borders, solid offset shadows, tactile click feedback, and tabular monospace numbers) matching user preference.

### Rule 3: Disk & Artifact Guard
- Check root free disk space (`df -h /`) before spawning heavyweight browser QA or installing browser/runtime dependencies:
  - **≥8 GB:** Normal execution.
  - **5–8 GB:** Warning state. Avoid redundant browser/runtime installations.
  - **<5 GB:** Block new heavyweight browser installations (`playwright install`).
  - **<3 GB:** Block new heavyweight browser QA runs.
  - **<2 GB:** Block new Kanban worker dispatches.
- Browser caches, recordings, and temporary screenshot artifacts must be cleaned after visual QA where safely reconstructable.
- **NEVER** delete user project source files, credentials, databases, production Docker data, or unrelated services.

### Rule 4: Resource Ownership & Role-Scoped Capability Architecture
Maintain strict role-scoped capability assignment. Do not load heavy MCP servers or broad toolsets into unassigned profiles for convenience.
- **ORION (Chief of Staff):** Lightweight orchestrator. Strict zero-production-edit invariant (`orion_production_edits == 0`). Must NOT acquire Playwright, Puppeteer, Postman, Canva, Firecrawl, or broad coding toolsets. All code remediation is routed to specialists via Kanban.
- **Kanban Board Scoping Invariant:** Always explicitly pass `--board <slug>` on CLI or `board="<slug>"` in `kanban_*` tools (e.g. `kanban_comment`, `kanban_list`, `kanban_show`). When multi-board workflows are active, omitting the board falls back to default/env board and triggers `unknown task` failures.
- **LENS / FRAME:** Visual QA, Playwright browser automation, cross-browser rendering inspection, frontend engineering.
- **AURORA:** Product design, Canva/design tools, visual architecture, Design DNA & Contract.
- **FORGE:** Software engineering, GitHub MCP, Postman MCP, API integration, backend services.
- **RADAR:** AI & technology intelligence, Firecrawl web search/extract.
- **PRISM:** Quantitative data science, functional regression, benchmark methodology, analytics verification.
- **SENTINEL:** Security audit, threat modeling, risk review, vulnerability scan, final correctness gate.
- **ATLAS:** Infrastructure, DevOps, Linux, container reliability, deployment.
- **QUANT:** Market and quantitative trading research.
- **NEXUS:** Documentation, SOPs, personal operations, and administration.

### Rule 5: QA Side-Effect Boundary, Sandbox Isolation & Probe Safety
- **Strict Side-Effect Boundary:** During tasks classified as `READ-ONLY`, `TEST-ONLY`, or `ACCEPTANCE AUDIT`, QA workers (LENS, PRISM, Reviewers, SENTINEL) are strictly forbidden from creating persistent production records, accounts, financial transactions, or mutating live balances without explicit user authorization.
- **Control Classification Pre-Execution:** Every control must be classified before interaction:
  - `SAFE_READ_ONLY` / `SAFE_EPHEMERAL` → Runtime execution allowed.
  - `PERSISTENT_WRITE` / `AUTH_CREATION` / `FINANCIAL` / `DESTRUCTIVE` → Prohibited in production; must use isolated ephemeral fixture, mock sandbox, or transaction rollback.
- **Zero-Assumption on Non-GET HTTP Probes (Auditor Probe Safety):**
  - Never assume an HTTP `POST`, `PUT`, `PATCH`, or `DELETE` request is "read-only" or will safely fail harmlessly on a live production URL, even when testing with intentionally malformed, incomplete, or dummy payloads. Internal framework validation, database defaults, or upstream gateway SDKs can still generate database records or trigger live financial invoices (e.g. creating pending QRIS invoices upstream).
  - All exploratory fuzzing and vulnerability scanning on live endpoints MUST use strictly safe methods (`GET`, `HEAD`, `OPTIONS`) or provably non-existent synthetic IDs that short-circuit on read-only queries (e.g. year 2099 codes). Any mutating payload tests must run against an isolated replica DB or staging instance.
- **Inadvertent Mutation Protocol (Disclosure & Non-Intervention):**
  - If an audit probe accidentally creates a live production record:
    1. Immediately publish a formal disclosure (`DISCLOSURE_*.md`) documenting the exact request headers, payload, timestamp, and row delta.
    2. Measure financial invariants (wallet balances, ledger sums, external provider credits) against the frozen pre-audit backup anchor.
    3. **DO NOT** perform reactive live rollbacks or ad-hoc cancellation requests (such as calling payment cancellation APIs which trigger secondary upstream provider mutations). Allow self-expiring records to expire naturally and document expected state lifecycle drift in an Anchor Delta Log.
- **Mixed Evidence Hierarchy:** A skipped persistent control with suitable lower-level evidence (e.g. client validation assertion + mock integration test) is valid and preferred over unsafe production mutations.
- **Destructive Tool Verification Sandbox Invariant:** When an independent verifier (SENTINEL, PRISM) audits or proves a flaw/guard bypass in a dangerous tool (e.g. database restore, migration, data scrubber, service reconfig), the verifier MUST NOT execute active write flags (`--execute`, `--restore`, `--drop`, `--force`) against any shared, staging, or production target to demonstrate the flaw. Exploit proofs for dangerous tooling must run strictly against isolated, throwaway target instances (e.g. a dedicated disposable database on a temporary socket or ephemeral port). Passing mutating flags against shared targets to prove a guard bypass breaches the QA side-effect boundary.
- **Adversarial Gate (SENTINEL):** SENTINEL must audit for `P0/P1 QA_UNAUTHORIZED_SIDE_EFFECT` whenever reviewer actions introduce unapproved production state mutations.

### Rule 6: Independent Review DAG & Mandatory Remediation Routing
- **Implementer != Reviewer Invariant:** An implementer profile must never approve its own work.
  - FRAME UI implementation → PRISM (functional) + LENS (visual/interaction QA)
  - FORGE backend/services → PRISM (functional/data) + SENTINEL (security review)
  - ATLAS infra/deployment → SENTINEL (security) + PRISM (operational check)
- **Mandatory Remediation Loop:** A verification defect or failing test NEVER authorizes reviewers to edit production code. Remediation must be assigned back to the implementer via Kanban.
- **Native Review Lane:** `kanban.review_dispatch: false` is enforced on ORION to prevent same-card self-review loops; all reviews are dispatched as distinct parent-gated child cards.

### Rule 7: Delegation Control Protocol (Hermes v0.20.2)
Specialists permitted to use subagent delegation (`delegate_task`) must follow strict control procedures:
1. **Smallest Sufficient Fan-out:** Spawn the smallest sufficient child set with non-overlapping scopes.
2. **Structured Contracts:** Enforce `output_schema` for all machine-consumed child outputs to validate data contracts.
3. **Live Orchestration:** Inspect live subagents via `action='list'`, steer active children via `action='steer'`, and terminate redundant or drifted workers early via `action='stop'`.
4. **Truncation & Max-Iterations Guard:** A truncated or iteration-capped child result is incomplete evidence and must never be counted as PASS.
5. **Worktree Isolation:** Coding subagents (FRAME/FORGE) must execute inside isolated Git worktrees (`worktree_isolation: true`) to prevent branch collision.

### Rule 8: Fleet Pre-Flight & End-to-End Readiness Verification
- **Multi-Layer Readiness Probe:** When mobilizing the fleet prior to high-stakes missions or upon operational readiness requests, verify peer agents across three distinct layers:
  1. *Catalog Discovery:* Query `a2a_list` to enumerate configured peer endpoints and ports.
  2. *Daemon Liveness:* Probe HTTP endpoints (`curl -s http://127.0.0.1:<port>/.well-known/agent.json`) to confirm local server processes are listening.
  3. *Active E2E Handshake:* Issue a single-turn `a2a_call` to each required specialist with a lightweight echo task (e.g. prompt for name, ready status, and core specialty).
- **Pitfall — Static HTTP is Not Execution Readiness:** A listening port or HTTP 200 response on `.well-known/agent.json` only proves the HTTP daemon is up; it fails to catch exhausted model quotas, rate-limiting, corrupted context databases, or crashed inference workers. Only an end-to-end task completion (`status='completed'`) confirms the peer's LLM pipeline is actually capable of processing work.
- **Batch Independent Probes:** Issue peer ping `a2a_call` requests concurrently across parallel tool calls or small batches with tight per-call expectations rather than serial blocking, preventing a single unresponsive peer from halting the entire pre-flight routine.
- **Readiness Matrix Synthesis:** Synthesize pre-flight results into an explicit status matrix (Role, Live Status, Verified Specialty, Infrastructure State) before accepting or dispatching complex multi-agent missions.

## Verification Checklist

- [ ] Exact Git commit SHA verified across PRISM, LENS, SENTINEL, and ORION.
- [ ] Defect Disposition Ledger complete (0 unclassified P0/P1/P2 items).
- [ ] QA Side-Effect Boundary verified: 0 unauthorized persistent records created by reviewers in production.
- [ ] Zero non-GET live probes without isolated sandbox or guaranteed read-only short-circuit.
- [ ] Root free disk space checked before browser runs; temp artifacts cleaned post-QA.
- [ ] Role-scoped capability architecture respected without capability creep on ORION.
- [ ] Independent reviewer invariant verified (`implementer != reviewer`).
- [ ] Delegation control protocol enforced on subagents with schema validation and truncation guards.
- [ ] Worktree isolation active and verified on parallel coding branches.
- [ ] Fleet pre-flight verification: active E2E handshake confirmed on all required peer agents before multi-agent DAG dispatch.
