# Media Streaming Monetization, Identity Decoupling & Compliance Architecture

This reference documents the security, legal, compliance, and product UX guidelines for operating and monetizing third-party media streaming and scraped video platforms.

---

## 1. The Legal & Identity Exposure Trap

### A. ccTLD Identity Verification & Personal Liability
- In jurisdictions like Indonesia, ccTLDs such as `.my.id`, `.biz.id`, and `.id` are regulated by national domain registries (PANDI) that mandate real-name identity verification (NIK/KTP or verified local mobile number).
- Subdomains attached to personal vanity domains (e.g. `stream.domain.my.id`) directly bind video scraping, proxying, and streaming operations to the individual owner.
- While unmonetized personal hobby projects or streaming frontends generally face civil takedowns (DMCA) or administrative ISP DNS blocking (TrustPositif/Kominfo), the transition to **monetization** elevates the legal classification to **commercial copyright infringement**.
- **Statutory Risk (Indonesia UU Hak Cipta No. 28/2014 Pasal 113):**
  - Paragraph (3): Commercial infringement of economic rights is punishable by imprisonment up to 4 years and/or fines up to Rp 1,000,000,000.
  - Paragraph (4): Piracy for commercial gain carries up to 10 years imprisonment and/or fines up to Rp 4,000,000,000.
- **Decoupling Invariant:**
  - Before introducing any payment mechanism, tip button, or commercial link, decouple streaming services onto disposable offshore domains (`.to`, `.cc`, `.is`, `.top`) registered via privacy-preserving registrars (Njalla, Porkbun, Namecheap) using crypto/anonymous payments.
  - Proxy all origin traffic through Cloudflare or reverse proxy clusters to hide the backend VPS origin IP.

---

## 2. Payment Processors, Platform AUPs & KYC Freezes

### A. Domestic Payment Gateways (Midtrans, Xendit, Pakasir)
- Domestic payment gateways operate under central bank licenses (PJP Bank Indonesia). Their Acceptable Use Policies (AUP) explicitly prohibit businesses dealing in unauthorized copyright distribution, streaming scraping, or unlicensed media.
- Automated merchant web crawlers and compliance audits inspect merchant URLs during onboarding and upon transaction spikes.
- Violations trigger immediate account termination, permanent KYC blacklisting across merchant registries, and holding of settlement funds for 90 to 180 days to guard against chargebacks and fraud inquiries.

### B. Creator Tipping Platforms (Saweria, Trakteer)
- Even though marketed as casual creator tipping platforms, their underlying settlement rails rely on official PJP payment infrastructure.
- User/competitor reports or automated scans showing tips linked to VIP streaming passes or gated episodes lead to account bans.
- If tipping links are used:
  - Position contributions strictly as voluntary server upkeep/coffee gratuity.
  - Never label transactions as "Buy VIP Pass", "Unlock Episode", or "Streaming Access".

### C. Safe Low-Risk Alternative: Non-Custodial Cryptocurrency
- Provide non-custodial wallet addresses for crypto donations:
  - USDT on low-fee networks (Polygon, BSC, TRC20).
  - Privacy-preserving coins such as Monero (XMR).
- Self-host BTCPayServer if automated webhooks or invoice confirmations are required.
- Zero KYC requirements, zero risk of third-party account freezing, and zero domestic banking transaction trail.

---

## 3. Ad Network Hygiene vs Google Safe Browsing

### A. Pitfalls of Programmatic Pop-up / Pop-under Networks
- Common ad networks for anime/streaming sites (PopAds, PropellerAds, Adsterra) heavily distribute gambling (judi online / slot) and deceptive software installers in Southeast Asia.
- Distributing or transmitting online gambling materials violates **UU No. 1/2024 (Revisi UU ITE) Pasal 27 ayat (2)**, carrying up to 10 years imprisonment and Rp 10,000,000,000 in fines.
- Dynamic script cloaking often slips past network quality filters, redirecting mobile users to malicious landing pages, phishing forms, or fake browser update APKs.
- **Google Safe Browsing Red Screen:** Google actively crawls and blacklists domains serving deceptive redirects. The full-screen red warning ("Deceptive Site Ahead") results in an immediate >95% drop in user traffic.

### B. Recommended Alternative: Curated Direct Affiliate
- Maintain the platform's core competitive advantage ("moat"): an immaculate, dark-mode, ad-free Apple/Netflix minimal UI.
- Implement **Direct Curated Affiliate Cards**:
  - VPN Services (Surfshark, Mullvad, NordVPN): Highly relevant to streaming users needing to bypass ISP throttling or regional geo-blocks. VPN affiliate programs offer 40%–70% commissions.
  - Anime merchandise, figure retailers, or indie wibu apparel.
- Deliver affiliates as static native HTML/CSS UI cards with direct anchor tags (`<a href="..." rel="noopener sponsored">`). Zero external third-party JavaScript, zero risk of malicious hijacking, and 100% immune to Google Safe Browsing penalties.

---

## 4. Product Strategy: Supporter-Driven Utility Freemium

### A. The Core Principle
- **Never paywall the content itself.** Streaming 720p/1080p must remain free and frictionless without registration. This preserves organic viral growth and audience loyalty.
- **Monetize convenience and utility tools** that power users and anime fans value:
  1. **Batch Download to Telegram:** Integrate Telegram bot (e.g. `@Animestrbot`) to deliver an entire 12-episode season directly to a user's Telegram saved messages in one click.
  2. **Priority CDN Mirror:** Provide low-latency, dedicated routing during evening peak hours (19:00–22:00 WIB) when standard upstream CDN routes experience packet congestion.
  3. **Custom Player Customization & Badges:** Exclusive subtitle font styling, custom color accents, and supporter badges.
