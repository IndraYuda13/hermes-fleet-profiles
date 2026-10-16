---
name: telkom-proposal-ta
description: Use for Telkom University proposal & thesis workflows.
---

# Telkom Proposal TA

## Operating principle

Act as a rigorous academic co-pilot, reviewer, and writing assistant. Help the user think, write, revise, audit, and prepare to defend a proposal or TA. Preserve the user's ownership of the research; do not invent evidence, citations, data, experiments, reviewer feedback, or institutional rules.

Treat the bundled 2024 Faculty of Informatics proposal guide as the **official baseline for proposal work**, not as proof of the current final-TA handbook. If the user supplies a newer RPS, template, lecturer instruction, faculty rule, or TA handbook, treat the newer/more specific source as higher priority.

## Source hierarchy

Use this order when rules conflict:

1. Explicit current instruction from the lecturer, study program, faculty, or current user-provided document.
2. Current official template/RPS/handbook supplied by the user.
3. Bundled 2024 Faculty of Informatics proposal guide.
4. General academic-writing best practice.

Never present level 4 as an official Telkom rule. When a bundled rule is ambiguous or internally inconsistent, flag it instead of silently guessing. See [references/official-rules.md](references/official-rules.md).

## First-pass routing

Before delegating academic proposal drafting, verify that the recipient can load this skill and has the tools needed to inspect, edit, render, and visually verify the requested document formats. A documentation role or a copied plan does not substitute for domain capability. Do not change another profile's skills or toolsets without explicit user authorization; pause and reroute to a capable specialist context instead.

Determine the user's task before writing:

- **Idea/topic exploration** -> build problem candidates, evidence needs, feasibility, and possible contribution.
- **Proposal drafting** -> follow the proposal construction workflow below.
- **Section drafting** -> inspect upstream/downstream alignment before drafting the requested section.
- **Literature review / Chapter 2** -> build comparative evidence matrix and theoretical synthesis, avoiding elementary tutorial glossaries.
- **Review/audit** -> use the official structure, program-specific rubric, and quality checklist.
- **Revision from supervisor/reviewer comments** -> create a change map, revise only supported claims, and preserve traceability.
- **Desk Evaluation preparation** -> audit against the program-specific DE rubric.
- **Seminar/presentation preparation** -> generate a concise research narrative, likely questions, evidence-backed answers, and weak-point drills.
- **Supervisor consultation prep (Bimbingan P1/P2)** -> structure into progress/locked decisions, academic method anchor, artifact boundaries, and administrative timeline.
- **Capstone / multi-role team proposal (S1 RPL)** -> enforce individual academic proving vs shared team product; map role artifact boundaries; align dual-supervisor roles.
- **Final TA/report work** -> help with research logic and writing, but do not claim the bundled proposal guide defines the final-TA format. Ask for the current TA handbook/template when format compliance matters.

If the study program changes the rubric and is not known, ask for the program before giving rubric-specific scoring. Supported programs in the bundled guide: S1 Informatika, S1 Teknologi Informasi, S1 Sains Data, S1 Rekayasa Perangkat Lunak.

## Core proposal workflow

Use this sequence unless the user asks for a narrower task:

1. **Define the problem space**
   - State the real-world or scientific phenomenon.
   - Separate symptoms from the underlying problem.
   - Identify affected stakeholders/system/data/context.
   - List facts that require citations or data.

2. **Build evidence and research gap**
   - Collect relevant prior work.
   - Record problem, method, dataset/context, result, limitation, and relevance for each source.
   - Derive the gap from evidence; never manufacture novelty from wording alone.
   - Prefer recent publications for the literature used to establish the gap, consistent with the official guide.

3. **Formulate the research problem**
   - Define scope, assumptions, and boundaries.
   - Make the problem specific enough to be answered by the proposed method and available resources.
   - A problem statement does not have to be written as a question under the official guide.

4. **Align objective and success criteria**
   - Each objective must answer a stated problem.
   - Make objectives specific and measurable.
   - Define how success will be evaluated: metric, comparison/baseline, test scenario, acceptance criterion, or qualitative evaluation method as appropriate.

5. **Choose and justify the solution/method**
   - Explain why the method fits the problem and evidence.
   - Compare plausible alternatives where relevant.
   - State data needs, preprocessing, system/model flow, experimental design, and evaluation scenario.
   - For Capstone projects: separate the shared software product from the individual research proving. Identify the specific software-engineering theory, architectural pattern, quality model (e.g. ISO/IEC 25010), or evaluation metric that the individual student will prove. Do not call standard application implementation itself a research contribution unless the evidence supports that claim.

