---
name: attack-surface-reconnaissance
description: Use when running domain recon and subdomain HTTP probing.
---

# Attack Surface & Subdomain Reconnaissance

Use this skill when mapping the external attack surface of a root domain or organization, enumerating subdomains, identifying live web services, detecting API endpoints, and filtering CDN/Cloudflare wildcard false positives.

## Core Toolchain (Installed in `/usr/local/bin/`)

- **`subfinder`**: Passive OSINT subdomain harvester (Certificate Transparency logs, AlienVault, Shodan, Censys, VirusTotal). Zero active network traffic to the target origin.
- **`dnsx`**: High-performance multi-threaded DNS resolver and dictionary brute-forcer.
- **`httpx-pd`**: Multi-threaded HTTP prober (detects HTTP status codes, titles, tech stacks, TLS, and response lengths).  
  *Note on Binary Collision*: On Python environments, the `httpx` command often resolves to the Python HTTP client CLI (`/root/.../venv/bin/httpx`). Always use `/usr/local/bin/httpx-pd` to invoke the ProjectDiscovery engine.
- **`nuclei`**: Template-based vulnerability scanner for exposed panels, CVEs, and misconfigurations.
- **`recon-scan`** (`/usr/local/bin/recon-scan <domain>`): Unified Python orchestrator running the full pipeline end-to-end.

---

## Standard Workflow

### 1. One-Shot Automated Scan
Run the production pipeline script directly:
```bash
recon-scan <target-domain>
```
Example:
```bash
recon-scan indrayuda.my.id
```

### 2. Manual CLI Pipeline (Step-by-Step)

If granular control is required:

#### Step 1: Passive Reconnaissance
Harvest public records without probing the target directly:
```bash
subfinder -d example.com -silent -o passive_subs.txt
```

#### Step 2: Active DNS Resolution & Bruteforce
Bruteforce common subdomains using `dnsx` with a curated wordlist:
```bash
dnsx -d example.com -w /tmp/wordlist.txt -silent -o active_subs.txt
```

#### Step 3: Deduplication
Merge passive and active targets:
```bash
cat passive_subs.txt active_subs.txt | sort -u > all_subs.txt
```

#### Step 4: Multi-Threaded HTTP Probing
Probe HTTP/HTTPS endpoints for status, title, and technology fingerprint:
```bash
httpx-pd -l all_subs.txt -silent -json \
  -title -status-code -tech-detect -follow-redirects \
  -content-length -timeout 5 -retries 1 \
  -o httpx_results.json
```

---

## Critical Rules & Pitfalls

### 1. Cloudflare / CDN Wildcard Filtering
- **Mechanism**: Domains with wildcard DNS (`*.example.com` -> CDN IP) will cause every bruteforced subdomain to resolve and return HTTP 200 with default edge headers (`[Cloudflare, HSTS, HTTP/3]`).
- **Rule**: Do not report a subdomain as a live application simply because it returns HTTP 200. Filter out false positives by verifying:
  1. A unique HTML `<title>` tag exists (e.g. `cPanel Login`, `phpMyAdmin`, or app title).
  2. Distinct response payload or non-CDN tech stack (e.g. `Express`, `Next.js`, `Alpine.js`).
  3. Response byte length differs from the default wildcard catch-all page.

### 2. Binary Collision Avoidance
- **Mechanism**: The Python `httpx` package installs an executable named `httpx` into virtualenvs, which shadows ProjectDiscovery's `httpx` in `$PATH`.
- **Rule**: Never call bare `httpx`. Always call `httpx-pd` on this system.

### 3. Categorized Triage Structure
When presenting reconnaissance results to the user or writing findings, always categorize into:
1. **🚀 Web Applications & Public Frontends**: Live user-facing portals (HTTP 200) with titles and web frameworks.
2. **⚙️ APIs, Automations & Internal Services**: Endpoints serving JSON, n8n, webhooks, or mail APIs.
3. **🖥️ Server & Hosting Management**: cPanel, WHM, phpMyAdmin, Portainer, or DirectAdmin panels.
4. **⚠️ Configured Failures / Dead Origins**: Subdomains actively routed to origin tunnels that are offline (HTTP 502 Bad Gateway or HTTP 530 Origin Down). These represent genuine configured infrastructure, unlike unmapped DNS.
