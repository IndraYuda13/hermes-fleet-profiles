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

### 2. Multi-Milestone Timeline Ingestion & Automated Alert Scheduling
Hackathons and innovation competitions operate under tight, multi-phase deadlines (e.g., abstract cutoff in <24 hours, proposal in 5 days, video/demo in weeks):
- **High-Resolution Timeline Flyer Extraction:**
  - Downscaled images from messaging platforms blur compact date ranges in sequence cards. Crop individual milestone boxes at 100% resolution into scratch before running vision inspection.
  - Verify track-specific dates (e.g., general registration vs specialized AI Agents category deadlines).
- **Cross-Check Real-Time System Clock Against All Forwarded Contests:**
  - Query real system time (`date`) immediately upon receiving date queries. Check system timestamp against *all* forwarded messages, links, and quoted blurbs in the conversation session, not just the latest photos. A related competition mentioned earlier in chat may have a registration cutoff closing on the same calendar day (within hours), requiring an immediate proactive callout.
- **Canonical Timeline Documentation:**
  - Persist the chronological table in `docs/timeline-lomba.md` covering: Stage Name, Date Range, Requirements/Deliverables, Official Submission URLs, and Status.
- **Automated Milestone Alerts via Hermes Cron:**
  - When team members request reminders ("kasih notifikasi di tanggal penting biar ga lupa"), schedule one-shot alerts directly to the team's active channel via `hermes cron create` or Python `from cron.jobs import create_job`:
    ```bash
    hermes cron create \
      --name "Reminder-<Comp>-<Milestone>" \
      --deliver origin \
      --repeat 1 \
      "<min> <hour> <day> <month> *" \
      "Kirim pesan pengingat ke grup WhatsApp tim: [REMINDER: <Milestone>] <Actionable instructions & submission URL>"
    ```
  - **Delivery Routing:** Use `--deliver origin` in live sessions, or specify explicit platform targeting like `--deliver "whatsapp:<group_jid>@g.us"` when batching programmatically to ensure alerts land in the exact team group.
  - **Enforce Single-Shot Execution (`--repeat 1`):** Calendar-bound competition milestones must specify `--repeat 1` so they fire once, record completion, and do not linger perpetually across future years.
  - **Cadence for Multi-Week Submission Deadlines:**
    - *H-7 (09:00 WIB):* Verify prototype architecture and draft proposal structure (page limits, typography, required sections).
    - *H-3 (09:00 WIB):* Validate live demo deployment stability, public repository accessibility, and record video walkthrough.
    - *H-1 (09:00 WIB):* Final administrative audit (naming conventions like `<COMP>_<Category>_<TeamName>.pdf`, cover logos, originality statements).
    - *Hari-H Kickoff (09:00 WIB):* Morning prompt to test public URL access from outside networks and submit early.
    - *Hari-H Emergency (18:00 WIB):* Final warning 6 hours before midnight cutoff (23:59 WIB) to avoid portal congestion.
  - **Dual-Stage Alert Pattern for Same-Day/Registration Deadlines:** On high-stakes registration cutoff days (e.g. abstract submission closing at 18:00 WIB):
    1. *Morning kickoff alert* (e.g. 09:00 WIB): Outlines required fields, team composition checklist, and abstract word limit.
    2. *Emergency alert* (e.g. 15:30 WIB / 2.5h prior): Final call to submit form and resolve any network/form issues before the portal closes.
- **Contest Scope Triage & De-selection (Purging De-scoped Alerts):**
  - When the team drops or opts out of a competition ("yang X catet, yang Y gausah"), immediately remove its scheduled cron jobs (`hermes cron remove <id>`) so the channel is not spammed with urgent countdowns for an abandoned track.
  - Update `docs/timeline-lomba.md` to mark the dropped contest as cancelled/out-of-scope and re-anchor documentation around the sole active target.
  - Audit the remaining competition's alert schedule for full pipeline coverage: ensure early gating milestones (initial proposal/registration deadlines and qualification announcement dates) have active alerts, not just later video/code submission dates weeks away. Missing an early gate prevents reaching the final stage entirely.

### 3. Scaffold the Competition Workspace
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

### 4. Establish Team Role Alignment (The 3H Model)
Map responsibilities across the three classic hackathon pillars:
- **Roster & Context Isolation:** Never project or assume rosters from academic coursework, university capstone/Tugas Akhir, previous hackathon teams, or unrelated projects. Different competitions have distinct team compositions; confirm team members and handles strictly from the official competition registration, project README, or direct user statement before mentioning names in proposals or conversation.
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

### 5. Divergent Raw Ideation Intake (Zero-Judgement Pool)
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

### 6. Triage and Selection Rubric
During the team review meeting, filter raw ideas using a 5-dimension score (1-5 each):
1. **Brief & Theme Fit:** Does it directly solve the organizer's target challenge?
2. **Feasibility (48-72h Slice):** Can a functional slice (not static mockups) be finished within the hackathon timeline?
3. **Demo Impact & WOW Factor:** Is the autonomous loop / agentic capability visibly demonstrable to judges?
4. **Deliverable Viability:** Does it naturally support a 15-page case study and 3-minute video walkthrough?
5. **Team Skill Synergy:** Does it fit the team's combined 3H strengths without severe external dependencies?

