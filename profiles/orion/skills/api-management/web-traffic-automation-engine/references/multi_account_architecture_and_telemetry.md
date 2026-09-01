# Multi-Account Architecture, Dynamic Limits, Payout & Web Telemetry SOP

Architecture and implementation standards for concurrent multi-worker daemons, dynamic limit scheduling without blind delays, automated FaucetPay USDT TRC20 wallet management, one-click payout execution, live email verification detection, and real-time fleet telemetry dashboards.

---

## 1. Multi-Account Isolation Invariant
- **1 Account : 1 Dedicated Proxy Node:**
  - Assign each account worker a unique physical/datacenter proxy node (`http://127.0.0.1:31001`, `:31002`, `:31003`, etc.).
  - Never share proxy IPs across concurrent worker threads to prevent bot detection and cross-account rate limiting.
- **Independent Worker Threads:**
  - Each worker runs in an isolated `threading.Thread` with its own `urllib.request.OpenerDirector`, cookie jar, and state.

---

## 2. Dynamic Limit Scheduling & Zero-Blind-Delay Protocol

### The Static Limit Pitfall:
- Preliminary metadata endpoints (e.g. `getLimits`) return fixed account ceilings (`limDay: 560`, `limHour: 65`), whereas live video task responses carry real-time decremented counters (`limitHour`, `limitDay`).
- Using fixed batch caps (e.g. arbitrary 50 videos) causes premature stops and misaligns with actual server quota.

### Dynamic Rollover Mathematics (Sub-Minute Precision):
Never use static `time.sleep(3600)` on hourly limit. Compute exact seconds to the rollover mark:
```python
def seconds_until_next_hour() -> int:
    now = datetime.now()
    # Rollover occurs at :00:15 of the next hour
    next_hour = (now + timedelta(hours=1)).replace(minute=0, second=15, microsecond=0)
    return max(5, int((next_hour - now).total_seconds()))

def seconds_until_next_day() -> int:
    now_utc = datetime.now(timezone.utc)
    # Daily reset occurs at 00:00:30 UTC
    next_day = (now_utc + timedelta(days=1)).replace(hour=0, minute=0, second=30, microsecond=0)
    return max(30, int((next_day - now_utc).total_seconds()))
```
- **Example:** If an account hits `limitInHour` at `11:58:00`, the worker sleeps only **135 seconds** (~2 minutes), not 1 hour.

### Transient Queue Buffering vs Quota Limit:
- If server returns `status: empty` or `noTask`, this indicates a momentary video queue refresh on the server, NOT quota exhaustion.
- Apply a fast **15-second backoff** (`adaptive_sleep(15)`). Reserve long rollover sleeps strictly for explicit `limitInHour` and `limitInDay` errors.

### Interruptible Adaptive Step-Sleep:
```python
def adaptive_sleep(self, total_seconds: int, reason: str = "limit"):
    start = time.time()
    while not self.stop_event.is_set():
        if time.time() - start >= total_seconds:
            break
        time.sleep(1)
```

---

## 3. FaucetPay USDT TRC20 Wallet Management & One-Click Payout

### Target Wallet Specification & Server Invariants:
- Platform supports payout service `faucetpayusdt` (Minimum: `$0.10 USD`).
- Saving/updating payout addresses requires calling:
  ```python
  POST /api/user/settings/save/
  Payload: {
      "method": "payments",
      "faucetpayusdt_wallet": "<TRC20_WALLET_ADDRESS>",
      "code": "<6_DIGIT_OTP_CODE_OR_EMPTY>"
  }
  ```
