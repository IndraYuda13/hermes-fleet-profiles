---
name: pakasir-payment-gateway
description: "Use when integrating PaKasir QRIS, VA, and webhook APIs."
---

# PaKasir Payment Gateway Integration & Operations

## Overview
PaKasir is an Indonesian payment gateway service supporting Dynamic QRIS and multi-bank Virtual Accounts (BCA, BRI, BNI, CIMB, Permata, etc.) under PT. Geksa.

Official documentation publishes two concurrent profiles:
1. **Legacy Non-Versioned Profile:** Documented at `/p/docs` with base URL `https://app.pakasir.com/api`.
2. **Candidate v2 Profile:** Documented at `/p/get-started`, `/p/create-transaction`, `/p/transaction-status`, `/p/webhook`, and `/p/fee-calculator`.

## API Endpoints & Contracts

### A. Legacy Non-Versioned Profile (`app.pakasir.com/api`)

Base URL: `https://app.pakasir.com/api`

### 1. Create Dynamic QRIS Transaction
- **Method:** `POST`
- **URL:** `https://app.pakasir.com/api/transactioncreate/qris`
- **Request Body (JSON):**
  ```json
  {
    "project": "<slug>",
    "order_id": "<unique_order_id>",
    "amount": 10000,
    "api_key": "<project_api_key>"
  }
  ```
- **Response Structure:**
  ```json
  {
    "payment": {
      "project": "lemon-ai-store",
      "order_id": "LEM-08271320-ABCD",
      "amount": 6000,
      "fee": 352,
      "total_payment": 6352,
      "payment_method": "qris",
      "payment_number": "00020101021226670016COM.NOBUBANK...",
      "expired_at": "2026-08-27T07:27:38.227Z"
    }
  }
  ```

### 2. Check Transaction Detail / Status
- **Method:** `GET`
- **URL:** `https://app.pakasir.com/api/transactiondetail?project={slug}&amount={amount}&order_id={order_id}&api_key={api_key}`
- **Security Rule:** Legacy detail endpoint places `api_key` in the query string. Redact query parameters before logging outbound requests to APM, proxies, or error monitors.
- **Response Structure:**
  ```json
  {
    "transaction": {
      "project": "<slug>",
      "order_id": "<order_id>",
      "amount": 6000,
      "status": "completed",
      "payment_method": "qris",
      "completed_at": "2026-08-27T13:35:00.000+07:00"
    }
  }
  ```

### 3. Cancel Transaction & Simulation
- **Cancel URL:** `POST https://app.pakasir.com/api/transactioncancel` with `project`, `order_id`, `amount`, `api_key`.
- **Simulation URL (Sandbox):** `POST https://app.pakasir.com/api/paymentsimulation` with same parameters.

### B. Candidate v2 Profile (`app.pakasir.com/api/v2`)

#### 1. Create Transaction (v2)
- **Method:** `POST`
- **URL:** `https://app.pakasir.com/api/v2/create-transaction/{slug}/{order_id}`
- **Headers:** `Content-Type: application/json`, `X-Signature: <signature>`
- **Request Body (JSON):**
  ```json
  {
    "method": "qris",
    "amount": 10000
  }
  ```
- **Behavior:** Public docs describe this endpoint as idempotent *find-or-create new* (repeating identical parameters returns the existing response). Rate limit is 2 requests/second.
- **Response:** Returns top-level object containing `txn_id`, `qr_string`, `fee`, `total_payment`, `status`, `completed_at`, `expired_at`.

#### 2. Check Transaction Status (v2)
- **Method:** `GET`
- **URL:** `https://app.pakasir.com/api/v2/transaction-status/{slug}/{txn_id}`
- **Headers:** `X-Api-Key: <project_api_key>`
- **Behavior:** Public rate limit is 1 query every 4 seconds per transaction. Returns `payment_id`, `status` (`pending`, `completed`, `canceled`), `completed_at`.

