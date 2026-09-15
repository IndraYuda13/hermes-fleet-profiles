# UI/UX Pro Max Archetypes Retrieval Index & Quick Queries

This reference indexes the 88 UI styles, 192 product palettes, and 74 font pairings integrated from `ui-ux-pro-max` for fast multi-agent design querying.

**Authority boundary:** this is a search index, not a direction selector. Archetype/category labels are vocabulary for retrieval after product truth and composition hypotheses exist. Never choose an archetype because a domain name appears in its `Best For` column, and never transfer an example palette/font/component grammar wholesale. `visual-authoring-core`, `DEFAULT_DEBT.md`, rendered evidence, and the accepted design contract outrank this catalog.

## 1. Fast CLI Query Examples

```bash
# Query specific style
python3 /root/.hermes/profiles/aurora/skills/creative/ui-ux-pro-max/scripts/search.py "editorial" --domain style

# Query product color palette
python3 /root/.hermes/profiles/aurora/skills/creative/ui-ux-pro-max/scripts/search.py "saas" --domain product

# Query typography pairings
python3 /root/.hermes/profiles/aurora/skills/creative/ui-ux-pro-max/scripts/search.py "tech" --domain typography

# Query UX accessibility & interaction rules
python3 /root/.hermes/profiles/aurora/skills/creative/ui-ux-pro-max/scripts/search.py "contrast" --domain ux
```

## 2. Distinct Visual Archetypes Matrix

| Archetype ID | Category | Search Traits | Common Association (not a recommendation) | Example Fonts (not defaults) |
|---|---|---|---|---|
| `editorial-grid-magazine` | Editorial / Magazine | Asymmetric multi-column, pull quotes, drop caps, print inspiration | News, Longform, Portfolios, Publications | Cormorant Garamond / Playfair + Inter / Libre Baskerville |
| `swiss-modernism-2-0` | Swiss Style | Strict mathematical grid, oversized sans, massive whitespace, no shadows | Enterprise apps, Documentation, SaaS | Inter / Helvetica Neue + Neue Haas Grotesk |
| `bauhaus` | Bauhaus / Constructivist | Primary color blocking, hard offset 4px shadow, geometric 0px radius | Artisan, Design flagship, Mobile tools | Outfit Black (900) + JetBrains Mono |
| `tactile-digital-deformable-ui` | Tactile Hardware | Teenage Engineering vibe, knurled knobs, mechanical press, LCD chips | Audio tools, Hardware controllers, Quant | IBM Plex Mono + Space Grotesk |
| `e-ink-paper` | E-Ink / Warm Paper | High contrast warm monochromatic, zero eye strain, hairline dividers | Reading platforms, Knowledge bases, Writers | Newsreader + Plus Jakarta Sans |
| `minimalist-monochrome` | Minimal Monochrome | Stark black & white, extreme contrast, surgical single accent | Flagship landing, High-end fashion, Art | Syne / Clash Grotesk + Satoshi |
| `data-dense-dashboard` | Dense Telemetry | Compact tabular density, real-time matrix, monospace stream, 0px borders | Quant trading, Security Ops, Log telemetry | JetBrains Mono + Fira Code |
| `fluent-2` / `spectrum-2` | Modern Systematic | Refined elevation, accessible semantic tokens, systematic rhythm | Enterprise B2B, Multi-tier platforms | Segoe UI / Adobe Clean + Inter |

## 3. Retrieval Rules for AURORA & FRAME
1. Treat common motifs (purple/cyan glow, rounded cards, glass, editorial serif, terminal styling, bento) as choices that require product/brief rationale, not as universal bans or recommendations.
2. Do not mistake a different costume for a different composition. Palette/font/radius/effect swaps on the same topology remain one direction.
3. Do not select an archetype from product category alone. First state mechanism/proof, reading/task path, content relationships, and candidate topology; use the catalog only to research a bounded question.
4. Record what a reference teaches and what must **not** be copied. If several borrowed traits come from one familiar style cluster, run the generic-default cluster gate.
5. Test rendered whole-viewport evidence through LENS on desktop and mobile; inspect detail crops only after macro hierarchy is visible.
