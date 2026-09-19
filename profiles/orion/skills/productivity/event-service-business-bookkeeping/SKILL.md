---
name: event-service-business-bookkeeping
description: Use when bookkeeping event/service pipelines & cashflow.
version: 1.0.0
metadata:
  hermes:
    tags: [finance, bookkeeping, cashflow, accounting, event-management, excel, openpyxl, invoicing, cogs]
    category: productivity
---

# Event and Service Business Financial Bookkeeping & Cashflow Architecture

This skill provides the operational framework, data architecture, and spreadsheet automation standards for event-driven, creative, and appointment-based service businesses (Make Up Artists, wedding photographers/videographers, event organizers, creative studios, catering, and sound/lighting providers).

---

## When to Use

- Building or auditing financial bookkeeping workbooks, client booking pipelines, or milestone payment schedules.
- Structuring cashflow models that track cash from initial booking deposit to final settlement.
- Designing financial controls to prevent uncollected receivables, project-level margin leaks, or personal/business fund co-mingling.
- Automating multi-sheet spreadsheets (Excel `.xlsx` via `openpyxl` or Google Sheets) with interconnected formulas (`SUMIFS`, `VLOOKUP`, `IF`, dynamic alert triggers).
- Drafting financial SOPs and payment policy guidelines for service clients and freelancers.

---

## 1. The 5-Phase Financial Lifecycle (Booking to Settlement)

Event services operate on long lead times (weeks or months between booking and service delivery). Manage all client projects through 5 sequential financial gates:

```text
[ Phase 1: H-Booking ] ──► [ Phase 2: H-30 Days ] ──► [ Phase 3: H-7 Days ] ──► [ Phase 4: Event Day ] ──► [ Phase 5: H+1 Finish ]
   Termin 1 (DP 30%)          Termin 2 (40%)            Termin 3 (Final 30%)        Execution & Extras         Kru Settlement
  Calendar slot locked       Production capital &       ZERO DEBT POLICY:           Signed onsite voucher      Pay freelancers &
    Non-refundable           booking freelance crew    Release field crew mandate    for overtime/add-ons      bank reconciliation
```

1. **Phase 1: H-Booking (Termin 1 / DP 20–30%):**
   - *Purpose:* Locks calendar date exclusively.
   - *Rule:* Non-refundable. Date is never held without cleared funds in the business account.
2. **Phase 2: H-30 Days (Termin 2 / 40–50%):**
   - *Purpose:* Working capital for event preparation.
   - *Rule:* Locks client rundown, orders perishable materials (e.g., fresh flowers, specific cosmetics, specialized props), and confirms freelance crew availability with non-refundable deposits.
3. **Phase 3: H-7 to H-3 Days (Termin 3 / Final Balance 20–30%):**
   - *Purpose:* Complete contract clearance before service delivery (**Zero Debt Policy**).
   - *Rule:* Prerequisite for issuing crew assignment orders.
4. **Phase 4: Event Day / D-Day (Service Execution & Field Extras):**
   - *Purpose:* Pure technical execution without financial confrontation.
   - *Rule:* Any field overtime or extra client requests must be documented on a signed onsite voucher before execution.
5. **Phase 5: H+1 Post-Event (Settlement & Reconciliation):**
   - *Purpose:* Disburse freelance crew honorariums and reconcile event profitability.
   - *Rule:* Settle crew fees only after receipt of equipment, timesheets, and field expense receipts. Invoice client for field add-ons within 24 hours.

---

## 2. The "Zero Debt on Event Day" Invariant

### The Golden Rule
**Never collect or negotiate core package balance payments on the day of the event.**

### Why (Failure Mechanism)
- Demanding payment during a wedding or live event damages the client's emotional experience, sparks hostility with family/organizers, and creates severe collection risks if the client departs immediately for honeymoon or travel.
- Event days are chaotic; collecting cash onsite risks theft, misplacement, or disputes over payment amounts.
- Enforcing **100% pre-payment by H-7 (grace period H-3)** ensures zero collection friction and guarantees client commitment.

---

## 3. Cost Architecture: Direct Project Costs (COGS) vs Operating Overhead (Opex)

Service owners frequently fail to realize cash profits because project working capital is co-mingled with business overhead or personal draws. Enforce strict classification:

### A. Direct Project Costs (COGS / Biaya Langsung Proyek)
- **Definition:** Expenses incurred solely because a specific client project exists. Zero if project does not happen.
- **Components:**
  - Freelance assistant & specialist honorariums (hairdo stylist, second shooter, lighting technician).
  - Project-specific consumables (false lashes, disposable sponges, softlens, fresh floral accessories, specialized film/printing).
  - Project mobility: fuel/BBM, highway tolls, parking, travel tickets, crew accommodation.
  - Rental costs for project-specific gear, backdrops, or gowns.
