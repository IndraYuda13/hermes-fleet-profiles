# Seamless Infinite Scroll & Continuous Catalog Ingestion Patterns

## Core Challenge
Traditional pagination ("Halaman 1, 2, 3") breaks immersion in content streaming and expansive e-commerce catalogs. However, naive infinite scroll often causes severe UX defects:
1. Scroll jumping / layout thrashing from overwriting `innerHTML` on each page append.
2. Duplicate cards injected when rapid inertial scrolling fires multiple concurrent API requests.
3. Stuck or dropped observer triggers when `IntersectionObserver` sentinel is offscreen or unobserved during DOM re-renders.
4. Inaccessible fallback for keyboard navigation, screen readers, or users with disabled JS/flaky network.

---

## 1. Dual-Trigger Architecture (Observer + Scroll Fallback)
Relying solely on `IntersectionObserver` can drop triggers during high-velocity fling scrolls on mobile or inside custom scroll parents. Combine it with a passive throttled window scroll fallback:

```javascript
function initInfiniteScroll(sentinelElement, loadNextBatch) {
  // 1. Primary: IntersectionObserver with generous rootMargin
  if ('IntersectionObserver' in window && sentinelElement) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const cs = state.catalogState;
          if (!cs.isLoading && cs.hasMore && cs.items.length > 0) {
            loadNextBatch();
          }
        }
      });
    }, {
      root: null, // viewport
      rootMargin: '300px 0px 300px 0px', // fetch 300px before user reaches bottom
      threshold: 0.01
    });

    observer.observe(sentinelElement);
  }

  // 2. Secondary: Passive throttled window scroll fallback (150ms)
  let scrollThrottle = null;
  window.addEventListener('scroll', () => {
    const cs = state.catalogState;
    if (cs.isLoading || !cs.hasMore || cs.items.length === 0) return;

    if (scrollThrottle) return;
    scrollThrottle = setTimeout(() => {
      scrollThrottle = null;
      const scrollBottom = window.innerHeight + window.scrollY;
      const threshold = document.documentElement.offsetHeight - 400;
      if (scrollBottom >= threshold) {
        loadNextBatch();
      }
    }, 150);
  }, { passive: true });
}
```

---

## 2. Multi-Layer Deduplication Guard
Under rapid continuous scrolling, network latency jitter can return overlapping items or race conditions. Implement double-layer deduplication:
1. **In-Memory Set:** Filter newly returned items against an ID Set of already loaded items:
   ```javascript
   const existingIds = new Set(cs.items.map(item => String(item.id)));
   const newSlice = newItems.filter(item => !existingIds.has(String(item.id)));
   cs.items = cs.items.concat(newSlice);
   ```
2. **DOM-Level Attribute Check:** Mark cards with `data-id="${item.id}"` and verify before injection:
   ```javascript
   if (appendOnly && container.querySelector(`[data-id="${item.id}"]`)) {
     return;
   }
   ```

---

## 3. Incremental DOM Append vs Layout Thrashing
- **On Reset / Filter Change (`reset = true`):** Clear container, display skeletons, reset page counter to 1, and scroll to top.
- **On Pagination Append (`reset = false`):** Do NOT touch existing DOM nodes or innerHTML. Append only the newly received `newSlice` elements using `document.createElement()` and `container.appendChild()`. This preserves active scroll position, video/canvas contexts, and hover/focus states.

---

## 4. Visual State Lifecycle & Accessibility
1. **Discrete Loading Pill:** Show a glassmorphism pill (`#catalog-scroll-spinner`) with spinner and text ("Memuat koleksi berikutnya...") directly above the sentinel.
2. **Accessible Fallback Button:** Retain `#catalog-load-more-btn` in the DOM as a visible/usable fallback if auto-scroll fails or user prefers explicit manual control.
3. **End-of-Catalog Indicator:** When `!cs.hasMore`, hide both the spinner and load more button, and reveal `#catalog-end-indicator` ("Semua koleksi telah ditampilkan").
