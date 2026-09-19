# Postman MCP Workflow & API Management

Navigation hierarchy, collection generation, and troubleshooting patterns when interacting with Postman via MCP (`mcp_postman_*`).

## 1. Resource Navigation Hierarchy

1. **Resolve User:** Call `mcp_postman_getAuthenticatedUser` to obtain `user.id`. Scoping to the user is required for workspace queries.
2. **Resolve Workspaces:** Call `mcp_postman_getWorkspaces` with `createdBy={user.id}`. Collections and environments are siloed per workspace; there is no global collection listing.
3. **Fetch Scoped Resources:** Iterate through workspace IDs to call `mcp_postman_getCollections(workspace=...)` or `mcp_postman_getEnvironments(workspace=...)`.
4. **Inspect Requests:** `mcp_postman_getCollection` returns a lightweight summary by default. Pass `model="full"` and use the collection's `uid` (`<OWNER_ID>-<UUID>`) to inspect actual request URLs, headers, and body configurations.

## 2. Collection Creation & Modification via MCP

- **Tool:** Use `mcp__postman__createCollection` or `mcp__postman__putCollection`.
- **Schema:** Pass collections conforming strictly to Postman Collection v2.1.0 schema (requires `info` and `item` array).
- **URL Schema Rule:** Always define request URLs as objects (`"url": { "raw": "https://..." }`). Passing a bare string causes the Postman API to silently drop the URL and store `""`.

## 3. Execution & Workarounds

- **Individual Request Execution:** Reconstruct requests as `curl` commands and run them in the terminal rather than using complex SDK runner loops unless executing full folders.
- **Missing Variables:** If `mcp_postman_getEnvironments` is empty, requests depending on environment variables (`client_id`, `client_secret`) will fail. Verify environment bindings before running.
- **Firecrawl SDK V1 Direct Invocation:** When self-hosted Firecrawl via `firecrawl-py` (v4) fails on v2 endpoint mismatches in native tools, call `V1FirecrawlApp(api_url="...", api_key="...")` directly via Python script.
