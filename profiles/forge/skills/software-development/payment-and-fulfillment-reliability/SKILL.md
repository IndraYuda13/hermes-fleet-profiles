---
name: payment-and-fulfillment-reliability
description: "Patterns for payment gateways, webhooks, and fulfillment."
version: 0.1.0
author: Indra Yuda (IndraYuda13), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [payment, fulfillment, webhook, idempotency, race-conditions, anti-fraud, h2h]
    related_skills: [express-api-development, software-development-workflows]
---

# Payment Gateway Integration & Fulfillment Engine Reliability

Production engineering standards, architectural patterns, and security controls for high-volume digital goods, top-up platforms (games, vouchers, PPOB), and digital payment gateways (Dynamic QRIS, E-Wallets, Virtual Accounts).

## When to Use

- Designing, auditing, or implementing Payment Gateway (PG) integrations and H2H (Host-to-Host) provider fulfillment services.
- Hardening webhook ingestion endpoints against race conditions, replay attacks, callback spoofing, and timing attacks.
- Implementing atomic state transitions, transactional claim locks, or outbox workers to eliminate double-fulfillment and financial loss.
- Establishing double-entry bookkeeping, balance reconciliation workers, and retry/circuit breaker policies.

## 1. Concurrency & Idempotency: Eliminating Double Fulfillment

In digital top-up platforms (margins typically 1-3%), double-fulfillment (calling upstream suppliers twice for one payment) causes direct, irreversible capital loss.

### 1.1 Atomic Conditional Update (Claim Lock)
Never use read-then-write logic (`SELECT status` -> `if status == 'PENDING'` -> `DISPATCH()`), which creates a Time-of-Check to Time-of-Use (TOCTOU) race window between client polling and webhook callbacks.

Use an atomic SQL update directly at the database engine level:

```sql
-- PostgreSQL Atomic Claim Lock
UPDATE orders 
SET status = 'PROCESSING_SUPPLIER', 
    paid_at = NOW(),
    updated_at = NOW() 
WHERE id = :order_id 
  AND status = 'PENDING_PAYMENT'
RETURNING id, final_payable_amount, target_account_id, sku_code;
```
If `rows_affected == 0`, another execution thread has already claimed the transaction; exit immediately without side effects.

### 1.2 Webhook Fast-Ack & Asynchronous Worker (Transactional Outbox)
Never call external upstream suppliers synchronously within the HTTP webhook handler.
1. Validate HMAC signature and deduplicate event in under 10ms.
2. Atomically update order state or write to an Outbox table in the same DB transaction.
3. Return `HTTP 200 OK` to the Payment Gateway immediately (< 200ms) to prevent webhook timeouts and retry storms.
4. An asynchronous worker process picks up the outbox event and dispatches fulfillment.

### 1.3 Asynchronous DB & Connection Pooling Guard
In async web frameworks (FastAPI / Starlette / Sanic / Tornado):
- Never invoke blocking synchronous DB drivers (e.g. raw `PyMySQL`, `psycopg2`, synchronous `sqlite3`) directly inside `async def` routes, as they block the central event loop.
- Use asynchronous drivers with connection pooling (`aiomysql`, `asyncpg`, `aiosqlite`, SQLAlchemy `async_sessionmaker`).
- Avoid running DDL or schema inspection checks (`CREATE TABLE IF NOT EXISTS`, `ALTER TABLE`) inside hot request paths or query helpers. Keep schema initialization strictly within application startup lifecycle (`lifespan`).
- Maintain persistent connection-pooled HTTP clients (e.g. shared `httpx.AsyncClient`) via app lifespan context rather than instantiating and closing connections on each individual request.

---

## 2. Upstream Dispatch & Resilience

### 2.1 Outbound Idempotency Key
Always supply the internal LemonTopup Order ID (or deterministic UUID) as the upstream provider's `ref_id` / `trx_id` / `idempotency_key`. If a network timeout or drop occurs, retrying with the exact same reference ID allows the supplier to return the previous transaction state without double-charging the deposit balance.

