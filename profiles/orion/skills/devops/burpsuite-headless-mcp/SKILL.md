---
name: burpsuite-headless-mcp
description: "Use when running Burp Suite headless with MCP in Linux VPS."
---

# Burp Suite Headless & BurpMCP-Ultra Architecture Guide

Panduan operasional setup Burp Suite Community / Pro di lingkungan Linux Headless (VPS Ubuntu) dan integrasi Model Context Protocol (MCP) untuk AI Security Agent.

---

## 1. Arsitektur Komponen Headless

Di VPS tanpa display monitor fisik, Burp Suite (Java Swing GUI) dioperasikan secara stabil menggunakan stack:

```
[PortSwigger Burp Suite] (DISPLAY=:99)
          │
    (X11 Socket)
          ▼
    [Xvfb :99] ◄─── [Fluxbox WM] (Window management & dialog lifecycle)
          │
    (RFB 5900)
          ▼
      [x11vnc] ◄─── [noVNC / Websockify] (Port 6080 HTTP Web GUI)
```

1. **`xvfb.service`**: Menyediakan virtual X11 server di display `:99`.
2. **`fluxbox.service`**: Window Manager ringan agar Burp window events & dialog focus (Terms agreement, project wizard) dapat dikontrol secara deterministik.
3. **`burpsuite.service`**: Menjalankan `/opt/burpsuite/BurpSuiteCommunity --user-config-file=/root/.BurpSuite/UserConfigCommunity.json`.
4. **`novnc.service`**: Bridge WebSocket ke VNC di port `6080` sehingga operator/human dapat menginspeksi atau mengonfigurasi Burp GUI via web browser di `http://<IP_VPS>:6080/vnc.html`.

---

## 2. BurpMCP-Ultra Extension & MCP Configuration

Extension `BurpMCP-Ultra` mengekspos 150+ tools Burp Suite (Proxy history, Repeater, Scanner, Fuzzer, JWT analysis, Collaborator) via Server-Sent Events (SSE) endpoint.

* **Lokasi Extension JAR:** `/opt/burp-extensions/burpmcp-ultra-2.3.0.jar`
* **Default MCP Port:** `http://127.0.0.1:9876/`
* **Default Dashboard Port:** `http://127.0.0.1:9878/`

### Konfigurasi Hermes MCP (`config.yaml` / profile `sentinel`)

```yaml
mcp_servers:
  burpmcp:
    url: "http://127.0.0.1:9876/"
    type: "sse"
    enabled: true
```

---

## 3. Integrasi & Routing Profile Hermes

* **Profile `sentinel`:** Spesialis Security & Threat Audit armada. Semua investigasi keamanan, proxy analysis, dan exploit verification dialokasikan ke Sentinel.
* **Profile `orion`:** Chief of Staff / Orchestrator. Mengoordinasikan penugasan via A2A mesh (port `9911` untuk Sentinel) tanpa membebani context token dengan 150 tools MCP secara langsung.
* **Open Pentest Skills:** 253 Playbooks tersimpan di `/root/.hermes/skills/open-pentest/` sebagai referensi taktis dan SOP pengujian parameter, injection, IDOR, hingga CTF.
