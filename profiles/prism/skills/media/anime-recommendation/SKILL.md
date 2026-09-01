---
name: anime-recommendation
description: SOP pencarian dan rekomendasi anime agar personal dan tidak duplikat dengan list tontonan Boskuu.
triggers:
  - User meminta rekomendasi anime
  - Boskuu minta dicarikan anime baru
---

# Anime Recommendation SOP

Jika Boskuu meminta rekomendasi anime, JANGAN berikan rekomendasi secara acak. Ikuti langkah-langkah berikut secara berurutan:

## 1. Cek Database Tracker
Gunakan terminal/read_file untuk membaca 3 file catatan anime di workspace (`/root/.openclaw/workspace/`):
- `WatchedAnime.txt` (anime yang sudah ditonton)
- `OnProgressAnime.txt` (anime yang sedang ditonton)
- `WishlistAnime.txt` (antrean tontonan)
*Tujuan: Memastikan tidak merekomendasikan anime yang sudah ada di list.*

## 2. Analisis Kriteria
Pahami genre atau mood yang diminta (misal: isekai, OP MC, komedi, dark fantasy). Jika permintaan terlalu umum, tanyakan vibe apa yang sedang diinginkan.

## 3. Pencarian Data & Verifikasi Adaptasi
Pencarian judul anime WAJIB menggunakan `web_extract` langsung ke halaman pencarian LiveChart HTML:
`https://www.livechart.me/search?q=<query>`
*(Jangan gunakan API `livechart.me/api/v1/anime` atau Jikan API karena sering timeout/bad request).*

Dari halaman search LiveChart tersebut, dapatkan anime ID-nya dari URL detail (contoh: `https://www.livechart.me/anime/10383`).

## 3A. Verifikasi Platform Streaming & Link MAL (Penting)
1. Panggil `web_extract` ke halaman detail LiveChart (`https://www.livechart.me/anime/<id>`) untuk mendapatkan link MyAnimeList (MAL) di bagian "External Resources" dan link ke streams.
2. Panggil `web_extract` ke halaman streams LiveChart (`https://www.livechart.me/anime/<id>/streams`).

**Aturan Parsing Platform Streaming:**
1. List semua platform streaming yang tertera di halaman tersebut (misal BiliBili, Crunchyroll, CatchPlay+ ID, Muse Asia, Muse Indonesia, Netflix).
2. Sertakan **link langsung (hidden link)** ke platform streaming yang ada di halaman tersebut.
3. **Filter Subtitle Indo:** 
   - Jika terdapat catatan seperti `※ Sub & Dub (English, French, German, ...)` atau `※ Sub (Hindi)`, **PERIKSA** apakah ada `Indonesian` di dalamnya.
   - Jika **TIDAK ADA** `Indonesian` dalam daftar `※ Sub`, **JANGAN** tampilkan platform tersebut.
   - Jika catatan `※ Sub` secara eksplisit mencantumkan `Indonesian` (contoh: `※ Sub (English, Thai, Vietnamese, Indonesian)`), ATAU jika platform tersebut khusus Indonesia (seperti `Muse Indonesia`, `CatchPlay+ ID`), MAKA tampilkan platform tersebut beserta linknya.
   - Jika tidak ada platform yang menyediakan Sub Indo resmi di halaman tersebut, tuliskan: "Tidak tersedia dengan sub Indo resmi".

## 3B. Ekstraksi Detail dari MyAnimeList (MAL)
Panggil `web_extract` ke link MyAnimeList yang didapat dari LiveChart (contoh: `https://myanimelist.net/anime/<mal_id>`) untuk mengambil info detail:
1. **Rating:** Ambil skor dari MAL (misal `7.06`).
2. **Genres:** Ambil daftar genre dari tabel Information (misal `Action, Adventure, Fantasy, Romance`).
3. **Episodes:** Ambil jumlah episode (misal `12 eps`).
4. **Sequel / Total Season:** Cek bagian `Related Entries`. Jika terdapat entri bertipe `Sequel` (misal `Sequel: Seirei Gensouki 2`), berarti anime tersebut memiliki Season 2 (abaikan entri `Adaptation` seperti Manga/Light Novel).

## 6. Format Pelaporan Hasil Recomendasi (Template)
Gunakan format berikut saat menyajikan rekomendasi kepada Boskuu:

```markdown
1. **[Judul Anime (Judul Inggris)]**
   - **Rating & Genre:** ⭐ [Rating]/10 | [Genre 1, Genre 2, ...]
   - **Total Episode & Season:** [X Eps] | [1 Season / Memiliki Sequel (Season 2)]
   - **Deskripsi:** [Penjelasan singkat sinopsis & daya tarik/point utama anime]
   - **Platform Streaming (Sub Indo):** [Platform 1](URL) | [Platform 2](URL) *(atau "Tidak tersedia dengan sub Indo resmi")*
```

## 7. Penawaran Update Tracker
Tanyakan ke Boskuu keputusannya.
- Jika ingin ditonton sekarang: Tambahkan judul ke `OnProgressAnime.txt`.
- Jika ingin disimpan: Tambahkan judul ke `WishlistAnime.txt`.