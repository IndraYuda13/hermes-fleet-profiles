---
name: business-email-and-hosting-triage
description: Use when business email or hosting gets suspended or locked.
---

# Business Email & Hosting Operations Playbook

Use this skill when diagnosing, mitigating, or resolving domain email outages, provider-level outbound delivery suspensions (e.g. Hostinger, cPanel/WHM, Google Workspace, Microsoft 365), high-bounce rate lockouts, and legacy IT account ownership transfers.

## 1. Outbound Suspension Triage (Error 554 5.7.1)

### Root Cause Identification
- **Error Code:** `554 5.7.1 Outbound sending is disabled for this account`
- **Common Trigger:** Mass sending (e.g. logistics line-ups, marketing blasts, transactional statements) containing obsolete, typoed, or non-existent recipient addresses causing a spike in hard bounces (>5-10%).
- **Security Action by Host:** The mail server automatically suspends outgoing SMTP traffic to protect domain reputation and prevent IP blacklisting on Spamhaus/Barracuda. Incoming mail (IMAP/POP3) typically remains unaffected.

### Critical Immediate Pitfall: The Outbox Re-Trigger Trap
Before requesting an unsuspend or waiting for automatic cooldown:
1. **Purge the Client Outbox First:** User MUST inspect the local email client (Outlook, Thunderbird, Apple Mail) and immediately delete or move to Drafts the queued/unsent email blast that failed in the `Outbox` folder.
2. **Consequence of Neglect:** If the provider unsuspends the account while the corrupted queue remains in the local Outbox, the client will immediately attempt redelivery, re-triggering the bounce threshold and causing an instant re-suspension.

## 2. Hostinger-Specific Account Delegation & Support Rules

- **Account Sharing Limitation:** Hostinger allows delegating "Admin Access" to third parties. However, support policies strictly forbid security-level actions (unsuspending accounts, resetting abuse locks, domain transfers) requested by delegated accounts.
- **Master Owner Requirement:** Such actions require communication from the primary registrant/purchaser email (Master Account).
- **Automated Cooldown:** If the Master Account is unreachable, Hostinger's automated reputation filter typically releases outbound blocks within 6 to 24 hours, provided no further bounced traffic is generated.

## 3. Zero-Downtime Emergency Mitigation Workarounds

When the primary mailbox is suspended and the business cannot wait:

### Strategy A: Temporary Mailbox + Dual Account View (Fastest, 3 Minutes)
1. Do **NOT** delete the suspended mailbox. Deleting a mailbox deletes all server-side historical mail, sent items, and folders permanently.
2. Create a fresh temporary mailbox in the hosting panel (e.g. `commercial@domain.com` or `ops@domain.com`).
3. Set an automatic forwarder from `suspended@domain.com` -> `temporary@domain.com`.
4. Add the temporary account into the user's desktop client (Outlook) alongside the existing account:
   - Historical emails, attachments, and records remain accessible and searchable in the original profile.
   - Immediate outgoing communication resumes seamlessly through the new profile.

### Hostinger Live Chat Bypass (Bypassing AI Bot "Kodee")
When contacting Hostinger support through the web chat widget, the AI bot ("Kodee") will aggressively intercept and attempt to deflect tickets with generic articles:
1. Immediately type keyword triggers: `Bicara dengan agen manusia` or `Live agent please, transfer to human`.
2. If offered articles or suggested FAQs, explicitly reject them by selecting: `Bukan, saya masih butuh bantuan` or `Tidak membantu`.
3. Re-type: `Saya butuh agen manusia sekarang untuk unsuspend email server`.
4. After 2 rejections, the automated queue transfers to a human technical support agent.
5. In the opening message to the human agent, immediately state that the mailbox password has already been changed and client devices verified clean—this bypasses repetitive first-tier troubleshooting scripts.

### Strategy B: Full Archive Mirroring (Import Email)
1. Use the hosting provider's "Import Email" / IMAP sync utility in the control panel.
2. Source: `suspended@domain.com` (with freshly updated password).
3. Target: `temporary@domain.com`.
4. Complete historical mailboxes copy over in the background without affecting production integrity.

