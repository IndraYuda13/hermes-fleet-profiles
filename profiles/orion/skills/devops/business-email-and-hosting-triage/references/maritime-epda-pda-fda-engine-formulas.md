# Maritime Port Disbursement Account (EPDA/PDA/FDA) Mathematical Engine

This reference details the official calculation structure, mathematical formulas, and invoicing schema for Indonesian port agency disbursements (e.g. PT. Berlian Global Maritim operations across Bahodopi, Lubuk Tutung, Taboneo, Muara Berau).

## 1. Input Parameters Schema

| Parameter | Symbol | Data Type | Example Value | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Vessel Name** | `vessel_name` | string | "MV PROPEL TBN" | Vessel identification |
| **Charterer / Principal** | `principal` | string | "SINAR NUSANTARA" | Invoiced party / Messrs |
| **Port / Terminal** | `port_name` | string | "BAHADOPI" | Port of call |
| **Estimated Time of Arrival** | `eta` | date/string | "3-Sep-2026" | Arrival timeline |
| **Gross Register Tonnage** | `GRT` | float | 22698 | Volume/tonnage rating |
| **Summer Deadweight** | `DWT` | float | 37504 | Cargo carrying capacity (MT) |
| **Length Overall** | `LOA` | float | 177.85 | Total vessel length (meters) |
| **Cargo Nature & Tonnage** | `cargo_desc`, `cargo_mt` | string, float | "STEEL BILLETS", 30000 | Metric tons loaded/discharged |
| **Port Stay Duration** | `days` | int | 3 | Berthing/quay stay days |
| **Crew Complement** | `crew_count` | int | 21 | Number of crew for health check |

## 2. Mathematical Tariff Invariants & Formulas

### A. Subtotal A: VAT-able Port Expenses (Subject to 11% PPN)
1. **Quay Dues (Uang Dermaga):**
   $$\text{Quay Dues} = \text{GRT} \times 0.10 \times \text{Days}$$
   *Example:* $22,698 \times 0.10 \times 3 = \$6,809.40$

2. **Pilotage (Jasa Pandu - 4 Movements):**
   Standard calling cycle requires 4 distinct pilot movements:
   - Movement 1: Inward (to Terminal Anchor)
   - Movement 2: Anchor to Berth
   - Movement 3: Berth to Anchor
   - Movement 4: Anchor to Departure
   Each movement formula:
   $$\text{Pilotage}_{\text{move}} = (\text{GRT} \times 0.06) + 139.60$$
   *Example per move:* $(22,698 \times 0.06) + 139.60 = \$1,501.48$
   $$\text{Pilotage}_{\text{total}} = 4 \times \text{Pilotage}_{\text{move}} = 4 \times 1,501.48 = \$6,005.92$$

3. **Towage (Jasa Tunda Kapal - 2 Movements):**
   Required for berthing and unberthing maneuvers (2 movements):
   $$\text{Towage} = [(\text{GRT} \times 0.10) + 2600.00] \times 2$$
   *Example:* $[(22,698 \times 0.10) + 2600.00] \times 2 = [2269.80 + 2600.00] \times 2 = \$9,739.60$

4. **Subtotal A Calculation:**
   $$\text{Subtotal A} = \text{Quay Dues} + \text{Pilotage}_{\text{total}} + \text{Towage}$$
   *Example:* $6,809.40 + 6,005.92 + 9,739.60 = \$22,554.92$

5. **VAT 11% (PPN):**
   $$\text{VAT}_{11} = \text{Subtotal A} \times 0.11$$
   *Example:* $22,554.92 \times 0.11 = \$2,481.04$

---

### B. Non-VAT Port Expenses (PNBP, Permits & Operational Logistics)
6. **Port Supervision (Dry Cargo):**
   $$\text{Supervision} = \text{Cargo MT} \times 0.00179$$
   *Example:* $30,000 \times 0.00179 = \$53.70$

7. **Harbour Dues (Uang Labuh 1st 15 Days):**
   $$\text{Harbour Dues} = \text{GRT} \times 0.045$$
   *Example:* $22,698 \times 0.045 = \$1,021.41$

