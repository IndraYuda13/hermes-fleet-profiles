# Claude Code quick reference

For a bounded task, prefer non-interactive print mode in an explicit repository:

```bash
claude -p 'Implement the described change and run the named test' --max-turns 10 --allowedTools 'Read,Edit,Bash'
```

Use `--output-format json` when another process must consume the result. Use a tmux/PTY session only for iterative work; handle workspace trust deliberately, monitor the pane, and close it at completion. Always inspect the generated diff and run the repository's focused validation independently.
