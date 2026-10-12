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
- **Scoring Rubric vs. Domain Methodology:**
  - Disentangle **Formal Rubric Criteria** (the explicit scoring dimensions like Innovation & Relevance 30%, Impact 20%, Sustainability 15%) from **Domain Solution Methodologies** (pedagogical, operational, or algorithmic frameworks used to solve the problem, e.g., TaRL, BKT, TRIZ).
  - Explicitly map each solution pillar into its corresponding scored rubric dimension so the pitch and concept paper directly maximize rubric points.
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
- **Roster & Context Isolation:** Never project or assume rosters from academic coursework, university capstone/Tugas Akhir, or commercial projects. Confirm team members and handles strictly from competition registration documents, project README, or recent git commit logs (`git log --format='%an <%ae>'`).
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
- **Read the whole ledger before numbering.** Read the full `ide/raw-ideas.md` (or grep `^### `) to find the highest existing ID. A partial read produces duplicate IDs, and IDs are the reference used at the meeting.
- **Dedupe by problem and solution, not by wording.** Members often rename the same option (for example a generic label like "Opsi 1" versus a plain-language description of the same thing). Before adding an item, search the ledger for the synonyms and the option label, and search the chat history if the user points to an earlier option. A re-mention becomes a dated annotation on the existing entry, not a new ID. Why: a second ID splits one decision across two entries at triage.
- **Keep the proposer's words.** Store the exact quote of the idea next to the structured fields, so the later triage can re-read the original intent.
- **Flag ambiguous terms instead of resolving them.** Record the literal reading in the Catatan field and list the open question for the meeting. Do not present a guessed meaning as fact.
- **Keep raw items unscored.** No verdicts, rankings, or "not final" disclaimers on new entries. Scoring belongs to the triage step below.
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

- **Conflating competition rosters with academic or capstone teams:** Assuming the user's academic capstone or course group members are on the hackathon team leads to incorrect role delegation, misattributed authors in proposals, and flawed presentation assignments. Verify the team roster directly from project git history or competition registration docs.
- **Conflating domain solution methodologies with formal scoring rubrics:** Mistaking a core methodology (e.g., TaRL, TRIZ, Lean Canvas) for a standalone grading category—or vice versa—obscures where points are actually won or lost. Map each domain pillar to its corresponding weighted rubric aspect (e.g. Innovation vs Impact) and verify against the official guidebook criteria before drafting pitch decks or papers.
- **Truncating detailed specs into lossy summaries during intake:** Summarizing multi-page member proposals into a few bullet points loses critical boundary definitions, configuration rules, and edge-case policies. Always copy the full text into `ide/detail/<id>-<slug>.md`.
- **Blurring deterministic code and LLM reasoning in agentic proposals:** Treating agent systems as purely prompt-driven invites severe safety and hallucination penalties from judges. Clearly delineate deterministic controls (threshold calculation, budget caps, approval locks, deduplication) from probabilistic LLM roles (parsing, dialogue, negotiation).
- **Critiquing during raw intake:** Debating feasibility while logging ideas suppresses participation and causes team members to withhold unconventional high-potential concepts.
- **Appending a duplicate when a member re-mentions an idea under a new name:** Two IDs for one idea split the triage decision and waste meeting time. Search for the synonym first and annotate the existing entry (see step 4).
- **Numbering from a partial read of the ledger:** Duplicate or skipped IDs break cross-references in the meeting notes. Read or grep the whole file before writing a new ID.
- **Updating a summary count by memory:** Documents that state an ID range (for example "Ide 001-010") go stale when items are added. Grep the docs folder for the old range after every append and update it.
- **Relying on ephemeral screenshot caches:** Guidebook screenshots and temporary image URLs expire; transcribe competition rules and grading rubrics into persistent Markdown files immediately.
- **Trusting a claimed rubric item without checking the source:** a teammate (or the user) may believe a scoring criterion exists (e.g. 'TaRL is scored') when the guidebook contains no such line. Extract the real scoring table from the original PDF — OCR image-based pages too — and verify every claimed criterion against it before designing deliverables around it.
- **Submitting conversational chatbots for agentic prompts:** Building a generic chat interface fails when competitions ask for Agentic AI; always implement explicit tool calling, external API integrations, or multi-step execution.
- **Postponing deployment until deadline day:** SSL certificate issuance, CORS configuration, and public DNS propagation routinely fail under last-minute pressure; deploy a hello-world container on day one.
- **Ignoring layout and formatting requirements:** Submitting proposals that exceed page caps or omit required cover logos results in administrative disqualification before technical judging starts.