### 7. Deliverables Hardening
- **Live Interface:** Deploy with public SSL on high-availability infrastructure; test on external networks and incognito sessions to verify no local environment leakage.
- **Proposal / Case Study:** Audit margins (e.g. 4-3-3-3 cm), font (TNR 12pt, 1.5 line spacing), and page budget strictly. Include required cover logos and system architecture diagrams.
- **Video Walkthrough (3-5 min):**
  - 0:00 - 0:30: Problem hook & urgency (Hustler)
  - 0:30 - 1:00: Solution concept & value prop (Hustler / Hipster)
  - 1:00 - 3:00: Live, unedited walkthrough of working prototype (Hipster / Hacker)
  - 3:00 - 4:00: System architecture, tool integrations, and impact metrics (Hacker / Hustler)

### 8. Public Repository Sanitization & Anti-Leak Audit
Before submitting a public Git repository or opening it for evaluation:
1. **Scrub AI/Agent Slop & Internal Tool References:**
   - Grep the entire repository (code, comments, docs, `.env.example`, tests) for mentions of AI tools or internal agent names (e.g., `Codex`, `Claude`, `Hermes`, `AGENTS.md`, `SENTINEL`, `ORION`, `FRAME`, `PRISM`).
   - Replace internal audit or multi-agent governance tags with professional technical commentary (e.g. `// Defense in depth security layering`, `// Authenticate before parsing request body`).
2. **Prevent Broken Build & Release Scripts from Gitignored Files:**
   - When files like `AGENTS.md`, temporary notes, or local `artifacts/` are removed or added to `.gitignore`, grep all build and release scripts (e.g. `release-manifest.mjs`, package scripts) to ensure no hardcoded paths throw runtime `ENOENT` crashes.
3. **Audit Documentation Links:**
   - Grep `docs/` for broken relative links pointing to deleted artifact folders (`../artifacts/qa/`) or removed internal guidelines.
4. **Enforce Automated Verification Gates:**
   - Run code style checks: `pnpm format:check` (fix with `pnpm format` or `prettier --write`).
   - Run linter: `pnpm lint` with `--max-warnings=0`.
   - Run typechecker: `pnpm typecheck` (or `tsc --noEmit`).
   - Ensure clean working tree and zero lint/type regressions.
5. **Audit Git Author & Commit Provenance:**
   - Inspect all commit authors via `git log --format='%an <%ae>' | sort -u`.
   - Ensure bot or synthetic email handles (e.g., `*@fleet.local`, `*@*.invalid`, `*Fleet*`) are not exposed as authors on public competitive deliverables.

---

## Pitfalls

- **Failing to cross-reference system clock against earlier forwarded announcements:** Focusing only on the most recent photo's deadline (e.g. weeks away) while ignoring an earlier forwarded blurb whose registration closes today (within hours) causes missed entry windows. Always verify `date` against all contests discussed in session.
- **Omitting `--repeat 1` on calendar-specific competition milestone cron jobs:** Leaving repeat unbounded causes jobs to linger indefinitely in scheduler state after execution. Enforce single-shot execution (`--repeat 1`).
- **Conflating competition rosters with academic, capstone, or other contest teams:** Assuming team members from previous hackathons or coursework belong to the current competition roster leads to misattributed authors in proposals and embarrassing corrections. Always verify the exact project roster from official registration or direct confirmation.
- **Leaving AI bot personas or agent names in public code comments and documentation:** Hardcoded references to LLM bots ("Codex", "AGENTS.md", fleet personas) in source code, `.env.example`, or specs signal uncurated AI generation to judges and invite scrutiny. Sanitize all comments to standard technical language.
- **Breaking release/manifest scripts when gitignoring local artifacts:** Removing `AGENTS.md` or `artifacts/` without updating build or release manifest scripts that stat those paths causes build failures in clean environments. Grep scripts whenever files are untracked.
- **Neglecting code style formatting before submission:** Code committed during rapid hackathon sprints often skips prettier; failing `pnpm format:check` in CI creates an unpolished impression.
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
- **Relying on full-overview downscaled images to read dense timeline flyers:** Infographics with multiple sequence cards blur dates when downscaled to fit model context. Crop individual stage cards at full resolution into scratch before running vision inspection to avoid misreading dates and deadlines.
- **Forgetting `--repeat 1` on one-off competition date reminders in cron:** Omitting `--repeat 1` leaves the cron job scheduled with repeat infinity (`∞`), meaning it lingers indefinitely after firing once and risks re-triggering in future years. Always set `--repeat 1` for calendar-specific competition milestones.
- **Scheduling deadline reminders too close to the cutoff:** Alerting the team 30 minutes before an abstract or proposal deadline gives zero buffer for team sign-off, formatting, or portal network lag. Always schedule a morning kickoff alert (e.g. 09:00 WIB) and an emergency alert H-4 hours before the portal closes.
- **Leaving scheduled cron alerts active after a competition is de-scoped:** Failing to purge cron jobs when a user decides not to pursue a contest ("yang X catet, yang Y gausah") causes confusing urgent alerts and ping spam on deadlines the team already abandoned. Immediately remove associated cron jobs upon de-selection.
- **Scheduling alerts only for final deliverables while skipping early qualification gates:** Setting reminders only for final code/video submissions (weeks out) while neglecting initial proposal/registration deadlines (days out) leads to silent disqualification. Always audit and schedule alerts across the full pipeline (registration/proposal -> qualification announcement -> final deliverables).
