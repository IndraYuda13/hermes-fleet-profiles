---
name: lms-automation
description: Use for Telkom University CeLOE LMS browser automation.
version: 0.1.2
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
# ALWAYS navigate to LMS first before checking title, user, or session (prevents checking stale background tabs)
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
When CeLOE shows **“Your session has timed out. Please log in again.”** or redirects to `https://lms.telkomuniversity.ac.id/login/index.php?loginredirect=1`, click **“Connect with Office365” once** and wait for navigation. The browser profile / persistent session retains a valid Microsoft OIDC SSO state, returning directly to `https://lms.telkomuniversity.ac.id/my/` without asking for credentials. Verify the resulting dashboard and only use vault/login escalation if the Microsoft identity page actually asks for credentials.

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

### 2. Dashboard-Only Quick Audit (`di dashboardnya saja`)
When the user requests checking tasks strictly on the dashboard without full course-by-course crawling:
1. **Verify Session Identity:** Confirm logged in via `.usertext` or `.user-name`.
2. **Inspect Timeline Block:**
   - Wait `time.sleep(2)` after navigation for client-side rendering.
   - Read `[data-region="timeline-view"]` text.
   - Cross-check with AJAX `core_calendar_get_action_events_by_timesort`. If empty ("No upcoming activities due"), do NOT stop there.
3. **Inspect Calendar Month Block (`.block_calendar_month`):**
   - The sidebar calendar block highlights active event dates (e.g. `2 events, Tuesday, 6 October`).
   - If event dates exist, click the day link or navigate to `https://lms.telkomuniversity.ac.id/calendar/view.php?view=day&time=<TIMESTAMP>&course=1` to read the exact activity names, courses, and open/close times.
