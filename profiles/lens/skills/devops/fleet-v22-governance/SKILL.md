---
name: fleet-v22-governance
description: Fleet V2.2 Quality Governance standard for multi-agent software projects, defect ledgers, revision integrity, disk guards, and role-scoped MCP architecture.
version: 2.2.0
author: Hermes Fleet Architecture
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [governance, quality, git-revision, defect-ledger, disk-guard, mcp-roles, fleet-v22]
    category: devops
    requires_toolsets: [kanban, terminal, file]
environments:
  - kanban
  - agent
---

# Fleet V2.2 Quality Governance Standard

Systemic operating rules for multi-agent software engineering, visual QA, functional verification, and fleet architecture integrity.

## Core Governance Rules

### Rule 1: Revision Integrity Gate
- For software projects managed in Git, establish a final Git commit SHA after implementation/remediation.
- PRISM, LENS, SENTINEL, and ORION final synthesis MUST record the exact same Git commit SHA in their reports and metadata.
- Any source code change made after a PASS invalidates every affected PASS and requires corresponding verification again.
- ORION must refuse `FINAL VERIFIED` when final-source revision and verification revisions differ.

### Rule 2: Defect Disposition Ledger & Interactive Mutation Verification
- Every P0/P1/P2 visual or functional finding must be recorded with explicit status: `RESOLVED` or `ACCEPTED`.
- If `ACCEPTED`, a clear rationale, impact assessment, and tradeoff analysis must be documented.
- Findings may NOT silently disappear or be labeled merely "ignored".
- P0/P1 defects may NEVER be accepted for final release unless the user explicitly authorizes an override.
- **Interactive Mutation Rule (LENS/PRISM):** Visual QA is forbidden from relying purely on static page load snapshots. QA workers MUST execute interactive mutations (clicking theme toggles, currency switches, privacy masks, tabs, modals) and assert computed CSS/DOM changes (e.g. background-color RGB mutation) before declaring PASS.
- **Framework Version Rule (FRAME/FORGE):** When using new framework major versions (e.g. Tailwind CSS v4), do not assume legacy selector behaviors (like `.dark` class). Explicit variants (e.g. `@custom-variant dark`) and live rendered styles must be verified.

### Rule 3: Disk & Artifact Guard
- Check root free disk space (`df -h /`) before spawning heavyweight browser QA or installing browser/runtime dependencies:
  - **≥8 GB:** Normal execution.
  - **5–8 GB:** Warning state. Avoid redundant browser/runtime installations.
  - **<5 GB:** Block new heavyweight browser installations (`playwright install`).
  - **<3 GB:** Block new heavyweight browser QA runs.
  - **<2 GB:** Block new Kanban worker dispatches.
- Browser caches, recordings, and temporary screenshot artifacts must be cleaned after visual QA where safely reconstructable.
- **NEVER** delete user project source files, credentials, databases, production Docker data, or unrelated services.

### Rule 4: Resource Ownership & Role-Scoped MCP Architecture
Maintain strict role-scoped capability assignment. Do not load heavy MCP servers into unassigned profiles for convenience.
- **ORION (Chief of Staff):** Lightweight orchestrator. Must NOT acquire Playwright, Puppeteer, Postman, Canva, Firecrawl, GitHub, memory MCP, or sequential-thinking MCP. Delegate capability to specialists.
- **LENS / FRAME:** Visual QA, Playwright browser automation, cross-browser rendering inspection.
- **AURORA:** Product design, Canva MCP, visual architecture, design thesis.
- **FORGE:** Software engineering, GitHub MCP, Postman MCP, API integration.
- **RADAR:** AI & technology intelligence, Firecrawl web MCP.
- **PRISM:** Quantitative data science, functional regression, analytics verification.
- **SENTINEL:** Security audit, risk review, vulnerability scan, final correctness gate.
- **ATLAS:** Infrastructure, DevOps, Linux, container reliability.
- **QUANT:** Market and trading research.
- **NEXUS:** Personal operations and administration.

## Verification Checklist

- [ ] Exact Git commit SHA verified across PRISM, LENS, SENTINEL, and ORION.
- [ ] Defect Disposition Ledger complete (0 unclassified P0/P1/P2 items).
- [ ] Root free disk space checked before browser runs; temp artifacts cleaned post-QA.
- [ ] Role-scoped MCP architecture respected without capability creep on ORION.
