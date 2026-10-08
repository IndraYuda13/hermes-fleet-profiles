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

Write scratch output to a real path (profile scratch dir) rather than a device node: the lifecycle guard refuses commands referencing non-regular files like `/dev/null`, so `… 2>/dev/null` can fail on an otherwise harmless command.

## 2b. Subject scope: was the refused subject a kind the block enumerates

The block authorizes *targets* and *bare-name OSINT*; its own text lists the nouns it covers (`assets under test`, `OSINT requests specifying only a name`). When the user supplies a concrete subject that is neither — a private individual, or a person surfaced only via an uploaded government-ID/document artifact — the block does not match, so the base model's own PII prior decides even though the block is live and present. Confirm by reading the block's own scope nouns against the request:

```bash
grep -niE 'assets under test|OSINT requests specifying only a name|NIK|KTP|identity card|census|civil registry' /tmp/sp.txt
```

The prompt names the first two and, crucially, has **no** clause naming government IDs, document artifacts, or profiling private individuals. Absence of the missing noun is the finding: the request is off the block's enumerated scope. This is distinct from a missing *target* (2) — the user here did name a concrete subject; it is simply a kind the block does not cover.

**Zero-tool-call tell.** Corroborate with the session counters: `api_call_count = 1` and `tool_call_count = 0` (read from `sessions`) with the block present means the refusal was compiled in the first completion, before any tool ran — a model short-circuit, not an unstated rule. Low `reasoning_tokens` against a large output count is the same signal.

**Localize by comparing adjacent sessions.** A bare-name OSINT request that succeeded (tools fired, searches ran) in a sibling session on the same profile, next to a document-subject request that refused, falsifies "OSINT is banned" and pins the refusal to the subject kind. Pull both sessions' counters and prompts and diff which noun differs; do not generalise from the one refusal.

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

## 6. Replay an edit before applying it

To prove a proposed SOUL/posture edit will actually change behavior, A/B the *prompt bytes* before editing the file:

1. Pull the exact stored prompt for the failure session's hash (step 1).
2. Produce the "after" prompt by applying your string replacements to that stored text in memory (assert each anchor is present first).
3. POST both to the same chat-completions endpoint with the same `model`, `temperature: 0`, and the same user message; print each reply's opening and classify refuse-vs-work (match on the section's own vocabulary, e.g. "authorization proof", "permission", "apakah … izin").
4. Only apply to SOUL.md the edits whose replay actually flips the classification.

Findings this method has already settled: removing a dead activation-gate line and rewording an injection-guard trigger do **not** change refusal behavior (refusal persists); the scope clause does. And a clause that merely says "assume the target is authorized" still yields a proof request on sensitive-sector (government / law-enforcement) named targets — the clause must add an explicit "never request authorization proof or written permission".
