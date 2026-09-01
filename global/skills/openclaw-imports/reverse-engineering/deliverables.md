# DELIVERABLES: Autonomous Execution Reporting

## Mandatory Reporting Format
Karena agen beroperasi secara otonom, setiap pembaruan pesan kepada Bre WAJIB menggunakan struktur pelaporan progres berikut. DILARANG menyertakan *internal monologue* atau penalaran internal yang panjang.

### 1. Status Eksekusi Terakhir
Jelaskan secara ringkas tindakan atau *command* spesifik yang baru saja Anda eksekusi secara mandiri di environment (contoh: "Telah menjalankan tcpdump selama 30 detik", "Telah menginjeksi script Frida ke PID 1234", atau "Telah melakukan hexdump pada pointer 0xABC...").

### 2. Temuan Utama (Faktual)
Laporkan *output*, log, atau data mentah terpenting yang berhasil Anda dapatkan dari eksekusi di atas. 
- Fokus pada *Custom Headers*, struktur *payload*, atau nilai *return* dari fungsi.
- Jika terjadi *error*, cantumkan pesan *error* atau *stack trace* utamanya.

### 3. Blocker & Risiko
Sebutkan hambatan teknis yang sedang aktif menghalangi proses (contoh: "Aplikasi mendeteksi Frida (Anti-Frida aktif)", "Payload dienkripsi via SSL Pinning", atau "Fungsi memori terobfuskasi").

### 4. Langkah Otonom Selanjutnya (Action Plan)
Sebutkan tindakan spesifik yang AKAN Anda eksekusi secara otomatis setelah laporan ini dikirim (contoh: "Akan menulis ulang script Frida untuk membypass SSL Pinning menggunakan teknik X"). 
*Catatan: Jika Anda telah mencapai batas percobaan (max 3x) atau menabrak aturan batas (boundaries), ubah bagian ini menjadi "Meminta Izin/Arahan dari Bre" beserta opsinya.*
