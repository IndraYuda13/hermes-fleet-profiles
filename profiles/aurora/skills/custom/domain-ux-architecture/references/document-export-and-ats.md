# Document Export and ATS Patterns

## Parser-safe structure

- Keep resumes and similarly parsed documents in a single linear reading order; multi-column sidebars interleave extraction and destabilize browser-to-PDF pagination.
- Use textual labels for contact links and clean tracking parameters from URLs; icon glyphs and noisy URLs degrade parser output.
- Keep repeatable content blocks together using page-break avoidance, and show an in-preview A4 height meter with a visible page boundary before export.
- Differentiate template archetypes through header alignment, hierarchy, dividers, type roles, and restrained color rather than changing the reading order.

## Live audit feedback

- Debounce dictionary, verb, metric, and format checks by roughly 150–200ms; synchronous inspection on every keystroke causes input lag.
- Keep score feedback compact and persistent, then place detailed findings in an off-canvas drawer; editors should retain their working position.
- Link every finding directly to the repairable field, and score contact integrity, action verbs, quantified outcomes, skill coverage, education/project depth, and formatting hygiene separately.
- Use animation frames only for visual counter or progress updates, never for analytical work.

## Persistence and export parity

- Store document data in a versioned envelope and pass every import through a normalization adapter; old or malformed browser data must not crash the editor.
- Maintain one mapping from preview classes to DOCX/PDF export properties; the exported file must preserve the selected template's alignment, fonts, and dividers.
- Support job-description keyword comparison, structured achievement prompts, and reorderable or hideable sections as optional productivity aids, not blockers to export.