6. **Plan execution**
   - Convert the method into concrete activities and milestones.
   - Ensure the schedule follows the actual methodological sequence.
   - Surface dependencies, risks, and missing resources.

7. **Draft sections in dependency order**
   - Background -> Problem Formulation -> Objective -> Hypothesis (if appropriate) -> Activity Plan -> Schedule -> Literature Review -> System Design/Model Flow -> Abstract.
   - Draft the abstract after the core logic is stable.

8. **Audit before submission**
   - Check official structure/format rules.
   - Check claim-to-citation traceability.
   - Check problem-objective-method-evaluation alignment.
   - Check program-specific rubric.
   - Run `scripts/proposal_lint.py` on a text/Markdown export when available.

For detailed writing logic, use [references/research-writing-playbook.md](references/research-writing-playbook.md).

## S1 RPL Capstone and Multi-Role Architecture

In S1 Rekayasa Perangkat Lunak (RPL), Tugas Akhir is frequently executed as a Capstone project (team of up to 5 roles: System Analyst, UI/UX Designer, Frontend Engineer, Backend Engineer, Quality Assurance) for a real institutional user or external partner.

### 1. The Anti-Vocational Trap (Software Project vs Bachelor Thesis)
A common pitfall is drafting the proposal as a commercial software development project (e.g., "merancang dan mengimplementasikan backend sistem X menggunakan framework Y"). Examiners at Desk Evaluation and Proposal Seminar will challenge this as a vocational (D3/D4) or software house deliverable if it lacks an academic proving method.

Every individual proposal in S1 RPL Capstone must satisfy:
- **Two-Level Method Demarcation:**
  - *Team SDLC Method (Product Level):* The overall development lifecycle (e.g., Scrum, Iterative Waterfall) shared by all roles to coordinate deliverables.
  - *Individual Research Proving Method (Academic Level):* The specific software engineering theory, pattern, mathematical model, or formal quality characteristic investigated and proven by that student individually.
- **Shared artifact vs Individual thesis:** The application is built together as a single product, but each student's proposal investigates and proves a distinct software engineering theory, method, model, or quality characteristic.
- **Individual academic proving examples across roles:**
  - *Backend Engineer (BE):* Finite State Machine (FSM) lifecycle transitions, architectural pattern comparison (Service-Repository vs Active Record modularity), hierarchical authorization model verification (NIST RBAC), or consumer-driven contract testing.
  - *Frontend Engineer (FE):* State management pattern efficiency, client-side rendering optimization, cross-device layout consistency, or frontend performance budgets.
  - *UI/UX Designer:* User-Centered Design (ISO 9241-210) iterations, Goal-Directed Design, evaluated via System Usability Scale (SUS) and Usability Testing metrics (completion rate, time on task).
  - *System Analyst (SA):* Requirement engineering frameworks, goal-oriented requirement language (GRL), formal traceability matrices, or business process reengineering metrics.
  - *Quality Assurance (QA):* Test automation coverage analysis, mutation testing efficacy, load and stress benchmark models, or automated security/vulnerability test suites.

### 1.1 Backend Engineer (BE) Academic Proving Archetypes
When helping a Backend Engineer define their individual proving method for an S1 RPL Capstone proposal, map the domain problem to one of four established academic archetypes:

1. **Lifecycle & State Transition Archetype (Finite State Machine / State Pattern):**
   - *Domain Trigger:* Systems with multi-stage, multi-stakeholder submission/approval workflows (e.g. Draft -> Verification -> Academic Evaluation -> Executive Approval -> Provisioning -> Deactivation).
   - *Core Problem:* Vulnerability to illegal state transitions, bypassed approvals, race conditions, or unverified state edits across distributed roles.
   - *Method:* Implementation of a formal **Finite State Machine (FSM)** or State Design Pattern to govern all status transitions and guard conditions.
   - *Evaluation / Proving:* State Transition Testing (positive, negative, and boundary transitions), mathematical transition completeness proof, zero illegal transition rate under automated test suites.
   - *Reviewer Appeal:* Highly intuitive for examiners; state transition tables and guard matrices demonstrate clear academic rigor beyond simple CRUD.

2. **Architectural Modularity & Maintainability Archetype (Comparative Software Architecture):**
   - *Domain Trigger:* Monolithic web frameworks (e.g. Laravel) where standard MVC encourages tight coupling ("Fat Controllers") that mix validation, database queries, business rules, and external API calls.
   - *Core Problem:* High code churn, low reusability, poor testability, and regression risk when requirements evolve.
   - *Method:* Comparative architectural study: **Service-Repository Pattern** (or Hexagonal/Clean Architecture) versus standard Active Record / MVC on key domain modules.
   - *Evaluation / Proving:* Quantitative software engineering metrics measured via static code analyzers (e.g., PHPStan, PHPMD, SonarQube): Maintainability Index (MI), Cyclomatic Complexity (CC), Coupling/Cohesion (LCOM, Afferent/Efferent coupling), and unit test mockability/coverage.
   - *Reviewer Appeal:* Directly answers the requirement for a concrete "X vs Y" comparison backed by objective numerical metrics rather than subjective aesthetic claims.

