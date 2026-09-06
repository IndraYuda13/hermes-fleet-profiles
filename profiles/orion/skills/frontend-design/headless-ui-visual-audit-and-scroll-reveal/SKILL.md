---
name: headless-ui-visual-audit-and-scroll-reveal
description: "Audit scroll-reveal UIs and headless visual verification."
version: 1.1.0
author: Hermes
license: MIT
metadata:
  hermes:
    tags: [UI, Frontend, Playwright, Visual-QA, Scroll-Reveal]
    category: frontend-design
---

# Headless UI Visual Audit & Scroll-Reveal Standards

Practical operational guidelines for auditing and verifying modern web applications, landing pages, and single-page applications using headless browsers (Playwright / CDP) and AI visual analyzers.

## 1. Scroll-Reveal & IntersectionObserver Audit Trap

### The Problem
Modern landing pages frequently utilize custom entrance wrappers (e.g. `FadeInUp` components) driven by `IntersectionObserver` that slide and fade elements from `opacity-0 translate-y-10` to `opacity-100 translate-y-0` with CSS transitions (e.g. `transition-all duration-1000 ease-out`).

In headless Chromium / CDP environments:
1. Taking static screenshots immediately following `page.goto` or instant programmatic jumps (`window.scrollTo(0, y)`) captures elements before the observer entry event settles or while the CSS transition is at frame 0.
2. In headless mode without active paint ticks or when timers are throttled, elements remain in an apparent `opacity: 0` state if the viewport jump is too abrupt.
3. This creates **false-positive defect verdicts** where a human or visual model reports that hero headings, FAQ accordions, or feature cards are "completely missing" or "blank voids".

### Deterministic Remediation Protocol
- **Smooth Incremental Scrubbing:** In Playwright or automated test scripts, simulate incremental user scrolling to trigger observers naturally:
  ```python
  # Scrub incrementally across viewport to trigger all IntersectionObservers
  for y in range(0, 3500, 400):
      await page.evaluate(f"window.scrollTo(0, {y})")
      await asyncio.sleep(0.15)
  await asyncio.sleep(1.0)
  ```
- **Settling Interval Buffer:** Always wait `transition-duration + transition-delay + 200ms` after scrolling an element into view before calling `capture_screenshot()`.
- **Targeted Scroll into View:** Use `element.scroll_into_view_if_needed()` followed by a 500ms–1000ms animation completion wait.
- **Root Margin Buffer:** Configure entrance observers with negative bottom margin buffer (`rootMargin: "0px 0px -40px 0px"`) so items trigger just before entering, ensuring full opacity when reaching center viewport.

---

## 2. Dynamic Video Backgrounds & Contrast Protection

### The Problem
Dark-mode hero and footer sections featuring looping `<video>` elements with glowing or dynamic gradients (e.g. hot amber, magenta, gold liquid ribbons) frequently cause WCAG contrast failures when body text or subheadings are styled with transparent or muted cool-grays (`text-gray-400` / `#9ca3af`). When glowing video highlights pass behind the copy, text becomes illegible.

### Best-Practice Remediation
1. **High-Contrast Text Values:** Upgrade secondary text over video canvas to `text-gray-200` or `text-gray-300`.
2. **Text Drop Shadow:** Apply an optical text drop shadow to guarantee legibility regardless of video frame luminance:
   ```css
   drop-shadow-[0_2px_8px_rgba(0,0,0,0.8)]
   ```
3. **Double-Layer Gradient Scrim:** Overlay `<video>` with a multi-stop gradient overlay:
   ```html
   <div className="absolute inset-0 bg-gradient-to-b from-black/40 via-transparent to-black -z-10 pointer-events-none" />
   ```
4. **Local Asset Staging:** Store video background assets locally in `public/videos/` and serve via HTTP/2 caching rather than relying exclusively on third-party CDNs that may throttle or fail on high-concurrency requests.

---

## 4. Infinite Horizon Marquee & Viewport Masking

To implement continuous horizontal tickers, partner marquees, and badge rails without edge-clipping glitches:
1. **Edge Fade Gradient Mask:** Apply a linear-gradient CSS mask to the overflow container:
   ```css
   mask-image: linear-gradient(to right, transparent, black 15%, black 85%, transparent);
   -webkit-mask-image: linear-gradient(to right, transparent, black 15%, black 85%, transparent);
   ```
2. **Infinite Track Multiplication:** Replicate brand/partner items at least 3–4 times within a `flex w-max` track running `animate-[marquee_30s_linear_infinite]`, paired with `flex-shrink-0 px-8` on each item to prevent screen gaps on wide monitors.
3. **Hover Suspension:** Pause animation during user interaction using `.animate-marquee:hover { animation-play-state: paused; }`.


---

## 3. Flawless Accordion Expansions (CSS Grid Trick)

To avoid JavaScript height recalculations and DOM layout thrashing on accordion components (e.g. FAQ sections):
- Use the CSS Grid transition trick:
  ```html
  <div className={`grid transition-[grid-template-rows] duration-300 ease-out ${isOpen ? "grid-rows-[1fr]" : "grid-rows-[0fr]"}`}>
    <div className="overflow-hidden">
      <p className="text-gray-400 text-sm pb-6 px-6">
        {answer}
      </p>
    </div>
  </div>
  ```
- Pair with an inline SVG Plus icon (`+`) that rotates 45 degrees (`rotate-45`) into a Close cross (`×`).
