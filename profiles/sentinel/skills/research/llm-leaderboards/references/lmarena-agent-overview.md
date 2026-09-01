# LMArena Agent arena (overview scrape)

Source: `https://lmarena.ai/leaderboard` → `https://arena.ai/leaderboard`

## When overview is enough
- User asks top ≤10 for Agent / Text / WebDev / Vision / Document
- `browser_navigate` + first snapshot already has each arena's top-10 chart
- Skip tab clicks unless rank >10, filters, or subcategory needed

## Agent metric
- Ranked by **net improvement %**, not Elo
- Format in snapshot: `12.72` + `%` + `±2.00%`
- Report as net improvement, not "score"

## Snapshot gotchas
- Model names may include mode suffixes: `(High)`, `(xHigh)`, `(Thinking)`, `(Max)`, harness tags like `(codex-harness)`
- Org icon text is incomplete (Anthropic/Meta often present; others often missing) — never invent vendor
- Snapshot can be huge (truncated with path under `~/.hermes/cache/web/`); Agent block is near the top of the overview, before Text

## Output shape (Boskuu / short)
Numbered or table: rank | exact model string | metric as shown | source link
