# Riset desain website untuk Hermes + Gemini 3.8 Flash + Lens

12 September 2026. Fokus: satu brief dari user menghasilkan website dengan kualitas desain tinggi melalui proses internal yang mandiri.

**Kesimpulan utama.** Setup lu sudah punya pelaksana, browser, dan reviewer visual. Prioritas berikutnya adalah memperjelas keputusan desain, mengalibrasi Lens terhadap selera lu, dan membuat temuannya mengikat proses revisi. Menambah jumlah agent belum tentu menyelesaikan ketiganya. Target satu prompt dari user masuk akal sebagai tujuan workflow; kesetaraan dengan studio kreatif untuk setiap jenis website belum dapat dijamin oleh skill atau model tertentu.

**Batas diagnosis.** Informasi setup berasal dari lu: Gemini 3.8 Flash, multi-agent, browser tersedia, Lens memeriksa visual, serta keluhan emoji sebagai ikon dan indikator active yang berkedip. Gue belum mengaudit konfigurasi, prompt Lens, log multimodal, atau contoh website hasil Hermes. Maka penyebab khusus setup lu di bawah adalah hipotesis yang bisa diuji, bukan temuan audit.

## 1. Apa yang sudah diperiksa

- Membuka homepage OFF+BRAND dengan browser Chromium melalui Microsoft Edge headless pada desktop 1440 × 1000 dan mobile 390 × 844.
- Memeriksa tangkapan hero, intro, bagian karya, dan footer; membaca computed style, daftar font, struktur halaman, serta penanda library dalam JavaScript publik.
- Membaca dokumentasi resmi Hermes, Google, Anthropic, Playwright, W3C, GSAP, dan repositori pengembang skill.
- Tidak melakukan benchmark Gemini pada website lu, profiling perangkat nyata, atau audit accessibility lengkap terhadap situs referensi. Screenshot tidak membuktikan kelancaran animasi atau performa produksi.

Bukti tampilan saat pemeriksaan: [desktop](C:/Users/ASUS/Documents/Codex/2026-09-12/bre-ai-gw-masih-sangat-sangat/outputs/reference/offbrand-desktop.png) dan [mobile](C:/Users/ASUS/Documents/Codex/2026-09-12/bre-ai-gw-masih-sangat-sangat/outputs/reference/offbrand-mobile.png). Keduanya tangkapan situs referensi untuk analisis, bukan desain yang dibuat dalam tugas ini.

**Observasi referensi.** Homepage yang diperiksa memakai latar hangat #E5E4E0, tipografi besar dengan font terdaftar “Ataero Retina OB Edition”, bola gradasi sebagai visual dominan, orbit tipis, dan karya dengan gambar kuat. Headline desktop terpecah melintasi ruang; mobile menumpuknya di atas objek. Halaman memuat aset Webflow dan bundle dengan penanda GSAP, ScrollTrigger, serta Three.js. Kehadiran library bukan bukti semua fiturnya aktif. [Situs yang diperiksa](https://www.itsoffbrand.com/).

**Interpretasi gue:** kekuatan referensi itu datang dari hubungan ukuran, posisi, ruang, gambar, dan gerak yang punya satu arah. Memindahkan bola, warna, atau animasinya ke setiap proyek akan menghasilkan template baru. Yang layak dijadikan standar adalah kualitas keputusan dan konsistensi pelaksanaannya.

## 2. Mengapa browser dan multi-agent belum cukup