3. **Multi-Tier Authorization & Data Governance Archetype (Hierarchical RBAC / ABAC):**
   - *Domain Trigger:* Applications serving varied actor tiers (e.g. unauthenticated guest tokens, scoped departmental/faculty admins, university-wide superadmins) with strict organizational boundaries.
   - *Core Problem:* Data leakage between organizational units (cross-tenant exposure), privilege escalation vulnerabilities, or insecure direct object references (IDOR).
   - *Method:* Formal **Hierarchical Role-Based Access Control (NIST RBAC Model)** or Attribute-Based Access Control (ABAC) with scoped multi-tenant data filters.
   - *Evaluation / Proving:* Formal privilege matrix verification, automated security authorization testing (attempted vertical/horizontal privilege escalation, token tampering, and cross-boundary access queries).
   - *Reviewer Appeal:* Addresses real data privacy compliance (e.g., personal data protection / PDP) with verifiable security boundaries.

4. **Resilient Integration & Contract Conformance Archetype (Anti-Corruption Layer & CDCT):**
   - *Domain Trigger:* Backend must synchronize with legacy university ERPs, SSO, or third-party core databases where only mock, dummy, or unstable REST interfaces are provided during development.
   - *Core Problem:* Schema drift, contract mismatches, or system failure when upstream external interfaces change.
   - *Method:* Architectural **Anti-Corruption Layer (ACL)** / Adapter Pattern combined with **Consumer-Driven Contract Testing (CDCT / OpenAPI Spec Verification)**.
   - *Evaluation / Proving:* Schema evolution tolerance testing, mock contract adherence rate, failure isolation, and network idempotency under simulated external failures.
   - *Reviewer Appeal:* Shows mature enterprise integration awareness and prevents project blocking when external dependencies are delayed.

### 1.2 System Analyst (SA) Academic Proving & Revision Archetype
When helping a System Analyst define their individual proving method and resolve supervisor revisions for an S1 RPL Capstone proposal:

1. **Academic Proving Archetype:**
   - *Domain Trigger:* Legacy or semi-manual multi-tier administrative workflows (e.g. unauthenticated applicant forms, faculty reviewers, central enterprise superadmins) transitioning to an integrated digital system.
   - *Core Problem:* Disconnect between *as-is* and *to-be* business processes, unstructured requirement elicitation, lack of architectural persistence, and unverified traceability from user needs to system blueprints.
   - *Method:* Object-Oriented Analysis and Design (OOAD) using Unified Modeling Language (UML) notations (Use Case, Activity, Sequence, Class Diagrams), relational Entity Relationship Diagram (ERD) schema modeling, and formal Software Requirements Specification (SRS) adhering to IEEE Std 830 / ISO/IEC/IEEE 29148.
   - *Evaluation / Proving:* Requirements Traceability Matrix (RTM) verifying full bidirectional mapping from stakeholder requirements to design models and black-box verification scenarios, coupled with formal *as-is* vs *to-be* Gap Analysis.

