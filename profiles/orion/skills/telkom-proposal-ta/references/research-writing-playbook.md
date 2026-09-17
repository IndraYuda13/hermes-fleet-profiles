# Research Writing Playbook

## 1. Topic selection

A usable undergraduate TA topic sits at the intersection of:

- a real, bounded problem;
- accessible evidence/data/system context;
- a method the student can execute;
- an evaluation that can be completed within the available time/resources;
- a contribution appropriate for S1 scope.

Avoid choosing a topic solely because a technology is trendy. Start from a problem, then determine whether the technology is justified.

### Topic stress test

Ask:

- What exactly is wrong, unknown, inefficient, inaccurate, risky, costly, or unaddressed?
- Who/what is affected?
- What evidence proves this is not just an assumption?
- What has already been tried?
- Why is the remaining gap worth addressing?
- What data/access/resources are available?
- How will success be measured?

If these cannot be answered, keep the topic provisional.

## 2. Background construction

Use a funnel, but make every transition evidence-based:

1. **Context** - define the domain and relevant phenomenon.
2. **Concrete problem** - state what happens and where.
3. **Impact** - explain why the problem matters.
4. **Prior approaches** - summarize what research/practice has tried.
5. **Limitation/gap** - show what remains unresolved.
6. **Research need** - explain why the proposed work follows logically.
7. **Direction** - introduce the intended method/approach without overselling it.

### Paragraph test

For every paragraph, identify its job in one phrase. If two adjacent paragraphs have no logical bridge, add evidence or restructure rather than adding filler transitions.

### Weak patterns

- broad opening with no relation to the actual research problem;
- statistics without source/year/population;
- “technology X is growing rapidly” filler;
- claiming no prior research without a systematic search;
- introducing the chosen algorithm before the gap is established;
- stating a solution as obviously superior before testing.

## 3. Problem formulation

A strong problem formulation specifies:

- target phenomenon/system;
- failure/knowledge gap;
- scope/context;
- constraints/assumptions;
- what must be determined, improved, compared, designed, or evaluated.

The bundled guide does not require question form. Use question form only if it improves clarity.

### Alignment test

For each problem P1, there should be at least one objective O1 that resolves it. Avoid objectives that introduce new work not motivated by the problem.

## 4. Objectives

Use observable verbs: evaluate, compare, design, implement, measure, analyze, determine, validate, characterize.

Avoid vague objectives such as “mengetahui”, “memahami”, or “membuat aplikasi” unless the actual research contribution is explicitly defined.

A measurable objective should imply an evaluation method.

Example pattern:

`Mengevaluasi [metode/sistem] untuk [task/problem] pada [context/data] menggunakan [metrics/baseline] untuk menentukan [research outcome].`

## 5. Hypothesis

Use only when useful for the research design. Keep it falsifiable/testable where possible.

Do not state the expected result as a guaranteed outcome. Use language such as “diperkirakan”, “dihipotesiskan”, or a formal H0/H1 structure when appropriate.

## 6. Literature review

Build synthesis around **research decisions**, not author chronology.

Suggested structure:

- problem/domain evidence;
- families of approaches/methods;
- comparison of data/context/metrics;
- strengths and limitations;
- unresolved gap;
- implication for the proposed approach.

### Evidence matrix

Maintain at least:

| ID | Citation | Problem | Method | Data/context | Metric | Result | Limitation | Relevance |
|---|---|---|---|---|---|---|---|---|

### Gap derivation

A defensible gap can come from, for example:

- unresolved limitation repeatedly reported in prior work;
- method not evaluated in the target context;
- incompatible/contradictory findings requiring comparison;
- evaluation missing an important dimension;
- dataset/context shift that affects validity;
- engineering constraint not addressed by prior approaches.

“Belum ada yang menggunakan X pada Y” is not automatically a meaningful gap. Explain why that absence matters and what knowledge/value the study adds.

## 7. Method selection

Create a method rationale table when the choice is contestable:

| Candidate | Why plausible | Limitation | Fit to problem/data | Decision |
|---|---|---|---|---|

Justification should depend on problem characteristics and evidence, not popularity.

## 8. Data plan

State:

- data source and ownership/access;
- unit of analysis;
- expected size/coverage;
- inclusion/exclusion criteria;
- labels/ground truth if any;
- cleaning/preprocessing;
- split/validation strategy;
- privacy/ethics concerns if relevant;
- fallback if access fails.

Do not invent a dataset that the user has not confirmed exists or is accessible.

## 9. System/model flow

Make every block correspond to a real step. Typical structure:

`input/data -> acquisition -> preprocessing -> method/model/system -> output -> evaluation`

For software-engineering work, include requirements/context, architecture/design, implementation plan, and verification/evaluation logic as appropriate.

For data-science/ML work, include leakage prevention, train/validation/test strategy, baseline, metrics, and reproducibility choices.

## 10. Evaluation design

Define:

- research question/objective being tested;
- metric or qualitative criterion;
- baseline/comparator where appropriate;
- test scenario;
- sample/data split;
- acceptance or interpretation rule;
- threats/limitations.

A result cannot support a claim broader than the evaluation context.

## 11. Contribution language

Use conservative contribution claims before execution:

- “proposal ini mengusulkan...”
- “penelitian dirancang untuk mengevaluasi...”
- “hasil yang diharapkan adalah...”

Avoid writing “metode ini meningkatkan...” unless actual evidence already exists and is cited.

## 12. Abstract drafting

Draft the abstract last using the official required pieces:

1. problem;
2. objective;
3. proposed method/solution;
4. planned data/case;
5. initial hypothesis/expected outcome;
6. up to 6 keywords.

Keep it consistent with the body. Do not introduce a metric, dataset, method, or claim that does not appear in the proposal.

## 13. Title design

A strong title is specific enough to reveal the core problem/approach/context without becoming a paragraph. Avoid filler such as “Analisis dan Implementasi” unless both are genuinely central.

Use placeholders rather than inventing context:

`[Action/Method] untuk [Problem/Task] pada [Context/Data]`

## 14. Academic integrity and AI-assisted writing

The agent may help organize, critique, explain, rewrite, and draft, but must preserve the distinction between user-provided facts and generated wording.

Never fabricate:

- interview results;
- survey responses;
- experiment metrics;
- code execution results;
- supervisor comments;
- citations;
- institutional approval;
- plagiarism/similarity percentages.

When evidence is unavailable, label the gap clearly.