### Strategy C: Client-Side Offline Archival (.PST Export in Outlook)
Before any major mailbox migration or server-side intervention, create a durable local backup:
1. In Outlook: `File` -> `Open & Export` -> `Import/Export` -> `Export to a file` -> `Outlook Data File (.pst)`.
2. Select the top-level mailbox root (`account@domain.com`) and ensure **"Include subfolders" is checked**.
3. Save to local disk or external storage (e.g. `Backup_Email_Date.pst`).
4. Skip the password prompt (leave empty) for seamless offline restoration or cross-machine transfer.

### Strategy D: Unresponsive IT Legacy Account Escalation Protocol
When a former IT administrator holding the hosting master account (`Master Owner`) is unresponsive or refuses to cooperate:
1. **Never Cite Security Incidents in Chats:** When drafting WhatsApp requests for the user to send into corporate groups or directly to previous IT, frame the transfer strictly around standard ongoing maintenance, DNS configuration, and operational full-access requirements. Citing suspensions or security breaches creates unnecessary panic and defensive stonewalling.
2. **Operational Continuity First:** Immediately deploy Strategy A (fresh temporary mailbox + server-side forwarder + dual client configuration) so day-to-day business operations are zero-downtime while administrative negotiations occur.
3. **Legal Account Recovery Escalation:** If former IT remains permanently uncontactable, advise the business owners to initiate the provider's official account ownership claim (e.g. Hostinger Account Recovery) using corporate proof of payment (billing bank statements), business registration documents, and director identification. Providers have dedicated legal/abuse teams to re-assign master ownership away from personal accounts.

## 4. Communication Etiquette for WhatsApp Support & Internal Stakeholder Alignment
When drafting messages for users to communicate with company owners, legacy IT, or marketing colleagues:
- Avoid overly bureaucratic or rigid language ("Dengan hormat", long administrative preambles) in chat channels.
- Use natural, respectful, and clear messaging suitable for WhatsApp.
- Check and adapt honorifics to match the owner/stakeholder relationship (e.g. use 'Kak <Name>' instead of 'Pak' when requested).
- Frame credential/account transfers around technical necessity and operational efficiency, never assigning blame for existing incidents.
- When drafting internal requests to take over master accounts from former IT personnel, focus purely on maintenance/full-access requirements without citing active incidents or security panics.

### Non-Blaming Incident Explanations for Marketing Colleagues (RCA Framing)
When communicating mailbox suspensions to non-technical marketing staff who may fear being blamed or penalized:
1. **No-Blame Infrastructure Framing:** Attribute the suspension strictly to automated host-level heuristic sensors, burst traffic filters, and recipient deferral thresholds rather than operator error. Frame the incident as the company's marketing volume outgrowing basic mailbox infrastructure.
2. **Relatable Operational Analogy:** Use functional hardware analogies (e.g. standard shared webmail is a messenger scooter designed for single letters; forcing 50+ simultaneous recipients overloads the engine, whereas an enterprise ESP like Brevo is a licensed freight truck built for bulk delivery).
3. **Formal Corporate Memo Structure (Professional Tier):**
   - *Incident Resolution Status:* Open with confirmation that the account is restored/unsuspended.
   - *Root Cause Analysis (RCA):* State host-level technical mechanisms objectively (shared hosting burst filters, bounce thresholds).
   - *Separation of Channels:* Position the solution as an architectural upgrade (Broadcast Channel vs Deal Desk).
   - *Support & Enablement:* Close with an offer of hands-on simulation and tooling support.

## 5. Web Assets & Embedded Media Operations
See `references/youtube-embed-and-hero-carousel-invariants.md` for technical invariants on resolving YouTube embed Error 153 via Smart Facade Players, handling user-mandated inline autoplay/loop iframe syntax, and preventing initial black-screen hero background bugs on client landing pages.

