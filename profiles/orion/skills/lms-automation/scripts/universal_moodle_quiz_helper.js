// Universal LMS Moodle Quiz Runner for Hermes browser_exec
// Evaluated inside browser tab via js('''...''')

(() => {
    // 1. Check if we are on quiz attempt page
    const qBox = document.querySelector('.que');
    if (qBox) {
        const qno = qBox.querySelector('.qno')?.innerText.trim() || '';
        const qtext = qBox.querySelector('.qtext')?.innerText.trim() || '';
        const options = Array.from(qBox.querySelectorAll('.answer > div, .answer li, .answer label, .answer .r0, .answer .r1')).map((el, i) => {
            const input = el.querySelector('input[type="radio"], input[type="checkbox"]');
            return {
                index: i,
                id: input?.id,
                value: input?.value,
                text: el.innerText.trim()
            };
        }).filter(o => o.text.length > 0);

        return {
            pageType: 'question',
            qno,
            qtext,
            options,
            hasNext: Boolean(document.querySelector('#mod_quiz-next-nav, input[name="next"]'))
        };
    }

    // 2. Check if we are on summary page
    const summaryTable = document.querySelector('.summary-table, #region-main');
    const processForm = document.querySelector('form[action*="processattempt.php"]');
    if (window.location.href.includes('summary.php') || (summaryTable && summaryTable.innerText.includes('Summary of attempt'))) {
        return {
            pageType: 'summary',
            canSubmitDirect: Boolean(processForm),
            summaryText: summaryTable ? summaryTable.innerText.slice(0, 500) : ''
        };
    }

    // 3. Check if we are on review page
    if (window.location.href.includes('review.php')) {
        const gradeTable = document.querySelector('.quizreviewsummary, .generaltable');
        return {
            pageType: 'review',
            summary: gradeTable ? gradeTable.innerText : ''
        };
    }

    return {
        pageType: 'unknown',
        url: window.location.href,
        title: document.title
    };
})()