- **Rule:** Every COGS transaction must carry a foreign key `ID_Booking_Ref` to evaluate individual project gross profit margins.

### B. Operating Overhead (Opex / Biaya Operasional Studio)
- **Definition:** Ongoing baseline costs to keep the business operational regardless of project volume.
- **Components:**
  - High-end inventory restock (bulk cosmetics, camera gear amortization, studio lighting).
  - Marketing & customer acquisition (Meta/Google Ads, portfolio photo shoots, influencer endorsements).
  - Studio rent, electricity, water, internet, and sanitization/maintenance.
  - Software subscriptions (cloud storage, invoicing, design tools).
- **Control Gate:** Cap total monthly Opex at 25%–30% of average monthly revenue.

---

## 4. Standard 6-Worksheet Architecture (Excel / Sheets Blueprint)

When delivering an automated financial spreadsheet for service/creative businesses, implement these 6 interconnected sheets:

### Sheet 1: `Dashboard` (Executive Cockpit)
- **Metric Cards:**
  - *Total Omset (Booked):* `=SUMIF(Registrasi_Klien!$K$5:$K$50, "<>6. Batal (Cancelled)", Registrasi_Klien!$N$5:$N$50)`
  - *Kas Masuk Riil (Verified):* `=SUMIF(Transaksi_Pendapatan!$I$5:$I$100, "Verified", Transaksi_Pendapatan!$F$5:$F$100)`
  - *Sisa Piutang (AR):* `=SUMIF(Registrasi_Klien!$K$5:$K$50, "<>6. Batal (Cancelled)", Registrasi_Klien!$P$5:$P$50)`
  - *Total Pengeluaran:* `=SUMIF(Pengeluaran_Operasional!$J$5:$J$100, "Approved", Pengeluaran_Operasional!$G$5:$G$100)`
  - *Estimasi Laba Bersih Operasional:* `=[Kas Masuk] - [Total Pengeluaran]`
- **Liquidity Ledger:** Breakdown of cash balances across physical petty cash and business bank accounts (BCA, Mandiri).
- **H-7 Watchlist Table:** Filtered list of upcoming events occurring within `< TODAY() + 7` that have remaining receivables.

### Sheet 2: `Registrasi_Klien` (Master Pipeline & AR Ledger)
- **Fields:** `ID_Booking`, `Tgl_Booking`, `Nama_Klien`, `WhatsApp`, `Kode_Paket`, `Nama_Paket`, `Tgl_Acara`, `Waktu_Standby`, `Lokasi_Venue`, `Zonasi`, `Status_Pipeline`, `Harga_Paket`, `Total_Addons`, `Total_Kontrak`, `Total_Terbayar`, `Sisa_Piutang`, `Status_Pelunasan`, `Alert_Jatuh_Tempo`, `Catatan`.
- **Core Formulas:**
  - *Nama Paket:* `=IFERROR(VLOOKUP(E5, Master_Data!$A$6:$F$12, 2, FALSE), "-")`
  - *Harga Paket:* `=IFERROR(VLOOKUP(E5, Master_Data!$A$6:$F$12, 4, FALSE), 0)`
  - *Total Kontrak:* `=Harga_Paket + Total_Addons`
  - *Total Terbayar:* `=SUMIFS(Transaksi_Pendapatan!$F$5:$F$100, Transaksi_Pendapatan!$C$5:$C$100, A5, Transaksi_Pendapatan!$I$5:$I$100, "Verified")`
  - *Sisa Piutang:* `=IF(Status_Pipeline="6. Batal (Cancelled)", 0, MAX(0, Total_Kontrak - Total_Terbayar))`
  - *Status Pelunasan:* `=IF(Sisa_Piutang<=0, "LUNAS", IF(Total_Terbayar>0, "SEBAGIAN (BELUM LUNAS)", "BELUM BAYAR"))`
  - *Alert Jatuh Tempo:* `=IF(Status_Pelunasan="LUNAS", "AMAN (LUNAS)", IF(Tgl_Acara < TODAY(), "OVERDUE (LEWAT)", IF(Tgl_Acara <= TODAY()+7, "URGENT (< H-7)", "NORMAL")))`

### Sheet 3: `Transaksi_Pendapatan` (Cash Inflows)
- **Fields:** `ID_Transaksi`, `Tgl_Transaksi`, `ID_Booking`, `Nama_Klien`, `Termin_Bayar`, `Nominal_Masuk`, `Akun_Tujuan`, `No_Ref_Transfer`, `Status_Verifikasi`, `Verifikator`, `Keterangan`.
- Client name auto-populates via `=IFERROR(VLOOKUP(C5, Registrasi_Klien!$A$5:$C$50, 3, FALSE), "-")`.
- Only records with `Status_Verifikasi = "Verified"` feed into revenue totals.

