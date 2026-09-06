# Google Ads Low-Cost High-Impact Playbook for Local & Custom B2B Services

## 1. The Core Efficiency Architecture
When running Google Ads for custom manufacturing, merchandise, or local service businesses with a modest budget (e.g. Rp 30,000 – Rp 50,000 / day):
1. **Never use Smart Campaigns:** Google's automated algorithm bids on broad matches, driving unqualified consumer/retail clicks that burn budget within hours.
2. **Search Network Only:** Turn off both "Include Google Search Partners" and "Include Google Display Network". Ads must only appear when users actively query Google Search.
3. **Presence-Only Geo-Targeting:** Set location options strictly to *"Presence: People in or regularly in your targeted locations"*. Never use the default "Presence or interest" (which shows ads to people outside the region researching the city).
4. **Ad Scheduling (CS Alignment):** Only run ads during active business hours (e.g. Monday–Saturday 08:00–18:00). Disable during night/off-hours because unresponded WhatsApp leads have an 80%+ drop-off rate if not answered within 3 minutes.
5. **Maximize Clicks with Max CPC Bid Cap:** Set a manual ceiling on cost-per-click (e.g. Rp 1,500 – Rp 2,500). This guarantees predictable traffic volume (15–30 qualified visitors per Rp 50k daily spend).

---

## 2. Match Types & High-Intent Keyword Sets
Never use broad match keywords without qualifiers. Only use **"Phrase Match"** and **[Exact Match]**.

### Ad Group 1: Urgent & Local Search (Direct Transacting)
- `"bikin pin custom jakarta"`
- `"vendor pin enamel cepat"`
- `[cetak pin custom terdekat]`
- `"jasa pembuatan pin logam"`
- `[pabrik pin custom jakarta]`
- `"pesan pin custom express"`

### Ad Group 2: Material-Specific & Corporate B2B
- `"pin kuningan 1mm"`
- `"pin plat kuningan magnet"`
- `[bikin lencana kuningan]`
- `"pin stainless steel custom"`
- `"lencana instansi plat solid"`
- `[pin magnet anti karat]`

### Ad Group 3: Community & Merchandise Niche
- `"hard enamel pin custom"`
- `"bikin soft enamel pin"`
- `[vendor pin enamel indonesia]`
- `"enamel pin murah jakarta"`

---

## 3. Negative Keyword Shield (Saves 60% of Ad Spend)
Input these negative keywords into the shared negative list on Day 1 before activating the campaign:

| Category | Negative Keywords |
| :--- | :--- |
| **DIY & Educational** | cara, tutorial, membuat sendiri, diy, belajar, gratis, download, template, cdr, psd, vektor, gambar, foto, logo, arti, filosofi, sejarah |
| **Retail & Marketplaces** | shopee, tokopedia, bukalapak, lazada, tiktok shop, satuan, 1 pcs, 1 biji, ecer, eceran, murah sekali, bekas, second |
| **Irrelevant Products & Homonyms** | medali, piala, konveksi kaos, topi, tali lanyard, id card kertas, loker, lowongan kerja, gaji, magang, bbm, pin atm, pin bb |

---

## 4. High-CTR Responsive Search Ads (RSA) Copywriting Formula

### The MOQ Filter Rule
Always include the Minimum Order Quantity (MOQ) in Headline 3 and Description 1 (e.g. *"Min. Order Cuma 25 Pcs"*). This pre-qualifies clicks: retail visitors wanting only 1 piece won't click and waste budget, while corporate, campus, and community organizers see it as an accessible threshold.

### Template Headlines
- **Headline 1 (Keyword + Speed):** `Bikin Pin Custom Jakarta - Pengerjaan Kilat 3-5 Hari`
- **Headline 2 (Material Differentiation):** `100% Plat Logam Solid 1mm - Bukan Bahan Cor`
- **Headline 3 (Pre-qualification):** `Min. Order Cuma 25 Pcs | Harga Pabrik Langsung`
- **Headline 4 (Hook / CTA):** `Free 3D Mockup Desain - Konsultasi WhatsApp Sekarang!`

### Template Descriptions
- **Description 1:** `Vendor Spesialis Pin Custom Sejak 2002. Bahan Kuningan & Stainless Asli 1mm Anti Karat. Pengait Magnet Anti Rusak Pakaian. Cek Pricelist Resmi Disini!`
- **Description 2:** `Punya Desain Sendiri? Kirim ke WA Kami & Dapatkan Pratinjau Desain GRATIS Sebelum Bayar. Siap Kirim Kilat ke Seluruh Indonesia. Chat Admin Fast Respon!`

---

## 5. Conversion Tracking Tag Implementation
Always track the exact event when a visitor clicks the WhatsApp CTA:
```html
<!-- Inside index.html WhatsApp CTA button -->
<a href="https://wa.me/62811958034?text=..." 
   target="_blank" 
   rel="noopener" 
   onclick="gtag('event', 'conversion', {'send_to': 'AW-XXXXXXXXX/AbCdEfGhIjK'});">
   Chat WhatsApp & Free Mockup
</a>
```
Review the **Search Terms report every 48 hours** during the first 2 weeks to identify and add new negative search queries.

