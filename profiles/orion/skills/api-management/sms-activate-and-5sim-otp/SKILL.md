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
1. **Buy Activation Number:**
   `GET /buy/activation/{country}/{operator}/{product}`
   Example: `GET /buy/activation/indonesia/any/whatsapp`
2. **Poll Order Status & SMS:**
   `GET /check/{order_id}`
3. **Finish Order (Confirm received):**
   `GET /finish/{order_id}`
4. **Cancel Order (Refund balance):**
   `GET /cancel/{order_id}` (valid only before SMS is received)
5. **Ban Number (Number invalid/registered):**
   `GET /ban/{order_id}`

## 2. Invariants & Best Practices

1. **Polling Timing:** Poll every 3–5 seconds. Never poll faster than 1s to avoid hitting rate limits.
2. **Rate Limits:** 100 req/sec per API Key and per IP. Exceeding 5 times in 10 minutes triggers a 10-minute ban.
3. **Rating System Protection:**
   - Finished order: `+0.5` rating
   - Manual cancel: `-0.10` rating
   - Timeout (letting 15 min expiry run out): `-0.15` rating
   - Ban number: `-0.10` rating
   - **Critical:** Always explicitly call `/cancel/{order_id}` if SMS does not arrive within 2–3 minutes. Letting orders time out damages account rating, which can lock the account if it drops to 0.

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
