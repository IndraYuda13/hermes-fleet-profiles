# SKPI Compliance & Verification Audit Checklist

Guidelines for ensuring technical certificates pass academic verification (SKPI / Surat Keterangan Pendamping Ijazah) in Indonesian universities (specifically Informatics / Software Engineering programs).

## 1. Verifier Acceptance vs Rejection Rules

### Mandatory Invariants for Acceptance
1. **Active Study Period:** Issue date MUST fall between Student Registration Date and Graduation Defense/Yudisium date (`T_enroll <= T_issue <= T_defense`).
2. **Direct Verification Link:** Document must contain an active Credential URL or scannable QR code leading to the individual recipient's record.
3. **Identity Match:** Recipient name and NIM on certificate must match PDDikti / SIAKAD university records exactly.
4. **Relevant Learning Domain:** Topic must map directly to Computer Science / Software Engineering graduate learning outcomes (CPL).
5. **Measurable Workload:** Course certificates must specify total learning hours (Jam Pelatihan / JP), ideally >=20-30 JP.

### Immediate Rejection Traps
- Broken or 404 verification URLs, or QR codes that redirect only to platform homepages.
- Certificates issued prior to university admission (high school period).
- Unofficial raster screenshots exported to PDF (lacks vector clarity and tamper protection).
- Overclaiming category (e.g., categorizing a 1-hour webinar attendance as a Technical Competency Certification).

## 2. Master Metadata Registry Schema (`certs_registry.csv`)

```csv
cert_id,issue_date,category_code,title_id,title_en,issuer,credential_id,verify_url,duration_hours,file_path,skpi_status
CRT-2024-001,2024-04-12,TEK,Pengembangan Backend Pemula,Beginner Backend Development,Dicoding,DIC-98214,https://www.dicoding.com/certificates/DIC-98214,50,01_kompetensi_teknis/20240412_TEK_Dicoding_Backend_DIC-98214.pdf,VERIFIED
CRT-2024-002,2024-06-15,TEK,Problem Solving (Basic),Problem Solving (Basic),HackerRank,HR-55210,https://www.hackerrank.com/certificates/HR-55210,,01_kompetensi_teknis/20240615_TEK_HackerRank_Problem-Solving_HR-55210.pdf,VERIFIED
CRT-2024-003,2024-07-20,PEL,Desain Web Responsif,Responsive Web Design,freeCodeCamp,FCC-8812,https://www.freecodecamp.org/certification/fcc/responsive-web-design,300,02_pelatihan_workshop/20240720_PEL_freeCodeCamp_Web-Design_FCC-8812.pdf,SUBMITTED
```

## 3. Directory & Naming Validation Regex
Regex pattern for file validation:
`^[0-9]{8}_(TEK|PEL|ORG|LOM|AST)_[A-Za-z0-9-]+_[A-Za-z0-9-]+_[A-Za-z0-9-]+\.pdf$`

Categories:
- `TEK`: Technical Competency / Industry Vendor Certification
- `PEL`: Training, Hands-on Workshop, Bootcamps
- `ORG`: Extracurricular Leadership, Student Organization
- `LOM`: Competition, Hackathon, Scientific Contest
- `AST`: Lab Assistant, Teaching Assistant, Research Assistant
