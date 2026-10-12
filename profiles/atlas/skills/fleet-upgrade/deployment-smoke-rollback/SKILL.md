---
name: deployment-smoke-rollback
description: Gate deployments on smoke checks and rollback.
version: 1.0.0
author: Fleet Upgrade Research
license: MIT
metadata:
  hermes:
    tags: [devops, deployment, reliability, rollback]
    category: fleet-upgrade
---
# Deployment Smoke & Rollback Gate

## When to Use
Use for service/container/config/database/network changes that are deployed or restarted.

## Procedure
1. Capture pre-change state: revision/image/config, service health, key ports/routes, and rollback source.
2. Define explicit success signals and rollback triggers before mutation. Inspect the actual launcher: startup may apply migrations or seed data, making a restart a database mutation. Require a separate release decision when only preparation or verification is authorized.
3. Gate the exact candidate before mutation: verify runtime-derived live DB identity against the isolated test cluster, capture each verification phase's raw exit and counts, and bind results to the resulting build identity. A rebuilt artifact invalidates evidence tied to the previous BuildID. See `references/isolated-release-gates.md` for isolation, migration rehearsal, and client compatibility checks.
4. Separate preparation permission from release permission. Resolve only concrete blockers with bounded probes; defer production-configured builds until source is frozen, and do not repeat a broad suite without a new falsifiable concern. For destructive cleanup, require a frozen reviewed target manifest and transaction-time retained-user exclusions; use the cleanup recipe in `references/isolated-release-gates.md`.
5. Apply the smallest reversible change.
6. Verify process/container status and dependency connectivity.
7. Run user-facing smoke checks on critical routes/functions.
8. Inspect fresh logs/metrics for new errors, crash loops, latency or saturation signals.
9. If smoke/health fails, execute or recommend the predeclared rollback rather than improvising endless live fixes. Do not restore an old database over newer user writes as routine rollback.
10. Recheck health after rollback or successful rollout.
11. Record exact commands, timestamps, artifact identity, and residual risk. Report concise factual outcomes and concrete blockers; runner exit zero is not an all-pass claim. Finish asynchronous verification only after owned jobs and listeners are quiescent.

## Pitfalls
- "container is running" treated as application health;
- deploy success without exercising the user path;
- rollback plan depends on an artifact that was not preserved;
- restart clears evidence before logs are captured;
- FK-only deletion ordering misses trigger-created dependent rows: rehearse transactional cleanup on a private restore, inspect delete-trigger side effects, and explicitly sweep generated target-owned tombstones before parent account deletion;
- an older restore can prove dependency sequencing but cannot certify an exact current deletion manifest: record live-versus-restore drift and require fresh maintenance backup plus count/credential-retention guards before release.

## Verification
Deployment is VERIFIED only with post-deploy smoke + health evidence and a known rollback path.