## 6. Bulk Email Marketing Isolation & Dedicated ESP Migration Architecture

### The "New Mailbox on Same Domain" Anti-Pattern
When an account like `marketing@domain.com` is suspended for blast mailing, creating `commercial@domain.com` on the same shared hosting server (Hostinger, cPanel) will trigger an immediate repeat suspension:
1. **Domain & IP-Level Reputation:** Shared hosts monitor abuse heuristics per domain and per shared server IP, not just per username. Once one mailbox triggers an abuse threshold, the domain enters a high-scrutiny probationary state.
2. **Shared Hosting AUP Violations:** Shared hosting SMTP is engineered solely for low-volume 1-on-1 transactional and business correspondence (typically capped at 100–500 emails/day). Automated burst sending violates Acceptable Use Policies (AUP).
3. **Blacklist Catastrophe:** Continued blasting from shared hosting risks landing the domain on Spamhaus, SORBS, or Barracuda blacklists, which causes critical corporate emails (invoices, director correspondence) to land in client SPAM folders or bounce globally.

### Domain Isolation Protocol (Primary vs Outreach Domains)
1. **Primary Domain Sanctity (`domain.com`):** Strictly reserve for 1-to-1 operational and financial communications. Never blast marketing campaigns or cold lists from the primary corporate domain.
2. **Secondary Outreach Domains (`domain-commercial.com`, `domain-marketing.com`):** Purchase cheap lookalike domains for outbound campaigns and set HTTP 301 redirects to the main corporate website. If a marketing domain's reputation degrades, the core business domain remains entirely unaffected.
3. **Pre-Send List Hygiene:** Run recipient lists through verification tools (ZeroBounce, NeverBounce) before sending. Maintain hard bounce rates below 2% to prevent ESP account freezes.

### Dedicated ESP Offloading & DNS Authentication (Brevo / Sendinblue Alignment)
To send bulk campaigns as `commercial@domain.com` without tripping shared hosting limits or showing `via sendinblue.com` in Gmail:
1. **Offload Delivery:** Use a specialized bulk ESP (e.g. Brevo free tier: 300 emails/day; Amazon SES, Mailgun, or MailerLite).
2. **DKIM & Domain Authentication:** In DNS (cPanel Zone Editor or Hostinger DNS), publish the ESP's verification code and custom DKIM records. This cryptographically proves domain ownership, satisfies strict DMARC (`p=quarantine` / `p=reject`), and strips the "via" third-party header in recipient mailboxes.
3. **Reply-To Routing:** Configure the ESP sender's `Reply-To` address to the corporate webmail mailbox (`commercial@domain.com`). Outbound traffic leaves via ESP IP pools, while incoming client replies flow directly to the hosting IMAP inbox.

### Brevo Modern UI & cPanel DNS Provisioning Playbook
In modern Brevo UI, domain and sender settings are housed under account settings, not the primary left sidebar:
1. **Navigate to Domains:** Click the **Account / Organization Dropdown** in the top-right corner (`[Account Name] ∨` or gear icon `⚙`) -> select **Settings** -> open **Senders, Domains & Dedicated IPs** -> select the **Domains** tab -> click **Add a domain**.
2. **Authentication Method:** Select **"Authenticate the domain yourself"** -> click **Save and authenticate**.
3. **Record Type Alignment (Modern Brevo Specification):**
   - *Domain Verification Record:* Type **`TXT`**, Name `@` (or `domain.com.`), Value `brevo-code:<32-char-hex>`.
   - *DKIM 1 Record:* Type **`CNAME`** (Brevo now uses managed CNAME delegation for automated DKIM key rotation, not static RSA TXT strings), Name `brevo1._domainkey` (cPanel appends `.domain.com.`), Value/Target `b1.<domain-slug>.dkim.brevo.com`.
   - *Optional DKIM 2 / DMARC:* If prompted, add secondary CNAME (`brevo2._domainkey`) or TXT `_dmarc`.