2. **Supervisor Revision Rules (Mandatory Invariants):**
   - **Dedicated Batasan Masalah Subchapter:** Never bury scope, assumptions, and limitations inside `1.2 Perumusan Masalah` narrative prose. Separate them into a distinct `1.3 Batasan Masalah` subchapter immediately following it.
   - **Explicit SDLC Methodology in Batasan Masalah:** Examiners and supervisors require explicitly stating the software engineering methodology/lifecycle (e.g., Waterfall SDLC with OOAD UML) within Batasan Masalah. Explicitly state artifact boundaries: the SA owns requirements elicitation, SRS, UML, ERD, and UI mockups, while full application coding (backend/frontend) and code-level testing are handled collaboratively by team peers in the Capstone framework.
   - **1-to-1 Symmetrical Alignment between Rumusan Masalah and Tujuan:** Every numbered problem question in `1.2 Perumusan Masalah` must be answered symmetrically by the corresponding numbered objective in `1.4 Tujuan`.
   - **Eradicate Faculty Template Placeholders:** Academic examiners reject proposals retaining raw template instructional prose (e.g., `"Jadwal pelaksanaan dibuat berdasarkan rencana kegiatan. Bar-chart bisa dibuat per bulan atau per minggu. Contoh bar-chart:"` or `"*Keterangan: shading warna grayscale"`). Replace with formal academic narrative, insert formal table captions (`Tabel 1.1 Jadwal Pelaksanaan Kegiatan Penelitian`) above tables with `<w:keepNext/>`, and attach clear explanatory footnotes below.
   - **Strict IEEE Sequential Citation & Quality Invariant:** Every listed reference in Daftar Pustaka MUST appear in strict sequential order `[1]`, `[2]`, `[3]`, etc., across the body text (starting in Bab 1). Purge all dummy placeholder references from template files (e.g., `[1] Ludeman... [2] ......`). A proposal with a bibliography but zero in-text citations will be penalized.
   - **Daftar Pustaka Quality & Recency Threshold:** Telkom FIF proposals require a minimum of 10 references, published within the last 5 years (e.g., 2021–2026), and all Indonesian journal publications must be accredited at minimum SINTA 3 (SINTA 1, 2, or 3) or be recognized international venues. For a 10–12 item bibliography, format with single spacing (or 1.05–1.1), `space_before=0`, `space_after=2-3pt`, and 10–10.5pt font so all entries sit cleanly on a single page without awkward page-break splits.
   - **Pre-Table Subsection Page-Break Rule:** When a subsection introduces a large table (such as `1.6 Jadwal Kegiatan` and `Tabel 1.1 Jadwal Pelaksanaan Kegiatan Penelitian`), insert an explicit page break before the subsection if it occurs in the lower half of the page. This prevents orphaned headings and introductory lines separated from the table.
   - **Tel-U FIF Document Layout Standards:**
     - Margins: Left 4.0 cm (1.58 in), Top 3.0 cm (1.18 in), Right 3.0 cm (1.18 in), Bottom 3.0 cm (1.18 in).
     - Typography: 100% Times New Roman throughout (Bab 16pt Bold Centered, Subbab 14pt Bold Left, body 12pt Justified with 1.5 line spacing, first line indent 1.0 cm).
     - Page Numbering: Cover (no number), Preliminary pages (Lembar Persetujuan, Abstrak, Daftar Isi) in Roman lower (`ii`, `iii`, `iv`), Main body (`BAB I PENDAHULUAN` through Lampiran) in Arabic (`1`, `2`, `3`...).
     - Lembar Persetujuan: Clear table grid borders (`w:val="none"`) for a clean 3-column academic signature block (Pembimbing 1, spacer, Pembimbing 2) with underlined names and verified official NIPs.
     - **Table of Contents (Daftar Isi):** Generate dual TOC (native Word field code `TOC \o "1-2" \h \z \u` plus visual right-aligned tab stops at 14 cm with dot leader `w:leader="dot"`). Never include template formatting tutorial subheadings (such as `2.2 Percetakan Proposal Tugas Akhir` or `2.3 Kaidah Penulisan`) in the Table of Contents (`DAFTAR ISI`). When chapters beyond Chapter 1 are in scaffolded/template state, list only the chapter-level entries (`BAB II KAJIAN PUSTAKA`, `BAB III PERANCANGAN SISTEM`). After LibreOffice headless export, extract actual page footers via PyMuPDF (`fitz`) and synchronize page numbers to match the rendered PDF 100%.

     3. **Python-docx Automation Pitfalls:**
     - **Paragraph Object Identity Comparison:** Never use `p == target_p` or `doc.paragraphs.index(target_p)`. In `python-docx`, every access to `doc.paragraphs` constructs fresh wrapper `Paragraph` objects, causing `==` to evaluate to `False` and `.index()` to raise `ValueError`. Always compare underlying XML elements: `p._p == target_p._p`.
     - **Phantom List Numbering (`w:numPr`) in Template Paragraphs:** When editing or replacing headings/subheadings in institutional docx templates (such as `Kajian Pustaka` or `Rencana Kegiatan`), the original paragraph often carries invisible list numbering properties (`<w:numPr><w:numId .../><w:ilvl .../></w:numPr>`). Changing the paragraph text to `A. Kajian Pustaka` without removing `w:numPr` causes Word and headless PDF exporters (LibreOffice) to prefix or inject automatic list numbers (e.g., `1.4.1`, `1.4.2`) above or before the text. Always execute `for n in p._p.xpath('./w:pPr/w:numPr'): p._p.pPr.remove(n)` before setting heading titles.
     - **Table Caption Attachment:** In `python-docx`, attach table captions immediately above tables via `table._tbl.addprevious(cap_xml)` containing `<w:pPr><w:keepNext/></w:pPr>` to avoid page-break separation between caption and table.

