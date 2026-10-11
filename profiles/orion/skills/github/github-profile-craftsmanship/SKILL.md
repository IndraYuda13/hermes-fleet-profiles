---
name: github-profile-craftsmanship
description: Polish GitHub profile design, showcase, and visual identity.
version: 1.0.0
metadata:
  hermes:
    tags: [github, portfolio, profile, design, craftsmanship, anti-slop]
    category: github
---

# GitHub Profile Craftsmanship & Anti-Slop Guide

Use when auditing, designing, or polishing a user's GitHub profile, pinned repositories, and project showcase.

## 1. Avoid Superficial "Checkbox" Audits
Do not stop at filling missing metadata fields (descriptions, tags/topics) merely to clear a numeric audit checklist. Inspect the actual rendered visual layout (`browser_exec` + `capture_screenshot` + `vision_analyze`) to evaluate typography, hierarchy, readability, and overall impression.

## 2. Eliminate Corporate Buzzword Inflation
- Never disguise personal tools, bots, scrapers, or automation scripts behind fake corporate jargon ("Enterprise-grade", "Production-oriented", "Battle-tested").
- Senior developers and technical recruiters view hyperbolic enterprise labels on small scripts as a negative signal.
- Use clean, precise, authentic technical phrasing (e.g. *"Multi-threaded stream automator with Turnstile bypass via Camoufox"* instead of *"Enterprise Pure Python Stream Automator"*).

## 3. Ban Cliché Badge Walls & Self-Inflicted Low Metrics
- Avoid 10–20 flat Shields.io badges lining the profile. It creates a dated "2020 tutorial" aesthetic.
- Never feature low vanity metrics (e.g., `Followers: 20` badge) prominently in the hero section; it highlights a nascent account rather than code substance.
- Maintain proper hierarchy: never list specific utility libraries (e.g., `Telethon`) alongside foundational programming languages (`Python`) or operating systems (`Linux`).

## 4. Align Claims with Concrete Code Evidence
- If the bio or tech stack advertises TypeScript/Next.js/React, ensure the pinned repositories or featured showcase actually include TypeScript/Next.js repositories, rather than pinning 100% Python automation scripts.
- Curate pinned repositories across the user's authentic specialties (e.g. distributed systems, reverse engineering, web frontends).

## 5. Clean Human Identity
- Ensure the profile display name is set to the user's actual human name rather than matching their raw bot/account handle (e.g. `Indra Yuda` instead of `IndraYuda13`).
- Strip out AI prompt leakage or internal notes (e.g. *"Showcase direction: clean, public-safe repositories with practical implementation value"*).

## 6. Symmetrical Pinned Repository Alignment
- On GitHub pinned repository cards, variable description lengths cause cards in the 2-column grid to stretch unevenly, breaking vertical rhythm.
- Keep all pinned repository descriptions uniformly calibrated to exactly 2 lines (approx. 80–110 characters). This ensures symmetrical card heights across all rows.
- When `gh api user -X PATCH` fails with HTTP 404 / missing `user` OAuth scope, automate profile updates directly via authenticated headless browser session (`https://github.com/settings/profile`).

## 7. Dynamic Gamification & "First Impression Waw"
When the user desires a vibrant, visually captivating, and fun tech portfolio rather than a dry resume:
- **Dynamic Typing Terminal (`readme-typing-svg`):** Use an animated SVG terminal typing effect cycling through authentic technical specialties (e.g. reverse engineering, distributed egress, anti-bot solvers).
- **Gamified Interactive Contribution Grid (`Platane/snk`):** Set up a GitHub Actions workflow (`.github/workflows/snake.yml`) that runs on schedule and transforms mundane commit grids into a live retro arcade Snake game eating commit squares. Support light/dark mode with `<picture>` tags.
- **Unified Visual Flow & Width Balancing:** When stacking elements (like `snk` contribution grids and `skillicons.dev`), stretch the icon container to match the wide 52-week horizontal grid width (e.g. 1 continuous row of 14 icons instead of narrow stacked clusters) to prevent disjointed "hourglass" layout defects.
- **Dynamic Header & Telemetry Cards:** Pair with waving gradient headers (`capsule-render`), real-time streak telemetry (`streak-stats`), and dynamic tech quotes (`quotes-github-readme`). Always verify third-party card uptime/response beforehand to prevent broken image cards.

