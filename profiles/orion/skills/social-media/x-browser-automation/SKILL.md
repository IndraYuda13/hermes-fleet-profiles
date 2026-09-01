---
name: x-browser-automation
description: "Use when automating X (Twitter) login and session cookies."
---

# X (Twitter) & Web Auth Automation

Workflows and anti-bot bypass patterns for automating X (Twitter) and authenticated web sessions via Hermes `browser_exec` and CDP.

## Anti-Bot & Auth Guardrails

### 1. Google OAuth Block on Automated Browsers
- **Symptom:** Google rejects direct login on automated browser sessions with *"Couldn't sign you in - This browser or app may not be secure"*.
- **Root Cause:** Automated CDP/Puppeteer/Playwright signatures trigger Google's bot detection heuristics on unauthenticated profiles.
- **Handling:**
  - Avoid performing fresh Google interactive logins in headless/automation instances.
  - Rely on direct service credentials (username/password) or session cookie transfer.

### 2. X (Twitter) Login Rate-Limiting on Cloud Datacenter IPs
- **Symptom:** X returns *"We’ve temporarily limited your login. Please try again later."* immediately upon entering username.
- **Root Cause:** X actively flags and blocks interactive login flows originating from cloud hosting IP ranges (Azure, AWS, GCP, Hetzner, etc.).
- **Solutions & Workarounds:**
  1. **Direct Cookie Injection (`auth_token` & `ct0`):**
     Extract `auth_token` and `ct0` cookies from an authenticated desktop browser session and inject directly via CDP:
     ```python
     cdp("Network.setCookie", name="auth_token", value=auth_token, domain=".x.com", path="/", secure=True, httpOnly=True)
     cdp("Network.setCookie", name="ct0", value=ct0, domain=".x.com", path="/", secure=True, httpOnly=False)
     cdp("Network.setCookie", name="twid", value=twid, domain=".x.com", path="/", secure=True, httpOnly=False)
     # Also set on .twitter.com for redundancy
     cdp("Network.setCookie", name="auth_token", value=auth_token, domain=".twitter.com", path="/", secure=True, httpOnly=True)
     goto_url("https://x.com/home")
     wait_for_load()
     ```

### 3. Multi-Profile Fleet Synchronization Pitfall
- **Symptom:** X is authenticated on one agent profile (e.g. `orion`), but peer subagents (e.g. `radar`, `lens`) see a guest landing page (`https://x.com/`).
- **Root Cause:** Hermes isolates browser state per-profile under `/root/.hermes/profiles/<name>/browser-profile/chrome/Default/Cookies`. Injecting cookies in one profile does not automatically update sibling agent SQLite stores.
- **Handling:** Synchronize the `browser-profile/chrome` directory across all agent profiles, making sure to exclude active lock/socket files (`Singleton*`, `*.lock`):
  ```python
  import glob, shutil, os
  def ignore_sockets(dir, files):
      return [f for f in files if "Singleton" in f or "Socket" in f or "lock" in f.lower()]
  src = "/root/.hermes/profiles/orion/browser-profile/chrome"
  for p in glob.glob("/root/.hermes/profiles/*"):
      if os.path.basename(p) == "orion": continue
      dst = os.path.join(p, "browser-profile/chrome")
      if os.path.exists(dst): shutil.rmtree(dst)
      shutil.copytree(src, dst, ignore=ignore_sockets)
  ```
  2. **Residential / VPN Proxy Node Routing (e.g. Surfshark Nodes):**
     Route the browser traffic through residential proxies, managed cloud browser services (Browserbase / Browser Use Cloud), or local OpenVPN/Tinyproxy containers (e.g. `surfshark-proxy-studio` nodes on ports `31001-31017`).
     *Note:* Verify VPN service credentials (`secrets/surfshark.auth`) are active before starting nodes to avoid `AUTH_FAILED` loops.
     *Chrome Flag:* Launch Chrome with `--proxy-server="http://host:port"` or configure via `browser.cdp_url` attachment. Note that in headless Linux mode, extension-based VPNs requiring manual GUI interaction (like Urban VPN popup) cannot establish background proxy tunnels without a visible display or direct CLI/protocol configuration.
     *Account-Level Cooldown Pitfall:* Multiple rapid failed login attempts from cloud IPs cause X to rate-limit the *username/account identifier* itself across all IPs ("We've temporarily limited your login"). When switching to a residential/VPN proxy after recent failures, enforce a 15–30 minute account-level cooldown before retrying.
     *Mobile-User Trap:* When the user is on mobile (no DevTools/F12 to grab `auth_token`), guide them to fetch their manual OpenVPN credentials from their VPN provider dashboard (e.g. `my.surfshark.com` -> VPN -> Manual setup -> OpenVPN / Credentials) rather than attempting unsupported mobile cookie inspection.
     *Profile Session Warmth Pitfall:* Avoid killing or restarting the Chrome daemon process indiscriminately while experimenting with proxies or other sites, because restarting Chrome drops active/cached SSO session tokens (such as Microsoft Office365 OIDC for university LMS portals) and forces re-authentication.
     *Profile Session Warmth Pitfall:* Avoid killing or restarting the Chrome daemon process indiscriminately while experimenting with proxies or other sites, because restarting Chrome drops active/cached SSO session tokens (such as Microsoft Office365 OIDC for university LMS portals) and forces re-authentication.
  3. **Official API CLI (`xurl`):**
     For non-interactive operations (posting, timeline monitoring, searching), use the `xurl` skill with official Developer OAuth 2.0 keys.

