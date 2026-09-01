# Python environment diagnosis reference

Use the exact interpreter that starts the failing process. First run a direct import and inspect its identity:

```bash
/path/to/python -c 'import sys, pkgutil; print(sys.executable); print(sys.path); import PACKAGE; print(PACKAGE.__file__)'
/path/to/python -m pip show DISTRIBUTION
```

## Check in this order

1. Import name versus distribution name (for example, `bs4` vs `beautifulsoup4`).
2. A local `package.py` / `package/` shadowing the intended dependency.
3. Venv/interpreter mismatch between `pip`, interactive Python, and the app command.
4. Wrong package or incompatible version when an imported symbol is absent.
5. Dependency-conflict warnings rather than repeatedly reinstalling the same package.
6. For systemd, inspect `ExecStart`, `Environment`, and the service user's paths; restart only after the unit points to the intended interpreter.

Confirm the direct import with the production interpreter after each change.
