---
name: google-search-console-automation
description: Use when automating Google Search Console API operations.
version: 1.6.0
author: Orion Fleet Lead
license: MIT
metadata:
  hermes:
    tags: [gsc, google-search-console, seo, indexing, sitemaps, oauth2, jwt]
    category: api-management
---

# Google Search Console (GSC) API Automation

## When to Use

Use this skill when:
1. Setting up headless, automated interaction with the Google Search Console (Webmasters) API.
2. Checking real-time indexing status and crawl history of URLs via the URL Inspection API.
3. Submitting or auditing sitemaps programmatically without manual browser clicks.
4. Extracting search analytics (clicks, impressions, CTR, average position, queries, landing pages).
5. Onboarding new domain properties, executing domain rebranding migrations, and automating DNS TXT ownership verification.

---

## 1. Authentication & Service Account Protocol

### A. The API Key Trap
* **Critical Rule**: Google Search Console API **strictly rejects** standard Google Cloud API keys with HTTP 400 (`API keys are not supported by this API`).
* Authentication must use OAuth2 with either User OAuth credentials or a **Google Cloud Service Account**.

### B. Service Account Setup Workflow
1. In Google Cloud Console (*IAM & Admin* -> *Service Accounts*):
   - Create a service account (e.g. `gsc-bot@<project-id>.iam.gserviceaccount.com`).
   - In the service account details, open the **Keys** tab -> *Add Key* -> *Create new key* -> choose **JSON**.
2. In Google Search Console (*Settings* ⚙️ -> *Users and permissions*):
   - Click **Add user** -> enter the service account email.
   - **Crucial Permission Requirement**: Assign **Owner** (*Pemilik*) permission if using the Web Search Indexing API. Assigning **Full** (*Penuh*) is sufficient for Webmasters/Sitemaps API but causes HTTP 403 `PERMISSION_DENIED: Failed to verify the URL ownership` on `urlNotifications:publish`.
3. Secure the downloaded JSON key file on the server (e.g. `chmod 600 ~/.hermes/gsc_service_account.json`).

### C. Zero-Dependency JWT Token Exchange (RS256)
Rather than installing heavy client libraries (`google-api-python-client`), generate an RS256-signed JWT assertion directly using standard Python `cryptography`:

```python
import time, json, urllib.request, urllib.parse, ssl, base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

def get_gsc_access_token(creds_path):
    with open(creds_path, 'r') as f:
        key_data = json.load(f)

    now = int(time.time())
    payload = {
        "iss": key_data['client_email'],
        "scope": "https://www.googleapis.com/auth/webmasters https://www.googleapis.com/auth/webmasters.readonly https://www.googleapis.com/auth/indexing",
        "aud": key_data['token_uri'],
        "exp": now + 3600,
        "iat": now
    }
    header = {"alg": "RS256", "typ": "JWT"}

    def b64url(b):
        return base64.urlsafe_b64encode(b).decode('utf-8').rstrip('=')

    header_b64 = b64url(json.dumps(header).encode('utf-8'))
    payload_b64 = b64url(json.dumps(payload).encode('utf-8'))
    signing_input = f"{header_b64}.{payload_b64}".encode('utf-8')

    priv_key = serialization.load_pem_private_key(key_data['private_key'].encode('utf-8'), password=None)
    sig = priv_key.sign(signing_input, padding.PKCS1v15(), hashes.SHA256())
    sig_b64 = b64url(sig)

    assertion = f"{header_b64}.{payload_b64}.{sig_b64}"
    post_data = urllib.parse.urlencode({
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": assertion
    }).encode('utf-8')

    ctx = ssl.create_default_context()
    req = urllib.request.Request(key_data['token_uri'], data=post_data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
        return json.loads(resp.read().decode('utf-8')).get('access_token')
```

### D. Interpreter Selection Pitfall
* Default system Python 3 on Linux hosts frequently lacks the `cryptography` library (`ModuleNotFoundError: No module named 'cryptography'`).
* Always point script shebangs or executions to the active virtual environment containing cryptography (e.g. `#!/usr/local/lib/hermes-agent/venv/bin/python3`).