## 8. Technical Certifications, Credentials & SKPI Vaulting
When curating developer certifications, digital badges, and academic credentials:
- **Tier Prioritization:** Prioritize Tier 1 official vendor credentials with Credly verification (Microsoft Applied Skills, AWS Educate, Cisco NetAcad, IBM Cognitive Class) for LinkedIn licenses and resume headers over non-verifiable completion slips. See `references/platform_matrix.md`.
- **Speedrun Verification Standards:** Fast-track through interactive scenario assessments or project submissions without violating academic integrity; bypass tutorial videos to launch directly into validated skill assessments (HackerRank, freeCodeCamp).
- **Consolidated Identity:** Register all platforms under one primary email to aggregate all verifiable badges on a single Credly profile URL.
- **Academic SKPI Compliance:** Enforce study-period date validity (`T_enroll <= T_issue <= T_defense`), exact name/NIM matching, vector PDF formats under 2MB, and directory naming conventions: `[YYYYMMDD]_[KATEGORI]_[PENERBIT]_[NAMA]_[ID].pdf`. See `references/skpi_compliance_checklist.md`.
- **Anti-Spam LinkedIn Discipline:** Never auto-broadcast micro-badges to the LinkedIn main feed; add them quietly to Licenses & Certifications to avoid recruiter feed fatigue.

## 9. Contact & Social Badges Craftsmanship
When adding social channels or contact badges (Telegram, Discord, X, LinkedIn, Email) to a profile README:
- **Case Preservation vs. Uppercase Degradation:** Never use Shields.io `style=for-the-badge` for usernames or contact handles. `for-the-badge` forces all text into uppercase (e.g. `@LemonTeaNyegerin` becomes `@LEMONTEANYEGERIN`), breaking case sensitivity, visual identity, and brand styling. Always use `style=flat-square` to preserve exact handle capitalization.
- **Icon-Led Two-Segment Anatomy:** To avoid a flat single-color blob, construct a clean two-segment flat badge using `label=%20` and `labelColor=18181b` with `logo=<platform>&logoColor=white`:
  `https://img.shields.io/badge/<Platform>-<@handle>-<brandColor>?style=flat-square&labelColor=18181b&logo=<platform>&logoColor=white&label=%20`
  This frames the white glyph in a clean dark container on the left, paired with the platform brand color and readable handle on the right. Note: `logoWidth` has no effect on `flat-square` badge dimensions.
- **GitHub Camo Proxy & Layout Constraints:**
  - GitHub markdown headers (`###`) remain strictly left-aligned by GitHub CSS even when nested inside `<p align="center">`. For intentional centering, use explicit HTML `<h3 align="center">`, or keep headers left-aligned with centered badges and `<sub>` caption copy below.
  - GitHub normalizes badge `<img>` height attributes through its asset proxy (`camo.githubusercontent.com`) and CSS aspect-ratio rules; inline `height="24"` will often render at the badge's native 20px height. Keep inline heights at 20–24px.
  - **Live Verification Protocol:** Always verify target URL availability (HTTP 200 via `curl -I` on `t.me/...` or destination), verify GitHub Camo cache resolution, and inspect actual rendered pixels via browser + vision analysis on the live profile page before closing.

## 10. Repository Initialization, Pre-Push Hygiene & Verification
When publishing a local workspace or project to a new GitHub repository:
- **Pre-Push Secret Audit:** Inspect `.gitignore` and `git status`. Run `git ls-files | grep -E "(\.env|secret|key|token)"` to verify no live credentials or un-gitignored `.env` files are tracked. Commit only `.env.example` templates.
- **README Verification:** Confirm `README.md` documents project overview, features, tech stack, environment variables, and run/build commands before initial push.
- **Remote Repository Creation:** Check existing remotes (`git remote -v && gh repo view <owner>/<repo>`). Default to `--private`:
  ```bash
  gh repo create <owner>/<repo> --source=. --remote=origin --private --push --description "<description>"
  ```
- **Verification:** Confirm branch tracking and fetch URL via `git remote -v` and `gh repo view <owner>/<repo>`.