- **Two-Stage Email Security Pipeline for Wallet Registration:**
  1. **Initial Registration Activation (`reqConfirm` / Link):** Unverified accounts (`emailactive: 0`) must first click the activation link sent via `POST /api/user/settings/confirm/` (`method=reqConfirm`). Attempting to save a wallet on unverified accounts returns error `confirmEmailFirst` without sending an OTP.
  2. **Wallet OTP Code Validation (`method=payments` with `code`):** Once email is active (`emailactive: 1`), sending `POST /api/user/settings/save/` with a new wallet address and `code=""` triggers the server to dispatch a **6-digit confirmation code** to the account's Gmail inbox and returns `{"status": "ok", "data": {"time": 300}}` (valid for 5 minutes). Submitting the code via the same endpoint locks the wallet permanently into `services.faucetpayusdt`. Submitting a wrong code returns error `codeIsWrong`.
  - **Payout Form Does NOT Accept Wallet Inline:** Note that `POST /api/user/payout/send/` only accepts `sum` and `service`. The backend automatically routes funds to the profile's saved wallet. If an account has never completed initial wallet verification in its profile, the payout endpoint rejects the request with `emailNotConfirmed`.
- **24-Hour Payout Suspension on Wallet Change:** Server suspends withdrawals for 24 hours immediately following any wallet update. Configure wallet addresses early during initial account setup.
- **Payout Transaction Status Tracking & Official Nuxt Codes:**
  - Payout history can be queried via `POST /api/user/payout/` (`method=history`, `page=1`).
  - Authoritative status codes returned by server (verified via live DOM `/payouts?tab=history` and Nuxt bundles):
    - `"1"` -> `PAID` / Completed (Funds successfully transferred and credited to wallet).
    - `"2"` -> `IN PROGRESS` / Processing by gateway.
    - `"3"` -> `UNDER REVIEW` / Processing queue (Transaction submitted and awaiting administrative/batch processing).
    - `"0"` -> `PAYMENT ERROR` / Failed.
  - **In-Flight Payout Concurrency Limit (`transactionsBeingChecked`):**
    - Platform strictly enforces 1 active pending withdrawal per account.
    - When a previous payout is in status `"3"` (UNDER REVIEW) or in queue, subsequent payout requests to `POST /api/user/payout/send/` return `{"status": "error", "message": "transactionsBeingChecked"}` (i18n: *"There is already a transaction under review. Please wait for the payout to be processed"*).
    - Auto-withdraw daemons must recognize `transactionsBeingChecked` as an in-flight pending status rather than an unhandled error, suppressing duplicate submission spam until the prior transaction reaches `"1"` (PAID) or `"0"` (FAILED).
  - Telemetry dashboard parses transaction ID, amount, wallet destination, and status badge to provide live visibility directly on worker cards.

### Live Server Email Verification & Wallet Synchronization Detection:
- The dashboard server automatically inspects `POST /api/user/settings/` (`method=get`) to detect:
  1. `emailactive == "1"` -> Renders `✓ Verified` badge; if `0`, renders `⚠ Unverified` badge with a 1-click `📩 Verif` trigger that fires `POST /api/user/settings/confirm/` (`method=reqConfirm`).
  2. `services.faucetpayusdt` -> Renders `🟢 TRC20: T...` (Synced on Server) vs `🟡 Local TRC20` (Configured locally but pending email activation on server) vs `⚠️ Set Wallet`.