---

## 2. Site Property Identifier & Domain Verification Protocol

### A. Site Property Types
Google Search Console has two property types:
1. **Domain Properties**: Covers all subdomains and protocols (`http`, `https`, `www`, non-www).
   - Format: `sc-domain:<domain>` (e.g. `sc-domain:example.com`). Requires DNS verification (TXT record).
2. **URL-Prefix Properties**: Covers exact protocol and directory.
   - Format: `https://example.com/`. Supports HTML file, meta tag, GTM, or DNS verification.

* **REST Path URL Encoding**: When constructing URL paths in the Webmasters API v3, always URL-encode the site identifier:
  `sc-domain:example.com` becomes `sc-domain%3Aexample.com`.

### B. DNS TXT Verification & Google DNS Propagation Preflight Gate
When onboarding a domain property or migrating domains:
1. Google generates a verification token: `google-site-verification=<token>`.
2. Publish as a `TXT` record on host `@` (or `<domain>.`) with TTL 3600.
3. **The Premature "Verify" Click Trap**:
   - Authoritative nameservers update immediately upon record insertion. However, Google's verification backend queries public recursive resolvers (specifically Google Public DNS `8.8.8.8`), which routinely cache previous negative responses (NXDOMAIN or prior empty TXT sets) for 30–120 seconds.
   - Directing the user or automated workflow to click "Verify" immediately results in a failed check and can trigger UI rate-limiting cooldowns.
   - **Verification Preflight Gate**: Always query Google DNS directly from the terminal before triggering verification:
     `dig @8.8.8.8 <domain> TXT +short | grep google-site-verification`
     Only advise the user to click "Verify" or trigger automated verification once `8.8.8.8` returns the verification token.

### C. Domain Migration & Rebranding Protocol
- GSC properties are strictly bound to their exact domain name; changing website domains (e.g. `old-domain.com` -> `new-domain.com`) does NOT transfer Search Console properties automatically.
- Setup sequence for rebranded sites:
  1. Register the new domain property `sc-domain:<new-domain>`.
  2. Complete DNS TXT verification via the preflight gate.
  3. Add the service account (`gsc-bot@...`) as **Owner** or **Full** user in *Settings -> Users and permissions* of the new property.
  4. Submit the new sitemap (`PUT /sitemaps/https%3A%2F%2F<new-domain>%2Fsitemap.xml`) via API.
  5. If the old domain is retained, configure HTTP 301 redirects and submit a Change of Address request in GSC settings. If the old domain is decommissioned, treat the new domain as a standalone property.

---

## 3. Core Operational Endpoints & Sitemaps

### A. List and Submit Sitemaps
* **List**: `GET https://www.googleapis.com/webmasters/v3/sites/{site_url_enc}/sitemaps`
* **Submit**: `PUT https://www.googleapis.com/webmasters/v3/sites/{site_url_enc}/sitemaps/{sitemap_url_enc}`
  - Returns HTTP 204 No Content on successful registration.

### B. Deprecation of GET Sitemap Ping Endpoints
* **Crucial Deprecation Notice**: Public GET ping URLs (`https://www.google.com/ping?sitemap=...` returning HTTP 404, and `https://www.bing.com/ping?sitemap=...` returning HTTP 410) were officially retired by search engines.
* Programmatic sitemap notifications must strictly use the GSC Webmasters API v3 `PUT .../sitemaps/{sitemap_url_enc}` method.

### C. The "Couldn't Fetch" (Pseudo-Error) UI Quirk on Pending Sitemaps
* **The Symptom**: Immediately after submitting a new sitemap, the GSC Web UI displays a red status label: `"Couldn't fetch"` / `"Tidak dapat mengambil peta situs"` with Type `"Unknown"` / `"Tidak diketahui"` and discovered URLs: 0.
* **The Mechanism**: GSC queues newly submitted sitemaps in an asynchronous background pipeline. When inspected via API (`GET /sitemaps`), the entry actually has `"isPending": true`, `"warnings": "0"`, `"errors": "0"`. The web dashboard renders `isPending: true` using the red "Couldn't fetch" error style until the worker queue processes the file.
* **Operational Rule**: Never delete and resubmit a sitemap showing this status. Resubmitting merely resets its position in the queue. Verify state via API: if `isPending: true` and `errors: 0`, advise the user to wait 1–12 hours for the status to transition to "Success" automatically.

