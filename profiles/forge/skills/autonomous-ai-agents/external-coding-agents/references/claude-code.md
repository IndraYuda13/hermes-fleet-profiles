# Claude Code quick reference

For a bounded task, prefer non-interactive print mode in an explicit repository:

```bash
claude -p 'Implement the described change and run the named test' --max-turns 10 --allowedTools 'Read,Edit,Bash'
```

Use `--output-format json` when another process must consume the result. Use a tmux/PTY session only for iterative work; handle workspace trust deliberately, monitor the pane, and close it at completion. Always inspect the generated diff and run the repository's focused validation independently.

## Interactive-mode specifics

- First-run dialogs: workspace trust defaults to "Yes" (press Enter); the `--dangerously-skip-permissions` warning defaults to **"No, exit"** — you must send Down then Enter to accept. Trust is remembered per directory; the permissions dialog recurs every launch.
- `--bare` skips OAuth along with hooks/plugins/MCP — it requires `ANTHROPIC_API_KEY` (or an `apiKeyHelper` in settings).
- `--max-turns` and `--max-budget-usd` apply to print mode only. Budget minimum is ~$0.05 (system-prompt cache creation); a lower value errors immediately.
- Session resumption: capture `session_id` from `--output-format json`, then `claude -p '<next>' --resume <id>`; `--continue` picks the most recent session **in the current directory**. `--fork-session` branches history.
- For live streaming output, `--output-format stream-json --verbose --include-partial-messages` emits newline-delimited events; filter text with `jq -rj 'select(.type == "stream_event" and .event.delta.type? == "text_delta") | .event.delta.text'`.
- Slash commands (e.g. `/compact`, `/review`) work only in interactive mode; in `-p` mode describe the task in natural language.
- Quality degrades measurably above ~70% context-window use — monitor with `/context` and `/compact` proactively in long interactive sessions.
