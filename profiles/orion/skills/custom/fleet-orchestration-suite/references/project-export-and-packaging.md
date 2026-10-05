# Project Repository Packaging, Worktree Exclusion & Client Delivery Standard

Use when bundling a project repository into an archive (ZIP/tar) for user download, Telegram delivery (`MEDIA:`), or client handoff, especially in environments with multiple git worktrees, active deployments, and heavy build artifacts.

## Packaging Workflow

1. **Measure Subdirectory Footprint First:**
   Before creating an archive, inspect directory disk usage (`du -h --max-depth=1 <project_path>`). In multi-agent / Kanban repositories, subdirectories like `.worktrees/` often contain multiple duplicate worktrees with nested `node_modules` and `.next`, routinely ballooning repository size to 5–10+ GB.

2. **Exclusion List (Mandatory):**
   Always exclude non-portable, generated, and oversized directories:
   - Dependency caches: `node_modules`, `vendor`, `.venv`, `venv`
   - Build & framework caches: `.next`, `.turbo`, `dist`, `build`, `out`, `__pycache__`, `.pytest_cache`
   - Git worktrees & repo internals: `.worktrees`, `.git` (unless raw history is explicitly requested)
   - Heavy audit / test run scratch: `qa_lens_run`, `coverage`, `.nyc_output`

3. **Inclusion Checklist (Deliverable Core):**
   Ensure all critical project assets requested by the user are bundled:
   - Source code: `src/`, `app/`, `components/`, `lib/`, `services/`, `workers/`
   - Environment files: `.env` (active environment if requested by owner), `.env.example`
   - Specifications & Documentation: `docs/PRD.md`, `docs/DESIGN_SYSTEM.md`, architecture docs, handoff notes
   - Database schema & migrations: `drizzle/`, `prisma/`, `migrations/`, `schema.ts`
   - Test suites & scripts: `tests/`, `scripts/`
   - Configuration files: `package.json`, lockfiles (`pnpm-lock.yaml`, `package-lock.json`), `tsconfig.json`
   - QA & Release evidence: `qa-artifacts/`

4. **Multi-Worktree / Live Release Reconciliation:**
   If the latest verified release lives in a specific git worktree (e.g. `.worktrees/v2-storefront`), do not exclude it entirely. Extract that specific worktree's clean source into a named sibling folder in the zip (e.g. `project-v2-storefront/`).

5. **Generate a `README_EXPORT.md`:**
   Always place a root `README_EXPORT.md` inside the archive explaining folder breakdown, `.env` setup, migrations, and run commands.

6. **Build to Scratch & Verify Before Delivery:**
   - Write the archive to the scratch directory (`~/.hermes/profiles/orion/cache/scratch/<project>-full.zip`).
   - For Telegram delivery: Verify final size < 50 MB before outputting `MEDIA:/path/to/file.zip`.
