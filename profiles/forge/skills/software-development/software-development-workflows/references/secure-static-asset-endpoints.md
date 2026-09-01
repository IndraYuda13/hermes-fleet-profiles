# Secure Dynamic Static Asset Serving & Path Traversal Testing

## Overview
When serving static or dynamic assets from subdirectories without mounting a full third-party static files middleware, FastAPI/Starlette route handlers must enforce strict canonical path containment and proper media-type negotiation. Additionally, automated tests for traversal vectors must account for client-side URL normalization.

---

## 1. FastAPI Dynamic Path Handler with Path Traversal Guard

```python
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

app = FastAPI()
BASE_ASSETS_DIR = (Path(__file__).resolve().parent / 'assets').resolve()

MEDIA_TYPE_MAP = {
    '.webp': 'image/webp',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.svg': 'image/svg+xml',
    '.json': 'application/json',
    '.ico': 'image/x-icon',
    '.css': 'text/css',
    '.js': 'text/javascript',
}

@app.get('/assets/{asset_path:path}', include_in_schema=False)
async def serve_asset(asset_path: str) -> FileResponse:
    # 1. Resolve target file against base directory
    target_file = (BASE_ASSETS_DIR / asset_path).resolve()

    # 2. Strict path traversal prevention: must remain inside BASE_ASSETS_DIR and be a real file
    if not target_file.is_relative_to(BASE_ASSETS_DIR) or not target_file.is_file():
        raise HTTPException(status_code=404, detail='asset not found')

    # 3. Determine media type and return with caching headers
    suffix = target_file.suffix.lower()
    media_type = MEDIA_TYPE_MAP.get(suffix, 'application/octet-stream')
    return FileResponse(
        target_file,
        media_type=media_type,
        headers={'Cache-Control': 'public, max-age=86400'}
    )
```

---

## 2. Testing Path Traversal Pitfalls (TestClient / HTTPX URL Normalization)

### Pitfall
Standard HTTP client implementations (including `httpx.Client`, `fastapi.testclient.TestClient`, and browser network stacks) normalize relative paths before dispatching the request:
- `client.get('/assets/../styles.css')` resolves client-side to `GET /styles.css`.
- If `/styles.css` is a valid root route, the assertion receives `200 OK` instead of reaching the `/assets` endpoint to test traversal rejection.

### Working Test Pattern
Send encoded traversal sequences so the relative path reaches the route handler intact:
```python
def test_path_traversal_rejection():
    client = TestClient(app)

    # Use encoded slashes and dots to bypass client-side pre-normalization
    r1 = client.get('/assets/..%2fstyles.css')
    assert r1.status_code == 404

    r2 = client.get('/assets/..%2f..%2fapp%2fwebhook.py')
    assert r2.status_code == 404

    r3 = client.get('/assets/%2e%2e%2fstyles.css')
    assert r3.status_code == 404
```

---

## 3. Buyer-Facing Static String Guards
When projects enforce strict term-linting (e.g. forbidding internal architecture keywords like `modal`, `sku`, `cache`, `provider` from leaking to buyer-visible frontend bundles):
- Check CSS comments and token annotations (`--surface-overlay: /* ... */`) in addition to HTML/JS.
- Use customer-facing vocabulary (`dialog`, `popover`, `floating-sheet`) rather than internal framework names (`modal`).
