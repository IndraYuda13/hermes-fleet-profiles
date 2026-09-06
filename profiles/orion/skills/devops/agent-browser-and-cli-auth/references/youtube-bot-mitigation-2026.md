# YouTube Headless Ingestion & Bot Mitigation (2026)

## Problem Overview
Automated ingestion workflows using `yt-dlp` on datacenter/cloud VPS (Azure, AWS, GCP, Hetzner) face aggressive multi-tier anti-bot gating from YouTube:
1. **HTTP 403 / "Sign in to confirm you're not a bot"** on player API queries from datacenter subnets.
2. **Session Rotation / Cookie Invalidation**: Exported cookies (`cookies.txt` or JSON) used from a distant datacenter IP trigger security heuristics:
   `"The provided YouTube account cookies are no longer valid. They have likely been rotated in the browser as a security measure."`
3. **Missing JS Runtime for Challenge Solving**: Modern YouTube requires JS challenge solvers (`n-challenge`, PO token). Without Node.js or Deno installed, format extraction drops formats or fails.

## Proven Remediation & Best Practices

### 1. JS Runtime & EJS Components (Mandatory)
Ensure `deno` (recommended) or `node` is available on the system:
```bash
# In shell
yt-dlp --js-runtimes deno --remote-components ejs:github ...

# In Python yt-dlp options
ydl_opts = {
    "js_runtimes": {"node": {"path": "/usr/bin/node"}},
    "remote_components": ["ejs:github"],
}
```

### 2. Format Selection Fallbacks
Some video formats (like pure `ba[ext=m4a]`) are restricted or require PO tokens on certain web clients. Use resilient format expressions:
```text
format: "18/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
```
Format `18` (360p muxed MP4/AAC) has the lowest friction and highest availability across downgraded, embedded, and legacy player clients.

### 3. Converting JSON Cookie Dumps to Netscape Format
When users export cookies from browser extensions in JSON format (array of objects), convert them to Netscape format required by `yt-dlp`:
```python
# Convert JSON cookies to Netscape format
with open("cookies.txt", "w") as f:
    f.write("# Netscape HTTP Cookie File\n")
    for c in cookies_json:
        domain = c.get("domain", ".youtube.com")
        flag = "TRUE" if domain.startswith(".") else "FALSE"
        path = c.get("path", "/")
        secure = "TRUE" if c.get("secure", False) else "FALSE"
        exp = int(c.get("expirationDate", 0))
        name = c.get("name")
        val = c.get("value")
        f.write(f"{domain}\t{flag}\t{path}\t{secure}\t{exp}\t{name}\t{val}\n")
```
Key cookies for YouTube authentication: `LOGIN_INFO`, `__Secure-1PSIDTS`, `__Secure-3PSIDTS`, `SID`, `HSID`, `SSID`, `SAPISID`.

### 3.1 Pre-download Slicing Strategy
Never download or transcribe full 1-2 hour raw videos upfront on resource-constrained servers:
- Limit initial audio download/transcription to the first 10-15 minutes (`--download-sections "*00:00:00-00:15:00"` or slice with ffmpeg).
- Podcasts and talkshows universally establish strong hooks in the first 5-10 minutes. Slicing reduces Whisper inference from 30+ minutes down to 1-2 minutes on CPU.

### 4. Player Client Fallback Cascade
When datacenter IP bot checks hit the default web/android client, leverage the `web_embedded` and `tv_downgraded` extractor arguments:
```bash
yt-dlp --extractor-args "youtube:player_client=web_embedded,tv_downgraded" ...
```

### 5. Proxy Isolation
To prevent Google from invalidating user cookies, route download traffic through residential or ISP proxies rather than directly from cloud datacenter IPs:
- `yt-dlp --proxy "http://user:pass@residential-proxy:port" ...`
- Local proxy daemons (e.g. Surfshark / rotating residential nodes).

### 6. Headless Sign-In Boundaries
Do not attempt direct headless browser login via automation tools (Playwright/Puppeteer/CDP) on `accounts.google.com`. Google flags headless automation (`"This browser or app may not be secure"`) and blocks the sign-in form immediately. Always inject user-exported cookies.
