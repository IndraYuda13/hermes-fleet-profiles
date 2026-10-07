# SOUL.md composition (adopted)

Installed at `/root/.hermes/profiles/testing/SOUL.md`. Composed verbatim from HackerAI resolved sections, in HackerAI assembler order (`systemPrompt()` in lib/system-prompt.ts).

Sections, in order:

1. `identity` (1142 chars)
2. `language` (323 chars)
3. `general` (404 chars)
4. `style` (482 chars)
5. `evidence` (230 chars)
6. `freshness` (1114 chars)
7. `mode_agent` (202 chars)
8. `tool_calling` (1946 chars)
9. `approval_full` (278 chars)
10. `lifecycle` (1055 chars)
11. `hygiene` (1268 chars)
12. `parallel` (1520 chars)
13. `scan` (554 chars)
14. `finding_quality` (2661 chars)
15. `deliverable` (1820 chars)
16. `delegation` (2391 chars)
17. `posture_local` (3929 chars)

Total: 21352 chars. Cap for ds@128K ctx: max(20K, min(ctx*4*0.06, 500K)) = 30,720 chars -> fits with 9368 chars headroom.

Skipped conditionals (kept in core-system-prompt-variants.md):
- sandbox_default (describes HackerAI cloud sandbox runtime — false environment for this profile)
- local_machine / product_free / product_pro (HackerAI free-tier product messaging)
- ask_free / ask_pro (ask-mode variants; this profile runs agent behavior)
- approval_ask / approval_auto (other approval modes; SOUL uses Full access = profile approvals off)
- posture_ask / posture_cloud (other execution environments; SOUL uses local-host posture)
- deepseek (model-conditional web-tool economy note)
- boundary (`<runtime_context>` anchor — internal caching marker, runtime context handled by Hermes)

Rebuild: use `scripts/build_lib.py` + `scripts/resolved_sections.json` + `scripts/source/` (preserved inside this skill under `scripts/`).
Verify: `hermes -p testing prompt-size --json`.