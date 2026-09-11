---
name: web-ui-mobile-gpu-and-privacy-hardening
description: Use when hardening UI against mobile GPU glitches and leaks.
version: 1.0.0
author: Orion Quality Governor
license: MIT
metadata:
  hermes:
    tags: [frontend, mobile-gpu, blur-glitch, privacy, hidden-admin, security, css]
    category: devops
---

# Web UI Mobile GPU Rendering & Privacy Hardening Standard

## When to Use
Use this skill whenever designing, building, refactoring, or verifying web frontends, mobile web interfaces, admin portals, or public websites to eliminate:
1. Mobile GPU hardware compositing failures (solid magenta/pink/orange block glitches from CSS blur).
2. Public leakage of "hidden" / secret admin routes in headers, navbars, or footers.
3. Information exposure of internal tech stack, server ports, or backend engines in consumer-facing footers.
4. Client-side vault credential exposure (default password leaks in modal hints, unencrypted client storage, or hardcoded keys).
5. Frontend source inspection vulnerability (unobfuscated business logic, devtools accessibility, and unminified bundles).

---

## 1. Mobile GPU Ambient Glow Composite Glitch Prevention

### The Defect
Placing large fixed-size DOM elements with CSS `filter: blur(...)` (e.g. `<div class="glow-ambient w-[600px] h-[600px] bg-[#E11D48] filter: blur(80px)">`) into the DOM for atmospheric stage lights.
On Android Chrome and various mobile GPUs (Adreno, Mali), CSS `filter: blur()` on large fixed-size divs frequently fails to composite properly during viewport scrolling, rendering as massive solid opaque rectangular blocks (bright magenta, neon cyan, or orange boxes) that block the screen and create dead space.

### The Invariant
**NEVER use huge blurred DOM divs for background atmospheric glows.**

### The Fix: Pure CSS Radial-Gradient
Apply radial gradients directly to `body` or a fixed container background:
```css
body {
  background-color: #070709;
  background-image: 
    radial-gradient(circle at 15% 15%, rgba(225, 29, 72, 0.08) 0%, transparent 40%),
    radial-gradient(circle at 85% 35%, rgba(217, 119, 6, 0.06) 0%, transparent 35%),
    radial-gradient(circle at 50% 85%, rgba(225, 29, 72, 0.05) 0%, transparent 45%);
  background-attachment: fixed;
}
```

---

## 2. Hidden Admin & Secret Portal Isolation Invariant

### The Defect
Adding convenient shortcut buttons, padlock icons, or footer links (e.g. `VAULT ADMIN`, `<a href="/arena-vault-99/">`) to a portal that was requested as "hidden" or secret.

### The Invariant
If an admin portal, upload screen, or management console is specified as **hidden / secret**:
1. **Zero Public Navigation**: No buttons, links, search keywords, or UI shortcuts in header, nav rail, drawer, or footer.
2. **Direct URL Only**: Access must be exclusively via direct URL navigation entered by the authorized operator.
3. **Zero JS Leak**: Do not expose secret route paths in client-side public bundles or search suggestions.

---

## 3. Zero Tech-Stack & Internal Port Leakage

### The Defect
Displaying internal architecture notes in production footers (e.g. `FASTAPI + SQLITE WAL`, `PORT 8395 / 8396`, `Autonomous Engine © 2026`).

### The Invariant
Production public interfaces must remain clean, professional, and consumer-facing. Never leak server ports, database engines, or internal process topologies into public headers/footers unless building an internal developer observability dashboard.

---

## 4. Hero Section Background Stacking & Legacy Template Defect Prevention

### The Defect (The BizPage / Legacy Slider "Blackout" Trap)
Legacy templates (such as Bootstrap BizPage / Owl Carousel) frequently include JavaScript in `main.js` that dynamically strips `<img>` elements from `.carousel-background` and moves the `src` into inline CSS `background-image`:
```javascript
// Legacy pattern in main.js
$(this).css("background-image", "url('" + $(this).children(".carousel-background").children("img").attr("src") + "')")
       .children(".carousel-background").remove();
```
When paired with asynchronous script execution (`defer`), dark container backgrounds (`#intro { background: #000; }`), and pseudo-element overlays (`::before` with 70%+ opacity), this causes:
1. **Flash of Blackout:** The hero area displays solid pitch-black during initial page load before JS executes.
2. **Double Overlay Darkness:** If an inline linear gradient and a stylesheet overlay (`rgba(0,0,0,0.7)`) both apply, photos and lighting effects (sparks, workshop action) are completely obscured into jet black.
3. **Navbar Overlap:** Fixed navigation headers colliding with hero headlines on viewport resize when proper padding isn't reserved.

