# Security and secret handling

## Runtime secret boundary

Tracked profile configs are declarative and sanitized. Runtime credentials live
only in the active profile's `~/.hermes/.env`, a systemd `EnvironmentFile`, or an
equivalent secret manager. The repository intentionally contains no usable
credential fallback.

Dashboard auth uses the Hermes-supported variables:

- `HERMES_DASHBOARD_BASIC_AUTH_USERNAME`
- `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD_HASH`
- `HERMES_DASHBOARD_BASIC_AUTH_SECRET`

Connector credentials use their provider variables, including
`FIRECRAWL_API_KEY` and `POSTMAN_API_KEY`.

## Required one-time response for historical exposure

1. Rotate every dashboard password/signing secret and connector key that has
   ever appeared in this repository.
2. Verify the new values only on the runtime host; do not paste them into an
   issue, PR, commit, CI variable log or chat transcript.
3. Preserve a private forensic backup, then rewrite repository history with a
   reviewed secret-replacement map.
4. Invalidate old clones or reclone after the history rewrite.
5. Run the fleet policy workflow and an independent secret scanner before
   lifting the incident.

History rewriting and credential rotation are intentionally not automated by
this repository because both require owner-controlled external coordination.