### Automated Withdrawal Execution Endpoint & `checkSecurity` Balance Fallback Invariant:
```python
POST /api/user/payout/send/
Payload: {
    "sum": "<BALANCE_FLOAT_STR>",
    "service": "faucetpayusdt",
    "captcha": ""
}
```
- **The `checkSecurity` Payout Pitfall & Multi-Tier Balance Resolution:**
  - *Symptom:* Dashboard or automated withdrawal fails with `"Balance ($0.0000) is below minimum $0.10 USD"` despite account balance being well above threshold (e.g. $0.60 USD).
  - *Root Cause:* Naively probing balance via `POST /api/user/` (`getCurrentUser`) fails when accounts are in an email/security confirmation quarantine, returning `{"status": "error", "message": "checkSecurity"}`. If the withdrawal logic defaults `bal` to `0.0`, it falsely rejects the payout.
  - *Key Server Invariant:* The actual payout submission endpoint (`/api/user/payout/send/`) and streaming task endpoints (`/api/user/tasks/`) remain **100% functional and authorized** under active session cookies even when `getCurrentUser` is quarantined by `checkSecurity`.
  - *Required Multi-Tier Balance Probe Implementation:*
    ```python
    def resolve_account_balance(email: str, cookie_str: str, proxy_url: str) -> float:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({"http": proxy_url, "https": proxy_url}))
        headers = {"User-Agent": "Mozilla/5.0", "Cookie": cookie_str, "Content-Type": "application/x-www-form-urlencoded"}

        # 1. Primary: getCurrentUser
        try:
            req_u = urllib.request.Request("https://luckywatch.pro/api/user/", data=urllib.parse.urlencode({"method": "getCurrentUser"}).encode(), headers=headers)
            u_res = json.loads(opener.open(req_u, timeout=3.5).read().decode())
            if u_res.get("status") == "ok" and u_res.get("data", {}).get("balance") is not None:
                return float(u_res["data"]["balance"])
        except Exception:
            pass

        # 2. Fallback A: Active task stream probe (bypasses checkSecurity quarantine)
        try:
            req_t = urllib.request.Request("https://luckywatch.pro/api/user/tasks/", data=urllib.parse.urlencode({"method": "get"}).encode(), headers=headers)
            t_res = json.loads(opener.open(req_t, timeout=3.5).read().decode())
            if t_res.get("status") == "ok" and isinstance(t_res.get("data"), dict) and t_res["data"].get("balance") is not None:
                return float(t_res["data"]["balance"])
        except Exception:
            pass

        # 3. Fallback B: Settings user profile probe
        try:
            req_s = urllib.request.Request("https://luckywatch.pro/api/user/settings/", data=urllib.parse.urlencode({"method": "get"}).encode(), headers=headers)
            s_res = json.loads(opener.open(req_s, timeout=3.5).read().decode())
            if s_res.get("status") == "ok" and s_res.get("data", {}).get("user", {}).get("balance") is not None:
                return float(s_res["data"]["user"]["balance"])
        except Exception:
            pass

        # 4. Fallback C: Live cached state from state/fleet_state.json
        if STATE_FILE.exists():
            try:
                st_data = json.loads(STATE_FILE.read_text())
                if email in st_data and st_data[email].get("balance") is not None:
                    return float(st_data[email]["balance"])
            except Exception:
                pass

        return 0.0
    ```

### Autonomous Background Auto-Withdrawal Protocol:
In addition to web-triggered payouts, worker daemon threads can run autonomous background withdrawals:
```python
def check_and_trigger_auto_withdraw(self, current_balance: float):
    auto_cfg = self.global_config.get("auto_withdraw", {})
    if not auto_cfg.get("enabled", False):
        return

    threshold = float(auto_cfg.get("threshold_usd", 0.10))
    wallet = self.account_config.get("faucetpay_usdt_trc20", "").strip()

    if not wallet or current_balance < threshold or current_balance < 0.10:
        return

    # Anti-spam: enforce minimum interval (e.g. 1 hour) between payout attempts
    if time.time() - getattr(self, "_last_auto_withdraw_time", 0) < 3600:
        return

    self._last_auto_withdraw_time = time.time()
    payload = {
        "sum": f"{current_balance:.5f}",
        "service": "faucetpayusdt",
        "captcha": ""
    }
    # Send payout request via worker proxy session...
```

### Dashboard Action Endpoints (`server.py`):
1. `POST /api/actions/save_wallet` -> Ingests `{"email": "...", "wallet": "..."}`, writes to `config.json`, and triggers remote wallet sync on `luckywatch.pro`.
2. `POST /api/actions/send_verify_email` -> Ingests `{"email": "..."}` and triggers `POST /api/user/settings/confirm/` (`method=reqConfirm`).
3. `POST /api/actions/withdraw` -> Ingests `{"email": "..."}`, validates balance >= minimum ($0.10), and sends payout request.
4. `POST /api/actions/withdraw_all` -> Ingests `{"threshold": 0.10}`, filters all ready accounts with configured wallets, and dispatches batch payout requests.

---

## 4. Smart Daily Activity Bonus Autoclaim (Strict 500/500 Tier Gating)

