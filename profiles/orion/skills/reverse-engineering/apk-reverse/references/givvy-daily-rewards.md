# Givvy Daily Rewards (givvy.daily.rewards.bulgaria) — catatan RE

Work dir: /root/reverse_work/givvy (README.md lengkap; script bot: givvy_api.py).

## Stack & tooling
- RN + Expo SDK 54, Hermes bytecode v96. Decompile: `pip install hermes-dec` → `hbc-decompiler base_extract/assets/index.android.bundle bundle_output.js` (23MB, ~2-3 menit). hermes-dec preserves Original function names — grep itu dulu.
- jadx 13 dex butuh RAM; jalankan background. APKPure: `https://d.apkpure.net/b/XAPK/<pkg>?version=latest` (UA browser; b/APK 403 untuk split).

## Fakta server (verified 2026-10-10)
- API: https://givvy-bulgaria-backend-347fb9c7c2be.herokuapp.com/api, clientKey `local-dev-client-key` (x-client-key), tanpa signing/attestation/pinning.
- Auth: register → OTP 6 digit email → /auth/verify-email → JWT exp ~10 th. Temp-mail lolos.
- /ads/reward {adType:video|interstitial, source:ad-tickets} = +1 ticket, cap 25/hr, tanpa bukti iklan.
- /games/double-ticket {game:math|memory|minesweeper|word-puzzle|bolt-sort} = +1 ticket TANPA cap (aslinya di belakang rewarded ad). Competitive keys = 400.
- /games/competitive/complete: server percaya sessionValid/sessionStatus dari client; score 800 → prize 83.
- /games/difficulty {game, adjustment:<int>}: geser level bebas.
- /steps/daily-sync SOLVED: items butuh {dayStr, date:'...T00:00:00.000Z', steps, platform:'android', provider:'android_step_counter', timeZone:'Europe/Sofia', samplesCount:1} — tanpa itu 400. Steps diterima apa adanya (50k lolos), reward ticket tidak instan.
- Cashout BUKAN API: webview givvy.bg?tab=cashout + FaceTec KYC biometrik.
- /config bocor TikTok access token tanpa auth.
- Impression: {adType:video, revenueEur, loader:levelplay} → adStats ecpm (bukan balance); maxAds 250/hr di situ.

## Gotcha
- Temp-mail API (api-tempmail.indrayuda.my.id) 403 tanpa User-Agent header.
- axios interceptor app kirim x-device-id == x-installation-id == installationId native.
- GET /leaderboard & /games/difficulty (GET) = 404; leaderboard datang di response competitive/start.
- JWT berisi sub/email/iat/exp saja.