8. **Light Dues (Uang Rambu Navigasi):**
   $$\text{Light Dues} = \text{GRT} \times 0.034$$
   *Example:* $22,698 \times 0.034 = \$771.73$

9. **Fixed Government Permits & Service Charges:**
   - **Shifting Permit:** Fixed $\$5,500.00$
   - **State Income Non-Tax (Seacom Permit PKKA):** Fixed $\$350.00$
   - **Boat Hire for Quarantine Inspection at Anchorage:** Fixed $\$500.00$
   - **Sundries (Miscellaneous / Operational Contingencies):** Fixed $\$1,050.00$

10. **Total Component 1 (Port Expenses):**
    $$\text{Component 1} = \text{Subtotal A} + \text{VAT}_{11} + \sum \text{Non-VAT Expenses}$$
    *Example:* $22,554.92 + 2,481.04 + (53.70 + 1,021.41 + 771.73 + 5,500 + 350 + 500 + 1,050) = \$34,282.80$

---

### C. Component 2: Agency Remuneration & Formalities
11. **Port Clearance In/Out & Operations:** Fixed Lumpsum $\$6,500.00$
12. **Agency Fee:** Fixed $\$1,500.00$
13. **Total Component 2:**
    $$\text{Component 2} = \$6,500.00 + \$1,500.00 = \$8,000.00$$

---

### D. Component 3: Vessel Expenses / Owner Account
14. **RT Swab Antigen / Health Inspection:**
    $$\text{Swab Fee} = \text{Rate per Crew} \times \text{Crew Count} = \$45.00 \times 21 = \$945.00$$
15. **Total Component 3:**
    $$\text{Component 3} = \$945.00$$

---

### E. Grand Total Consolidation
$$\text{Grand Total} = \text{Component 1} + \text{Component 2} + \text{Component 3}$$
*Example:* $\$34,282.80 + \$8,000.00 + \$945.00 = \mathbf{\$43,227.80\text{ USD}}$

---

## 3. Standard Invoicing & Remittance Schema

```json
{
  "bank_details": {
    "account_no": "125-00-6660778-9 (USD)",
    "account_title": "USD Account",
    "swift_code": "BMRIIDJA",
    "bank_name": "Bank Mandiri (Persero) Tbk.",
    "branch": "KCP Jakarta Kelapa Gading",
    "bank_address": "Jl. Boulevard Raya Blok TB2 No. 6-8, Kelapa Gading, Jakarta Utara 14240",
    "beneficiary": "PT. Berlian Global Maritim",
    "legal_address": "Jl. Cicarawa 3 Blok H2/6, Kel Sukapura, Kec Cilincing, Jakarta Utara 14140, Indonesia"
  },
  "head_office": {
    "address": "The Kensington Office Tower, Lt. 1 Unit E, Kelapa Gading Timur, Jakarta Utara, 14240, Indonesia",
    "phone": "+62 21 3973 6967",
    "email": "agency@bg-maritim.com; accounts@bg-maritim.com; alian@bg-maritim.com",
    "website": "www.berlianglobalmaritim.com"
  }
}
```

## 4. Reusable Algorithm Implementation (Python)

```python
def calculate_epda(grt: float, days: int, cargo_mt: float, crew_count: int,
                   agency_fee: float = 1500.0, clearance_fee: float = 6500.0) -> dict:
    # 1. VAT-able items
    quay_dues = grt * 0.10 * days
    pilotage_per_move = (grt * 0.06) + 139.60
    pilotage_total = pilotage_per_move * 4
    towage = ((grt * 0.10) + 2600.00) * 2
    
    subtotal_a = quay_dues + pilotage_total + towage
    vat_11 = subtotal_a * 0.11

    # 2. Non-VAT items
    supervision = cargo_mt * 0.00179
    harbour_dues = grt * 0.045
    light_dues = grt * 0.034
    fixed_permits = 5500.00 + 350.00 + 500.00 + 1050.00
    
    port_expenses_non_vat = supervision + harbour_dues + light_dues + fixed_permits
    component_1 = subtotal_a + vat_11 + port_expenses_non_vat

    # 3. Agency & Clearance
    component_2 = clearance_fee + agency_fee

    # 4. Vessel Expenses
    component_3 = 45.00 * crew_count

    # 5. Grand Total
    grand_total = component_1 + component_2 + component_3

    return {
        "subtotal_a_vatable": round(subtotal_a, 2),
        "vat_11": round(vat_11, 2),
        "component_1_port_expenses": round(component_1, 2),
        "component_2_agency_clearance": round(component_2, 2),
        "component_3_vessel_expenses": round(component_3, 2),
        "grand_total_usd": round(grand_total, 2)
    }
```