### D. Server-Side Hardening for Googlebot Sitemap Crawling
Ensure web servers (Apache, Nginx, LiteSpeed) satisfy these headers for sitemaps:
1. **Enforce HTTPS Redirect**: If `http://domain.com/sitemap.xml` returns 200 without redirecting, Googlebot can encounter protocol split issues. Enforce 301 redirect to HTTPS.
2. **Proper MIME Type**: Serve `.xml` files with `Content-Type: text/xml; charset=UTF-8` or `application/xml`.
3. **Cache Invalidation**: Set `Cache-Control: no-cache, no-store, must-revalidate` on `sitemap.xml` so updates reflect immediately.
4. **CORS Header**: Add `Access-Control-Allow-Origin: *` to prevent cross-origin fetch failures in auxiliary diagnostic tools.

---

## 4. URL Inspection & Indexing Triage

### A. URL Inspection API
Inspect real-time indexing status without waiting for aggregated dashboard charts:
* **Endpoint**: `POST https://searchconsole.googleapis.com/v1/urlInspection/index:inspect`
* **Payload**:
  ```json
  {
    "inspectionUrl": "https://example.com/target-page.html",
    "siteUrl": "sc-domain:example.com"
  }
  ```
* **Status Triage Matrix**:
  | `verdict` | `coverageState` | Operational Meaning & Immediate Action |
  | :--- | :--- | :--- |
  | `PASS` | `Submitted and indexed` | Page is actively crawled and live in Google index. Check `lastCrawlTime` to verify freshness. |
  | `NEUTRAL` | `URL is unknown to Google` | Page URL is registered in sitemap queue but Googlebot has not visited yet. Normal for newly deployed content. |
  | `FAIL` | `Crawled - currently not indexed` or `Discovered - currently not indexed` | Quality, thin content, canonical, or server response issue. Requires content/E-E-A-T audit. |

#### Executable Python Inspection Function
```python
def inspect_url_status(creds_path, site_url, target_url):
    token = get_gsc_access_token(creds_path)
    inspect_url = "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect"
    payload = json.dumps({"inspectionUrl": target_url, "siteUrl": site_url}).encode('utf-8')
    req = urllib.request.Request(
        inspect_url,
        data=payload,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST"
    )
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
        res = json.loads(resp.read().decode('utf-8'))
        return res.get("inspectionResult", {}).get("indexStatusResult", {})
```

#### Executable Concurrent Full-Site Inspection Script
When auditing indexing across dozens of URLs (e.g. from `sitemap.xml`), never inspect sequentially (each request takes 2–4s, causing script timeouts). Use `ThreadPoolExecutor` with per-request timeouts:

```python
import concurrent.futures, json, urllib.request, xml.etree.ElementTree as ET

def audit_all_sitemap_urls(creds_path, site_url, sitemap_path, max_workers=5):
    token = get_gsc_access_token(creds_path)
    inspect_url = "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect"
    
    tree = ET.parse(sitemap_path)
    urls = [elem.text for elem in tree.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]

    def check_url(target_u, timeout=12):
        body = json.dumps({"inspectionUrl": target_u, "siteUrl": site_url}).encode("utf-8")
        req = urllib.request.Request(
            inspect_url, data=body,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                idx = data.get("inspectionResult", {}).get("indexStatusResult", {})
                return {
                    "url": target_u,
                    "verdict": idx.get("verdict"),
                    "coverage": idx.get("coverageState", "Unknown"),
                    "crawled": idx.get("lastCrawlTime")
                }
        except Exception as e:
            return {"url": target_u, "error": str(e)}

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(check_url, urls))

    indexed = [r for r in results if r.get("verdict") == "PASS" or ("indexed" in r.get("coverage", "").lower() and "not" not in r.get("coverage", "").lower())]
    discovered = [r for r in results if "Discovered" in r.get("coverage", "")]
    unknown = [r for r in results if "unknown" in r.get("coverage", "").lower()]
    retries = [r["url"] for r in results if "error" in r]

    for u in retries:
        retry_res = check_url(u, timeout=25)
        if "error" not in retry_res:
            if retry_res.get("verdict") == "PASS":
                indexed.append(retry_res)
            elif "Discovered" in retry_res.get("coverage", ""):
                discovered.append(retry_res)
            else:
                unknown.append(retry_res)

    return {"indexed": indexed, "discovered": discovered, "unknown": unknown}
```