#### 3. Public Fee Calculator (v2)
- **Method:** `GET`
- **URL:** `https://app.pakasir.com/api/v2/payment-fee/{amount}`
- **Note:** Public estimate endpoint; does not establish contractual fee allocation (merchant-paid vs customer-paid).

## Critical Architectural Invariants & Integration Traps

1. **Strict Profile Isolation (No Silent Fallback):**
   Legacy and v2 profiles differ in endpoint paths, auth headers (`api_key` in payload/query vs `X-Signature`/`X-Api-Key`), and response schema (`payment_number` vs `qr_string`, nested `payment` vs top-level `txn_id`). Never implement automatic fallback between legacy and v2. Keep the profile explicitly configured (`PAKASIR_API_PROFILE=legacy` or `v2`) or fail closed as `UNRESOLVED` (mock-only).
2. **v2 `X-Signature` Canonical Input Trap:**
   Public v2 documentation displays `X-Signature` in create requests but does NOT publish the canonical string format, secret key source, or hashing algorithm. Never invent an HMAC formula. The exact signature specification must be confirmed with merchant support or official sandbox test vectors before enabling v2 in production.
3. **Internal Business Cutoff vs Remote Provider Expiry:**
   Do not assume a remote 10-minute hard QR death. Public v2 status documentation explicitly states cancellation occurs after 24 hours (`melewati 1x24 jam`). The 10-minute (+2m grace) window is an internal business cutoff in your local database. If a buyer pays after 12 minutes, the gateway may still clear the funds. Handle late payments via `ReconciliationCase` and wallet credit rather than silent overselling.
4. **Webhook Inconsistency & Mandatory Authenticated Inquiry:**
   In official v2 webhook documentation, the example payload for a "successful payment" paradoxically displayed `"status": "pending"` and `"completed_at": null`. Webhook callbacks must be treated strictly as untrusted notification hints. Never settle an order or deliver goods directly from the webhook payload. Always execute an authoritative status inquiry (`/api/transactiondetail` or `/api/v2/transaction-status`) before updating order status.
5. **Merchant Category Restrictions (`PK-MERCHANT`):**
   Pakasir terms explicitly list digital/premium account sales among unsupported/non-focus categories. Keep live QRIS activation blocked (`PAYMENTS_LIVE_ENABLED=false`) until merchant account KYC and written project approval for the specific SKU/business model are verified.
6. **Query Credential Sanitization:**
   Legacy `GET /api/transactiondetail` places `api_key` in the URL query string. Always scrub or redact query parameters in logging middleware, reverse proxies, and error monitoring tools to prevent secret leakage.
7. **Zero Fabricated QR on Creation Timeout/Error Invariant:**
   When QR creation fails or times out, never catch the error and substitute a hardcoded, static, or placeholder QR string to appease the UI. A fabricated QR leads to payment misdirection where users pay an untracked target while the system registers an unverified invoice. Instead, record the payment attempt as `CREATE_UNKNOWN` (or fail-closed), initiate authenticated inquiry or recovery using the same immutable order ID, and withhold QR display until a verified provider response matches accepted amounts and expiry.
8. **Simulation Endpoint Segregation (Zero In-Source Forced-Paid Simulator):**
   Never implement state-changing simulation query parameters (e.g. `GET .../check?simulate=paid`) in production application routes. Client-triggered payment settlement, stock commitment, and fulfillment advancement without provider inquiry bypass the money source-of-truth and expose routes to CSRF, prefetching crawlers, and unauthorized fulfillment. Mocks must live strictly in isolated test harnesses or dedicated mock adapters (`MockPakasirAdapter`) under `NODE_ENV !== 'production'`, never accessible in public route handlers.

## Webhook Handling Protocol

When payment succeeds, PaKasir dispatches a `POST` request to the project's configured webhook URL.

