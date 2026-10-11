# Google Ads & AdSense Compliance Audit Protocol

Pre-flight compliance workflow for auditing websites, landing pages, and ad creatives prior to launching Google Ads campaigns or applying for Google AdSense monetization on YMYL financial portals.

---

## 7-Stage Pre-Flight Compliance Workflow

### Stage 1: Pre-Ad Technical & UX Audit
Audit target websites across desktop (1280px+) and mobile (360px–390px) viewports before configuring any campaign:
1. **Responsiveness & Zero Layout Shift**: Verify `document.documentElement.scrollWidth === document.documentElement.clientWidth` on mobile screens. PageSpeed score 90+ with Core Web Vitals (LCP < 2.5s, CLS < 0.1).
2. **Zero Broken Links**: Crawl internal links across navigation menus, footers, and in-body links. Every page must return `HTTP 200 OK`.
3. **Clean DOM Tree (No Naked Debug Text Nodes)**: Ensure comment tags (`<!-- ... -->`) did not lose comment delimiters. Unescaped comments become visible text nodes that automated crawlers flag as "low quality site / broken formatting".
4. **Better Ads Standards Enforcement**: Eliminate aggressive pop-ups, modal overlays, automatic redirects, and video/audio autoplay with sound. Preserve natural browser history navigation; never trap the user with back-button redirects.
5. **Mandatory Transparency Pages**:
   - **Contact (`/kontak.html`)**: Physical office address, official editorial email (`mailto:`), phone (`tel:`), WhatsApp service, response SLA.
   - **About Us (`/tentang-kami.html`)**: Editorial standards, author/researcher credentials, and E-E-A-T background.
   - **Privacy Policy (`/kebijakan-privasi.html`)**: Compliant with local privacy laws and Google AdSense/DART cookie disclosure with opt-out mechanisms.
   - **Legal Disclaimer (`/disclaimer.html`)**: Explicit declaration that the portal is an educational publisher and NOT a lender, creditor, or financial broker.
6. **HTTPS & TLS Verification**: Valid SSL certificate (TLS 1.2/1.3) with HTTP-to-HTTPS 301 redirection and HSTS headers.

---

### Stage 2: Crawler & Bot Accessibility Verification
Ensure Google policy review crawlers have unrestricted access:
1. **Explicit `robots.txt` Permissions**: Allow `Googlebot`, `AdsBot-Google`, `AdsBot-Google-Mobile`, and `Mediapartners-Google` at the web root.
2. **Authorized Digital Sellers (`ads.txt`)**: Deploy `ads.txt` at root domain returning `HTTP 200 OK`.
3. **WAF & Anti-Bot Whitelisting**: Ensure Cloudflare/LiteSpeed firewalls do not challenge Googlebot IP ranges (AS15169) with CAPTCHA or Turnstile.

---

### Stage 3: Landing Page & Ad Congruence (1-to-1 Mapping)
Every distinct ad group must resolve to a dedicated landing page that exactly mirrors the promoted proposition:
1. **Topic Alignment**: Ad highlighting "OJK Legality Directory" must feature the searchable database directly above the fold.
2. **Commercial Consistency**: Numerical claims in ad copy (interest rates, pricing, cashback, fees) must be prominently displayed and substantiated on the landing page. Never send traffic to generic homepage aggregators.

---

### Stage 4: Business Category & Policy Center Clearance
1. **Entity Classification**: Register Google Ads profile as **News & Education Publisher**, not as an unlicensed financial institution or lender.
2. **Google Financial Services / Personal Loans Compliance**:
   - **Repayment Terms**: Repayment period must be $\ge 60$ days (avoid payday loans / tenor $< 60$ days which trigger global bans).
   - **Maximum APR**: Explicitly state the maximum annual interest rate (e.g., APR 24%–48%).
   - **Representative Loan Example**: Clear calculation table detailing principal, loan term, monthly installment, administration fees, and total repayment.
3. **Trademark & Fair Use Clauses**: State in disclaimer that company and brand names belong to their respective owners and are cited under nominative fair use for independent news reporting.

---

### Stage 5: Clean Ad Copy Construction (RSA Standards)
Adhere strictly to Google Editorial Guidelines:
- **No Excessive Capitalization**: Avoid "CEK DISINI SEKARANG" (use Title Case or Sentence Case).
- **No Punctuation Abuse**: Never use repeated exclamation marks ("Klik Sekarang!!!").
- **No Gimmicky Characters**: Avoid unapproved symbols, emoticons, or spacing hacks.
- **Prohibited Unsubstantiated Claims**: Never claim "Nomor 1 di Indonesia", "Pasti Cair 100%", "Tanpa Bunga Selamanya", or "Bebas Risiko" without independent cited audit evidence.
- **URL Integrity**: Final URL matches destination exactly (including trailing slash or `.html`).

---

### Stage 6: Policy Manager Submission & Appeal Discipline
1. Monitor Google Ads -> Tools & Settings -> Policy Manager dashboard. Allow 24–48 hours for automated crawler bots (`AdsBot-Google`).
2. Identify exact violation code, remediate the offending string/asset, verify with headless browser probes, and submit an appeal **only once** after root cause remediation is confirmed.

---

### Stage 7: Routine Re-Audit & Automated Monitoring
1. **Automated Status Probes**: Scheduled probes verifying promotional landing pages return `HTTP 200 OK` and mobile viewports remain uncorrupted.
2. **Content Change Gate**: Run regression checks ensuring global navigation, footer transparency links, and `robots.txt` rules remain intact on template updates.
