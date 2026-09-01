---
name: hermes-agent-memory-limits
description: Pitfalls and operational truths regarding Hermes Agent's declarative memory (FTS5 SQLite) limits.
---

# `hermes-agent-memory-limits`

Pitfalls and operational truths regarding Hermes Agent's declarative memory (FTS5 SQLite) limits.

## The 8000 Character Limit
Hermes Agent uses a hardcoded 8000-character limit for its FTS5 SQLite declarative memory (`USER PROFILE` and general memory). 

### Pitfalls to Avoid
1. **Do not search for `1375` or `8000` in config files**: The limit is not exposed in `config.yaml`.
2. **Do not attempt to `sed` patch the source code**: Running bulk find-and-replace for "8000" across `/usr/local/lib/hermes-agent/` is extremely dangerous. It will corrupt unrelated network timeouts, port configurations, tokenizers, and dependencies.
3. **Do not try to force large documents into memory**: The DB is not designed for full document storage.

### The Right Way (Lazy & Safe)
If a user requires a large document (e.g., a 15,000 character `USER.md`) to be present in context, **do not put it in the SQLite DB**.

Instead, rely on one of these approaches:
1. **On-Demand Reading**: Use `read_file` to pull the document when context is needed.
2. **Session Injection**: Create a skill or cronjob that runs at session initialization to load the file into the active context stream.
3. **Summarization**: Keep the `USER PROFILE` in the DB as a strict, condensed index (under 8000 chars) that references external files for the full details.

When a user asks to increase the memory limit beyond 8000, explicitly state that it is hardcoded in the source and recommend on-demand file reading instead of risking source corruption.