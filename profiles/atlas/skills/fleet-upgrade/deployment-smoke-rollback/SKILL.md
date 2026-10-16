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
4. Separate preparation permission from release permission, explicitly distinguishing service stop, schema COMMIT, cleanup COMMIT, artifact switch and publication. After authorized maintenance stop, report actual downtime immediately and issue a bounded review receipt naming service state, backup, exact SQL/diff hashes and the next authorized boundary; do not imply production is unchanged when additive schema transactions have committed. Resolve only concrete blockers with bounded probes; defer production-configured builds until source is frozen, and do not repeat a broad suite without a new falsifiable concern. For destructive cleanup, require a frozen reviewed target manifest and transaction-time retained-user exclusions; use the cleanup recipe in `references/isolated-release-gates.md`.
5. Stage runtime helpers and service overrides outside production while source owners finish; do not make a moving-source build a prerequisite for reviewable preparation. Verify supervisor lifecycle with process fixtures before real startup, preserve existing supervision/logging, and distinguish fixture-only checks from application boot evidence. Apply the smallest reversible change only after the release gate.
6. Verify process/container status and dependency connectivity. For a production-public build tested in shadow, inspect compiled browser and server routing before any write smoke; public environment constants can be inlined into server chunks, so runtime environment overrides alone do not establish isolation.
7. Run user-facing smoke checks on critical routes/functions through the actual public HTTPS proxy, using ordinary session cookies and clearly owned synthetic fixtures. Include signup/login/logout, persisted state after reauthentication, cookie security attributes, and a foreign-Origin mutation with a valid session plus unchanged fixture state. Loopback success and source security gates do not certify the deployed proxy/auth boundary. Keep cookie values and generated passwords out of receipts; distinguish HTTP assignment lifecycle from connected board/UI execution.
8. Inspect fresh logs/metrics for new errors, crash loops, latency or saturation signals.
9. If smoke/health fails, execute or recommend the predeclared rollback rather than improvising endless live fixes. Do not restore an old database over newer user writes as routine rollback.
10. Recheck health after rollback or successful rollout.
11. Record exact commands, timestamps, artifact identity, and residual risk. Return a compact operational checklist with concrete staged paths, executed checks and remaining gates, rather than repeating permission questions already resolved. Runner exit zero is not an all-pass claim. Finish asynchronous verification only after owned jobs and listeners are quiescent.

## Pitfalls
- "container is running" treated as application health;
- proving the served revision by BUILD_ID file or by content-hash/chunk-name comparison is unsafe when the source delta is small: unchanged pages (and the offline shell) reuse identical chunk names, so identical `_next/static/chunks/*.js` names across old and new releases do NOT distinguish them. Assert on the running process instead: `readlink /proc/$(systemctl show <unit> -p MainPID --value)/cwd` and the resolved unit `WorkingDirectory`, plus a build-dir probe (`/_next/static/<NEW_BUILD_ID>/_buildManifest.js` => 200 while the old id => 404). Note `_buildManifest.js` is absent from App-Router Turbopack builds, so use it only as a presence probe, not as a fetch target;
- hardlink-copied `node_modules` (cp -al) share inodes with the source tree: never run a build or install that writes into node_modules (e.g. pnpm install) unless the link is replaced first, or you mutate the shared tree;
- staging a release tree from `git archive` drops gitignored-but-required files: confirm build scripts do not depend on them and place required runtime inputs (e.g. `.browser-tests/*.js` fixtures) deliberately;
- a cheap isolated stage boot (separate loopback ports, prod untouched) before the prod switch catches fatal boot errors at near-zero cost and is worth doing even under time pressure;
- deploy success without exercising the user path;
- rollback plan depends on an artifact that was not preserved;
- restart clears evidence before logs are captured;
- FK-only deletion ordering misses trigger-created dependent rows: rehearse transactional cleanup on a private restore, inspect delete-trigger side effects, and explicitly sweep generated target-owned tombstones before parent account deletion;
- an older restore can prove dependency sequencing but cannot certify an exact current deletion manifest: record live-versus-restore drift and require fresh maintenance backup plus count/credential-retention guards before release.

## Verification
Deployment is VERIFIED only with post-deploy smoke + health evidence and a known rollback path. When the requested scope is a user-visible flow, drive the deployed PUBLIC origin with a real browser (fresh signup -> the exact flow -> screenshots), not just HTTP status codes: status 200 on a page proves the proxy, not the feature. Distinguish deploy-infrastructure failures from smoke-script bugs before invoking rollback; fix and rerun the script when the product itself is sound.