### 1.3 Quality Assurance (QA) Academic Proving Archetype
When helping a Quality Assurance (QA) engineer define their individual proving method for an S1 RPL Capstone proposal:

1. **Academic Proving Archetype (Automated Multi-Tier & Mutation Testing):**
   - *Domain Trigger:* Systems with multi-stage, high-density transactional forms (e.g. 7-block unauthenticated registrations, conditional logic between applicant categories, local storage draft recovery), multi-role administrative review and disposition workflows, critical bidirectional external REST API integrations (e.g. iGracias/ERP), weighted scoring evaluations (e.g. MONEV formulas), and seasonal peak concurrent traffic.
   - *Core Problem:* Black-box manual testing is slow, non-repeatable, and prone to human tester bias; conventional unit test code coverage (line/branch coverage) yields a false sense of security (assertion-less tests with >90% coverage that fail to catch real faults); manual API validation cannot guarantee contract immutability; load tolerances are unknown prior to production release.
   - *Method:* **Automated Multi-Tier Testing Framework** (Test Pyramid: Unit Tests, API Contract Testing with schema validation, Automated E2E Browser Testing for multi-step UI flows) combined with **Mutation Testing (e.g. Stryker / Infection)** for assertion quality and synthetic load/stress testing (e.g. k6).
   - *Evaluation / Proving:* Objective **Mutation Score Indicator (MSI)** quantifying test suite fault-detection sensitivity (>80% killed mutant threshold), 100% API schema contract adherence rate, tail latency metrics (P95/P99) under simulated concurrent load, mapped formally to international quality standard **ISO/IEC 25010** characteristics (*Functional Suitability*, *Performance Efficiency*, *Reliability*).
   - *Reviewer Appeal:* Immediately elevates QA beyond simple "menjalankan Black Box testing manual dengan tabel Excel" into rigorous, repeatable software engineering science with quantitative metrics.

### 2. Dual-Supervisor Dynamic (P1 User/Mitra vs P2 KK/Academic)
- **Pembimbing 1 (P1 - Institutional User / Product Owner):** Focuses on business processes, functional completeness, user requirements, domain rules, and deployment readiness. P1 locks the tech stack and workflow requirements.
- **Pembimbing 2 (P2 - Kelompok Keahlian / Academic Advisor):** Focuses on academic rigor, research methodology, theoretical grounding, literature review depth, research problem formulation, and defense survival.
- **Consultation strategy:**
  - Do not treat P2 as a business stakeholder; bring questions about methodology, proving scope, artifact separation, and defense expectations.
  - Keep P2 updated on decisions locked with P1/Mitra so P2 can help align academic arguments with real technical constraints.
  - When pitching a backend proving method:
    - *To P1:* Frame it around operational integrity, zero data loss, prevention of approval bypasses, and data privacy.
    - *To P2:* Frame it around software engineering theory, formal models (FSM, NIST RBAC), specific comparative baselines (X vs Y), and measurable evaluation metrics.

### 3. Consultation Preparation Protocol
Before meeting supervisors (especially when transitioning between chapters):
1. **Locked Facts:** State what has already been decided with P1 and the development team (tech stack, DB, architecture, domain constraints) to avoid circular debates.
2. **Individual Research Question:** Bring 2-3 candidate research angles/methods for the individual role to discuss with P2 (e.g., formalizing RBAC vs benchmarking modular patterns vs ISO/IEC 25010 quality metrics) to avoid the vocational trap before locking Chapter 1.
3. **Artifact Boundaries:** Clarify the exact demarcation between team roles (e.g., BE vs FE in a monolith stack like Laravel Blade, BE vs QA in test suite ownership).
4. **Environment & Integration Scope:** Lock whether external systems (e.g., iGracias/ERP) are evaluated via mock/dummy contracts or live staging, preventing scope creep.
5. **Workflow & Tracking Specifics:** Resolve handling of unauthenticated external actors (e.g., external lecturers without SSO submitting forms and tracking status).
6. **Administrative & Template Checks:** Confirm pending faculty deadlines (EPRT score requirements, SK TA issuance timeline, Desk Evaluation schedules) and whether Subbab 1.4 (Hipotesis) is expected by P2 or safely omitted under official optional guidelines.

