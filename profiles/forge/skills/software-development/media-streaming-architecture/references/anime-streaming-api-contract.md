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
- **Direct-Route Fallback Pattern for `season_info` (Proxy 412 Bypass):** Upstream endpoint `https://api.bilibili.tv/intl/gateway/web/v2/ogv/play/season_info` sering memicu `412 Precondition Failed` jika diakses via exit node proxy SOCKS5 tertentu, namun merespons `200 OK` secara instan ketika diakses via direct network host lokal (`proxies={'http': '', 'https': ''}`). Di `BstationClient.get_season_info()`, lakukan request awal secara direct tanpa proxy; jika direct route gagal atau me-return non-200/timeout, baru fallback ke configured proxy.
- **Multi-Node Fallback Pool Pattern:** Untuk endpoint yang rawan rate limit/WAF (seperti `search_v2`), definisikan fallback proxy pool (contoh: `[32012, 32007, 32011, 32006]`). Jika node primer me-return HTTP 412, 429, atau 403, tangkap status tersebut dan otomatis coba node berikutnya di pool sebelum menyerah.
  - **Graceful Upstream Search Handling:** Pada fungsi search upstream (seperti `search_v2`), jangan memanggil `r.raise_for_status()` mentah-mentah yang memicu 500 Unhandled Exception saat upstream me-return non-200 (misal 412 atau 502). Gunakan blok `try-except`, periksa `r.status_code != 200`, log warning, dan kembalikan list kosong `[]` atau cached results.
  - **Null-Safety Parsing:** Payload timeline `https://api.bilibili.tv/intl/gateway/web/v2/ogv/timeline` mengembalikan `"cards": null` untuk hari tanpa tayangan atau di region geo-restricted. Begitu pula field `modules`, `items`, `seasons`, `styles`, `subtitles`, `sections`, dan `body`. Jangan pernah mengiterasi `day.get('cards', [])` karena `dict.get()` tetap mengembalikan `None` jika key ada tapi bernilai `null`, yang memicu `TypeError: 'NoneType' object is not iterable`. Selalu gunakan `(day.get('cards') or [])` untuk seluruh iterasi list dari upstream.

---

## 2. API Schema Contract

### A. Featured Spotlight (`GET /api/featured`) & Popular (`GET /api/popular`)
Endpoint feed katalog utama untuk konsumsi Hero Carousel dan shelf rail "Koleksi Favorit Penonton".

- **Envelope Contract:**
  - `GET /api/featured` -> `{"code": 0, "cached": boolean, "featured": [...]}`
  - `GET /api/popular` -> `{"code": 0, "cached": boolean, "popular": [...]}`

- **Item Object Contract (Dual Status/Index-Show Consistency):**
  Untuk mencegah contract mismatch antar endpoint (di mana featured menggunakan `status` dan popular menggunakan `index_show`), backend wajib menyediakan kedua key tersebut secara bersamaan:

```json
{
  "season_id": "37738",
  "title": "Jujutsu Kaisen",
  "cover": "https://pic.bstarstatic.com/ogv/6e22a23939fa8dcaaf50385d9a39b944b2e7ea6a.png",
  "rating": "9.8",
  "index_show": "Total 24 Episode",
  "status": "Total 24 Episode",
  "description": "High school student Yuuji Itadori spends his days...",
  "styles": ["Aksi", "Fantasi", "Shounen"]
}
```

- **Frontend Resilience Contract:**
  1. Frontend mengimplementasikan **Cascading Hero Fallback**: jika `featured[]` bernilai kosong, hero carousel otomatis fallback menggunakan top anime dari timeline seasonal (`getSeasonal()`) atau katalog.
  2. Frontend mengeliminasi hardcoded dummy season ID (seperti `'2097863'`). Jika item tidak memiliki `season_id` valid, tombol "Nonton Sekarang" & "Daftar Episode" di-disable / hidden dan hero menampilkan skeleton/empty state, mencegah trigger error dialog player akibat season invalid.

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

### E. Catalog Harvester (`items_v2` vs Multi-Keyword Search)
- **Problem:** Mengumpulkan seluruh katalog anime dengan brute-force multi-keyword search (`search_v2`) pada 70+ keyword paralel memicu HTTP 412 (WAF block/bot detection) dan hanya menghasilkan subset kecil (31 - 113 anime).
- **Official OGV Index Endpoint:** Gunakan endpoint resmi kategori OGV Bstation:
  `GET https://api.bilibili.tv/intl/gateway/web/v2/ogv/index/items_v2`
  - Query parameters:
    - `season_type=1,4` (`1` = Anime Jepang, `4` = Donghua/Anime OGV)
    - `pn=1, 2, ...` (1-indexed paging)
    - `ps=50` (maksimal 50 item per request; `ps > 50` memicu error response `-400`)
    - `platform=web`
    - `s_locale=id_ID`
  - Response structure:
    `data`: `{"cards": [...], "total": 332, "size": 50, "num": 1, "has_next": true/false}`
