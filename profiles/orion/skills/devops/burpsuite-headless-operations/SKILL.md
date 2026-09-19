---
name: burpsuite-headless-operations
description: Use when running headless Burp Suite & BurpMCP on VPS.
---

# Burp Suite Headless & BurpMCP-Ultra Operations

Standard operating procedures for deploying, running, and integrating Burp Suite Community/Pro headless on Linux VPS with BurpMCP-Ultra (150+ tools) for AI security agents.

## 1. Headless Virtual Display Architecture
In VPS environments without a physical monitor, Burp Suite (Java Swing GUI) runs deterministically using virtual display layers:
- **`xvfb.service` (`DISPLAY=:99`):** Provides the virtual X11 framebuffer server (`Xvfb :99 -screen 0 1024x768x16 -ac +extension RANDR`).
- **`fluxbox.service`:** Lightweight window manager ensuring Burp window events, modal dialogs (Terms agreement, project wizard), and focus lifecycles are handled deterministically without stalling.
- **`burpsuite.service`:** Launches Burp Suite with user config:
  `/opt/burpsuite/BurpSuiteCommunity --user-config-file=/root/.BurpSuite/UserConfigCommunity.json`.
- **`novnc.service`:** Bridges WebSockets to VNC port `5900` on port `6080` (`websockify --web /usr/share/novnc/ 6080 localhost:5900`), enabling browser-based manual GUI inspection at `http://<IP_VPS>:6080/vnc.html`.

## 2. BurpMCP-Ultra Extension & MCP Configuration
- **Extension JAR:** `/opt/burp-extensions/burpmcp-ultra-2.3.0.jar`.
- **Default Ports:** MCP SSE endpoint at `http://127.0.0.1:9876/`, Web Dashboard at `http://127.0.0.1:9878/`.
- **Hermes Profile Allocation:**
  - Dedicated security profile (`sentinel`): Configured with Burp MCP server for security audits, proxy inspection, and exploit verification.
  - Orchestrator profile (`orion`): Coordinates via A2A mesh (port 9911) without polluting the conversational token context with 150+ tool schemas.
- **Hermes MCP Config (`~/.hermes/profiles/sentinel/config.yaml`):**
  ```yaml
  mcp_servers:
    burpmcp:
      url: "http://127.0.0.1:9876/"
      type: "sse"
      enabled: true
      headers:
        Authorization: "Bearer <TOKEN_FROM_SERVER_TAB>"
  ```
  *(Note: If client does not support custom headers, use token path: `http://127.0.0.1:9876/<TOKEN>/` with mandatory trailing slash).*

## 3. Installation & Verification
1. Install Java 21 & Xvfb: `sudo apt update && sudo apt install -y openjdk-21-jre xvfb xauth libxrender1 libxtst6 libxi6`.
2. Download & Run Burp Suite Linux installer:
   ```bash
   wget "https://portswigger.net/burp/releases/download?product=community&version=2024.12.1&type=Linux" -O burpsuite_installer.sh
   chmod +x burpsuite_installer.sh
   ./burpsuite_installer.sh -q
   ```
3. Run headless via Xvfb: `xvfb-run -a /usr/local/BurpSuiteCommunity/BurpSuiteCommunity &` (or supervise via systemd, see `references/systemd-novnc-architecture.md`).
4. Load BurpMCP-Ultra JAR (`/opt/burp-extensions/burpmcp-ultra-2.3.0.jar`) in Burp Extensions (Java Extension).
5. Verify ports: `9876` (MCP SSE), `9878` (Dashboard), `6080` (noVNC web GUI), and `8080` (proxy listener).