---

## 6. Micro-Budget Scaling: The Rp 100k – Rp 500k/Month Protocol

When operational cashflow is tightly constrained and the business cannot sustain standard ad budgets:

### A. The 22–25 Working Days Rule (Never 30 Calendar Days)
Spreading Rp 500.000 over 30 calendar days yields Rp 16.666/day (~11 clicks/day). On Sundays and nights, search traffic shifts toward retail/hobbyists looking for single items while CS is offline, resulting in 80%+ wasted ad spend.
- **Optimal Schedule:** Run **Monday–Friday (08:30–17:30 WIB)** and **Saturday (09:00–13:00 WIB)** at **Rp 20.000 / day** (25 days total).
- **Target CPC Cap:** Set Max CPC at **Rp 1.400 – Rp 1.600** (sweet spot: **Rp 1.500**). This delivers ~13–15 high-intent clicks daily (~333 clicks/month).

### B. The 5 Golden Keywords Model for Micro-Budgets
Do not dilute micro-budgets across dozens of keywords. Restrict campaign strictly to 5 high-intent transactional pairs:
1. `[vendor pin enamel]` / `"vendor pin enamel"`
2. `"cetak pin enamel custom"` / `[cetak pin enamel custom]`
3. `"pabrik pin custom"` / `"produsen pin custom"`
4. `"pesan pin logo perusahaan"` / `"bikin pin kuningan custom"`
5. `"supplier pin logam jakarta"`

### C. Funnel Unit Economics & The 1-Deal BEP Invariant
In custom B2B manufacturing with an Average Order Value (AOV) > Rp 1.250.000 (MOQ 50 pcs @ Rp 25.000) and 50% gross margin:
- **Conversion Math:** 333 clicks $\rightarrow$ 8% WA chat rate (27 leads @ Rp 18.750/lead) $\rightarrow$ 20% closing rate (~5 orders).
- **Projected Revenue:** 5 deals $\times$ Rp 1.800.000 = **Rp 9.600.000 omset** (Gross ROAS 19.2x, Net Profit ~Rp 4.300.000 from Rp 500k ad spend).
- **Break-Even Invariant:** The business only needs **exactly 1 closed deal per month** to break even on ad spend.

### D. The Absolute Minimum Viable Test: Rp 100.000 Total
If even Rp 500.000 cannot be spared:
- **Total Top-up:** Rp 100.000 (via GoPay/OVO/Virtual Account).
- **Budget Harian:** Rp 14.000/day for **7 business days only** (Monday–Friday, 09:00–15:00 WIB).
- **Exact-Match Isolation (Only 2 Keywords):** `[vendor pin enamel jakarta]` and `[bikin pin kuningan jakarta]`.
- **Target:** 8–10 clicks/day. One order of 50 pcs generates Rp 1.250.000 omset, immediately returning 12x ad spend.

### E. The Safe Recovery Loop (Zero-Cost Cashflow Rule)
If operating cash is negative or near zero, **forbid starting Google Ads immediately**. Execute the zero-cost sequence first:
1. Reactivate 20–30 past clients on WhatsApp with mold-fee waiver / magnet upgrade incentives (CAC Rp 0).
2. Close at least 1 re-order (yielding Rp 500k–Rp 600k net profit).
3. Reinvest Rp 100.000 from that realized profit into the 7-day micro-ad test.
*Never fund ad experiments from strained operational cash reserves.*

---

## 7. Zero-Cost Recovery Playbook (When Budget is Rp 0)

When a business states *"bisnis ini agak susah buat keluarin budget"* (cannot afford any paid ads):

### 1. WhatsApp Past Client Reactivation (Days 1–3)
- **Do not send generic broadcasts:** Always send warm, 1-on-1 personal messages checking on past orders.
- **The Service-First Hook:**
  > *"Halo Kak [Nama], salam kenal kembali dari [Brand]. Mau tanya kak, untuk produk yang dipesan waktu itu masih awet dan aman dipakai kan ya? Btw izin info kak, workshop kami sedang buka slot prioritas pengerjaan kilat. Khusus klien lama untuk re-order desain/logo sama, biaya master cetakan GRATIS 100% + bonus upgrade pengait magnet tanpa tambahan biaya. Barangkali ada agenda event dalam waktu dekat kak?"*

### 2. Google Business Profile Visual Frequency (100% Free)
- Update profile title with high-intent local SEO anchors: `[Brand] - Vendor [Spesialisasi]`.
- Upload 5 fresh, well-lit smartphone photos of finished goods, packaging, and dispatch boxes every week.
- Request 3–5 trusted clients to leave 5-star reviews containing exact material keywords (e.g. *"plat kuningan 1mm tebal asli bukan cor"*).

### 3. Direct B2B Outreach (Event Organizers & Creative Agencies)
- Search Instagram for local Event Organizers, Wedding Organizers, and Creative Agencies.
- Send polite, partner-oriented DMs offering wholesale/reseller margins and strict on-time delivery guarantees for their corporate events.
