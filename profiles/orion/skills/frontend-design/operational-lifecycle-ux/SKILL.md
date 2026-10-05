---
name: operational-lifecycle-ux
description: Use when designing multi-stage operational field workflows.
version: 1.1.0
author: Orion
license: MIT
metadata:
  hermes:
    tags: [ux, operational, logistics, stepper, field-agent, telemetry, ais]
    related_skills: [frontend-craft-and-hardening, live-ui-kanban-orchestration]
---

# Operational Lifecycle & Multi-Stage Field Stepper Architecture

## When to Use
Use when building operational dashboards, field-agent applications, logistics portals, or multi-stage industrial tools where users get overwhelmed by unorganized telemetry or need a clear chronological progression (e.g. vessel intake → berthing → loading progress → departure clearance).

## 1. The Raw Dashboard Anti-Pattern (Cognitive Overwhelm)
Dumping live telemetry, sensor gauges, and complex controls into a single unguided dashboard immediately confuses operational users and clients. Users do not know where to start, what phase the asset is in, or what action is expected of them.

## 2. Chronological Lifecycle Stepper Standard
Break complex operational workflows into 4 sequential real-world phases:
1. **Intake / Data Registration (`Mengisi Data`):** Vessel/asset specs, contract parameters, initial proforma estimates (EPDA).
2. **Arrival & Readiness Checklist (`Kapal Sandar`):** Sequential clearance gates (anchor drop, quarantine inspection, pilotage/tug, all-fast berthing, initial draft survey) with 1-click confirmation buttons.
3. **Live Operations & Telemetry (`Progress Kapal`):** Real-time work counters (tonnage loaded, hatch progression, loading rate) paired with emergency weather/contingency controls (BIMCO rain clause laytime stopper) and live AIS satellite tracking.
4. **Departure & Financial Reconciliation (`Keberangkatan & Akun`):** Outward clearance, port clearance issuance, and final disbursement account reconciliation (EPDA vs FDA).

## 3. Deep-Linking via URL Hash Synchronization
- Sync active stepper tabs bidirectionally with URL hashes (`#tab1`, `#tab2`, `#tab3`, `#tab4`, `#new`).
- When an operator clicks a step, update `window.location.hash = 'tab' + index;`.
- On `DOMContentLoaded`, read `window.location.hash` and invoke `switchTab(...)` so links shared via email, chat, or bookmark load directly into the relevant phase.

## 4. One-Click Confirmation with Immutable Timestamps
- Replace generic checkboxes with explicit confirmation buttons (`✓ Tiba Dikonfirmasi`, `✓ Lolos Karantina`, `✓ Pandu Onboard`).
- Clicking records an immutable client/server timestamp and appends a formal event into the legal audit trail (Statement of Facts / SOF).

## 5. High-Impact Contingency Action Bars
- Operational risk controls (e.g. weather delays, hazardous stops) must be prominent top-level alert bars, not hidden inside settings or nested menus.
- Clicking the contingency button immediately toggles state across all connected client views, suspends contractual timer calculations (e.g. laytime), and updates button labels dynamically.

## 6. Real-Time Telemetry & Hardware Cross-Verification
- Pair live IoT / AIS satellite telemetry (e.g. AISStream WebSocket feeds) directly with operational checklists.
- Use physical metrics to cross-verify operator claims: e.g. Speed Over Ground (SOG) < 0.2 kts verifies anchorage/all-fast berthing; displacement/draft change verifies initial vs final draft surveys.
- For streaming feeds, use bounding-box geospatial filtering to keep client bandwidth bounded. Prepend incoming packets to a rolling visual ticker (capped at 20-30 entries) to give field personnel and principals instant situational awareness.
- When rendering radar displays, use pure CSS/SVG sweep animations with cardinal axis crosshairs and concentric range rings rather than heavy mapping libraries when rapid glanceability is required.
- See `references/ais-telemetry-integration.md` for WebSocket schemas, message parsing, and canvas/CSS radar animation recipes.

## 7. Pitfalls to Avoid
- **Do not mix intake with execution:** Keep vessel registration (specifications, EPDA) in Stage 1 so operators aren't forced to re-enter parameters during high-pressure berthing or loading stages.
- **Never hide legal clause triggers behind dialogs:** Demurrage and laytime stoppage triggers (such as BIMCO weather clauses) must be one-click actions on the primary dashboard; burying them causes delayed entries that fail contractual scrutiny.
- **Always handle WebSocket reconnection gracefully:** Field and port environments suffer frequent micro-disconnections. Reconnect automatically with backoff, while keeping cached telemetry visible so the interface never blinks blank.