### Webhook Payload:
```json
{
  "amount": 6000,
  "order_id": "LEM-08271320-ABCD",
  "project": "lemon-ai-store",
  "status": "completed",
  "payment_method": "qris",
  "completed_at": "2026-08-27T13:35:00.000+07:00"
}
```

### Verification & Failsafe Rules:
1. **Match Project Slug:** Ignore any payload where `payload.project != configured_project`.
2. **Re-query Transaction Detail & URL Secret Token:**
   - PaKasir payloads do not feature asymmetric HMAC signatures. Always make an independent verification call to `GET /api/transactiondetail` to confirm `status == 'completed'`.
   - **Anti-Amplification DoS & Fail-Closed Token Guard:** Because verification requires an outbound HTTP call to PaKasir, protect the endpoint against fake-payload flooding by registering a secret query/path token in the PaKasir dashboard URL (e.g. `/webhook/pakasir?token=<secret>`). Immediately reject requests with invalid tokens before executing any outbound verification.
   - **Fail-Closed Secret Invariant:** If the webhook secret is empty, undefined, or missing from environment variables, verification must **fail-closed** (`return false`). Never default to `true` on missing configuration (`if (!secret) return true;`), as that allows unauthorized external callers to forge completed transactions when environment configuration is incomplete.
3. **Atomic DB State Lock (Anti-Double Fulfillment):** When a webhook and background poller run concurrently, both can detect a paid order at the same time. Never use a read-then-write pattern or return truthy order objects if already paid. Use atomic SQL transitions:
   ```sql
   UPDATE orders
   SET status = 'paid', paid_at = datetime('now')
   WHERE order_id = ? AND status = 'pending';
   ```
   Only proceed to `deliver_product()` if `cur.rowcount > 0`. If `rowcount == 0` (another worker already won the race), return `200 OK` and skip duplicate delivery.
4. **Fast-Ack Webhook & Decoupled Fulfillment:** Never execute slow or variable-latency upstream fulfillment (such as H2H top-up APIs like Digiflazz, which can take 5–20 seconds) synchronously inside the webhook handler. After verifying the transaction and acquiring the atomic claim lock, return `200 OK` immediately (<100ms) to PaKasir and dispatch fulfillment to an asynchronous background task / queue. Synchronous processing risks gateway HTTP timeouts and redundant retry storms.
5. **Idempotency Key to Upstream H2H:** When dispatching top-ups to upstream providers (e.g. Digiflazz), always pass the unique internal `order_id` as the upstream `ref_id` so provider-side duplicate rejection protects balance even under retry storms.
6. **Background Poller Fallback & Mobile Tab-Switch Re-sync:**
   - In sandbox or flaky network conditions, webhooks may experience delays. Always run a background polling worker (e.g. interval 3–5 seconds) querying pending transactions via `/api/transactiondetail` to auto-resolve paid orders in real-time.
   - **Mobile Browser Throttling Fix:** When mobile users switch away to their e-wallet / banking apps to pay, mobile browsers (Safari/Chrome) throttle or freeze background JS timers. Attach a `visibilitychange` listener on the QRIS checkout page:
     ```javascript
     document.addEventListener('visibilitychange', () => {
       if (document.visibilityState === 'visible') checkPaymentStatus();
     });
     ```
     This triggers immediate status re-validation the moment the user returns to the browser.
7. **Upstream Timeout Non-Refund Invariant (Prevent Financial Leaks):**
   - Transient network/read timeouts during upstream H2H fulfillment (e.g. Digiflazz HTTP timeout) must **NEVER** trigger automatic buyer refund.
   - A timeout represents an indeterminate state (unknown status), not an execution failure. The upstream provider may have successfully charged merchant balance and delivered the item while the HTTP connection dropped.
   - Immediate auto-refund creates double financial loss (product delivered + money refunded).
   - Flag the order as `pending_reconciliation` (or `paid_submit_failed`) and require resolution via upstream webhook/status check before any manual or automated refund is evaluated.
