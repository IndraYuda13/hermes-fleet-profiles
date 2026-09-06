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

## 4. Module View & Completion Trigger

For resources (`/mod/resource/view.php?id=...`) and video URLs (`/mod/url/view.php?id=...`):
- Moodle marks them "Done" via the `course_module_viewed` event.
- You do NOT need to stream the video or download the full document.
- Simply navigating to the URL via `goto_url(url)` followed by `wait_for_load()` immediately satisfies the completion condition in the backend.

## 5. Course Enrolments & AJAX Service API

To inspect courses and deadlines without parsing the full HTML dashboard:
- Endpoint: `POST /lib/ajax/service.php?sesskey=<SESSKEY>&info=<METHOD>`
- Methods:
  - `core_calendar_get_action_events_by_timesort`: Actionable calendar events.
  - `core_course_get_enrolled_courses_by_timeline_classification`: Filter by `'all'`, `'inprogress'`, `'future'`, `'past'`.
  - `core_enrol_get_users_courses`: User course registrations.