### B. Web Search Indexing API Protocol (Bulk Priority Crawling)
The Web Search Indexing API (`https://indexing.googleapis.com/v3/urlNotifications:publish`) allows programmatic notification to Googlebot to recrawl or index URLs with priority latency (hours instead of days/weeks):
* **Endpoint**: `POST https://indexing.googleapis.com/v3/urlNotifications:publish`
* **Payload**: `{"url": "https://example.com/target-page.html", "type": "URL_UPDATED"}`
* **Scope**: `https://www.googleapis.com/auth/indexing`

* **Hard Gate 1: GSC Ownership Level (Owner vs Full)**:
  - The Service Account must have permission level **`siteOwner`** (Owner / Pemilik) on the target domain property in GSC *Users and permissions*.
  - If set to `siteFullUser` (Full / Penuh), the API strictly returns:
    `HTTP 403: Permission denied. Failed to verify the URL ownership.`
* **Hard Gate 2: Cloud Project Enablement (1-Click URL)**:
  - Enabling `indexing.googleapis.com` via the Cloud Service Usage API fails with HTTP 403 `PERMISSION_DENIED` unless the service account has the `Service Usage Admin` role.
  - Provide the project owner with the direct 1-click console URL:
    `https://console.developers.google.com/apis/api/indexing.googleapis.com/overview?project=<project_id>`
* **Pacing**: Space bulk publishing calls by 300–500ms to avoid burst rate-limiting.
* **Domain Topology & Blast Radius in Bulk Indexing Campaigns**:
  - *Subdomain Testing Phase*: Bootstrapping multi-page or tiered campaigns across subdomains of a single root domain (e.g. `sub1.domain.com`, `sub2.domain.com`) minimizes registration overhead and aggregates initial domain equity.
  - *Certificate Transparency (CT) Reconnaissance Footprint*: Issuing SSL certificates for subdomains publicly logs all FQDNs to public Certificate Transparency logs (searchable via `crt.sh`, Censys, SecurityTrails). Competitors, crawlers, and automated scanners can enumerate every active subdomain under a parent apex domain in seconds.
  - *Dedicated Domain Isolation*: Once traffic flows and operational viability are proven, decouple high-intent endpoints into dedicated standalone root domains. Subdomain clustering creates a single point of failure: an algorithmic penalty, spam flag, or registrar de-indexing against the apex domain de-indexes all subdomains simultaneously. Separate root domains isolate the blast radius.

### C. The 3-Stage Publishing Lifecycle & Pre-Crawl Readiness Audit
Before inspecting or submitting URLs for indexing, run a **Pre-Crawl Readiness Audit** across all site routes to avoid wasted crawl budget and indexing rejections:
1. **HTTP Status & MIME**: Returns HTTP 200 OK and `Content-Type: text/html`.
2. **Canonical Integrity**: `<link rel="canonical" href="...">` points to the exact live production domain and protocol (no legacy rebrand domains, staging subdomains, or unrouted parameters).
3. **Robots Directives**: Ensure `<meta name="robots">` does **NOT** contain `noindex` or `none`.
4. **Sitemap Coverage**: Ensure target URL is present in `sitemap.xml`.
5. **Internal Connectivity**: URL must be reachable via site navigation or anchor links (avoid orphaned pages).

