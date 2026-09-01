---
name: osint-phone-profiling
description: Use when profiling phone numbers, HLR, or caller identities.
version: 1.0.0
author: Orion Lead Red Teamer
license: MIT
metadata:
  hermes:
    tags: [osint, phone-lookup, hlr, profiling, digital-footprint, reconnaissance]
    category: research
---

# Phone Number OSINT & Digital Footprint Profiling

## When to Use

Use this skill when:
1. Performing authorized open-source intelligence (OSINT), threat actor profiling, fraud verification, or digital footprint tracing on phone numbers (specifically Indonesian and international MSISDN).
2. Investigating caller identity, provider network details (HLR), and payment/e-wallet associations.
3. Formulating active vs. passive verification roadmaps for identity resolution.

---

## 1. Multi-Tiered Phone Profiling Framework

Phone profiling follows a 3-stage progressive information-gathering ladder:

```
[Tier 1: Passive HLR & Carrier Data]
               │
               ▼
[Tier 2: Public Footprint, Dorking & Breach Intel]
               │
               ▼
[Tier 3: E-Wallet, Messaging & Identity Correlation]
```

---

## 2. Tier 1: HLR Lookup & Telecommunication Routing

Home Location Register (HLR) determines the original issuing operator, brand, and geographic region of SIM card batch issuance (note: HLR indicates registration distribution, not real-time GPS).

### Indonesian Numbering Plan Reference:
| Prefix Range | Telecommunication Provider | Common Regional Hubs |
| :--- | :--- | :--- |
| `0811`, `0812`, `0813`, `0821`, `0822`, `0852`, `0853` | Telkomsel (Halo, simpATI, AS) | Nationwide |
| `0814`, `0815`, `0816`, `0855`, `0856`, `0857`, `0858` | Indosat Ooredoo Hutchison (IM3) | `0857-1x`: Jabodetabek/West Java |
| `0817`, `0818`, `0819`, `0859`, `0877`, `0878` | XL Axiata | Java / Bali / Sumatra |
| `0831`, `0832`, `0833`, `0838` | AXIS (XL Axiata) | Nationwide |
| `0895`, `0896`, `0897`, `0898`, `0899` | Tri (IOH) | Nationwide |
| `0881`, `0882`, `0883`, `0884`, `0885`, `0886`, `0887`, `0888`, `0889` | Smartfren (CDMA/LTE) | Major Urban Centers |

---

## 3. Tier 2: Search Engine Dorking & Fraud Blacklist Scanning

Search across multiple permutation formats to catch unindexed forum posts, marketplace listings, or fraud reports:

```bash
# Query Permutations for target numbers:
"085719391268" OR "0857-1939-1268" OR "6285719391268" OR "+6285719391268" OR "0857 1939 1268"
```

### Key Target Platforms:
- **Fraud Databases**: Kredibel.co.id, Lapor.go.id, CekRekening.id.
- **Classifieds & Marketplaces**: OLX, Carousell, Tokopedia/Shopee seller forums, Facebook Marketplace archives.
- **Social Media Archives**: Pastebin, GitHub gists, Telegram public channel logs.

---

## 4. Tier 3: Verified Identity Enumeration Paths

When public search engines yield zero matches, apply targeted verification vectors:

### A. E-Wallet Name Enumeration (Verified KTP/KYC Name Preview)
Payment gateways and banking endpoints display verified account names prior to transaction confirmation:
- Transfer inquiry on **DANA, GoPay, OVO, ShopeePay, LinkAja**.
- Interbank Virtual Account transfer check.
- *Mechanism:* System queries account holder name from central switch and presents masked or full KYC name.

### B. Global Caller ID & Crowdsourced Tagging
- **Getcontact / Truecaller / Sync.me**: Query crowdsourced address book tags to establish:
  - Personal nicknames.
  - Work affiliation / office name.
  - Reputation flags (e.g. "Penipu", "Spam", "Kurir").

### C. Direct Messaging Probing
- **WhatsApp Web / API Direct Link**: `https://wa.me/<international_number>`
  - Inspect profile picture (reverse image search via Yandex/Google Lens).
  - Inspect status bio and business profile catalog.
- **Telegram Contact Import**: Add number to disposable contact list to resolve Telegram User ID, display name, and @username.

---

## 5. Technical Limitations & Boundaries

1. **Real-time GPS Tracking**:
   - Carrier-grade real-time triangulation requires lawful intercept access (SS7/Diameter network signaling or direct BTS telco logs).
   - Without telco access, real-time location can only be acquired via interactive tracking mechanisms (e.g. tokenized canary links / IP loggers requiring the target to open a URL).
2. **Privacy & Reporting**:
   - Always present OSINT findings factually with confidence levels (Confirmed KYC vs Crowdsourced Tag vs Inferred Region).
