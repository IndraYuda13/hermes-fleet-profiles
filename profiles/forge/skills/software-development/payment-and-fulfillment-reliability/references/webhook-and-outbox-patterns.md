# Payment Gateway & Webhook Hardening References

## 1. Multi-Provider HMAC Implementasi & Header Map

| Provider | Signature Header | Raw Payload Schema | Timestamp Header |
| :--- | :--- | :--- | :--- |
| Pakasir | `X-Pakasir-Signature` | `HMAC-SHA256(raw_body, secret)` | `X-Pakasir-Timestamp` |
| Xendit | `x-callback-token` | Verification via pre-shared secret string / HMAC | N/A |
| Midtrans | N/A (In-Body `signature_key`) | `SHA512(order_id + status_code + gross_amount + server_key)` | N/A |
| Digiflazz (H2H) | In-Body `sign` | `MD5(username + api_key + ref_id)` | N/A |
| VIP Reseller | In-Body `sign` | `MD5(api_id + api_key)` | N/A |

---

## 2. PostgreSQL Atomic Claim & Outbox Template

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

## 3. Fast-Ack Ingestion Workflow

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