### 4. Requirements Provenance and Elicitation Maturity (Draft SRS vs Academic Scope)
In Capstone / real-partner projects, early elicitation inputs often arrive via draft SRS documents, supervisor meeting recordings/transcripts, or informal brief notes.
- **Three-tier information discipline:**
  1. *Empirical Domain Evidence:* Verified operational pain points, existing system manual bottlenecks (e.g., forms failing to persist data to a database, manual re-entry into ERP/iGracias). These are valid factual grounds for Chapter 1 Background.
  2. *Draft Product Requirements:* Unapproved feature backlogs, draft SRS tables, or tentative field lists. Treat these strictly as initial product engineering requirements subject to SA specification and partner sign-off, never as "final locked system specifications" or "proven research problems".
  3. *Individual Academic Proving Scope:* The specific research problem, theoretical model, or quality characteristic proven by the student. Never derive this passively from an engineering feature list or invent it without P2 agreement.
- **Stale elicitation avoidance:** When real elicitation meetings have occurred, do not retain boilerplate claims in Chapter 1 stating "no interviews or operational observations were conducted". Update the provenance to cite the specific stakeholder consultation and draft SRS as initial exploratory elicitation.

### 5. Scanned Document and OCR Verification Discipline
Partner specifications and institutional guidelines frequently exist only as scanned image PDFs (`NeedsOcrError`).
- **Never trust raw OCR text for critical specifications:** OCR routinely corrupts mathematical operators, score boundaries (e.g., `< 2.00` and `2.01-3.00` omitting `2.00`), API endpoints, and institutional formulas.
- **Visual verification protocol:** Render relevant PDF pages to high-resolution images (`pdftoppm`) and inspect them visually (e.g., via vision tools) before committing business rules, evaluation formulas, or API contract details to the proposal.

## Chapter 2 (Kajian Pustaka) Standard & Anti-Glossary Rule

Under the Telkom Faculty of Informatics rubric (Form TA1-05), the literature review carries high grading weight, with **40% dedicated to comparative analysis of strengths and weaknesses of prior work**.

### 1. The Anti-Glossary Trap
Never structure Chapter 2 as an elementary textbook glossary (e.g., defining "Pengertian PHP", "Pengertian Website", "Pengertian Database", "Pengertian Laravel"). Reviewers reject this as filler. Every theory included must directly justify a research decision or system design choice in Chapter 3.

### 2. Standard 3-Tier Structure for Chapter 2
- **2.1 Kajian Penelitian Sejenis (State of the Art & Research Gap):**
  - Synthesize 10-15 peer-reviewed publications (journals/conferences within the last 5 years).
  - Categorize by problem domain and methodological approach, not a sequence of disconnected summaries.
  - Mandatory comparative evidence matrix covering: Author/Year, Research Problem, Method/Architecture, Strengths, Weaknesses/Limitations, and Specific Relevance to this TA.
  - Conclude with an explicit derivation of the *research gap*.
- **2.2 Landasan Teori Rekayasa (Domain & Engineering Theory):**
  - Only concepts directly underpinning the proposed engineering solution.
  - Examples for Backend TA: Multi-tier Role-Based Access Control (RBAC), Finite State Machine (FSM) for lifecycle transitions, Service-Repository architectural pattern, and server-side validation/sanitization models.
- **2.3 Standar Kualitas & Evaluasi Perangkat Lunak:**
  - Formal software engineering evaluation models (e.g., ISO/IEC 25010 sub-characteristics: Functional Suitability, Performance Efficiency, Security/Data Integrity).
  - Verification traceability principles (e.g., ISTQB requirements-to-test traceability matrix).
- **2.4 Kerangka Pikir (Synthesis / Conceptual Framework):**
  - Narrative and diagrammatic synthesis showing how limitations of prior work and selected engineering theories lead directly to the Chapter 3 design.

## LaTeX Template Discipline & Migration Rules

When working with Telkom University LaTeX templates (`Template_Proposal_FIF` / `Template_Proposal_RPL`) or performing Word-to-LaTeX migrations:

1. **Strict Styling Preservation ("jgn ubah styling template latex awal"):**
   - Retain 100% of the institutional template structure: `\documentclass`, margins (`\marginsize{4cm}{3cm}{3cm}{3cm}`), native line spacing (`\linespread{1}`), section fonts, cover layout, and approval sheet environments.
   - **Never inject `\usepackage{setspace}` or change to `\onehalfspacing`** across the document. The institutional LaTeX template is configured for `\linespread{1}`. Injecting `setspace` inflates document length, breaks pagination, and alters institutional typesetting.
   - **Only edit metadata in `main.tex`:** Fill lines 54-73 (`\title`, `\EngTitle`, `\author`, `\NIM`, `\Prodi`, `\KK`, `\Gelar`, `\date`, `\Tanggal`, `\Bulan`, supervisors, Kaprodi). Do not modify the preamble, package imports, or class definitions. If TikZ node placement syntax (`below=... of ...`) is needed, only append `positioning` to `\usetikzlibrary{shapes.geometric, arrows, positioning}`.
   - **Preserve Cover.tex and Lembar-Persetujuan.tex As-Is:** Do not alter vertical spaces (`\vspace{ 2cm}`, `\vspace{1.5 cm}`), do not reduce logo scale (keep `[scale=0.17]{Tel-U-Logo}` in figure), do not replace `\rm` with `\rmfamily`, and do not alter table column widths (`\begin{tabular}{ m{7cm} m{7cm} }`). Both pages compile to exactly 1 page each out-of-the-box.

