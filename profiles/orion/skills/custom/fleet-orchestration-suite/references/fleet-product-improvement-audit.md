# Fleet Product Improvement Audit Workflow

## Overview
When the user asks open-ended improvement questions about an existing web application or service (e.g., "what can be improved on X?", "audit this web app", "find weaknesses in our checkout"), ORION should conduct a structured fleet-wide audit rather than relying on solo intuition.

## Step-by-Step Procedure

### 1. Direct Source Grounding (Zero-Hallucination Invariant)
Before contacting any specialist, ORION must inspect the actual codebase on disk:
- Locate the repository / project files (`find`, `search_files`, `read_file`)
- Read core architecture files: entry points, state management, API routes, database schemas, styling tokens, and deployment service files
- Identify key facts: frontend stack, backend integration status, payment gateways, authentication model, and database structures
- Never prompt specialists with hypothetical descriptions when real source is available

### 2. Formulating the Specialist Task Payload
Construct a comprehensive briefing for `a2a_orchestrate`:
- State the product context and target URL / directory path
- List concrete architectural facts discovered in step 1 (lines of code, state patterns, hardcoded fixtures, active daemons, database locations)
- Explicitly ask each specialist for their **single highest-impact recommendation from their specialty domain**
- Instruct specialists to be concrete and actionable (cite line numbers, specific endpoints, or architectural disconnects)

### 3. Native Fan-Out via `a2a_orchestrate`
```python
a2a_orchestrate(
    capability="*",
    message="TASK: Review [Product Name] ... KEY FACTS: [Facts list] ... Please give your single most impactful recommendation from your specialty.",
    mode="all"
)
```

### 4. Synthesis & Prioritization Matrix
Synthesize the peer responses into a decision-ready hierarchy:
1. **Critical / Business-Blocking (Revenue Zero):** Disconnects between frontend and backend, dead mockups, missing endpoints
2. **Security & Data Integrity:** Price manipulation in client state, missing server-side validation, unauthenticated webhooks
3. **UX & Conversion Optimization:** Funnel friction, redundant wizard steps, lack of price anchoring or per-unit savings
4. **Implementation & Performance:** Fragile DOM re-renders (`innerHTML`), missing persistence, accessibility concerns
5. **Operational / SRE Handoff:** Missing API contracts, lack of health checks, deployment misconfigurations

### 5. Kanban Task Dispatch Pitfalls

#### `kanban_create` Tool vs CLI
The `kanban_create` tool schema does NOT expose a `title` parameter, but the kernel requires it. If the tool call fails with `title is required`, fall back to the CLI.

#### Shell Body Injection (Critical Pitfall)
When using `hermes kanban create` via terminal with a `--body` argument, special characters in the body (backticks, `$variables`, paths with `/`, URLs with `://`, angle brackets `<>`, pipe `|`) cause bash expansion and corrupt the task body.

**Working pattern:**
```python
# 1. Write body to temp file using write_file (avoids shell entirely)
write_file("/tmp/task_body.md", body_content)
# 2. Inject via $(cat ...)
terminal('hermes kanban create "Title" --assignee forge --body "$(cat /tmp/task_body.md)" --workspace "dir:/path" --goal --json')
```
**Never** pass body content directly as an inline string in `terminal()` — bash interprets it.

### 6. Final Synthesis Standard
- Acknowledge what is already well-built to maintain constructive framing
- Present findings with clear "Problem → Impact → Fix" structure
- Provide a concise executive TL;DR with the single highest-priority next step
- Offer immediate decomposition into actionable Kanban tasks
