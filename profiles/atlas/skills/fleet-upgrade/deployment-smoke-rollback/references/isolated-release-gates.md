# Isolated release gates

## 1. Identify and isolate
1. Read live service WorkingDirectory, launcher, process environment and listener owner. Extract database endpoint without exposing secrets. Compare actual SQL identity, not database-name patterns:
   ```sql
   select current_database(), inet_server_addr(), inet_server_port(),
          current_setting('data_directory'),
          (select system_identifier from pg_control_system());
   ```
   Use available privileges; if cluster identity cannot be read, document the verification gap rather than substituting a guessed name.
2. Create the candidate from exact approved live HEAD, preserving dirty user artifacts separately. Use a private dependency copy rather than a writable symlink into live modules. Keep candidate builds, browser profiles, coverage and backups on the filesystem with verified headroom.
3. Set app/provider/DB ports explicitly, disable external LLM calls, omit live credentials and disable reuse-existing-server. Make every preflight failure abort the launch with `set -e` or `guard || exit`; otherwise a failed guard merely prints a warning and tests still execute.
4. Probe listener ownership and bind availability before launch. Distinguish TIME_WAIT from an active listener using `ss` and a socket bind with SO_REUSEADDR when appropriate; never kill an unknown owner to free a port.

## 2. Run complete evidence without hiding failures
- Execute format, types, lint, unit/coverage, SQL/integration, build and browser phases with separate logs and exit records when a short-circuiting verify chain would hide later results. Preserve the aggregate failed status even when the orchestrating shell completes successfully.
- Use a fresh dedicated synthetic DB when fixtures collide on repeated SQL runs; prepare current migrations there and rerun the failed integration leg. Do not reset a shared or live DB to make tests green.
- Request coverage on failed tests explicitly when supported, for example `vitest run --coverage --coverage.reportOnFailure --coverage.reportsDirectory=<evidence-dir>`; a coverage flag alone may emit no report after failure.
- For relocated pnpm dependencies, first test `pnpm --config.verifyDepsBeforeRun=false exec <tool>` or invoke the installed Node CLI directly. Prefer explicit arguments over a shell function when tools spawn non-Bash subprocesses, because exported functions do not reliably carry into those children. Do not enable unattended module purge as a workaround.
- An external Playwright runtime config may substitute direct installed Next/provider launch commands and evidence destinations without editing test source. Preserve authentication/demo settings and isolation checks; disclose the config difference in the receipt.
- Parse test reporter totals, not console impressions. Trace widespread failures to shared helpers or fixture assumptions before classifying them. Explain an outdated assertion only with inspected current behavior; do not label all remaining failures historical.
- Bind source SHA, newly emitted BuildID, public/offline manifest and verification logs together. A successful build on the actual Node executable demonstrates that execution, not certification of a different pinned version.

## 3. Rehearse migration and restore safely
1. Restore a restricted baseline dump into an isolated non-app DB. Compare table counts and deterministic original-column fingerprints before and after the candidate migration.
2. When additive columns change full-row fingerprints, project the preexisting columns before concluding history changed. Check old registry rows separately from newly added registrations.
3. If a restore-time CHECK invokes functions that depend on other tables, ordinary COPY order can reject rows that become valid after all data exists. Prefer dependency-aware ordering; obtain explicit approval for a temporary constraint exception without interpreting a production no-drop rule as permission or as an absolute ban on approved private rehearsal. On the isolated rehearsal only: restore pre-data, temporarily drop the identified dependent CHECK, restore data and post-data, recreate CHECK NOT VALID, then VALIDATE. Retain the error and require final validation; never treat a permanently disabled constraint as a successful restore.
4. Take a fresh release backup immediately before authorized mutation. Include generated public SW/offline assets as well as source, build, configuration and user changes. Earlier rehearsal snapshots are not current rollback backups.

### Exact account cleanup rehearsal
1. Freeze exact eligible IDs in a restricted manifest before opening signup. Classify restrictive dependent content explicitly, distinguishing teacher-owned content from global/system collections and anonymous board identities. Never substitute a later query-all-delete for the reviewed manifest.
2. Take a fresh read-only `pg_dump -Fc`, checksum it, and restore into a newly named empty database on the verified isolated cluster. Keep the dump and SQL containing IDs private. Record snapshot timing: a consistent dump is not a maintenance write freeze.
3. Apply each approved migration and its filename/checksum ledger entry in the same transaction. Parse transaction boundaries rather than assuming `begin;` is the first line, since migrations may start with comments. Reconcile the actual live ledger, not a synthetic test ledger.
4. Add positive private retention fixtures: give one recorded legacy target credentials, and create a new signup identity with credentials/session. Select cleanup targets only from the frozen IDs, excluding credential-bearing and anonymous users inside the transaction. Lock the relevant auth tables or otherwise prevent signup/credential races under maintenance.
5. Traverse actual foreign keys, classify shared-owner dependencies, and delete only exact target-dependent rows child-first. Inspect DELETE triggers as well as FKs; sweep newly generated target-owned tombstones before deleting account parents. Fail closed on dependency cycles or retained-user references rather than widening the cascade.
6. Compare deterministic full-row fingerprints of all non-target rows before/after cleanup, plus protected credentials, sessions, anonymous identities and system-set counts. Require zero unvalidated application constraints. Fixture counts differ from real release counts; do not copy rehearsal expectations blindly.
7. Author the reviewed production transaction separately with frozen targets, credential exclusions, drift/rowcount guards and protected-data assertions. Until approved, label it a review draft and end it with ROLLBACK. Recheck against the maintenance snapshot before enabling COMMIT.

## 4. Establish rollout and rollback compatibility
- Inspect build-time public env values before promotion: a test artifact can bake its isolated provider URL into browser assets. Freeze final source, then produce a separate production-configured release artifact rather than copying the isolated build blindly. Keep live AI configuration unchanged; disable external calls only in shadow runtime. A production-public-env build may still direct browser writes to live endpoints, so intercept/reroute those origins to an isolated provider for write smoke, or identify a separate test build honestly. Structural URL checks and another BuildID's browser tests do not certify the release artifact.
- Inspect startup migration/seed behavior and the migration ledger before restart. A manually applied but unstamped migration may be applied again by the launcher; require a reviewed transactional migration-plus-ledger recipe. Prefer explicitly managed app/provider processes without prepare/seed side effects for persistent deployments, with the runtime-strategy change reviewed separately. Do not copy the test environment into production.
- Treat credential/schema upgrades as a rollback boundary: an old passwordless app/provider may be unsafe for new credential-bearing users or may reject a newer ledger. If downgrade compatibility is not exercised, retain current auth/schema and prescribe maintenance plus forward repair. Pre-write snapshot recovery requires separate approval; never overwrite post-reopening signups.
- Test old and new clients against the migrated backend, including pending writes. Retain old static chunks needed by open tabs. Confirm SW activation is gated by client safety and does not cache private/API/RSC responses.
- Treat IndexedDB version upgrades as a rollback boundary: additive stores can still make an older application's lower-version open fail. Certify a downgrade-compatible artifact or specify forward-fix mitigation; reverting server source alone is not a data-preserving rollback.
- Preserve new database writes during rollback. Prefer reviewed compatibility migrations restoring legacy RPC behavior while retaining new tables/history; snapshot restore is disaster recovery requiring explicit data-loss acceptance.
