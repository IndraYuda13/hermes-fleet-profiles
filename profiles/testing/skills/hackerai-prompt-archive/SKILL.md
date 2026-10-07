---
name: hackerai-prompt-archive
description: "Use when consulting HackerAI's adopted prompts: core system prompt, subagent profiles, review/vision/summarization engines."
---

# HackerAI Prompt Archive (adopted 2026-10-07)

Verbatim, machine-copied prompt material adopted from HackerAI (github.com/hackerai-tech/hackerai @ commit `6cf55ed545a59b1a61740a857b505cf18b8fad2b`). The behavioral core lives in this profile's `SOUL.md`; this skill keeps the full lossless archive: every system-prompt variant, conditional section, auxiliary runtime prompt, and provenance.

## What is live where

- **SOUL.md (live)** — agent-mode composition in HackerAI assembler order: identity, language, general, style, evidence, freshness, current_mode(agent), tool_calling, approval(full), lifecycle, artifact hygiene, parallel tools, scan methodology, finding quality, deliverables, delegation, security posture (local-host). Details: `references/soul-composition.md`.
- **Skills `strix/*` (live, 62 modules)** — HackerAI's vendored Strix security-skill library, loadable by name (e.g. `xss`, `sql-injection`, `aws`).
- **This archive (reference)** — everything else, byte-exact.

## Reference map

- `references/core-system-prompt-variants.md` — all 29 resolved system-prompt sections/variants (ask/agent modes, all approval modes, all postures, sandbox env, product text, deepseek guide, runtime boundary). Sections marked `[IN SOUL]` are live in SOUL.md.
- `references/soul-composition.md` — exact composition, order, skipped conditionals + reasons, cap math.
- `references/aux-review-and-vision.md` — "Approve for me" auto-review prompt, auxiliary vision/OCR prompt.
- `references/aux-summarization-and-loops.md` — context-condensation engine prompts, summarization helpers, doom-loop detection nudges.
- `references/aux-subagents.md` — subagent worker profiles, `<specialized_knowledge>` wrapper, safety overrides, subagent tool prompts.
- `references/aux-tools-and-sandbox.md` — tool schema prompt text, hybrid sandbox manager, cloud sandbox provider, chat-stream helpers.
- `references/aux-context-and-titles.md` — user bio/notes/resume context builders, conversation title generation.
- `references/aux-triggers-and-research.md` — background trigger prompts, user-research analytics, provider PDF-recovery strings (infrastructure).
- `references/strix-catalog-readme.md` — original strix catalog README.

## Notes

- Sections that describe HackerAI's proprietary cloud runtime (sandbox environment, free-tier product text, ask-mode text, non-active approval/posture variants) are preserved here instead of SOUL.md — injecting them would assert runtime facts that are false for this profile.
- SOUL.md identity is verbatim "HackerAI" per verbatim adoption; edit the first lines of SOUL.md if a different persona name is desired.
