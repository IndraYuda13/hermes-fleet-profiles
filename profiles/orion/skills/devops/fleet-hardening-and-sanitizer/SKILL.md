---
name: fleet-hardening-and-sanitizer
description: Protocol for fail-closed fleet review packaging, secret sanitization, and v0.20.2 delegation/worktree E2E verification.
user-invocable: true
metadata:
  hermes:
    tags: [sanitizer, review-bundle, delegation-control, worktree-isolation, verification, fleet-v32]
    category: devops
    requires_toolsets: [terminal, file]
---

# Fleet v3.2 Review Packaging, Sanitization, and E2E Verification Protocol

## 1. Fail-Closed Review Packaging Protocol (`fleet-review-bundle`)
When exporting fleet configurations, memories, and prompts for external architecture reviews or auditing:

1. **Zero Credential-Derived Literals:** Never encode known, rotated, partial, or real password strings in the sanitizer source. Use generic structural regexes matching key name shapes (`api_key:`, `password:`, `token:`, `Bearer`, `http://user:pass@host`).
2. **Context-Aware Secret Redaction:** Redact values only when matching sensitive key contexts (e.g. `password_hash:`, `credential_verifier:`). Preserve generic checksums, artifact digests, and Git commit SHAs (`sha256: <64-hex>`).
3. **No Unscanned Tooling Exemptions:** All staged files—including the bundler script itself under `review_tooling/`—must pass through the fail-closed scanner.
4. **Deterministic Self-Test:** Use synthetic positive fixtures (base64-encoded to keep the scanner source clean) and negative fixtures to guarantee 100% positive detection and 0 false positives.

## 2. Delegation Control & Worktree Verification Protocol (Hermes v0.20.2)
1. **Live Orchestration (`delegate_task`):**
   - Use `action='list'` to monitor running subagents and execution times.
   - Use `action='steer'` with `subagent_id` to inject course corrections without interrupting in-flight tool calls.
   - Use `action='stop'` with `subagent_id` to cleanly request interruption at the next iteration boundary.
2. **Structured Output Contract:** Enforce `output_schema` for all machine-consumed return payloads. When invalid, parse errors and use `build_retry_message` for bounded correction retries.
3. **Truncation Guard:** Any child result reaching `max_iterations` must be marked incomplete and rejected as valid PASS evidence.
4. **Worktree Isolation:** Subagents on coding profiles (`FRAME` and `FORGE`) must work in isolated Git worktrees (`.worktrees/subagent_*`) with independent branches to prevent checkout collisions on the parent repository.
