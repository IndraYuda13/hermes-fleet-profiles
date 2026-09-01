# Payment Gateway & Fulfillment Engine Reliability & Security Architecture

Patterns, anti-tampering guards, and concurrency controls for high-throughput digital goods (top-up, vouchers, digital cashiers, PPOB) where supplier margins are thin (1-3%) and double fulfillment or price tampering is fatal.

---

## 1. Concurrency & Double-Fulfillment Prevention (TOCTOU Elimination)

### The Race Condition Problem
When a customer clicks "Check Payment / Cek Status" while a Payment Gateway (PG) webhook hits the server at the exact same millisecond:
- Naive read-then-write: `if (order.status === 'PENDING') { await fulfillSupplier(order); }`
- Result: Both execution contexts see `PENDING`, both fire upstream provider orders, causing **double balance deduction** on non-refundable supplier balances.

### Standard Fix: Atomic Conditional SQL Lock
```sql
-- Atomic state transition lock in PostgreSQL / MySQL
UPDATE orders 
SET status = 'PROCESSING_SUPPLIER', 
    paid_at = NOW(),
    updated_at = NOW() 
WHERE id = :order_id 
  AND status = 'PENDING_PAYMENT'
RETURNING id, final_payable_amount, target_account_id, sku_code;
```
*Rule:* Only the process that receives `rows_affected == 1` proceeds to enqueue/dispatch fulfillment. A return of `0` halts immediately.

---

## 2. Webhook Fast-Ack & Transactional Outbox Pattern

Never execute synchronous supplier API calls inside the incoming PG webhook handler.

1. **Ingest & Verify (<10ms):** Validate signature, verify timestamp drift, check event idempotency.
2. **Atomic Record:** Transition order state to `PAID` / insert outbox event record within a DB transaction.
3. **Fast Ack:** Return `HTTP 200 OK` to Payment Gateway in `<200ms` to prevent PG connection timeouts and webhook retry storms.
4. **Asynchronous Worker:** Background queue worker picks up the outbox event to dispatch upstream fulfillment.

---

## 3. Webhook Security, Integrity & Anti-Replay

### Raw-Body HMAC-SHA256 Verification
Frameworks that parse JSON before signature checking alter key ordering and whitespace, leading to signature invalidation or bypass.

```python
import hmac
import hashlib

def verify_webhook_signature(raw_body: bytes, received_signature: str, secret_key: bytes) -> bool:
    expected = hmac.new(key=secret_key, msg=raw_body, digestmod=hashlib.sha256).hexdigest()
    # Constant-time comparison prevents timing side-channel attacks
    return hmac.compare_digest(expected, received_signature)
```

```javascript
const crypto = require('crypto');

function verifyWebhookSignature(rawBodyBuffer, receivedSignature, secret) {
  const expected = crypto.createHmac('sha256', secret).update(rawBodyBuffer).digest('hex');
  const bufExpected = Buffer.from(expected, 'utf8');
  const bufReceived = Buffer.from(receivedSignature, 'utf8');
  if (bufExpected.length !== bufReceived.length) return false;
  return crypto.timingSafeEqual(bufExpected, bufReceived);
}
```

### Anti-Replay & Deduplication
1. **Timestamp Drift Check:**
   Reject callbacks where $|T_{\text{server}} - T_{\text{webhook}}| > 300\text{ seconds}$ (5 minutes).
2. **Distributed Redis Idempotency Lock:**
   ```bash
   SET payment:event_dedup:{provider_code}:{event_id} 1 EX 86400 NX
   ```
   If Redis returns `NULL` (key exists), return `HTTP 200 OK` immediately without re-processing.

---

## 4. Zero-Trust Pricing & Target Account Immutability

1. **Client Price Paranoia:**
   Frontend never passes prices or totals. Client passes only `sku_id` and `target_user_id`. Backend computes price from database truth at order creation time.
2. **Immutable Order Snapshot:**
   Snapshot `base_price`, `admin_fee`, `discount_amount`, `unique_code`, `final_payable_amount`, `target_user_id`, `zone_id` at creation.
3. **Exact Amount Match Assertion:**
   ```javascript
   if (BigInt(webhook.paid_amount) !== BigInt(order.final_payable_amount)) {
     await flagSuspiciousPayment(order.id, webhook);
     throw new Error('Payment amount mismatch: possible tampering');
   }
   ```
4. **Currency Data Types:**
   Never use IEEE 754 floating point numbers (`FLOAT` / `DOUBLE`). Always use `BIGINT` (in lowest currency units, e.g. Rupiah/Cents) or `DECIMAL(15,2)`.

---

## 5. Upstream H2H Fulfillment & Circuit Breakers

1. **Deterministic Upstream Idempotency:**
   Pass LemonTopup internal `order_id` (or deterministic UUID) as the provider's `ref_id` / `partner_trx_id`. On network drop/timeout, retrying with the identical `ref_id` causes the provider to return the existing transaction state instead of placing a duplicate order.
2. **Exponential Backoff with Full Jitter:**
   $$T_{\text{wait}} = \min(T_{\text{max}}, T_{\text{base}} \times 2^{\text{attempt}}) + \text{random\_jitter}(0, 500\text{ms})$$
   ($T_{\text{base}} = 2\text{s}$, $T_{\text{max}} = 60\text{s}$, max attempts = 4).
3. **Circuit Breaker:**
   If upstream provider returns $>5$ consecutive 5xx errors or network timeouts within 1 minute, trip the circuit breaker and switch to backup aggregator or queue for manual operator review.

---

## 6. Periodic Reconciliation & Ledger Settlement

- **Polling Worker (1-2 min interval):** Scans orders in `PROCESSING_SUPPLIER` or `SUPPLIER_PENDING` older than 2 minutes and queries supplier status endpoint using `ref_id`.
- **Daily Double-Entry Sync:** Reconcile PG settlement payouts vs Supplier balance deductions vs Internal database revenue to catch discrepancies automatically.
