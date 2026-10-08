---
name: prompt-activation-debugging
description: "Use when auditing live agent prompts or refusals."
version: 1.0.0
author: hermes-curator
license: MIT
metadata:
  hermes:
    tags: [prompt, debugging, hermes-internals, refusal-analysis]
    related_skills: [hermes-agent]
---

# Prompt activation debugging

Diagnose "why did it refuse / why did it do that" and "which prompt is actually running" by reading the *injected* system prompt out of runtime state, not the source files. SOUL.md on disk is a source, not proof. A profile can hold stale copies (a scratch/working copy that differs from the live file, or an archived pre-adoption draft), so any claim about prompt behavior must be grounded in the bytes the model actually received.

## When to Use

- The user asks why the agent refused, hedged, or behaved differently than its prompt seems to instruct.
- The user asks which part of a system prompt (SOUL.md, posture, injected blocks) is responsible for a behavior.
- You need to confirm which prompt variant is live for a profile or session before quoting or reasoning about it.

## Procedure

1. **Find which prompt the session used.** The session row records it:
   ```sql
   SELECT id, title, profile_name, model, system_prompt_hash FROM sessions WHERE id = ?;
   ```
   (`<profile>/state.db`, table `sessions`.) List recent sessions to match the turn you are explaining.
2. **Resolve the exact injected text** by hash:
   ```sql
   SELECT prompt FROM system_prompts WHERE hash = ?;
   ```
   That column IS the full system prompt: SOUL.md first, then the Hermes runtime preamble, then the `<available_skills>` list and the MEMORY / USER PROFILE blocks.
3. **Prove membership and order.** `soul_text.strip() in prompt` should be True with SOUL at offset 0; the Hermes preamble starts at the marker `You run on Hermes Agent (by Nous Research)`. Everything between SOUL and that marker, plus everything after, is runtime-injected rather than SOUL content — check there before blaming SOUL for a behavior.
4. **Read the actual turn.** `SELECT role, content FROM messages WHERE session_id = ? ORDER BY id` gives the user/assistant exchange you are explaining.
5. **Diff candidates against the live file** before quoting any SOUL copy. A hash mismatch between a scratch/cached copy and the live SOUL is normal after a re-adoption; trust `state.db`, never the most recently modified file.

Query via `sqlite3` from `execute_code` or `terminal`.

## Pitfall: the lifecycle guard rejects non-regular files

Commands that reference `/dev/null` (or other non-regular files) are blocked by the lifecycle guard, so `diff a b > /dev/null` and trailing `2>/dev/null` can fail even though the command is harmless. Write scratch output to real files under the profile scratch dir instead, and clean them up after.

## Reading refusal behavior

The anti-refusal section of the security posture (live name: `<authorized_security_posture>`) works on exactly one precondition: it settles authorization **over targets the user supplies in-conversation**. A request naming no concrete target ("any website", "some site", "find vulns anywhere") supplies no scope, so the section has nothing to authorize and the base model's refusal prior wins — even though the same section separately forbids asking for clarification about a target. One concrete token (domain / IP / subnet) is what flips it on. When explaining a refusal, say which of the two is in play: missing scope, or a genuinely out-of-scope ask.

Do not infer a section's role from its name alone — read the live variant. Posture sections differ by execution environment and adoption vintage, and an archived draft is not the live text.

## Reporting this kind of analysis

Answer in the user's working language. Quote the live bytes, name the mechanism, and separate observation (the hash-matched prompt) from inference (which section drove the behavior). Do not paste the whole 40K prompt — cite the section and the specific lines.