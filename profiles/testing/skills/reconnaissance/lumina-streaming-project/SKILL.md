---
name: lumina-streaming-project
description: Use when working on the LUMINA streaming app project.
version: 1.0.0
author: hermes-testing
license: MIT
metadata:
  hermes:
    tags: [streaming, framextv, replication, lumina]
    related_skills: [web-surface-triage, strix/spa-frontend-recon]
---

# LUMINA Streaming App (frameXTV-parity clone)

Live: `https://stream.indrayuda.my.id` — replikasi frameXTV dengan 7 provider VOD.

## When to Use
- Bekerja pada proyek LUMINA (menambah fitur, fix bug, test) di `/mnt/anime-streaming-web`.
- Menjawab pertanyaan tentang arsitektur player/provider/subtitle LUMINA.
- Menjalankan regression test suite untuk situs streaming ini.

## Lokasi & deploy
- Project: `/mnt/anime-streaming-web` (git, branch `feat/multi-provider-v2`)
- Repo: `github.com/IndraYuda13/animestr-web` (PR #2)
- Live: `https://stream.indrayuda.my.id` (nginx → backend `127.0.0.1:8430`, systemd `animestr-backend`)
- Restart backend: `sudo systemctl restart animestr-backend`
- Env: `ANIMESTR_RESIDENTIAL_PROXY=http://127.0.0.1:31004` (chain venus wajib residential proxy)
- Python: `/usr/local/lib/hermes-agent/venv/bin/python3` (wasmtime ada)

## Test flow wajib (RED -> FIX -> GREEN -> sweep)
```bash
V=/usr/local/lib/hermes-agent/venv/bin/python3
$V tests/test_routes_smoke.py        # 17 API checks
$V tests/test_e2e_routes.py          # 22 routes Playwright
$V tests/test_e2e_interactions.py    # 6 interaksi (hero/rail/card hover)
$V tests/test_round2_criteria.py     # 10 checks (#11 mapping, #12 picker/CC)
$V tests/test_srt_to_vtt.py          # 4 unit checks
$V tests/test_player_overlay_ui.py   # 13 checks
$V tests/test_progress_resume_v2.py  # 22 checks (progress/resume/history v2)
$V tests/test_search_resilience.py   # 3 checks (retry TMDB/mirror)
LUMINA_SWEEP_MAX=5 $V tests/test_sweep_all.py
```
Alur bug: tulis test dulu (GAGAL) → fix → PASS → sweep semua route.

## Pitfalls penting
- **Headless Chrome tidak bisa memutar HLS** (tanpa codec H.264/AAC) — verifikasi playback via proxy 206 + segmen ffprobe OK + hls.js parse fragmen. Uji tontonan akhir harus browser user.
- **Anime ID**: MAL/AniList harus di-map ke TMDB TV id via `tmdb_id_for_anime()` (TheTVDB + mirror scoring exact-match, spin-off dihukum) SEBELUM dikirim ke bowler/headhunter — tanpa mapping, MAL 38000 dikira TMDB 38000 = konten salah (film India).
- **Cache busting**: setelah ubah JS, bump `?v=` di `frontend/index.html` (app.js) dan `frontend/app.js` (imports v2/*.js).
- **`confirm()` native memblokir headless** — pakai `fxConfirm` in-page modal (pages.js).
- **Probe stream**: `_PROBE_CACHE` (TTL 90s) — verdict = HTTP 200 + body `#EXTM3U`; registry lanjut ke provider berikut kalau stream mati (kasus 502 transcoding).
- **Hero autoplay pause saat hover** = perilaku benar; test E2E harus gerakkan mouse keluar hero dulu.
- **Anime page kosong / rails**: `norm()` harus handle rail berupa `{results:[...]}` bukan array.
- **Route history**: `app.js` harus panggil `showV2Route('history')` bukan `showHistoryView()` legacy.
- **Legacy `#/watch?season_id=`**: redirect cerdas ke v2 (yt-dlp upstream rusak).
- **UI parity reference**: `frontend/v2/fx.css` (tokens `--fx-bg:#09090b`), struktur frameXTV = `max-w-7xl mx-auto` + `flex-col sm:flex-row`; title page mobile center / desktop left.
- **Player controls = overlay di dalam player** (BUKAN bar di bawah): tombol ⚙ (`#fx-ovl-set`) + CC (`#fx-ovl-cc`) di `.fx-ovl` pojok kanan atas (opacity .55 → 1 saat hover), panel `#fx-setpanel` (hidden default) berisi `#fx-server`/`#fx-resolution`/`#fx-sub`/`#fx-cc-btn`/`#fx-eps`/`#fx-prev`/`#fx-next`. Mobile = bottom-sheet. Tutup: ✕ / klik area player / Esc. Bar `.fx-ctrl` LAMA SUDAH DIHAPUS — jangan hidupkan lagi.
- **Selector penting player**: `#fx-setpanel-close`, `.fx-ovl-btn`; test suite `tests/test_player_overlay_ui.py` (10 checks) menjaga struktur ini.
- **Provider**: 7 (miner, valkyrie, super_barbarian, bowler, headhunter, hog_rider, lavahound); bowler & headhunter bootstrap sementara via `api.framextv.tech`.
- **Performa (ronde-7)**: `/api/v2/stream?fast=1` = provider pertama HIDUP (grace 2s); full = merge semua + cache 300s; job background dipakai ulang (JANGAN resolve dobel). Frontend render detail dulu → video dari fast → picker diperkaya saat full tiba. Proxy retry 1x untuk 5xx (node transcoding 502).
- **Trailer YouTube**: index.html meta referrer WAJIB `strict-origin-when-cross-origin` (no-referrer → Error 153 "player configuration error"); iframe butuh `referrerpolicy` + `origin` param + link fallback.
- **Episodic controls** (Prev/Episodes/Next) di overlay kiri `#fx-ovl-ep` — SELALU terlihat, jangan dipindah ke panel pengaturan.
- **Ikon mylist**: pakai `BM_ICON`/`BM_ICON_ON`/`bmLabel` dari state.js (bukan teks '+'/'✓'). E2E test harus bersihkan `.fx-modal` nyangkut sebelum klik overlay.
- **`test_provider_registry.py` tanpa output** = file pytest-style (fungsi `test_*`) tanpa `__main__`; jalankan via `$V -m pytest tests/test_provider_registry.py` (4/4). Jangan salah baca sebagai gagal.
- **Test legacy di `frontend/` SUDAH MATI**: `test_continue_watching.py` + `test_resume_playback.py` menguji arsitektur v1 (`window.__animestr`, `#main-video`, `#view-watch`, `wait_until="networkidle"` yang tidak pernah tenang) — sudah di-rename `.deprecated`; penggantinya `tests/test_progress_resume_v2.py`. Jangan hidupkan lagi.
- **Playwright `add_init_script` tidak berlaku untuk hash-navigation** pada situs ini: `localStorage` harus di-set SETELAH `goto(SITE + '/')` (origin sudah terbentuk), baru `goto(SITE + '/#/player/...')`. Kalau init-script dipakai, seed terbaca `null` dan resume bar "tidak muncul" padahal fitur sehat.
- **`innerText` vs `textContent` pada badge jumlah**: CSS `text-transform:uppercase` membuat `innerText` = "1 JUDUL" walau DOM-nya "1 judul" — assertion history harus pakai `textContent`.
- **Progress/resume v2**: `localStorage['v2:progress']` (key `{type}:{id}[:{s}:{e}]`), interval save 5s, trim 60 entri terbaru. Resume bar (`#fx-resume-host`) hanya muncul kalau `prog.t > 30` dan tidak ada `?t=` beda >5s. Uji resume dengan `page.route("**/api/v2/proxy**", abort)` supaya video tidak play dan menimpa seed progress.
- **`search_full()` (backend/metadata/tmdb.py) tanpa retry = silent failure**: satu hiccup TMDB langsung `{'results': []}`. Fix ronde-8: retry 3x backoff kuadratik (timeout 12s lalu 6s) → fallback mirror → baru kontrak kosong. Guard: `tests/test_search_resilience.py`.
- **registry pitfall**: `job.lock` TIDAK reentrant — jangan panggil `_finalize_full` saat lock ditahan (deadlock); collector wajib `as_completed(..., timeout=60)` + finalize + set done.
- **CC panel**: `v2:cc-settings` + `v2:cc-custom` di localStorage; SRT→VTT convert di `srtToVtt()` (timing-line-only regex — jangan replace berantai, merusak timestamp).

## Referensi
- `docs/DEPLOYMENT_NOTES.md` — endpoint v2, provider ops, test flow
- `docs/PROVIDER_BLUEPRINT.md` — hasil RE 7 chain provider
- `/root/framextv_analysis/` — hasil RE frameXTV (chunks, blueprint)
