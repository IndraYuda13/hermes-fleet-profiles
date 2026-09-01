# Enterprise Corporate & B2B Web Redesign Guide (Bootstrap 5.3 + High SEO)

When modernizing legacy WordPress / Elementor / PHP business sites into high-performance, mobile-first static or hybrid landing pages:

## 1. Architecture & Design Principles
- **Modern Color Palettes**: Tailor to the industry (e.g., Deep Navy `#0A192F` + Maritime Blue `#0F3460` + Cyan Accent `#00D2D3` for maritime/logistics; Rich Green `#22b14c` + Pure White for manufacturing/printing).
- **Typography Pairing**: `Plus Jakarta Sans` or `Inter` for clean UI body text paired with bold display headings (`Cabinet Grotesk`, `Source Serif 4`, etc.).
- **Live Stats & Trust Badges**: Hero stat boxes with animated counters (IntersectionObserver + `requestAnimationFrame`), CIQ / ISO / BIMCO certification badges, and trust strips.

## 2. SEO & GEO Engine Architecture
- **Schema.org Hierarchy**:
  - Use `Corporation` or `LocalBusiness` on homepage with complete NAP (Name, Address, Phone), `contactPoint`, `areaServed`, `availableLanguage`, and `sameAs` (LinkedIn, etc.).
  - Use `Article` or `BlogPosting` for insights and case studies.
  - Use `FAQPage` with 1:1 question-and-answer pairs matching on-page DOM text.
- **Semantic Structure**: Proper `<header>`, `<nav class="navbar sticky-top">`, `<main>`, `<section id="...">`, `<article>`, and `<footer>` containers.

## 3. Performance & Mobile Responsiveness
- **Zero Bloat**: Replace 2MB+ Elementor/jQuery plugins with native Bootstrap 5.3.3 utility classes and lightweight vanilla JS.
- **Deliverables**: Package ready-to-deploy archives (`tar.gz` containing `index.html`, `css/style.css`, and `js/main.js`) with single-click download for users.
