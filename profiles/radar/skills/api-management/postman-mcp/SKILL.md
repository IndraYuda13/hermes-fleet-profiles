---
name: postman-mcp
description: "Workflow for navigating Postman via MCP: resolving user, workspaces, and fetching collections."
---

# Postman MCP Workflow

When interacting with the Postman MCP server to retrieve collections, environments, or mocks, follow this hierarchy:

## 1. Resolve User
Call `mcp_postman_getAuthenticatedUser` to get the `user.id`. This is required to scope subsequent queries to the current user.

## 2. Resolve Workspaces
Call `mcp_postman_getWorkspaces` with `createdBy={user.id}`. This returns the IDs of workspaces owned by the user. 

## 3. Fetch Scoped Resources
Tools like `mcp_postman_getCollections` or `mcp_postman_getEnvironments` require a `workspace` ID. To list all resources in an account, iterate through the workspace IDs found in step 2 and call the respective tool for each ID.

## 4. Creating Collections via MCP
When asked to create a collection, use `mcp__postman__createCollection`.
- **Do not** generate local `.postman_collection.json` files or use the missing `postman` CLI unless the MCP server is unavailable.
- **Workflow:** Get User (`getAuthenticatedUser`) -> Get Workspaces (`getWorkspaces`) -> Call `createCollection` with the target `workspace` ID.
- **Payload:** The `collection` argument must strictly follow the Postman Collection v2.1.0 schema (requires `info` and `item` array).

### Pitfalls
- **No Global Collection List:** Collections and environments are siloed per workspace. You cannot fetch "all collections" in one API call; you must loop over workspaces.
- **Do not guess IDs:** Always traverse the hierarchy: User -> Workspaces -> Collections/Resources.
- **Collection ID Format:** When calling `mcp_postman_getCollection`, the `collectionId` parameter requires the collection's `uid` (format: `<OWNER_ID>-<UUID>`), not just the UUID `id`. Use the `uid` field from the `getCollections` list.
- **Retrieving & Executing Requests:** By default, `mcp_postman_getCollection` returns a lightweight map. To view actual request URLs, headers, and body configurations, you MUST pass `model="full"`. To execute a request, reconstruct it as a `curl` command and run it directly in the terminal—do not use Postman runner tools or SDKs unless executing full folder loops.
- **Missing Credentials/Variables:** Before manually executing requests from a collection, verify if required variables exist. If `mcp_postman_getEnvironments` is empty, requests will likely fail due to missing context (like `client_id`, `client_secret`, or `grant_type`).
- **Creating/Updating Requests (URL format):** When passing request data to `mcp__postman__createCollection` or `mcp__postman__putCollection`, always define the URL as an object (`"url": { "raw": "https://..." }`). Passing a plain string causes the Postman API to silently drop the URL and save it as an empty string `""`.
- **Handling Internal Firecrawl SDK Bugs:** When using `firecrawl` self-hosted via `firecrawl-py` (v4), the native Hermes tools (`web_extract`, `web_search`) might fail due to v2 endpoint mismatches. Bypass the tools and call the `V1FirecrawlApp` directly via Python script (`from firecrawl import V1FirecrawlApp; app = V1FirecrawlApp(api_url="...", api_key="...")`).