---
name: cpanel-gsc-publishing-ops
description: Use when running cPanel uploads or GSC indexing pipelines.
version: 1.1.0
author: ORION
license: proprietary
metadata:
  hermes:
    tags: [cpanel, gsc, publishing, indexing, python, dailyfinance, reverse-proxy]
    related_skills: [dailyfinance-seo-mastery, cloudflare-tunnel-operations]
---

# cPanel & Google Indexing Publication Pipeline Operations

## When to Use

Use this skill when:
- Executing or troubleshooting standalone article publishing scripts (`publisher_engine.py`, `publish_*.py`).
- Handling cPanel UAPI file operations via `cpanel_pinjolresmi.py`.
- Submitting newly published or updated URLs to Google Search via `gsc_indexing.py`.
- Reconstructing missing or deleted helper utilities (`cpanel_pinjolresmi.py`, `gsc_indexing.py`) from bytecode caches.
- Upscaling low-resolution vector graphics or infographics for Google Discover compliance.
- Provisioning cPanel subdomains and issuing AutoSSL for internal services or CMS gateways.
- Bridging cPanel subdomains to private VPS backends via transparent PHP cURL reverse proxy gateways.

## Core Procedures & Standards

### 1. Standalone Publishing Script Setup (`sys.path` Hierarchy)
Standalone publishing scripts (such as `publish_bansos_article.py` or batch loaders) must ALWAYS prepend both `/root` and the website mirror directory before importing `publisher_engine`:
```python
import sys
# /root contains cpanel_pinjolresmi.py and gsc_indexing.py
sys.path.insert(0, '/root')
sys.path.insert(0, '/root/dailyfinance_web')

import publisher_engine
```
*Pitfall:* `publisher_engine.py` executes top-level imports of `cpanel_pinjolresmi` and `gsc_indexing`. Failing to insert `/root` causes an immediate `ModuleNotFoundError` even if `dailyfinance_web` is in `sys.path`.

### 2. cPanel File API Return Signature & Verification
- `cpanel_pinjolresmi.list_files(remote_dir='public_html')`: Returns a raw Python `list` of file dictionaries (each containing keys like `'file'`, `'size'`, `'mtime'`). It does NOT return a wrapper dictionary.
  - Correct check: `len(res)` or `[f.get('file') for f in res]`.
  - Anti-pattern: `res.get('status')` throws `AttributeError: 'list' object has no attribute 'get'`.
- `cpanel_pinjolresmi.upload_file(remote_dir, remote_filename, content, content_type='text/html', overwrite=True)`:
  - Argument name is `remote_filename`, NOT `filename`.
  - Always verify upload response: `res.get('status') == 1`.

### 3. Google Indexing API Operations
- Script location: `/root/gsc_indexing.py`.
- Credentials file: `/root/.hermes/gsc_service_account.json` (Service Account: `gsc-bot@jovial-backup-484516-f6.iam.gserviceaccount.com`).
- Property URL: `sc-domain:dailyfinance.id` with `siteOwner` permission.
- Status verification:
  ```bash
  /usr/local/lib/hermes-agent/venv/bin/python /root/gsc_indexing.py status
  ```
- URL notification push:
  ```bash
  /usr/local/lib/hermes-agent/venv/bin/python /root/gsc_indexing.py push <url1> [url2 ...]
  ```
- Always verify output reports `0 failed` across submitted URLs (article HTML, `index.html`, and `blog.html`).

### 4. Bytecode Recovery Protocol for Lost Utilities
If `/root/cpanel_pinjolresmi.py` or `/root/gsc_indexing.py` is removed or corrupted:
1. Python compiles modules into `/root/__pycache__/` (e.g. `cpanel_pinjolresmi.cpython-311.pyc`, `gsc_indexing.cpython-311.pyc`).
2. Read and inspect AST constants and code objects using `marshal.load()` with offset 16 (skipping the 16-byte .pyc header in Python 3.11+).
3. Use Python's built-in `dis.dis()` to extract exact function logic, variable names, and API endpoints.
4. Regenerate clean source code directly from verified bytecode rather than re-inventing authentication or parameter logic.

### 5. Low-Resolution Vector & Infographic Upscaling (Google Discover ≥1200px)
When essential graphics or infographics exist only as low-resolution thumbnails (e.g. 319x181 or 474x270 px) and no native high-resolution asset can be sourced:
1. Resample to standard 16:9 landscape (1280x720 px) using high-grade Lanczos interpolation:
   ```python
   from PIL import Image, ImageOps, ImageFilter

   im = Image.open(src_path)
   im = ImageOps.exif_transpose(im)
   im_rgb = im.convert('RGB')
   im_resized = im_rgb.resize((1280, 720), Image.Resampling.LANCZOS)
   ```
