---
name: fleet-defect-rembukan
description: Use when runtime defects need fleet briefing & Kanban.
version: 1.0.0
author: Hermes Fleet Architecture
metadata:
  hermes:
    tags: [orchestration, defect-lifecycle, multi-agent, rembukan, kanban, fleet-governance]
    category: autonomous-ai-agents
    requires_toolsets: [kanban, terminal]
---

# Fleet Defect Briefing & Collaborative Rembukan Protocol

Use this skill when encountering any runtime failure, API contract rejection (e.g. rate limits, single-flight constraints like `transactionsBeingChecked`), memory bloat, or system anomaly.

## Core Rule: Zero-Solo Invariant (No Heroics)
ORION is Chief of Staff and Quality Governor. When a defect or unexpected runtime behavior is observed:
1. **Never stop at just an explanation or attempt to resolve/silence it alone.**
2. **First isolate and discover the root cause.**
3. **Immediately brief all relevant specialist profiles via native A2A (`a2a_orchestrate`).**
4. **Dispatch collaborative remediation tasks to domain owners via Kanban (`kanban_create`).**
5. **Ensure operational deployment includes cache invalidation headers and Git remote push verification before declaring completion.**

## 4-Step Defect Remediation Flow

```
[1. Discover & Isolate] ──► [2. Fleet Briefing via A2A] ──► [3. Kanban DAG Dispatch] ──► [4. Independent QA Gate]
  - Trace logs & errors       - a2a_orchestrate briefing      - FORGE: Logic & backend        - PRISM: Invariant assertions
  - Pin upstream semantics    - Domain-specific prompts       - FRAME: UI states & locks      - LENS: Visual presentation
  - Determine blast radius    - Collect rembukan designs      - ATLAS: SRE & daemon guards    - ORION: Final gate closure
```

### Step 1: Discover & Isolate
- Inspect runtime logs and API responses to isolate the exact error code or constraint.
- Classify whether the defect is a logical conflict, state desync, concurrency race, or upstream policy limit.

### Step 2: Fleet Briefing via Native A2A
- Broadcast a clear, structured briefing to the fleet using `a2a_orchestrate(capability="*")`:
  - **Konteks Masalah**: Error snippet, impacted accounts/services.
  - **Akar Masalah**: Underlying cause (e.g. single-flight pending transaction limit).
  - **Area Tinjauan**: Questions for FORGE (logic), FRAME (UI), PRISM (tests), ATLAS (SRE), SENTINEL (security).

### Step 3: Collaborative Kanban DAG Dispatch
- Create structured Kanban cards assigning distinct ownership:
  - **Backend/Logic**: State machine, backoff timers, error suppression (assigned to FORGE).
  - **Frontend/UI**: State-aware badges, action button safety locks, tooltips (assigned to FRAME).
  - **Infra/SRE**: Log rotation, cgroup memory caps, service recovery (assigned to ATLAS).
  - **QA & Verification**: Zero-spam assertions, test matrices (assigned to PRISM / LENS).
- **Native Kanban Toolset Invariant:** Always execute Kanban operations (`kanban_create`, `kanban_list`, `kanban_show`, `kanban_complete`, etc.) via native function calls rather than executing `hermes kanban ...` via the `terminal` tool. Native tools operate directly against SQLite DB (`~/.hermes/kanban.db`), avoiding process overhead, quoting bugs, and interactive shell issues. Reserve `terminal` strictly for invoking the background dispatcher (`hermes kanban dispatch`) if immediate manual promotion is required.

### Step 4: Independent Verification & Synthesis
- Implementer profiles complete work and hand off structured metadata.
- Verifier profiles execute independent tests and prove invariant compliance before closing cards.
- ORION synthesizes the final outcome for the user with reproducible evidence.

## Fleet Product Improvement Audits
For open-ended improvement audits and architecture reviews, see `references/fleet-product-improvement-audit.md` for the full grounding, dispatch, and synthesis protocol (includes Kanban CLI body injection pitfall).

For static HTML/JS storefront audits specifically (digital product stores, catalogs), see `references/static-site-storefront-audit.md` for a reusable checklist covering server, performance, mobile UX, data quality, security, and conversion.

For third-party provider incident triage (such as business email outbound suspensions `554 5.7.1 Outbound sending is disabled` on Hostinger/cPanel), see `references/business-email-outbound-suspension.md` for the triage checklist, mandatory password reset, and Hostinger Live Chat unsuspend procedure.

## Multi-Agent Web Pipeline Pitfalls & Best Practices
- **Editable Install / Finder Namespace Guard:** When executing Kanban CLI tasks or custom subprocesses inside Hermes virtualenvs, ensure package namespace paths like `hermes_state_holders.py` are properly resolvable via `.pth` or PYTHONPATH so `_connect()` / `kanban_create` does not fail with `ModuleNotFoundError`.
- **Kanban Card Title Invariant:** Always provide an explicit `title` in `kanban_create` dict payloads; omitting title will be rejected immediately by the tool schema.
- **Split-Stream Video Architectures:** When orchestrating video streaming from providers with separate DASH/video-only and audio-only streams (e.g. Bstation), enforce zero-transcode remuxing (`ffmpeg -c:v copy -c:a copy -movflags frag_keyframe+empty_moov -f mp4 pipe:1`) at the FORGE layer to guarantee sub-second initial playback latency without CPU exhaustion.

