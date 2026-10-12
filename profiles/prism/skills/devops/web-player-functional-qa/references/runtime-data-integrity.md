# Runtime data-integrity probes

## 1. Freeze and isolate before mutation

1. Read mission constraints, schema, RPC contracts, and existing fixtures before designing assertions. Inspect exact response-state enums; scanner classifications need not equal persistence states.
2. Create a private immutable source view: `mkdir -p "$FROZEN"`, then `git archive "$SHA" | tar -x -C "$FROZEN"`. Keep independent probes/logs outside the shared implementation checkout. Record SHA256 manifests for relevant backend, contract, migration, and storage files.
3. Resolve the test DB URL explicitly rather than trusting harness defaults. Before creating fixtures, query `pg_control_system()`, `current_setting('data_directory')`, `inet_server_port()`, and `current_database()` on the approved isolated target. Compare against the isolation receipt, then create a verifier-owned database namespace. A different database name on the live cluster is not cluster isolation.
4. Bootstrap actual migrations into that database. Pass the explicit DB URL on every command, for example `TEST_DATABASE_URL="$OWN_DB_URL" node scripts/test-db.mjs prepare` when the project supplies that harness. Never copy private production data into a synthetic fixture.
5. Run SQL with `psql "$OWN_DB_URL" -X -qAt -v ON_ERROR_STOP=1 -f "$PROBE"`; use `BEGIN`/`ROLLBACK` around fixtures and preserve stdout, stderr, exit status, and probe digest. Assert each mutation's response before asserting its downstream effect, because an expected-looking later failure may originate in rejected input.

## 2. Persisted lifecycle and algorithm oracles

- Run relevant existing SQL regressions, then add independent assertions against persisted rows and real RPC outputs. Label reused assertions separately from new scenarios; counts are not a substitute for coverage.
- For grouping, sweep legal roster sizes/group counts with none, partial, complete, and tied evidence. Assert exact-once membership, absence exclusion, no empty groups, requested count, deterministic retries, and balance where promised. Use bounded synthetic loops instead of a full app build when the uncertainty is entirely server-side.
- For evidence selection, construct different forms/versions with the same competency, as well as changed mappings. Assert one comparable cohort, exact known/unknown counts, latest valid response revision, and frozen published sidecars. Different competency mappings alone do not prove same-competency version isolation.
- Distinguish null/blank/unreadable/review from an explicit answered unknown choice. Assert accepted status, score, DTO representation, correction history, duplicate history count, and stale-revision conflicts independently.
- Exercise two meetings through actual prepare/save/begin/close and correction actions. Assert corrected evidence affects only the next suggestion, active/closed snapshots stay fixed, late submissions do not resurrect boards, group progress does not become individual grades, and root result counts exclude child entries.
- Treat sequential stale-revision checks as CAS evidence, not simultaneous-race certification. Treat server/TS generators as separate algorithms unless direct parity has actually been tested.

## 3. Standalone IndexedDB upgrade without a full build

1. Launch a private Vite server on `127.0.0.1` with port `0` and an ephemeral Chromium context. This allows importing actual client TypeScript without competing with a shared integration build.
2. Use the historical schema declarations to create a uniquely named old-version Dexie database. Seed representative drafts, pending mutations, nullable/unknown answers, sync queues, and presence records. Avoid copying user names or private records.
3. Close the old connection. Import the current application's database factory through Vite and open the same database name. Compare complete stored values, not just row counts; then write a new-version pending record.
4. Close/reopen and assert old records plus new pending data remain. Reopen using old-client declarations to test backward reading where supported. Close all connections before deleting only the synthetic database; shut down browser/server in `finally`.
5. Report this as storage-schema preservation only. Full app pending-drain/replay, service-worker rollout, simultaneous old-tab upgrade blocking, quota failure, and deployment behavior need their own probes.

## 4. Client pending-drain and conflict probes

1. In the standalone Chromium/Vite harness, import the actual queue, sync, pending-read, and conflict-resolution functions. Establish the synthetic local access grant through the real access helper; do not bypass the application's storage guard.
2. Queue a contract-valid response, inject an HTTP409 transport response, and assert both the surfaced conflict and every retained draft field. Repeat with a network failure. Compare structured values fieldwise or with deep equality, not raw object `JSON.stringify` equality, because schema parsing can reorder properties without changing data.
3. Supply a schema-valid ACK and assert the accepted count plus pending deletion. Prefer an ACK captured from a real isolated SQL/RPC fixture; label transport injection explicitly, since it proves client behavior rather than real HTTP integration.
4. Hold the fetch promise with an explicit gate. Start sync, wait until fetch is entered, queue a newer edit, then release the ACK. Assert newer answers survive and their revision rebases to the acknowledged server revision. Use deterministic promise gates, not timing sleeps, to make the race reproducible.
5. Attempt conflict resolution against the stale draft and assert rejection leaves current pending intact. Then test explicit local choice preserves answers with the chosen remote revision, and explicit server choice clears only the matching draft.
6. Keep these results separate from full-app restart/replay and service-worker evidence. A local drain test does not prove real transport integration or deployment safety.

## 5. Summary semantics across evidence states

1. Use real backend outputs to identify reachable `known`, `no_result`, `not_comparable`, and unmapped/insufficient states. Construct same-competency/different-version fixtures so a valid historical result can exist while remaining outside the selected comparable cohort.
2. Render the actual summary component for each state. For a pure React component, `createServer({configFile:false, root: candidate, esbuild:{jsx:'automatic'}, server:{middlewareMode:true}})`, `ssrLoadModule(componentPath)`, and `renderToStaticMarkup(React.createElement(Component, props))` provide a bounded semantic repro without a full build. Close Vite in `finally`.
3. Assert both per-record wording and aggregate headers. Existing-but-not-comparable evidence must not be described as absent; unknown must not be converted to a score or global skill level. For a reason-aware repair, retest the original failing reason plus no-result, incomplete, and unmapped neighbors to prevent a new blanket fallback. Inspect actual `renderToStaticMarkup` output before choosing literal assertions: static markup can omit hydration comment separators, so assert semantic text rather than assuming client-render serialization. Route wrong semantics to the UI owner while preserving a separately correct backend gate.
4. Treat SSR as component semantic evidence only, not rendered-pixel, navigation, hydration, or accessibility certification. Use the independent live UI gate for those claims.

## 6. Preserve independent evidence

Keep failed probe logs. Correct a verifier-owned test defect only after checking the contract, then rerun the affected probe completely; never patch product implementation to make an independent gate green. Hash final probe bytes so later assertions cannot silently inherit an older log. If the integrated source changes, compare relevant manifests and rerun invalidated criteria before carry-forward. Record manifest roots and changed-file exclusions explicitly: unchanged backend files do not certify a modified PDF generator or other excluded surface. Read the actual build identifier (for Next.js, `.next/BUILD_ID`) independently of Git HEAD and compare it with the requested artifact; source-only SSR evidence may remain valid when build identity differs, but do not bind it to the reported build. Put the authoritative current verdict first in the report and label prior defects/revisions as historical or superseded so a repaired finding does not remain an apparent active veto. Separate an unexecuted probe from a reproduced product defect in the handoff.
