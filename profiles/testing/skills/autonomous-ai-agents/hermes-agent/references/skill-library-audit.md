# Skill Library Audit (installed profile skills)

When the user asks which installed skills are unused / dead weight / safe to
remove ("clean up my skills"), audit the profile's skill library and produce a
grouped list for the user to prune from. Never delete in the audit turn —
present the list and wait for picks. This user reviews before deleting.

## Inputs (all under the profile's skills dir, e.g. `~/.hermes/profiles/<name>/skills`)

| File | What it gives |
|---|---|
| `<skill>/SKILL.md` | The installed skills; walk for it. Skip `.hub/`, `.archive/`. |
| `.usage.json` | Per-skill telemetry: `use_count`, `view_count`, `last_used_at`, `last_patched_at`, `created_at`, `created_by` (`agent` \| `learn` \| null), `pinned`, `state`. Read-only. |
| `.bundled_manifest` | `name:md5` of everything that shipped with Hermes. A skill NOT listed here is custom/imported (imported packs, session-learned skills) — irreplaceable, weight its removal differently. |
| `.curator_ledger.jsonl` | Creation/patch events with `actor` (`agent`/`curator`), `ts`, `evidence.session_id`. Dates custom skills and shows what is actively maintained. |

## Procedure

1. Inventory: count `SKILL.md` files under the skills dir (exclude `.hub/`)
   and size per skill.
2. Cross-reference each skill against `.usage.json` (`use_count ≥ 1` = used)
   and `.bundled_manifest` (bundled default vs custom/imported).
3. Apply the tracking-start caveat: `.usage.json` has a start date (earliest
   `created_at`). Skills last used before tracking began read `use_count: 0`
   falsely — before calling an older skill unused, check its file mtime and
   the curator ledger, and state the caveat in the report.
4. Report three groups, terse: used (with use counts + last-used dates as
   keep evidence, sorted by count); unused bundled defaults (re-obtainable
   from a fresh install, low-risk); unused custom/imported (irreplaceable).
   For an imported pack, list it at pack-folder level too — it is one unit.
   Flag separately any never-used skill created/patched within the last few
   days: a fresh skill may belong to an active project, not be garbage.
5. STOP and hand the pick back to the user. Reply in Indonesian, to the
   point: grouped list, counts, no essays.

## Deletion mechanics (only after the user picks)

- Agent-created skills (`created_by: agent`/`learn`): prefer the curator —
  reversible, keeps a pre-run backup: `hermes curator archive <skill>`;
  `hermes curator list-archived` / `hermes curator restore` to undo.
- Bundled / hub-installed skills are out of the curator's scope: remove by
  deleting the directory from the skills tree, or move it to a non-scanned
  `.archive/` folder as a safety net.
- Driving via tools: `skill_manage(action=delete)` per skill; for multi-skill
  packs delete the pack folder.

## Matching pitfalls

- Usage keys are recorded both bare (`spa-frontend-recon`) and path-qualified
  (`strix/spa-frontend-recon`); match on the basename.
- Imported packs may use underscores in dir names while the catalog shows
  dashes — normalize `_`→`-` before matching.
- Identical basenames can exist in two locations; detect duplicates and
  disambiguate by full path before any removal.

## Script

`scripts/audit_skill_usage.py [SKILLS_DIR]` (defaults to `$HERMES_HOME/skills`)
prints the full grouped breakdown above — read-only, no deletions.
