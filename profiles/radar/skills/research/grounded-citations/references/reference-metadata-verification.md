# Reference-List Metadata Verification

Auditing an EXISTING bibliography (someone else's reference list, a draft's
Daftar Pustaka) is a different job from generating citations: the question is
whether each entry describes a real publication with correct
authors/year/venue/pages/DOI, and whether it supports the sentence it is
attached to. Keep those two questions separate — metadata correctness and claim
support are independent findings.

## Query the DOI registrar, not a title search

Crossref is the primary metadata source for a DOI:

```bash
DOI="10.xxxx/yyyy"
ENC=$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1],safe='/'))" "$DOI")
curl -s --max-time 40 "https://api.crossref.org/works/$ENC" \
  -H "User-Agent: Audit/1.0 (mailto:you@example.org)"
```

- Encode the DOI but keep `/` unescaped so the path resolves.
- Always send a contact `mailto` in the User-Agent (polite pool; fewer rate errors).
- Query **by DOI**. A title search returns look-alikes and cannot prove identity.
- Read and compare: `DOI`, `type`, `title`, `container-title`, `volume`,
  `issue`, `page`, `issued`, `published-print` vs `published-online`,
  `publisher`, `ISSN`, `URL`, `author[].given/family` (ordered), `license`.
- A 404 is a finding: the DOI does not resolve. Say so; do not substitute the
  nearest plausible record.

## Field-by-field comparison

| Field | Compare against | Failure mode |
|---|---|---|
| Authors | Ordered full author list + count | First author name/spelling wrong; a paper with many authors cited as if one |
| Year | Year of the version cited | Print vs online registration can differ by a year — flag, never silently "fix" |
| Venue | `container-title` as registered | Entry uses an invented or abbreviated journal name |
| Volume/issue/pages | Exact match to record | Page range taken from a preprint or a different issue |
| DOI | Resolves, and matches the entry's target | DOI points at a different article than the citation claims |

`First, A. dkk.` / `et al.` is acceptable style for 4+ authors, but the **first
author must match exactly**. Report style-level differences separately from
errors so the author can choose what to accept.

## What metadata verification does NOT establish

- **Metadata correctness is not claim support.** The registrar record says the
  paper exists; it says nothing about whether the cited sentence is what the
  paper found. Support needs the abstract or full text, read from the publisher
  or an open copy. A `abstract` field in the record is sometimes present and
  often absent — record which case you are in.
- When the audit question includes "does it support the claim", emit two axes:
  metadata `VERIFIED` + support `UNVERIFIED` is a legitimate, common outcome.
- Never pad a bibliography to reach a minimum entry count. Ambiguous minimums
  (e.g. a guide that contradicts itself) go to the supervisor as a question.

## State vocabulary (use these words)

- `VERIFIED` — you inspected the object itself (registrar record, live page,
  downloaded PDF) for the exact claim.
- `UNVERIFIED` — plausible but uncorroborated this run; no inspectable evidence.
- `BLOCKED` — a named external condition prevents inspection: file not
  provided, log in required, paywall.
- Keep `claim_type` separate (`FACT | OBSERVATION | CALCULATION | INFERENCE |
  PROPOSAL`). Never upgrade "record exists" into "source supports this".

## Non-public and internal sources

- Internal SRS, meeting transcripts, briefs, deck templates: mark `BLOCKED` when
  the artifact is not in your hands. Never cite a private document as if read.
- Record what the document itself says about itself: creator as printed on
  page 1, version, status, last-updated. A doc marked *Draft* never becomes
  evidence of a decided requirement, and file metadata (author/print date) does
  not override the creator printed on the page.
- A transcript is a report of what was said, not an approved minute; label it.

## Read-only audit hygiene

- Copy the artifact into your own scratch dir and hash it. Never edit the
  original. Record `sha256sum` before and after and report the match.
- Verify an official URL with a HEAD first (status, `content-type`,
  `last-modified`); for a PDF actually download it and inspect it
  (`file`, `pdfinfo` for page count, `pdftotext` for the claimed section).
  An HTTP 200 is not evidence the document is the version being audited.
- **Never call live endpoints of the system under audit merely to prove they
  exist or are reachable**, especially when they may hold personal data. Request
  a sanitized spec or a sample payload from the owner instead.
- Keep the audit read-only: the deliverable is findings, not an edited document.

## Pause protocol (parent stops you mid-run)

Do not remediate, do not spawn peers, do not write a "best effort" report. Reply
with exactly: (a) whether the run started, (b) the exact output files produced
with paths, (c) explicit confirmation it is paused, (d) original hashes intact.
If the target report was never written, say that plainly rather than implying a
partial artifact exists on disk.
