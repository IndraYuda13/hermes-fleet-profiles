---
name: sms-activate-and-5sim-otp
description: Use when integrating virtual number SMS OTP APIs.
---

# Virtual Number & SMS OTP API Integration

SOP and reference patterns for virtual number and SMS OTP provider APIs (specifically 5sim.net and SMS-Activate style pull-based APIs).

## 1. Provider Architecture: 5sim.net

5sim.net (and 5sim.biz) does **NOT** provide Webhooks or callback URLs. It operates strictly on **HTTP GET polling**.

- **Base URL:** `https://5sim.net/v1/user`
- **Auth Header:** `Authorization: Bearer <API_KEY>`

### Primary Lifecycle Endpoints:
1. **Get Profile & Balance:**
   `GET /v1/user/profile` -> returns `id`, `email`, `balance` (USD), `rating` (0..96), `frozen_balance`.
2. **List Countries & Operators (Guest):**
   `GET /v1/guest/countries` -> directory of 150+ countries with ISO, dial prefix (`+62`, `+1`), and operator names.
3. **List Products & Live Stock (Guest):**
   `GET /v1/guest/products/{country}/{operator}` -> products dict with `Category`, `Qty` (live stock), and `Price` (wholesale USD).
4. **Buy Activation Number:**
   `GET /v1/user/buy/activation/{country}/{operator}/{product}`
   Example: `GET /v1/user/buy/activation/indonesia/any/whatsapp`
5. **Poll Order Status & SMS:**
   `GET /v1/user/check/{order_id}`
6. **Finish Order (Confirm received):**
   `GET /v1/user/finish/{order_id}` (grants +0.5 rating points)
7. **Cancel Order (Refund balance):**
   `GET /v1/user/cancel/{order_id}` (valid only before SMS is received; auto-refunds USD balance; penalty -0.10 rating)
8. **Ban Number (Number invalid/registered):**
   `GET /v1/user/ban/{order_id}` (auto-refunds USD balance; penalty -0.10 rating)

## 2. Invariants & Best Practices

1. **Polling Timing:** Poll every 3–5 seconds. Never poll faster than 1s to avoid hitting rate limits.
2. **Rate Limits:** 100 req/sec per API Key and per IP. Exceeding 5 times in 10 minutes triggers a 10-minute ban.
3. **Rating System Protection & Proactive Cancellation:**
   - Finished order: `+0.5` rating
   - Manual cancel: `-0.10` rating
   - Timeout (letting 15 min expiry run out): `-0.15` rating
   - Ban number: `-0.10` rating
   - **Critical Cancellation Rules:**
     * **User Self-Cancel:** Allow users to self-cancel after a minimum cooldown (e.g. 2 minutes) if no SMS has arrived. If SMS has arrived, cancel/ban is strictly blocked.
     * **Proactive Background Auto-Cancel:** Always proactively call `/cancel/{order_id}` via background worker before the 15-minute expiration (e.g. at minute 10) if no SMS arrives. Letting orders time out passively incurs the maximum penalty (-0.15), damaging account rating which blocks ordering for 24 hours if rating reaches 0. Proactive cancel also guarantees 100% USD refund to provider balance, which can be refunded 100% to the user's internal wallet balance.
4. **Local Sprite Sheet Asset Invariant (Zero Scraping Dependency):**
   - 5sim does **NOT** provide product icon URLs in its API responses. The web interface renders icons via a single combined sprite sheet (`https://5sim.net/media/sprites/services.webp` and fallback `services.png`) mapped to 352 CSS classes (`.services-<product>`).
   - When building a web storefront, download both sprite image files into local `/static/sprites/` and extract the 352 CSS coordinate rules locally into `services-sprite.css`. Never scrape icons on the fly or rely on third-party hotlinking. Provide a clean SVG/monogram fallback for newly introduced products not yet in the sprite sheet.
5. **1-Click Wallet Checkout Pattern vs QRIS Deposit:**
   - Never force users to scan QRIS for individual micro-OTP purchases ($0.05–$0.50). This introduces high friction and payment gateway overhead.
   - Mandate user authentication (bcrypt + JWT) and internal wallet balance. Purchases must be 1-click instant, using atomic database locking (`BEGIN IMMEDIATE` in SQLite) to deduct balance and request the number in one transaction.
   - Direct QRIS payment gateway (e.g. PaKasir) exclusively to a "Top Up / Isi Saldo" drawer. Charge the payment gateway fee to the buyer (buyer fee invariant) so the deposited wallet balance remains exact and whole.
