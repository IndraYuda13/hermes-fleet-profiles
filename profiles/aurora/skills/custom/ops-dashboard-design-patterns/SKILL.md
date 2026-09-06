---
name: ops-dashboard-design-patterns
description: Use when designing ops, incident, or SRE dashboards.
version: 1.0.0
metadata:
  hermes:
    tags: [design, ui, ops, incident-management, dashboard, sre, devops]
    category: custom
---

# Ops & Incident Dashboard Design Patterns

Use when designing UI for incident management, service operations, SRE monitoring, on-call dashboards, or any tool where users operate under time pressure with high-density operational data.

## Domain Characteristics

- Users are under stress during active incidents (time-critical, high cognitive load)
- Information density must be high but scannable -- not decorative
- Dark-first design reduces eye strain during long on-call shifts and makes signal colors more vivid
- **Triple-coded status**: never color alone; pair with icon + text label; critical states use all three
- **Keyboard-first**: SREs live in terminals; J/K nav, Cmd+K palettes, and keyboard shortcuts signal respect for their workflow
- Persistent critical actions: the most important action (e.g. "Declare Incident") must be accessible from any view

## Shell Archetypes (ranked by ops fitness)

1. **Split Pane (Ledger/Workspace)**: Left = scrollable list, Right = selected item detail. Best for multi-incident monitoring. No sidebar needed.
2. **Horizontal Ribbon Zones**: Top = service health map, Middle = content, Bottom = action bar. Novel, good for service-topology-centric views.
3. **Single-Column Feed**: Linear stream with inline expansion. Simple but sacrifices simultaneous list+detail visibility.

**Anti-pattern**: Left sidebar + topbar + 4 KPI cards + table + drawer is the generic SaaS dashboard -- avoid for ops tools.

## Typography Strategy

- Monospaced font (JetBrains Mono, IBM Plex Mono, Source Code Pro) for ALL data: timestamps, IDs, metrics, percentages
- Sans-serif (Inter, IBM Plex Sans) for prose and UI labels
- `font-variant-numeric: tabular-nums` on all numeric columns for alignment
- Scale: 11px data-sm / 13px body / 16px heading / 20px display

## Color Strategy

- Dark base surfaces: `#08-#0F` deepest, `#12-#1A` raised, `#1A-#22` elevated
- Signal colors vivid against dark: Critical red `#E5484D`, Warning amber `#E5A00D`, Caution gold `#D4A72C`, Info blue `#3B82F6`, Healthy green `#30A46C`
- Each signal color needs a muted variant for badge backgrounds (10-15% opacity tint)
- Zero box-shadow; elevation via background color shifts only
- 1px structural borders in `#1E-#2A` range

## Signature Elements

- **Severity Spine**: 2px left-edge colored bar on list rows for instant severity scan
- **Live Elapsed Timer**: Ticking counter (`2h 14m`) on active items
- **Status Dot**: Global indicator reflecting highest active severity; pulses on critical
- **Command Palette**: Ctrl+K overlay for rapid navigation
- **Persistent Critical Action**: Always-visible primary action button

## State Treatments

- Loading: Skeleton rows matching row layout (not spinner), pulse opacity 0.3-0.6
- Empty: Centered icon + title + calm description ("All clear")
- Error: Warning icon + retry button with critical accent
- Active: Full-color severity, ticking timer, elevated background
- Resolved: Dimmed severity (50% opacity), static duration, green badge

## Detailed Reference Analysis

See `references/ops-incident-dashboard-patterns.md` for full reference product analysis, data model, scoring matrix, and deliverable structure.

## Pitfalls

- Do not default to light mode for ops tools; dark-first is ergonomically correct for monitoring and on-call shifts
- Do not use spinners for loading states; skeleton rows preserve spatial layout expectations
- Do not rely on color alone for any status indicator (accessibility + stress readability)
- Do not use box-shadow for elevation in dark themes; background color shifts are more effective
- Form-heavy incident creation is an anti-pattern; minimize required fields to title + severity, make everything else editable post-creation
