# Cloudflare Turnstile Resolution, Security Checkpoint & Session Lifecycle SOP

Operational procedures for Cloudflare Turnstile token resolution, handling datacenter IP blocking, cross-node solving fallback, account security challenge resolution (`checkSecurity`), and persistent session lifecycle management.

---

## 1. Two Captcha Layers in Web Automation

| Layer | Trigger | Mechanism | Resolution Strategy |
|---|---|---|---|
| **Entrance Layer (Login)** | Public Signin / Auth | Cloudflare Turnstile (`sitekey`) | Local Solver API (:5072) / Cross-Node Solving / Residential Cookie Injection |
| **In-Session Layer (Tasks)** | Periodic Checkpoint (`curDay % 15 == 0`) | Custom Pictogram Sequence | Vision LLM Microservice (:5073) -> Local Neural Model |

---

## 2. Cloudflare Turnstile Datacenter IP Challenge Problem

### The Root Cause:
- Cloudflare Turnstile uses machine-learning risk scoring based on IP reputation, browser TLS fingerprint, WebGL capabilities, and mouse kinematics.
- When requested from a Datacenter / Cloud VPS IP (or specific flagged proxy nodes), Turnstile elevates to an interactive / managed challenge mode that headless solvers fail to solve within normal timeouts (35–45s).
- Residential browser sessions pass Turnstile in <2 seconds.

---

## 3. Triple Strategy for Turnstile Resilience

### Strategy A: Exponential Retry Loop with Backoff (Automated Solver)
Wrap authentication calls in a 5-attempt retry loop:
- Attempt 1: 3s delay
- Attempt 2: 6s delay
- Attempt 3: 9s delay
- Attempt 4: 12s delay
- Attempt 5: 15s delay

### Strategy B: Dynamic Rotating Proxy Node Pool & Configurable Batch Retries (Auto-Failover)
- Never tie initial Turnstile authentication strictly to one account's assigned proxy.
- Maintain a pool of all available proxy nodes (e.g., Node 01 to Node 15 across ID, SG, MY, TH, HK, TW, KR, etc.).
- On authentication failure:
  1. Rotate through proxy nodes sequentially across attempts (e.g. Attempt 1 on Node 1, Attempt 2 on Node 2, ..., Attempt 10 on Node 10).
  2. Configure attempt budget and cooldown via `turnstile.max_login_retries_per_batch` (default: 10) and `turnstile.cooldown_on_failure_seconds` (default: 300s).
  3. If a batch of 10 attempts fails, do NOT terminate the worker thread. Enter the configured **cooldown (e.g. 300s / 5 minutes)**.
  4. On the next batch, continue rotating through the subsequent proxy nodes (Node 11 to Node 15, then wraparound to Node 01) until a clean token and session cookies are captured.
  5. Once `hash` is obtained and cached, the worker reverts strictly to its dedicated proxy node for all operational traffic.

### Strategy C: Multi-Tier Session Validation & False-Expiry Prevention (Bypass Invariant)
- In SPA / Nuxt platforms, Turnstile is **only evaluated once** to issue authentication session cookies (`hash`, `signed=1`).
- Once the `hash` cookie is obtained, save it to `state/sessions.json`.
- **The `checkSecurity` False-Expiry Trap:**
  - When accounts change IP nodes, `/api/user/` (`getCurrentUser`) often returns `{"status": "error", "message": "checkSecurity"}`.
  - A naive validator that only checks `getCurrentUser` will falsely treat this as an expired session and trigger an unnecessary Turnstile login loop.
  - **Critical Invariant:** In-session task endpoints (`/api/user/tasks/` with `method=getLimits`, `get`, and `checkIp`) **remain 100% authorized and active** under the cached `hash` cookie even when profile endpoints return `checkSecurity`!
- **3-Tier Validation Hierarchy on Worker Startup:**
  1. **Tier 1 (Profile Check):** Check `POST /api/user/` (`getCurrentUser`). If `status == "ok"` and user data is present, session is valid.
  2. **Tier 2 (Task Limits Probe):** If Tier 1 fails or returns `checkSecurity`, probe `POST /api/user/tasks/` (`method=getLimits`). If limits or `limitDay` are returned, session is **VALID** -> proceed to task execution.
  3. **Tier 3 (Active Task Probe):** Check `POST /api/user/tasks/` (`method=get`). If a task or `limitInHour`/`limitInDay` is returned, session is **VALID** -> cache `data.balance` and proceed.
  4. Only if ALL 3 tiers fail (e.g. `authRequired` or `sessionExpired`) should the worker declare the session expired and invoke the Turnstile solver.

---

## 4. In-Place Captcha Challenge Refresh & Multi-Attempt Solver Resilience
- In dynamic platforms, if submitted captcha coordinates are slightly outside tolerance or expire, the backend may return a fresh challenge (`status: "data"` with new `image` and `queue`) rather than a simple error.
- **In-Place Re-Solving Protocol:**
  - When captcha submit response contains a new challenge payload, do NOT skip the task or trigger a long sleep.
  - Immediately pass the refreshed base64 queue and grid image to the Vision AI solver microservice in-place.
  - Submit the second attempt's coordinates. On success, mark reward claimed and dispatch positive feedback to the training dataset.

---

## 5. Account Security Challenge Resolution (`checkSecurity` & `sendConfirmCode`)

### Root Cause & Symptoms:
- When an account changes egress IP, user-agent, or logs in from a new VPS node, server endpoints (`POST /api/user/` or `/user/settings/save/`) may return error `checkSecurity`.
- Under this state, normal settings endpoints fail to dispatch email confirmation codes for wallet updates because the account is in security quarantine.

### Resolution Protocol & Decision Tree:
```
[Server Endpoint Error: 'checkSecurity']
          │
          ▼
Trigger dedicated security verification endpoint:
POST /api/user/verification/ (method=sendConfirmCode)
          │
          ▼
Server sends 6-digit OTP code to Gmail (valid for 300s)
          │
          ▼
Submit code via POST /api/user/verification/ (method=checkCode, code="<6_digits>")
          │
          ▼
Account unlocked -> emailActive: 1 -> resume normal operations & wallet sync!
```

