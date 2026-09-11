# Live Game Nickname Inquiry & Debounced Lookup Pattern

Protocol for implementing and verifying real-time game account / nickname validation in digital cashier & topup web interfaces.

## 1. Frontend Real-Time Debounce Architecture
* **Input Debouncing:** Debounce input events (300ms–400ms) on User ID and Zone/Server ID fields.
* **Sequence Token Protection:** Maintain a monotonic sequence counter (`currentInquirySeq`) to drop stale responses arriving out of order during rapid typing.
* **Loading & Status Feedback:**
  * Render an animated checking pill (`.inquiry-pill.checking`) during in-flight network requests.
  * Render a high-contrast success pill (`.inquiry-pill.valid`) showing verified nickname upon match.
  * Render an alert warning pill (`.inquiry-pill.warning`) on invalid ID or account not found.

```javascript
let currentInquirySeq = 0;
let inquiryDebounceTimer = null;

function triggerDebouncedInquiry(brandKey, form, container) {
  if (inquiryDebounceTimer) clearTimeout(inquiryDebounceTimer);
  inquiryDebounceTimer = setTimeout(() => {
    performLiveInquiry(brandKey, form, container);
  }, 350);
}

async function performLiveInquiry(brandKey, form, container) {
  const seq = ++currentInquirySeq;
  // Send POST /web-api/inquiry/game-id
  // Discard if seq !== currentInquirySeq
}
```

## 2. Upstream Inquiry Architecture & Community Gateways
* **Public & Community Gateways:** Community-maintained endpoints (e.g. `api.isan.eu.org/nickname/ml?id={user_id}&zone={zone_id}`) reverse-engineer official partner inquiry endpoints (Codashop, UniPin, Dunia Games, SmileOne) into lightweight JSON interfaces.
* **Self-Hosted Aggregator Alternative:** When third-party community endpoints experience rate-limits or downtime, implement a local scraper/proxy with session rotation or integrate official aggregator APIs.
* **Non-Blocking Graceful Fallback:** If upstream inquiry APIs or game servers time out (8s timeout budget) or return network errors, NEVER block user checkout. Return `supports_inquiry: false` with an advisory note so the customer can proceed without friction.
* **Zone ID / Server Validation:** Ensure required parameters (e.g. MLBB Zone ID, Genshin server prefix) are validated locally before dispatching external HTTP requests.

## 3. Account History Retention (localStorage)
* Upon successful verification, automatically persist verified target credentials to `localStorage` (max 15 entries) to enable frictionless single-click repeat purchases.
