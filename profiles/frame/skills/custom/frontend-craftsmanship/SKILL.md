---
name: frontend-craftsmanship
description: Build polished responsive UI and verify the rendered implementation.
version: 2.0.0
metadata:
  hermes:
    tags: [frontend, responsive, ui, engineering]
    category: custom
---

# Frontend Craftsmanship

## Procedure

1. Read AURORA's design intent when available; understand why before implementing what.
2. Build semantic, maintainable components with clear state ownership and accessible interactions.
3. Establish typography hierarchy, readable line lengths, numeric alignment, spacing rhythm, and density.
4. Implement coherent iconography and intentional interaction states.
5. Treat each responsive range as a composition rather than a scaled desktop.
6. Stress long labels, huge values, zero items, many items, validation, loading, errors, modals, dropdowns, sidebars, and theme changes.
7. Inspect hover, focus, keyboard, active, pressed, disabled, touch, and navigation states.
8. Render the actual interface; inspect visually and inspect browser console.
9. Fix visual issues even when code/test tools report no error.
10. After the final material change, rerun functional, build, and visual gates.

Do not reuse an older PASS after code changes.

## Static editorial surfaces and publishing handoff

- Inspect the actual publisher signature and all side effects before calling it; generation helpers may also deploy, mutate registries, or submit URLs.
- When ownership is mechanics-only, keep sanitization in generated artifacts and preserve shared templates, unrelated pages, and existing sidebar policy. Hold publication until the editorial artifact and required independent review are approved.
- Compare local and live membership pages and sitemap by byte hashes, and back up both before changes. Recheck drift immediately before deployment so a stale mirror cannot overwrite newer content.
- Validate one exact article-title H1, required numbered section headings, body-plus-FAQ word count, metadata length, approved outbound links, current live CSS versions, and parseable JSON-LD before rendering. Remove fabricated counters from newly injected listing cards as well as article chrome, without rewriting unrelated historical cards.
- Exercise lazy-loaded editorial images by scrolling them into view before checking decode/load success. Capture and visually inspect both required mobile and desktop renders; screenshot capture alone is not visual verification.
- Verify licensed assets through their source pages and actual pixels, not search snippets alone. Publish linked author/source/license credits and adaptation disclosures; retain share-alike licensing on derivatives when required.
- Do not use Google's Indexing API for ordinary news articles. Keep Search Console sitemap submission and URL inspection separate from indexing claims, and use the exact approved property identifier.
- Report preparation, deployment, and live verification as distinct states; successful preparation is not publication.

For the staged workflow and asset handling recipe, read `references/static-editorial-publishing.md`.
