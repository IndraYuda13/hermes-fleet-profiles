# Google Stitch MCP Design Reference Integration

## Purpose
Use Google Stitch (`https://stitch.withgoogle.com/`) via Model Context Protocol (MCP) as an external visual ideation and reference engine to break LLM design homogenization.

## The Anti-Homogenization Pitfall
Token-level anti-slop rules (Obsidian `#0b0c0e`, 1px borders, tabular monospace) alone do NOT prevent an interface from feeling like "AI slop" if the high-level macro-composition defaults to predictable LLM tropes (repetitive 2-column/card-grid layouts, generic KPI blocks, standard dashboard cards). Stitch provides fresh spatial layouts and visual tension that prevent the fleet from designing into a repetitive rut.

## MCP Configuration & Integration

### Requirements
- Google Cloud Project with Stitch API enabled (`gcloud beta services mcp enable stitch.googleapis.com`).
- Authentication via `GOOGLE_CLOUD_PROJECT` (Application Default Credentials) or `STITCH_API_KEY`.

### Hermes Config (`~/.hermes/config.yaml`)
```yaml
mcp_servers:
  stitch:
    command: npx
    args:
      - -y
      - "@_davideast/stitch-mcp"
      - proxy
    env:
      GOOGLE_CLOUD_PROJECT: "your-gcp-project-id"
      # Or: STITCH_API_KEY: "your-key"
```

## Tools Provided by Stitch MCP
- `generate_screen_from_text`: Generate diverse layout variations directly from creative prompts.
- `extract_design_context`: Scan rendered screens to extract color systems, font pairings, and spatial spacing tokens.
- `fetch_screen_image` / `get_screen_image`: Download high-res preview screenshots for LENS / AURORA visual inspection.
- `fetch_screen_code` / `get_screen_code`: Inspect the prototype HTML/CSS structure.
- `list_projects` / `list_screens`: Access screens designed directly on `stitch.withgoogle.com`.

## 3-Stage Reference Execution Pattern (Anti-Copy Invariant)
1. **Ideation & Seed Generation:** Generate or fetch 2–3 candidate screens from Stitch to explore non-trivial spatial compositions (e.g. editorial broadsheets, tactile ateliers, asymmetric portfolios).
2. **Design DNA Extraction (AURORA):** Extract macro composition, spatial hierarchy, and typography tension into `DESIGN_DNA.md`. Do not copy raw code.
3. **Faithful Production Build (FRAME):** Handcraft production-grade React/Tailwind/CSS components honoring the visual inspiration while preserving real engineering data, accessibility, and zero-overflow invariants.