2. Apply a subtle unsharp mask filter to restore line contrast and eliminate edge softening:
   ```python
   im_sharp = im_resized.filter(ImageFilter.UnsharpMask(radius=1.5, percent=120, threshold=3))
   im_sharp.save(out_webp_path, 'WEBP', quality=88)
   ```
3. This satisfies Google Discover's mandatory ≥1,200px width requirement while maintaining sharp vector outlines and typography without ringing artifacts.

### 6. cPanel Subdomain Provisioning & AutoSSL Workflow
When a dedicated subdomain (such as `cms.dailyfinance.id`) is required on a domain hosted on cPanel:
1. Always keep project services on the target project's own domain; never deploy them under an unrelated personal domain.
2. Create the subdomain via UAPI:
   ```python
   cpanel.uapi('SubDomain', 'addsubdomain', domain='cms', rootdomain='dailyfinance.id', dir='public_html/cms')
   ```
   This creates the Document Root directory and adds the local DNS A record pointing to the cPanel host IP.
3. Trigger and verify AutoSSL:
   ```python
   cpanel.uapi('SSL', 'start_autossl_check')
   # Check installed certificate hosts
   hosts = cpanel.uapi('SSL', 'installed_hosts')['cpanelresult']['data']
   ```
4. Verify HTTPS TLS handshake: `curl -sSI https://cms.dailyfinance.id`.

### 7. Transparent PHP Reverse Proxy Gateway Architecture (cPanel to Private Tunnel)
When connecting a public cPanel subdomain to a daemon running on an internal VPS without inbound open ports:
1. Do not rely on Apache `mod_proxy` (`RewriteRule [P]`) or Python CGI scripts on LiteSpeed/cPanel — Apache mod_proxy frequently fails with SSL upstream handshake errors to Cloudflare edges, and CGI scripts trigger permission / chroot issues (`lscgid: execve(): Permission denied`).
2. Deploy a lightweight, transparent PHP cURL proxy (`index.php`) and `.htaccess` in the subdomain document root (e.g. `public_html/cms/`):
   - `.htaccess`: Forces HTTPS and routes all incoming requests to `index.php`:
     ```apache
     RewriteEngine On
     RewriteCond %{HTTPS} off
     RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
     RewriteCond %{REQUEST_FILENAME} !-f
     RewriteCond %{REQUEST_FILENAME} !-d
     RewriteRule ^(.*)$ index.php [QSA,L]
     ```
   - `index.php`: Captures the HTTP request method, incoming headers (stripping conflicting hop-by-hop headers like Host/Transfer-Encoding), request body (supporting JSON, raw text, and multipart/form-data binary uploads), executes cURL to a private Cloudflare Tunnel ingress URL (e.g. `https://cms-backend.indrayuda.my.id`), rewrites response `Location` redirect headers back to the public subdomain, and relays `Set-Cookie` headers for session persistence.
3. Testing form submission & redirects:
   - When validating POST authentication (e.g. `/login`), never test with `curl -L -X POST` — curl repeats POST across 302 redirects, triggering `405 Method Not Allowed` on GET-only target pages.
   - Separate into two discrete requests:
     ```bash
     # 1. Authenticate and write cookie jar
     curl -s -c /tmp/cookie.txt -d "password=..." https://cms.dailyfinance.id/login
     # 2. Access protected endpoint via GET with cookie
     curl -s -b /tmp/cookie.txt https://cms.dailyfinance.id/
     ```

## Pitfalls & Anti-Patterns (Rule + WHY)

- **Always keep project tools and CMS services strictly on the project's own domain — never default to personal domains.** Placing a business portal's administration panel or CMS on an unrelated personal domain breaks brand credibility, causes user confusion, and complicates domain-level access controls.
- **Never use Apache `RewriteRule [P]` (mod_proxy) or CGI scripts in cPanel to proxy HTTPS traffic to Cloudflare Tunnel edges — Apache mod_proxy often fails with 500 errors on upstream SNI/SSL handshakes, and CGI triggers LiteSpeed permission blocks.** Deploy a transparent PHP cURL proxy (`index.php`) that forwards raw request bodies, handles multipart uploads, rewrites `Location` redirect headers, and preserves session cookies.
- **Do not use `curl -L -X POST` to test authenticated login flows across 302 redirects — curl re-uses POST against the redirected GET URL, causing false `405 Method Not Allowed` errors.** Store the session cookie on the initial POST with `-c cookie.txt`, then query the redirected URL via standard GET using `-b cookie.txt`.
