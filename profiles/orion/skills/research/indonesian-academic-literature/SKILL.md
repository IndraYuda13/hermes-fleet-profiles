---
name: indonesian-academic-literature
description: Use when searching SINTA journals or Indonesian papers.
---

# Indonesian Academic Literature (SINTA & Institutional Repositories)

## Operating Principle
When sourcing Indonesian academic references for research, proposals, or undergraduate theses (TA), prioritize peer-reviewed national journals indexed by SINTA (Science and Technology Index) and university repositories. Do not rely on unverified search results or hallucinate citations.

## Accreditation Verification & Audit Procedure
When asked to verify whether specific user-supplied journals meet a requested tier threshold (e.g., "cek jurnal ini SINTA berapa dan memenuhi spesifikasi minimal SINTA 3"):

1. **Deterministic Verification Lookup**:
   - Web Search: Query `site:sinta.kemdiktisaintek.go.id "<Nama Jurnal>"` or `"<Nama Jurnal>" sinta`.
   - Direct SINTA Profile: Extract the journal profile ID (`sinta.kemdiktisaintek.go.id/journals/profile/<id>`).
   - Alternative Check: Inspect `cekjurnal.id/jurnal/<slug>` or the SINTA author view (`view=garuda` displaying `Accred : Sinta X`).
   - Unaccredited Indicator: If the SINTA profile states `Accred : Unknown`, or the journal's OJS masthead indexes with Google Scholar/Garuda/Crossref without an official SINTA SK badge, classify it as **Non-SINTA / Unaccredited**.

2. **Binary Compliance Decision**:
   - Compare strictly against the requested threshold: SINTA 1 > 2 > 3 > 4 > 5 > 6.
   - For "minimal SINTA 3": SINTA 1–3 = **MEMENUHI SPESIFIKASI**, SINTA 4–6 and Non-SINTA = **BELUM MEMENUHI SPESIFIKASI**.

3. **Actionable Remediation (1-to-1 Topical Replacement)**:
   - When a paper fails the threshold, do not simply reject it and stop.
   - Extract the specific functional topic (e.g., recruitment/internship registration workflow, lecturer performance evaluation dashboard, SUS usability testing).
   - Immediately provide verified 1-to-1 substitute papers from SINTA 1, 2, or 3 journals covering that exact topic, complete with title, authors, volume/year, and direct PDF download links.

## SINTA Hierarchy & Tier Rules
- **Tier Ordering (Inversely Numbered)**: SINTA 1 is the highest tier, SINTA 6 is the lowest (SINTA 1 > SINTA 2 > SINTA 3 > SINTA 4 > SINTA 5 > SINTA 6).
- **"Minimal SINTA N" Criteria**: A requirement such as "minimal SINTA 3" strictly admits SINTA 1, SINTA 2, and SINTA 3. Never propose SINTA 4, 5, 6, or unaccredited venues when a minimum tier is set.
- **Journal vs. Proceeding Distinction**: University proceedings (e.g., *eProceedings of Engineering Telkom University*, seminar proceedings) and student repositories are not accredited SINTA journals, even if indexed on GARUDA. Clearly differentiate them from peer-reviewed SINTA journals.
- **Accreditation Verification**: Verify a journal's current tier via `sinta.kemdiktisaintek.go.id/journals/profile/<id>` or `cekjurnal.id/jurnal/<slug>`. Do not guess or assume accreditation based on publisher name alone.

## SINTA vs. GARUDA Architecture
- **SINTA (`sinta.kemdiktisaintek.go.id`)**: Official index ranking journals into tiers (SINTA 1 through SINTA 6). However, SINTA's portal is primarily an author/institution/journal directory, often protected by strict WAF/Cloudflare or lacking full-text document search APIs.
- **GARUDA (`garuda.kemdiktisaintek.go.id` - Garba Rujukan Digital)**: The official full-text document indexing engine under Kemdiktisaintek. It aggregates and indexes articles from all SINTA-accredited journals across Indonesia.
- **Golden Rule**: Always search and fetch national journal articles via **GARUDA** endpoints rather than scraping SINTA directly.

## Language Specification & Dual-Title Metadata Handling
- **The Dual-Title Metadata Trap**: Many top-tier national journals (SINTA 2 & SINTA 3, such as RESTI, TEKNOSI, SISTEMASI, JAIC) mandate English titles in their official publication metadata/OJS index for international indexing eligibility, even when the entire article body and discussion are written in Indonesian.
- **Strict Indonesian Title Audits**: When users or supervisors demand references with titles strictly in Indonesian:
  1. **Category A — 100% Native Indonesian Titles**: The article title itself is written in Indonesian and explicitly features the target methodology and metrics (e.g., *JURIKOM*, *J-PTIIK*, *Sistemasi*).
  2. **Category B — English Metadata Title with Indonesian Full Text**: The title appears in English in bibliographic indices, but the full-text body and methodology are in Indonesian (e.g., *TEKNOSI*, *SISTEMASI*).
  3. **Category C — Full English Naskah**: Both metadata and full PDF are in English (e.g., *JSI UI*, *SJI UNNES*).
