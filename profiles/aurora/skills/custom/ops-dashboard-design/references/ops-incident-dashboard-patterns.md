# Ops & Incident Dashboard -- Detailed Reference Patterns

Condensed from live research (2026-09-02) on PagerDuty, incident.io, FireHydrant, Grafana Cloud IRM, Rootly, ATC display guidelines, Bloomberg Terminal, and Linear.

## Reference Products Quick-Reference

| Product | Best For | Watch Out For |
|---------|----------|---------------|
| PagerDuty | Metric taxonomy (MTTA/MTTR), filter cascade architecture | Flat visual hierarchy, generic shell |
| incident.io | Progressive disclosure, badge refinement, hover states, collapsible sidebar | Standard sidebar pattern, light-mode-first |
| FireHydrant | Command Center concept, milestone state machine, persistent declare action | Form-heavy creation, traditional nav |
| Grafana IRM | Timeline-centric design, observability integration | Too chart-heavy, pricing leaks into UX |
| Rootly | Workflow automation concepts, AI-assisted incident handling | Web UI is secondary to Slack |
| Bloomberg Terminal | Dense grids, monospaced alignment, keyboard-first navigation | Extreme austerity, high training cost |
| Linear | Cmd+K palette, spring-based transitions, focus state design | Too minimal for ops density, common purple accent |

## Synthesized Design Principles

### P1: Triple-Coded Status (from ATC, PagerDuty, incident.io)
Never communicate status through color alone. Every status indicator uses at least two of: color, icon/shape, text label. Critical states use all three.

### P2: Command Center Focal Architecture (from FireHydrant)
An active incident is the user's entire world. The detail view should feel like a dedicated workspace, not a panel tacked onto a list.

### P3: Temporal Primacy (from FireHydrant, Grafana IRM)
Timeline is the backbone. Entries must be scannable, typed by category, and always show elapsed time.

### P4: Keyboard-First Action Model (from Linear, Bloomberg)
Primary actions must be keyboard-accessible. Command palette strongly indicated.

### P5: Signal-Over-Decoration (from ATC, Bloomberg)
Every visual element must carry information. No decorative waste.

### P6: Progressive Disclosure Under Pressure (from incident.io)
Show minimum for triage; reveal detail on deliberate interaction.

### P7: Persistent Access to Critical Actions (from FireHydrant)
"Declare Incident" accessible from any view, any time.

## Incident Data Model (Minimum Viable)

```
Incident: id, title, severity (SEV1-4), status (investigating/identified/mitigating/resolved),
  commander, affectedServices[], declaredAt, resolvedAt, duration, timeline[]

TimelineEntry: timestamp, type (detection/escalation/status_change/action/communication/resolution),
  actor, content

Service: id, name, status (healthy/degraded/disrupted/unknown),
  tier (critical/standard/auxiliary), team, uptimePercent

Person: id, name, role (IC/Responder/Observer), initials
```

## Weighted Scoring Matrix for Direction Selection

| Criterion | Weight |
|-----------|--------|
| Product Fit & Context Alignment | 25% |
| Task Efficiency & Cognitive Load | 20% |
| Information Clarity & Hierarchy | 20% |
| Visual Distinctiveness & Brand Longevity | 15% |
| Accessibility & Readability | 10% |
| Responsive Adaptation Suitability | 5% |
| Implementation Feasibility | 5% |

## Deliverable Structure (proven effective for fleet gauntlet)

1. PRODUCT_CONTEXT.md -- personas, journeys, data model, prohibited aesthetics
2. REFERENCE_LEDGER.md -- 8+ live-researched references with adopt/reject matrix
3. DESIGN_DIRECTIONS.md -- 3+ structurally distinct candidates, weighted scoring, UI Style Fingerprint
4. DESIGN_DNA.md -- complete visual spec with hex tokens, type scale, components, states, signature elements
5. DESIGN_CONTRACT.md -- binding FRAME contract: layout diagrams, component specs, state machines, keyboard behavior, data requirements with code, acceptance criteria (checkboxes), P0/P1/P2 priorities, freedom/constraint boundaries
6. evidence/manifests/aurora-contract.json -- evidence manifest

Key success factors:
- Explicit freedom/constraint split prevents both FRAME guessing and over-specification
- P0/P1/P2 priorities give FRAME clear implementation order
- Data requirements with sample code eliminate data-structure guessing
- Acceptance criteria as checkboxes make QA binary pass/fail
- UI Style Fingerprint (12 macro-composition dimensions) catches portfolio collisions before they happen
