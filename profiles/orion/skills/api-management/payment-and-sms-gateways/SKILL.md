---
name: payment-and-sms-gateways
description: Use when integrating QRIS payments or SMS OTP number APIs.
version: 1.1.0
author: Hermes Agent Curator
license: MIT
metadata:
  hermes:
    tags: [payment, qris, pakasir, sms-otp, 5sim, virtual-numbers, wallet-ledger, webhooks]
---

# Payment Gateways & Virtual Number SMS OTP Integrations

Consolidated operational runbook for integrating Indonesian digital payment gateways (PaKasir QRIS & Virtual Accounts) and virtual number SMS OTP verification APIs (5sim.net, SMS-Activate) with wallet ledgers, atomic state locking, and fail-closed security.

## When to Use
- Integrating QRIS or Virtual Account checkout flows and verifying asynchronous payment webhooks.
- Allocating virtual phone numbers, polling incoming SMS OTPs, and managing provider rating scores.
- Designing dual-payment architectures (internal wallet balance vs direct gateway payments).
- Implementing atomic transaction transitions, stock reservations, and idempotent upstream fulfillment.

---

## 1. QRIS & Payment Gateway Integration (PaKasir Standards)

### API Profiles & Contracts
1. **Legacy Profile (`app.pakasir.com/api` — DEPRECATED):**
   - **Deprecation Warning:** PaKasir API v1 is officially deprecated and scheduled for complete shutdown on **20 October 2026**. All active integrations must migrate to v2 immediately.
   - Create QRIS: `POST /api/transactioncreate/qris` with `project`, `order_id`, `amount`, `api_key`. Returns `payment_number` (raw QR string) and `expired_at`.
   - Transaction Detail: `GET /api/transactiondetail?project=...&amount=...&order_id=...&api_key=...`. *Security Rule:* Redact query credentials in outbound logging.
   - Cancel / Simulation: `POST /api/transactioncancel` and `POST /api/paymentsimulation`.
2. **v2 Profile (`app.pakasir.com/api/v2` — Mandatory Standard):**
   - Create: `POST /api/v2/create-transaction/{slug}/{order_id}` with header `X-Api-Key: <api_key>` and body `{"method": "qris", "amount": 10000}`. Idempotent (*find or create*).
   - Response Fields: Returns `txn_id`, `qr_string`, `fee`, `total_payment`, `expired_at`, `is_sandbox`.
   - Transaction Status: `GET /api/v2/transaction-status/{slug}/{txn_id}` with header `X-Api-Key: <api_key>`. Rate limit: 1 request every 4 seconds per transaction.
   - Cancel Transaction: `POST /api/v2/cancel-transaction/{slug}/{txn_id}` with header `X-Api-Key: <api_key>`. Rate limit: 2 requests/second.
   - Fee Calculator: `GET /api/v2/payment-fee/{amount}` (public endpoint, no API key required).
   - *Profile Isolation Rule:* Never implement silent runtime fallback between legacy and v2 due to incompatible schemas (`payment_number` vs `qr_string`) and credential formats (`api_key` in body vs `X-Api-Key` header). Store `txn_id` permanently in the database upon order creation.

### Webhook Handling Protocol
1. **v2 Webhook Authentication Header (`X-Secret`):**
   - PaKasir v2 delivers payments via `POST` with header `X-Secret: <webhook_secret>` (configured at project level).
   - Validate `X-Secret` using constant-time comparison (`hmac.compare_digest`). Reject missing or mismatching headers with HTTP 401 immediately (fail-closed).
2. **Fail-Closed Secret Trap (Anti-Bypass Invariant):**
   - Never write `if token and token != secret: raise 401`. An empty or omitted token makes the condition falsy, allowing unauthenticated callers to bypass validation completely. Always enforce fail-closed: `if not token or not hmac.compare_digest(str(token), str(secret)): raise HTTPException(401)`.
