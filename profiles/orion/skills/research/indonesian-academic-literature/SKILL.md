---
name: indonesian-academic-literature
description: Use when searching SINTA journals or Indonesian papers.
---

# Indonesian Academic Literature (SINTA & Institutional Repositories)

## Operating Principle
When sourcing Indonesian academic references for research, proposals, or undergraduate theses (TA), prioritize peer-reviewed national journals indexed by SINTA (Science and Technology Index) and university repositories. Do not rely on unverified search results or hallucinate citations.

## SINTA vs. GARUDA Architecture
- **SINTA (`sinta.kemdiktisaintek.go.id`)**: Official index ranking journals into tiers (SINTA 1 through SINTA 6). However, SINTA's portal is primarily an author/institution/journal directory, often protected by strict WAF/Cloudflare or lacking full-text document search APIs.
- **GARUDA (`garuda.kemdiktisaintek.go.id` - Garba Rujukan Digital)**: The official full-text document indexing engine under Kemdiktisaintek. It aggregates and indexes articles from all SINTA-accredited journals across Indonesia.
- **Golden Rule**: Always search and fetch national journal articles via **GARUDA** endpoints rather than scraping SINTA directly.

## Deterministic Literature Retrieval Workflow

### 1. Document Search on GARUDA
Endpoint: `https://garuda.kemdiktisaintek.go.id/documents?q=<query>`
- Method: Direct HTTP GET with standard `User-Agent: Mozilla/5.0` header.
- Supports boolean search terms and phrase matching, e.g.:
  `"user centered design" AND "system usability scale"`
- Results contain links to document detail pages:
  `/documents/detail/<doc_id>`

### 2. Metadata & PDF Extraction
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

def search_garuda(query, max_results=5):
    encoded_q = urllib.parse.quote(query)
    search_url = f"https://garuda.kemdiktisaintek.go.id/documents?q={encoded_q}"
    req = urllib.request.Request(search_url, headers={"User-Agent": "Mozilla/5.0"})
    html = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", errors="ignore")
    
    doc_ids = re.findall(r'/documents/detail/(\d+)', html)
    unique_ids = list(dict.fromkeys(doc_ids))[:max_results]
    
    results = []
    for doc_id in unique_ids:
        detail_url = f"https://garuda.kemdiktisaintek.go.id/documents/detail/{doc_id}"
        d_req = urllib.request.Request(detail_url, headers={"User-Agent": "Mozilla/5.0"})
        d_html = urllib.request.urlopen(d_req, timeout=15).read().decode("utf-8", errors="ignore")
        
        xmps = re.findall(r'<xmp>(.*?)</xmp>', d_html)
        pdf_match = re.search(r'<a\s+[^>]*href=\"([^\"]+download[^\"]*)\"', d_html)
        
        if len(xmps) >= 3:
            results.append({
                "journal": xmps[0].strip(),
                "issue": xmps[1].strip(),
                "title": xmps[2].strip(),
                "authors": [a.strip() for a in xmps[3:7]],
                "download_url": pdf_match.group(1) if pdf_match else None,
                "garuda_url": detail_url
            })
    return results
```

## SINTA Tiers & Prestigious National Computing Journals
When filtering by SINTA accreditation:
- **SINTA 1**: Scopus-indexed top national journals (e.g. *Journal of ICT Research and Applications* - ITB).
- **SINTA 2** (Gold standard for Informatics/RPL TA references):
  - *Jurnal RESTI* (Rekayasa Sistem dan Teknologi Informasi - IAII)
  - *TEKNOSI* (Jurnal Nasional Teknologi dan Sistem Informasi - Universitas Andalas)
  - *JUTIF* (Jurnal Rekayasa Perangkat Lunak dan Informatika - Universitas Jenderal Soedirman)
  - *JUITA* (Jurnal Informatika - Universitas Muhammadiyah Purwokerto)
  - *JEPIN* (Jurnal Edukasi dan Penelitian Informatika - Universitas Tanjungpura)
  - *Jurnal Sistem Informasi (JSI)* (FASILKOM Universitas Indonesia)
  - *Jurnal Infotel* (Telkom University)
- **SINTA 3 & 4**: Good supporting references (e.g. *Sistemasi* [S3], *J-PTIIK UB* [S3/S4], *JATI ITN* [S4], *SIBC UPN* [S4]).

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

## Citation Currency Rules
- References establishing the research gap and recent state of the art MUST be within the **last 5 years** (e.g., 2021-2026 for a 2026 submission).
- Classical foundational papers (e.g. ISO 9241-210 for UCD, Brooke 1996 for SUS) may be older, but current comparative evaluation work must be recent.
