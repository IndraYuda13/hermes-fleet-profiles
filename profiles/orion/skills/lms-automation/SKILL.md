---
name: lms-automation
description: Automates Telkom University LMS workflows via Hermes browser tool.
version: 0.1.0
author: Hermes
platforms: [linux]
metadata:
  hermes:
    tags: [Lms, Moodle, Telkom-University, Automation, Browser-Exec]
---

# LMS Automation

Automates CeLOE Moodle LMS workflows (lms.telkomuniversity.ac.id) using Hermes native browser engine (`browser_exec`). Covers Cloudflare clearance injection, Microsoft OIDC SSO, calendar event scraping, module auto-completion, and automated quiz solving.

## When to Use
- Checking active tasks, assignments, and calendar deadlines on CeLOE LMS.
- Inspecting enrolled courses and progress in Telkom University LMS.
- Auto-completing learning modules (resources, video URLs) via view events.
- Answering and submitting Moodle quizzes directly via native browser execution.

## Prerequisites
- Dedicated Chrome automation server running CDP on `127.0.0.1:9222` (`hermes-chrome-cdp.service`).
- Local FlareSolverr service running on `http://127.0.0.1:8191/v1`.
- Active session cookies stored in `/root/.openclaw/workspace/state/lms_browser_state.json`.
- Strictly native `browser_exec` execution (do not use Playwright or Node scripts).

## How to Run
Invoke all workflows directly through the `browser_exec` tool in Hermes:
```python
# Launch or verify CDP tab
info = page_info()
goto_url("https://lms.telkomuniversity.ac.id/my/")
wait_for_load()
```

## Quick Reference
- **Dashboard:** `https://lms.telkomuniversity.ac.id/my/`
- **Course View:** `https://lms.telkomuniversity.ac.id/course/view.php?id=<COURSE_ID>`
- **Quiz Attempt:** `https://lms.telkomuniversity.ac.id/mod/quiz/view.php?id=<CMID>`
- **Next Question Button:** `#mod_quiz-next-nav` (never click generic submit)
- **Direct Quiz Finish:** `document.querySelector('form[action*="processattempt.php"]').submit();`
- **Half-solve handoff mode:** answer every page, stop ON `summary.php`, never submit (leave attempt "In progress" for the user).

## Procedure

### 0. Expired LMS session: retry Microsoft SSO before treating it as a login blocker
When CeLOE shows **“Your session has timed out. Please log in again.”**, click **“Connect with Office365” once** and wait for navigation. The browser may retain a valid Microsoft SSO session, in which case Moodle returns directly to `https://lms.telkomuniversity.ac.id/my/` without asking for credentials. Verify the resulting dashboard and only use vault/login escalation if the Microsoft identity page actually asks for credentials.

```python
# On LMS timed-out login page: start the retained Office365 SSO flow once
js("""(() => {
  const el = [...document.querySelectorAll('a, button')]
    .find(x => /Connect with Office365/i.test(x.innerText || ''));
  if (!el) throw new Error('Office365 connect control not found');
  el.click();
})()""")
wait_for_load()
print(js("(() => ({url: location.href, title: document.title}))()"))
# Success is the LMS dashboard (/my/), not a credential form.
```

### 1. Cloudflare Clearance & Session Injection
Before accessing CeLOE, obtain cookies from FlareSolverr and inject stored session cookies:
```python
import json, time

# Inject session cookies
with open('/root/.openclaw/workspace/state/lms_browser_state.json') as f:
    state = json.load(f)

for c in state.get('cookies', []):
    domain = c['domain'].lstrip('.')
    cdp("Network.setCookie",
        name=c["name"], value=c["value"], domain=domain,
        path=c.get("path", "/"), secure=c.get("secure", False),
        httpOnly=c.get("httpOnly", False)
    )

goto_url("https://lms.telkomuniversity.ac.id/my/")
wait_for_load()
```

### 2. Auto-Complete Resource and Video Modules
Moodle CeLOE records completion on the `course_module_viewed` event:
```python
# Navigate to module URL to trigger completion
goto_url("https://lms.telkomuniversity.ac.id/mod/resource/view.php?id=173")
wait_for_load()
# State immediately updates to "Done" in course tracking
```

### 3. Answering Quiz Questions Sequentially
Loop through attempt pages in `browser_exec`:
```python
# 1. Read question text and options
q = js('''(() => {
    const qBox = document.querySelector('.que');
    return {
        text: qBox.querySelector('.qtext')?.innerText.trim(),
        options: Array.from(qBox.querySelectorAll('.answer input[type="radio"]')).map((el, i) => ({
            id: el.id, index: i, text: el.closest('div, label, li').innerText.trim()
        }))
    };
})()''')

# 2. Select the correct option with full event dispatch
target_id = q['options'][chosen_index]['id']
js(f'''(() => {{
    const r = document.getElementById("{target_id}");
    if (r) {{
        r.click();
        r.checked = true;
        r.dispatchEvent(new Event('change', {{ bubbles: true }}));
    }}
}})()''')

# 3. Advance to next question
js('document.querySelector("#mod_quiz-next-nav")?.click()')
wait_for_load()
```

### 4. Bypassing Modal and Submitting Quiz
On `summary.php`, bypass the confirmation popup modal by submitting the underlying form directly:
```python
js('document.querySelector(\\'form[action*="processattempt.php"]\\')?.submit()')
wait_for_load()
```

### 5. Partial Solve & Handoff (answer all, DO NOT submit)
When the user must do the final submission themselves (in-class password quiz, personal review, exam integrity):
1. Enter with the provided quiz password, solve page by page, clicking `#mod_quiz-next-nav` after each page. The navigation POST is what persists that page's responses server-side.
2. On the LAST page click the "Finish attempt..." control to reach `summary.php`. Despite the label, this only opens the review-before-submit page; Moodle does NOT auto-submit.
3. STOP at summary. Never click "Submit all and finish"; never call the `processattempt.php` form. The attempt stays "In progress" for the user.
4. Dump a question/answer digest to the workspace, navigate the automation tab back to the dashboard (do not leave it parked on the attempt), then hand off: the user resumes on their own device (Continue attempt), reviews, and submits.
- **Trap:** stopping at the last question page WITHOUT the Next/Finish click leaves that page's answers unsaved server-side. Only page navigation persists responses (site autosave may be disabled).
- **Trap:** after handoff keep the automation session idle on that attempt; two sessions posting to the same attempt can trip Moodle's `sequencecheck` validation.

## Pitfalls
- **Modal Hangs:** Clicking the modal button "Submit all and finish" on `summary.php` often stalls due to Bootstrap transition lags. Always call `form.submit()` directly.
- **Previous Button Collision:** Moodle renders both "Previous page" and "Next page" inputs inside `#responseform`. Always target `#mod_quiz-next-nav`.
- **Radio State Loss:** Setting `radio.checked = true` without `.click()` or dispatching `'change'` may fail to update Moodle's `sequencecheck`.
- **CDP Daemon Inactive:** If `browser_exec` fails with Errno 111, ensure `hermes-chrome-cdp.service` is active (`systemctl status hermes-chrome-cdp.service`).

## Verification
Confirm login and session validity in CeLOE:
```python
user = js("document.querySelector('.usertext, .user-name, .logininfo')?.innerText || ''")
assert "INDRA YUDA" in user
print("CeLOE Session Verified:", user.strip())
```