3. **Mandatory Field Assertions:**
   - Webhook v2 body payload: `{"txn_id": "...", "order_id": "...", "amount": 10000, "status": "completed", "completed_at": "...", "is_sandbox": false}`.
   - Notice: v2 payloads omit the legacy `project` slug. Always validate that `amount` and `order_id` match the database order record exactly before crediting funds.
3. **Mandatory Authenticated Status Inquiry:**
   - Webhook callbacks are untrusted hints. Never settle an order directly from webhook bodies alone without verifying `status == 'completed'`. When in doubt, make an authoritative outbound call (`GET /api/v2/transaction-status/{slug}/{txn_id}`).
4. **Atomic DB State Lock (Anti-Double Fulfillment):**
   ```sql
   UPDATE orders
   SET status = 'paid', paid_at = datetime('now')
   WHERE order_id = ? AND status = 'pending';
   ```
   Only proceed to product delivery if `rowcount > 0`. If `rowcount == 0`, return HTTP 200 and skip duplicate fulfillment.
5. **Decoupled Fulfillment:** Return HTTP 200 to the payment gateway within <100ms. Dispatch slow upstream fulfillment (e.g. H2H top-up APIs) to an asynchronous background worker.

### QRIS Checkout Traps & Invariants
- **Zero Fabricated QR on Error:** When QR creation fails, never return a hardcoded or placeholder QR string. Record the attempt as `CREATE_UNKNOWN` and withhold display until a verified response returns.
- **Reservation Window & Grace Period (10m + 2m):** While gateways expire QR invoices after 10 minutes, banking clearing delays often arrive between minutes 10:00–12:00. Hold stock reservations for 12 minutes (10m + 2m grace) before releasing. If paid after 12 minutes and stock is exhausted, credit the buyer's internal wallet (`RECONCILIATION_CREDIT`) excluding gateway fees; never silently oversell.
- **Mobile QRIS Ergonomics:** Provide a 1-tap "Simpan QRIS ke Galeri" button converting QR bytes into downloadable PNGs so mobile users can scan via mobile banking galleries.
- **Status Decoupling:** Keep Payment Status (`UNPAID` -> `PAID` -> `EXPIRED`), Order Status (`AWAITING_PAYMENT` -> `PROCESSING` -> `COMPLETED`), and Fulfillment Status decoupled across separate database columns.

---

## 2. Virtual Number & SMS OTP APIs (5sim & Pull-Based)

### Provider Architecture & HTTP Polling
Providers like 5sim.net operate strictly via **HTTP GET polling** (no webhooks).
- Base URL: `https://5sim.net/v1/user` with `Authorization: Bearer <API_KEY>`.
- Profile & Balance: `GET /v1/user/profile`.
- Products & Stock: `GET /v1/guest/products/{country}/{operator}`.
- Buy Number: `GET /v1/user/buy/activation/{country}/{operator}/{product}`.
- Check Order / SMS: `GET /v1/user/check/{order_id}`.
- Finish Order: `GET /v1/user/finish/{order_id}` (+0.5 rating).
- Cancel Order: `GET /v1/user/cancel/{order_id}` (USD balance refunded).
- Ban Order: `GET /v1/user/ban/{order_id}` (Number reused/burned).

### Invariants & Best Practices
1. **Rating Protection & Proactive Cancellation:**
   - Letting an order hit the 15-minute expiration passively incurs maximum rating penalty (-0.15). If rating drops to 0, account ordering is suspended for 24h.
   - Always run a background worker to call `/cancel/{order_id}` proactively at minute 10 if no SMS arrives, protecting rating and recovering 100% USD balance.
2. **Candidate Operator Resolution Hierarchy:**
   - Never pass `operator="any"` blindly (frequently checks only physical carriers with 0 stock).
   - In `/v1/guest/prices`, virtual operators may show huge stock but `rate: 0` (0% delivery rate).
   - Hierarchy: (1) Real physical carriers first, (2) Proven delivery rates (`rate > 0`), (3) Lowest wholesale cost, (4) Available stock count.