### The Invariants & Fixes
1. **Inline HTML Fallback:** Always declare `style="background-image: url('...'); background-size: cover; background-position: center;"` directly on the slide container in the HTML itself. Never rely exclusively on deferred JavaScript to mount hero imagery.
2. **Balanced Overlay Ratios:** Keep dark scrim overlays between `rgba(0,0,0,0.35)` and `rgba(0,0,0,0.65)` maximum, ensuring background textures, lighting, and action remain crisp while preserving text readability.
3. **Dedicated Hero Header Offset:** Maintain explicit `padding-top: 60px` to `80px` on the hero content container to guarantee zero collisions with fixed navigation bars across mobile and desktop breakpoints.

---

## 5. Client-Side Vault Security & Zero Plaintext Credential Invariant

### The Defect (Development Hint Leak & Hardcoded Keys)
Storing plaintext password strings (`const VAULT_KEYS = { ... }`) in client JavaScript or leaving default password hint boxes in modal forms (e.g. `Kunci Default: papiaw-umum`). Any visible credential or plaintext comparison (`if (password === '...')`) in client-side code completely invalidates security claims.

### The Invariant
1. **Zero-Knowledge Decryption (AES-256-GCM / PBKDF2):** Sensitive vault catalogs must be stored exclusively as encrypted ciphertexts. Derive 256-bit encryption keys mathematically using Web Crypto API (`crypto.subtle`) with PBKDF2 (100,000 iterations of SHA-256) and AES-GCM. Never store or compare plaintext passwords in source code.
2. **Zero-Leak UI & Modals:** Modals, cards, and tooltips must NEVER expose default keys, password hints, or test credentials in production builds. If hints were used during local development, purge them completely before release.
3. **Zero-Bypass Navigation Guards:** Direct URL or view switching (`showView('private')`) must check in-memory decrypted state, falling back to modal authentication if data is `null`.
4. **Volatile Memory Purge on Lock:** Explicitly set decrypted in-memory variables to `null` and clear DOM containers when re-locking vaults. Never persist decrypted plaintext in `sessionStorage` or `localStorage`.

---

## 6. Anti-Inspect Armor & Production Code Obfuscation Standard

### The Defect
Shipping readable, unminified source code with obvious variable names for sensitive client applications, allowing visitors to reverse-engineer client logic via DevTools.

### The Invariant
1. **1-Line Extreme Minification:** Compress production HTML, CSS, and JS into single-line dense blocks without comments or whitespace.
2. **AST Control-Flow Flattening & Hexadecimal Mangling:** Obfuscate client JavaScript using string array encoding (base64/rc4), control flow flattening, and hex identifiers (`_0x4b1a`).
3. **Anti-Inspect Event Interception:** Capture and prevent `contextmenu` (right click) and keyboard shortcuts (`F12`, `Ctrl+Shift+I/J/C`, `Ctrl+U`, `Ctrl+S`, `Cmd+Option+I`).
4. **Window Binding Integrity:** Always explicitly bind public handler functions invoked by inline HTML attributes (`onclick`, `onsubmit`) to `window` before obfuscation to prevent `ReferenceError` when global identifiers are mangled.
5. **Separate Source from Dist:** Always preserve clean, indented master source in a separate `_source` directory so maintenance remains trivial for the owner while distributing the armored build to hosting.
6. **Automated Dual-Mode Rebuild Tooling:** Provide a static build automation script (e.g. `build_armor.py`) in the source repository so any edits to clean source HTML can be deterministically compiled into the production 1-line obfuscated bundle with zero manual copy-paste errors.
7. **Obfuscation vs Mathematical Decryption Distinction:** Clearly distinguish code obfuscation (cosmetic anti-inspect armor for DOM and reverse-engineering deterrence) from cryptographic zero-knowledge encryption (AES-256-GCM + PBKDF2 data protection). Never claim obfuscation alone provides confidentiality, and never rely on obfuscated plaintext comparisons for security.

---

## 7. cPanel SSL Auto-Provisioning & HTTPS Redirection Workflow

### The Procedure
When deploying a custom static domain (e.g. `papiaw.my.id` / `paplaw.my.id`) to cPanel:
1. **AutoSSL Trigger:** Navigate to `cPanel > SSL/TLS Status` (under *Security*). Select domain and click **Run AutoSSL**. Validation completes within 2–5 minutes, turning padlocks green with "AutoSSL Domain Validated".
2. **Force HTTPS Redirect:** In `cPanel > Domains`, toggle **Force HTTPS Redirect** to `ON`. If the UI switch is missing, add Apache mod_rewrite directives in `public_html/.htaccess`:
   ```apache
   RewriteEngine On
   RewriteCond %{HTTPS} off
   RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
   ```
