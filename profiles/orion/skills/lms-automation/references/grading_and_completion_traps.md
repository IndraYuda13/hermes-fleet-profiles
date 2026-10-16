# CeLOE grading & activity traps (deep-audit depth)

Loaded when a quiz/assignment status or a completion percentage looks wrong, or when reading completion details fails.

## Gradebook screen traps
- **Recalculation screen:** navigating to `grade/report/user/index.php?id=<ID>` often shows an intermediate "Recalculating grades 100% Continue" page. Reading the DOM immediately yields zero grade rows; reload the URL or wait before scraping.
- **Unconfigured gradebook:** many CeLOE courses never configure aggregation, so the user report shows only header rows with `-` and zero graded items even when attempts exist. Never treat an empty gradebook as "quiz unattempted" - visit `mod/quiz/view.php?id=<CMID>` directly and look for `Attempt 1 summary` with `Status: Finished`, or `Review not permitted / No more attempts are allowed`.

## Completion percentage lies
- Progress bars may cap below 100% (e.g. 85%) even when every student-accessible module shows Done: hidden sections, instructor manual sign-offs, and disabled completion rules count into the aggregate. `course/completion.php?id=X` returns "you do not currently have permissions" for students. Never infer missing work from the percentage alone; enumerate activities and their states instead.
- **Multi-track elective deflation:** in courses with `mod/groupselect` tracks (e.g. Career Coach STAR: Entrepreneurship / Intrapreneurship / Studi Lanjut), the bar aggregates ALL tracks, so finishing 100% of the chosen track still displays 20-30%. Always open `groupselect/view.php?id=<CMID>` to learn the student's active track before calling other tracks' modules "pending".

## Reading completion & announcements
- Completion requirement text on activity pages lives in Bootstrap popovers: read `data-content` / `data-bs-content`, `innerText` is empty.
- Internship / project / competition courses often have no `mod/assign`; the rubric and Google Drive/Forms submission links sit in the Announcements forum (`mod/forum/view.php?id=X`). Check the forum before declaring the course inactive.
- **HVP auto-completion:** opening `mod/hvp/view.php?id=X` once marks it Done (View completion). Visit each pending video, then reload the course page. Manual "Mark as done" buttons on quiz rows persist after attempts and can be clicked safely.

## AJAX service limits
- `core_calendar_get_action_events_by_timesort` throws an opaque exception (`[object Object]`) when `limitnum > 50`. Use `limitnum: 50` and widen with `timesortfrom`/`timesortto`.
- `core_calendar_get_calendar_monthly_view` takes `month` with a +1 offset (`month: 11` = October). Verify `d[0].data.date.month/.year` or sweep a 3-month window.
- `core_message_get_conversations` is disabled site-wide; use `message_popup_get_popup_notifications` for broadcasts.

## Quiz mechanics
- Only page navigation (`#mod_quiz-next-nav` POST) persists responses; stopping on the last question page without clicking Next/Finish leaves that page unsaved.
- Two sessions posting to the same attempt can trip `sequencecheck` validation - keep the automation tab idle on a handed-off attempt.
- Moodle renders both Previous and Next inputs inside `#responseform`; always target `#mod_quiz-next-nav`, never a generic submit.
- Setting `radio.checked = true` alone may not update `sequencecheck`; also `.click()` and dispatch `change`.
- On `summary.php` the Bootstrap modal often hangs; submit `form[action*="processattempt.php"]` directly.