2. **Scaffolded Chapters Without Content (Headings-Only Rule):**
   - When migrating drafts where subsequent chapters (e.g., Bab 3 Perancangan Sistem or Lampiran) are not yet authored in the source document, generate only the required `\section` and `\subsection` headings and leave the body content empty under those headings.
   - **Consecutive Heading Vbox Overflow Pitfall:** In LaTeX, consecutive `\section` / `\subsection` headings with zero body text in between trigger `Overfull \vbox ... has occurred while \output is active`. Headings have internal penalties (`\nopagebreak`) preventing page breaks directly between headings, forcing LaTeX to hold all consecutive headings on a single page. If more than 8-10 empty headings are stacked, they exceed the text height. To prevent this, keep empty scaffolded subheadings budgeted to fit cleanly within one page (~7-9 headings total) or place an explicit page break between major sections.

3. **Abstract Single-Page Budget:**
   - The Indonesian Abstract (`Abstrak-Indo.tex`) must fit strictly on a single page (Page 3). Keep abstract text to ~250 words across 3 compact paragraphs and limit vertical space before keywords (`\vspace{0.3cm}`) so that trailing keywords never spill over to Page 4.

4. **Table Dimension Budgeting & Cell Padding Invariant:**
   - In standard 14.0 cm text width templates, column widths in `\begin{tabular}{|c|p{...}|...}` must account for cell padding (`2 * \tabcolsep` per column). For wide tables (Gantt schedule with 8 columns or comparison matrix with 5 columns), set `\setlength{\tabcolsep}{3pt}` or `3.5pt` and use `>{\raggedright\arraybackslash}p{...}` to enable word-breaking. Sum of `p{...}` widths plus all column paddings must stay `<= 14.0 cm`.

5. **Natbib Citation Style Compatibility:**
   - Telkom LaTeX templates frequently use `\bibliographystyle{plain}` in `main.tex`. Using `\citet{key}` with `plain.bst` triggers `Package natbib Warning: Author undefined for citation`. When `plain.bst` is active, write narrative citations as `NamaPenulis dkk. \cite{key}` instead of `\citet{key}`.

6. **Dual Deliverable Packaging (.pdf + .zip):**
   - When delivering LaTeX proposal drafts, always dispatch both the compiled view (`.pdf`) and the clean source archive (`.zip`) at the root level (no extra wrapping folder, stripped of `*.aux`, `*.log`, `*.bbl`, `*.out`, `*.toc`) so the student can immediately open the PDF or import the ZIP into Overleaf/TeXstudio without path conflicts.

## Evidence and citation discipline

Never fabricate references, DOI, author names, publication venues, page numbers, statistics, datasets, or findings.

When a factual claim lacks support, do one of the following:

- request a source,
- search/verify it using available research tools,
- mark it `[BUTUH SUMBER]`, or
- rewrite it as a clearly labeled research motivation/hypothesis rather than a fact.

For literature work, prefer a structured evidence matrix. At minimum capture:

| Source | Problem | Method | Data/context | Main result | Limitation | Relevance/gap |
|---|---|---|---|---|---|---|

Synthesize across sources by themes, agreements, conflicts, limitations, and unresolved gaps. Do not create a sequence of isolated summaries unless the user explicitly asks for that format.

## Alignment contract

Before finalizing any substantial draft, verify these links:

`evidence -> gap -> problem -> objective -> method -> data -> evaluation -> expected contribution`

Flag any broken link explicitly. Examples:

- objective has no corresponding problem;
- method is introduced without justification;
- evaluation metric does not measure the stated objective;
- contribution is broader than the experiment can support;
- background contains claims not used to motivate the problem;
- literature review does not support the selected method or research gap.

## Writing behavior

Use formal academic Indonesian for document prose unless the user requests another language. Keep discussion with the user conversational if that is their style.

For proposal prose:

- prefer precise, complete, compact sentences;
- avoid first-person pronouns in formal Indonesian proposal prose, consistent with the bundled guide;
- define abbreviations on first use;
- keep terminology consistent;
- avoid inflated claims such as “terbukti terbaik”, “sangat efektif”, or “novel” without evidence;
- distinguish observed facts, cited findings, assumptions, hypotheses, and planned work;
- do not write future planned results as if they already happened.