3. **Cloudflare Proxy Sync:** If DNS is proxied via Cloudflare (orange cloud), set Cloudflare SSL/TLS encryption mode to **Full** or **Full (Strict)** to prevent redirect loops or 525 handshake errors.

---

## 8. Client-Side Software Download Vault & Asset Hosting Architecture

### Binary Hosting Partitioning (cPanel vs External Object Storage)
When turning static landing pages or client-side vaults into application download portals (Android APK, Windows EXE, Mac DMG, Linux DEB):
1. **Small Assets (< 25-50 MB):** Host directly in `public_html/apps/` or `public_html/downloads/` on the static web hosting server for direct, zero-dependency download URLs (`https://domain.com/apps/app-name.apk`).
2. **Large Installers (> 50-100 MB):** Never host multi-hundred-megabyte installer binaries directly on shared cPanel hosting. High-concurrency downloads exhaust shared server bandwidth, trigger PHP/Apache connection timeouts, and rapidly deplete cPanel inode and disk quotas. Instead, offload binaries to GitHub Releases, Backblaze B2 + Cloudflare, or Google Drive direct download links, embedding the external CDN URL in the client-side card schema.

### Standardized Downloadable Catalog Schema
When populating dynamically rendered or encrypted software catalogs, structure items with explicit platform badges, versioning, size metrics, and dual action triggers:
```json
{
  "id": "app-01",
  "category": "android",
  "typeBadge": "APK",
  "badgeClass": "badge-apk",
  "title": "Application Name",
  "desc": "Precise functional summary of the utility, features, and target OS requirements.",
  "meta": {
    "size": "18.4 MB",
    "date": "Sep 2026",
    "version": "v1.4.2",
    "downloads": 142
  },
  "downloadUrl": "https://domain.com/apps/app-v1.4.2.apk",
  "actionLabel": "Unduh APK"
}
```

### Direct Download vs Deep-Link Copy Actions
Always provide two distinct interaction controls on each software card:
1. **Direct Download Button:** An anchor tag with `href="${item.downloadUrl}" target="_blank"` and optional `download` attribute for single-click local saving.
2. **Clipboard Share Button:** A secondary action that copies the direct download URL to clipboard (`navigator.clipboard.writeText(...)`) with toast confirmation, enabling users to share links directly into WhatsApp, Telegram, or cross-device setups without re-authenticating the vault.

---

## 9. Remote Hosting Integration & Agent Deployment Workflows (FTP vs cPanel UAPI)

### Method A: Scoped FTP Deployment (Recommended & Principle of Least Privilege)
When connecting autonomous agents or CI/CD pipelines to a client cPanel server:
1. **Directory Sandboxing:** Create a dedicated FTP account in `cPanel > FTP Accounts` with the directory strictly locked to `public_html` (or a specific subdomain folder). Never grant FTP access to the user home root (`/home/username`), preventing accidental deletion of server configurations, SSL keys, or mailbox databases.
2. **Connection Parameters:** Host: domain or server IP, Port: `21` (or `990` for FTPS), Username: `user@domain.com`, Password.
3. **Automated Upload Tooling:** Use Python standard library `ftplib.FTP` or `FTP_TLS` to automate sync and deployment without requiring third-party CLI installations on the host.

### Method B: cPanel UAPI Token Automation
When using cPanel native REST API for file management and automation:
1. **Token Provisioning:** Generate a token in `cPanel > Manage API Tokens` (under *Security*). Name: e.g. `agent-deploy`, set expiration to "Will not expire".
2. **Authentication Header Requirement:**
   cPanel UAPI strictly requires the header format:
   `Authorization: cpanel <cpanel_username>:<api_token>`
3. **The 403 Forbidden Username Trap:**
   - *Trap:* Attempting API requests using the token alone (`Bearer <token>`) or guessing the domain name or email address as the username.
   - *Mechanism:* cPanel rejects the request with `HTTP 403 Forbidden` because the token is mathematically bound to the specific underlying Unix user account.
   - *Rule:* The `<cpanel_username>` must be the exact cPanel system username (typically a short string <= 8 characters assigned upon account creation, visible in the top-right user menu of the cPanel dashboard).
4. **Port & SSL Verification:** cPanel API runs on port `2083` via HTTPS. When connecting directly via server IP or before SSL propagation completes, configure SSL contexts to handle self-signed certificates (`ssl.CERT_NONE` or custom CA trust) to avoid immediate connection refusal.


