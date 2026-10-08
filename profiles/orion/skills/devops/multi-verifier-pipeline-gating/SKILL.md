---
name: multi-verifier-pipeline-gating
description: Sync parallel verifiers and resolve split review verdicts.
version: 1.0.0
author: Hermes Fleet Architecture
platforms: [linux]
metadata:
  hermes:
    tags: [multi-agent, verification-gate, split-verdict, kanban-orchestration, quality-governance]
    category: devops
    requires_toolsets: [kanban, terminal]
---

# Multi-Verifier Pipeline Gating & Split Verdict Resolution

Operating standard for orchestrating parallel independent verifiers, preventing race conditions across validation gates, and resolving split verifier verdicts without stalling or skipping quality controls.

## When to Use

- When dispatching parallel verifiers (e.g., functional verification by PRISM, security audit by SENTINEL, visual QA by LENS) against an implementer's frozen commit SHA.
- When verifiers complete at different times (asymmetric completion) and one gate reports PASS while another is still running.
- When verifier verdicts split (e.g., functional passes `VERIFIED`, but security returns `REVISE` with P0/P1 defects).
- When verifier runs time out or exhaust retry budgets on long-running test suites.

## Core Procedures

### 1. Frozen Revision Binding
1. **Commit Freeze:** Every verification task must target an exact, immutable Git commit SHA.
2. **Read-Only Invariant:** Verifiers operate in strict read-only mode on application source code; they never mutate production logic or bypass tests.
3. **Report Artifact Binding:** Verification reports (`docs/*_VERIFICATION_REPORT.md`) must explicitly declare the target commit SHA and list individual check statuses.

### 2. Asymmetric Completion & Turn Yield
Parallel verifiers rarely finish at the same second:
1. **First Wake Arrival:** When the first verifier reports `VERIFIED`, inspect its report and confirm the verdict.
2. **Check Sibling Status:** Inspect the active sibling verifier task immediately (`kanban show <sibling_task_id>`).
3. **Anti-Premature Advancement Invariant:** NEVER unlock the next phase, create downstream implementation cards, or claim phase completion while any sibling verifier is still in flight.
4. **Yield Turn:** State the partial verification status to the user and immediately release the turn so the gateway can wake when the remaining verifier concludes.

### 3. Split Verdict Triage (VERIFIED vs REVISE)
When one verifier issues `VERIFIED` and a sibling issues `REVISE`:
1. **Preserve Validated Evidence:** Retain the passing verifier's results; do not discard them.
2. **Isolate Concrete Defect Ledger:** Extract the exact list of blocking defects (e.g., SEC-01..03, visual overflow, idempotency race) and acceptance criteria from the revising verifier.
3. **Dispatch Targeted Remediation:** Assign a remediation task back to the original implementer referencing ONLY the failing items and the original commit SHA.
4. **Lock Remediated SHA:** Once the implementer commits the fix, capture the new commit SHA.
5. **Targeted Re-Verification:** Dispatch a re-verification card specifically to the verifier that flagged the issue, bound to the new commit SHA. If the remediation modified shared contracts, re-run both verifiers.
6. **Unanimous Approval Required:** Advance to downstream stages only when both verifiers certify the active commit SHA.

### 4. Test Concurrency & Database Isolation
When multiple verifiers run functional and security suites simultaneously:
1. **Database Contention Guard:** If tests execute against a live PostgreSQL instance, verify whether tests perform destructive operations (e.g. `TRUNCATE`, dropping schemas, resetting migration tables).
2. **Isolation Mitigation:** Ensure parallel test runners run on distinct database names or use isolated schemas/transaction rollbacks to prevent false-positive concurrency failures.

### 5. Automated Timeout Notifications & Dispatcher Retry Handling
When long-running verifiers (e.g., executing comprehensive functional test suites, deep security leak harnesses, or Playwright audits) trigger automated timeout notifications (`timed out; dispatcher will retry`):
1. **Verify Active Progress Before Intervening:** Do not immediately spawn duplicate review tasks or conclude that the audit failed. Inspect worker execution logs via `hermes kanban log <task_id>` to check whether the worker was in the middle of executing a test runner or compiling.
2. **Preserve Commit Gating across Retries:** Verify that the retried worker continues execution on the exact frozen Git commit SHA rather than uncommitted working-tree modifications.
3. **Yield Turn for Active Retries:** If the worker is actively executing its retry attempt, yield the turn cleanly.

## Pitfalls

- **Premature Phase Advancement:** Unlocking Phase N+1 because PRISM passed while SENTINEL is still auditing leaves critical security vulnerabilities unaddressed in downstream code.
- **Implementer Self-Certification:** Accepting an implementer's claim that a fix worked without an independent verifier re-auditing the exact commit SHA violates separation of duties.
- **Task Duplication on Timeout Alerts:** Spawning duplicate cards when receiving `timed out; dispatcher will retry` creates conflicting review runs and database contention. Inspect `kanban log <task_id>` and let the dispatcher retry conclude.
- **Scratch Directory Vitest Inclusion Failures:** Verifiers creating probe tests in profile scratch directories (`/root/.hermes/profiles/<role>/cache/scratch/`) will hit test runner failures if running `vitest run <scratch_path>` against project configs that restrict `include` to `tests/**/*.test.ts`. Probes must be executed with `node ./node_modules/.bin/tsx <script>` or `--config <scratch_config>`.
