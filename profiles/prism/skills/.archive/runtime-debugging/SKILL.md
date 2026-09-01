---
name: runtime-debugging
description: Use when a Python or Node.js failure needs breakpoint-driven inspection, process attachment, stack walking, or environment diagnosis beyond a focused test or normal logs.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [debugging, python, nodejs, pdb, debugpy, inspector, breakpoints]
    related_skills: [systematic-debugging, test-driven-development]
---

# Runtime Debugging

## Overview

Use a debugger after creating a tight reproducible loop and forming a hypothesis. Start with the built-in debugger; attach remote tooling only when the process cannot be restarted or source-free inspection is needed. Keep all inspect/debug ports loopback-bound.

## When to Use

- Tests or services need variable, stack, closure, or state inspection beyond logs.
- A long-running Python/Node process must be attached without rewriting the whole workflow.
- Python imports/packages work in one context but fail in another interpreter or service.

## First Steps

1. Reproduce the exact symptom with a focused command.
2. Trace the failing path and identify the smallest useful breakpoint.
3. Choose the language/runtime tool below.
4. Remove temporary debug code and rerun the repro plus appropriate regression checks.

## Python

| Need | Tool |
|---|---|
| Quick local stop | `breakpoint()` / pdb |
| Launch without source edit | `python -m pdb script.py` |
| Pytest failure inspection | `pytest --pdb` without xdist |
| Long-running or IDE attach | `python -m debugpy --listen 127.0.0.1:5678 ...` |

For a running service, verify the interpreter and package location before installing anything:

```bash
python3 -c 'import sys; print(sys.executable); print("\n".join(sys.path))'
python3 -m pip show <distribution>
python3 -c 'import <module>; print(<module>.__file__)'
```

A systemd `ExecStart` that selects a different Python/venv is often the root cause. Check module shadowing and distribution-vs-import naming before changing versions.

## Node.js

| Need | Tool |
|---|---|
| Start paused | `node inspect script.js` or `node --inspect-brk script.js` |
| Attach to running process | `kill -SIGUSR1 <pid>` then `node inspect -p <pid>` |
| Programmatic inspection | Chrome DevTools Protocol client |

Use `--inspect-brk` when breakpoints must be set before startup code runs. Bind to `127.0.0.1`; exposing inspector ports permits arbitrary code execution.

## Common Pitfalls

- pdb under pytest-xdist appears to hang—disable xdist for that run.
- `breakpoint()` in CI/non-TTY contexts can block forever; remove it before commit.
- An attached inspector does not automatically include child processes.
- Debugger success is not a regression test; return to the original focused loop.
- Do not blindly retry package installs; first compare executable, `sys.path`, and installed distribution.

## Verification Checklist

- [ ] The debug target and loopback port are the intended process.
- [ ] The suspected state was observed at a relevant breakpoint.
- [ ] The root cause, not only the symptom, was identified.
- [ ] Temporary debug hooks were removed.
- [ ] The focused repro and regression checks were rerun.
