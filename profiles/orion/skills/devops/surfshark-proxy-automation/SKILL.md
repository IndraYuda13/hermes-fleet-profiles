---
name: surfshark-proxy-automation
description: "Operate Surfshark proxy nodes and browser integration."
version: 0.1.0
author: Hermes
platforms: [linux]
metadata:
  hermes:
    tags: [Surfshark, Proxy, Openvpn, Browser, Automation]
---

# Surfshark Proxy Automation

Manages local Docker-based OpenVPN Surfshark proxy studio nodes and orchestrates Hermes browser sessions with dedicated proxy egress.

## When to Use
- Starting, switching, or repairing local Surfshark proxy nodes.
- Routing Hermes browser automation (`browser_exec`, Playwright, CDP) through Indonesian or international residential/VPN IPs.
- Diagnosing authentication failures (`AUTH_FAILED`), credential rot, or regional egress routing.

## Prerequisites
- Working Docker Compose stack in `/root/.openclaw/workspace/projects/surfshark-proxy-studio`.
- Valid manual OpenVPN service credentials stored in `secrets/surfshark.auth`.
- Tools available: `terminal`, `browser_exec`, `write_file`, `read_file`.

## Quick Reference
- Config directory: `/root/.openclaw/workspace/projects/surfshark-proxy-studio`
- Auth file: `secrets/surfshark.auth` (Line 1: Username, Line 2: Password)
- Node configs: `configs/surfshark/node-*.ovpn`
- HTTP Proxy: `http://127.0.0.1:31001`
- SOCKS5 Proxy: `socks5://127.0.0.1:32001`

## Procedure

### 1. Update Service Credentials
When `AUTH_FAILED` occurs, obtain fresh manual OpenVPN credentials from Surfshark dashboard and write them using `write_file`:
```text
<USERNAME>
<PASSWORD>
```
File path: `/root/.openclaw/workspace/projects/surfshark-proxy-studio/secrets/surfshark.auth`

### 2. Switch Country or Server Region
Modify `remote` line in `configs/surfshark/node-01.ovpn`:
- Indonesia (Jakarta): `remote id-jak.prod.surfshark.com 1194`
- Singapore: `remote sg-sng.prod.surfshark.com 1194`
- US (New York): `remote us-nyc.prod.surfshark.com 1194`

### 3. Start Node Container
Invoke through the `terminal` tool with `background=True`:
```bash
cd /root/.openclaw/workspace/projects/surfshark-proxy-studio && docker compose up surfshark-node-01
```

### 4. Verify Proxy Egress IP
Invoke through the `terminal` tool:
```bash
curl -x http://127.0.0.1:31001 -s https://api.ipify.org?format=json
```

### 5. Attach Hermes Browser to Proxy
1. Launch dedicated Chrome via `terminal` (`background=True`):
```bash
/opt/google/chrome/chrome --remote-debugging-port=9222 --user-data-dir=/root/.hermes/profiles/orion/browser-profile/chrome --proxy-server="http://127.0.0.1:31001" --headless=new --no-sandbox --disable-dev-shm-usage --noerrdialogs --ozone-platform=headless --window-size=1280,800
```
2. Configure Hermes CDP URL and reload browser daemon:
```bash
hermes config set browser.cdp_url "http://127.0.0.1:9222"
```
3. Use `browser_exec` to navigate and verify pages with proxy IP.

## Pitfalls
- Do not use regular Surfshark account email/password for OpenVPN; only manual service credentials work.
- In headless Chrome mode, extension-based VPN UI popups are inaccessible; use `--proxy-server` CLI parameter routing instead.
- If restarting Chrome, remove stale `Singleton*` locks in the profile directory before spawning a new instance.

## Verification
Run `terminal` command:
```bash
curl -x http://127.0.0.1:31001 -s https://api.ipify.org?format=json
```
Expected output contains the active VPN server IP (e.g., `93.185.162.x` for Indonesia).
