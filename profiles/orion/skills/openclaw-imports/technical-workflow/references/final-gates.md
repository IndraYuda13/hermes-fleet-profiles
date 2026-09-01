# Final Gates

Do not say `done`, `fixed`, `confirmed`, `works`, or similar unless these gates pass.

## 1. Oracle gate

Ask:
- what exact result was supposed to happen?
- what concrete evidence proves it happened?
- is the evidence downstream enough, or only intermediate?

If the answer is only a UI change, a partial log line, or a callback without downstream effect, the gate is not closed yet.

## 2. Artifact gate

Ask:
- is the workframe still accurate?
- is the parent checklist updated?
- does the relevant artifact set exist for this lane?
- are decisions, blockers, or proof recorded where future sessions can find them?

If not, update the artifacts before reporting completion.

## 3. Notes and change-log gate

Ask:
- did I update the relevant structured note, roadmap, boundary note, or flow note?
- if code changed, did I update the project change log in the same cycle?
- if I learned a reusable lesson, did I store it somewhere future sessions can find?

## 4. Repo or backup gate

Ask:
- if I changed a real git repo, did I commit and push it?
- if this was workspace-only knowledge or skill work, did I run the workspace backup lane?

## 5. Reporting gate

Final report should cover four things in plain language:
- active step
- finding
- meaning
- next step

If a blocker remains, say it directly.
Do not dress up partial progress as completion.
