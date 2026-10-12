---
name: academic-report-deliverables
description: Use when building academic assignment reports as docx+PDF.
version: 0.1.0
author: Hermes
license: MIT
metadata:
  hermes:
    tags: [Report, Docx, PDF, Assignment, GSN, GenAI-Experiment]
---

# Academic Report Deliverables (docx + PDF)

Use for turning course material, a reference paper, or a GenAI experiment into a submission-ready assignment report.

## When to Use
- The user asks for an assignment report, case study, or GSN/assurance-argument deliverable in docx and/or PDF.
- A GenAI experiment must be documented as part of a graded submission.

## Always-on rules
- NO em dashes or en dashes (U+2012 to U+2015, U+2212) anywhere in the deliverable: body text, tables, captions, and diagram SVG text. Scan every build; regenerate offending AI-written text rather than blind-replacing characters.
- Mirror the assignment template exactly: same chapter order, headings, and table shapes as the brief.
- Fill only facts you know. Leave `[placeholder]` text for unknowns (for example, teammates not yet named) and tell the user which ones remain.
- House style: Times New Roman 12 pt, A4, 2.54 cm margins, Table Grid panels with light shading for prompt and output quotes, D9D9D9 header rows.
- Never invent GenAI output. Run the experiment for real, or leave the section marked as not run.

## Procedure
1. **Extract the brief.** `pdftotext -layout` the assignment file. Record required sections, point weights, word limits, and required deliverable formats (for example, docx and PDF both).
2. **Gather inputs.** Read the reference material fully before drafting. For a GenAI experiment, capture the exact prompt, the raw output, the reported model id, the date, and how the source text was supplied.
3. **Build the docx** with python-docx, using the project venv Python (`pip install python-docx` if missing). Keep the build as a re-runnable script (for example `build_docx.py`) so edits regenerate the whole file.
4. **Build diagrams** (for example GSN) with a Python SVG builder that places shapes and connectors by hand:
   - Draw connectors before shapes so arrowheads sit under the boxes.
   - Keep legend wording identical to the figure caption; a mismatch reads as an error to graders.
   - Convert with `rsvg-convert` at 2x, then vision-check for text overflow before embedding with `doc.add_picture(width=Inches(6.3))`.
5. **Export the PDF:** `soffice --headless --convert-to pdf --outdir <dir> <file>.docx`.
6. **Verify before delivery:**
   - Page count with `pdfinfo`.
   - Render each page with `pdftoppm -png -r 80` and inspect every page visually.
   - Dash scan of `word/document.xml` (via `zipfile`), of `pdftotext` output, and of the SVG.
   - Round-trip the docx with python-docx to confirm it opens.
7. **Deliver from a durable directory.** Keep the project folder outside the Hermes scratch cache, which prunes idle entries after about 24 hours. Copy final docx, PDF, and diagram PNG to a delivery folder together.

## Pitfalls
- **Regenerate, don't patch the PDF.** Editing only the docx leaves a stale PDF; rebuild both from the same build run.
- **Gateway SSE responses.** A local model gateway can answer in server-sent-events form even with `stream:false`. Parse both JSON and `data:` lines, and archive the full raw transcript next to the report so the experiment can be audited.
- **Summaries of a paper are not evidence of reading.** When the assignment asks for key points written by the student, the AI-generated part must be labelled as such and the student must review it; never present generated key points as the student's own reading.
- **Cover-page placeholders are a hand-off, not a finish.** Tell the user every placeholder that remains before they submit.
- **Diagram claims must match the analysis.** If the evidence fails a sub-claim, show that branch as unsupported in the diagram and say so in the conclusion; do not draw it as satisfied.
