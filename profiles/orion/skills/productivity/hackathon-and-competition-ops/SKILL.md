---
name: hackathon-and-competition-ops
description: "Use when entering hackathons or tech innovation contests."
---

# Hackathon and Competition Operations

A structured playbook for hackathons, innovation challenges, and agentic/software competitions from rule ingestion to submission.

## When to Use

- Preparing for hackathons, case competitions, or innovation challenges.
- Ingesting competition guidebooks, rules, and scoring rubrics.
- Facilitating multi-member brainstorming and managing raw idea intake before team meetings.
- Aligning team roles under the Hacker-Hipster-Hustler (3H) model.
- Evaluating and filtering idea candidates into viable competition submissions.
- Hardening deliverables (live web prototype, case study proposal, video demo, public repository).

---

## Procedure

### 1. Ingest Competition Rules and Brief
Extract and record hard constraints before any technical development:
- **Scope & Grand Theme:** Target problem space, industry focus, and sub-themes.
- **Team Eligibility & Composition:** Permitted team sizes, multi-campus allowances, and required role competencies.
- **Deliverables Matrix:**
  - Live public demo URL (e.g. Vercel, VPS, Streamlit)
  - Public code repository or workflow export
  - Written proposal or UX case study (format, page budget, typography, margin rules, mandatory cover logos)
  - Video demo (duration limit, hosting platform, required segments)
  - Statement of originality / administrative forms
- **Timelines:** Registration deadline, abstract deadline, prototype submission, and pitching rounds.

*Rule:* Transcribe image-based or PDF guidebook pages into persistent Markdown in `docs/<competition>-notes.md` immediately; ephemeral message attachments and image caches expire.

### 2. Scaffold the Competition Workspace
Establish an isolated, versioned project directory:
```text
<competition-workspace>/
├── README.md                  # Overview, deliverables checklist, deadlines
├── docs/                      # Guidebook transcriptions, scoring rubrics, API specs
├── ide/
│   ├── raw-ideas.md           # Unfiltered idea ledger across all team members
│   ├── detail/                # Verbatim long-form proposals or specs (e.g. 001-<slug>.md)
│   └── shortlisted-concept.md # Polished concept chosen after triage
└── src/                       # Working prototype source
```

### 3. Establish Team Role Alignment (The 3H Model)
Map responsibilities across the three classic hackathon pillars:
- **Hacker (The Builder / Tech):**
  - Architecture, AI/LLM integration, tool calling, RAG pipelines, API keys.
  - Deployment, database, and backend reliability.
  - Goal: Ensure the prototype executes reliably and does not fail during live demo.
- **Hipster (The Designer / UI-UX / Aesthetic):**
  - User journeys, interaction design, visual identity, and front-end polish.
  - Presentation slide deck typography and layout.
  - Goal: Make the product intuitive, visually distinctive (anti-slop), and effortless for judges to understand.
- **Hustler (The Business / Pitcher / Storyteller):**
  - Problem validation, business model, ROI/efficiency metrics.
  - Pitch narrative, script writing, video narration, and live Q&A defense.
  - Goal: Convince judges of real-world necessity, market viability, and financial/operational impact.

### 4. Divergent Raw Ideation Intake (Zero-Judgement Pool)
When collecting ideas from team members prior to a sync meeting:
- **Zero-Critique Rule:** Record every proposal without debating, filtering, or forcing premature design specs during intake.
- **Two-Tier Idea Logging:**
  1. *Structured Ledger (`ide/raw-ideas.md`):* Log each entry with standard schema:
     - `ID & Title`
     - `Proposer (Member)` & `Date Added`
     - `Problem Addressed`
     - `Proposed Solution & Core Flow`
     - `Design Highlights & Guardrails` (deterministic vs LLM split, human-in-the-loop snapshot binding)
     - `Document Status & Source Link`
     - `Technical / Functional Tags` (e.g. Enterprise, Procurement, Automation, HITL)
  2. *Verbatim Document Archival (`ide/detail/<id>-<slug>.md`):* Whenever a member submits a long-form draft, concept document, or multi-page spec, store the exact text unmodified alongside the ledger summary so that edge cases, calculations, and boundaries are preserved.
- Maintain 3 explicit zones in the ledger:
  - 💡 **Active Raw Pool:** All incoming ideas.
  - 🅿️ **Parking Lot:** Promising but unverified ideas needing pre-meet research.
  - 🚮 **Discarded / Out-of-Scope:** Formally rejected post-meeting with a 1-line reason.

### 5. Triage and Selection Rubric
During the team review meeting, filter raw ideas using a 5-dimension score (1-5 each):
1. **Brief & Theme Fit:** Does it directly solve the organizer's target challenge?
2. **Feasibility (48-72h Slice):** Can a functional slice (not static mockups) be finished within the hackathon timeline?
3. **Demo Impact & WOW Factor:** Is the autonomous loop / agentic capability visibly demonstrable to judges?
4. **Deliverable Viability:** Does it naturally support a 15-page case study and 3-minute video walkthrough?
5. **Team Skill Synergy:** Does it fit the team's combined 3H strengths without severe external dependencies?

### 6. Deliverables Hardening
- **Live Interface:** Deploy with public SSL on high-availability infrastructure; test on external networks and incognito sessions to verify no local environment leakage.
- **Proposal / Case Study:** Audit margins (e.g. 4-3-3-3 cm), font (TNR 12pt, 1.5 line spacing), and page budget strictly. Include required cover logos and system architecture diagrams.
- **Video Walkthrough (3-5 min):**
  - 0:00 - 0:30: Problem hook & urgency (Hustler)
  - 0:30 - 1:00: Solution concept & value prop (Hustler / Hipster)
  - 1:00 - 3:00: Live, unedited walkthrough of working prototype (Hipster / Hacker)
  - 3:00 - 4:00: System architecture, tool integrations, and impact metrics (Hacker / Hustler)

---

## Pitfalls

- **Truncating detailed specs into lossy summaries during intake:** Summarizing multi-page member proposals into a few bullet points loses critical boundary definitions, configuration rules, and edge-case policies. Always copy the full text into `ide/detail/<id>-<slug>.md`.
- **Blurring deterministic code and LLM reasoning in agentic proposals:** Treating agent systems as purely prompt-driven invites severe safety and hallucination penalties from judges. Clearly delineate deterministic controls (threshold calculation, budget caps, approval locks, deduplication) from probabilistic LLM roles (parsing, dialogue, negotiation).
- **Critiquing during raw intake:** Debating feasibility while logging ideas suppresses participation and causes team members to withhold unconventional high-potential concepts.
- **Relying on ephemeral screenshot caches:** Guidebook screenshots and temporary image URLs expire; transcribe competition rules and grading rubrics into persistent Markdown files immediately.
- **Submitting conversational chatbots for agentic prompts:** Building a generic chat interface fails when competitions ask for Agentic AI; always implement explicit tool calling, external API integrations, or multi-step execution.
- **Postponing deployment until deadline day:** SSL certificate issuance, CORS configuration, and public DNS propagation routinely fail under last-minute pressure; deploy a hello-world container on day one.
- **Ignoring layout and formatting requirements:** Submitting proposals that exceed page caps or omit required cover logos results in administrative disqualification before technical judging starts.