Anthropic mendokumentasikan kecenderungan output frontend menuju pola umum dan penggunaan skill untuk memberi arahan yang lebih spesifik. Itu mendukung penggunaan instruksi desain yang konkret; artikel tersebut tidak membuktikan semua model akan membaik dengan besaran yang sama. [Riset skill frontend](https://claude.com/blog/improving-frontend-design-through-skills).

Dalam eksperimen harness terpisah, Anthropic memisahkan generator dan evaluator, memberi evaluator akses browser, lalu mengalibrasinya dengan contoh penilaian. Mereka menjalankan 5–15 iterasi; sebagian run berlangsung hingga empat jam. Iterasi terakhir tidak selalu paling disukai. Ini bukti proses internal dapat membantu dalam eksperimen mereka, bukan jaminan bahwa Lens atau Gemini lu otomatis menghasilkan efek serupa. [Eksperimen generator–evaluator](https://www.anthropic.com/engineering/harness-design-long-running-apps).

Hipotesis untuk setup lu, urut berdasarkan kemudahan dibuktikan:

| Dugaan | Cara mengecek | Perubahan jika terbukti |
|---|---|---|
| Lens hanya mengecek overlap, error, dan layout | Baca tiga review terakhir: adakah evaluasi komposisi dan identitas? | Tambahkan rubric desain serta referensi pembanding |
| Review tidak mengikat | Cari apakah hasil tetap diserahkan saat temuan belum selesai | Orkestrator wajib menunggu review dan verifikasi ulang |
| Larangan cuma tersimpan di percakapan lama | Periksa paket instruksi yang benar-benar diterima builder dan Lens | Simpan kebijakan permanen yang singkat; muat di setiap handoff |
| Lens menerima screenshot yang terlalu kecil atau hanya deskripsi | Periksa payload multimodal dan contoh crop | Kirim gambar yang dapat dibaca, crop detail, serta bukti viewport |
| Semua agent mendesain sendiri | Bandingkan type scale, radius, ikon, dan spacing per section | Satu pemilik keputusan global; semua pelaksana mengikuti kontrak yang sama |
| Kritik terlalu abstrak | Cari komentar seperti “lebih premium” tanpa lokasi dan tindakan | Wajib ada masalah, bukti, dampak, revisi, dan cara memeriksa |
| Visual utama merupakan placeholder | Periksa apa yang sebenarnya mengisi area terbesar | Rencanakan aset dan crop sebelum full implementation |

Dokumentasi Hermes membedakan snapshot teks dengan screenshot visual. Pada jalur native vision, gambar diteruskan langsung; jalur lain dapat memakai model vision tambahan. Nama agent “Lens” tidak menunjukkan model mana yang menerima piksel. Periksa jalur aktual tanpa mengasumsikan browser lu rusak. [Referensi tool Hermes](https://hermes-agent.nousresearch.com/docs/reference/tools-reference).

## 3. Perbaiki gejala yang lu sebut dengan aturan operasional

**Ikon.** Default proyek lu: emoji Unicode dilarang sebagai ikon kontrol, navigasi, kartu fitur, dan dekorasi UI. Pilih satu keluarga SVG dengan ukuran dan ketebalan konsisten, atau hilangkan ikon jika label sudah cukup. Konten yang memang berupa emoji dari user tetap konten; jangan dihapus oleh pemeriksaan global. Lucide dapat dipakai sebagai titik awal karena menyediakan aset SVG dan aturan konsistensi, tetapi mengganti emoji dengan Lucide saja belum menciptakan art direction. [Dokumentasi Lucide](https://lucide.dev/guide/).

**Status.** State stabil seperti Active, Available, Connected, dan Online menggunakan label tenang. Dot kecil statis boleh jika berguna. Animasi hanya untuk event atau proses yang sedang berlangsung: memuat, merekam, menyinkronkan. Durasi dan kondisi berhentinya harus jelas. Status tidak boleh mengandalkan warna saja. [W3C: penggunaan warna](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html).

**Gerak.** Setiap gerak harus punya tujuan, trigger, perilaku akhir, dan fallback. Bedakan gerak identitas brand dengan indikator aplikasi. Bentuk yang terus bergerak untuk presentasi brand dapat masuk akal; titik yang berkedip untuk state permanen dapat mengganggu. `prefers-reduced-motion` perlu dipertimbangkan; WCAG 2.3.3 tentang animasi dari interaksi berada pada level AAA, jadi jangan salah melabelinya sebagai kewajiban AA menyeluruh. [W3C: animation from interactions](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html).

**Larangan tidak cukup.** Setelah menghapus emoji dan pulse, hasil mungkin sekadar lebih bersih. Untuk mencapai tingkat craft tinggi, builder masih perlu menentukan konsep, hierarki, gambar, komposisi, urutan cerita, dan perubahan susunan pada mobile.

Jangan menjadikan font Inter, gradient, warna ungu, border radius, dan card sebagai dosa universal. Nilai kesesuaiannya dengan pekerjaan halaman. UI administrasi yang efisien mungkin membutuhkan tabel dan pola familier; landing page brand mungkin membutuhkan ekspresi yang lebih kuat.

## 4. Kontrak desain sebelum full implementation

Kontrak adalah dokumen keputusan ringkas yang dipakai semua agent. Nama file di sini usulan, bukan konfigurasi bawaan Hermes.

| Isi | Yang harus tertulis |
|---|---|
| Produk dan audience | Siapa pengunjung, apa yang dicari, tindakan utamanya |
| Janji brand | Satu kalimat yang spesifik, dengan bukti yang tersedia |
| Konsep | Ide yang menghubungkan subject matter dengan bentuk visual |
| Hierarki | Elemen pertama, kedua, ketiga yang harus terlihat |
| Tipografi | Peran font, skala ukuran, line-height, measure, dan aturan line break |
| Komposisi | Grid, alignment, proporsi teks/gambar, ruang kosong, ritme antarsection |
| Warna | Peran canvas, ink, accent, muted, semantic status |
| Aset | Subjek, sumber, crop desktop/mobile, ukuran, format, fallback |
| Gerak | Tujuan, trigger, durasi usulan, akhir, reduced-motion |
| Responsive | Apa yang disusun ulang, dikurangi, diprioritaskan |
| Kebijakan | Emoji UI, status pulse, data contoh, batasan aksesibilitas |

Contoh arahan buatan untuk brand furnitur: “Material menjadi bukti kualitas: macro kayu dan sambungan, judul editorial yang singkat, warna netral hangat, spesifikasi mudah dibandingkan, motion mengungkap detail konstruksi.” Ini lebih bisa dikerjakan daripada “website luxury minimal premium”.

Jangan menentukan tipografi tanpa copy yang mendekati final. Panjang judul dan isi adalah bagian dari komposisi. Jangan membuat klaim klien, testimoni, jumlah pengguna, atau penghargaan fiktif agar layout terlihat meyakinkan.

## 5. Workflow satu brief dengan eksplorasi dan revisi internal

**Tahap A — brief dan referensi.** Gunakan konteks yang sudah ada. Jika informasi nonkritis kurang, tulis asumsi. Ambil 3–5 referensi yang punya tugas spesifik: komposisi, type, aset, interaksi. Setiap referensi harus dijelaskan apa yang dipelajari dan apa yang tidak relevan. OFF+BRAND boleh menjadi acuan craft; referensi domain memastikan halaman tetap cocok dengan audience.

**Tahap B — tiga kandidat kecil.** Buat tiga konsep yang berbeda dalam struktur, gambar, dan hierarki. Render hero serta satu section lanjutan, plus susunan mobile sederhana. Ganti warna saja tidak dihitung sebagai kandidat berbeda. Hindari membangun tiga website penuh sebelum tahu mana yang layak.

**Tahap C — seleksi dan kontrak.** Lens membandingkan kandidat terhadap brief. Satu pemilik desain memilih arah utuh dan mencatat alasannya. Jangan mencampur semua kandidat sampai identitasnya kabur. Setelah dipilih, kontrak menjadi sumber keputusan bersama.

**Tahap D — aset dan satu potongan lengkap.** Siapkan visual dominan, font yang dapat digunakan, copy, dan crop. Selesaikan hero + satu section pada desktop/mobile. Jika potongan itu belum kuat, revisi konsep atau aset sekarang. Polesan kecil pada akhir tidak akan menyelamatkan struktur dasar yang lemah.

**Tahap E — bangun dan review.** Kerjakan section lain dengan token yang sama. Lens membaca hasil render, memeriksa interaksi, dan mengembalikan maksimal lima temuan prioritas beserta semua pelanggaran wajib. Builder memperbaiki, Lens memeriksa ulang build yang baru.

**Tahap F — simpan versi terbaik.** Usulan awal: sediakan anggaran 2–4 siklus revisi setelah konsep dipilih. Angka ini budget eksperimen, bukan angka yang terbukti optimal. Jika dua siklus tidak membantu, evaluasi ulang arah atau aset. Simpan kandidat terbaik; jangan menganggap file terbaru selalu terbaik. Berhenti sesuai budget yang disepakati dan laporkan bila standar belum tercapai.

## 6. Susunan peran untuk sistem lu

| Peran | Tanggung jawab | Batas keputusan |
|---|---|---|
| Orkestrator / pemilik desain | Brief, pemilihan konsep, kontrak, anggaran, status selesai | Menjaga satu arah visual |
| Builder | Komponen, layout, responsive, interaksi | Tidak mengganti konsep global secara sepihak |
| Lens | Kritik visual, pembandingan, bukti review, verifikasi perbaikan | Tidak menyetujui hanya dari penjelasan builder |
| Produser aset, bila perlu | Foto/ilustrasi/render, crop, kompresi | Mengikuti bahasa visual yang dipilih |

Ini pembagian fungsi yang bisa dipetakan ke agent lu yang sudah ada. Satu agent bisa menjalankan beberapa fungsi secara berurutan. Paralel berguna untuk pencarian referensi, kandidat terisolasi, dan produksi aset setelah arahnya jelas. Banyak agent mengedit stylesheet atau menentukan selera bersamaan menciptakan risiko ketidakselarasan.

Handoff harus membawa brief, kontrak, file yang boleh diedit, build ID, URL preview, bukti, batasan, dan kriteria selesai. Nama persona seperti “world-class designer” saja tidak memberi informasi tersebut.

## 7. Lens perlu bukti dan kalibrasi selera

**Kalibrasi awal yang gue usulkan:** kumpulkan 12 contoh hasil baik/buruk dari beberapa domain yang relevan. Beri label pilihan lu dan 1–3 alasan konkret per contoh. Gunakan delapan untuk melatih penilaian lewat konteks dan empat sebagai contoh baru yang tidak diperlihatkan sebelumnya. Jumlahnya starter set praktis, bukan ukuran statistik yang tervalidasi.

Kalibrasi bukan daftar screenshot cantik. Contoh “ditolak” harus menjelaskan bahwa headline dan card punya bobot sama, detail status mencuri perhatian, foto tidak membuktikan produk, atau layout bisa dipakai brand apa pun dengan mengganti logo. Contoh “diterima” menjelaskan keputusan mana yang bekerja.

**Pisahkan tiga penilaian:** kepatuhan preferensi lu; mutu desain; fungsi dan aksesibilitas. Hasil dapat lulus dua yang terakhir tetapi tetap melanggar selera lu. Hasil yang artistik juga dapat gagal fungsi. Skor rata-rata tidak boleh menyembunyikan tombol utama yang mati.

Usulan bobot awal untuk website brand: identitas 25%, komposisi 25%, tipografi 15%, aset 15%, interaksi/motion 10%, responsive 10%. Fungsi inti dan pelanggaran wajib merupakan syarat terpisah. Ambang 85/100 dan setiap dimensi minimal 8/10 dapat dipakai untuk memulai, kemudian dikalibrasi terhadap penilaian lu. Skor itu tidak membuktikan “setara OFF+BRAND”.

Lens harus menyimpan URL, build, viewport, state, dan bukti per temuan. “Terlihat profesional” tidak cukup. Review gerak membutuhkan rangkaian frame atau pemeriksaan browser selama beberapa detik; gambar tunggal tidak menunjukkan kedipan. Full-page screenshot membantu melihat ritme, sementara viewport/crop membantu membaca detail.

Screenshot comparison dari Playwright berguna untuk menangkap perubahan terhadap baseline yang sudah diterima. Ia tidak menentukan keindahan. Baseline buruk hanya akan mengabadikan desain buruk, dan hasil raster dapat berbeda menurut lingkungan browser. [Dokumentasi visual comparison](https://playwright.dev/docs/test-snapshots).

## 8. Skill dan tooling yang paling relevan

| Kandidat | Peran dalam setup lu | Batas praktis |
|---|---|---|
| Impeccable | Arah desain, kritik, pengurangan dekorasi, polish | Terapkan melalui orkestrator; uji terhadap selera lu |
| Anthropic frontend-design | Alternatif fondasi instruksi art direction | Jangan menumpuk dua kebijakan estetika yang bertentangan |
| Vercel web-design-guidelines | Pemeriksaan UX, a11y, dan implementasi | Lulus audit teknis tidak berarti original |
| Playwright atau browser Hermes yang sudah tersedia | Screenshot, interaksi, state, bukti regresi | Harus benar-benar dipanggil sebelum selesai |
| Satu sistem ikon SVG | Konsistensi kontrol dan navigasi | Ikon bukan pengganti konten atau konsep |
| GSAP/Three.js bila brief membutuhkannya | Gerak kompleks atau visual 3D | Bukan persyaratan semua website |

Impeccable menyediakan alur craft, critique, audit, dan polish serta instalasi untuk Hermes. Dokumentasinya menyatakan hook desain otomatis tidak terpasang pada Hermes. Karena itu pilih skill ini sebagai bahan proses dan jadwalkan pemeriksaannya secara eksplisit. [Repo resmi Impeccable](https://github.com/pbakaus/impeccable).

Contoh perintah dokumentasi untuk instalasi per proyek; ini **belum dijalankan** dan perlu disesuaikan dengan versi lokal:

```text
npx impeccable install --providers=hermes --scope=project
hermes skills trust
```

Perintah kedua adalah mekanisme Hermes untuk mempercayai skill lokal proyek. Setelahnya pastikan skill terlihat dan lakukan satu percobaan pemanggilan. Jangan menganggap menyalin folder berarti setiap worker memuat instruksinya. [Dokumentasi skill Hermes](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills).

Alternatif fondasi: [frontend-design resmi Anthropic](https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md). Pelengkap teknis: [web-design-guidelines Vercel](https://github.com/vercel-labs/agent-skills/blob/main/skills/web-design-guidelines/SKILL.md). Rekomendasi gue: satu fondasi desain, kebijakan preferensi lu, kontrak proyek, dan rubric Lens. Muat materi detail sesuai kebutuhan.

## 9. Perlakuan terhadap Gemini 3.8 Flash

Dokumentasi resmi mencantumkan `gemini-3.8-flash` mendukung input gambar, video, dan thinking low/medium/high, dengan output teks. Model ini tidak menghasilkan gambar secara native. Default thinking yang didokumentasikan adalah medium. Jika perlu gambar orisinal, sediakan tool produksi aset terpisah. [Spesifikasi Gemini 3.8 Flash](https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash), [panduan model terbaru](https://ai.google.dev/gemini-api/docs/latest-model).

Jangan langsung menyimpulkan Flash tidak mampu. Mulai dengan model yang sama dan perbaiki proses. Eksperimen berikutnya: gunakan thinking high untuk pemilihan konsep dan review Lens jika provider serta adapter Hermes meneruskan setting itu. Cek request/log; menulis “think harder” belum membuktikan konfigurasi API berubah.

Jika hasil tetap tidak memadai, bandingkan model vision alternatif khusus untuk pemilik desain atau Lens, dengan brief, aset, budget, dan rubric yang sama. Pilih lewat hasil penilaian lu, bukan nama kelas model. Model berbeda juga tidak menjamin penilaian independen atau lebih baik.

Catatan implementasi Hermes: dokumentasi saat riset menyebut `delegation.model` berlaku global pada anak `delegate_task`, bukan parameter model per tugas. `/review` memiliki pengaturan model terpisah. Jika Lens lu punya routing kustom, periksa implementasinya; jangan mengasumsikan tiap nama agent otomatis punya model sendiri. [Dokumentasi delegasi](https://hermes-agent.nousresearch.com/docs/user-guide/features/delegation).

## 10. Cara membuktikan perbaikannya

Jalankan eksperimen bertahap dengan input sama:

| Kondisi | Perubahan |
|---|---|
| A | Setup sekarang |
| B | A + kebijakan ikon/status + syarat review mengikat |
| C | B + referensi teranotasi + kontrak + tiga kandidat kecil |
| D | C + Lens terkalibrasi dan bukti verifikasi ulang |
| E, opsional | D + perubahan model/tingkat thinking pada peran yang dipilih |

Gunakan tiga brief awal: situs brand yang kaya visual; SaaS dengan demo produk; dashboard dengan banyak informasi. Ulangi tiap kondisi dua kali sebagai pilot. Ini memberi gambaran awal, bukan estimasi statistik presisi. Setelah memilih kandidat workflow, konfirmasi pada brief baru agar tidak mengoptimalkan sistem untuk contoh latihan saja.

Bandingkan A/B tanpa nama model dan acak posisi kiri/kanan. Lu menilai kecocokan audience, hierarki, kekhasan, dan kenyamanan. Ukur preferensi manusia, jumlah pelanggaran wajib, kelulusan tugas utama, jumlah revisi manual setelah handoff, waktu total, token/biaya, serta versi yang paling disukai.

Kenaikan skor Lens tanpa kenaikan preferensi lu adalah tanda reviewer salah kalibrasi atau generator mengoptimalkan skor. Jangan menyimpan setiap output sebagai contoh bagus otomatis. Memory desain hanya mempromosikan pola yang sudah diterima, lengkap dengan konteks kapan pola itu cocok.

## 11. Kualitas saat digunakan

Website dengan motion harus tetap terbaca ketika gerak dikurangi, navigasi harus dapat dioperasikan lewat keyboard/touch, font dan aset harus termuat, serta form perlu state validasi dan hasil yang benar. Untuk implementasi GSAP, `matchMedia()` dapat membantu mengatur kondisi responsive dan preferensi gerak. [GSAP matchMedia](https://gsap.com/docs/v3/GSAP/gsap.matchMedia()/).

Target Core Web Vitals yang didokumentasikan: LCP ≤ 2,5 detik, INP ≤ 200 ms, CLS ≤ 0,1 pada persentil ke-75, dipisah mobile/desktop. Itu target pengalaman lapangan. Pengukuran lokal atau satu skor Lighthouse bukan bukti pencapaian field metrics. Tidak ada klaim bahwa referensi maupun hasil Hermes sudah mencapai target ini. [Web Vitals](https://web.dev/articles/vitals).

Benchmark rekonstruksi screenshot juga berbeda dari menemukan konsep brand baru. Design2Code menilai konversi screenshot menjadi implementasi; performa pada tugas tersebut tidak dengan sendirinya membuktikan kemampuan menciptakan art direction. [Paper Design2Code](https://arxiv.org/abs/2403.03163).

**Prioritas penerapan untuk lu:** pertama, kebijakan ikon/status dan review yang mengikat. Kedua, kontrak bersama dan paket contoh selera. Ketiga, kandidat konsep serta perencanaan aset. Keempat, eksperimen model bila proses yang sudah diperbaiki masih belum memenuhi standar. Dua dokumen pendamping menyediakan prompt orkestrator dan kontrak Lens untuk adaptasi; keduanya belum dipasang atau diuji di Hermes lu.