4. **cPanel Zone Editor Navigation Pitfall (`Manage` vs Quick Action Buttons):**
   - *Trap:* Attempting to add records using the quick action buttons on the cPanel Zone Editor domain summary table (`+ A Record`, `+ CNAME Record`, `+ MX Record`).
   - *Mechanism:* The quick buttons omit `TXT` records, confusing users into thinking TXT records are unsupported or hidden.
   - *Rule:* Always instruct users to click **`Manage`** on the far right (Actions column) of the domain row in Zone Editor. Inside the Manage table, click the top **`+ Add Record`** button which provides the complete record type dropdown (TXT, CNAME, MX, etc.).
5. **Duplicate DMARC Record Collision Trap (RFC 7489 Violation):**
   - *Trap:* When adding the ESP's DMARC record (`_dmarc` TXT with `rua=mailto:...`), cPanel hosting frequently already contains a default pre-generated DMARC record (`v=DMARC1; p=none;`).
   - *Mechanism:* Brevo immediately detects collision and displays a red warning: *"We have detected multiple DMARC records in your domain. For optimal deliverability, keep only one DMARC."* RFC 7489 Section 6.6.3 dictates that multiple DMARC records invalidate domain policy for receiving mail servers.
   - *Rule:* In cPanel Zone Editor Manage table, filter by `_dmarc`. Delete the generic pre-existing row, preserving strictly the single ESP-aligned record containing the `rua` report destination. Re-click **Authenticate this domain** to clear the error.
6. **Sender Identity & 2024+ Freemail Compliance Enforcement:**
   - *Trap:* Creating Brevo Senders using freemail addresses (`@gmail.com`, `@yahoo.com`) triggers severe deliverability warnings and forces a shared default DKIM signature (`via sendinblue.com`).
   - *Rule:* Under **Senders**, always add a sender address matching the newly authenticated custom domain (e.g. `marketing@domain.com`). With the parent domain authenticated, the sender immediately receives full `Verified` status, custom domain DKIM signing, and 100% compliance with Google/Yahoo 2024+ bulk sender requirements.
