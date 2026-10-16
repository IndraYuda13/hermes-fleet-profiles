# Telkom University Faculty of Informatics LaTeX Proposal Workflow

## 1. Template Structure and File Modularization

The official Telkom University Faculty of Informatics proposal template (`Template_Proposal_FIF` / `Template_Proposal_RPL`) is based on the `book` class (`\documentclass[a4paper,12pt,oneside]{book}`) and decomposes into modular components:

- `main.tex`: Master document, package imports, macro declarations (author, NIM, title, supervisors, Kaprodi), layout dimensions, and inclusion order.
- `Cover.tex`: Proposal cover page.
- `Lembar-Persetujuan.tex`: Supervisor approval signature page.
- `Abstrak-Indo.tex`: Indonesian abstract and keywords.
- `Pendahuluan.tex`: Chapter 1 (Latar Belakang, Perumusan Masalah, Tujuan, Batasan Masalah, Rencana Kegiatan, Jadwal Kegiatan).
- `Kajian-Pustaka.tex`: Chapter 2 (Landasan Teori, Penelitian Terdahulu / Matriks Studi Terkait, Sintesis).
- `Metodologi.tex`: Chapter 3 (Perancangan Sistem atau Alur Pemodelan).
- `References.bib`: BibTeX bibliography database.
- `Lampiran.tex`: Supporting instruments (questionnaires, evaluation scenarios, payload mappings).
- `Tel-U-Logo.png`: University emblem.

## 2. Strict Layout and Dimension Invariants

- **Text Width Constraint (14.0 cm):**
  - Page: A4 (width 21.0 cm).
  - Margins: Left 4.0 cm, Right 3.0 cm (`\marginsize{4cm}{3cm}{3cm}{3cm}`).
  - Printable Text Width: exactly `21.0 - 4.0 - 3.0 = 14.0 cm`.
  - Every table, figure, and multi-column block must fit within 14.0 cm.

- **Lembar Persetujuan Signature Columns & Underline Wrapping:**
  - Standard 2-column tables using `m{7.0cm}` cause overfull hboxes because `2 * 7.0cm + 4 * \tabcolsep` exceeds 14.0 cm.
  - Long Indonesian supervisor names inside `\uline{...}` (from package `ulem`) do not wrap automatically. If the column is narrow (`m{5.8cm}`), names longer than ~30 characters overflow the column border.
  - Optimal dimension: `m{6.4cm} m{6.4cm}` with `\setlength{\tabcolsep}{3pt}`:
    ```latex
    \setlength{\tabcolsep}{3pt}
    \begin{center}
    \begin{tabular}{ m{6.4cm} m{6.4cm} }
    \centering \uline{\PembimbingSatuNama} & \centering \uline{\PembimbingDuaNama} \tabularnewline
    \centering \uline{\PembimbingSatuGelar} & \centering \uline{\PembimbingDuaGelar} \tabularnewline
    \centering NIP: \NIPPembimbingSatu & \centering NIP: \NIPPembimbingDua \tabularnewline
    \end{tabular}
    \end{center}
    ```
    Total table width is `2 * 6.4cm + 4 * 3pt = 12.8cm + 12pt = 13.22cm < 14.0cm`, fitting long names cleanly on a single line.

- **Cover Page Float Hazard:**
  - Never wrap `Tel-U-Logo.png` in a floating environment (`\begin{figure}[h]`) on the cover page.
  - Floats inside `\titlepage` drift vertically, pushing the bottom institutional text ("Bandung", "2026") onto a blank second page.
  - Embed directly using inline centering: `{\centering\includegraphics[scale=0.14]{Tel-U-Logo}\par}` with compact `\vspace{0.8cm}` to `\vspace{1.0cm}` spacing.

- **Abstract Single-Page Enforcement:**
  - Under `\onehalfspacing` (1.5 line spacing), Indonesian abstract text with 3 paragraphs and keywords spills onto Page 2.
  - Wrap `Abstrak-Indo.tex` in a single-space environment with compact font:
    ```latex
    \chapter*{Abstrak}
    \begin{singlespace}
    \small
    <Abstract paragraphs>
    \vspace{0.3cm}
    \noindent \textbf{Kata Kunci:} ...
    \end{singlespace}
    ```

- **Wide Comparison Tables (Chapter 2):**
  - Matriks Penelitian Terdahulu (`Tabel 2.1`) has high text density across 5 columns (No, Peneliti, Judul, Hasil, Hubungan/Gap).
  - Explicit column widths must sum to `<= 11.5 cm` to leave room for cell padding (`10 * \tabcolsep = ~2.1 cm`).
  - Always use `>{\raggedright\arraybackslash}p{...}` (from package `array`) so words in narrow columns wrap and hyphenate correctly instead of overflowing with `Overfull \hbox`.
  - Set `\setlength{\tabcolsep}{3pt}`, use `\scriptsize`, and keep text in each cell concise to prevent `LaTeX Warning: Float too large for page by ...pt`:
    ```latex
    \begin{table}[!htbp]
    \centering
    \caption{Matriks Perbandingan Penelitian Terdahulu dan Posisi Penelitian}
    \label{tabel_penelitian_terdahulu}
    \vspace{0.2cm}
    \scriptsize
    \setlength{\tabcolsep}{3pt}
    \renewcommand{\arraystretch}{1.1}
    \begin{tabular}{|c|>{\raggedright\arraybackslash}p{2.0cm}|>{\raggedright\arraybackslash}p{2.3cm}|>{\raggedright\arraybackslash}p{3.1cm}|>{\raggedright\arraybackslash}p{3.5cm}|}
    ...
    ```

