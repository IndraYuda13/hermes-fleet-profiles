# PostgreSQL-backed RPC gate recipe

## 1. Freeze and separate

Resolve the exact authorized SHA, then archive tracked source independently of the moving checkout:

```bash
mkdir -p "$SOURCE" "$RUNTIME" "$EVIDENCE"
git -C "$REPO" archive "$SHA" | tar -x -C "$SOURCE"
chmod -R a-w "$SOURCE"
git -C "$REPO" archive "$SHA" | tar -x -C "$RUNTIME"
```

Create directories before selecting them as a command workdir. Keep generated logs, Vite caches and probe scripts outside the immutable archive. Use the existing dependency installation only after verifying it belongs to the permitted candidate, not production. Hash reviewed source files programmatically and retain the relative-path manifest.

## 2. Establish DB identity before fixture writes

Inspect the repository harness's URL validation before choosing a fresh DB name. Match its required namespace without weakening its guard. Use only an explicitly authorized cluster connection, with no fallback to default environment URLs.

```sql
select current_database(), inet_server_port(),
       current_setting('data_directory'), system_identifier
from pg_control_system();
```

Compare the result with the authorized isolation receipt. Stop on mismatch. Create an own fresh synthetic DB only after this check; apply bootstrap and sorted frozen migrations with `psql -X -v ON_ERROR_STOP=1`. Preserve preparation logs. Do not reuse another verifier's fixtures or a private restore database.

## 3. Probe the real boundary

- Inspect API auth/body parsing and direct RPC grants separately; HTTP validation does not protect independently callable SQL functions.
- Use distinct owner, other-owner, paired anonymous and unpaired anonymous test actors. Superuser may install synthetic fixtures, but switch to the runtime role and JWT claims before testing access decisions.
- Query private helper execution privileges and attempt intended-denied calls under runtime roles. Source REVOKE statements alone are not runtime permission proof. If qualified-name lookup itself is blocked by private-schema USAGE, perform catalog inspection as the fixture administrator with an explicit target role, e.g. `has_function_privilege('authenticated', 'private_schema.helper(jsonb)', 'EXECUTE')`; keep hostile RPC calls under the runtime role and report schema denial separately. Do not grant extra schema access merely to make the probe run.
- Reuse fixture construction if useful, but author independent assertions for cross-owner reads, private fields, binding mismatch, revoked grants, stale epochs, replay mismatch and competing CAS requests.
- For history/checker probes, record the answer call, check call and persisted progress. A stored hostile model is not a correctness bypass unless actual feedback or protected state demonstrates the impact.
- When a synthetic immutable version is modified by fixture setup, disclose that setup and roll it back; do not claim the probe proves unauthorized version mutation.
- Run legacy and new writers against the same protected state to detect downgrade paths. Verify response history and grades after rejection, duplicates and corrections.
- Test one rejection condition at a time when claiming branch coverage. An oversized payload with an unknown field proves rejection but cannot establish that the size limiter, rather than strict-schema validation, caused it. Likewise sequential stale-CAS tests do not prove concurrent serialization.
- Separate fixture checks from independently authored attack assertions and count labels programmatically. End authority matrices with persisted revision, receipt count and grade/history readback so harmless-looking errors cannot hide partial mutation.

## 4. Close accurately

Separate regression counts from independently authored probe coverage. Bind every result to the source revision, DB identity and command output. Keep unexecuted scripts labeled unexecuted, not evidence. A partial gate cannot be carried as release certification, even with unchanged digests. Retain only synthetic, nonsecret reproducible artifacts and identify the smallest remaining approval or access requirement.
