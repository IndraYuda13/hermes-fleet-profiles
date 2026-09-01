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
2. Define explicit success signals and rollback triggers before mutation.
3. Apply the smallest reversible change.
4. Verify process/container status and dependency connectivity.
5. Run user-facing smoke checks on critical routes/functions.
6. Inspect fresh logs/metrics for new errors, crash loops, latency or saturation signals.
7. If smoke/health fails, execute or recommend the predeclared rollback rather than improvising endless live fixes.
8. Recheck health after rollback or successful rollout.
9. Record exact commands, timestamps, artifact identity, and residual risk.

## Pitfalls
- "container is running" treated as application health;
- deploy success without exercising the user path;
- rollback plan depends on an artifact that was not preserved;
- restart clears evidence before logs are captured.

## Verification
Deployment is VERIFIED only with post-deploy smoke + health evidence and a known rollback path.