8. **State Terminal Guard (Anti-Reversal):**
   - Out-of-order webhook deliveries or late retry callbacks carrying a `failed` or `pending` status must never revert an order that has already reached terminal `completed` / `success` state.
   - Enforce unidirectional state machine transitions (`waiting_payment` -> `submitting` -> `success` / `failed`).
9. **Mobile QRIS Ergonomics (1-Tap Save to Gallery):**
   - Mobile users shopping on a smartphone cannot point their camera at their own screen to scan QRIS.
   - Always provide a 1-tap **"Simpan QRIS ke Galeri"** (Download Image) button alongside the rendered QR code using Canvas/Blob data URL so users can easily select the QR image from their m-banking / e-wallet gallery scanner.
10. **Chat Cleanliness (Auto-Delete Invoice):** Persist `chat_id` and `message_id` of the invoice/QR image when generated. Immediately call `bot.delete_message` on the invoice upon payment verification before delivering the fulfillment message.
11. **Order Expiration & Cancellation Handling:**
   - Run periodic sweep (e.g. in background poller) for pending orders exceeding timeout (e.g. 15 mins).
   - Upon timeout or user manual cancellation: call `transactioncancel`, release database reservation lock (`status = 'available'`), delete the QR invoice message from chat, and send clean feedback.
12. **Bulk Delivery via File Attachment (Anti-4096 Character Limit):**
   - For single item orders (`qty == 1`): deliver in chat text message directly.
   - For bulk / multi-item orders (`qty > 1` or `qty > 5`): generate an in-memory `.txt` file attachment containing all items/tokens/links and send via `send_document` to prevent Telegram's 4096 character message truncation error.
13. **Admin-Buyer Deduplication:**
   - If `buyer_user_id == ADMIN_USER_ID`, suppress the separate admin sales notification to prevent duplicate pings in the admin's personal chat.

## Web E-Commerce Dual-Payment Architecture (Wallet Balance vs Direct QRIS)

In web stores supporting both wallet balance and direct QRIS checkout:

### 1. Distinct Order ID Namespaces
Distinguish transaction types via deterministic prefixes in `order_id` so the shared webhook handler routes correctly without ambiguous table lookups:
- `DEP-<timestamp>-<user_id>` for balance deposit.
- `ORD-<timestamp>-<user_id>` for direct cart checkout.

### 2. Atomic Wallet Ledger Invariant (Append-Only)
When checking out using stored user balance, bypass PaKasir entirely and use an atomic conditional decrement inside a database transaction paired with an immutable ledger entry:
```sql
-- 1. Decrement cached balance with row-level safety
UPDATE wallet_accounts
SET balance = balance - :total_amount, updated_at = NOW()
WHERE user_id = :user_id AND balance >= :total_amount;

-- 2. In the same transaction, write the immutable ledger entry
INSERT INTO wallet_ledger (id, user_id, entry_type, amount, balance_after, reference_type, reference_id, description, created_at)
VALUES (:ledger_id, :user_id, 'PURCHASE', -:total_amount, :new_balance, 'ORDER', :order_id, 'Pembayaran pesanan', NOW());
```
- If `rowcount == 0`, immediately fail checkout with `400 Insufficient Balance`.
- Enforce deposit bounds: min deposit (e.g. Rp5.000), max deposit per transaction (e.g. Rp1.000.000), and max balance ceiling (e.g. Rp2.000.000).
- Saldo tidak boleh ditimpa langsung (`balance = X`). Setiap koreksi saldo wajib via entry ledger baru bertipe `ADJUSTMENT` dengan reason dan audit trail aktor/IP.

### 3. Pre-Order Quota, Reservation Window & Grace Period (10m + 2m)
- **Direct QRIS Reservation Hold:** Decrement available stock/quota conditionally when issuing the QRIS invoice (`available = on_hand - reserved - committed`):
  ```sql
  UPDATE variant_stock SET reserved = reserved + :qty WHERE variant_id = :variant_id AND (on_hand - reserved - committed) >= :qty;
  ```