7. **Finalizing Authentication:** Return to Brevo and click **"Authenticate this domain"** until status shows green checkmarks across all published records. Under **Senders**, add a verified sender matching the domain.
8. **Campaign Recipients Configuration & Exclusion Trap:**
   - *Trap A (Inverted Exclusion):* Users mistake the "Don't send to" field under Advanced Options for the target recipient field, leaving "Send to" blank while blacklisting their own test addresses.
   - *Trap B (Zero-Contact List / Disabled Save):* Selecting a newly generated folder or empty list (e.g. `Your first list (1/1)` where `(1/1)` denotes selected list count, NOT contact count) locks the "Save" button in a disabled (grey) state because computed recipient count remains 0.
   - *Workaround:* Switch dropdown tab to **Individual contacts** to select specific registered addresses directly, or bypass audience configuration entirely during delivery verification by using the **"Send a test"** button in the campaign editor header.

   ## 7. Newsletter & HTML Campaign Production for Brevo (PDF-to-Email, OCR & Asset Invariants)

   ### Scanned/Exported PDF Newsletter Decomposition & OCR Threading
   When converting client PDF newsletters or weekly news digests into HTML email templates:
   1. **Text Layer Preflight:** Probe the PDF with PyMuPDF (`page.get_text()`). Many corporate PDFs sent via email are printed Gmail threads or flattened graphic design exports where `len(text) == 0`.
   2. **OpenMP CPU Deadlock Pitfall (Tesseract CLI on Virtualized Hosts):**
   - *Trap:* Running `tesseract page.png output` on multi-core Linux VPS (Azure, KVM) causes Tesseract to hang indefinitely or time out.
   - *Mechanism:* Tesseract's default multi-threaded OpenMP runtime experiences thread contention and deadlocks on virtualized vCPU topologies without hardware AVX isolation.
   - *Rule:* Always prefix Tesseract execution with `OMP_THREAD_LIMIT=1`:
    `OMP_THREAD_LIMIT=1 tesseract page.png output --psm 6`
    This forces single-threaded execution, processing full-page scans in under 1 second without freezing.
   3. **Asset Extraction:** Extract embedded images directly via PyMuPDF (`page.get_images()`) to preserve original photograph resolutions rather than cropping blurry rasterized full-page screenshots.

   ### Responsive Table Architecture & Brevo Template Tags
   1. **Bulletproof Table Nesting:** Use nested tables (`cellpadding="0" cellspacing="0" border="0"`) with a max-width container of 600–640px centered on `#f1f5f9`.
   2. **Complete Inline Styling:** Every `<td>`, `<p>`, `<h1>`-`<h4>`, and `<a>` must carry explicit inline `style="..."` attributes (font-family, font-size, line-height, color, margin). Major clients (Gmail, Outlook) strip external and `<style>` blocks in certain view modes.
   3. **Hidden Preheader Snippet:** Place a 1px hidden preheader block immediately after `<body>` so mobile lock screens and inbox lists show a curated teaser instead of raw utility links:
   `<div style="display:none; font-size:1px; line-height:1px; max-height:0px; max-width:0px; opacity:0; overflow:hidden;">Teaser text...</div>`
   4. **Mandatory Brevo Compliance Tags:**
   - *View Online:* `<a href="{{ mirror }}">Buka di Browser Anda</a>`
   - *Unsubscribe Footer:* `<a href="{{ unsubscribe }}">Berhenti Berlangganan (Unsubscribe)</a>` (mandatory under CAN-SPAM and Google/Yahoo 2024+ sender rules to prevent spam flagging).
   - *Physical Corporate Address:* Must be stated in the footer table to comply with global bulk mailing regulations.

   ### Email Image Asset Delivery & Brevo ZIP Invariant
   - **The Base64 Data URI Anti-Pattern:** Never embed base64 image strings (`<img src="data:image/jpeg;base64,...">`) into email HTML. Gmail, Yahoo, and Outlook desktop reject or strip data URIs, leaving broken placeholder boxes, and large base64 payloads trip Gmail's 102 KB message clipping limit (`[Message clipped] View entire message`).
   - **Brevo Native ZIP Upload Workflow:**
   1. Structure the deliverable folder with `index.html` at the root and an `images/` subfolder containing local relative paths (`<img src="images/asset.jpg">`).
   2. Compress into a single archive: `zip -r campaign_bundle.zip index.html images/`.
   3. In Brevo Campaign creation (`Design` step), choose **Upload a file** (or **Upload a ZIP file**). Brevo automatically extracts the HTML, uploads all images in `images/` to its global CDN, and transparently rewrites local paths to CDN URLs (`https://img.mailinblue.com/...`).
   - **Hosted Fallback Workflow:** For users who prefer pasting code into Brevo's **Paste your code** HTML editor, deploy the images to a public web server (e.g. `https://domain.com/assets/newsletter/...`) and substitute image paths so the raw HTML renders immediately without requiring ZIP decompression.
   - **The Relative Path Copy-Paste Pitfall:**
     - *Trap:* Delivering HTML emails with relative image paths (`src="images/..."`) and expecting non-technical users to upload via ZIP.
     - *Mechanism:* Users almost invariably use Brevo's "Paste your code" / HTML box instead of ZIP upload. In cloud webmail editors, relative paths evaluate against the ESP's domain (`https://app.brevo.com/images/...`) and render as broken image icons (`[x]`).
     - *Rule:* Always host campaign images on a reliable HTTPS CDN or public web server (`https://...`) and embed absolute HTTPS URLs directly in the default ready-to-paste deliverable (`newsletter_ready_to_paste.html`). Offer the ZIP bundle only as a secondary asset archive.

