---
name: desktop-workbench-and-directory-architecture
description: "Use when building desktop workbenches and directories."
version: 1.0.0
author: Hermes
license: MIT
metadata:
  hermes:
    tags: [Frontend, Desktop, UX, Architecture, Directory, Search, Performance]
    category: frontend-design
---

# Desktop Workbench & High-Capacity Directory Architecture

Engineering standard and design patterns for building desktop-first utility applications, interactive search workbenches, and high-capacity client-side searchable directories.

## When to Use
Use when building or refactoring tools with input controls and dynamic results (route finders, calculators, filterable directories, inventory searchers) where wide monitors create visual fatigue or when rendering large multi-category datasets (100+ to 1,000+ items).

---

## 1. Desktop Split-Workbench Layout (The Wide-Monitor Fatigue Defect)

### The Anti-Pattern
Placing search controls, dropdowns, and results in a single full-width vertical stack on wide screens (1280px–1920px+) causes excessive eye travel across empty space, awkward stretched inputs, and forces repetitive scrolling back to the top whenever adjusting search parameters.

### Standard Procedure: Asymmetrical Two-Column Split
On desktop screens (`lg` breakpoint, $\ge 992\text{px}$):
1. **Sticky Control Sidebar (`col-lg-5` or `col-lg-4`):**
   - Encapsulate inputs, origin/destination selectors, mode switches, and action buttons in a dedicated card.
   - Enforce `position: sticky; top: 90px; z-index: 10;`.
   - Keep maximum height within viewport bounds (`max-height: calc(100vh - 120px); overflow-y: auto;`) so controls never clip on compact laptop displays.
2. **Scrollable Output Stream (`col-lg-7` or `col-lg-8`):**
   - Render detailed results, itineraries, transit stops, or matching records in the fluid right column.
   - Users can scroll through long itineraries while search parameters remain pinned and instantly editable.
3. **Responsive Mobile Transition ($\le 991\text{px}$):**
   - Switch container to standard vertical flow (`flex-column`).
   - Revert sidebar positioning to `position: static;` so it does not occlude subsequent result content.

---

## 2. High-Capacity Directory Progressive Rendering

### The Anti-Pattern
Rendering hundreds of rich card components (200+ cards containing badges, buttons, and metadata) in a single synchronous DOM injection causes frame drops, spikes First Contentful Paint (FCP), and causes severe Cumulative Layout Shift (CLS).

### Standard Procedure: Progressive Batching & Real-Time Filtering
1. **Bounded Initial Batch:**
   - Render an initial batch (e.g. 24 cards) on initial page load or whenever category filters change.
   - Prevents DOM bloat while immediately filling the visible desktop viewport.
2. **Progressive "Load More" Expansion:**
   - Provide a prominent, quiet action button ("Tampilkan Rute Lainnya (+N)") that appends the next batch without re-rendering existing DOM nodes or shifting scroll position.
   - Display a live count indicator (e.g. `Menampilkan 24 dari 242 rute`).
3. **Exact Category & Filter Count Badges:**
   - Precompute exact category distributions across the dataset.
   - Display live count chips on category filter buttons (e.g. `Semua (242)`, `BRT (30)`, `Pengumpan (64)`, `Transjabodetabek (18)`).
   - Dynamic button states: set solid primary accent on active filter, subtle outline on inactive filters.
4. **Multi-Field Instant Search Listener:**
   - Listen to `input` events on the search bar.
   - Normalize queries (`trim().toLowerCase()`) and match against multiple fields: identifier code, origin, destination, transit hubs, and category labels.
   - Automatically reset batch pagination to the initial limit on new queries so matching records are immediately visible.

---

## 3. Official Public Transport & Entity Data Ingestion Standard

When ingesting official transport or multi-tier service catalogs:
1. **Category Separation:**
   - Partition routes into official service tiers: Bus Rapid Transit (BRT), Feeder/Pengumpan, Aglomerasi Komuter (Transjabodetabek), Premium/Royaltrans, Angkutan Lingkungan (Mikrotrans), and Wisata.
2. **Badge Color Semantics:**
   - Preserve official identity colors for core transit corridors (e.g. K1 Red, K2 Royal Blue, K3 Yellow, K13 Violet) while applying calm category badges (Emerald for Komuter, Purple for Premium, Orange for Feeder).
3. **Direct Official Asset Links:**
   - Provide direct action links to official diagrammatic schematics (PDF/JPG) hosted on official authority CDNs to give users verifiable transit references.

---

## 4. Verification Checklist
- [ ] Viewport 1280px: Sticky workbench remains visible while scrolling 10+ result items.
- [ ] Viewport 390px: Layout cleanly collapses to single column with zero horizontal overflow (`scrollWidth <= clientWidth`).
- [ ] Search input responds instantly (< 50ms) across 200+ records without debounce lag.
- [ ] Zero undefined/null string interpolations in rendered badges, cards, or titles.
- [ ] Zero unhandled JavaScript errors in browser console.
