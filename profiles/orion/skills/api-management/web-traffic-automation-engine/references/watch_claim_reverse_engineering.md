# Watch & Claim Reverse-Engineering Playbook

Exhaustive technical methodology for reverse-engineering modern SPA / Nuxt 3 video watch and reward platforms into 100% pure Python HTTP requests without browser automation.

---

## 1. Network Inspection & Client Bundle Extraction
1. **Download Frontend Chunks:**
   - On Nuxt 3 / Vite applications, inspect the HTML source to find script bundles under `/_nuxt/*.js` or `/assets/*.js`.
   - Download all chunk files to a local directory (e.g. `/tmp/nuxt_chunks/`) via `terminal` tool or direct HTTP request.
2. **Key Chunk Search Patterns:**
   - Search for action classes, API paths, and endpoints:
     - `watchActions`, `captchaActions`, `authActions`, `user/tasks`, `user/auth`, `user/captcha`.
     - Error strings and status keys: `limitInHour`, `limitInDay`, `noTask`, `toFast`, `verifTimeExpired`, `timeIsOver`, `cannotPassTestTask`.
     - Request parameter signatures: `method:`, `TaskId:`, `coor:`, `fin:`, `captchaResponse:`, `mac:`.

---

## 2. API Discovery & True Reward Attribution
- **The Dummy Endpoint Trap:**
  - In many reward platforms, clicking "Watch Video" or "Start Task" calls an initial registration endpoint (e.g. `POST /api/user/tasks/start/` with `fin=0` or `status=start`).
  - Some developers assume calling `fin=1` immediately afterwards will credit the reward. In production systems with server-side validation, `fin=1` is either ignored or flags the account.
- **The True Verification Sequence:**
  1. `POST /api/user/tasks/` (`method=get`) -> Returns `TaskId`, `duration` (e.g. 12s), `ytId`, `limitHour`, `limitDay`.
  2. `POST /api/user/tasks/start/` (`TaskId=..., fin=0`) -> Registers playback initiation with server-side timestamp.
  3. `time.sleep(duration + 1)` -> Enforces real playback delay to satisfy server-side timer validation.
  4. `POST /api/user/captcha/check/` (`refreshTask=0`) -> Executes actual verification check. If no visual captcha is required, returns `{"status": "ok", "data": {"reward": 0.00025}}`.

---

## 3. Device Telemetry & Header Emulation
- Platforms with strict anti-bot filters reject desktop browsers or mismatching platform headers.
- **Canonical Mobile Android Signature:**
  - `User-Agent`: `Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36`
  - `Content-Type`: `application/x-www-form-urlencoded`
  - `Origin`: `https://target-domain.com`
  - `Referer`: `https://target-domain.com/watch`
  - Telemetry payload (if required): `platform: Linux armv81`, `dpr: 2.625`, `videoCard[renderer]: Mali-G715-Immortalis MC11`.

---

## 4. Nuxt Action Tracing Reference Table

| Action Method | Target Endpoint | Payload Structure | Expected Response |
|---|---|---|---|
| `getLimits` | `POST /api/user/tasks/` | `method=getLimits` | `{"data": {"limDay": 560, "limHour": 65}}` (Static Account Limits) |
| `getTask` | `POST /api/user/tasks/` | `method=get&mac=0` | `{"data": {"id": "540723", "duration": 12, "limitHour": 64, "limitDay": 558}}` |
| `startTask` | `POST /api/user/tasks/start/` | `TaskId=540723&fin=0` | `{"status": "ok", "data": true}` |
| `checkCaptcha` | `POST /api/user/captcha/check/` | `refreshTask=0` | `{"status": "ok", "data": {"reward": 0.00025}}` OR Captcha Payload |
| `solveCaptcha` | `POST /api/user/captcha/check/` | `coor[0][x]=..&coor[0][y]=..` | `{"status": "ok", "message": "Проверка пройдена"}` |
| `getCurrentUser` | `POST /api/user/` | `method=getCurrentUser` | `{"data": {"balance": 0.10665, "clover": 6602}}` |