## 5. Single-Page A4 Print & Client-Side PDF Generation Invariant

When rendering EPDA documents in web applications for international shipowners:
1. **Strict 1-Page A4 Geometry (Zero Spillover Invariant):**
   - Standard A4 viewport dimensions: $210\text{ mm} \times 297\text{ mm}$ (exactly $794\text{ px} \times 1123\text{ px}$ at 96 DPI).
   - If document height exceeds 1123px by even a few pixels, browser print engines trigger an unformatted 2-page printout with orphan footer rows, degrading professional credibility.
   - Design Invariants:
     - Outer sheet padding: `8mm 12mm`.
     - Base font size: `8.5pt` (`7.8pt` in cost table cells).
     - Cell padding: `2.5px 5px`.
     - Header logo height: max `45px - 50px`.
     - Bank details & signature block height: max `120px`.
2. **Dual PDF Export Pipeline:**
   - *Pipeline A (Direct Client-Side Canvas via `html2pdf.js`):* Uses `html2pdf().set({ margin: [6, 8, 6, 8], filename: 'EPDA_<VESSEL>_<PORT>_BGM.pdf', image: { type: 'jpeg', quality: 0.98 }, html2canvas: { scale: 2, useCORS: true }, jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' } }).from(element).save()` for one-click file download.
   - *Pipeline B (Native Print Stylesheet Fallback):* Set `@media print { @page { size: A4 portrait; margin: 8mm 10mm; } .no-print { display: none !important; } }` so `window.print()` seamlessly prints or saves to PDF without UI panels.

## 6. Fast Email & WhatsApp Quotation Digest Schema

When principals request immediate preliminary cost indications before reviewing full PDF attachments, provide a concise plaintext digest:

```text
Dear Sir/Madam,

Good day.
Please find below the summary of our Estimated Port Disbursement Account (EPDA) for your vessel:

VESSEL PARTICULARS:
- Vessel Name   : <VESSEL_NAME>
- Port of Call  : <PORT_NAME>
- Cargo / Qty   : <CARGO_DESC_AND_TONNAGE>
- Est. Port Stay: <DAYS> Days

ESTIMATED COST BREAKDOWN:
1) Port & Official Dues : USD <COMPONENT_1_PORT_EXPENSES>
2) Agency & Clearance   : USD <COMPONENT_2_AGENCY_CLEARANCE>
3) Vessel / Crew Health : USD <COMPONENT_3_VESSEL_EXPENSES>
--------------------------------------------------
GRAND TOTAL (USD)       : USD <GRAND_TOTAL_USD>

*Full formal official EPDA in PDF format with complete tariff calculations and Mandiri USD remittance details is attached.
Should you require any further assistance, please do not hesitate to contact us.

Best regards,
Alian / Port Operations Desk
PT. BERLIAN GLOBAL MARITIM
The Kensington Office Tower, Kelapa Gading, Jakarta Utara
Email: agency@bg-maritim.com | Phone: +62 21 3973 6967
Website: www.bg-maritim.com
```

## 7. Strategic 9 Hubs Port Matrix & Cargo Profile Alignment

Disbursement models must align with the agency's official Company Profile operational hubs:

