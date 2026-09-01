# OpenAPI 3.0, Swagger UI & Modern Python Packaging Guide

## 1. Lightweight Standalone Swagger UI & OpenAPI Specification

When integrating interactive documentation into lightweight Python frameworks (Quart, Flask, aiohttp, Starlette) without introducing heavy third-party framework extensions:

### OpenAPI 3.0.3 Spec Route (`/openapi.json`)
- Return a standard Python dictionary conforming to OpenAPI 3.0.3 with `info`, `servers`, `paths`, and `components.schemas`.
- Declare query/body parameters, required flags, examples, and typed error responses for standard API client compatibility.

### Standalone CDN Swagger UI Route (`/swagger`, `/docs`)
- Serve an HTML page embedding Swagger UI directly from CDN (`swagger-ui-dist@5` bundle + standalone preset).
- Point `SwaggerUIBundle({ url: "/openapi.json", dom_id: "#swagger-ui", deepLinking: true })`.
- Apply a clean modern/dark CSS theme (`#0f172a` slate background, `#38bdf8` accent headers, customized `.opblock`, `.responses-inner`, and `.scheme-container`) to avoid default unstyled light mode.
- Provide a navigation header with direct links to Home and raw `/openapi.json`.

---

## 2. PEP 621 / PEP 517 `pyproject.toml` Packaging & Build Validation

### Standard Structure (`setuptools.build_meta`)
```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "package-name"
version = "1.0.0"
description = "Description"
readme = "README.md"
requires-python = ">=3.10"
license = { text = "MIT" }
authors = [{ name = "Author Name" }]
dependencies = [
    "quart>=0.19.0",
]

[project.scripts]
package-cli = "module:entry_function"

[tool.setuptools]
py-modules = ["api_module", "config_module"]
```

### Critical Pitfalls
- **PEP 639 License Conflict:** Never combine `license = ...` in `[project]` with `"License :: OSI Approved :: ..."` inside `classifiers`. Modern setuptools enforces PEP 639 and raises `setuptools.errors.InvalidConfigError: License classifiers have been superseded by license expressions`.
- **Validation Pipeline:** Always verify packaging locally before pushing:
  ```bash
  pip install -e .
  python -m build
  twine check dist/*
  ```

---

## 3. GitHub Actions CI Matrix & Testing Discovery

### Matrix Testing with Fallback Discovery
When projects do not mandate `pytest` or use standard library `unittest`:
```yaml
jobs:
  test-and-lint:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: ['3.10', '3.11', '3.12']
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip
      - run: |
          pip install -r requirements.txt flake8
          python -m py_compile *.py
          flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics --exclude=.venv,build,dist
          python -m unittest discover -s tests -p "test_*.py" -v
```
