# Micro-Budget Google Ads B2B Snippets & Script Playbook

Gunakan panduan dan template ini saat menjalankan kampanye Google Ads Search dengan anggaran mikro (Rp 300.000 – Rp 500.000 / bulan atau Rp 15.000 – Rp 20.000 / hari kerja) untuk bisnis custom manufacturing atau jasa B2B lokal.

## 1. Unit Economics B2B Micro-Budget (Formula 25 Hari Kerja)

Jangan membagi anggaran dengan 30 hari kalender. Anggaran harus dialokasikan **hanya pada hari kerja aktif (Senin – Jumat 08.30 – 17.30 WIB dan Sabtu 09.00 – 13.00 WIB)** saat staf procurement/EO aktif bekerja dan CS standby membalas chat di bawah 3 menit:

- **Alokasi:** Rp 500.000 / 25 hari = Rp 20.000 / hari kerja.
- **Max CPC Cap:** Kunci batas maksimal CPC di angka Rp 1.500 – Rp 2.000 per klik.
- **Volume Klik:** ~333 klik berkualitas tinggi per bulan (~13–15 klik/hari kerja).
- **Konversi Chat WhatsApp (8%):** ~27 prospek chat masuk/bulan.
- **Closing Rate (20%):** ~5 transaksi closing.
- **AOV (Min. 50–100 pcs):** Rp 1.800.000.
- **Proyeksi Omset:** Rp 9.600.000 (Gross ROAS 19,2x lipat dari modal Rp 500rb).

## 2. 5 Pasang Golden Keywords B2B (Anti-Broad Match)

Dilarang menggunakan Broad Match tanpa tanda kutip karena akan memakan saldo untuk pencarian eceran atau tutorial. Wajib gunakan Phrase Match (`"..."`) dan Exact Match (`[...]`):

1. `[vendor pin enamel]` & `"vendor pin enamel"`
2. `[cetak pin enamel custom]` & `"cetak pin enamel custom"`
3. `"pabrik pin custom"` & `"produsen pin custom"`
4. `"pesan pin logo perusahaan"` & `"bikin pin kuningan custom"`
5. `"supplier pin logam jakarta"` & `[bikin pin custom jakarta]`

## 3. Negative Keywords Guardrail (Blokir Pemborosan Saldo)

Masukkan daftar ini ke menu **Negative Keywords** sebelum mengaktifkan kampanye:

```text
# Pencari Eceran & Marketplace
shopee
tokopedia
bukalapak
lazada
tiktok shop
satuan
ecer
eceran
1 pcs
1 biji
beli 1
harga satuan
tanpa minimum order

# Pencari Tutorial, File Gratisan & Desain
gratis
free
cara membuat
tutorial
diy
belajar
template
canva
cdr
corel
vector
gambar
logo
download

# Ambiguitas & Salah Kategori Produk
medali
piala
konveksi kaos
topi
lanyard
tali id card
id card kertas
loker
lowongan kerja
gaji
pin atm
pin bbm
```

## 4. Copywriting Teks Iklan (Responsive Search Ads)

### Headlines (Filter Kuantiti & Umpan Konversi)
- `Bikin Pin Custom Jakarta - Kilat 3-5 Hari`
- `100% Plat Logam Solid 1mm - Bukan Cor`
- `Min. Order Cuma 25 Pcs | Tangan Pertama`
- `Free 3D Mockup Desain - Chat WA Kami!`
- `Spesialis Pin Enamel & Kuningan Magnet`

### Descriptions
- `Vendor Spesialis Pin Custom Sejak 2002. Bahan Kuningan & Stainless Asli 1mm Anti Karat. Pengait Magnet Anti Rusak Pakaian. Cek Pricelist Resmi!`
- `Punya Desain Sendiri? Kirim ke WA Kami & Dapatkan Pratinjau Mockup 3D GRATIS Sebelum Bayar. Siap Kirim Kilat ke Seluruh Indonesia. Chat Admin Fast Respon!`

## 5. Google Ads WhatsApp Conversion Tracking Snippet

Pasang pada tombol WhatsApp di HTML agar Google dapat mengoptimalkan algoritma bidding berdasarkan klik chat riil:

```html
<script>
function trackWhatsAppConversion(label) {
  if (typeof gtag === 'function') {
    gtag('event', 'conversion', {
      'send_to': 'AW-XXXXXXXXX/conversion_label',
      'event_category': 'WhatsApp_Lead',
      'event_label': label || 'General_CTA'
    });
  }
}
</script>
```
