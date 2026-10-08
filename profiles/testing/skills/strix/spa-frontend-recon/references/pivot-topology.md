# Pivot Topology: Where a SPA's Attack Surface Actually Lives

A JS shell usually fronts several independent services on sibling subdomains. Expect this shape and enumerate each:

| Role | Typical host | What to test |
| --- | --- | --- |
| Static shell + SPA | apex / `www` | catch-all confirmation; source maps; security headers |
| Portal/REST API | `api.` or `belakan.`/`admin.` | endpoint enumeration, param handling, auth (JWT/session), PHP/Laravel debug, mass assignment, BFLA |
| Asset/CDN microservice | `cdn.` | CORS, path handling, direct file exposure, framework fingerprint (e.g. Express `X-Powered-By`) |
| Analytics/metrics | `analytics.` | self-hosted instance (Plausible/Matomo/Grafana) — exposed health/DB status, version, CORS with credentials |
| Managed backend | Firebase/GCP/etc. | security rules (read AND write) for Firestore, Storage, RTDB — see firebase skill |

## Ordering

1. Confirm the shell is a catch-all (Step 1) so you stop brute-forcing it.
2. Recover source (Steps 2–3), harvest hosts/endpoints (Step 4).
3. Pivot host-by-host (Step 5); fingerprint and test each independently — do not assume the apex host's hardening carries to siblings.
4. Exercise the managed backend rules directly rather than through the UI (Step 6).

## API host triage cues (PHP/Laravel-style)

- `X-Powered-By: PHP/x.y.z` → version disclosure; probe for debug/ignition/telescope (usually 404 in prod — do not report absence)
- `401 {"message":"Unauthenticated."}` on a protected route (e.g. `/api/user`) is correct behavior, not a finding
- Sessions via `XSRF-TOKEN` + `<name>_session` cookies → CSRF token present; login should reject wrong creds (verify with a 302 back to `/login`)
- A generic maintenance/500 HTML page reused as the error body means error-based oracles are unavailable — rely on status + length + timing deltas instead

## Firestore rules: unauthenticated REST still matters

- Anonymous sign-up via Identity Toolkit `accounts:signUp` may be disabled (`ADMIN_ONLY_OPERATION`); this does NOT stop unauthenticated REST reads/writes — attempt them directly with no token.
- Query every collection unauthenticated over `https://firestore.googleapis.com/v1/projects/<project>/databases/(default)/documents/<collection>`. Console "test mode" or a stale rule often leaves a single collection (commonly `setting`/`config`) world-readable while siblings correctly return 403.
- Test writes with a throwaway document in an isolated path and delete it afterward.
