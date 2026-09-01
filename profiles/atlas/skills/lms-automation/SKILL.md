---
name: lms-automation
description: Automates Telkom University LMS workflows using Hermes browser tool.
---

# LMS Automation

Automates LMS workflows for Telkom University CeLOE (lms.telkomuniversity.ac.id) via Hermes native browser engine (`browser_exec`).

## Context & Environment
- **Target:** lms.telkomuniversity.ac.id
- **Browser Engine:** Hermes native `browser_exec` (`browser.use_real_profile: true`).
- **Cloudflare Bypass:** Local FlareSolverr (`http://127.0.0.1:8191/v1`) via CDP cookie injection.
- **SSO Authentication:** Microsoft Office 365 OIDC (`/auth/oidc/`) with persistent session in Chrome.
- **Student Email:** `indrayuda@student.telkomuniversity.ac.id`

## Primary Workflow — Check Tasks & Deadlines (100% Native Hermes Browser)

Execute directly inside Hermes `browser_exec` tool without writing or running external node/playwright scripts:

```python
# 1. Fetch Cloudflare clearance & User-Agent from FlareSolverr
import urllib.request, json, time

post_data = json.dumps({
    "cmd": "request.get",
    "url": "https://lms.telkomuniversity.ac.id/login/index.php",
    "maxTimeout": 60000
}).encode("utf-8")

req = urllib.request.Request("http://127.0.0.1:8191/v1", data=post_data, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req) as resp:
    sol = json.loads(resp.read().decode("utf-8"))["solution"]

ua = sol["userAgent"]
cookies = sol["cookies"]

# 2. Configure CDP emulation and strip webdriver flag
cdp("Emulation.setUserAgentOverride", userAgent=ua)
cdp("Page.addScriptToEvaluateOnNewDocument", source="Object.defineProperty(navigator, 'webdriver', { get: () => undefined });")

# 3. Inject clearance & session cookies
for c in cookies:
    cdp("Network.setCookie",
        name=c["name"],
        value=c["value"],
        domain=c["domain"],
        path=c.get("path", "/"),
        secure=c.get("secure", False),
        httpOnly=c.get("httpOnly", False)
    )

# 4. Open LMS Login Index
goto_url("https://lms.telkomuniversity.ac.id/login/index.php")
wait_for_load()
time.sleep(2)

# 5. Click Connect with Office365 to trigger silent Microsoft SSO
js("document.querySelector('a[href*=\"/auth/oidc/\"]')?.click()")
time.sleep(6)
wait_for_load()
time.sleep(3)

# 6. Verify Dashboard and Extract Calendar / Tasks via Moodle AJAX API
sesskey = js("window.M?.cfg?.sesskey || document.querySelector('input[name=\"sesskey\"]')?.value || ''")
events_data = js('''(() => {
    const now = Math.floor(Date.now() / 1000);
    return fetch('/lib/ajax/service.php?sesskey=' + encodeURIComponent(window.M?.cfg?.sesskey || '') + '&info=core_calendar_get_action_events_by_timesort', {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify([{
            index: 0,
            methodname: "core_calendar_get_action_events_by_timesort",
            args: {
                timesortfrom: now - (60 * 86400),
                timesortto: now + (60 * 86400),
                limitnum: 50
            }
        }])
    }).then(r => r.json());
})()''')

print("EVENTS_RESULT:", events_data)
```

## Output Formatting
When presenting LMS tasks/deadlines to the user (Boskuu), use this exact format:
"Berikut daftar tugas dan kuis aktif Boskuu di LMS (CeLOE):
[Hari, Tanggal]
• Nama Tugas (Mata Kuliah) • Deadline: HH:MM WIB"

If no active tasks:
State current date/time, confirmation of 60-day window checked, and course status.
