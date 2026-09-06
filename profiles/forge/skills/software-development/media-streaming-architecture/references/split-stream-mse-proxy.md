# Split-Stream MSE & Stateless Proxy Architecture Reference

## 1. Nginx Reverse Proxy Configuration

Untuk melayani endpoint video streaming proxy dengan penanganan Range request yang efisien tanpa disk write:

```nginx
# /etc/nginx/sites-available/stream.indrayuda.my.id

server {
    server_name stream.indrayuda.my.id;

    # Frontend SPA
    location / {
        root /var/www/stream-frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # API backend
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Video stream proxy passthrough
    location /api/stream/proxy {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_buffering off;
        
        # Range header forwarding
        proxy_set_header Range $http_range;
        proxy_set_header If-Range $http_if_range;
        
        # Timeouts for streaming
        proxy_connect_timeout 5s;
        proxy_read_timeout 60s;
        proxy_send_timeout 60s;
    }
}
```

## 2. FastAPI Streaming Proxy Implementation

Pola implementasi async passthrough stream dengan FastAPI & httpx:

```python
import hmac
import hashlib
import urllib.parse
from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.responses import StreamingResponse
import httpx

app = FastAPI()
SECRET_KEY = b"your-super-secret-key-change-in-prod"
ALLOWED_HOST_SUFFIXES = (
    ".bilivideo.com",
    ".bilivideo.cn",
    ".bilibili.tv",
    ".akamaized.net"
)

def verify_token(raw_url: str, exp: int, token: str) -> bool:
    payload = f"{raw_url}:{exp}".encode("utf-8")
    expected = hmac.new(SECRET_KEY, payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, token)

def is_allowed_host(url_str: str) -> bool:
    try:
        parsed = urllib.parse.urlparse(url_str)
        if parsed.scheme not in ("http", "https"):
            return False
        if parsed.username or parsed.password:
            return False
        host = (parsed.hostname or "").lower()
        return any(host == s.lstrip(".") or host.endswith(s) for s in ALLOWED_HOST_SUFFIXES)
    except Exception:
        return False

@app.get("/api/stream/proxy")
async def stream_proxy(request: Request, url: str, exp: int, token: str):
    if not verify_token(url, exp, token):
        raise HTTPException(status_code=403, detail="Invalid or expired stream token")
    
    if not is_allowed_host(url):
        raise HTTPException(status_code=400, detail="Disallowed target host")

    upstream_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": "https://www.bilibili.tv/"
    }
    
    # Forward client range if present
    client_range = request.headers.get("range")
    if client_range:
        upstream_headers["Range"] = client_range

    client = httpx.AsyncClient(follow_redirects=False, timeout=15.0)
    
    try:
        req = client.build_request("GET", url, headers=upstream_headers)
        upstream_res = await client.send(req, stream=True)
        
        # Build response headers
        res_headers = {}
        for h in ("content-type", "content-length", "content-range", "accept-ranges", "etag"):
            if h in upstream_res.headers:
                res_headers[h] = upstream_res.headers[h]
        
        async def body_stream():
            try:
                async for chunk in upstream_res.aiter_bytes(chunk_size=65536):
                    if await request.is_disconnected():
                        break
                    yield chunk
            finally:
                await upstream_res.aclose()
                await client.aclose()

        return StreamingResponse(
            body_stream(),
            status_code=upstream_res.status_code,
            headers=res_headers
        )
    except Exception as e:
        await client.aclose()
        raise HTTPException(status_code=502, detail=f"Upstream stream error: {e}")
```
