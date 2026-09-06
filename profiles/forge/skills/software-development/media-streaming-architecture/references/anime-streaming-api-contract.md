# Anime Streaming Backend API & Data Schemas (Bstation / Animestr)

Dokumentasi skema payload API dan data contract riil dari backend service Bstation (@Animestrbot) untuk konsumsi frontend / mobile web client.

## 1. Gateway & Auth Prerequisites
- Base URL upstream: `https://api.bilibili.tv/intl/gateway/web/v2/`
- Header upstream wajib:
  - `User-Agent`: Desktop browser UA (`Mozilla/5.0 ... Chrome/...`)
  - `Referer`: `https://www.bilibili.tv/`
  - `Accept`: `application/json, text/plain, */*`
- Dependency SOCKS5: Di Python/requests, koneksi via SOCKS5 proxy (`socks5://...`) wajib menginstal `requests[socks]` atau `PySocks`.
- **Proxy Geo-Licensing & Upstream Null-Safety Pitfalls:**
  - **Geo-Restriction & IP Cleanness (HTTP 412 / Bot Detection):** Bstation membatasi lisensi OGV (Official Anime) per negara dan menerapkan rate limiting / Cloudflare-style blocking (HTTP 412) pada IP proxy publik/datacenter yang kotor saat volume query search tinggi. Contoh: IP node Singapore (`SG`) dapat mengembalikan 0 OGV anime di search (`modules=['ugc']`) dan `cards: null` di timeline. Node Thailand (`TH`, port 32007) dapat terkena HTTP 412 saat burst search. Node Filipina (`PH`, port 32012 clean) menyediakan katalog OGV penuh (`modules=['ogv_subject', 'ugc']`, 80+ timeline cards, bebas 412).
  - **Multi-Node Fallback Pool Pattern:** Untuk endpoint yang rawan rate limit/WAF (seperti `search_v2`), definisikan fallback proxy pool (contoh: `[32012, 32007, 32011, 32006]`). Jika node primer me-return HTTP 412, 429, atau 403, tangkap status tersebut dan otomatis coba node berikutnya di pool sebelum menyerah.
  - **Graceful Upstream Search Handling:** Pada fungsi search upstream (seperti `search_v2`), jangan memanggil `r.raise_for_status()` mentah-mentah yang memicu 500 Unhandled Exception saat upstream me-return non-200 (misal 412 atau 502). Gunakan blok `try-except`, periksa `r.status_code != 200`, log warning, dan kembalikan list kosong `[]` atau cached results.
  - **Null-Safety Parsing:** Payload timeline `https://api.bilibili.tv/intl/gateway/web/v2/ogv/timeline` mengembalikan `"cards": null` untuk hari tanpa tayangan atau di region geo-restricted. Begitu pula field `modules`, `items`, `seasons`, `styles`, `subtitles`, `sections`, dan `body`. Jangan pernah mengiterasi `day.get('cards', [])` karena `dict.get()` tetap mengembalikan `None` jika key ada tapi bernilai `null`, yang memicu `TypeError: 'NoneType' object is not iterable`. Selalu gunakan `(day.get('cards') or [])` untuk seluruh iterasi list dari upstream.

---

## 2. API Schema Contract

### A. Featured Spotlight (`GET /api/featured`)
Mengembalikan anime unggulan untuk Hero Spotlight Banner dan seasonal showcase.

```json
{
  "status": "success",
  "count": 8,
  "data": [
    {
      "season_id": "37738",
      "title": "Jujutsu Kaisen",
      "cover_url": "https://pic.bstarstatic.com/ogv/6e22a23939fa8dcaaf50385d9a39b944b2e7ea6a.png",
      "banner_url": "https://pic.bstarstatic.com/ogv/a906aaeab52bc0d3ad4f6fd3426f81491f122558.png",
      "rating": "9.8",
      "genres": ["Action", "Fantasy", "School", "Shounen"],
      "synopsis": "High school student Yuuji Itadori spends his days...",
      "episode_count": 24,
      "status": "Tamat",
      "release_year": "2020",
      "is_featured": true
    }
  ]
}
```

### B. Search (`GET /api/search?q={query}`)
Pencarian cepat untuk Command Palette (`Cmd+K`) dan search grid. Upstream memisahkan hasil OGV (official anime) dan UGC (user uploads). Filter hanya item yang memiliki `season_id` valid untuk streaming resmi.

```json
{
  "status": "success",
  "query": "jujutsu",
  "total": 15,
  "data": [
    {
      "season_id": "37738",
      "title": "Jujutsu Kaisen",
      "cover_url": "https://pic.bstarstatic.com/ogv/6e22a23939fa8dcaaf50385d9a39b944b2e7ea6a.png",
      "rating": "9.8",
      "status": "Tamat",
      "index_show": "Total 24 Episode",
      "is_ogv": true
    }
  ]
}
```

### C. Episodes List (`GET /api/episodes/{season_id}`)
Daftar episode per section/season lengkap dengan thumbnail cover dan status akses (free vs VIP).

```json
{
  "status": "success",
  "season_id": "37738",
  "title": "Jujutsu Kaisen",
  "total_episodes": 24,
  "sections": [
    {
      "section_title": "Season 1",
      "episodes": [
        {
          "episode_id": "379287",
          "index": 1,
          "short_title": "E1",
          "long_title": "Ryomen Sukuna",
          "title": "E1 - Ryomen Sukuna",
          "thumbnail_url": "https://pic.bstarstatic.com/ogv/a906aaeab52bc0d3ad4f6fd3426f81491f122558.png",
          "duration": 1420,
          "streamable": true,
          "is_vip": false,
          "publish_time": "2021-06-03T00:00:00+08:00"
        }
      ]
    }
  ]
}
```

### D. Subtitles (`GET /api/subtitles/{season_id}/{episode_id}?lang={id|en}`)
- Endpoint upstream Bstation: `GET https://api.bilibili.tv/intl/gateway/web/v2/subtitle?episode_id={episode_id}`
- Upstream mengembalikan multi-language array (`video_subtitle`) berisi URL file `.json` (SRT format) dan `.ass` (Advanced SubStation).
- Backend mengonversi format sumber on-the-fly menjadi WebVTT standar compliant:
  - Header: `Content-Type: text/vtt; charset=utf-8`
  - CORS: `Access-Control-Allow-Origin: *`
  - Caching: `Cache-Control: public, max-age=86400`
- Langsung dihubungkan ke native HTML5 `<track>`:
  ```html
  <track kind="subtitles" label="Bahasa Indonesia" srclang="id" src="/api/subtitles/{season_id}/{episode_id}?lang=id" default>
  <track kind="subtitles" label="English" srclang="en" src="/api/subtitles/{season_id}/{episode_id}?lang=en">
  ```

---

## 3. UI Density & Layout Sizing Baselines
- **Featured Hero:** 1 item spotlight (16:9 / 21:9 banner).
- **Featured Carousel:** 6 - 8 item pilihan.
- **Search Grid:** 12 - 20 card per page (default pagination upstream: 20).
- **Poster Aspect Ratio:** 2:3 vertical cover (`w: 240px, h: 360px` di desktop, fluid di mobile).
- **Episode Card Ratio:** 16:9 horizontal thumbnail dengan title, duration badge, dan progress bar.
