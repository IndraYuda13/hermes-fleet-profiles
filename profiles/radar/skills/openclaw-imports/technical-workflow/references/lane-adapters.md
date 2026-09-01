# Lane Adapters

Use the adapter that matches the active technical lane. Keep the parent checklist, success oracle, and artifact set from `SKILL.md` in force.

## 1. Coding and patch work

Use this for normal code changes, bug fixes, refactors, scripts, and repo work.

### Start
- inspect the exact files and existing behavior first
- identify the smallest change surface that can solve the real problem
- define the success oracle before editing
- create at least a short workframe and parent checklist
- if the work is larger than a quick fix, create an implementation plan

### While working
- prefer minimal-diff fixes over broad cleanup
- keep file touch list explicit
- if there is a project change log, update it in the same cycle
- if tests exist, run the narrowest test set that proves the change
- if tests do not fully prove the behavior, add runtime verification
- if approach changes, record the decision and why

### Before calling it done
- confirm the changed behavior with a real oracle
- update the relevant change log or roadmap
- store a verification record with exact evidence
- if the folder is its own git repo, finish with `git status -> commit -> push`

## 2. Automation, bot, and web workflow work

Use this for browser flows, bots, API automation, auth/session handling, shortlink/faucet flows, and similar work.

### Start
- map the strongest evidence lane first
- identify auth, session, endpoint, timer, captcha, or queue boundaries
- create a flow map or oracle map early
- avoid spending time on FAQ or TOS unless they directly explain a blocker

### While working
- prefer the proven HTTP or artifact-backed lane over broad browser assumptions
- keep retries bounded. if the same attempt fails repeatedly, change hypothesis
- distinguish UI movement from true downstream success
- treat logs, callbacks, and intermediate screens as hints, not final proof
- write blockers in exact terms with evidence, not vague summaries

### Before calling it done
- verify the downstream claimed effect
- document the flow, blocker, and durable lesson in structured notes
- update the roadmap or project checklist in the same cycle
- store a verification record that separates intermediate signals from real success

## 3. Reverse engineering and protocol work

Use this only together with the dedicated `reverse-engineering` skill, not instead of it.

### Start
- re-read the relevant case notes first
- rebuild the boundary catalog for the active target if needed
- mark what is proven, what is open, and what is already falsified
- open a hypothesis log if the path is not yet clear

### While working
- trace backward one step at a time
- do not upgrade guesses into conclusions
- favor concrete entry points such as request-signing inputs, bridges, parsers, pinning, and state-mutation boundaries
- persist meaningful artifacts and lessons immediately
- when a claim gets stronger, add proof instead of only rewriting conclusions

### Before calling it done
- make sure the core boundary claim is backed by real evidence
- update the case note, reusable lesson, and checklist
- update the proof log for any promoted claim
- if a patch or tool changed code, update the project change log too
