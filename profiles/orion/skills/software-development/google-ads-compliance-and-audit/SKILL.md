---
name: google-ads-compliance-and-audit
description: Use when auditing sites for Google Ads or campaign review.
category: software-development
tags:
  - google-ads
  - adsense
  - landing-page-audit
  - policy-compliance
  - better-ads-standards
  - ymyl-financial-services
  - adsbot-crawler
  - personal-loans-disclosure
---

# Google Ads Compliance & Landing Page Audit Protocol

Standardized operational workflow for auditing websites, landing pages, and ad creatives prior to launching Google Ads campaigns or applying for Google AdSense monetization. Prevents ad disapprovals, policy violations, and account suspensions.

---

## 7-Stage Pre-Flight Compliance Workflow

### Stage 1: Pre-Ad Technical & UX Audit
Audit the target website thoroughly across desktop (1280px+) and mobile (360px–390px) viewports before configuring any campaign.

1. **Responsiveness & Zero Layout Shift**:
   - Verify `document.documentElement.scrollWidth === document.documentElement.clientWidth` on mobile screens to ensure zero horizontal scrollbars or clipping.
   - PageSpeed score must exceed 90+ with Core Web Vitals (LCP < 2.5s, CLS < 0.1).
2. **Zero Broken Links**:
   - Crawl internal links across all navigation menus, footers, and in-body links. Every page must return `HTTP 200 OK`.
3. **Zero Leaked Template Comments & Clean DOM Tree (No Naked Debug Text Nodes)**:
   - When migrating or batch-converting HTML templates, ensure comment tags (`<!-- ... -->`) did not lose their comment delimiters. Unescaped comments become raw `NavigableString` text nodes that render visibly in the browser (e.g. naked "Footer" above dark footers, "Navbar" or "Header" below menus, "Lead Paragraph" above articles).
   - Run an AST-level DOM scan (BeautifulSoup) across all site HTML files checking for naked text strings whose direct parent is a block container (`body`, `main`, `div`) without typographic tags (`p`, `span`, `h1`–`h6`, `li`, `td`). Google Ads reviewers and automated crawler heuristics flag leaked template labels as "Site under construction / broken formatting / low quality site".
4. **Better Ads Standards Enforcement**:
   - Eliminate aggressive floating pop-ups, modals, or newsletter overlays that obscure main content upon arrival.
   - Eliminate automatic redirects (`window.location` jumps) and interstitial loading delays.
   - Eliminate video/audio `autoplay` with sound enabled.
   - Preserve natural browser history navigation; never trap the user with back-button redirection scripts.
5. **Mandatory Transparency Pages**:
   - **Contact (`/kontak.html`)**: Must list a verifiable physical operational office address, official editorial email (`mailto:`), dedicated partnership email, customer phone number (`tel:`), WhatsApp service, and explicit response SLA (e.g., 1x24 business hours).
   - **About Us (`/tentang-kami.html`)**: Clear organizational mission, editorial standards, author/researcher credentials, and E-E-A-T background.
   - **Privacy Policy (`/kebijakan-privasi.html`)**: Compliant with local privacy laws (e.g., UU PDP) and explicit Google AdSense / DART cookie disclosure with opt-out mechanisms.
   - **Legal Disclaimer (`/disclaimer.html`)**: Explicit declaration of independence, stating the portal is an educational publisher and NOT a lender, creditor, or financial broker.
6. **HTTPS & TLS Verification**:
   - Ensure a valid SSL certificate (TLS 1.2/1.3) with automatic HTTP-to-HTTPS 301 redirection and HSTS headers.

---

### Stage 2: Crawler & Bot Accessibility Verification
Ensure Google's automated policy review crawlers have unrestricted access to all assets and landing pages.

1. **Explicit `robots.txt` Permissions**:
   Configure `/robots.txt` at the web root to explicitly permit Google ad crawlers:
   ```text
   User-agent: Googlebot
   Allow: /

   User-agent: AdsBot-Google
   Allow: /

   User-agent: AdsBot-Google-Mobile
   Allow: /

   User-agent: Mediapartners-Google
   Allow: /

   User-agent: *
   Allow: /

   Sitemap: https://yourdomain.com/sitemap.xml
   ```
2. **Authorized Digital Sellers (`ads.txt`)**:
   Deploy an `ads.txt` file at the root domain returning `HTTP 200 OK` (prevent 404 responses during ad verification crawls).
3. **WAF & Anti-Bot Whitelisting**:
   Ensure web application firewalls (Cloudflare, LiteSpeed, ModSecurity) do not challenge or block Googlebot IP ranges (AS15169) with CAPTCHA or Turnstile.

---

### Stage 3: Landing Page & Ad Congruence (1-to-1 Mapping)
Every distinct ad group must resolve to a dedicated landing page that exactly mirrors the promoted proposition.

