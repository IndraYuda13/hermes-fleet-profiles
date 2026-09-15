---
name: external-coding-agents
description: Use when delegating a coding, review, or refactoring task to Claude Code, OpenAI Codex, or OpenCode from Hermes.
version: 1.0.0
author: Hermes Agent Curator
license: MIT
metadata:
  hermes:
    tags: [coding-agents, claude-code, codex, opencode, delegation, cli]
    related_skills: [hermes-agent]
---

# External Coding Agents

## Overview

Use an external coding CLI when a bounded autonomous implementation or independent review is more efficient than performing it directly. Keep the agent in one explicit repository or isolated worktree, constrain its permissions to the task, and verify its resulting diff yourself.

## Choose an agent and mode

| Need | Preferred route | Why |
|---|---|---|
| Bounded Claude task or structured analysis | Claude Code print mode | Non-interactive, resumable, supports JSON output and tool allowlists |
| OpenAI Codex implementation/review in a git repository | `codex exec` | Native Codex task execution with sandbox controls |
| Provider-agnostic one-shot or interactive TUI | `opencode run` / OpenCode TUI | Flexible models and simple session continuation |
| Multi-turn conversation with any CLI | Its interactive mode in a tracked background/PTY session | Enables follow-ups and progress checks |

## Shared operating procedure

1. **Preflight:** verify the CLI version and authentication; identify the repository, its rules file, and its focused test command.
2. **Isolate:** use an explicit `workdir`; for concurrent edits use separate git worktrees. Never let two coding agents edit one working tree concurrently.
3. **Bound the task:** give the requirement, relevant paths, expected tests, and a clear stop condition. Prefer read-only permissions for review tasks.
4. **Run the simplest mode:** use a one-shot command for a bounded task. Use a PTY/background session only when follow-up exchange is genuinely required.
5. **Verify independently:** inspect `git diff`, run targeted tests, and do not report the agent's self-description as proof.
6. **Clean up:** stop interactive sessions and remove temporary worktrees only after retaining required evidence.

## Claude Code

Use print mode for most bounded work, e.g. `claude -p '<task>' --max-turns 10` with an explicit workdir and restrictive `--allowedTools` where possible. Use a tmux/PTY session only for iterative work. Capture structured output when a machine-readable result is required. Full command, permission, session, and MCP guidance is in `references/claude-code.md`.

## OpenAI Codex

Codex requires a git repository; use `codex exec '<task>'` for one-shot work and a tracked PTY/background process for long tasks. Prefer its normal sandbox or `--full-auto` for workspace edits. In a gateway/service environment where the sandbox cannot initialize, use `--sandbox danger-full-access` only with an explicit workdir, a clean starting status, and post-run diff/test review. When connecting Codex CLI via custom proxies or gateways, configure `wire_api = "responses"`; routing through standard chat-completions proxies flattens `namespace` tools and prevents `exec`/`apply_patch` execution. See `references/openai-codex.md`.

## OpenCode

Use `opencode run '<task>'` for bounded work; it does not need an interactive TUI. For iteration, start the TUI in a PTY-backed background process, monitor logs, and exit with Ctrl+C rather than `/exit`. Verify the resolved binary and provider authentication if behavior differs between shells. See `references/opencode.md`.

## Runner-specific boundary notes

- **Claude Code:** use `--output-format json` or a JSON schema only when a caller must consume structured output; use `--bare` only when intentionally skipping repository hooks/rules. Prefer `claude -w <name> --tmux` for a managed isolated interactive session rather than a hand-built shared workspace.
- **Codex:** start in a git repository; keep normal sandboxing unless the service context demonstrably cannot initialize it. `danger-full-access` is an explicitly scoped exception, never a default.
- **OpenCode:** resolve the actual binary and provider auth in the shell that will run it. Interactive instances require a PTY and should be stopped with Ctrl+C.

## Common pitfalls

- Treating a CLI's success text as verification rather than running the project check.
- Routing modern Codex CLI through chat-completions translation proxies that discard `namespace` tools—the model produces conversational diffs without invoking disk or exec tools.
- Failing to sanitize delimiters across tool outputs (`function_call_output` / `custom_tool_call_output`)—untrusted shell or diff content containing delimiter tokens triggers indirect tool injection.
- Reusing a working directory across concurrent autonomous editors.
- Sending an unbounded prompt without a test or completion criterion.
- Launching an interactive TUI for a task that a one-shot command can finish.
- Leaving a background TUI alive after the task is complete.

## Verification checklist

- [ ] CLI readiness and auth were checked without exposing credentials.
- [ ] Workdir/worktree scope was explicit and non-conflicting.
- [ ] Diff was read after the agent completed.
- [ ] Targeted project validation was executed and its output inspected.
- [ ] Background sessions and temporary resources were closed or intentionally retained.
