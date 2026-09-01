# OpenAI Codex quick reference

Codex runs from a git repository. For a one-shot task:

```bash
codex exec 'Make the specified focused change and run its tests'
```

Use the normal sandbox or `--full-auto` for intentional workspace edits. If Codex runs under a service context where its sandbox cannot initialize, `--sandbox danger-full-access` is an exception—not a default—and requires a narrow workdir, clean baseline, and independent diff/test review. Use separate worktrees for concurrent Codex tasks.