### Reward Tiers & Constraints:
- Endpoint: `POST /api/user/tasks/dailyBonus/` (`method=getInfo` and `method=getBonus`).
- Tier Structure:
  - 100 views -> 100 clovers ($0.00 USD)
  - 200 views -> 500 clovers ($0.00 USD)
  - 300 views -> 1000 clovers ($0.00 USD)
  - 400 views -> $0.005 USD
  - **500 views -> $0.010 USD (MAXIMUM PRIZE)**
- **Critical Invariant:** The Daily Activity Bonus can **ONLY be claimed ONCE per UTC day**. If claimed prematurely at tier 100, 200, 300, or 400, the remaining tiers for that day are forfeited.
- **Smart Autoclaim Implementation:**
```python
def claim_daily_bonus(self) -> Dict[str, Any]:
    info = self._api("user/tasks/dailyBonus/", data={"method": "getInfo"})
    if info.get("status") != "ok" or not info.get("data"):
        return {"status": "error"}

    data = info["data"]
    daily_bonus_cnt = int(data.get("dailyBonusCnt", 0))
    view_cur_day = int(data.get("viewCurDay", 0))

    # Already claimed today
    if daily_bonus_cnt > 0:
        return {"status": "already_claimed", "viewCurDay": view_cur_day}

    # STRICT GATE: Only claim when reached the max 500 tier
    if view_cur_day >= 500:
        logger.info(f"🏆 MAX TIER REACHED ({view_cur_day}/500 views)! Claiming $0.010 USD Daily Bonus ...")
        return self._api("user/tasks/dailyBonus/", data={"method": "getBonus"})
    else:
        needed = 500 - view_cur_day
        logger.info(f"⏳ Daily Bonus Progress: {view_cur_day}/500 views ({needed} more needed for max $0.01). Claim postponed.")
        return {"status": "in_progress", "viewCurDay": view_cur_day, "needed": needed}
```

---

## 5. Web Telemetry Dashboard & Withdrawal Readiness Hub

### Key Architectural Pillars:
1. **Zero External Dependencies:** Built with Python standard library `http.server` serving inline HTML/CSS/JS.
2. **Parallel Multithreaded Upstream Polling:** Never poll multi-account proxy endpoints sequentially in the web handler (which causes 8-10s latency for 5 accounts). Use `concurrent.futures.ThreadPoolExecutor(max_workers=5)` with per-account short timeouts (2.5s) to guarantee sub-second (<300ms) dashboard response times.
3. **Session User-Agent Consistency Invariant:** When an account passes a security checkpoint (`checkSecurity`), its session cookie is bound to the exact User-Agent header used during the verification call. Always ensure both the worker daemon (`bot.py`) and the telemetry server (`server.py`) use an identical User-Agent (e.g. `Mozilla/5.0`) across all subsequent task, balance, and settings requests to avoid re-triggering security quarantine.
4. **Worker-Level Multi-Endpoint Balance Fallback (Eliminating `$None` & `checkSecurity` Stalls):** When accounts trigger security challenges on `/api/user/` (`getCurrentUser`), standard profile queries return `{"status": "error", "message": "checkSecurity"}` and yield `None` balance. Implement a 3-tier fallback hierarchy in `get_user_info()`:
   - Primary: `/api/user/` (`getCurrentUser`).
   - Fallback 1: `/api/user/settings/` (`data.user.balance`).
   - Fallback 2: Real-time task stream extraction directly from `/api/user/tasks/` (`method=get` returns `data.balance`), cached in worker memory (`_last_known_balance`).
   This ensures worker logs, auto-withdraw logic, and dashboard stats always have real-time balance data even during IP/profile security quarantine.
5. **Direct User Object Ingestion for Dynamic Real-Time Balance in Telemetry:** In telemetry handlers, always parse balance and clovers directly from the primary `settings` response object (`user_obj.balance` & `user_obj.clover`) in addition to `/user/` endpoint fallbacks, preventing stale `$0.0000000` default displays when multi-account endpoints return nested objects.
### 6. 24/7 Fleet Production Hardening, Anti-Detection & Jitter Standards:
- **Zero Shadowed Methods Invariant:**
  - Avoid multiple definitions of `def run(self)` or lifecycle methods in worker classes. Python silently overrides the earlier definition with the later one. Always consolidate execution logic into a single unified state-machine loop.