- **Harvesting Strategy & Quirks:**
  1. **Loop Stop Condition:** `while pn <= 10`: hentikan loop jika `cards` kosong, `has_next is False`, atau total collected `>= total`.
  2. **Rate Limiting:** Jeda `asyncio.sleep(0.05)` antar page request (hanya ~7 request untuk 332 anime).
  3. **Trailing Whitespace Sanitization:** String dalam `style_list` sering memiliki trailing whitespace dari upstream (contoh: `"Aksi "`, `"Fantasi "`, `"Fiksi ilmiah "`). Wajib lakukan `.strip()` pada setiap item style agar filter frontend tidak miss-match.
  4. **Field Fallbacks:** `items_v2` tidak menyertakan field `rating`/`score` dan `description`. Pertahankan default `rating: '9.5'` dan `description: ''` agar kontrak skema frontend tetap kompatibel.
  5. **Timeline Merge:** Overlay data dari `/intl/gateway/web/v2/ogv/timeline` untuk memperbarui status penayangan episode terbaru (`index_show`).
  6. **Stale Cache Fallback:** Jika harvest gagal total karena network error, jangan overwrite in-memory cache dengan list kosong; pertahankan cache valid sebelumnya.
  7. **Proxy Regional Catalog Override (`proxies={'http': None, 'https': None}`):** Parameter `s_locale=id_ID` saja TIDAK cukup jika session klien memakai proxy luar negeri (misal SG port 32001 mengembalikan 254 anime; HK port 32012 mengembalikan 1003 anime). Untuk memanen katalog resmi Indonesia (332 anime), lewati proxy session dengan `proxies={'http': None, 'https': None}` jika server host memiliki direct IP, atau rutekan ke exit node IP yang sesuai region target.
  8. **Feed Resilience & Negative Cache Trap Mitigation (`/api/featured` & `/api/popular`):**
     - **Negative Cache Trap:** Jangan pernah memanggil `set_cache(key, data, ttl=3600)` jika `len(data) == 0`. Caching array kosong mengunci halaman depan (Home) dalam keadaan blank selama durasi TTL saat terjadi transient rate limit atau schema drop di search upstream.
     - **3-Tier Multi-Level Sourcing:**
       - **Tier 1 (In-Memory Catalog Slice):** Ambil feed `/api/popular` dan `/api/featured` langsung dari slice store katalog aktif (`build_full_catalog`) di memory (sort by rating / timeline rank). Ini mengeliminasi 8-16 outbound HTTP search calls menjadi sub-5ms in-memory query dan kebal terhadap perubahan modul OGV di `search_v2`.
       - **Tier 2 (Stale Memory Fallback):** Simpan state non-empty terakhir (`_LAST_KNOWN_POPULAR`, `_LAST_KNOWN_FEATURED`) di memory proses. Jika reload katalog gagal, layani stale data ini.
       - Tier 3 (Immutable Static Seed): Sediakan daftar seed statis terverifikasi (season_id, title, cover CDN, rating, status) agar endpoint memiliki jaminan matematis tidak pernah me-return `[]` bahkan saat cold start tanpa koneksi internet.

### F. Dynamic Catalog & Content Type Separation (`GET /api/catalog`)
- **Upstream items_v2 Season Type & Platform Behavior (Web vs Android 360+ Expansion):**
  - Memanggil `items_v2` dengan gabungan `season_type='1,4'` mengembalikan card objects **tanpa key `season_type`** (field bernilai `None`/absen di level item).
  - Untuk memisahkan anime dan donghua secara deterministik, panen `season_type=1` (Anime Jepang) dan `season_type=4` (Donghua Tiongkok) dalam pemanggilan terpisah.
  - **Platform Android Expansion (78 Anime + 282 Donghua = 360 Total):**
    - Saat menggunakan `platform='web'`, upstream memotong `season_type=1` hanya pada 50 judul.
    - Menggunakan `platform='android'` memperluas `season_type=1` menjadi **78 judul Anime Jepang** (membuka judul unggulan seperti *Demon Slayer: Swordsmith Village Arc*, *BLEACH* + film-filmnya, *Tonikaku Kawaii S2*, *Black Summoner*, *Spy Classroom*, dll).
    - `season_type=4` tetap mengembalikan **282 judul Donghua**.
    - Total katalog terpadu mencapai **360 judul unik**.
  - Hasil panen di Indonesia via Android: `season_type=1` menghasilkan 78 judul, `season_type=4` menghasilkan 282 judul, dengan **0 ID overlap** (disjoint murni). Backend menyematkan `'type': 'anime'` (`season_type: 1`) atau `'type': 'donghua'` (`season_type: 4`) ke memory store saat deduplikasi.