| Hub Code | Strategic Hub | Key Ports / Terminals Covered | Primary Cargo Niche | Typical Vessel Size (DWT / GRT) |
| :--- | :--- | :--- | :--- | :--- |
| `morowali` | **Morowali Hub** | Bahodopi, Morowali Industrial Park (IMIP) | Steel Billets, Nickel Ore, Ferro-Nickel | 35k–50k DWT / 20k–30k GRT |
| `balikpapan`| **Balikpapan Hub** | Lubuk Tutung (Kobexindo Jetty), Sangatta, Adang Bay, Bunati | Steam Coal, Metallurgical Coal | 50k–70k DWT / 35k–45k GRT |
| `taboneo` | **Taboneo Hub** | Taboneo Anchorage, Muara Berau STS Transshipment | Thermal Coal, Capesize/Panamax Bulk | 65k–180k DWT / 40k–95k GRT |
| `cigading` | **Cigading Hub** | Cigading Port, Ciwandan, Merak (Banten) | Clinker, Bulk Cement, Iron Sand | 40k–55k DWT / 25k–35k GRT |
| `dumai` | **Dumai Hub** | Dumai (Lubuk Gaung), Belawan (Sumatra) | Crude Palm Oil (CPO), Oleochemicals | 20k–35k DWT / 15k–25k GRT |
| `batam` | **Batam Hub** | Nipah Transit & STS Anchorage, Batu Ampar | Marine Bunkering (VLSFO), STS Oil | 15k–30k DWT / 10k–20k GRT |
| `gresik` | **Gresik Hub** | Gresik Port, Tanjung Perak, Lamongan Shorebase | Bulk Wheat, Chemical Fertilizer, Grain | 30k–45k DWT / 20k–28k GRT |
| `jakarta` | **Jakarta HQ** | Tanjung Priok Port, Marunda | Steel Plates, Heavy Lift, General Cargo | 20k–30k DWT / 14k–20k GRT |
| `manokwari` | **Manokwari Hub** | Manokwari (Maruni Cement Jetty, Papua Barat) | Cement Bags, Construction Minerals | 15k–25k DWT / 12k–18k GRT |

## 8. Typography & CSS Visual Authenticity Invariant

When building or styling maritime disbursement accounting interfaces:
1. **Monospace Accounting Grid:** Use `Consolas`, `Courier New`, or `IBM Plex Mono` for all data rows, calculations, and financial summaries. Proportional sans-serif fonts in data tables misalign decimal points and look like casual office memos rather than authentic port disbursement sheets.
2. **Explicit 4-Column Layout:** Cost schedules must strictly structure as:
   `[PARTICULARS] (Left) | [TARIFF / CALCULATION BASIS] (Center) | [AMOUNT USD] (Right) | [REMARKS] (Left)`
3. **Table Borders:** Apply complete 1px black borders (`border-collapse: collapse; border: 1px solid #000000;`) on all cells to replicate the traditional matrix format used by international disbursement auditors.
4. **Header Styling:** Group headings (e.g. `1) PORT EXPENSES`) must feature dark navy backgrounds (`#002060`) with bold white capital text, while sub-groups (`2) AGENCY FEE`, `3) VESSEL EXPENSES`) use slate gray (`#64748b`) with crisp contrast.

## 9. Interactive Split-Screen Architecture & Live Financial KPIs

When building an operator-facing digital EPDA generator:
1. **Split-Screen Workspace Layout:**
   - *Left Pane (500–540px, dark theme `#0d131f`):* Operational controls containing the 9 Company Profile Hub selector, accordion cards for Vessel Particulars, VAT-able Port Expenses, Non-VAT Government Charges, Agency Remuneration, and Crew Health Checks.
   - *Right Pane (Scrollable preview canvas `#05070d`):* Centered live A4 paper canvas (`210mm` width, `#ffffff` background) updating instantaneously as operators type.
2. **Top Executive KPI Bar (Instant Commercial Decision Support):**
   - Place 4 live metrics in the sticky application header:
     - **Estimasi Grand Total (USD):** Neon cyan highlight displaying the overall proforma disbursement total.
     - **Equivalent IDR (Kurs Mandiri):** Emerald green highlight converting USD to IDR at standard bank remittance exchange rate (e.g. Rp 16,500/USD).
     - **Port & Official Dues:** Pass-through costs payable to port authorities and government entities.
     - **Agency Margin:** Gross profit earned directly by the agency (Port clearance lumpsum + Agency fee), highlighted in amber gold.
3. **One-Click Corporate Alignment:**
   - Clicking any of the 9 operational hub buttons must immediately populate canonical vessel dimensions, typical commodity tonnages, and localized port charges without requiring manual tariff lookups.



