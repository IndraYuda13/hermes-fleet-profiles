---
name: python-package-troubleshooting
description: "Diagnose and resolve common Python package installation and import errors (e.g., ModuleNotFoundError, mismatched library versions/imports)."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Python, pip, troubleshooting, debugging, packages]
    related_skills: [systematic-debugging, python-debugpy]
---

# Python Package Troubleshooting

This skill provides a systematic approach for diagnosing and resolving Python package installation, import, and versioning issues. Apply this when encountering `ModuleNotFoundError`, `ImportError`, or situations where a package is installed but cannot be imported or behaves unexpectedly.

## Trigger Scenarios

- A script fails with `ModuleNotFoundError` or `ImportError`.
- A package is installed (e.g., via `pip install X`) but `import X` fails.
- A package is installed, but `from X import Y` throws `ImportError: cannot import name 'Y' from 'X'`.
- Running a Python script fails due to missing dependencies not listed in `requirements.txt`.
- Mismatches between expected package functionality and the currently installed version.

## Pitfalls & Core Rules

1.  **Do Not Blindly Retry:** If `pip install X` fails or `import X` fails after a successful install, do not just run the exact same command again. This creates a loop. Analyze *why* it failed.
2.  **Verify the Package Name:** The name you import (e.g., `import bs4`) is often different from the name you install (e.g., `pip install beautifulsoup4`). If `pip install X` fails to find the package, search PyPI or the web to find the correct package name.
3.  **Check for Name Collisions (Shadowing):** Ensure the script isn't named the same as a standard library module or a third-party package (e.g., a file named `csv.py` will break `import csv`).
4.  **Virtual Environments (venv):** Always verify if the script should be run inside a virtual environment. If so, ensure the `pip install` and `python` commands are executed *using that environment's binaries* (e.g., `source venv/bin/activate && pip install X` or `/path/to/venv/bin/pip install X`).
5.  **Look for Alternative Packages/Forks:** If a specific class or function is missing from a package (e.g., `ImportError: cannot import name 'XVideos' from 'xvideos'`), it's highly likely you have installed a generic or outdated package sharing the namespace.
    -   *Action:* Search for forks or alternative packages providing that specific functionality (e.g., `xvideos-py`, `xvideos-api`, `xvideos-dl` instead of just `xvideos`).
6. **Dependency Conflicts:** If `pip install` warns about dependency conflicts (e.g., `ERROR: pip's dependency resolver does not currently take into account...`), pay attention. You may need to downgrade or upgrade specific packages (e.g., `pip install rich==14.3.3`) to satisfy all requirements for the project.
7.  **Systemd Services vs Global vs Venv Python Paths:** When troubleshooting Python issues for daemons/background services managed by systemd, a common pitfall is path mismatch.
    -   *Systemd ExecStart:* Often hardcodes `/usr/bin/python3`, which runs using system global site-packages.
    -   *Venv vs Global mismatch:* If libraries (like Telethon) are installed inside a local workspace venv or global environment at different times, running the script with the wrong python binary can cause runtime crashes (e.g., `ValueError: too many values to unpack` in Telethon due to SQLite session format differences between version 1.25 and 1.44).
    -   *Action:* Explicitly configure `ExecStart` in systemd services to point to the correct python interpreter binary (e.g., `/usr/local/lib/hermes-agent/venv/bin/python3`) that carries the compatible packages. Run `sudo systemctl daemon-reload && sudo systemctl restart <service>` after editing.

## Systematic Debugging Steps

### Step 1: Identify the Exact Error

Read the traceback carefully.
-   Is it a `ModuleNotFoundError`? (Package not installed or not in the Python path).
-   Is it an `ImportError`? (Package installed, but the specific module, class, or function is missing).

### Step 2: Test the Import Directly

Before modifying the script, verify the import in a clean Python shell:

```bash
python3 -c "import <module_name>; print(dir(<module_name>))"
```

If this fails, the package is either missing, installed in a different environment, or broken.

### Step 3: Verify the Environment

Determine where Python is looking for packages:

```bash
python3 -c "import sys; print('\n'.join(sys.path))"
pip show <module_name>
```

If `pip show` works but the script fails, they are using different environments.

### Step 4: Resolve Naming / Import Mismatches

If `import X` works but `from X import Y` fails (and you expect `Y` to exist):
1.  Check the contents of the installed package: `python3 -c "import X; print(dir(X))"`.
2.  If `Y` is missing, you likely have the wrong package installed under the namespace `X`.
3.  Uninstall the incorrect package: `pip uninstall -y X`.
4.  Search for the correct package (e.g., via web search or checking project documentation/memory) and install it.
5.  Test the import again.

### Step 5: Handle Missing Requirements

If a script requires a package not explicitly listed in `requirements.txt`:
1. Install it manually.
2. Consider adding it to the `requirements.txt` or updating the project documentation so future deployments don't hit the same error.

## Example: The "Wrong Package Namespace" Scenario

**Problem:**
Script contains: `from xvideos import XVideos`
Error: `ImportError: cannot import name 'XVideos' from 'xvideos'`

**Analysis:**
The package `xvideos` is installed, but it doesn't contain the `XVideos` class. This means the PyPI package named `xvideos` is not the package the script author intended to use.

**Resolution Path:**
1.  Uninstall the wrong package: `pip uninstall -y xvideos`
2.  Search for the correct package (e.g., `xvideos-py`, `xvideos-dl`, `xvideos-api`).
3.  Install candidates and test:
    ```bash
    pip install xvideos-py
    python3 -c "from xvideos import XVideos; print(XVideos)"
    ```
4.  If successful, the issue is resolved. If not, repeat with another candidate or modify the script to match the API of the available package.