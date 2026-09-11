# Static Site Storefront Audit Checklist

Reusable checklist for auditing static HTML/JS storefronts (digital product stores, catalogs, landing pages) served via Python/Node/Caddy behind Cloudflare Tunnel. Distilled from fleet audit of Tokono digital store (Sep 2026).

## Server & Infrastructure (ATLAS/FORGE)

- [ ] **Concurrency**: Python `SimpleHTTPRequestHandler` / `socketserver.TCPServer` is single-threaded. Use `ThreadingHTTPServer` at minimum, or Caddy/nginx for production.
- [ ] **Public directory isolation**: Server should serve ONLY a `public/` subdirectory, not the entire project root (exposes QA screenshots, scripts, internal data files, markdown reports).
- [ ] **Caching strategy**: `no-cache, no-store` on static assets (JS/CSS/images) is actively harmful — forces CF edge to BYPASS cache. Set `public, max-age=604800` on immutable assets, `no-cache` only on HTML entry point.
- [ ] **Gzip/Brotli**: Compress text assets at origin. `products.js` (119KB) → 21KB gzipped (82% savings).
- [ ] **Security headers**: CSP, X-Content-Type-Options, X-Frame-Options, Referrer-Policy. Remove blanket `Access-Control-Allow-Origin: *`.
- [ ] **Health endpoint**: `/health` returning JSON with timestamp for monitoring.
- [ ] **MIME types**: `.svg` → `image/svg+xml`, `.ico` → `image/x-icon`, `.webp` → `image/webp`.

## Frontend Performance (FRAME)

- [ ] **Tailwind CDN**: Never use `cdn.tailwindcss.com` in production (~300KB JS render-blocker). Build to static CSS: `npx tailwindcss -o styles.css --minify` → ~15-25KB.
- [ ] **Image lazy loading**: Add `loading="lazy"` to images below the fold. Add explicit `width`/`height` to prevent CLS.
- [ ] **Large asset logos**: Convert PNG logos to WebP (e.g., `canva.png` 107KB → ~5KB WebP). Replace `.ico` files used as logos with proper PNG/SVG.
- [ ] **Skeleton loading states**: Add CSS-only skeleton cards matching real card dimensions. Zero loading state = blank page on 3G/4G.
- [ ] **onerror infinite loop**: `onerror="this.src='fallback.svg'"` loops if fallback also fails. Fix: `onerror="this.onerror=null; this.style.display='none'"`.

## Mobile UX (AURORA/FRAME)

- [ ] **Mobile filters**: If sidebar is `hidden lg:block`, mobile users (majority in ID) have zero filtering. Add a bottom-sheet filter drawer.
- [ ] **Touch targets**: Minimum 44px for interactive elements. Common violation: wishlist/action buttons at 28px (`w-7 h-7`).
- [ ] **Mobile grid**: `grid-cols-1` wastes horizontal space. Use `grid-cols-2` with compact card variant on mobile (≥375px).
- [ ] **Modal → bottom sheet**: Centered modals on mobile waste vertical space. Use slide-up bottom sheet pattern for product detail/checkout.

## Data Quality

- [ ] **Floating point artifacts**: `4.3999999999999995` in rating data. Pre-round with `Math.round(val * 10) / 10`.
- [ ] **Fake discount badges**: Hardcoded fallback like `discountBadge || "-35%"` fabricates discounts. Calculate dynamically from `originalPrice` vs `price`.
- [ ] **Placeholder contact info**: Dummy WhatsApp numbers, placeholder emails. Conversion killer.
- [ ] **Logo file verification**: Cross-check every `icon.logo` reference against actual files in logos/ directory.

## Security (FORGE/SENTINEL)

- [ ] **innerHTML XSS**: Product data (name, tagline, description, variant fields) flowing into `innerHTML` without escaping. Add `escHTML()` helper.
- [ ] **Fake payment flow**: Simulated QRIS/payment that always succeeds erodes trust. Either connect to real gateway or clearly mark as "Coming Soon".
- [ ] **Client-side invoice generation**: `Math.random()` invoice IDs with no server-side state = no audit trail.

## Trust & Conversion (AURORA)

- [ ] **Trust badges**: Move "Garansi", "Aktivasi Instan", "QRIS" from buried sub-footer to visible horizontal strip above catalog.
- [ ] **How It Works section**: 3-step visual flow (Pilih → Bayar → Terima) critical for first-time visitors.
- [ ] **Hero/featured products**: Flat uniform grid gives equal weight to all products. Spotlight top sellers.
- [ ] **Dead navigation links**: `#hash` anchors with no matching sections are trust-damaging dead links.
- [ ] **Accessibility**: Modal focus trapping, `role="dialog"`, keyboard navigation for clickable divs, Escape key handlers, skip-to-main link, WCAG AA contrast compliance.
