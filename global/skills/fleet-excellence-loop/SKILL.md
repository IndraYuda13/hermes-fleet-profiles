---
name: fleet-excellence-loop
description: Evidence-first execution loop for substantial Hermes fleet work. Use when a task is open-ended, multi-step, production-shaped, quality-sensitive, or easy to stop too early. Forces inspection, explicit acceptance, a working artifact, adversarial self-review, repair, real verification, and revision-bound closure without adding pointless ceremony.
metadata:
  hermes:
    editorial_name: "Fleet Excellence Loop"
    editorial_description: "Turn substantial tasks into inspect-build-challenge-repair-verify loops with evidence-bound completion."
---

# Fleet Excellence Loop

Use this skill for M2/M3 work and for M1 work where the first result is easy to overestimate. It operationalizes the fleet runtime core; it does not replace a domain skill.

## 1. Define the finish line

Write a compact contract before large execution:

```text
Outcome:
Scope / protected constraints:
Critical unknowns:
Acceptance criteria:
Failure cases that matter:
Evidence required:
Verifier, if required:
```

Do not turn this into a long planning document. Its purpose is to make premature completion difficult.

## 2. Inspect before invention

Read the current implementation, examples, runtime state, or primary sources that govern the task. Find the load-bearing paths and the likely failure modes. When work is visual, inspect pixels; when behavioral, exercise behavior; when current/factual, verify the source.

## 3. Build an exercisable result

Create the smallest complete result that can be tested in its real mode. Avoid placeholder-heavy scaffolding that cannot reveal whether the approach is actually good.

## 4. Run a hostile self-review

After a working result exists, switch from author to attacker. Ask only questions that can cause a concrete change:

- What requirement did I satisfy only superficially?
- Where did I accept a framework/model default instead of making a decision?
- What breaks under realistic edge states, scale, timing, content, concurrency, or device constraints?
- Which claim has weaker evidence than its wording suggests?
- What would a strong independent reviewer reject first?

Record the material findings, then fix them. Do not produce a ceremonial critique and ship the same artifact.

## 5. Verify the current result

Match the proof to the claim. Examples:

- source/build/test/runtime for software behavior;
- rendered viewport and interaction evidence for UI;
- reproducible measurements for performance/data;
- exploit reproduction and fixed-revision retest for security;
- dated primary sources for current research.

Evidence belongs to the exact revision or artifact it measured. A later material edit invalidates affected proof.

## 6. Use independent challenge where it adds information

For material work, a peer or verifier should receive the outcome, acceptance criteria, artifact/revision, and evidence—not the creator's persuasive narrative. Ask them to falsify the result, not to say whether it seems good.

## 7. Iterate by information gain

Continue a round when it reveals or resolves a material issue. Stop adding rounds when they only restate previous findings. If the quality bar remains unmet, change the approach or escalate; never lower the bar silently.

## Completion packet

Return the finished artifact/result, the checks that actually ran, their outcomes, the current revision when relevant, and material residual limits. Do not dump internal transcripts or inflate routine checks into a long report.
