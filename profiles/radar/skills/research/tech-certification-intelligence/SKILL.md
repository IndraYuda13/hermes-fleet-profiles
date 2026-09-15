---
name: tech-certification-intelligence
description: Audit tech certs, digital badges, and credentials.
version: 1.0.0
license: MIT
metadata:
  hermes:
    tags: [certifications, badges, credly, skpi, tech-credentials, portfolio]
    category: research
---

# Tech Certification Intelligence

Investigate, categorize, and evaluate technical certifications, digital badges, and developer credentials for portfolio, academic credit (SKPI), and LinkedIn optimization.

## When to Use
- Evaluating technical certifications, digital badges, or developer skill assessments.
- Finding free, subsidized, or high-ROI credentials for software engineering, cloud, cybersecurity, data/AI, or devops.
- Verifying whether a certification program or student badge is active, transitioning, or sunset.
- Determining completion mechanics (proctored exam, interactive sandbox lab, unproctored quiz, or code project test suite).

## Procedure

### 1. Active Program & Sunset Verification
Before recommending or pursuing any credential, verify that the issuing program is actively issuing badges:
- Query official vendor community forums and deprecation trackers for sunset/retirement notices (e.g. legacy student ambassador/expert programs being phased out).
- Never rely on social media or blog guides older than 6 months without cross-checking the current live landing page.

### 2. Search Query Discipline
Strict search backends often return empty results when queries are over-constrained:
- Avoid chaining three or more quoted exact-phrase tokens (e.g. `"A" "B" "C" "D"`).
- Use 1-2 core keywords plus at most one quoted string (e.g. `"Microsoft Learn" Applied Skills`).
- If web_search returns empty results unexpectedly, strip quote operators and retry, or use live page scraping / browser inspection on known vendor roots.

### 3. Verification & Platform Taxonomy
Classify credentials into their functional tiers:
- **Tier 1 (Vendor Official & Credly/Accredible Verified)**: Microsoft Applied Skills, AWS Educate/Training, Cisco NetAcad/SkillsForAll, IBM Cognitive Class, Fortinet Training Institute. These carry third-party cryptographic verification and are recognized by corporate recruiters and academic committees.
- **Tier 2 (Skill Assessment & Code-Verified)**: HackerRank Skill Verification, freeCodeCamp projects, Kaggle Micro-courses. These prove actual coding or algorithmic competency via automated test suites without video watch gating.
- **Tier 3 (Bulk Completion / Attendance Certificates)**: MOOC video completion certificates (Coursera audit, Simplilearn SkillUp, Great Learning). Useful for meeting raw training hour requirements (JP) for academic transcripts, but low signal for competitive engineering roles.

### 4. Assessment Path Analysis
Identify the fastest legitimate path to credentialing:
- **Direct Assessment**: Platforms like HackerRank or Microsoft Applied Skills permit taking the evaluation immediately without completing prerequisites or watching lectures.
- **Unproctored Quiz Bypass**: Modular platforms (IBM Cognitive Class, Cisco Skills For All) allow jumping directly to chapter quizzes and final exams if domain knowledge is already possessed.
- **Automated Test Suite Submission**: Project-based platforms (freeCodeCamp) issue certificates upon passing automated test cases against user-submitted project URLs, bypassing intermediate tutorials.

### 5. Identity & Federation Uniformity
- Always bind vendor learning accounts to a single unified email or add secondary email addresses to one primary Credly/Accredible account to avoid fragmented badge portfolios.

## Pitfalls
- **Recommending retired badges**: Check vendor community boards for deprecation notices before citing developer badges; third-party blogs frequently recommend defunct programs.
- **Over-constraining discovery searches**: Chaining multiple quoted phrases in search tools frequently yields empty result arrays due to backend boolean parsing quirks.
- **Equating completion certificates with certification exams**: Clearly delineate between training completion badges (e.g. AWS Educate) and proctored industry certification exams (e.g. AWS Solutions Architect).

## Linked References
- `references/platform-matrix.md`: Verified inventory of active platforms, credential types, verification providers, and completion mechanics.
