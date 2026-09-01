---
name: web-traffic-automation-engine
description: "Build pure Python HTTP scrapers, bots, and workers."
version: 1.5.0
author: Hermes
platforms: [linux, darwin, windows]
metadata:
  hermes:
    tags: [Automation, Scraping, Reverse-Engineering, Captcha, Proxy]
---

# Web Traffic & Pure Python HTTP Automation Engine

Standardized architecture, reverse-engineering methodology, and execution protocol for high-performance, browser-less automation, Cloudflare Turnstile resolution, multimodal visual sequence captcha solving, automated FaucetPay USDT TRC20 wallet management, security checkpoint bypass, and 24/7 multi-account fleet management.

## When to Use
- Reverse-engineering SPA / Nuxt 3 / Vue web applications into pure HTTP request workflows.
- Building 100% Python HTTP task runners, video watch bots, reward claimers, and multi-account automation engines.
- Solving dual-layer captchas (Cloudflare Turnstile + internal visual sequence icon click captchas).
- Transitioning cloud Vision LLM solvers into standalone zero-token local datasets.
- Resolving account security challenges (`checkSecurity`) via dedicated verification endpoints (`sendConfirmCode`).
- Gating and executing smart Daily Activity Bonus autoclaim on maximum 500/500 view tier ($0.010 USD).
- Integrating automated FaucetPay USDT TRC20 wallet management, email verification detection, 1-click batch payout execution, and autonomous background auto-withdrawal engine.
- Hardening 24/7 fleet architectures against memory bloat (bounded log tail seek), race conditions (thread-safe atomic JSON writes), method shadowing bugs, and dashboard action endpoint security (API key auth).
- Designing self-healing multi-worker scaling architectures (10-100+ accounts) with non-blocking error isolation and adaptive backoffs.
- Building real-time multi-account web telemetry dashboards with interactive withdrawal readiness hubs, search filters, and dense table views.

## Prerequisites
- Python 3.9+ with standard library (`urllib.request`, `urllib.parse`, `threading`, `json`, `time`, `http.server`).
- Local proxy nodes (e.g. Surfshark Docker Proxy Studio on ports `31001`..`31005`).
- Local Cloudflare Turnstile Solver API on port `5072` (optional, for initial login token acquisition).
- Multimodal Vision LLM Gateway (e.g. 9router on port `20128` with `gemini-3.7-flash-high` or `gemini-3.6-flash`).

## Core Invariants & Rules
1. **100% Pure Python Requests / Urllib Only:**
   - Automation and claimer scripts must NEVER run Playwright, Selenium, or Camoufox in their 24/7 runtime loop.
   - All network calls, form logins, and task claims execute via direct REST/HTTP requests.
2. **Hermes Native Browser Boundary:**
   - Visual auditing, initial bundle extraction, and page inspection must strictly use the native Hermes browser (`browser_exec` / CDP).
3. **1 Account : 1 Dedicated Proxy Node Isolation:**
   - Always assign exactly one dedicated egress proxy node per account worker thread to avoid shared IP shadowbans.
4. **Zero Blind Delays (Sub-Minute Precision Rollover):**
   - Never execute arbitrary static sleep intervals (`time.sleep(3600)`). Compute exact remaining seconds to the `:00:15` hourly reset or UTC midnight.
5. **Interruptible Adaptive Step-Sleep:**
   - Use 1-second step-checked loops (`while remaining > 0 and not stop_event`) instead of monolithic blocking sleeps.
6. **Public Git Sanitization Invariant:**
   - Always untrack `config.json`, provide sanitized `config.example.json`, and squash/scrub credentials from git history before making repositories public.

## Quick Reference Commands

| Task | Invocation / Endpoint | Reference SOP |
|---|---|---|
| Proxy Connectivity Test | `urllib.request.urlopen("https://api.ipify.org?format=json")` via ProxyHandler | Section 1 |
| Turnstile Solve Polling | `GET http://127.0.0.1:5072/turnstile?url=...&sitekey=...` | `references/turnstile_and_session_lifecycle.md` |
| Security Challenge Code Dispatch | `POST /api/user/verification/` (`method=sendConfirmCode`) | `references/turnstile_and_session_lifecycle.md` |
| Security Challenge Code Verify | `POST /api/user/verification/` (`method=checkCode`, `code=...`) | `references/turnstile_and_session_lifecycle.md` |
| Visual Icon Captcha Solve | `POST http://127.0.0.1:5073/solve` with `queue_base64` & `image_base64` | `references/visual_icon_captcha_and_dataset_flywheel.md` |
| Trigger Email Verification | `POST /api/user/settings/confirm/` (`method=reqConfirm`) | `references/multi_account_architecture_and_telemetry.md` |
| Save Payout Wallet | `POST /api/user/settings/save/` (`method=payments`, `faucetpayusdt_wallet=...`) | `references/multi_account_architecture_and_telemetry.md` |
| Execute Payout Request | `POST /api/user/payout/send/` (`service=faucetpayusdt`, `sum=...`) | `references/multi_account_architecture_and_telemetry.md` |
| Auto-Withdraw Daemon Loop | Triggered automatically on reward claim when balance >= threshold | `references/multi_account_architecture_and_telemetry.md` |
| Mark Dataset Ground Truth | `POST http://127.0.0.1:5073/feedback` with `{"sample_id": "...", "verified": true}` | `references/visual_icon_captcha_and_dataset_flywheel.md` |
| Start Multi-Bot Daemon | Invoke `python3 bot.py` through `terminal` tool or systemd | `templates/multi_account_bot_template.py` |
| Start Web Telemetry Server | Invoke `python3 server.py` (Port 8280 -> Cloudflare Tunnel) | `templates/telemetry_dashboard_server.py` |

