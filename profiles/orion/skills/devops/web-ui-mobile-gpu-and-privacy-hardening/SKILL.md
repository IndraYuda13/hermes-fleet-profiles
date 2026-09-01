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
