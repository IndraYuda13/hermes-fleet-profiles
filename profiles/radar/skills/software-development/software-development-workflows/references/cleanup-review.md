# Cleanup review reference

Use cleanup only on a defined diff. Search the codebase for reuse candidates before replacing new code, and inspect history/contract consumers before deleting an apparently redundant line. Classify proposed edits:

- **Safe:** proven-unused imports, dead comments, pass-through clutter.
- **Careful:** internal simplifications that require focused tests.
- **Risky:** public API, persistence, concurrency, or semantic changes—record for review rather than auto-applying.

Do not turn a cleanup pass into a broad rewrite. Re-run focused checks after each meaningful edit.
