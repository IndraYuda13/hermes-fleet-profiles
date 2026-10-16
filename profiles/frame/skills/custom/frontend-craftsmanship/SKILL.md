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

## Evidence-gated repair

- When a reported cosmetic defect names a cause, measure that cause before fixing it. Append an empty peer element to the same parent and diff the parent's height: a delta of zero means the parent's own gap or a sibling margin already governs the spacing and the suspect element is not the cause. Report the ruled-out cause with its measurement and the specific evidence still needed, rather than shipping a plausible-looking change that adds risk to a pre-release diff.
- Revert a speculative cosmetic hunk that no measurement supports, and keep the commit limited to changes you can justify. An unverified "tidy" edit in a release-bound diff costs review time and can regress a surface nobody re-checked.
- Verify a claimed off-surface defect only against the surface itself: an assertion that passes because the element was never rendered is not evidence. Reach the state that renders it, or label the gap explicitly in the handoff.

## Static editorial surfaces and publishing handoff

- Inspect the actual publisher signature and all side effects before calling it; generation helpers may also deploy, mutate registries, or submit URLs.
- When ownership is mechanics-only, keep sanitization in generated artifacts and preserve shared templates, unrelated pages, and existing sidebar policy. Hold publication until the editorial artifact and required independent review are approved.
- Compare local and live membership pages and sitemap by byte hashes, and back up both before changes. Recheck drift immediately before deployment so a stale mirror cannot overwrite newer content.
- Validate one exact article-title H1, required numbered section headings, body-plus-FAQ word count, metadata length, approved outbound links, current live CSS versions, and parseable JSON-LD before rendering. Remove fabricated counters from newly injected listing cards as well as article chrome, without rewriting unrelated historical cards.
- Derive visible publication time and structured publication/modification timestamps from one timezone-aware instant in the publication's timezone; require modified >= published. Avoid template-fixed future publication hours. Do not label secondary-source news as official unless the editorial evidence supports that status.
- Bind metadata-only repairs to fresh hashes and narrowly scoped independent approval. Replace or clearly mark stale evidence manifests so earlier hashes cannot be mistaken for the released revision.
- After an RPC timeout, read deployment state and live targets before retrying; an interrupted reply does not mean the mutation failed. Never duplicate publication to recover a missing response.
- Exercise lazy-loaded editorial images by scrolling them into view before checking decode/load success. Capture and visually inspect both required mobile and desktop renders; screenshot capture alone is not visual verification.
- Verify licensed assets through their source pages and actual pixels, not search snippets alone. Publish linked author/source/license credits and adaptation disclosures; retain share-alike licensing on derivatives when required.
- Do not use Google's Indexing API for ordinary news articles. Keep Search Console sitemap submission and URL inspection separate from indexing claims, and use the exact approved property identifier.
- Report preparation, deployment, and live verification as distinct states; successful preparation is not publication.

For the staged workflow and asset handling recipe, read `references/static-editorial-publishing.md`.