- **Android Telemetry & Client Hints Harmonization:**
  - Standardize `User-Agent` and Client Hints headers across all requests to match Android GPU telemetry (`videoCard[renderer]`: `Mali-G715-Immortalis MC11`, `platform`: `Linux armv81`):
    - `Sec-CH-UA`: `"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"`
    - `Sec-CH-UA-Mobile`: `?1`
    - `Sec-CH-UA-Platform`: `"Android"`
    - `Sec-Fetch-Site`: `same-origin`, `Sec-Fetch-Mode`: `cors`, `Sec-Fetch-Dest`: `empty`
- **Staggered Hourly Wake-Up Jitter (Anti-Thundering-Herd on Captcha Solvers):**
  - When workers sleep until the `:00:15` hourly reset, calculate a deterministic staggered wake-up offset based on account index or email hash:
    ```python
    stagger_offset = (account_index * 8) + random.uniform(0, 4)
    sleep_seconds = seconds_until_next_hour() + stagger_offset
    ```
  - This spreads 15-50 workers across a 2-minute window, eliminating traffic spikes and timeout queues on local Vision LLM (:5073) and Turnstile (:5072) solvers.
- **Smart Daily Bonus End-of-Day (EOD) Fallback:**
  - If a worker has not reached the top 500-view tier ($0.010 USD) but the UTC day has less than 30 minutes remaining (`secondsUntilEndOfDay <= 1800`), gracefully claim the highest achieved milestone (tier 400 = $0.005, tier 300 = 1000 clovers, etc.) rather than letting the day's accumulated reward reset to $0.
- **Behavioral Timing & Coordinate Click Jitter:**
  - Add natural variance to video playback sleep: `time.sleep(duration + random.uniform(0.5, 1.8))`.
  - Add humanized click coordinate jitter (+-1 to +-2 px) around solved icon captcha centroids, clamping within image boundaries [5, 295].
- **Bounded Tail Seek for Log Streaming (Memory Leak Elimination):**
  - Never parse long-running daemon logs by reading the entire file (`LOG_FILE.read_text().splitlines()`). As log files grow to tens of megabytes, this causes server RAM to spike to 400MB-600MB+ per polling request.
  - Implement a bounded tail seek reader reading only the last 64KB-128KB chunk via `f.seek(max(0, file_size - 65536))` in binary mode, decoding with `errors="ignore"`, and slicing the last 150-200 lines. This keeps memory footprint under 30MB with sub-15ms parsing latency.
- **Thread-Safe Atomic State Persistence:**
  - In multi-worker architectures (15+ threads), concurrent uncoordinated file writes to `fleet_state.json` or `sessions.json` cause race conditions and corrupted JSON (`JSONDecodeError`).
  - Enforce a global `threading.Lock()` and atomic write pattern:
    ```python
    _STATE_LOCK = threading.Lock()

    def atomic_write_json(path: Path, data: dict):
        with _STATE_LOCK:
            tmp_path = path.with_suffix(".tmp")
            tmp_path.write_text(json.dumps(data, indent=2))
            os.replace(tmp_path, path)
    ```
- **Action Endpoints Security & API Key Guard:**
  - Public-facing telemetry dashboards exposed via Cloudflare Tunnel must secure all mutating action endpoints (`/api/actions/withdraw`, `/api/actions/save_wallet`, `/api/actions/retry`) with persistent API Key / Bearer token authentication in backend request headers and inject the token into authenticated client templates, rejecting unauthorized public crawler requests with `401 Unauthorized`.
- **Linux Logrotate & Systemd Cgroup Memory Limits:**
  - Pair systemd services with `/etc/logrotate.d/<app>` using `size 50M`, `daily`, `rotate 7`, `compress`, `missingok`, `notifempty`, `copytruncate`.
  - Add `MemoryHigh=400M`, `MemoryMax=512M`, and `TimeoutStopSec=15` to systemd unit files to prevent unbounded memory leaks on 24/7 VPS hosts.
