---
name: tech-certification-harvesting
description: Harvest tech certs and organize credentials for SKPI.
version: 1.0.0
metadata:
  hermes:
    tags: [certifications, badges, credly, skpi, portfolio, career, education]
    category: productivity
---

# Tech Certification & Credential Harvesting

Workflow for identifying, fast-tracking (speedrunning), verifying, and archiving legitimate technical certificates and digital badges for engineering portfolios, LinkedIn, and university graduation requirements (SKPI / Surat Keterangan Pendamping Ijazah).

## When to Use
- User asks where or how to quickly acquire technical certificates or digital badges for free or minimal effort.
- Curating an engineering portfolio for job applications, career showcases, or LinkedIn profiles.
- Preparing documentation, metadata registries, and PDF vaults for university SKPI submission.
- Auditing credential legitimacy to prioritize high-yield vendor credentials over low-value completion slips.

## Procedure

### 1. Identify Target Objective & Credential Tier
Determine whether the immediate goal is technical demonstration, vendor prestige, or academic credit volume:
- **Tier 1 (Official Vendor & Credly-Verified):** Microsoft Applied Skills, AWS Educate, Cisco Networking Academy, IBM Cognitive Class, Fortinet. Prioritize for LinkedIn licenses, resume headers, and institutional SKPI verifiers.
- **Tier 2 (Skill Assessment & Code-Verified):** HackerRank Skill Certification, freeCodeCamp 300-hour projects, Kaggle Micro-courses. Prioritize for Software Engineering / Data portfolios where direct proof of algorithmic and project execution matters.
- **Tier 3 (Institutional/Bulk Course Completion):** MOOC completions (Dicoding, Great Learning, Simplilearn). Use primarily to fulfill aggregate learning hours (Jam Pelatihan / JP) for university graduation quotas.

### 2. Fast-Track Execution (Speedrun Protocols)
Apply platform-specific acceleration methods without violating academic honesty:
- **Assessment-Only Platforms (HackerRank, Microsoft Applied Skills):** Bypass tutorials and slide decks; launch directly into the live coding challenge or interactive cloud sandbox lab assessment.
- **Project-Only Submission (freeCodeCamp):** Jump directly to the 5 required certification projects at the bottom of the curriculum; submit validated project repositories and pass test suites without doing hundreds of basic drills.
- **Module Post-Test / Final Exam (AWS Educate, Cisco NetAcad, IBM Cognitive Class):** Skip chronological video playback; review module summaries and proceed directly to end-of-module knowledge checks and final certification exams (target 70–80% passing grade).

### 3. Credential Verification & Identity Consolidation
Ensure all earned credentials can be programmatically and visually audited:
- **Consolidated Credly Identity:** Register and complete all vendor tracks using a single primary email address (or add institutional/alternate emails as secondary addresses under one Credly account) to aggregate all badges into a single public verifiable profile.
- **Direct Traceability:** Ensure every certificate record includes a permanent public verification URL and Credential ID, avoiding generic landing page redirects.

### 4. Archive Structuring & Local Vaulting
Maintain a deterministic directory structure and master registry:
```text
certificates-vault/
├── 01_kompetensi_teknis/      # Vendor & assessment certs (AWS, MSFT, Cisco, HackerRank)
├── 02_pelatihan_workshop/     # Course completions, bootcamps (>=20 JP)
├── 03_organisasi_kepanitiaan/ # Extracurricular leadership, event committees
├── 04_prestasi_kompetisi/     # Hackathons, algorithmic contests, awards
└── certs_registry.csv         # Single source of truth metadata table
```

File naming convention:
`[YYYYMMDD]_[KATEGORI]_[PENERBIT]_[NAMA-KEGIATAN]_[ID-KREDENSIAL].pdf`

Master registry schema (`certs_registry.csv`):
`cert_id,issue_date,category_code,title_id,title_en,issuer,credential_id,verify_url,duration_hours,file_path,skpi_status`

### 5. SKPI Compliance & Quality Gate
Before submitting to university academic portals:
- Verify that the issuance date falls strictly within the active enrollment window (between semester 1 and before the degree defense/yudisium).
- Verify that the name and student ID (NIM) exactly match official university records (PDDikti / SIAKAD).
- Maintain vector PDF format under 2 MB; never upload converted phone screenshots or rasterized scans.
- Enforce portfolio balance: allocate 45-50% to technical competencies, 25-30% to field/organizational experience, 15-20% to workshops, and 5-10% to competitions/achievements.

## Pitfalls
- **Deprecated Credential Pathways:** Always verify platform status before recommending legacy tracks — programs such as the original Postman Student Expert badge have been decommissioned and no longer issue new digital credentials.
- **LinkedIn Feed Flooding:** Do not auto-publish dozens of micro-badges to the LinkedIn main feed in a single session — batch uploads trigger algorithmic spam suppression and devalue portfolio signals to recruiters. Add them silently to the Licenses & Certifications section without toggling "Notify network".
- **Screenshot PDF Uploads:** Converting raster screenshots to PDF causes verifier rejection in academic portals — verifiers require vector text and scannable QR codes for audit traceability.
- **Out-of-Scope Dates:** Submitting pre-university (high school) or post-graduation certificates to SKPI results in automatic rejection — academic verifiers discard any record outside the active enrollment interval.

## Linked References
- `references/platform_matrix.md`: Detailed breakdown of free platforms, URLs, passing criteria, and Credly integration status.
- `references/skpi_compliance_checklist.md`: Audit checklist and regex naming validator for bulk SKPI submission.
