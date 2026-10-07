# Adoption packaging - manifest

- Source: https://github.com/hackerai-tech/hackerai @ `6cf55ed545a59b1a61740a857b505cf18b8fad2b`
- Adopted: 2026-10-07 into Hermes profile `testing`; extraction is machine-copied byte-exact (no retyping).

## Contents

- `build_lib.py` - resolver extracting every prompt section/string from source files (template literals, line continuations, escapes).
- `resolved_sections.json` - all 29 resolved section values (43136 chars total).
- `source/` - 90 machine-copied source files from the repo at that commit.

## Live vs archived

- Live in SOUL.md: 17-section agent-mode composition (see ../references/soul-composition.md).
- Live as skills: 62 Strix modules (profile `skills/strix/...`).
- Archived here: all prompt variants/conditional sections and auxiliary runtime prompts (see ../references/).