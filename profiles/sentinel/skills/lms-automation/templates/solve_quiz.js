const { chromium } = require('playwright');
const fs = require('fs');

const answersPath = '/tmp/quiz_answers.json';
const scrapedPath = '/tmp/scraped_quiz.json';

if (!fs.existsSync(answersPath) || !fs.existsSync(scrapedPath)) {
    console.error("Missing quiz answers or scraped data.");
    process.exit(1);
}

const answers = JSON.parse(fs.readFileSync(answersPath, 'utf8'));
const scraped = JSON.parse(fs.readFileSync(scrapedPath, 'utf8'));

const targetUrl = scraped.quizUrl;
const attemptId = scraped.attemptId;

(async () => {
    const userDataDir = '/root/.openclaw/workspace/state/lms_chrome_profile';
    const context = await chromium.launchPersistentContext(userDataDir, {
        headless: true,
        proxy: { server: 'http://20.192.4.173:33101', username: 'surfstudio-proxyId-node01', password: 'a89fba258b5953c10c091290cfd85240fdba6be655d411a3' },
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu']
    });
    
    try {
        const page = await context.newPage();
        
        console.log('Navigating directly to Moodle OIDC SSO URL...');
        await page.goto('https://lms.telkomuniversity.ac.id/auth/oidc/', { waitUntil: 'commit', timeout: 60000 });
        await page.waitForTimeout(6000);

        console.log('Navigating to attempt page to solve...');
        
        // Loop page by page
        for (let pageNum = 0; pageNum < answers.length; pageNum++) {
            console.log(`Processing page ${pageNum}...`);
            let loaded = false;
            for (let retry = 0; retry < 5; retry++) {
                try {
                    await page.goto(`https://lms.telkomuniversity.ac.id/mod/quiz/attempt.php?attempt=${attemptId}&page=${pageNum}`, { waitUntil: 'commit', timeout: 35000 });
                    await page.waitForTimeout(2000);
                    loaded = true;
                    break;
                } catch(e) {
                    console.log(`Error page ${pageNum} (retry ${retry+1}/5): ${e.message}`);
                    await page.waitForTimeout(4000);
                }
            }

            if (!loaded) continue;

            const qData = await page.evaluate(() => {
                const qNode = document.querySelector('.que');
                if (!qNode) return null;
                const qNum = qNode.querySelector('.no')?.innerText.trim().replace(/Question\s+/i, '') || '';
                const qText = qNode.querySelector('.qtext')?.innerText.trim() || '';
                const options = Array.from(qNode.querySelectorAll('.answer div[class^="r"]')).map(opt => {
                    const label = opt.querySelector('label, span.flex-fill') || opt;
                    const input = opt.querySelector('input');
                    let text = label.innerText.trim();
                    text = text.replace(/^[a-z]\.\s*/i, '').trim();
                    return { id: input?.id || '', text };
                });
                return { qNum, qText, options };
            });

            if (!qData) continue;

            const targetAnswer = answers.find(item => item.qNum === qData.qNum);
            if (targetAnswer) {
                const cleanTarget = targetAnswer.correctText.replace(/[^a-zA-Z0-9]/g, '').toLowerCase();
                const matchedOption = qData.options.find(opt => {
                    const cleanOpt = opt.text.replace(/[^a-zA-Z0-9]/g, '').toLowerCase();
                    return cleanOpt.includes(cleanTarget) || cleanTarget.includes(cleanOpt);
                });

                if (matchedOption) {
                    console.log(`Clicking answer option for Q${qData.qNum}: "${matchedOption.text}"`);
                    await page.evaluate((targetId) => {
                        const input = document.getElementById(targetId);
                        if (input) {
                            const label = document.querySelector(`label[for="${targetId}"]`);
                            if (label) label.click();
                            else input.click();
                        }
                    }, matchedOption.id);
                    await page.waitForTimeout(1500);
                } else {
                    console.log(`No matching option found for Q${qData.qNum}`);
                }
            }
        }

        console.log('\nNavigating to summary page for POST submit emulation...');
        
        let summaryLoaded = false;
        for (let retry = 0; retry < 5; retry++) {
            try {
                await page.goto(`https://lms.telkomuniversity.ac.id/mod/quiz/summary.php?attempt=${attemptId}`, { waitUntil: 'commit', timeout: 30000 });
                await page.waitForTimeout(4000);
                summaryLoaded = true;
                break;
            } catch(e) {
                await page.waitForTimeout(3000);
            }
        }

        if (summaryLoaded) {
            const sesskey = await page.evaluate(() => {
                const inputSess = document.querySelector('input[name="sesskey"]');
                if (inputSess) return inputSess.value;
                const logoutLink = document.querySelector('a[href*="login/logout.php?sesskey="]');
                if (logoutLink) {
                    const match = logoutLink.href.match(/sesskey=([^&]+)/);
                    return match ? match[1] : null;
                }
                return null;
            });
            
            console.log("Sesskey:", sesskey);
            
            if (sesskey) {
                // Emulate submit form
                await page.evaluate((skey) => {
                    const form = document.createElement('form');
                    form.method = 'POST';
                    form.action = 'processattempt.php';
                    
                    const inputSess = document.createElement('input');
                    inputSess.type = 'hidden';
                    inputSess.name = 'sesskey';
                    inputSess.value = skey;
                    form.appendChild(inputSess);
                    
                    const inputFinish = document.createElement('input');
                    inputFinish.type = 'hidden';
                    inputFinish.name = 'finishattempt';
                    inputFinish.value = '1';
                    form.appendChild(inputFinish);
                    
                    const inputTime = document.createElement('input');
                    inputTime.type = 'hidden';
                    inputTime.name = 'timeup';
                    inputTime.value = '0';
                    form.appendChild(inputTime);
                    
                    document.body.appendChild(form);
                    form.submit();
                }, sesskey);
                
                await page.waitForTimeout(10000);
                console.log("Post submission triggered.");
            } else {
                console.log("Failed to extract sesskey.");
            }
        }

        console.log('Checking final status...');
        await page.goto(targetUrl, { waitUntil: 'commit' });
        await page.waitForTimeout(5000);
        
        const finalPageText = await page.evaluate(() => document.body.innerText);
        fs.writeFileSync('/tmp/quiz_final_result.txt', finalPageText);
        console.log("=== FINAL RESULTS ===");
        console.log(finalPageText);

    } catch (err) {
        console.error('Error during run:', err);
    } finally {
        await context.close();
    }
})();