- **Cart Does Not Hold Stock:** Keranjang belanja strictly tidak menahan stok; reservasi hanya terjadi saat checkout QRIS di-submit dan invoice dibuat.
- **10-Minute Expiration + 2-Minute Grace Period:** Invoice PaKasir kedaluwarsa dalam 10 menit, namun latensi kliring bank atau network webhook sering tiba pada menit 10:00–12:00. Worker background baru boleh melepaskan reservasi stok dan membatalkan invoice setelah `12 menit` (10m window + 2m grace period).
- **Late Payment Fee Exclusion on Auto-Credit:** Jika pembayaran valid tiba setelah 12 menit dan stok varian sudah habis direbut pembeli lain:
  - Sistem **tidak boleh melakukan silent oversell**.
  - Atomik kreditkan dana produk ke wallet internal pembeli (`entry_type = 'RECONCILIATION_CREDIT'`).
  - **Biaya QRIS (gateway fee) tidak dikembalikan** ke wallet karena biaya tersebut sudah dipotong agregator/bank.
  - Tandai status pesanan menjadi `RECONCILIATION_REQUIRED` dengan audit trail lengkap.

### 4. Three-Tier Status Decoupling (Payment vs Order vs Item Fulfillment)
Jangan pernah mencampur status pembayaran dengan status pemenuhan ke dalam 1 kolom `status`:
- **Payment Status:** `UNPAID` / `PENDING` -> `PAID` -> `EXPIRED` / `FAILED`
- **Order Status:** `AWAITING_PAYMENT` -> `PAID` / `PROCESSING` -> `PARTIALLY_COMPLETED` -> `COMPLETED` / `CANCELLED`
- **OrderItem Fulfillment Status:** `PENDING` -> `PROCESSING` -> `COMPLETED` / `REFUNDED`
Pemisahan ini esensial untuk pesanan multi-item di mana sebagian produk selesai diproses seketika sementara item lain masih menunggu antrean.

### 5. Real-Time Payment Screen Sync (Polling / SSE)
Web frontends cannot rely on push notifications like Telegram. Expose a lightweight status endpoint `GET /api/orders/{order_id}/status`:
- Frontend polls every 2.5s while active.
- Re-check immediately on `visibilitychange` (user returning from m-banking/e-wallet app).
- Redirect automatically to order confirmation upon `status === 'paid'`.

## Telegram Bot + FastAPI Architecture Pattern

Run both the Telegram Bot (`python-telegram-bot` v20+ async) and Webhook receiver (`FastAPI` + `Uvicorn`) inside a single Python process and event loop:

```python
import asyncio
import io
import qrcode
from fastapi import FastAPI, Request
from telegram.ext import Application
import uvicorn

app = FastAPI()
tg_app = None

@app.post("/webhook/pakasir")
async def webhook_handler(request: Request):
    data = await request.json()
    if data.get("status") in ("completed", "paid"):
        order_id = data.get("order_id")
        # 1. Update database status
        # 2. Deliver product to user via tg_app.bot.send_message
        await tg_app.bot.send_message(chat_id=user_id, text="Product delivered!")
    return {"status": "ok"}

async def main():
    global tg_app
    tg_app = Application.builder().token(BOT_TOKEN).build()
    # Add command/callback handlers...
    await tg_app.initialize()
    await tg_app.start()
    await tg_app.updater.start_polling(drop_pending_updates=True)

    server = uvicorn.Server(uvicorn.Config(app=app, host="127.0.0.1", port=8145))
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
```

## In-Memory QRIS Image Generation

Convert `payment_number` directly to high-contrast QR bytes in memory without disk I/O:
```python
def generate_qris_photo(qr_string: str) -> bytes:
    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(qr_string)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
```
