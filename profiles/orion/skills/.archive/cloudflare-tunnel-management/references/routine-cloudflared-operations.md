---
name: cloudflared-tunnel-operations
description: Routine management, diagnostic, and routing operations for Cloudflared tunnels. Use when setting up new ingress rules, restarting tunnels, or verifying tunnel status.
---

# Cloudflared Tunnel Operations

Execute recurring routing and daemon operations consistently and safely for Cloudflare tunnels.

## Scope Guardrails

- Use this skill when requested to add a new subdomain routing entry to an existing tunnel, check tunnel status, or update Cloudflared daemon behavior.
- Use `systemctl` for daemon management instead of backgrounding the `cloudflared` binary directly via `&`.

## Modifying Ingress Rules

Use this when the user asks to point a new subdomain to a local port via an existing tunnel (e.g. `vps-baru` or `web`).

1. **Locate Config:** Check `/etc/cloudflared/` for the tunnel's config file (e.g. `config-vps-baru.yml`).
2. **Verify Config Shape:** Confirm the file contains the `ingress:` array.
3. **Patch Safely:** Use `sed` or temporary python script writes in the terminal to append the new hostname and service port directly into the file. Because it is a system-owned file, the `patch` tool cannot be used directly. Ensure no duplicate key definitions (e.g. `service`) are written during regex insertion.
4. **Local Binding Security & Host Headers:** 
   - Hermes dashboard and several local services verify host headers for security and refuse non-loopback binds unless explicitly configured.
   - When routing a service that binds strictly to `127.0.0.1`, use the `httpHostHeader` option under `originRequest` in the Cloudflare ingress entry to rewrite the header to `localhost` or `127.0.0.1`.
   - Example ingress configuration with host header rewriting:
     ```yaml
     - hostname: yoursubdomain.example.com
       service: http://127.0.0.1:9119
       originRequest:
         httpHostHeader: 127.0.0.1
     ```
5. **Restart Tunnel Service:** 
   - Verify service name (usually matches `cloudflared.service` or an instantiated unit like `cloudflared@<name>`).
   - Run `systemctl restart cloudflared`.
6. **Verify Start & DNS/Caching Pitfalls:** 
   - Wait a few seconds, then verify via `systemctl status cloudflared --no-pager` that the tunnel successfully re-established connection with Cloudflare edge nodes.
   - **Cache Poisoning Pitfall:** If an initial access to the domain fails with a 404 or 403 (due to header or path issues), Cloudflare may cache the failed response. Even after fixing the host header, subsequent requests may still return 404. Instruct the user to perform a *Hard Refresh* (`Ctrl + F5` or `Cmd + Shift + R`), use incognito mode, or purge Cloudflare cache if they get blank pages or cached errors.

## Communication Style

- Confirm exactly which tunnel and file was updated.
- Confirm exactly which target URL/domain was added and the target port.
- Notify the user to verify DNS CNAME setup if it's a new domain record.
- Keep it short and factual.