### Hostinger Shared Hosting Bulk Sending Limits & AUP Policy Facts
When explaining suspensions to business owners or clients, cite Hostinger's official technical constraints (Knowledge Base #1583510 and #6550582):
1. **Deferred Email Fatal Limit (5/hour):** Hostinger cPanel mail servers strictly cap deferred messages (bounced, non-existent, or spam-filtered addresses) at **5 messages per hour**. If 5 emails bounce within 60 minutes, outgoing email capabilities for the entire hosting plan are automatically disabled.
2. **Recipient Capping:** Max 20 recipients per message on cPanel webmail; max 100 on Hostinger Business/Titan.
3. **Hourly Burst Limit:** Max 200 outgoing messages/hour (cPanel/SMTP+PHP). Sudden spikes trigger automated heuristic anti-abuse scanners that suspend the mailbox to protect server IP hygiene.
4. **Official Policy:** Hostinger's *Is Mass Mailing Supported?* policy explicitly prohibits unsolicited bulk outreach, mandates explicit opt-in lists with visible unsubscribe links, and directs all broadcast mailing to dedicated third-party ESPs.

## 8. Two-Door Corporate Architecture & Executive Stakeholder Alignment

### The Two-Door Architecture (Market Radar vs Deal Desk)
To eliminate email suspension risk while preserving active outreach and formal contract negotiations, divide domain communication into two decoupled operational lanes:
1. **Pintu 1: Market Radar (`commercial@domain.com` via Dedicated ESP):**
   - *Role:* Outbound bulk newsletter broadcasts, industry market snapshots, and awareness campaigns.
   - *Platform:* Brevo (or equivalent ESP) using custom authenticated domain DKIM/DMARC.
   - *Safety:* Offloaded entirely from shared hosting SMTP, zero impact on server reputation.
2. **Pintu 2: Deal Desk (`marketing@domain.com` or `sales@domain.com` via Corporate Webmail/Outlook):**
   - *Role:* Formal 1-on-1 business transactions, official price quotations, Proforma Disbursement Accounts (PDA), billing, and contract execution.
   - *Platform:* Hostinger Webmail / Microsoft Outlook.
   - *Traffic:* Low volume, high value, 100% human-typed (5–20 emails/day), permanently immune to automated spam triggers.
3. **Automated Handover via ESP `Reply-To` Header:**
   - In the ESP campaign settings for `commercial@domain.com`, set the `Reply-To` address to `marketing@domain.com`.
   - When a recipient replies or clicks inquiry CTAs in the broadcast newsletter, the inbound lead automatically lands in the backoffice deal desk without manual forwarding.
4. **Post-Unsuspend Forwarder Teardown (hPanel Hostinger):**
   - Once the primary mailbox (`marketing@domain.com`) is restored, if a temporary server-side forwarder was previously enabled, remove it so both accounts operate independently:
   - In hPanel -> Emails -> Mailboxes, find the email row -> click the three-dot kebab menu (`⋮`) on the far right -> select **Forwarders / Pengalihan Email** (or navigate to the top **Forwarders** tab) -> click the red Trash / Delete icon (`Hapus`) on the forwarding destination. This stops unintended message duplication and enforces clean channel separation.

### Non-Technical Executive & Marketing Team Presentation Blueprint
When onboarding company leadership (owners/directors) and marketing teams who fear technical complexity:
1. **Lead with Operational Benefits, Not Server Jargon:** Avoid discussing DNS, DKIM records, or SMTP protocols. Focus on 4 tangible business values:
   - *100% Suspension Immunity:* Permanent protection against business email downtime.
   - *Zero Incremental Cost:* 300 free emails/day (9,000/month) on standard ESP tiers.
   - *Primary Inbox Deliverability:* Verified domain cryptographic signatures prevent landing in client SPAM/Promotions tabs.
   - *Live Engagement Analytics:* Full visibility into which prospective clients opened, read, and clicked links.
2. **The Meeting Live-Demo Technique:**
   - During the introductory meeting, send an immediate test broadcast newsletter to the stakeholders' mobile devices.
   - Have them inspect the corporate mobile layout, then immediately open the ESP live analytics dashboard to demonstrate real-time open-tracking. This visually validates the platform's professional superiority over standard webmail.

