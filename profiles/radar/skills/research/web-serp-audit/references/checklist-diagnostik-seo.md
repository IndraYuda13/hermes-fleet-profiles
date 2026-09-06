# Checklist Diagnostik Penurunan Traffic & Omset Web Komersial

Gunakan checklist ini secara terstruktur saat menganalisis keluhan penurunan omset organik pada situs web e-commerce atau jasa:

### 1. Pengecekan Server & Protokol
- [ ] Uji respon status code HTTP untuk apex domain (`https://domain.com/`) dan subdomain `www` (`https://www.domain.com/`). Apakah salah satunya mengembalikan HTTP 301 ke canonical URL utama?
- [ ] Periksa DNS IP: Apakah blog atau landing page penting ditaruh di subdomain dengan IP server terpisah yang memecah otoritas domain?
- [ ] Validasi robots.txt: Pastikan CSS, JS, dan path gambar penting tidak di-disallow sehingga crawler dapat me-render halaman secara utuh.
- [ ] Validasi sitemap.xml: Hitung jumlah total URL yang di-submit. Apakah ada endpoint produk penting yang luput dimasukkan?

### 2. Evaluasi Arsitektur Halaman (Information Architecture)
- [ ] Cek status endpoint spesifik per kategori produk (uji probe HTTP GET). Apakah mengembalikan 200 OK atau 404 Not Found?
- [ ] Evaluasi kedalaman topik: Apakah situs mengandalkan struktur *One-Page Brochure* tipis (<1000 kata) yang mencoba meranking puluhan kata kunci sekaligus? Jika ya, rekomendasikan pembuatan *Silo Pages* (dedicated landing pages per intent produk).

### 3. Evaluasi On-Page & Schema Markup
- [ ] Audit H1: Apakah H1 mencantumkan kata kunci komersial utama atau hanya nama brand/domain?
- [ ] Validasi Schema JSON-LD:
  - Catat batasan FAQPage rich results di Google (hanya efektif untuk situs otoritas medis/pemerintah sejak Aug 2023).
  - Pastikan menggunakan Schema LocalBusiness atau Product/Offer dengan atribut harga yang konsisten dengan teks halaman.
- [ ] Singkirkan meta keywords usang yang berpotensi memicu flag keyword stuffing.

### 4. Lanskap Persaingan SERP & Posisi Pasar
- [ ] Identifikasi apakah kueri transaksional ("beli X", "harga X") didominasi marketplace besar (Shopee, Tokopedia) yang menawarkan garansi transaksi, review pembeli, dan bebas ongkir.
- [ ] Identifikasi apakah kueri berbasis geografi ("vendor X [kota]") terkanibalisasi oleh Google Maps Local 3-Pack.
- [ ] Formulasikan rekomendasi diferensiasi bisnis:
  - Transisi dari perang eceran satuan ke positioning B2B/grosir (MOQ, mockup pra-cetak gratis, faktur pajak resmi).
  - Optimasi listing Google Business Profile dengan dokumentasi fisik workshop untuk merebut Local Pack.
