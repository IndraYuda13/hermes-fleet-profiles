# Persistent authentication review recipe

## 1. Bind scope and isolate execution
Read the contract and implementation: strict request schemas, origin/body handling, authenticated-user validation, native provider calls, credential hashing, token lookup/revocation, rate storage and additive migration. Record HEAD and dirty paths; exclude unrelated concurrent changes explicitly.

Use an owned synthetic database and free nonlive provider port. Confirm the actual PostgreSQL cluster before creating fixtures, not merely the configured URL:
```bash
psql "$ISOLATED_ADMIN_URL" -X -qAt -v ON_ERROR_STOP=1 -c 'select system_identifier from pg_control_system()'
createdb -h "$TEST_HOST" -p "$TEST_PORT" -U "$TEST_USER" "$OWN_TEST_DB"
```
Pin the returned cluster identity in diagnostics where supported. Apply current migrations to the clean owned database and run targeted SQL/unit/HTTP checks. Reset rate fixtures only in that owned database. Stop the provider in a finally block and confirm its port has no listener afterward; never reuse a shared application's provider just because it is available.

## 2. Independent bypass matrix
Generate synthetic passwords/tokens in RAM and retain only labels/counts in artifacts. Exercise these paths over actual HTTP and inspect resulting SQL state:

| Boundary | Probe and required outcome |
|---|---|
| Registration | Register then login; duplicate signup with different password cannot replace UUID/credential. Normalized legacy email signup cannot create credentials for the existing owner. |
| Enrollment | Valid authenticated legacy bearer can enroll its own subject. Absent, forged JWT, anonymous, expired, revoked and refresh bearer cannot enroll. Supplied alternate email/id must be rejected. Verify failed takeover leaves the target credential absent. |
| Token kinds | Refresh cannot read user/enroll; access cannot refresh. Rotation preserves subject and invalidates old access and refresh; old refresh replay fails. |
| Persistence | Actually stop and restart provider; new password login, existing access and rotated access preserve identity. Throttling remains exhausted after restart. |
| Logout | Local logout invalidates the access/refresh pair, including after restart when claimed. |
| Test capabilities | Exercise OTP, inband link and PKCE endpoints with internal-test and reveal flags enabled against a public origin. They must fail closed. Attempt any sample-password override under the same public configuration. |
| Privacy | Wrong-password/unregistered errors remain generic. Check captured logs for synthetic password/token/email without printing those values. Reject oversized bodies. |

An opaque persisted-token provider must look up the capability hash rather than trust decoded JWT claims. Native SDK getUser validation and mock route tests do not by themselves prove hosted JWT behavior.

## 3. Storage inspection
Verify salted slow hashing parameters, random salt, timing-safe comparison and comparable missing-user hashing. Verify private credential/session/rate tables reject client roles, session lookup stores token hashes rather than raw tokens, and rate buckets hash email/peer identity. Trace the proxy header trust boundary separately: application hashing does not make attacker-controlled X-Real-IP trustworthy. Flag retention/capacity policy separately from an auth bypass.

## 4. Decision and rollout limits
Record exact source/probe digests, commands, individual suite counts and observed failures. Do not count every unit test as a runtime exploit assertion. Carry earlier evidence only when relevant bytes and assumptions are unchanged, and state precisely what is carried.

Treat pre-change memory-only sessions as a rollout problem: they cannot automatically survive a restart without persisted capabilities. Require authenticated enrollment before restart or trusted operator recovery; never solve migration by allowing public legacy-email claims. Clean migration success does not certify reconciliation of a previously applied draft schema. Keep local unverified-email behavior, hosted SMTP configuration, production proxy enforcement and browser cookie flow as separate evidence scopes.