1. **Topic Alignment**:
   - If the ad highlights "OJK Legality Directory", the destination page must feature the searchable database directly above the fold.
   - If the ad highlights "Loan Interest Calculator", the landing page must immediately provide the calculation engine.
2. **Commercial & Promotional Consistency**:
   - Any numerical claim stated in ad copy (interest rates, pricing, cashback, fees) must be prominently displayed and substantiated on the landing page.
   - Never send traffic to generic homepage aggregators or unrelated blog indices.

---

### Stage 4: Business Category & Policy Center Clearance
Identify whether the business falls into Google Ads Restricted Categories (Financial Products, Healthcare, Gambling, Adult).

1. **Entity Classification for Media & Portals**:
   - Portals reviewing financial products or fintechs must register their Google Ads profile as **News & Education Publisher**, not as an unlicensed financial institution or money lender.
2. **Google Financial Services / Personal Loans Compliance**:
   When reviewing, comparing, or hosting content about personal loans (e.g., KTA, P2P lending):
   - **Minimum & Maximum Repayment Terms**: Repayment period must be $\ge 60$ days (strictly avoid payday loans / tenor $< 60$ days which trigger immediate global bans).
   - **Maximum Annual Percentage Rate (APR)**: Must explicitly state the maximum annual interest rate (e.g., APR 24%–48%).
   - **Representative Loan Example**: Must provide a clear representative calculation table detailing principal, loan term, monthly installment, upfront administration fees, and total repayment amount.
3. **Trademark & Fair Use Clauses**:
   Include a clear trademark attribution clause in the disclaimer stating that company and brand names belong to their respective owners and are cited under nominative fair use for independent news reporting.

---

### Stage 5: Clean Ad Copy Construction (RSA Standards)
Draft Responsive Search Ads (RSA) adhering strictly to Google Editorial Guidelines:

1. **Prohibited Stylistic Patterns**:
   - **No Excessive Capitalization**: Avoid "CEK DISINI SEKARANG" (use clean Title Case or Sentence Case).
   - **No Punctuation Abuse**: Never use repeated exclamation marks (e.g., "Klik Sekarang!!!").
   - **No Gimmicky Characters**: Avoid unapproved symbols, emoticons, or spacing hacks.
   - **Zero Typographical Errors**: Verify grammar and syntax thoroughly.
2. **Prohibited Unsubstantiated Claims**:
   - Never claim "Nomor 1 di Indonesia", "Pasti Cair 100%", "Tanpa Bunga Selamanya", or "Bebas Risiko" without independent, cited audit evidence.
3. **URL Integrity**:
   - Ensure **Final URL** matches the destination page exactly (including trailing slash or `.html` extensions).
   - **Display URL** must use the exact domain of the Final URL.

---

### Stage 6: Policy Manager Submission & Appeal Discipline
1. **Initial Submission**:
   Submit ad creatives and monitor the **Google Ads &rarr; Tools & Settings &rarr; Policy Manager** dashboard.
2. **Review Window**:
   Allow 24 to 48 hours for automated crawler bots (`AdsBot-Google`) to complete landing page evaluations.
3. **Disapproval Handling**:
   - Identify the exact policy violation code cited in the Policy Manager.
   - Inspect the landing page DOM to eliminate the offending string, asset, or broken script.
   - Verify the landing page with headless browser probes.
   - Submit an appeal **only once** after root cause remediation has been confirmed on the live server. Avoid premature repeated appeals.

---

### Stage 7: Routine Re-Audit & Automated Monitoring
Google continuously re-crawls active ads and landing pages. Maintain operational hygiene to prevent unexpected retro-disapprovals:

1. **Automated Status Probes**:
   Run scheduled status probes verifying that all promotional landing pages return `HTTP 200 OK` and mobile viewports remain uncorrupted.
2. **Content Change Gate**:
   When updating portal templates or publishing new articles, run regression checks ensuring that global navigation, footer transparency links, and `robots.txt` rules remain intact.

---

## Practical Pitfalls & Hard Constraints

- **Never omit physical office address or direct phone in Contact**: Google Ads human reviewers and automated quality bots flag landing pages as untrustworthy (*Untrustworthy / Deceptive Content*) when only a web form or anonymous email is provided.
- **Never cloak or serve dynamic content based on User-Agent**: If `AdsBot-Google` detects a different page structure or redirected content compared to a normal browser, the domain receives a permanent circumvention ban (*Circumventing Systems*).
- **Never publish payday loan promotions under 60 days**: Promising cash loans payable in 7, 14, or 30 days is an automated trigger for immediate policy rejection under Google Personal Loans Policy.
- **Never use unverified superlatives in headlines**: Phrases like "Platform Terbaik" or "Dijamin Resmi" must be replaced with factual, descriptive language like "Direktori Berizin OJK" or "Simulasi Perhitungan Suku Bunga".
