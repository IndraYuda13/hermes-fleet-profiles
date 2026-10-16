# Live runtime origin / CSRF / cookie boundary gate

Use when code is already deployed and the open question is whether the REAL public
runtime enforces origin/CSRF, cookie attributes, session isolation and refresh/logout.
Source reading is not evidence here: Origin rewriting, forwarded proto and host
rewriting live in the proxy/deployment layer, so the gate must exercise real HTTPS.

## Procedure

1. Discover the actual public entry point, release directory, build id and the
   private runtime-config path plus proxy conf path from the handoff/receipt files.
   Record the Git HEAD at the same time.
2. Bind evidence to a revision BEFORE probing: hash the private runtime config and
   the proxy conf, read the deployed build id (`release/.next/BUILD_ID`), and compare
   against the handoff hashes. Re-hash everything AFTER the final probe run and
   require equality in the same receipt - a config edit mid-gate invalidates every
   earlier observation.
3. Read the source origin contract before designing the Origin cases, so the
   expected result is derived from code, not assumed. Example: a `isSameOrigin`
   helper that returns false when the Origin header is absent means a
   cookie-bearing request with no Origin MUST be 403 - label that contract match,
   not a vulnerability, and refuse to silently accept null-Origin.
4. Call a real provider/API login with an OWN synthetic fixture read from a private
   fixture file (email, password, seeded ids). Never print the secret; keep it in
   process memory only. A generated synthetic fixture over normal HTTP is the
   authorized path where typing a password into a browser is not.
5. Positive path: login 200 and read back an own previously persisted object
   (class/lesson/group) to prove the session really authenticates and the data
   survived.
6. Hostile-origin matrix on state-changing endpoints. Send the SAME valid session
   with each of: foreign origin, literal `null`, and no Origin header. Require 403 on
   all three, and after EACH rejection read back the own collection and require exact
   equality. Status code alone is not evidence of no mutation.
7. Session-class isolation: take the second surface's cookies (e.g. board) and send
   them to the first surface's API explicitly, bypassing browser path scoping by
   setting the Cookie header by hand. Path attributes only constrain browsers, so
   prove the server-side role check with a forced header and require 401.
8. Cookie evidence: capture attributes only - name, Secure, HttpOnly, SameSite,
   Path - never values. Assert Secure+HttpOnly+SameSite=Lax and the surface-specific
   path for each surface.
9. Refresh/logout boundary: decode the session cookie in RAM, call the public token
   endpoint (`grant_type=refresh_token`, apikey header) and require 200 with the same
   user id; then install the refreshed credential on the real public app and require
   an authenticated call to succeed. Then normal logout, require the teacher API to
   return 401, and require the newest refresh token to be rejected by the provider.
10. Close with the exact command and its exit code, the revision/digests, the
    observations, and the residuals. Stop there.

## Pitfalls

- Do NOT assert a specific provider error schema for token revocation. Hosted and
  local/self-hosted auth providers return different shapes for the same rejection
  (`code=invalid_credentials` vs `error_code=refresh_token_not_found`). Assert on the
  rejection (status in 400/401/403) plus the observed provider metadata, and read the
  real error body before tightening anything.
- A first-pass harness assertion failure is NOT a security regression. Inspect the
  actual response metadata, then relax only the reviewer's assertion, never the
  security check, and rerun the full probe so the passing run is on the fixed script.
- `requests`/client sessions hide the raw cookie jar layout; parse the combined
  cookie value yourself (strip the `base64-` prefix, urlsafe-decode, pad `=` to a
  multiple of 4) when you need the refresh token, rather than dumping cookie values.
- Cookie Path is not an authorization control server-side. Always pair a cookie
  attribute check with a forced cross-surface request.
- The gate stays bounded even when it passes over real HTTPS: report an ACCEPTED
  auth boundary with its limits, never a whole-product PASS. Do not claim expiry
  driven automatic refresh, immediate access-JWT revocation, or surfaces you did not
  exercise.

## Evidence and receipt rules

- Keep P0/P1 findings only, plus explicit limitations; no secret values, tokens,
  cookie values, private identities or secret-bearing URLs in the receipt.
- Write the sanitized machine proof to a JSON file (checks with ok/status, hashes,
  source, build, verification_status, limits) and a short human Markdown gate receipt
  next to the handoff.
- State the command line and exit code that produced the evidence, and note explicitly
  that the production source/config was untouched.
- Preserve unrelated existing fixtures/records; only create clearly-own synthetic
  records and never delete or rewrite other users' data or touch the DB directly.