6. **Dynamic Retail Pricing Engine & Zero-Loss Invariant:**
   When reselling 5sim OTP numbers in local fiat (such as IDR via QRIS):
   - Always apply a safe forex buffer (e.g. Rp 17,000 / USD) to cover currency volatility and crypto/card deposit spread (3–5%).
   - Apply profit margin (e.g. 25–50%) plus platform flat fee (e.g. Rp 500) to cover hosting and gateway fees.
   - Enforce a strict minimum price floor (e.g. Rp 2,000) to ensure micro-cost numbers ($0.05–$0.10) remain profitable.
   - Round up to clean currency increments (e.g. nearest 100).
   - **In-Stock Candidate Alignment Invariant (Never Price Against 0-Stock Operators):**
     * Never compute catalog or retail prices using `min(all_costs)` across all operators if the cheapest operator has `count == 0`. Pricing against a 0-stock phantom operator (e.g. $0.0897) while buying an active in-stock operator (e.g. $0.2141) creates immediate negative margins and direct store losses.
     * The retail price MUST be derived from the specific candidate operator that will actually be purchased (filtered to `count > 0` and prioritized by delivery rate).
   - **Strict Maximum Wholesale Cost Guard (`max_price`):**
     * At checkout, compute the break-even wholesale cost ceiling: `max_breakeven_usd = round(price_idr / exchange_rate, 4)`.
     * Never dispatch order attempts to operators whose wholesale cost exceeds `max_breakeven_usd`.
     * Always pass `max_price = max_breakeven_usd` to the upstream provider's buy API call (e.g. 5sim `maxPrice` parameter) to guarantee fail-safe rejection if provider prices spike dynamically.
7. **The `operator="any"` Upstream Trap & Candidate Stock Resolution:**
   - In 5sim, passing `operator="any"` often ONLY checks physical carrier pools (Claro, Tigo, Telkomsel, etc.), which frequently have 0 stock. The vast majority of numbers exist in virtual pools (`virtual34`, `virtual53`, `virtual58`, `virtual65`). Requesting `any` blindly will return `"no free phones"` even when hundreds of thousands of numbers exist under virtual operators.
   - **Operator Quality & Success Rate Metrics (`rate`):** In 5sim `/v1/guest/prices`, virtual operators often advertise huge counts (e.g., 79,000+) but with `rate: 0` (0% success delivery rate). These providers frequently fail upstream and auto-cancel within 1–2 minutes.
   - **Resolution Sorting Hierarchy:** Query `/v1/guest/prices` for `(country, product)`, filter operators with `count > 0`, and sort candidates by:
     1. Real physical carriers first (`not op.startswith("virtual")`).
     2. Operators with proven delivery rates (`rate > 0`).
     3. Lowest wholesale cost.
     4. Highest available stock count.
   - Iterate candidate operators sequentially. If all candidates fail or return out-of-stock, roll back user balance and report honest exhaustion.
8. **Strict Zero-Simulation & Production Fail-Closed Invariant:**
   - Never allow client-side fake mock fallbacks (`// Fallback for testing`, generating fake `OTP-XXXXXX` codes, simulated phone numbers, or hardcoded prices) when an allocation API returns an error or 400.
   - When upstream provider allocation fails: immediately roll back the user's wallet balance atomically with a ledger entry (`rollback`), return the honest provider error detail to the client, and keep the user's balance and order history 100% bound to database truth. Fake mock fallbacks cause ghost orders, 404 lookup errors in history, and phantom balance deductions.
9. **User-Facing Semantic Status Badging (Anti-Raw-Enum Slop):**
   - Never expose raw database enum strings (such as `number_ready`, `refunded`, `timeout`, `canceled`, `banned`) directly to end users.
   - Map raw states to localized, human-friendly semantic status badges with appropriate visual styling:
     * `number_ready` / `active` -> "Menunggu SMS" (Warm amber/yellow pill, active/waiting)
     * `completed` -> "SMS Diterima" (Emerald green pill, success)
     * `canceled` / `refunded` -> "Dana Dikembalikan" (Soft blue pill, financial reversal)
     * `timeout` / `expired` -> "Kedaluwarsa (Refund)" (Muted slate/gray pill)
10. **Client Balance Single Source of Truth (No Local Arithmetic):**
   - In UI checkout, cancellation, or refund flows, never perform client-side manual balance arithmetic (`state.balance += refund` or `state.balance -= price`).
   - The backend database ledger is the sole authority. Always re-synchronize the user session directly from `/api/auth/me` or account endpoint on state changes. Local additions compound into phantom inflated balances whenever a user re-opens a refunded order from history.
