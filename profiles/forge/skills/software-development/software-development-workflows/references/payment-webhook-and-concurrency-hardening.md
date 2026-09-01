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

## 2. Standardized Timezone Parsing (Python 3.12+)
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

## 3. Database Fallback vs Fail-Closed Policy
- **Plaintext JSON Storage Pitfall:** Storing financial transactions in unencrypted local JSON files on disk when the primary database is unreachable creates data desynchronization, file corruption risks under concurrent writes, and PII leaks.
- **Policy:** In financial/topup backends, enforce **fail-closed / fail-safe** behavior. Return HTTP `503 Service Unavailable` with structured retry guidance rather than silent unencrypted disk buffering.

## 4. Game ID Inquiry Engine & Downstream Fallbacks
- **Inline Validation:** Validate user IDs in real-time before payment rather than post-payment.
- **Graceful Fallback:** If upstream inquiry provider is down or times out, never block the checkout flow. Return an explicit flag (`supports_inquiry=false` or `inquiry_available=false`) and prompt the buyer to double-check their destination ID manually.