- **State-Aware Toast UI & Bounded Client Log FIFO:**
  - State-aware toasts (Emerald for success, Rose for error, Amber for warning, Cyan for info) to avoid deceptive green checkmarks on error events.
  - Client-side DOM FIFO buffer capping `#log-stream` at max 200 elements to prevent browser memory leaks during continuous multi-day sessions.
   - *The Log Parsing Trap:* Deducing live worker status (`ACTIVE`, `SLEEPING`, `ERROR`, `IDLE`) by parsing log files via regex (`parse_bot_logs`) fails at scale. When an account enters a long sleep (e.g. 14-hour daily limit cap), it produces zero logs. High-volume active workers generate thousands of lines, pushing the sleeping worker out of the scan window and causing the dashboard to falsely classify it as `IDLE`.
   - *Architectural Fix:* Completely decouple log stream rendering from live state management. Workers atomically persist their operational state (`status`, `countdown_sleep`, `sleep_until_ts`, `current_task`, `daily_done`, `hourly_done`, `balance`, `clovers`, `error_reason`) to a dedicated JSON state store (`state/fleet_state.json`). The web telemetry server reads this state store in $O(1)$ time (<1ms), guaranteeing 100% deterministic accuracy for 100+ accounts regardless of log volume or sleep durations. Log files are retained strictly for the terminal UI tab (scanned to 150-200 lines max).
7. **Smooth State Transitions (Hybrid Client-Server Interpolation):** Polling server snapshots at 2000ms intervals causes stuttering countdown timers. Implement a client-side 1000ms interval loop (`setInterval(..., 1000)`) that decrements `acc.countdown_sleep` locally every second, ensuring rhythmic second-by-second countdowns and instantaneous status transitions.
8. **100+ Account Scaling Architecture:**
   - **Background Polling Daemon:** For fleets >= 50-100 accounts, avoid fetching all accounts on-demand in HTTP GET handlers. Run an asynchronous background polling loop with staggered account rotations and cache snapshots for instantaneous (<200ms) UI load.
   - **Dense Table Ledger & Quick Search:** Provide instant search/filter pills (`Active`, `Sleeping`, `Error`, `Ready Payout`) and compact table views (1 row per account) to monitor 100+ accounts efficiently without scroll fatigue.
   - **Thread Isolation & Self-Healing:** Every worker thread must catch all exceptions, handle retry cooldowns (e.g. 10x Turnstile retry -> 5m sleep -> next proxy batch), and never terminate, ensuring 99 workers continue operating when 1 worker is resolving a challenge.
9. **Apple-Grade Dark Glass Aesthetic:** Deep obsidian canvas (`#07090E`), translucent glass cards (`backdrop-blur-md`), 1px specular borders (`border-white/10`), and Inter / JetBrains Mono typography.
10. **Interactive Withdrawal Readiness Hub & Auto-Withdraw Pill:**
   - Configurable threshold presets (`$0.10`, `$0.50`, `$1.00`, `$5.00`) and custom input with `localStorage` persistence.
   - Live Auto-Withdraw Toggle Switch (`⚡ Auto: ON ($0.10)` / `OFF`) linked to `POST /api/actions/config_auto_withdraw` and `config.json`.
   - Dual-level progress bars (combined fleet progress + individual account cards).
   - Automated readiness verdict: `"READY TO WITHDRAW (N Accounts)"` with gold/emerald glow.
   - Global `"⚡ Auto Withdraw All Ready"` button and per-account `"💸 Payout"` actions.
11. **Dual-View Switcher:** Instant toggle between visual Card Grid and dense Matrix Table Ledger.
12. **Multi-Channel Log Terminal:** Segmented tabs (`ALL FLEET`, per-account channels), level filters (`ALL`, `SUCCESS`, `WARN`, `ERROR`), live search, and auto-scroll lock.
