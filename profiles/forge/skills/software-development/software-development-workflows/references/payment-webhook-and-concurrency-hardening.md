# Payment Webhook, Concurrency, and Timezone Hardening

## Overview
Critical pitfalls and proven architectural patterns for payment callback processing, concurrency safety, and transaction reconciliation in topup/e-commerce backend systems.

## 1. Webhook Concurrency & Idempotency Locking
- **Race Condition Hazard:** Payment gateways (e.g. Pakasir, Midtrans, Xendit) and asynchronous background polling workers frequently trigger settlement simultaneously.
- **Double Fulfillment Pitfall:** If worker A and worker B both inspect order status as `waiting_payment`, both might call upstream provider APIs (e.g. Digiflazz topup), causing double charges.
- **Atomic Database Locking Pattern:**
  Use an atomic state-transition query directly at the database level:
  ```sql
  UPDATE app_orders
  SET status = 'submitting', updated_at = :now
  WHERE order_id = :order_id AND status IN ('waiting_payment', 'paid_submit_failed');
  ```
  If `affected_rows == 0`, immediately return `200 OK` (idempotent duplicate acknowledgment) without initiating fulfillment.

## 2. Multi-Provider HMAC Verification & Header Map

| Provider | Signature Header | Raw Payload Schema | Timestamp Header |
| :--- | :--- | :--- | :--- |
| Pakasir | `X-Pakasir-Signature` | `HMAC-SHA256(raw_body, secret)` | `X-Pakasir-Timestamp` |
| Xendit | `x-callback-token` | Verification via pre-shared secret string / HMAC | N/A |
| Midtrans | N/A (In-Body `signature_key`) | `SHA512(order_id + status_code + gross_amount + server_key)` | N/A |
| Digiflazz (H2H) | In-Body `sign` | `MD5(username + api_key + ref_id)` | N/A |
| VIP Reseller | In-Body `sign` | `MD5(api_id + api_key)` | N/A |

### Raw Body HMAC Verification
Verify signatures against raw bytes directly from the socket before JSON body-parsing to prevent deserialization drift. Always use constant-time comparison (`hmac.compare_digest`) to prevent timing attacks.

## 3. Transactional Outbox Pattern & Fast-Ack Ingestion

```sql
-- Schema Outbox
CREATE TABLE payment_outbox (
    id BIGSERIAL PRIMARY KEY,
    order_id VARCHAR(64) NOT NULL,
    event_type VARCHAR(32) NOT NULL,
    payload JSONB NOT NULL,
    status VARCHAR(16) DEFAULT 'PENDING',
    retry_count INT DEFAULT 0,
    next_retry_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_payment_outbox_processing ON payment_outbox(status, next_retry_at)
WHERE status = 'PENDING';
```

### Fast-Ack Ingestion Workflow
```
[ PG Ingress Socket ]
         |
         +---> [ Read Raw Bytes ] ---> [ Constant-Time HMAC Check ] (Fail: 401 Unauthorized)
         |
         +---> [ Redis SETNX Dedup ] (Duplicate: Immediate 200 OK)
         |
         +---> [ BEGIN DB Transaction ]
                 |
                 +-> UPDATE orders SET status='PROCESSING_SUPPLIER' WHERE id=:id AND status='PENDING_PAYMENT'
                 +-> INSERT INTO payment_outbox (order_id, event_type, payload) VALUES (...)
                 |
               [ COMMIT ]
         |
         +---> [ Return HTTP 200 OK (<200ms) ]
```

## 4. Standardized Timezone Parsing (Python 3.12+)
- **Manual String Offset Pitfall:** Never parse ISO timestamps using manual string splitting or hardcoded second offsets (e.g. `completed_at.split('.')[0] + 25200`). This breaks across timezone shifts, leap seconds, and string format variations.
- **Python 3.12 `datetime.utcnow()` Deprecation:** `datetime.utcnow()` is deprecated.
- **Proven Pattern:**
  Store and parse all timestamps as timezone-aware UTC:
  ```python
  from datetime import datetime, timezone

  # Current UTC timestamp:
  now_utc = datetime.now(timezone.utc)

  # Parsing ISO-8601 string:
  clean_iso = raw_timestamp.replace('Z', '+00:00')
  completed_dt = datetime.fromisoformat(clean_iso).astimezone(timezone.utc)
  completed_ts = int(completed_dt.timestamp())
  ```

## 5. Database Fallback vs Fail-Closed Policy
- **Plaintext JSON Storage Pitfall:** Storing financial transactions in unencrypted local JSON files on disk when the primary database is unreachable creates data desynchronization, file corruption risks under concurrent writes, and PII leaks.
- **Policy:** In financial/topup backends, enforce **fail-closed / fail-safe** behavior. Return HTTP `503 Service Unavailable` with structured retry guidance rather than silent unencrypted disk buffering.

## 6. Game ID Inquiry Engine & Downstream Fallbacks
- **Inline Validation:** Validate user IDs in real-time before payment rather than post-payment.
- **Graceful Fallback:** If upstream inquiry provider is down or times out, never block the checkout flow. Return an explicit flag (`supports_inquiry=false` or `inquiry_available=false`) and prompt the buyer to double-check their destination ID manually.