11. **Terminal View vs Active Polling Separation:**
   - In order tracking modals, inspect `order.status` before starting intervals. If the order is already in a terminal state (`completed`, `refunded`, `canceled`, `timeout`), render static terminal state views immediately.
   - Never start countdown timers or polling loops on closed orders; polling already-closed orders triggers duplicate refund toasts, unwanted background requests, and race conditions.
12. **Storefront Editorial Cleanliness (Zero Developer Slop & No Bullet Dots):**
   - Strictly prohibit developer-facing telemetry badges (e.g., "352 OFFICIAL ICONS", internal debug tags, mock statistics) on consumer storefronts. Users evaluate utility, not framework self-praise.
   - Ban bullet separator characters (`•`, `&bull;`, `\u2022`) in status rows, hero taglines, and metadata badges. Use clean editorial em-dashes (`—`) or structured badge pills.
13. **Explicit UTC Timezone Contract for Countdown Timers (The 7-Hour Premature Timeout Trap):**
   - When SQLite or backend databases store UTC timestamps as plain strings without timezone indicators (e.g. `2026-09-17 11:46:37`), client browsers in positive GMT offsets (e.g. Asia/Jakarta UTC+7) parse `new Date(str)` as *local device time* instead of UTC.
   - This creates an immediate multi-hour artificial gap (e.g. 25,200s), causing 10-minute order timers to read `00:00` at second 0 and trigger premature auto-cancellations.
   - **Contract Rule:**
     * Backend must always emit explicit ISO-8601 strings with `"Z"` suffix (e.g. `strftime('%Y-%m-%dT%H:%M:%SZ')` or `.isoformat() + 'Z'`).
     * Frontend must parse dates through a defensive `parseUTCDate` normalizer that automatically appends `Z` if no timezone marker exists, and clamps `elapsedSeconds >= 0`.
14. **Cancellation & Refund Fail-Closed Verification (No Optimistic Refunds):**
   - In automated or manual cancellation routines, the frontend must NEVER transition into a "Refunded" UI state or announce balance replenishment unless the backend cancellation endpoint explicitly returns HTTP 200 OK.
   - If the backend rejects the cancellation (such as active 2-minute provider cooldown with HTTP 400), the order remains active in the database. Falsely displaying a refund message causes extreme user distrust when refreshing the page shows the balance still deducted.
15. **Masked Number Rejection Invariant (`*` in Phone Numbers):**
   - Certain virtual operators or unstable provider pools on 5sim return masked phone numbers containing asterisks (e.g. `+447****7658`) or truncated strings with fewer than 7 digits.
   - End users cannot enter a masked number into the target verification app (e.g. WhatsApp, Shopee, Telegram).
   - **Enforcement:** Immediately inspect `phone = str(order.get('phone', '')).strip()`. If `*` in phone or length < 7 digits:
     1. Reject the allocated order immediately.
     2. Call `/cancel/{order_id}` on 5sim to release the number and recover provider funds without penalty.
     3. Continue to the next candidate operator in the resolved list.
     4. Never persist or surface a masked phone number to the buyer. If all candidates fail or return masked numbers, roll back user balance 100% and notify honestly.

## 3. Reusable Async Polling Pattern (Python)

```python
import asyncio
import httpx

API_KEY = "YOUR_API_KEY"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Accept": "application/json"}

async def get_5sim_otp(order_id: int, max_wait_sec: int = 180, poll_interval: int = 4) -> str | None:
    async with httpx.AsyncClient(timeout=10) as client:
        start = asyncio.get_event_loop().time()
        check_url = f"https://5sim.net/v1/user/check/{order_id}"
        finish_url = f"https://5sim.net/v1/user/finish/{order_id}"
        cancel_url = f"https://5sim.net/v1/user/cancel/{order_id}"

        while asyncio.get_event_loop().time() - start < max_wait_sec:
            try:
                res = await client.get(check_url, headers=HEADERS)
                if res.status_code == 200:
                    data = res.json()
                    sms_list = data.get("sms") or []
                    if sms_list:
                        otp_code = sms_list[-1].get("code")
                        await client.get(finish_url, headers=HEADERS)
                        return otp_code
                    if data.get("status") in ["CANCELED", "TIMEOUT", "BANNED"]:
                        return None
            except Exception:
                pass
            await asyncio.sleep(poll_interval)

        # Proactive cancel to save rating if timeout reached
        try:
            await client.get(cancel_url, headers=HEADERS)
        except Exception:
            pass
        return None
```
