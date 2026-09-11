---
name: google-stitch-mcp
description: "Use when using Google Stitch MCP for UI design references."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [stitch, google, mcp, design, ui, frontend]
    category: creative
---

# Google Stitch MCP Skill

Google Stitch (`stitch.withgoogle.com`) provides an official Model Context Protocol (MCP) server at `https://stitch.googleapis.com/mcp` for AI-powered UI/UX design generation, screen extraction, and design system authoring.

## When to Use

- Connecting Hermes Agent or IDE coding agents to Google Stitch via MCP.
- Generating UI screens, layout variations, and prototypes from natural language prompts.
- Extracting raw HTML/CSS and high-resolution screenshots from Stitch project screens.
- Synchronizing Google `DESIGN.md` token specifications directly with Stitch design systems.
- Using Stitch screens as external visual references and composition anchors without blindly cloning templates.

## Hermes MCP Configuration

Stitch supports direct HTTP transport using the `X-Goog-Api-Key` header. Add the following entry to `~/.hermes/config.yaml` under `mcp_servers`:

```yaml
mcp_servers:
  stitch:
    url: "https://stitch.googleapis.com/mcp"
    headers:
      X-Goog-Api-Key: "<STITCH_API_KEY>"
    timeout: 180
```

## Available MCP Tools

| Tool Name | Purpose | Key Arguments |
|---|---|---|
| `list_projects` | List existing projects and metadata | `{}` |
| `get_project` | Retrieve project details, theme, and designMd | `name: "projects/<id>"` |
| `create_project` | Create a new project workspace | `title: "Project Name"` |
| `list_screens` | List screens within a project | `projectId: "projects/<id>"` |
| `get_screen` | Get screen metadata, HTML code URL, and screenshot | `name: "projects/<id>/screens/<id>"` |
| `generate_screen_from_text` | Generate a new UI screen based on a prompt | `prompt: "...", projectId: "projects/<id>"` |
| `edit_screens` | Modify existing screen elements via prompt | `screenIds: [...], prompt: "..."` |
| `generate_variants` | Generate visual or thematic variants of a screen | `screenId: "...", variantCount: N` |
| `upload_design_md` | Upload a local `DESIGN.md` spec to a Stitch project | `projectId: "...", designMd: "..."` |
| `create_design_system_from_design_md` | Create a Stitch design system from `DESIGN.md` | `designMd: "..."` |

## Design Reference Workflow (Anti-Slop Practice)

1. **Ideate in Stitch (On-Demand / User-Selected Only):** Use Stitch manually in the browser (`stitch.withgoogle.com`) or as an occasional manual reference tool when exploring unusual layouts. Avoid automating heavy batch generation pipelines across every task to prevent excessive token and API consumption.
2. **Extract Context:** Fetch `designMd` and screenshot URLs (`get_screen`) only when an explicit project ID or screen is provided.
3. **Analyze Composition:** Review typography scale, whitespace ratios, and layout rhythm rather than copying code verbatim.
4. **Implement Cleanly:** Build production components with clean semantic HTML/Tailwind tailored to the target application.
