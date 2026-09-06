---
name: web-serp-audit
description: Audit SEO, SERP cannibalization, and website visibility.
version: 1.0.0
author: RADAR
license: MIT
metadata:
  hermes:
    tags: [seo, serp, audit, indexing, web-analytics, market-discovery]
    category: research
---

# Web SERP & Technical SEO Audit

Use when investigating traffic drops, organic visibility loss, algorithm update impacts (Helpful Content / Core Update), or marketplace/local pack cannibalization for commercial websites.

## Procedure

1. **Infrastructure & Canonical Audit**
   - Probe apex domain and www variants via `curl -sI` to check for clean 301 redirects vs dual-serving (HTTP 200).
   - Check DNS resolution (A records) to detect fragmented subdomains or disparate hosting setups.
   - Inspect `robots.txt` and `sitemap.xml` for crawl budget issues, missing URLs, or broken endpoints.

2. **Information Architecture & Silo Integrity**
   - Test key commercial/product endpoints for 404 errors or thin single-page brochure architectures (<1000 words covering too many diverse intents).
   - Verify whether subdomains (e.g., `blog.example.com`) should be consolidated into subfolders (`example.com/blog/`) to preserve link authority.

3. **On-Page & Semantic Structure**
   - Extract and verify heading hierarchy (single clear H1, properly nested H2/H3).
   - Flag outdated keyword stuffing in `<meta name="keywords">`.
   - Audit Schema.org structured data: note that `FAQPage` rich snippets were restricted by Google in Aug 2023 for general commercial sites; recommend `Product`, `Offer`, or `LocalBusiness`.
   - Ensure consistency of business information (pricing, MOQ, NAP).

4. **SERP Cannibalization & Market Positioning**
   - Assess competition across 3 tiers:
     - Tier 1: E-commerce Marketplaces (Shopee, Tokopedia) taking low-MOQ/retail transactional intent.
     - Tier 2: Google Local 3-Pack (Maps) intercepting geo-targeted searches ("vendor X jakarta").
     - Tier 3: Social/Visual discovery (TikTok Shop, Instagram, Pinterest).
   - Synthesize recovery recommendations across Technical, Architecture, Positioning (e.g. B2B wholesale MOQ vs retail), and Local SEO (Google Business Profile).
