# Repository Vendorization, Portability, and External Path Decoupling

When decoupling a project from external directories or making a mono-host prototype portable for git distribution, follow this structured pattern.

## 1. Audit and Map External Seams

Audit the repository for machine-specific or external user home directory paths:
```bash
# Search for absolute paths leaking developer homes or external workspaces
search_files(pattern="/root/|/home/|sys\.path\.insert", path=".", target="content")
```

Common leak vectors:
- `sys.path.insert(0, "/path/to/other/repo")` in Python entrypoints.
- Hardcoded cookie, secret, or database paths in config modules.
- Hardcoded `PYTHONPATH` or working directories in systemd service units.
- Absolute paths in documentation, deployment guides, or verification scripts.

## 2. Vendorize Modules Cleanly

1. Copy target modules into an internal directory (e.g. `backend/core/` or `lib/vendor/`).
2. Verify package markers (`__init__.py`).
3. Audit vendorized modules internally for residual references to the old parent repository or machine paths.
4. Avoid circular imports by keeping vendorized utility modules leaf-oriented.

## 3. Dynamic Seam and Path Resolution

Instead of requiring external `PYTHONPATH` or inserting brittle hardcoded absolute strings, implement self-resolving directory resolution in entrypoints:

```python
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

# Enable imports when run either from root or from within the package subdirectory
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Defensive import fallback supporting both top-level and package-namespaced imports
try:
    from core.service_client import ServiceClient
except ImportError:
    from backend.core.service_client import ServiceClient
```

## 4. Secret & State Decoupling (.gitignore + Example Templates)

When decoupling services that rely on local credentials (e.g. Netscape `cookies.txt`, API keys, session tokens):
1. **Verify Git Exclusions**:
   ```bash
   git check-ignore -v backend/cookies.txt
   ```
   Never rely on developer memory; confirm the exact file path is matched by `.gitignore`.
2. **Provide Actionable `.example` Files**:
   Create `<file>.example` (e.g. `cookies.txt.example`) documenting:
   - Format specification (Netscape format vs JSON vs dotenv).
   - Step-by-step export instructions (browser extensions, tools, required auth fields).
   - Valid dummy headers and sample rows.
3. **Flexible Runtime Lookup Hierarchy**:
   Resolution priority order:
   - Direct local file (`BASE_DIR / "cookies.txt"`)
   - Environment variable override (`os.environ.get("SERVICE_COOKIE_PATH")`)
   - Project root fallback (`PROJECT_ROOT / "cookies.txt"`)

## 5. Service & Deployment Synchronization

If the application runs as a systemd service:
1. Update `animestr-backend.service` (or equivalent unit file) in both the repository and `/etc/systemd/system/`.
2. Clean `PYTHONPATH` to reference only repository-internal directories.
3. Run `systemctl daemon-reload` before restarting the service to ensure changes take effect:
   ```bash
   cp repo/my-service.service /etc/systemd/system/my-service.service
   systemctl daemon-reload
   systemctl restart my-service.service
   ```

## 6. Zero-Leak Verification Gate

Before committing and finalizing:
1. `python3 -m py_compile <files>` to verify syntax across all vendorized and calling files.
2. Run an isolated import check using `python3 -c "import backend.main"` from outside the source folder without any external `PYTHONPATH`.
3. Assert HTTP health endpoints return 200 and report loaded state (`cookies_loaded: true`).
4. Re-run `search_files` across the entire repo tree to confirm zero residual hits for the external path.
