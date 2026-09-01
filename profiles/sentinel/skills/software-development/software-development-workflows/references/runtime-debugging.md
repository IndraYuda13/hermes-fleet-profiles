# Runtime Debugging

Use breakpoint-driven inspection only after the parent workflow has a focused reproducer and a falsifiable hypothesis.

## Python

- Local: `breakpoint()` / pdb.
- No source edit: `python -m pdb script.py`.
- Test failure: `pytest --pdb` with xdist disabled.
- Long-running/IDE attach: `python -m debugpy --listen 127.0.0.1:5678 ...`.

Before changing packages, compare the interpreter that runs the service with `python -m pip` and the imported module path. For systemd, inspect `ExecStart`; a different venv/interpreter or local module shadowing is often the cause.

## Node.js

- Start paused: `node inspect script.js` or `node --inspect-brk script.js`.
- Attach: `kill -SIGUSR1 <pid>`, then `node inspect -p <pid>`.
- Use a CDP client only when repeatable programmatic inspection is necessary.

Keep inspector/debugger ports on `127.0.0.1`. Remove temporary hooks before committing and rerun the original focused repro plus regression checks.
