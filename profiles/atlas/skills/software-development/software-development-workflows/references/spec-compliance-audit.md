# Read-only specification compliance audit

Use this for phase-gate, architecture, paper-only, or contract compliance reviews against a governing specification such as `AGENTS.md`.

## Method

1. **Establish authority and scope**
   - Read the governing document before the candidate artifacts.
   - Extract binding language (`MUST`, `MUST NOT`, `REQUIRED`, `BLOCK`, acceptance gates) and phase-specific deliverables.
   - Confirm repository state and review boundaries without changing files.

2. **Build a requirement-to-evidence matrix**
   - For every phase requirement, record: source section/line, expected artifact, claimed status, concrete evidence, and verdict.
   - Treat host versions, prose assertions, and checkbox state as different evidence types; one does not substitute for another.
   - A dependency decision is incomplete until every required extension point is evidenced, especially critical routing or trust-boundary paths.

3. **Audit decision provenance**
   - Accepted ADRs need observable support: pinned upstream revision, exact file/API/tool surface, probe command or reproducible procedure, and result.
   - “Verified” or “gate passed” is unsupported when the journal contains only a prose description or pseudo-command. Require an exact command/script and fresh output or downgrade the claim.
   - Distinguish evidence observed during this review from historical claims that could not be independently reproduced.

4. **Reconcile cross-document contracts**
   - Compare the master spec, ADRs, architecture diagrams, implementation plan, build log, and configuration defaults.
   - Search for stage-order conflicts, role input/output mismatches, profile-versus-quorum conflicts, capabilities named in the spec but absent from the plan, and exceptions that silently weaken a MUST.
   - An ADR does not supersede the governing spec unless authority to do so is explicit. If its resolution drops one side of a contradiction, report the contradiction as unresolved.

5. **Check implementation-plan actionability**
   - Distinguish an executable plan from a phase roadmap. Require exact create/modify/test paths, small independently verifiable tasks, dependency order, concrete acceptance oracles, exact RED/GREEN commands with expected outcomes, and explicit checkpoint boundaries.
   - Flag one-checkbox epics such as “implement all adapters/skills” even when the overall phase order is sensible.

6. **Check hard boundaries and negative paths**
   - Trace the full control path to every mutation: deterministic checks, approval, idempotency, isolation, and fail-closed behavior.
   - Draw rejection, timeout, cancellation, approval-expiry, disabled-execution, and uncertain-result branches. A consistent happy-path diagram can still leave non-execution states without a terminal report path.
   - Distinguish an optional operation from mandatory authorization. For example, execution may be optional while approval remains mandatory whenever mutation occurs.
   - For paper-only systems, inspect both presence of forbidden live-money capability and omission of required simulator capability. “No live code found” does not prove the complete paper path exists.

7. **Check secrets with bounded claims**
   - Check `.gitignore`, tracked and untracked files, secret patterns, runtime databases, keys, logs, and generated artifacts. Manually classify placeholders, example local credentials, hashes, and real secrets.
   - Phrase conclusions within the observed scope: “No secret material was found in the reviewed repository snapshot.” Repository inspection cannot prove that a key was never printed historically or absent from unrelated external logs.
   - If no dedicated scanner is available, disclose the regex/manual method rather than presenting equivalent assurance.

8. **Re-anchor and report findings-first**
   - Record branch, `HEAD`, working-tree status, and reviewed artifact hashes at the start. Re-check them before reporting because authors or parallel workers may update files during the audit; classify findings against the final snapshot rather than stale lines.
   - Put blocking findings first, ordered by severity.
   - Give concrete `path`, section, and line range where available.
   - For each finding state requirement, observed gap/contradiction, impact on the gate, and concrete repair.
   - Then list non-blocking risks, positive controls, evidence commands run, snapshot identity, and explicit read-only/no-change confirmation.

## Common mistakes

- Trusting checked boxes or a build-log PASS string without the actual verification command.
- Treating a local toolchain version as proof of an upstream minimum-version audit.
- Verifying an endpoint independently but not proving the selected runtime dependency can route through it.
- Calling a contradiction resolved when the chosen design still violates one binding clause.
- Auditing only forbidden behavior and missing required capabilities omitted from the implementation plan.
- Reporting untracked phase artifacts as a defect when the phase is explicitly pre-commit; report repository state accurately instead.