Do not paraphrase a source so closely that it becomes disguised copying. Preserve citation attribution during revision.

## Review modes

When reviewing a draft, default to **diagnose before rewrite**. Return:

1. short overall diagnosis;
2. critical issues first;
3. a table with `Location | Issue | Why it matters | Rule/evidence | Proposed fix`;
4. revised text only for the passages that need it, unless the user asks for a full rewrite;
5. unresolved evidence/questions.

Use severity labels:

- **BLOCKER**: unsupported/fabricated evidence, broken research logic, wrong required section, or major non-compliance.
- **MAJOR**: weak gap, vague objective, unjustified method, weak evaluation plan, or major rubric exposure.
- **MINOR**: clarity, terminology, style, formatting, or local citation issue.

When the user asks for a “dosen/reviewer simulation,” ask concrete questions that probe assumptions, evidence, feasibility, method choice, evaluation, contribution, and scope. Do not merely generate generic viva questions.

## Official proposal compliance

For exact structure, abstract contents, formatting rules, timeline, process, and known ambiguities, load [references/official-rules.md](references/official-rules.md).

For the Telkom University LaTeX proposal template architecture, compilation chain, and Word-to-LaTeX migration workflows, load [references/latex-proposal-workflow.md](references/latex-proposal-workflow.md).

For program-specific CLOs and grading rubrics (literature review, bimbingan, Desk Evaluation, and seminar), load [references/rubrics.md](references/rubrics.md).

For the semester/process workflow and practical checkpoints, load [references/proposal-process.md](references/proposal-process.md).

For detailed section-by-section drafting guidance and examples of good reasoning, load [references/research-writing-playbook.md](references/research-writing-playbook.md).

For final pre-submission QA, load [references/quality-checklists.md](references/quality-checklists.md).

The original source document is preserved as [references/official-guide-2024.pdf](references/official-guide-2024.pdf) for manual verification when exact wording/layout is needed.

For provenance of the uploaded LMS bundle, load [references/lms-material-note-2026.md](references/lms-material-note-2026.md). Do not use that note as a rulebook.

## Deterministic linting

When the proposal is available as plain text or Markdown, run:

```bash
python scripts/proposal_lint.py path/to/proposal.md
```

Use the linter as a **warning system**, not as a substitute for academic judgment. Explain false positives where appropriate.

### Bounded chapter revision delivery

- Bind completion to the requested chapter/version, not to the entire proposal. If a Chapter 1-only revision triggers missing Chapter 2/3 warnings, disclose them as limits on full-proposal readiness; do not fabricate extra chapters to silence the linter.
- Verify the rendered PDF uses the requested font rather than silently accepting metric-compatible substitution. Prefer an isolated render configuration over changing global font configuration, and recheck pagination after correcting a font.
- When checking DOCX-to-PDF paragraph completeness, remove page-number footers from the comparison stream before evaluating paragraphs that cross page breaks. A footer inserted inside extracted text can create a false missing-paragraph finding.
- Keep a factual revision distinct from academic finalization. Record unresolved proving scope, method, evaluation criteria, and partner contract decisions in a companion note, without presenting them as approved research choices.
- **Recursive revision discovery:** Traverse recursive subdirectories under the role workspace (such as `revisi_bab1_<date>/`) rather than assuming the root folder holds the newest deliverable. Revision folders contain the latest bimbingan iterations, updated PDF exports, and companion notes (`CATATAN_REVISI.md`) which supersede older baseline drafts.
- **Dual-format delivery and metadata handoff:** When dispatching academic deliverables to messaging platforms, provide both the editable document (`.docx`) and compiled view (`.pdf`) via native platform media transfer. Pair the transfer with verified document attributes: exact file modification timestamp (`stat`), version tag, supervisor names, and a concise summary of delta changes from the revision ledger.

## Output defaults

Adapt the output to the task, but prefer:

- **Drafting:** polished text + a short note listing claims that still need sources/data.
- **Planning:** concise roadmap with dependencies and deliverables.
- **Literature review:** evidence matrix + synthesis + candidate gap.
- **Audit:** severity-ranked findings + concrete fixes + rubric mapping.
- **Revision:** before/after or change map when useful.
- **Seminar prep:** 5-10 minute narrative + likely reviewer questions + evidence-backed answer cues.
- **File delivery / progress check:** send both `.docx` and `.pdf` with exact file modification timestamp, author/NIM, supervisor list, version tag, and bulleted summary of key updates from the change log.

Never bury uncertainty. If an institutional rule cannot be verified from the available material, say so and identify what document would resolve it.
