---
name: surfshark-proxy-automation
description: "Operate Surfshark proxy nodes, relay, and browser routing."
version: 0.2.0
author: Hermes
platforms: [linux]
metadata:
  hermes:
    tags: [Surfshark, Proxy, Openvpn, Browser, Automation]
---

# Surfshark Proxy Automation

Manages local Docker-based OpenVPN Surfshark proxy studio nodes, the public authenticated relay, and orchestrates Hermes browser sessions with dedicated proxy egress.

## Architecture & Quick Reference
- **Stack Directory:** `/root/.openclaw/workspace/projects/surfshark-proxy-studio`
- **Auth Secrets:**
  - OpenVPN Service Auth: `secrets/surfshark.auth` (Line 1: Username, Line 2: Password)
  - Public Relay Env: `secrets/public-proxy.env` (Auth credentials & host setup)
- **Local Proxy Nodes (Docker, 15 Nodes):**
  - HTTP Proxy: `http://127.0.0.1:31001` - `31015`
  - SOCKS5 Proxy: `socks5://127.0.0.1:32001` - `32015`
- **Public Authenticated Proxy Relay (`proxy-studio-public-proxy.service`):**
  - Node 01 - 04: Ports `33101` - `33104`
  - Rotating: Port `33105`
  - Ingress: Public IP `20.192.4.173:<port>` with Basic Auth (`surfstudio-proxyId-*:<password>`)
  - Cloudflare Tunnel ingress: `proxy-node1.indrayuda.my.id` -> `127.0.0.1:33101` (HTTP only)
- **Studio Dashboard & API (`proxy-studio.service`):**
  - Port `8808` (`https://proxy-studio.indrayuda.my.id`)

## Triage Procedure (When Proxy Reported "Mati")

### 1. Check Local OpenVPN Docker Nodes
Verify if the Docker containers are running and responding:
```bash
docker ps --filter "name=surfshark-node" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```
Test egress through local HTTP port:
```bash
curl -m 5 -x http://127.0.0.1:31001 -s https://api.ipify.org?format=json
```

### 2. Check Public Proxy Relay Daemon
If local Docker nodes are alive but external access or Cloudflare tunnel fails (returning 502 Bad Gateway or Connection Refused):
```bash
systemctl status proxy-studio-public-proxy.service --no-pager
```
If inactive or dead (common after host reboots if not enabled):
```bash
systemctl enable --now proxy-studio-public-proxy.service
```
Verify listening ports `33101 - 33105`:
```bash
netstat -tlpn | grep -E "3310[1-5]"
```

### 3. Verify Public Authenticated Relay Egress
Test relay egress using credentials from `secrets/public-proxy.env`:
```bash
curl -x http://surfstudio-proxyId-node01:<PASSWORD>@20.192.4.173:33101 -s https://api.ipify.org?format=json
```

## Maintenance Procedures

### Update Service Credentials
When `AUTH_FAILED` occurs in OpenVPN container logs, obtain fresh manual OpenVPN credentials from Surfshark dashboard and write them using `write_file`:
```text
<USERNAME>
<PASSWORD>
```
File path: `/root/.openclaw/workspace/projects/surfshark-proxy-studio/secrets/surfshark.auth`

### Switch Country or Server Region
Modify `remote` line in `configs/surfshark/node-*.ovpn`:
- Indonesia (Jakarta): `remote id-jak.prod.surfshark.com 1194`
- Singapore: `remote sg-sng.prod.surfshark.com 1194`
- US (New York): `remote us-nyc.prod.surfshark.com 1194`
Then restart the targeted node container:
```bash
cd /root/.openclaw/workspace/projects/surfshark-proxy-studio && docker compose restart surfshark-node-01
```

### Attach Hermes Browser to Proxy
1. Ensure `hermes-chrome-cdp.service` uses `--proxy-server="http://127.0.0.1:31001"` (or desired node port).
2. Configure Hermes CDP URL if needed:
```bash
hermes config set browser.cdp_url "http://127.0.0.1:9222"
```
3. Use `browser_exec` to navigate and verify pages with proxy IP.

## Pitfalls
- **Post-reboot relay failure:** `proxy-studio-public-proxy.service` must be enabled in systemd (`systemctl enable`), otherwise Docker containers will run after reboot but all public ports (`33101-33105`) will remain closed, causing Cloudflare 502 and external client connection refusal.
- **Cloudflare Tunnel Limitations:** Cloudflare HTTP tunnels do not support raw HTTP CONNECT tunneling over 80/443 without Cloudflare Zero Trust warp client. Mobile/desktop apps using standard proxy settings must connect directly to the public VPS IP (`20.192.4.173:<port>`).
- **OpenVPN Auth Type:** Never use regular Surfshark account email/password for OpenVPN; only manual service credentials work.
- **Headless Chrome Locks:** If restarting Chrome, remove stale `Singleton*` locks in the profile directory (`/root/.hermes/profiles/orion/browser-profile/chrome`) before spawning a new instance.
