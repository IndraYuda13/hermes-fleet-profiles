# Editorial Footer & Publisher Contact Architecture for Media Portals

Guidelines for authoring, sanitizing, and deploying publisher contact blocks and footer columns across financial news and YMYL media portals.

---

## 1. Publisher Brand Identity vs. Regulatory Complaint Hotlines

### Pitfall of Lingering Regulatory Advisory Blocks
When transitioning or operating a general financial news and literacy portal (e.g., DailyFinance.id), retaining prominent regulatory complaint hotlines (e.g. OJK hotline 157, WhatsApp pengaduan, email aduan pinjol ilegal) in the global 4-column footer creates brand confusion:
- It makes the site appear like an auxiliary debt counseling or loan dispute desk rather than an independent daily business media publisher.
- It introduces visual clutter and distracts corporate partners, advertisers, and press agencies from locating the media outlet's official contact points.

### Canonical Publisher Contact Column Rule
The contact column (typically Column 4 of a standard 4-column magazine footer) must strictly serve editorial and commercial correspondence:
- **Title**: `Kontak & Kerjasama` or `Hubungi Redaksi`.
- **Purpose Text**: Concise invitation for media partnerships, business relations, press releases (*siaran pers*), and advertising inquiries.
- **Single Canonical Contact**: Display only the official corporate/partnership email address (e.g., `partnership@dailyfinance.id`).
- **Visual Styling**:
  - High-contrast highlight (e.g., vibrant cyan `#38bdf8` on dark theme).
  - Preceded by a clean, semantic envelope icon (`<i class="fa-regular fa-envelope text-info"></i>`).
  - Active clickable hyperlink with explicit `mailto:` protocol.
  - Zero external phone numbers, personal chat numbers, or regulatory grievance hotlines unless specifically segregated onto a dedicated compliance/legal subpage.

---

## 2. Global Sitewide Propagation & Sync Protocol

Whenever a footer modification is requested on a specific page (e.g., `tentang-kami.html`):
1. **Identify Footer Canon**:
   - Inspect whether the footer is shared across static HTML pages and whether a template builder exists (e.g., `builder_hotmagazine.py`).
2. **Synchronize All Static Files**:
   - Never update only the single requested URL and leave other pages out of sync.
   - Batch-replace the exact HTML block across all active production HTML files.
   - Update the generator script / template builder so future batch builds preserve the new footer.
3. **Deploy & Re-Index**:
   - Upload all modified HTML files to production hosting (e.g. cPanel `public_html/`).
   - Trigger the search engine indexing API (e.g. Google Indexing API) for the modified canonical URLs.