## 9. cPanel API / UAPI Remote Deployment & Host Resolution Protocol

When connecting an autonomous agent or remote CI/CD deployer to a client's cPanel environment via cPanel API 2 / UAPI tokens (`Authorization: cpanel <user>:<token>`):

### Authentication & Username Invariants
- **Username Resolution:** The authorization header format is `Authorization: cpanel <username>:<token>`. The `<username>` MUST strictly match the cPanel account user (displayed under `General Information` -> `Current User`, e.g. `papiawmy`), NOT the client's email address, domain prefix, or the label given to the API token.

### Cloud VM vs Shared Hosting Firewall Invariant (CSF/cPHulk Drops) & Proxy Egress
- **The Domain IP Trap:** Attempting to connect directly to the primary domain's resolved IP address (e.g. `http(s)://<domain_ip>:2083`) from cloud datacenters (Azure, AWS, DigitalOcean, GCP) frequently results in indefinite timeouts or connection drops (`ETIMEDOUT` / packet loss).
- **Mechanism:** Commercial shared web hosting providers (especially in Indonesia / regional networks) employ ConfigServer Security & Firewall (CSF), cPHulk, or upstream ISP rate-limiters configured to drop foreign datacenter IP blocks and non-standard ports (2082/2083/ICMP ping) to prevent brute-force attacks.
- **Proxy Routing Solution:** Route the API/HTTP client requests through an intermediary local or residential proxy (e.g. local forward proxy `http://127.0.0.1:31001`). This changes the egress IP away from cloud provider CIDRs, immediately establishing successful HTTPS handshakes on port 2083.
- **Node URL Verification:** Never assume the domain's web IP is the cPanel management endpoint. Shared hosting clusters routinely separate the web ingress IP from the cPanel management node (e.g. cluster node `srvX.provider.com:2083` vs website IP).
- **Actionable Rule:** Always instruct the user to copy the exact URL visible in their browser address bar while logged into cPanel (e.g. `https://srvX.provider.com:2083`), or read the `Server Name` / `Shared IP Address` from the cPanel `General Information` sidebar.

### cPanel UAPI & API2 Working Function Signatures for Remote Deployers
When automating file operations via REST API:
1. **Directory Creation (mkdir):** Do NOT call non-existent UAPI `autocreate_directory` or `create_directory`. Use cPanel API 2 `Fileman/mkdir`:
   `/json-api/cpanel?cpanel_jsonapi_user=<user>&cpanel_jsonapi_apiversion=2&cpanel_jsonapi_module=Fileman&cpanel_jsonapi_func=mkdir&path=<parent_path>&name=<new_folder>`.
   - *Subdirectory Creation Trap:* Calling `save_file_content` targeting a file inside a non-existent subdirectory fails with `The file "..." does not exist for the account.` Always invoke `Fileman/mkdir` first before uploading files into new subfolders.
2. **File Upload / Save:**
   - *Direct Text/Payload:* Use UAPI `POST /execute/Fileman/save_file_content` with `dir`, `file` (NOT `filename`), and `content`.
   - *Binary/Multipart Upload:* Use UAPI `POST /execute/Fileman/upload_files` with `multipart/form-data` containing form fields `dir` (e.g. `public_html/apps`) and `file-1` with filename and binary content.
3. **Directory Listing:** Use UAPI `GET /execute/Fileman/list_files?dir=<dir>`.
4. **File Deletion (Unlink):** Do NOT call non-existent UAPI `delete_file` or `delete_files`. Use cPanel API 2 `Fileman/fileop`:
   `/json-api/cpanel?cpanel_jsonapi_user=<user>&cpanel_jsonapi_apiversion=2&cpanel_jsonapi_module=Fileman&cpanel_jsonapi_func=fileop&op=unlink&sourcefiles=<path>`.

