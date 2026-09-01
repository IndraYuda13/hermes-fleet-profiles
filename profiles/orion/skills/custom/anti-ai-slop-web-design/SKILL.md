---
name: anti-ai-slop-web-design
description: Use when designing web UI to eliminate generic AI slop.
version: 1.0.0
author: Orion Fleet Lead
license: MIT
metadata:
  hermes:
    tags: [frontend, design, ui, anti-slop, neobrutalism, swiss, typography]
    category: custom
---

# Anti-AI Slop Web Design & Aesthetic Enforcement

## When to Use

Use this skill whenever orchestrating, designing, building, reviewing, or QAing web user interfaces, dashboards, landing pages, or applications to ensure they do NOT converge into generic "AI slop". Trigger on any web design / frontend creation task.

**Related:** For full Visual Intelligence orchestration workflow (UI Design Depth routing, AURORA 8-step research, Design DNA/Contract, LENS dual-mode QA), see the `fleet-visual-intelligence` skill.

## 1. The Anatomy of Prohibited AI Slop

The following clichés are strictly banned unless explicitly requested by the user:
- **Generic Dark Gradient / Glow**: `#0f172a` (slate-900) background with ambient purple/cyan blur blobs (`bg-gradient-to-tr from-purple-500/20 to-cyan-500/20`).
- **Uniform Rounded-2xl Pills**: `rounded-2xl` or `rounded-3xl` applied indiscriminately across all containers, cards, inputs, and buttons.
- **Translucent Glassmorphism Cliché**: `backdrop-blur-md bg-white/5 border border-white/10` across every surface.
- **Predictable Typography**: Defaulting to `Inter`, `Roboto`, `Arial`, or unconfigured system sans-serif.
- **Cookie-Cutter Hero Section**: Centered H1 with multi-color gradient text (`bg-clip-text text-transparent bg-gradient-to-r...`), 2 centered pill buttons, and a generic 3-column feature grid.

## 2. Multi-Agent Design Gate Workflow

1. **Phase 1: AURORA (Design Architecture & Token Lock)**
   - Commit to a clear **Aesthetic Archetype** before any code is written.
   - Lock exact color tokens (CSS variables / hex), typography scales, border geometries, and layout densities in `DESIGN_SPEC.md`.
   - Explicitly define anti-slop constraints in the handoff for FRAME.

2. **Phase 2: FRAME (Faithful Frontend Implementation)**
   - Adhere strictly to `DESIGN_SPEC.md`.
   - Avoid adding unauthorized gradients, blur effects, or generic rounded corners.
   - Implement tactile micro-interactions (mechanical active states, crisp borders, high-density data layouts).

3. **Phase 3: LENS (Visual & Anti-Slop Audit)**
   - Perform real-browser rendering inspection across viewports via Playwright / CDP.
   - Audit for absence of AI slop tokens.
   - Verify color contrast, typography hierarchy, and interactive states.

## 3. UI/UX Pro Max Engine & 88+ Design Archetypes

To prevent the fleet from falling into **binary over-correction** (e.g. only building black terminal brutalism to avoid slop), the fleet integrates the local **UI/UX Pro Max** search engine:

```bash
python3 /root/.hermes/profiles/aurora/skills/creative/ui-ux-pro-max/scripts/search.py "<query>" --domain <style|color|chart|landing|product|ux|typography|icons|gsap|react|web>
```

### Core Design Archetypes (Rotate across projects):
1. **Minimalist Neo-Brutalism & High-Contrast Monospace (`neubrutalism` / `minimalist-monochrome`):** 0px/1px radius, sharp `#27272A` borders, monospace-first, surgical green/amber phosphor accents.
2. **Swiss Modernism 2.0 (`swiss-modernism-2-0` / `minimalism-and-swiss-style`):** Strict grid, oversized functional typography, bold hierarchy, expansive negative space.
3. **Editorial Grid / Magazine (`editorial-grid-magazine`):** Asymmetric multi-column print structure, drop caps, pull quotes, serif/sans pairing (`Cormorant Garamond` + `Libre Baskerville`).
4. **Tactile Digital / Hardware UI (`tactile-digital-deformable-ui` / `retro-futurism`):** Teenage Engineering / Dieter Rams industrial feel, tactile button presses, recessed panels, segmented displays.
5. **Bauhaus / Constructivist (`bauhaus`):** Primary color blocking, hard offset shadow (`4px 4px 0px #000`), geometric cards, bold uppercase headlines.
6. **E-Ink / Paper (`e-ink-paper`):** Warm monochromatic high-contrast, paper texture, minimal eye strain.
7. **Data-Dense Telemetry (`data-dense-dashboard` / `real-time-monitoring`):** High info density, compact status chips, monospace streams, precision borders.
8. **Spatial / Minimal Monochrome (`minimalist-monochrome` / `exaggerated-minimalism`):** Clean stark contrast, massive whitespace, clamp typography.

## 4. Execution Pitfalls & Anti-Slop Enforcement Rules
- **Exhaustive Deep-Audit Protocol (Anti-Sloth)**: Refer to `references/exhaustive-audit-protocol.md`. LENS and SENTINEL must perform 100% route/modal inventory extraction, 3-layer atomic interaction stress testing, and active parameter fuzzing rather than passive superficial reviews.
- **Binary Over-Correction Pitfall**: Avoiding AI slop does NOT mean every website must be a black hacker terminal. AURORA must actively choose distinct archetypes matching the product type.
- **Pre-Execution Disk Check**: Always ensure ≥8GB root disk before dispatching browser QA (`LENS`), and clean temporary browser caches (`.cache/puppeteer`, `.cache/uv`, test artifacts) immediately after verification.
- **Strict Separation of Design vs Implementation**: Never let FRAME start coding without AURORA's explicit `DESIGN_SPEC.md` token lock; otherwise models default to generic AI presets.
- **Production Iteration & Clean Rollback Protocol**: Refer to `references/production-iteration-rollback.md` when experimenting on live web services. Always snapshot the stable commit SHA before deploying experimental design overhauls, and execute immediate clean rollback if the operator rejects the direction.
- **Gateway Process Isolation Guard**: Board management & task creation commands that spawn workers or scripts must avoid recursive process restarts. When seeding multiple parent-gated tasks programmatically via Python, write directly to the SQLite Kanban DB (`tasks` and `task_links` tables) rather than invoking nested shell CLI loops.
- **Live Verification & Proactive Operator Delivery**: Use LENS to capture real browser screenshots across multiple viewports (Desktop 1920x1080 and Mobile 390x844) to confirm zero visual regression and verify real interaction before claiming completion. ORION must proactively notify and deliver live artifacts/screenshots immediately upon completion without waiting for operator prompts.
- **Baseline Audit Discipline**: Refer to `references/baseline-audit-discipline.md` during fleet audits to strictly partition `EXISTING_BASELINE_FEATURE` from `NEWLY_IMPLEMENTED_CHANGE`, enforce `orion_production_edits == 0`, and avoid manufacturing artificial improvements when a system is already healthy.
