---
name: competition-prototype-hardening
description: "Use when hardening competition prototypes and demo seeders."
---

# Competition Prototype Hardening & Evaluation Preparation

A specialized engineering standard for preparing software prototypes, test accounts, seed datasets, and Git repositories for live hackathon demos, pitch evaluations, and competition judging.

## When to Use

- Preparing a project for live demonstration before hackathon or innovation contest judges.
- Building automated seeders that populate realistic evaluation data without manual setup.
- Scrubbing public repositories of internal AI bot artifacts, agent names, and dead references.
- Hardening authentication to work reliably without external email or OAuth dependencies.
- Auditing release manifests, build scripts, and Git commit provenance before final submission.

---

## Procedure

### 1. Build an Idempotent, High-Signal Demonstration Seeder
Judges evaluate software in short windows (3-5 minutes) and cannot perform extensive manual data entry. Provide an automated CLI script (e.g. `scripts/seed-dummy-account.mjs`) following these four rules:
- **Direct Database Password Hashing:**
  - Insert pre-hashed credentials (e.g. scrypt, Argon2id, bcrypt) directly into the database credentials table.
  - Bypass live email confirmation, magic links, and third-party OAuth so the account logs in immediately on local loopback, offline staging, or network-restricted venue Wi-Fi.
- **Multi-Tier Competence & Capability Distribution:**
  - Do NOT seed uniform dummy data (e.g., all 5/5 or random noise).
  - Explicitly seed distinct capability tiers (e.g., 30% advanced mastery, 40% intermediate with specific misconceptions, 30% foundational requiring scaffolding).
  - Map question items and assessment runs directly to curriculum/competency IDs so adaptive grouping, recommendation, or leveling algorithms visibly bifurcate students into defensible intervention groups on the first click.
- **Dual-State Operational Scenario:**
  - **Completed / Closed Session:** Pre-populate at least one finalized session with historical analytics, diagnostic cards, and reports so judges can inspect retrospective dashboards immediately.
  - **Active / Live Session:** Pre-populate at least one in-flight session in `active` state so clicking "Lanjutkan" immediately demonstrates real-time classroom interactions, QR pairing, or station rotations without preliminary setup.
- **Transactional Idempotency:**
  - Wrap the seeder in a clean teardown-and-insert transaction that purges previous test records for that teacher/user ID before re-populating.
  - Support configurable CLI flags (`--email=...`, `--password=...`) with robust defaults.

### 2. Public Repository Sanitization & Anti-Leak Audit
Before submitting a public Git repository or opening it to external reviewers:
- **Scrub Agent & AI Assistant Artifacts:**
  - Grep the entire repository (code, comments, documentation, test files, configs) for names of LLM coding tools or multi-agent personas (e.g., `Codex`, `Claude`, `Hermes`, `AGENTS.md`, `SENTINEL`, `ORION`, `FRAME`, `PRISM`).
  - Replace internal multi-agent audit notes with standard technical architectural comments (e.g. `// Defense in depth security layering`, `// Authenticate before parsing request body`).
- **Clean Configuration Examples:**
  - Inspect `.env.example` and sample configs; remove references indicating models used during development (e.g., replace "The model running Codex is not an application default" with generic operator instructions).
- **Sanitize Mock Payloads & Test Fixtures:**
  - Search test files for sentinel strings (e.g., replace `"PRIVATE, SENTINEL"` with realistic domain fixtures like `"PRIVATE, SISWA"`).
- **Audit Documentation Links:**
  - Remove dead markdown links pointing to deleted QA artifact folders (e.g. `../artifacts/qa/`) or removed internal guidelines.

### 3. Build & Release Script Integrity
When untracking internal files or adding them to `.gitignore`:
- **Verify Build & Manifest File Roots:**
  - When removing `AGENTS.md` or local `artifacts/`, grep all build and release scripts (e.g., `release-manifest.mjs`, package release runners) to ensure they do not attempt to `stat` or hash non-existent files.
  - Run the release manifest generator locally to confirm zero `ENOENT` crashes.

### 4. Enforce Pre-Submission Quality Gates
Execute the full quality battery and ensure all gates pass before pushing:
```bash
# 1. Code style check
pnpm format:check   # Fix with pnpm format or prettier --write

# 2. Strict linter check
pnpm lint           # Enforce zero warnings (--max-warnings=0)

# 3. TypeScript type validation
pnpm typecheck      # next typegen && tsc --noEmit

# 4. Unit & integration test execution
pnpm test:unit      # Confirm all domain logic assertions pass
```

### 5. Git Provenance and Team Attribution
- **Audit Commit Authors:**
  - Inspect commit authors across the branch: `git log --format='%an <%ae>' | sort -u`.
  - Ensure commits reflect genuine team member handles or official GitHub noreply addresses; eliminate synthetic bot emails (e.g. `@fleet.local`, `@*.invalid`).
- **Strict Team Roster Isolation:**
  - Never project team member names from university coursework, capstone/Tugas Akhir, or past hackathons onto the current project.
  - Verify official team composition directly from competition registration or direct team confirmation before authoring pitch docs, concept papers, or commit logs.

---

## Pitfalls

- **Failing to seed realistic skill distributions for adaptive algorithms:** Seeding identical dummy scores (e.g., all 5/5 or all random) prevents judges from observing adaptive grouping, leveling, or recommendation features in action. Seed explicit multi-tier cohorts (low, mid, high) so sorting and partitioning algorithms visibly bifurcate.
- **Relying on live email delivery or signup verification during competitive demos:** Competitions often take place in network-restricted or offline environments; test accounts must have pre-verified credentials directly hashed in the database so authentication works immediately without network email dependencies.
- **Breaking release and manifest scripts when gitignoring local artifacts:** Removing `AGENTS.md` or `artifacts/` without updating build or release manifest scripts that stat those paths causes build failures in clean environments. Grep scripts whenever files are untracked.
- **Leaving AI bot personas or agent names in public code comments and documentation:** Hardcoded references to LLM bots ("Codex", "AGENTS.md", fleet personas) in source code, `.env.example`, or specs signal uncurated AI generation to judges and invite scrutiny. Sanitize all comments to standard technical language.
- **Conflating competition rosters with academic, capstone, or other contest teams:** Assuming team members from previous hackathons or coursework belong to the current competition roster leads to misattributed authors in proposals and embarrassing corrections. Always verify the exact project roster from official registration or direct confirmation.
- **Neglecting code style formatting before submission:** Code committed during rapid hackathon sprints often skips prettier; failing `pnpm format:check` in CI creates an unpolished impression.