3. **Strict Maximum Wholesale Cost Guard (`max_price` Quirk):**
   - **5sim API Pitfall:** The `maxPrice` query parameter is **strictly ignored by 5sim upstream unless `operator` is explicitly set to `any`**. When purchasing with a specific operator name, `maxPrice` has no effect.
   - Rule: Always check wholesale cost locally against `/v1/guest/prices` before issuing the buy call. Compute break-even cost: `max_breakeven_usd = round(price_idr / exchange_rate, 4)` and abort if operator price exceeds threshold.
4. **Money-Loss Guard on Cancel/Ban Failure:**
   - **Merchant Financial Loss Pitfall:** In 5sim, `/cancel/{id}` and `/ban/{id}` reject with HTTP 400 if SMS has already arrived (`order has sms`) or the order has expired.
   - Never catch/swallow provider cancel/ban exceptions and proceed to refund the customer's wallet 100%. If upstream cancellation fails, the customer may obtain the OTP while also receiving a full refund, forcing the merchant to absorb the wholesale cost. Only refund after upstream returns HTTP 200 / status `CANCELED`, or route to manual merchant review.
5. **Guest Order Refund Misattribution Trap:**
   - When supporting guest checkouts alongside registered accounts, never fall back to `order["user_id"] or caller_user_id` when crediting refunds.
   - An authenticated caller could cancel expired/unclaimed guest orders and fraudulently absorb the refund into their own account balance.
   - Invariant: Only credit user balance if `order["user_id"]` is explicitly set AND matches the authenticated session. Guest refunds must route to original gateway payment method or manual administrative triage.
6. **Masked Number Rejection (`*` in Phone Numbers):**
   - If an allocated phone number contains asterisks (e.g. `+447****7658`) or has < 7 digits, cancel immediately via `/cancel/{order_id}` and advance to the next candidate operator.
7. **Zero-Simulation & Fail-Closed Invariant:**
   - Never generate fake `OTP-XXXXXX` mocks or fake numbers in production when provider allocation fails. Roll back user wallet balance atomically and report honest exhaustion.
8. **Explicit UTC Timezone Contract & Worker TypeError Trap:**
   - SQLite `datetime('now')` generates naive UTC strings (`YYYY-MM-DD HH:MM:SS`). Python's `datetime.fromisoformat()` produces naive datetimes.
   - Comparing a naive datetime with an aware UTC datetime (`datetime.now(timezone.utc)`) raises `TypeError: can't compare offset-naive and offset-aware datetimes`.
   - If wrapped in `try ... except Exception: pass`, background auto-cancel/auto-refund workers fail silently on every tick and never execute.
   - Always normalize:
     ```python
     if dt.tzinfo is None:
         dt = dt.replace(tzinfo=timezone.utc)
     ```
   - Emit backend order creation timestamps in explicit ISO-8601 with `"Z"` suffix (e.g. `2026-09-17T11:46:37Z`) to prevent client and server timezone drift.

---

## 3. Shared Wallet Ledger & Transaction Safety

1. **Atomic Wallet Ledger (Append-Only):**
   ```sql
   -- Decrement balance with row-level check
   UPDATE wallet_accounts
   SET balance = balance - :amount, updated_at = NOW()
   WHERE user_id = :user_id AND balance >= :amount;

   -- Write immutable audit ledger entry
   INSERT INTO wallet_ledger (id, user_id, entry_type, amount, balance_after, reference_type, reference_id, created_at)
   VALUES (:id, :user_id, 'PURCHASE', -:amount, :new_balance, :ref_type, :ref_id, NOW());
   ```
2. **1-Click Wallet Checkout vs Direct QRIS:** Direct micro-transactions ($0.05–$0.50) through payment gateways create high fees. Mandate wallet balance for micro-transactions and route QRIS strictly to account deposits.
3. **Timeout Non-Refund Invariant:** Upstream network timeouts during fulfillment represent an indeterminate state, not a failure. Never auto-refund immediately; flag as `pending_reconciliation` until verified to prevent double financial loss.
