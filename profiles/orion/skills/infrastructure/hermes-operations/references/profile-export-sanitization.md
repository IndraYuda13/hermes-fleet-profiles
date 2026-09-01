# Profile Export & Sanitization Recipe for External Auditing

When exporting Hermes profile directories for review, research, or passing to external LLMs/teams for evaluation:

## Sensitive Vectors in Profiles
1. `config.yaml`: Contains API keys (`api_key`, `FIRECRAWL_API_KEY`, `POSTMAN_API_KEY`, etc.), web/dashboard auth (`auth: password:...`, `password_hash`, `secret`).
2. `memories/`: Contains `MEMORY.md` and `USER.md` which may record environment credentials, portal passwords, database usernames, or API tokens.
3. `.env` / `auth.json`: Holds raw session credentials and auth tokens.
4. `sessions/` / `state.db`: Can leak prompt history containing confidential user data.

## Sanitization Workflow
1. Export only non-runtime artifacts (`SOUL.md`, `profile.yaml`, `config.yaml`, `memories/`, and metadata lists of installed skills).
2. Omit runtime databases, lockfiles, cache directories (`cache/`, `audio_cache/`, `sessions/`, `state.db*`).
3. Run regex redaction targeting:
   - `api_key: ...`
   - `password: ...` / `password_hash: ...`
   - `secret: ...`
   - `token: ...`
   - Specific key formats (`sk-...`, `PMAK-...`, etc.)
   - Plaintext passwords recorded in declarative memory notes.
4. Verify redaction with `grep -riE` before archiving to `.zip` or `.tar.gz`.
