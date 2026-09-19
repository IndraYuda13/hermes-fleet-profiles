# Ops and Incident Interface Patterns

## Command workspace

- Prefer a horizontal command strip with service status, segmented navigation, keyboard hints, on-call identity, and the persistent critical action; avoid a generic sidebar-plus-topbar shell.
- Use a ledger/workspace split for concurrent triage: keep the incident list at roughly 35–40% width on desktop and make the selected incident a dedicated workspace rather than a secondary drawer.
- Recompose deliberately on smaller screens: stack ledger and workspace at tablet widths, then use full-screen transitions and a collapsed command bar on phones.
- Use a service-topology ribbon only when topology is the primary task; otherwise the split workspace provides better incident context.

## Operational readability

- Use monospace for IDs, timestamps, durations, percentages, and severity labels; use a sans-serif for prose and controls, and apply tabular numerals to aligned data.
- Encode status with at least two channels—color, shape/icon, and text—and use all three for critical states; never rely on color alone.
- Reserve signal colors for status, use solid dark surface progression for elevation, and avoid decorative gradients or shadows that compete with operational signals.
- Prefer contextual inline metrics and short aggregate summaries over a row of generic KPI cards; use compact sparklines inside tables when trends matter.
- Keep density high but scannable: use 36–40px rows, 4px spacing increments, short interaction motion, skeleton rows instead of spinners, and reduced-motion fallbacks.

## Response workflow

- Make the typed timeline the detail backbone and show elapsed time so responders can reconstruct causality without switching context.
- Reveal communications, responders, service impact, and extended actions progressively after triage; pressure workflows need a small initial decision surface.
- Keep incident declaration available everywhere and require only title and severity initially; add the rest after the incident exists.
- Implement and test every displayed shortcut—command palette, list navigation, selection, dismissal, and tab switching—before showing its hint.
- Prevent high-frequency telemetry updates from mutating layout geometry; animate composited transforms and stop render work when the view is hidden or offscreen.

## Contract and fixture QA

- Include realistic fixtures covering healthy, degraded, disrupted, and unknown services; active and resolved incidents; every severity; typed timeline entries; responders; and plausible MTTA/MTTR values.
- Specify product context, reference decisions, candidate directions, visual DNA, implementation contract, acceptance criteria, and evidence artifacts for full design missions.
- Treat overflow, runtime errors, unreadable contrast, missing focus states, and ungrounded data as hard failures before visual polish is accepted.