- Always explicitly segregate candidate papers into these categories so students can choose what strictly complies with their supervisor's editorial preference.

## Direct Metric Verification (e.g., SUS Scores)
- **Never infer empirical evaluation scores from abstracts**: Many abstracts summarize results vaguely (e.g. "hasil menunjukkan peningkatan usability yang baik") without mentioning exact numbers.
- **Inspect Full-Text PDF**: Download the PDF via OJS or GARUDA direct link and extract the relevant text (`pdftotext` or regex) to confirm:
  1. Whether the methodology (e.g., UCD, SUS 10-item) was actually executed vs. merely listed as a related keyword.
  2. Exact numeric scores (e.g., baseline vs. redesigned SUS scores: 52.25 -> 76.5, 72.5, 77.0, 90.35).
  3. Grade scale / Adjective rating (e.g., "Acceptable", "Good", "Excellent", Grade B).

## Deliverable Format: The 4-Section Supervisor Defense Package
When preparing a curated literature submission for thesis supervisors, structure the output into 4 transparent sections:

1. **Curated Literature Table**:
   - Columns: `No | Judul | Penulis | Tahun | Nama Jurnal + Peringkat SINTA | Metode | Skor Evaluasi (jika ada) | Link (DOI / URL) | Relevansi & Diferensiasi dengan TA`.
   - In `Relevansi & Diferensiasi`, state explicitly:
     - How the study relates to the student's problem.
     - The concrete difference (e.g. single-role vs. multi-role verification, mobile vs. web, B2C vs. internal university governance).
     - In which chapter it should be cited (Bab 1 Latar Belakang, Bab 2 Tinjauan Pustaka, or Bab 3 Metodologi).
2. **Audit Jurnal yang Ditolak (Rejection Ledger)**:
   - List candidate journals evaluated but excluded, citing objective grounds: SINTA tier below threshold (SINTA 4/5/6), unaccredited/unknown status, publication date > 5 years old, or non-journal type (student proceeding/institutional repository).
   - This proves academic rigor and shows the supervisor that the student actively filtered invalid references.
3. **Catatan Paper Belum Terverifikasi / Gray Area**:
   - Flag venues where accreditation is in transition, newly published, or missing ARJUNA sync.
4. **Rekomendasi Pemilihan Berdasarkan Posisi Bab**:
   - Point out the single strongest paper for motivating the Background (Bab 1), the strongest paper for justifying the chosen Method (Bab 2), and the benchmark paper for Evaluation targets (Bab 3).

## Deterministic Literature Retrieval Workflow

### 1. Document Search on GARUDA
Endpoint: `https://garuda.kemdiktisaintek.go.id/documents?q=<query>`
- Method: Direct HTTP GET with standard `User-Agent: Mozilla/5.0` header.
- **Search Query Pitfall**: Avoid overly restrictive boolean queries with year tokens (e.g. `"UCD" "SUS" 2021`), which cause GARUDA's search index to miss valid matches. Instead, search core methodology phrases (e.g. `"User Centered Design" "System Usability Scale"` or `"UCD" "SUS"`), retrieve document detail IDs across pages, and filter publication years programmatically in Python from `xmp[1]`.
- Results contain links to document detail pages: `/documents/detail/<doc_id>`

### 2. Handling Publisher OJS 403 / Cloudflare / Timeouts
- Many Indonesian university OJS hosts block datacenter IPs with 403 Forbidden or encounter network timeouts.
- **Remediation**:
  1. Inspect GARUDA's cached detail page metadata (`/documents/detail/<id>`).
  2. Use GARUDA's direct download proxy endpoint: `http://download.garuda.kemdiktisaintek.go.id/article.php?article=<id>&val=<val>&title=<title>`.
  3. Resolve the canonical DOI URL (`https://doi.org/...`).

### 3. Metadata & PDF Extraction
Endpoint: `https://garuda.kemdiktisaintek.go.id/documents/detail/<doc_id>`
- Extract metadata cleanly from `<xmp>` tags:
  - `xmp[0]`: Journal Name
  - `xmp[1]`: Volume, Issue, Year
  - `xmp[2]`: Article Title
  - `xmp[3:]`: Authors
- Extract direct PDF download link:
  - Regex search: `<a\s+[^>]*href=\"([^\"]+download[^\"]*)\"`
  - This points directly to the publisher's Open Journal Systems (OJS) PDF download endpoint.

### Python Extraction Snippet
```python
import urllib.request
import urllib.parse
import re

def search_garuda(query, max_results=10):
    encoded_q = urllib.parse.quote(query)
    search_url = f"https://garuda.kemdiktisaintek.go.id/documents?q={encoded_q}"
    req = urllib.request.Request(search_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    html = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", errors="ignore")
    
    doc_ids = re.findall(r'/documents/detail/(\d+)', html)
    unique_ids = list(dict.fromkeys(doc_ids))[:max_results]
    
    results = []
    for doc_id in unique_ids:
        detail_url = f"https://garuda.kemdiktisaintek.go.id/documents/detail/{doc_id}"
        d_req = urllib.request.Request(detail_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        try:
            d_html = urllib.request.urlopen(d_req, timeout=15).read().decode("utf-8", errors="ignore")
            xmps = re.findall(r'<xmp>(.*?)</xmp>', d_html)
            pdf_match = re.search(r'<a\s+[^>]*href=\"([^\"]+download[^\"]*)\"', d_html)
            
            if len(xmps) >= 3:
                results.append({
                    "doc_id": doc_id,
                    "journal": xmps[0].strip(),
                    "issue": xmps[1].strip(),
                    "title": xmps[2].strip(),
                    "authors": [a.strip() for a in xmps[3:7]],
                    "download_url": pdf_match.group(1) if pdf_match else None,
                    "garuda_url": detail_url
                })
        except Exception:
            continue
    return results
```