### Dedicated FTP Deployment Fallback
- When cPanel port 2083 is firewalled against external datacenter IPs or UAPI endpoints return 403 due to shared hosting policy constraints, pivot immediately to a dedicated **FTP Account**:
  1. Have the user navigate to cPanel -> `FTP Accounts`.
  2. Create a restricted deployment user (e.g. `deploy@domain.com`) with directory strictly bounded to `/public_html`.
  3. Connect via FTP/FTPS (port 21). Port 21 is universally permitted through hosting firewalls and bypasses cPanel management API port blocks.

## 10. Client-Side Encrypted Vault: Software & App Store Architecture

When configuring an encrypted client-side storage vault (AES-256-GCM + PBKDF2) as a personal Software & App Hub:
1. **Catalog JSON Schema:** Structure each application item with:
   - `id`: unique identifier.
   - `category`: platform category (`android`, `windows`, `web`, `zip`).
   - `typeBadge`: visible tag (`Android APK`, `Windows x64`, `Web App / PWA`, `Portable ZIP`).
   - `badgeClass`: color-coded neon classes (`badge-apk`, `badge-exe`, `badge-web`, `badge-zip`).
   - `icon`: platform FontAwesome icon (`fa-brands fa-android`, `fa-brands fa-windows`, `fa-solid fa-globe`, `fa-solid fa-file-zipper`).
   - `title`: clear software name and edition.
   - `desc`: functional capability description.
   - `meta`: dictionary containing `size` (e.g. `28.4 MB`), `date`, `downloads`, and `ver` (`v2.4.1`).
   - `downloadUrl`: direct link (e.g. `https://domain.com/apps/app-name.apk` or relative path `./cv/`).
   - `actionLabel`: contextual CTA (`Unduh APK`, `Unduh Installer (.exe)`, `Buka / Gunakan Tool`, `Unduh ZIP Portable`).
2. **Interactive Platform Tabs & Search:**
   - Filter pills must filter in-memory decrypted arrays by `item.category` (`all`, `android`, `windows`, `web`, `zip`).
   - Search input must query across `title`, `desc`, `typeBadge`, and `meta.ver`.
3. **One-Click Link Sharing:** Pair the primary download button with a secondary `Salin Link` button invoking `navigator.clipboard.writeText(item.downloadUrl)` with instant toast confirmation.
4. **Physical File Hosting Isolation:** Store large installer packages in a dedicated subfolder (e.g. `public_html/apps/`) created via API 2 `mkdir`, keeping root `public_html/` uncluttered.
5. **Installation Notes & Setup Warning Badges:** When distributing software requiring specific installation flags (e.g. unchecking auto-updates on patched utilities, disabling telemetry, or run-as-admin requirements), embed a high-contrast inline amber callout (`color: var(--accent-amber); font-weight: 600;`) accompanied by an alert icon (`fa-circle-exclamation`). Placing technical warnings directly inside the card body ensures recipients heed critical setup constraints before launching installers.
6. **Direct Download vs Tool Launcher Differentiation:** Differentiate direct-download items (APK, EXE, ZIP) linking to public distribution mirrors (`https://domain.com/apps/<file>`) with `target="_blank"` from internal web-app launchers (PWA, interactive tools) that link to relative local paths (e.g. `./cv/`) within the same session.
7. **Dual-Source Mirror Pattern (Cloud Storage / MediaFire + Direct Server Fallback):** When users link external cloud storage or file lockers (e.g. Google Drive `drive.google.com/file/d/...`, MediaFire `mediafire.com/file/...`), implement a dual-action layout:
   - *Primary CTA:* Links directly to the user-specified cloud storage URL (`Unduh (Google Drive)` or `Unduh (MediaFire)`).
   - *Secondary Mirror CTA:* Host a standalone copy on the local web server (`public_html/apps/<file>`) and display a direct download button (`<i class="fa-solid fa-bolt"></i> Server Direct`). This provides immediate redundancy if third-party file locker bandwidth is throttled, ads block the download, or cloud drive quotas are exceeded.