### 2.2 Exponential Backoff with Jitter
For transient errors (HTTP 502/503/504 or network timeouts):
$$T_{\text{wait}} = \min(T_{\text{max}}, T_{\text{base}} \times 2^{\text{attempt}}) + \text{jitter}$$
- Defaults: $T_{\text{base}} = 2\text{s}$, $T_{\text{max}} = 60\text{s}$, Max Attempts = 4.
- Add randomized jitter (0 to 500ms) to prevent thundering herd spikes against the provider.

### 2.3 Circuit Breaker & Failover
If an upstream aggregator fails consecutively (>5 times within 1 minute), trip the circuit breaker and route the SKU to a secondary backup supplier or queue the order for manual reconciliation.

### 2.4 Indeterminate Upstream Timeout & Anti-False-Refund Rule
Never trigger an automatic refund or mark an order terminal `FAILED` solely on an upstream HTTP timeout / network exception (`httpx.HTTPError`, `ReadTimeout`, `ConnectTimeout`).
- **The Financial Trap:** In H2H top-up integrations, upstream aggregators often process and deduct balance even if the HTTP response connection drops before returning. Refunding the customer immediately on timeout causes double financial loss (deposit balance lost + customer balance credited).
- **Correct State Transition:** Mark the order as `SUBMITTED`, `PROCESSING_SUPPLIER`, or `PENDING_RECONCILIATION`.
- **Resolution:** Let subsequent upstream webhooks or periodic reconciliation pollers (`status` inquiry by `ref_id`) resolve the final state (`SUCCESS` vs terminal `FAILED`) before initiating any wallet or payment gateway refund.

---

## 3. Webhook Security & Anti-Fraud (SENTINEL Standard)

### 3.1 Raw Body HMAC Verification & Constant-Time Comparison
- Verify signatures against **raw bytes** (`raw_body`) directly from the socket before JSON body-parsing to avoid deserialization drift.
- Use constant-time comparison to prevent side-channel timing attacks:
```python
import hmac
import hashlib

def verify_pg_signature(raw_body: bytes, signature_header: str, secret_key: bytes) -> bool:
    expected = hmac.new(key=secret_key, msg=raw_body, digestmod=hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature_header)
```

### 3.2 Anti-Replay & Deduplication
- **Timestamp Tolerance Window:** Tolerate a maximum clock drift of $|T_{\text{server}} - T_{\text{webhook}}| \le 300\text{s}$ (5 minutes).
- **Atomic Event Dedup:** Store `(provider_id + event_id)` in Redis with a 24-hour TTL using `SETNX`. Return `200 OK` immediately if the key already exists.

### 3.3 Zero-Trust Client Pricing & Amount Tampering Prevention
- Never trust prices sent from the client. Catalog lookup must occur on the server during order creation.
- Store an immutable snapshot: `base_price`, `admin_fee`, `discount_amount`, `unique_code`, `final_payable_amount`.
- Validate `webhook.paid_amount == order.final_payable_amount`. If mismatched, hold fulfillment and alert.
- Store all monetary values as `DECIMAL(15,2)` or integer cents/rupiah (`BIGINT`). Never use IEEE 754 floating point numbers.

### 3.4 Immutable Destination Data & Secrets Rotation
- Destination target accounts (Game UID, Zone ID, MSISDN) are locked in the DB upon order creation and must never be altered by webhook parameters.
- Webhook verification should support dual active keys (`CURRENT_SECRET` and `PREVIOUS_SECRET`) for zero-downtime rotation.

---

## 4. Reconciliation & Failure Recovery

