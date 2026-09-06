# Exhaustive Deep-Audit & Anti-Sloth Protocol (LENS & SENTINEL)

## Overview
This reference outlines the mandatory exhaustive inspection rules for LENS (Visual QA) and SENTINEL (Security Audit) to eliminate passive, superficial, or incomplete verification loops.

---

## 1. LENS: 100% Route & Interaction Traversal Protocol

1. **Mandatory Route & Endpoint Inventory Extraction:**
   - Before executing any visual assertion, LENS must parse the codebase router/frontend (`app.js`, `routes.py`, `urls.py`, `views/`) to construct a complete manifest of all paths, wizard steps, modals, and dynamic drawer states.
   - QA CANNOT be marked PASS if any route or modal is omitted from visual inspection.

2. **3-Layer Atomic Interaction Testing:**
   - **Layer 1: Surface Traversal:** Every major page, tab, sub-view, and dialog.
   - **Layer 2: Control State Matrix:** Every button, link, accordion, toggle, and slider must be exercised in:
     - `default` state
     - `hover` / `focus` state
     - `active` / `clicked` state
     - `disabled` / `loading` state
   - **Layer 3: Form Stress & Boundary Inputs:**
     - Blank / Empty submission (verify error toast/banner positioning and visibility)
     - Valid standard payload
     - Extreme string length & special character stress test (verify zero layout clipping, zero horizontal overflow-x).

3. **Multi-Viewport Visual Matrix:**
   - Desktop Full HD: 1920x1080
   - Laptop / Standard Desktop: 1440x900
   - Tablet: 768x1024 / 1024x768
   - Modern Mobile: 390x844
   - Compact Mobile: 360x800

4. **Visual Consistency Auditing:**
   - Confirm font pairing, weight hierarchy, and token contrast across all sub-views.
   - Assert zero unhandled horizontal scrolling (`overflow-x == 0`).
   - Deliver full artifact screenshots for each step in `artifacts/`.

---

## 2. SENTINEL: Active Adversarial Attack & Security Gate

1. **Active Endpoint & Parameter Fuzzing:**
   - XSS Injection on all input forms and URL parameters: Polyglots, SVG vectors, `<img src=x onerror=...>`, `javascript:`.
   - SQLi / NoSQLi payload probing on filter/search parameters.
   - Business Logic & Negative Value Testing (e.g. negative balances, integer overflow, currency manipulation).

2. **Authorization & Boundary Verification:**
   - Broken Object Level Authorization (BOLA/IDOR) across user/order identifiers.
   - CSRF and CORS configuration inspection.
   - Sensitive data exposure in client-side JS bundles, log exports, or LocalStorage.

3. **Runtime Resource Resilience:**
   - Audit continuous event loops, WebGL/Canvas rendering memory allocation, and WebSocket reconnect loops for memory leaks and client-side DoS.