### Sheet 4: `Pengeluaran_Operasional` (Cash Outflows & COGS)
- **Fields:** `ID_Pengeluaran`, `Tgl_Pengeluaran`, `Kategori_Biaya`, `Subkategori`, `ID_Booking_Ref`, `Deskripsi_Biaya`, `Nominal_Keluar`, `Sumber_Dana`, `No_Bukti_Nota`, `Status_Approval`, `Penanggung_Jawab`.
- Separates COGS (`ID_Booking_Ref != "-"`) from Opex (`ID_Booking_Ref = "-"`).
- Only records with `Status_Approval = "Approved"` feed into outflow totals.

### Sheet 5: `Arus_Kas` (Monthly Cashflow Statement)
- Section A: Inflows by milestone type (DP1, Termin 2, Final, Add-on).
- Section B1: Project COGS (Assistants, Specialists, Travel, Consumables).
- Section B2: Studio Opex (Cosmetics/Gear Restock, Ads, Rent, Utilities).
- Net Cash Flow: `= Total_Inflows - (Subtotal_COGS + Subtotal_Opex)`.
- Section D: Bank Reconciliation: `Beginning Balance + Net Cash Flow = Theoretical Ending Balance`. Must equal physical bank balance (`Variance = Rp 0`).

### Sheet 6: `Master_Data` (Catalog & Account Master)
- Master price list of packages, standard add-on rates, and official receiving bank accounts. Prevents manual typos and pricing drift.

---

## 5. Internal Controls & Fraud Prevention Checklist

When delivering bookkeeping systems to service founders, mandate these 4 operational invariants:

1. **Strict Business Account Separation:**
   - Invoices must display registered business accounts only. Never route client payments to personal bank accounts.
2. **Dual-Check Credit Verification ("No Screenshot-Only Trust"):**
   - Admin staff must never mark payments `Verified` based on client transfer screenshots alone (prone to spoofed e-wallet images or scheduled transfers that were cancelled). Admin must verify cleared credit in online banking.
3. **Signed Field Add-on Vouchers:**
   - Extra service hours, additional family makeups, or overtime requested onsite must be signed by the event representative/organizer on a duplicate voucher before execution.
4. **Weekly Monday Bank Reconciliation (Bank Opname):**
   - Every Monday morning, compare the spreadsheet liquidity ledger against live banking apps. Any variance must be traced and resolved within 24 hours.

---

## 6. Companion Deliverable Guidelines

When fulfilling user requests for business bookkeeping:
- **Always provide a real working spreadsheet (`.xlsx`)** generated via Python `openpyxl` with styled headers (Navy/Rose/Gold palettes), zebra-striped rows, explicit number formatting (`Rp #,##0`), and working uppercase Excel formulas.
- **Provide a 2-page A4 companion SOP guide (`.pdf`)** summarizing payment stages, cancellation policies, unit economics, and cashflow management rules.
- **Companion Web Application Alternative (Interactive Dashboard):** When users find spreadsheet navigation daunting or confusing ("agak bingung"), deliver a lightweight client-side Single Page Application (SPA) dashboard (`index.html`) containing:
  1. Executive KPI Scorecard (Omset, Real Cash Inflow, Receivables, Opex, Net Profit).
  2. Multi-Account Liquidity Ledger (BCA, Mandiri, Studio Cash).
  3. Interactive H-7 Early Warning Watchlist with one-click WhatsApp billing reminder generator (`wa.me/?text=...`).
  4. Client-side JSON backup/restore (`exportDataJSON()` / `importDataJSON()`) so users never lose operational records.
- **Package deliverables into a single downloadable `.zip`** alongside direct file links for immediate deployment.

---

## 7. High-Turnover Walk-In Service Businesses (Barbershops, Salons, Reflexology)

For walk-in retail services operating on daily commission models rather than milestone bookings:
- Apply the daily per-staff commission formulation ($R_i \times P_i - K_i + T_i$) and shop share calculation ($R_i \times (1 - P_i)$).
- **Mandate Cash Drawer vs QRIS Reconciliation:** Reconcile cash register intake against staff daily cash payouts to detect whether the drawer has a net cash surplus to bank or a cash deficit requiring the owner to transfer funds to staff from QRIS receipts.
- **Retrospective Monthly Auditing & Executive PDF Reports:** When recalculating historical months under new commission splits (e.g., shifting to 60% per head), compile a 2-page executive statement (Page 1: KPI & P&L + Cash Reconciliation, Page 2: 31-Day Audit Journal) strictly omitting manual signature/stamp blocks per digital ERP standards.
- Detailed formulas, drawer settlement rules, 1-click WhatsApp closing templates, and retrospective 2-page PDF audit standards are documented in `references/daily-commission-and-drawer-reconciliation.md`.
