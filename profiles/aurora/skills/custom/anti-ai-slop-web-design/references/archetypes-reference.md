# UI/UX Pro Max Archetypes Reference & Quick Queries

This reference indexes the 88 UI styles, 192 product palettes, and 74 font pairings integrated from `ui-ux-pro-max` for fast multi-agent design querying.

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

| Archetype ID | Category | Key Traits | Best For | Primary Fonts |
|---|---|---|---|---|
| `editorial-grid-magazine` | Editorial / Magazine | Asymmetric multi-column, pull quotes, drop caps, print inspiration | News, Longform, Portfolios, Publications | Cormorant Garamond / Playfair + Inter / Libre Baskerville |
| `swiss-modernism-2-0` | Swiss Style | Strict mathematical grid, oversized sans, massive whitespace, no shadows | Enterprise apps, Documentation, SaaS | Inter / Helvetica Neue + Neue Haas Grotesk |
| `bauhaus` | Bauhaus / Constructivist | Primary color blocking, hard offset 4px shadow, geometric 0px radius | Artisan, Design flagship, Mobile tools | Outfit Black (900) + JetBrains Mono |
| `tactile-digital-deformable-ui` | Tactile Hardware | Teenage Engineering vibe, knurled knobs, mechanical press, LCD chips | Audio tools, Hardware controllers, Quant | IBM Plex Mono + Space Grotesk |
| `e-ink-paper` | E-Ink / Warm Paper | High contrast warm monochromatic, zero eye strain, hairline dividers | Reading platforms, Knowledge bases, Writers | Newsreader + Plus Jakarta Sans |
| `minimalist-monochrome` | Minimal Monochrome | Stark black & white, extreme contrast, surgical single accent | Flagship landing, High-end fashion, Art | Syne / Clash Grotesk + Satoshi |
| `data-dense-dashboard` | Dense Telemetry | Compact tabular density, real-time matrix, monospace stream, 0px borders | Quant trading, Security Ops, Log telemetry | JetBrains Mono + Fira Code |
| `fluent-2` / `spectrum-2` | Modern Systematic | Refined elevation, accessible semantic tokens, systematic rhythm | Enterprise B2B, Multi-tier platforms | Segoe UI / Adobe Clean + Inter |

## 3. Anti-Slop Golden Rules for AURORA & FRAME
1. **Never use generic purple/cyan gradient glow cards.**
2. **Never round everything with `rounded-2xl` or `rounded-3xl`.**
3. **Never apply `backdrop-blur-md` glassmorphism as a default.**
4. **Never fall into binary over-correction by turning every UI into a black hacker terminal.**
5. **Always declare an explicit visual archetype matching the product domain before generating HTML/CSS.**
6. **Always test real-browser rendering via LENS across Desktop (1920x1080) and Mobile (390x844).**
