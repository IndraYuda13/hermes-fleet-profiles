# Upstream Runtime Contract Audit

Use this procedure when auditing a third-party repository for integration without modifying the consuming project.

## Scope and evidence discipline

1. Record the upstream remote, default branch, full commit SHA, commit date, nearest tag, and package-declared version. Treat the SHA—not a release label—as the audited identity.
2. Clone into a dedicated audit directory outside the target project. Before and after the audit, record a target-project sentinel such as a checksum plus size/mtime for a known file. Also verify the audit clone is clean.
3. Cite concrete `path:line-range` evidence for every contract claim. Compare prose docs, package metadata, registry manifests, and executable registration; report mismatches instead of choosing whichever is convenient.

## Installation and runtime validation

1. Read build metadata and entry points first: Python/runtime range, direct and optional dependencies, console scripts, environment variables, and packaging include/exclude rules.
2. Test a fresh install from an isolated copy or worktree, not from the consumer environment. Let the resolver choose current allowed versions once; this detects missing upper bounds and stale imports.
3. If the unconstrained install fails, identify the incompatible dependency boundary and retry with a known-compatible version only to distinguish source correctness from dependency-range correctness. Report both outcomes; do not describe the pin as proof that the stock install works.
4. Exercise imports, entry points, tool enumeration, and the non-live test suite. Package installation success alone does not prove runtime compatibility.

## MCP and tool-surface inventory

1. Identify the server implementation, actual transport selected by the entry point, response envelope, and tool input/output schema generation mechanism.
2. Enumerate tools from the live MCP registry when possible. Use source AST/decorator enumeration as a cross-check, not as the only count.
3. Capture exact tool names and representative generated schemas. Compare the runtime count with README and registry metadata.
4. Classify each tool by effect:
   - external-data read;
   - local/account read;
   - persistent mutation;
   - execution/import of user-selected code;
   - mixed or hidden side effects such as cache/schema writes.
5. A single server containing both reads and mutations is not a trustworthy read-only boundary merely because clients are prompted not to call mutations. Prefer separate registration surfaces/processes or enforce an allowlist outside the model.

## Storage and schema audit

Record default paths, environment/CLI overrides, whether server and CLI honor the same overrides, account isolation model, authentication/ownership assumptions, database mode, all tables and constraints, cache behavior, and transaction boundaries. Note when nominally read-only calls create directories, schemas, cache rows, or network state.

## Semantic audit

For backtests, inspect input ordering and validation, point-in-time guarantees, API patch completeness, spread/depth/fee assumptions, exception handling, timestamps, open-position valuation, liquidation/settlement, and result formulas. A replay that reports ending cash while assigning zero value to open positions is an execution demo, not a portfolio-return backtest.

For resolution, inspect the exact winner predicate, closed/disputed/invalid handling, ambiguous and split payouts, stale metadata risk, idempotency, and whether canonical resolution rules/source are represented in the market schema. Do not infer correct resolution semantics from a final-looking price alone.

## Extension, orchestration, and overlay audit

When the consumer needs to extend an agent/runtime rather than merely call one, inspect each extension class separately:

1. **Declarative content:** user skills/prompts, preset YAML/JSON, templates, and package-data rules. Record search order, override precedence, and whether upgrades preserve user files.
2. **Executable plugins:** tool, provider, channel, route, scheduler, and storage plugin registries. Distinguish a documented convention from a real `entry_points`, import-hook, registry, or filesystem loader.
3. **Orchestration:** inspect preset schemas, DAG validation, concurrency model, per-worker model/tool/skill controls, and any unconditional system-prompt rules. A dependency on an orchestration library does not prove that library drives runtime execution; verify imports and call paths.
4. **MCP trust boundary:** record transport, server-level `enabledTools`/allowlist behavior, generated local tool names, per-agent tool filtering, and whether API/session callers can inject server definitions. Prefer two independent gates: operator-owned server allowlist plus worker/preset tool whitelist.
5. **Callable surfaces:** inventory REST/MCP/Python entry points, start/poll/cancel/retry behavior, streaming protocol, authentication, and whether final results can be retrieved after a client disconnect.
6. **Trace extraction:** locate live events, durable JSONL/state files, artifact directories, token usage, correlation IDs, sidecar/offload handling, and public retrieval endpoints. If raw traces lack an API, say that the companion must use a read-only volume or its own extractor.

Validate filesystem extension points with a tiny fixture under a temporary `HOME`; do not write into the real user state. If the product advertises a relocatable runtime root, set that override during the probe and compare every extension/state path. Flag split-brain behavior where sessions/runs honor the override but skills, presets, memory, or config remain anchored to `Path.home()`.

### Overlay versus fork decision

Recommend a thin companion/overlay when required behavior fits public REST/MCP/Python calls, declarative user skills/presets, operator-owned allowlists, and read-only artifact extraction. Pin the upstream Git SHA and keep deterministic domain logic outside the agent runtime.

Escalate to a fork only when the consumer must change a closed seam: no executable plugin hook for required tools/routes/providers, mandatory upstream worker prompts, missing structured-output contracts that cannot be enforced externally, unsafe trust boundaries, or storage paths that cannot be isolated. License permission alone is not a reason to fork.

## Version and no-change evidence

Report source `main`, nearest release tag, package-declared version, and published registry version separately; they commonly drift. Never describe unreleased `main` behavior as available from the latest PyPI/npm release. For a moving upstream, compare `git ls-remote` again before finalizing.

For the consumer project, capture `HEAD`, `git status --short`, and hashes of relevant tracked files before and after. Size/mtime is only a supplemental sentinel: another process can touch a file during the audit, so an mtime change is not proof that the auditor modified it.

## Completion evidence

Report:

- audited URL, default branch, full SHA, commit date, nearest tag, source version, and published version;
- fresh-install/import/test/tool-enumeration and temporary-fixture probe outputs;
- exact source `path:line-range` supporting each stack and contract claim;
- declarative versus executable extension points and their precedence;
- provider/base-URL/model configuration proof without exposing secrets;
- MCP allowlist layers and caller-injection boundary;
- callable workflow and event/trace extraction paths;
- documentation/metadata/runtime discrepancies;
- overlay-versus-fork verdict with explicit fork triggers;
- target-project no-change evidence.