Webmasters, clients, and automated agents frequently conflate three distinct operational stages of a newly published webpage:
1. **Stage 1 — Live on Server**:
   - Condition: Target URL returns HTTP 200 OK, full byte payload, valid MIME type (`text/html`), and correct `<link rel="canonical">`.
   - Verification: Direct HTTP GET / HEAD request via curl or Python `urllib` (using residential/datacenter proxy if firewalled).
2. **Stage 2 — Submitted & Queued in Sitemap**:
   - Condition: Target URL is registered inside `sitemap.xml`, and the sitemap has been registered with GSC (`PUT /sitemaps/...`).
   - Verification: GSC Webmasters API `GET /sitemaps` returns the sitemap path with `"isPending": true`, `"errors": "0"`.
3. **Stage 3 — Indexed in Google Search**:
   - Condition: Googlebot has crawled the URL, evaluated content quality, and added it to Google's search index.
   - Verification: URL Inspection API returns `verdict: "PASS"`, `coverageState: "Submitted and indexed"`, and a non-null `lastCrawlTime`.

* **The "URL is unknown to Google" Fallacy**:
  - When inspecting a URL in Stage 2, the API returns:
    `verdict: "NEUTRAL"`, `coverageState: "URL is unknown to Google"`, `lastCrawlTime: null`.
  - **Operational Rule**: Never report this to the user as an error, broken link, or failed submission. It simply means the URL is in the normal Googlebot crawl queue between Stage 2 and Stage 3. Googlebot typically processes new sitemap items within 2 to 24 hours.
  - To accelerate Stage 2 to Stage 3 for time-sensitive articles, instruct the webmaster to perform a manual priority crawl request via the Search Console Web UI (paste URL in the inspection bar -> click "Request Indexing" / *Minta Pengindeksan*).

#### Stakeholder Communication Protocol: Web Visibility vs SERP Indexing
When users or clients ask: *"Apakah halaman sudah terindeks di GSC dan orang bisa melihat?"*:
1. **Differentiate Public Availability from Search Indexing Immediately**:
   - **Bisa Dilihat (Public Web Accessibility)**: State unambiguously that if Stage 1 is verified (HTTP 200 OK, navbar link, homepage card), the page is **100% accessible right now**. Any user clicking the URL, accessing the domain, or opening links from social media/chat can see and use the page instantly.
   - **Terindeks di GSC (Google SERP Indexing)**: Clarify that Google search engine indexing is an asynchronous crawler pipeline. Submitting via Google Indexing API places the URL in the crawler queue; Googlebot smartphone crawler will visit and render the page within hours to 1–2 days.
2. **Explain `URL is unknown to Google` with Technical Context**:
   - Never report `verdict: "NEUTRAL"` or `coverageState: "URL is unknown to Google"` as a failure or broken URL.
   - Explain clearly that for content published within the last few hours, this status confirms the URL is in the standard crawl queue awaiting its initial crawler visit, and compare it against an established URL (which shows `verdict: "PASS"`, `coverageState: "Submitted and indexed"`).

### D. Automated 3-Stage Verification Script (Probe + Sitemap + Inspection)
```python
import urllib.request, ssl, json, sys

def verify_publication_pipeline(target_url, sitemap_url, gsc_client):
    report = {"url": target_url}
    
    # Stage 1: Server Live Check
    try:
        req = urllib.request.Request(target_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            report["stage1_live"] = {"status": resp.status, "ok": resp.status == 200}
    except Exception as e:
        report["stage1_live"] = {"status": "FAILED", "error": str(e), "ok": False}
        return report

    # Stage 2: Sitemap Registration Check
    try:
        with urllib.request.urlopen(sitemap_url, timeout=10) as sm_resp:
            sm_content = sm_resp.read().decode('utf-8')
            in_sitemap = target_url in sm_content
            sm_status = gsc_client.get_sitemaps()
            report["stage2_sitemap"] = {
                "in_xml": in_sitemap,
                "gsc_registered": len(sm_status.get("sitemap", [])) > 0,
                "is_pending": sm_status.get("sitemap", [{}])[0].get("isPending", False),
                "ok": in_sitemap
            }
    except Exception as e:
        report["stage2_sitemap"] = {"error": str(e), "ok": False}

    # Stage 3: GSC Indexing Status Check
    try:
        insp = gsc_client.inspect_url(target_url).get("inspectionResult", {}).get("indexStatusResult", {})
        verdict = insp.get("verdict")
        coverage = insp.get("coverageState")
        report["stage3_indexed"] = {
            "verdict": verdict,
            "coverage": coverage,
            "last_crawl": insp.get("lastCrawlTime"),
            "indexed": verdict == "PASS" and "indexed" in coverage.lower()
        }
    except Exception as e:
        report["stage3_indexed"] = {"error": str(e), "indexed": False}

    return report
```

