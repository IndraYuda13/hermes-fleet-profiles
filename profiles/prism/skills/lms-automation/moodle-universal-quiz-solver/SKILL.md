---
name: moodle-universal-quiz-solver
description: Otomatisasi pengerjaan kuis Moodle universal (scrape dinamis, AI logic, auto-solve).
---
# LMS Moodle Universal Automation

Workflow universal untuk melakukan otomatisasi pengerjaan kuis pada platform LMS berbasis Moodle (seperti CeLOE Telkom University) secara cerdas, adaptif terhadap acakan (shuffle), dinamis terhadap jumlah soal, dan aman.

## Arsitektur & Pipeline

Arsitektur dibagi menjadi 3 tahap mandiri yang berkomunikasi lewat file JSON:
1. **Universal Scraper (`/root/.openclaw/workspace/projects/lms-automation/universal_scrape.js`)**
   - Menelusuri seluruh kuis halaman demi halaman secara dinamis (mendeteksi tombol "Next" DOM).
   - Menyimpan seluruh teks soal dan daftar opsi jawaban ke `/tmp/scraped_quiz.json`.
2. **AI Decision Logic**
   - AI membaca `/tmp/scraped_quiz.json`.
   - AI menentukan jawaban yang benar secara mandiri dan logis.
   - Jawaban disimpan ke `/tmp/quiz_answers.json` berupa array: `[{"qNum": "1", "correctText": "Teks Jawaban Yang Benar"}]`.
3. **Universal Solver (`/root/.openclaw/workspace/projects/lms-automation/universal_solve.js`)**
   - Memasuki kuis dari halaman 0.
   - Mencocokkan teks opsi di layar dengan `quiz_answers.json` menggunakan text fuzzy matching.
   - Mengklik label jawaban dan memicu navigasi fisik "Next" agar database Moodle menyimpan progres jawaban secara valid.
   - Menangani submit akhir di halaman `summary.php` baik secara DOM click maupun POST fallback.

## Implementasi & Lokasi Script

Seluruh script engine universal disimpan secara permanen di:
- `/root/.openclaw/workspace/projects/lms-automation/universal_scrape.js`
- `/root/.openclaw/workspace/projects/lms-automation/universal_solve.js`

## Langkah Kerja Pengerjaan Kuis

### Langkah 1: Jalankan Scraper
```bash
NODE_PATH=/root/.openclaw/workspace/node_modules node /root/.openclaw/workspace/projects/lms-automation/universal_scrape.js "<URL_KUIS_LMS>"
```

### Langkah 2: Proses Analisis AI
Baca file `/tmp/scraped_quiz.json`, lalu rumuskan jawaban yang tepat untuk masing-masing soal. Tulis hasilnya ke `/tmp/quiz_answers.json` dengan struktur berikut:
```json
[
  {
    "qNum": "1",
    "correctText": "Jawaban A"
  }
]
```

### Langkah 3: Jalankan Solver
```bash
NODE_PATH=/root/.openclaw/workspace/node_modules node /root/.openclaw/workspace/projects/lms-automation/universal_solve.js
```

## Penanganan Masalah (Troubleshooting)

- **Sesi Expired / MFA**: Jika bot terlempar ke form login Microsoft, selesaikan OTP Authenticator dari pengguna.
- **ERR_NETWORK_CHANGED / Timeout**: Jaringan proxy terkadang bermasalah. Script di atas sudah memiliki penanganan error built-in berupa reload otomatis (retry).