1. **Periodic Status Poller Worker (1-2 min):** Scan for orders in `PROCESSING_SUPPLIER` or `SUPPLIER_PENDING` older than 2 minutes and query the upstream provider by `ref_id`.
2. **Double-Entry Bookkeeping Ledger:** Maintain immutable audit rows for balance mutations:
   - Debit: Payment Gateway Clearing Account
   - Credit: Sales Revenue & Platform Fee
   - Debit: Cost of Goods Sold (COGS)
   - Credit: Upstream Deposit Balance
3. Daily automated reconciliation matching PG settlements, supplier ledger deductions, and fulfilled database orders.

---

## 5. Multi-Tier Balance Extraction & Resilient Payout Fallback

When operating automated withdrawal, payout, or top-up disbursement workers against upstream services with intermittent security checks or route-specific rate limits (e.g. `checkSecurity` on user profile endpoints while stream/task endpoints remain accessible):

### 5.1 Multi-Tier Balance Resolution Hierarchy
Never rely on a single endpoint for balance gating before payout submission:
1. **Tier 1 (Direct Profile Endpoint):** Query primary user profile/balance API (`/api/user/`).
2. **Tier 2 (Active Task/Stream Probe):** Query alternative active task/stream endpoints (`/api/user/tasks/` method: `get`) that return live balances without triggering profile-level security checks.
3. **Tier 3 (Persistent Fleet State Cache):** Read live deterministic state (`fleet_state.json` or Redis) populated by worker threads during reward claims, preventing false zero-balance falls.
4. **Tier 4 (In-Memory Last Known Value):** Maintain thread-safe in-memory last known balance if external queries fail or time out.

### 5.2 Anti-Flapping Payout Rate Limiting
- Enforce strict cooldowns between auto-withdraw calls (e.g., minimum 3600s per account) to avoid hammering upstream payout endpoints on transient rejections (`noFunds` / `minSum`).
- Pass strict fixed-precision string sums (e.g. `{bal:.7f}`) matching the upstream payout contract without float rounding errors.

### 5.3 Upstream Payout History Schema Normalization & Sort Invariants
- Upstream payout APIs frequently vary their response schemas across versions or methods (e.g. `data.history.data` vs `data.items`). Always employ fallback extraction chains:
  ```python
  items = res.get("data", {}).get("history", {}).get("data", [])
  if not items:
      items = res.get("data", {}).get("items", [])
  ```
- Many upstream ledger endpoints return entries sorted ascending by primary key (`id` or `unixtime`). Never assume index `[0]` is the latest payout without explicit descending sort normalization:
  ```python
  sorted_items = sorted(
      items,
      key=lambda x: int(x.get("unixtime", 0) or x.get("id", 0)),
      reverse=True
  )
  latest_payout = sorted_items[0] if sorted_items else None
  ```

### 5.4 Payout Lifecycle Gate & Review Lock State Machine
- When a payout enters in-flight verification (`UNDER REVIEW` / `IN PROGRESS`):
  - Set `payout_under_review = True` and set an active backoff window (e.g. +6 hours / 21600s).
  - Suppress further auto-withdrawal calls before network transmission (zero POST spam).
- When payout history sync detects terminal settlement (`PAID` or `PAYMENT ERROR`):
  - Immediately clear `payout_under_review = False` and reset `payout_backoff_until = 0.0` to restore normal worker cycle.

### 5.5 HTTP Anti-Caching for Real-Time Telemetry & Dashboards
- To prevent reverse proxies (e.g. Cloudflare, Nginx) and browser clients from serving stale payout and balance metrics, enforce explicit HTTP anti-cache headers across dashboard HTML and `/api/stats` handlers:
  ```http
  Cache-Control: no-cache, no-store, must-revalidate
  Pragma: no-cache
  Expires: 0
  ```

---

## Verification

- Test concurrent burst callbacks using HTTP load tools to ensure only 1 fulfillment call executes.
- Verify signature verification fails on altered body bytes or tampered amount parameters.
- Verify upstream retries reuse the identical internal `ref_id`.
