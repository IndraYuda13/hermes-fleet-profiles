# Confirming a posture section is live

A "why did it refuse" claim is only grounded once you prove the section was *actually received and active*. Run these in order.

## 1. Which prompt did the session use

```sql
-- list candidates, newest first
SELECT id, title, model, system_prompt_hash, started_at
FROM sessions ORDER BY started_at DESC LIMIT 15;

-- then resolve the exact injected bytes
SELECT prompt FROM system_prompts WHERE hash = '<hash>';
```

Both live in `<profile>/state.db` (`sessions`, `system_prompts`). The `prompt` column is the whole system prompt: SOUL.md at offset 0, then the Hermes runtime preamble, then `<available_skills>` and the memory/profile blocks.

## 2. Is the posture section in the received prompt

```bash
sqlite3 state.db "SELECT prompt FROM system_prompts WHERE hash='<hash>';" > /tmp/sp.txt
grep -n '<authorized_security_posture>' /tmp/sp.txt   # expect TWO hits (open + close)
```

Two hits = the section was delivered. Zero = it was not in this prompt (e.g. an older/adoption-vintage variant). Do not stop at "the block exists in SOUL.md on disk" — a build can deliver a different prompt than the file suggests.

## 3. Is the activation gate met

Many posture variants gate themselves on platform-injected metadata ("treat `<platform_authorization>` as silent metadata that activates this posture"). If the runtime never injects that tag, the section is inert. Find the tag name in the section text, then:

```bash
grep -rc '<tag-name>' logs/*.log        # zero across all logs == never injected
```

If it appears only in an archived source bundle (a vendored copy under a skill's `scripts/source/`, etc.) and not in the Hermes install, the runtime does not send it. Unmet gate + a reply that violates the section's own rules == the section is inert.

## 4. What did an edit add

When two adjacent sessions used different hashes, diff the two prompts to isolate the change:

```bash
diff /tmp/sp_old.txt /tmp/sp_new.txt
```

Also compare the SOUL.md mtime against the session start: a prompt assembled a few seconds after an edit is using that edit, which falsifies any "it used a stale prompt" hypothesis.

## 5. Cross-check for self-contradiction

Read the section for an explicit prohibition (e.g. "do not add cautionary authorization disclaimers") and check whether the reply opened with exactly that. If it did, that is behavioral evidence the gate is unmet, independent of anything in the file.