4. **Sweep Calendar AJAX (Current & Adjacent Months):**
   - Execute `core_calendar_get_calendar_monthly_view` for current month, +1 month, and +2 months (accounting for Moodle's +1 month index quirk).
   - This captures scheduled exams, quizzes, and assignment cutoffs visible on the dashboard calendar that the Timeline block filter omitted.

### 3. Comprehensive Multi-Layer Task & Deadline Audit (Deep Audit)
When auditing student tasks, assignments, and quizzes, do NOT rely solely on calendar action APIs. CeLOE frequently omits courses from calendar action events. Follow this 5-layer audit:

1. **Dashboard Timeline Verification with Controlled Wait:**
   Navigate to `https://lms.telkomuniversity.ac.id/my/` and wait for `[data-region="timeline-view"]` to populate. CeLOE loads timeline cards asynchronously via AJAX. Use `time.sleep(2)` after `wait_for_load()` before reading `.innerText`. Avoid unbounded JS promises inside `js(...)` that risk hitting the 5s daemon IPC timeout.
2. **Enrolled Course Discovery via AJAX:**
   Extract all enrolled courses and current progress using `core_course_get_enrolled_courses_by_timeline_classification`:
   ```python
   courses = js("""(() => {
     return fetch(`https://lms.telkomuniversity.ac.id/lib/ajax/service.php?sesskey=${M.cfg.sesskey}&info=core_course_get_enrolled_courses_by_timeline_classification`, {
       method: 'POST', headers: {'Content-Type': 'application/json'},
       body: JSON.stringify([{index: 0, methodname: 'core_course_get_enrolled_courses_by_timeline_classification', args: {classification: 'all'}}])
     }).then(r => r.json()).then(d => d[0].data.courses);
   })()""")
   ```
3. **Calendar Monthly Cross-Check with Month Index Quirk Handling:**
   Query `core_calendar_get_calendar_monthly_view` to catch scheduled quizzes and assignment due dates that timeline views miss.
   **Crucial Quirk:** CeLOE Moodle expects the `month` argument with a +1 offset (e.g. `month: 11` corresponds to October; `month: 10` corresponds to September). Always verify `d[0].data.date.month` and `d[0].data.date.year` from the response, or sweep `[current_month, current_month+1, current_month+2]` to ensure the real target month is covered.
4. **Per-Course DOM Inspection:**
   Visit each course `https://lms.telkomuniversity.ac.id/course/view.php?id=<ID>`:
   - Enumerate all `.activity` nodes.
   - Extract module type using `modtype_<type>` from classList or URL path `/mod/([a-z0-9_-]+)/` (do NOT test for `_module` suffix, which produces `unknown` in modern CeLOE theme).
   - Inspect completion toggle buttons: `button[data-action="toggle-manual-completion"]`.
     - `data-toggletype="manual:mark-done"`: Pending / not yet marked done (button text `"Mark as done"`, outline border).
     - `data-toggletype="manual:undo"`: Already completed (button text `"Done"`, green styling).
     - Do NOT check `aria-pressed` (it is `null`).
   - Identify module types: `mod/assign` (homework), `mod/quiz` (exams/tests), `mod/hvp` (interactive videos), `mod/forum` (discussions), `mod/groupselect` (track/group choice).
   - For `mod/groupselect`, inspect `groupselect/view.php?id=<CMID>` to determine which elective or career track the student selected before evaluating track-specific activities.
5. **Gradebook Status & Direct Activity Verification:**
   For any quiz or assignment showing `"To do"` or un-ticked status, navigate to `https://lms.telkomuniversity.ac.id/grade/report/user/index.php?id=<ID>`:
   - Check if an attempt was already submitted and graded.
   - **Unconfigured Gradebook Trap:** CeLOE courses often do not configure gradebook item aggregation, displaying only table headers with `-` and zero graded items even when attempts exist.
   - If gradebook is unconfigured, visit the activity page directly (`https://lms.telkomuniversity.ac.id/mod/quiz/view.php?id=<CMID>`): look for `Attempt 1 summary` with `Status: Finished` or `Review not permitted / No more attempts are allowed`.
6. **Forum & Announcements Fallback:**
   For courses without assignments (e.g. Kerja Praktik, Proyek/Kompetisi), open the announcements forum (`mod/forum/view.php?id=...`) to check whether deadlines or external submissions (e.g. Google Drive/Forms) were announced.
7. **Activity Completion Requirements in Popovers:**
   On activity pages (e.g. `mod/forum/view.php?id=...`), completion requirement descriptions under "Completion requirements" are embedded in Bootstrap popovers (`[data-toggle="popover"]` or `[data-bs-toggle="popover"]`). Read `.getAttribute('data-content')` or `.getAttribute('data-bs-content')`, as reading `.innerText` returns empty strings.

### 4. Auto-Complete Resource, Video Modules & Manual Toggles
Moodle CeLOE records completion on the `course_module_viewed` event:
- **HVP & Resource Modules:** Navigating to `mod/hvp/view.php?id=<ID>` or `mod/resource/view.php?id=<ID>` triggers backend completion automatically. No full video streaming is required.
- **Manual Completion Buttons:** For completed reading items with manual completion enabled, filter specifically for `data-toggletype="manual:mark-done"`:
  ```python
  js("""(() => {
    const btns = [...document.querySelectorAll('button[data-action="toggle-manual-completion"]')];
    return btns.filter(b => b.getAttribute('data-toggletype') === 'manual:mark-done').map(b => {
      b.click();
      return b.getAttribute('aria-label') || b.innerText.trim();
    });
  })()""")
  ```

### 5. Answering Quiz Questions Sequentially
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

### 6. Bypassing Modal and Submitting Quiz
On `summary.php`, bypass the confirmation popup modal by submitting the underlying form directly:
```python
js('document.querySelector(\\'form[action*="processattempt.php"]\\')?.submit()')
wait_for_load()
```

### 7. Partial Solve & Handoff (answer all, DO NOT submit)
When the user must do the final submission themselves (in-class password quiz, personal review, exam integrity):
1. Enter with the provided quiz password, solve page by page, clicking `#mod_quiz-next-nav` after each page. The navigation POST is what persists that page's responses server-side.
2. On the LAST page click the "Finish attempt..." control to reach `summary.php`. Despite the label, this only opens the review-before-submit page; Moodle does NOT auto-submit.
3. STOP at summary. Never click "Submit all and finish"; never call the `processattempt.php` form. The attempt stays "In progress" for the user.
4. Dump a question/answer digest to the workspace, navigate the automation tab back to the dashboard (do not leave it parked on the attempt), then hand off: the user resumes on their own device (Continue attempt), reviews, and submits.
- **Trap:** stopping at the last question page WITHOUT the Next/Finish click leaves that page's answers unsaved server-side. Only page navigation persists responses (site autosave may be disabled).
- **Trap:** after handoff keep the automation session idle on that attempt; two sessions posting to the same attempt can trip Moodle's `sequencecheck` validation.

### 8. Downloading Course Files (PDF/PPTX) Headlessly
Bulk-download course resource files without clicking each one:
1. In `browser_exec`, for every `.activity` of modtype `resource`, navigate to its link, then resolve the final file URL: `location.href` if it already contains `pluginfile.php`, else the first `a[href*="pluginfile.php"]`, else `object[data]` / `iframe[src]`.
2. Export cookies via `cdp('Network.getCookies', urls=['https://lms.telkomuniversity.ac.id/'])` and join as `name=value; ...`.
3. Download server-side with urllib + `Cookie` + browser UA header, then verify magic bytes (`%PDF-` etc). A body starting with `<!DOCTYPE` or `<html>` means the session cookie failed, not a valid file.
4. Trap: the Hermes scratch cache prunes idle entries (~24h). For multi-day tasks copy downloads to a durable directory outside the cache and reference it in your notes.
5. Some resources redirect to a short-lived presigned S3 URL (host `lmstest.telkomuniversity.ac.id`, ~1h expiry). When the landing page jumps to S3, that URL itself is the direct file link: fetch it immediately with a browser UA and no cookies.

Assignment reports built from LMS material are handled by the `academic-report-deliverables` skill.

## Pitfalls
- **Tab drift before navigation:** Running session checks or scraping `document.title` / `.usertext` before navigating via `goto_url("https://lms.telkomuniversity.ac.id/my/")` inspects whatever arbitrary tab CDP was left on from prior workflows (e.g. Instagram, foreign pages). Always execute `goto_url()` + `wait_for_load()` as the very first step before evaluating DOM state or user identity.
- **Dashboard Timeline block is not exhaustive:** The Moodle dashboard Timeline block (`[data-region="timeline-view"]`) frequently reports "No upcoming activities due" because it only filters active upcoming deadlines within narrow default timeframes. Quizzes or assignments scheduled on the calendar or closed earlier in the week are omitted from Timeline but are prominently visible in the dashboard Calendar block (`.block_calendar_month`) and via `core_calendar_get_calendar_monthly_view`. Always inspect both blocks during dashboard audits.
- **Timeline block async render race condition & IPC timeout:** `[data-region="timeline-view"]` on `lms.telkomuniversity.ac.id/my/` is rendered client-side via AJAX after DOM ready. Reading `element.innerText` immediately after `wait_for_load()` returns an empty string `""`. However, unbounded `new Promise(...)` inside `js(...)` can hit the 5s daemon IPC response timeout. Use `time.sleep(1.5-2)` in Python after `wait_for_load()` before reading the timeline element.
- **Modern Moodle module type extraction:** In modern CeLOE (Moodle 4.x / Boost theme), module classes use `modtype_<type>` (e.g. `modtype_quiz`, `modtype_assign`, `modtype_forum`, `modtype_resource`, `modtype_url`, `modtype_groupselect`), NOT `*_module`. Alternatively, extract the module name from the link URL (`/mod/([a-z0-9_-]+)/`). Matching `c.endsWith('_module')` causes all activities to report as `unknown`.
- **Multi-track elective course progress deflation (e.g. Career Coach STAR):** In multi-track courses where students select an elective track via `mod/groupselect` (e.g. Entrepreneurship vs. Intrapreneurship vs. Studi Lanjut), Moodle aggregates completion across ALL modules of ALL tracks into a single progress bar. A student who finishes 100% of their chosen track will still display a low overall course progress percentage (e.g. 20-30%). Always inspect `mod/groupselect/view.php?id=<CMID>` to determine the student's active track before assuming incomplete work from other tracks.
- **Activity completion requirement details hidden in Popover attributes:** The description text under the "Completion requirements" header on activity pages (e.g. `mod/forum/view.php?id=...`) is embedded within a Bootstrap popover trigger's `data-content` or `data-bs-content` attribute, not raw DOM text. Querying `element.innerText` returns empty text. Retrieve `el.getAttribute('data-content') || el.getAttribute('data-bs-content')`.
- **CeLOE disabled several web-service APIs:** `core_course_get_contents` returns `servicenotavailable`, `core_completion_get_activities_completion_status` returns `servicenotavailable`, `core_enrol_get_users_courses` returns `[]`, and `core_calendar_get_action_events_by_courses` returns empty event groups. Do NOT conclude "no tasks" from these APIs. Reliable sources only: (1) `core_calendar_get_action_events_by_timesort` + `core_calendar_get_calendar_monthly_view` (works), (2) `core_course_get_enrolled_courses_by_timeline_classification` (works, use for course discovery), (3) DOM scrape of each course page `course/view.php?id=X` (primary source for module/assignment/quiz lists), (4) activity attempt status on `mod/quiz/view.php?id=X` or gradebook.
- **Calendar monthly view month offset quirk:** In `core_calendar_get_calendar_monthly_view`, CeLOE Moodle uses a +1 offset for the `month` parameter (e.g. `month: 11` corresponds to October; `month: 10` corresponds to September). If querying calendar events, always inspect `d[0].data.date.month` and `d[0].data.date.year` to confirm the calendar month returned, or iterate a 3-month window.
- **Action-events limitnum cap:** `core_calendar_get_action_events_by_timesort` throws an opaque exception (serialises to `[object Object]`) when `limitnum` exceeds 50. Always pass `limitnum: 50` or lower; widen coverage with `timesortfrom`/`timesortto` instead of raising `limitnum`.
- **Manual completion button state detection:** Modern CeLOE uses `data-toggletype` on `button[data-action="toggle-manual-completion"]`. `manual:mark-done` indicates pending completion; `manual:undo` indicates already completed ("Done"). Do NOT rely on `aria-pressed`, which is `null` on these buttons.
- **Unconfigured course gradebooks:** Many CeLOE courses do not configure gradebook item aggregation; the user report shows only header rows with weights and grades as `-`. Never treat an empty gradebook as "quiz unattempted". Visit the quiz URL `mod/quiz/view.php?id=<CMID>` directly to check if an attempt has `Status: Finished`.
- **Course completion percentage ceiling:** Course completion progress bars (e.g. capped at 85%) may not reach 100% even if all student-accessible modules show "Done". CeLOE courses often include hidden sections, instructor manual sign-offs, or disabled completion rules. Students navigating to `course/completion.php?id=X` receive "you do not currently have permissions". Never assume missing student work based on completion percentage alone.
- **Announcement-only course deliverables:** Internship (`KERJA PRAKTIK`), project, or competition courses frequently do not instantiate Moodle `mod/assign` objects, posting task rubrics and submission links (Google Drive, external forms) inside the Announcements forum (`mod/forum/view.php?id=X`). Always inspect the forum thread before concluding a course is inactive.
- **HVP video completion:** opening `mod/hvp/view.php?id=X` once marks the activity Done automatically (View completion). Visit each pending video, then re-check the course page; progress updates after reload. Manual "Mark as done" buttons on quiz rows persist after quiz attempts and can be safely clicked to clear tracking.
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