---

## 5. Search Analytics Query
* **Endpoint**: `POST https://www.googleapis.com/webmasters/v3/sites/{site_url_enc}/searchAnalytics/query`
* **Payload**:
  ```json
  {
    "startDate": "YYYY-MM-DD",
    "endDate": "YYYY-MM-DD",
    "dimensions": ["query", "page"],
    "rowLimit": 25
  }
  ```
* **Latency Caveat**: GSC analytics data has an inherent 48–72 hour reporting lag. New sites or newly indexed pages will return empty rows until Google aggregates search performance logs.

---

## 6. Pitfalls & Anti-Patterns

- **Sequential URL Inspection Timeout on Site Audits**: Inspecting 20+ URLs sequentially via the GSC URL Inspection API will exceed standard script and tool execution timeouts (each inspection takes 2–4 seconds over HTTPS). Always execute inspections concurrently using `ThreadPoolExecutor(max_workers=5)` with per-request timeouts (10–12s), and isolate failed reads for single-URL retries with a generous timeout (25–30s).
- **Conflating Public Web Accessibility with Search Engine Indexing**: Telling stakeholders a newly launched feature or page "is not yet visible to people" when it is merely awaiting Googlebot's asynchronous crawl queue. The page is immediately accessible to any human visitor while Googlebot processes indexing asynchronously.
- **Assigning 'Full' Instead of 'Owner' Permissions for Indexing API**: While 'Full' permission in Search Console allows reading analytics and submitting sitemaps, the Web Search Indexing API (`urlNotifications:publish`) strictly enforces verified ownership and fails with HTTP 403 `Permission denied. Failed to verify the URL ownership.` The service account must be designated as 'Owner' (Pemilik) in GSC Users and permissions.
- **Premature DNS Verification Clicking**: Triggering domain verification in GSC before verifying that Google Public DNS (`8.8.8.8`) has purged negative caches and resolved the new `google-site-verification` TXT record. Always run `dig @8.8.8.8 <domain> TXT +short | grep google-site-verification` first.
- **Misinterpreting "URL is unknown to Google" as a Submission Failure**: Assuming that `coverageState: "URL is unknown to Google"` indicates an indexing error on newly published content. Newly deployed pages take hours to be crawled by Googlebot; if the sitemap is submitted with `isPending: true` and 0 errors, the page is properly queued.
- **Reporting Stale GSC Web Dashboard Errors Without API Verification**: Relying on web dashboard snapshot cards that display red "Couldn't fetch" labels instead of checking the live JSON response from the Webmasters API (`isPending: true`, `errors: "0"`).
- **Attempting Indexing API for Standard Content**: Google Indexing API returns HTTP 403 or silently discards standard web pages/articles. Use sitemaps and GSC URL Inspection manual submission instead.
- **Programmatic Service Usage Enablement Trap**: Attempting to enable Google Cloud APIs (`indexing.googleapis.com`) via `serviceusage.googleapis.com` using a standard service account token fails with HTTP 403 `PERMISSION_DENIED` because service accounts lack the `Service Usage Admin` IAM role. Direct the human project owner to the direct 1-click console URL (`https://console.developers.google.com/apis/api/<service>/overview?project=<project_id>`) instead.
- **Triggering Indexing Requests on Unaudited Pages**: Submitting URLs with stale canonical tags, residual `noindex` directives, or broken internal links wastes crawler budget and causes Googlebot to discard the page. Run the automated pre-crawl readiness scan across all routes first.
