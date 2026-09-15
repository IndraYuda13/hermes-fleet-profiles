# Python Test Harness & Strict Warning Verification

## Overview
When auditing and verifying Python test suites under Python 3.12+ (especially with strict warning flags like `pytest -W error` or deprecation verification), follow these guidelines to ensure reproducible and unpolluted test execution.

## 1. Zero-Warning Standards in Modern Python (3.12+)

### UTC Timestamps
* `datetime.datetime.utcnow()` is deprecated since Python 3.12 and scheduled for removal.
* **Fix**: Use `datetime.datetime.now(datetime.timezone.utc)` or `datetime.datetime.now(datetime.UTC)`.
* For ISO 8601 formatting: `datetime.now(timezone.utc).isoformat()`.

### ResourceWarning: Unclosed File Handles
* Naked file opens like `source = open('path/to/file.py').read()` leave file descriptors open until garbage collected. Under strict warning gates (`-W error`), this triggers `ResourceWarning: unclosed file` during runner teardown.
* **Best Practice**:
  ```python
  # Recommended
  from pathlib import Path
  source = Path('path/to/file.py').read_text(encoding='utf-8')
  
  # Or with context manager
  with open('path/to/file.py', 'r', encoding='utf-8') as f:
      source = f.read()
  ```

## 2. Pytest Configuration & Discovery Isolation

* **Discovery Scoping in Monorepos & Multi-Package Trees**: Bare `pytest` recursively discovers all `test_*.py` files across the entire workspace. In repositories containing skill trees, plugins, or heterogeneous tools, this triggers collection crashes:
  - Missing optional dependencies in sibling packages (e.g. `ModuleNotFoundError: No module named 'docx'`).
  - Namespace collisions from identical test filenames across subtrees (`import file mismatch: imported module 'test_core' has this __file__ attribute...`).
* **Root Configuration Requirement**: Always declare explicit test paths and module roots in `pytest.ini` or `pyproject.toml`:
  ```ini
  [pytest]
  testpaths = tests
  pythonpath = .
  ```
* **Ad-Hoc & Unconfigured Execution**: When invoking tests without a root `pytest.ini`, never run bare `pytest` from the workspace root. Always scope the target path and pythonpath explicitly:
  ```bash
  PYTHONPATH=. pytest tests/ -v
  ```
* **Failure Distinction**: Distinguish test collection errors in unconfigured sibling directories from genuine test assertion failures in the target suite before declaring a build or test suite broken.
* **Asyncio Mode**: Set `asyncio_mode = strict` or `auto` explicitly in `pytest.ini` when using `pytest-asyncio`.

## 3. Concurrency & Idempotency Testing

* Test atomic state transitions by simulating concurrent execution (e.g. 2 sequential or simultaneous claims on the same resource) to verify that only one worker acquires the lock/claim while the other receives `None` or an exception.
