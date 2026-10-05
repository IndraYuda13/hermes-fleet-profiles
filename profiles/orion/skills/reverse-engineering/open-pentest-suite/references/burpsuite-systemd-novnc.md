# Burp Suite & noVNC Systemd Integration

## 1. Systemd Service Templates

### `/etc/systemd/system/xvfb.service`
```ini
[Unit]
Description=X Virtual Frame Buffer Service
After=network.target

[Service]
ExecStart=/usr/bin/Xvfb :99 -screen 0 1024x768x16 -ac +extension RANDR
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### `/etc/systemd/system/fluxbox.service`
```ini
[Unit]
Description=Fluxbox Window Manager for Burp
After=xvfb.service
Requires=xvfb.service

[Service]
Environment=DISPLAY=:99
ExecStart=/usr/bin/fluxbox
Restart=always
User=root

[Install]
WantedBy=multi-user.target
```

### `/etc/systemd/system/novnc.service`
```ini
[Unit]
Description=noVNC Web Interface for Burp Suite GUI
After=xvfb.service
Requires=xvfb.service

[Service]
ExecStart=/usr/bin/websockify --web /usr/share/novnc/ 6080 localhost:5900
Restart=always
User=root

[Install]
WantedBy=multi-user.target
```

### `/etc/systemd/system/burpsuite.service`
```ini
[Unit]
Description=Burp Suite Community Headless with MCP
After=xvfb.service fluxbox.service
Requires=xvfb.service fluxbox.service

[Service]
Type=simple
Environment=DISPLAY=:99
Environment=JAVA_HOME=/opt/burpsuite/jre
ExecStart=/opt/burpsuite/BurpSuiteCommunity --user-config-file=/root/.BurpSuite/UserConfigCommunity.json
Restart=always
RestartSec=10
TimeoutStartSec=60
User=root

[Install]
WantedBy=multi-user.target
```

## 2. Port Architecture
- `5900`: x11vnc RFB raw port (local only)
- `6080`: noVNC HTTP WebSocket Web GUI (`http://localhost:6080/vnc.html`)
- `8080`: Burp Suite HTTP/HTTPS Proxy Listener
- `9876`: BurpMCP-Ultra MCP SSE Server Endpoint
- `9878`: BurpMCP-Ultra Realtime Web Dashboard