## SINTA Tiers & Prestigious National Computing Journals
When filtering by SINTA accreditation:
- **SINTA 1**: Scopus-indexed top national journals:
  - *TELKOMNIKA* (Telecommunication Computing Electronics and Control - Universitas Ahmad Dahlan)
  - *Journal of ICT Research and Applications* (ITB)
  - *IJEEI* (Indonesian Journal of Electrical Engineering and Informatics)
- **SINTA 2** (Gold standard for Informatics/RPL TA references):
  - *Jurnal RESTI* (Rekayasa Sistem dan Teknologi Informasi - IAII)
  - *TEKNOSI* (Jurnal Nasional Teknologi dan Sistem Informasi - Universitas Andalas)
  - *JUTIF* (Jurnal Rekayasa Perangkat Lunak dan Informatika - Universitas Jenderal Soedirman)
  - *JUITA* (Jurnal Informatika - Universitas Muhammadiyah Purwokerto)
  - *JEPIN* (Jurnal Edukasi dan Penelitian Informatika - Universitas Tanjungpura)
  - *Jurnal Sistem Informasi (JSI)* (FASILKOM Universitas Indonesia)
  - *Jurnal Infotel* (Telkom University)
- **SINTA 3**: Strong peer-reviewed national journals:
  - *JURIKOM* (Jurnal Riset Komputer - STMIK Budi Darma)
  - *J-PTIIK* (Jurnal Pengembangan Teknologi Informasi dan Ilmu Komputer - FILKOM Universitas Brawijaya)
  - *JAIC* (Journal of Applied Informatics and Computing - Politeknik Negeri Batam)
  - *Sistemasi* (Jurnal Sistem Informasi - Universitas Islam Indragiri)
  - *JUTISI* (Jurnal Ilmiah Teknik Informatika dan Sistem Informasi)
- **SINTA 4**: Acceptable secondary references (e.g. *JATI ITN*, *SIBC UPN*).

## Thematic Grouping & Proposal Synthesis
When delivering literature recommendations for software engineering / information system proposals:
1. **Group by Functional Module / Research Theme**: Rather than a flat list, categorize papers by the specific system sub-problems (e.g., Recruitment/Registration portal, Monitoring Multi-Role Dashboard, Performance Evaluation/Monev workflow).
2. **Explicit Usage Mapping**:
   - **Bab 1 (Latar Belakang / State of the Art)**: Point out specific gaps—e.g. how previous studies solved isolated modules, while the proposed work unifies the full lifecycle.
   - **Bab 2 (Kajian Pustaka / Studi Terkait)**: Structure into the comparative synthesis table (Author/Year, Method, Context, Evaluation Metric, Limitations).

## Telkom University Institutional Repositories
- **Open Library**: `https://openlibrary.telkomuniversity.ac.id/`
  - Repository for internal theses, undergraduate TA reports, books, and collections.
  - Requires authenticated session for internal full-text reports, but catalog metadata is publicly searchable.
- **eProceedings Telkom University**: `https://openlibrarypublications.telkomuniversity.ac.id/`
  - Published conference proceedings and student papers based on TA research.
  - Sub-portals:
    - `.../index.php/engineering` (eProceedings of Engineering - IF, IT, SE, TE)
    - `.../index.php/appliedscience` (eProceedings of Applied Science - D3/D4)
    - `.../index.php/management` (eProceedings of Management)
  - Full papers in PDF format are publicly downloadable directly via `/index.php/<section>/article/download/<id>/<file_id>`.

## Citation Currency Rules & Pitfalls
- **Currency Threshold**: References establishing the research gap and recent state of the art MUST be within the **last 5 years** (e.g., 2021-2026 for a 2026 submission). Classical foundational papers (e.g. ISO 9241-210 for UCD, Brooke 1996 for SUS) are exceptions.
- **Garuda Indexing ≠ SINTA Accreditation**: GARUDA indexes both accredited and unaccredited Indonesian journals; verify the venue on the SINTA portal (`sinta.kemdiktisaintek.go.id`) before confirming tier or citing.
- **Volume Number ≠ SINTA Tier**: High volume numbers (e.g., Vol. 16) indicate publication longevity, not accreditation rank. Never infer accreditation rank from volume/issue numbers.
- **Actionable Remediation**: When a candidate paper is rejected for failing the minimum SINTA tier, never leave the user without a path forward; always supply 1-to-1 substitute papers from SINTA 1–3 that preserve the exact functional topic.
