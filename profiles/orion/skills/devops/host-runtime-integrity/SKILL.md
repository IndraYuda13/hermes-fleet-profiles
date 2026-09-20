---
name: host-runtime-integrity
description: Protect host agent runtime from unauthorized edits.
version: 1.1.0
author: Hermes Fleet Architecture
license: MIT
metadata:
  hermes:
    category: devops
    requires_toolsets: [terminal, file]
    tags: [runtime, host, integrity, governance, source-code, framework]
---

# Host Runtime Integrity & Framework Protection

Operating rules for preserving host agent runtime code, distinguishing framework repositories from user fleet/project checkouts, safely handling runtime or toolset anomalies, and executing verified framework rollbacks.

## Core Rules & Invariants

### 1. Zero Framework Source Mutation
- Multi-agent workers and orchestrators must NEVER edit, patch, or commit to the host agent installation or source code (e.g. `/usr/local/lib/hermes-agent`, system Python site-packages, or agent CLI internals) unless the user gives explicit, unambiguous authorization for that exact framework source modification.
- **Why (The Mechanism & Pitfall):** The host agent runtime is shared infrastructure executed by long-running systemd gateway daemons across all fleet profiles. Modifying it locally introduces massive git divergence from upstream (e.g. hundreds or thousands of commits behind), destabilizes background daemons, breaks update and rollback mechanisms, and conflates user application/fleet configuration with agent engine development.

### 2. Strict Repository Boundary Disambiguation
Always verify the identity and purpose of local git repositories before inspecting or committing:
- **Framework Source Repo:** `/usr/local/lib/hermes-agent` (remote: `NousResearch/hermes-agent`). Read-only for fleet workers; never mutate or push during user or fleet operations.
- **User Fleet Profiles Repo:** `/root/projects/hermes-fleet-profiles` (remote: `IndraYuda13/hermes-fleet-profiles`). Backs up fleet configurations, skills, and profile definitions (`/root/.hermes/profiles/*`).
- **User Project Repositories:** Standalone application workspaces (e.g. `/root/projects/...`, `/root/cust/...`).
- **Rule:** Never assume a repository in the filesystem belongs to the user without checking `git remote -v`. Never attempt to push framework source changes upstream during user profile tasks.

### 3. Handling Dispatcher, Skill, and Toolset Failures
When a Kanban worker or gateway fails at bootstrap due to unknown skills, missing toolsets, or dispatcher constraints:
- **Immutable Skill Pin Trap:** Task attributes (like `skills: [...]`) are immutable in the Kanban database. Retrying an unrunnable task will fail indefinitely.
- **The Correct Remediation:**
  1. Do NOT hack or patch framework files (`kanban_db_dispatch.py`, `kanban_ops.py`, etc.).
  2. For skill-pin failures: cancel or comment on the failed task, then spawn a replacement task with sanitized `skills: []` so the worker uses its profile defaults.
  3. For profile-level toolset mismatches: resolve within the profile configuration (`~/.hermes/profiles/<profile>/config.yaml`), or update the task's assignee.
  4. If a genuine framework limitation prevents progress and cannot be addressed via configuration, mark the task as blocked with `kind="needs_input"` and explain the limitation to the user.

### 4. Emergency Framework Rollback & Restoration Protocol
If an unauthorized local commit or dirty state is accidentally introduced to the framework repository:
1. **Preflight Guard**: Verify current HEAD matches the exact unauthorized commit SHA and ensure no unstaged/untracked collisions exist.
2. **Sole Authorized Revert**: Execute a clean, single-purpose revert (`git revert --no-edit <unauthorized_sha>`) creating a local recovery commit. Never push this revert upstream.
3. **Byte-Identical Tree Equivalence**: Verify `git diff --exit-code <pre_patch_baseline_sha> HEAD` produces zero diff. The tracked working tree must match baseline byte-for-byte.
4. **Targeted Gateway Reload Only**: Identify the specific service hosting the affected daemon (e.g., `systemctl --user restart hermes-gateway-groupbot.service` for the embedded dispatcher). Verify new PID, active status, and lock acquisition (`/root/.hermes/kanban/.dispatcher.lock`). Do NOT restart untouched peer gateways (e.g., `hermes-gateway-testing.service`).

### 5. Independent Verification of Recovery & The Absent Manifest Trap
When an independent verifier (e.g. PRISM) inspects a completed rollback:
- **The Absent Manifest Trap**: Demanding an exact path→SHA-256 manifest comparison for untracked files or configs when no immutable preflight manifest was captured prior to the rollback. Stalling verification over retrospective baseline absence blocks valid recovery.
- **Verification Protocol**:
  1. Verify all falsifiable, inspectable state: git HEAD, tree equivalence vs baseline (`diff --quiet`), absence in upstream remote, gateway unit status/PID, and lock ownership.
  2. For preservation claims lacking a preflight snapshot: mark preservation comparison as `UNVERIFIED` (explicitly citing absent preflight manifest) rather than `BLOCKED` or `FAILED`.
  3. Never fabricate retroactive comparison data, and never mutate source or restart services solely to manufacture retrospective verification evidence.

## Verification Checklist

- [ ] Repository identity verified (`git remote -v`) before touching git state.
- [ ] Host framework code (`/usr/local/lib/hermes-agent`) remains completely untouched (zero diff vs baseline).
- [ ] Dispatcher or bootstrap errors resolved via task parameters or profile configs, not framework source edits.
- [ ] No unauthorized upstream push attempted against framework remotes.
- [ ] Rollback verified by byte-identical git diff against pre-patch baseline.
- [ ] Retrospective preservation checks without a pre-existing manifest marked `UNVERIFIED`, not blocked.
