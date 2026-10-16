# Oracle Patterns

Choose the oracle that matches the claim.

## Coding fixes
- targeted test passes
- exact failing command now exits cleanly
- exact output now matches expected result

## Automation and bot flows
- downstream state changes as expected
- final URL / response / balance / status is correct
- not just a button click, callback, or intermediate message

## Ops work
- process is alive
- service is healthy
- one real post-restart task succeeds

All three are often needed for a strong ops success claim.

## Destructive database transactions

1. Inspect the authorization, fixed target manifest, exact transaction, dependency graph, migration envelopes and existing raw proof before executing. Define protected identity/content classes explicitly; ownership alone must not override protection of global/system content.
2. Restore an existing approved snapshot into a dedicated isolated database. Assert database name, port and cluster identity before mutations so a copied connection cannot select production or another worker's rehearsal.
3. Apply the exact migration-plus-ledger envelopes. Bind source file SHA256, embedded ledger digest and resulting ledger row; successful SQL execution alone does not prove they match.
4. Add positive fixtures: a frozen candidate that acquires credentials and a newly created identity outside the manifest, including a retained session. Assert preservation of their dependent content, not only their auth rows.
5. Execute the unchanged guarded ROLLBACK template with `psql -X -v ON_ERROR_STOP=1`. Record its SHA256 and exit status. Repeat with aggregate assertions immediately before rollback to inspect the actual post-delete state without publishing private records.
6. Fingerprint full retained rows with deterministic ordering and record coverage. Compare all application-table fingerprints before/after rollback to prove the rehearsal left no persistent data changes. Keep private dumps and raw logs restricted; report only counts, digests and protected-class results.
7. Force `SET CONSTRAINTS ALL IMMEDIATE` before rollback when rehearsing COMMIT readiness. Do not treat `pg_constraint.convalidated=true` as evidence that pending deferred foreign keys passed; it describes catalog validation state.
8. Exercise at least one mismatched-count or stale-manifest rejection and verify rollback. Keep this negative result separate from the successful guarded happy path.
9. Review the release transaction against the certified template. Rebind changed manifest/counts and final SQL digest under a complete dependency-write freeze; auth-table locks alone do not serialize class/result/content writers. Require explicit zero assertions for new dependency tables represented only by empty fixtures, or add nonzero fixtures and retest their deletion order.

Counts cannot detect same-count target substitution. Preserve exact frozen identities, transaction-time credential/anonymity exclusions, shared-owner classification and retained-row fingerprints together. A reviewed ROLLBACK script is not a reviewed live COMMIT artifact; changed predicates, dependency ordering or protection logic invalidate the corresponding rehearsal evidence.

## Reverse engineering claims
- xref or trace proves the caller/callee path
- hook or packet proves runtime behavior
- patch or replay proves the claimed effect

## Research or diagnosis
- artifact backs the conclusion
- strongest alternative explanation was checked or falsified

## Quick downgrade rule
If only intermediate proof exists, say `partial`, `narrowed`, or `pending verification`, not `confirmed`.