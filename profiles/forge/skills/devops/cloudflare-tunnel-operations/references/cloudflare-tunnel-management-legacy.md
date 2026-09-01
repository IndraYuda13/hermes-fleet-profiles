---
name: cloudflare-tunnel-management
description: Manage, configure, expose, and troubleshoot web services routed via Cloudflare Tunnels (cloudflared) on the VPS.
category: devops
---

# Cloudflare Tunnel Management

Use this skill when exposing new local services to the internet via Cloudflare Tunnels (`cloudflared`), managing ingress configurations, updating DNS mappings, or troubleshooting tunnel connection issues (such as blank pages, 400 Bad Request, or 404 errors).

## Trigger Conditions
- Exposing a local port/service (e.g. FastAPI, Node, Web UIs) via a subdomain (e.g. `*.indrayuda.my.id`).
- Adding, editing, or removing entries in `/etc/cloudflared/config-*.yml`.
- Mapping DNS CNAME records to Cloudflare Tunnels.
- Debugging connection or routing issues through tunnels.

## Step-by-Step Workflow

### 1. Identify the Active Tunnel Configuration
List available tunnels and identify the active one:
```bash
cloudflared tunnel list
```
Find the active config file, typically located in `/etc/cloudflared/config-<tunnel-name>.yml`.

### 2. Update the Ingress Configuration
Edit the configuration file to map the new hostname to the local service port.
```yaml
ingress:
  - hostname: service.indrayuda.my.id
    service: http://127.0.0.1:PORT
```
> **⚠️ Critical Pitfall (Host Header Validation):**
> Many web dashboards or APIs (like the Hermes Agent Dashboard) validate the incoming HTTP `Host` header for security. If accessed via a public hostname through a tunnel, they will return a `400 Bad Request` or an empty/blank page. 
> To bypass this, force the tunnel to rewrite the host header to `localhost` or `127.0.0.1` by adding `originRequest`:
> ```yaml
>   - hostname: service.indrayuda.my.id
>     service: http://127.0.0.1:PORT
>     originRequest:
>       noTLSVerify: true
>       httpHostHeader: 127.0.0.1
> ```

Always place the fallback `service: http_status:404` at the very end of the `ingress` list.

### 3. Apply the Config Changes
Restart the `cloudflared` daemon to apply the ingress changes:
```bash
systemctl restart cloudflared
```
Verify the daemon status:
```bash
systemctl status cloudflared
```

### 4. Configure DNS Routing
Ensure the DNS record for the subdomain is created and routed to the correct tunnel ID:
```bash
cloudflared tunnel route dns -f <TUNNEL_ID> <HOSTNAME>
```
*Note: Use the `-f` (force) flag to overwrite any existing CNAME records that might be pointing to a different tunnel ID. If you omit `-f` and a record already exists for that name, the command will fail with a Cloudflare API error (Code 1003).*

---

## Troubleshooting Pitfalls

### Issue: The page remains blank or returns a Cloudflare cached 404/403
- **Root Cause:** If the initial request failed because of an incorrect host header or wrong DNS mapping, Cloudflare might cache the error state (especially for static assets like `.js` or `.css` files).
- **Resolution:**
  1. Test the service locally on the VPS using `curl -sI -H "Host: 127.0.0.1" http://127.0.0.1:PORT` to ensure it is serving content.
  2. Perform a hard refresh in the browser (`Ctrl + F5` or `Cmd + Shift + R`).
  3. Purge the Cloudflare cache for the target zone from the Cloudflare Dashboard (**Caching -> Configuration -> Purge Everything**).

### Issue: "mapping key already defined" YAML error
- **Root Cause:** Duplicate YAML keys under the same ingress hostname entry.
- **Resolution:** Double check the ingress list structure. Ensure each hostname mapping has exactly one `service` key.

## References
- See `references/hermes-dashboard-setup.md` for a complete example of setting up the Hermes Dashboard behind a Cloudflare Tunnel with a systemd service.