## Procedure

### Step 1: Client Bundle Reverse-Engineering
1. Fetch target HTML and identify script chunks under `/_nuxt/*.js`.
2. Search for action classes (`watchActions`, `captchaActions`, `authActions`, `payoutActions`, `verificationActions`) to extract API endpoints and payload serialization.
3. Trace full claim sequence: `POST /user/tasks/` (`method=get`) -> `POST /user/tasks/start/` (`fin=0`) -> `sleep(duration)` -> `POST /user/captcha/check/`.

### Step 2: Multi-Account Daemon Setup & Scaling
1. Configure `config.json` mapping each account to a dedicated proxy node (`http://127.0.0.1:31001`..`:31005`).
2. Implement `AccountWorker(threading.Thread)` with dynamic infinite loop, login retry backoff, and dynamic task-level quota tracking (`limitHour`, `limitDay`).
3. Handle transient empty queues with fast 15s backoff and hourly limits with exact `:00:15` sub-minute rollover calculation.

### Step 3: Dual-Layer Captcha, Security Challenge & Dataset Flywheel Integration
1. Resolve login Turnstile via solver API or residential cookie injection, persisting `hash` and `signed` to `state/sessions.json`.
2. Handle account IP changes or `checkSecurity` challenges by triggering `POST /api/user/verification/` (`method=sendConfirmCode`) and verifying with `checkCode`.
3. Connect periodic in-session visual sequence captchas to `IconCaptchaSolver` microservice (Port `5073`).
4. Record lossless PNGs and JSONL annotations, confirming ground truth on successful reward claim.

### Step 4: Web Telemetry, Wallet Management, Email Verif & Payout Hub
1. Deploy `server.py` on port `8280` serving single-file inline dark glass dashboard.
2. Aggregate live multi-account balances, clover multipliers, active/sleeping worker statuses, live email verification badges, and server wallet synchronization detection.
3. Sediakan modal input/edit FaucetPay USDT TRC20 wallet per-akun dengan trigger sinkronisasi otomatis ke remote server dan 1-click email verification trigger.
4. Provide interactive withdrawal threshold selection ($0.10, $0.50, $1.00, $5.00, Custom) with local storage sync, per-account payout buttons, live transaction status tracking (`PAID` status code `"1"`), and global "Auto Withdraw All Ready" batch execution.

## Reference Documentation Index
- `references/watch_claim_reverse_engineering.md`: Complete playbook for Nuxt 3 chunk extraction, payload reconstruction, and reward attribution flows.
- `references/visual_icon_captcha_and_dataset_flywheel.md`: SOP for 3-icon sequence captchas, Vision LLM integration, latency constraints, coordinate math, and self-training dataset harvesting.
- `references/turnstile_and_session_lifecycle.md`: Turnstile token resolution, datacenter IP bypass strategies, cross-node solving fallback, security challenge resolution (`checkSecurity`), and session cookie caching.
- `references/multi_account_architecture_and_telemetry.md`: 1-Account-1-Proxy isolation, infinite dynamic stream loop, precision sub-minute rollover, FaucetPay USDT TRC20 wallet manager, live email verification detection, official Nuxt payout status codes (`"1"` = PAID), and Apple-grade telemetry dashboard with withdrawal readiness hub.
- `templates/multi_account_bot_template.py`: Runnable template for multi-worker daemons with dynamic limit handling.
- `templates/icon_captcha_solver_client.py`: Complete standalone microservice template for Vision LLM icon captcha solving.
- `templates/telemetry_dashboard_server.py`: Complete web telemetry dashboard server template.

## Verification
Verify the multi-account engine, solver microservice, and telemetry dashboard:
```bash
# 1. Verify proxy nodes health
python3 -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:31001').status)"
# 2. Verify Icon Captcha Solver API
curl -s http://127.0.0.1:5073/health
# 3. Verify Live Web Telemetry API
curl -s http://127.0.0.1:8280/api/stats
```