- **Season Type 4 Style Anomaly (Dracin vs Donghua):**
  - Pada `season_type=4`, terdapat ~169 dari 282 judul yang tidak memiliki `style_list` atau `styles`.
  - **Aturan Kurasi:** Jangan membuang/memfilter item tanpa style secara sepihak. Judul donghua 3D sci-fi resmi Bilibili (seperti *The Age Of Cosmos Exploration* / 大宇宙时代, `season_id: 2101898`, adaptasi Liu Cixin) metadata `styles`-nya memang kosong di upstream Bstation ID. Menghapusnya akan menghilangkan donghua resmi. Seluruh item `season_type=4` harus tetap dikategorikan sebagai `'donghua'`.
- **Endpoint Request Contract (`GET /api/catalog`):**
  - `type`: `all` (default) | `anime` | `donghua` | `anime,donghua` (mendukung filter tunggal maupun kombinasi).
  - `letter`: Optional `A`..`Z` | `#` (filter huruf awal judul untuk navigasi alfabetik A-Z).
  - `genre`: Optional filter genre/style.
  - `sort`: `title` (default alfabetik A-Z) | `rating` | `latest`.
  - `page`: `int >= 1` (default 1).
  - `pagesize`: `int 1..100` (default 24).
- **Endpoint Response Contract:**
  - `type_counts`: Root counter `{"all": 547, "anime": 265, "donghua": 282}` untuk render badge tab dinamis di frontend tanpa re-query.
  - `catalog`: Array objek anime di mana setiap item memuat atribut konsisten `type` (`'anime'` | `'donghua'`), `season_type` (`1` | `4`), `status`, dan `index_show`.

### G. Blockbuster Anime Seed Discovery Harvester (Unlocking Hidden OGV Titles)
- **Problem (Hidden Anime in `items_v2`):** Endpoint kategori `items_v2` Bstation sengaja menyembunyikan sebagian besar anime legendaris & blockbuster Jepang (seperti *One Piece*, *Naruto*, *Naruto Shippuden*, *Boruto*, *Jujutsu Kaisen*, *Attack on Titan*, *Demon Slayer*, *SPY x FAMILY*, *Frieren*, *Bleach*, *Haikyuu*, *Hunter x Hunter*, *KonoSuba*, *Re:Zero*, *Slime/Tensura*, *One Punch Man*, *JoJo*, *Dr. Stone*, dll). Hanya ~78 anime Jepang standar yang muncul di kategori `season_type=1`.
- **Hybrid Seed Integration Architecture:**
  1. Buat seed manifest terverifikasi (`backend/anime_seeds.json`) yang dipanen via discovery search (`search_v2` dengan ogv modules filter) atau kurasi season resmi.
  2. Pastikan setiap entri seed memiliki schema lengkap: `season_id`, `title`, `cover`, `rating`, `index_show`, `status`, `styles`, `type: 'anime'`, `description`.
  3. Di `build_full_catalog()`:
     - Panen `items_v2` (360 judul: 78 anime + 282 donghua).
     - Merge entri dari `anime_seeds.json` dengan deduplikasi ketat by `season_id`.
     - Stempel `'type': 'anime'` untuk seluruh seed blockbuster Jepang.
     - Total katalog melonjak dari 360 menjadi 540+ judul (Anime Jepang mencapai 260+ judul).
  4. Response `/api/catalog` tetap responsif sub-10ms (disajikan dari in-memory catalog store yang sudah di-merge).

---

## 3. UI Density & Layout Sizing Baselines
- **Featured Hero:** 1 item spotlight (16:9 / 21:9 banner).
- **Featured Carousel:** 6 - 8 item pilihan.
- **Search Grid:** 12 - 20 card per page (default pagination upstream: 20).
- **Poster Aspect Ratio:** 2:3 vertical cover (`w: 240px, h: 360px` di desktop, fluid di mobile).
- **Episode Card Ratio:** 16:9 horizontal thumbnail dengan title, duration badge, dan progress bar.
