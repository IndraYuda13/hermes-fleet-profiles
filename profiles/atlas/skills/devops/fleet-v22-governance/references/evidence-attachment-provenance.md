# Evidence Attachment Provenance

Operating the kanban attachment store when relaying, replacing, or certifying evidence artifacts.
Depth for `fleet-v22-governance` Rule 5: the always-on rules stay in SKILL.md, this file carries
only the store mechanics that matter sometimes.

## Board scoping

- `hermes kanban attach` without `--board <slug>` resolves against the *default* board and fails with
  `unknown task <task_id>` even when the task exists on a project board. The error names the task,
  never the board, so it reads as a missing task and tempts you to conclude the id is wrong. Pass
  `--board <slug>` on the CLI (or `board=` to the `kanban_attach` tool) whenever the task is not on
  `default`.

## Staging transports

- If a base64/`.b64` staging fallback was created before the by-path attach succeeded, delete it once
  the real attachments land: a stale transport beside the canonical copies invites a downstream lane
  to re-attach duplicates. Create the encoding in scratch (`$TMPDIR`) and attach from there. A
  `.b64`/encoded copy written into the report or evidence directory becomes indistinguishable from a
  run artefact in the next lane's listing and gets attached as if a run produced it. When a peer asks
  you to write an encoding INTO the evidence directory, that request is the signal to stage elsewhere
  and hand back the hash plus the stored path instead.

## Identifying the current copy

- **By hash, never by filename or id.** The attachment store renames on collision instead of
  overwriting, so a dedup variant (`Name (1).md`, `Name (2).md`) holds real bytes while the canonical
  `Name.md` can hold older ones. Record id, upload recency, and the filename a peer quotes prove
  nothing about currency. Hash every candidate against the source and classify each CURRENT or STALE;
  the artifact you delete must be the mismatching one.
- **A name-based reader cannot see a content swap.** Replacing bytes under an unchanged canonical
  filename leaves other lanes reading correct content, but any consumer that cached the old attachment
  id or `created_at` keeps the stale bytes. Report the new attachment id in the handoff so name-caching
  consumers refresh; a consumer holding only the name cannot detect the swap.
- **Identical names are indistinguishable in the CLI listing.** `hermes kanban attachments <task_id>`
  prints id, size, and uploader but not a content hash, so two variants read as ordinary siblings.
  Resolve ambiguity from the bytes on disk under `attachments/<task_id>/`, not from the listing. The
  CLI removes by id: `hermes kanban attach-rm <attachment_id>`.

## Replace-before-prune ordering

To leave exactly one canonical copy: (1) remove the stale holder to free the canonical name,
(2) attach the current source under the canonical name, (3) confirm the new copy's hash equals the
source, (4) only then remove the redundant duplicate. Guard step 4 with `cmp`/hash equality against
the new canonical copy so no unique bytes can be dropped. The name being briefly free between steps 1
and 2 is harmless; the *content* must never be at zero live copies. Deleting the current copy in an
early wave because the plan listed it first is the failure this ordering exists to prevent.

## Uploader provenance

- Set `--author` to the profile that actually performed the upload. If ownership is already wrong,
  remove and re-attach (`hermes kanban attach-rm <id>`, then attach again) rather than leaving a
  misattributed artifact in the evidence set.