- **Table Cell Shading for Gantt Charts (Jadwal Kegiatan):**
  - In `Tabel 1.1` (Jadwal Kegiatan), shaded months must be explicitly styled with `\cellcolor{black!20}` or `\cellcolor{gray!30}`.
  - With 8 columns (No, Kegiatan, Bln 1-6), default `\tabcolsep = 6pt` introduces `16 * 6pt = 3.39cm` of horizontal padding.
  - Set `\setlength{\tabcolsep}{3.5pt}` and column width `>{\raggedright\arraybackslash}p{4.2cm}` so total width stays strictly within 14.0 cm:
    ```latex
    \setlength{\tabcolsep}{3.5pt}
    \begin{tabular}{|c|>{\raggedright\arraybackslash}p{4.2cm}|c|c|c|c|c|c|}
    ```

- **TikZ Conceptual Framework Diagram Sizing:**
  - When rendering conceptual frameworks (`tikzpicture`), set node styles with explicit width:
    ```latex
    \begin{tikzpicture}[
        box/.style={draw, rectangle, rounded corners=3pt, text width=12.2cm, align=center, font=\small, inner sep=6pt},
        arrow/.style={->, >=stealth, thick, line width=1pt}
    ]
    ```
  - Keep `text width <= 12.2cm` to account for box padding, borders, and margins, ensuring the entire diagram centers symmetrically within 14.0 cm text width.

## 3. Package Dependencies and Build Chain

- **Required System Packages (Ubuntu/Debian):**
  - `texlive-latex-base`, `texlive-latex-recommended`, `texlive-fonts-recommended`, `texlive-latex-extra`, `texlive-science` (provides `algorithm.sty` and `algpseudocode.sty`), `texlive-bibtex-extra`.
- **Special Character Escaping:**
  - Percent signs in body prose (e.g. evaluation weights `40%`, `20%`) MUST be escaped as `\%`. Unescaped `%` comments out the remainder of the line and corrupts sentences.
  - URLs in lists or footnotes: do not use raw `\url` with long hostnames inside narrow items; use `\texttt{...}` or declare `\def\UrlBreaks{\do\/\do-\do.}` in preamble.
- **Natbib Compatibility with Numeric Bibliography Styles:**
  - The template's `main.tex` imports `\usepackage{natbib}` but uses `\bibliographystyle{plain}`.
  - `plain.bst` produces numeric keys `[1]` and does not write author-year tokens to the `.bbl` file.
  - Using `\citet{key}` causes `Package natbib Warning: Author undefined for citation`.
  - Fix: In body prose, write author citations as `NamaPenulis dkk. \cite{key}` (e.g. `Papadakis dkk. \cite{papadakis2019mutation}`). This renders cleanly in all bibliographic styles without natbib warnings.
- **Deterministic 4-Pass Compilation Chain:**
  ```bash
  pdflatex -interaction=nonstopmode main.tex
  bibtex main
  pdflatex -interaction=nonstopmode main.tex
  pdflatex -interaction=nonstopmode main.tex
  ```
  Check `main.log` for undefined citations or labels (`LaTeX Warning: Reference ... undefined` or `Citation ... undefined`).

## 4. Deliverable Packaging & Overleaf Import Hygiene

When delivering LaTeX proposals to students:

1. **Root-Level ZIP Archiving:**
   - Overleaf, TeXstudio, and VS Code LaTeX extensions expect `main.tex` directly at the root of the imported ZIP archive.
   - Do NOT wrap files inside an extra root folder when zipping.
   - Strip all build artifacts (`*.aux`, `*.log`, `*.bbl`, `*.blg`, `*.out`, `*.toc`, `*.lof`, `*.lot`, and preview renders):
     ```bash
     cd Template_Proposal_RPL_<Name>
     zip -r ../Template_Proposal_RPL_<Name>.zip main.tex Cover.tex Lembar-Persetujuan.tex Abstrak-Indo.tex Pendahuluan.tex Kajian-Pustaka.tex Metodologi.tex Lampiran.tex References.bib Tel-U-Logo.png main.pdf
     ```
2. **Dual-Format Delivery:**
   - Always deliver both the compiled `main.pdf` (immediate viewing on mobile/desktop without compiling) and `Template_Proposal_RPL_<Name>.zip` (editable source ready for supervisor revision).
