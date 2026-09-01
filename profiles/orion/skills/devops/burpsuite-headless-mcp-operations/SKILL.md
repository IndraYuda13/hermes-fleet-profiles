---
name: burpsuite-headless-mcp-operations
description: "Use when running headless Burp Suite & BurpMCP on VPS."
---

# Burp Suite Headless & BurpMCP-Ultra Operations

Standard Operating Procedure untuk menginstal, menjalankan Burp Suite secara headless di VPS Ubuntu, dan mengintegrasikan **BurpMCP-Ultra** (150 tools) ke AI Agent Hermes / Sentinel via Model Context Protocol (MCP).

## 1. Arsitektur & Penempatan Profile Hermes
- **Separation of Concerns**: Pasang Burp MCP Server pada profile spesialis security (`sentinel`) atau fallback global (`~/.hermes/config.yaml`).
- **Token Efficiency**: Hindari memasang 150 tools Burp langsung di profile orchestrator (`orion`) untuk mencegah overhead token context pada percakapan general.

## 2. Instalasi Burp Suite Headless di Ubuntu
```bash
# 1. Dependensi Java & Virtual Framebuffer
sudo apt update
sudo apt install -y openjdk-21-jre xvfb xauth libxrender1 libxtst6 libxi6

# 2. Download Installer Burp Suite Linux x64
wget "https://portswigger.net/burp/releases/download?product=community&version=2024.12.1&type=Linux" -O burpsuite_installer.sh
chmod +x burpsuite_installer.sh
./burpsuite_installer.sh -q

# 3. Jalankan Headless via Xvfb
xvfb-run -a /usr/local/BurpSuiteCommunity/BurpSuiteCommunity &
```

## 3. Instalasi Extension BurpMCP-Ultra
1. Download release JAR terbaru dari `Cy-S3c/BurpMCP-Ultra` (misal `burpmcp-ultra-2.3.0.jar`).
2. Muat JAR ke Burp Suite Extensions (Java Extension).
3. Server MCP aktif secara default pada port `http://127.0.0.1:9876/` (SSE) dan Dashboard pada `http://127.0.0.1:9878`.

## 4. Konfigurasi MCP di Hermes
Tambahkan ke `~/.hermes/profiles/sentinel/config.yaml`:
```yaml
mcp_servers:
  burp:
    url: "http://127.0.0.1:9876/"
    type: "sse"
    headers:
      Authorization: "Bearer <TOKEN_FROM_SERVER_TAB>"
```

Jika client tidak mendukung custom headers, gunakan format token path:
```yaml
mcp_servers:
  burp:
    url: "http://127.0.0.1:9876/<TOKEN_FROM_SERVER_TAB>/"
    type: "sse"
```
*(Wajib sertakan trailing slash `/`)*.
