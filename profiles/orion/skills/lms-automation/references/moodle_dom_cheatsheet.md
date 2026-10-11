# Moodle DOM & Technical Cheatsheet for CeLOE (Telkom University)

This reference documents the exact DOM elements, form targets, and browser behavior discovered during live quiz and module automation on Telkom University CeLOE Moodle.

## 1. Quiz Navigation & Form Elements

- **Question Wrapper:** `.que`
- **Question Number:** `.qno`
- **Question Body:** `.qtext`
- **Options List:** `.answer > div, .answer li, .answer label, .answer .r0, .answer .r1`
- **Radio Inputs:** `.answer input[type="radio"]`
- **Next Page Button:** `#mod_quiz-next-nav` (or `input[name="next"]`)
- **Previous Page Button:** `#mod_quiz-prev-nav` (Avoid clicking generic submit buttons)
- **Sequence Check Token:** `input[name*=":sequencecheck"]` (Maintains Moodle attempt integrity)

## 2. Radio Selection & Event Dispatching

Setting `radio.checked = true` alone is often ignored by Moodle's YUI/jQuery listeners. Always execute the 3-step trigger:
```javascript
const radio = document.querySelector(selector);
radio.click();
radio.checked = true;
radio.dispatchEvent(new Event('change', { bubbles: true }));
```

## 3. The "Submit All and Finish" Modal Trap & Direct Form Bypass

On `mod/quiz/summary.php`:
- Clicking the visual "Submit all and finish" button triggers a Bootstrap modal.
- Automated clicks on the modal confirmation button frequently fail or hang due to modal animation timing and backdrop overlays.
- **Direct Solution:** Moodle renders an inline hidden form pointing to `processattempt.php`. Submitting it directly bypasses the modal completely:
```javascript
const form = document.querySelector('form[action*="processattempt.php"]');
if (form) {
    form.submit();
}
```
This cleanly lands on `mod/quiz/review.php` with 100% reliability.

## 4. Module View, Video & Manual Completion Triggers

### A. Auto-Completion via View Event
For resources (`/mod/resource/view.php?id=...`), interactive videos (`/mod/hvp/view.php?id=...`), and video URLs (`/mod/url/view.php?id=...`):
- Moodle marks them "Done" via the `course_module_viewed` event.
- You do NOT need to stream the video or download the full document.
- Simply navigating to the URL via `goto_url(url)` followed by `wait_for_load()` immediately satisfies the completion condition in the backend.

### B. Manual Completion Toggles
Some course modules require student manual confirmation even if quizzes or assignments are passed:
- **Button Selector:** `button[data-action="toggle-manual-completion"]`
- **State Check:** Check `button.innerText.includes('Mark as done')` vs `'Done'`.
- Clicking the button flips completion server-side and immediately updates the course progress bar upon page refresh.

## 5. Course Enrolments & AJAX Service API Matrix

CeLOE has selectively restricted several standard Moodle web-service endpoints. Use this compatibility matrix:

| AJAX Method (`POST /lib/ajax/service.php?sesskey=...`) | Status on CeLOE | Notes |
| :--- | :--- | :--- |
| `core_course_get_enrolled_courses_by_timeline_classification` | **Functional** | Essential for course discovery (`args: {classification: 'all'}`). Returns course ID, full name, progress %. |
| `core_calendar_get_calendar_monthly_view` | **Functional** | Returns calendar day events, quiz schedules, and assignment dates. |
| `core_calendar_get_action_events_by_timesort` | **Partial** | Functional but frequently returns 0 events; do not rely on it as sole truth. |
| `core_course_get_contents` | **Disabled** | Returns `servicenotavailable`. Must scrape `/course/view.php?id=X` DOM directly. |
| `core_enrol_get_users_courses` | **Broken** | Returns empty array `[]`. Use timeline classification instead. |
| `core_completion_get_activities_completion_status` | **Disabled** | Returns `servicenotavailable`. |
| `core_calendar_get_action_events_by_courses` | **Broken** | Returns empty event groupings. |

## 6. Gradebook & Course Completion Limits

- **Gradebook URL:** `https://lms.telkomuniversity.ac.id/grade/report/user/index.php?id=<COURSE_ID>`
  - Scrape table rows `tr` to extract quiz scores, submission status, and feedback.
  - Gradebook confirms whether a quiz or assignment is submitted, regardless of whether manual completion badges are checked.
- **Course Completion Ceiling:**
  - `course/completion.php?id=<COURSE_ID>` is restricted to instructors ("You do not currently have permissions").
  - An 85% or non-100% progress score on a course where all visible items are "Done" is normal: instructors frequently configure hidden items or manual completion criteria that students cannot trigger.

## 7. Modern Activity Detection & Class Mappings

In Moodle 4.x / CeLOE Boost theme, `.activity` elements use `modtype_<module>`:
- `modtype_quiz`: Quizzes and tests
- `modtype_assign`: Homework and assignments
- `modtype_forum`: Announcements and discussion boards
- `modtype_resource`: PDF/slides/files
- `modtype_url`: External URLs, meeting recordings
- `modtype_hvp`: Interactive H5P content
- `modtype_groupselect`: Track / group self-selection

Safe module extractor:
```javascript
const modType = ([...activityEl.classList].find(c => c.startsWith('modtype_')) || '').replace('modtype_', '')
  || (activityEl.querySelector('a')?.href.match(/\/mod\/([a-z0-9_-]+)\//)?.[1] || 'unknown');
```

## 8. Completion Requirements in Bootstrap Popovers

On modern CeLOE activity pages, descriptions under the "Completion requirements" header are embedded inside Bootstrap popovers rather than rendered inline text:
```javascript
const popover = document.querySelector('[data-toggle="popover"], [data-bs-toggle="popover"]');
const criteriaHtml = popover ? (popover.getAttribute('data-content') || popover.getAttribute('data-bs-content') || '') : '';
```
Querying `.innerText` directly on the header container yields empty strings.

## 9. Group Self-Selection (`mod/groupselect`) & Multi-Track Completion

- URL: `https://lms.telkomuniversity.ac.id/mod/groupselect/view.php?id=<CMID>`
- Identify active track: check which group `tr` row lists the student's name in the `Members` column.
- **Progress Deflation Quirk:** In elective track courses (e.g. Career Coach STAR with Entrepreneurship / Intrapreneurship / Studi Lanjut), Moodle aggregates all track modules into the course progress percentage. Completing 100% of an assigned track leaves the course progress bar around 20%-30%. Never report modules from unselected tracks as missing work.
