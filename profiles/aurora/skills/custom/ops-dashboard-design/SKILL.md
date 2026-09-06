---
name: ops-dashboard-design
description: Use when designing ops, incident, or monitoring UIs.
version: 1.0.0
metadata:
  hermes:
    tags: [ui, ux, ops, dashboard, incident-management, monitoring, design-patterns]
    category: custom
---

# Ops Dashboard Design Patterns

Use when designing ops dashboards, incident management tools, monitoring UIs, service health dashboards, SRE command centers, or any high-density real-time operational interface. Complements `elite-product-design` and `anti-ai-slop-design` with domain-specific patterns proven in fleet missions.

## Shell Archetype: Command Strip + Split Panes

For ops/monitoring tools, avoid the standard left-sidebar + topbar pattern -- it is the #1 macro-collision with generic SaaS templates and consistently scores lower in direction comparisons.

**Proven alternative:** Horizontal command strip (48px) + vertical split panes.

### Command Strip Zones
- Left: Wordmark + global severity indicator dot + service status dot cluster
- Center: Segmented tabs (not sidebar nav items)
- Right: Keyboard shortcut hint + on-call badge + primary action button (e.g. "+ Incident")

### Split Pane Behavior
- Desktop 1440px+: side-by-side (35-40% ledger left, 60-65% workspace right)
- Tablet 768px: stacked (ledger 40vh top, workspace below)
- Mobile 390px/320px: single pane with full-screen transitions, collapsed command bar

## Typography: Dual Font Strategy

Always specify separate fonts for data vs prose in data-heavy tools:
- **Monospaced** (JetBrains Mono, Fira Code, Source Code Pro): timestamps, IDs, durations, uptime %, MTTA/MTTR, severity labels, table data
- **Sans-serif** (Inter, IBM Plex Sans, Source Sans): UI labels, descriptions, body prose
- Apply `font-variant-numeric: tabular-nums` on all numeric displays

"Inter for everything" is a slop indicator in ops tools.

## Status Communication: Triple-Coding

Never rely on color alone. Every status indicator must use at least 2 of:
1. **Color** -- red/amber/green/blue/gray
2. **Icon shape** -- octagon=critical, triangle=warning, diamond=caution, circle=info, checkmark=healthy
3. **Text label** -- "SEV1", "Degraded", "Healthy"

Critical states (SEV1, disrupted) must use all three.

## Signal Color Palette (Dark Theme)

| Role | Hex | Usage |
|------|-----|-------|
| Critical/SEV1 | `#EF4444` | Disrupted, critical alert |
| Warning/SEV2 | `#F59E0B` | Degraded, warning |
| Caution/SEV3 | `#EAB308` | Minor, attention needed |
| Info/SEV4 | `#3B82F6` | Informational |
| Healthy | `#22C55E` | Operational, resolved |
| Unknown | `#6B7280` | Unknown state |

Signal colors are reserved for status. Never use decoratively. Pair with background tints at 10-15% opacity for badge backgrounds.

## Metric Presentation

Avoid the 4-box KPI card row. Metrics should be contextual and inline:
- Active incident count in command strip (ambient, not a card)
- Per-service metrics as table columns (uptime %, MTTA, MTTR)
- Sparkline trends inline in analytics tables (40px wide, 5-point)
- Aggregate counts as compact text: `3 Active | 1 SEV1 | 2 SEV2`

## Keyboard-First Interaction

SRE/ops users live in terminals. Design for keyboard:
- `Ctrl+K` / `Cmd+K`: Command palette (centered overlay, max-width 560px)
- `J/K`: Navigate list items (with visible selection change)
- `Enter`: Select/open detail
- `Escape`: Close overlay/deselect
- `N`: Primary action when no input focused
- `1-3`: Tab switching

Focus rings: 2px solid, 2px offset, never suppressed.

## Density & Motion

- Density dial: 7-9/10 for ops tools
- Row height: 36-40px for list items
- Spacing base unit: 4px (scale: 2/4/8/12/16/24/32)
- Motion budget: 150ms max per interaction
- No decorative/entrance animations
- Loading: skeleton pulse at 1.5s ease-in-out, not spinners
- `prefers-reduced-motion`: disable all transitions except opacity

## Surface Hierarchy (Dark Theme)

Elevation through background color progression, not box-shadow:
- Base: `#0A0E14`
- Raised (panes): `#121820`
- Overlay (dropdowns, palette): `#1A2030`
- Hover: `#1E2838`
- Active: `#243040`
- Command strip: `#161C26`
- Borders: 1px solid `#1E2530` (structural, never decorative)

No box shadows. No gradients. Solid fills only.

## Signature Elements

- **Severity Spine**: 2px vertical bar on left edge of incident rows, colored by severity. Creates a visual "waterfall" for scanning severity distribution. Widens to 3px on selected row.
- **Live Elapsed Timer**: Active incidents show ticking elapsed time in mono, warning-colored. Resolved incidents show muted total duration.
- **Service Status Dot Cluster**: Compact row of 6-8px dots in command strip, one per service, colored by status.

## Data Fixture Strategy

DESIGN_CONTRACT must include complete JSON data fixtures, not just schema:
- 6+ services covering all status states (healthy, degraded, disrupted, unknown)
- 4+ incidents with mix of active and resolved, spanning all severity levels
- Full timeline entries per incident with typed events
- Named responders with distinct roles
- Analytics data with realistic MTTA/MTTR values

This is the primary defense against Lorem Ipsum leakage at implementation.

## Fleet Gauntlet Artifact Checklist

For full design missions, verify before declaring PASS:
1. `PRODUCT_CONTEXT.md` -- personas, journeys, data model, prohibited aesthetics
2. `REFERENCE_LEDGER.md` -- 3+ references with what-to-learn / what-not-to-copy matrix
3. `DESIGN_DIRECTIONS.md` -- 3+ structurally distinct candidates, weighted scoring, anti-AI-slop gate, macro-collision check
4. `DESIGN_DNA.md` -- complete visual spec with hex tokens, type scale, spacing, icons, motion, signature elements
5. `DESIGN_CONTRACT.md` -- binding FRAME spec with realistic JSON data fixtures, keyboard/ARIA, numbered acceptance criteria
6. `evidence/manifests/aurora-contract.json` -- mission_id, git_revision, claim/status/reference triples

## Pitfalls

- **Sidebar trap**: Left sidebar is the default AI-generated composition. Wastes horizontal space and creates macro-collision.
- **Color-only status**: Fails WCAG and fails under stress. Triple-code everything.
- **Chart overload**: Stacking 6+ chart types forces users to decode each visual language. Use dense tables + inline sparklines.
- **Light-mode default**: Ops tools are used in dark rooms, during off-hours shifts. Dark-first makes signal colors more vivid.
- **Form-heavy actions**: Fastest path to "incident exists" should be minimal (title + severity). Everything else editable post-creation.
- **Decorative whitespace**: In ops tools, every pixel carries information or facilitates orientation. Density is a feature.
- **High-frequency DOM reflows**: Never mutate geometry properties (`width`, `left`) inside high-frequency playback/telemetry tickers (like `timeupdate` or 10Hz socket tickers); use CSS transform scale/compositing to prevent layout thrashing.
- **Unverified shortcut badges**: Never render keyboard shortcut hints in UI chrome unless active keydown event listeners actually exist in JS.