## Live Timeline & Tweet Scraping via CDP / DOM

When extracting timeline tweets or trending topics from an authenticated X session:

### 1. Extracting "Untuk Anda" / "For You" Algorithmic Feed
The user's customized feed (e.g. AI news, tailored interests) lives under the "Untuk Anda" / "For you" tab. Always ensure the tab is clicked, and use progressive scrolling with deduplication because X dynamically unmounts/recycles off-screen DOM nodes:

```python
# Direct extraction of "Untuk Anda" / "For You" timeline with deduplication
import time, json

goto_url("https://x.com/home")
time.sleep(3)
wait_for_load()

# Ensure "Untuk Anda" / "For you" tab is active
js('''(() => {
    const tabs = Array.from(document.querySelectorAll('[role="tab"]'));
    for (const t of tabs) {
        if (t.innerText.includes("Untuk Anda") || t.innerText.includes("For you") || t.innerText.includes("Untuk anda")) {
            t.click();
            break;
        }
    }
})()''')
time.sleep(2)

collected = []
seen = set()

# Progressive scroll loop (e.g. 10-15 steps)
for step in range(12):
    items = js('''(() => {
        const tweets = [];
        const articles = document.querySelectorAll('article[data-testid="tweet"]');
        for (const a of articles) {
            const user = a.querySelector('[data-testid="User-Name"]')?.innerText?.replace(/\\n/g, ' ') || '';
            const text = a.querySelector('[data-testid="tweetText"]')?.innerText || '';
            const time = a.querySelector('time')?.getAttribute('datetime') || '';
            if (text) {
                tweets.push({ user, text, time });
            }
        }
        return tweets;
    })()''')

    for item in items:
        key = item["text"][:60]
        if key not in seen:
            seen.add(key)
            collected.append(item)

    js("window.scrollBy(0, 1500)")
    time.sleep(2)
```

## CDP Network Traffic Capture & Extension Workflows

### 1. Network Traffic Inspection & API Interception
Hermes `browser_exec` provides direct access to Chrome DevTools Protocol (`cdp(...)`):
```python
# Enable network traffic monitoring
cdp("Network.enable")

# Inspect recent resources and timing
resources = js('''(() => {
    return performance.getEntriesByType("resource").slice(-10).map(r => ({
        name: r.name,
        duration: Math.round(r.duration),
        initiatorType: r.initiatorType,
        transferSize: r.transferSize
    }));
})()''')

# Modify or block requests on-the-fly
cdp("Fetch.enable", patterns=[{"urlPattern": "*api.x.com*", "requestStage": "Request"}])
```

### 2. Chrome Extension & Userscript Injection
- **Chrome Extension Loading:** In Hermes configuration (`config.yaml`), extension control is enabled via `browser.extension_control.enabled: true`. Custom extensions can be unpacked and loaded into the Chrome daemon profile.
- **Pre-Navigation Script Injection via CDP:**
  ```python
  cdp("Page.addScriptToEvaluateOnNewDocument", source="""
      // Injected script runs before page scripts
      console.log('Pre-load script active');
  """)
  ```
